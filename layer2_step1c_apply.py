"""
layer2_step1c_apply.py — SA2 polygon OVERWRITE rebuild.

Step 1 (postcode concordance) was 1:1 and arbitrary for postcodes
spanning multiple SA2s. Step 1b (NULL-fill polygon backfill) only
touched the 887 NULL rows. The remaining 17,000+ services kept
their potentially-wrong postcode-derived sa2_code. The cross-state-
mismatch probe (2026-04-28) found ~1,435 services where services.state
disagrees with their currently-assigned SA2's state — proving the
problem is systemic, not edge-case.

Step 1c is the OVERWRITE rebuild:
  - All active services with lat/lng (~17,880) are re-derived via
    point-in-polygon, regardless of current sa2_code value.
  - Updates write BOTH sa2_code AND sa2_name (sa2_name was also
    being shown wrongly on the centre page).
  - Services without lat/lng (~340) are untouched.

Modes:
  (default)   compute proposed updates; write dry-run report; NO DB mutation.
  --apply     same compute + DB mutation inside transaction with invariants.

Inputs:
  data/kintell.db
  abs_data/ASGS_2021_Main_Structure_GDA2020.gpkg  (layer SA2_2021_AUST_GDA2020)

Outputs:
  recon/layer2_step1c_apply_dryrun.md   (dry-run only)
  recon/layer2_step1c_apply.md          (apply only)
  data/kintell.db.backup_pre_step1c_<ts>  (apply only)
  audit_log row, action='sa2_polygon_overwrite_v1'   (apply only)

Invariants (apply mode; ROLLBACK on violation):
  hit_rate >= 0.99
  every assigned sa2_code present in abs_sa2_erp_annual.sa2_code
  cross-state mismatches drop to < 50 (down from ~1,435)

audit_log schema:
  audit_id INTEGER PK, actor TEXT NN, action TEXT NN,
  subject_type TEXT NN, subject_id INTEGER NN,
  before_json TEXT, after_json TEXT, reason TEXT,
  occurred_at TEXT default datetime('now')

Pattern inherited from layer2_step1b_apply.py (preflight, sjoin within,
backup, transactional apply, audit_log).
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = "data/kintell.db"
GPKG_PATH = "abs_data/ASGS_2021_Main_Structure_GDA2020.gpkg"
SA2_LAYER = "SA2_2021_AUST_GDA2020"
HIT_RATE_THRESHOLD = 0.99
CROSS_STATE_RESIDUAL_MAX = 50  # post-overwrite cross-state mismatch cap
AUDIT_ACTION = "sa2_polygon_overwrite_v1"
ACTOR = "layer2_step1c_apply"
DRYRUN_REPORT = "recon/layer2_step1c_apply_dryrun.md"
APPLY_REPORT = "recon/layer2_step1c_apply.md"

SA2_CODE_ATTR = "SA2_CODE_2021"
SA2_NAME_ATTR = "SA2_NAME_2021"
SA2_STATE_ATTR = "STATE_NAME_2021"

# Map services.state (2-3 letter) -> sa2_cohort.state_name (full).
# Used for cross-state mismatch counts (pre and post).
SVC_STATE_TO_FULL = {
    "NSW": "New South Wales",
    "VIC": "Victoria",
    "QLD": "Queensland",
    "SA":  "South Australia",
    "WA":  "Western Australia",
    "TAS": "Tasmania",
    "NT":  "Northern Territory",
    "ACT": "Australian Capital Territory",
}


# ---------------------------------------------------------------------------
# Preflight
# ---------------------------------------------------------------------------
def preflight() -> None:
    for p in (DB_PATH, GPKG_PATH):
        if not Path(p).exists():
            print(f"ERROR: not found: {p}", file=sys.stderr)
            sys.exit(1)


def import_geo():
    try:
        import geopandas as gpd
        import pandas as pd
        from shapely.geometry import Point
        return gpd, pd, Point
    except ImportError as e:
        print(f"ERROR: required package missing ({e})", file=sys.stderr)
        print("Run: pip install --break-system-packages geopandas shapely "
              "pyogrio rtree", file=sys.stderr)
        sys.exit(2)


def to_native(v):
    if v is None:
        return None
    if hasattr(v, "item"):
        return v.item()
    return v


# ---------------------------------------------------------------------------
# Cross-state mismatch counter — used pre and post to verify invariant.
# Operates on a connection (so post-update count uses uncommitted state).
# ---------------------------------------------------------------------------
def count_cross_state_mismatches(conn) -> int:
    case_when = " ".join(
        f"WHEN '{full}' THEN '{abbr}'"
        for abbr, full in SVC_STATE_TO_FULL.items()
    )
    sql = f"""
        SELECT COUNT(*)
          FROM services s
          JOIN sa2_cohort c ON s.sa2_code = c.sa2_code
         WHERE s.is_active = 1
           AND s.lat IS NOT NULL AND s.lng IS NOT NULL
           AND s.state IS NOT NULL
           AND s.state != CASE c.state_name
                {case_when}
                ELSE c.state_name END
    """
    return conn.execute(sql).fetchone()[0]


# ---------------------------------------------------------------------------
# Build audit_log INSERT
# ---------------------------------------------------------------------------
def build_audit_insert(pre_state: dict, post_state: dict, sa2_features: int):
    before = {
        "rows": pre_state["n_total_active"],
        "payload": {
            "active_services":     pre_state["n_total_active"],
            "with_latlng":         pre_state["n_candidates"],
            "without_latlng":      pre_state["n_no_latlng"],
            "with_sa2_code":       pre_state["n_with_sa2_pre"],
            "cross_state_mismatches": pre_state["cross_state_mm_pre"],
        },
    }
    after = {
        "rows": pre_state["n_total_active"],
        "payload": {
            "candidates_attempted": pre_state["n_candidates"],
            "assigned":             post_state["n_assigned"],
            "missed":               post_state["n_missed"],
            "hit_rate":             round(post_state["hit_rate"], 6),
            "rows_changed_sa2":     post_state["n_rows_changed"],
            "rows_unchanged_sa2":   post_state["n_rows_unchanged"],
            "cross_state_mismatches_post": post_state["cross_state_mm_post"],
            "method":               "sjoin within (EPSG:4326 -> EPSG:7844)",
            "source_gpkg":          GPKG_PATH,
            "source_layer":         SA2_LAYER,
            "sa2_features":         sa2_features,
        },
    }
    reason = (
        f"Layer 2 Step 1c: SA2 polygon OVERWRITE rebuild. "
        f"Re-derived sa2_code for {pre_state['n_candidates']:,} active "
        f"services with lat/lng. "
        f"Hit rate {post_state['hit_rate']:.2%} "
        f"({post_state['n_assigned']}/{pre_state['n_candidates']}). "
        f"Rows where sa2_code changed: {post_state['n_rows_changed']:,}. "
        f"Cross-state mismatches: "
        f"{pre_state['cross_state_mm_pre']:,} -> "
        f"{post_state['cross_state_mm_post']:,}. "
        f"Source: {GPKG_PATH} layer {SA2_LAYER}."
    )
    sql = (
        "INSERT INTO audit_log "
        "(actor, action, subject_type, subject_id, "
        " before_json, after_json, reason) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)"
    )
    params = [
        ACTOR,
        AUDIT_ACTION,
        "services",
        0,
        json.dumps(before, sort_keys=True),
        json.dumps(after, sort_keys=True),
        reason,
    ]
    return sql, params


# ---------------------------------------------------------------------------
# Compute proposed updates (does NOT mutate)
# ---------------------------------------------------------------------------
def compute_updates(conn, gpd, pd, Point):
    cur = conn.cursor()

    # Pre-state counts
    n_total_active = cur.execute(
        "SELECT COUNT(*) FROM services WHERE is_active = 1"
    ).fetchone()[0]
    n_with_latlng = cur.execute(
        "SELECT COUNT(*) FROM services "
        " WHERE is_active = 1 "
        "   AND lat IS NOT NULL AND lng IS NOT NULL"
    ).fetchone()[0]
    n_no_latlng = n_total_active - n_with_latlng
    n_with_sa2_pre = cur.execute(
        "SELECT COUNT(*) FROM services "
        " WHERE is_active = 1 AND sa2_code IS NOT NULL"
    ).fetchone()[0]
    cross_state_mm_pre = count_cross_state_mismatches(conn)

    print(f"Pre-state: active={n_total_active:,}  "
          f"with_latlng={n_with_latlng:,}  "
          f"with_sa2={n_with_sa2_pre:,}  "
          f"cross_state_mm={cross_state_mm_pre:,}")

    # Candidate set: every active service with lat/lng (overwrite mode)
    candidates_df = pd.read_sql_query(
        "SELECT service_id, "
        "       CAST(lat AS REAL) AS lat, "
        "       CAST(lng AS REAL) AS lng, "
        "       state, "
        "       sa2_code AS old_sa2_code, "
        "       sa2_name AS old_sa2_name "
        "  FROM services "
        " WHERE is_active = 1 "
        "   AND lat IS NOT NULL AND lng IS NOT NULL",
        conn,
    )
    n_candidates = len(candidates_df)
    print(f"Loaded {n_candidates:,} candidate services")

    # Load SA2 polygons
    print(f"Reading SA2 layer '{SA2_LAYER}' from {GPKG_PATH} (~30-60s) ...")
    sa2_full = gpd.read_file(GPKG_PATH, layer=SA2_LAYER, engine="pyogrio")
    sa2_gdf = sa2_full[
        [SA2_CODE_ATTR, SA2_NAME_ATTR, SA2_STATE_ATTR, "geometry"]
    ].copy()
    sa2_features = len(sa2_gdf)
    print(f"Loaded {sa2_features:,} SA2 polygons "
          f"(CRS: "
          f"{sa2_gdf.crs.to_authority() if sa2_gdf.crs else '?'})")

    # Build points and reproject
    points_gdf = gpd.GeoDataFrame(
        candidates_df,
        geometry=[Point(lon, lat) for lon, lat in
                  zip(candidates_df["lng"], candidates_df["lat"])],
        crs="EPSG:4326",
    )
    points_proj = points_gdf.to_crs(sa2_gdf.crs)

    print("Performing point-in-polygon (sjoin within) ...")
    joined = gpd.sjoin(points_proj, sa2_gdf,
                       how="left", predicate="within")
    joined = joined.drop_duplicates(subset="service_id", keep="first")

    has_match = joined[SA2_CODE_ATTR].notna()
    n_assigned = int(has_match.sum())
    n_missed = int((~has_match).sum())
    hit_rate = (n_assigned / n_candidates) if n_candidates else 0.0
    print(f"Hit rate: {n_assigned}/{n_candidates} ({hit_rate:.2%})")

    # Canonical-universe check: assigned codes must all exist in
    # abs_sa2_erp_annual (so Layer 3 reads will have data).
    assigned_codes = set(
        joined.loc[has_match, SA2_CODE_ATTR].astype(str).tolist()
    )
    canonical_codes = set(
        str(r[0]) for r in cur.execute(
            "SELECT DISTINCT sa2_code FROM abs_sa2_erp_annual "
            " WHERE sa2_code IS NOT NULL"
        ).fetchall()
    )
    orphans = assigned_codes - canonical_codes
    print(f"Canonical-universe orphans: {len(orphans):,}")

    # Diff vs current state: how many rows would have sa2_code change?
    joined_assigned = joined[has_match].copy()
    joined_assigned["new_sa2_code"] = (
        joined_assigned[SA2_CODE_ATTR].astype(str)
    )
    joined_assigned["old_sa2_code_str"] = (
        joined_assigned["old_sa2_code"].astype(str)
        .where(joined_assigned["old_sa2_code"].notna(), other="")
    )
    n_rows_changed = int(
        (joined_assigned["new_sa2_code"]
         != joined_assigned["old_sa2_code_str"]).sum()
    )
    n_rows_unchanged = n_assigned - n_rows_changed
    print(f"Rows where sa2_code changes: {n_rows_changed:,} "
          f"(unchanged: {n_rows_unchanged:,})")

    # Invariant violations (gating apply)
    violations: list[str] = []
    if hit_rate < HIT_RATE_THRESHOLD:
        violations.append(
            f"hit_rate {hit_rate:.2%} < {HIT_RATE_THRESHOLD:.0%}"
        )
    if orphans:
        violations.append(
            f"{len(orphans)} sa2_codes outside abs_sa2_erp_annual"
        )

    pre_state = {
        "n_total_active":     n_total_active,
        "n_candidates":       n_candidates,
        "n_no_latlng":        n_no_latlng,
        "n_with_sa2_pre":     n_with_sa2_pre,
        "cross_state_mm_pre": cross_state_mm_pre,
        "n_assigned":         n_assigned,
        "n_missed":           n_missed,
        "hit_rate":           hit_rate,
        "n_rows_changed":     n_rows_changed,
        "n_rows_unchanged":   n_rows_unchanged,
        "sa2_features":       sa2_features,
        "orphans":            sorted(orphans),
        "violations":         violations,
    }
    return joined, has_match, pre_state


# ---------------------------------------------------------------------------
# Backup
# ---------------------------------------------------------------------------
def take_backup(backup_path: str) -> None:
    src = sqlite3.connect(DB_PATH)
    dst = sqlite3.connect(backup_path)
    try:
        src.backup(dst)
    finally:
        dst.close()
        src.close()


# ---------------------------------------------------------------------------
# Markdown report
# ---------------------------------------------------------------------------
def write_report(out_path: str, mode: str, joined, has_match,
                 pre_state: dict, post_state: dict | None,
                 backup_path: str | None, audit_id: int | None,
                 audit_sql: str, audit_params: list,
                 pd) -> None:
    lines: list[str] = []

    def w(s: str = "") -> None:
        lines.append(s)

    title = ("Layer 2 Step 1c — Apply Report"
             if mode == "apply"
             else "Layer 2 Step 1c — Dry-Run Report")
    w(f"# {title}")
    w("")
    w(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    w(f"Mode: **{mode.upper()}**")
    w("")
    if mode == "apply" and backup_path:
        w(f"Backup: `{backup_path}`")
        w(f"audit_id: **{audit_id}**")
        w("")

    w("## Pre-state (services table)")
    w("")
    w(f"- Active services: **{pre_state['n_total_active']:,}**")
    w(f"- With lat/lng: **{pre_state['n_candidates']:,}** "
      f"(candidate set)")
    w(f"- Without lat/lng (untouched): **{pre_state['n_no_latlng']:,}**")
    w(f"- With sa2_code populated: "
      f"**{pre_state['n_with_sa2_pre']:,}**")
    w(f"- Cross-state mismatches (services.state vs sa2_cohort.state_name): "
      f"**{pre_state['cross_state_mm_pre']:,}**")
    w("")

    w("## Polygon derivation")
    w("")
    w(f"- SA2 features: **{pre_state['sa2_features']:,}**")
    w(f"- Assigned: **{pre_state['n_assigned']:,}**")
    w(f"- Missed: **{pre_state['n_missed']:,}** "
      "(offshore points / null-island)")
    w(f"- Hit rate: **{pre_state['hit_rate']:.2%}** "
      f"(threshold: {HIT_RATE_THRESHOLD:.0%})")
    w("")
    w(f"- Rows where sa2_code CHANGES: "
      f"**{pre_state['n_rows_changed']:,}**")
    w(f"- Rows where sa2_code unchanged: "
      f"**{pre_state['n_rows_unchanged']:,}**")
    w("")
    if pre_state["orphans"]:
        w(f"⚠ **{len(pre_state['orphans'])} orphan sa2_codes** "
          "(not in abs_sa2_erp_annual):")
        for s in pre_state["orphans"][:20]:
            w(f"- `{s}`")
        if len(pre_state["orphans"]) > 20:
            w(f"_+{len(pre_state['orphans']) - 20} more_")
        w("")

    if pre_state["violations"]:
        w("## ⚠ Invariant violations (apply would be refused)")
        w("")
        for v in pre_state["violations"]:
            w(f"- {v}")
        w("")
    else:
        w("✓ All pre-apply invariants pass.")
        w("")

    if post_state is not None:
        w("## Post-state (after COMMIT)")
        w("")
        w(f"- Cross-state mismatches: "
          f"**{post_state['cross_state_mm_post']:,}** "
          f"(was {pre_state['cross_state_mm_pre']:,}, "
          f"cap is < {CROSS_STATE_RESIDUAL_MAX})")
        delta = (pre_state['cross_state_mm_pre']
                 - post_state['cross_state_mm_post'])
        w(f"- Net cross-state corrections: **{delta:,}**")
        w("")

    # Misses sample
    misses = joined[~has_match]
    if len(misses):
        w(f"## Misses ({len(misses):,} services with no SA2 match)")
        w("")
        w("Typically offshore points (Norfolk Island, Christmas Island, "
          "Cocos), or services with bad lat/lng. Their existing sa2_code "
          "is left unchanged.")
        w("")
        sample = misses.head(20)
        w("| service_id | lat | lng | state |")
        w("|---:|---:|---:|---|")
        for _, r in sample.iterrows():
            sid = int(r["service_id"]) if r["service_id"] is not None else ""
            state_v = r.get("state") or ""
            w(f"| {sid} | {r['lat']} | {r['lng']} | {state_v} |")
        if len(misses) > 20:
            w(f"_+{len(misses) - 20} more_")
        w("")

    # Sample of changed rows (most useful — these are the corrections)
    assigned = joined[has_match].copy()
    if len(assigned):
        assigned["new_sa2_code"] = (
            assigned[SA2_CODE_ATTR].astype(str)
        )
        assigned["old_sa2_code_str"] = (
            assigned["old_sa2_code"].astype(str)
            .where(assigned["old_sa2_code"].notna(), other="")
        )
        changed = assigned[
            assigned["new_sa2_code"] != assigned["old_sa2_code_str"]
        ]
        if len(changed):
            w(f"## Sample of changed rows (first 30 of "
              f"{len(changed):,})")
            w("")
            w("| service_id | state | old_sa2_code | old_sa2_name | "
              "new_sa2_code | new_sa2_name | new_sa2_state |")
            w("|---:|---|---|---|---|---|---|")
            for _, r in changed.sort_values("service_id").head(30).iterrows():
                sid = (int(r["service_id"])
                       if r["service_id"] is not None else "")
                state_v = r.get("state") or ""
                old_code = r.get("old_sa2_code") or ""
                old_name = r.get("old_sa2_name") or ""
                w(f"| {sid} | {state_v} | {old_code} | {old_name} "
                  f"| {r[SA2_CODE_ATTR]} | {r[SA2_NAME_ATTR]} "
                  f"| {r[SA2_STATE_ATTR]} |")
            w("")

    # Top 20 SA2s by service count post-apply
    if pre_state["n_assigned"] > 0:
        top = (assigned.groupby([SA2_CODE_ATTR, SA2_NAME_ATTR])
               .size().reset_index(name="services")
               .sort_values("services", ascending=False).head(20))
        w("## Top 20 SA2s by service count (post-apply)")
        w("")
        w("| sa2_code | sa2_name | services |")
        w("|---|---|---:|")
        for _, row in top.iterrows():
            w(f"| {row[SA2_CODE_ATTR]} | {row[SA2_NAME_ATTR]} "
              f"| {row['services']:,} |")
        w("")

    w("## Audit log")
    w("")
    if mode == "dry-run":
        w(f"Would insert: action=`{AUDIT_ACTION}`, actor=`{ACTOR}`, "
          f"subject_type=`services`")
        w("")
        w("Simulated INSERT:")
        w("")
        w("```sql")
        w(audit_sql)
        w("```")
        w("")
        w("Params:")
        w("")
        w("```")
        for i, p in enumerate(audit_params):
            display = str(p)
            if len(display) > 400:
                display = display[:397] + "..."
            w(f"  [{i}] {display}")
        w("```")
    else:
        w(f"Inserted: action=`{AUDIT_ACTION}`, "
          f"audit_id=**{audit_id}**")
    w("")

    w("---")
    w("End of report.")
    w("")

    Path("recon").mkdir(exist_ok=True)
    Path(out_path).write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="Mutate DB. Default is dry-run.")
    ap.add_argument("--dry-run", action="store_true",
                    help="(default) Compute only; no DB mutation.")
    args = ap.parse_args()
    apply_mode = bool(args.apply)
    mode = "apply" if apply_mode else "dry-run"

    preflight()
    gpd, pd, Point = import_geo()

    # Read-only conn for compute
    try:
        conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    except sqlite3.Error:
        conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    print(f"Mode: {mode.upper()}")
    print()

    joined, has_match, pre_state = compute_updates(conn, gpd, pd, Point)
    audit_sql, audit_params = build_audit_insert(
        pre_state,
        # Placeholder post-state; rewritten after apply commits
        {
            "n_assigned":          pre_state["n_assigned"],
            "n_missed":            pre_state["n_missed"],
            "hit_rate":            pre_state["hit_rate"],
            "n_rows_changed":      pre_state["n_rows_changed"],
            "n_rows_unchanged":    pre_state["n_rows_unchanged"],
            "cross_state_mm_post": -1,  # filled in apply branch only
        },
        pre_state["sa2_features"],
    )
    conn.close()

    # ----- DRY RUN -----
    if not apply_mode:
        write_report(DRYRUN_REPORT, "dry-run",
                     joined, has_match, pre_state,
                     None, None, None,
                     audit_sql, audit_params, pd)
        print()
        print(f"DRY-RUN OK  wrote {DRYRUN_REPORT}")
        if pre_state["violations"]:
            print("⚠ Invariant violations present — apply would be refused:")
            for v in pre_state["violations"]:
                print(f"  - {v}")
        else:
            print("✓ All pre-apply invariants pass. To execute:")
            print("    python layer2_step1c_apply.py --apply")
        return 0

    # ----- APPLY -----
    if pre_state["violations"]:
        print("\n✗ INVARIANT VIOLATIONS — refusing to apply:",
              file=sys.stderr)
        for v in pre_state["violations"]:
            print(f"  - {v}", file=sys.stderr)
        return 2

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"data/kintell.db.backup_pre_step1c_{ts}"
    print(f"\nTaking backup: {backup_path}")
    take_backup(backup_path)
    backup_size_mb = os.path.getsize(backup_path) / (1024 * 1024)
    print(f"  backup size: {backup_size_mb:,.1f} MB")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    audit_id = None
    post_state: dict | None = None
    try:
        cur.execute("BEGIN")

        assigned = joined[has_match]
        update_pairs = [
            (str(row[SA2_CODE_ATTR]),
             str(row[SA2_NAME_ATTR]),
             to_native(row["service_id"]))
            for _, row in assigned.iterrows()
        ]

        # OVERWRITE — set BOTH sa2_code and sa2_name.
        cur.executemany(
            "UPDATE services SET sa2_code = ?, sa2_name = ? "
            " WHERE service_id = ?",
            update_pairs,
        )
        n_updated = cur.rowcount
        print(f"  UPDATEd {len(update_pairs):,} rows "
              f"(cursor rowcount={n_updated})")

        # Canonical-universe invariant
        bad = cur.execute(
            "SELECT COUNT(*) FROM services s "
            " WHERE s.sa2_code IS NOT NULL "
            "   AND s.sa2_code NOT IN "
            "       (SELECT sa2_code FROM abs_sa2_erp_annual "
            "         WHERE sa2_code IS NOT NULL)"
        ).fetchone()[0]
        if bad > 0:
            raise RuntimeError(
                f"{bad} services have sa2_code outside canonical universe"
            )
        print(f"  canonical-universe check: OK ({bad} orphans)")

        # Cross-state invariant
        cross_state_mm_post = count_cross_state_mismatches(conn)
        if cross_state_mm_post >= CROSS_STATE_RESIDUAL_MAX:
            raise RuntimeError(
                f"cross-state mismatches post-update "
                f"({cross_state_mm_post}) >= cap "
                f"({CROSS_STATE_RESIDUAL_MAX})"
            )
        print(f"  cross-state mismatches post: {cross_state_mm_post} "
              f"(was {pre_state['cross_state_mm_pre']}, "
              f"cap < {CROSS_STATE_RESIDUAL_MAX})")

        post_state = {
            "n_assigned":          pre_state["n_assigned"],
            "n_missed":            pre_state["n_missed"],
            "hit_rate":            pre_state["hit_rate"],
            "n_rows_changed":      pre_state["n_rows_changed"],
            "n_rows_unchanged":    pre_state["n_rows_unchanged"],
            "cross_state_mm_post": cross_state_mm_post,
        }
        # Rebuild audit with real post-state
        audit_sql, audit_params = build_audit_insert(
            pre_state, post_state, pre_state["sa2_features"]
        )
        cur.execute(audit_sql, audit_params)
        audit_id = cur.lastrowid
        print(f"  audit_log row inserted: audit_id={audit_id}")

        cur.execute("COMMIT")
        print("✓ COMMITTED")
    except Exception as e:
        try:
            cur.execute("ROLLBACK")
        except sqlite3.Error:
            pass
        print(f"\n✗ ROLLED BACK: {e}", file=sys.stderr)
        conn.close()
        return 3
    finally:
        try:
            conn.close()
        except Exception:
            pass

    write_report(APPLY_REPORT, "apply",
                 joined, has_match, pre_state, post_state,
                 backup_path, audit_id, audit_sql, audit_params, pd)
    print()
    print(f"APPLY OK  wrote {APPLY_REPORT}")
    print(f"          backup: {backup_path}")
    print(f"          audit_id: {audit_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
