"""
Layer 2 Step 5b-prime — Apply v3.
==================================
Ingests SA2-level education + employment metrics from two sources into
a new table `abs_sa2_education_employment_annual` (long format):

  1. ABS Data by Region "Education and employment database.xlsx"
     - 9 core education + employment metrics
     - 7 RWCI-input metrics (occupation knowledge mix + industry
       knowledge sectors)
  2. Census 2021 TSP T33 derived rates (6 sex-disaggregated)

v3 adds 7 RWCI-input metrics (col 72/73/75/76 industry knowledge
sectors + col 83/84/87 occupation knowledge mix). RWCI itself is
derived downstream — no schema change.

v2 fix retained: tolerant pct invariants. ABS confidentialization
randomly perturbs small cell counts, so rates can exceed 100% in
low-population SA2s. AVG-based plausibility check is the real gate.

Usage:
  python layer2_step5b_prime_apply.py             # dry-run (default)
  python layer2_step5b_prime_apply.py --apply     # commits to DB
"""

import argparse
import csv
import json
import re
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

import openpyxl


# --- Paths ----------------------------------------------------------------

DB_PATH = Path("data/kintell.db")
EE_WB   = Path("abs_data/Education and employment database.xlsx")
T33_CSV = Path("recon/layer2_step5b_prime_t33_derived.csv")

TABLE  = "abs_sa2_education_employment_annual"
ACTOR  = "layer2_step5b_prime_apply"
ACTION = "abs_sa2_education_employment_ingest_v1"


# --- Metric definitions ---------------------------------------------------

# (col_index_1based, metric_name, cadence, kind)
EE_METRICS = [
    # Core education + employment
    (4,  "ee_preschool_4yo_count",                  "annual", "count"),
    (9,  "ee_preschool_total_count",                "annual", "count"),
    (11, "ee_preschool_15h_plus_count",             "annual", "count"),
    (12, "ee_year12_completion_pct",                "census", "pct"),
    (22, "ee_bachelor_degree_pct",                  "census", "pct"),
    (54, "ee_unemployment_rate_persons_pct",        "census", "pct"),
    (55, "ee_lfp_persons_pct",                      "census", "pct"),
    (60, "ee_jobs_females_count",                   "annual", "count"),
    (62, "ee_jobs_total_count",                     "annual", "count"),
    # RWCI inputs — occupation knowledge mix (Census)
    (83, "ee_managers_pct",                         "census", "pct"),
    (84, "ee_professionals_pct",                    "census", "pct"),
    (87, "ee_clerical_admin_pct",                   "census", "pct"),
    # RWCI inputs — industry knowledge sectors (annual jobs counts)
    (72, "ee_jobs_info_media_count",                "annual", "count"),
    (73, "ee_jobs_finance_count",                   "annual", "count"),
    (75, "ee_jobs_professional_scientific_count",   "annual", "count"),
    (76, "ee_jobs_admin_support_count",             "annual", "count"),
]

# T33 derived: only ingest females + males (persons covered by EE DB col 54/55)
T33_DERIVED = [
    ("F", "lfp_rate_pct",   "census_lfp_females_pct"),
    ("F", "unemp_rate_pct", "census_unemp_females_pct"),
    ("F", "emp_to_pop_pct", "census_emp_to_pop_females_pct"),
    ("M", "lfp_rate_pct",   "census_lfp_males_pct"),
    ("M", "unemp_rate_pct", "census_unemp_males_pct"),
    ("M", "emp_to_pop_pct", "census_emp_to_pop_males_pct"),
]

ALL_METRICS    = [m[1] for m in EE_METRICS] + [d[2] for d in T33_DERIVED]
CENSUS_METRICS = [m[1] for m in EE_METRICS if m[2] == "census"] + [d[2] for d in T33_DERIVED]
ANNUAL_METRICS = [m[1] for m in EE_METRICS if m[2] == "annual"]
PCT_METRICS    = [m[1] for m in EE_METRICS if m[3] == "pct"] + [d[2] for d in T33_DERIVED]
COUNT_METRICS  = [m[1] for m in EE_METRICS if m[3] == "count"]

# Per-metric expected AVG ranges (national plausibility check).
PCT_AVG_RANGES = {
    "ee_year12_completion_pct":          (35, 75),
    "ee_bachelor_degree_pct":            (5, 30),
    "ee_unemployment_rate_persons_pct":  (2, 12),
    "ee_lfp_persons_pct":                (50, 75),
    "ee_managers_pct":                   (8, 25),
    "ee_professionals_pct":              (15, 40),
    "ee_clerical_admin_pct":             (8, 20),
    "census_lfp_females_pct":            (50, 70),
    "census_lfp_males_pct":              (60, 80),
    "census_unemp_females_pct":          (2, 12),
    "census_unemp_males_pct":            (2, 12),
    "census_emp_to_pop_females_pct":     (45, 70),
    "census_emp_to_pop_males_pct":       (55, 80),
}

OUTLIER_FAIL_THRESHOLD_PCT = 5.0

SA2_CODE_RE = re.compile(r"^\d{9}$")


# --- Backup ---------------------------------------------------------------

def take_backup(db_path):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = db_path.parent / f"{db_path.name}.backup_pre_step5b_prime_{ts}"
    print(f"[backup] copying {db_path} -> {backup}")
    shutil.copy2(db_path, backup)
    print(f"  backup size: {backup.stat().st_size:,} bytes")
    return backup


# --- Read EE Database -----------------------------------------------------

def read_ee_database():
    print(f"[read EE] {EE_WB}")
    wb = openpyxl.load_workbook(EE_WB, read_only=True, data_only=True)
    ws = wb["Table 1"]
    rows = []
    for r_idx, row in enumerate(ws.iter_rows(min_row=8, values_only=True), start=8):
        if not row or len(row) < 3:
            continue
        code = row[0]
        year = row[2]
        if code is None or year is None or not isinstance(year, int):
            continue
        s = str(code).strip()
        if not SA2_CODE_RE.match(s):
            continue
        for (col_idx, metric_name, _cad, _kind) in EE_METRICS:
            if col_idx - 1 >= len(row):
                continue
            v = row[col_idx - 1]
            if v is None or v == "" or v == "-":
                continue
            if isinstance(v, (int, float)):
                val = float(v)
            else:
                try:
                    val = float(str(v).replace(",", ""))
                except (ValueError, TypeError):
                    continue
            rows.append((s, year, metric_name, val))
        if r_idx % 5000 == 0:
            print(f"  scanned to row {r_idx}, captured {len(rows):,}")
    wb.close()
    print(f"  EE rows captured: {len(rows):,}")
    return rows


# --- Read T33 derived CSV -------------------------------------------------

def read_t33_derived():
    print(f"[read T33] {T33_CSV}")
    rows = []
    skipped_none = 0
    with open(T33_CSV, "r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            sa2 = row["sa2_code"].strip()
            if not SA2_CODE_RE.match(sa2):
                continue
            try:
                year = int(row["year"])
            except (ValueError, TypeError):
                continue
            sex = row["sex"]
            for (sx, csv_col, metric_name) in T33_DERIVED:
                if sx != sex:
                    continue
                v = (row.get(csv_col) or "").strip()
                if v in ("", "None"):
                    skipped_none += 1
                    continue
                try:
                    val = float(v)
                except ValueError:
                    continue
                rows.append((sa2, year, metric_name, val))
    print(f"  T33 rows captured: {len(rows):,}, skipped (None/empty): {skipped_none:,}")
    return rows


# --- Per-metric summary --------------------------------------------------

def report_per_metric(conn):
    cur = conn.cursor()
    cur.execute(f"""
        SELECT metric_name,
               COUNT(*) AS n,
               MIN(value), MAX(value), AVG(value),
               COUNT(DISTINCT sa2_code) AS sa2s,
               COUNT(DISTINCT year)     AS yrs,
               SUM(CASE WHEN value > 100 THEN 1 ELSE 0 END) AS gt100,
               SUM(CASE WHEN value <   0 THEN 1 ELSE 0 END) AS lt0
        FROM {TABLE}
        GROUP BY metric_name
        ORDER BY metric_name
    """)
    rows = cur.fetchall()
    print(f"\n  Per-metric summary:")
    print(f"  {'metric':<44}{'rows':>9}{'sa2s':>7}{'yrs':>5}{'min':>9}{'max':>10}"
          f"{'avg':>9}{'>100':>7}{'<0':>5}")
    print(f"  {'-'*44}{'-'*9}{'-'*7}{'-'*5}{'-'*9}{'-'*10}{'-'*9}{'-'*7}{'-'*5}")
    for (name, n, vmin, vmax, vavg, sa2s, yrs, gt100, lt0) in rows:
        print(f"  {name:<44}{n:>9,}{sa2s:>7,}{yrs:>5}{vmin:>9.2f}{vmax:>10.2f}"
              f"{vavg:>9.2f}{gt100:>7,}{lt0:>5,}")
    return rows


# --- Invariants ----------------------------------------------------------

def check_invariants(conn):
    errors = []
    warnings = []
    cur = conn.cursor()

    cur.execute(f"SELECT COUNT(*) FROM {TABLE}")
    total = cur.fetchone()[0]
    if total < 100_000:
        errors.append(f"total rows {total:,} < 100,000 floor")
    if total > 300_000:
        errors.append(f"total rows {total:,} > 300,000 ceiling")

    cur.execute(f"SELECT metric_name FROM {TABLE} GROUP BY metric_name")
    found = {r[0] for r in cur.fetchall()}
    missing = set(ALL_METRICS) - found
    if missing:
        errors.append(f"missing metrics: {sorted(missing)}")
    extra = found - set(ALL_METRICS)
    if extra:
        errors.append(f"unexpected metrics: {sorted(extra)}")

    for name in CENSUS_METRICS:
        cur.execute(f"SELECT DISTINCT year FROM {TABLE} WHERE metric_name=?", (name,))
        yrs = {r[0] for r in cur.fetchall()}
        outside = yrs - {2011, 2016, 2021}
        if outside:
            errors.append(f"census metric {name}: years outside [2011,2016,2021]: {sorted(outside)}")

    for name in ANNUAL_METRICS:
        cur.execute(f"SELECT MIN(year), MAX(year) FROM {TABLE} WHERE metric_name=?", (name,))
        ymin, ymax = cur.fetchone()
        if ymin is not None and (ymin < 2017 or ymax > 2026):
            errors.append(f"annual metric {name}: year range [{ymin},{ymax}] outside [2017,2026]")

    for name in PCT_METRICS:
        cur.execute(f"""
            SELECT AVG(value), COUNT(*),
                   SUM(CASE WHEN value > 100 THEN 1 ELSE 0 END),
                   SUM(CASE WHEN value <   0 THEN 1 ELSE 0 END)
            FROM {TABLE} WHERE metric_name = ?
        """, (name,))
        avg, n, gt100, lt0 = cur.fetchone()
        if n == 0 or avg is None:
            continue

        rng = PCT_AVG_RANGES.get(name)
        if rng:
            lo, hi = rng
            if avg < lo or avg > hi:
                errors.append(
                    f"pct metric {name}: AVG {avg:.2f} outside expected [{lo}, {hi}]"
                )

        outliers = (gt100 or 0) + (lt0 or 0)
        outlier_pct = 100.0 * outliers / n
        if outlier_pct > OUTLIER_FAIL_THRESHOLD_PCT:
            errors.append(
                f"pct metric {name}: {outlier_pct:.1f}% rows outside [0,100] "
                f"(threshold {OUTLIER_FAIL_THRESHOLD_PCT}%) — systemic issue"
            )
        elif outliers > 0:
            warnings.append(
                f"pct metric {name}: {outliers} rows outside [0,100] "
                f"({outlier_pct:.2f}% — within ABS confidentialization tolerance)"
            )

        cur.execute(f"SELECT MAX(value) FROM {TABLE} WHERE metric_name = ?", (name,))
        vmax = cur.fetchone()[0]
        if vmax is not None and vmax > 500:
            errors.append(f"pct metric {name}: max {vmax} > 500 (egregious)")

    for name in COUNT_METRICS:
        cur.execute(f"SELECT MIN(value) FROM {TABLE} WHERE metric_name=?", (name,))
        row = cur.fetchone()
        if row[0] is not None and row[0] < 0:
            errors.append(f"count metric {name}: negative min {row[0]}")

    cur.execute(f"SELECT COUNT(DISTINCT sa2_code) FROM {TABLE}")
    distinct_sa2 = cur.fetchone()[0]
    if distinct_sa2 < 2_300:
        errors.append(f"distinct SA2 codes {distinct_sa2} < 2300 floor")

    cur.execute(
        f"SELECT COUNT(*) FROM {TABLE} "
        f"WHERE LENGTH(sa2_code) != 9 OR sa2_code GLOB '*[^0-9]*'"
    )
    bad = cur.fetchone()[0]
    if bad > 0:
        errors.append(f"{bad} rows have malformed SA2 codes")

    return errors, warnings, total, distinct_sa2


# --- Main -----------------------------------------------------------------

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--apply", action="store_true",
                   help="Commit changes (default: dry-run)")
    args = p.parse_args()

    for label, pth in [("DB", DB_PATH), ("EE Database", EE_WB), ("T33 derived", T33_CSV)]:
        if not pth.exists():
            print(f"ERROR: {label} not found at {pth}")
            sys.exit(1)

    mode = "APPLY" if args.apply else "DRY-RUN"
    print("=" * 60)
    print(f"  Layer 2 Step 5b-prime — {mode} (v3 with RWCI inputs)")
    print("=" * 60)

    backup_path = take_backup(DB_PATH) if args.apply else None

    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("BEGIN IMMEDIATE")

    try:
        print("\n[schema]")
        conn.execute(f"DROP TABLE IF EXISTS {TABLE}")
        conn.execute(f"""
            CREATE TABLE {TABLE} (
                sa2_code    TEXT    NOT NULL,
                year        INTEGER NOT NULL,
                metric_name TEXT    NOT NULL,
                value       REAL,
                PRIMARY KEY (sa2_code, year, metric_name)
            )
        """)
        conn.execute(f"CREATE INDEX idx_abs_sa2_ee_metric ON {TABLE}(metric_name)")
        conn.execute(f"CREATE INDEX idx_abs_sa2_ee_year ON {TABLE}(year)")
        print(f"  Created {TABLE} (+ 2 indexes)")

        print()
        ee_rows = read_ee_database()
        t33_rows = read_t33_derived()

        print("\n[insert]")
        all_rows = ee_rows + t33_rows
        print(f"  inserting {len(all_rows):,} rows...")
        conn.executemany(
            f"INSERT INTO {TABLE} (sa2_code, year, metric_name, value) VALUES (?,?,?,?)",
            all_rows,
        )

        report_per_metric(conn)

        print("\n[invariants]")
        errors, warnings, total, distinct_sa2 = check_invariants(conn)
        if warnings:
            print(f"  WARNINGS ({len(warnings)}, non-fatal):")
            for w in warnings:
                print(f"    - {w}")
        if errors:
            print(f"  FAILED ({len(errors)}):")
            for e in errors:
                print(f"    - {e}")
            raise RuntimeError(f"{len(errors)} invariant failures")
        print(f"  OK. total={total:,}, distinct_sa2={distinct_sa2:,}")

        if args.apply:
            annual_years = {}
            for sa2, year, metric, val in all_rows:
                if metric in ANNUAL_METRICS:
                    annual_years.setdefault(metric, set()).add(year)
            annual_years = {k: sorted(v) for k, v in annual_years.items()}

            rwci_input_metrics = [
                "ee_managers_pct", "ee_professionals_pct", "ee_clerical_admin_pct",
                "ee_jobs_info_media_count", "ee_jobs_finance_count",
                "ee_jobs_professional_scientific_count", "ee_jobs_admin_support_count",
            ]
            payload = {
                "rows": total,
                "rows_ee": len(ee_rows),
                "rows_t33_derived": len(t33_rows),
                "distinct_sa2": distinct_sa2,
                "metrics_count": len(ALL_METRICS),
                "metric_names": ALL_METRICS,
                "rwci_input_metrics": rwci_input_metrics,
                "ee_workbook": str(EE_WB),
                "t33_csv": str(T33_CSV),
                "backup": str(backup_path) if backup_path else None,
                "format": "long (sa2_code, year, metric_name, value)",
                "census_years": [2011, 2016, 2021],
                "annual_years_per_metric": annual_years,
                "abs_confidentialization_note": (
                    "Pct values may exceed 100 in low-population SA2s due to "
                    "ABS independent perturbation of cell counts. Means and "
                    "national aggregates remain accurate. Downstream consumers "
                    "should use stratified percentile cohorts (Decision 54) "
                    "and may need to filter implausible values for display."
                ),
                "rwci_note": (
                    "RWCI (Remote Work Capacity Index) is a behavioural modifier "
                    "computed downstream from occupation knowledge mix "
                    "(managers + professionals + clerical %) and industry "
                    "knowledge sectors (info_media + finance + prof_sci + "
                    "admin_support / total_jobs). Banded within state x "
                    "remoteness cohort per Decision 54."
                ),
            }
            after_json = json.dumps({"rows": total, "payload": payload})
            reason = (
                "Phase 2.5 Layer 2 Step 5b-prime: SA2 education + employment "
                "time series. 16 metrics from ABS Data by Region "
                "Education and Employment Database (preschool counts; Year 12 + "
                "Bachelor %; persons unemployment rate + LFP %; jobs counts; "
                "RWCI inputs: managers/professionals/clerical %, plus knowledge-"
                "sector industry job counts) + 6 sex-disaggregated labour force "
                "rates derived from Census 2021 TSP T33 (female + male LFP, "
                "unemployment, employment-to-pop for 2011/2016/2021). Recovers "
                "LFP-persons signal (deferred from Step 5b due to Decision 57), "
                "adds female LFP coverage, and lays groundwork for RWCI "
                "behavioural modifier in centre-page demand stability commentary."
            )
            conn.execute("""
                INSERT INTO audit_log
                  (actor, action, subject_type, subject_id,
                   before_json, after_json, reason, occurred_at)
                VALUES (?, ?, ?, 0, ?, ?, ?, ?)
            """, (
                ACTOR, ACTION, TABLE,
                json.dumps({"rows": 0}),
                after_json,
                reason,
                datetime.utcnow().isoformat(),
            ))
            print(f"\n[audit_log] inserted action '{ACTION}'")

        if args.apply:
            conn.commit()
            print("\n=== COMMITTED ===")
            print(f"  table:  {TABLE}")
            print(f"  rows:   {total:,}")
            print(f"  backup: {backup_path}")
        else:
            conn.rollback()
            print("\n=== DRY-RUN COMPLETE (rolled back) ===")
            print("  Re-run with --apply to commit.")

    except Exception as e:
        conn.rollback()
        print(f"\n!!! ROLLBACK: {e}")
        if args.apply and backup_path:
            print(f"DB unchanged. Backup retained at: {backup_path}")
        sys.exit(2)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
