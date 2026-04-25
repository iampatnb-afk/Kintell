"""
add_commentary_threshold.py  v1
════════════════════════════════════════════════════════════════
Phase 0a Step 3a — adds one row to model_assumptions:

    commentary_inspection_threshold = 0.30

This threshold drives the Quality card's COM (Commentary) line:
"Elevated inspection exposure" appears when more than this fraction
of a group's active centres are past the due-soon threshold.

WHY A SEPARATE SCRIPT
─────────────────────
The main seed_model_assumptions.py covered the 10 values agreed in
the project brief §6.2. This new value emerged in the Step 3
planning conversation (2026-04-25) as a consequence of decision 5:
COM tooltips must cite a real assumption value, not a hardcoded
percentage. Keeping it as a small addition rather than re-running
the main seed preserves a clean per-step audit trail.

DESIGN
──────
  • INSERT OR IGNORE — re-running is a no-op if the row exists.
  • Takes a DB backup before mutation.
  • Audit-logs via existing audit_log table.
  • --dry-run flag prints the plan without mutating.

USAGE
─────
  python add_commentary_threshold.py --dry-run
  python add_commentary_threshold.py
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
BACKUP_PREFIX = "kintell.db.backup_pre_commentary_threshold_"
ACTOR = "add_commentary_threshold.py"

NEW_ROW = {
    "key":          "commentary_inspection_threshold",
    "display_name": "Commentary trigger: inspection exposure",
    "value_numeric": 0.30,
    "value_text":   None,
    "units":        "fraction",
    "description":  (
        "Threshold above which the Quality card's COM (Commentary) line "
        "'Elevated inspection exposure' is rendered. Triggers when more "
        "than this fraction of active centres exceed the due-soon "
        "threshold (inspection_due_soon_months). Sourced from the brief "
        "§14 example rule. Phase 7's commentary_rules table will "
        "eventually centralise rules; this row is the single source of "
        "truth for the threshold value itself."
    ),
    "source":       "Brief §14 example rule",
}


def take_backup(db_path: Path) -> Path:
    if not db_path.exists():
        raise SystemExit(f"  ✗ DB not found: {db_path}")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = db_path.parent / f"{BACKUP_PREFIX}{ts}"
    shutil.copy2(db_path, backup)
    return backup


def write_audit_row(conn: sqlite3.Connection, before_count: int, after_count: int, was_inserted: bool) -> None:
    before_json = {"row_count": before_count}
    after_json = {
        "row_count": after_count,
        "inserted_key": NEW_ROW["key"] if was_inserted else None,
        "no_op": not was_inserted,
    }
    reason = (
        "Add commentary_inspection_threshold (0.30) to model_assumptions. "
        "Required by Phase 0a Step 3 — Quality card COM tooltip must cite "
        "a real assumption value, not a hardcoded percentage. Decision 5 "
        "in the 2026-04-25 planning conversation."
    )
    conn.execute(
        """INSERT INTO audit_log
              (actor, action, subject_type, subject_id,
               before_json, after_json, reason, occurred_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            ACTOR,
            "add_model_assumption",
            "model_assumptions",
            NEW_ROW["key"],
            json.dumps(before_json),
            json.dumps(after_json),
            reason,
            datetime.now().isoformat(timespec="seconds"),
        ),
    )


def run(dry_run: bool) -> int:
    print("─" * 64)
    print("  Add commentary_inspection_threshold to model_assumptions")
    print("  (Phase 0a Step 3a)")
    print("─" * 64)

    if not DB_PATH.exists():
        print(f"  ✗ {DB_PATH} not found. Run from the repo root.")
        return 1

    print(f"  DB     : {DB_PATH}")
    print(f"  Mode   : {'DRY RUN' if dry_run else 'APPLY'}")

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    # Sanity: table must exist
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='model_assumptions'"
    )
    if not cur.fetchone():
        conn.close()
        print("  ✗ model_assumptions table not found. Run migrate_schema_v0_5.py first.")
        return 1

    before_count = conn.execute("SELECT COUNT(*) FROM model_assumptions").fetchone()[0]
    cur = conn.execute(
        "SELECT 1 FROM model_assumptions WHERE assumption_key = ?", (NEW_ROW["key"],)
    )
    already_exists = cur.fetchone() is not None

    print(f"  Rows before : {before_count}")
    print(f"  Target key  : {NEW_ROW['key']}")
    print(f"  Target value: {NEW_ROW['value_numeric']}  {NEW_ROW['units']}")
    print(f"  Status      : {'already present (no-op)' if already_exists else 'will insert'}")

    if dry_run:
        conn.close()
        print("\n  ✓ Dry run complete. No changes made.")
        return 0

    backup = take_backup(DB_PATH)
    print(f"  Backup : {backup}")

    now_iso = datetime.now().isoformat(timespec="seconds")
    try:
        cur = conn.execute(
            """INSERT OR IGNORE INTO model_assumptions
                  (assumption_key, display_name, value_numeric, value_text,
                   units, description, source, last_changed_by,
                   last_changed_at, is_active)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)""",
            (
                NEW_ROW["key"],
                NEW_ROW["display_name"],
                NEW_ROW["value_numeric"],
                NEW_ROW["value_text"],
                NEW_ROW["units"],
                NEW_ROW["description"],
                NEW_ROW["source"],
                ACTOR,
                now_iso,
            ),
        )
        was_inserted = cur.rowcount > 0
        after_count = conn.execute("SELECT COUNT(*) FROM model_assumptions").fetchone()[0]
        write_audit_row(conn, before_count, after_count, was_inserted)
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        conn.close()
        print(f"\n  ✗ Insert failed: {e}")
        print(f"  Recovery: restore from {backup}")
        return 1

    print(f"  Rows after  : {after_count}")
    print(f"  Inserted    : {'yes' if was_inserted else 'no (key already present)'}")

    # Final validation: row exists with correct value
    cur = conn.execute(
        "SELECT assumption_key, value_numeric, units, source "
        "FROM model_assumptions WHERE assumption_key = ?",
        (NEW_ROW["key"],),
    )
    row = cur.fetchone()
    if row is None:
        print("\n  ✗ Validation failed: target row not present after insert.")
        conn.close()
        return 1

    print(f"\n  Final state:")
    print(f"    {row[0]:32s}  {row[1]:>6.2f}  {row[2]}  ({row[3]})")
    conn.close()
    print(f"\n  ✓ Step 3a complete. {NEW_ROW['key']} present in model_assumptions.")
    print(f"  ✓ Backup retained at {backup}")
    return 0


def main():
    p = argparse.ArgumentParser(description="Add commentary_inspection_threshold to model_assumptions")
    p.add_argument("--dry-run", action="store_true", help="Print plan without mutating DB")
    args = p.parse_args()
    sys.exit(run(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
