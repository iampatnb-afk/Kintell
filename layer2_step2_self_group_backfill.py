#!/usr/bin/env python3
"""
layer2_step2_self_group_backfill.py v1 — Phase 2.5 Layer 2 Step 2

Creates one self-group per orphan entity (entities with active services
but group_id IS NULL). 2,320 entities -> 2,320 new groups.

Per Patrick's rule: group_name = entity_name (single-entity groups
duplicate the name).

Pattern (Decision 10):
  1. Backup
  2. Pre-state invariants
  3. Build changeset (ownership_type derivation, slug generation)
  4. BEGIN TRANSACTION
  5. INSERT 2,320 groups
  6. SELECT new group_ids back via parent_entity_id mapping
  7. UPDATE 2,320 entities to set group_id
  8. INSERT audit_log row
  9. Post-state invariants -> assert
 10. COMMIT (or ROLLBACK + raise)
 11. Post-commit re-verify

Schema decisions:
  - canonical_name = entity.legal_name
  - display_name   = entity.legal_name
  - slug           = slugify(legal_name) + '-' + str(entity_id)
                     (guaranteed unique; preflight confirmed no
                     canonical_name collision against existing groups)
  - is_for_profit  = derived from ownership_type
                     (private->1, nfp/government/independent_school/
                      catholic_school->0, unknown->NULL)
  - ownership_type = derived from most-common provider_management_type
                     across the entity's active services (PMT_MAP below)
  - parent_entity_id = entity_id (marks the group as a self-group;
                       previously 0/4187 groups used this field)
  - is_active      = 1
  - created_at, updated_at = datetime('now')
"""
import os
import re
import sys
import json
import shutil
import sqlite3
import datetime
from collections import Counter

DB = os.path.join("data", "kintell.db")
TS = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = f"{DB}.backup_pre_self_group_backfill_{TS}"
CHANGESET_CSV = os.path.join("recon", f"layer2_step2_changeset_{TS}.csv")
ACTOR = "layer2_step2_self_group_backfill_v1"
ACTION = "self_group_backfill_v1"

# Invariant baselines (from recon + step 1 results)
EXPECTED_SERVICES_TOTAL = 18223
EXPECTED_ENTITIES_TOTAL = 7143
EXPECTED_GROUPS_TOTAL_PRE = 4187
EXPECTED_ORPHAN_COUNT = 2320

PMT_MAP = {
    "Private for profit": "private",
    "Private not for profit community managed": "nfp",
    "Private not for profit other organisations": "nfp",
    "Independent schools": "independent_school",
    "Catholic schools": "catholic_school",
    "Government managed": "government",
    "State/Territory Government managed": "government",
    "State/Territory government schools": "government",
    "State/Territory and Local Government managed": "government",
    "Local Government": "government",
    "Other": "unknown",
    None: "unknown",
}

OWNERSHIP_TO_FOR_PROFIT = {
    "private": 1,
    "nfp": 0,
    "government": 0,
    "independent_school": 0,
    "catholic_school": 0,
    "unknown": None,
}


def slugify(s: str) -> str:
    s = s.lower()
    s = s.replace("&", " and ")
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s.strip())
    s = re.sub(r"-+", "-", s)
    return s


def banner(msg):
    print("\n" + "=" * 60)
    print(msg)
    print("=" * 60)


def main():
    if not os.path.exists(DB):
        sys.exit(f"FATAL: {DB} not found")

    # ------------------------------------------------------------------
    # 1. Backup
    # ------------------------------------------------------------------
    banner("1. Backup")
    shutil.copy2(DB, BACKUP)
    print(f"  copied -> {BACKUP}")
    print(f"  size: {os.path.getsize(BACKUP):,} bytes")
    if os.path.getsize(BACKUP) != os.path.getsize(DB):
        sys.exit("FATAL: backup size mismatch")

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    def cnt(table, where=""):
        sql = f"SELECT COUNT(*) FROM {table}"
        if where:
            sql += f" WHERE {where}"
        cur.execute(sql)
        return cur.fetchone()[0]

    # ------------------------------------------------------------------
    # 2. Pre-state invariants
    # ------------------------------------------------------------------
    banner("2. Pre-state invariants")
    pre = {
        "services_total": cnt("services"),
        "entities_total": cnt("entities"),
        "groups_total": cnt("groups"),
        "groups_with_parent_entity": cnt("groups", "parent_entity_id IS NOT NULL"),
        "audit_log_count": cnt("audit_log"),
    }
    cur.execute("""
        SELECT COUNT(DISTINCT e.entity_id)
          FROM entities e
          JOIN services s ON s.entity_id = e.entity_id
         WHERE s.is_active=1 AND e.group_id IS NULL;
    """)
    pre["orphan_count"] = cur.fetchone()[0]
    for k, v in pre.items():
        print(f"  {k:<32} {v}")

    if pre["services_total"] != EXPECTED_SERVICES_TOTAL:
        sys.exit(f"FATAL: services_total {pre['services_total']} != {EXPECTED_SERVICES_TOTAL}")
    if pre["entities_total"] != EXPECTED_ENTITIES_TOTAL:
        sys.exit(f"FATAL: entities_total {pre['entities_total']} != {EXPECTED_ENTITIES_TOTAL}")
    if pre["groups_total"] != EXPECTED_GROUPS_TOTAL_PRE:
        sys.exit(f"FATAL: groups_total {pre['groups_total']} != {EXPECTED_GROUPS_TOTAL_PRE}")
    if pre["orphan_count"] != EXPECTED_ORPHAN_COUNT:
        sys.exit(f"FATAL: orphan_count {pre['orphan_count']} != {EXPECTED_ORPHAN_COUNT}")
    if pre["groups_with_parent_entity"] != 0:
        sys.exit(
            f"FATAL: groups_with_parent_entity {pre['groups_with_parent_entity']} != 0 "
            f"(self-group convention assumes this field is unused pre-step-2)"
        )

    # ------------------------------------------------------------------
    # 3. Build changeset
    # ------------------------------------------------------------------
    banner("3. Build changeset")
    cur.execute("""
        SELECT e.entity_id,
               e.legal_name,
               GROUP_CONCAT(s.provider_management_type, '|||') AS pmts
          FROM entities e
          JOIN services s ON s.entity_id = e.entity_id
         WHERE s.is_active=1 AND e.group_id IS NULL
         GROUP BY e.entity_id, e.legal_name
         ORDER BY e.entity_id;
    """)
    orphans = cur.fetchall()
    if len(orphans) != EXPECTED_ORPHAN_COUNT:
        sys.exit(f"FATAL: orphan resultset {len(orphans)} != {EXPECTED_ORPHAN_COUNT}")

    new_group_rows = []          # for INSERT
    audit_rows = []              # for changeset CSV
    ownership_dist = Counter()
    unmapped_pmts = Counter()

    for entity_id, legal_name, pmts_concat in orphans:
        if pmts_concat is None:
            most_common_pmt = None
        else:
            pmts = pmts_concat.split("|||")
            most_common_pmt = Counter(pmts).most_common(1)[0][0]
        ownership = PMT_MAP.get(most_common_pmt, "unknown")
        if most_common_pmt not in PMT_MAP:
            unmapped_pmts[most_common_pmt] += 1
        is_for_profit = OWNERSHIP_TO_FOR_PROFIT[ownership]
        slug = f"{slugify(legal_name)}-{entity_id}"
        new_group_rows.append((
            legal_name,         # canonical_name
            legal_name,         # display_name
            slug,               # slug
            is_for_profit,      # is_for_profit
            ownership,          # ownership_type
            entity_id,          # parent_entity_id
        ))
        audit_rows.append((entity_id, legal_name, slug, ownership, is_for_profit, most_common_pmt))
        ownership_dist[ownership] += 1

    print(f"  changeset size           : {len(new_group_rows):,}")
    print(f"  ownership_type distribution:")
    for ot, n in ownership_dist.most_common():
        print(f"    {n:>5}  {ot}")
    if unmapped_pmts:
        print(f"  WARNING — unmapped PMTs (defaulted to unknown):")
        for pmt, n in unmapped_pmts.most_common():
            print(f"    {n}x {pmt!r}")

    # Slug uniqueness check inside changeset
    slug_counts = Counter(r[2] for r in new_group_rows)
    dup_slugs = {s: c for s, c in slug_counts.items() if c > 1}
    if dup_slugs:
        sys.exit(f"FATAL: duplicate slugs in changeset: {dup_slugs}")

    # Slug uniqueness against existing groups
    cur.execute("SELECT slug FROM groups;")
    existing_slugs = {row[0] for row in cur.fetchall() if row[0]}
    new_slugs = {r[2] for r in new_group_rows}
    collision = existing_slugs & new_slugs
    if collision:
        sys.exit(f"FATAL: slug collision with existing groups: {sorted(collision)[:10]}")

    print(f"  slug uniqueness          : OK ({len(new_slugs)} new, no internal/existing collisions)")

    os.makedirs("recon", exist_ok=True)
    import csv
    with open(CHANGESET_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["entity_id", "legal_name", "slug", "ownership_type", "is_for_profit", "most_common_pmt"])
        for r in audit_rows:
            w.writerow(r)
    print(f"  changeset csv -> {CHANGESET_CSV}")

    # ------------------------------------------------------------------
    # 4-9. Transaction
    # ------------------------------------------------------------------
    banner("4. Apply transaction")
    try:
        cur.execute("BEGIN TRANSACTION;")

        # Step A: INSERT 2,320 groups
        cur.executemany("""
            INSERT INTO groups
                (canonical_name, display_name, slug, is_for_profit,
                 ownership_type, parent_entity_id, is_active,
                 created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, 1, datetime('now'), datetime('now'));
        """, new_group_rows)
        print(f"  INSERT groups            : {cur.rowcount} rows")

        # Step B: build entity_id -> group_id mapping
        cur.execute("""
            SELECT group_id, parent_entity_id
              FROM groups
             WHERE parent_entity_id IS NOT NULL;
        """)
        eid_to_gid = {row[1]: row[0] for row in cur.fetchall()}
        if len(eid_to_gid) != len(new_group_rows):
            raise RuntimeError(
                f"map size {len(eid_to_gid)} != changeset {len(new_group_rows)}"
            )
        print(f"  entity_id -> group_id    : {len(eid_to_gid)} mappings")

        # Step C: UPDATE entities.group_id
        update_pairs = [(gid, eid) for eid, gid in eid_to_gid.items()]
        cur.executemany("""
            UPDATE entities
               SET group_id = ?, updated_at = datetime('now')
             WHERE entity_id = ?;
        """, update_pairs)
        print(f"  UPDATE entities          : {cur.rowcount} rows")

        # Step D: audit_log
        before_json = json.dumps({
            "groups_total": pre["groups_total"],
            "orphan_entity_count": pre["orphan_count"],
            "groups_with_parent_entity": pre["groups_with_parent_entity"],
        })
        after_json = json.dumps({
            "groups_total_delta": len(new_group_rows),
            "entities_linked": len(update_pairs),
            "ownership_distribution": dict(ownership_dist),
        })
        reason = (
            f"Phase 2.5 Layer 2 Step 2 — orphan-entity self-group backfill. "
            f"Created {len(new_group_rows)} groups (one per orphan entity with active services), "
            f"linked entities.group_id. Per Patrick: group_name=entity_name. "
            f"ownership_type derived from most-common provider_management_type per entity. "
            f"parent_entity_id=entity_id marks self-groups (was 0/4187 used). "
            f"slug pattern: slugify(legal_name)-{{entity_id}}. "
            f"Backup: {BACKUP}. Changeset: {CHANGESET_CSV}."
        )
        cur.execute("""
            INSERT INTO audit_log
                (actor, action, subject_type, subject_id,
                 before_json, after_json, reason)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (ACTOR, ACTION, "entities_groups", 0, before_json, after_json, reason))
        print(f"  INSERT audit_log         : 1 row")

        # Step E: post-state invariants
        post = {
            "services_total": cnt("services"),
            "entities_total": cnt("entities"),
            "groups_total": cnt("groups"),
            "groups_with_parent_entity": cnt("groups", "parent_entity_id IS NOT NULL"),
        }
        cur.execute("""
            SELECT COUNT(DISTINCT e.entity_id)
              FROM entities e
              JOIN services s ON s.entity_id = e.entity_id
             WHERE s.is_active=1 AND e.group_id IS NULL;
        """)
        post["orphan_count"] = cur.fetchone()[0]
        print(f"  post-state (in-tx):")
        for k, v in post.items():
            print(f"    {k:<32} {v}")

        assert post["services_total"] == pre["services_total"], "services rowcount changed"
        assert post["entities_total"] == pre["entities_total"], "entities rowcount changed"
        assert post["groups_total"] == pre["groups_total"] + len(new_group_rows), \
            f"groups_total {post['groups_total']} != pre {pre['groups_total']} + {len(new_group_rows)}"
        assert post["orphan_count"] == 0, \
            f"orphan_count post-backfill should be 0, got {post['orphan_count']}"
        assert post["groups_with_parent_entity"] == len(new_group_rows), \
            f"groups_with_parent_entity {post['groups_with_parent_entity']} != {len(new_group_rows)}"

        conn.commit()
        print("  COMMIT OK")

    except Exception as e:
        conn.rollback()
        print(f"  ROLLBACK: {e}")
        raise

    # ------------------------------------------------------------------
    # 10. Post-commit re-verify
    # ------------------------------------------------------------------
    banner("5. Post-commit re-verify")
    final = {
        "groups_total": cnt("groups"),
        "groups_with_parent_entity": cnt("groups", "parent_entity_id IS NOT NULL"),
        "audit_log_count": cnt("audit_log"),
    }
    cur.execute("""
        SELECT COUNT(DISTINCT e.entity_id)
          FROM entities e
          JOIN services s ON s.entity_id = e.entity_id
         WHERE s.is_active=1 AND e.group_id IS NULL;
    """)
    final["orphan_count"] = cur.fetchone()[0]
    for k, v in final.items():
        print(f"  {k:<32} {v}")
    cur.execute("""
        SELECT audit_id, action, subject_type, occurred_at
          FROM audit_log ORDER BY audit_id DESC LIMIT 1;
    """)
    print(f"  last audit row: {cur.fetchone()}")

    assert final["audit_log_count"] == pre["audit_log_count"] + 1
    assert final["orphan_count"] == 0
    assert final["groups_total"] == pre["groups_total"] + len(new_group_rows)

    conn.close()
    banner("DONE")
    print(f"  backup        : {BACKUP}")
    print(f"  changeset     : {CHANGESET_CSV}")
    print(f"  groups added  : {len(new_group_rows)}")
    print(f"  entities linked: {len(update_pairs)}")


if __name__ == "__main__":
    main()
