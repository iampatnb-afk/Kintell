"""
probe_service_catchment_cache.py v2
=====================================
Sub-pass 4.3.5 — pre-mutation read-only probe per STD-30 and DEC-65.

v2 change: the audit_log section in v1 assumed a column named `id`,
which is not the actual PK. v2 calls PRAGMA table_info on audit_log
first to surface the real schema, then queries via rowid (always
available in SQLite unless WITHOUT ROWID is declared, which audit_log
does not).

Inventories the current state of `service_catchment_cache` before the
schema migration that adds 7 columns. Read-only: opens the DB in
read-only mode and performs no writes.

Outputs to console:
  1. service_catchment_cache — current schema (column name, type,
     nullability, default, PK flag) via PRAGMA table_info.
  2. service_catchment_cache — current row count.
  3. service_catchment_cache — current index list via PRAGMA
     index_list (so the migration does not collide with an existing
     index).
  4. audit_log — schema (PRAGMA table_info) so the migration script
     can hardcode the correct INSERT column list per STD-11.
  5. audit_log — latest 5 rows by rowid.
  6. Backup file listing in data/ (most recent 10) — confirms STD-08
     backups are landing where expected and surfaces any stale
     pre_4_3_5_* file from a prior aborted attempt.
  7. Existence check for the 7 columns the migration will add — so
     re-running the probe after the migration shows the new shape
     and so an accidental partial migration is visible.

Does NOT search the codebase for consumers — that is a separate
PowerShell Select-String step.

Usage (from repo root):
    python probe_service_catchment_cache.py
"""

import os
import sqlite3
import sys

DB_PATH = os.path.join("data", "kintell.db")
TABLE = "service_catchment_cache"
EXPECTED_NEW_COLUMNS = [
    "adjusted_demand",
    "capture_rate",
    "demand_supply",
    "child_to_place",
    "calibrated_rate",
    "rule_text",
    "calibration_run_at",
]


def section(title: str) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def open_readonly(db_path: str) -> sqlite3.Connection:
    """Open SQLite in read-only mode via URI. Probe must not write."""
    if not os.path.exists(db_path):
        print(f"ERROR: DB not found at {db_path}", file=sys.stderr)
        sys.exit(1)
    uri = f"file:{db_path}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def print_table_info(cur: sqlite3.Cursor, table: str) -> list:
    """Print PRAGMA table_info as a formatted table. Return rows."""
    cur.execute(f"PRAGMA table_info({table})")
    rows = cur.fetchall()
    if not rows:
        print(f"WARNING: {table} not found in DB.")
        return rows
    print(f"{'cid':<5}{'name':<28}{'type':<14}{'notnull':<9}"
          f"{'dflt':<18}{'pk':<3}")
    print("-" * 76)
    for cid, name, ctype, notnull, dflt, pk in rows:
        print(f"{cid:<5}{name:<28}{ctype:<14}{notnull:<9}"
              f"{str(dflt):<18}{pk:<3}")
    return rows


def main() -> None:
    print(f"Probe target : {os.path.abspath(DB_PATH)}")
    print(f"Open mode    : read-only (URI mode=ro)")
    print(f"Probe version: v2")
    conn = open_readonly(DB_PATH)
    cur = conn.cursor()

    # 1. Schema of service_catchment_cache
    section(f"1. {TABLE} — current schema (PRAGMA table_info)")
    rows = print_table_info(cur, TABLE)

    # 2. Row count
    section(f"2. {TABLE} — row count")
    cur.execute(f"SELECT COUNT(*) FROM {TABLE}")
    (n,) = cur.fetchone()
    print(f"rows: {n}")
    if n == 0:
        print("(matches OI-05: table is empty — migration is "
              "structurally safe.)")
    else:
        print("WARNING: table is NOT empty. OI-05 is stale. "
              "Stop and re-plan before mutating.")

    # 3. Indexes
    section(f"3. {TABLE} — indexes (PRAGMA index_list)")
    cur.execute(f"PRAGMA index_list({TABLE})")
    idx_rows = cur.fetchall()
    if not idx_rows:
        print("(no indexes)")
    else:
        for row in idx_rows:
            print(row)

    # 4. audit_log schema
    section("4. audit_log — schema (PRAGMA table_info)")
    audit_cols = print_table_info(cur, "audit_log")

    # 5. audit_log latest rows by rowid
    section("5. audit_log — latest 5 rows (by rowid)")
    cur.execute(
        "SELECT rowid, * FROM audit_log ORDER BY rowid DESC LIMIT 5"
    )
    audit_rows = cur.fetchall()
    if not audit_rows:
        print("(audit_log is empty)")
    else:
        col_names = ["rowid"] + [c[1] for c in audit_cols]
        for r in audit_rows:
            print()
            for name, val in zip(col_names, r):
                sval = str(val)
                if len(sval) > 80:
                    sval = sval[:77] + "..."
                print(f"  {name:<16} {sval}")

    # 6. Backup file listing
    section("6. data/ — most recent 10 backup-pattern files")
    data_dir = "data"
    if os.path.isdir(data_dir):
        entries = []
        for name in os.listdir(data_dir):
            full = os.path.join(data_dir, name)
            if os.path.isfile(full) and "backup" in name.lower():
                entries.append((os.path.getmtime(full), name))
        entries.sort(reverse=True)
        for _, name in entries[:10]:
            print(name)
        if not entries:
            print("(no backup-pattern files in data/)")
    else:
        print(f"WARNING: {data_dir} dir not found")

    # 7. Existence check for the 7 new columns
    section(f"7. {TABLE} — existence check for the 7 new columns")
    existing = {row[1] for row in rows}
    print(f"{'column':<28}{'present?':<10}")
    print("-" * 38)
    for col in EXPECTED_NEW_COLUMNS:
        present = "YES" if col in existing else "no"
        print(f"{col:<28}{present:<10}")
    overlap = [c for c in EXPECTED_NEW_COLUMNS if c in existing]
    if overlap:
        print()
        print(f"WARNING: {len(overlap)} of the 7 target columns "
              f"already exist: {overlap}")
        print("Migration is NOT clean — re-plan before applying.")
    else:
        print()
        print("All 7 target columns are absent. "
              "Migration is clean to apply.")

    conn.close()
    print()
    print("Probe complete. No writes performed.")


if __name__ == "__main__":
    main()
