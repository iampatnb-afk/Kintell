"""
census_tsp_remoteness_probe.py

Read-only probe of abs_data/2021_TSP_SA2_for_AUS_short-header.zip
for any embedded SA2 -> Remoteness Area lookup file.

Census TSP DataPacks sometimes bundle geography concordance files in
a Metadata/ subfolder. We peek inside the zip without extracting.

Strategy:
  1. List zip contents.
  2. Identify candidate files via filename keywords (geog, remote,
     metadata, concord, lookup, ra_).
  3. Probe each candidate's first 5 rows for remoteness header text.
  4. Targeted scan: any small CSV (<100KB) at the archive top level
     to catch unconventionally-named metadata files.

Output: stdout. No file writes. No extraction.

Usage:
  python census_tsp_remoteness_probe.py
"""
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
ZIP_PATH = REPO_ROOT / "abs_data" / "2021_TSP_SA2_for_AUS_short-header.zip"

KEYWORDS_FILENAME = [
    "geog", "remote", "concord", "metadata",
    "lookup", "ra_", "_ra", "asgs", "areas",
]
KEYWORDS_HEADER = [
    "aria", "remote", "remoteness",
    "ra_code", "ra_name", "ra_2021",
]
SMALL_CSV_BYTES = 100 * 1024  # 100 KB threshold for "small" candidates


def filename_matches(name: str) -> bool:
    low = name.lower()
    return any(kw in low for kw in KEYWORDS_FILENAME)


def header_matches(line: str) -> bool:
    low = line.lower()
    return any(kw in low for kw in KEYWORDS_HEADER)


def peek_first_rows(zf, name, max_bytes=8192, max_lines=5):
    try:
        with zf.open(name) as fh:
            chunk = fh.read(max_bytes).decode("utf-8", errors="replace")
        return chunk.splitlines()[:max_lines]
    except Exception as e:
        return [f"_(read error: {e})_"]


def main():
    print("Census TSP remoteness probe - read-only")
    print(f"Zip: {ZIP_PATH}")
    if not ZIP_PATH.exists():
        print("ERROR: zip not found")
        return 1
    sz_mb = ZIP_PATH.stat().st_size / (1024 * 1024)
    print(f"Size: {sz_mb:.1f} MB")
    print()

    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        all_infos = zf.infolist()
        all_names = [i.filename for i in all_infos]
        size_by_name = {i.filename: i.file_size for i in all_infos}

        print(f"Total entries: {len(all_names)}")
        csv_count = sum(1 for n in all_names if n.lower().endswith(".csv"))
        xlsx_count = sum(1 for n in all_names if n.lower().endswith(".xlsx"))
        txt_count = sum(1 for n in all_names if n.lower().endswith(".txt"))
        print(f"  CSVs:   {csv_count:,}")
        print(f"  XLSXs:  {xlsx_count}")
        print(f"  TXTs:   {txt_count}")
        print()

        # Show top-level directory layout
        top_dirs = sorted({n.split("/")[0] for n in all_names if "/" in n})
        print("Top-level entries:")
        for d in top_dirs[:20]:
            print(f"  - {d}/")
        top_files = [n for n in all_names if "/" not in n]
        for f in top_files[:10]:
            print(f"  - {f}")
        print()

        # 1. Filename-keyword candidates
        candidates = sorted([n for n in all_names if filename_matches(n)])
        print(f"Filename-keyword candidates: {len(candidates)}")
        for n in candidates[:30]:
            print(f"  - {n} ({size_by_name[n]:,} bytes)")
        if len(candidates) > 30:
            print(f"  ... +{len(candidates)-30} more")
        print()

        # 2. Probe each candidate's headers
        header_hits = []
        for n in candidates:
            if not n.lower().endswith((".csv", ".txt")):
                continue
            print(f"=== {n} ===")
            lines = peek_first_rows(zf, n)
            for i, line in enumerate(lines):
                snippet = line[:240]
                print(f"  row {i}: {snippet}")
                if i == 0 and header_matches(line):
                    print("  >>> REMOTENESS keyword in header row")
                    header_hits.append(n)
            print()

        # 3. Targeted scan: small CSVs anywhere in the zip
        print("Scanning all small CSVs for SA2 + remoteness header co-occurrence...")
        small_csvs = [
            n for n in all_names
            if n.lower().endswith(".csv")
            and size_by_name.get(n, 0) <= SMALL_CSV_BYTES
        ]
        print(f"  Small CSVs to scan: {len(small_csvs)}")
        sa2_ra_hits = []
        for n in small_csvs[:200]:  # cap to avoid runaway
            lines = peek_first_rows(zf, n, max_bytes=2048, max_lines=1)
            if not lines:
                continue
            head = lines[0]
            if "SA2" in head.upper() and header_matches(head):
                sa2_ra_hits.append((n, head))
                print(f"  HIT: {n}")
                print(f"       header: {head[:300]}")
        print()

    print("=" * 64)
    if header_hits or sa2_ra_hits:
        print("OUTCOME: remoteness/SA2 data FOUND in TSP zip.")
        if header_hits:
            print("  Filename-candidate hits with remoteness in header:")
            for n in header_hits:
                print(f"    - {n}")
        if sa2_ra_hits:
            print("  Small CSVs with SA2+remoteness co-occurrence:")
            for n, _ in sa2_ra_hits:
                print(f"    - {n}")
    else:
        print("OUTCOME: no SA2 + remoteness columns in TSP zip.")
        print("Need separate ABS Remoteness Areas data source.")
    print("=" * 64)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
