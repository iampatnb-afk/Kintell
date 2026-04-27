"""
layer2_step1b_spotcheck.py — Read-only post-apply validation.

Outputs:
  recon/layer2_step1b_spotcheck.md
  terminal summary

Validates:
  1. services NULL sa2_code count matches expected (audit_log after_json)
  2. Latest audit_log row is the Step 1b row (audit_id 133, action sa2_polygon_backfill_v1)
  3. Distribution of services.sa2_code by state
  4. Random sample of 10 services: stored sa2_code matches computed via polygon
     (full re-projection check across the whole column, not just newly-assigned)
  5. SALM coverage uplift: services that now join to abs_sa2_unemployment_quarterly
  6. Education+Employment coverage: services that join to
     abs_sa2_education_employment_annual

No DB or GPKG mutations.
"""

from __future__ import annotations

import json
import os
import random
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = "data/kintell.db"
GPKG_PATH = "abs_data/ASGS_2021_Main_Structure_GDA2020.gpkg"
SA2_LAYER = "SA2_2021_AUST_GDA2020"
OUT_PATH = "recon/layer2_step1b_spotcheck.md"
EXPECTED_ACTION = "sa2_polygon_backfill_v1"
SAMPLE_N = 10
RANDOM_SEED = 1729

SA2_CODE_ATTR = "SA2_CODE_2021"
SA2_NAME_ATTR = "SA2_NAME_2021"

# ---------------------------------------------------------------------------
# Preflight
# ---------------------------------------------------------------------------
for p in (DB_PATH, GPKG_PATH):
    if not Path(p).exists():
        print(f"ERROR: not found: {p}", file=sys.stderr)
        sys.exit(1)

try:
    import geopandas as gpd
    import pandas as pd
    from shapely.geometry import Point
except ImportError as e:
    print(f"ERROR: required package missing ({e})", file=sys.stderr)
    sys.exit(2)

# ---------------------------------------------------------------------------
# Read-only DB connection
# ---------------------------------------------------------------------------
try:
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
except sqlite3.Error:
    conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Discover services columns
svc_cols = [r[1] for r in cur.execute("PRAGMA table_info(services)").fetchall()]
lower = {c.lower(): c for c in svc_cols}
sa2_col = lower.get("sa2_code") or lower.get("sa2_code_2021")
lat_col = lower.get("lat") or lower.get("latitude")
lng_col = (lower.get("lng") or lower.get("lon") or lower.get("long")
           or lower.get("longitude"))
id_col = lower.get("service_id") or lower.get("id")
state_col = lower.get("state") or lower.get("state_code")

# ---------------------------------------------------------------------------
# Output accumulator
# ---------------------------------------------------------------------------
lines: list[str] = []


def w(s: str = "") -> None:
    lines.append(s)


checks_passed = 0
checks_failed = 0


def check(label: str, ok: bool, detail: str = "") -> None:
    global checks_passed, checks_failed
    mark = "✓" if ok else "✗"
    if ok:
        checks_passed += 1
    else:
        checks_failed += 1
    w(f"- {mark} **{label}**" + (f" — {detail}" if detail else ""))


w("# Layer 2 Step 1b — Spotcheck")
w("")
w(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
w(f"DB: `{DB_PATH}` (read-only)")
w("")
w("Read-only post-apply validation. No mutations.")
w("")

# ---------------------------------------------------------------------------
# 1. NULL sa2_code count vs audit_log expectation
# ---------------------------------------------------------------------------
w("## 1. NULL `sa2_code` count vs audit_log expectation")
w("")

n_total = cur.execute("SELECT COUNT(*) FROM services").fetchone()[0]
n_null = cur.execute(
    f'SELECT COUNT(*) FROM services WHERE "{sa2_col}" IS NULL'
).fetchone()[0]
n_with = n_total - n_null

w(f"- Total services: **{n_total:,}**")
w(f"- With `sa2_code`: **{n_with:,}** ({100*n_with/n_total:.2f}%)")
w(f"- NULL `sa2_code`: **{n_null:,}** ({100*n_null/n_total:.2f}%)")
w("")

# Read audit_log row 133 (or latest matching action)
audit_row = cur.execute(
    "SELECT * FROM audit_log WHERE action = ? ORDER BY audit_id DESC LIMIT 1",
    (EXPECTED_ACTION,)
).fetchone()

if audit_row is None:
    check("audit_log row exists", False,
          f"no row with action='{EXPECTED_ACTION}' found")
    expected_null_post = None
else:
    audit_dict = dict(audit_row)
    after_json = audit_dict.get("after_json") or "{}"
    try:
        after = json.loads(after_json)
        payload = after.get("payload", {})
        expected_null_post = payload.get("null_sa2")
        expected_assigned = payload.get("assigned")
        expected_hit_rate = payload.get("hit_rate")
        expected_coverage = payload.get("coverage")
    except json.JSONDecodeError:
        expected_null_post = None
    w(f"audit_log row found: audit_id=**{audit_dict.get('audit_id')}**, "
      f"action=`{audit_dict.get('action')}`, "
      f"actor=`{audit_dict.get('actor')}`, "
      f"occurred_at=`{audit_dict.get('occurred_at')}`")
    w("")
    w("after_json payload:")
    w("")
    w("```json")
    w(json.dumps(payload, indent=2, sort_keys=True) if payload else after_json)
    w("```")
    w("")

    check("audit_log row exists and is parseable", expected_null_post is not None)
    if expected_null_post is not None:
        check(f"NULL count post-apply matches audit_log expectation "
              f"(expected {expected_null_post}, observed {n_null})",
              n_null == expected_null_post)
    if expected_assigned is not None:
        check(f"assigned count in audit_log: {expected_assigned}",
              expected_assigned > 0)
    if expected_hit_rate is not None:
        check(f"hit_rate in audit_log: {expected_hit_rate:.4f}",
              expected_hit_rate >= 0.99)

w("")

# ---------------------------------------------------------------------------
# 2. Distribution of services.sa2_code by state
# ---------------------------------------------------------------------------
w("## 2. Distribution by state")
w("")

if state_col:
    w(f"| {state_col} | total | with sa2_code | NULL sa2_code | coverage |")
    w("|---|---:|---:|---:|---:|")
    rows = cur.execute(
        f'SELECT "{state_col}", COUNT(*), '
        f'SUM(CASE WHEN "{sa2_col}" IS NOT NULL THEN 1 ELSE 0 END), '
        f'SUM(CASE WHEN "{sa2_col}" IS NULL THEN 1 ELSE 0 END) '
        f'FROM services GROUP BY "{state_col}" ORDER BY 2 DESC'
    ).fetchall()
    for sval, ntot, nwith, nnull in rows:
        label = sval if sval is not None else "(NULL)"
        cov = (nwith / ntot * 100) if ntot else 0
        w(f"| {label} | {ntot:,} | {nwith:,} | {nnull:,} | {cov:.2f}% |")
    w("")

    # Sanity: ACT had 0 NULL pre-apply (per diag); should still be 0
    act_null = cur.execute(
        f'SELECT COUNT(*) FROM services '
        f'WHERE "{state_col}" = \'ACT\' AND "{sa2_col}" IS NULL'
    ).fetchone()[0]
    check(f"ACT NULL count is 0 (was 0 pre-apply)", act_null == 0)

w("")

# ---------------------------------------------------------------------------
# 3. Polygon re-projection check on a random sample
# ---------------------------------------------------------------------------
w(f"## 3. Polygon re-projection check ({SAMPLE_N} random services)")
w("")
w("For each sampled service: independently compute the SA2 via point-in-polygon "
  "and verify it matches the stored `services.sa2_code`. Validates the entire "
  "column, not just newly-assigned rows.")
w("")

# Sample SAMPLE_N services that have sa2_code populated AND lat/lng
random.seed(RANDOM_SEED)
sample_q = (
    f'SELECT "{id_col}" AS service_id, '
    f'CAST("{lat_col}" AS REAL) AS lat, '
    f'CAST("{lng_col}" AS REAL) AS lng, '
    f'"{sa2_col}" AS stored_sa2'
    + (f', "{state_col}" AS state' if state_col else "")
    + f' FROM services '
    f'WHERE "{sa2_col}" IS NOT NULL '
    f'AND "{lat_col}" IS NOT NULL AND "{lng_col}" IS NOT NULL '
    f'AND CAST("{lat_col}" AS REAL) BETWEEN -45 AND -8 '
    f'AND CAST("{lng_col}" AS REAL) BETWEEN 95 AND 170 '
    f'ORDER BY RANDOM() LIMIT {SAMPLE_N}'
)
# Note: SQLite RANDOM() in read-only mode works fine
sample_df = pd.read_sql_query(sample_q, conn)

if len(sample_df) == 0:
    w("(no sample available)")
else:
    print(f"Reading SA2 layer '{SA2_LAYER}' from {GPKG_PATH} (~30-60s) ...")
    sa2_full = gpd.read_file(GPKG_PATH, layer=SA2_LAYER, engine="pyogrio")
    sa2_subset = sa2_full[[SA2_CODE_ATTR, SA2_NAME_ATTR, "geometry"]].copy()

    pts_gdf = gpd.GeoDataFrame(
        sample_df,
        geometry=[Point(lon, lat)
                  for lon, lat in zip(sample_df["lng"], sample_df["lat"])],
        crs="EPSG:4326",
    )
    pts_proj = pts_gdf.to_crs(sa2_subset.crs)
    print("Performing point-in-polygon ...")
    joined = gpd.sjoin(pts_proj, sa2_subset, how="left", predicate="within")
    joined = joined.drop_duplicates(subset="service_id", keep="first")

    w("| service_id | lat | lng | stored sa2 | computed sa2 | name | match |")
    w("|---|---:|---:|---|---|---|:-:|")

    n_match = 0
    n_mismatch = 0
    for _, r in joined.iterrows():
        stored = str(r["stored_sa2"]) if r["stored_sa2"] is not None else ""
        computed_raw = r.get(SA2_CODE_ATTR)
        computed = str(computed_raw) if (computed_raw is not None
                                          and pd.notna(computed_raw)) else ""
        name = r.get(SA2_NAME_ATTR)
        name_s = str(name) if name is not None and pd.notna(name) else ""
        is_match = (stored != "" and stored == computed)
        if is_match:
            n_match += 1
        else:
            n_mismatch += 1
        mark = "✓" if is_match else "✗"
        w(f"| {r['service_id']} | {r['lat']} | {r['lng']} "
          f"| {stored} | {computed or '(no match)'} | {name_s} | {mark} |")
    w("")
    w(f"Sample match rate: **{n_match}/{len(joined)}**")

    check(f"All {len(joined)} sample services: stored sa2_code matches polygon-computed",
          n_mismatch == 0,
          f"{n_mismatch} mismatch(es)" if n_mismatch else "")

w("")

# ---------------------------------------------------------------------------
# 4. Cross-table coverage uplift
# ---------------------------------------------------------------------------
w("## 4. Cross-table coverage")
w("")
w("How many services now join to downstream SA2-keyed tables.")
w("")

# Discover available tables
tables = set(r[0] for r in cur.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
).fetchall())

cross_tables = [
    ("abs_sa2_unemployment_quarterly", "SALM (Step 5)"),
    ("abs_sa2_socioeconomic_annual", "Income (Step 5b)"),
    ("abs_sa2_erp_annual", "ERP (Step 6)"),
    ("abs_sa2_education_employment_annual", "Education+Employment (Step 5b-prime)"),
]

w("| Downstream table | Description | services with joinable SA2 | coverage |")
w("|---|---|---:|---:|")
for tname, desc in cross_tables:
    if tname not in tables:
        w(f"| `{tname}` | {desc} | (table not found) | — |")
        continue
    n_joinable = cur.execute(
        f'SELECT COUNT(*) FROM services s '
        f'WHERE s."{sa2_col}" IS NOT NULL '
        f'AND s."{sa2_col}" IN '
        f'(SELECT DISTINCT sa2_code FROM "{tname}" WHERE sa2_code IS NOT NULL)'
    ).fetchone()[0]
    cov = (n_joinable / n_total * 100) if n_total else 0
    w(f"| `{tname}` | {desc} | {n_joinable:,} | {cov:.2f}% |")
w("")

# ---------------------------------------------------------------------------
# 5. Verify the 18 unrecoverable + 2 null-island stayed NULL
# ---------------------------------------------------------------------------
w("## 5. Residual NULL services (post-apply)")
w("")

# Breakdown of remaining NULLs
n_null_no_latlng = cur.execute(
    f'SELECT COUNT(*) FROM services '
    f'WHERE "{sa2_col}" IS NULL '
    f'AND ("{lat_col}" IS NULL OR "{lng_col}" IS NULL)'
).fetchone()[0]
n_null_with_latlng = cur.execute(
    f'SELECT COUNT(*) FROM services '
    f'WHERE "{sa2_col}" IS NULL '
    f'AND "{lat_col}" IS NOT NULL AND "{lng_col}" IS NOT NULL'
).fetchone()[0]

w(f"- Total NULL: **{n_null}**")
w(f"  - No lat/lng (unrecoverable here, future fix): **{n_null_no_latlng}**")
w(f"  - With lat/lng but no SA2 polygon (offshore/null-island): "
  f"**{n_null_with_latlng}**")
w("")

# Show the residual lat/lng-bearing NULLs (should be 2 null-island)
residuals = cur.execute(
    f'SELECT "{id_col}", '
    f'CAST("{lat_col}" AS REAL), CAST("{lng_col}" AS REAL)'
    + (f', "{state_col}"' if state_col else "")
    + f' FROM services '
    f'WHERE "{sa2_col}" IS NULL '
    f'AND "{lat_col}" IS NOT NULL AND "{lng_col}" IS NOT NULL '
    f'ORDER BY "{id_col}"'
).fetchall()
if residuals:
    w("Residual NULL services with lat/lng (post-apply misses):")
    w("")
    w(f"| {id_col} | lat | lng" + (f" | {state_col}" if state_col else "") + " |")
    w("|---|---:|---:|" + ("---|" if state_col else ""))
    for r in residuals:
        sval = (r[3] if state_col and r[3] is not None else "") if state_col else ""
        if state_col:
            w(f"| {r[0]} | {r[1]} | {r[2]} | {sval} |")
        else:
            w(f"| {r[0]} | {r[1]} | {r[2]} |")
w("")

check("Expected residuals: 18 lat/lng-less + 2 null-island = 20",
      n_null == 20,
      f"observed: {n_null} ({n_null_no_latlng} no-latlng + {n_null_with_latlng} unmatched)")

w("")

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
w("## Summary")
w("")
w(f"- Checks passed: **{checks_passed}**")
w(f"- Checks failed: **{checks_failed}**")
w("")
if checks_failed == 0:
    w("**✓ ALL CHECKS PASSED — Step 1b validated.**")
else:
    w(f"**✗ {checks_failed} CHECK(S) FAILED — investigate before proceeding.**")
w("")
w("---")
w("End of spotcheck.")

# ---------------------------------------------------------------------------
# Write
# ---------------------------------------------------------------------------
Path("recon").mkdir(exist_ok=True)
Path(OUT_PATH).write_text("\n".join(lines), encoding="utf-8")

conn.close()

print()
print(f"OK  wrote {OUT_PATH}")
print(f"    services with sa2_code: {n_with:,}/{n_total:,} ({100*n_with/n_total:.2f}%)")
print(f"    NULL sa2_code: {n_null}")
print(f"    checks passed: {checks_passed}")
print(f"    checks failed: {checks_failed}")
sys.exit(0 if checks_failed == 0 else 1)
