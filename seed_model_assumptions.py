"""
seed_model_assumptions.py  v1
════════════════════════════════════════════════════════════════
Phase 0a Step 2 — seed the model_assumptions table with the
ten configurable parameters every formula reads from at render
time.

WHY THIS EXISTS
───────────────
Per remara_project_status_2026-04-25 §4 decision 13:
  "model_assumptions table is the single source of truth for
   every configurable parameter. No hardcoded ratios, occupancy
   numbers, thresholds, or operating days anywhere in application
   code."

This script seeds that table once. After this runs, every formula
in the platform reads its inputs from this table.

DESIGN
──────
  • INSERT OR IGNORE strategy. Re-running this script is a no-op
    for any key that already exists. Manual updates made via SQL
    or future UI are preserved across re-runs.
  • Each seed value carries: key, display name, value, units,
    description, source, and an actor stamp ('seed_model_assumptions.py').
  • Takes a DB backup before any mutation (defensive).
  • Audit-logs the seed action via the audit_log table using its
    actual columns (verified 2026-04-25).
  • Prints before/after row counts for verification.

SEED VALUES (per project brief §6.2 — Patrick confirmed 2026-04-25)
──────────────────────────────────────────────────────────────────
  educator_ratio_0_24m            1:4    NQF national
  educator_ratio_24_36m           1:5    NQF national
  educator_ratio_36m_plus         1:11   NQF national
  occupancy_low                   0.70   Brief default (Module 4)
  occupancy_mid                   0.80   Brief default (Module 4)
  occupancy_high                  0.90   Brief default (Module 4)
  operating_days_per_year         240    Brief default (Module 4)
  inspection_due_soon_months      18     Existing UI threshold
  inspection_overdue_years        2      Existing UI threshold
  industry_avg_daily_fee_aud      NULL   Pending Phase 5

USAGE
─────
  python seed_model_assumptions.py --dry-run     (test plan)
  python seed_model_assumptions.py               (apply)

VALIDATION (after run)
──────────────────────
  python -c "import sqlite3; c=sqlite3.connect('data/kintell.db'); print(c.execute('SELECT COUNT(*) FROM model_assumptions').fetchone()[0])"
  → expects: 10
"""

import argparse
import json
import os
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

# UTF-8 on Windows
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DB_PATH = Path("data") / "kintell.db"
BACKUP_PREFIX = "kintell.db.backup_pre_seed_assumptions_"
ACTOR = "seed_model_assumptions.py"


# ─── Seed data ────────────────────────────────────────────────────
# (key, display_name, value_numeric, value_text, units, description, source)
SEED_ROWS = [
    (
        "educator_ratio_0_24m",
        "Educator ratio (0–24 months)",
        0.25,                  # 1 educator per 4 children = 0.25
        "1:4",
        "ratio",
        "Maximum children per educator for the 0–24 months age band. "
        "Drives required_educators on Workforce cards.",
        "NQF national default",
    ),
    (
        "educator_ratio_24_36m",
        "Educator ratio (24–36 months)",
        0.20,                  # 1:5
        "1:5",
        "ratio",
        "Maximum children per educator for the 24–36 months age band. "
        "Drives required_educators on Workforce cards. Some states stricter.",
        "NQF national default",
    ),
    (
        "educator_ratio_36m_plus",
        "Educator ratio (36+ months)",
        0.0909,                # 1:11 ≈ 0.0909
        "1:11",
        "ratio",
        "Maximum children per educator for the 36+ months age band. "
        "Drives required_educators on Workforce cards. Some states stricter.",
        "NQF national default",
    ),
    (
        "occupancy_low",
        "Occupancy assumption (low)",
        0.70,
        None,
        "fraction",
        "Conservative occupancy used in revenue capacity range "
        "(low end of three-band display).",
        "Brief §9 default",
    ),
    (
        "occupancy_mid",
        "Occupancy assumption (mid)",
        0.80,
        None,
        "fraction",
        "Mid-case occupancy used in revenue capacity range "
        "(centre of three-band display).",
        "Brief §9 default",
    ),
    (
        "occupancy_high",
        "Occupancy assumption (high)",
        0.90,
        None,
        "fraction",
        "Aspirational occupancy used in revenue capacity range "
        "(high end of three-band display).",
        "Brief §9 default",
    ),
    (
        "operating_days_per_year",
        "Operating days per year",
        240.0,
        None,
        "days",
        "Operating days used in revenue capacity formula. "
        "Reflects standard centre calendar after closure days, public "
        "holidays, and shutdown periods.",
        "Brief §9 default",
    ),
    (
        "inspection_due_soon_months",
        "Inspection 'due soon' threshold",
        18.0,
        None,
        "months",
        "Centres with last inspection older than this are flagged "
        "as due-soon on the Quality card. Existing UI uses this.",
        "Existing operator.html convention",
    ),
    (
        "inspection_overdue_years",
        "Inspection 'overdue' threshold",
        2.0,
        None,
        "years",
        "Centres with last inspection older than this are flagged "
        "as overdue (amber) on the Quality card. Existing UI uses this.",
        "Existing operator.html convention",
    ),
    (
        "industry_avg_daily_fee_aud",
        "Industry average daily fee (AUD)",
        None,                  # NULL — pending Phase 5
        None,
        "AUD/day",
        "Industry average daily fee per place. Seeded NULL because "
        "no authoritative source yet. Populated in Phase 5 once "
        "KidSoft integration provides per-service real fees, or once "
        "an analyst-supplied fallback is agreed.",
        "Pending — Phase 5",
    ),
]


def take_backup(db_path: Path) -> Path:
    if not db_path.exists():
        raise SystemExit(f"  ✗ DB not found: {db_path}")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = db_path.parent / f"{BACKUP_PREFIX}{ts}"
    shutil.copy2(db_path, backup)
    return backup


def get_existing_keys(conn: sqlite3.Connection) -> set:
    cur = conn.execute("SELECT assumption_key FROM model_assumptions")
    return {r[0] for r in cur.fetchall()}


def get_row_count(conn: sqlite3.Connection) -> int:
    return conn.execute("SELECT COUNT(*) FROM model_assumptions").fetchone()[0]


def write_audit_row(conn: sqlite3.Connection, before_count: int, after_count: int, inserted_keys: list, skipped_keys: list) -> None:
    before_json = {"row_count": before_count}
    after_json = {
        "row_count": after_count,
        "inserted_keys": sorted(inserted_keys),
        "skipped_keys_already_present": sorted(skipped_keys),
    }
    reason = (
        "Seed model_assumptions with 10 default values per project brief §6.2. "
        "Patrick confirmed defaults 2026-04-25. Phase 0a Step 2."
    )
    conn.execute(
        """INSERT INTO audit_log
              (actor, action, subject_type, subject_id,
               before_json, after_json, reason, occurred_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            ACTOR,
            "seed_model_assumptions",
            "table",
            "model_assumptions",
            json.dumps(before_json),
            json.dumps(after_json),
            reason,
            datetime.now().isoformat(timespec="seconds"),
        ),
    )


def run(dry_run: bool) -> int:
    print("─" * 64)
    print("  Seed model_assumptions  (Phase 0a Step 2)")
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

    before_keys = get_existing_keys(conn)
    before_count = get_row_count(conn)
    print(f"  Rows before : {before_count}")

    seed_keys = {row[0] for row in SEED_ROWS}
    will_insert = sorted(seed_keys - before_keys)
    will_skip = sorted(seed_keys & before_keys)

    print(f"  Will insert : {len(will_insert)} rows")
    for k in will_insert:
        print(f"    + {k}")
    if will_skip:
        print(f"  Will skip   : {len(will_skip)} rows (already present)")
        for k in will_skip:
            print(f"    = {k}")

    if dry_run:
        conn.close()
        print("\n  ✓ Dry run complete. No changes made.")
        return 0

    # Apply: backup first
    backup = take_backup(DB_PATH)
    print(f"  Backup : {backup}")

    now_iso = datetime.now().isoformat(timespec="seconds")
    inserted_keys = []
    skipped_keys = list(will_skip)

    try:
        for (key, display_name, val_num, val_txt, units, desc, source) in SEED_ROWS:
            if key in before_keys:
                continue
            conn.execute(
                """INSERT OR IGNORE INTO model_assumptions
                      (assumption_key, display_name, value_numeric, value_text,
                       units, description, source, last_changed_by,
                       last_changed_at, is_active)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)""",
                (key, display_name, val_num, val_txt, units, desc, source, ACTOR, now_iso),
            )
            inserted_keys.append(key)

        after_count = get_row_count(conn)
        write_audit_row(conn, before_count, after_count, inserted_keys, skipped_keys)
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        conn.close()
        print(f"\n  ✗ Seed failed: {e}")
        print(f"  Recovery: restore from {backup}")
        return 1

    after_count = get_row_count(conn)
    print(f"  Rows after  : {after_count}")
    print(f"  Inserted    : {len(inserted_keys)}")
    print(f"  Skipped     : {len(skipped_keys)}")

    # Validate: 10 keys present total
    after_keys = get_existing_keys(conn)
    missing = seed_keys - after_keys
    if missing:
        print(f"\n  ✗ Validation failed. Missing keys: {sorted(missing)}")
        conn.close()
        return 1

    # Show the seeded rows for visibility
    print("\n  Seeded values:")
    cur = conn.execute(
        """SELECT assumption_key, value_numeric, value_text, units
             FROM model_assumptions
            WHERE assumption_key IN ({})
            ORDER BY assumption_key""".format(",".join("?" * len(seed_keys))),
        tuple(seed_keys),
    )
    for k, vn, vt, u in cur.fetchall():
        if vt is not None:
            display = vt
        elif vn is not None:
            display = f"{vn:g}"
        else:
            display = "NULL"
        print(f"    {k:32s}  {display:>8s}  {u or ''}")

    conn.close()
    print(f"\n  ✓ Seed complete. {len(seed_keys)} target keys present in model_assumptions.")
    print(f"  ✓ Backup retained at {backup}")
    return 0


def main():
    p = argparse.ArgumentParser(description="Seed model_assumptions with default values (Phase 0a Step 2)")
    p.add_argument("--dry-run", action="store_true", help="Print plan without mutating DB")
    args = p.parse_args()
    sys.exit(run(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
