"""
migrate_training_completions_tables.py  v1
════════════════════════════════════════════════════════════════
Phase 1.5 Step 1 — additive migration: adds two tables for the
NCVER training-completions ingest.

  training_completions             — one row per (state, remoteness,
                                     program, year) leaf cell from the
                                     NCVER VOCSTATS Program Completions
                                     DataBuilder export.
  training_completions_ingest_run  — one row per ingest invocation,
                                     captures source, filter, caveats,
                                     row count.

DESIGN
──────
  • Purely additive. No mutation of existing tables. DROP TABLE
    removes both with zero impact on existing data.
  • Idempotent. CREATE TABLE IF NOT EXISTS — safe to re-run.
  • Takes a DB backup before mutation per project standard.
  • Writes one audit_log row marking the schema change (using the
    actual audit_log columns: actor/action/subject_type/subject_id/
    before_json/after_json/reason/occurred_at).
  • --dry-run flag prints plan without mutating.

USAGE
─────
    python migrate_training_completions_tables.py --dry-run
    python migrate_training_completions_tables.py

VALIDATION (post-run, automatic):
    Confirms both tables exist with expected columns and that
    audit_log gained one schema_migration_training_completions row.

MANUAL VALIDATION:
    sqlite3 data/kintell.db ".schema training_completions"
    sqlite3 data/kintell.db ".schema training_completions_ingest_run"
"""

import argparse
import json
import os
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DB_PATH = Path("data") / "kintell.db"
BACKUP_PREFIX = "kintell.db.backup_pre_training_completions_"
ACTOR = "migrate_training_completions_tables.py"

EXPECTED_TABLES = {"training_completions", "training_completions_ingest_run"}

DDL = """
-- ─── training_completions_ingest_run ──────────────────────────
-- One row per ingest invocation. Captures provenance for every
-- batch of training_completions rows so caveats and source URLs
-- are recoverable later.
CREATE TABLE IF NOT EXISTS training_completions_ingest_run (
    run_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file         TEXT NOT NULL,
                        -- path to the xlsx ingested
    source_label        TEXT,
                        -- human label, e.g. 'NCVER VOCSTATS 2024'
    publication_date    TEXT,
                        -- ISO date of the underlying publication
    filter_description  TEXT,
                        -- copy of the filter footer from the export
    caveats             TEXT,
                        -- NSW-2024-overstated note, rounding-to-5 etc.
    rows_ingested       INTEGER NOT NULL DEFAULT 0,
    ingested_at         TEXT NOT NULL DEFAULT (datetime('now')),
    ingested_by         TEXT NOT NULL
);

-- ─── training_completions ─────────────────────────────────────
-- One row per (state × remoteness × program × year) leaf cell.
-- Aggregate rows (national totals, state totals, state×remoteness
-- totals) are NOT stored here — re-derive at query time.
CREATE TABLE IF NOT EXISTS training_completions (
    completion_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    state_code          TEXT NOT NULL,
                        -- NSW, VIC, QLD, SA, WA, TAS, NT, ACT,
                        -- OFFSHORE, UNKNOWN
    state_name          TEXT NOT NULL,
                        -- 'New South Wales', etc., as shown in source
    remoteness_band     TEXT,
                        -- 'Major cities', 'Inner regional',
                        -- 'Outer regional', 'Remote', 'Very remote',
                        -- 'Not known'. NULL when source has no
                        -- remoteness (Offshore, Unknown state).
    qualification_code  TEXT NOT NULL,
                        -- CHC30121, CHC30113, CHC50121, CHC50113
    qualification_name  TEXT NOT NULL,
                        -- full title from the source
    qualification_level TEXT NOT NULL CHECK (qualification_level IN ('cert3','diploma')),
    qualification_era   TEXT NOT NULL CHECK (qualification_era IN ('old','new')),
                        -- old = pre-2021 codes (CHC*0113)
                        -- new = post-2021 codes (CHC*0121)
    year                INTEGER NOT NULL,
    completions         INTEGER NOT NULL DEFAULT 0,
                        -- '-' from source stored as 0 per source
                        -- footer ('A dash represents a zero')
    ingest_run_id       INTEGER NOT NULL,
    FOREIGN KEY (ingest_run_id)
        REFERENCES training_completions_ingest_run(run_id)
);

-- Indexes for the read patterns we expect:
--   filter by (state, year) for state-level supply analysis
CREATE INDEX IF NOT EXISTS ix_tc_state_year
    ON training_completions(state_code, year);

--   filter by (qualification_level, year) for level-level supply
CREATE INDEX IF NOT EXISTS ix_tc_level_year
    ON training_completions(qualification_level, year);

--   join back to ingest run for provenance lookups
CREATE INDEX IF NOT EXISTS ix_tc_run
    ON training_completions(ingest_run_id);
"""


def take_backup(db_path: Path) -> Path:
    if not db_path.exists():
        raise SystemExit(f"  ✗ DB not found: {db_path}")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = db_path.parent / f"{BACKUP_PREFIX}{ts}"
    shutil.copy2(db_path, backup)
    return backup


def get_existing_tables(conn):
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    return {r[0] for r in cur.fetchall()}


def get_table_columns(conn, table):
    return [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]


def has_audit_log(conn):
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='audit_log'")
    return cur.fetchone() is not None


def write_audit_row(conn, before_tables, after_tables):
    before_json = {
        "table_count": len(before_tables),
        "tables_present": sorted(before_tables),
    }
    after_json = {
        "table_count": len(after_tables),
        "tables_added": sorted(after_tables - before_tables),
        "indexes_added": ["ix_tc_state_year", "ix_tc_level_year", "ix_tc_run"],
    }
    reason = (
        "Phase 1.5 Step 1 — staging tables for NCVER training "
        "completions ingest. Will hold supply-side data for the "
        "Workforce module's required-vs-supply comparison. Source: "
        "NCVER VOCSTATS Program Completions DataBuilder."
    )
    conn.execute(
        """INSERT INTO audit_log
              (actor, action, subject_type, subject_id,
               before_json, after_json, reason, occurred_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            ACTOR,
            "schema_migration_training_completions",
            "schema",
            "training_completions+training_completions_ingest_run",
            json.dumps(before_json),
            json.dumps(after_json),
            reason,
            datetime.now().isoformat(timespec="seconds"),
        ),
    )


def run(dry_run):
    print("─" * 64)
    print("  Schema migration — training_completions tables")
    print("  (Phase 1.5 Step 1)")
    print("─" * 64)

    if not DB_PATH.exists():
        print(f"  ✗ {DB_PATH} not found. Run from the repo root.")
        return 1

    print(f"  DB     : {DB_PATH}")
    print(f"  Mode   : {'DRY RUN' if dry_run else 'APPLY'}")

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    before_tables = get_existing_tables(conn)
    print(f"  Tables : {len(before_tables)} present before migration")

    already_present = EXPECTED_TABLES & before_tables
    if already_present:
        print(f"  Note   : already present (idempotent re-run): {sorted(already_present)}")

    if dry_run:
        print("\n  Would create (if not already present):")
        for t in sorted(EXPECTED_TABLES - before_tables):
            print(f"    • {t}")
        print("\n  Would create indexes:")
        print("    • ix_tc_state_year")
        print("    • ix_tc_level_year")
        print("    • ix_tc_run")
        if has_audit_log(conn):
            print("\n  Would write one audit_log row: action='schema_migration_training_completions'")
        conn.close()
        print("\n  ✓ Dry run complete. No changes made.")
        return 0

    # Apply
    backup = take_backup(DB_PATH)
    print(f"  Backup : {backup}")

    try:
        conn.executescript(DDL)
        if has_audit_log(conn):
            after_tables = get_existing_tables(conn)
            write_audit_row(conn, before_tables, after_tables)
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        conn.close()
        print(f"\n  ✗ Migration failed: {e}")
        print(f"  Recovery: restore from {backup}")
        return 1

    after_tables = get_existing_tables(conn)
    new_tables = after_tables - before_tables
    print(f"  Tables added : {sorted(new_tables) if new_tables else '(idempotent re-run, no new tables)'}")

    # Validate columns
    tc_cols = set(get_table_columns(conn, "training_completions"))
    tcir_cols = set(get_table_columns(conn, "training_completions_ingest_run"))

    expected_tc = {
        "completion_id", "state_code", "state_name", "remoteness_band",
        "qualification_code", "qualification_name", "qualification_level",
        "qualification_era", "year", "completions", "ingest_run_id",
    }
    expected_tcir = {
        "run_id", "source_file", "source_label", "publication_date",
        "filter_description", "caveats", "rows_ingested",
        "ingested_at", "ingested_by",
    }

    tc_ok = tc_cols == expected_tc
    tcir_ok = tcir_cols == expected_tcir
    print(f"  training_completions cols          : {len(tc_cols)} {'✓' if tc_ok else '✗'}")
    print(f"  training_completions_ingest_run cols: {len(tcir_cols)} {'✓' if tcir_ok else '✗'}")

    # Verify indexes
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='index' "
        "AND name IN ('ix_tc_state_year','ix_tc_level_year','ix_tc_run')"
    )
    indexes = {r[0] for r in cur.fetchall()}
    idx_ok = indexes == {"ix_tc_state_year", "ix_tc_level_year", "ix_tc_run"}
    print(f"  Indexes              : {sorted(indexes)} {'✓' if idx_ok else '✗'}")

    # Verify audit row
    audit_ok = True
    if has_audit_log(conn):
        cur = conn.execute(
            "SELECT COUNT(*) FROM audit_log WHERE action='schema_migration_training_completions'"
        )
        audit_count = cur.fetchone()[0]
        audit_ok = audit_count >= 1
        print(f"  audit_log row        : {audit_count} row(s) {'✓' if audit_ok else '✗'}")

    conn.close()

    if tc_ok and tcir_ok and idx_ok and audit_ok:
        print("\n  ✓ Migration complete. Schema ready for ingest.")
        print(f"  ✓ Backup retained at {backup}")
        return 0
    else:
        print("\n  ✗ Validation failed. Review the output above.")
        print(f"  Recovery: restore from {backup} if needed.")
        return 1


def main():
    p = argparse.ArgumentParser(description="Migration: training_completions + training_completions_ingest_run")
    p.add_argument("--dry-run", action="store_true", help="Print plan without mutating DB")
    args = p.parse_args()
    sys.exit(run(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
