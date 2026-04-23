"""
tier2_diagnose.py  v1
────────────────────────────────────────────────────────────────
Phase B read-only diagnostic for the Tier 2 NQS ingest.

Answers five questions before we touch the DB:
  1. How many Service Approval Numbers in NQS Data Q4 2025 match
     services in kintell.db? Any mismatches?
  2. What Provider Management Type values exist, and how do they
     map to the ownership_type scheme ('private','nfp','government')?
  3. What's the coverage of each candidate field in the NQS file?
     (ARIA+, SEIFA, Lat/Lng, Service Sub Type, Final Report Sent Date)
  4. Does the NQS file contain services NOT in kintell.db, or vice
     versa? (Informs whether a pure UPDATE is safe, or whether we
     need INSERT+UPDATE logic.)
  5. Distribution of Service Sub Type and ARIA+ values (so we know
     what the Remoteness card will actually show).

NO WRITES. This is the "you approve before we mutate" checkpoint.
"""

import sqlite3
from collections import Counter
from pathlib import Path

import openpyxl

ROOT    = Path(__file__).resolve().parent
DB_PATH = ROOT / "data" / "kintell.db"
XLSX    = ROOT / "abs_data" / "NQS Data Q4 2025.XLSX"

# Candidate field columns in the NQS file we want to bring across.
# Header strings are exact — confirmed from nqs_xlsx_inspect.json.
FIELDS_OF_INTEREST = [
    "Service Approval Number",
    "Service Name",
    "Provider ID",
    "Provider Name",
    "Provider Management Type",
    "Service Type",
    "Service Sub Type",
    "Approval Date",
    "Final Report Sent Date",
    "Maximum total places",
    "SEIFA",
    "ARIA+",
    "Latitude",
    "Longitude",
    "Overall Rating",
    "Postcode",
    "Quality Area 1",
    "Quality Area 2",
    "Quality Area 3",
    "Quality Area 4",
    "Quality Area 5",
    "Quality Area 6",
    "Quality Area 7",
]


def read_nqs():
    print(f"\n── Reading {XLSX.name} (Approved Services sheet) ──")
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    ws = wb["Approved Services"]
    rows_iter = ws.iter_rows(values_only=True)
    headers = list(next(rows_iter))

    # Map each field-of-interest to its column index, or None if missing
    col_ix = {f: (headers.index(f) if f in headers else None)
              for f in FIELDS_OF_INTEREST}

    missing = [f for f, ix in col_ix.items() if ix is None]
    if missing:
        print(f"  WARNING: columns not found in file: {missing}")
    print(f"  Headers found: {sum(1 for ix in col_ix.values() if ix is not None)}"
          f" / {len(FIELDS_OF_INTEREST)}")

    # Read all rows into a list of dicts keyed by FIELDS_OF_INTEREST
    records = []
    for row in rows_iter:
        rec = {}
        for f, ix in col_ix.items():
            rec[f] = row[ix] if ix is not None and ix < len(row) else None
        records.append(rec)

    wb.close()
    print(f"  Data rows read: {len(records)}")
    return records


def coverage(records, field):
    """Count non-null / non-empty values for a field."""
    n = sum(1 for r in records
            if r.get(field) not in (None, "", " ") and str(r.get(field)).strip())
    return n, len(records)


def fetch_kintell_services():
    conn = sqlite3.connect(str(DB_PATH))
    rows = conn.execute(
        "SELECT service_id, service_approval_number, service_name, "
        "       suburb, state, postcode, approved_places, "
        "       is_active, entity_id "
        "  FROM services"
    ).fetchall()
    # Also entity→group mapping, so we can report group-level counts
    ent_rows = conn.execute(
        "SELECT entity_id, group_id FROM entities"
    ).fetchall()
    conn.close()
    ent_to_group = dict(ent_rows)
    return rows, ent_to_group


def main():
    # ── Load the NQS file ────────────────────────────────────────
    records = read_nqs()

    # ── Field coverage ───────────────────────────────────────────
    print("\n── Field coverage in NQS file ──")
    for f in FIELDS_OF_INTEREST:
        n, total = coverage(records, f)
        pct = 100.0 * n / total if total else 0
        print(f"  {f:35} {n:>6} / {total}   ({pct:5.1f}%)")

    # ── Service Approval Number match against kintell.db ────────
    print("\n── Service Approval Number match vs kintell.db ──")
    rows, ent_to_group = fetch_kintell_services()
    db_sans = {r[1]: r for r in rows if r[1]}
    print(f"  kintell.db services total         : {len(rows):>6}")
    print(f"  kintell.db with non-null SAP#     : {len(db_sans):>6}")

    nqs_sans = {r["Service Approval Number"]: r for r in records
                if r.get("Service Approval Number")}
    print(f"  NQS rows with non-null SAP#       : {len(nqs_sans):>6}")

    matched    = set(db_sans.keys()) & set(nqs_sans.keys())
    db_only    = set(db_sans.keys()) - set(nqs_sans.keys())
    nqs_only   = set(nqs_sans.keys()) - set(db_sans.keys())
    print(f"  Matched (both)                    : {len(matched):>6}")
    print(f"  In DB but not in NQS file         : {len(db_only):>6}")
    print(f"  In NQS file but not in DB         : {len(nqs_only):>6}")

    match_pct = 100.0 * len(matched) / len(db_sans) if db_sans else 0
    print(f"  Match rate (DB services covered)  : {match_pct:5.1f}%")

    # ── Provider Management Type distribution ───────────────────
    print("\n── Provider Management Type distribution (full NQS file) ──")
    pmt_counts = Counter(
        (r.get("Provider Management Type") or "(null)")
        for r in records
    )
    for label, count in pmt_counts.most_common():
        print(f"  {label:55} {count:>6}")

    # Suggested mapping
    print("\n  Proposed mapping to groups.ownership_type:")
    mapping = []
    for label in pmt_counts:
        lo = label.lower()
        if "not for profit" in lo or "non-profit" in lo or "nonprofit" in lo:
            target = "nfp"
        elif "government" in lo or "state" in lo or "department" in lo:
            target = "government"
        elif "private" in lo or "for profit" in lo:
            target = "private"
        elif label == "(null)":
            target = "(leave as unknown)"
        else:
            target = "(review manually)"
        mapping.append((label, target, pmt_counts[label]))
    for label, target, n in sorted(mapping, key=lambda x: -x[2]):
        print(f"    {label:55} → {target}   ({n})")

    # ── ARIA+ distribution ──────────────────────────────────────
    print("\n── ARIA+ distribution (full NQS file) ──")
    aria_counts = Counter((r.get("ARIA+") or "(null)") for r in records)
    for label, count in aria_counts.most_common():
        print(f"  {label:40} {count:>6}")

    # ── Service Sub Type distribution ───────────────────────────
    print("\n── Service Sub Type distribution (full NQS file) ──")
    sst_counts = Counter((r.get("Service Sub Type") or "(null)") for r in records)
    for label, count in sst_counts.most_common():
        print(f"  {label:40} {count:>6}")

    # ── SEIFA value range ───────────────────────────────────────
    print("\n── SEIFA value inspection ──")
    seifa_vals = [r.get("SEIFA") for r in records if r.get("SEIFA") is not None]
    if seifa_vals:
        # Force to int where possible
        ints = []
        others = []
        for v in seifa_vals:
            try:
                ints.append(int(v))
            except (ValueError, TypeError):
                others.append(v)
        if ints:
            print(f"  Numeric values    : {len(ints)}")
            print(f"  Min / Max         : {min(ints)} / {max(ints)}")
            sdist = Counter(ints)
            for k in sorted(sdist):
                print(f"    decile {k:>2}      {sdist[k]:>6}")
        if others:
            print(f"  Non-numeric       : {len(others)}  samples: {others[:5]}")
    else:
        print("  No SEIFA values present")

    # ── Lat/Lng presence ────────────────────────────────────────
    print("\n── Lat/Lng coverage ──")
    both = sum(1 for r in records
               if r.get("Latitude") is not None and r.get("Longitude") is not None)
    print(f"  Both present      : {both}")
    print(f"  Rows in file      : {len(records)}")
    print(f"  Coverage          : {100.0*both/len(records):.1f}%")

    # ── Final Report Sent Date coverage ─────────────────────────
    print("\n── Final Report Sent Date (rating_issued_date source) ──")
    frsd_n = sum(1 for r in records if r.get("Final Report Sent Date"))
    # Sample a few to see format
    samples = [r.get("Final Report Sent Date") for r in records
               if r.get("Final Report Sent Date")][:5]
    print(f"  Populated         : {frsd_n} / {len(records)} ({100.0*frsd_n/len(records):.1f}%)")
    print(f"  Sample values     : {[str(s) for s in samples]}")

    # ── Group-level impact preview ──────────────────────────────
    print("\n── Group-level impact preview ──")
    # For each group in DB, find what ownership_type it would get
    # based on the plurality of its services' Provider Management Type
    group_pmts = {}
    for sap in matched:
        db_row = db_sans[sap]
        entity_id = db_row[8]
        gid = ent_to_group.get(entity_id)
        if gid is None:
            continue
        pmt = nqs_sans[sap].get("Provider Management Type") or "(null)"
        group_pmts.setdefault(gid, Counter())[pmt] += 1

    print(f"  Groups with ≥1 matched service    : {len(group_pmts)}")
    # Show a distribution of what ownership_type each group would get
    derived = Counter()
    for gid, cnt in group_pmts.items():
        top_label, _ = cnt.most_common(1)[0]
        lo = top_label.lower()
        if "not for profit" in lo:
            target = "nfp"
        elif "government" in lo:
            target = "government"
        elif "private" in lo or "for profit" in lo:
            target = "private"
        else:
            target = "(leave as unknown)"
        derived[target] += 1
    print(f"  Ownership-type distribution across {sum(derived.values())} matched groups:")
    for label, count in derived.most_common():
        print(f"    {label:25} {count:>6}")

    # Sparrow + Harmony specifically
    for name, gid in [("Sparrow", 1887), ("Harmony", 236)]:
        c = group_pmts.get(gid, Counter())
        top = c.most_common(3)
        print(f"  {name} (gid {gid}) PMT counts: {top}")

    print("\n── End of diagnostic ──")
    print("Nothing has been written to the database.")


if __name__ == "__main__":
    main()
