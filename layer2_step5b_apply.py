"""
Layer 2 Step 5b APPLY v3 — Income Database SA2 socioeconomic ingest
─────────────────────────────────────────────────────────────────
v2 -> v3 changes:
  - Drop labour_force_participation_pct (col 54). Caught in v2 dry-run:
    column publishes "participation rate (%)" for AUST/State aggregate
    rows but a count metric (not pct) for SA2 rows under the same
    header. Mean of SA2 values was 3,146 (count), not 30-80% expected.
    See Decision 57 for methodology refinement.
  - 6 metrics (was 7).
  - LFP discovery deferred to Tier 2 (Education and Employment
    Database broader probe).

v1 -> v2 dropped female_jobs_count (0% SA2 coverage; AUST/State only).

Pattern matches Layer 2 steps 1, 2, 4, 5, 5c, 6:
  backup -> BEGIN -> CREATE TABLE -> ETL -> audit_log -> invariants -> COMMIT

Schema:
  abs_sa2_socioeconomic_annual (
    sa2_code     TEXT,
    year         INTEGER,
    metric_name  TEXT,
    value        REAL,
    PRIMARY KEY (sa2_code, year, metric_name)
  )

6 metrics ingested per (SA2, year) from Income Database.xlsx Table 1:

  median_equiv_household_income_weekly       col 11  Census-only ($, weekly)
  median_employee_income_annual              col 26  Annual ($)
  median_own_business_income_annual          col 32  Annual ($)
  median_investment_income_annual            col 38  Annual ($)
  median_superannuation_income_annual        col 44  Annual ($)
  median_total_income_excl_pensions_annual   col 50  Annual ($)

Census-only metrics: ~3 data points per SA2 (2011, 2016, 2021).
Annual metrics: ~7-9 data points per SA2 (2018-2024).
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
ABS = PROJECT_ROOT / "abs_data"
WORKBOOK = ABS / "Income Database.xlsx"
DB = PROJECT_ROOT / "data" / "kintell.db"
OUT_DIR = PROJECT_ROOT / "recon"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_PATH = PROJECT_ROOT / "data" / f"kintell.db.backup_pre_step5b_{TS}"
CHANGESET_PATH = OUT_DIR / f"layer2_step5b_changeset_{TS}.csv"

SHEET = "Table 1"
SA2_CODE_COL = 0
REGION_LABEL_COL = 1
YEAR_COL = 2
DATA_START_ROW = 8

# (col_index, metric_name, cadence)
METRIC_COLUMNS = [
    (11, "median_equiv_household_income_weekly", "census"),
    (26, "median_employee_income_annual", "annual"),
    (32, "median_own_business_income_annual", "annual"),
    (38, "median_investment_income_annual", "annual"),
    (44, "median_superannuation_income_annual", "annual"),
    (50, "median_total_income_excl_pensions_annual", "annual"),
]
CENSUS_YEARS = {2011, 2016, 2021}

NULL_MARKERS = {"-", "..", "np", "n.a.", "na", "NA", "NP", "—", ""}

ACTOR = "layer2_step5b_apply"
ACTION = "abs_sa2_socioeconomic_ingest_v1"
SUBJECT_TYPE = "abs_sa2_socioeconomic_annual"
SUBJECT_ID = 0


def banner(title: str) -> str:
    return f"\n{'-' * 70}\n{title}\n{'-' * 70}"


def to_number(v):
    if v is None:
        return None
    s = str(v).strip()
    if s in NULL_MARKERS:
        return None
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


def extract_rows() -> tuple[list, dict]:
    wb = openpyxl.load_workbook(WORKBOOK, read_only=True, data_only=True)
    ws = wb[SHEET]

    out = []
    seen_years = set()
    seen_sa2 = set()
    skipped_non_sa2 = 0
    skipped_no_year = 0

    for r_idx, row in enumerate(ws.iter_rows(values_only=True), start=1):
        if r_idx < DATA_START_ROW:
            continue
        if SA2_CODE_COL >= len(row):
            continue

        code_cell = row[SA2_CODE_COL]
        if code_cell is None:
            continue
        code = str(code_cell).strip()
        if not (code.isdigit() and len(code) == 9):
            skipped_non_sa2 += 1
            continue

        year_val = row[YEAR_COL] if YEAR_COL < len(row) else None
        year = to_number(year_val)
        if year is None:
            skipped_no_year += 1
            continue
        year = int(year)

        seen_sa2.add(code)
        seen_years.add(year)

        for col_idx, metric_name, _cadence in METRIC_COLUMNS:
            if col_idx >= len(row):
                continue
            val = to_number(row[col_idx])
            out.append((code, year, metric_name, val))

    wb.close()
    return out, {
        "distinct_sa2": len(seen_sa2),
        "years": sorted(seen_years),
        "skipped_non_sa2": skipped_non_sa2,
        "skipped_no_year": skipped_no_year,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true",
                        help="Mutate the DB. Without flag, dry-run only.")
    args = parser.parse_args()

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(banner(f"LAYER 2 STEP 5B v3 — SOCIOECONOMIC INGEST ({mode})"))
    print(f"Workbook:  {WORKBOOK}")
    print(f"DB:        {DB}")
    print(f"Timestamp: {TS}")

    if not DB.exists():
        print("FAIL: DB not found")
        return 1
    if not WORKBOOK.exists():
        print(f"FAIL: workbook not found at {WORKBOOK}")
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # ---- EXTRACT ---------------------------------------------------
    print(banner("EXTRACT"))
    t0 = time.time()
    rows, meta = extract_rows()
    elapsed = time.time() - t0

    n_total = len(rows)
    n_nonnull = sum(1 for r in rows if r[3] is not None)
    print(f"  Rows extracted:      {n_total:,}")
    print(f"  Non-null:            {n_nonnull:,}")
    print(f"  Distinct SA2:        {meta['distinct_sa2']:,}")
    print(f"  Years covered:       {meta['years']}")
    print(f"  Skipped (non-SA2):   {meta['skipped_non_sa2']:,}")
    print(f"  Extract time:        {elapsed:.1f}s")

    # Per-metric coverage
    print()
    print("Per-metric non-null coverage (cadence-aware):")
    print(f"  {'metric':50s}  {'cadence':10s}  {'expected':>9}  "
          f"{'non-null':>9}  {'pct':>6}")
    for col_idx, metric_name, cadence in METRIC_COLUMNS:
        if cadence == "census":
            relevant = [r for r in rows
                        if r[2] == metric_name and r[1] in CENSUS_YEARS]
        else:
            relevant = [r for r in rows if r[2] == metric_name]
        nn = sum(1 for r in relevant if r[3] is not None)
        total = len(relevant)
        pct = 100 * nn / total if total else 0
        print(f"  {metric_name:50s}  {cadence:10s}  "
              f"{total:>9,}  {nn:>9,}  {pct:>5.1f}%")

    # Sanity check 1: Census 2021 household income range
    print(banner("SANITY CHECK 1: median household income (Census 2021)"))
    target = "median_equiv_household_income_weekly"
    census_2021 = [r[3] for r in rows
                   if r[2] == target and r[1] == 2021
                   and r[3] is not None]
    if census_2021:
        avg = sum(census_2021) / len(census_2021)
        print(f"  2021 SA2 samples: n={len(census_2021):,} "
              f"min=${min(census_2021):.0f}  mean=${avg:.0f}  "
              f"max=${max(census_2021):.0f}")
        if 500 <= avg <= 3000:
            print(f"  PASS: mean ${avg:.0f}/week is in expected range")
        else:
            print(f"  WARN: mean ${avg:.0f} outside expected $500-$3000")

    # Sanity check 2: median employee income, latest year
    print(banner("SANITY CHECK 2: median employee income (latest year)"))
    target = "median_employee_income_annual"
    by_year = {}
    for r in rows:
        if r[2] == target and r[3] is not None:
            by_year.setdefault(r[1], []).append(r[3])
    if by_year:
        latest_year = max(by_year.keys())
        vals = by_year[latest_year]
        avg = sum(vals) / len(vals)
        print(f"  {latest_year} SA2 samples: n={len(vals):,} "
              f"min=${min(vals):.0f}  mean=${avg:.0f}  "
              f"max=${max(vals):.0f}")
        if 35000 <= avg <= 90000:
            print(f"  PASS: mean ${avg:.0f}/year in expected range")
        else:
            print(f"  WARN: mean ${avg:.0f}/year outside $35K-$90K")

    # Sanity check 3: Census 2021 household income, growth check
    print(banner("SANITY CHECK 3: Census household income growth 2011->2021"))
    by_year = {}
    target = "median_equiv_household_income_weekly"
    for r in rows:
        if r[2] == target and r[3] is not None and r[1] in (2011, 2021):
            by_year.setdefault(r[1], {})[r[0]] = r[3]
    if 2011 in by_year and 2021 in by_year:
        common_sa2 = (set(by_year[2011].keys()) & set(by_year[2021].keys()))
        if common_sa2:
            growth = []
            for sa2 in common_sa2:
                v11, v21 = by_year[2011][sa2], by_year[2021][sa2]
                if v11 > 0:
                    growth.append((v21 - v11) / v11 * 100)
            if growth:
                avg_g = sum(growth) / len(growth)
                print(f"  Common SA2s: {len(common_sa2):,}")
                print(f"  Growth 2011->2021: mean {avg_g:.1f}%")
                if 30 <= avg_g <= 80:
                    print(f"  PASS: 10-year growth in plausible range")
                else:
                    print(f"  WARN: growth {avg_g:.1f}% unusual "
                          f"(expected 30-80% over 10 years)")

    # Sample
    print(banner("SAMPLE — Braidwood (sa2=101021007), non-null only"))
    sample = [r for r in rows if r[0] == "101021007" and r[3] is not None]
    print(f"  {len(sample)} non-null rows")
    for r in sample:
        print(f"    year={r[1]}  metric={r[2]:50s}  value={r[3]}")

    # Changeset
    print(banner("CHANGESET"))
    with open(CHANGESET_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["sa2_code", "year", "metric_name", "value"])
        w.writerows(rows)
    print(f"Changeset written: {CHANGESET_PATH}")

    if not args.apply:
        print(banner("DRY-RUN COMPLETE"))
        print("No DB mutation. Review sanity checks above.")
        print("Re-run with --apply when ready:")
        print("  python layer2_step5b_apply.py --apply")
        return 0

    # ================================================================
    # APPLY MODE
    # ================================================================
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

        cur.execute("""
            CREATE TABLE IF NOT EXISTS abs_sa2_socioeconomic_annual (
                sa2_code     TEXT NOT NULL,
                year         INTEGER NOT NULL,
                metric_name  TEXT NOT NULL,
                value        REAL,
                PRIMARY KEY (sa2_code, year, metric_name)
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS ix_socio_metric "
                    "ON abs_sa2_socioeconomic_annual(metric_name)")
        cur.execute("CREATE INDEX IF NOT EXISTS ix_socio_year "
                    "ON abs_sa2_socioeconomic_annual(year)")
        print("CREATE TABLE / INDEXES: OK")

        cur.execute("SELECT COUNT(*) FROM abs_sa2_socioeconomic_annual")
        pre_count = cur.fetchone()[0]
        print(f"Pre-state: {pre_count:,} rows")
        if pre_count > 0:
            print("ABORT: table is not empty.")
            conn.execute("ROLLBACK")
            return 1

        # INSERT chunked
        print(banner("INSERT"))
        chunk_size = 1000
        inserted = 0
        for i in range(0, n_total, chunk_size):
            chunk = rows[i:i + chunk_size]
            cur.executemany(
                "INSERT INTO abs_sa2_socioeconomic_annual "
                "(sa2_code, year, metric_name, value) "
                "VALUES (?, ?, ?, ?)",
                chunk
            )
            inserted += len(chunk)
        print(f"Inserted {inserted:,} rows")

        cur.execute("SELECT COUNT(*) FROM abs_sa2_socioeconomic_annual")
        post_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(DISTINCT sa2_code) "
                    "FROM abs_sa2_socioeconomic_annual")
        post_sa2 = cur.fetchone()[0]
        cur.execute("SELECT COUNT(DISTINCT metric_name) "
                    "FROM abs_sa2_socioeconomic_annual")
        post_metrics = cur.fetchone()[0]

        print(banner("POST-INVARIANTS"))
        print(f"  rows:             {post_count:,}")
        print(f"  distinct sa2:     {post_sa2:,}")
        print(f"  distinct metrics: {post_metrics}")

        if post_count != n_total:
            print(f"ABORT: post_count {post_count} != extracted {n_total}")
            conn.execute("ROLLBACK")
            return 1
        if post_metrics != len(METRIC_COLUMNS):
            print(f"ABORT: post_metrics {post_metrics} != "
                  f"expected {len(METRIC_COLUMNS)}")
            conn.execute("ROLLBACK")
            return 1

        # Audit log
        print(banner("AUDIT LOG"))
        payload = {
            "rows_inserted": post_count,
            "distinct_sa2": post_sa2,
            "metrics_count": post_metrics,
            "metric_names": [m for _, m, _ in METRIC_COLUMNS],
            "metric_cadence": {m: c for _, m, c in METRIC_COLUMNS},
            "years_list": meta["years"],
            "non_null_total": n_nonnull,
            "source_file": WORKBOOK.name,
            "source_sheet": SHEET,
            "backup_path": BACKUP_PATH.name,
            "changeset_csv": CHANGESET_PATH.name,
        }
        cur.execute("""
            INSERT INTO audit_log (
                actor, action, subject_type, subject_id,
                before_json, after_json, reason, occurred_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ACTOR, ACTION, SUBJECT_TYPE, SUBJECT_ID,
            json.dumps({"rows": pre_count}),
            json.dumps({"rows": post_count, "payload": payload}),
            "Layer 2 Step 5b: SA2 socioeconomic time series "
            "(6 income metrics, mixed annual + Census cadence)",
            datetime.now().isoformat(),
        ))
        cur.execute("SELECT MAX(audit_id) FROM audit_log")
        new_audit_id = cur.fetchone()[0]
        print(f"audit_log row: id={new_audit_id} action='{ACTION}'")

        conn.commit()
        print(banner("COMMIT SUCCESSFUL"))
        print(f"  Rows in abs_sa2_socioeconomic_annual: {post_count:,}")
        print(f"  Backup file:    {BACKUP_PATH.name}")
        print(f"  Changeset CSV:  {CHANGESET_PATH.name}")
        print(f"  audit_id:       {new_audit_id}")
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
