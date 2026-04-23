"""
migrate_schema_v0_4.py  v1
────────────────────────────────────────────────────────────────
Tier 2 Phase C — additive schema migration for the NQS ingest.

Adds these columns to the services table:
  aria_plus                TEXT      -- ABS Remoteness 5-band string
  seifa_decile             INTEGER   -- 1..10, nullable
  service_sub_type         TEXT      -- 'LDC','OSHC','PSK','FDC','Other'
  provider_management_type TEXT      -- raw ACECQA string, retained
  qa1 .. qa7               TEXT      -- one column per NQS quality area

All columns are nullable. No existing column is renamed or removed.

Idempotent: if a column already exists, that ADD is skipped. Safe to
run multiple times without side effects.

Pre-flight:
  - Confirms DB exists.
  - Writes a timestamped backup to data\kintell.db.backup_migrate_v04_<ts>
    BEFORE touching the schema. This backup is separate from the
    pre-tier2 backup and gives us a second recovery point that is
    strictly "just before the schema change".

Post-flight:
  - Reports the new column list.
  - Writes one row to audit_log (action='schema_migration_v0_4')
    capturing before/after column counts so the migration is visible
    in the merge-review history for audit completeness.

CLI:
  python migrate_schema_v0_4.py            (real run)
  python migrate_schema_v0_4.py --dry-run  (prints plan, no writes)
"""

import argparse
import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

ROOT    = Path(__file__).resolve().parent
DB_PATH = ROOT / "data" / "kintell.db"

# Columns to add. Each tuple: (column_name, column_type, comment)
# Order matters only for readability in the printed report.
NEW_SERVICES_COLUMNS = [
    ("aria_plus",                "TEXT",    "ABS Remoteness 5-band string"),
    ("seifa_decile",             "INTEGER", "SEIFA decile 1..10"),
    ("service_sub_type",         "TEXT",    "LDC / OSHC / PSK / FDC / Other"),
    ("provider_management_type", "TEXT",    "raw ACECQA PMT string (for reference)"),
    ("qa1",                      "TEXT",    "Quality Area 1 rating"),
    ("qa2",                      "TEXT",    "Quality Area 2 rating"),
    ("qa3",                      "TEXT",    "Quality Area 3 rating"),
    ("qa4",                      "TEXT",    "Quality Area 4 rating"),
    ("qa5",                      "TEXT",    "Quality Area 5 rating"),
    ("qa6",                      "TEXT",    "Quality Area 6 rating"),
    ("qa7",                      "TEXT",    "Quality Area 7 rating"),
]


def connect():
    if not DB_PATH.exists():
        raise RuntimeError(f"Database not found: {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def existing_columns(conn, table):
    return {r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()}


def backup_db():
    ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = DB_PATH.with_name(f"kintell.db.backup_migrate_v04_{ts}")
    shutil.copy2(DB_PATH, dst)
    return dst


def log_audit(conn, before_cols, after_cols, added_cols):
    conn.execute(
        "INSERT INTO audit_log "
        "(actor, action, subject_type, subject_id, "
        " before_json, after_json, reason) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            "system",
            "schema_migration_v0_4",
            "table",                  # subject_type
            0,                        # subject_id (N/A for a schema-level action)
            json.dumps({"services_columns": sorted(before_cols)}),
            json.dumps({"services_columns": sorted(after_cols)}),
            f"Added {len(added_cols)} columns to services: {sorted(added_cols)}",
        ),
    )


def main():
    parser = argparse.ArgumentParser(description="Schema migration v0.4 for Tier 2 NQS ingest.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show plan; write nothing.")
    args = parser.parse_args()

    conn = connect()
    try:
        before = existing_columns(conn, "services")
        plan = [(col, typ, note) for col, typ, note in NEW_SERVICES_COLUMNS
                if col not in before]
        skip = [(col, typ, note) for col, typ, note in NEW_SERVICES_COLUMNS
                if col in before]

        print(f"\n── migrate_schema_v0_4 ──")
        print(f"DB: {DB_PATH}")
        print(f"services table currently has {len(before)} columns")
        print()

        if skip:
            print(f"Already present, skipping ({len(skip)}):")
            for col, typ, note in skip:
                print(f"  ✓ {col:28} {typ:8}  — {note}")
            print()

        if not plan:
            print("Nothing to add. services table is already at v0.4.")
            return 0

        print(f"Will add ({len(plan)}):")
        for col, typ, note in plan:
            print(f"  + {col:28} {typ:8}  — {note}")
        print()

        if args.dry_run:
            print("--dry-run: no writes. Exiting.")
            return 0

        # Backup before any writes
        backup_path = backup_db()
        print(f"Backup written: {backup_path.name}")

        # Apply each ADD COLUMN in its own transaction
        added = []
        for col, typ, note in plan:
            try:
                conn.execute(f"ALTER TABLE services ADD COLUMN {col} {typ}")
                added.append(col)
                print(f"  + added {col}")
            except sqlite3.OperationalError as e:
                # Safety net — another process added the column between our
                # PRAGMA check and the ALTER. Not fatal, just report.
                if "duplicate column" in str(e).lower():
                    print(f"  ~ {col} already existed (race); continuing")
                else:
                    raise

        after = existing_columns(conn, "services")
        log_audit(conn, before, after, added)
        conn.commit()

        print()
        print(f"services table now has {len(after)} columns (added {len(added)})")
        print(f"audit_log row written (action='schema_migration_v0_4').")
        print()
        return 0

    except Exception as e:
        conn.rollback()
        print(f"ERROR — migration rolled back: {e}", file=sys.stderr)
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
