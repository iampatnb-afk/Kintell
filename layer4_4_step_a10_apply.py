r"""
layer4_4_step_a10_apply.py — A10 Demographic Mix bundle ingest (v1).

Ingests three Census TSP SA2-level metrics into
`abs_sa2_education_employment_annual` (long-format), plus a new
`abs_sa2_country_of_birth_top_n` table for the top-3 countries of birth
per SA2 (2021 only, context display only).

Source: abs_data/2021_TSP_SA2_for_AUS_short-header.zip
Tables read: T06A/B/C (ATSI), T08A/B (country of birth), T14A/B/C (family composition).

Note: roadmap initially named T07/T08/T19. Probe of the TSP zip showed
T07 is fertility (children-ever-born × age) and T19 is tenure type/landlord.
The correct subjects for the Demographic Mix bundle are T06 (ATSI),
T08 (country of birth), T14 (family composition). See recon/a10_c8_design.md.

Metrics (all stored as percentage 0-100, matching census_*_pct convention):

  1. census_atsi_share_pct
       Source: T06 Tot_Indig_P / Tot_Tot_P × 100
       National 2021 reference: ~3.2%

  2. census_overseas_born_share_pct
       Source: T08 (Tot - Aust - Country_birt_ns) / Tot × 100
       (Country_birt_ns excluded from numerator per NES precedent.)
       National 2021 reference: ~27%

  3. census_single_parent_family_share_pct
       Source: T14 Tot_FH_One_PFam / Tot_FH_Tot × 100
       (Share of family households that are one-parent families.)
       National 2021 reference: ~16%

Plus:
  4. abs_sa2_country_of_birth_top_n (NEW table)
       Top-3 countries (excluding Australia) per SA2 for 2021.
       (sa2_code, census_year, rank, country_name, count, share_pct)
       PRIMARY KEY (sa2_code, census_year, rank).
       Display-only. No banding, no calibration influence.

STD-30 pre-mutation discipline:
  - Pre-state inventory + idempotency check per metric
  - Single backup before write
  - audit_log row per metric per DEC-62 schema
  - Post-state verification

Usage:
    python layer4_4_step_a10_apply.py             # dry-run (default)
    python layer4_4_step_a10_apply.py --apply     # write
    python layer4_4_step_a10_apply.py --replace --apply   # replace existing rows

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
TOPN_TABLE = "abs_sa2_country_of_birth_top_n"
ACTOR = "layer4_4_step_a10_apply"

# ─────────────────────────────────────────────────────────────────────
# Source files in the TSP zip
# ─────────────────────────────────────────────────────────────────────
ZIP_PREFIX = "2021 Census TSP Statistical Area 2 for AUS/"
T06_NAMES = [f"{ZIP_PREFIX}2021Census_T06{ab}_AUST_SA2.csv" for ab in "ABC"]
T08_NAMES = [f"{ZIP_PREFIX}2021Census_T08{ab}_AUST_SA2.csv" for ab in "AB"]
T14_NAMES = [f"{ZIP_PREFIX}2021Census_T14{ab}_AUST_SA2.csv" for ab in "ABC"]

CENSUS_YEARS = [2011, 2016, 2021]

# ─────────────────────────────────────────────────────────────────────
# Per-metric column maps (pre-validated against TSP zip headers 2026-05-09)
# ─────────────────────────────────────────────────────────────────────
# T06 — ATSI: each year's columns sit in a different file:
#   2011 → T06A, 2016 → T06B, 2021 → T06C.
ATSI_COLS = {
    2011: {"file_idx": 0, "indig": "C11_Tot_Indig_P", "tot": "C11_Tot_Tot_P"},
    2016: {"file_idx": 1, "indig": "C16_Tot_Indig_P", "tot": "C16_Tot_Tot_P"},
    2021: {"file_idx": 2, "indig": "C21_Tot_Indig_P", "tot": "C21_Tot_Tot_P"},
}

# T08 — country of birth: Aust_* sits in T08A; Tot_* and Country_birt_ns_* in T08B.
# After horizontal merge on SA2_CODE_2021 the columns are accessible together.
OVERSEAS_COLS = {
    2011: {"aust": "Aust_C11_P", "tot": "Tot_C11_P", "ns": "Country_birt_ns_C11_P"},
    2016: {"aust": "Aust_C16_P", "tot": "Tot_C16_P", "ns": "Country_birt_ns_C16_P"},
    2021: {"aust": "Aust_C21_P", "tot": "Tot_C21_P", "ns": "Country_birt_ns_C21_P"},
}

# T14 — family composition: each year's `Tot_FH_*` totals sit in a different file:
#   2011 → T14A, 2016 → T14B, 2021 → T14C.
SINGLE_PARENT_COLS = {
    2011: {"file_idx": 0, "one_pfam": "C11_Tot_FH_One_PFam", "fh_tot": "C11_Tot_FH_Tot"},
    2016: {"file_idx": 1, "one_pfam": "C16_Tot_FH_One_PFam", "fh_tot": "C16_Tot_FH_Tot"},
    2021: {"file_idx": 2, "one_pfam": "C21_Tot_FH_One_PFam", "fh_tot": "C21_Tot_FH_Tot"},
}

# ─────────────────────────────────────────────────────────────────────
# Metric definitions (drives generic ingest pipeline)
# ─────────────────────────────────────────────────────────────────────
METRICS = [
    {
        "name": "census_atsi_share_pct",
        "action": "census_atsi_share_ingest_v1",
        "national_2021_band": (2.5, 4.0),   # ABS published ~3.2%
        "reason": (
            "A10 ATSI share ingest (v1). Stores percentage (0-100) matching "
            "census_*_pct convention. Formula: Tot_Indig_P / Tot_Tot_P * 100, "
            "where Tot_Tot_P = Indig + NonInd + Indig_status_not_stated. "
            "Source: ABS Census 2021 TSP T06A/B/C."
        ),
    },
    {
        "name": "census_overseas_born_share_pct",
        "action": "census_overseas_born_share_ingest_v1",
        "national_2021_band": (25.0, 30.0),  # ABS published ~27.6%
        "reason": (
            "A10 overseas-born share ingest (v1). Stores percentage (0-100). "
            "Formula: (Tot - Aust - Country_birt_ns) / Tot * 100. "
            "Country_birt_ns excluded from numerator per NES precedent "
            "(STD: not-stated excluded from numerator, kept in denominator). "
            "Source: ABS Census 2021 TSP T08A+T08B."
        ),
    },
    {
        "name": "census_single_parent_family_share_pct",
        "action": "census_single_parent_family_share_ingest_v1",
        "national_2021_band": (14.0, 18.0),  # ABS published ~16%
        "reason": (
            "A10 single-parent-family share ingest (v1). Stores percentage (0-100). "
            "Formula: Tot_FH_One_PFam / Tot_FH_Tot * 100. "
            "Share of family households that are one-parent families "
            "(LP_H/GH/OH excluded from denominator — family households only). "
            "Source: ABS Census 2021 TSP T14A/B/C."
        ),
    },
]

# ─────────────────────────────────────────────────────────────────────
# Verification SA2s — 3 carried from A2 + 1 new high-ATSI per D-A4
# ─────────────────────────────────────────────────────────────────────
VERIFY_SA2 = [
    ("211011251", "Bayswater Vic"),
    ("118011341", "Bondi Junction-Waverly NSW"),
    ("506031124", "Bentley-Wilson-St James WA"),
    ("702041063", "Outback NT (high-ATSI verify)"),
]

# Top-N config
TOP_N = 3


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
# Source loaders (one per TSP table family)
# =====================================================================
def _read_csv_from_zip(z, name):
    import pandas as pd
    if name not in z.namelist():
        print(f"ERROR: expected CSV not found in zip: {name}")
        sys.exit(2)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        df = pd.read_csv(io.BytesIO(z.read(name)), dtype=str)
    df.columns = [str(c).strip() for c in df.columns]
    if "SA2_CODE_2021" not in df.columns:
        print(f"ERROR: SA2_CODE_2021 missing in {name}.")
        sys.exit(2)
    df["SA2_CODE_2021"] = df["SA2_CODE_2021"].astype(str).str.strip()
    sa2_re = re.compile(r"^\d{9}$")
    df = df[df["SA2_CODE_2021"].str.match(sa2_re)].copy()
    return df


def read_t06(z):
    """Read T06A/B/C, return dict[year] → DataFrame indexed by SA2."""
    out = {}
    for yr in CENSUS_YEARS:
        idx = ATSI_COLS[yr]["file_idx"]
        df = _read_csv_from_zip(z, T06_NAMES[idx]).set_index("SA2_CODE_2021")
        for col_key in ("indig", "tot"):
            col = ATSI_COLS[yr][col_key]
            if col not in df.columns:
                print(f"ERROR: T06[{yr}] missing column {col}.")
                sys.exit(2)
        out[yr] = df
    print(f"  T06: {[(yr, len(df)) for yr, df in out.items()]}")
    return out


def read_t08(z):
    """Read T08A and T08B, merge horizontally on SA2_CODE_2021."""
    a = _read_csv_from_zip(z, T08_NAMES[0])
    b = _read_csv_from_zip(z, T08_NAMES[1])
    # Drop SA2_CODE_2021 duplicate from B before merge
    merged = a.merge(b.drop(columns=[]), on="SA2_CODE_2021", how="inner",
                     suffixes=("", "_DROP"))
    # Drop any duplicated columns (Netherlands is split across A and B for a few year-sex
    # combinations; right-side wins are fine since they're identical or B has the slice
    # A doesn't).
    for col in list(merged.columns):
        if col.endswith("_DROP"):
            merged = merged.drop(columns=[col])
    for yr in CENSUS_YEARS:
        for col_key in ("aust", "tot", "ns"):
            col = OVERSEAS_COLS[yr][col_key]
            if col not in merged.columns:
                print(f"ERROR: T08[{yr}] merged missing column {col}. "
                      f"Available subset: {[c for c in merged.columns if col.split('_')[0] in c][:6]}")
                sys.exit(2)
    print(f"  T08 merged: {len(merged):,} rows × {len(merged.columns)} cols")
    return merged.set_index("SA2_CODE_2021")


def read_t14(z):
    """Read T14A/B/C, return dict[year] → DataFrame indexed by SA2."""
    out = {}
    for yr in CENSUS_YEARS:
        idx = SINGLE_PARENT_COLS[yr]["file_idx"]
        df = _read_csv_from_zip(z, T14_NAMES[idx]).set_index("SA2_CODE_2021")
        for col_key in ("one_pfam", "fh_tot"):
            col = SINGLE_PARENT_COLS[yr][col_key]
            if col not in df.columns:
                print(f"ERROR: T14[{yr}] missing column {col}.")
                sys.exit(2)
        out[yr] = df
    print(f"  T14: {[(yr, len(df)) for yr, df in out.items()]}")
    return out


# =====================================================================
# Per-metric derivation
# =====================================================================
def to_int(v):
    try:
        return int(v) if v not in ("", "..", "np", None) else None
    except (ValueError, TypeError):
        return None


def derive_atsi(t06):
    """Returns (rows, source_dict). rows = list[(sa2, year, value_pct)]."""
    rows = []
    skipped_null = 0
    skipped_zero_total = 0
    source = {}
    sa2s = sorted(set.intersection(*(set(df.index) for df in t06.values())))
    for sa2 in sa2s:
        per_year = {}
        for yr in CENSUS_YEARS:
            indig = to_int(t06[yr].at[sa2, ATSI_COLS[yr]["indig"]])
            tot   = to_int(t06[yr].at[sa2, ATSI_COLS[yr]["tot"]])
            per_year[yr] = (indig, tot)
            if indig is None or tot is None:
                skipped_null += 1
                continue
            if tot == 0:
                skipped_zero_total += 1
                continue
            pct = max(0.0, min(100.0, (indig / tot) * 100.0))
            rows.append((sa2, yr, round(pct, 4)))
        source[sa2] = per_year
    print(f"  ATSI rows: {len(rows):,}  null-skip: {skipped_null:,}  "
          f"zero-total-skip: {skipped_zero_total:,}")
    return rows, source


def derive_overseas(t08):
    rows = []
    skipped_null = 0
    skipped_zero_total = 0
    clamped = 0
    source = {}
    for sa2 in t08.index:
        per_year = {}
        for yr in CENSUS_YEARS:
            aust = to_int(t08.at[sa2, OVERSEAS_COLS[yr]["aust"]])
            tot  = to_int(t08.at[sa2, OVERSEAS_COLS[yr]["tot"]])
            ns   = to_int(t08.at[sa2, OVERSEAS_COLS[yr]["ns"]])
            per_year[yr] = (aust, tot, ns)
            if aust is None or tot is None or ns is None:
                skipped_null += 1
                continue
            if tot == 0:
                skipped_zero_total += 1
                continue
            overseas_count = tot - aust - ns
            if overseas_count < 0:
                clamped += 1
                overseas_count = 0
            pct = max(0.0, min(100.0, (overseas_count / tot) * 100.0))
            rows.append((sa2, yr, round(pct, 4)))
        source[sa2] = per_year
    print(f"  OS-born rows: {len(rows):,}  null-skip: {skipped_null:,}  "
          f"zero-total-skip: {skipped_zero_total:,}  clamped-neg: {clamped:,}")
    return rows, source


def derive_single_parent(t14):
    rows = []
    skipped_null = 0
    skipped_zero_total = 0
    source = {}
    sa2s = sorted(set.intersection(*(set(df.index) for df in t14.values())))
    for sa2 in sa2s:
        per_year = {}
        for yr in CENSUS_YEARS:
            opf = to_int(t14[yr].at[sa2, SINGLE_PARENT_COLS[yr]["one_pfam"]])
            fht = to_int(t14[yr].at[sa2, SINGLE_PARENT_COLS[yr]["fh_tot"]])
            per_year[yr] = (opf, fht)
            if opf is None or fht is None:
                skipped_null += 1
                continue
            if fht == 0:
                skipped_zero_total += 1
                continue
            pct = max(0.0, min(100.0, (opf / fht) * 100.0))
            rows.append((sa2, yr, round(pct, 4)))
        source[sa2] = per_year
    print(f"  1PF rows: {len(rows):,}  null-skip: {skipped_null:,}  "
          f"zero-fh_tot-skip: {skipped_zero_total:,}")
    return rows, source


# =====================================================================
# Sanity checks
# =====================================================================
def sanity_atsi(source, rows):
    print("\n  ATSI national weighted by year:")
    out = {}
    for yr in CENSUS_YEARS:
        i_sum = 0; t_sum = 0
        for sa2, py in source.items():
            indig, tot = py.get(yr, (None, None))
            if indig is None or tot is None or tot <= 0: continue
            i_sum += indig; t_sum += tot
        nat = (i_sum / t_sum * 100.0) if t_sum else 0
        out[yr] = round(nat, 4)
        flag = ""
        if yr == 2021 and not (2.5 <= nat <= 4.0):
            flag = f"  [WARN: expected 2.5-4.0%, got {nat:.2f}%]"
        elif yr == 2021:
            flag = "  [in 2.5-4.0 expected band]"
        print(f"    {yr}: {nat:.2f}%{flag}")
    _print_verify(rows, "ATSI %")
    return out


def sanity_overseas(source, rows):
    print("\n  OS-born national weighted by year:")
    out = {}
    for yr in CENSUS_YEARS:
        os_sum = 0; t_sum = 0
        for sa2, py in source.items():
            aust, tot, ns = py.get(yr, (None, None, None))
            if aust is None or tot is None or ns is None or tot <= 0: continue
            os_sum += max(0, tot - aust - ns)
            t_sum += tot
        nat = (os_sum / t_sum * 100.0) if t_sum else 0
        out[yr] = round(nat, 4)
        flag = ""
        if yr == 2021 and not (25.0 <= nat <= 30.0):
            flag = f"  [WARN: expected 25-30%, got {nat:.2f}%]"
        elif yr == 2021:
            flag = "  [in 25-30 expected band]"
        print(f"    {yr}: {nat:.2f}%{flag}")
    _print_verify(rows, "OS-born %")
    return out


def sanity_single_parent(source, rows):
    print("\n  Single-parent-family national weighted by year:")
    out = {}
    for yr in CENSUS_YEARS:
        opf_sum = 0; fht_sum = 0
        for sa2, py in source.items():
            opf, fht = py.get(yr, (None, None))
            if opf is None or fht is None or fht <= 0: continue
            opf_sum += opf; fht_sum += fht
        nat = (opf_sum / fht_sum * 100.0) if fht_sum else 0
        out[yr] = round(nat, 4)
        flag = ""
        if yr == 2021 and not (14.0 <= nat <= 18.0):
            flag = f"  [WARN: expected 14-18%, got {nat:.2f}%]"
        elif yr == 2021:
            flag = "  [in 14-18 expected band]"
        print(f"    {yr}: {nat:.2f}%{flag}")
    _print_verify(rows, "1PF %")
    return out


def _print_verify(rows, label):
    by_sa2_year = {(s, y): v for s, y, v in rows}
    print(f"\n  Verification SA2s ({label} by year):")
    for sa2, name in VERIFY_SA2:
        cells = " ".join(
            f"{yr}={by_sa2_year[(sa2, yr)]:.2f}%"
            if (sa2, yr) in by_sa2_year else f"{yr}=NA"
            for yr in CENSUS_YEARS
        )
        print(f"    {sa2} ({name}): {cells}")


# =====================================================================
# Top-N country of birth
# =====================================================================
# Columns excluded from "country" candidates (not real countries)
TOPN_EXCLUDE_PREFIXES = {"Aust", "Tot", "Country_birt_ns", "Born_elsewhere"}


def _t08_country_columns_2021(t08):
    """Return list of (column_name, country_label) for 2021 _P columns,
    excluding Australia and aggregate buckets."""
    out = []
    for c in t08.columns:
        if not c.endswith("_C21_P"):
            continue
        prefix = c[: -len("_C21_P")]
        if prefix in TOPN_EXCLUDE_PREFIXES:
            continue
        # Pretty label: "New_Zealand" → "New Zealand", "Unitd_Kingdom" → "United Kingdom" via small map
        label = _country_label(prefix)
        out.append((c, label))
    return out


def _country_label(prefix):
    """Map TSP short-header country prefix → readable label."""
    fixups = {
        "Unit_Sts_Amer": "United States",
        "Unitd_Kingdom": "United Kingdom",
        "Hong_Kong": "Hong Kong",
        "New_Zealand": "New Zealand",
        "South_Africa": "South Africa",
        "Sri_Lanka": "Sri Lanka",
    }
    if prefix in fixups:
        return fixups[prefix]
    return prefix.replace("_", " ")


def derive_topn(t08):
    """For each SA2, find the top-N countries by 2021 _P count.
    Returns list[(sa2, year, rank, country_name, count, share_pct)]."""
    cols = _t08_country_columns_2021(t08)
    print(f"  Top-N source columns (2021): {len(cols)} candidates")

    rows = []
    skipped = 0
    for sa2 in t08.index:
        tot = to_int(t08.at[sa2, OVERSEAS_COLS[2021]["tot"]])
        if tot is None or tot <= 0:
            skipped += 1
            continue
        counts = []
        for col, label in cols:
            v = to_int(t08.at[sa2, col])
            if v is None or v <= 0:
                continue
            counts.append((v, label))
        if not counts:
            continue
        counts.sort(key=lambda r: -r[0])
        for rank, (v, label) in enumerate(counts[:TOP_N], start=1):
            share = round(v / tot * 100.0, 4)
            rows.append((sa2, 2021, rank, label, v, share))
    print(f"  Top-N rows generated: {len(rows):,}  (sa2-skipped no-tot: {skipped})")
    return rows


# =====================================================================
# DB write helpers
# =====================================================================
def ensure_topn_table(con, apply_mode):
    cur = con.cursor()
    exists = cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (TOPN_TABLE,),
    ).fetchone()
    if exists:
        print(f"  {TOPN_TABLE}: already exists.")
        return False
    if not apply_mode:
        print(f"  {TOPN_TABLE}: WOULD CREATE on --apply.")
        return False
    cur.execute(f"""
        CREATE TABLE "{TOPN_TABLE}" (
            sa2_code     TEXT    NOT NULL,
            census_year  INTEGER NOT NULL,
            rank         INTEGER NOT NULL,
            country_name TEXT    NOT NULL,
            count        INTEGER,
            share_pct    REAL,
            PRIMARY KEY (sa2_code, census_year, rank)
        )
    """)
    cur.execute(
        "INSERT INTO audit_log "
        "(actor, action, subject_type, subject_id, before_json, after_json, reason, occurred_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))",
        (
            ACTOR,
            "country_of_birth_top_n_create_v1",
            "schema",
            0,
            json.dumps({"existed": False}),
            json.dumps({"created_table": TOPN_TABLE}),
            "A10 schema mutation: create table for top-3 country-of-birth display "
            "context (D-A2). New table not part of existing long-format because "
            "country_name is text and rank is structural.",
        ),
    )
    print(f"  {TOPN_TABLE}: CREATED.")
    return True


def pre_state_for_metric(con, metric_name):
    cur = con.cursor()
    existing = cur.execute(
        f'SELECT COUNT(*) FROM "{TARGET_TABLE}" WHERE metric_name = ?',
        (metric_name,),
    ).fetchone()[0]
    return existing


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


def write_topn(con, rows, replace=False):
    cur = con.cursor()
    if replace:
        n = cur.execute(f'DELETE FROM "{TOPN_TABLE}"').rowcount
        print(f"  Deleted {n:,} existing rows from {TOPN_TABLE}")
    cur.executemany(
        f'INSERT INTO "{TOPN_TABLE}" '
        f"(sa2_code, census_year, rank, country_name, count, share_pct) "
        f"VALUES (?, ?, ?, ?, ?, ?)",
        rows,
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
    backup_path = DB_PATH.parent / f"pre_layer4_4_step_a10_{timestamp}.db"
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
    print(f"Source: {ZIP_PATH}")
    print(f"Mode:   {'APPLY' if apply_mode else 'DRY-RUN'}"
          f"{'  REPLACE' if replace else ''}")

    preflight()

    section("Reading source")
    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        t06 = read_t06(z)
        t08 = read_t08(z)
        t14 = read_t14(z)

    section("Deriving + sanity (per metric)")
    print("\n[1/3] census_atsi_share_pct")
    atsi_rows, atsi_src = derive_atsi(t06)
    atsi_nat = sanity_atsi(atsi_src, atsi_rows)

    print("\n[2/3] census_overseas_born_share_pct")
    os_rows, os_src = derive_overseas(t08)
    os_nat = sanity_overseas(os_src, os_rows)

    print("\n[3/3] census_single_parent_family_share_pct")
    sp_rows, sp_src = derive_single_parent(t14)
    sp_nat = sanity_single_parent(sp_src, sp_rows)

    metric_payloads = {
        "census_atsi_share_pct":                  (atsi_rows, atsi_nat),
        "census_overseas_born_share_pct":         (os_rows,   os_nat),
        "census_single_parent_family_share_pct":  (sp_rows,   sp_nat),
    }

    section("Top-N country of birth (2021)")
    topn_rows = derive_topn(t08)
    print(f"\n  Top-3 spotcheck ({len(VERIFY_SA2)} verify SA2s):")
    by_sa2_topn = {}
    for sa2, yr, rank, name, count, share in topn_rows:
        by_sa2_topn.setdefault(sa2, []).append((rank, name, count, share))
    for sa2, vname in VERIFY_SA2:
        triples = by_sa2_topn.get(sa2, [])
        triples.sort()
        cells = ", ".join(f"#{r} {n} ({c}, {s:.1f}%)" for r, n, c, s in triples)
        print(f"    {sa2} ({vname}): {cells if cells else 'NO DATA'}")

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
    topn_table_exists = bool(cur.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (TOPN_TABLE,),
    ).fetchone())
    topn_existing = 0
    if topn_table_exists:
        topn_existing = cur.execute(f'SELECT COUNT(*) FROM "{TOPN_TABLE}"').fetchone()[0]
    print(f"  {TOPN_TABLE}: table_exists={topn_table_exists} rows={topn_existing:,}")

    # Idempotency: any non-empty without --replace blocks
    blockers = [m for m, n in pre_existing.items() if n > 0]
    if (blockers or topn_existing > 0) and not replace and apply_mode:
        print()
        print("  ERROR: existing rows present and --replace not set:")
        for m in blockers:
            print(f"    - {m}: {pre_existing[m]:,} rows")
        if topn_existing > 0:
            print(f"    - {TOPN_TABLE}: {topn_existing:,} rows")
        print(f"  Re-run with --replace --apply to overwrite.")
        con.close()
        sys.exit(4)

    if not apply_mode:
        section("DRY-RUN — no DB mutation")
        for m_name, (rows, _nat) in metric_payloads.items():
            print(f"  Would insert {len(rows):,} rows into {TARGET_TABLE} for {m_name}")
        print(f"  Would CREATE {TOPN_TABLE} (if missing) and insert {len(topn_rows):,} rows")
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

    # 0. Top-N table create (if needed) — schema row first per audit ordering preference
    created_topn = ensure_topn_table(con, apply_mode=True)

    # 1-3. Long-format metric writes + per-metric audit rows
    audit_ids = {}
    for spec in METRICS:
        m_name = spec["name"]
        rows, nat = metric_payloads[m_name]
        inserted = write_long_metric(con, m_name, rows, replace=replace)
        print(f"  Wrote {inserted:,} rows for {m_name}")
        before = {"existing_rows_for_metric": pre_existing[m_name]}
        after = {
            "rows_inserted": inserted,
            "sa2_count": len({r[0] for r in rows}),
            "years": sorted({r[1] for r in rows}),
            "national_2011_pct": nat.get(2011),
            "national_2016_pct": nat.get(2016),
            "national_2021_pct": nat.get(2021),
            "backup": str(backup_path),
            "replaced": replace,
            "unit": "percentage_0_to_100",
        }
        aid = write_audit_log(con, spec["action"], TARGET_TABLE, before, after, spec["reason"])
        audit_ids[m_name] = aid
        print(f"    audit_id={aid}")

    # 4. Top-N data write + audit
    topn_inserted = write_topn(con, topn_rows, replace=replace)
    print(f"  Wrote {topn_inserted:,} rows for {TOPN_TABLE}")
    topn_aid = write_audit_log(
        con,
        "country_of_birth_top_n_ingest_v1",
        TOPN_TABLE,
        {"existing_rows": topn_existing, "table_created_this_run": created_topn},
        {
            "rows_inserted": topn_inserted,
            "sa2_count": len({r[0] for r in topn_rows}),
            "census_year": 2021,
            "top_n": TOP_N,
            "backup": str(backup_path),
        },
        "A10 country-of-birth top-3 ingest (v1, 2021 only). Display-only "
        "context table accompanying census_overseas_born_share_pct. "
        "No banding, no calibration influence (D-A2).",
    )
    print(f"    audit_id={topn_aid}")

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
    c = cur.execute(f'SELECT COUNT(*) FROM "{TOPN_TABLE}"').fetchone()[0]
    print(f"  {TOPN_TABLE}: {c:,} rows")

    print("\n  Verification SA2 spot-check (2021):")
    for sa2, name in VERIFY_SA2:
        bits = [name]
        for m_name, lbl in [
            ("census_atsi_share_pct", "ATSI"),
            ("census_overseas_born_share_pct", "OS"),
            ("census_single_parent_family_share_pct", "1PF"),
        ]:
            v = cur.execute(
                f'SELECT value FROM "{TARGET_TABLE}" '
                f'WHERE sa2_code=? AND metric_name=? AND year=2021',
                (sa2, m_name),
            ).fetchone()
            bits.append(f"{lbl}={v[0]:.1f}%" if v else f"{lbl}=NA")
        print(f"    {sa2} {' '.join(bits)}")

    con.close()
    print()
    print("APPLIED.")
    print()
    print("Next:")
    print("  1. python patch_b2_layer3_add_demographic_mix.py --apply")
    print("  2. python layer3_apply.py --apply")
    print("  3. python layer3_x_catchment_metric_banding.py --apply  # OI-35 workaround")


if __name__ == "__main__":
    main()
