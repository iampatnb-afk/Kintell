"""
gpkg_inspect.py

Read-only probe of the ABS GeoPackage to determine whether remoteness
fields are bundled alongside SA2 polygons.

A GeoPackage is a SQLite database — we open it directly with stdlib
sqlite3, no fiona / geopandas / GDAL needed.

Output: stdout summary of:
  - All non-internal tables (= layers)
  - Column list of any SA2-named layer
  - One sample row of attribute values from the SA2 layer
  - Recommendation: existing GeoPackage usable, or separate ABS file
    needed.

Usage:
  cd <repo root>
  python gpkg_inspect.py
"""
import re
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
GPKG_PATH = REPO_ROOT / "abs_data" / "ASGS_2021_Main_Structure_GDA2020.gpkg"


def main():
    print("ABS GeoPackage inspect - read-only")
    print(f"File: {GPKG_PATH}")
    print()

    if not GPKG_PATH.exists():
        print(f"ERROR: GeoPackage not found at {GPKG_PATH}")
        return 1

    uri = f"file:{GPKG_PATH.as_posix()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    cur = conn.cursor()

    # 1. List all user tables (= layers + GPKG metadata tables)
    cur.execute("""
        SELECT name FROM sqlite_master
         WHERE type = 'table'
         ORDER BY name
    """)
    all_tables = [r[0] for r in cur.fetchall()]
    print(f"All tables in GeoPackage: {len(all_tables)}")
    print()

    # 2. The actual data layers are listed in gpkg_contents
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

    # 3. Find the SA2 layer
    sa2_layer = None
    for name, dtype, ident in layers:
        if "SA2" in name.upper() and dtype == "features":
            sa2_layer = name
            break
    if not sa2_layer:
        for name in all_tables:
            if "SA2" in name.upper() and not name.startswith("gpkg_") \
                    and not name.startswith("rtree_"):
                sa2_layer = name
                break

    if not sa2_layer:
        print("ERROR: no SA2 layer found.")
        return 1

    print(f"SA2 layer: {sa2_layer}")
    print()

    # 4. List columns of the SA2 layer
    cur.execute(f"PRAGMA table_info('{sa2_layer}')")
    cols = cur.fetchall()  # cid, name, type, notnull, dflt, pk
    print(f"Columns ({len(cols)}):")
    for cid, cname, ctype, notnull, dflt, pk in cols:
        print(f"  {cid:>3}  {cname:<30}  {ctype}")
    print()

    # 5. Look for remoteness-related columns
    col_names = [c[1] for c in cols]
    rem_keys = [c for c in col_names if (
        "REMOTE" in c.upper() or
        "ARIA" in c.upper() or
        c.upper().startswith("RA_") or
        c.upper() == "RA"
    )]

    state_keys = [c for c in col_names if (
        "STATE" in c.upper() or
        c.upper().startswith("STE_") or
        c.upper().startswith("STE")
    )]

    print(f"Remoteness-related columns found: {rem_keys or 'NONE'}")
    print(f"State-related columns found:      {state_keys or 'NONE'}")
    print()

    # 6. Sample one row (drop geometry binary blob for readability)
    geom_col_re = re.compile(r"^geom|geometry|shape", re.IGNORECASE)
    select_cols = [c for c in col_names if not geom_col_re.match(c)]
    select_sql = ", ".join(f'"{c}"' for c in select_cols)
    try:
        cur.execute(f'SELECT {select_sql} FROM "{sa2_layer}" LIMIT 1')
        row = cur.fetchone()
    except sqlite3.Error as e:
        row = None
        print(f"ERROR sampling: {e}")
    if row:
        print("Sample row (first feature, geometry column omitted):")
        for cname, val in zip(select_cols, row):
            print(f"  {cname:<30}  {val}")
        print()

    # 7. Recommendation
    print("=" * 64)
    if rem_keys:
        print("OUTCOME: remoteness IS bundled in the existing GeoPackage.")
        print("Path A unblocked using existing file. No new download.")
        print(f"Use field(s): {rem_keys}")
    else:
        print("OUTCOME: remoteness is NOT bundled in this GeoPackage.")
        print("Will need to source an ABS SA2 -> Remoteness Area lookup.")
        print("Most likely candidate file:")
        print("  ABS publishes 'Remoteness Areas (RA) - 2021' as a")
        print("  separate ASGS layer / GeoPackage / Excel concordance.")
        print("  https://www.abs.gov.au/statistics/standards/")
        print("  australian-statistical-geography-standard-asgs-edition-3/")
        print("  jul2021-jun2026/access-and-downloads/digital-boundary-files")
    print("=" * 64)

    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
