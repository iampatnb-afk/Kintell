"""
Layer 2 Step 5b SPOTCHECK — quick read-only DB sanity query
Confirms abs_sa2_socioeconomic_annual is queryable end-to-end and
joins cleanly to services on sa2_code.
"""
import sqlite3
from pathlib import Path

DB = Path.cwd() / "data" / "kintell.db"

conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
cur = conn.cursor()

print("=" * 60)
print("ABS_SA2_SOCIOECONOMIC SPOTCHECK")
print("=" * 60)

# 1. Row counts
cur.execute("SELECT COUNT(*) FROM abs_sa2_socioeconomic_annual")
print(f"Total rows:        {cur.fetchone()[0]:,}")

cur.execute("SELECT COUNT(DISTINCT sa2_code) "
            "FROM abs_sa2_socioeconomic_annual")
print(f"Distinct SA2:      {cur.fetchone()[0]:,}")

cur.execute("SELECT COUNT(DISTINCT metric_name) "
            "FROM abs_sa2_socioeconomic_annual")
print(f"Distinct metrics:  {cur.fetchone()[0]}")

# 2. Per-metric coverage at latest available year for each metric
print()
print("Latest year per metric (non-null SA2 count + value range):")
cur.execute("""
    SELECT metric_name,
           MAX(year) AS latest_year
    FROM abs_sa2_socioeconomic_annual
    WHERE value IS NOT NULL
    GROUP BY metric_name
""")
metric_latest = cur.fetchall()
for metric, latest_y in metric_latest:
    cur.execute("""
        SELECT COUNT(*),
               ROUND(MIN(value), 0),
               ROUND(AVG(value), 0),
               ROUND(MAX(value), 0)
        FROM abs_sa2_socioeconomic_annual
        WHERE metric_name = ? AND year = ? AND value IS NOT NULL
    """, (metric, latest_y))
    n, mn, avg, mx = cur.fetchone()
    print(f"  {metric[:48]:48s} {latest_y}  n={n:>5,}  "
          f"min={int(mn):>9,}  mean={int(avg):>9,}  "
          f"max={int(mx):>9,}")

# 3. Service coverage with 2021 household income
cur.execute("""
    SELECT
        COUNT(DISTINCT s.service_id) AS total_services,
        COUNT(DISTINCT CASE WHEN x.value IS NOT NULL
                            THEN s.service_id END) AS matched
    FROM services s
    LEFT JOIN abs_sa2_socioeconomic_annual x
      ON s.sa2_code = x.sa2_code
     AND x.year = 2021
     AND x.metric_name = 'median_equiv_household_income_weekly'
""")
total, matched = cur.fetchone()
pct = 100.0 * matched / total if total else 0
print()
print(f"Service coverage with Census 2021 household income: "
      f"{matched:,}/{total:,} ({pct:.1f}%)")

# 4. Sample 5 services + their 2021 household income
print()
print("Sample 5 services + Census 2021 household income (weekly):")
cur.execute("""
    SELECT s.service_name, s.suburb, s.sa2_code, x.value
    FROM services s
    JOIN abs_sa2_socioeconomic_annual x
      ON s.sa2_code = x.sa2_code
     AND x.year = 2021
     AND x.metric_name = 'median_equiv_household_income_weekly'
    WHERE s.sa2_code IS NOT NULL AND x.value IS NOT NULL
    LIMIT 5
""")
for row in cur.fetchall():
    name, suburb, sa2, val = row
    print(f"  {str(name)[:35]:35s} | {str(suburb)[:15]:15s} | "
          f"sa2={sa2} | ${val:.0f}/wk")

# 5. Braidwood trajectory (consistent with Step 5/6 spotchecks)
print()
print("Braidwood (sa2=101021007) — full income trajectory:")
cur.execute("""
    SELECT year, metric_name, value
    FROM abs_sa2_socioeconomic_annual
    WHERE sa2_code = '101021007'
      AND value IS NOT NULL
    ORDER BY year, metric_name
""")
prev_year = None
for year, metric, val in cur.fetchall():
    if year != prev_year:
        print(f"  --- {year} ---")
        prev_year = year
    print(f"    {metric[:48]:48s}  {val}")

# 6. Cross-source coherence: does richer SA2 (high household income)
# also have lower unemployment? Quick correlation peek.
print()
print("Cross-source coherence — top 5 highest-income SA2s, "
      "their 2025-Q4 SALM rate:")
cur.execute("""
    SELECT x.sa2_code, x.value AS income,
           u.rate AS unemp_rate
    FROM abs_sa2_socioeconomic_annual x
    LEFT JOIN abs_sa2_unemployment_quarterly u
      ON x.sa2_code = u.sa2_code AND u.year_qtr = '2025-Q4'
    WHERE x.year = 2021
      AND x.metric_name = 'median_equiv_household_income_weekly'
      AND x.value IS NOT NULL
    ORDER BY x.value DESC
    LIMIT 5
""")
for sa2, income, rate in cur.fetchall():
    rate_s = f"{rate:.1f}%" if rate is not None else "-"
    print(f"  sa2={sa2}  income=${int(income):,}/wk  unemp={rate_s}")

print()
print("Bottom 5 lowest-income SA2s, their 2025-Q4 SALM rate:")
cur.execute("""
    SELECT x.sa2_code, x.value AS income,
           u.rate AS unemp_rate
    FROM abs_sa2_socioeconomic_annual x
    LEFT JOIN abs_sa2_unemployment_quarterly u
      ON x.sa2_code = u.sa2_code AND u.year_qtr = '2025-Q4'
    WHERE x.year = 2021
      AND x.metric_name = 'median_equiv_household_income_weekly'
      AND x.value IS NOT NULL
    ORDER BY x.value ASC
    LIMIT 5
""")
for sa2, income, rate in cur.fetchall():
    rate_s = f"{rate:.1f}%" if rate is not None else "-"
    print(f"  sa2={sa2}  income=${int(income):,}/wk  unemp={rate_s}")

conn.close()
print()
print("=" * 60)
print("SPOTCHECK COMPLETE")
print("=" * 60)
