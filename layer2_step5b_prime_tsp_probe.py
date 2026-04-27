"""
Layer 2 Step 5b-prime — Census 2021 TSP wide probe (read-only).
================================================================
T07 in 2021 TSP is fertility (NCB), not labour force. This probe
scans EVERY CSV in the zip and reports which tables contain
labour-force columns (matching LFS / LFPR / Empd / Unempd / Empl
patterns) and sex-disaggregated columns (matching _F_, _M_, Fem,
Mal patterns).

Outputs:
  console + recon/layer2_step5b_prime_tsp_probe.txt
"""

import zipfile
import csv
import io
import re
from pathlib import Path
from collections import defaultdict

ABS_DATA = Path("abs_data")
RECON_DIR = Path("recon")
OUT_TXT = RECON_DIR / "layer2_step5b_prime_tsp_probe.txt"

# Patterns to flag a column as labour-force related
LF_PATTERNS = [
    re.compile(r"\bLFS\b", re.IGNORECASE),
    re.compile(r"\bLFPR\b", re.IGNORECASE),
    re.compile(r"\bEmpd\b", re.IGNORECASE),
    re.compile(r"\bUnempd\b", re.IGNORECASE),
    re.compile(r"\bEmpl\b", re.IGNORECASE),
    re.compile(r"\bUnempl\b", re.IGNORECASE),
    re.compile(r"\bLab(o|ou)r", re.IGNORECASE),
    re.compile(r"\bPartic", re.IGNORECASE),
]

# Patterns to flag a column as sex-disaggregated
SEX_PATTERNS = [
    re.compile(r"_F_", re.IGNORECASE),
    re.compile(r"_M_", re.IGNORECASE),
    re.compile(r"_Fem", re.IGNORECASE),
    re.compile(r"_Mal", re.IGNORECASE),
    re.compile(r"_Fe_", re.IGNORECASE),
    re.compile(r"_Ma_", re.IGNORECASE),
    re.compile(r"Female", re.IGNORECASE),
    re.compile(r"\bMale\b", re.IGNORECASE),
]

TABLE_RE = re.compile(r"(T\d{2}[A-Z]?)_AUST_SA2", re.IGNORECASE)


def find_zip():
    cands = sorted(ABS_DATA.glob("*TSP*.zip"))
    if not cands:
        cands = sorted(ABS_DATA.glob("*tsp*.zip"))
    return cands[0] if cands else None


def col_matches(col, patterns):
    return any(p.search(col) for p in patterns)


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
    out("")

    with zipfile.ZipFile(zp) as zf:
        names = zf.namelist()
        sa2_csvs = sorted([n for n in names if n.endswith(".csv") and "SA2" in n.upper()])
        out(f"SA2 CSVs in zip: {len(sa2_csvs)}")
        out("")

        # Group by table number
        by_table = defaultdict(list)
        for n in sa2_csvs:
            m = TABLE_RE.search(n)
            if m:
                by_table[m.group(1).upper()].append(n)
            else:
                by_table["?"].append(n)
        out(f"Distinct tables: {len(by_table)}")
        out(f"Table list: {sorted(by_table.keys())}")
        out("")

        # Scan each CSV's header
        lf_hits = {}      # table -> list of LF-matching cols
        sex_hits = {}     # table -> list of sex-matching cols
        sample_cols = {}  # table -> first 3 non-code cols (for table identification)

        for n in sa2_csvs:
            m = TABLE_RE.search(n)
            tbl = m.group(1).upper() if m else "?"
            with zf.open(n) as fh:
                text = io.TextIOWrapper(fh, encoding="utf-8-sig", newline="")
                header = next(csv.reader(text))
            non_code = [c for c in header if c not in ("SA2_CODE_2021", "SA2_NAME_2021")]
            sample_cols.setdefault(tbl, []).extend(non_code[:3])
            lf = [c for c in header if col_matches(c, LF_PATTERNS)]
            sx = [c for c in header if col_matches(c, SEX_PATTERNS)]
            if lf:
                lf_hits.setdefault(tbl, []).extend(lf)
            if sx:
                sex_hits.setdefault(tbl, []).extend(sx)

        # Report tables with labour-force hits
        out("=" * 70)
        out("TABLES WITH LABOUR-FORCE COLUMNS")
        out("=" * 70)
        if not lf_hits:
            out("  NONE — TSP may not include labour force at SA2.")
        else:
            for tbl, cols in sorted(lf_hits.items()):
                out(f"\n[{tbl}] {len(cols)} LF cols. Files in this table:")
                for n in by_table.get(tbl, []):
                    out(f"  {n}")
                out(f"  First 6 LF cols: {cols[:6]}")
                # Cross-check: any sex-disaggregated LF cols?
                sx_in_lf = [c for c in cols if col_matches(c, SEX_PATTERNS)]
                out(f"  Sex-disaggregated LF cols: {len(sx_in_lf)}")
                if sx_in_lf:
                    out(f"    First 6: {sx_in_lf[:6]}")

        out("")
        out("=" * 70)
        out("ALL TABLES — first 3 columns each (for identification)")
        out("=" * 70)
        for tbl in sorted(sample_cols.keys()):
            out(f"  [{tbl}] {sample_cols[tbl][:3]}")

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nFull output also at: {OUT_TXT}")


if __name__ == "__main__":
    main()
