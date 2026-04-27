"""
Layer 2 Step 5b-prime — T33 LFP extractor (read-only + derive).
================================================================
Scans T33A-H from the 2021 TSP zip, pulls all-ages-aggregate columns
(C{yr}_{sex}_Tot_{Em_Tot|Unem_Tot|Tot_labo_for|Not_LF|LF_NS|Tot})
per (year, sex), computes LFP rate + Unemployment rate +
Employment-to-pop rate, and writes a CSV plus sanity summary.

Output:
  recon/layer2_step5b_prime_t33_derived.csv  (one row per SA2 × year × sex)
  recon/layer2_step5b_prime_t33_extract.md   (sanity summary)

ABS 2021 Census national benchmarks for sanity check:
  Persons LFP ~65.1%, Female LFP ~60.8%, Male LFP ~70.5%
"""

import zipfile
import csv
import io
import re
from pathlib import Path
from collections import defaultdict

ABS_DATA = Path("abs_data")
RECON_DIR = Path("recon")
DERIVED_CSV = RECON_DIR / "layer2_step5b_prime_t33_derived.csv"
EXTRACT_MD = RECON_DIR / "layer2_step5b_prime_t33_extract.md"

# Match: C{11|16|21}_{M|F|P}_Tot_{metric}
TOT_RE = re.compile(
    r"^C(11|16|21)_([MFP])_Tot_(Em_Tot|Unem_Tot|Tot_labo_for|Not_LF|LF_NS|Tot)$"
)

T33_FILE_RE = re.compile(r"T33[A-H]_AUST_SA2")


def find_zip():
    cands = sorted(ABS_DATA.glob("*TSP*.zip"))
    return cands[0] if cands else None


def main():
    RECON_DIR.mkdir(exist_ok=True)
    zp = find_zip()
    if not zp:
        print("ERROR: no TSP zip in abs_data/")
        return

    print(f"Reading: {zp}")

    # Master store: (sa2, year, sex) -> {metric: int_value}
    data = defaultdict(dict)

    with zipfile.ZipFile(zp) as zf:
        t33_files = sorted([n for n in zf.namelist()
                            if T33_FILE_RE.search(n) and n.endswith(".csv")])
        print(f"T33 files: {len(t33_files)}")
        for f in t33_files:
            print(f"  {Path(f).name}")
        print("")

        for fpath in t33_files:
            print(f"[scan] {Path(fpath).name}")
            with zf.open(fpath) as fh:
                text = io.TextIOWrapper(fh, encoding="utf-8-sig", newline="")
                reader = csv.reader(text)
                header = next(reader)

                col_map = []  # list of (idx, year, sex, metric)
                for i, c in enumerate(header):
                    m = TOT_RE.match(c)
                    if m:
                        col_map.append((i, m.group(1), m.group(2), m.group(3)))

                if not col_map:
                    print(f"        no Tot-aggregate cols, skipping")
                    continue

                # Show what we found
                seen_keys = sorted({(y, s) for _, y, s, _ in col_map})
                print(f"        {len(col_map)} cols across (year, sex): {seen_keys}")

                rows_in = 0
                for row in reader:
                    if not row:
                        continue
                    sa2 = row[0]
                    if not sa2 or not sa2.isdigit():
                        continue
                    rows_in += 1
                    for (i, year, sex, metric) in col_map:
                        if i >= len(row):
                            continue
                        v = row[i].strip()
                        if v in ("", "..", "np"):
                            continue
                        try:
                            data[(sa2, year, sex)][metric] = int(v)
                        except ValueError:
                            try:
                                data[(sa2, year, sex)][metric] = int(float(v))
                            except ValueError:
                                pass
                print(f"        rows: {rows_in}")

    print(f"\nTotal (SA2, year, sex) records: {len(data):,}")

    # Write CSV
    rows_written = 0
    skipped_no_pop = 0
    with open(DERIVED_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "sa2_code", "year", "sex",
            "em_tot", "unem_tot", "tot_labo_for", "not_lf", "lf_ns", "pop_15ov",
            "lfp_rate_pct", "unemp_rate_pct", "emp_to_pop_pct",
        ])
        for (sa2, year, sex), m in sorted(data.items()):
            em = m.get("Em_Tot")
            unem = m.get("Unem_Tot")
            lf = m.get("Tot_labo_for")
            nlf = m.get("Not_LF")
            ns = m.get("LF_NS")
            pop = m.get("Tot")

            if pop is None or pop == 0:
                skipped_no_pop += 1
                continue

            denom = (lf or 0) + (nlf or 0)
            lfp_rate = round(100.0 * lf / denom, 2) if (lf is not None and denom) else None
            unemp_rate = round(100.0 * unem / lf, 2) if (lf and unem is not None) else None
            emp_to_pop = round(100.0 * em / denom, 2) if (em is not None and denom) else None

            writer.writerow([sa2, f"20{year}", sex, em, unem, lf, nlf, ns, pop,
                             lfp_rate, unemp_rate, emp_to_pop])
            rows_written += 1

    print(f"Wrote {rows_written:,} rows to {DERIVED_CSV}")
    print(f"Skipped (no pop_15ov): {skipped_no_pop:,}")

    # Build sanity summary
    L = []
    L.append("# T33 LFP Extraction — Sanity Summary")
    L.append("")
    L.append(f"Source: `{zp}`")
    L.append(f"Records (SA2 × year × sex): {len(data):,}")
    L.append(f"Rows in derived CSV: {rows_written:,}")
    L.append(f"Skipped (no pop_15ov): {skipped_no_pop:,}")
    L.append("")
    L.append("## National aggregate by year × sex (sum across all SA2s)")
    L.append("")
    L.append("**Benchmarks (ABS 2021 Census):** Persons LFP ~65.1%, "
             "Female LFP ~60.8%, Male LFP ~70.5%.")
    L.append("")
    L.append("| Year | Sex | Tot LF | Not LF | LF NS | Pop 15+ | LFP rate (%) | Unemp rate (%) |")
    L.append("|-----:|:----|-------:|-------:|------:|--------:|-------------:|---------------:|")

    aggs = defaultdict(lambda: defaultdict(int))
    for (sa2, year, sex), m in data.items():
        for k in ["Em_Tot", "Unem_Tot", "Tot_labo_for", "Not_LF", "LF_NS", "Tot"]:
            v = m.get(k, 0) or 0
            aggs[(year, sex)][k] += v

    for (year, sex) in sorted(aggs.keys()):
        a = aggs[(year, sex)]
        lf = a["Tot_labo_for"]
        nlf = a["Not_LF"]
        ns = a["LF_NS"]
        pop = a["Tot"]
        denom = lf + nlf
        lfp = round(100.0 * lf / denom, 2) if denom else None
        unemp = round(100.0 * a["Unem_Tot"] / lf, 2) if lf else None
        L.append(f"| 20{year} | {sex} | {lf:,} | {nlf:,} | {ns:,} | {pop:,} | {lfp} | {unemp} |")

    # Sample rows for visual inspection
    L.append("")
    L.append("## Sample SA2 rows (first 5 SA2s, all sex × year)")
    L.append("")
    L.append("| SA2 | Year | Sex | LF | Not LF | Pop 15+ | LFP (%) | Unemp (%) |")
    L.append("|-----|-----:|:----|---:|-------:|--------:|--------:|----------:|")
    seen_sa2 = set()
    for (sa2, year, sex), m in sorted(data.items()):
        seen_sa2.add(sa2)
        if len(seen_sa2) > 5:
            break
        lf = m.get("Tot_labo_for", 0) or 0
        nlf = m.get("Not_LF", 0) or 0
        pop = m.get("Tot", 0) or 0
        unem = m.get("Unem_Tot", 0) or 0
        if pop == 0:
            continue
        denom = lf + nlf
        lfp = round(100.0 * lf / denom, 2) if denom else None
        unemp = round(100.0 * unem / lf, 2) if lf else None
        L.append(f"| {sa2} | 20{year} | {sex} | {lf:,} | {nlf:,} | {pop:,} | {lfp} | {unemp} |")

    EXTRACT_MD.write_text("\n".join(L), encoding="utf-8")
    print(f"\nWrote {EXTRACT_MD}")
    print("\nNext: review the sanity summary, confirm LFP rates land near "
          "ABS benchmarks (~65/61/70), then proceed to combined apply.")


if __name__ == "__main__":
    main()
