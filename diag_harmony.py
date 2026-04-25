import sqlite3, json
c = sqlite3.connect("data/kintell.db")
rows = c.execute("""
    SELECT c.candidate_id, c.composite_confidence, c.status,
           json_extract(c.evidence_json,'$.brand') as brand,
           json_extract(c.evidence_json,'$.canonical_group_id') as canon_gid,
           json_extract(c.evidence_json,'$.canonical_group') as canon_name,
           gA.canonical_name as from_name
      FROM link_candidates c
      JOIN groups gA ON gA.group_id = c.from_id
     WHERE LOWER(json_extract(c.evidence_json,'$.brand')) LIKE '%harmony%'
     ORDER BY c.composite_confidence DESC
""").fetchall()
print(f"Total Harmony rows: {len(rows)}")
for r in rows[:5]:
    print(r)
print("---")
# Status distribution
print("By status:", dict(c.execute("""
    SELECT c.status, COUNT(*)
      FROM link_candidates c
     WHERE LOWER(json_extract(c.evidence_json,'$.brand')) LIKE '%harmony%'
     GROUP BY c.status
""").fetchall()))
