r"""
A2-wire probe — read populate_service_catchment_cache.py to find:
  - calibrate_participation_rate import + call site
  - how income_decile, female_lfp_pct, aria_band are sourced
  - any existing nes_share_pct reference (likely the dormant None placeholder)
  - service_catchment_cache schema (where calibrated_rate persists)

Read-only. Run from repo root:
    python recon\probes\probe_a2_wire.py
"""

import re
import sqlite3
import sys
from pathlib import Path

POPULATOR = Path("populate_service_catchment_cache.py")
DB_PATH = Path("data") / "kintell.db"


def section(title):
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def show_block(text, line_no, before=8, after=20):
    lines = text.splitlines()
    start = max(0, line_no - 1 - before)
    end = min(len(lines), line_no + after)
    for i in range(start, end):
        marker = ">>" if i == line_no - 1 else "  "
        print(f"  {marker} L{i+1:4}: {lines[i]}")


def main():
    if not POPULATOR.exists():
        print(f"ERROR: {POPULATOR} not found.")
        sys.exit(1)
    if not DB_PATH.exists():
        print(f"ERROR: {DB_PATH} not found.")
        sys.exit(1)

    text = POPULATOR.read_text(encoding="utf-8")
    lines = text.splitlines()
    print(f"  {POPULATOR}: {len(text):,} chars, {len(lines)} lines")

    # ----------------------------------------------------------------
    section("1. Import lines")
    for i, ln in enumerate(lines, start=1):
        if "calibrat" in ln.lower() or "import" in ln and ("catchment" in ln.lower() or "calibration" in ln.lower()):
            print(f"  L{i:4}: {ln}")

    # ----------------------------------------------------------------
    section("2. calibrate_participation_rate call sites")
    for i, ln in enumerate(lines, start=1):
        if "calibrate_participation_rate" in ln:
            print(f"\n  Hit at L{i}:")
            show_block(text, i, before=10, after=15)

    # ----------------------------------------------------------------
    section("3. References to nes_share / nes_share_pct in code")
    for i, ln in enumerate(lines, start=1):
        if "nes_share" in ln.lower() or "nes_share_pct" in ln.lower():
            print(f"  L{i:4}: {ln}")

    # ----------------------------------------------------------------
    section("4. SQL queries — find how income_decile / female_lfp_pct / aria_band are sourced")
    # Look for SELECT statements that mention any of these
    sql_kw = ["income_decile", "female_lfp", "aria_band", "irsd_decile", "lfp_females"]
    for i, ln in enumerate(lines, start=1):
        if any(k in ln for k in sql_kw):
            print(f"  L{i:4}: {ln.rstrip()}")

    # ----------------------------------------------------------------
    section("5. SQL FROM clauses — which tables are read")
    for i, ln in enumerate(lines, start=1):
        m = re.search(r"\bFROM\s+([\w_\"`]+)", ln, re.IGNORECASE)
        if m:
            print(f"  L{i:4}: {ln.strip()[:100]}")

    # ----------------------------------------------------------------
    section("6. service_catchment_cache schema (DB)")
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    try:
        cols = cur.execute('PRAGMA table_info("service_catchment_cache")').fetchall()
        for c in cols:
            print(f"  {c[1]:<35} {c[2]}")
        rc = cur.execute('SELECT COUNT(*) FROM service_catchment_cache').fetchone()[0]
        print(f"\n  Row count: {rc:,}")

        # Sample of calibrated_rate values for high/low NES SA2s
        print("\n  Current calibrated_rate for verification SA2s:")
        verify = [
            ("211011251", "Bayswater Vic (NES 31.1%)"),
            ("118011341", "Bondi Junction-Waverly NSW (NES 23.6%)"),
            ("506031124", "Bentley-Wilson-St James WA (NES 37.6%)"),
        ]
        for sa2, name in verify:
            row = cur.execute(
                "SELECT calibrated_rate, rule_text FROM service_catchment_cache "
                "WHERE sa2_code = ? LIMIT 1",
                (sa2,),
            ).fetchone()
            if row:
                rate = row[0]
                rule = row[1] or ""
                rule_short = rule[:120] + "..." if len(rule) > 120 else rule
                print(f"    {sa2} ({name}): rate={rate}")
                print(f"      rule_text: {rule_short}")
            else:
                print(f"    {sa2} ({name}): no row in service_catchment_cache")
    except Exception as e:
        print(f"  ERROR: {e}")
    con.close()

    print()
    print("Done. Read-only probe — no DB mutation.")


if __name__ == "__main__":
    main()
