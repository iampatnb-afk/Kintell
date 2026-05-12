r"""
Verify storage state — fraction (v2) or percentage (v3)?

Read-only.
    python verify_a2_state.py
"""

import sqlite3
from pathlib import Path

con = sqlite3.connect(Path("data") / "kintell.db")
cur = con.cursor()

print("=" * 60)
print("Storage check — NES values for verification SA2s (2021):")
print("=" * 60)
for sa2, name in [("211011251", "Bayswater Vic"),
                  ("118011341", "Bondi NSW"),
                  ("506031124", "Bentley WA")]:
    row = cur.execute(
        "SELECT value FROM abs_sa2_education_employment_annual "
        "WHERE sa2_code = ? AND metric_name = 'census_nes_share_pct' AND year = 2021",
        (sa2,),
    ).fetchone()
    val = row[0] if row else None
    if val is None:
        print(f"  {sa2} ({name}): MISSING")
    elif val < 1.0:
        print(f"  {sa2} ({name}): {val} -> FRACTION (v2 storage; Path A not applied)")
    else:
        print(f"  {sa2} ({name}): {val} -> PERCENTAGE (v3 storage; Path A applied)")

print()
print("=" * 60)
print("Recent audit_log actions for NES + populator + layer3:")
print("=" * 60)
rows = cur.execute(
    "SELECT audit_id, action, occurred_at FROM audit_log "
    "WHERE action LIKE '%nes%' OR action LIKE '%catchment_cache%' OR action LIKE '%layer3%' "
    "ORDER BY audit_id DESC LIMIT 10"
).fetchall()
for r in rows:
    print(f"  audit_id={r[0]:>4}  {r[1]:<45}  {r[2]}")

con.close()
