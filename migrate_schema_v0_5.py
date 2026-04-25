"""
migrate_schema_v0_5.py  v2
════════════════════════════════════════════════════════════════
Schema migration v0.5 — Foundation tables for the Market /
Workforce / Compliance / Valuation Intelligence Overlay.

v2 changes:
  • audit_log INSERT corrected. v1 used (action, subject_type,
    subject_id, payload, actor, created_at) which assumed a
    schema that doesn't exist. Actual audit_log columns are
    (actor, action, subject_type, subject_id, before_json,
    after_json, reason, occurred_at) — verified 2026-04-25.

Adds two new tables. Purely additive — no changes to existing
tables, columns, or indexes.

  metric_definitions    — Documents every metric the platform
                          surfaces. Name, formula, classification
                          (OBS/DER/COM), source, description,
                          version. Read by the UI badge component.

  model_assumptions     — Single source of truth for every
                          configurable parameter (educator ratios,
                          occupancy bands, operating days, due-soon
                          and overdue thresholds, industry avg fee).
                          Every formula reads its inputs from here
                          at render time. Changes audit-logged.

Design (per remara_project_status_2026-04-25 §4 decisions 11–13):
  • Additive only. No mutation of existing tables, columns, or
    indexes. DROP TABLE removes both with zero side effects on
    the existing 4,078 active groups, 7,143 entities, 18,223
    services, 110 accepted merges.
  • Idempotent. CREATE TABLE IF NOT EXISTS — safe to re-run.
  • Takes its own backup before mutation per project standard
    (working_standards #8). Backup tag: pre_schema_v0_5_<ts>.
  • Writes one audit_log row marking the schema change with
    before/after table sets.
  • --dry-run flag prints the plan without mutating anything.

Usage:
    python migrate_schema_v0_5.py --dry-run     (test plan)
    python migrate_schema_v0_5.py               (apply)

Validation (post-run, automatic):
    Checks both new tables exist with the expected columns and
    that audit_log gained one schema_migration_v0_5 row.

Manual validation (after run):
    sqlite3 data/kintell.db ".schema metric_definitions"
    sqlite3 data/kintell.db ".schema model_assumptions"
    sqlite3 data/kintell.db "SELECT action, created_at FROM audit_log WHERE action='schema_migration_v0_5';"
"""

import argparse
import json
import os
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

# UTF-8 on Windows so unicode box-drawing chars don't crash cp1252
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DB_PATH = Path("data") / "kintell.db"
BACKUP_PREFIX = "kintell.db.backup_pre_schema_v0_5_"

EXPECTED_TABLES = {"metric_definitions", "model_assumptions"}

DDL = """
-- ─── metric_definitions ────────────────────────────────────────
-- Documents every metric the platform surfaces.
-- Read by the OBS/DER/COM badge component on every UI card.
CREATE TABLE IF NOT EXISTS metric_definitions (
    metric_key       TEXT PRIMARY KEY,
                     -- short key used by code, e.g. 'children_per_place'
    display_name     TEXT NOT NULL,
                     -- human label shown in UI, e.g. 'Children per place'
    classification   TEXT NOT NULL CHECK (classification IN ('OBS','DER','COM')),
                     -- OBS = Observed (ABS, ACECQA, KidSoft, inspection records)
                     -- DER = Derived (transparent formula over OBS inputs)
                     -- COM = Commentary (rule-based interpretation, no AI)
    formula          TEXT,
                     -- plain-English formula for DER metrics; NULL for OBS
                     -- e.g. 'children_0_4 / licensed_places (SA2)'
    source           TEXT,
                     -- authoritative source for OBS metrics
                     -- e.g. 'ABS Census 2021', 'ACECQA NQS Q4 2025'
    units            TEXT,
                     -- e.g. 'count', 'ratio', 'AUD/day', 'percent', 'months'
    description      TEXT,
                     -- analyst-facing description, what it tells you
    version          TEXT NOT NULL DEFAULT 'v1',
                     -- bump when formula or interpretation changes
    created_at       TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at       TEXT
);

-- ─── model_assumptions ─────────────────────────────────────────
-- Single source of truth for every configurable parameter.
-- Every formula reads from here at render time. No hardcoded
-- ratios, thresholds, or defaults in application code.
CREATE TABLE IF NOT EXISTS model_assumptions (
    assumption_key   TEXT PRIMARY KEY,
                     -- short key used by code, e.g. 'educator_ratio_0_24m'
    display_name     TEXT NOT NULL,
                     -- human label, e.g. 'Educator ratio (0-24 months)'
    value_numeric    REAL,
                     -- numeric value when applicable; NULL otherwise
    value_text       TEXT,
                     -- text value (e.g. '1:4') when numeric inadequate
    units            TEXT,
                     -- e.g. 'ratio', 'percent', 'days', 'months', 'AUD/day'
    description      TEXT,
                     -- why this value, what depends on it
    source           TEXT,
                     -- e.g. 'NQF national', 'analyst judgement', 'KidSoft'
    last_changed_by  TEXT,
                     -- who set the current value (script name or 'manual')
    last_changed_at  TEXT NOT NULL DEFAULT (datetime('now')),
    is_active        INTEGER NOT NULL DEFAULT 1
);

-- Indexes for the read patterns we expect:
--   metric_definitions: lookup by key (PK already covers)
--   metric_definitions: filter by classification for badge rendering
CREATE INDEX IF NOT EXISTS ix_metric_def_classification
    ON metric_definitions(classification);

--   model_assumptions: filter to active values only
CREATE INDEX IF NOT EXISTS ix_model_assumption_active
    ON model_assumptions(is_active) WHERE is_active = 1;
"""


def take_backup(db_path: Path) -> Path:
    if not db_path.exists():
        raise SystemExit(f"  ✗ DB not found: {db_path}")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = db_path.parent / f"{BACKUP_PREFIX}{ts}"
    shutil.copy2(db_path, backup)
    return backup


def get_existing_tables(conn: sqlite3.Connection) -> set:
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    return {r[0] for r in cur.fetchall()}


def get_table_columns(conn: sqlite3.Connection, table: str) -> list:
    cur = conn.execute(f"PRAGMA table_info({table})")
    return [r[1] for r in cur.fetchall()]


def has_audit_log(conn: sqlite3.Connection) -> bool:
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='audit_log'"
    )
    return cur.fetchone() is not None


def write_audit_row(conn: sqlite3.Connection, before_tables: set, after_tables: set) -> None:
    # audit_log actual columns (verified 2026-04-25):
    #   audit_id, actor, action, subject_type, subject_id,
    #   before_json, after_json, reason, occurred_at
    before_json = {
        "table_count": len(before_tables),
        "tables_present": sorted(before_tables),
    }
    after_json = {
        "table_count": len(after_tables),
        "tables_added": sorted(after_tables - before_tables),
        "indexes_added": ["ix_metric_def_classification", "ix_model_assumption_active"],
    }
    reason = (
        "Foundation for OBS/DER/COM classification + configurable-assumptions "
        "discipline (Phase 0a). See remara_project_status_2026-04-25 §4 "
        "decisions 11-13."
    )
    conn.execute(
        """INSERT INTO audit_log
              (actor, action, subject_type, subject_id,
               before_json, after_json, reason, occurred_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            "migrate_schema_v0_5.py",
            "schema_migration_v0_5",
            "schema",
            "metric_definitions+model_assumptions",
            json.dumps(before_json),
            json.dumps(after_json),
            reason,
            datetime.now().isoformat(timespec="seconds"),
        ),
    )


def run(dry_run: bool) -> int:
    print("─" * 64)
    print("  Schema migration v0.5  (metric_definitions + model_assumptions)")
    print("─" * 64)

    if not DB_PATH.exists():
        print(f"  ✗ {DB_PATH} not found. Run from the repo root.")
        return 1

    print(f"  DB     : {DB_PATH}")
    print(f"  Mode   : {'DRY RUN' if dry_run else 'APPLY'}")

    # Pre-state
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
        print("\n  Would create indexes (if not already present):")
        print("    • ix_metric_def_classification")
        print("    • ix_model_assumption_active")
        if has_audit_log(conn):
            print("\n  Would write one audit_log row: action='schema_migration_v0_5'")
        else:
            print("\n  Note: audit_log table not found — would skip audit row.")
        conn.close()
        print("\n  ✓ Dry run complete. No changes made.")
        return 0

    # Apply: backup first
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

    # Post-state validation
    after_tables = get_existing_tables(conn)
    new_tables = after_tables - before_tables
    print(f"  Tables added : {sorted(new_tables) if new_tables else '(idempotent re-run, no new tables)'}")

    # Validate columns are correct on each new table
    md_cols = set(get_table_columns(conn, "metric_definitions"))
    ma_cols = set(get_table_columns(conn, "model_assumptions"))

    expected_md = {
        "metric_key", "display_name", "classification", "formula",
        "source", "units", "description", "version", "created_at", "updated_at",
    }
    expected_ma = {
        "assumption_key", "display_name", "value_numeric", "value_text",
        "units", "description", "source", "last_changed_by",
        "last_changed_at", "is_active",
    }

    md_ok = md_cols == expected_md
    ma_ok = ma_cols == expected_ma

    print(f"  metric_definitions cols : {len(md_cols)} {'✓' if md_ok else '✗'}")
    print(f"  model_assumptions  cols : {len(ma_cols)} {'✓' if ma_ok else '✗'}")

    # Verify indexes
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='index' "
        "AND name IN ('ix_metric_def_classification','ix_model_assumption_active')"
    )
    indexes = {r[0] for r in cur.fetchall()}
    idx_ok = indexes == {"ix_metric_def_classification", "ix_model_assumption_active"}
    print(f"  Indexes              : {sorted(indexes)} {'✓' if idx_ok else '✗'}")

    # Verify audit row landed
    audit_ok = True
    if has_audit_log(conn):
        cur = conn.execute(
            "SELECT COUNT(*) FROM audit_log WHERE action='schema_migration_v0_5'"
        )
        audit_count = cur.fetchone()[0]
        audit_ok = audit_count >= 1
        print(f"  audit_log row        : {audit_count} row(s) {'✓' if audit_ok else '✗'}")
    else:
        print("  audit_log row        : table missing, skipped")

    conn.close()

    if md_ok and ma_ok and idx_ok and audit_ok:
        print("\n  ✓ Migration complete. Schema v0.5 applied.")
        print(f"  ✓ Backup retained at {backup}")
        return 0
    else:
        print("\n  ✗ Validation failed. Review the output above.")
        print(f"  Recovery: restore from {backup} if needed.")
        return 1


def main():
    p = argparse.ArgumentParser(description="Schema migration v0.5: metric_definitions + model_assumptions")
    p.add_argument("--dry-run", action="store_true", help="Print plan without mutating DB")
    args = p.parse_args()
    sys.exit(run(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
