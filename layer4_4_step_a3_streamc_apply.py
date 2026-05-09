r"""
layer4_4_step_a3_streamc_apply.py — A3 + Stream C bundle ingest (v1).

Ingests four SA2-level metrics into `abs_sa2_education_employment_annual`
(long-format), bundling A3 (parent-cohort) with Stream C (marital +
fertility) per a3_streamc_design.md ratified 2026-05-10.

Sources:
  - abs_data/Population and People Database.xlsx (sheet "Table 1") — ERP
  - abs_data/2021_TSP_SA2_for_AUS_short-header.zip — Census TSP T05 + T07

Metrics (all stored as percentage 0-100 per DEC-78,
band cohort state_x_remoteness, neutral framing, no calibration):

  1. erp_parent_cohort_25_44_share_pct
       Annual cadence (2011, 2016, 2018-2024).
       Source: ERP "Persons - 25-29..40-44 years (no.)" (cols 89,90,91,92 / 121).
       Formula: sum(persons 25_29..40_44) / total_persons * 100
       National 2021 reference: ~28-30%

  2. census_partnered_25_44_share_pct
       Census 3-point (2011, 2016, 2021).
       Source: T05 Mar_RegM_P + Mar_DFM_P over ages 25_29..40_44, vs Tot_P.
       National 2021 reference: ~58-65%

  3. census_women_35_44_with_child_share_pct
       Census 3-point.
       Source: T07 women 35_39 + 40_44.
       Formula: (Tot - NCB_0 - NCB_NS) / (Tot - NCB_NS) * 100
       (NS excluded from both numerator + denominator per A10 NES precedent.)
       National 2021 reference: ~75-82%
       Display label: "Share of women aged 35 to 44 with at least one child"

  4. census_women_25_34_with_child_share_pct
       Census 3-point.
       Same formula but ages 25_29 + 30_34.
       National 2021 reference: ~50-60% (under-cohort, more childcare-relevant)
       Display label: "Share of women aged 25 to 34 with at least one child"

STD-30 pre-mutation discipline: pre-state inventory + idempotency check
per metric, single backup before write, 4 audit_log rows per DEC-62 schema,
post-state verification across 4 verify SA2s.

Usage:
    python layer4_4_step_a3_streamc_apply.py             # dry-run (default)
    python layer4_4_step_a3_streamc_apply.py --apply     # write
    python layer4_4_step_a3_streamc_apply.py --replace --apply

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
ERP_WORKBOOK = Path("abs_data") / "Population and People Database.xlsx"
TARGET_TABLE = "abs_sa2_education_employment_annual"
ACTOR = "layer4_4_step_a3_streamc_apply"

# ─────────────────────────────────────────────────────────────────────
# Source files in the TSP zip
# ─────────────────────────────────────────────────────────────────────
ZIP_PREFIX = "2021 Census TSP Statistical Area 2 for AUS/"
T05_NAMES = [f"{ZIP_PREFIX}2021Census_T05{ab}_AUST_SA2.csv" for ab in "ABC"]
T07_NAMES = [f"{ZIP_PREFIX}2021Census_T07{ab}_AUST_SA2.csv" for ab in "ABC"]

CENSUS_YEARS = [2011, 2016, 2021]
PARENT_AGE_BANDS = ["25_29", "30_34", "35_39", "40_44"]
WOMEN_3544_BANDS = ["35_39", "40_44"]
WOMEN_2534_BANDS = ["25_29", "30_34"]

# ─────────────────────────────────────────────────────────────────────
# ERP column map (col indices in sheet "Table 1") — confirmed by probe.
# Layer2 step 6 already uses col 0 (sa2), 2 (year), 121 (total_persons).
# We add cols 89..92 for Persons 25-44 sum.
# ─────────────────────────────────────────────────────────────────────
ERP_SHEET = "Table 1"
ERP_DATA_START_ROW = 8                 # row 7 is header; row 8 begins data
ERP_COL_SA2 = 0
ERP_COL_YEAR = 2
ERP_COL_TOTAL_PERSONS = 3              # "Estimated resident population - year ended 30 June" (all ages)
                                       # NOT 121 (which is fertility rate decimal — original step6 diag mis-guessed)
ERP_COLS_PERSONS_25_44 = [89, 90, 91, 92]   # Persons 25-29, 30-34, 35-39, 40-44 (no.)
ERP_NULL_MARKERS = {"", "-", "..", "np", None}

# ─────────────────────────────────────────────────────────────────────
# Verification SA2s — same as A10
# ─────────────────────────────────────────────────────────────────────
VERIFY_SA2 = [
    ("211011251", "Bayswater Vic"),
    ("118011341", "Bondi Junction-Waverly NSW"),
    ("506031124", "Bentley-Wilson-St James WA"),
    ("702041063", "Outback NT"),
]

# ─────────────────────────────────────────────────────────────────────
# Metric definitions (drives generic ingest pipeline)
# ─────────────────────────────────────────────────────────────────────
METRICS = [
    {
        "name": "erp_parent_cohort_25_44_share_pct",
        "action": "erp_parent_cohort_25_44_share_ingest_v1",
        "national_2021_band": (26.0, 32.0),
        "reason": (
            "A3 parent-cohort 25-44 share ingest (v1). Stores percentage "
            "(0-100). Formula: sum(persons 25_29..40_44) / total_persons * 100. "
            "Source: ABS ERP 'Population and People Database.xlsx' sheet "
            "'Table 1' cols 89,90,91,92 (Persons 5-year bands) / col 121 "
            "(total_persons all ages). Annual cadence — full available year "
            "set in workbook (typically 2011, 2016, 2018-2024)."
        ),
    },
    {
        "name": "census_partnered_25_44_share_pct",
        "action": "census_partnered_25_44_share_ingest_v1",
        "national_2021_band": (55.0, 68.0),
        "reason": (
            "Stream C partnered 25-44 share ingest (v1). Stores percentage "
            "(0-100). Formula: sum(Mar_RegM_P + Mar_DFM_P over 25_29..40_44) "
            "/ sum(Tot_P over 25_29..40_44) * 100. Sharp 25-44 window matches "
            "parent cohort. NS excluded (TSP T05 short-header does not break "
            "out separated/divorced/widowed; complement is 'never married + "
            "sep + div + wid' rather than just never-married). "
            "Source: ABS Census 2021 TSP T05A/B/C."
        ),
    },
    {
        "name": "census_women_35_44_with_child_share_pct",
        "action": "census_women_35_44_with_child_share_ingest_v1",
        "national_2021_band": (72.0, 85.0),
        "reason": (
            "Stream C women-35-44 with at least one child share ingest (v1). "
            "Stores percentage (0-100). Formula: (Tot - NCB_0 - NCB_NS) / "
            "(Tot - NCB_NS) * 100 over ages 35_39 + 40_44, T07 (women only, "
            "AP = aged persons female). NS excluded from both numerator and "
            "denominator per NES/ATSI precedent. Reads as 'completed-fertility "
            "proxy': by 35+ Australian women's CEFB profile is ~95%+ stable. "
            "Source: ABS Census 2021 TSP T07A/B/C."
        ),
    },
    {
        "name": "census_women_25_34_with_child_share_pct",
        "action": "census_women_25_34_with_child_share_ingest_v1",
        "national_2021_band": (38.0, 55.0),
        "reason": (
            "Stream C women-25-34 with at least one child share ingest (v1). "
            "Stores percentage (0-100). Formula: (Tot - NCB_0 - NCB_NS) / "
            "(Tot - NCB_NS) * 100 over ages 25_29 + 30_34, T07. "
            "Under-cohort to the 35-44 fertility proxy — Patrick rationale: "
            "more directly indexed to active childcare years than 35-44, "
            "which 'feels old' for childcare relevance. "
            "Source: ABS Census 2021 TSP T07A/B/C."
        ),
    },
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


# =====================================================================
# Preflight
# =====================================================================
def preflight():
    if not DB_PATH.exists():
        print(f"ERROR: {DB_PATH} not found. Run from repo root.")
        sys.exit(1)
    if not ZIP_PATH.exists():
        print(f"ERROR: {ZIP_PATH} not found.")
        sys.exit(1)
    if not ERP_WORKBOOK.exists():
        print(f"ERROR: {ERP_WORKBOOK} not found.")
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


# =====================================================================
# Helpers
# =====================================================================
def to_int(v):
    if v is None:
        return None
    s = str(v).strip()
    if s in ERP_NULL_MARKERS:
        return None
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return None


# =====================================================================
# TSP zip readers (T05 + T07)
# =====================================================================
def _read_csv_from_zip(z, name):
    import pandas as pd
    if name not in z.namelist():
        print(f"ERROR: expected CSV not found in zip: {name}")
        sys.exit(2)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        df = pd.read_csv(io.BytesIO(z.read(name)), dtype=str, low_memory=False)
    df.columns = [str(c).strip() for c in df.columns]
    if "SA2_CODE_2021" not in df.columns:
        print(f"ERROR: SA2_CODE_2021 missing in {name}.")
        sys.exit(2)
    df["SA2_CODE_2021"] = df["SA2_CODE_2021"].astype(str).str.strip()
    sa2_re = re.compile(r"^\d{9}$")
    df = df[df["SA2_CODE_2021"].str.match(sa2_re)].copy()
    return df


def _merge_tsp_files(z, names, label):
    """Read N TSP CSVs and merge horizontally on SA2_CODE_2021."""
    dfs = [_read_csv_from_zip(z, n) for n in names]
    merged = dfs[0]
    for nxt in dfs[1:]:
        merged = merged.merge(nxt, on="SA2_CODE_2021", how="inner",
                              suffixes=("", "_DROP"))
        for col in list(merged.columns):
            if col.endswith("_DROP"):
                merged = merged.drop(columns=[col])
    print(f"  {label} merged: {len(merged):,} rows × {len(merged.columns)} cols")
    return merged.set_index("SA2_CODE_2021")


def read_t05(z):
    return _merge_tsp_files(z, T05_NAMES, "T05")


def read_t07(z):
    return _merge_tsp_files(z, T07_NAMES, "T07")


def _verify_t05_columns(t05):
    """Halt early if any required T05 column is missing."""
    missing = []
    for yr_short in ("11", "16", "21"):
        for age in PARENT_AGE_BANDS:
            for cat in ("Mar_RegM", "Mar_DFM"):
                col = f"C{yr_short}_{age}_{cat}_P"
                if col not in t05.columns:
                    missing.append(col)
            tot_col = f"C{yr_short}_{age}_Tot_P"
            if tot_col not in t05.columns:
                missing.append(tot_col)
    if missing:
        print(f"ERROR: T05 missing {len(missing)} expected columns. First 6: {missing[:6]}")
        sys.exit(2)
    print(f"  T05 column verify: all {3 * len(PARENT_AGE_BANDS) * 3} required cols present.")


def _verify_t07_columns(t07):
    """Halt early if any required T07 column is missing."""
    needed_ages = sorted(set(WOMEN_3544_BANDS + WOMEN_2534_BANDS))
    missing = []
    for yr_short in ("11", "16", "21"):
        for age in needed_ages:
            # T07 uses _AP_{age}_NCB_{count}; we need NCB_0, NCB_NS, Tot.
            for var in (f"NCB_0", f"NCB_NS"):
                col = f"C{yr_short}_AP_{age}_{var}"
                if col not in t07.columns:
                    missing.append(col)
            tot_col = f"C{yr_short}_AP_{age}_Tot"
            if tot_col not in t07.columns:
                missing.append(tot_col)
    if missing:
        print(f"ERROR: T07 missing {len(missing)} expected columns. First 6: {missing[:6]}")
        sys.exit(2)
    print(f"  T07 column verify: all {3 * len(needed_ages) * 3} required cols present.")


# =====================================================================
# T05 marital derivation — partnered 25-44 share
# =====================================================================
YR_SHORT = {2011: "11", 2016: "16", 2021: "21"}


def derive_partnered_25_44(t05):
    rows = []
    skipped_null = 0
    skipped_zero_total = 0
    source = {}
    for sa2 in t05.index:
        per_year = {}
        for yr in CENSUS_YEARS:
            yshort = YR_SHORT[yr]
            partnered = 0
            tot = 0
            null_cell = False
            for age in PARENT_AGE_BANDS:
                regm = to_int(t05.at[sa2, f"C{yshort}_{age}_Mar_RegM_P"])
                dfm  = to_int(t05.at[sa2, f"C{yshort}_{age}_Mar_DFM_P"])
                t    = to_int(t05.at[sa2, f"C{yshort}_{age}_Tot_P"])
                if regm is None or dfm is None or t is None:
                    null_cell = True
                    break
                partnered += regm + dfm
                tot += t
            per_year[yr] = (partnered if not null_cell else None,
                            tot if not null_cell else None)
            if null_cell:
                skipped_null += 1
                continue
            if tot == 0:
                skipped_zero_total += 1
                continue
            pct = max(0.0, min(100.0, (partnered / tot) * 100.0))
            rows.append((sa2, yr, round(pct, 4)))
        source[sa2] = per_year
    print(f"  partnered_25_44 rows: {len(rows):,}  null-skip: {skipped_null:,}  "
          f"zero-tot-skip: {skipped_zero_total:,}")
    return rows, source


# =====================================================================
# T07 fertility derivation — women X-Y with at least one child share
# =====================================================================
def _derive_women_with_child_share(t07, age_bands, label):
    rows = []
    skipped_null = 0
    skipped_zero_denom = 0
    source = {}
    for sa2 in t07.index:
        per_year = {}
        for yr in CENSUS_YEARS:
            yshort = YR_SHORT[yr]
            ncb0_sum = 0
            ncbns_sum = 0
            tot_sum = 0
            null_cell = False
            for age in age_bands:
                ncb0 = to_int(t07.at[sa2, f"C{yshort}_AP_{age}_NCB_0"])
                ncbns = to_int(t07.at[sa2, f"C{yshort}_AP_{age}_NCB_NS"])
                t = to_int(t07.at[sa2, f"C{yshort}_AP_{age}_Tot"])
                if ncb0 is None or ncbns is None or t is None:
                    null_cell = True
                    break
                ncb0_sum += ncb0
                ncbns_sum += ncbns
                tot_sum += t
            denom = (tot_sum - ncbns_sum) if not null_cell else None
            num = (tot_sum - ncb0_sum - ncbns_sum) if not null_cell else None
            per_year[yr] = (num, denom)
            if null_cell:
                skipped_null += 1
                continue
            if denom is None or denom <= 0:
                skipped_zero_denom += 1
                continue
            pct = max(0.0, min(100.0, (num / denom) * 100.0))
            rows.append((sa2, yr, round(pct, 4)))
        source[sa2] = per_year
    print(f"  women_with_child {label} rows: {len(rows):,}  "
          f"null-skip: {skipped_null:,}  zero-denom-skip: {skipped_zero_denom:,}")
    return rows, source


def derive_women_35_44_with_child(t07):
    return _derive_women_with_child_share(t07, WOMEN_3544_BANDS, "35-44")


def derive_women_25_34_with_child(t07):
    return _derive_women_with_child_share(t07, WOMEN_2534_BANDS, "25-34")


# Sanity bands for women-with-child sanity_check (per metric)
SANITY_W3544 = (72.0, 85.0)
SANITY_W2534 = (38.0, 55.0)


# =====================================================================
# ERP derivation — parent cohort 25-44 share (annual)
# =====================================================================
def read_erp_parent_cohort():
    """Read ERP workbook Table 1; per (sa2, year) compute (persons_25_44, total_persons)."""
    import openpyxl
    wb = openpyxl.load_workbook(ERP_WORKBOOK, read_only=True, data_only=True)
    ws = wb[ERP_SHEET]

    sa2_re = re.compile(r"^\d{9}$")
    out = {}  # (sa2, year) -> (persons_25_44, total_persons)
    skipped_no_sa2 = 0
    skipped_invalid_sa2 = 0

    for row_idx, row in enumerate(ws.iter_rows(values_only=True), start=1):
        if row_idx < ERP_DATA_START_ROW:
            continue
        if len(row) <= max(ERP_COL_TOTAL_PERSONS, *ERP_COLS_PERSONS_25_44):
            continue

        sa2_cell = row[ERP_COL_SA2]
        if sa2_cell is None:
            skipped_no_sa2 += 1
            continue
        sa2 = str(sa2_cell).strip()
        if not sa2_re.match(sa2):
            skipped_invalid_sa2 += 1
            continue

        year_raw = row[ERP_COL_YEAR]
        year = to_int(year_raw)
        if year is None:
            continue

        # Sum 4 age cols; if any is null, skip this SA2-year.
        persons_25_44 = 0
        had_null = False
        for ci in ERP_COLS_PERSONS_25_44:
            v = to_int(row[ci])
            if v is None:
                had_null = True
                break
            persons_25_44 += v
        if had_null:
            continue

        tot = to_int(row[ERP_COL_TOTAL_PERSONS])
        if tot is None or tot <= 0:
            continue

        out[(sa2, year)] = (persons_25_44, tot)

    print(f"  ERP rows extracted: {len(out):,}  "
          f"skipped-no-sa2: {skipped_no_sa2:,}  invalid-sa2: {skipped_invalid_sa2:,}")
    years_seen = sorted({y for (_s, y) in out.keys()})
    print(f"  ERP years: {years_seen}")
    return out


def derive_parent_cohort(erp):
    rows = []
    source = {}
    for (sa2, year), (p25_44, tot) in erp.items():
        if tot <= 0:
            continue
        pct = max(0.0, min(100.0, (p25_44 / tot) * 100.0))
        rows.append((sa2, year, round(pct, 4)))
        source.setdefault(sa2, {})[year] = (p25_44, tot)
    print(f"  parent_cohort_25_44 rows: {len(rows):,}")
    return rows, source


# =====================================================================
# Sanity checks
# =====================================================================
def _print_verify(rows, label, years):
    by_sa2_year = {(s, y): v for s, y, v in rows}
    print(f"\n  Verification SA2s ({label} by year):")
    for sa2, name in VERIFY_SA2:
        cells = " ".join(
            f"{yr}={by_sa2_year[(sa2, yr)]:.2f}%"
            if (sa2, yr) in by_sa2_year else f"{yr}=NA"
            for yr in years
        )
        print(f"    {sa2} ({name}): {cells}")


def sanity_partnered(source, rows):
    print("\n  Partnered 25-44 national weighted by year:")
    out = {}
    for yr in CENSUS_YEARS:
        p_sum = 0
        t_sum = 0
        for sa2, py in source.items():
            p, t = py.get(yr, (None, None))
            if p is None or t is None or t <= 0:
                continue
            p_sum += p
            t_sum += t
        nat = (p_sum / t_sum * 100.0) if t_sum else 0
        out[yr] = round(nat, 4)
        flag = ""
        if yr == 2021 and not (55.0 <= nat <= 68.0):
            flag = f"  [WARN: expected 55-68%, got {nat:.2f}%]"
        elif yr == 2021:
            flag = "  [in 55-68 expected band]"
        print(f"    {yr}: {nat:.2f}%{flag}")
    _print_verify(rows, "Partnered 25-44 %", CENSUS_YEARS)
    return out


def sanity_women_with_child(source, rows, label, expected_lo, expected_hi):
    print(f"\n  Women-with-child {label} national weighted by year:")
    out = {}
    for yr in CENSUS_YEARS:
        n_sum = 0
        d_sum = 0
        for sa2, py in source.items():
            n, d = py.get(yr, (None, None))
            if n is None or d is None or d <= 0:
                continue
            n_sum += n
            d_sum += d
        nat = (n_sum / d_sum * 100.0) if d_sum else 0
        out[yr] = round(nat, 4)
        flag = ""
        if yr == 2021 and not (expected_lo <= nat <= expected_hi):
            flag = f"  [WARN: expected {expected_lo}-{expected_hi}%, got {nat:.2f}%]"
        elif yr == 2021:
            flag = f"  [in {expected_lo}-{expected_hi} expected band]"
        print(f"    {yr}: {nat:.2f}%{flag}")
    _print_verify(rows, f"Women {label} 1+child %", CENSUS_YEARS)
    return out


def sanity_parent_cohort(source, rows):
    print("\n  Parent-cohort 25-44 national weighted by year:")
    out = {}
    years_seen = sorted({yr for py in source.values() for yr in py})
    for yr in years_seen:
        p_sum = 0
        t_sum = 0
        for sa2, py in source.items():
            cell = py.get(yr)
            if cell is None:
                continue
            p, t = cell
            if t is None or t <= 0:
                continue
            p_sum += p
            t_sum += t
        nat = (p_sum / t_sum * 100.0) if t_sum else 0
        out[yr] = round(nat, 4)
        flag = ""
        if yr == 2021 and not (26.0 <= nat <= 32.0):
            flag = f"  [WARN: expected 26-32%, got {nat:.2f}%]"
        elif yr == 2021:
            flag = "  [in 26-32 expected band]"
        print(f"    {yr}: {nat:.2f}%{flag}")
    _print_verify(rows, "Parent cohort 25-44 %", years_seen)
    return out


# =====================================================================
# DB write helpers
# =====================================================================
def pre_state_for_metric(con, metric_name):
    cur = con.cursor()
    return cur.execute(
        f'SELECT COUNT(*) FROM "{TARGET_TABLE}" WHERE metric_name = ?',
        (metric_name,),
    ).fetchone()[0]


def write_long_metric(con, metric_name, rows, replace=False):
    cur = con.cursor()
    if replace:
        n = cur.execute(
            f'DELETE FROM "{TARGET_TABLE}" WHERE metric_name = ?',
            (metric_name,),
        ).rowcount
        print(f"  Deleted {n:,} existing rows for metric_name='{metric_name}'")
    cur.executemany(
        f'INSERT INTO "{TARGET_TABLE}" (sa2_code, year, metric_name, value) '
        f"VALUES (?, ?, ?, ?)",
        [(sa2, yr, metric_name, val) for sa2, yr, val in rows],
    )
    return cur.rowcount


def write_audit_log(con, action, subject_type, before, after, reason):
    cur = con.cursor()
    cur.execute(
        "INSERT INTO audit_log "
        "(actor, action, subject_type, subject_id, before_json, after_json, reason, occurred_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))",
        (ACTOR, action, subject_type, 0,
         json.dumps(before), json.dumps(after), reason),
    )
    return cur.execute("SELECT MAX(audit_id) FROM audit_log").fetchone()[0]


def backup_db():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.parent / f"pre_layer4_4_step_a3_streamc_{timestamp}.db"
    print(f"  Backup: copying {DB_PATH} -> {backup_path}")
    shutil.copy2(DB_PATH, backup_path)
    size_mb = backup_path.stat().st_size / (1024 * 1024)
    print(f"  Backup size: {size_mb:.1f} MB")
    return backup_path


# =====================================================================
# Main
# =====================================================================
def main():
    args = parse_args()
    apply_mode = args["apply"]
    replace = args["replace"]

    print(f"DB:     {DB_PATH}")
    print(f"Zip:    {ZIP_PATH}")
    print(f"ERP:    {ERP_WORKBOOK}")
    print(f"Mode:   {'APPLY' if apply_mode else 'DRY-RUN'}"
          f"{'  REPLACE' if replace else ''}")

    preflight()

    section("Reading TSP source")
    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        t05 = read_t05(z)
        _verify_t05_columns(t05)
        t07 = read_t07(z)
        _verify_t07_columns(t07)

    section("Reading ERP source")
    erp = read_erp_parent_cohort()

    section("Deriving + sanity (per metric)")
    print("\n[1/4] erp_parent_cohort_25_44_share_pct")
    pc_rows, pc_src = derive_parent_cohort(erp)
    pc_nat = sanity_parent_cohort(pc_src, pc_rows)

    print("\n[2/4] census_partnered_25_44_share_pct")
    pn_rows, pn_src = derive_partnered_25_44(t05)
    pn_nat = sanity_partnered(pn_src, pn_rows)

    print("\n[3/4] census_women_35_44_with_child_share_pct")
    w3544_rows, w3544_src = derive_women_35_44_with_child(t07)
    w3544_nat = sanity_women_with_child(w3544_src, w3544_rows, "35-44", *SANITY_W3544)

    print("\n[4/4] census_women_25_34_with_child_share_pct")
    w2534_rows, w2534_src = derive_women_25_34_with_child(t07)
    w2534_nat = sanity_women_with_child(w2534_src, w2534_rows, "25-34", *SANITY_W2534)

    metric_payloads = {
        "erp_parent_cohort_25_44_share_pct":          (pc_rows,    pc_nat),
        "census_partnered_25_44_share_pct":           (pn_rows,    pn_nat),
        "census_women_35_44_with_child_share_pct":    (w3544_rows, w3544_nat),
        "census_women_25_34_with_child_share_pct":    (w2534_rows, w2534_nat),
    }

    section("Pre-state inventory")
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    max_audit = cur.execute("SELECT COALESCE(MAX(audit_id),0) FROM audit_log").fetchone()[0]
    target_total = cur.execute(f'SELECT COUNT(*) FROM "{TARGET_TABLE}"').fetchone()[0]
    print(f"  audit_log max audit_id: {max_audit:,}")
    print(f"  {TARGET_TABLE} rows:    {target_total:,}")
    pre_existing = {}
    for m_name in metric_payloads:
        n = pre_state_for_metric(con, m_name)
        pre_existing[m_name] = n
        print(f"  {m_name}: {n:,} existing rows")

    blockers = [m for m, n in pre_existing.items() if n > 0]
    if blockers and not replace and apply_mode:
        print()
        print("  ERROR: existing rows present and --replace not set:")
        for m in blockers:
            print(f"    - {m}: {pre_existing[m]:,} rows")
        print("  Re-run with --replace --apply to overwrite.")
        con.close()
        sys.exit(4)

    if not apply_mode:
        section("DRY-RUN — no DB mutation")
        for m_name, (rows, _nat) in metric_payloads.items():
            print(f"  Would insert {len(rows):,} rows into {TARGET_TABLE} for {m_name}")
        print(f"  Would write 4 audit_log rows (next audit_id starts at {max_audit + 1})")
        print(f"  Would back up DB before write")
        print()
        print("  To proceed: re-run with --apply"
              f"{'' if not replace else ' (replace mode active)'}")
        con.close()
        return

    section("Backup")
    backup_path = backup_db()

    section("Writing")
    audit_ids = {}
    for spec in METRICS:
        m_name = spec["name"]
        rows, nat = metric_payloads[m_name]
        inserted = write_long_metric(con, m_name, rows, replace=replace)
        print(f"  Wrote {inserted:,} rows for {m_name}")
        years = sorted({r[1] for r in rows})
        before = {"existing_rows_for_metric": pre_existing[m_name]}
        after = {
            "rows_inserted": inserted,
            "sa2_count": len({r[0] for r in rows}),
            "years": years,
            "national_pct_by_year": {str(y): nat.get(y) for y in years},
            "backup": str(backup_path),
            "replaced": replace,
            "unit": "percentage_0_to_100",
        }
        aid = write_audit_log(con, spec["action"], TARGET_TABLE, before, after, spec["reason"])
        audit_ids[m_name] = aid
        print(f"    audit_id={aid}")

    con.commit()

    section("Post-state")
    cur = con.cursor()
    for m_name in metric_payloads:
        c, lo, hi, mean = cur.execute(
            f'SELECT COUNT(*), MIN(value), MAX(value), AVG(value) '
            f'FROM "{TARGET_TABLE}" WHERE metric_name = ?',
            (m_name,),
        ).fetchone()
        print(f"  {m_name}: {c:,} rows  range [{lo:.2f}, {hi:.2f}]  mean {mean:.2f}")

    print("\n  Verification SA2 spot-check (latest year per metric):")
    for sa2, name in VERIFY_SA2:
        bits = [f"{sa2} {name}"]
        for m_name, lbl in [
            ("erp_parent_cohort_25_44_share_pct", "PC25-44"),
            ("census_partnered_25_44_share_pct", "Partnered25-44"),
            ("census_women_35_44_with_child_share_pct", "W35-44+ch"),
            ("census_women_25_34_with_child_share_pct", "W25-34+ch"),
        ]:
            v = cur.execute(
                f'SELECT value FROM "{TARGET_TABLE}" '
                f'WHERE sa2_code=? AND metric_name=? '
                f'ORDER BY year DESC LIMIT 1',
                (sa2, m_name),
            ).fetchone()
            bits.append(f"{lbl}={v[0]:.1f}%" if v else f"{lbl}=NA")
        print(f"    " + " | ".join(bits))

    con.close()
    print()
    print("APPLIED.")
    print()
    print("Next:")
    print("  1. python patch_b2_layer3_add_a3_streamc.py --apply")
    print("  2. python layer3_apply.py --apply")
    print("  3. python layer3_x_catchment_metric_banding.py --apply  # OI-35 workaround")


if __name__ == "__main__":
    main()
