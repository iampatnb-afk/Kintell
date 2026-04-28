"""
sa2_cohort_probe.py

One-shot read-only spot-check of the sa2_cohort table after apply.
"""
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent / "data" / "kintell.db"
conn = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
cur = conn.cursor()

print("=== sa2_cohort summary ===")
n_rows, n_bands, n_states = cur.execute(
    "SELECT COUNT(*), COUNT(DISTINCT ra_band), COUNT(DISTINCT state_code) "
    "FROM sa2_cohort"
).fetchone()
print(f"  rows: {n_rows:,}")
print(f"  distinct ra_band: {n_bands}")
print(f"  distinct state_code: {n_states}")
print()

print("=== ra_band distribution ===")
for band, n in cur.execute(
    "SELECT ra_band, COUNT(*) FROM sa2_cohort "
    "GROUP BY ra_band ORDER BY ra_band IS NULL, ra_band"
).fetchall():
    label = band if band is not None else "(null)"
    print(f"  band {label}: {n:,}")
print()

print("=== state_code distribution ===")
for sc, sn, n in cur.execute(
    "SELECT state_code, state_name, COUNT(*) FROM sa2_cohort "
    "GROUP BY state_code, state_name ORDER BY state_code"
).fetchall():
    print(f"  {sc} {sn}: {n:,}")
print()

print("=== audit_log row 135 ===")
row = cur.execute(
    "SELECT audit_id, actor, action, subject_type, after_json, occurred_at "
    "FROM audit_log WHERE audit_id = 135"
).fetchone()
if row:
    audit_id, actor, action, subject_type, after_json, occurred_at = row
    print(f"  audit_id:     {audit_id}")
    print(f"  actor:        {actor}")
    print(f"  action:       {action}")
    print(f"  subject_type: {subject_type}")
    print(f"  after_json:   {after_json}")
    print(f"  occurred_at:  {occurred_at}")
else:
    print("  NOT FOUND")

conn.close()
