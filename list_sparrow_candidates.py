import sqlite3
c = sqlite3.connect("data/kintell.db")
rows = c.execute("""
    SELECT c.candidate_id, c.composite_confidence,
           gA.canonical_name, gB.canonical_name
      FROM link_candidates c
      JOIN groups gA ON gA.group_id = c.from_id
      JOIN groups gB ON gB.group_id = c.to_id
     WHERE LOWER(json_extract(c.evidence_json,'$.brand'))
           = 'sparrow early learning'
     ORDER BY c.composite_confidence DESC
""").fetchall()
for r in rows:
    print(r)
