"""
init_db.py
────────────────────────────────────────────────────────────────
Creates an empty Kintell ownership-graph SQLite database from
the schema file.

Inputs:
  - ownership_graph_schema_v0_2.sql  (in remara-agent root)

Output:
  - data\\kintell.db

Usage:
  python init_db.py            # refuses to overwrite an existing DB
  python init_db.py --force    # recreates the DB from scratch

Run from: C:\\Users\\Patrick Bell\\remara-agent
"""

import sqlite3
import sys
from pathlib import Path

ROOT       = Path(__file__).resolve().parent
SCHEMA     = ROOT / "ownership_graph_schema_v0_2.sql"
DB_PATH    = ROOT / "data" / "kintell.db"
DATA_DIR   = DB_PATH.parent

FORCE = "--force" in sys.argv

def main():
    print(f"Schema file : {SCHEMA}")
    print(f"Database    : {DB_PATH}")

    if not SCHEMA.exists():
        print(f"\n[X] Schema file not found: {SCHEMA}")
        sys.exit(1)

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if DB_PATH.exists():
        if not FORCE:
            print("\n[!] Database already exists. Pass --force to recreate.")
            sys.exit(1)
        print("\n[!] --force: deleting existing database.")
        DB_PATH.unlink()

    sql = SCHEMA.read_text(encoding="utf-8")

    print("\nCreating database...")
    with sqlite3.connect(str(DB_PATH)) as conn:
        conn.executescript(sql)

    # Verify
    with sqlite3.connect(str(DB_PATH)) as conn:
        tables = [r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' ORDER BY name"
        ).fetchall()]
        indexes = [r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='index' AND name NOT LIKE 'sqlite_%' "
            "ORDER BY name"
        ).fetchall()]

    print(f"\n[OK] Created {len(tables)} tables and {len(indexes)} indexes.")
    print(f"\nTables:")
    for t in tables:
        print(f"  - {t}")
    print(f"\nFirst 5 indexes:")
    for i in indexes[:5]:
        print(f"  - {i}")
    print(f"  ... and {max(0, len(indexes) - 5)} more")

    size_kb = DB_PATH.stat().st_size / 1024
    print(f"\nDatabase size: {size_kb:.1f} KB")

if __name__ == "__main__":
    main()
