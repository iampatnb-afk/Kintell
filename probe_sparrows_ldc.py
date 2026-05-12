import sqlite3
con = sqlite3.connect("data/kintell.db")
con.row_factory = sqlite3.Row

# First check whether Sparrows Group exists at all
print("=== Operators with 'Sparrow' in name ===")
rows = con.execute("""
    SELECT g.group_id, g.canonical_name, g.display_name, g.ownership_type, COUNT(s.service_id) AS n_centres
    FROM groups g
    LEFT JOIN entities e ON e.group_id = g.group_id
    LEFT JOIN services s ON s.entity_id = e.entity_id AND s.is_active = 1
    WHERE g.canonical_name LIKE '%Sparrow%' OR g.display_name LIKE '%Sparrow%'
    GROUP BY g.group_id
    ORDER BY n_centres DESC
""").fetchall()
for r in rows:
    print(f"  group_id={r['group_id']}  name={r['canonical_name']!r}  ownership={r['ownership_type']!r}  n={r['n_centres']}")

# If Sparrows exists, show a representative LDC centre
if rows:
    gid = rows[0]['group_id']
    print(f"\n=== Sample LDC centres in group_id={gid} (LDC + active + has SA2) ===")
    sample = con.execute("""
        SELECT s.service_id, s.service_name, s.suburb, s.state, s.sa2_code
        FROM services s
        JOIN entities e ON s.entity_id = e.entity_id
        WHERE e.group_id = ?
          AND s.service_sub_type = 'LDC'
          AND s.is_active = 1
          AND s.sa2_code IS NOT NULL
        ORDER BY s.service_name
        LIMIT 8
    """, (gid,)).fetchall()
    for s in sample:
        print(f"  service_id={s['service_id']:>5}  {s['service_name']:<40}  {s['suburb']!r:<25}  sa2={s['sa2_code']}")

# Fallback: top-10 for-profit LDC operators by centre count
print("\n=== Top for-profit LDC operators (fallback if no Sparrows) ===")
rows2 = con.execute("""
    SELECT g.canonical_name, g.ownership_type, COUNT(s.service_id) AS n_ldc
    FROM groups g
    JOIN entities e ON e.group_id = g.group_id
    JOIN services s ON s.entity_id = e.entity_id
    WHERE s.service_sub_type = 'LDC' AND s.is_active = 1
      AND g.ownership_type LIKE '%for-profit%'
    GROUP BY g.group_id
    HAVING n_ldc >= 5
    ORDER BY n_ldc DESC
    LIMIT 10
""").fetchall()
for r in rows2:
    print(f"  {r['canonical_name']:<40}  ({r['ownership_type']:<25})  n={r['n_ldc']}")
