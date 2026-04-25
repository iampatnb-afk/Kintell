"""
inspect_schema.py  v1
---------------------
Read-only. Dumps the column lists for the tables we care about and
shows a sample pending row from link_candidates so we can write
diagnostics against the real schema.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("data/kintell.db")
TABLES = ["link_candidates", "groups", "entities", "services"]


def section(title: str) -> None:
    print()
    print("=" * 72)
    print(f"  {title}")
    print("=" * 72)


def main() -> None:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row

    for t in TABLES:
        section(f"Schema: {t}")
        cols = con.execute(f"PRAGMA table_info({t})").fetchall()
        if not cols:
            print(f"  (table {t} not found)")
            continue
        for c in cols:
            # PRAGMA table_info columns: cid, name, type, notnull, dflt_value, pk
            print(f"  {c['cid']:>2}  {c['name']:<28} {c['type']:<14} "
                  f"{'NOT NULL' if c['notnull'] else '':<8} "
                  f"{'PK' if c['pk'] else ''}")

    section("link_candidates: status breakdown")
    for row in con.execute(
        "SELECT status, COUNT(*) AS n FROM link_candidates GROUP BY status"
    ).fetchall():
        print(f"  {row['status']:<12} {row['n']}")

    section("link_candidates: one pending row (all columns)")
    row = con.execute(
        "SELECT * FROM link_candidates WHERE status = 'pending' LIMIT 1"
    ).fetchone()
    if row is None:
        print("  (no pending rows)")
    else:
        for k in row.keys():
            v = row[k]
            s = str(v)
            if len(s) > 200:
                s = s[:200] + f"... [{len(str(v)) - 200} more chars]"
            print(f"  {k:<28} {s}")

    con.close()


if __name__ == "__main__":
    main()
