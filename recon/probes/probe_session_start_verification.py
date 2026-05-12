"""
probe_session_start_verification.py
====================================
Read-only session-start verification gate.

Purpose
-------
Confirm the database state matches the monolith's
"Verification SA2s end-state" block for SA2 211011251 (Bayswater Vic)
at end-of-day 2026-05-04.

Expected per kintell_project_status_2026-05-04.txt:
  - SA2 211011251 row(s) present in service_catchment_cache
  - calibrated_rate = 0.48 (single value across all services in this SA2)
  - rule_text contains the fragment: "0.02 high NES share (0.31)"
    (the en-dash before "0.02" is dropped from the substring check
    to avoid Unicode minus vs ASCII minus mismatches on Windows)

This script does NOT mutate the DB. The sqlite connection is opened
read-only via the URI form (?mode=ro). No INSERT, UPDATE, DELETE, or
DDL is executed. No audit_log row is written.

Usage
-----
From the repo root in PowerShell:

    python recon\probes\probe_session_start_verification.py

Exit codes
----------
  0  PASS   — state matches monolith
  1  FAIL   — state diverges (operator should flag before any work)
  2  ERROR  — DB file not found
  3  ERROR  — no rows for the verification SA2
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

VERIFICATION_SA2 = "211011251"   # Bayswater Vic
EXPECTED_RATE = 0.48
EXPECTED_NUDGE_FRAGMENT = "0.02 high NES share"
EXPECTED_SHARE_FRAGMENT = "(0.31)"


def find_db() -> Path | None:
    """Locate data/kintell.db relative to the script or CWD.

    Script location is normally repo_root/recon/probes/<script>.py, so
    parents[2] resolves to repo root. Falls back to CWD/data if the
    repo-root candidate is missing (operator may run from a different
    working directory)."""
    candidates = [
        Path(__file__).resolve().parents[2] / "data" / "kintell.db",
        Path.cwd() / "data" / "kintell.db",
        Path.cwd().parent / "data" / "kintell.db",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def main() -> int:
    db_path = find_db()
    if db_path is None:
        print("[ERROR] could not locate data/kintell.db relative to the "
              "script or current directory.")
        print("        run this from the repo root, e.g. C:\\path\\to\\kintell-repo")
        return 2

    uri = f"file:{db_path.as_posix()}?mode=ro"
    print(f"[probe] db    : {db_path}")
    print(f"[probe] mode  : read-only (sqlite URI)")
    print(f"[probe] sa2   : {VERIFICATION_SA2} (Bayswater Vic)")
    print()

    with sqlite3.connect(uri, uri=True) as con:
        con.row_factory = sqlite3.Row
        rows = con.execute(
            """
            SELECT service_id,
                   sa2_code,
                   calibrated_rate,
                   rule_text
            FROM service_catchment_cache
            WHERE sa2_code = ?
            ORDER BY service_id
            """,
            (VERIFICATION_SA2,),
        ).fetchall()

    if not rows:
        print(f"[ERROR] no rows in service_catchment_cache for "
              f"SA2 {VERIFICATION_SA2}")
        return 3

    # The calibration rule for this SA2 is SA2-driven (NES, ARIA,
    # income decile, female LFP — all SA2-level inputs), so every
    # service row in this SA2 should carry the same rate + rule_text.
    distinct_rates = sorted({r["calibrated_rate"] for r in rows})
    distinct_rules = {r["rule_text"] for r in rows}

    print(f"[probe] rows for SA2 {VERIFICATION_SA2}: {len(rows)}")
    print(f"[probe] distinct calibrated_rate values: {distinct_rates}")
    print(f"[probe] distinct rule_text values      : {len(distinct_rules)}")
    print()

    # Sample row (first by service_id ordering)
    sample = rows[0]
    print("Sample row:")
    print(f"  service_id      : {sample['service_id']}")
    print(f"  sa2_code        : {sample['sa2_code']}")
    print(f"  calibrated_rate : {sample['calibrated_rate']}")
    print(f"  rule_text       : {sample['rule_text']}")
    print()

    # ----- Verification checks ------------------------------------------
    rate_single = len(distinct_rates) == 1
    rate_ok = rate_single and abs(distinct_rates[0] - EXPECTED_RATE) < 1e-9

    nudge_ok = all(EXPECTED_NUDGE_FRAGMENT in r["rule_text"] for r in rows)
    share_ok = all(EXPECTED_SHARE_FRAGMENT in r["rule_text"] for r in rows)

    print("=" * 64)
    print("VERIFICATION RESULT")
    print("=" * 64)
    print(f"  calibrated_rate is single-valued ............... "
          f"{'PASS' if rate_single else 'FAIL'}")
    print(f"  calibrated_rate == 0.48 ........................ "
          f"{'PASS' if rate_ok else 'FAIL'}")
    print(f"  rule_text contains '{EXPECTED_NUDGE_FRAGMENT}' .. "
          f"{'PASS' if nudge_ok else 'FAIL'}")
    print(f"  rule_text contains '{EXPECTED_SHARE_FRAGMENT}' . "
          f"{'PASS' if share_ok else 'FAIL'}")
    print()

    if rate_ok and nudge_ok and share_ok:
        print("[OK] monolith verification SA2 end-state confirmed.")
        print("     safe to proceed with session-start gate report.")
        return 0

    print("[MISMATCH] state diverges from monolith.")
    print("           DO NOT begin work — flag the discrepancy first.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
