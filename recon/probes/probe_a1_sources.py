r"""
A1 source-data probe — read-only.

Three questions:
1. What years does abs_data/Population and People Database.xlsx actually contain
   for column 'Persons - 0-4 years (no.)'?
2. What's the nested structure of docs/sa2_history.json, and how does Bayswater
   211011251 look inside it (pop_0_4 quarterly array length, NULL count)?
3. Are pre-2019 under-5 figures in another DB table we can re-use?

Run from repo root:
    python recon\probes\probe_a1_sources.py
"""

import json
import sqlite3
import sys
import warnings
from pathlib import Path

DB_PATH = Path("data") / "kintell.db"
HISTORY_JSON = Path("docs") / "sa2_history.json"
ABS_POP_XLSX = Path("abs_data") / "Population and People Database.xlsx"

BAYSWATER = "211011251"
BONDI = "118011341"


def section(title):
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def main():
    # -----------------------------------------------------------------------
    # Q1: Excel year coverage for Persons - 0-4 years
    # -----------------------------------------------------------------------
    section("1. Population and People Database.xlsx — year coverage for under-5")
    if not ABS_POP_XLSX.exists():
        print(f"  {ABS_POP_XLSX} not found.")
        print("  Listing abs_data/ contents instead:")
        abs_dir = Path("abs_data")
        if abs_dir.exists():
            for f in sorted(abs_dir.iterdir()):
                size_mb = f.stat().st_size / (1024 * 1024) if f.is_file() else 0
                print(f"    {f.name} ({size_mb:.1f} MB)" if f.is_file() else f"    {f.name}/")
        else:
            print("    abs_data/ does not exist.")
    else:
        try:
            import pandas as pd
        except ImportError:
            print("  pandas not available; skipping Excel inspection.")
        else:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                try:
                    df = pd.read_excel(
                        ABS_POP_XLSX,
                        sheet_name="Table 1",
                        header=6,
                        dtype=str,
                        engine="openpyxl",
                    )
                except Exception as e:
                    print(f"  Error reading Excel: {e}")
                    df = None

            if df is not None:
                df.columns = [str(c).strip() for c in df.columns]
                print(f"  Columns ({len(df.columns)}): {list(df.columns)[:15]}")
                if "Year" in df.columns:
                    years = sorted(df["Year"].dropna().astype(str).str.strip().unique())
                    print(f"  Distinct Year values: {years[:30]}")
                    print(f"  Total distinct years: {len(years)}")
                else:
                    print("  No 'Year' column found.")

                pop_col = "Persons - 0-4 years (no.)"
                if pop_col in df.columns:
                    sample = df[df["Code"].astype(str).str.strip() == BAYSWATER]
                    print(f"\n  Bayswater {BAYSWATER} rows: {len(sample)}")
                    if len(sample) > 0 and "Year" in sample.columns:
                        for _, row in sample[["Year", pop_col]].iterrows():
                            print(f"    Year={row['Year']!r:<10} {pop_col}={row[pop_col]!r}")

                    sample = df[df["Code"].astype(str).str.strip() == BONDI]
                    print(f"\n  Bondi {BONDI} rows: {len(sample)}")
                    if len(sample) > 0 and "Year" in sample.columns:
                        for _, row in sample[["Year", pop_col]].iterrows():
                            print(f"    Year={row['Year']!r:<10} {pop_col}={row[pop_col]!r}")
                else:
                    print(f"  Column {pop_col!r} not found.")
                    cand = [c for c in df.columns if "0-4" in c or "under" in c.lower()]
                    print(f"  Candidate under-5 columns: {cand}")

    # -----------------------------------------------------------------------
    # Q2: sa2_history.json nested structure + Bayswater
    # -----------------------------------------------------------------------
    section("2. sa2_history.json — nested structure + Bayswater pop_0_4")
    if not HISTORY_JSON.exists():
        print(f"  {HISTORY_JSON} not found.")
    else:
        data = json.loads(HISTORY_JSON.read_text(encoding="utf-8"))
        print(f"  Top-level keys: {list(data.keys())}")
        print(f"  schema: {data.get('schema')}")
        print(f"  generated: {data.get('generated')}")
        print(f"  sa2_count: {data.get('sa2_count')}")
        quarters = data.get("quarters", [])
        print(f"  quarters: {len(quarters)} entries; "
              f"first={quarters[:3]}, last={quarters[-3:]}")

        # Find the nested SA2 dict
        sa2_dict = None
        sa2_dict_key = None
        for k, v in data.items():
            if isinstance(v, dict) and len(v) > 100 and all(
                isinstance(sub_k, str) and sub_k.isdigit() for sub_k in list(v.keys())[:5]
            ):
                sa2_dict = v
                sa2_dict_key = k
                break

        if sa2_dict is None:
            print("\n  Could not auto-locate per-SA2 dict.")
            print("  Sampling each top-level value:")
            for k, v in data.items():
                if isinstance(v, dict):
                    sample_keys = list(v.keys())[:3]
                    print(f"    {k}: dict with {len(v)} keys; sample={sample_keys}")
                elif isinstance(v, list):
                    print(f"    {k}: list of {len(v)} items")
                else:
                    print(f"    {k}: {type(v).__name__}")
        else:
            print(f"\n  Per-SA2 data lives under top-level key: {sa2_dict_key!r}")
            print(f"  Total SA2 keys in that dict: {len(sa2_dict)}")
            print(f"  Bayswater {BAYSWATER} present: {BAYSWATER in sa2_dict}")
            print(f"  Bondi    {BONDI} present: {BONDI in sa2_dict}")

            for sa2 in (BAYSWATER, BONDI):
                if sa2 not in sa2_dict:
                    continue
                entry = sa2_dict[sa2]
                print(f"\n  --- {sa2} ---")
                if isinstance(entry, dict):
                    print(f"  entry keys: {list(entry.keys())[:15]}")
                    if "pop_0_4" in entry:
                        arr = entry["pop_0_4"]
                        non_null = sum(1 for x in arr if x is not None)
                        print(f"  pop_0_4: length {len(arr)}, "
                              f"non-null {non_null}, "
                              f"nulls {len(arr) - non_null}")
                        # First non-null index
                        first_nn = next((i for i, x in enumerate(arr) if x is not None), None)
                        last_nn = next(
                            (len(arr) - 1 - i for i, x in enumerate(reversed(arr)) if x is not None),
                            None,
                        )
                        if first_nn is not None and quarters:
                            print(f"  first non-null quarter: idx {first_nn} -> {quarters[first_nn]}")
                            print(f"  last non-null quarter:  idx {last_nn} -> {quarters[last_nn]}")
                            print(f"  first 5 values: {arr[:5]}")
                            print(f"  last 5 values: {arr[-5:]}")

    # -----------------------------------------------------------------------
    # Q3: alternative pre-2019 under-5 sources in DB
    # -----------------------------------------------------------------------
    section("3. Alternative DB tables — looking for pre-2019 under-5 figures")
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    for tbl in ("abs_sa2_socioeconomic_annual", "abs_sa2_education_employment_annual"):
        print(f"\n  --- {tbl} ---")
        try:
            cols = [c[1] for c in cur.execute(f'PRAGMA table_info("{tbl}")').fetchall()]
            print(f"  columns: {cols}")
        except Exception as e:
            print(f"  error: {e}")
            continue

        # See if there's a metric/measure column that might hold under-5
        likely_metric_cols = [
            c for c in cols if c.lower() in ("metric", "measure", "indicator", "topic", "category")
        ]
        if likely_metric_cols:
            mc = likely_metric_cols[0]
            try:
                vals = cur.execute(
                    f'SELECT DISTINCT "{mc}" FROM "{tbl}" '
                    f'WHERE LOWER("{mc}") LIKE \'%age%\' '
                    f'   OR LOWER("{mc}") LIKE \'%child%\' '
                    f'   OR LOWER("{mc}") LIKE \'%under%\' '
                    f'   OR LOWER("{mc}") LIKE \'%0-4%\' '
                    f'   OR LOWER("{mc}") LIKE \'%0_4%\' '
                    f'LIMIT 20'
                ).fetchall()
                print(f"  {mc} values matching age/child/under/0-4: "
                      f"{[v[0] for v in vals]}")
            except Exception as e:
                print(f"  metric query error: {e}")
        else:
            print("  (no obvious metric/measure column)")

    con.close()
    print()
    print("Done. Read-only probe — no DB mutation.")


if __name__ == "__main__":
    main()
