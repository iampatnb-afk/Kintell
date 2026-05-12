r"""
A2 metadata probe — find language table in TSP zip via metadata Excel.

Reads Metadata_2021_TSP_DataPack_R1_R2.xlsx from inside the zip, finds
T-codes whose description mentions language/English, then opens the
corresponding CSV(s) to inspect column structure.

Read-only. Run from repo root:
    python recon\probes\probe_a2_tsp_metadata.py
"""

import io
import re
import sys
import zipfile
import warnings
from pathlib import Path

ZIP_PATH = Path("abs_data") / "2021_TSP_SA2_for_AUS_short-header.zip"

LANGUAGE_KEYWORDS = ["language", "english", "speaks", "lote", "proficien"]


def main():
    if not ZIP_PATH.exists():
        print(f"ERROR: {ZIP_PATH} not found.")
        sys.exit(1)

    try:
        import pandas as pd
    except ImportError:
        print("pandas required.")
        sys.exit(1)

    print(f"Opening {ZIP_PATH}...")
    print()

    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        # ---------------------------------------------------------------
        # 1) Read the metadata Excel — map T-codes to descriptions
        # ---------------------------------------------------------------
        meta_name = "Metadata/Metadata_2021_TSP_DataPack_R1_R2.xlsx"
        if meta_name not in z.namelist():
            cands = [n for n in z.namelist() if "metadata" in n.lower()
                     and n.endswith(".xlsx")]
            print(f"Default metadata path not found. Candidates: {cands}")
            if not cands:
                sys.exit(1)
            meta_name = cands[0]

        print(f"Reading metadata: {meta_name}")
        with z.open(meta_name) as f:
            data = f.read()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            sheets = pd.read_excel(io.BytesIO(data), sheet_name=None,
                                   dtype=str, engine="openpyxl")

        print(f"Metadata sheets: {list(sheets.keys())}")
        print()

        # ---------------------------------------------------------------
        # 2) Find rows describing language-related tables
        # ---------------------------------------------------------------
        print("Sheets containing language-related rows:")
        all_lang_rows = []
        for sname, df in sheets.items():
            df = df.fillna("")
            # Concatenate all string cells per row to a search-blob
            blobs = df.astype(str).agg(" | ".join, axis=1).str.lower()
            mask = blobs.str.contains(
                "|".join(LANGUAGE_KEYWORDS), regex=True, na=False
            )
            hits = df[mask]
            if len(hits) > 0:
                print(f"\n  --- {sname} ({len(hits)} hits) ---")
                # Print non-empty cells per hit row
                for idx, row in hits.head(15).iterrows():
                    cells = [(c, str(v)) for c, v in row.items() if str(v).strip()]
                    cells_str = " | ".join(f"{c}={v[:60]}" for c, v in cells[:6])
                    print(f"    [{idx}] {cells_str}")
                    all_lang_rows.append((sname, idx, row))

        # ---------------------------------------------------------------
        # 3) Extract distinct T-codes from the hit rows
        # ---------------------------------------------------------------
        print("\n" + "=" * 60)
        print("Distinct T-codes referenced in language-related rows:")
        t_codes_found = set()
        for sname, idx, row in all_lang_rows:
            text = " ".join(str(v) for v in row.values if str(v).strip())
            for m in re.finditer(r"\bT(\d{1,2})([A-Z])?\b", text):
                t_codes_found.add(m.group(1).zfill(2))
        print(f"  {sorted(t_codes_found)}")

        # ---------------------------------------------------------------
        # 4) For each candidate T-code, peek at the corresponding CSV
        # ---------------------------------------------------------------
        print("\n" + "=" * 60)
        print("Peeking at candidate CSV files:")

        for tc in sorted(t_codes_found):
            csv_candidates = [
                n for n in z.namelist()
                if f"_T{tc}" in n and n.endswith(".csv")
            ]
            if not csv_candidates:
                continue
            print(f"\n  T{tc}: {len(csv_candidates)} CSV file(s)")
            for c in csv_candidates[:5]:
                print(f"    {c}")

            # Read the first one
            first = csv_candidates[0]
            with z.open(first) as f:
                head_bytes = f.read(4096)
            head_text = head_bytes.decode("utf-8", errors="replace")
            lines = head_text.splitlines()[:3]
            print(f"  First 3 lines of {Path(first).name}:")
            for ln in lines:
                trimmed = ln if len(ln) <= 200 else ln[:197] + "..."
                print(f"    {trimmed}")

            # Show column headers fully
            if lines:
                cols = lines[0].split(",")
                print(f"  Column count: {len(cols)}")
                # Print English / non-English / language columns
                lang_cols = [
                    (i, c) for i, c in enumerate(cols)
                    if any(k in c.lower() for k in ["lang", "engl", "speak", "lote"])
                ]
                if lang_cols:
                    print("  Language-related columns:")
                    for i, c in lang_cols[:25]:
                        print(f"    [{i}] {c.strip()}")
                else:
                    # Show first 30 column names so we can spot relevant ones
                    print("  First 30 columns:")
                    for i, c in enumerate(cols[:30]):
                        print(f"    [{i}] {c.strip()}")

    print()
    print("Done. Read-only probe — no DB mutation.")


if __name__ == "__main__":
    main()
