# layer2_step1_preflight.py
# Phase 2.5 Layer 2 Step 1 — SA2 backfill PREFLIGHT (read-only)
# No mutations. Confirms services schema, postcode/latlng coverage, and join shape.
import os, sqlite3, csv, datetime, sys

DB = os.path.join("data", "kintell.db")
CONCORDANCE = os.path.join("abs_data", "postcode_to_sa2_concordance.csv")
OUT = os.path.join("recon", "layer2_step1_preflight.md")

lines = []
def emit(s=""):
    print(s)
    lines.append(s)

emit("# Layer 2 Step 1 — SA2 Backfill Preflight (read-only)")
emit(f"_Generated: {datetime.datetime.now().isoformat(timespec='seconds')}_")
emit("")

# 1. services schema
conn = sqlite3.connect(DB)
cur = conn.cursor()
emit("## services schema (columns relevant to backfill)")
cur.execute("PRAGMA table_info(services);")
cols = cur.fetchall()
relevant = ("postcode", "latitude", "longitude", "lat", "lng",
            "sa2_code", "sa2_name", "service_approval_number",
            "service_id", "is_active")
have = {}
for c in cols:
    name = c[1]
    if name.lower() in relevant or "postcode" in name.lower() or "lat" in name.lower() or "lng" in name.lower() or "lon" in name.lower() or "sa2" in name.lower():
        emit(f"  - {name:<30} {c[2]:<10} pk={c[5]} notnull={c[3]}")
        have[name.lower()] = name
emit("")

# 2. Coverage on active services
emit("## Coverage on active services")
def cov(col, label=None):
    label = label or col
    try:
        cur.execute(f"SELECT COUNT(*) FROM services WHERE is_active=1 AND {col} IS NOT NULL AND TRIM(CAST({col} AS TEXT)) != '';")
        n = cur.fetchone()[0]
        emit(f"  {label:<30} {n:>6}/18223 ({n/18223*100:5.1f}%)")
        return n
    except Exception as e:
        emit(f"  {label:<30} ERROR: {e}")
        return None

cov("postcode")
cov("lat")
cov("lng")
cov("sa2_code", "sa2_code (current)")
cov("sa2_name", "sa2_name (current)")
emit("")

# 3. Concordance load
emit("## Concordance load")
if not os.path.exists(CONCORDANCE):
    emit(f"FATAL: {CONCORDANCE} missing")
    sys.exit(1)
pc_to_sa2 = {}
with open(CONCORDANCE, "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        pc = row["POSTCODE"].strip()
        # Normalize to 4-digit
        if pc.isdigit():
            pc = pc.zfill(4)
        pc_to_sa2[pc] = (row["SA2_CODE"].strip(), row["SA2_NAME"].strip())
emit(f"  unique postcodes in concordance: {len(pc_to_sa2):,}")
sample = list(pc_to_sa2.items())[:5]
for k, v in sample:
    emit(f"    {k} -> {v}")
emit("")

# 4. Simulate join
emit("## Simulated join: services.postcode -> concordance.SA2_CODE")
cur.execute("SELECT service_id, postcode, lat, lng FROM services WHERE is_active=1;")
rows = cur.fetchall()
matched = 0
no_postcode = 0
orphan_pc = []
matched_sample = []
for sid, pc, lat, lng in rows:
    if pc is None or str(pc).strip() == "":
        no_postcode += 1
        continue
    pcnorm = str(pc).strip()
    if pcnorm.replace(".0", "").isdigit():
        pcnorm = pcnorm.replace(".0", "").zfill(4)
    if pcnorm in pc_to_sa2:
        matched += 1
        if len(matched_sample) < 3:
            matched_sample.append((sid, pcnorm, pc_to_sa2[pcnorm]))
    else:
        orphan_pc.append((sid, pcnorm, lat, lng))

emit(f"  total active services         : {len(rows):,}")
emit(f"  matched on postcode           : {matched:,} ({matched/len(rows)*100:.2f}%)")
emit(f"  no postcode populated         : {no_postcode:,}")
emit(f"  orphan (postcode not in conc) : {len(orphan_pc):,}")
emit("")
emit("  sample matches:")
for s in matched_sample:
    emit(f"    service_id={s[0]} pc={s[1]} -> sa2={s[2]}")
emit("")

# 5. Orphan postcode breakdown — top 20
emit("## Orphan postcodes (top 20 by service count)")
from collections import Counter
orphan_counts = Counter(p[1] for p in orphan_pc)
for pc, n in orphan_counts.most_common(20):
    # show one sample lat/lng
    sample = next((o for o in orphan_pc if o[1] == pc), None)
    emit(f"  {pc:<8} {n:>4} services  e.g. service_id={sample[0]} lat={sample[2]} lng={sample[3]}")
emit("")

# 6. Plan summary
total = len(rows)
expected_matched = matched
expected_unfilled = no_postcode + len(orphan_pc)
emit("## Apply-script projected effect")
emit(f"  UPDATE services SET sa2_code, sa2_name on  : {expected_matched:,} active services")
emit(f"  Will leave NULL on                          : {expected_unfilled:,} (postcode missing or orphan)")
emit(f"  Coverage after backfill                     : {expected_matched/total*100:.2f}% active services")
emit(f"  Gap from 100% requires lat/lng polygon lookup (deferred — no SA2 polygon file in abs_data)")
emit("")

conn.close()

os.makedirs("recon", exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"\n[wrote {OUT}]")

