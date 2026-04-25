"""
migrate_schema_v0_3.py  v1
--------------------------
Additive schema migration for the Operator Summary Page.

Adds two columns to data/kintell.db:
  groups.parent_entity_id  INTEGER nullable  -> entities(entity_id)
  entities.is_notional     INTEGER DEFAULT 0

Plus a partial index on groups.parent_entity_id for later join perf.

Safety design:
  1. Pre-flight snapshot: counts of active groups, deactivated groups,
     entities, services, accepted merges, pending proposals, audit_log
     rows, plus entity counts in any active group whose canonical_name
     contains 'SPARROW' or 'HARMONY' (our two consolidated operators).
  2. Backup: copy data/kintell.db to data/kintell.db.backup_<timestamp>.
  3. Migrate: idempotent ALTER TABLE ADD COLUMN — skipped if the
     column already exists. Never re-commits or re-runs anything that
     would change existing data.
  4. Post-flight snapshot + delta check: every pre-flight count must
     match post-flight. Any drift is a FAIL and prints rollback path.
  5. Schema pretty-print so you can see the new columns landed.

Run from project root. Read-and-alter; no data rows modified.
"""

import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path("data/kintell.db")


def section(title: str) -> None:
    print()
    print("=" * 72)
    print(f"  {title}")
    print("=" * 72)


def snapshot(con: sqlite3.Connection) -> dict:
    s = {}
    s["total_groups"] = con.execute(
        "SELECT COUNT(*) FROM groups"
    ).fetchone()[0]
    s["active_groups"] = con.execute(
        "SELECT COUNT(*) FROM groups WHERE is_active=1"
    ).fetchone()[0]
    s["deactivated_groups"] = con.execute(
        "SELECT COUNT(*) FROM groups WHERE is_active=0"
    ).fetchone()[0]
    s["entities"] = con.execute(
        "SELECT COUNT(*) FROM entities"
    ).fetchone()[0]
    s["services"] = con.execute(
        "SELECT COUNT(*) FROM services"
    ).fetchone()[0]
    s["accepted_merges"] = con.execute(
        "SELECT COUNT(*) FROM link_candidates WHERE status='accepted'"
    ).fetchone()[0]
    s["pending_proposals"] = con.execute(
        "SELECT COUNT(*) FROM link_candidates WHERE status='pending'"
    ).fetchone()[0]
    s["audit_log_rows"] = con.execute(
        "SELECT COUNT(*) FROM audit_log"
    ).fetchone()[0]

    def entities_in(gid: int) -> int:
        return con.execute(
            "SELECT COUNT(*) FROM entities WHERE group_id=?", (gid,)
        ).fetchone()[0]

    sparrow = con.execute(
        "SELECT group_id, canonical_name FROM groups "
        "WHERE is_active=1 AND canonical_name LIKE '%SPARROW%' "
        "ORDER BY group_id"
    ).fetchall()
    harmony = con.execute(
        "SELECT group_id, canonical_name FROM groups "
        "WHERE is_active=1 AND canonical_name LIKE '%HARMONY%' "
        "ORDER BY group_id"
    ).fetchall()

    s["sparrow_landmarks"] = [
        (gid, name, entities_in(gid)) for gid, name in sparrow
    ]
    s["harmony_landmarks"] = [
        (gid, name, entities_in(gid)) for gid, name in harmony
    ]
    return s


def print_snapshot(label: str, s: dict) -> None:
    print(f"[{label}]")
    print(f"  total groups           : {s['total_groups']}")
    print(f"  active                 : {s['active_groups']}")
    print(f"  deactivated            : {s['deactivated_groups']}")
    print(f"  entities               : {s['entities']}")
    print(f"  services               : {s['services']}")
    print(f"  accepted merges        : {s['accepted_merges']}")
    print(f"  pending proposals      : {s['pending_proposals']}")
    print(f"  audit_log rows         : {s['audit_log_rows']}")
    for gid, name, n in s["sparrow_landmarks"]:
        shortname = name if len(name) < 55 else name[:52] + "..."
        print(f"  Sparrow gid {gid:<5} ({shortname:<55}) : {n} entities")
    for gid, name, n in s["harmony_landmarks"]:
        shortname = name if len(name) < 55 else name[:52] + "..."
        print(f"  Harmony gid {gid:<5} ({shortname:<55}) : {n} entities")


def column_exists(con: sqlite3.Connection, table: str, col: str) -> bool:
    rows = con.execute(f"PRAGMA table_info({table})").fetchall()
    return any(r[1] == col for r in rows)


def print_table_schema(con: sqlite3.Connection, table: str) -> None:
    print(f"  {table}:")
    for r in con.execute(f"PRAGMA table_info({table})").fetchall():
        cid, name, typ, notnull, default, pk = r
        tags = []
        if pk:      tags.append("PK")
        if notnull: tags.append("NOT NULL")
        if default is not None: tags.append(f"default={default}")
        suffix = ("  [" + ", ".join(tags) + "]") if tags else ""
        print(f"    {cid:>2}  {name:<24} {typ:<12}{suffix}")


def main() -> None:
    if not DB_PATH.exists():
        print(f"DB not found at {DB_PATH.resolve()}. Run from project root.")
        sys.exit(1)

    section("1. Pre-migration snapshot")
    con = sqlite3.connect(DB_PATH)
    pre = snapshot(con)
    print_snapshot("pre", pre)
    con.close()

    section("2. Backup")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = DB_PATH.with_name(f"kintell.db.backup_{ts}")
    shutil.copy2(DB_PATH, backup)
    size_kb = backup.stat().st_size / 1024
    print(f"backup saved to : {backup}  ({size_kb:.1f} KB)")

    section("3. Migrate (ALTER TABLE ADD COLUMN — idempotent)")
    con = sqlite3.connect(DB_PATH)

    if column_exists(con, "groups", "parent_entity_id"):
        print("  groups.parent_entity_id         already present — skipped")
    else:
        con.execute(
            "ALTER TABLE groups "
            "ADD COLUMN parent_entity_id INTEGER "
            "REFERENCES entities(entity_id)"
        )
        con.commit()
        print("  groups.parent_entity_id         ADDED")

    if column_exists(con, "entities", "is_notional"):
        print("  entities.is_notional            already present — skipped")
    else:
        con.execute(
            "ALTER TABLE entities "
            "ADD COLUMN is_notional INTEGER DEFAULT 0"
        )
        con.commit()
        print("  entities.is_notional            ADDED")

    con.execute(
        "CREATE INDEX IF NOT EXISTS ix_groups_parent_entity "
        "ON groups(parent_entity_id) "
        "WHERE parent_entity_id IS NOT NULL"
    )
    con.commit()
    print("  ix_groups_parent_entity (partial) ensured")

    con.close()

    section("4. Post-migration snapshot")
    con = sqlite3.connect(DB_PATH)
    post = snapshot(con)
    print_snapshot("post", post)

    section("5. Delta check")
    diffs = []
    scalar_keys = [
        "total_groups", "active_groups", "deactivated_groups",
        "entities", "services", "accepted_merges",
        "pending_proposals", "audit_log_rows",
    ]
    for k in scalar_keys:
        if pre[k] != post[k]:
            diffs.append(f"{k}: {pre[k]} -> {post[k]}")
            print(f"  {k:<22} CHANGED: {pre[k]} -> {post[k]}")
        else:
            print(f"  {k:<22} unchanged ({pre[k]})")
    if pre["sparrow_landmarks"] != post["sparrow_landmarks"]:
        diffs.append(
            f"sparrow_landmarks drifted: {pre['sparrow_landmarks']} "
            f"-> {post['sparrow_landmarks']}"
        )
    else:
        print(f"  sparrow_landmarks       unchanged")
    if pre["harmony_landmarks"] != post["harmony_landmarks"]:
        diffs.append("harmony_landmarks drifted")
    else:
        print(f"  harmony_landmarks       unchanged")

    # New-column assertions
    if not column_exists(con, "groups", "parent_entity_id"):
        diffs.append("groups.parent_entity_id NOT present after migration")
    if not column_exists(con, "entities", "is_notional"):
        diffs.append("entities.is_notional NOT present after migration")

    # Defaults sanity
    mn_mx = con.execute(
        "SELECT COALESCE(MIN(is_notional),0), COALESCE(MAX(is_notional),0) "
        "FROM entities"
    ).fetchone()
    print(f"  is_notional range       min={mn_mx[0]}, max={mn_mx[1]} (both should be 0)")
    if mn_mx != (0, 0):
        diffs.append(f"is_notional default unexpected: {mn_mx}")

    non_null_parents = con.execute(
        "SELECT COUNT(*) FROM groups WHERE parent_entity_id IS NOT NULL"
    ).fetchone()[0]
    print(f"  groups with parent set  {non_null_parents} (expected 0)")
    if non_null_parents != 0:
        diffs.append(
            f"parent_entity_id has {non_null_parents} non-null rows unexpectedly"
        )

    section("6. Schema after migration")
    print_table_schema(con, "groups")
    print()
    print_table_schema(con, "entities")
    con.close()

    section("RESULT")
    if diffs:
        print("FAILED — drift or missing columns detected:")
        for d in diffs:
            print(f"  - {d}")
        print()
        print(f"Backup available at: {backup}")
        print("To roll back, stop any process using the DB and run:")
        print(f"  Copy-Item -Path '{backup}' -Destination '{DB_PATH}' -Force")
        sys.exit(2)

    print("OK. Schema is now v0.3.")
    print(f"Backup retained at: {backup}")
    print("Re-run is safe (ALTER statements are idempotent).")


if __name__ == "__main__":
    main()
