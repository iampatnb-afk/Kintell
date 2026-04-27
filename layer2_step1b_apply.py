"""
layer2_step1b_apply.py (v2) — SA2 polygon point-in-polygon backfill.

Modes:
  (default)   compute proposed updates; write dry-run report; NO DB mutation.
  --apply     same compute + DB mutation inside transaction with invariants.

Inputs:
  data/kintell.db
  abs_data/ASGS_2021_Main_Structure_GDA2020.gpkg  (layer SA2_2021_AUST_GDA2020)

Outputs:
  recon/layer2_step1b_apply_dryrun.md   (dry-run only)
  recon/layer2_step1b_apply.md          (apply only)
  data/kintell.db.backup_pre_step1b_<ts>  (apply only)
  audit_log row, action='sa2_polygon_backfill_v1'   (apply only)

Invariants (apply mode; ROLLBACK on violation):
  hit_rate >= 0.99
  every assigned sa2_code present in abs_sa2_erp_annual.sa2_code
  post-update NULL sa2_code count matches expected

audit_log schema (kintell.db):
  audit_id INTEGER PK, actor TEXT NN, action TEXT NN,
  subject_type TEXT NN, subject_id INTEGER NN,
  before_json TEXT, after_json TEXT, reason TEXT,
  occurred_at TEXT default datetime('now')
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
AUDIT_ACTION = "sa2_polygon_backfill_v1"
ACTOR = "layer2_step1b_apply"
DRYRUN_REPORT = "recon/layer2_step1b_apply_dryrun.md"
APPLY_REPORT = "recon/layer2_step1b_apply.md"

SA2_CODE_ATTR = "SA2_CODE_2021"
SA2_NAME_ATTR = "SA2_NAME_2021"
SA2_STATE_ATTR = "STATE_NAME_2021"


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
        print("Run: pip install --break-system-packages geopandas shapely pyogrio rtree",
              file=sys.stderr)
        sys.exit(2)


# ---------------------------------------------------------------------------
# Coerce numpy scalars to Python natives for SQLite
# ---------------------------------------------------------------------------
def to_native(v):
    if v is None:
        return None
    if hasattr(v, "item"):  # numpy scalar
        return v.item()
    return v


# ---------------------------------------------------------------------------
# Build audit_log INSERT — exact schema match
# ---------------------------------------------------------------------------
def build_audit_insert(pre_state: dict, sa2_features: int):
    """Return (sql, params) for audit_log INSERT.

    Schema is fixed; matches kintell.db convention from prior steps.
    occurred_at omitted -> default datetime('now') fires.
    """
    n_total = pre_state["n_total_services"]
    null_post = pre_state["expected_null_post"]
    coverage_post = (n_total - null_post) / n_total if n_total else 0.0

    before = {
        "rows": n_total,
        "payload": {
            "with_sa2": n_total - pre_state["n_null_pre"],
            "null_sa2": pre_state["n_null_pre"],
            "candidates": pre_state["n_candidates"],
            "unrecoverable_no_latlng": pre_state["n_unrecoverable"],
        },
    }
    after = {
        "rows": n_total,
        "payload": {
            "with_sa2": n_total - null_post,
            "null_sa2": null_post,
            "assigned": pre_state["n_assigned"],
            "missed": pre_state["n_missed"],
            "hit_rate": round(pre_state["hit_rate"], 6),
            "coverage": round(coverage_post, 6),
            "method": "sjoin within (EPSG:4326 -> EPSG:7844)",
            "source_gpkg": GPKG_PATH,
            "source_layer": SA2_LAYER,
            "sa2_features": sa2_features,
        },
    }
    reason = (
        f"Layer 2 Step 1b: SA2 polygon point-in-polygon backfill. "
        f"Assigned {pre_state['n_assigned']}/{pre_state['n_candidates']} "
        f"candidates ({pre_state['hit_rate']:.2%}). "
        f"Misses: {pre_state['n_missed']} (offshore/null-island, no AU SA2 polygon). "
        f"NULL sa2_code: {pre_state['n_null_pre']} -> {null_post} "
        f"(of which {pre_state['n_unrecoverable']} have no lat/lng and are unrecoverable here). "
        f"Net SA2 coverage post-apply: {coverage_post:.2%}. "
        f"Source: {GPKG_PATH} layer {SA2_LAYER} (EPSG:7844)."
    )

    sql = (
        "INSERT INTO audit_log "
        "(actor, action, subject_type, subject_id, before_json, after_json, reason) "
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
# Compute proposed updates
# ---------------------------------------------------------------------------
def compute_updates(conn, gpd, pd, Point):
    cur = conn.cursor()

    svc_cols = [r[1] for r in cur.execute("PRAGMA table_info(services)").fetchall()]
    lower = {c.lower(): c for c in svc_cols}
    sa2_col = lower.get("sa2_code") or lower.get("sa2_code_2021")
    lat_col = lower.get("lat") or lower.get("latitude")
    lng_col = (lower.get("lng") or lower.get("lon") or lower.get("long")
               or lower.get("longitude"))
    id_col = lower.get("service_id") or lower.get("id")
    state_col = lower.get("state") or lower.get("state_code")

    if not all([sa2_col, lat_col, lng_col, id_col]):
        print(f"ERROR: services missing required columns. Have: {svc_cols}",
              file=sys.stderr)
        sys.exit(3)

    n_total_services = cur.execute("SELECT COUNT(*) FROM services").fetchone()[0]
    n_null_pre = cur.execute(
        f'SELECT COUNT(*) FROM services WHERE "{sa2_col}" IS NULL'
    ).fetchone()[0]
    n_unrecov = cur.execute(
        f'SELECT COUNT(*) FROM services '
        f'WHERE "{sa2_col}" IS NULL '
        f'AND ("{lat_col}" IS NULL OR "{lng_col}" IS NULL)'
    ).fetchone()[0]

    select_cols = (f'"{id_col}" AS service_id, '
                   f'CAST("{lat_col}" AS REAL) AS lat, '
                   f'CAST("{lng_col}" AS REAL) AS lng')
    if state_col:
        select_cols += f', "{state_col}" AS state'
    candidates_sql = (
        f"SELECT {select_cols} FROM services "
        f'WHERE "{sa2_col}" IS NULL '
        f'AND "{lat_col}" IS NOT NULL AND "{lng_col}" IS NOT NULL'
    )
    candidates_df = pd.read_sql_query(candidates_sql, conn)
    n_candidates = len(candidates_df)
    print(f"Loaded {n_candidates:,} candidate services")

    print(f"Reading SA2 layer '{SA2_LAYER}' from {GPKG_PATH} (~30-60s) ...")
    sa2_full = gpd.read_file(GPKG_PATH, layer=SA2_LAYER, engine="pyogrio")
    sa2_gdf = sa2_full[[SA2_CODE_ATTR, SA2_NAME_ATTR, SA2_STATE_ATTR, "geometry"]].copy()
    sa2_features = len(sa2_gdf)
    print(f"Loaded {sa2_features:,} SA2 polygons "
          f"(CRS: {sa2_gdf.crs.to_authority() if sa2_gdf.crs else '?'})")

    points_gdf = gpd.GeoDataFrame(
        candidates_df,
        geometry=[Point(lon, lat)
                  for lon, lat in zip(candidates_df["lng"], candidates_df["lat"])],
        crs="EPSG:4326",
    )
    points_proj = points_gdf.to_crs(sa2_gdf.crs)

    print("Performing point-in-polygon (sjoin within) ...")
    joined = gpd.sjoin(points_proj, sa2_gdf, how="left", predicate="within")
    joined = joined.drop_duplicates(subset="service_id", keep="first")

    has_match = joined[SA2_CODE_ATTR].notna()
    n_assigned = int(has_match.sum())
    n_missed = int((~has_match).sum())
    hit_rate = (n_assigned / n_candidates) if n_candidates else 0.0
    print(f"Hit rate: {n_assigned}/{n_candidates} ({hit_rate:.2%})")

    assigned_codes = set(
        joined.loc[has_match, SA2_CODE_ATTR].astype(str).tolist()
    )
    canonical_codes = set(
        str(r[0]) for r in cur.execute(
            "SELECT DISTINCT sa2_code FROM abs_sa2_erp_annual "
            "WHERE sa2_code IS NOT NULL"
        ).fetchall()
    )
    orphans = assigned_codes - canonical_codes
    print(f"Canonical-universe orphans: {len(orphans)}"
          + (f"  e.g. {sorted(orphans)[:5]}" if orphans else ""))

    violations: list[str] = []
    if hit_rate < HIT_RATE_THRESHOLD:
        violations.append(
            f"hit_rate {hit_rate:.2%} < threshold {HIT_RATE_THRESHOLD:.0%}"
        )
    if orphans:
        violations.append(
            f"{len(orphans)} assigned sa2_codes not in abs_sa2_erp_annual"
        )

    pre_state = {
        "n_total_services": n_total_services,
        "n_null_pre": n_null_pre,
        "n_unrecoverable": n_unrecov,
        "n_candidates": n_candidates,
        "n_assigned": n_assigned,
        "n_missed": n_missed,
        "hit_rate": hit_rate,
        "violations": violations,
        "orphans": sorted(orphans),
        "expected_null_post": n_null_pre - n_assigned,
        "id_col": id_col,
        "state_col": state_col,
        "sa2_col": sa2_col,
        "sa2_features": sa2_features,
    }
    return joined, has_match, pre_state


# ---------------------------------------------------------------------------
# Markdown report
# ---------------------------------------------------------------------------
def write_report(out_path: str, mode: str, joined, has_match, pre_state,
                 backup_path: str | None, audit_id: int | None,
                 audit_sql: str, audit_params: list) -> None:
    lines: list[str] = []

    def w(s: str = "") -> None:
        lines.append(s)

    title = "DRY RUN" if mode == "dry-run" else "APPLIED"
    w(f"# Layer 2 Step 1b — Apply ({title})")
    w("")
    w(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    w(f"Mode: **{mode}**")
    if backup_path:
        w(f"Backup: `{backup_path}`")
    w("")

    w("## Summary")
    w("")
    coverage_post = ((pre_state["n_total_services"] - pre_state["expected_null_post"])
                     / pre_state["n_total_services"]
                     if pre_state["n_total_services"] else 0)
    w(f"- Services total: **{pre_state['n_total_services']:,}**")
    w(f"- NULL `sa2_code` pre-apply: **{pre_state['n_null_pre']:,}**")
    w(f"  - Unrecoverable (no lat/lng): **{pre_state['n_unrecoverable']:,}**")
    w(f"  - Step 1b candidates: **{pre_state['n_candidates']:,}**")
    w(f"- Assigned: **{pre_state['n_assigned']:,}**")
    w(f"- Missed: **{pre_state['n_missed']:,}**")
    w(f"- Hit rate: **{pre_state['hit_rate']:.2%}** "
      f"(threshold {HIT_RATE_THRESHOLD:.0%})")
    w(f"- Expected NULL `sa2_code` post-apply: "
      f"**{pre_state['expected_null_post']:,}** "
      f"(unrecoverable {pre_state['n_unrecoverable']} + missed {pre_state['n_missed']})")
    w(f"- Net SA2 coverage post-apply: **{coverage_post:.2%}**")
    w("")

    w("## Invariants")
    w("")
    if pre_state["violations"]:
        w("**✗ VIOLATIONS — apply will be refused:**")
        w("")
        for v in pre_state["violations"]:
            w(f"- {v}")
    else:
        w("✓ All invariants pass.")
        w(f"- hit_rate {pre_state['hit_rate']:.2%} ≥ {HIT_RATE_THRESHOLD:.0%}")
        w(f"- canonical-universe orphans: 0 "
          f"(all assigned sa2_codes present in `abs_sa2_erp_annual`)")
    w("")

    if pre_state["state_col"] and pre_state["n_assigned"] > 0:
        w("## Distribution of assignments by state")
        w("")
        assigned = joined[has_match]
        if "state" in assigned.columns:
            grp = (assigned.groupby("state", dropna=False)
                   .agg(services=("service_id", "count"),
                        distinct_sa2s=(SA2_CODE_ATTR, "nunique"))
                   .sort_values("services", ascending=False))
            w("| state | services | distinct SA2s |")
            w("|---|---:|---:|")
            for state_val, row in grp.iterrows():
                label = state_val if state_val is not None else "(NULL)"
                w(f"| {label} | {row['services']:,} | {row['distinct_sa2s']:,} |")
            w("")

    if pre_state["n_assigned"] > 0:
        w("## Top 20 SA2s by assignment count")
        w("")
        assigned = joined[has_match]
        top = (assigned.groupby([SA2_CODE_ATTR, SA2_NAME_ATTR])
               .size().reset_index(name="services")
               .sort_values("services", ascending=False).head(20))
        w("| sa2_code | sa2_name | services |")
        w("|---|---|---:|")
        for _, row in top.iterrows():
            w(f"| {row[SA2_CODE_ATTR]} | {row[SA2_NAME_ATTR]} "
              f"| {row['services']:,} |")
        w("")

    w("## Misses (services that did not match any SA2 polygon)")
    w("")
    misses = joined[~has_match]
    if len(misses) == 0:
        w("(none)")
    else:
        w("| service_id | lat | lng | state |")
        w("|---|---:|---:|---|")
        for _, row in misses.iterrows():
            state_v = (row["state"] if "state" in misses.columns
                       and row["state"] is not None else "")
            w(f"| {row['service_id']} | {row['lat']} | {row['lng']} | {state_v} |")
    w("")

    if pre_state["n_assigned"] > 0:
        w("## Sample assignments (first 30 by service_id)")
        w("")
        assigned = joined[has_match].sort_values("service_id").head(30)
        w("| service_id | lat | lng | state | sa2_code | sa2_name | sa2_state |")
        w("|---|---:|---:|---|---|---|---|")
        for _, row in assigned.iterrows():
            state_v = (row["state"] if "state" in assigned.columns
                       and row["state"] is not None else "")
            w(f"| {row['service_id']} | {row['lat']} | {row['lng']} "
              f"| {state_v} | {row[SA2_CODE_ATTR]} "
              f"| {row[SA2_NAME_ATTR]} | {row[SA2_STATE_ATTR]} |")
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
            if len(display) > 300:
                display = display[:297] + "..."
            w(f"  [{i}] {display}")
        w("```")
    else:
        w(f"Inserted: action=`{AUDIT_ACTION}`, audit_id=**{audit_id}**")
    w("")

    w("---")
    w("End of report.")
    w("")

    Path("recon").mkdir(exist_ok=True)
    Path(out_path).write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Backup using SQLite backup API
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

    try:
        conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    except sqlite3.Error:
        conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    print(f"Mode: {mode.upper()}")

    joined, has_match, pre_state = compute_updates(conn, gpd, pd, Point)
    audit_sql, audit_params = build_audit_insert(pre_state,
                                                 pre_state["sa2_features"])
    conn.close()

    # ----- DRY RUN -----
    if not apply_mode:
        write_report(DRYRUN_REPORT, "dry-run", joined, has_match, pre_state,
                     None, None, audit_sql, audit_params)
        print()
        print(f"DRY-RUN OK  wrote {DRYRUN_REPORT}")
        if pre_state["violations"]:
            print("⚠ Invariant violations present — apply would be refused:")
            for v in pre_state["violations"]:
                print(f"  - {v}")
        else:
            print("✓ All invariants pass. To execute:")
            print("    python layer2_step1b_apply.py --apply")
        return 0

    # ----- APPLY -----
    if pre_state["violations"]:
        print("\n✗ INVARIANT VIOLATIONS — refusing to apply:", file=sys.stderr)
        for v in pre_state["violations"]:
            print(f"  - {v}", file=sys.stderr)
        return 2

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"data/kintell.db.backup_pre_step1b_{ts}"
    print(f"\nTaking backup: {backup_path}")
    take_backup(backup_path)
    backup_size_mb = os.path.getsize(backup_path) / (1024 * 1024)
    print(f"  backup size: {backup_size_mb:,.1f} MB")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    audit_id = None
    try:
        cur.execute("BEGIN")

        assigned = joined[has_match]
        update_pairs = [
            (str(row[SA2_CODE_ATTR]), to_native(row["service_id"]))
            for _, row in assigned.iterrows()
        ]

        sa2_col = pre_state["sa2_col"]
        id_col = pre_state["id_col"]
        cur.executemany(
            f'UPDATE services SET "{sa2_col}" = ? WHERE "{id_col}" = ?',
            update_pairs
        )
        n_updated = cur.rowcount
        print(f"  UPDATEd {len(update_pairs)} rows (cursor rowcount={n_updated})")

        n_null_post = cur.execute(
            f'SELECT COUNT(*) FROM services WHERE "{sa2_col}" IS NULL'
        ).fetchone()[0]
        expected = pre_state["expected_null_post"]
        if n_null_post != expected:
            raise RuntimeError(
                f"Post-update NULL count {n_null_post} != expected {expected}"
            )
        print(f"  post-update NULL count: {n_null_post} (matches expected)")

        bad = cur.execute(
            f'SELECT COUNT(*) FROM services s '
            f'WHERE s."{sa2_col}" IS NOT NULL '
            f'AND s."{sa2_col}" NOT IN '
            f'(SELECT sa2_code FROM abs_sa2_erp_annual WHERE sa2_code IS NOT NULL)'
        ).fetchone()[0]
        if bad > 0:
            raise RuntimeError(
                f"{bad} services have sa2_code outside canonical universe"
            )
        print(f"  canonical-universe check: OK ({bad} orphans)")

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

    write_report(APPLY_REPORT, "apply", joined, has_match, pre_state,
                 backup_path, audit_id, audit_sql, audit_params)
    print()
    print(f"APPLY OK  wrote {APPLY_REPORT}")
    print(f"          backup: {backup_path}")
    print(f"          audit_id: {audit_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
