r"""
A2 zip-content probe — find the language-table candidate inside the 2021
TSP zip without extracting it.

Read-only. Run from repo root:
    python recon\probes\probe_a2_tsp_zip.py
"""

import sys
import zipfile
from pathlib import Path

ZIP_PATH = Path("abs_data") / "2021_TSP_SA2_for_AUS_short-header.zip"

LANGUAGE_KEYWORDS = [
    "language", "lang", "lanp", "lote", "english",
    "country", "birthplace", "speaks", "homelang",
]


def main():
    if not ZIP_PATH.exists():
        print(f"ERROR: {ZIP_PATH} not found.")
        sys.exit(1)

    print(f"Opening {ZIP_PATH} ({ZIP_PATH.stat().st_size / 1024 / 1024:.1f} MB)...")
    print()

    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        names = z.namelist()
        print(f"Total entries in zip: {len(names)}")

        # Top-level directory structure
        top_dirs = sorted({n.split("/", 1)[0] for n in names if "/" in n})
        print(f"Top-level dirs: {top_dirs[:10]}")
        print()

        # Sample of file extensions
        exts = {}
        for n in names:
            ext = Path(n).suffix.lower()
            exts[ext] = exts.get(ext, 0) + 1
        print(f"Extensions: {exts}")
        print()

        # T-numbered tables — show distinct table identifiers
        # ABS TSP filenames look like: 2021Census_T01_AUST_SA2.csv or similar
        import re
        t_codes = set()
        for n in names:
            m = re.search(r"_T(\d+)[A-Z_]?", n)
            if m:
                t_codes.add(m.group(1))
        print(f"Distinct T-codes seen: {sorted(t_codes, key=int)}")
        print()

        # Language-table candidates by keyword in filename
        print("Files whose name matches a language keyword:")
        candidates = []
        for n in names:
            lower = n.lower()
            for kw in LANGUAGE_KEYWORDS:
                if kw in lower:
                    candidates.append((kw, n))
                    break
        for kw, n in candidates[:30]:
            info = z.getinfo(n)
            size_kb = info.file_size / 1024
            print(f"  [{kw:>8}] {n} ({size_kb:.1f} KB)")
        if not candidates:
            print("  (none — keyword search returned nothing)")
        print()

        # Show sample filenames at each top-level
        print("Sample filenames per top-level dir:")
        for d in top_dirs[:5]:
            sample = [n for n in names if n.startswith(d + "/")][:5]
            print(f"  {d}/")
            for s in sample:
                print(f"    {s}")
            print()

        # If we found a "Metadata" file or similar, peek at it
        meta_candidates = [n for n in names if "metadata" in n.lower()
                           or "readme" in n.lower()
                           or "contents" in n.lower()]
        print(f"Metadata/readme/contents files found: {len(meta_candidates)}")
        for m in meta_candidates[:5]:
            print(f"  {m}")

    print()
    print("Done. Read-only probe — no DB mutation.")


if __name__ == "__main__":
    main()
