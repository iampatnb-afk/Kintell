"""
A1 probe — pop_0_4 coverage in abs_sa2_erp_annual.

Read-only. Reframes OI-30 finding now that we know the table has 2011-2024
year coverage already. Question becomes: does age_group='0-4' exist for
the historical years (2011/2016/2018) or only 2019+?

Run from repo root:
    python recon\probes\probe_a1_pop04_coverage.py
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path("data") / "kintell.db"


def section(title):
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def main():
    if not DB_PATH.exists():
        print(f"ERROR: {DB_PATH} not found. Run from repo root.", file=sys.stderr)
        sys.exit(1)

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    section("1. Distinct age_group values in abs_sa2_erp_annual")
    rows = cur.execute(
        "SELECT age_group, COUNT(*) FROM abs_sa2_erp_annual "
        "GROUP BY age_group ORDER BY age_group"
    ).fetchall()
    for ag, n in rows:
        print(f"  {ag!r:20} {n:>10,} rows")
    print(f"\n  Total distinct age_groups: {len(rows)}")

    section("2. 0-4 coverage by year (SA2 count)")
    rows = cur.execute(
        "SELECT year, COUNT(DISTINCT sa2_code) "
        "FROM abs_sa2_erp_annual WHERE age_group = '0-4' "
        "GROUP BY year ORDER BY year"
    ).fetchall()
    if not rows:
        print("  No rows where age_group = '0-4'. Check exact label spelling.")
    else:
        for y, n in rows:
            print(f"  {y}: {n:,} SA2s with pop_0_4")

    section("3. Bayswater 211011251 (OI-30 subject) pop_0_4 by year")
    rows = cur.execute(
        "SELECT year, persons FROM abs_sa2_erp_annual "
        "WHERE sa2_code = '211011251' AND age_group = '0-4' ORDER BY year"
    ).fetchall()
    if not rows:
        print("  No 0-4 rows for this SA2.")
    else:
        for y, p in rows:
            print(f"  {y}: {p}")

    section("4. Bondi Junction-Waverly 118011341 (control) pop_0_4 by year")
    rows = cur.execute(
        "SELECT year, persons FROM abs_sa2_erp_annual "
        "WHERE sa2_code = '118011341' AND age_group = '0-4' ORDER BY year"
    ).fetchall()
    if not rows:
        print("  No 0-4 rows for this SA2.")
    else:
        for y, p in rows:
            print(f"  {y}: {p}")

    section("5. SA2 code drift across years")
    in_2011_not_2024 = cur.execute(
        "SELECT COUNT(*) FROM ("
        "  SELECT DISTINCT sa2_code FROM abs_sa2_erp_annual WHERE year = 2011 "
        "  EXCEPT "
        "  SELECT DISTINCT sa2_code FROM abs_sa2_erp_annual WHERE year = 2024"
        ")"
    ).fetchone()[0]
    in_2024_not_2011 = cur.execute(
        "SELECT COUNT(*) FROM ("
        "  SELECT DISTINCT sa2_code FROM abs_sa2_erp_annual WHERE year = 2024 "
        "  EXCEPT "
        "  SELECT DISTINCT sa2_code FROM abs_sa2_erp_annual WHERE year = 2011"
        ")"
    ).fetchone()[0]
    print(f"  In 2011 but not 2024: {in_2011_not_2024} codes")
    print(f"  In 2024 but not 2011: {in_2024_not_2011} codes")
    if in_2011_not_2024 == 0 and in_2024_not_2011 == 0:
        print("  -> Codes are stable. Single ASGS edition throughout.")
    else:
        print("  -> Code drift present. ASGS-edition concordance needed.")

    section("6. Total rows by (year, age_group) sanity")
    rows = cur.execute(
        "SELECT year, COUNT(DISTINCT age_group) FROM abs_sa2_erp_annual "
        "GROUP BY year ORDER BY year"
    ).fetchall()
    for y, n in rows:
        print(f"  {y}: {n} age_groups")

    con.close()
    print()
    print("Done. Read-only probe — no DB mutation.")


if __name__ == "__main__":
    main()
