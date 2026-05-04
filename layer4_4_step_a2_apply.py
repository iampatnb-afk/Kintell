r"""
layer4_4_step_a2_apply.py — A2 NES share ingest (v3).

v3 (2026-05-04, post-B2-discovery): UNIT FIX.
  v2 stored NES as fraction (0-1), e.g. 0.31. This was inconsistent with
  the project convention for census_*_pct metrics (LFP family stores
  percentage 0-100). When registered for centre-page render with
  value_format='percent', a fraction-stored value would display as
  "0.31%" instead of "31%".

  v3 stores NES as percentage (0-100). The calibration's existing
  fraction thresholds (>=0.30, <=0.05) are now satisfied by the wire
  (populate_service_catchment_cache.py) dividing by 100 on read before
  passing to calibrate_participation_rate.

  Net effect on calibrated_rate values: identical (same fraction reaches
  the calibration). The change is purely about storage convention.

Reads from abs_data/2021_TSP_SA2_for_AUS_short-header.zip:
  T10A: Uses_Engl_only_C{11,16,21}_P
  T10B: Tot_C{11,16,21}_P, Lang_used_home_NS_C{11,16,21}_P

Derives NES percentage per SA2 per Census year (2011, 2016, 2021):

    nes_pct = (tot - uses_engl_only - lang_used_home_ns) / tot * 100

Persists into abs_sa2_education_employment_annual under metric_name
'census_nes_share_pct'. v3 stores PERCENTAGE — consistent with
census_lfp_*_pct family.

STD-30 pre-mutation discipline:
  - Pre-state inventory + idempotency check
  - Backup before write
  - audit_log row per DEC-62 schema
  - Post-state verification

Usage:
    python layer4_4_step_a2_apply.py             # dry-run (default)
    python layer4_4_step_a2_apply.py --apply     # write
    python layer4_4_step_a2_apply.py --replace --apply   # replace existing rows

Run from repo root.
"""

import io
import json
import re
import shutil
import sqlite3
import sys
import warnings
import zipfile
from datetime import datetime
from pathlib import Path

DB_PATH = Path("data") / "kintell.db"
ZIP_PATH = Path("abs_data") / "2021_TSP_SA2_for_AUS_short-header.zip"
TARGET_TABLE = "abs_sa2_education_employment_annual"
METRIC_NAME = "census_nes_share_pct"
ACTOR = "layer4_4_step_a2_apply"
ACTION = "census_nes_share_ingest_v3"

T10A_NAME = "2021 Census TSP Statistical Area 2 for AUS/2021Census_T10A_AUST_SA2.csv"
T10B_NAME = "2021 Census TSP Statistical Area 2 for AUS/2021Census_T10B_AUST_SA2.csv"

CENSUS_YEARS = [2011, 2016, 2021]
ENGL_COL  = {2011: "Uses_Engl_only_C11_P",  2016: "Uses_Engl_only_C16_P",  2021: "Uses_Engl_only_C21_P"}
LNS_COL   = {2011: "Lang_used_home_NS_C11_P", 2016: "Lang_used_home_NS_C16_P", 2021: "Lang_used_home_NS_C21_P"}
TOT_COL   = {2011: "Tot_C11_P",            2016: "Tot_C16_P",            2021: "Tot_C21_P"}

VERIFY_SA2 = [
    ("211011251", "Bayswater Vic"),
    ("118011341", "Bondi Junction-Waverly NSW"),
    ("506031124", "Bentley-Wilson-St James WA"),
]


def section(title):
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def parse_args():
    return {
        "apply": "--apply" in sys.argv,
        "replace": "--replace" in sys.argv,
    }


def preflight():
    if not DB_PATH.exists():
        print(f"ERROR: {DB_PATH} not found. Run from repo root.")
        sys.exit(1)
    if not ZIP_PATH.exists():
        print(f"ERROR: {ZIP_PATH} not found.")
        sys.exit(1)
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    tabs = {r[0] for r in cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()}
    for need in ("audit_log", TARGET_TABLE):
        if need not in tabs:
            print(f"ERROR: required table '{need}' missing.")
            con.close()
            sys.exit(1)
    con.close()


def read_source():
    try:
        import pandas as pd
    except ImportError:
        print("ERROR: pandas required.")
        sys.exit(1)

    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        for nm in (T10A_NAME, T10B_NAME):
            if nm not in z.namelist():
                print(f"ERROR: expected CSV not found in zip: {nm}")
                sys.exit(2)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            t10a = pd.read_csv(io.BytesIO(z.read(T10A_NAME)), dtype=str)
            t10b = pd.read_csv(io.BytesIO(z.read(T10B_NAME)), dtype=str)

    for df, label in [(t10a, "T10A"), (t10b, "T10B")]:
        df.columns = [str(c).strip() for c in df.columns]
        if "SA2_CODE_2021" not in df.columns:
            print(f"ERROR: SA2_CODE_2021 column missing in {label}.")
            sys.exit(2)
        df["SA2_CODE_2021"] = df["SA2_CODE_2021"].astype(str).str.strip()

    print(f"  T10A: {len(t10a):,} rows, {len(t10a.columns)} cols")
    print(f"  T10B: {len(t10b):,} rows, {len(t10b.columns)} cols")

    missing = []
    for yr in CENSUS_YEARS:
        if ENGL_COL[yr] not in t10a.columns:
            missing.append(f"T10A.{ENGL_COL[yr]}")
        if TOT_COL[yr] not in t10b.columns:
            missing.append(f"T10B.{TOT_COL[yr]}")
        if LNS_COL[yr] not in t10b.columns:
            missing.append(f"T10B.{LNS_COL[yr]}")
    if missing:
        print(f"ERROR: required columns missing: {missing}")
        sys.exit(2)

    sa2_re = re.compile(r"^\d{9}$")
    t10a_sa2 = t10a[t10a["SA2_CODE_2021"].str.match(sa2_re)].copy()
    t10b_sa2 = t10b[t10b["SA2_CODE_2021"].str.match(sa2_re)].copy()
    print(f"  T10A SA2-filtered: {len(t10a_sa2):,}")
    print(f"  T10B SA2-filtered: {len(t10b_sa2):,}")

    t10a_idx = t10a_sa2.set_index("SA2_CODE_2021")
    t10b_idx = t10b_sa2.set_index("SA2_CODE_2021")

    sa2s = sorted(set(t10a_idx.index) & set(t10b_idx.index))
    print(f"  SA2s present in both: {len(sa2s):,}")

    def to_int(v):
        try:
            return int(v) if v not in ("", "..", "np", None) else None
        except (ValueError, TypeError):
            return None

    result = {}
    for sa2 in sa2s:
        per_year = {}
        for yr in CENSUS_YEARS:
            tot = to_int(t10b_idx.at[sa2, TOT_COL[yr]])
            eng = to_int(t10a_idx.at[sa2, ENGL_COL[yr]])
            lns = to_int(t10b_idx.at[sa2, LNS_COL[yr]])
            per_year[yr] = (tot, eng, lns)
        result[sa2] = per_year
    return result


def derive_nes(source):
    """Compute NES percentage. Returns list of (sa2, year, percentage) tuples."""
    rows = []
    skipped_zero_total = 0
    skipped_null = 0
    clamped_negative = 0
    for sa2, per_year in source.items():
        for yr, (tot, eng, lns) in per_year.items():
            if tot is None or eng is None or lns is None:
                skipped_null += 1
                continue
            if tot == 0:
                skipped_zero_total += 1
                continue
            nes_count = tot - eng - lns
            if nes_count < 0:
                clamped_negative += 1
                nes_count = 0
            pct = (nes_count / tot) * 100.0
            pct = max(0.0, min(100.0, pct))
            rows.append((sa2, yr, round(pct, 4)))

    print(f"  Rows derived: {len(rows):,}")
    print(f"  Skipped — null values:    {skipped_null:,}")
    print(f"  Skipped — total = 0:      {skipped_zero_total:,}")
    print(f"  Clamped — neg numerator:  {clamped_negative:,} (DEC-59)")
    return rows


def sanity_checks(source, rows):
    if not rows:
        print("  ERROR: no rows derived.")
        sys.exit(3)

    pcts = [r[2] for r in rows]
    in_range = sum(1 for p in pcts if 0 <= p <= 100)
    out_range = len(pcts) - in_range
    print(f"  Values in [0, 100]: {in_range:,} / {len(pcts):,} ({out_range} outside)")

    print("\n  National NES share by year (weighted):")
    natl_by_year = {}
    for yr in CENSUS_YEARS:
        tot_sum = 0
        nes_sum = 0
        for sa2, per_year in source.items():
            tot, eng, lns = per_year.get(yr, (None, None, None))
            if tot is None or eng is None or lns is None or tot <= 0:
                continue
            nes = max(0, tot - eng - lns)
            tot_sum += tot
            nes_sum += nes
        nat_pct = (nes_sum / tot_sum) * 100.0 if tot_sum else 0
        natl_by_year[yr] = nat_pct
        flag = ""
        if yr == 2021:
            if 20.0 <= nat_pct <= 25.0:
                flag = "  [in published 22-24% band]"
            else:
                flag = f"  [WARN: expected 20-25, got {nat_pct:.2f}]"
        print(f"    {yr}: {nat_pct:.2f}%{flag}")

    by_year = {}
    for _, yr, _ in rows:
        by_year[yr] = by_year.get(yr, 0) + 1
    print(f"\n  Rows by year: {sorted(by_year.items())}")

    print("\n  Verification SA2s (NES % by year):")
    by_sa2_year = {(s, y): p for s, y, p in rows}
    for sa2_code, name in VERIFY_SA2:
        vals = [(yr, by_sa2_year.get((sa2_code, yr))) for yr in CENSUS_YEARS]
        cells = " ".join(
            f"{yr}={v:.2f}%" if v is not None else f"{yr}=NA"
            for yr, v in vals
        )
        print(f"    {sa2_code} ({name}): {cells}")

    return {
        "rows_total": len(rows),
        "rows_in_range": in_range,
        "national_2011_pct": round(natl_by_year[2011], 4),
        "national_2016_pct": round(natl_by_year[2016], 4),
        "national_2021_pct": round(natl_by_year[2021], 4),
        "by_year": by_year,
    }


def pre_state(con):
    cur = con.cursor()
    existing = cur.execute(
        f'SELECT COUNT(*) FROM "{TARGET_TABLE}" WHERE metric_name = ?',
        (METRIC_NAME,),
    ).fetchone()[0]
    audit_id = cur.execute(
        "SELECT COALESCE(MAX(audit_id), 0) FROM audit_log"
    ).fetchone()[0]
    table_count = cur.execute(f'SELECT COUNT(*) FROM "{TARGET_TABLE}"').fetchone()[0]
    return {"existing_rows_for_metric": existing,
            "max_audit_id": audit_id,
            "target_table_rows": table_count}


def backup_db():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.parent / f"pre_layer4_4_step_a2_v3_{timestamp}.db"
    print(f"  Backup: copying {DB_PATH} -> {backup_path}")
    shutil.copy2(DB_PATH, backup_path)
    size_mb = backup_path.stat().st_size / (1024 * 1024)
    print(f"  Backup size: {size_mb:.1f} MB")
    return backup_path


def write_rows(con, rows, replace=False):
    cur = con.cursor()
    if replace:
        n = cur.execute(
            f'DELETE FROM "{TARGET_TABLE}" WHERE metric_name = ?',
            (METRIC_NAME,),
        ).rowcount
        print(f"  Deleted {n:,} existing rows for metric_name='{METRIC_NAME}'")
    cur.executemany(
        f'INSERT INTO "{TARGET_TABLE}" (sa2_code, year, metric_name, value) '
        f"VALUES (?, ?, ?, ?)",
        [(sa2, yr, METRIC_NAME, val) for sa2, yr, val in rows],
    )
    return cur.rowcount


def write_audit_log(con, before, after):
    cur = con.cursor()
    cur.execute(
        "INSERT INTO audit_log "
        "(actor, action, subject_type, subject_id, before_json, after_json, reason, occurred_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))",
        (
            ACTOR,
            ACTION,
            TARGET_TABLE,
            0,
            json.dumps(before),
            json.dumps(after),
            "A2 NES share ingest (v3) — UNIT FIX. Stores percentage (0-100) "
            "matching census_*_pct convention. Wire (populate_service_catchment_cache.py) "
            "divides by 100 on read before passing to calibrate_participation_rate "
            "(which keeps its fraction thresholds per STD-34 lock). "
            "Formula: ((Tot - Uses_Engl_only - Lang_used_home_NS) / Tot) * 100.",
        ),
    )
    new_id = cur.execute("SELECT MAX(audit_id) FROM audit_log").fetchone()[0]
    return new_id


def post_state(con):
    cur = con.cursor()
    rows = cur.execute(
        f'SELECT COUNT(*), MIN(value), MAX(value), AVG(value) '
        f'FROM "{TARGET_TABLE}" WHERE metric_name = ?',
        (METRIC_NAME,),
    ).fetchone()
    print(f"  Rows for metric: {rows[0]:,}")
    print(f"  value range:     [{rows[1]:.2f}%, {rows[2]:.2f}%]")
    print(f"  value mean:      {rows[3]:.2f}%")
    print()
    print("  Verification SA2 spot-check (2021):")
    for sa2_code, name in VERIFY_SA2:
        v = cur.execute(
            f'SELECT value FROM "{TARGET_TABLE}" '
            f"WHERE sa2_code = ? AND metric_name = ? AND year = 2021",
            (sa2_code, METRIC_NAME),
        ).fetchone()
        v_str = f"{v[0]:.2f}%" if v else "MISSING"
        print(f"    {sa2_code} ({name}): {v_str}")


def main():
    args = parse_args()
    apply_mode = args["apply"]
    replace = args["replace"]

    print(f"DB:        {DB_PATH}")
    print(f"Source:    {ZIP_PATH}")
    print(f"Target:    {TARGET_TABLE} (metric_name='{METRIC_NAME}')")
    print(f"Mode:      {'APPLY' if apply_mode else 'DRY-RUN'}"
          f"{'  REPLACE' if replace else ''}")
    print(f"Formula:   nes_pct = ((Tot - Uses_Engl_only - Lang_used_home_NS) / Tot) * 100")
    print(f"Storage:   PERCENTAGE (0-100) — v3 unit fix")

    preflight()

    con = sqlite3.connect(DB_PATH)
    before = pre_state(con)
    section("Pre-state")
    for k, v in before.items():
        print(f"  {k}: {v:,}" if isinstance(v, int) else f"  {k}: {v}")

    if before["existing_rows_for_metric"] > 0 and not replace:
        print()
        print(f"  ERROR: {before['existing_rows_for_metric']} rows already exist "
              f"for metric_name='{METRIC_NAME}'.")
        print(f"  Re-run with --replace to overwrite (this is the v2->v3 unit-fix path).")
        con.close()
        sys.exit(4)

    section("Reading source")
    source = read_source()

    section("Deriving NES percentages")
    rows = derive_nes(source)

    section("Sanity checks")
    sanity = sanity_checks(source, rows)

    if not apply_mode:
        section("DRY-RUN — no DB mutation")
        print(f"  Would insert: {len(rows):,} rows into {TARGET_TABLE}")
        print(f"  Would write audit_log row (next audit_id: {before['max_audit_id'] + 1})")
        print(f"  Would back up DB before write")
        print()
        print(f"  To proceed: re-run with --apply"
              f"{'' if not replace else ' (replace mode active)'}")
        con.close()
        return

    section("Backup")
    backup_path = backup_db()

    section("Writing")
    inserted = write_rows(con, rows, replace=replace)
    print(f"  Inserted: {inserted:,} rows")

    after_payload = {
        "rows_inserted": inserted,
        "sa2_count": len({r[0] for r in rows}),
        "years": sorted({r[1] for r in rows}),
        "national_2011_pct": sanity["national_2011_pct"],
        "national_2016_pct": sanity["national_2016_pct"],
        "national_2021_pct": sanity["national_2021_pct"],
        "backup": str(backup_path),
        "replaced": replace,
        "unit": "percentage_0_to_100",
    }
    new_audit_id = write_audit_log(con, before, after_payload)
    print(f"  audit_log row written: audit_id={new_audit_id}")

    con.commit()

    section("Post-state")
    post_state(con)

    con.close()
    print()
    print("APPLIED.")


if __name__ == "__main__":
    main()
