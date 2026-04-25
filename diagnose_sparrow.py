"""
diagnose_sparrow.py  (v3)
────────────────────────────────────────────────────────────────
Phase 1 — Sparrow case diagnostic.

v3 changes:
  - CSV columns are lowercase with no spaces (servicename,
    providerlegalname, provider_approval_number, etc.)
  - ACECQA snapshot has no ABN column. Use provider_approval_number
    as the joining key instead.

Read-only. Run from: C:\\Users\\Patrick Bell\\remara-agent
"""

import csv
import json
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent
OPERATORS_FILE = ROOT / "operators_target_list.json"
SNAPSHOT_FILE  = ROOT / "data" / "services_snapshot.csv"

SEARCH_TERM    = "sparrow"
BRAND_PREFIXES = ("sparrow early learning", "sparrow nest")


def print_header(title):
    line = "=" * 72
    print(f"\n{line}\n {title}\n{line}")


def norm(s):
    return (s or "").strip().lower()


# === Load sources ====================================================
operators = []
if OPERATORS_FILE.exists():
    with OPERATORS_FILE.open(encoding="utf-8") as f:
        operators = json.load(f)
    if isinstance(operators, dict):
        operators = list(operators.values())

rows = []
columns = []
if SNAPSHOT_FILE.exists():
    with SNAPSHOT_FILE.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames or []
        rows = list(reader)

# Column shortcuts (v3 — lowercase, no spaces)
SERVICE_COL  = "servicename"
PROVIDER_COL = "providerlegalname"
STATE_COL    = "state"
SUBURB_COL   = "suburb"
SAP_COL      = "serviceapprovalnumber"
PAP_COL      = "provider_approval_number"
PLACES_COL   = "numberofapprovedplaces"


# === PART A: Sparrow records in operators_target_list.json ===========
print_header(f"A. TARGET-LIST RECORDS MATCHING '{SEARCH_TERM}'")

def recursive_search(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            np = f"{path}.{k}" if path else k
            yield from recursive_search(v, np)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from recursive_search(v, f"{path}[{i}]")
    elif isinstance(obj, str) and SEARCH_TERM in obj.lower():
        yield path, obj

target_matches = []
for i, rec in enumerate(operators):
    if not isinstance(rec, dict):
        continue
    if list(recursive_search(rec)):
        target_matches.append((i, rec))

total_centres = 0
total_sparrow_branded = 0
for idx, rec in target_matches:
    n = len(rec.get("centres") or [])
    total_centres += n
    sb = sum(1 for c in (rec.get("centres") or [])
             if any(p in norm(c.get("service_name"))
                    for p in BRAND_PREFIXES))
    total_sparrow_branded += sb
    print(f"  #{idx:<5} {rec.get('legal_name','(none)'):50s}"
          f"  centres={n:<3}  sparrow-branded={sb}")

print(f"\n  Records matching: {len(target_matches)}")
print(f"  Total centres in those records: {total_centres}")
print(f"  Of which Sparrow-branded (by service_name): "
      f"{total_sparrow_branded}")


# === PART B: Sparrow-branded services in ACECQA ======================
print_header("B. ACECQA SERVICES WITH SPARROW BRAND IN SERVICE_NAME")

if not rows:
    print("  [X] snapshot empty or not found")
else:
    print(f"  File: {SNAPSHOT_FILE}")
    print(f"  Rows: {len(rows)}")

    branded = [r for r in rows
               if any(p in norm(r.get(SERVICE_COL))
                      for p in BRAND_PREFIXES)]

    print(f"\n  Sparrow-branded ACECQA centres: {len(branded)}")

    by_prov = defaultdict(list)
    for r in branded:
        key = (r.get(PROVIDER_COL) or "(unknown)").strip()
        by_prov[key].append(r)

    paps_all = sorted({(r.get(PAP_COL) or "").strip()
                       for r in branded if r.get(PAP_COL)})

    print(f"  Distinct Provider Legal Names: {len(by_prov)}")
    print(f"  Distinct Provider Approval #s: {len(paps_all)}")

    print(f"\n  --- Breakdown by provider ---")
    for prov, recs in sorted(by_prov.items(), key=lambda x: -len(x[1])):
        paps = sorted({(r.get(PAP_COL) or "").strip()
                       for r in recs if r.get(PAP_COL)})
        states = sorted({(r.get(STATE_COL) or "").strip()
                         for r in recs if r.get(STATE_COL)})
        total_places = 0
        for r in recs:
            try:
                total_places += int(r.get(PLACES_COL) or 0)
            except ValueError:
                pass
        print(f"\n    {prov}")
        print(f"      Centres : {len(recs)}")
        print(f"      Places  : {total_places}")
        if paps:   print(f"      PA(s)   : {', '.join(paps)}")
        if states: print(f"      States  : {', '.join(states)}")
        for r in recs[:4]:
            loc = r.get(SUBURB_COL, "")
            st  = r.get(STATE_COL, "")
            print(f"        - {r.get(SERVICE_COL,'')}  ({loc} {st})".rstrip())
        if len(recs) > 4:
            print(f"        ... and {len(recs) - 4} more")


# === PART C: Cross-reference ACECQA Sparrow -> target-list record ====
print_header("C. CROSS-REFERENCE: ACECQA SPARROW -> TARGET-LIST RECORD")

if rows and operators:
    sap_to_rec  = {}
    ns_to_rec   = {}
    pap_to_rec  = defaultdict(set)

    for idx, rec in enumerate(operators):
        if not isinstance(rec, dict):
            continue
        # Collect provider approval numbers declared on the group record
        for pn in (rec.get("provider_numbers") or []):
            pap_to_rec[str(pn).strip()].add(
                (idx, rec.get("legal_name")))
        for c in (rec.get("centres") or []):
            if not isinstance(c, dict):
                continue
            sap = (c.get("service_approval_number")
                   or c.get("service_approval")
                   or c.get("svc_approval_number")
                   or "").strip()
            if sap:
                sap_to_rec[sap] = (idx, rec.get("legal_name"))
            nm = norm(c.get("service_name"))
            st = norm(c.get("state"))
            if nm:
                ns_to_rec[(nm, st)] = (idx, rec.get("legal_name"))

    matched_sap  = 0
    matched_ns   = 0
    matched_pap  = 0
    orphans      = []

    for row in rows:
        svc = norm(row.get(SERVICE_COL))
        if not any(p in svc for p in BRAND_PREFIXES):
            continue

        sap = (row.get(SAP_COL) or "").strip()
        pap = (row.get(PAP_COL) or "").strip()
        st  = norm(row.get(STATE_COL))
        nm  = norm(row.get(SERVICE_COL))

        hit = None
        reason = None
        if sap and sap in sap_to_rec:
            hit = sap_to_rec[sap]; reason = "SAP"
            matched_sap += 1
        elif (nm, st) in ns_to_rec:
            hit = ns_to_rec[(nm, st)]; reason = "name+state"
            matched_ns += 1
        elif pap and pap in pap_to_rec:
            hits = pap_to_rec[pap]
            hit = next(iter(hits)); reason = "PA#"
            matched_pap += 1

        if not hit:
            orphans.append(row)

    print(f"  Matched via service approval number  : {matched_sap}")
    print(f"  Matched via (service_name, state)    : {matched_ns}")
    print(f"  Matched via provider approval number : {matched_pap}")
    print(f"  ORPHAN Sparrow centres (no match)    : {len(orphans)}")

    for r in orphans[:25]:
        svc  = r.get(SERVICE_COL, "")
        st   = r.get(STATE_COL, "")
        prov = r.get(PROVIDER_COL, "")
        pap  = r.get(PAP_COL, "")
        print(f"    - {svc}  ({st})")
        print(f"        AP legal name: {prov}")
        print(f"        PA #        : {pap}")
    if len(orphans) > 25:
        print(f"    ... and {len(orphans) - 25} more")

print_header("END")
