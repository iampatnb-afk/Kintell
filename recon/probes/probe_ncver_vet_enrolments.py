"""
recon/probes/probe_ncver_vet_enrolments.py — Layer 4.3 sub-pass 4.3.3 (Thread D)

Read-only probe: is NCVER VET enrolments data for childcare-relevant
qualifications (CHC30121 Cert III, CHC50121 Diploma) already in
kintell.db from earlier panel3 work?

Context: DEC-76 (Workforce supply context block) lists 4 V1 rows.
Three are state-level/national. The fourth — NCVER VET enrolments at
SA2/remoteness — was tracked as OI-20 V1.5 enrichment because it was
unclear whether the data was already ingested. If a relevant table
exists with usable rows, NCVER promotes immediately to a V1 row in
the workforce block (no ingest required, just a renderer wire-up
follow-up sub-pass).

NCVER Total VET Activity (TVA) data is published at SA4 + remoteness
combinations. The relevant qualifications:
  CHC30121 — Cert III in Early Childhood Education and Care
  CHC30113 — Cert III in ECEC (superseded; transition spans 2022-2024)
  CHC50121 — Diploma in Early Childhood Education and Care
  CHC50113 — Diploma in ECEC (superseded)

What this probe answers:
  1. Does any table with 'ncver' / 'vet' / 'tva' / 'enrolment' /
     'qualification' in its name exist?
  2. Do any tables carry rows referencing the four CHC codes above?
  3. What's the row-count + period coverage + geographic resolution
     of any matching table?
  4. Is there a provenance row in *_ingest_run referencing NCVER?

This script READS only. Output basis for recon/layer4_3_sub_pass_
4_3_3_probe.md and the OI-20 follow-up disposition.

Run from repo root:
  python recon/probes/probe_ncver_vet_enrolments.py
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

CHC_CODES = ("CHC30121", "CHC30113", "CHC50121", "CHC50113")

print("=" * 72)
print("NCVER VET enrolments probe (Thread D) — recon read-only")
print("=" * 72)
print(f"DB: {DB_PATH}")
print()

# 1. Tables matching NCVER / VET / training / qualification / enrolment
print("─" * 72)
print("1. Tables with NCVER / VET / TVA / training / qualification keywords")
print("─" * 72)
keywords = ("ncver", "vet_", "_vet", "tva", "training", "qualification", "enrolment", "enrolment", "completion")
tables = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
).fetchall()
candidates = []
for t in tables:
    nm = t["name"].lower()
    if any(k in nm for k in keywords):
        candidates.append(t["name"])

if not candidates:
    print("  (no tables match)")
else:
    for tbl in candidates:
        try:
            n = conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
            print(f"  {tbl}: {n:,} rows")
        except sqlite3.OperationalError as e:
            print(f"  {tbl}: ERROR {e}")
print()

# 2. For each candidate, dump schema + sample
print("─" * 72)
print("2. Schema + sample for each candidate table")
print("─" * 72)
if not candidates:
    print("  (skipped — no candidates)")
for tbl in candidates:
    print(f"\n  TABLE {tbl}")
    try:
        cols = conn.execute(f"PRAGMA table_info({tbl})").fetchall()
        for c in cols:
            print(f"    {c['name']}: {c['type']}")
        sample = conn.execute(f"SELECT * FROM {tbl} LIMIT 3").fetchall()
        print(f"  SAMPLE (first 3 rows):")
        for s in sample:
            print(f"    {dict(s)}")
    except sqlite3.OperationalError as e:
        print(f"    ERROR: {e}")
print()

# 3. Search ALL tables for rows referencing the CHC codes (catches
#    cases where the table name doesn't match our keywords).
print("─" * 72)
print("3. Rows referencing CHC30121 / CHC30113 / CHC50121 / CHC50113")
print("─" * 72)
hits = []
for t in tables:
    tbl = t["name"]
    try:
        for c in conn.execute(f"PRAGMA table_info({tbl})").fetchall():
            if c["type"].upper() in ("TEXT", "VARCHAR") or "CHAR" in c["type"].upper():
                # Try a likely match — code/qualification/program columns
                col = c["name"]
                col_lower = col.lower()
                if any(t in col_lower for t in ("code", "qualif", "program", "course", "level")):
                    for chc in CHC_CODES:
                        n = conn.execute(
                            f"SELECT COUNT(*) FROM {tbl} WHERE {col} = ?",
                            (chc,),
                        ).fetchone()[0]
                        if n > 0:
                            hits.append((tbl, col, chc, n))
    except sqlite3.OperationalError:
        continue

if not hits:
    print("  (no rows found referencing any CHC code)")
else:
    for tbl, col, chc, n in hits:
        print(f"  {tbl}.{col} = '{chc}': {n:,} rows")
print()

# 4. Geographic resolution check — if any candidate table carries
#    sa4/sa2/remoteness columns
print("─" * 72)
print("4. Geographic resolution columns in candidate tables")
print("─" * 72)
geo_cols_target = ("sa4_code", "sa4_name", "sa2_code", "sa2_name", "remoteness", "ra_code", "ra_band", "state")
for tbl in candidates:
    try:
        cols = {c["name"].lower() for c in conn.execute(f"PRAGMA table_info({tbl})").fetchall()}
        present = [g for g in geo_cols_target if g in cols]
        print(f"  {tbl}: {present if present else '(no geographic columns)'}")
    except sqlite3.OperationalError:
        continue
print()

# 5. Provenance rows
print("─" * 72)
print("5. NCVER / VET / TVA references in *_ingest_run tables")
print("─" * 72)
provenance_tables = [
    t["name"] for t in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%ingest_run%'"
    ).fetchall()
]
if not provenance_tables:
    print("  (no *_ingest_run tables)")
else:
    for tbl in provenance_tables:
        try:
            rows = conn.execute(
                f"SELECT * FROM {tbl} WHERE "
                f"lower(coalesce(source, '')) LIKE '%ncver%' OR "
                f"lower(coalesce(source, '')) LIKE '%vet%' OR "
                f"lower(coalesce(source, '')) LIKE '%tva%' "
                f"LIMIT 5"
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
print("  recon/layer4_3_sub_pass_4_3_3_probe.md")
print("=" * 72)

conn.close()
