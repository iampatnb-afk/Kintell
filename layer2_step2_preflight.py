# layer2_step2_preflight.py — read-only
# Confirm orphan-entity shape and propose ownership_type derivation distribution.
import os, sqlite3, datetime, json
from collections import Counter

DB = os.path.join("data", "kintell.db")
conn = sqlite3.connect(DB)
cur = conn.cursor()

print("# Layer 2 Step 2 — Orphan-Entity Self-Group Backfill — Preflight")
print(f"_Generated: {datetime.datetime.now().isoformat(timespec='seconds')}_\n")

# 1. entities schema
print("## entities schema")
cur.execute("PRAGMA table_info(entities);")
for c in cur.fetchall():
    print(f"  - {c[1]:<28} {c[2]:<10} pk={c[5]} notnull={c[3]}")

# 2. groups schema
print("\n## groups schema")
cur.execute("PRAGMA table_info(groups);")
for c in cur.fetchall():
    print(f"  - {c[1]:<28} {c[2]:<10} pk={c[5]} notnull={c[3]}")

# 3. groups indexes (look for UNIQUE constraints on name)
print("\n## groups indexes")
cur.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='groups';")
for n, s in cur.fetchall():
    print(f"  - {n}: {s}")

# 4. Confirm orphan count
cur.execute("""
SELECT COUNT(DISTINCT e.entity_id)
  FROM entities e
  JOIN services s ON s.entity_id = e.entity_id
 WHERE s.is_active = 1 AND e.group_id IS NULL;
""")
n_orphans = cur.fetchone()[0]
print(f"\n## Orphan count")
print(f"  entities with active services AND group_id IS NULL: {n_orphans}")

# 5. Distinct PMT values across services of orphan entities
print("\n## provider_management_type distribution across orphan entities' services")
cur.execute("""
SELECT s.provider_management_type, COUNT(*) AS n
  FROM entities e
  JOIN services s ON s.entity_id = e.entity_id
 WHERE s.is_active = 1 AND e.group_id IS NULL
 GROUP BY s.provider_management_type
 ORDER BY n DESC;
""")
for pmt, n in cur.fetchall():
    print(f"  {n:>5}  {pmt!r}")

# 6. Sample 10 orphans with their services & PMT
print("\n## Sample of 10 orphan entities (entity name + service count + PMT)")
cur.execute("""
SELECT e.entity_id, e.legal_name,
       COUNT(s.service_id) AS n_services,
       GROUP_CONCAT(DISTINCT s.provider_management_type) AS pmts
  FROM entities e
  JOIN services s ON s.entity_id = e.entity_id
 WHERE s.is_active = 1 AND e.group_id IS NULL
 GROUP BY e.entity_id, e.legal_name
 ORDER BY n_services DESC, e.entity_id
 LIMIT 10;
""")
for r in cur.fetchall():
    print(f"  id={r[0]:<6} svc={r[2]:>3} name={r[1][:50]!r:<55} pmts={r[3]}")

# 7. Existing groups.ownership_type enum values (Decision 9)
print("\n## Existing groups.ownership_type distribution (for enum reference)")
cur.execute("SELECT ownership_type, COUNT(*) FROM groups GROUP BY ownership_type ORDER BY COUNT(*) DESC;")
for ot, n in cur.fetchall():
    print(f"  {n:>5}  {ot!r}")

# 8. Proposed PMT -> ownership_type mapping (per Decision 9 six-value enum)
print("\n## Proposed PMT -> ownership_type mapping")
PMT_MAP = {
    "Private for profit": "private",
    "Private not for profit community managed": "nfp",
    "Private not for profit other organisations": "nfp",
    "Independent schools": "independent_school",
    "Catholic schools": "catholic_school",
    "Government managed": "government",
    "State/Territory Government managed": "government",
    "Local Government": "government",
    None: "unknown",
}
for k, v in PMT_MAP.items():
    print(f"  {k!r:<55} -> {v!r}")

# 9. Project the derivation across orphan entities (most-common PMT per entity)
print("\n## Projected ownership_type distribution after self-group backfill")
cur.execute("""
SELECT e.entity_id, e.legal_name,
       GROUP_CONCAT(s.provider_management_type) AS pmts
  FROM entities e
  JOIN services s ON s.entity_id = e.entity_id
 WHERE s.is_active = 1 AND e.group_id IS NULL
 GROUP BY e.entity_id;
""")
projected = Counter()
for entity_id, name, pmts_concat in cur.fetchall():
    if pmts_concat is None:
        projected["unknown"] += 1
        continue
    pmts = [p.strip() if p else None for p in pmts_concat.split(",")]
    most_common = Counter(pmts).most_common(1)[0][0]
    ot = PMT_MAP.get(most_common, "unknown")
    projected[ot] += 1
for k, v in projected.most_common():
    print(f"  {v:>5}  {k}")

# 10. Check for duplicate proposed group names (will multiple orphans share a name?)
print("\n## Duplicate-name check among orphan entity legal_name values")
cur.execute("""
SELECT e.legal_name, COUNT(*) AS n
  FROM entities e
  JOIN services s ON s.entity_id = e.entity_id
 WHERE s.is_active = 1 AND e.group_id IS NULL
 GROUP BY e.legal_name
HAVING n > 1
 ORDER BY n DESC LIMIT 10;
""")
rows = cur.fetchall()
if not rows:
    print("  no duplicates among orphan entity legal_name values")
else:
    print(f"  {len(rows)} duplicate names found (top 10):")
    for nm, n in rows:
        print(f"    {n}x {nm!r}")

# 11. Existing groups with same name as any orphan entity (collision risk)
print("\n## Collision check vs existing groups.group_name")
cur.execute("""
SELECT e.legal_name, COUNT(DISTINCT e.entity_id) AS n_orphans
  FROM entities e
  JOIN services s ON s.entity_id = e.entity_id
  JOIN groups g ON g.group_name = e.legal_name
 WHERE s.is_active = 1 AND e.group_id IS NULL
 GROUP BY e.legal_name
 ORDER BY n_orphans DESC;
""")
rows = cur.fetchall()
if not rows:
    print("  no orphan name collides with an existing group name")
else:
    print(f"  {len(rows)} orphan names collide with existing group names (top 10):")
    for nm, n in rows[:10]:
        print(f"    {n}x orphan(s) named {nm!r} — group with same name already exists")

conn.close()
