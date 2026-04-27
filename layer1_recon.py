# layer1_recon.py
# Phase 2.5 Layer 1 — DB inventory + silent-bug audit (read-only)
# No mutations. Prints to stdout AND writes recon\layer1_db_findings.md
import sqlite3, os, sys, datetime

DB = os.path.join("data", "kintell.db")
OUT = os.path.join("recon", "layer1_db_findings.md")

TABLES_OF_INTEREST = [
    "service_snapshots",
    "entity_snapshots",
    "group_snapshots",
    "regulatory_events",
    "service_catchment_cache",
    "service_tenures",
    "properties",
    "people",
    "person_roles",
    "financials",
]

lines = []
def emit(s=""):
    print(s)
    lines.append(s)

emit(f"# Phase 2.5 Layer 1 — DB Recon Findings")
emit(f"_Generated: {datetime.datetime.now().isoformat(timespec='seconds')}_")
emit(f"_DB: `{DB}`_")
emit("")

if not os.path.exists(DB):
    emit(f"FATAL: {DB} not found.")
    sys.exit(1)

conn = sqlite3.connect(DB)
cur = conn.cursor()

# All tables in DB
emit("## All tables in DB")
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
all_tables = [r[0] for r in cur.fetchall()]
emit(f"Total tables: {len(all_tables)}")
for t in all_tables:
    emit(f"  - {t}")
emit("")

# Per-table inventory
emit("## Inventory of snapshot/history/regulatory tables")
emit("")
for t in TABLES_OF_INTEREST:
    emit(f"### `{t}`")
    if t not in all_tables:
        emit(f"  STATUS: TABLE DOES NOT EXIST")
        emit("")
        continue
    try:
        cur.execute(f"SELECT COUNT(*) FROM {t};")
        rc = cur.fetchone()[0]
    except Exception as e:
        emit(f"  rowcount ERROR: {e}")
        emit("")
        continue
    emit(f"  rowcount: {rc}")
    cur.execute(f"PRAGMA table_info({t});")
    cols = cur.fetchall()
    emit(f"  columns ({len(cols)}):")
    for c in cols:
        # cid, name, type, notnull, dflt, pk
        emit(f"    - {c[1]:<35} {c[2]:<15} pk={c[5]} notnull={c[3]}")
    # Per-column non-null coverage when rc > 0
    if rc > 0:
        emit(f"  non-null coverage (count where col IS NOT NULL):")
        for c in cols:
            cn = c[1]
            try:
                cur.execute(f"SELECT COUNT({cn}) FROM {t};")
                nn = cur.fetchone()[0]
                pct = (nn / rc * 100) if rc else 0
                emit(f"    - {cn:<35} {nn:>8}  ({pct:5.1f}%)")
            except Exception as e:
                emit(f"    - {cn:<35} ERROR: {e}")
    emit("")

# Silent-bug audit
emit("## Silent-bug audit queries")
emit("")

audits = [
    ("seifa_decile / sa2_code coverage on active services",
     """SELECT COUNT(*) AS total,
               COUNT(seifa_decile) AS with_seifa,
               COUNT(sa2_code) AS with_sa2
        FROM services WHERE is_active = 1;"""),
    ("transfer_date population on active services",
     """SELECT COUNT(*) AS active_services,
               SUM(CASE WHEN last_transfer_date IS NOT NULL
                          AND last_transfer_date != ''
                        THEN 1 ELSE 0 END) AS with_transfer
        FROM services WHERE is_active = 1;"""),
    ("entities with active services but group_id IS NULL",
     """SELECT COUNT(DISTINCT e.entity_id) AS orphan_entities
        FROM entities e
        JOIN services s ON s.entity_id = e.entity_id
        WHERE s.is_active = 1
          AND e.group_id IS NULL;"""),
]

for label, sql in audits:
    emit(f"### {label}")
    emit("```sql")
    emit(sql.strip())
    emit("```")
    try:
        cur.execute(sql)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description]
        emit("Result:")
        emit("  " + " | ".join(cols))
        for r in rows:
            emit("  " + " | ".join(str(v) for v in r))
    except Exception as e:
        emit(f"ERROR: {e}")
    emit("")

# Bonus: list all tables not yet inventoried so we know what else exists
emit("## Other tables in DB (not in scope but listed for completeness)")
others = [t for t in all_tables if t not in TABLES_OF_INTEREST]
for t in others:
    try:
        cur.execute(f"SELECT COUNT(*) FROM {t};")
        rc = cur.fetchone()[0]
        emit(f"  - {t:<40} rowcount={rc}")
    except Exception as e:
        emit(f"  - {t:<40} ERROR: {e}")

conn.close()

os.makedirs("recon", exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"\n[wrote {OUT}]")
