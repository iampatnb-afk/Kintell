r"""
Probe T10A + T10B full column list to find the correct
"uses other language" and "language not stated" columns.

Read-only. Run from repo root:
    python recon\probes\probe_a2_t10_columns.py
"""

import io
import sys
import zipfile
from pathlib import Path

ZIP_PATH = Path("abs_data") / "2021_TSP_SA2_for_AUS_short-header.zip"

T10A = "2021 Census TSP Statistical Area 2 for AUS/2021Census_T10A_AUST_SA2.csv"
T10B = "2021 Census TSP Statistical Area 2 for AUS/2021Census_T10B_AUST_SA2.csv"


def main():
    if not ZIP_PATH.exists():
        print(f"ERROR: {ZIP_PATH} not found.")
        sys.exit(1)

    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        for name in (T10A, T10B):
            if name not in z.namelist():
                print(f"ERROR: {name} not in zip.")
                continue
            with z.open(name) as f:
                head_bytes = f.read(8192)
            head_text = head_bytes.decode("utf-8", errors="replace")
            header_line = head_text.splitlines()[0]
            cols = header_line.split(",")
            print()
            print("=" * 72)
            print(f"{Path(name).name} — {len(cols)} columns")
            print("=" * 72)

            # Group columns by their stem (strip _C11/C16/C21 + _M/_F/_P)
            stems = {}
            import re
            for c in cols:
                # Remove trailing _C\d\d_[MFP]
                stem = re.sub(r"_C(11|16|21)_[MFP]$", "", c.strip())
                stems.setdefault(stem, []).append(c.strip())

            print(f"  Distinct column stems: {len(stems)}")
            for stem, members in stems.items():
                print(f"\n  STEM: {stem!r}  ({len(members)} columns)")
                # Print just the C21_P columns for readability
                p21 = [m for m in members if m.endswith("_C21_P")]
                if p21:
                    print(f"    C21 Persons columns: {p21}")
                else:
                    # If no C21_P, print the first few
                    print(f"    Sample members: {members[:6]}")

    print()
    print("Done. Read-only probe.")


if __name__ == "__main__":
    main()
