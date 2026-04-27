"""
Layer 2 Step 6 SPOTCHECK — quick read-only DB sanity query
Confirms abs_sa2_erp_annual is queryable end-to-end and joins cleanly
to services on sa2_code.
"""
import sqlite3
from pathlib import Path

DB = Path.cwd() / "data" / "kintell.db"

conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
cur = conn.cursor()

print("=" * 60)
print("ABS_SA2_ERP_ANNUAL SPOTCHECK")
print("=" * 60)

# 1. Row counts
cur.execute("SELECT COUNT(*) FROM abs_sa2_erp_annual")
print(f"Total rows:        {cur.fetchone()[0]:,}")

cur.execute("SELECT COUNT(DISTINCT sa2_code) FROM abs_sa2_erp_annual")
print(f"Distinct SA2:      {cur.fetchone()[0]:,}")

cur.execute("SELECT COUNT(DISTINCT year) FROM abs_sa2_erp_annual")
print(f"Distinct years:    {cur.fetchone()[0]}")

# 2. Years covered
cur.execute("""
    SELECT year, COUNT(*) AS rows,
           SUM(CASE WHEN persons IS NOT NULL THEN 1 ELSE 0 END) AS non_null
    FROM abs_sa2_erp_annual
    GROUP BY year
    ORDER BY year
""")
print()
print("Year coverage:")
print(f"  {'year':>6}  {'rows':>8}  {'non-null':>10}")
for year, rows, non_null in cur.fetchall():
    print(f"  {year:>6}  {rows:>8,}  {non_null:>10,}")

# 3. Join to services — first 5 services in 2024 with their under-5 count
print()
print("Join sanity: first 5 services + 2024 SA2 under-5 cohort:")
cur.execute("""
    SELECT s.service_name, s.suburb, s.sa2_code, e.persons
    FROM services s
    JOIN abs_sa2_erp_annual e ON s.sa2_code = e.sa2_code
    WHERE s.sa2_code IS NOT NULL
      AND e.year = 2024
      AND e.age_group = 'under_5_persons'
    LIMIT 5
""")
for row in cur.fetchall():
    name, suburb, sa2, persons = row
    print(f"  {str(name)[:40]:40s} | {str(suburb)[:15]:15s} | "
          f"sa2={sa2} | u5_2024={persons}")

# 4. Service coverage — how many services have a matching SA2 in the table?
cur.execute("""
    SELECT
        COUNT(DISTINCT s.service_id) AS total_services,
        COUNT(DISTINCT CASE WHEN e.sa2_code IS NOT NULL
                            THEN s.service_id END) AS matched_services
    FROM services s
    LEFT JOIN abs_sa2_erp_annual e
      ON s.sa2_code = e.sa2_code AND e.year = 2024
                                  AND e.age_group = 'under_5_persons'
""")
total, matched = cur.fetchone()
pct = 100.0 * matched / total if total else 0
print()
print(f"Service coverage with 2024 under-5 data: "
      f"{matched:,}/{total:,} ({pct:.1f}%)")

# 5. Trajectory check on Sparrow's Ellenbrook (well-known to project)
print()
print("Trajectory check — Ellenbrook WA (Sparrow cluster):")
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
        SELECT year, persons FROM abs_sa2_erp_annual
        WHERE sa2_code = ? AND age_group = 'under_5_persons'
        ORDER BY year
    """, (sa2,))
    print(f"  {'year':>6}  {'under-5':>8}")
    for year, persons in cur.fetchall():
        marker = "" if persons is not None else "(no data)"
        print(f"  {year:>6}  {persons if persons is not None else '-':>8}  {marker}")
else:
    print("  No Ellenbrook services with SA2 found.")

conn.close()
print()
print("=" * 60)
print("SPOTCHECK COMPLETE")
print("=" * 60)
