r"""
A2 scoping probe — NES (Non-English Speaking household share) at SA2.

Per OI-19 + STD-34: nes_share_pct is the dormant nudge in
calibrate_participation_rate. Goal: confirm whether NES is already
partly ingested, or whether A2 is a from-scratch ABS workbook ingest.

Read-only. Run from repo root:
    python recon\probes\probe_a2_nes_inventory.py
"""

import re
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path("data") / "kintell.db"
ABS_DIR = Path("abs_data")
CALIB_MODULE = Path("catchment_calibration.py")


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

    # -----------------------------------------------------------------
    section("1. abs_sa2_* tables — inventory")
    rows = cur.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type='table' AND name LIKE 'abs_sa2_%' "
        "ORDER BY name"
    ).fetchall()
    for (t,) in rows:
        try:
            count = cur.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
            cols = [c[1] for c in cur.execute(f'PRAGMA table_info("{t}")').fetchall()]
            print(f"  {t} ({count:,} rows) cols={cols}")
        except Exception as e:
            print(f"  {t}: error {e}")

    # -----------------------------------------------------------------
    section("2. Distinct metric_name values in LONG-format tables")
    for tbl in ("abs_sa2_socioeconomic_annual", "abs_sa2_education_employment_annual"):
        try:
            metrics = cur.execute(
                f'SELECT DISTINCT metric_name FROM "{tbl}" ORDER BY metric_name'
            ).fetchall()
        except Exception as e:
            print(f"\n  {tbl}: error {e}")
            continue
        print(f"\n  --- {tbl} ({len(metrics)} distinct metrics) ---")
        for (m,) in metrics:
            print(f"    {m}")

    # -----------------------------------------------------------------
    section("3. Search for language / NES / LOTE / English markers")
    keywords = ["language", "nes", "lote", "english", "born", "country", "speaking"]
    for tbl in ("abs_sa2_socioeconomic_annual", "abs_sa2_education_employment_annual"):
        try:
            print(f"\n  --- {tbl} ---")
            for kw in keywords:
                like = f"%{kw}%"
                hits = cur.execute(
                    f'SELECT DISTINCT metric_name FROM "{tbl}" '
                    f'WHERE LOWER(metric_name) LIKE ? '
                    f'LIMIT 5',
                    (like,),
                ).fetchall()
                if hits:
                    print(f"    keyword '{kw}': {[h[0] for h in hits]}")
        except Exception as e:
            print(f"  error: {e}")

    # -----------------------------------------------------------------
    section("4. Other tables that might hold NES data")
    other_tables = cur.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type='table' AND name NOT LIKE 'abs_sa2_%' "
        "AND name NOT LIKE 'sqlite_%' "
        "ORDER BY name"
    ).fetchall()

    nes_candidate_names = []
    for (t,) in other_tables:
        if any(s in t.lower() for s in ["census", "tsp", "language", "nes", "demograph"]):
            nes_candidate_names.append(t)

    if nes_candidate_names:
        print("  Candidate tables by name:")
        for t in nes_candidate_names:
            try:
                count = cur.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
                cols = [c[1] for c in cur.execute(f'PRAGMA table_info("{t}")').fetchall()]
                print(f"    {t} ({count:,} rows) cols={cols}")
            except Exception:
                pass
    else:
        print("  No tables matching census/tsp/language/nes/demograph in name.")

    # Check all non-abs_sa2 tables for a column called nes_share_pct or similar
    print("\n  Columns matching nes / language / lote across all tables:")
    found_cols = []
    for (t,) in other_tables + rows:
        try:
            cols = cur.execute(f'PRAGMA table_info("{t}")').fetchall()
            for c in cols:
                cn = c[1].lower()
                if any(s in cn for s in ["nes", "language", "lote", "english", "born_overseas"]):
                    found_cols.append((t, c[1]))
        except Exception:
            pass
    if found_cols:
        for t, c in found_cols:
            print(f"    {t}.{c}")
    else:
        print("    (none found)")

    con.close()

    # -----------------------------------------------------------------
    section("5. catchment_calibration.py — how is nes_share_pct used?")
    if not CALIB_MODULE.exists():
        print(f"  {CALIB_MODULE} not found.")
    else:
        text = CALIB_MODULE.read_text(encoding="utf-8")
        print(f"  File: {len(text):,} chars, {text.count(chr(10))} lines")
        relevant = [
            (i, line.rstrip())
            for i, line in enumerate(text.splitlines(), start=1)
            if "nes" in line.lower() or "language" in line.lower()
        ]
        print(f"  References to NES / language: {len(relevant)}")
        for i, line in relevant[:30]:
            trimmed = line if len(line) <= 110 else line[:107] + "..."
            print(f"    L{i}: {trimmed}")

    # -----------------------------------------------------------------
    section("6. abs_data/ source files — Census-flavoured inventory")
    if not ABS_DIR.exists():
        print(f"  {ABS_DIR} not found.")
    else:
        for f in sorted(ABS_DIR.iterdir()):
            if not f.is_file():
                continue
            name = f.name.lower()
            if any(s in name for s in ["census", "tsp", "language", "lote", "general community", "g0", "g04", "g05"]):
                size_mb = f.stat().st_size / (1024 * 1024)
                print(f"    {f.name} ({size_mb:.1f} MB)")
        print()
        # Also show any directories that might contain TSP files
        for f in sorted(ABS_DIR.iterdir()):
            if f.is_dir():
                print(f"  Subdir: {f.name}/")
                for sub in sorted(f.iterdir())[:10]:
                    if sub.is_file():
                        size_mb = sub.stat().st_size / (1024 * 1024)
                        print(f"    {sub.name} ({size_mb:.1f} MB)")
                    else:
                        print(f"    {sub.name}/")

    print()
    print("Done. Read-only probe — no DB mutation.")


if __name__ == "__main__":
    main()
