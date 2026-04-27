"""
Layer 2 Step 5 SPOTCHECK — quick read-only DB sanity query
Confirms abs_sa2_unemployment_quarterly is queryable end-to-end and
joins cleanly to services on sa2_code.
"""
import sqlite3
from pathlib import Path

DB = Path.cwd() / "data" / "kintell.db"

conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
cur = conn.cursor()

print("=" * 60)
print("SALM SA2 SPOTCHECK")
print("=" * 60)

# 1. Row counts
cur.execute("SELECT COUNT(*) FROM abs_sa2_unemployment_quarterly")
print(f"Total rows:        {cur.fetchone()[0]:,}")

cur.execute("SELECT COUNT(DISTINCT sa2_code) "
            "FROM abs_sa2_unemployment_quarterly")
print(f"Distinct SA2:      {cur.fetchone()[0]:,}")

cur.execute("SELECT MIN(year_qtr), MAX(year_qtr) "
            "FROM abs_sa2_unemployment_quarterly")
mn, mx = cur.fetchone()
print(f"Quarter range:     {mn} -> {mx}")

# 2. Latest quarter snapshot — count of SA2s with non-null rate
cur.execute("""
    SELECT year_qtr, COUNT(*) AS rows,
           SUM(CASE WHEN rate IS NOT NULL THEN 1 ELSE 0 END) AS non_null
    FROM abs_sa2_unemployment_quarterly
    WHERE year_qtr IN ('2024-Q4', '2025-Q1', '2025-Q2',
                       '2025-Q3', '2025-Q4')
    GROUP BY year_qtr
    ORDER BY year_qtr
""")
print()
print("Recent quarter coverage:")
print(f"  {'quarter':>8}  {'rows':>6}  {'non-null':>10}")
for q, n, nn in cur.fetchall():
    print(f"  {q:>8}  {n:>6,}  {nn:>10,}")

# 3. Service coverage — services with matching SA2 in latest quarter
cur.execute("""
    SELECT
        COUNT(DISTINCT s.service_id) AS total_services,
        COUNT(DISTINCT CASE WHEN u.sa2_code IS NOT NULL
                            THEN s.service_id END) AS matched_services
    FROM services s
    LEFT JOIN abs_sa2_unemployment_quarterly u
      ON s.sa2_code = u.sa2_code AND u.year_qtr = '2025-Q4'
""")
total, matched = cur.fetchone()
pct = 100.0 * matched / total if total else 0
print()
print(f"Service coverage with 2025-Q4 SALM rate: "
      f"{matched:,}/{total:,} ({pct:.1f}%)")

# 4. Distribution of latest-quarter unemployment rates
cur.execute("""
    SELECT
        ROUND(MIN(rate), 1)  AS rate_min,
        ROUND(AVG(rate), 1)  AS rate_mean,
        ROUND(MAX(rate), 1)  AS rate_max
    FROM abs_sa2_unemployment_quarterly
    WHERE year_qtr = '2025-Q4' AND rate IS NOT NULL
""")
mn, avg, mx = cur.fetchone()
print(f"2025-Q4 rate distribution (across SA2s): "
      f"min={mn}%  mean={avg}%  max={mx}%")

# 5. Sample 5 services + their 2025-Q4 SALM rate
print()
print("Sample 5 services + 2025-Q4 SALM unemployment:")
cur.execute("""
    SELECT s.service_name, s.suburb, s.sa2_code, u.rate, u.count, u.labour_force
    FROM services s
    JOIN abs_sa2_unemployment_quarterly u
      ON s.sa2_code = u.sa2_code AND u.year_qtr = '2025-Q4'
    WHERE s.sa2_code IS NOT NULL AND u.rate IS NOT NULL
    LIMIT 5
""")
for row in cur.fetchall():
    name, suburb, sa2, rate, cnt, lf = row
    print(f"  {str(name)[:35]:35s} | {str(suburb)[:15]:15s} | "
          f"sa2={sa2} | rate={rate}% (cnt={cnt}/lf={lf})")

# 6. Ellenbrook trajectory (consistent with Step 6 spotcheck)
print()
print("Ellenbrook WA — SALM unemployment trajectory:")
cur.execute("""
    SELECT DISTINCT s.sa2_code, s.suburb
    FROM services s
    WHERE s.suburb LIKE '%ELLENBROOK%' AND s.sa2_code IS NOT NULL
    LIMIT 1
""")
sample = cur.fetchone()
if sample:
    sa2, suburb = sample
    print(f"  SA2 {sa2} ({suburb})")
    cur.execute("""
        SELECT year_qtr, rate, count, labour_force
        FROM abs_sa2_unemployment_quarterly
        WHERE sa2_code = ?
          AND (year_qtr LIKE '%-Q4'
               OR year_qtr IN ('2025-Q1', '2025-Q2', '2025-Q3'))
        ORDER BY year_qtr
    """, (sa2,))
    print(f"  {'quarter':>8}  {'rate':>5}  {'count':>5}  {'lf':>6}")
    for q, rate, cnt, lf in cur.fetchall():
        rate_s = f"{rate}%" if rate is not None else "-"
        cnt_s = str(cnt) if cnt is not None else "-"
        lf_s = str(lf) if lf is not None else "-"
        print(f"  {q:>8}  {rate_s:>5}  {cnt_s:>5}  {lf_s:>6}")
else:
    print("  No Ellenbrook services with SA2 found.")

conn.close()
print()
print("=" * 60)
print("SPOTCHECK COMPLETE")
print("=" * 60)
