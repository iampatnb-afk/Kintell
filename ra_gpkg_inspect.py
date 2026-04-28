"""
ra_gpkg_inspect.py

Read-only probe of the ABS Remoteness Areas GeoPackage:
  abs_data/ASGS_Ed3_2021_RA_GDA2020.gpkg

Output: stdout summary of layers, columns, sample row.
No file writes.

Usage:
  python ra_gpkg_inspect.py
"""
import re
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
GPKG_PATH = REPO_ROOT / "abs_data" / "ASGS_Ed3_2021_RA_GDA2020.gpkg"


def main():
    print("RA GeoPackage inspect - read-only")
    print(f"File: {GPKG_PATH}")
    print()

    if not GPKG_PATH.exists():
        print(f"ERROR: {GPKG_PATH} not found")
        return 1

    uri = f"file:{GPKG_PATH.as_posix()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    cur = conn.cursor()

    # All tables
    cur.execute("""
        SELECT name FROM sqlite_master
         WHERE type = 'table'
         ORDER BY name
    """)
    all_tables = [r[0] for r in cur.fetchall()]
    print(f"Total tables in GeoPackage: {len(all_tables)}")
    print()

    # Data layers
    try:
        cur.execute("""
            SELECT table_name, data_type, identifier
              FROM gpkg_contents
             ORDER BY table_name
        """)
        layers = cur.fetchall()
    except sqlite3.Error as e:
        print(f"ERROR reading gpkg_contents: {e}")
        layers = []

    print("Data layers (per gpkg_contents):")
    for name, dtype, ident in layers:
        print(f"  - {name} ({dtype}) [{ident}]")
    print()

    # Pick the most likely RA layer
    ra_layer = None
    for name, dtype, _ in layers:
        if dtype == "features" and ("RA" in name.upper() or "REMOTE" in name.upper()):
            ra_layer = name
            break
    if not ra_layer and layers:
        # Fall back to first features layer
        ra_layer = next((n for n, dt, _ in layers if dt == "features"), None)

    if not ra_layer:
        print("ERROR: no features layer found.")
        return 1

    print(f"RA layer: {ra_layer}")
    print()

    # Columns
    cur.execute(f"PRAGMA table_info('{ra_layer}')")
    cols = cur.fetchall()
    print(f"Columns ({len(cols)}):")
    for cid, cname, ctype, notnull, dflt, pk in cols:
        print(f"  {cid:>3}  {cname:<30}  {ctype}")
    print()

    # Row count
    try:
        cur.execute(f'SELECT COUNT(*) FROM "{ra_layer}"')
        row_count = cur.fetchone()[0]
        print(f"Feature count: {row_count:,}")
    except sqlite3.Error as e:
        print(f"COUNT failed: {e}")
        row_count = 0
    print()

    # Sample first row (omit geometry)
    geom_col_re = re.compile(r"^geom|geometry|shape", re.IGNORECASE)
    col_names = [c[1] for c in cols]
    select_cols = [c for c in col_names if not geom_col_re.match(c)]
    select_sql = ", ".join(f'"{c}"' for c in select_cols)
    try:
        cur.execute(f'SELECT {select_sql} FROM "{ra_layer}" LIMIT 5')
        rows = cur.fetchall()
        print(f"Sample rows ({len(rows)}, geometry omitted):")
        for ridx, row in enumerate(rows):
            print(f"  Row {ridx}:")
            for cname, val in zip(select_cols, row):
                v = str(val)[:80] if val is not None else "None"
                print(f"    {cname:<30}  {v}")
            print()
    except sqlite3.Error as e:
        print(f"Sample SELECT failed: {e}")

    # Detect RA-related and SA2-related cols
    ra_keys = [c for c in col_names if (
        "REMOTE" in c.upper() or
        c.upper() == "RA" or
        c.upper().startswith("RA_") or
        "ARIA" in c.upper()
    )]
    sa2_keys = [c for c in col_names if "SA2" in c.upper()]

    print(f"RA-related cols:  {ra_keys or 'NONE'}")
    print(f"SA2-related cols: {sa2_keys or 'NONE'}")
    print()

    print("=" * 64)
    if sa2_keys and ra_keys:
        print("OUTCOME: layer carries SA2 + RA -- direct lookup possible.")
    elif ra_keys:
        print("OUTCOME: layer carries RA polygons only.")
        print("  Path forward: point-in-polygon SA2 centroid -> RA polygon")
        print("  (same pattern as Step 1b).")
    else:
        print("OUTCOME: no RA columns visible. Manual inspection needed.")
    print("=" * 64)

    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
