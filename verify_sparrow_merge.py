import sqlite3
c = sqlite3.connect("data/kintell.db")

# Active groups holding Sparrow services
rows = c.execute("""
    SELECT g.group_id, g.canonical_name, g.is_active,
           COUNT(DISTINCT e.entity_id) AS ents,
           COUNT(DISTINCT s.service_id) AS svcs
      FROM groups g
      JOIN entities e ON e.group_id = g.group_id
      JOIN services s ON s.entity_id = e.entity_id
     WHERE LOWER(s.service_name) LIKE 'sparrow early learning%'
        OR LOWER(s.service_name) LIKE 'sparrow nest%'
     GROUP BY g.group_id
     ORDER BY svcs DESC
""").fetchall()

print("ACTIVE groups currently holding Sparrow-branded services:")
for gid, name, active, ents, svcs in rows:
    tag = "ACTIVE" if active else "soft-deleted"
    print(f"  #{gid:<5} [{tag}]  {ents:2d} entities  {svcs:3d} services   {name}")

# Overall status
print("\nStatus:")
by_status = dict(c.execute(
    "SELECT status, COUNT(*) FROM link_candidates "
    "WHERE link_type='group_merge' GROUP BY status"
).fetchall())
print(f"  Pending  : {by_status.get('pending',0)}")
print(f"  Accepted : {by_status.get('accepted',0)}")
print(f"  Rejected : {by_status.get('rejected',0)}")
print(f"  Parked   : {by_status.get('parked',0)}")

active_gc = c.execute("SELECT COUNT(*) FROM groups WHERE is_active=1").fetchone()[0]
total_gc  = c.execute("SELECT COUNT(*) FROM groups").fetchone()[0]
print(f"\nActive groups: {active_gc} / {total_gc} total")
