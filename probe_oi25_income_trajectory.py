"""
PROBE — OI-25: Census income trajectory shows single point.

Reproduces the EXACT SQL that centre_page.py:_metric_trajectory runs
for the three Census-source income metrics, against the verification
SA2 (service_id=103 — Kool HQ Waverley, Bondi Junction-Waverly).

Then shows a broader view: all (year, metric_name) rows present for
that SA2 in abs_sa2_socioeconomic_annual, including NULL counts.

Read-only — no DB writes. Safe to run multiple times.

Usage:
    cd C:\\Users\\Patrick Bell\\remara-agent
    python probe_oi25_income_trajectory.py
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path("data/kintell.db")
SERVICE_ID = 103
TABLE = "abs_sa2_socioeconomic_annual"

# (centre_page metric_name, DB metric_name filter) per
# LAYER3_METRIC_TRAJECTORY_SOURCE in centre_page.py v12.
METRICS_TO_PROBE = [
    ("sa2_median_household_income", "median_equiv_household_income_weekly"),
    ("sa2_median_employee_income",  "median_employee_income_annual"),
    ("sa2_median_total_income",     "median_total_income_excl_pensions_annual"),
]


def main() -> int:
    if not DB_PATH.exists():
        print(f"ERROR: {DB_PATH} not found. Run from repo root "
              f"(C:\\Users\\Patrick Bell\\remara-agent).")
        return 1

    con = sqlite3.connect(str(DB_PATH))
    con.row_factory = sqlite3.Row

    print("=" * 72)
    print(f"PROBE OI-25 — Census income trajectory for service_id={SERVICE_ID}")
    print("=" * 72)

    # 1. Resolve SA2 for the verification service.
    svc = con.execute(
        "SELECT service_name, sa2_code, sa2_name "
        "  FROM services WHERE service_id = ?",
        (SERVICE_ID,),
    ).fetchone()
    if not svc:
        print(f"ERROR: service_id={SERVICE_ID} not found in services table.")
        con.close()
        return 1

    sa2_code = svc["sa2_code"]
    print(f"Service:  {svc['service_name']}")
    print(f"SA2:      {sa2_code}  ({svc['sa2_name']})")
    print()

    # 2. Per metric: run the exact SQL trajectory builder uses.
    for centre_metric, db_metric_name in METRICS_TO_PROBE:
        print("-" * 72)
        print(f"METRIC:    {centre_metric}")
        print(f"DB filter: metric_name = '{db_metric_name}'")
        print("-" * 72)

        sql = (
            f"SELECT year AS period, value AS value "
            f"  FROM {TABLE} "
            f" WHERE sa2_code = ? AND metric_name = ? "
            f" ORDER BY year"
        )
        try:
            rows = con.execute(sql, (sa2_code, db_metric_name)).fetchall()
        except sqlite3.OperationalError as e:
            print(f"  SQL error: {e}")
            print()
            continue

        print(f"Rows returned by SQL: {len(rows)}")
        if not rows:
            print("  (no rows — SA2 + metric combo absent from table)")
        else:
            kept = 0
            dropped = 0
            for r in rows:
                v = r["value"]
                v_type = type(v).__name__
                v_repr = repr(v)
                if v is None:
                    status = "NULL  -> _metric_trajectory DROPS"
                    dropped += 1
                else:
                    try:
                        float(v)
                        status = "OK    -> _metric_trajectory KEEPS"
                        kept += 1
                    except (TypeError, ValueError):
                        status = f"NON-NUMERIC ({v_type})  -> _metric_trajectory DROPS"
                        dropped += 1
                print(f"  year={r['period']!s:<6}  value={v_repr:<18}  {status}")
            print(f"  -> {kept} point(s) reach renderer; {dropped} dropped")
        print()

    # 3. Broader view: what years/metrics exist for this SA2 at all?
    print("-" * 72)
    print(f"BROADER VIEW — all (year, metric_name) for SA2 {sa2_code}")
    print(f"in {TABLE}")
    print("-" * 72)

    rows = con.execute(
        f"SELECT metric_name, year, COUNT(*) AS n_rows, "
        f"       SUM(CASE WHEN value IS NULL THEN 1 ELSE 0 END) AS n_null "
        f"  FROM {TABLE} "
        f" WHERE sa2_code = ? "
        f" GROUP BY metric_name, year "
        f" ORDER BY metric_name, year",
        (sa2_code,),
    ).fetchall()

    if not rows:
        print(f"  (no rows at all for SA2 {sa2_code} in {TABLE})")
    else:
        cur = None
        for r in rows:
            if r["metric_name"] != cur:
                cur = r["metric_name"]
                print(f"\n  {cur}")
            null_note = f"  [{r['n_null']} NULL value(s)]" if r["n_null"] else ""
            print(f"    year={r['year']}  rows={r['n_rows']}{null_note}")

    print()
    print("=" * 72)
    print("PROBE COMPLETE — read-only, no DB writes.")
    print("=" * 72)

    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
