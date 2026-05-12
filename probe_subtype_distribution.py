import sqlite3
con = sqlite3.connect("data/kintell.db")
con.row_factory = sqlite3.Row
print("=== service_sub_type distribution ===")
rows = con.execute(
    "SELECT service_sub_type, COUNT(*) AS n, "
    "SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) AS active "
    "FROM services GROUP BY service_sub_type ORDER BY n DESC"
).fetchall()
for r in rows:
    st = r['service_sub_type'] or '(null)'
    print(f"  {st:<40}  total={r['n']:>6}  active={r['active']:>6}")
print()
print("=== Verification centre subtype ===")
r = con.execute("SELECT service_id, service_name, service_sub_type FROM services WHERE service_id = 103").fetchone()
print(f"  service_id={r['service_id']}  name={r['service_name']!r}  sub_type={r['service_sub_type']!r}")
