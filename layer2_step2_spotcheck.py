# layer2_step2_spotcheck.py — read-only verification
import sqlite3, os
DB = os.path.join("data", "kintell.db")
conn = sqlite3.connect(DB)
cur = conn.cursor()

def q(sql, params=()):
    cur.execute(sql, params)
    return cur.fetchall()

print("=== 1. Coverage summary ===")
for label, sql in [
    ("entities total", "SELECT COUNT(*) FROM entities"),
    ("entities with group_id", "SELECT COUNT(*) FROM entities WHERE group_id IS NOT NULL"),
    ("entities still orphan (no group_id)", "SELECT COUNT(*) FROM entities WHERE group_id IS NULL"),
    ("groups total", "SELECT COUNT(*) FROM groups"),
    ("groups that are self-groups (parent_entity_id IS NOT NULL)", "SELECT COUNT(*) FROM groups WHERE parent_entity_id IS NOT NULL"),
]:
    print(f"  {label:<58} {q(sql)[0][0]}")

print("\n=== 2. Radford College Limited (silent bug #3 from session 2026-04-26) ===")
rows = q("""SELECT e.entity_id, e.legal_name, e.group_id,
                   g.canonical_name, g.ownership_type, g.is_for_profit, g.parent_entity_id
              FROM entities e
              LEFT JOIN groups g ON g.group_id = e.group_id
             WHERE e.legal_name LIKE '%Radford%';""")
for r in rows:
    print(f"  entity_id={r[0]} '{r[1]}'")
    print(f"    -> group_id={r[2]} canonical='{r[3]}' ownership='{r[4]}' for_profit={r[5]} parent_entity_id={r[6]}")

print("\n=== 3. The 'big OSHC' orphans (TheirCare, Camp Australia, Team Holiday, OSHCLUB) ===")
rows = q("""SELECT e.entity_id, e.legal_name, g.ownership_type, g.is_for_profit, g.slug
              FROM entities e
              JOIN groups g ON g.group_id = e.group_id
             WHERE e.legal_name IN ('TheirCare Pty Ltd', 'Camp Australia Pty Limited',
                                    'TEAM HOLIDAY PTY LTD', 'OSHCLUB PTY LTD',
                                    'Helping Hands Network Pty Ltd')
             ORDER BY e.entity_id;""")
for r in rows:
    print(f"  id={r[0]:<5} {r[1]:<35} ownership={r[2]:<20} for_profit={r[3]} slug={r[4]}")

print("\n=== 4. Government department orphans (should be ownership=government) ===")
rows = q("""SELECT e.entity_id, e.legal_name, g.ownership_type, g.is_for_profit
              FROM entities e
              JOIN groups g ON g.group_id = e.group_id
             WHERE e.legal_name IN ('Department of Education',
                                    'ACT Education Directorate',
                                    'Department of Education and Training')
             ORDER BY e.entity_id;""")
for r in rows:
    print(f"  id={r[0]:<5} {r[1]:<40} ownership={r[2]} for_profit={r[3]}")

print("\n=== 5. The Campbelltown duplicate-name pair (slug disambiguation check) ===")
rows = q("""SELECT e.entity_id, e.legal_name, g.group_id, g.canonical_name, g.slug
              FROM entities e
              JOIN groups g ON g.group_id = e.group_id
             WHERE e.legal_name = 'Campbelltown Anglican Schools Council'
             ORDER BY e.entity_id;""")
for r in rows:
    print(f"  entity_id={r[0]} -> group_id={r[2]} canonical='{r[3]}' slug='{r[4]}'")

print("\n=== 6. Sample 5 random self-groups (sanity check schema) ===")
rows = q("""SELECT group_id, canonical_name, slug, ownership_type, is_for_profit,
                   parent_entity_id, is_active, created_at
              FROM groups
             WHERE parent_entity_id IS NOT NULL
             ORDER BY RANDOM() LIMIT 5;""")
for r in rows:
    print(f"  gid={r[0]:<5} '{r[1][:35]:<35}' slug='{r[2][:40]}'")
    print(f"    ownership={r[3]} for_profit={r[4]} parent_entity={r[5]} active={r[6]} created={r[7]}")

print("\n=== 7. Cross-check: every self-group's parent_entity_id points to an entity that points back ===")
rows = q("""SELECT COUNT(*) AS bad
              FROM groups g
              LEFT JOIN entities e ON e.entity_id = g.parent_entity_id
             WHERE g.parent_entity_id IS NOT NULL
               AND (e.entity_id IS NULL OR e.group_id != g.group_id);""")
print(f"  inconsistent self-group<->entity links: {rows[0][0]} (expect 0)")

conn.close()
