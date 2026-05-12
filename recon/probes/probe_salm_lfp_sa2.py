"""
recon/probes/probe_salm_lfp_sa2.py — Layer 4.3 sub-pass 4.3.2 (Thread B)

Read-only probe: does ABS / JSA SALM publish labour force participation
(LFP) at SA2 level, alongside the existing unemployment series?

Context: Centre page currently renders LFP triplet (sa2_lfp_persons /
_females / _males) at LITE weight per DEC-75 because LFP is sourced
from Census 2021 TSP T33A-H — only 3 data points across 2011/2016/2021.
SALM publishes unemployment rate quarterly at SA2 (already ingested
into abs_sa2_unemployment_quarterly). If SALM also publishes LFP at
SA2, that source upgrades LFP to ~60 quarterly points and the rows
promote back to FULL weight (trajectory chart + cohort histogram).

What this probe answers:
  1. Does any existing kintell.db table carry SA2-level LFP data?
  2. If not, what columns does abs_sa2_unemployment_quarterly carry?
     (LFP might be in there as a sibling column without us realising.)
  3. What's the row-count + period coverage of the SALM-derived
     unemployment data? (Same SA2-quarter granularity is the target
     for any LFP ingest.)

This script READS only — no DB mutations, no ingest. The output goes
into recon/layer4_3_sub_pass_4_3_2_probe.md as the basis for whether
to queue an LFP ingest as a follow-up sub-pass.

Run from repo root:
  python recon/probes/probe_salm_lfp_sa2.py

Output: prints to stdout. Operator captures to clipboard / file and
pastes into the recon artefact.
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "kintell.db"

if not DB_PATH.exists():
    print(f"ERROR: {DB_PATH} not found.")
    sys.exit(1)

conn = sqlite3.connect(str(DB_PATH))
conn.row_factory = sqlite3.Row

print("=" * 72)
print("SALM LFP probe (Thread B) — recon read-only")
print("=" * 72)
print(f"DB: {DB_PATH}")
print()

# 1. Inventory: any table with 'lfp' in its name?
print("─" * 72)
print("1. Tables with 'lfp' in name (case-insensitive)")
print("─" * 72)
rows = conn.execute("""
    SELECT name FROM sqlite_master
    WHERE type='table' AND lower(name) LIKE '%lfp%'
    ORDER BY name
""").fetchall()
if rows:
    for r in rows:
        n = conn.execute(f"SELECT COUNT(*) FROM {r['name']}").fetchone()[0]
        print(f"  {r['name']}: {n} rows")
else:
    print("  (none)")
print()

# 2. Inventory: any table with 'salm' in its name?
print("─" * 72)
print("2. Tables with 'salm' in name (case-insensitive)")
print("─" * 72)
rows = conn.execute("""
    SELECT name FROM sqlite_master
    WHERE type='table' AND lower(name) LIKE '%salm%'
    ORDER BY name
""").fetchall()
if rows:
    for r in rows:
        n = conn.execute(f"SELECT COUNT(*) FROM {r['name']}").fetchone()[0]
        print(f"  {r['name']}: {n} rows")
else:
    print("  (none)")
print()

# 3. abs_sa2_unemployment_quarterly: schema + period coverage + sample
print("─" * 72)
print("3. abs_sa2_unemployment_quarterly — schema + coverage + sample")
print("─" * 72)
try:
    cols = conn.execute("PRAGMA table_info(abs_sa2_unemployment_quarterly)").fetchall()
    print("  Columns:")
    for c in cols:
        print(f"    {c['name']}: {c['type']}")
    print()

    n = conn.execute("SELECT COUNT(*) FROM abs_sa2_unemployment_quarterly").fetchone()[0]
    print(f"  Total rows: {n:,}")

    sa2_n = conn.execute(
        "SELECT COUNT(DISTINCT sa2_code) FROM abs_sa2_unemployment_quarterly"
    ).fetchone()[0]
    print(f"  Distinct SA2s: {sa2_n:,}")

    period_range = conn.execute("""
        SELECT MIN(period_label) AS min_p, MAX(period_label) AS max_p,
               COUNT(DISTINCT period_label) AS n_periods
        FROM abs_sa2_unemployment_quarterly
    """).fetchone()
    print(f"  Period range: {period_range['min_p']} → {period_range['max_p']}")
    print(f"  Distinct periods: {period_range['n_periods']}")

    print()
    print("  Sample row (3 rows for any SA2):")
    sample = conn.execute("""
        SELECT * FROM abs_sa2_unemployment_quarterly
        WHERE sa2_code = (
            SELECT sa2_code FROM abs_sa2_unemployment_quarterly LIMIT 1
        )
        ORDER BY period_label
        LIMIT 3
    """).fetchall()
    for s in sample:
        print(f"    {dict(s)}")

except sqlite3.OperationalError as e:
    print(f"  ERROR: {e}")
print()

# 4. Search for any column named like 'lfp' or 'participation' or
#    'labour_force' anywhere in the DB (sibling-column hypothesis)
print("─" * 72)
print("4. Columns named like LFP/participation across all tables")
print("─" * 72)
candidate_terms = ("lfp", "participation", "labour_force", "labor_force", "labour_for")
matches = []
for tbl_row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
    tbl = tbl_row["name"]
    try:
        for c in conn.execute(f"PRAGMA table_info({tbl})").fetchall():
            cn = c["name"].lower()
            if any(term in cn for term in candidate_terms):
                matches.append((tbl, c["name"], c["type"]))
    except sqlite3.OperationalError:
        continue
if matches:
    for tbl, col, typ in matches:
        print(f"  {tbl}.{col} ({typ})")
else:
    print("  (none found)")
print()

# 5. Provenance row inspection — JSA SALM-related ingest_run rows
print("─" * 72)
print("5. JSA / SALM provenance rows in *_ingest_run tables (if any)")
print("─" * 72)
provenance_tables = []
for tbl_row in conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%ingest_run%'"
).fetchall():
    provenance_tables.append(tbl_row["name"])

if not provenance_tables:
    print("  (no *_ingest_run tables found)")
else:
    for tbl in provenance_tables:
        try:
            rows = conn.execute(
                f"SELECT * FROM {tbl} WHERE lower(coalesce(source, '')) LIKE '%jsa%' "
                f"OR lower(coalesce(source, '')) LIKE '%salm%' LIMIT 5"
            ).fetchall()
            if rows:
                print(f"  {tbl}:")
                for r in rows:
                    print(f"    {dict(r)}")
        except sqlite3.OperationalError:
            continue

print()
print("=" * 72)
print("Probe complete. Capture this output and paste into")
print("  recon/layer4_3_sub_pass_4_3_2_probe.md")
print("=" * 72)

conn.close()
