import sqlite3
c = sqlite3.connect("data/kintell.db")
print("Active groups holding any Harmony-branded service:")
for r in c.execute("""
    SELECT g.group_id, g.canonical_name, g.is_active,
           COUNT(DISTINCT e.entity_id) AS ents,
           COUNT(s.service_id) AS svcs,
           SUM(s.approved_places) AS places
      FROM groups g
      JOIN entities e ON e.group_id = g.group_id
      JOIN services s ON s.entity_id = e.entity_id
     WHERE LOWER(s.service_name) LIKE 'harmony early%'
     GROUP BY g.group_id
     ORDER BY svcs DESC
""").fetchall():
    tag = "ACTIVE" if r[2] else "soft-deleted"
    print(f"  #{r[0]:<5} [{tag:13s}] {r[3]:2d} entities  {r[4]:3d} services  {r[5]} places   {r[1]}")
