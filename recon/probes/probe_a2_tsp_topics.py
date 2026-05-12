r"""
Quick probe — list all T-tables in 2021 TSP zip with descriptions.
Read-only. ~30 seconds.

Run from repo root:
    python recon\probes\probe_a2_tsp_topics.py
"""

import io
import sys
import warnings
import zipfile
from pathlib import Path

ZIP_PATH = Path("abs_data") / "2021_TSP_SA2_for_AUS_short-header.zip"
META_NAME = "Metadata/Metadata_2021_TSP_DataPack_R1_R2.xlsx"

NATIONALITY_KW = ["country", "birthplace", "ancestry", "religion",
                  "indigenous", "born", "citizenship"]


def main():
    if not ZIP_PATH.exists():
        print(f"ERROR: {ZIP_PATH} not found.")
        sys.exit(1)

    try:
        import pandas as pd
    except ImportError:
        print("pandas required.")
        sys.exit(1)

    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        with z.open(META_NAME) as f:
            data = f.read()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df = pd.read_excel(
                io.BytesIO(data),
                sheet_name="Table number, name, population",
                dtype=str,
                engine="openpyxl",
            )

    df = df.fillna("")
    print(f"Sheet rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print()

    # The shape we saw earlier: col 0 = T-code, col 1 = name, col 2 = population
    print("All T-tables (T-code, name, population):")
    print("-" * 72)
    for _, row in df.iterrows():
        cells = [str(v).strip() for v in row.values]
        nonempty = [c for c in cells if c]
        if not nonempty:
            continue
        # Skip header-ish rows
        joined = " | ".join(nonempty[:3])
        if "T" in cells[0] and any(ch.isdigit() for ch in cells[0]):
            print(f"  {joined}")

    print()
    print("Nationality-related T-tables (matched by keyword):")
    print("-" * 72)
    found = False
    for _, row in df.iterrows():
        cells = [str(v).strip() for v in row.values]
        joined = " ".join(cells).lower()
        if any(kw in joined for kw in NATIONALITY_KW):
            t = cells[0] if cells[0] else "?"
            name = cells[1] if len(cells) > 1 else ""
            print(f"  {t:6} {name}")
            found = True
    if not found:
        print("  (none matched)")

    print()
    print("Done. Read-only probe.")


if __name__ == "__main__":
    main()
