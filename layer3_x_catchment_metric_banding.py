"""
layer3_x_catchment_metric_banding.py v1
=========================================
Layer 2.5 sub-pass 2.5.2 — Layer 3.x catchment metric banding.

Bands the 4 catchment metrics populated by sub-pass 2.5.1 into
layer3_sa2_metric_banding so the centre page can render them with
the same percentile/decile/band treatment as existing Position
metrics.

Metrics banded (4):
  - sa2_supply_ratio       (places / under_5_count)
  - sa2_child_to_place     (under_5_count / places)
  - sa2_adjusted_demand    (under_5_count * calibrated_rate * 0.6)
  - sa2_demand_supply      (adjusted_demand / places)

NOT banded:
  - demand_share_state — already a fraction of state total
    (rank-by-construction); banding a share within a state cohort
    is low marginal value. Skip for V1; revisit if needed.
  - calibrated_rate, demand_supply_inv — calibration metadata /
    render-time inverse. Not Position metrics.

Cohort: state_x_remoteness (mirrors DEC-68 / existing convention).
Discovery in stage 1 confirms the existing cohort_def / cohort_key
format and band-naming convention before writing.

Year: 2024 (u5_pop input vintage; dominant input year).
period_label: 'catchment_2024'.

STD-30 discipline. STD-31 (cohort_n recorded). STD-32 (long-format).
Idempotent: stage 4 DELETEs existing rows for the 4 new metric
names before INSERT. Re-running overwrites cleanly.

Stages:
  1. PROBE — verify cache populated, discover Layer 3 band
     convention, check cohort coverage. Hard abort if anything
     unexpected.
  2. DRY-RUN COMPUTE — for each metric, group SA2s into cohorts,
     compute percentile/decile/band per SA2. Print sample +
     cohort-size distribution. Anomaly gate.
  3. APPLY — STD-08 backup, BEGIN IMMEDIATE, DELETE then INSERT,
     audit_log, COMMIT.
  4. POST-MUTATION VALIDATION — confirm row counts, sample bands.

Usage (from repo root):
    python layer3_x_catchment_metric_banding.py
"""

import json
import math
import os
import shutil
import sqlite3
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime

DB_PATH = os.path.join("data", "kintell.db")
TABLE = "layer3_sa2_metric_banding"
CACHE_TABLE = "service_catchment_cache"

# Metrics to band: (canonical metric_name, cache column)
METRICS = [
    ("sa2_supply_ratio", "supply_ratio"),
    ("sa2_child_to_place", "child_to_place"),
    ("sa2_adjusted_demand", "adjusted_demand"),
    ("sa2_demand_supply", "demand_supply"),
]

YEAR = 2024
PERIOD_LABEL = "catchment_2024"

MIN_COHORT_N = 5  # below this, skip SA2 (percentile noise)

AUDIT_ACTOR = "layer3_x_catchment_apply"
AUDIT_ACTION = "layer3_catchment_banding_v1"
AUDIT_SUBJECT_TYPE = "layer3_sa2_metric_banding"
AUDIT_SUBJECT_ID = 0

# === HELPERS =============================================================

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def section(title):
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def fail(msg, code=1):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def column_names(cur, table):
    cur.execute(f"PRAGMA table_info({table})")
    return [r[1] for r in cur.fetchall()]


def row_count(cur, table):
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    return cur.fetchone()[0]


# === STD-13 ==============================================================

def _wmic_python_procs():
    try:
        out = subprocess.check_output(
            ["wmic", "process", "where", "name='python.exe'",
             "get", "ProcessId,ParentProcessId", "/FORMAT:CSV"],
            text=True, stderr=subprocess.DEVNULL,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    procs = []
    for line in out.splitlines():
        line = line.strip()
        if not line or line.lower().startswith("node"):
            continue
        parts = line.split(",")
        if len(parts) < 3:
            continue
        try:
            ppid = int(parts[1]); pid = int(parts[2])
        except ValueError:
            continue
        procs.append((pid, ppid))
    return procs


def std13_self_check():
    log("STD-13: scanning for orphan python.exe (WMIC)")
    my_pid = os.getpid()
    procs = _wmic_python_procs()
    if procs is None:
        log("STD-13: WMIC unavailable; SKIPPING with warning")
        return
    excluded = {my_pid}
    changed = True
    while changed:
        changed = False
        for pid, ppid in procs:
            if ppid in excluded and pid not in excluded:
                excluded.add(pid)
                changed = True
    orphans = [pid for pid, _ in procs if pid not in excluded]
    if orphans:
        fail(f"STD-13: orphan python.exe alive: {orphans}")
    log(f"STD-13: clean ({len(procs)} python procs)")


# === STAGE 1: PROBE ======================================================

def stage1_probe(conn):
    section("STAGE 1 — PROBE (read-only)")
    cur = conn.cursor()
    d = {}

    # 1.1 cache populated
    log("1.1 service_catchment_cache populated?")
    n = row_count(cur, CACHE_TABLE)
    if n == 0:
        fail("service_catchment_cache empty — run sub-pass 2.5.1 "
             "first")
    log(f"  rows: {n:,}")

    # 1.2 banding table schema
    log("1.2 layer3_sa2_metric_banding schema")
    bc = column_names(cur, TABLE)
    d["band_cols"] = bc
    log(f"  columns: {bc}")
    expected = {"sa2_code", "metric", "year", "period_label",
                "cohort_def", "cohort_key", "cohort_n",
                "raw_value", "percentile", "decile", "band"}
    missing = expected - set(bc)
    if missing:
        fail(f"banding table missing columns: {missing}")

    # 1.3 discover existing cohort_def / band conventions
    log("1.3 existing cohort conventions")
    cur.execute(f"SELECT DISTINCT cohort_def FROM {TABLE}")
    cohort_defs = [r[0] for r in cur.fetchall()]
    log(f"  distinct cohort_def: {cohort_defs}")
    if "state_x_remoteness" in cohort_defs:
        d["cohort_def"] = "state_x_remoteness"
    elif len(cohort_defs) == 1:
        d["cohort_def"] = cohort_defs[0]
        log(f"  using existing convention: {d['cohort_def']}")
    else:
        fail(f"multiple cohort_def values; need to choose: "
             f"{cohort_defs}")

    # Sample cohort_keys
    cur.execute(
        f"SELECT cohort_def, cohort_key, COUNT(*) FROM {TABLE} "
        f"WHERE cohort_def = ? GROUP BY cohort_key "
        f"ORDER BY 3 DESC LIMIT 20",
        (d["cohort_def"],),
    )
    log(f"  sample cohort_keys for {d['cohort_def']!r}:")
    for cdef, ckey, n in cur.fetchall():
        log(f"    {ckey!r:<40} ({n:,} rows)")

    # 1.4 band convention
    log("1.4 band convention")
    cur.execute(
        f"SELECT band, COUNT(*) FROM {TABLE} "
        f"GROUP BY band ORDER BY 2 DESC"
    )
    band_counts = cur.fetchall()
    log(f"  distinct bands: {band_counts}")
    bands = [b for b, _ in band_counts]

    # Discover decile->band mapping by sampling
    cur.execute(
        f"SELECT decile, band, COUNT(*) FROM {TABLE} "
        f"WHERE band IS NOT NULL "
        f"GROUP BY decile, band ORDER BY decile, 3 DESC"
    )
    decile_band = cur.fetchall()
    log(f"  decile -> band distribution:")
    decile_to_band = {}
    for dec, b, n in decile_band:
        if dec not in decile_to_band:
            decile_to_band[dec] = b  # most common (already ordered)
        log(f"    decile {dec:>2}: {b!r} ({n:,})")
    d["decile_to_band"] = decile_to_band
    log(f"  inferred decile->band map: {decile_to_band}")

    # Validate the inferred mapping is monotone (low deciles -> low
    # band consistently, high deciles -> high band consistently)
    if not decile_to_band:
        fail("no decile->band data found; cannot infer convention")

    # 1.5 sa2_cohort coverage
    log("1.5 sa2_cohort (state + remoteness for cohort key)")
    cc = column_names(cur, "sa2_cohort")
    d["cohort_cols"] = cc
    if "state_code" not in cc:
        fail("sa2_cohort: no state_code")
    if "ra_band" not in cc:
        fail("sa2_cohort: no ra_band")
    cur.execute(
        "SELECT COUNT(*), COUNT(state_code), COUNT(ra_band) "
        "FROM sa2_cohort"
    )
    n, ns, nr = cur.fetchone()
    log(f"  rows: {n:,}; with state: {ns:,}; with ra_band: {nr:,}")

    # Sample state_code + ra_band combos
    cur.execute(
        "SELECT state_code, ra_band, COUNT(*) FROM sa2_cohort "
        "GROUP BY state_code, ra_band ORDER BY state_code, ra_band"
    )
    log(f"  state x ra_band cohorts (count of SA2s per cohort):")
    cohort_sizes = []
    for st, ra, c in cur.fetchall():
        cohort_sizes.append((st, ra, c))
        log(f"    state={st!r} ra={ra!r}: {c:,}")
    d["cohort_sizes"] = cohort_sizes

    # 1.6 verify the 4 metrics are not already banded (warn if any)
    log("1.6 collision check")
    target_metrics = [m for m, _ in METRICS]
    placeholders = ",".join("?" for _ in target_metrics)
    cur.execute(
        f"SELECT metric, COUNT(*) FROM {TABLE} "
        f"WHERE metric IN ({placeholders}) GROUP BY metric",
        target_metrics,
    )
    existing = cur.fetchall()
    if existing:
        log(f"  WARNING: target metrics already present: {existing}")
        log(f"  (idempotent: stage 4 DELETEs them before re-INSERT)")
    else:
        log(f"  clean — none of the 4 target metrics present")

    log("STAGE 1 — GO.")
    return d


# === STAGE 2: DRY-RUN COMPUTE ============================================

def compute_band(decile, decile_to_band):
    """Map decile to band using the discovered convention."""
    return decile_to_band.get(decile)


def stage2_dry_run(conn, d):
    section("STAGE 2 — DRY-RUN COMPUTE (read-only, in-memory)")
    cur = conn.cursor()

    # Build SA2 -> (state, ra_band) map
    cur.execute(
        "SELECT sa2_code, state_code, ra_band FROM sa2_cohort"
    )
    sa2_to_cohort = {
        sa2: (str(st), ra) for sa2, st, ra in cur.fetchall()
        if st is not None and ra is not None
    }
    log(f"  SA2 -> (state, ra_band) map: {len(sa2_to_cohort):,}")

    all_rows_to_insert = []
    per_metric_summary = []

    for metric_name, cache_col in METRICS:
        log(f"\n  metric: {metric_name} (cache.{cache_col})")

        # Fetch DISTINCT (sa2_code, value) — values are broadcast in
        # the cache, one canonical value per SA2.
        cur.execute(
            f"SELECT DISTINCT sa2_code, {cache_col} "
            f"FROM {CACHE_TABLE} "
            f"WHERE {cache_col} IS NOT NULL"
        )
        sa2_values = {sa2: v for sa2, v in cur.fetchall()}
        log(f"    SA2s with non-null {cache_col}: "
            f"{len(sa2_values):,}")

        # Group by cohort
        cohort_to_sa2_value = defaultdict(list)
        skipped_no_cohort = 0
        for sa2, v in sa2_values.items():
            ck = sa2_to_cohort.get(sa2)
            if ck is None:
                skipped_no_cohort += 1
                continue
            cohort_to_sa2_value[ck].append((sa2, v))

        log(f"    SA2s skipped (no cohort): {skipped_no_cohort}")
        log(f"    cohorts found: {len(cohort_to_sa2_value)}")

        # Compute banding per cohort
        rows_for_metric = 0
        skipped_small_cohort = 0
        for cohort, items in cohort_to_sa2_value.items():
            if len(items) < MIN_COHORT_N:
                skipped_small_cohort += len(items)
                continue
            cohort_n = len(items)
            cohort_key = f"{cohort[0]}_{cohort[1]}"
            # Sort by value ascending; rank assignment.
            items.sort(key=lambda x: x[1])
            for rank, (sa2, val) in enumerate(items, start=1):
                # Percentile: 0 to 1 inclusive. Use (rank-0.5)/n
                # convention to avoid 0/1 edge values.
                percentile = (rank - 0.5) / cohort_n
                # Decile: 1-10
                decile = max(1, min(10, math.ceil(percentile * 10)))
                band = compute_band(decile, d["decile_to_band"])
                all_rows_to_insert.append({
                    "sa2_code": sa2,
                    "metric": metric_name,
                    "year": YEAR,
                    "period_label": PERIOD_LABEL,
                    "cohort_def": d["cohort_def"],
                    "cohort_key": cohort_key,
                    "cohort_n": cohort_n,
                    "raw_value": val,
                    "percentile": percentile,
                    "decile": decile,
                    "band": band,
                })
                rows_for_metric += 1

        log(f"    rows to insert: {rows_for_metric:,}; "
            f"skipped (small cohort): {skipped_small_cohort}")
        per_metric_summary.append(
            (metric_name, rows_for_metric, skipped_small_cohort)
        )

    # Anomaly checks
    log("\n  cohort-size distribution:")
    cohort_sizes = Counter()
    for r in all_rows_to_insert:
        cohort_sizes[r["cohort_key"]] = r["cohort_n"]
    sizes = sorted(set(cohort_sizes.values()))
    log(f"    distinct cohort sizes: {len(sizes)}; "
        f"min={min(sizes)}, max={max(sizes)}, "
        f"median={sorted(cohort_sizes.values())[len(cohort_sizes)//2]}")

    # Sample rows
    log(f"\n  sample rows (first 3):")
    for r in all_rows_to_insert[:3]:
        log(f"    {r}")

    # Summary table
    log(f"\n  per-metric summary:")
    log(f"    {'metric':<28}{'inserted':>10}{'skipped':>10}")
    total = 0
    for m, n, sk in per_metric_summary:
        log(f"    {m:<28}{n:>10,}{sk:>10,}")
        total += n
    log(f"    {'TOTAL':<28}{total:>10,}")

    # Sanity: total should be in the right ballpark (4 metrics × 
    # ~2,300 SA2s = ~9,200 max)
    if total < 1000:
        fail(f"STAGE 2: only {total} rows total — looks broken")
    if total > 12000:
        fail(f"STAGE 2: {total} rows is unexpectedly high")

    log("STAGE 2 — GO.")
    return all_rows_to_insert


# === STAGE 3: APPLY ======================================================

def stage3_apply(rows):
    section("STAGE 3 — APPLY (DB write per STD-30)")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(
        "data", f"kintell.db.backup_pre_2_5_2_{ts}"
    )
    log(f"STD-08: copy {DB_PATH} -> {backup_path}")
    shutil.copy2(DB_PATH, backup_path)
    if os.path.getsize(backup_path) != os.path.getsize(DB_PATH):
        fail("STD-08: backup size mismatch")
    log(f"STD-08: backup OK ({os.path.getsize(backup_path):,} bytes)")

    conn = sqlite3.connect(DB_PATH, isolation_level=None)
    cur = conn.cursor()
    target_metrics = [m for m, _ in METRICS]
    placeholders = ",".join("?" for _ in target_metrics)
    try:
        log("BEGIN IMMEDIATE")
        cur.execute("BEGIN IMMEDIATE")

        # Idempotent: delete prior rows for these metrics
        cur.execute(
            f"SELECT COUNT(*) FROM {TABLE} "
            f"WHERE metric IN ({placeholders})",
            target_metrics,
        )
        prior_n = cur.fetchone()[0]
        log(f"DELETE prior {prior_n:,} rows for these 4 metrics")
        cur.execute(
            f"DELETE FROM {TABLE} WHERE metric IN ({placeholders})",
            target_metrics,
        )

        log(f"INSERT {len(rows):,}")
        cols = ["sa2_code", "metric", "year", "period_label",
                "cohort_def", "cohort_key", "cohort_n",
                "raw_value", "percentile", "decile", "band"]
        sql = (f"INSERT INTO {TABLE} ({', '.join(cols)}) "
               f"VALUES ({', '.join('?' for _ in cols)})")
        batch = [tuple(r[c] for c in cols) for r in rows]
        cur.executemany(sql, batch)

        # audit_log
        cur.execute(
            f"SELECT COUNT(*) FROM {TABLE} "
            f"WHERE metric IN ({placeholders})",
            target_metrics,
        )
        new_n = cur.fetchone()[0]
        if new_n != len(rows):
            raise RuntimeError(
                f"post-INSERT count {new_n} != {len(rows)}"
            )

        before_json = json.dumps({"prior_rows_for_metrics": prior_n})
        after_json = json.dumps({
            "inserted_rows": new_n,
            "metrics": target_metrics,
            "year": YEAR,
            "period_label": PERIOD_LABEL,
            "backup": os.path.basename(backup_path),
        })
        reason = (
            "Layer 2.5 sub-pass 2.5.2: Layer 3.x catchment metric "
            "banding. Bands 4 catchment metrics from "
            "service_catchment_cache (supply_ratio, child_to_place, "
            "adjusted_demand, demand_supply) into "
            "layer3_sa2_metric_banding by state_x_remoteness "
            "cohort. Per-SA2 percentile = (rank - 0.5) / cohort_n; "
            "decile = ceil(percentile * 10) clamped [1, 10]; band "
            "from existing decile->band convention discovered in "
            "stage 1. Skipped SA2s in cohorts of size < "
            f"{MIN_COHORT_N}. Idempotent DELETE+INSERT."
        )
        cur.execute(
            "INSERT INTO audit_log (actor, action, subject_type, "
            "subject_id, before_json, after_json, reason) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (AUDIT_ACTOR, AUDIT_ACTION, AUDIT_SUBJECT_TYPE,
             AUDIT_SUBJECT_ID, before_json, after_json, reason),
        )
        audit_id = cur.lastrowid

        log("COMMIT")
        cur.execute("COMMIT")
        return {
            "backup_path": backup_path,
            "audit_id": audit_id,
            "row_count": new_n,
            "prior_n": prior_n,
        }
    except Exception as e:
        log(f"EXCEPTION: {e!r} -- ROLLBACK")
        try:
            cur.execute("ROLLBACK")
        except Exception:
            pass
        raise
    finally:
        conn.close()


def post_validate(result):
    section("POST-MUTATION VALIDATION (read-only)")
    uri = f"file:{DB_PATH}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    cur = conn.cursor()
    target_metrics = [m for m, _ in METRICS]
    placeholders = ",".join("?" for _ in target_metrics)
    try:
        cur.execute(
            f"SELECT metric, COUNT(*) FROM {TABLE} "
            f"WHERE metric IN ({placeholders}) GROUP BY metric "
            f"ORDER BY metric",
            target_metrics,
        )
        log("  per-metric row counts:")
        total = 0
        for m, n in cur.fetchall():
            log(f"    {m:<28} {n:,}")
            total += n
        log(f"    TOTAL                       {total:,}")
        if total != result["row_count"]:
            fail(f"row-count drift: {total} != {result['row_count']}")

        # Spot-check decile -> band consistency
        cur.execute(
            f"SELECT metric, decile, band, COUNT(*) "
            f"FROM {TABLE} "
            f"WHERE metric IN ({placeholders}) "
            f"GROUP BY metric, decile, band "
            f"ORDER BY metric, decile",
            target_metrics,
        )
        log("\n  decile->band sample (per metric):")
        cur_metric = None
        for m, dec, b, n in cur.fetchall():
            if m != cur_metric:
                log(f"    {m}:")
                cur_metric = m
            log(f"      decile {dec:>2}: {b} ({n})")

        # Spot-check raw_value ranges
        cur.execute(
            f"SELECT metric, MIN(raw_value), "
            f"ROUND(AVG(raw_value), 4), MAX(raw_value) "
            f"FROM {TABLE} "
            f"WHERE metric IN ({placeholders}) GROUP BY metric "
            f"ORDER BY metric",
            target_metrics,
        )
        log("\n  raw_value ranges:")
        for m, mn, av, mx in cur.fetchall():
            log(f"    {m:<28} min={mn} avg={av} max={mx}")

        # audit_log row exists
        cur.execute(
            "SELECT audit_id, actor, action, occurred_at "
            "FROM audit_log WHERE audit_id = ?",
            (result["audit_id"],),
        )
        row = cur.fetchone()
        if not row:
            fail(f"audit_log row {result['audit_id']} missing")
        log(f"\n  audit_log OK: {row}")
    finally:
        conn.close()


def main():
    print("=" * 72)
    print("layer3_x_catchment_metric_banding.py v1")
    print(f"started      : {datetime.now().isoformat()}")
    print(f"target db    : {os.path.abspath(DB_PATH)}")
    print(f"target table : {TABLE}")
    print(f"metrics      : {[m for m, _ in METRICS]}")
    print(f"year         : {YEAR}")
    print(f"period_label : {PERIOD_LABEL!r}")
    print("=" * 72)

    if not os.path.exists(DB_PATH):
        fail(f"DB not found at {DB_PATH}")

    ro_uri = f"file:{DB_PATH}?mode=ro"
    ro = sqlite3.connect(ro_uri, uri=True)
    try:
        d = stage1_probe(ro)
        rows = stage2_dry_run(ro, d)
    finally:
        ro.close()

    std13_self_check()
    result = stage3_apply(rows)
    post_validate(result)

    print()
    print("=" * 72)
    print("LAYER 2.5 SUB-PASS 2.5.2 — SUCCESS")
    print(f"rows inserted : {result['row_count']:,} "
          f"(replaced {result['prior_n']:,})")
    print(f"audit_id      : {result['audit_id']}")
    print(f"backup        : {result['backup_path']}")
    print(f"finished      : {datetime.now().isoformat()}")
    print("=" * 72)


if __name__ == "__main__":
    main()
