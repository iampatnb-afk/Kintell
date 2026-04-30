"""
populate_service_catchment_cache.py v4
=======================================
Layer 2.5 sub-pass 2.5.1 — populator for service_catchment_cache.

v2 changes from v1:
  - Correct table names per inventory:
      ERP:          abs_sa2_erp_annual (long-format, age_group filter)
      Unemployment: abs_sa2_unemployment_quarterly (rate, year_qtr)
      Income:       abs_sa2_socioeconomic_annual (long-format)
      SEIFA:        abs_sa2_socioeconomic_annual (long-format)
      Female LFP:   abs_sa2_education_employment_annual (long-format)
      Banding:      layer3_sa2_metric_banding, column 'metric' (not
                    'metric_name')
  - Active services filter: services.is_active = 1
    AND sa2_code IS NOT NULL.
  - new_competitor_12m source: services.approval_granted_date.
  - Stage 1 prints distinct metric_name / age_group values for each
    long-format table so any pattern-match miss surfaces a usable
    list without another full round.

[Same multi-stage structure / gates / STD-30 discipline as v1.]

Usage (from repo root):
    python populate_service_catchment_cache.py
"""

import json
import os
import shutil
import sqlite3
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from statistics import median

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from catchment_calibration import calibrate_participation_rate  # noqa

try:
    from catchment_calibration import ATTENDANCE_FACTOR  # noqa
except ImportError:
    ATTENDANCE_FACTOR = 0.6


# === CONSTANTS ===========================================================
DB_PATH = os.path.join("data", "kintell.db")
TABLE = "service_catchment_cache"

AUDIT_ACTOR = "layer2_5_apply"
AUDIT_ACTION = "service_catchment_cache_populate_v1"
AUDIT_SUBJECT_TYPE = "service_catchment_cache"
AUDIT_SUBJECT_ID = 0

MAX_NULL_PCT_U5_POP = 0.05
MAX_NULL_PCT_PLACES = 0.01
MAX_NULL_PCT_CALIBRATED_RATE = 0.01
MAX_NULL_PCT_DEMAND_SHARE_STATE = 0.01
RATE_MIN = 0.43
RATE_MAX = 0.55
MAX_RATIO_SANITY = 10000.0
EXPECTED_COLUMN_COUNT = 24

ALL_COLUMNS = [
    "service_id", "sa2_code", "sa2_name", "u5_pop", "median_income",
    "seifa_irsd", "unemployment_pct", "supply_ratio", "supply_band",
    "supply_ratio_4q_change", "is_deteriorating",
    "competing_centres_count", "new_competitor_12m",
    "ccs_dependency_pct", "as_of_date", "created_at", "updated_at",
    "adjusted_demand", "demand_share_state", "demand_supply",
    "child_to_place", "calibrated_rate", "rule_text",
    "calibration_run_at",
]


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


def utc_now_str():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def column_names(cur, table):
    cur.execute(f"PRAGMA table_info({table})")
    return [row[1] for row in cur.fetchall()]


def row_count(cur, table):
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    return cur.fetchone()[0]


def find_metric(metrics, *patterns_any):
    """Find first metric matching ANY of the all-must-be-present
    pattern groups. Each pattern group is a tuple of substrings; the
    metric matches the group if all substrings are in the metric name
    (case-insensitive)."""
    for pgroup in patterns_any:
        for m in metrics:
            ml = m.lower()
            if all(p in ml for p in pgroup):
                return m
    return None


def find_age_group(values, *patterns):
    """Find first age_group value matching any pattern (substring,
    case-insensitive, after stripping whitespace and dashes)."""
    for v in values:
        s = str(v).lower().replace(" ", "").replace("-", "").replace("_", "")
        for p in patterns:
            ps = p.lower().replace(" ", "").replace("-", "").replace("_", "")
            if s == ps:
                return v
    return None


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
    log(f"STD-13: clean ({len(procs)} python procs, all descendants)")


# === STAGE 1: PROBE ======================================================

def stage1_probe(conn):
    section("STAGE 1 — PROBE (read-only source discovery)")
    cur = conn.cursor()
    d = {"warnings": []}

    # --- 1.1 services ----------------------------------------------------
    log("1.1 services")
    sc = column_names(cur, "services")
    d["services_cols"] = sc
    if "service_id" not in sc:
        fail("services: no service_id column")
    if "sa2_code" not in sc:
        fail("services: no sa2_code column")
    if "is_active" not in sc:
        fail("services: no is_active column")
    if "approved_places" not in sc:
        fail("services: no approved_places column")
    if "state" not in sc:
        fail("services: no state column")

    af = "is_active = 1 AND sa2_code IS NOT NULL AND sa2_code != ''"
    d["active_filter"] = af
    d["services_pk"] = "service_id"
    d["services_name_col"] = "service_name" if "service_name" in sc else None
    d["services_places_col"] = "approved_places"
    d["services_state_col"] = "state"
    d["services_open_col"] = (
        "approval_granted_date" if "approval_granted_date" in sc else None
    )

    cur.execute(f"SELECT COUNT(*) FROM services WHERE {af}")
    n_active = cur.fetchone()[0]
    d["n_active"] = n_active
    log(f"  active services (is_active=1, sa2-assigned): "
        f"{n_active:,} of {row_count(cur, 'services'):,}")
    log(f"  open-date col: {d['services_open_col']}")

    # --- 1.2 abs_sa2_erp_annual ------------------------------------------
    log("1.2 abs_sa2_erp_annual (under-5 population)")
    erp_cols = column_names(cur, "abs_sa2_erp_annual")
    d["erp_cols"] = erp_cols
    if "age_group" not in erp_cols or "persons" not in erp_cols:
        fail(f"abs_sa2_erp_annual: missing expected cols. "
             f"got: {erp_cols}")
    cur.execute(
        "SELECT DISTINCT age_group FROM abs_sa2_erp_annual "
        "ORDER BY age_group"
    )
    age_vals = [r[0] for r in cur.fetchall()]
    log(f"  age_group values ({len(age_vals)}): {age_vals}")
    u5_age = None
    persons_cands = [v for v in age_vals
                     if "person" in str(v).lower()
                     and ("under" in str(v).lower()
                          or "u5" in str(v).lower())]
    if persons_cands:
        u5_age = persons_cands[0]
    else:
        for v in age_vals:
            vl = str(v).lower().replace("_", "").replace("-", "").replace(" ", "")
            if vl in ("04", "u5", "under5"):
                u5_age = v
                break
    if not u5_age:
        # Fallback: find smallest band starting with 0
        for v in age_vals:
            s = str(v).strip()
            if s.startswith("0") and any(c in s for c in ("-", "_", "to")):
                u5_age = v
                log(f"  fallback under-5 match: {u5_age!r}")
                break
    if not u5_age:
        fail(f"abs_sa2_erp_annual: cannot identify under-5 age_group "
             f"in {age_vals}")
    d["erp_u5_age"] = u5_age
    cur.execute("SELECT MAX(year) FROM abs_sa2_erp_annual")
    d["erp_latest_year"] = cur.fetchone()[0]
    log(f"  using age_group={u5_age!r}, latest year={d['erp_latest_year']}")

    # --- 1.3 sa2_cohort --------------------------------------------------
    log("1.3 sa2_cohort")
    coh = column_names(cur, "sa2_cohort")
    if "ra_band" not in coh or "state_code" not in coh:
        fail(f"sa2_cohort missing expected cols: {coh}")
    d["cohort_state_col"] = "state_code"
    d["cohort_name_col"] = "sa2_name" if "sa2_name" in coh else None
    log(f"  rows: {row_count(cur, 'sa2_cohort'):,}")

    # --- 1.4 layer3_sa2_metric_banding -----------------------------------
    log("1.4 layer3_sa2_metric_banding (income decile lookup)")
    bc = column_names(cur, "layer3_sa2_metric_banding")
    if "metric" not in bc or "decile" not in bc:
        fail(f"banding: missing metric/decile. cols: {bc}")
    cur.execute(
        "SELECT DISTINCT metric FROM layer3_sa2_metric_banding "
        "ORDER BY metric"
    )
    metrics = [r[0] for r in cur.fetchall()]
    log(f"  metrics ({len(metrics)}): {metrics}")
    inc_metric = find_metric(
        metrics,
        ("median", "household", "income"),
        ("median", "income"),
        ("household", "income"),
        ("income",),
    )
    if not inc_metric:
        fail(f"banding: no income metric found in {metrics}")
    d["band_income_metric"] = inc_metric
    log(f"  income metric for decile: {inc_metric}")

    # --- 1.5 abs_sa2_education_employment_annual (female LFP) ------------
    log("1.5 abs_sa2_education_employment_annual (female LFP)")
    ec = column_names(cur, "abs_sa2_education_employment_annual")
    d["edu_cols"] = ec
    if "metric_name" not in ec or "value" not in ec:
        fail(f"edu_emp: missing metric_name/value. cols: {ec}")
    cur.execute(
        "SELECT DISTINCT metric_name "
        "FROM abs_sa2_education_employment_annual "
        "ORDER BY metric_name"
    )
    edu_metrics = [r[0] for r in cur.fetchall()]
    log(f"  metric_name values ({len(edu_metrics)}):")
    for m in edu_metrics:
        log(f"    - {m}")
    flpf_metric = find_metric(
        edu_metrics,
        ("lfp", "female"),
        ("labour", "female", "participation"),
        ("labour", "female", "rate"),
        ("labor", "female", "participation"),
        ("female", "lfp", "pct"),
        ("female", "labour", "force"),
    )
    if flpf_metric:
        d["flpf_metric"] = flpf_metric
        cur.execute(
            "SELECT MAX(year) FROM abs_sa2_education_employment_annual "
            "WHERE metric_name = ?",
            (flpf_metric,),
        )
        d["flpf_year"] = cur.fetchone()[0]
        # Sample row
        cur.execute(
            "SELECT sa2_code, value FROM "
            "abs_sa2_education_employment_annual "
            "WHERE metric_name = ? AND year = ? LIMIT 1",
            (flpf_metric, d["flpf_year"]),
        )
        sample = cur.fetchone()
        log(f"  female LFP metric: {flpf_metric!r} "
            f"(year {d['flpf_year']}; sample {sample})")
    else:
        d["flpf_metric"] = None
        d["warnings"].append(
            "no female LFP metric matched; calibration nudge "
            "for female_lfp_pct will fire as None on every SA2"
        )
        log("  female LFP: NOT MATCHED — passing None to calibrator")

    # --- 1.6 abs_sa2_socioeconomic_annual (income, SEIFA) ----------------
    log("1.6 abs_sa2_socioeconomic_annual (median income + SEIFA)")
    sec = column_names(cur, "abs_sa2_socioeconomic_annual")
    if "metric_name" not in sec or "value" not in sec:
        fail(f"socioec: missing metric_name/value. cols: {sec}")
    cur.execute(
        "SELECT DISTINCT metric_name FROM abs_sa2_socioeconomic_annual "
        "ORDER BY metric_name"
    )
    sec_metrics = [r[0] for r in cur.fetchall()]
    log(f"  metric_name values ({len(sec_metrics)}):")
    for m in sec_metrics:
        log(f"    - {m}")

    inc_raw_metric = find_metric(
        sec_metrics,
        ("median", "household", "income"),
        ("median", "income"),
        ("household", "income"),
    )
    d["soc_income_metric"] = inc_raw_metric
    log(f"  median_income raw metric: {inc_raw_metric}")

    irsd_metric = find_metric(
        sec_metrics,
        ("irsd", "score"),
        ("irsd",),
        ("seifa", "irsd"),
    )
    d["soc_irsd_metric"] = irsd_metric
    log(f"  seifa_irsd metric: {irsd_metric}")

    # --- 1.7 abs_sa2_unemployment_quarterly ------------------------------
    log("1.7 abs_sa2_unemployment_quarterly")
    uc = column_names(cur, "abs_sa2_unemployment_quarterly")
    if "rate" not in uc or "year_qtr" not in uc:
        fail(f"unemp: missing rate/year_qtr. cols: {uc}")
    cur.execute(
        "SELECT MAX(year_qtr) FROM abs_sa2_unemployment_quarterly"
    )
    d["unemp_latest_qtr"] = cur.fetchone()[0]
    log(f"  latest year_qtr: {d['unemp_latest_qtr']}")

    log("STAGE 1 — GO. Essentials present.")
    return d


# === STAGE 2: CALIBRATION SMOKE-TEST =====================================

def stage2_calibration_smoketest(conn, d):
    section("STAGE 2 — CALIBRATION SMOKE-TEST (read-only)")
    cur = conn.cursor()

    # ARIA per SA2
    cur.execute("SELECT sa2_code, ra_band FROM sa2_cohort")
    aria_map = dict(cur.fetchall())
    log(f"  ARIA: {len(aria_map):,} SA2s")

    # Income decile per SA2 from layer3 banding (latest year)
    inc_decile_map = {}
    if d["band_income_metric"]:
        cur.execute(
            "SELECT MAX(year) FROM layer3_sa2_metric_banding "
            "WHERE metric = ?",
            (d["band_income_metric"],),
        )
        latest = cur.fetchone()[0]
        cur.execute(
            "SELECT sa2_code, decile FROM layer3_sa2_metric_banding "
            "WHERE metric = ? AND year = ?",
            (d["band_income_metric"], latest),
        )
        inc_decile_map = dict(cur.fetchall())
        log(f"  income decile: {len(inc_decile_map):,} SA2s "
            f"(year={latest})")

    # Female LFP per SA2 (latest year for that metric)
    flpf_map = {}
    if d.get("flpf_metric"):
        cur.execute(
            "SELECT sa2_code, value FROM "
            "abs_sa2_education_employment_annual "
            "WHERE metric_name = ? AND year = ?",
            (d["flpf_metric"], d["flpf_year"]),
        )
        for sa2, v in cur.fetchall():
            try:
                flpf_map[sa2] = float(v) if v is not None else None
            except (ValueError, TypeError):
                flpf_map[sa2] = None
        log(f"  female LFP: {len(flpf_map):,} SA2s")

    log("running calibrate_participation_rate over all SA2s")
    rates = []
    rate_counter = Counter()
    rule_counter = Counter()
    cal_results = {}
    failures = 0
    for sa2 in aria_map:
        try:
            rate, rule = calibrate_participation_rate(
                income_decile=inc_decile_map.get(sa2),
                female_lfp_pct=flpf_map.get(sa2),
                nes_share_pct=None,
                aria_band=aria_map.get(sa2),
            )
            cal_results[sa2] = (rate, rule)
            rates.append(rate)
            rate_counter[round(rate, 3)] += 1
            rule_counter[rule] += 1
        except Exception as e:
            failures += 1
            if failures <= 3:
                log(f"  failure {sa2}: {e!r}")

    if failures > 0:
        fail(f"STAGE 2: {failures} calibration failures")

    if rates:
        log(f"  calibrated {len(rates):,}; "
            f"min/median/max: {min(rates):.3f} / "
            f"{median(rates):.3f} / {max(rates):.3f}")
        log(f"  rate distribution:")
        rmax = max(rate_counter.values())
        for r, n in sorted(rate_counter.items()):
            bar = "#" * int(50 * n / rmax)
            log(f"    {r:.3f}: {n:5,} {bar}")
        log(f"  distinct rule_text variants: {len(rule_counter)}")
        for rule, n in rule_counter.most_common(5):
            log(f"    {n:5,}× {rule[:80]}")

    if rates and (min(rates) < RATE_MIN or max(rates) > RATE_MAX):
        fail(f"STAGE 2: rate outside [{RATE_MIN}, {RATE_MAX}]")
    if len(rate_counter) == 1:
        fail("STAGE 2: all rates identical — calibration inputs "
             "all None")

    log("STAGE 2 — GO.")
    return {"cal_results": cal_results, "aria_map": aria_map}


# === STAGE 3: DRY-RUN COMPUTE ============================================

def stage3_dry_run(conn, d, smoke):
    section("STAGE 3 — DRY-RUN COMPUTE (read-only, in-memory)")
    cur = conn.cursor()

    # --- 3.1 per-SA2 attribute lookups ------------------------------------
    log("3.1 loading per-SA2 attributes")

    # u5_pop from ERP long-format (filter by age_group + latest year)
    cur.execute(
        "SELECT sa2_code, persons FROM abs_sa2_erp_annual "
        "WHERE age_group = ? AND year = ?",
        (d["erp_u5_age"], d["erp_latest_year"]),
    )
    u5_map = {}
    for sa2, p in cur.fetchall():
        try:
            u5_map[sa2] = int(p) if p is not None else None
        except (ValueError, TypeError):
            u5_map[sa2] = None
    log(f"  u5_pop ({d['erp_u5_age']}, {d['erp_latest_year']}): "
        f"{len(u5_map):,} SA2s, "
        f"non-null={sum(1 for v in u5_map.values() if v):,}")

    # SA2 → name + state from cohort
    name_map = {}
    sa2_state_map = {}
    cur.execute(
        f"SELECT sa2_code, "
        f"{d['cohort_name_col'] or 'NULL'} AS name, "
        f"{d['cohort_state_col']} FROM sa2_cohort"
    )
    for sa2, nm, st in cur.fetchall():
        if nm:
            name_map[sa2] = nm
        if st:
            sa2_state_map[sa2] = st

    # median_income from socioec long-format (latest year for metric)
    income_map = {}
    if d.get("soc_income_metric"):
        cur.execute(
            "SELECT MAX(year) FROM abs_sa2_socioeconomic_annual "
            "WHERE metric_name = ?",
            (d["soc_income_metric"],),
        )
        yr = cur.fetchone()[0]
        cur.execute(
            "SELECT sa2_code, value FROM "
            "abs_sa2_socioeconomic_annual "
            "WHERE metric_name = ? AND year = ?",
            (d["soc_income_metric"], yr),
        )
        income_map = {sa2: v for sa2, v in cur.fetchall()
                      if v is not None}
        log(f"  median_income ({yr}): {len(income_map):,}")

    # seifa_irsd from socioec long-format (latest year)
    seifa_map = {}
    if d.get("soc_irsd_metric"):
        cur.execute(
            "SELECT MAX(year) FROM abs_sa2_socioeconomic_annual "
            "WHERE metric_name = ?",
            (d["soc_irsd_metric"],),
        )
        yr = cur.fetchone()[0]
        cur.execute(
            "SELECT sa2_code, value FROM "
            "abs_sa2_socioeconomic_annual "
            "WHERE metric_name = ? AND year = ?",
            (d["soc_irsd_metric"], yr),
        )
        seifa_map = {sa2: int(v) if v is not None else None
                     for sa2, v in cur.fetchall()
                     if v is not None}
        log(f"  seifa_irsd ({yr}): {len(seifa_map):,}")

    # unemployment_pct latest year_qtr
    unemp_map = {}
    cur.execute(
        "SELECT sa2_code, rate FROM abs_sa2_unemployment_quarterly "
        "WHERE year_qtr = ?",
        (d["unemp_latest_qtr"],),
    )
    unemp_map = {sa2: v for sa2, v in cur.fetchall()
                 if v is not None}
    log(f"  unemployment_pct ({d['unemp_latest_qtr']}): "
        f"{len(unemp_map):,}")

    # --- 3.2 places + centre counts per SA2 ------------------------------
    log("3.2 aggregating active services per SA2")
    af = d["active_filter"]
    cur.execute(
        f"SELECT sa2_code, SUM(approved_places), COUNT(*) "
        f"FROM services WHERE {af} GROUP BY sa2_code"
    )
    places_map = {}
    centres_count_map = {}
    for sa2, total, n in cur.fetchall():
        places_map[sa2] = int(total) if total is not None else 0
        centres_count_map[sa2] = n
    log(f"  SA2s with active services: {len(places_map):,}; "
        f"total places: {sum(places_map.values()):,}")

    # SA2 → state fallback via services if cohort missing
    cur.execute(
        f"SELECT DISTINCT sa2_code, state FROM services WHERE {af}"
    )
    for sa2, st in cur.fetchall():
        if sa2 not in sa2_state_map and st:
            sa2_state_map[sa2] = st

    # new_competitor_12m per SA2 (services opened in last 365 days)
    new_comp_map = defaultdict(int)
    if d.get("services_open_col"):
        oc = d["services_open_col"]
        try:
            cur.execute(
                f"SELECT sa2_code, COUNT(*) FROM services "
                f"WHERE {af} AND {oc} IS NOT NULL "
                f"AND julianday({oc}) >= "
                f"julianday('now', '-365 days') "
                f"GROUP BY sa2_code"
            )
            for sa2, n in cur.fetchall():
                new_comp_map[sa2] = n
            log(f"  new_competitor_12m: flagged in "
                f"{len(new_comp_map):,} SA2s")
        except sqlite3.OperationalError as e:
            log(f"  new_competitor_12m query failed: {e!r} → all NULL")
            new_comp_map = None
    else:
        new_comp_map = None
        log("  new_competitor_12m: no opened-date col → all NULL")

    # --- 3.3 per-SA2 derived ratios + state denominators -----------------
    log("3.3 computing per-SA2 ratios + state denominators "
        "(option a: all SA2s in state)")
    cal = smoke["cal_results"]
    cal_run_at = utc_now_str()

    sa2_records = {}
    state_demand_totals = defaultdict(float)
    sa2_with_no_pop = 0
    sa2_with_zero_places = 0

    all_sa2s = set(sa2_state_map) | set(places_map) | set(u5_map) \
        | set(cal)

    for sa2 in all_sa2s:
        u5 = u5_map.get(sa2)
        places = places_map.get(sa2)
        state = sa2_state_map.get(sa2)
        rate, rule = cal.get(sa2, (None, None))

        if u5 is None or u5 == 0:
            sa2_with_no_pop += 1

        if u5 is not None and rate is not None:
            adj_demand = u5 * rate * ATTENDANCE_FACTOR
        else:
            adj_demand = None

        # Option (a): denominator includes ALL SA2s in state with
        # computable adjusted_demand, regardless of services
        if adj_demand is not None and state:
            state_demand_totals[state] += adj_demand

        if places and places > 0 and u5 is not None and u5 > 0:
            supply_ratio = places / u5
            child_to_place = u5 / places
            demand_supply = (
                adj_demand / places if adj_demand is not None else None
            )
        else:
            if places == 0:
                sa2_with_zero_places += 1
            supply_ratio = None
            child_to_place = None
            demand_supply = None

        sa2_records[sa2] = {
            "u5_pop": u5, "places": places, "state": state,
            "supply_ratio": supply_ratio,
            "child_to_place": child_to_place,
            "adjusted_demand": adj_demand,
            "demand_supply": demand_supply,
            "calibrated_rate": rate,
            "rule_text": rule,
        }

    for sa2, rec in sa2_records.items():
        st = rec["state"]
        ad = rec["adjusted_demand"]
        if ad is not None and st and state_demand_totals.get(st):
            rec["demand_share_state"] = ad / state_demand_totals[st]
        else:
            rec["demand_share_state"] = None

    log(f"  SA2 records: {len(sa2_records):,}")
    log(f"  state demand totals: "
        f"{dict((k, round(v, 0)) for k, v in state_demand_totals.items())}")
    log(f"  SA2s with no u5: {sa2_with_no_pop}; "
        f"with zero places: {sa2_with_zero_places}")

    # --- 3.4 per-service rows --------------------------------------------
    log("3.4 building per-service rows")
    nc = d["services_name_col"]
    select_cols = ["service_id", "sa2_code"]
    if nc:
        select_cols.append(nc)
    cur.execute(
        f"SELECT {', '.join(select_cols)} FROM services WHERE {af}"
    )
    raw = cur.fetchall()
    log(f"  active services: {len(raw):,}")

    today = datetime.now().strftime("%Y-%m-%d")
    rows = []
    null_counts = Counter()

    for r in raw:
        service_id, sa2 = r[0], r[1]
        sname = r[2] if nc and len(r) > 2 else None
        rec = sa2_records.get(sa2, {})

        cc = centres_count_map.get(sa2, 0)
        competing = max(0, cc - 1)
        new_comp = (
            new_comp_map.get(sa2, 0) if new_comp_map is not None
            else None
        )

        row = {
            "service_id": service_id,
            "sa2_code": sa2,
            "sa2_name": name_map.get(sa2) or sname,
            "u5_pop": rec.get("u5_pop"),
            "median_income": income_map.get(sa2),
            "seifa_irsd": seifa_map.get(sa2),
            "unemployment_pct": unemp_map.get(sa2),
            "supply_ratio": rec.get("supply_ratio"),
            "supply_band": None,
            "supply_ratio_4q_change": None,
            "is_deteriorating": None,
            "competing_centres_count": competing,
            "new_competitor_12m": new_comp,
            "ccs_dependency_pct": None,
            "as_of_date": today,
            "created_at": None,
            "updated_at": None,
            "adjusted_demand": rec.get("adjusted_demand"),
            "demand_share_state": rec.get("demand_share_state"),
            "demand_supply": rec.get("demand_supply"),
            "child_to_place": rec.get("child_to_place"),
            "calibrated_rate": rec.get("calibrated_rate"),
            "rule_text": rec.get("rule_text"),
            "calibration_run_at": cal_run_at,
        }
        for k, v in row.items():
            if v is None:
                null_counts[k] += 1
        rows.append(row)

    # --- 3.5 anomaly gate ------------------------------------------------
    log("3.5 anomaly gate")
    n = len(rows)
    if n == 0:
        fail("STAGE 3: zero rows")

    def pct_null(col):
        return null_counts.get(col, 0) / n

    log(f"  rows: {n:,}")
    log("  null pct by column:")
    for c in ALL_COLUMNS:
        nn = null_counts.get(c, 0)
        log(f"    {c:<28} null={nn:>6,} ({pct_null(c) * 100:5.1f}%)")

    if pct_null("u5_pop") > MAX_NULL_PCT_U5_POP:
        fail(f"STAGE 3 GATE: u5_pop null pct "
             f"{pct_null('u5_pop')*100:.2f}% > "
             f"{MAX_NULL_PCT_U5_POP*100:.0f}%")
    if pct_null("calibrated_rate") > MAX_NULL_PCT_CALIBRATED_RATE:
        fail(f"STAGE 3 GATE: calibrated_rate null pct "
             f"{pct_null('calibrated_rate')*100:.2f}%")
    if pct_null("demand_share_state") > \
            MAX_NULL_PCT_DEMAND_SHARE_STATE:
        fail(f"STAGE 3 GATE: demand_share_state null pct "
             f"{pct_null('demand_share_state')*100:.2f}%")
    if pct_null("supply_ratio") > MAX_NULL_PCT_PLACES:
        log(f"  WARNING: supply_ratio null pct "
            f"{pct_null('supply_ratio')*100:.2f}%")

    # Per-ratio distribution (always print for visibility)
    for col in ("supply_ratio", "child_to_place",
                "demand_supply", "demand_share_state"):
        vals = sorted(r[col] for r in rows
                      if r.get(col) is not None)
        if vals:
            log(f"  {col}: n={len(vals):,} min={vals[0]:.4f} "
                f"median={vals[len(vals)//2]:.4f} "
                f"p99={vals[int(len(vals)*0.99)]:.2f} "
                f"max={vals[-1]:.2f}")
    extreme = []
    for r in rows:
        for col in ("supply_ratio", "child_to_place",
                    "demand_supply", "demand_share_state"):
            v = r.get(col)
            if v is not None and v > MAX_RATIO_SANITY:
                extreme.append((r["service_id"],
                                r["sa2_code"], col, v))
    if extreme:
        log(f"  ratios > {MAX_RATIO_SANITY}: {len(extreme)}; top 10:")
        for s_id, sa2, col, v in sorted(
                extreme, key=lambda x: -x[3])[:10]:
            log(f"    service={s_id} sa2={sa2} {col}={v:.2f}")
        fail(f"STAGE 3 GATE: {len(extreme)} ratios > "
             f"{MAX_RATIO_SANITY}")

    log("  sample rows:")
    for r in rows[:3]:
        sample = {k: r[k] for k in (
            "service_id", "sa2_code", "sa2_name", "u5_pop",
            "supply_ratio", "calibrated_rate", "adjusted_demand",
            "demand_share_state", "demand_supply", "child_to_place",
            "competing_centres_count", "rule_text",
        )}
        log(f"    {sample}")

    log("STAGE 3 — GO.")
    return rows


# === STAGE 4: APPLY ======================================================

def stage4_apply(rows, db_path):
    section("STAGE 4 — APPLY (DB write per STD-30)")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(
        "data", f"kintell.db.backup_pre_2_5_1_{ts}"
    )
    log(f"STD-08: copying {db_path} -> {backup_path}")
    shutil.copy2(db_path, backup_path)
    if os.path.getsize(backup_path) != os.path.getsize(db_path):
        fail("STD-08: backup size mismatch")
    log(f"STD-08: backup OK "
        f"({os.path.getsize(backup_path):,} bytes)")

    log("opening RW")
    conn = sqlite3.connect(db_path, isolation_level=None)
    cur = conn.cursor()
    try:
        log("BEGIN IMMEDIATE")
        cur.execute("BEGIN IMMEDIATE")

        cols = column_names(cur, TABLE)
        if len(cols) != EXPECTED_COLUMN_COUNT:
            raise RuntimeError(
                f"column count {len(cols)} != "
                f"{EXPECTED_COLUMN_COUNT}"
            )
        if "demand_share_state" not in cols:
            raise RuntimeError("demand_share_state missing — run "
                               "4.3.5b first")

        prior_n = row_count(cur, TABLE)
        log(f"DELETE FROM {TABLE} (prior {prior_n})")
        cur.execute(f"DELETE FROM {TABLE}")

        insert_cols = [c for c in ALL_COLUMNS
                       if c not in ("created_at", "updated_at")]
        ph = ", ".join("?" for _ in insert_cols)
        cl = ", ".join(insert_cols)
        sql = f"INSERT INTO {TABLE} ({cl}) VALUES ({ph})"
        batch = [tuple(r[c] for c in insert_cols) for r in rows]
        log(f"INSERT {len(rows):,}")
        cur.executemany(sql, batch)

        new_n = row_count(cur, TABLE)
        if new_n != len(rows):
            raise RuntimeError(
                f"post-INSERT count {new_n} != {len(rows)}"
            )

        before_json = json.dumps({"prior_rows": prior_n})
        after_json = json.dumps({
            "inserted_rows": new_n,
            "backup": os.path.basename(backup_path),
            "attendance_factor": ATTENDANCE_FACTOR,
        })
        reason = (
            "Layer 2.5 sub-pass 2.5.1: full populate of "
            "service_catchment_cache. Per-SA2 calibrated rate + "
            "rule_text from catchment_calibration.py; per-SA2 "
            "ratios; demand_share_state per option (a) (state-wide "
            "denominator over all SA2s, not only service-bearing). "
            "Best-effort columns NULL where source absent. "
            "Idempotent DELETE+INSERT."
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
    try:
        n = row_count(cur, TABLE)
        if n != result["row_count"]:
            fail(f"row count drift: {n} != {result['row_count']}")
        log(f"  row count OK ({n:,})")

        cur.execute(
            f"SELECT COUNT(*) FROM {TABLE} "
            f"WHERE service_id IS NULL OR sa2_code IS NULL"
        )
        bad = cur.fetchone()[0]
        if bad > 0:
            fail(f"{bad} rows have NULL key columns")

        cur.execute(
            f"SELECT MIN(calibrated_rate), MAX(calibrated_rate), "
            f"AVG(calibrated_rate) FROM {TABLE} "
            f"WHERE calibrated_rate IS NOT NULL"
        )
        mn, mx, av = cur.fetchone()
        log(f"  calibrated_rate min/max/avg: "
            f"{mn}, {mx}, {av:.4f}" if av else f"  cal: {mn}/{mx}")
        if mn is not None and (mn < RATE_MIN or mx > RATE_MAX):
            fail("calibrated_rate out of range")

        cur.execute(
            f"SELECT s.state, ROUND(SUM(c.demand_share_state), 3) "
            f"FROM {TABLE} c JOIN services s "
            f"ON c.service_id = s.service_id "
            f"GROUP BY s.state ORDER BY s.state"
        )
        log("  demand_share_state per state (services-level sum, "
            "≤ 1 by construction since cache rows broadcast):")
        for st, s in cur.fetchall():
            log(f"    {st}: {s}")

        cur.execute(
            "SELECT audit_id, actor, action, subject_type, "
            "subject_id, occurred_at FROM audit_log "
            "WHERE audit_id = ?",
            (result["audit_id"],),
        )
        row = cur.fetchone()
        if not row:
            fail(f"audit_log row {result['audit_id']} missing")
        log(f"  audit_log OK: {row}")
    finally:
        conn.close()


def main():
    print("=" * 72)
    print("populate_service_catchment_cache.py v2")
    print(f"started      : {datetime.now().isoformat()}")
    print(f"target db    : {os.path.abspath(DB_PATH)}")
    print(f"attendance_f : {ATTENDANCE_FACTOR}")
    print("=" * 72)

    if not os.path.exists(DB_PATH):
        fail(f"DB not found at {DB_PATH}")

    ro_uri = f"file:{DB_PATH}?mode=ro"
    ro = sqlite3.connect(ro_uri, uri=True)
    try:
        d = stage1_probe(ro)
        smoke = stage2_calibration_smoketest(ro, d)
        rows = stage3_dry_run(ro, d, smoke)
    finally:
        ro.close()

    std13_self_check()
    result = stage4_apply(rows, DB_PATH)
    post_validate(result)

    print()
    print("=" * 72)
    print("LAYER 2.5 SUB-PASS 2.5.1 — SUCCESS")
    print(f"rows populated : {result['row_count']:,}")
    print(f"audit_id       : {result['audit_id']}")
    print(f"backup         : {result['backup_path']}")
    print(f"finished       : {datetime.now().isoformat()}")
    print("=" * 72)


if __name__ == "__main__":
    main()
