"""
layer2_step1b_diag.py — Read-only diagnostic for SA2 polygon backfill.

Inputs:
  - data/kintell.db  (read-only)
  - abs_data/ASGS_2021_Main_Structure_GDA2020.gpkg  (read-only)

Output:
  - recon/layer2_step1b_diag.md
  - terminal summary

No DB or GPKG writes.

Validates:
  1. services table — count + bounds of rows with NULL sa2_code but populated lat/lng
  2. GeoPackage layer probe — SA2 layer accessible, CRS reported
  3. 5 sample candidate services — manual SA2 derivation via point-in-polygon
"""

from __future__ import annotations

import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = "data/kintell.db"
GPKG_PATH = "abs_data/ASGS_2021_Main_Structure_GDA2020.gpkg"
OUT_PATH = "recon/layer2_step1b_diag.md"
SAMPLE_N = 5
EXPECTED_RECOV = 887  # from project doc
RECOV_TOL = 20

# ---------------------------------------------------------------------------
# Preflight: files
# ---------------------------------------------------------------------------
for p in (DB_PATH, GPKG_PATH):
    if not Path(p).exists():
        print(f"ERROR: not found: {p}", file=sys.stderr)
        sys.exit(1)

# ---------------------------------------------------------------------------
# Preflight: imports
# ---------------------------------------------------------------------------
try:
    import geopandas as gpd
    import pyogrio
    import pandas as pd
    from shapely.geometry import Point
except ImportError as e:
    print(f"ERROR: required package missing ({e})", file=sys.stderr)
    print("Run: pip install --break-system-packages geopandas shapely pyogrio rtree",
          file=sys.stderr)
    sys.exit(2)

# ---------------------------------------------------------------------------
# DB connect (read-only)
# ---------------------------------------------------------------------------
try:
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
except sqlite3.Error:
    conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Discover services columns
svc_cols = [r[1] for r in cur.execute("PRAGMA table_info(services)").fetchall()]
if not svc_cols:
    print("ERROR: services table not found", file=sys.stderr)
    sys.exit(3)


def first_col(target_cols: list[str], candidates: list[str]) -> str | None:
    lower = {c.lower(): c for c in target_cols}
    for cand in candidates:
        if cand.lower() in lower:
            return lower[cand.lower()]
    return None


sa2_col = first_col(svc_cols, ["sa2_code", "sa2_code_2021"])
lat_col = first_col(svc_cols, ["lat", "latitude"])
lng_col = first_col(svc_cols, ["lng", "lon", "long", "longitude"])
state_col = first_col(svc_cols, ["state", "state_code", "state_abbr"])
id_col = first_col(svc_cols, ["service_id", "id", "service_approval_number", "san"])

missing = [n for n, v in [("sa2", sa2_col), ("lat", lat_col),
                          ("lng", lng_col), ("id", id_col)] if v is None]
if missing:
    print(f"ERROR: required columns not found in services: {missing}",
          file=sys.stderr)
    print(f"  available: {svc_cols}", file=sys.stderr)
    sys.exit(4)

# ---------------------------------------------------------------------------
# Output accumulator
# ---------------------------------------------------------------------------
lines: list[str] = []


def w(s: str = "") -> None:
    lines.append(s)


w("# Layer 2 Step 1b — Diagnostic A")
w("")
w(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
w(f"DB: `{DB_PATH}` (read-only)")
w(f"GPKG: `{GPKG_PATH}`")
w(f"Services columns detected: id=`{id_col}`, sa2=`{sa2_col}`, "
  f"lat=`{lat_col}`, lng=`{lng_col}`, state=`{state_col}`")
w("")
w("Read-only diagnostic. No DB or GPKG mutations.")
w("")

# ---------------------------------------------------------------------------
# 1. services NULL sa2_code analysis
# ---------------------------------------------------------------------------
w("## 1. `services` table — NULL `sa2_code` analysis")
w("")
n_total = cur.execute("SELECT COUNT(*) FROM services").fetchone()[0]
n_with = cur.execute(
    f'SELECT COUNT(*) FROM services WHERE "{sa2_col}" IS NOT NULL'
).fetchone()[0]
n_null = n_total - n_with
n_recov = cur.execute(
    f'SELECT COUNT(*) FROM services '
    f'WHERE "{sa2_col}" IS NULL AND "{lat_col}" IS NOT NULL AND "{lng_col}" IS NOT NULL'
).fetchone()[0]
n_unrecov = n_null - n_recov

pct_with = (100 * n_with / n_total) if n_total else 0.0
w(f"- Total services: **{n_total:,}**")
w(f"- With `{sa2_col}`: **{n_with:,}** ({pct_with:.2f}%)")
w(f"- NULL `{sa2_col}`: **{n_null:,}** ({100 - pct_with:.2f}%)")
w(f"  - With `{lat_col}/{lng_col}` (Step 1b candidates): **{n_recov:,}**")
w(f"  - Without lat/lng (unrecoverable here): **{n_unrecov:,}**")
w("")

verdict = ("✓ matches" if abs(n_recov - EXPECTED_RECOV) <= RECOV_TOL
           else "⚠ MISMATCH — investigate before apply")
w(f"Doc-stated expectation: ~{EXPECTED_RECOV} candidates. "
  f"Observed: {n_recov:,}. {verdict}")
w("")

# Bounds (CAST AS REAL — services.lat/lng may be stored as TEXT)
bounds = cur.execute(
    f'SELECT MIN(CAST("{lat_col}" AS REAL)), MAX(CAST("{lat_col}" AS REAL)), '
    f'MIN(CAST("{lng_col}" AS REAL)), MAX(CAST("{lng_col}" AS REAL)) '
    f'FROM services '
    f'WHERE "{sa2_col}" IS NULL '
    f'AND "{lat_col}" IS NOT NULL AND "{lng_col}" IS NOT NULL'
).fetchone()
w("Bounds of candidate lat/lng:")
w(f"- lat: {bounds[0]} → {bounds[1]}")
w(f"- lng: {bounds[2]} → {bounds[3]}")

# Suspicious points
n_zero = cur.execute(
    f'SELECT COUNT(*) FROM services '
    f'WHERE "{sa2_col}" IS NULL '
    f'AND CAST("{lat_col}" AS REAL) = 0 AND CAST("{lng_col}" AS REAL) = 0'
).fetchone()[0]
n_outside = cur.execute(
    f'SELECT COUNT(*) FROM services '
    f'WHERE "{sa2_col}" IS NULL '
    f'AND "{lat_col}" IS NOT NULL AND "{lng_col}" IS NOT NULL '
    f'AND (CAST("{lat_col}" AS REAL) < -45 '
    f'  OR CAST("{lat_col}" AS REAL) > -8 '
    f'  OR CAST("{lng_col}" AS REAL) < 95 '
    f'  OR CAST("{lng_col}" AS REAL) > 170)'
).fetchone()[0]
oddities = []
if n_zero:
    oddities.append(f"- {n_zero} candidate(s) at (0, 0) — null-island, won't match")
if n_outside:
    oddities.append(f"- {n_outside} candidate(s) outside AU rough bbox "
                    f"(lat -45..-8, lng 95..170)")
w("")
if oddities:
    w("⚠ Suspicious points:")
    for o in oddities:
        w(o)
else:
    w("✓ All candidates within plausible AU bbox.")
w("")

# By state
if state_col:
    w(f"### Candidates by `{state_col}`")
    w("")
    w(f"| {state_col} | total | null_sa2 | null_sa2_with_latlng |")
    w("|---|---:|---:|---:|")
    states = cur.execute(
        f'SELECT "{state_col}", COUNT(*) FROM services '
        f'GROUP BY "{state_col}" ORDER BY 2 DESC'
    ).fetchall()
    for sval, _ in states:
        n_s = cur.execute(
            f'SELECT COUNT(*) FROM services WHERE "{state_col}" IS ?',
            (sval,)
        ).fetchone()[0]
        n_s_null = cur.execute(
            f'SELECT COUNT(*) FROM services '
            f'WHERE "{state_col}" IS ? AND "{sa2_col}" IS NULL',
            (sval,)
        ).fetchone()[0]
        n_s_recov = cur.execute(
            f'SELECT COUNT(*) FROM services '
            f'WHERE "{state_col}" IS ? AND "{sa2_col}" IS NULL '
            f'AND "{lat_col}" IS NOT NULL AND "{lng_col}" IS NOT NULL',
            (sval,)
        ).fetchone()[0]
        label = sval if sval is not None else "(NULL)"
        w(f"| {label} | {n_s:,} | {n_s_null:,} | {n_s_recov:,} |")
    w("")

# ---------------------------------------------------------------------------
# 2. GeoPackage probe
# ---------------------------------------------------------------------------
w("## 2. GeoPackage probe")
w("")
gpkg_size_mb = os.path.getsize(GPKG_PATH) / (1024 * 1024)
w(f"Path: `{GPKG_PATH}`")
w(f"Size: {gpkg_size_mb:,.1f} MB")
w("")

print("[probe] listing GPKG layers ...")
try:
    layers_info = pyogrio.list_layers(GPKG_PATH)
except Exception as e:
    print(f"ERROR listing layers: {e}", file=sys.stderr)
    sys.exit(5)

layer_names = [str(row[0]) for row in layers_info]
w(f"Layers found: {len(layer_names)}")
w("")
w("| Layer | Geometry |")
w("|---|---|")
for row in layers_info:
    w(f"| `{row[0]}` | {row[1]} |")
w("")

# Pick SA2 layer
preferred = ["SA2_2021", "SA2_2021_AUST_GDA2020", "SA2"]
sa2_layer = None
for p in preferred:
    if p in layer_names:
        sa2_layer = p
        break
if sa2_layer is None:
    cands = [n for n in layer_names if n.upper().startswith("SA2")]
    if cands:
        sa2_layer = cands[0]
if sa2_layer is None:
    w("⚠ No SA2 layer found. Cannot proceed with sample derivations.")
    Path("recon").mkdir(exist_ok=True)
    Path(OUT_PATH).write_text("\n".join(lines), encoding="utf-8")
    print("ERROR: no SA2 layer in GPKG", file=sys.stderr)
    sys.exit(6)

w(f"Selected SA2 layer: **`{sa2_layer}`**")
w("")

print(f"[probe] reading SA2 layer '{sa2_layer}' (this may take 30-60s) ...")
sa2_gdf = gpd.read_file(GPKG_PATH, layer=sa2_layer, engine="pyogrio")
w(f"SA2 features: **{len(sa2_gdf):,}**")
w(f"SA2 columns: {', '.join(sa2_gdf.columns)}")
w(f"SA2 CRS: `{sa2_gdf.crs}`")
authority = sa2_gdf.crs.to_authority() if sa2_gdf.crs is not None else None
if authority:
    w(f"  - Authority: **{authority[0]}:{authority[1]}**")
w("")

# Detect SA2 attribute columns
sa2_cols_lower = {c.lower(): c for c in sa2_gdf.columns}


def pick(table_lookup: dict, cands: list[str]) -> str | None:
    for c in cands:
        if c.lower() in table_lookup:
            return table_lookup[c.lower()]
    return None


sa2_code_attr = pick(sa2_cols_lower,
                     ["sa2_code_2021", "sa2_main_2021", "sa2_code21", "sa2_code"])
sa2_name_attr = pick(sa2_cols_lower,
                     ["sa2_name_2021", "sa2_name21", "sa2_name"])
state_attr = pick(sa2_cols_lower,
                  ["ste_name_2021", "state_name_2021", "ste_name21", "state_name"])

w(f"SA2 attribute mapping: code=`{sa2_code_attr}`, "
  f"name=`{sa2_name_attr}`, state=`{state_attr}`")
w("")

# ---------------------------------------------------------------------------
# 3. Sample manual derivations
# ---------------------------------------------------------------------------
w(f"## 3. Sample manual SA2 derivation ({SAMPLE_N} services)")
w("")

sample_select = f'"{id_col}", CAST("{lat_col}" AS REAL) AS lat_r, CAST("{lng_col}" AS REAL) AS lng_r'
if state_col:
    sample_select += f', "{state_col}"'
sample_q = (
    f'SELECT {sample_select} FROM services '
    f'WHERE "{sa2_col}" IS NULL '
    f'AND "{lat_col}" IS NOT NULL AND "{lng_col}" IS NOT NULL '
    f'AND CAST("{lat_col}" AS REAL) BETWEEN -45 AND -8 '
    f'AND CAST("{lng_col}" AS REAL) BETWEEN 95 AND 170 '
    f'ORDER BY "{id_col}" '
    f'LIMIT {SAMPLE_N}'
)
sample = cur.execute(sample_q).fetchall()

if not sample:
    w("(no candidates available within AU bbox to sample)")
    hit = miss = 0
else:
    pts_data = []
    for row in sample:
        pts_data.append({
            "service_id": row[0],
            "lat": row[1],
            "lng": row[2],
            "service_state": row[3] if state_col else None,
            "geometry": Point(row[2], row[1]),  # (lon, lat)
        })
    pts_gdf = gpd.GeoDataFrame(pts_data, crs="EPSG:4326")

    print("[probe] reprojecting points + spatial join ...")
    pts_proj = pts_gdf.to_crs(sa2_gdf.crs)
    joined = gpd.sjoin(pts_proj, sa2_gdf, how="left", predicate="within")

    # Dedupe in case a point falls in >1 polygon (shouldn't, but be safe)
    joined = joined.drop_duplicates(subset=["service_id"], keep="first")

    w(f"| {id_col} | lat | lng | service_state | derived_sa2 | derived_name | sa2_state |")
    w("|---|---:|---:|---|---|---|---|")
    hit = miss = 0
    for _, r in joined.iterrows():
        code = r.get(sa2_code_attr) if sa2_code_attr else None
        name = r.get(sa2_name_attr) if sa2_name_attr else None
        sst = r.get(state_attr) if state_attr else None
        code_s = str(code) if code is not None and pd.notna(code) else "(no match)"
        name_s = str(name) if name is not None and pd.notna(name) else ""
        sst_s = str(sst) if sst is not None and pd.notna(sst) else ""
        svc_state = r["service_state"] if r["service_state"] is not None else ""
        if code_s != "(no match)":
            hit += 1
        else:
            miss += 1
        w(f"| {r['service_id']} | {r['lat']} | {r['lng']} | {svc_state} "
          f"| {code_s} | {name_s} | {sst_s} |")
    w("")
    w(f"Sample hit rate: **{hit}/{len(sample)}** ({miss} miss).")
w("")

# ---------------------------------------------------------------------------
# 4. Sanity / expectations
# ---------------------------------------------------------------------------
w("## 4. Sanity / expectations for apply phase")
w("")
w(f"- Doc-stated expectation: ~99% hit rate on the full {n_recov:,}-candidate set.")
w("- Misses likely from offshore/external-territory services (Norfolk Island, "
  "Christmas Island, Cocos (Keeling), Ashmore & Cartier).")
w("- Apply phase will:")
w("  1. Take timestamped backup `data/kintell.db.backup_pre_step1b_<ts>` (Standard 8)")
w("  2. Build spatial index over SA2 polygons (shapely STRtree or rtree)")
w("  3. Reproject service points (EPSG:4326) → SA2 CRS")
w("  4. UPDATE services SET sa2_code = ? WHERE service_id = ?")
w("  5. Sanity invariants:")
w("     - hit rate ≥ 99%")
w("     - every assigned `sa2_code` present in `abs_sa2_erp_annual.sa2_code`")
w("  6. audit_log row: `sa2_polygon_backfill_v1`")
w("")
w("## 5. Manual review checklist before apply")
w("")
w(f"- [ ] Candidate count ({n_recov:,}) is within tolerance of doc-stated 887")
w(f"- [ ] No suspicious bbox outliers (see §1; null-island={n_zero}, "
  f"outside-AU={n_outside})")
w(f"- [ ] SA2 layer CRS confirmed: `{sa2_gdf.crs}`")
w(f"- [ ] All sample services produced sensible SA2 matches (see §3)")
if state_col:
    w(f"- [ ] Sample-derived `sa2_state` matches `services.{state_col}` "
      f"where present (visual cross-check)")
w("")
w("---")
w("End of diagnostic.")
w("")

# ---------------------------------------------------------------------------
# Write
# ---------------------------------------------------------------------------
Path("recon").mkdir(exist_ok=True)
Path(OUT_PATH).write_text("\n".join(lines), encoding="utf-8")

conn.close()

print()
print(f"OK  wrote {OUT_PATH}")
print(f"    candidates (NULL sa2 with lat/lng): {n_recov:,}  (doc says ~{EXPECTED_RECOV})")
print(f"    SA2 layer: {sa2_layer}  ({len(sa2_gdf):,} features)")
print(f"    SA2 CRS: {sa2_gdf.crs}")
print(f"    sample hit rate: {hit}/{SAMPLE_N}")
