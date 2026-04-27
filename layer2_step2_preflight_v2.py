# layer2_step2_preflight_v2.py — read-only, with fixes
import os, sqlite3, datetime
from collections import Counter

DB = os.path.join("data", "kintell.db")
conn = sqlite3.connect(DB)
cur = conn.cursor()

print("# Layer 2 Step 2 — Orphan-Entity Self-Group Backfill — Preflight v2")
print(f"_Generated: {datetime.datetime.now().isoformat(timespec='seconds')}_\n")

PMT_MAP = {
    "Private for profit": "private",
    "Private not for profit community managed": "nfp",
    "Private not for profit other organisations": "nfp",
    "Independent schools": "independent_school",
    "Catholic schools": "catholic_school",
    "Government managed": "government",
    "State/Territory Government managed": "government",
    "State/Territory government schools": "government",
    "State/Territory and Local Government managed": "government",
    "Local Government": "government",
    "Other": "unknown",
    None: "unknown",
}

# 1. Confirmed orphan count
cur.execute("""
SELECT COUNT(DISTINCT e.entity_id)
  FROM entities e
  JOIN services s ON s.entity_id = e.entity_id
 WHERE s.is_active = 1 AND e.group_id IS NULL;
""")
print(f"## Orphan entity count: {cur.fetchone()[0]}\n")

# 2. Re-run distribution with fixed map
print("## Projected ownership_type distribution (corrected map)")
cur.execute("""
SELECT e.entity_id, e.legal_name,
       GROUP_CONCAT(s.provider_management_type, '|||') AS pmts
  FROM entities e
  JOIN services s ON s.entity_id = e.entity_id
 WHERE s.is_active = 1 AND e.group_id IS NULL
 GROUP BY e.entity_id;
""")
projected = Counter()
unmapped_pmts = Counter()
for entity_id, name, pmts_concat in cur.fetchall():
    if pmts_concat is None:
        projected["unknown"] += 1
        continue
    pmts = pmts_concat.split("|||")
    most_common = Counter(pmts).most_common(1)[0][0]
    if most_common not in PMT_MAP:
        unmapped_pmts[most_common] += 1
    ot = PMT_MAP.get(most_common, "unknown")
    projected[ot] += 1
for k, v in projected.most_common():
    print(f"  {v:>5}  {k}")
print(f"  total            {sum(projected.values())}")
if unmapped_pmts:
    print(f"\n  WARNING — unmapped PMT values (defaulted to unknown):")
    for pmt, n in unmapped_pmts.most_common():
        print(f"    {n}x {pmt!r}")

# 3. Distinct entities with same legal_name (proper dup check)
print("\n## Distinct orphan entities sharing a legal_name (UNIQUE collision risk)")
cur.execute("""
SELECT legal_name, COUNT(DISTINCT entity_id) AS n
  FROM (
    SELECT DISTINCT e.entity_id, e.legal_name
      FROM entities e
      JOIN services s ON s.entity_id = e.entity_id
     WHERE s.is_active = 1 AND e.group_id IS NULL
  )
 GROUP BY legal_name
HAVING n > 1
 ORDER BY n DESC;
""")
rows = cur.fetchall()
if not rows:
    print("  none — every orphan entity has a unique legal_name")
else:
    print(f"  {len(rows)} legal_names shared by multiple orphan entities:")
    for nm, n in rows[:20]:
        print(f"    {n}x {nm!r}")

# 4. Collision against existing groups.canonical_name
print("\n## Collisions vs existing groups.canonical_name")
cur.execute("""
SELECT DISTINCT e.legal_name
  FROM entities e
  JOIN services s ON s.entity_id = e.entity_id
  JOIN groups g ON g.canonical_name = e.legal_name
 WHERE s.is_active = 1 AND e.group_id IS NULL;
""")
rows = cur.fetchall()
if not rows:
    print("  none — no orphan name collides with an existing group canonical_name")
else:
    print(f"  {len(rows)} orphan legal_names already exist as group canonical_names:")
    for (nm,) in rows[:20]:
        print(f"    {nm!r}")

# 5. UNIQUE indexes on groups (verify which column carries the constraint)
print("\n## UNIQUE constraints on groups (from sqlite_master)")
cur.execute("""
SELECT name, sql FROM sqlite_master
 WHERE type='index' AND tbl_name='groups';
""")
for n, s in cur.fetchall():
    print(f"  - {n}: {s}")
# Try to expose autoindex column
cur.execute("PRAGMA index_list(groups);")
for row in cur.fetchall():
    print(f"  index_list: {row}")
    cur.execute(f"PRAGMA index_info('{row[1]}');")
    for ii in cur.fetchall():
        print(f"    -> col {ii}")

# 6. Slug check — find existing slug pattern
print("\n## Existing slug samples (to mimic format)")
cur.execute("SELECT canonical_name, slug FROM groups WHERE slug IS NOT NULL AND slug != '' LIMIT 8;")
for r in cur.fetchall():
    print(f"  {r[0][:50]!r:<55} -> slug={r[1]!r}")

# 7. parent_entity_id usage on existing groups
print("\n## parent_entity_id usage on existing groups")
cur.execute("SELECT COUNT(*) FROM groups WHERE parent_entity_id IS NOT NULL;")
print(f"  groups with parent_entity_id populated: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM groups WHERE parent_entity_id IS NULL;")
print(f"  groups with parent_entity_id NULL     : {cur.fetchone()[0]}")

conn.close()
