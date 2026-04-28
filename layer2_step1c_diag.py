"""
layer2_step1c_diag.py — Read-only diagnostic for the SA2 overwrite rebuild.

Inputs:
  - data/kintell.db                                       (read-only)
  - abs_data/ASGS_2021_Main_Structure_GDA2020.gpkg        (read-only)

Output:
  - recon/layer2_step1c_diag.md
  - terminal summary

No DB or GPKG mutation. Mirrors layer2_step1b_diag.py structure but
scoped to the OVERWRITE problem: every active service with lat/lng,
not just the NULL-sa2 candidate set.

What we measure:
  1. Candidate set — all active services with lat/lng (= the population
     Step 1c will touch).
  2. Per-state cross-state mismatch counts (services.state vs sa2_cohort.state_name
     under current sa2_code) — the smoking gun (~1,435 from earlier probe).
  3. Sample 10 cross-state mismatches: derive their TRUE SA2 via point-
     in-polygon, show before/after.
  4. Sample 10 currently-correct rows: confirm polygon derivation
     leaves them unchanged (sanity check that we won't regress good data).
  5. GeoPackage layer probe (CRS + feature count) for Step 1c apply
     parity.

This is the gate before generating layer2_step1c_apply.py output —
if the polygon derivation doesn't reproduce the known-good rows, we
stop and re-think. If it consistently fixes the cross-state mismatches,
we proceed to dry-run.
"""

from __future__ import annotations

import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = "data/kintell.db"
GPKG_PATH = "abs_data/ASGS_2021_Main_Structure_GDA2020.gpkg"
OUT_PATH = "recon/layer2_step1c_diag.md"
SAMPLE_MM = 10  # cross-state mismatches to derive
SAMPLE_OK = 10  # currently-correct rows to confirm

SA2_LAYER = "SA2_2021_AUST_GDA2020"
SA2_CODE_ATTR = "SA2_CODE_2021"
SA2_NAME_ATTR = "SA2_NAME_2021"
SA2_STATE_ATTR = "STATE_NAME_2021"

# Map services.state (2-3 letter) <-> sa2_cohort.state_name (full)
SVC_STATE_TO_FULL = {
    "NSW": "New South Wales",
    "VIC": "Victoria",
    "QLD": "Queensland",
    "SA": "South Australia",
    "WA": "Western Australia",
    "TAS": "Tasmania",
    "NT": "Northern Territory",
    "ACT": "Australian Capital Territory",
}


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
    import pyogrio  # noqa: F401
    from shapely.geometry import Point
except ImportError as e:
    print(f"ERROR: required package missing ({e})", file=sys.stderr)
    print("Run: pip install --break-system-packages geopandas shapely "
          "pyogrio rtree", file=sys.stderr)
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


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
lines: list[str] = []


def w(s: str = "") -> None:
    lines.append(s)


w("# Layer 2 Step 1c — Diagnostic (overwrite rebuild)")
w("")
w(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
w(f"DB: `{DB_PATH}` (read-only)")
w(f"GPKG: `{GPKG_PATH}`")
w("")
w("Read-only diagnostic. No DB or GPKG mutations.")
w("")
w("**Premise.** Step 1 used a postcode→SA2 concordance which is 1:1, so "
  "for postcodes spanning multiple SA2s the publisher chose arbitrarily. "
  "Step 1b corrected only the 887 NULLs, not the 17,336 already-populated "
  "(potentially wrong) rows. The May 2026 cross-state-mismatch probe "
  "found ~1,435 services whose `services.state` disagrees with their "
  "currently-assigned SA2's state. Step 1c is the OVERWRITE rebuild: "
  "every active service with lat/lng gets its sa2_code re-derived "
  "by point-in-polygon, regardless of the existing value.")
w("")

# ---------------------------------------------------------------------------
# 1. Candidate set
# ---------------------------------------------------------------------------
w("## 1. Candidate set")
w("")
n_active = cur.execute(
    "SELECT COUNT(*) FROM services WHERE is_active = 1"
).fetchone()[0]
n_with_latlng = cur.execute(
    "SELECT COUNT(*) FROM services "
    " WHERE is_active = 1 "
    "   AND lat IS NOT NULL AND lng IS NOT NULL"
).fetchone()[0]
n_with_sa2 = cur.execute(
    "SELECT COUNT(*) FROM services "
    " WHERE is_active = 1 AND sa2_code IS NOT NULL"
).fetchone()[0]
n_no_latlng = n_active - n_with_latlng

w(f"- Active services: **{n_active:,}**")
w(f"- With lat/lng (Step 1c will touch these): **{n_with_latlng:,}**")
w(f"- With sa2_code populated: **{n_with_sa2:,}**")
w(f"- Without lat/lng (untouchable here, retained as-is): "
  f"**{n_no_latlng:,}**")
w("")

# ---------------------------------------------------------------------------
# 2. Cross-state mismatch baseline
# ---------------------------------------------------------------------------
w("## 2. Cross-state mismatch baseline (current state)")
w("")
w("Services where `services.state` disagrees with the state of their "
  "currently-assigned SA2 via `sa2_cohort`. These are the rows Step 1c "
  "is intended to correct.")
w("")

# Build a single CASE expression using SVC_STATE_TO_FULL inverted
# to translate sa2_cohort.state_name back to 2-3 letter for compare
case_when = " ".join(
    f"WHEN '{full}' THEN '{abbr}'"
    for abbr, full in SVC_STATE_TO_FULL.items()
)
mm_sql = f"""
    SELECT s.state AS svc_state,
           c.state_name AS sa2_state,
           COUNT(*) AS n
      FROM services s
      JOIN sa2_cohort c ON s.sa2_code = c.sa2_code
     WHERE s.is_active = 1
       AND s.lat IS NOT NULL AND s.lng IS NOT NULL
       AND s.state IS NOT NULL
       AND s.state != CASE c.state_name
            {case_when}
            ELSE c.state_name END
     GROUP BY s.state, c.state_name
     ORDER BY n DESC
"""
mm_rows = cur.execute(mm_sql).fetchall()
total_mm = sum(r["n"] for r in mm_rows)

w(f"**Total cross-state mismatches: {total_mm:,}** "
  f"(out of {n_with_latlng:,} candidates with lat/lng — "
  f"{100 * total_mm / n_with_latlng:.2f}%)")
w("")
w("| services.state | sa2_cohort.state_name | services |")
w("|---|---|---:|")
for r in mm_rows:
    w(f"| {r['svc_state']} | {r['sa2_state']} | {r['n']:,} |")
w("")

# Within-state remoteness mismatches
ra_mm = cur.execute("""
    SELECT COUNT(*)
      FROM services s
      JOIN sa2_cohort c ON s.sa2_code = c.sa2_code
     WHERE s.is_active = 1
       AND s.aria_plus IS NOT NULL
       AND c.ra_name IS NOT NULL
       AND s.aria_plus != c.ra_name
""").fetchone()[0]
w(f"**Within-state remoteness mismatches** "
  f"(services.aria_plus != sa2_cohort.ra_name): **{ra_mm:,}**")
w("")

# ---------------------------------------------------------------------------
# 3. Load SA2 polygons + reproject
# ---------------------------------------------------------------------------
print("[probe] reading SA2 polygons (~30-60s)...", flush=True)
sa2_full = gpd.read_file(GPKG_PATH, layer=SA2_LAYER, engine="pyogrio")
sa2_gdf = sa2_full[
    [SA2_CODE_ATTR, SA2_NAME_ATTR, SA2_STATE_ATTR, "geometry"]
].copy()
sa2_features = len(sa2_gdf)
sa2_authority = (sa2_gdf.crs.to_authority()
                 if sa2_gdf.crs is not None else None)

w("## 3. GeoPackage SA2 layer")
w("")
w(f"- Layer: `{SA2_LAYER}`")
w(f"- Features: **{sa2_features:,}**")
w(f"- CRS: `{sa2_gdf.crs}`")
if sa2_authority:
    w(f"- Authority: **{sa2_authority[0]}:{sa2_authority[1]}**")
w(f"- File size: "
  f"**{os.path.getsize(GPKG_PATH) / (1024*1024):,.1f} MB**")
w("")


# Helper: derive SA2 for a list of (service_id, lat, lng) tuples
def derive_sa2_for(rows: list[sqlite3.Row]) -> pd.DataFrame:
    pts = pd.DataFrame([
        {"service_id": r["service_id"],
         "lat": float(r["lat"]),
         "lng": float(r["lng"])}
        for r in rows
    ])
    if pts.empty:
        return pts
    points_gdf = gpd.GeoDataFrame(
        pts,
        geometry=[Point(lon, lat)
                  for lon, lat in zip(pts["lng"], pts["lat"])],
        crs="EPSG:4326",
    )
    points_proj = points_gdf.to_crs(sa2_gdf.crs)
    joined = gpd.sjoin(points_proj, sa2_gdf,
                       how="left", predicate="within")
    joined = joined.drop_duplicates(subset="service_id", keep="first")
    return joined


# ---------------------------------------------------------------------------
# 4. Sample cross-state mismatches: derive TRUE SA2
# ---------------------------------------------------------------------------
w(f"## 4. Sample of {SAMPLE_MM} cross-state mismatches (before / after)")
w("")
w("For each, the existing `sa2_code` (from postcode-derived Step 1) is "
  "shown alongside the polygon-derived SA2 from the service's lat/lng. "
  "If Step 1c is right, every row should show the after-state matching "
  "`services.state`.")
w("")

mm_sample_sql = f"""
    SELECT s.service_id, s.service_name, s.state AS svc_state,
           s.suburb, s.postcode,
           CAST(s.lat AS REAL)  AS lat,
           CAST(s.lng AS REAL)  AS lng,
           s.sa2_code           AS old_sa2_code,
           s.sa2_name           AS old_sa2_name,
           c.state_name         AS old_sa2_state
      FROM services s
      JOIN sa2_cohort c ON s.sa2_code = c.sa2_code
     WHERE s.is_active = 1
       AND s.lat IS NOT NULL AND s.lng IS NOT NULL
       AND s.state IS NOT NULL
       AND s.state != CASE c.state_name
            {case_when}
            ELSE c.state_name END
     ORDER BY s.service_id
     LIMIT {SAMPLE_MM}
"""
mm_sample = cur.execute(mm_sample_sql).fetchall()

if not mm_sample:
    w("(no cross-state mismatches sampled — investigate, was expecting "
      f"~{total_mm:,})")
else:
    print(f"[probe] deriving SA2 for {len(mm_sample)} mismatch samples...",
          flush=True)
    mm_derived = derive_sa2_for(mm_sample)
    by_id = {r["service_id"]: r for r in mm_sample}

    w("| service_id | name (truncated) | svc_state | postcode | "
      "old_sa2_code | old_sa2_state | new_sa2_code | new_sa2_state | "
      "fixes? |")
    w("|---:|---|---|---|---|---|---|---|---|")
    n_fixed = 0
    for _, r in mm_derived.iterrows():
        sid = int(r["service_id"]) if r["service_id"] is not None else None
        old = by_id.get(sid)
        new_code = r.get(SA2_CODE_ATTR)
        new_state = r.get(SA2_STATE_ATTR)
        new_code_s = (str(new_code)
                      if new_code is not None and pd.notna(new_code)
                      else "(no match)")
        new_state_s = (str(new_state)
                       if new_state is not None and pd.notna(new_state)
                       else "")
        # Compare new_state to svc_state (full -> abbrev)
        new_state_abbr = next(
            (k for k, v in SVC_STATE_TO_FULL.items()
             if v == new_state_s),
            new_state_s,
        )
        svc_state_old = old["svc_state"] if old is not None else ""
        is_fixed = (new_state_abbr == svc_state_old)
        if is_fixed:
            n_fixed += 1
        svc_name = old["service_name"] if old is not None else ""
        name_trunc = (svc_name or "")[:32]
        postcode = old["postcode"] if old is not None else ""
        old_sa2_code = old["old_sa2_code"] if old is not None else ""
        old_sa2_state = old["old_sa2_state"] if old is not None else ""
        w(f"| {sid} | {name_trunc} | {svc_state_old} | "
          f"{postcode} | {old_sa2_code} | "
          f"{old_sa2_state} | {new_code_s} | "
          f"{new_state_s} | {'✓' if is_fixed else '✗'} |")
    w("")
    w(f"**Fixes-state in sample: {n_fixed}/{len(mm_sample)}**")
    w("")

# ---------------------------------------------------------------------------
# 5. Sample currently-CORRECT rows: confirm polygon doesn't regress
# ---------------------------------------------------------------------------
w(f"## 5. Sample of {SAMPLE_OK} currently-correct rows (regression check)")
w("")
w("These are services whose `services.state` already matches the state "
  "of their assigned SA2. After polygon derivation the new `sa2_code` "
  "may or may not differ — but if it does differ, the new SA2 must "
  "still be in the same state. Any row where new_state != svc_state "
  "would mean the polygon math is breaking known-good data.")
w("")

ok_sample_sql = f"""
    SELECT s.service_id, s.service_name, s.state AS svc_state,
           s.suburb, s.postcode,
           CAST(s.lat AS REAL) AS lat,
           CAST(s.lng AS REAL) AS lng,
           s.sa2_code AS old_sa2_code,
           s.sa2_name AS old_sa2_name
      FROM services s
      JOIN sa2_cohort c ON s.sa2_code = c.sa2_code
     WHERE s.is_active = 1
       AND s.lat IS NOT NULL AND s.lng IS NOT NULL
       AND s.state IS NOT NULL
       AND s.state = CASE c.state_name
            {case_when}
            ELSE c.state_name END
     ORDER BY s.service_id
     LIMIT {SAMPLE_OK}
"""
ok_sample = cur.execute(ok_sample_sql).fetchall()
ok_by_id = {r["service_id"]: r for r in ok_sample}

if not ok_sample:
    w("(no currently-correct rows — implausible; investigate)")
else:
    print(f"[probe] deriving SA2 for {len(ok_sample)} OK samples...",
          flush=True)
    ok_derived = derive_sa2_for(ok_sample)
    w("| service_id | svc_state | old_sa2_code | new_sa2_code | "
      "new_sa2_state | same_code | same_state |")
    w("|---:|---|---|---|---|---|---|")
    n_same_code = 0
    n_same_state = 0
    for _, r in ok_derived.iterrows():
        sid = int(r["service_id"]) if r["service_id"] is not None else None
        old = ok_by_id.get(sid)
        new_code = r.get(SA2_CODE_ATTR)
        new_state = r.get(SA2_STATE_ATTR)
        new_code_s = (str(new_code)
                      if new_code is not None and pd.notna(new_code)
                      else "(no match)")
        new_state_s = (str(new_state)
                       if new_state is not None and pd.notna(new_state)
                       else "")
        old_sa2_code = old["old_sa2_code"] if old is not None else ""
        svc_state_old = old["svc_state"] if old is not None else ""
        same_code = (new_code_s == str(old_sa2_code))
        new_state_abbr = next(
            (k for k, v in SVC_STATE_TO_FULL.items() if v == new_state_s),
            new_state_s,
        )
        same_state = (new_state_abbr == svc_state_old)
        if same_code:
            n_same_code += 1
        if same_state:
            n_same_state += 1
        w(f"| {sid} | {svc_state_old} | {old_sa2_code} | "
          f"{new_code_s} | {new_state_s} | "
          f"{'✓' if same_code else '✗'} | "
          f"{'✓' if same_state else '✗'} |")
    w("")
    w(f"**Same-code in sample: {n_same_code}/{len(ok_sample)}** "
      f"(some-code-changes are EXPECTED — postcode-correct rows can "
      f"still be on the wrong side of an SA2 boundary inside the right state)")
    w(f"**Same-state in sample: {n_same_state}/{len(ok_sample)}** "
      f"(should be 100% — anything less is a regression risk)")
    w("")

# ---------------------------------------------------------------------------
# 6. Service 246 specifically (the symptom that started this)
# ---------------------------------------------------------------------------
w("## 6. Service 246 — the original symptom")
w("")
s246 = cur.execute("""
    SELECT s.service_id, s.service_name, s.state AS svc_state,
           s.suburb, s.postcode,
           CAST(s.lat AS REAL) AS lat,
           CAST(s.lng AS REAL) AS lng,
           s.sa2_code AS old_sa2_code,
           s.sa2_name AS old_sa2_name,
           c.state_name AS old_sa2_state
      FROM services s
      LEFT JOIN sa2_cohort c ON s.sa2_code = c.sa2_code
     WHERE s.service_id = 246
""").fetchone()
if s246 is None:
    w("(service_id 246 not found)")
else:
    w(f"- Service: **{s246['service_name']}** "
      f"({s246['suburb']}, {s246['svc_state']} {s246['postcode']})")
    w(f"- lat/lng: **{s246['lat']}, {s246['lng']}**")
    w(f"- Current sa2_code: **{s246['old_sa2_code']}** "
      f"(`{s246['old_sa2_name']}`, "
      f"sa2_cohort.state_name=`{s246['old_sa2_state']}`)")

    print("[probe] deriving SA2 for service 246...", flush=True)
    s246_derived = derive_sa2_for([s246])
    if not s246_derived.empty:
        r0 = s246_derived.iloc[0]
        new_code = r0.get(SA2_CODE_ATTR)
        new_name = r0.get(SA2_NAME_ATTR)
        new_state = r0.get(SA2_STATE_ATTR)
        if new_code is not None and pd.notna(new_code):
            w(f"- **New sa2_code (polygon-derived): "
              f"{new_code}** (`{new_name}`, state=`{new_state}`)")
        else:
            w("- New sa2_code: **(no match — investigate lat/lng)**")
    w("")

# ---------------------------------------------------------------------------
# 7. Apply preview
# ---------------------------------------------------------------------------
w("## 7. Apply preview (what Step 1c will do)")
w("")
w("- For each of the **~17,880 services with lat/lng**, derive sa2_code "
  "via point-in-polygon against the SA2 GeoPackage.")
w("- For matches, **UPDATE services SET sa2_code = ?, sa2_name = ?** "
  "(both, because sa2_name was also being shown wrongly).")
w("- Untouched: services without lat/lng (~340), polygon misses "
  "(expected: a handful of offshore points).")
w("- Pre-state captured into `audit_log.before_json`; post-state into "
  "`after_json`.")
w("- Apply-mode invariants:")
w("  - hit rate ≥ 99% on candidate set")
w("  - cross-state mismatches drop from current "
  f"{total_mm:,} to **< 50** "
  "(a handful expected from genuine boundary cases / NQAITS lat/lng "
  "errors)")
w("  - every assigned sa2_code present in `abs_sa2_erp_annual` "
  "(canonical-universe check, same as Step 1b)")
w("- Audit action: `sa2_polygon_overwrite_v1`. New backup file: "
  "`data/kintell.db.backup_pre_step1c_<ts>`.")
w("")

# ---------------------------------------------------------------------------
# Write
# ---------------------------------------------------------------------------
Path("recon").mkdir(exist_ok=True)
Path(OUT_PATH).write_text("\n".join(lines), encoding="utf-8")
conn.close()

print()
print(f"OK  wrote {OUT_PATH}")
print(f"    candidates (active with lat/lng): {n_with_latlng:,}")
print(f"    cross-state mismatches (current): {total_mm:,}")
print(f"    SA2 features: {sa2_features:,}")
print(f"    SA2 CRS: {sa2_gdf.crs}")
