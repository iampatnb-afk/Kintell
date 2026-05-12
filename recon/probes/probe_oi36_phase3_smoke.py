"""
probe_oi36_phase3_smoke.py
==========================
Read-only smoke test for OI-36 (C2-NES render-side).

Run AFTER:
  1. The OI-36 patch has landed (centre.html / centre_page.py).
  2. review_server.py has been restarted per STD-13 + STD-14.

Confirms that the upstream data path the renderer depends on is sane
across the three verification SA2s. Three checks per SA2:

  - Storage value matches monolith (within 0.5 pp tolerance)
  - Layer 3 banding row exists with the expected band
  - service_catchment_cache shows the expected calibration nudge state

A full smoke test ALSO requires opening the centre page in a browser
and visually confirming the new row renders. The script prints the
URLs to use at the end.

Read-only. Does not mutate the DB. Does not hit review_server.py.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path


SCENARIOS = [
    {
        "sa2":            "211011251",
        "name":           "Bayswater Vic",
        "expected_pct":   31.07,
        "expected_band":  "high",
        "expected_nudge": True,
    },
    {
        "sa2":            "118011341",
        "name":           "Bondi Junction-Waverly NSW",
        "expected_pct":   23.58,
        "expected_band":  "mid",
        "expected_nudge": False,
    },
    {
        "sa2":            "506031124",
        "name":           "Bentley-Wilson WA",
        "expected_pct":   37.55,
        "expected_band":  "high",
        "expected_nudge": True,
    },
]


def find_db() -> Path | None:
    for c in [
        Path(__file__).resolve().parents[2] / "data" / "kintell.db",
        Path.cwd() / "data" / "kintell.db",
    ]:
        if c.exists():
            return c
    return None


def get_band_row(con, sa2: str):
    return con.execute(
        """
        SELECT band, decile, value
        FROM layer3_sa2_metric_banding
        WHERE sa2_code = ? AND metric = 'sa2_nes_share'
        LIMIT 1
        """,
        (sa2,),
    ).fetchone()


def get_sample_service(con, sa2: str):
    """Return one service_id anchored in this SA2 — for the browser
    smoke test URLs at the end."""
    row = con.execute(
        """
        SELECT service_id
        FROM service_catchment_cache
        WHERE sa2_code = ?
        ORDER BY service_id
        LIMIT 1
        """,
        (sa2,),
    ).fetchone()
    return row["service_id"] if row else None


def main() -> int:
    db_path = find_db()
    if db_path is None:
        print("[ERROR] could not locate data/kintell.db")
        return 2

    uri = f"file:{db_path.as_posix()}?mode=ro"
    print(f"[probe] db: {db_path} (read-only)")
    print()

    all_ok = True
    sample_service_ids = {}

    with sqlite3.connect(uri, uri=True) as con:
        con.row_factory = sqlite3.Row

        for scen in SCENARIOS:
            sa2 = scen["sa2"]
            name = scen["name"]
            print("-" * 70)
            print(f"SA2 {sa2}  {name}")
            print("-" * 70)

            # 1. Storage
            row = con.execute(
                """
                SELECT year_period, census_nes_share_pct
                FROM abs_sa2_education_employment_annual
                WHERE sa2_code = ? AND census_nes_share_pct IS NOT NULL
                ORDER BY year_period DESC LIMIT 1
                """,
                (sa2,),
            ).fetchone()
            if row is None:
                print("  [FAIL] storage    : no row")
                all_ok = False
                continue

            v = row["census_nes_share_pct"]
            year = row["year_period"]
            ok_value = abs(v - scen["expected_pct"]) < 0.5
            tag = "PASS" if ok_value else "FAIL"
            print(f"  [{tag}] storage    : year={year}  value={v:.2f}  "
                  f"(expect ~{scen['expected_pct']})")
            if not ok_value:
                all_ok = False

            # 2. Banding
            br = get_band_row(con, sa2)
            if br is None:
                print("  [FAIL] banding    : no row in layer3_sa2_metric_banding")
                all_ok = False
            else:
                ok_band = br["band"] == scen["expected_band"]
                tag = "PASS" if ok_band else "FAIL"
                print(f"  [{tag}] banding    : decile={br['decile']:>2}  "
                      f"band={br['band']:<5}  (expect '{scen['expected_band']}')")
                if not ok_band:
                    all_ok = False

            # 3. Calibration
            cal = con.execute(
                """
                SELECT calibrated_rate, rule_text
                FROM service_catchment_cache
                WHERE sa2_code = ?
                LIMIT 1
                """,
                (sa2,),
            ).fetchone()
            if cal is None:
                print("  [FAIL] cache      : no service_catchment_cache row")
                all_ok = False
            else:
                has_high_nudge = "high NES share" in (cal["rule_text"] or "")
                ok_nudge = has_high_nudge == scen["expected_nudge"]
                tag = "PASS" if ok_nudge else "FAIL"
                exp = "yes" if scen["expected_nudge"] else "no"
                got = "yes" if has_high_nudge else "no"
                print(f"  [{tag}] calibration: rate={cal['calibrated_rate']}  "
                      f"high-nudge={got}  (expect {exp})")
                if not ok_nudge:
                    all_ok = False

            sample_service_ids[sa2] = get_sample_service(con, sa2)
            print()

    print("=" * 70)
    print("BROWSER SMOKE-TEST URLS")
    print("=" * 70)
    print("Open each URL in a browser (review_server.py running on :8001).")
    print("In the Catchment Position card, confirm a new row labelled")
    print("'Non-English speaking at home' (or similar) with:")
    print("  - value displayed as a percentage with 1 decimal place ('31.1%')")
    print("  - a band chip matching the expected band below")
    print()
    for scen in SCENARIOS:
        sid = sample_service_ids.get(scen["sa2"])
        url = f"http://localhost:8001/centre/{sid}" if sid else "(no service in this SA2)"
        print(f"  {scen['name']:<32} {scen['expected_band']:<5}  {url}")
    print()

    print("=" * 70)
    if all_ok:
        print("[OK] DB-side smoke test passed for all three SA2s.")
        print("     Now visually confirm in browser as listed above.")
        return 0
    else:
        print("[FAIL] one or more SA2s failed DB-side smoke test.")
        print("       Review output above before browser smoke test.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
