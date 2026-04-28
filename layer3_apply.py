"""
layer3_apply.py

Layer 3: compute within-cohort percentile/decile/band for each
(metric x SA2 x latest-year) tuple and write to
layer3_sa2_metric_banding.

Reads:
  - sa2_cohort (cohort lookup, built by sa2_cohort_apply.py)
  - abs_sa2_erp_annual
  - abs_sa2_births_annual
  - abs_sa2_socioeconomic_annual
  - abs_sa2_education_employment_annual
  - abs_sa2_unemployment_quarterly

Writes:
  layer3_sa2_metric_banding (
    sa2_code     TEXT NOT NULL,
    metric       TEXT NOT NULL,
    year         INTEGER NOT NULL,
    period_label TEXT,             -- e.g. '2025-Q4' for quarterly
    cohort_def   TEXT NOT NULL,    -- 'state'|'remoteness'|'state_x_remoteness'
    cohort_key   TEXT,             -- e.g. '1' (state) or '1_2' (state_x_rem)
    cohort_n     INTEGER,          -- size of cohort used to compute rank
    raw_value    REAL,
    percentile   REAL,             -- 0..100
    decile       INTEGER,          -- 1..10
    band         TEXT,             -- 'low'|'mid'|'high'
    PRIMARY KEY (sa2_code, metric, year, cohort_def)
  )

Banding cutoffs (locked, per layer3_decisions D2):
  low  = decile 1..3
  mid  = decile 4..6
  high = decile 7..10

Modes:
  --dry-run   compute, validate, write recon md. NO DB writes.
  --apply     full mutation: backup -> transaction -> audit_log

Standards:
  -  8 : timestamped backup before mutation
  - 30 : hardcoded audit_log INSERT

Usage:
  python layer3_apply.py --dry-run
  python layer3_apply.py --apply
"""
import argparse
import shutil
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
DB_PATH = REPO_ROOT / "data" / "kintell.db"
DRYRUN_OUT = REPO_ROOT / "recon" / "layer3_apply_dryrun.md"
APPLY_OUT = REPO_ROOT / "recon" / "layer3_apply.md"

MIN_COHORT_COVERAGE = 500


# Metric registry: each metric defines its source, filter, default cohort.
METRICS = [
    {
        "canonical": "sa2_under5_count",
        "source_table": "abs_sa2_erp_annual",
        "value_column": "persons",
        "filter_clause": "age_group = 'under_5_persons'",
        "year_column": "year",
        "cohort_def": "state",
    },
    {
        "canonical": "sa2_total_population",
        "source_table": "abs_sa2_erp_annual",
        "value_column": "persons",
        "filter_clause": "age_group = 'total_persons'",
        "year_column": "year",
        "cohort_def": "state_x_remoteness",
    },
    {
        "canonical": "sa2_births_count",
        "source_table": "abs_sa2_births_annual",
        "value_column": "births_count",
        "filter_clause": None,
        "year_column": "year",
        "cohort_def": "state_x_remoteness",
    },
    {
        "canonical": "sa2_unemployment_rate",
        "source_table": "abs_sa2_unemployment_quarterly",
        "value_column": "rate",
        "filter_clause": None,
        "year_column": "year_qtr",   # text 'YYYY-Qn'
        "cohort_def": "state",
        "is_quarterly": True,
    },
    {
        "canonical": "sa2_median_employee_income",
        "source_table": "abs_sa2_socioeconomic_annual",
        "value_column": "value",
        "filter_clause": "metric_name = 'median_employee_income_annual'",
        "year_column": "year",
        "cohort_def": "remoteness",
    },
    {
        "canonical": "sa2_median_household_income",
        "source_table": "abs_sa2_socioeconomic_annual",
        "value_column": "value",
        "filter_clause": "metric_name = 'median_equiv_household_income_weekly'",
        "year_column": "year",
        "cohort_def": "remoteness",
    },
    {
        "canonical": "sa2_median_total_income",
        "source_table": "abs_sa2_socioeconomic_annual",
        "value_column": "value",
        "filter_clause": "metric_name = 'median_total_income_excl_pensions_annual'",
        "year_column": "year",
        "cohort_def": "remoteness",
    },
    {
        "canonical": "sa2_lfp_persons",
        "source_table": "abs_sa2_education_employment_annual",
        "value_column": "value",
        "filter_clause": "metric_name = 'ee_lfp_persons_pct'",
        "year_column": "year",
        "cohort_def": "state_x_remoteness",
    },
    {
        "canonical": "sa2_lfp_females",
        "source_table": "abs_sa2_education_employment_annual",
        "value_column": "value",
        "filter_clause": "metric_name = 'census_lfp_females_pct'",
        "year_column": "year",
        "cohort_def": "state_x_remoteness",
    },
    {
        "canonical": "sa2_lfp_males",
        "source_table": "abs_sa2_education_employment_annual",
        "value_column": "value",
        "filter_clause": "metric_name = 'census_lfp_males_pct'",
        "year_column": "year",
        "cohort_def": "state_x_remoteness",
    },
]


# --------------------------------------------------------------------
# Cohort lookup
# --------------------------------------------------------------------

def load_cohort_lookup(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT sa2_code, state_code, state_name, ra_code, ra_name, ra_band
          FROM sa2_cohort
    """)
    lookup = {}
    for sa2, sc, sn, rc, rn, rb in cur.fetchall():
        lookup[sa2] = {
            "state_code": sc,
            "state_name": sn,
            "ra_code": rc,
            "ra_name": rn,
            "ra_band": rb,
        }
    return lookup


def build_cohort_key(cohort_row, cohort_def):
    if cohort_def == "national":
        return "AU"
    if cohort_def == "state":
        return cohort_row["state_code"]
    if cohort_def == "remoteness":
        rb = cohort_row["ra_band"]
        return str(rb) if rb is not None else None
    if cohort_def == "state_x_remoteness":
        if cohort_row["state_code"] and cohort_row["ra_band"] is not None:
            return f"{cohort_row['state_code']}_{cohort_row['ra_band']}"
        return None
    raise ValueError(f"unknown cohort_def: {cohort_def}")


# --------------------------------------------------------------------
# Year selection per metric
# --------------------------------------------------------------------

def pick_latest_period(conn, metric):
    cur = conn.cursor()
    table = metric["source_table"]
    val_col = metric["value_column"]
    yr_col = metric["year_column"]
    filter_clause = metric.get("filter_clause") or ""
    extra = f"AND {filter_clause}" if filter_clause else ""

    cur.execute(f"""
        SELECT {yr_col}, COUNT(DISTINCT sa2_code) AS n
          FROM {table}
         WHERE {val_col} IS NOT NULL
           {extra}
      GROUP BY {yr_col}
      ORDER BY {yr_col} DESC
    """)
    rows = cur.fetchall()
    if not rows:
        return None, 0

    # First row meeting the coverage floor; otherwise the most-populated row
    for period, n in rows:
        if n >= MIN_COHORT_COVERAGE:
            return period, n
    period, n = max(rows, key=lambda x: x[1])
    return period, n


# --------------------------------------------------------------------
# Per-metric banding
# --------------------------------------------------------------------

def compute_banding_for_metric(conn, metric, cohort_lookup):
    period, coverage = pick_latest_period(conn, metric)
    if period is None:
        return [], {
            "metric": metric["canonical"],
            "period": None,
            "coverage": 0,
            "rows_emitted": 0,
            "cohort_sizes": [],
            "skipped_no_cohort": 0,
        }

    cur = conn.cursor()
    table = metric["source_table"]
    val_col = metric["value_column"]
    yr_col = metric["year_column"]
    filter_clause = metric.get("filter_clause") or ""
    extra = f"AND {filter_clause}" if filter_clause else ""

    cur.execute(f"""
        SELECT sa2_code, {val_col}
          FROM {table}
         WHERE {yr_col} = ?
           AND {val_col} IS NOT NULL
           {extra}
    """, (period,))
    sa2_values = cur.fetchall()

    cohort_def = metric["cohort_def"]
    is_quarterly = metric.get("is_quarterly", False)

    # Year + period_label
    if is_quarterly:
        year = int(str(period).split("-")[0])
        period_label = str(period)
    else:
        year = int(period)
        period_label = None

    # Bucket by cohort_key
    by_cohort = defaultdict(list)
    skipped_no_cohort = 0
    for sa2, val in sa2_values:
        coh = cohort_lookup.get(sa2)
        if coh is None:
            skipped_no_cohort += 1
            continue
        key = build_cohort_key(coh, cohort_def)
        if key is None:
            skipped_no_cohort += 1
            continue
        by_cohort[key].append((sa2, float(val)))

    rows = []
    cohort_sizes = []
    for cohort_key, items in by_cohort.items():
        items.sort(key=lambda x: x[1])
        n = len(items)
        cohort_sizes.append((cohort_key, n))
        for rank0, (sa2, val) in enumerate(items):
            # mid-rank percentile -- avoids 0 and 100 endpoints
            percentile = (rank0 + 0.5) / n * 100.0
            decile = min(10, int(rank0 / n * 10) + 1)
            if decile <= 3:
                band = "low"
            elif decile <= 6:
                band = "mid"
            else:
                band = "high"
            rows.append({
                "sa2_code": sa2,
                "metric": metric["canonical"],
                "year": year,
                "period_label": period_label,
                "cohort_def": cohort_def,
                "cohort_key": cohort_key,
                "cohort_n": n,
                "raw_value": val,
                "percentile": round(percentile, 4),
                "decile": decile,
                "band": band,
            })

    return rows, {
        "metric": metric["canonical"],
        "period": period,
        "coverage": coverage,
        "rows_emitted": len(rows),
        "cohort_sizes": cohort_sizes,
        "skipped_no_cohort": skipped_no_cohort,
    }


# --------------------------------------------------------------------
# Apply
# --------------------------------------------------------------------

def apply_layer3(rows):
    print("APPLY mode: backup -> transaction -> audit_log", flush=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = (REPO_ROOT / "data" /
                   f"kintell.db.backup_pre_layer3_{timestamp}")
    print(f"  backup -> {backup_path.name} ...")
    shutil.copy2(DB_PATH, backup_path)
    backup_size_mb = backup_path.stat().st_size / (1024 * 1024)
    print(f"  backup ok ({backup_size_mb:.1f} MB)")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("BEGIN")

        cur.execute("DROP TABLE IF EXISTS layer3_sa2_metric_banding")
        cur.execute("""
            CREATE TABLE layer3_sa2_metric_banding (
                sa2_code     TEXT NOT NULL,
                metric       TEXT NOT NULL,
                year         INTEGER NOT NULL,
                period_label TEXT,
                cohort_def   TEXT NOT NULL,
                cohort_key   TEXT,
                cohort_n     INTEGER,
                raw_value    REAL,
                percentile   REAL,
                decile       INTEGER,
                band         TEXT,
                PRIMARY KEY (sa2_code, metric, year, cohort_def)
            )
        """)
        cur.execute("CREATE INDEX idx_l3_sa2 "
                    "ON layer3_sa2_metric_banding(sa2_code)")
        cur.execute("CREATE INDEX idx_l3_metric "
                    "ON layer3_sa2_metric_banding(metric)")
        cur.execute("CREATE INDEX idx_l3_band "
                    "ON layer3_sa2_metric_banding(band)")

        cur.executemany("""
            INSERT INTO layer3_sa2_metric_banding
                (sa2_code, metric, year, period_label, cohort_def,
                 cohort_key, cohort_n, raw_value, percentile, decile, band)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            (r["sa2_code"], r["metric"], r["year"], r["period_label"],
             r["cohort_def"], r["cohort_key"], r["cohort_n"],
             r["raw_value"], r["percentile"], r["decile"], r["band"])
            for r in rows
        ])

        cur.execute("SELECT COUNT(*) FROM layer3_sa2_metric_banding")
        inserted = cur.fetchone()[0]
        if inserted != len(rows):
            raise RuntimeError(
                f"insert count mismatch: expected {len(rows)}, "
                f"got {inserted}")

        # Standard 30 - hardcoded audit_log INSERT
        cur.execute("""
            INSERT INTO audit_log
                (actor, action, subject_type, subject_id,
                 before_json, after_json, reason)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "layer3_apply",
            "layer3_banding_v1",
            "layer3_sa2_metric_banding",
            0,
            '{"rows": 0}',
            f'{{"rows": {inserted}}}',
            ("Layer 3 banding: percentile/decile/band per "
             "(metric x SA2 x latest-year x cohort). "
             f"{inserted} rows. {len(METRICS)} metrics."),
        ))
        cur.execute("SELECT last_insert_rowid()")
        audit_id = cur.fetchone()[0]

        conn.commit()
        print(f"  COMMIT ok. {inserted:,} rows. audit_id {audit_id}")
        return inserted, audit_id, backup_path
    except Exception as e:
        conn.rollback()
        print(f"  ROLLBACK on error: {e}")
        raise
    finally:
        conn.close()


# --------------------------------------------------------------------
# Markdown emit
# --------------------------------------------------------------------

def emit_markdown(out_path, mode, rows, summaries, apply_result=None):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out = []
    w = out.append

    w(f"# Layer 3 banding apply - {mode.upper()}")
    w("")
    w(f"_Generated: {datetime.now().isoformat(timespec='seconds')}_")
    w("")
    w("Banding rules (per `recon/layer3_decisions.md` D2):")
    w("- low  = decile 1-3")
    w("- mid  = decile 4-6")
    w("- high = decile 7-10")
    w("")
    w(f"Total rows produced: **{len(rows):,}**")
    w(f"Metrics processed: {len(summaries)}")
    w("")

    if apply_result:
        rows_inserted, audit_id, backup = apply_result
        w("## Apply outcome")
        w("")
        w(f"- Rows inserted: **{rows_inserted:,}**")
        w(f"- audit_id: **{audit_id}**")
        w(f"- Backup: `data/{backup.name}`")
        w("")

    w("## Per-metric summary")
    w("")
    w("| Metric | Latest period | Coverage | Rows | Skipped (no cohort) |")
    w("|---|---|---:|---:|---:|")
    for s in summaries:
        period = s["period"] if s["period"] is not None else "_(no data)_"
        w(f"| `{s['metric']}` | {period} | {s['coverage']} | "
          f"{s['rows_emitted']:,} | {s['skipped_no_cohort']} |")
    w("")

    w("## Cohort sizes per metric")
    w("")
    for s in summaries:
        if not s["cohort_sizes"]:
            continue
        w(f"### `{s['metric']}` ({s['period']})")
        w("")
        w("| cohort_key | size |")
        w("|---|---:|")
        for k, n in sorted(s["cohort_sizes"]):
            w(f"| `{k}` | {n} |")
        w("")

    w("## Band distribution per metric")
    w("")
    band_counter = defaultdict(Counter)
    for r in rows:
        band_counter[r["metric"]][r["band"]] += 1
    w("| Metric | low | mid | high |")
    w("|---|---:|---:|---:|")
    for metric in sorted(band_counter.keys()):
        c = band_counter[metric]
        w(f"| `{metric}` | {c['low']:,} | {c['mid']:,} | {c['high']:,} |")
    w("")

    w("## Sample rows (first 15)")
    w("")
    w("| sa2_code | metric | year | cohort_def | cohort_key | "
      "cohort_n | raw_value | pctile | decile | band |")
    w("|---|---|---:|---|---|---:|---:|---:|---:|---|")
    for r in rows[:15]:
        rv = (f"{r['raw_value']:,.2f}"
              if r['raw_value'] is not None else "n/a")
        w(f"| `{r['sa2_code']}` | `{r['metric']}` | {r['year']} | "
          f"{r['cohort_def']} | `{r['cohort_key']}` | {r['cohort_n']} | "
          f"{rv} | {r['percentile']:.1f} | {r['decile']} | "
          f"{r['band']} |")
    w("")

    out_path.write_text("\n".join(out), encoding="utf-8")
    size = out_path.stat().st_size
    print(f"Wrote {out_path.relative_to(REPO_ROOT)} ({size:,} bytes)")


# --------------------------------------------------------------------
# Main
# --------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if not DB_PATH.exists():
        print(f"ERROR: DB not found at {DB_PATH}")
        return 1

    mode_label = "APPLY" if args.apply else "DRY-RUN"
    print(f"layer3_apply - {mode_label}")
    print(f"DB: {DB_PATH}")
    print()

    uri = f"file:{DB_PATH.as_posix()}?mode=ro"
    conn_ro = sqlite3.connect(uri, uri=True)
    cohort_lookup = load_cohort_lookup(conn_ro)
    print(f"sa2_cohort: {len(cohort_lookup):,} SA2s loaded")
    print()

    all_rows = []
    summaries = []
    for metric in METRICS:
        print(f"Processing {metric['canonical']} "
              f"(cohort_def={metric['cohort_def']})...")
        rows, summary = compute_banding_for_metric(
            conn_ro, metric, cohort_lookup)
        all_rows.extend(rows)
        summaries.append(summary)
        period_str = summary["period"] if summary["period"] else "n/a"
        print(f"  period={period_str}, rows={len(rows):,}, "
              f"skipped={summary['skipped_no_cohort']}")
    conn_ro.close()

    print()
    print(f"Total rows produced: {len(all_rows):,}")
    print()

    if args.dry_run:
        emit_markdown(DRYRUN_OUT, "dry-run", all_rows, summaries,
                      apply_result=None)
        print()
        print("DRY-RUN complete. No DB changes.")
        print(f"Review: {DRYRUN_OUT.relative_to(REPO_ROOT)}")
        return 0

    if args.apply:
        if len(all_rows) < 10_000:
            print(f"ABORT: only {len(all_rows):,} rows produced, "
                  "below 10,000 sanity floor.")
            return 1

        result = apply_layer3(all_rows)
        emit_markdown(APPLY_OUT, "apply", all_rows, summaries,
                      apply_result=result)
        print()
        print("APPLY complete.")
        print(f"Review: {APPLY_OUT.relative_to(REPO_ROOT)}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
