"""
Layer 2 Step 5b-prime — T33 labour force probe (read-only).
============================================================
Dump '_Tot_' age aggregate columns from T33C (Males), T33F (Females),
T33H (Persons) so we can identify exact column names for SA2-level
LFP/employment rate derivation.

Outputs:
  recon/layer2_step5b_prime_t33_headers.txt
"""

import zipfile
import csv
import io
from pathlib import Path

ABS_DATA = Path("abs_data")
RECON_DIR = Path("recon")
OUT = RECON_DIR / "layer2_step5b_prime_t33_headers.txt"

TARGETS = {
    "T33C": "Males",
    "T33F": "Females",
    "T33H": "Persons",
}


def find_zip():
    cands = sorted(ABS_DATA.glob("*TSP*.zip"))
    return cands[0] if cands else None


def main():
    RECON_DIR.mkdir(exist_ok=True)
    zp = find_zip()
    if not zp:
        print("ERROR: no TSP zip in abs_data/")
        return

    lines = []
    def out(s=""):
        print(s)
        lines.append(s)

    out(f"Probing: {zp}")

    with zipfile.ZipFile(zp) as zf:
        names = zf.namelist()
        for tbl, label in TARGETS.items():
            path = next((n for n in names
                         if f"{tbl}_AUST_SA2" in n and n.endswith(".csv")), None)
            if not path:
                out(f"\nNOT FOUND: {tbl}")
                continue
            out("")
            out(f"===== {tbl} ({label}) =====")
            out(f"File: {path}")
            with zf.open(path) as fh:
                text = io.TextIOWrapper(fh, encoding="utf-8-sig", newline="")
                reader = csv.reader(text)
                header = next(reader)

                tot_cols = [(i, c) for i, c in enumerate(header) if "_Tot_" in c]
                out(f"Total cols: {len(header)}, "
                    f"'_Tot_' age aggregate cols: {len(tot_cols)}")
                out("")
                out("All '_Tot_' age aggregate columns:")
                for i, c in tot_cols:
                    out(f"  [{i:>3}] {c}")

                out("")
                out("First 8 columns (for structure context):")
                for i in range(min(8, len(header))):
                    out(f"  [{i:>3}] {header[i]}")

                out("")
                out("Last 8 columns:")
                for i in range(max(0, len(header) - 8), len(header)):
                    out(f"  [{i:>3}] {header[i]}")

                out("")
                out("First 2 data rows (first 6 cols):")
                for j, row in enumerate(reader):
                    if j >= 2:
                        break
                    out(f"  row {j}: SA2={row[0]} ... {row[1:6]}")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWritten to: {OUT}")


if __name__ == "__main__":
    main()
