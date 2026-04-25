"""
build_historical_data.py
Extracts sector trend data from NQAITS Quarterly Data Splits (Q3 2013 - Q4 2025).xlsx
Outputs: data/sector_history.json — used by generate_dashboard.py for trend charts

Run: python build_historical_data.py
Takes ~2-3 minutes (50 sheets)

Additions (2026-04-16):
  - Supply/demand ratio: licensed places per 100 children under 5
    (national, from ABS Population and People Database.xlsx)
  - New service approvals per quarter
    (from serviceapprovalgranteddate in NQAITS sheets)
  - ARIA zero-gap fix: Q2 2018–Q3 2021 set to null (not 0)
    so dashboard charts interpolate cleanly across the gap
"""

import pandas as pd
import json
import numpy as np
from pathlib import Path
from datetime import datetime

BASE_DIR  = Path(__file__).parent
DATA_DIR  = BASE_DIR / "data"
NQS_FILE  = BASE_DIR / "abs_data" / "NQAITS Quarterly Data Splits (Q3 2013 - Q4 2025).xlsx"
ABS_POP   = BASE_DIR / "abs_data" / "Population and People Database.xlsx"
OUT_FILE  = DATA_DIR / "sector_history.json"

QUARTER_SHEETS = [
    "Q32013","Q42013","Q12014","Q22014","Q32014","Q42014",
    "Q12015","Q22015","Q32015","Q42015","Q12016","Q22016","Q32016","Q42016",
    "Q12017","Q22017","Q32017","Q42017","Q12018","Q22018","Q32018","Q42018",
    "Q12019","Q22019","Q32019","Q42019","Q12020","Q22020","Q32020","Q42020",
    "Q12021","Q22021","Q32021","Q42021","Q12022","Q22022","Q32022","Q42022",
    "Q12023","Q22023","Q32023","Q42023","Q12024","Q22024","Q32024","Q42024",
    "Q12025","Q22025","Q32025","Q42025",
]

STATES = ["NSW","VIC","QLD","WA","SA","TAS","ACT","NT"]

ARIA_CATEGORIES = [
    "Major Cities of Australia",
    "Inner Regional Australia",
    "Outer Regional Australia",
    "Remote Australia",
    "Very Remote Australia",
]

# Quarters where ARIA source data is missing — set by_aria to None so charts
# interpolate cleanly rather than showing a false zero-gap.
# Source data gaps: Q2 2018 through Q3 2021 (inclusive).
ARIA_NULL_QUARTERS = set([
    "Q22018","Q32018","Q42018",
    "Q12019","Q22019","Q32019","Q42019",
    "Q12020","Q22020","Q32020","Q42020",
    "Q12021","Q22021","Q32021",
])

def quarter_to_date(q):
    qnum = int(q[1])
    year = int(q[2:])
    month = {1:3, 2:6, 3:9, 4:12}[qnum]
    return f"{year}-{month:02d}-01"

def quarter_label(q):
    return f"Q{q[1]} {q[2:]}"

def quarter_year(q):
    """Return (qnum, year) as ints."""
    return int(q[1]), int(q[2:])

def date_to_quarter_key(date_val):
    """
    Convert a date (or string) to a quarter key like 'Q12019'.
    Returns None if unparseable.
    """
    try:
        if pd.isnull(date_val):
            return None
        dt = pd.to_datetime(date_val, errors="coerce")
        if pd.isnull(dt):
            return None
        qnum = (dt.month - 1) // 3 + 1
        return f"Q{qnum}{dt.year}"
    except Exception:
        return None


# ---------------------------------------------------------------------------
# ABS Population data loading
# ---------------------------------------------------------------------------

def load_abs_population():
    """
    Load national under-5 population (Persons 0-4 years) from ABS Population
    and People Database, Table 1.

    Returns a dict keyed by calendar year (int): {2019: 1554029, ...}

    Data is annual (June 30 each year), available from 2019 onwards.
    The ABS file has columns split across two header rows; the column we want
    is 'Persons - 0-4 years (no.)'.
    """
    if not ABS_POP.exists():
        print(f"  WARNING: ABS population file not found at {ABS_POP}")
        print("  Supply/demand ratio will be omitted from output.")
        return {}

    print(f"  Loading ABS population data from {ABS_POP.name} ...")
    try:
        df = pd.read_excel(ABS_POP, sheet_name="Table 1", header=6, engine="openpyxl",
                           # openpyxl may raise on external links — catch below
                           )
    except Exception:
        # Fallback: try with xlrd or ignore_ext
        try:
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                df = pd.read_excel(ABS_POP, sheet_name="Table 1", header=6)
        except Exception as e:
            print(f"  WARNING: Could not read ABS population file: {e}")
            return {}

    # Filter to national row (Code == 'AUS')
    nat = df[df["Code"] == "AUS"][["Year", "Persons - 0-4 years (no.)"]].copy()
    nat.columns = ["year", "pop_0_4"]
    nat["year"] = pd.to_numeric(nat["year"], errors="coerce")
    nat["pop_0_4"] = pd.to_numeric(nat["pop_0_4"], errors="coerce")
    nat = nat.dropna()

    result = {int(row.year): int(row.pop_0_4) for _, row in nat.iterrows()}
    print(f"  ABS data loaded: years {sorted(result.keys())}")
    return result


def interpolate_under5_population(abs_data, quarter_key):
    """
    Return an estimated national under-5 population for the given quarter,
    by linear interpolation between annual June-30 data points.

    ABS data is as-at June 30 each year, so we map:
      Q2 YYYY  -> exactly the June 30 value for that year
      Q3 YYYY  -> 25% of the way from YYYY to YYYY+1
      Q4 YYYY  -> 50% of the way from YYYY to YYYY+1
      Q1 YYYY  -> 75% of the way from YYYY-1 to YYYY  (i.e. the March quarter)

    Returns None if the quarter falls outside the available data range.
    """
    if not abs_data:
        return None

    qnum, year = quarter_year(quarter_key)

    # Map quarter to a fractional year position (June 30 = year + 0.5)
    # Q1 = March    -> year + 0.25  (mid-way through first half)
    # Q2 = June     -> year + 0.5   (exactly June 30)
    # Q3 = September -> year + 0.75
    # Q4 = December  -> year + 1.0  (year-end, half-way to next June)
    frac_map = {1: 0.25, 2: 0.5, 3: 0.75, 4: 1.0}
    frac_year = year + frac_map[qnum]

    # ABS annual data is as-at June 30 (year + 0.5 in our scale)
    years_available = sorted(abs_data.keys())
    if not years_available:
        return None

    # Build lookup: fractional year -> population
    pop_by_frac = {y + 0.5: abs_data[y] for y in years_available}
    fracs = sorted(pop_by_frac.keys())

    min_frac = fracs[0]
    max_frac = fracs[-1]

    if frac_year < min_frac or frac_year > max_frac + 0.5:
        # Before 2019 data, or beyond end of ABS coverage — no estimate
        return None

    # Find bracketing data points for interpolation
    lower_frac = None
    upper_frac = None
    for f in fracs:
        if f <= frac_year:
            lower_frac = f
        if f >= frac_year and upper_frac is None:
            upper_frac = f

    if lower_frac is None:
        return int(pop_by_frac[upper_frac])
    if upper_frac is None or upper_frac == lower_frac:
        return int(pop_by_frac[lower_frac])

    # Linear interpolation
    t = (frac_year - lower_frac) / (upper_frac - lower_frac)
    pop_lower = pop_by_frac[lower_frac]
    pop_upper = pop_by_frac[upper_frac]
    estimated = pop_lower + t * (pop_upper - pop_lower)
    return int(round(estimated))


# ---------------------------------------------------------------------------
# Per-sheet processing
# ---------------------------------------------------------------------------

def process_sheet(df, quarter_key=None):
    df.columns = [str(c).strip() for c in df.columns]
    df = df[df.iloc[:,0].notna()]

    col_map = {}
    for col in df.columns:
        cl = col.lower()
        if "overall rating" in cl or "overall nqs" in cl:
            col_map["overall"] = col
        elif "managing jurisdiction" in cl or col.upper() in STATES:
            col_map["state"] = col
        elif "provider management" in cl or "management type" in cl:
            col_map["mgmt"] = col
        elif "maximum total places" in cl or "approved places" in cl:
            col_map["places"] = col
        elif col.strip() == "ARIA+":
            col_map["aria"] = col
        elif "approval date" in cl or "approvaldate" in cl or "serviceapprovalgranteddate" in cl or "service approval granted date" in cl:
            col_map["approval_date"] = col

    # Also check explicit ARIA+ column
    if "ARIA+" in df.columns:
        col_map["aria"] = "ARIA+"

    if "overall" not in col_map:
        return None

    overall_col      = col_map["overall"]
    state_col        = col_map.get("state")
    mgmt_col         = col_map.get("mgmt")
    places_col       = col_map.get("places")
    aria_col         = col_map.get("aria")
    approval_date_col = col_map.get("approval_date")

    # Filter to LDC only
    ldc_cols = [c for c in df.columns if "long day" in c.lower() or "centre-based" in c.lower()]
    if ldc_cols:
        ldc_mask = df[ldc_cols[0]].astype(str).str.upper().isin(["YES","Y","TRUE","1"])
        df_ldc = df[ldc_mask]
    else:
        df_ldc = df

    total = len(df_ldc)
    if total == 0:
        return None

    # NQS distribution
    ratings   = df_ldc[overall_col].astype(str).str.strip()
    exceeding = int((ratings == "Exceeding NQS").sum())
    meeting   = int((ratings == "Meeting NQS").sum())
    working   = int((ratings == "Working Towards NQS").sum())
    sig_imp   = int(ratings.str.contains("Significant", na=False).sum())

    # Places
    total_places = 0
    if places_col:
        try:
            total_places = int(pd.to_numeric(df_ldc[places_col], errors="coerce").sum())
        except Exception:
            pass

    # By state
    by_state = {}
    if state_col:
        for state in STATES:
            mask = df_ldc[state_col].astype(str).str.strip().str.upper() == state
            by_state[state] = int(mask.sum())

    # NFP vs for-profit
    nfp_count = 0
    fp_count  = 0
    if mgmt_col:
        mgmt = df_ldc[mgmt_col].astype(str).str.lower()
        nfp_count = int(mgmt.str.contains("not.for.profit|community|church|government|local gov", na=False).sum())
        fp_count  = int(mgmt.str.contains("private for profit|for.profit", na=False).sum())

    # ARIA+ remoteness breakdown
    # For quarters in the known data gap, emit None so dashboard interpolates.
    by_aria = None
    if quarter_key and quarter_key.upper() in ARIA_NULL_QUARTERS:
        by_aria = None  # explicit null — chart will interpolate
    elif aria_col and aria_col in df_ldc.columns:
        by_aria = {}
        for cat in ARIA_CATEGORIES:
            count = int((df_ldc[aria_col].astype(str).str.strip() == cat).sum())
            by_aria[cat] = count
        # If all counts are zero, the column was present but empty — treat as null
        if sum(by_aria.values()) == 0:
            by_aria = None

    # New service approvals this quarter
    # Count LDC rows where serviceapprovalgranteddate falls within this quarter.
    new_approvals = None
    if approval_date_col and quarter_key:
        try:
            dates = pd.to_datetime(df_ldc[approval_date_col], errors="coerce")
            qnum, yr = quarter_year(quarter_key)
            q_start_month = {1:1, 2:4, 3:7, 4:10}[qnum]
            q_end_month   = {1:3, 2:6, 3:9, 4:12}[qnum]
            q_start = pd.Timestamp(yr, q_start_month, 1)
            q_end   = pd.Timestamp(yr, q_end_month, 1) + pd.offsets.MonthEnd(0)
            new_approvals = int(((dates >= q_start) & (dates <= q_end)).sum())
        except Exception as e:
            new_approvals = None

    return {
        "total_ldc":      total,
        "total_places":   total_places,
        "exceeding":      exceeding,
        "meeting":        meeting,
        "working":        working,
        "sig_imp":        sig_imp,
        "by_state":       by_state,
        "by_aria":        by_aria,       # None for gap quarters; dict otherwise
        "nfp":            nfp_count,
        "forprofit":      fp_count,
        "new_approvals":  new_approvals, # count of new LDC approvals this quarter
    }


# ---------------------------------------------------------------------------
# Main build
# ---------------------------------------------------------------------------

def build():
    print("=== Building sector history from NQAITS data ===")
    print(f"Source: {NQS_FILE.name}")

    if not NQS_FILE.exists():
        print(f"ERROR: {NQS_FILE} not found")
        return

    # Load ABS population data for supply/demand ratio
    abs_pop = load_abs_population()

    xl = pd.ExcelFile(NQS_FILE)
    available = {s.replace("data","").upper(): s for s in xl.sheet_names if s.startswith("Q")}
    print(f"Quarters available: {len(available)}")

    history = []
    for q in QUARTER_SHEETS:
        sheet_key  = q.upper()
        sheet_name = available.get(sheet_key)
        if not sheet_name:
            continue

        try:
            df = pd.read_excel(NQS_FILE, sheet_name=sheet_name, dtype=str)
            metrics = process_sheet(df, quarter_key=q)
            if metrics:
                # Compute supply/demand ratio: licensed places per 100 children under 5
                under5_pop   = interpolate_under5_population(abs_pop, q)
                supply_demand_ratio = None
                if under5_pop and under5_pop > 0 and metrics["total_places"] > 0:
                    supply_demand_ratio = round(
                        metrics["total_places"] / under5_pop * 100, 2
                    )

                entry = {
                    "quarter":              quarter_label(q),
                    "date":                 quarter_to_date(q),
                    "under5_pop":           under5_pop,           # national 0-4 ERP (interpolated)
                    "supply_demand_ratio":  supply_demand_ratio,  # licensed places per 100 under-5
                    **metrics
                }
                history.append(entry)
                if len(history) % 10 == 0 or len(history) <= 3:
                    aria_summary = (
                        f"ARIA: {sum(entry['by_aria'].values()):,} classified"
                        if entry.get("by_aria") else "ARIA: null (gap)"
                    )
                    print(f"  {quarter_label(q)}: {metrics['total_ldc']:,} LDC, "
                          f"{metrics['exceeding']:,} Exceeding, "
                          f"{aria_summary}, "
                          f"ratio={supply_demand_ratio}, "
                          f"new_approvals={metrics['new_approvals']}")
        except Exception as e:
            print(f"  ERROR {q}: {e}")

    print(f"\nProcessed {len(history)} quarters")

    # Summarise new_approvals coverage
    n_with_approvals = sum(1 for h in history if h.get("new_approvals") is not None)
    print(f"Quarters with new_approvals data: {n_with_approvals}/{len(history)}")
    total_approvals_recorded = sum(h["new_approvals"] for h in history if h.get("new_approvals") is not None)
    print(f"Total new LDC approvals across all quarters: {total_approvals_recorded:,}")

    # Summarise supply/demand ratio coverage
    n_with_ratio = sum(1 for h in history if h.get("supply_demand_ratio") is not None)
    print(f"Quarters with supply/demand ratio: {n_with_ratio}/{len(history)}")

    out = {
        "generated": str(pd.Timestamp.now().date()),
        "quarters":  len(history),
        "history":   history,
    }
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved: {OUT_FILE}")

    if history:
        latest = history[-1]
        print(f"\nLatest ({latest['quarter']}):")
        print(f"  LDC services:         {latest['total_ldc']:,}")
        print(f"  Exceeding NQS:        {latest['exceeding']:,} ({round(latest['exceeding']/latest['total_ldc']*100)}%)")
        print(f"  Under-5 population:   {latest.get('under5_pop', 'N/A')}")
        print(f"  Supply/demand ratio:  {latest.get('supply_demand_ratio', 'N/A')} places per 100 children")
        print(f"  New approvals (qtr):  {latest.get('new_approvals', 'N/A')}")
        print(f"  ARIA breakdown:")
        if latest.get("by_aria"):
            for k, v in latest["by_aria"].items():
                print(f"    {k}: {v:,}")
        else:
            print("    null (gap quarter)")


if __name__ == "__main__":
    build()
