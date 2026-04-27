#!/usr/bin/env python3
"""
layer2_step1_sa2_backfill.py v2 — Phase 2.5 Layer 2 Step 1
SA2 backfill on services via postcode_to_sa2_concordance.csv.

v2 changes:
  - Filter blank-SA2 rows at concordance load (436 postcodes have ('', '')
    in the source CSV; treating these as unmatched rather than writing
    empty strings to services.sa2_code).
  - Updated audit_log reason and skip-count reporting.

Pattern (Decision 10):
  1. Take own timestamped backup
  2. Build changeset in memory; write to recon/ for audit
  3. Pre-state invariants
  4. BEGIN TRANSACTION
  5. UPDATE services SET sa2_code, sa2_name (executemany)
  6. INSERT audit_log row
  7. Post-state invariants — assert all hold
  8. COMMIT (or ROLLBACK + re-raise on any exception)
  9. Post-commit re-verify
"""
import os
import sys
import csv
import json
import shutil
import sqlite3
import datetime

DB = os.path.join("data", "kintell.db")
CONCORDANCE = os.path.join("abs_data", "postcode_to_sa2_concordance.csv")
TS = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = f"{DB}.backup_pre_sa2_backfill_{TS}"
CHANGESET_CSV = os.path.join("recon", f"layer2_step1_changeset_{TS}.csv")
ACTOR = "layer2_step1_sa2_backfill_v2"
ACTION = "sa2_backfill_v1"

# Invariant baselines (from recon/layer1_db_findings.md and preflight)
EXPECTED_SERVICES_TOTAL = 18223
EXPECTED_ENTITIES = 7143
EXPECTED_GROUPS = 4187


def banner(msg):
    print("\n" + "=" * 60)
    print(msg)
    print("=" * 60)


def main():
    if not os.path.exists(DB):
        sys.exit(f"FATAL: {DB} not found")
    if not os.path.exists(CONCORDANCE):
        sys.exit(f"FATAL: {CONCORDANCE} not found")

    # ------------------------------------------------------------------
    # 1. Backup (Standard 8)
    # ------------------------------------------------------------------
    banner("1. Backup")
    shutil.copy2(DB, BACKUP)
    print(f"  copied -> {BACKUP}")
    print(f"  size: {os.path.getsize(BACKUP):,} bytes")
    if os.path.getsize(BACKUP) != os.path.getsize(DB):
        sys.exit("FATAL: backup size mismatch")

    # ------------------------------------------------------------------
    # 2. Load concordance (filter blanks)
    # ------------------------------------------------------------------
    banner("2. Load concordance")
    pc_to_sa2 = {}
    skipped_blank = 0
    total_rows = 0
    with open(CONCORDANCE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_rows += 1
            pc = row["POSTCODE"].strip()
            sa2_code = row["SA2_CODE"].strip()
            sa2_name = row["SA2_NAME"].strip()
            if sa2_code == "" or sa2_name == "":
                skipped_blank += 1
                continue
            if pc.isdigit():
                pc = pc.zfill(4)
            pc_to_sa2[pc] = (sa2_code, sa2_name)
    print(f"  total rows in CSV       : {total_rows:,}")
    print(f"  skipped (blank SA2)     : {skipped_blank:,}")
    print(f"  loaded postcodes        : {len(pc_to_sa2):,}")

    # ------------------------------------------------------------------
    # 3. Connect + pre-state invariants
    # ------------------------------------------------------------------
    banner("3. Pre-state invariants")
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    def cnt(table, where=""):
        sql = f"SELECT COUNT(*) FROM {table}"
        if where:
            sql += f" WHERE {where}"
        cur.execute(sql)
        return cur.fetchone()[0]

    pre = {
        "services_total": cnt("services"),
        "services_active": cnt("services", "is_active=1"),
        "services_sa2_populated": cnt(
            "services",
            "is_active=1 AND sa2_code IS NOT NULL AND sa2_code != ''",
        ),
        "entities_total": cnt("entities"),
        "groups_total": cnt("groups"),
        "audit_log_count": cnt("audit_log"),
    }
    for k, v in pre.items():
        print(f"  {k:<28} {v}")

    if pre["services_total"] != EXPECTED_SERVICES_TOTAL:
        sys.exit(f"FATAL: services_total {pre['services_total']} != expected {EXPECTED_SERVICES_TOTAL}")
    if pre["entities_total"] != EXPECTED_ENTITIES:
        sys.exit(f"FATAL: entities_total {pre['entities_total']} != expected {EXPECTED_ENTITIES}")
    if pre["groups_total"] != EXPECTED_GROUPS:
        sys.exit(f"FATAL: groups_total {pre['groups_total']} != expected {EXPECTED_GROUPS}")
    if pre["services_sa2_populated"] != 0:
        sys.exit(
            f"FATAL: services_sa2_populated {pre['services_sa2_populated']} != 0 "
            f"(backfill must run on a clean column; aborting to avoid partial-state)"
        )

    # ------------------------------------------------------------------
    # 4. Build changeset
    # ------------------------------------------------------------------
    banner("4. Build changeset")
    cur.execute(
        """SELECT service_id, postcode
             FROM services
            WHERE is_active=1
              AND postcode IS NOT NULL
              AND TRIM(postcode) != '';"""
    )
    raw_rows = cur.fetchall()
    no_postcode_count = pre["services_active"] - len(raw_rows)

    changeset = []   # list of (sa2_code, sa2_name, service_id)
    audit_rows = []  # list of (service_id, postcode_norm, sa2_code, sa2_name)
    unmatched = []   # list of (service_id, postcode_norm)

    for sid, pc in raw_rows:
        pcnorm = str(pc).strip()
        if pcnorm.replace(".0", "").isdigit():
            pcnorm = pcnorm.replace(".0", "").zfill(4)
        if pcnorm in pc_to_sa2:
            sa2_code, sa2_name = pc_to_sa2[pcnorm]
            changeset.append((sa2_code, sa2_name, sid))
            audit_rows.append((sid, pcnorm, sa2_code, sa2_name))
        else:
            unmatched.append((sid, pcnorm))

    print(f"  changeset (matched updates) : {len(changeset):,}")
    print(f"  unmatched                   : {len(unmatched):,}")
    print(f"  no postcode populated       : {no_postcode_count:,}")

    from collections import Counter
    unmatched_pcs = Counter(p[1] for p in unmatched)
    if unmatched_pcs:
        print(f"  unmatched postcode top-10:")
        for pc, n in unmatched_pcs.most_common(10):
            print(f"    {pc}: {n} services")

    os.makedirs("recon", exist_ok=True)
    with open(CHANGESET_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["service_id", "postcode_normalized", "sa2_code", "sa2_name"])
        for r in audit_rows:
            w.writerow(r)
    print(f"  changeset csv -> {CHANGESET_CSV}")

    # ------------------------------------------------------------------
    # 5+6+7. Transaction: UPDATE services + INSERT audit_log + invariants
    # ------------------------------------------------------------------
    banner("5. Apply transaction")
    try:
        cur.execute("BEGIN TRANSACTION;")
        cur.executemany(
            "UPDATE services SET sa2_code=?, sa2_name=? WHERE service_id=?;",
            changeset,
        )
        print(f"  UPDATE services         : {cur.rowcount} rows affected")

        before_json = json.dumps({
            "services_sa2_populated": pre["services_sa2_populated"],
            "concordance_rows_loaded": len(pc_to_sa2),
            "concordance_rows_skipped_blank": skipped_blank,
        })
        after_json = json.dumps({
            "services_sa2_populated": len(changeset),
            "unmatched_postcodes": len(unmatched),
            "no_postcode": no_postcode_count,
            "coverage_pct_active": round(len(changeset) / pre["services_active"] * 100, 4),
        })
        reason = (
            f"Phase 2.5 Layer 2 Step 1 — postcode-keyed SA2 backfill "
            f"via abs_data/postcode_to_sa2_concordance.csv (v2: blank-SA2 rows filtered). "
            f"{len(changeset)} services updated; {len(unmatched)} unmatched (postcode "
            f"absent or blank in concordance); {no_postcode_count} no-postcode services. "
            f"Concordance: {len(pc_to_sa2)} loaded, {skipped_blank} blank skipped. "
            f"Backup: {BACKUP}. Changeset: {CHANGESET_CSV}. "
            f"Step 1b TODO: lat/lng polygon point-in-polygon for unmatched, "
            f"requires SA2 boundary geometry file (not in abs_data)."
        )
        cur.execute(
            """INSERT INTO audit_log
                 (actor, action, subject_type, subject_id, before_json, after_json, reason)
               VALUES (?, ?, ?, ?, ?, ?, ?);""",
            (ACTOR, ACTION, "services", 0, before_json, after_json, reason),
        )
        print(f"  INSERT audit_log        : 1 row")

        post = {
            "services_total": cnt("services"),
            "services_active": cnt("services", "is_active=1"),
            "services_sa2_populated": cnt(
                "services",
                "is_active=1 AND sa2_code IS NOT NULL AND sa2_code != ''",
            ),
            "entities_total": cnt("entities"),
            "groups_total": cnt("groups"),
        }
        print(f"  post-state (in-tx):")
        for k, v in post.items():
            print(f"    {k:<28} {v}")

        assert post["services_total"] == pre["services_total"], "services rowcount changed"
        assert post["services_active"] == pre["services_active"], "active services changed"
        assert post["entities_total"] == pre["entities_total"], "entities changed"
        assert post["groups_total"] == pre["groups_total"], "groups changed"
        assert post["services_sa2_populated"] == len(changeset), (
            f"sa2 populated {post['services_sa2_populated']} != changeset {len(changeset)}"
        )

        conn.commit()
        print("  COMMIT OK")

    except Exception as e:
        conn.rollback()
        print(f"  ROLLBACK: {e}")
        raise

    # ------------------------------------------------------------------
    # 8. Post-commit re-verify (Standard 5)
    # ------------------------------------------------------------------
    banner("6. Post-commit re-verify")
    final = {
        "services_total": cnt("services"),
        "services_sa2_populated": cnt(
            "services",
            "is_active=1 AND sa2_code IS NOT NULL AND sa2_code != ''",
        ),
        "audit_log_count": cnt("audit_log"),
    }
    for k, v in final.items():
        print(f"  {k:<28} {v}")
    cur.execute(
        """SELECT audit_id, action, subject_type, occurred_at
             FROM audit_log
            ORDER BY audit_id DESC LIMIT 1;"""
    )
    row = cur.fetchone()
    print(f"  last audit row: {row}")

    assert final["audit_log_count"] == pre["audit_log_count"] + 1
    assert final["services_sa2_populated"] == len(changeset)

    conn.close()
    banner("DONE")
    print(f"  backup     : {BACKUP}")
    print(f"  changeset  : {CHANGESET_CSV}")
    print(f"  coverage   : {len(changeset)}/{pre['services_active']} active services "
          f"({len(changeset) / pre['services_active'] * 100:.2f}%)")
    print(f"  gap        : {len(unmatched) + no_postcode_count} services "
          f"(deferred to step 1b — lat/lng polygon lookup)")


if __name__ == "__main__":
    main()
