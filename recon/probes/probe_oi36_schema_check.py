"""
probe_oi36_schema_check.py
==========================
Quick read-only check of the abs_sa2_education_employment_annual schema
so the smoke probe can be re-shipped with the correct year column name.

The previous smoke probe assumed 'year_period' — it does not exist.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path


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
    with sqlite3.connect(uri, uri=True) as con:
        con.row_factory = sqlite3.Row

        # 1. PRAGMA table_info — list all columns
        print("=" * 60)
        print("Columns in abs_sa2_education_employment_annual:")
        print("=" * 60)
        cols = con.execute(
            "PRAGMA table_info(abs_sa2_education_employment_annual)"
        ).fetchall()
        for c in cols:
            print(f"  {c['cid']:>3}  {c['name']:<35}  {c['type']}")
        print()

        # 2. Sample row for the verification SA2
        print("=" * 60)
        print("Sample rows for SA2 211011251 (Bayswater Vic):")
        print("=" * 60)
        rows = con.execute(
            """
            SELECT *
            FROM abs_sa2_education_employment_annual
            WHERE sa2_code = '211011251'
              AND census_nes_share_pct IS NOT NULL
            LIMIT 3
            """
        ).fetchall()
        if not rows:
            print("  no rows with non-null census_nes_share_pct")
        else:
            for r in rows:
                d = dict(r)
                print("  " + " | ".join(f"{k}={d[k]}" for k in d))
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
