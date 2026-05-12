"""
probe_oi36_unit_discipline.py
=============================
Read-only check: confirm the sa2_nes_share unit convention is
consistent across the storage -> wire -> render path so the rendered
value reads "31.07%" not "0.31%" and not "0.0031%".

Storage : abs_sa2_education_employment_annual.census_nes_share_pct
          should be percentage (0-100), e.g. 31.07
Wire    : populate_service_catchment_cache.py reads the value, divides
          by 100, passes to calibrate_participation_rate() (fraction).
Render  : centre_page.py payload + centre.html should display the
          stored value as a percentage with 1-decimal-place formatting,
          e.g. "31.1%".

This script:
  1. Reads census_nes_share_pct for the verification SA2s and confirms
     the values look like percentages (range 0-100, not 0-1).
  2. Reads service_catchment_cache.rule_text + calibrated_rate for the
     same SA2s and confirms the calibration nudge fragment is present
     where expected.
  3. Reports any obvious unit inconsistencies.

Read-only. Does not mutate the DB.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path


VERIFICATION_SA2S = [
    # (sa2_code, name,                     expected_pct, expected_band)
    ("211011251", "Bayswater Vic",                  31.07, "high"),
    ("118011341", "Bondi Junction-Waverly NSW",     23.58, "mid"),
    ("506031124", "Bentley-Wilson WA",              37.55, "high"),
]

NUDGE_FRAGMENT = "high NES share"


def find_db() -> Path | None:
    for c in [
        Path(__file__).resolve().parents[2] / "data" / "kintell.db",
        Path.cwd() / "data" / "kintell.db",
    ]:
        if c.exists():
            return c
    return None


def main() -> int:
    db_path = find_db()
    if db_path is None:
        print("[ERROR] could not locate data/kintell.db")
        return 2

    uri = f"file:{db_path.as_posix()}?mode=ro"
    print(f"[probe] db: {db_path} (read-only)")
    print()

    overall_ok = True

    with sqlite3.connect(uri, uri=True) as con:
        con.row_factory = sqlite3.Row

        print("=" * 70)
        print("1. STORAGE CONVENTION  abs_sa2_education_employment_annual")
        print("=" * 70)
        for sa2, name, expected_pct, _ in VERIFICATION_SA2S:
            row = con.execute(
                """
                SELECT year_period, census_nes_share_pct
                FROM abs_sa2_education_employment_annual
                WHERE sa2_code = ? AND census_nes_share_pct IS NOT NULL
                ORDER BY year_period DESC
                LIMIT 1
                """,
                (sa2,),
            ).fetchone()
            if row is None:
                print(f"  [FAIL] {sa2} {name}: no NES row in storage table")
                overall_ok = False
                continue

            v = row["census_nes_share_pct"]
            year = row["year_period"]
            ok_range = 0 < v < 100
            ok_value = abs(v - expected_pct) < 0.5
            ok_units = v > 1.0  # if stored as fraction this would be ~0.31

            tag = "PASS" if (ok_range and ok_value and ok_units) else "FAIL"
            print(f"  [{tag}] {sa2} {name:<32} year={year}  value={v:>7.2f}  "
                  f"(expect ~{expected_pct})")
            if not ok_units:
                print("         ^^ value < 1.0 suggests fraction storage, "
                      "NOT percentage. Render would display incorrectly.")
                overall_ok = False
            elif not ok_value:
                print("         ^^ value differs from monolith expectation")
                overall_ok = False
        print()

        print("=" * 70)
        print("2. WIRE BOUNDARY  service_catchment_cache.rule_text")
        print("=" * 70)
        for sa2, name, _, expected_band in VERIFICATION_SA2S:
            row = con.execute(
                """
                SELECT rule_text, calibrated_rate
                FROM service_catchment_cache
                WHERE sa2_code = ?
                LIMIT 1
                """,
                (sa2,),
            ).fetchone()
            if row is None:
                print(f"  [FAIL] {sa2}: no service_catchment_cache row")
                overall_ok = False
                continue

            rt = row["rule_text"] or ""
            cr = row["calibrated_rate"]
            has_nudge = NUDGE_FRAGMENT in rt

            if expected_band == "high":
                ok = has_nudge
                expectation = "expect high-NES nudge fragment"
            else:
                ok = True
                expectation = "no high-NES nudge expected"

            tag = "PASS" if ok else "FAIL"
            print(f"  [{tag}] {sa2} {name:<32} rate={cr}  ({expectation})")
            print(f"         rule: {rt[:120]}{'...' if len(rt) > 120 else ''}")
            if not ok:
                overall_ok = False
        print()

    print("=" * 70)
    if overall_ok:
        print("[OK] unit discipline confirmed.")
        print("     Storage: percentage (0-100). Wire divides at boundary.")
        print("     Render side should display value with '%' suffix at 1dp.")
        return 0
    else:
        print("[FAIL] unit discipline mismatch  DO NOT proceed with patch")
        print("       until storage/wire/render convention is reconciled.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
