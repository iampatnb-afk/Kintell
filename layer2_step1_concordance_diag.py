# layer2_step1_concordance_diag.py — read-only
import csv, os
from collections import defaultdict, Counter

CONC = os.path.join("abs_data", "postcode_to_sa2_concordance.csv")

print("=== Concordance diagnostic ===")
total_rows = 0
empty_sa2 = []
empty_name = []
postcode_versions = defaultdict(list)  # postcode -> list of (sa2_code, sa2_name)

with open(CONC, "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    print(f"columns: {reader.fieldnames}")
    for row in reader:
        total_rows += 1
        pc_raw = row.get("POSTCODE", "")
        sa2 = row.get("SA2_CODE", "")
        nm = row.get("SA2_NAME", "")
        pc = pc_raw.strip()
        if pc.isdigit():
            pc = pc.zfill(4)
        postcode_versions[pc].append((sa2.strip(), nm.strip()))
        if sa2.strip() == "":
            empty_sa2.append((pc, nm))
        if nm.strip() == "":
            empty_name.append((pc, sa2))

print(f"\ntotal rows in CSV          : {total_rows:,}")
print(f"unique postcodes (after norm): {len(postcode_versions):,}")
print(f"rows with empty SA2_CODE   : {len(empty_sa2):,}")
print(f"rows with empty SA2_NAME   : {len(empty_name):,}")

# Postcodes with multiple rows
multi = {pc: vs for pc, vs in postcode_versions.items() if len(vs) > 1}
print(f"postcodes with >1 row      : {len(multi):,}")
if multi:
    print("\nFirst 10 multi-mapped postcodes:")
    for pc, vs in list(multi.items())[:10]:
        print(f"  {pc}: {vs}")

# Postcodes where dict-load semantics (last-wins) ended up with empty SA2
problematic = []
for pc, vs in postcode_versions.items():
    final_sa2, final_name = vs[-1]  # what the dict ends up with
    if final_sa2 == "":
        problematic.append((pc, vs))

print(f"\npostcodes where last-wins dict load yields empty SA2: {len(problematic):,}")
if problematic:
    print("First 15:")
    for pc, vs in problematic[:15]:
        print(f"  {pc}: rows={vs}")

# Now intersect with active services to count affected
import sqlite3
conn = sqlite3.connect(os.path.join("data", "kintell.db"))
cur = conn.cursor()
cur.execute("SELECT postcode FROM services WHERE is_active=1 AND postcode IS NOT NULL AND TRIM(postcode) != '';")
service_pcs = []
for (pc,) in cur.fetchall():
    pcn = str(pc).strip()
    if pcn.replace(".0", "").isdigit():
        pcn = pcn.replace(".0", "").zfill(4)
    service_pcs.append(pcn)
conn.close()

problematic_set = {p[0] for p in problematic}
affected = [pc for pc in service_pcs if pc in problematic_set]
print(f"\nactive services hitting an empty-SA2 postcode: {len(affected):,}")
print(f"affected postcode breakdown (top 20):")
for pc, n in Counter(affected).most_common(20):
    print(f"  {pc}: {n} services")
