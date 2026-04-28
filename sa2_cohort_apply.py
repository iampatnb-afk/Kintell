"""
sa2_cohort_apply.py  (v2 - spatial join)

Layer 3 prep step: build the sa2_cohort lookup table by spatially
joining SA2 centroids to ABS Remoteness Area polygons.

Sources:
  abs_data/ASGS_2021_Main_Structure_GDA2020.gpkg
    -> SA2_2021_AUST_GDA2020 (SA2 polygons + state attrs)
  abs_data/ASGS_Ed3_2021_RA_GDA2020.gpkg
    -> RA_2021_AUST_GDA2020 (54 RA polygons)

Approach (matches Step 1b pattern):
  1. Read both layers via geopandas
  2. Project to EPSG:3577 (GDA2020 Australian Albers, metric)
  3. Compute SA2 centroids
  4. sjoin SA2 centroids 'within' RA polygons
  5. Map RA_NAME -> ra_band (1=Major Cities .. 5=Very Remote)
  6. Validate against DB (coverage, services x-check)
  7. Apply: backup -> drop/create sa2_cohort -> insert -> audit_log

Output schema:
  sa2_cohort (
    sa2_code   TEXT PRIMARY KEY,
    sa2_name   TEXT,
    state_code TEXT,    -- '1'..'9' from SA2 polygon attrs
    state_name TEXT,
    ra_code    TEXT,    -- 2-digit ABS code (e.g., '10', '24')
    ra_name    TEXT,    -- e.g., 'Major Cities of Australia'
    ra_band    INTEGER  -- 1=Major Cities .. 5=Very Remote
  )

Standards:
  -  8 : timestamped backup before mutation
  - 28 : pre-mutation inventory taken separately (db_inventory.py)
  - 30 : hardcoded audit_log INSERT (no generic discovery)

Modes:
  --dry-run   compute, validate, write recon md. NO DB writes.
  --apply     full mutation pattern.

Usage:
  python sa2_cohort_apply.py --dry-run
  python sa2_cohort_apply.py --apply
"""
import argparse
import shutil
import sqlite3
import sys
import warnings
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

try:
    import geopandas as gpd
except ImportError:
    print("ERROR: geopandas not installed. Should already be present from Step 1b.")
    sys.exit(1)


REPO_ROOT = Path(__file__).resolve().parent
DB_PATH = REPO_ROOT / "data" / "kintell.db"
MAIN_GPKG = REPO_ROOT / "abs_data" / "ASGS_2021_Main_Structure_GDA2020.gpkg"
RA_GPKG = REPO_ROOT / "abs_data" / "ASGS_Ed3_2021_RA_GDA2020.gpkg"
SA2_LAYER = "SA2_2021_AUST_GDA2020"
RA_LAYER = "RA_2021_AUST_GDA2020"
DRYRUN_OUT = REPO_ROOT / "recon" / "layer3_prep_sa2_cohort_apply_dryrun.md"
APPLY_OUT = REPO_ROOT / "recon" / "layer3_prep_sa2_cohort_apply.md"


# Map RA name to band (1=most urban, 5=most remote).
# Universal across states.
RA_NAME_TO_BAND = {
    "Major Cities of Australia": 1,
    "Inner Regional Australia": 2,
    "Outer Regional Australia": 3,
    "Remote Australia": 4,
    "Very Remote Australia": 5,
}


def fmt_int(n):
    return f"{n:,}" if n is not None else "n/a"


# --------------------------------------------------------------------
# Phase 1: Spatial join
# --------------------------------------------------------------------

def compute_cohort():
    print("Loading SA2 polygons...", flush=True)
    sa2 = gpd.read_file(MAIN_GPKG, layer=SA2_LAYER)
    print(f"  {len(sa2):,} SA2 features, CRS={sa2.crs}")

    print("Loading RA polygons...", flush=True)
    ra = gpd.read_file(RA_GPKG, layer=RA_LAYER)
    print(f"  {len(ra):,} RA features, CRS={ra.crs}")

    # Reproject to EPSG:3577 (GDA2020 Australian Albers, metric) for
    # clean centroid computation. Both files are GDA2020 family so
    # the transform is exact.
    print("Reprojecting to EPSG:3577 for spatial work...", flush=True)
    sa2_p = sa2.to_crs(epsg=3577)
    ra_p = ra.to_crs(epsg=3577)

    print("Computing SA2 centroids...", flush=True)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sa2_centroids = sa2_p.copy()
        sa2_centroids["geometry"] = sa2_p.geometry.centroid

    print("Spatial join SA2 centroid -> RA polygon (within)...", flush=True)
    ra_keep = ra_p[["RA_CODE_2021", "RA_NAME_2021", "geometry"]]
    joined = gpd.sjoin(
        sa2_centroids[
            ["SA2_CODE_2021", "SA2_NAME_2021",
             "STATE_CODE_2021", "STATE_NAME_2021", "geometry"]
        ],
        ra_keep,
        predicate="within",
        how="left",
    )

    n_total = len(joined)
    n_unmatched = joined["RA_CODE_2021"].isna().sum()
    print(f"  joined rows: {n_total:,}")
    print(f"  unmatched (centroid outside any RA): {n_unmatched:,}")

    # Fallback for unmatched: spatial join with 'intersects' on the
    # original SA2 polygon to RA. Catches edge cases where a centroid
    # falls in a tiny gap (e.g., offshore islands).
    if n_unmatched > 0:
        print("Fallback: SA2 polygon-intersects-RA for unmatched...",
              flush=True)
        unmatched_codes = set(
            joined.loc[joined["RA_CODE_2021"].isna(), "SA2_CODE_2021"]
        )
        sa2_unmatched = sa2_p[
            sa2_p["SA2_CODE_2021"].isin(unmatched_codes)
        ][["SA2_CODE_2021", "geometry"]]
        if len(sa2_unmatched):
            fb = gpd.sjoin(
                sa2_unmatched,
                ra_keep,
                predicate="intersects",
                how="left",
            )
            # If multiple intersecting RAs, pick the one with largest
            # overlap area (correct for boundary SA2s)
            fb_resolved = {}
            for sa2_code, group in fb.groupby("SA2_CODE_2021"):
                if len(group) == 1:
                    fb_resolved[sa2_code] = (
                        group["RA_CODE_2021"].iloc[0],
                        group["RA_NAME_2021"].iloc[0],
                    )
                else:
                    # Largest-overlap-area resolution
                    sa2_geom = sa2_p.loc[
                        sa2_p["SA2_CODE_2021"] == sa2_code, "geometry"
                    ].iloc[0]
                    best_area = -1
                    best_pair = (None, None)
                    for _, r in group.iterrows():
                        ra_geom = ra_p.loc[
                            ra_p["RA_CODE_2021"] == r["RA_CODE_2021"],
                            "geometry"
                        ].iloc[0]
                        try:
                            inter_area = sa2_geom.intersection(ra_geom).area
                        except Exception:
                            inter_area = 0
                        if inter_area > best_area:
                            best_area = inter_area
                            best_pair = (r["RA_CODE_2021"],
                                         r["RA_NAME_2021"])
                    fb_resolved[sa2_code] = best_pair
            print(f"  fallback resolved: {len(fb_resolved):,}")
            # Apply fallback values into the joined frame
            for sa2_code, (rc, rn) in fb_resolved.items():
                mask = joined["SA2_CODE_2021"] == sa2_code
                joined.loc[mask, "RA_CODE_2021"] = rc
                joined.loc[mask, "RA_NAME_2021"] = rn
            n_unmatched_after = joined["RA_CODE_2021"].isna().sum()
            print(f"  still unmatched after fallback: "
                  f"{n_unmatched_after:,}")

    # Build cohort rows
    multi_match_sa2s = []
    seen = Counter(joined["SA2_CODE_2021"])
    for sa2_code, n in seen.items():
        if n > 1:
            multi_match_sa2s.append(sa2_code)

    deduped = joined.drop_duplicates(subset=["SA2_CODE_2021"], keep="first")

    cohort_rows = []
    for _, r in deduped.iterrows():
        ra_name = r["RA_NAME_2021"]
        ra_code = r["RA_CODE_2021"]
        ra_band = RA_NAME_TO_BAND.get(ra_name) if ra_name else None
        cohort_rows.append({
            "sa2_code": str(r["SA2_CODE_2021"]),
            "sa2_name": r["SA2_NAME_2021"],
            "state_code": str(r["STATE_CODE_2021"]),
            "state_name": r["STATE_NAME_2021"],
            "ra_code": str(ra_code) if ra_code is not None else None,
            "ra_name": ra_name,
            "ra_band": ra_band,
        })

    cohort_rows.sort(key=lambda x: x["sa2_code"])
    print(f"  cohort rows: {len(cohort_rows):,}")
    print(f"  SA2s with no RA assignment: "
          f"{sum(1 for r in cohort_rows if r['ra_name'] is None):,}")
    print(f"  SA2s flagged multi-match (pre-dedupe): "
          f"{len(multi_match_sa2s):,}")
    return cohort_rows, multi_match_sa2s


# --------------------------------------------------------------------
# Phase 2: Validate against DB
# --------------------------------------------------------------------

def validate_against_db(cohort_rows):
    print("Validating against DB...", flush=True)
    findings = {}

    uri = f"file:{DB_PATH.as_posix()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    cur = conn.cursor()

    cur.execute("SELECT DISTINCT sa2_code FROM abs_sa2_erp_annual")
    erp_sa2 = {r[0] for r in cur.fetchall()}
    cohort_sa2 = {r["sa2_code"] for r in cohort_rows}

    findings["erp_distinct_sa2"] = len(erp_sa2)
    findings["cohort_distinct_sa2"] = len(cohort_sa2)
    findings["coverage_overlap"] = len(erp_sa2 & cohort_sa2)
    findings["erp_not_in_cohort"] = sorted(erp_sa2 - cohort_sa2)
    findings["cohort_not_in_erp"] = sorted(cohort_sa2 - erp_sa2)

    findings["ra_distribution"] = dict(
        Counter(r["ra_name"] for r in cohort_rows).most_common())
    findings["state_distribution"] = dict(
        Counter(r["state_name"] for r in cohort_rows).most_common())
    findings["ra_band_distribution"] = dict(
        Counter(r["ra_band"] for r in cohort_rows).most_common())

    # services.aria_plus cross-check
    cur.execute("""
        SELECT sa2_code, aria_plus, COUNT(*) AS n
          FROM services
         WHERE sa2_code IS NOT NULL AND aria_plus IS NOT NULL
      GROUP BY sa2_code, aria_plus
    """)
    services_counts = defaultdict(Counter)
    for sa2, aria, n in cur.fetchall():
        services_counts[sa2][aria] += n
    services_modal = {
        sa2: c.most_common(1)[0][0] for sa2, c in services_counts.items()
    }
    cohort_lookup = {r["sa2_code"]: r["ra_name"] for r in cohort_rows}
    matches = 0
    mismatches = []
    for sa2, svc_aria in services_modal.items():
        coh_ra = cohort_lookup.get(sa2)
        if coh_ra is None:
            continue
        if svc_aria == coh_ra:
            matches += 1
        else:
            mismatches.append({
                "sa2_code": sa2,
                "services": svc_aria,
                "cohort": coh_ra,
            })
    findings["services_xcheck_compared"] = len(services_modal)
    findings["services_xcheck_matches"] = matches
    findings["services_xcheck_mismatches"] = mismatches

    conn.close()

    print(f"  ERP distinct SA2:        {findings['erp_distinct_sa2']:,}")
    print(f"  cohort distinct SA2:     {findings['cohort_distinct_sa2']:,}")
    print(f"  overlap:                 {findings['coverage_overlap']:,}")
    print(f"  ERP-not-in-cohort:       {len(findings['erp_not_in_cohort']):,}")
    print(f"  cohort-not-in-ERP:       {len(findings['cohort_not_in_erp']):,}")
    print(f"  services x-check pairs:  "
          f"{findings['services_xcheck_compared']:,}")
    print(f"  services x-check match:  "
          f"{findings['services_xcheck_matches']:,}")
    print(f"  services x-check miss:   {len(mismatches):,}")
    return findings


# --------------------------------------------------------------------
# Phase 3: Apply
# --------------------------------------------------------------------

def apply_cohort(cohort_rows):
    print("APPLY mode: backup -> transaction -> audit_log", flush=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = (REPO_ROOT / "data" /
                   f"kintell.db.backup_pre_sa2_cohort_{timestamp}")
    print(f"  backup -> {backup_path.name} ...")
    shutil.copy2(DB_PATH, backup_path)
    backup_size_mb = backup_path.stat().st_size / (1024 * 1024)
    print(f"  backup ok ({backup_size_mb:.1f} MB)")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("BEGIN")

        cur.execute("DROP TABLE IF EXISTS sa2_cohort")
        cur.execute("""
            CREATE TABLE sa2_cohort (
                sa2_code   TEXT NOT NULL PRIMARY KEY,
                sa2_name   TEXT,
                state_code TEXT,
                state_name TEXT,
                ra_code    TEXT,
                ra_name    TEXT,
                ra_band    INTEGER
            )
        """)
        cur.execute("CREATE INDEX idx_sa2_cohort_state "
                    "ON sa2_cohort(state_code)")
        cur.execute("CREATE INDEX idx_sa2_cohort_ra "
                    "ON sa2_cohort(ra_code)")
        cur.execute("CREATE INDEX idx_sa2_cohort_ra_band "
                    "ON sa2_cohort(ra_band)")

        cur.executemany("""
            INSERT INTO sa2_cohort
                (sa2_code, sa2_name, state_code, state_name,
                 ra_code, ra_name, ra_band)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [
            (r["sa2_code"], r["sa2_name"], r["state_code"],
             r["state_name"], r["ra_code"], r["ra_name"], r["ra_band"])
            for r in cohort_rows
        ])

        cur.execute("SELECT COUNT(*) FROM sa2_cohort")
        inserted = cur.fetchone()[0]
        if inserted != len(cohort_rows):
            raise RuntimeError(
                f"insert count mismatch: expected {len(cohort_rows)}, "
                f"got {inserted}")

        # Standard 30 - hardcoded 7-col audit_log INSERT
        cur.execute("""
            INSERT INTO audit_log
                (actor, action, subject_type, subject_id,
                 before_json, after_json, reason)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "sa2_cohort_apply",
            "sa2_cohort_build_v1",
            "sa2_cohort",
            0,
            '{"rows": 0}',
            f'{{"rows": {inserted}}}',
            ("Build sa2_cohort lookup via SA2 centroid -> RA polygon "
             "spatial join; sources ASGS_2021_Main_Structure_GDA2020.gpkg "
             "and ASGS_Ed3_2021_RA_GDA2020.gpkg; "
             f"{inserted} SA2s assigned"),
        ))
        cur.execute("SELECT last_insert_rowid()")
        audit_id = cur.fetchone()[0]

        conn.commit()
        print(f"  COMMIT ok. {inserted:,} rows. audit_id {audit_id}")
        return inserted, audit_id, backup_path
    except Exception as e:
        conn.rollback()
        print(f"  ROLLBACK on error: {e}")
        raise
    finally:
        conn.close()


# --------------------------------------------------------------------
# Markdown emit
# --------------------------------------------------------------------

def emit_markdown(out_path, mode, cohort_rows, multi_match,
                  validation, apply_result=None):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out = []
    w = out.append

    w(f"# SA2 Cohort Apply (Layer 3 prep) - {mode.upper()}")
    w("")
    w(f"_Generated: {datetime.now().isoformat(timespec='seconds')}_")
    w("")
    w("Method: spatial join SA2 centroid -> RA polygon (EPSG:3577 metric).")
    w("Sources:")
    w("- `abs_data/ASGS_2021_Main_Structure_GDA2020.gpkg` (SA2 polygons)")
    w("- `abs_data/ASGS_Ed3_2021_RA_GDA2020.gpkg` (RA polygons)")
    w("")
    w(f"Total cohort rows: {len(cohort_rows):,}")
    w("")

    if apply_result:
        rows_inserted, audit_id, backup = apply_result
        w("## Apply outcome")
        w("")
        w(f"- Rows inserted: **{rows_inserted:,}**")
        w(f"- audit_id: **{audit_id}**")
        w(f"- Backup: `data/{backup.name}`")
        w("")

    w("## State distribution")
    w("")
    w("| State | SA2 count |")
    w("|---|---:|")
    for state, n in sorted(validation["state_distribution"].items(),
                           key=lambda x: -x[1]):
        w(f"| {state} | {fmt_int(n)} |")
    w("")

    w("## Remoteness distribution")
    w("")
    w("| RA name | SA2 count |")
    w("|---|---:|")
    for ra, n in sorted(validation["ra_distribution"].items(),
                        key=lambda x: -(x[1] or 0)):
        w(f"| {ra or '_(null)_'} | {fmt_int(n)} |")
    w("")

    w("## RA band distribution (1=Major Cities .. 5=Very Remote)")
    w("")
    w("| Band | SA2 count |")
    w("|---:|---:|")
    for band, n in sorted(validation["ra_band_distribution"].items(),
                          key=lambda x: (x[0] is None, x[0])):
        b = band if band is not None else "_(null)_"
        w(f"| {b} | {fmt_int(n)} |")
    w("")

    w("## Coverage check vs `abs_sa2_erp_annual`")
    w("")
    w(f"- ERP distinct SA2:    {fmt_int(validation['erp_distinct_sa2'])}")
    w(f"- Cohort distinct SA2: {fmt_int(validation['cohort_distinct_sa2'])}")
    w(f"- Overlap:             {fmt_int(validation['coverage_overlap'])}")
    w(f"- ERP not in cohort:   "
      f"{fmt_int(len(validation['erp_not_in_cohort']))}")
    w(f"- Cohort not in ERP:   "
      f"{fmt_int(len(validation['cohort_not_in_erp']))}")
    w("")
    if validation['erp_not_in_cohort']:
        w("**ERP-only SA2s (would lack cohort, max 20):**")
        w("")
        for s in validation['erp_not_in_cohort'][:20]:
            w(f"- `{s}`")
        if len(validation['erp_not_in_cohort']) > 20:
            w(f"_+{len(validation['erp_not_in_cohort'])-20} more_")
        w("")
    if validation['cohort_not_in_erp']:
        w("**Cohort-only SA2s (likely synthetic / no usual address, max 20):**")
        w("")
        for s in validation['cohort_not_in_erp'][:20]:
            w(f"- `{s}`")
        if len(validation['cohort_not_in_erp']) > 20:
            w(f"_+{len(validation['cohort_not_in_erp'])-20} more_")
        w("")

    w("## Cross-check vs `services.aria_plus`")
    w("")
    compared = validation['services_xcheck_compared']
    matches = validation['services_xcheck_matches']
    miss_count = len(validation['services_xcheck_mismatches'])
    pct = (matches * 100.0 / compared) if compared else 0
    w(f"- Pairs compared:  {fmt_int(compared)}")
    w(f"- Matches:         {fmt_int(matches)} ({pct:.2f}%)")
    w(f"- Mismatches:      {fmt_int(miss_count)}")
    w("")
    if validation['services_xcheck_mismatches']:
        w("**Sample mismatches (first 30):**")
        w("")
        w("| sa2_code | services.aria_plus | cohort.ra_name |")
        w("|---|---|---|")
        for m in validation['services_xcheck_mismatches'][:30]:
            w(f"| `{m['sa2_code']}` | {m['services']} | {m['cohort']} |")
        w("")

    if multi_match:
        w("## Multi-match SA2s (pre-dedupe)")
        w("")
        w(f"_{len(multi_match)} SA2s had >1 RA match before dedupe. "
          "Resolved by largest-area overlap or first-match. First 20:_")
        w("")
        for s in multi_match[:20]:
            w(f"- `{s}`")
        w("")

    w("## Sample cohort rows (first 10)")
    w("")
    w("| sa2_code | sa2_name | state | ra_name | ra_band |")
    w("|---|---|---|---|---:|")
    for r in cohort_rows[:10]:
        w(f"| `{r['sa2_code']}` | {r['sa2_name']} | {r['state_name']} | "
          f"{r['ra_name']} | {r['ra_band']} |")
    w("")

    out_path.write_text("\n".join(out), encoding="utf-8")
    size = out_path.stat().st_size
    print(f"Wrote {out_path.relative_to(REPO_ROOT)} ({size:,} bytes)")


# --------------------------------------------------------------------
# Main
# --------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if not DB_PATH.exists():
        print(f"ERROR: DB not found at {DB_PATH}")
        return 1
    if not MAIN_GPKG.exists():
        print(f"ERROR: Main GeoPackage not found: {MAIN_GPKG}")
        return 1
    if not RA_GPKG.exists():
        print(f"ERROR: RA GeoPackage not found: {RA_GPKG}")
        return 1

    mode_label = "APPLY" if args.apply else "DRY-RUN"
    print(f"sa2_cohort_apply v2 (spatial) - {mode_label}")
    print(f"Repo: {REPO_ROOT}")
    print(f"DB:   {DB_PATH}")
    print()

    cohort_rows, multi_match = compute_cohort()
    validation = validate_against_db(cohort_rows)

    if args.dry_run:
        emit_markdown(DRYRUN_OUT, "dry-run", cohort_rows, multi_match,
                      validation, apply_result=None)
        print()
        print("DRY-RUN complete. No DB changes.")
        print(f"Review: {DRYRUN_OUT.relative_to(REPO_ROOT)}")
        return 0

    if args.apply:
        if validation["cohort_distinct_sa2"] < 2400:
            print(f"ABORT: cohort distinct SA2 = "
                  f"{validation['cohort_distinct_sa2']} < 2400 (sanity floor)")
            return 1
        if len(validation["erp_not_in_cohort"]) > 50:
            print(f"ABORT: ERP-not-in-cohort = "
                  f"{len(validation['erp_not_in_cohort'])} > 50")
            return 1

        result = apply_cohort(cohort_rows)
        emit_markdown(APPLY_OUT, "apply", cohort_rows, multi_match,
                      validation, apply_result=result)
        print()
        print("APPLY complete.")
        print(f"Review: {APPLY_OUT.relative_to(REPO_ROOT)}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
