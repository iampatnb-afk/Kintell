"""
probe_oi36_schema_check_v2.py
=============================
Read-only. Discovers the exact metric_name string used for NES share
in the long-format abs_sa2_education_employment_annual table.

The table is long-format: (sa2_code, year, metric_name, value). My
previous probes assumed wide-format columns. This probe lists distinct
metric_name values containing 'nes' so we can see exactly what string
A2 used (could be 'census_nes_share_pct', 'nes_share', 'nes_share_pct',
or something else).
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

        # 1. distinct metric_name values containing 'nes'
        print("=" * 60)
        print("metric_name values containing 'nes' (case-insensitive):")
        print("=" * 60)
        rows = con.execute(
            """
            SELECT DISTINCT metric_name, COUNT(*) as n
            FROM abs_sa2_education_employment_annual
            WHERE LOWER(metric_name) LIKE '%nes%'
            GROUP BY metric_name
            ORDER BY metric_name
            """
        ).fetchall()
        if not rows:
            print("  (no rows)")
        else:
            for r in rows:
                print(f"  {r['metric_name']:<40} count={r['n']}")
        print()

        # 2. all distinct metric names so I can also confirm naming style
        print("=" * 60)
        print("All distinct metric_name values in this table:")
        print("=" * 60)
        rows = con.execute(
            """
            SELECT DISTINCT metric_name, COUNT(*) as n
            FROM abs_sa2_education_employment_annual
            GROUP BY metric_name
            ORDER BY metric_name
            """
        ).fetchall()
        for r in rows:
            print(f"  {r['metric_name']:<40} count={r['n']}")
        print()

        # 3. sample rows for Bayswater
        print("=" * 60)
        print("Sample rows for SA2 211011251 (Bayswater Vic), any NES metric:")
        print("=" * 60)
        rows = con.execute(
            """
            SELECT sa2_code, year, metric_name, value
            FROM abs_sa2_education_employment_annual
            WHERE sa2_code = '211011251'
              AND LOWER(metric_name) LIKE '%nes%'
            ORDER BY year, metric_name
            """
        ).fetchall()
        if not rows:
            print("  (no NES rows for Bayswater)")
        else:
            for r in rows:
                print(f"  year={r['year']}  metric={r['metric_name']}  "
                      f"value={r['value']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
