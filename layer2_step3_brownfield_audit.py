# layer2_step3_brownfield_audit.py — read-only
# Characterise date-format scope in services for brownfield re-classification.
import os, sqlite3, re, datetime
from collections import Counter

DB = os.path.join("data", "kintell.db")
OUT = os.path.join("recon", "layer2_step3_brownfield_audit_findings.md")

DATE_COLS = ["last_transfer_date", "approval_granted_date"]

# Format detectors
PAT_YYYY_MM_DD = re.compile(r"^\d{4}-\d{2}-\d{2}( \d{2}:\d{2}:\d{2})?$")
PAT_DD_MM_YYYY = re.compile(r"^\d{2}/\d{2}/\d{4}$")
PAT_DD_MM_YY = re.compile(r"^\d{2}/\d{2}/\d{2}$")
PAT_MON_YYYY = re.compile(r"^[A-Za-z]{3}-\d{4}$")  # e.g. Feb-2023

def classify(v):
    if v is None or v == "":
        return "null_or_empty"
    s = str(v).strip()
    if PAT_YYYY_MM_DD.match(s):
        return "YYYY-MM-DD"
    if PAT_DD_MM_YYYY.match(s):
        return "DD/MM/YYYY"
    if PAT_DD_MM_YY.match(s):
        return "DD/MM/YY"
    if PAT_MON_YYYY.match(s):
        return "Mon-YYYY"
    return f"other"

lines = []
def emit(s=""):
    print(s)
    lines.append(s)

emit("# Phase 2.5 Layer 2 Step 3 — Brownfield Audit Findings")
emit(f"_Generated: {datetime.datetime.now().isoformat(timespec='seconds')}_")
emit("")
emit("Read-only characterisation of date-format scope across the two")
emit("transfer/approval date columns that drive brownfield classification.")
emit("Source bug (this session): centre_page.py v1's `_parse_date()` only")
emit("recognised YYYY-MM-DD; DD/MM/YYYY values silently fell through and")
emit("brownfield centres were misclassified as greenfield.")
emit("")

conn = sqlite3.connect(DB)
cur = conn.cursor()

# Confirm columns exist
cur.execute("PRAGMA table_info(services);")
existing = {c[1] for c in cur.fetchall()}
emit("## Column existence")
for c in DATE_COLS:
    emit(f"  - {c:<30} {'PRESENT' if c in existing else 'MISSING'}")
emit("")

active_total = cur.execute("SELECT COUNT(*) FROM services WHERE is_active=1;").fetchone()[0]
emit(f"## Active services total: {active_total:,}")
emit("")

for col in DATE_COLS:
    if col not in existing:
        continue
    emit(f"## `{col}`")
    cur.execute(f"SELECT {col} FROM services WHERE is_active=1;")
    vals = [r[0] for r in cur.fetchall()]
    fmts = Counter(classify(v) for v in vals)
    emit(f"  format distribution (active services):")
    for fmt, n in fmts.most_common():
        pct = n / active_total * 100
        emit(f"    {fmt:<20} {n:>6}  ({pct:5.1f}%)")
    # Sample values per format
    samples = {}
    for v in vals:
        f = classify(v)
        if f not in samples:
            samples[f] = []
        if len(samples[f]) < 3 and v not in (None, ""):
            samples[f].append(v)
    emit(f"  sample values per format:")
    for f, ss in samples.items():
        if f == "null_or_empty":
            continue
        emit(f"    {f:<20} {ss}")
    emit("")

# Cross-tab — what's the overlap between approval_granted_date and last_transfer_date formats?
emit("## Cross-tab: approval_granted_date format X last_transfer_date format")
cur.execute("""
SELECT approval_granted_date, last_transfer_date
  FROM services WHERE is_active=1;
""")
ct = Counter()
for ag, tr in cur.fetchall():
    ct[(classify(ag), classify(tr))] += 1
# print as a table
agf = sorted({k[0] for k in ct.keys()})
trf = sorted({k[1] for k in ct.keys()})
header = "approval_granted_date \\ last_transfer_date"
emit(f"  {header}")
hdr = " " * 24 + "  ".join(f"{f:>14}" for f in trf)
emit(f"  {hdr}")
for af in agf:
    row = f"  {af:<24}"
    for tf in trf:
        row += f"  {ct.get((af, tf), 0):>14}"
    emit(row)
emit("")

# Misclassification scope — services that *would be* classified differently
# under a YYYY-MM-DD-only parser vs a multi-format parser
emit("## Misclassification scope (if parser is YYYY-MM-DD-only)")
emit("")
emit("Brownfield = service has a non-null transfer_date older than approval_granted.")
emit("A YYYY-MM-DD-only parser fails on DD/MM/YYYY values, treating them as null.")
emit("So: services with DD/MM/YYYY in last_transfer_date are mis-marked greenfield.")
emit("")
cur.execute("""
SELECT COUNT(*) FROM services
 WHERE is_active=1
   AND last_transfer_date IS NOT NULL
   AND TRIM(last_transfer_date) != '';
""")
total_with_transfer = cur.fetchone()[0]
emit(f"  active services with any last_transfer_date    : {total_with_transfer:,}")

cur.execute("SELECT last_transfer_date FROM services WHERE is_active=1;")
ddmm = sum(1 for (v,) in cur.fetchall() if classify(v) == "DD/MM/YYYY")
emit(f"  active services with DD/MM/YYYY last_transfer  : {ddmm:,}")
emit(f"  -> services likely mis-marked greenfield by buggy parser: {ddmm:,}")
emit("")

# Same analysis for approval_granted_date (used for centre age)
cur.execute("SELECT approval_granted_date FROM services WHERE is_active=1;")
ag_ddmm = sum(1 for (v,) in cur.fetchall() if classify(v) == "DD/MM/YYYY")
emit(f"  active services with DD/MM/YYYY approval_granted: {ag_ddmm:,}")
emit(f"  -> services with unparsed approval date by buggy parser: {ag_ddmm:,}")
emit("")

# Sample of misclassified services (DD/MM/YYYY transfer + a real entity)
emit("## Sample of likely-misclassified services (showing 10)")
cur.execute("""
SELECT service_id, service_name, last_transfer_date, approval_granted_date
  FROM services WHERE is_active=1
   AND last_transfer_date LIKE '__/__/____';
""")
samples = cur.fetchall()
for r in samples[:10]:
    emit(f"  id={r[0]:<6} '{r[1][:40]}' transfer={r[2]} approval={r[3]}")
emit(f"  (total candidates: {len(samples):,})")
emit("")

# Code-path audit: where are these columns read in the codebase?
# We can't search code from here, so just enumerate likely consumers.
emit("## Code-path audit checklist")
emit("")
emit("The data shows DD/MM/YYYY values exist; impact depends on parser robustness")
emit("in each consuming code path. Patrick to confirm format handling in:")
emit("  - operator_page.py        (uses last_transfer_date for brownfield logic)")
emit("  - generate_dashboard.py   (places-over-time, growth metrics)")
emit("  - centre_page.py v2       (already fixed — handles DD/MM/YYYY)")
emit("  - any module*.py that reads services date columns")
emit("")
emit("Recommended grep:")
emit("  Get-ChildItem -Recurse -Filter *.py | Select-String 'last_transfer_date|approval_granted_date'")
emit("")

conn.close()

os.makedirs("recon", exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"\n[wrote {OUT}]")
