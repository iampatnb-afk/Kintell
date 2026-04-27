"""
Layer 2 Step 6 APPLY v2 — ABS ERP at SA2 ingest (long format)
─────────────────────────────────────────────────────────────
v2 changes from v1:
  - audit_log INSERT now binds to the real schema discovered in
    diag section 8: (actor, action, subject_type, subject_id,
    before_json, after_json, reason, occurred_at).
  - data_start_row=8 (not 7 — row 7 is the sub-header).
  - total_persons=3 (Estimated resident population, all ages).
    NOT 121 (fertility rate decimal).

Pattern matches Layer 2 steps 1, 2, 4:
  backup -> BEGIN -> CREATE TABLE -> ETL -> audit_log -> invariants -> COMMIT

Two modes:
  (default)  --dry-run : extract + write changeset CSV; no DB mutation
  --apply              : backup + transaction + INSERT + audit + commit

Long-format schema:
  abs_sa2_erp_annual (sa2_code, year, age_group, persons)
  age_group in {under_5_persons, under_5_males, under_5_females, total_persons}
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path

import openpyxl

PROJECT_ROOT = Path.cwd()
WORKBOOK = PROJECT_ROOT / "abs_data" / "Population and People Database.xlsx"
DB = PROJECT_ROOT / "data" / "kintell.db"
OUT_DIR = PROJECT_ROOT / "recon"
COL_MAP_PATH = OUT_DIR / "layer2_step6_column_map.json"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_PATH = PROJECT_ROOT / "data" / f"kintell.db.backup_pre_step6_{TS}"
CHANGESET_PATH = OUT_DIR / f"layer2_step6_changeset_{TS}.csv"

AGE_GROUP_MAP = [
    ("under_5_persons", "under_5_persons"),
    ("under_5_males", "under_5_males"),
    ("under_5_females", "under_5_females"),
    ("total_persons", "total_persons"),
]

# Audit identity for this ingest
ACTOR = "layer2_step6_apply_v2"
ACTION = "sa2_erp_ingest_v1"
SUBJECT_TYPE = "abs_sa2_erp_annual"
SUBJECT_ID = 0  # table-scoped event; no per-row subject


def banner(title: str) -> str:
    return f"\n{'-' * 70}\n{title}\n{'-' * 70}"


def to_int(v, null_markers: set[str]) -> int | None:
    if v is None:
        return None
    s = str(v).strip()
    if s in null_markers:
        return None
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return None


def load_column_map() -> dict:
    if not COL_MAP_PATH.exists():
        print(f"FAIL: column map not found at {COL_MAP_PATH}")
        print("      Run layer2_step6_diag.py first.")
        sys.exit(1)
    return json.loads(COL_MAP_PATH.read_text(encoding="utf-8"))


def validate_column_map(col_map: dict) -> list[str]:
    cm = col_map["columns"]
    issues = []
    for k in ["sa2_code", "region_label", "year_column",
              "under_5_persons", "under_5_males", "under_5_females",
              "total_persons"]:
        if cm.get(k) is None:
            issues.append(f"  - `{k}` is null in column map")
    return issues


def extract_rows(col_map: dict) -> list[tuple]:
    cm = col_map["columns"]
    null_markers = set(col_map["null_markers"])
    skip_until = col_map["data_start_row"] - 1

    out: list[tuple] = []
    wb = openpyxl.load_workbook(WORKBOOK, read_only=True, data_only=True)
    ws = wb[col_map["table_sheet"]]

    for row_idx, row in enumerate(ws.iter_rows(values_only=True), start=1):
        if row_idx <= skip_until:
            continue

        sa2_cell = row[cm["sa2_code"]] if cm["sa2_code"] < len(row) else None
        if sa2_cell is None:
            continue
        sa2 = str(sa2_cell).strip()
        if not (sa2.isdigit() and len(sa2) == 9):
            continue

        yr_col = cm["year_column"]
        year_val = row[yr_col] if yr_col < len(row) else None
        year = to_int(year_val, null_markers)
        if year is None:
            continue

        for age_group, key in AGE_GROUP_MAP:
            col_idx = cm.get(key)
            if col_idx is None:
                continue
            if col_idx >= len(row):
                continue
            persons = to_int(row[col_idx], null_markers)
            out.append((sa2, year, age_group, persons))

    wb.close()
    return out


def write_changeset(rows: list[tuple]) -> None:
    with open(CHANGESET_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["sa2_code", "year", "age_group", "persons"])
        w.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true",
                        help="Mutate the DB. Without this flag, dry-run only.")
    args = parser.parse_args()

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(banner(f"LAYER 2 STEP 6 v2 — ABS ERP INGEST ({mode})"))
    print(f"Workbook:   {WORKBOOK}")
    print(f"DB:         {DB}")
    print(f"Column map: {COL_MAP_PATH}")
    print(f"Timestamp:  {TS}")

    if not WORKBOOK.exists():
        print("FAIL: workbook not found")
        return 1
    if not DB.exists():
        print("FAIL: DB not found")
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    col_map = load_column_map()
    issues = validate_column_map(col_map)
    if issues:
        print(banner("ABORT: column map incomplete"))
        for i in issues:
            print(i)
        print(f"\nEdit / regenerate the JSON at:\n  {COL_MAP_PATH}")
        return 1

    print(banner("RESOLVED COLUMN MAP"))
    for k, v in col_map["columns"].items():
        print(f"  {k:20s} -> {v}")

    # ---- EXTRACT ----------------------------------------------------
    print(banner("EXTRACT"))
    t0 = time.time()
    rows = extract_rows(col_map)
    elapsed = time.time() - t0
    print(f"Extracted {len(rows):,} long-format rows in {elapsed:.1f}s")

    n_total = len(rows)
    n_nonnull = sum(1 for r in rows if r[3] is not None)
    n_null = n_total - n_nonnull
    distinct_sa2 = len({r[0] for r in rows})
    distinct_years = sorted({r[1] for r in rows})
    distinct_age = sorted({r[2] for r in rows})

    print(f"  Distinct SA2:      {distinct_sa2:,}")
    print(f"  Distinct years:    {distinct_years}")
    print(f"  Age groups:        {distinct_age}")
    print(f"  Non-null persons:  {n_nonnull:,}")
    print(f"  Null persons:      {n_null:,}  (years 2011/2016 expected)")

    print("\nFirst 8 rows:")
    for r in rows[:8]:
        print(f"  {r}")

    if rows:
        sample_sa2 = rows[0][0]
        sample = [r for r in rows if r[0] == sample_sa2]
        print(f"\nFull extraction for SA2 {sample_sa2} ({len(sample)} rows):")
        for r in sample[:40]:
            print(f"  year={r[1]}  age_group={r[2]:18s}  persons={r[3]}")

    # Sanity check: under_5_males + under_5_females should ~= under_5_persons
    print(banner("SANITY CHECK: under-5 males + females ~= persons"))
    by_year_sa2 = {}
    for r in rows:
        by_year_sa2.setdefault((r[0], r[1]), {})[r[2]] = r[3]
    mismatches = 0
    checks = 0
    sample_mismatches = []
    for (sa2, year), grp in by_year_sa2.items():
        m = grp.get("under_5_males")
        f = grp.get("under_5_females")
        p = grp.get("under_5_persons")
        if m is None or f is None or p is None:
            continue
        checks += 1
        if abs((m + f) - p) > 5:  # allow tiny ABS rounding
            mismatches += 1
            if len(sample_mismatches) < 5:
                sample_mismatches.append((sa2, year, m, f, p))
    print(f"  Checks performed: {checks:,}")
    print(f"  Mismatches > 5:   {mismatches}")
    if sample_mismatches:
        print("  Sample mismatches:")
        for x in sample_mismatches:
            print(f"    sa2={x[0]} year={x[1]}  m={x[2]} f={x[3]} p={x[4]}")
    else:
        print("  All under-5 splits internally consistent.")

    # Sanity check: total_persons should be substantially larger than under_5
    print(banner("SANITY CHECK: total_persons >> under_5_persons"))
    ratio_samples = []
    for (sa2, year), grp in list(by_year_sa2.items())[:1000]:
        u5 = grp.get("under_5_persons")
        tot = grp.get("total_persons")
        if u5 is None or tot is None or u5 == 0:
            continue
        ratio = tot / u5 if u5 > 0 else None
        if ratio is not None:
            ratio_samples.append((sa2, year, u5, tot, ratio))
    if ratio_samples:
        ratios = [r[4] for r in ratio_samples]
        avg = sum(ratios) / len(ratios)
        print(f"  Sample size: {len(ratio_samples):,}")
        print(f"  Mean ratio (total/u5): {avg:.1f}  (expect ~15-30 for "
              f"healthy SA2; under 5 means total_persons is wrong)")
        print(f"  Min: {min(ratios):.1f}  Max: {max(ratios):.1f}")
        if avg < 5:
            print("  WARNING: ratio looks wrong. total_persons may be "
                  "the wrong column.")
        for s in ratio_samples[:3]:
            print(f"    sa2={s[0]} year={s[1]}  u5={s[2]} total={s[3]} "
                  f"ratio={s[4]:.1f}")

    # ---- CHANGESET CSV ----------------------------------------------
    print(banner("CHANGESET"))
    write_changeset(rows)
    print(f"Changeset written to: {CHANGESET_PATH}")

    if not args.apply:
        print(banner("DRY-RUN COMPLETE"))
        print("No DB mutation. Review the sanity checks above.")
        print("If the data looks correct, re-run with --apply:")
        print("  python layer2_step6_apply.py --apply")
        return 0

    # =================================================================
    # APPLY MODE
    # =================================================================
    print(banner("BACKUP"))
    shutil.copy2(DB, BACKUP_PATH)
    print(f"OK: backed up to {BACKUP_PATH}")
    print(f"    size: {BACKUP_PATH.stat().st_size:,} bytes")

    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    try:
        print(banner("BEGIN TRANSACTION"))
        cur.execute("BEGIN TRANSACTION")

        # CREATE TABLE
        cur.execute("""
            CREATE TABLE IF NOT EXISTS abs_sa2_erp_annual (
                sa2_code   TEXT    NOT NULL,
                year       INTEGER NOT NULL,
                age_group  TEXT    NOT NULL,
                persons    INTEGER,
                PRIMARY KEY (sa2_code, year, age_group)
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS ix_erp_year "
                    "ON abs_sa2_erp_annual(year)")
        cur.execute("CREATE INDEX IF NOT EXISTS ix_erp_age "
                    "ON abs_sa2_erp_annual(age_group)")
        print("CREATE TABLE / INDEX: OK")

        # Pre-invariant
        cur.execute("SELECT COUNT(*) FROM abs_sa2_erp_annual")
        pre_count = cur.fetchone()[0]
        print(f"Pre-state: abs_sa2_erp_annual has {pre_count:,} rows")
        if pre_count > 0:
            print("ABORT: table is not empty.")
            conn.execute("ROLLBACK")
            return 1

        # INSERT
        print(banner("INSERT"))
        chunk_size = 1000
        inserted = 0
        for i in range(0, n_total, chunk_size):
            chunk = rows[i:i + chunk_size]
            cur.executemany(
                "INSERT INTO abs_sa2_erp_annual "
                "(sa2_code, year, age_group, persons) "
                "VALUES (?, ?, ?, ?)",
                chunk
            )
            inserted += len(chunk)
        print(f"Inserted {inserted:,} rows")

        # Post-invariant
        cur.execute("SELECT COUNT(*) FROM abs_sa2_erp_annual")
        post_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(DISTINCT sa2_code) "
                    "FROM abs_sa2_erp_annual")
        post_sa2 = cur.fetchone()[0]
        cur.execute("SELECT COUNT(DISTINCT year) "
                    "FROM abs_sa2_erp_annual")
        post_years = cur.fetchone()[0]
        cur.execute("SELECT COUNT(DISTINCT age_group) "
                    "FROM abs_sa2_erp_annual")
        post_age = cur.fetchone()[0]

        print(banner("POST-INVARIANTS"))
        print(f"  rows:           {post_count:,}")
        print(f"  distinct sa2:   {post_sa2:,}")
        print(f"  distinct years: {post_years:,}")
        print(f"  age groups:     {post_age:,}")

        if post_count != n_total:
            print(f"ABORT: post_count {post_count} != extracted {n_total}")
            conn.execute("ROLLBACK")
            return 1

        # ---- AUDIT LOG (real schema) --------------------------------
        print(banner("AUDIT LOG"))
        payload = {
            "rows_inserted": post_count,
            "distinct_sa2": post_sa2,
            "distinct_years": post_years,
            "years_list": distinct_years,
            "age_groups": distinct_age,
            "non_null_persons": n_nonnull,
            "null_persons": n_null,
            "source_file": WORKBOOK.name,
            "backup_path": BACKUP_PATH.name,
            "changeset_csv": CHANGESET_PATH.name,
            "column_map_resolved": col_map["columns"],
        }
        cur.execute("""
            INSERT INTO audit_log (
                actor, action, subject_type, subject_id,
                before_json, after_json, reason, occurred_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ACTOR,
            ACTION,
            SUBJECT_TYPE,
            SUBJECT_ID,
            json.dumps({"rows": pre_count}),
            json.dumps({"rows": post_count, "payload": payload}),
            "Layer 2 Step 6: ABS ERP at SA2 ingest (long format)",
            datetime.now().isoformat(),
        ))
        cur.execute("SELECT MAX(audit_id) FROM audit_log")
        new_audit_id = cur.fetchone()[0]
        print(f"audit_log row: id={new_audit_id} action='{ACTION}'")

        # ---- COMMIT -------------------------------------------------
        conn.commit()
        print(banner("COMMIT SUCCESSFUL"))
        print(f"  Rows in abs_sa2_erp_annual:  {post_count:,}")
        print(f"  Backup file:                 {BACKUP_PATH.name}")
        print(f"  Changeset CSV:               {CHANGESET_PATH.name}")
        print(f"  audit_id:                    {new_audit_id}")
        return 0

    except Exception as exc:
        print(banner(f"FAIL: {type(exc).__name__}"))
        print(str(exc))
        try:
            conn.execute("ROLLBACK")
            print("ROLLBACK successful - DB unchanged.")
        except Exception:
            pass
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
