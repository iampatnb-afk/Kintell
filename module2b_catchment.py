"""
module2b_catchment.py — Catchment & Market Context Enrichment
Remara Agent | Part of run_daily.py chain

INPUT:  leads_enriched.json  (from module2_enrichment.py)
OUTPUT: leads_catchment.json (enriched lead cards with catchment data)

Catchment block includes:
  - SA2 code + name (postcode->SA2 via fuzzy-matched concordance)
  - Population 0-4: latest value + CAGR growth trend
  - Median household income: latest value + CAGR growth trend
  - Estimated CCS subsidy rate at median income + gap fee sensitivity
  - SEIFA IRSD + IRSAD deciles (socio-economic indicators)
  - Supply ratio: LDC licensed places / under-5 population
  - NFP ratio: % of LDC centres in SA2 that are not-for-profit
  - Average daily fee (StartingBlocks stub)
  - Contact matches from childcare contacts databases
  - Qikreport-style summary card

Required files in abs_data/:
  Population and People Database.xlsx
  Income Database.xlsx
  Family and Community Database.xlsx
  postcode_to_sa2_concordance.csv  (pre-built via build_concordance.py)

Run standalone:
  python module2b_catchment.py
  python module2b_catchment.py --live
"""

import json
import sys
import time
import logging
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

import pandas as pd
from rapidfuzz import fuzz, process

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

BASE_DIR          = Path(__file__).parent
ABS_DIR           = BASE_DIR / "abs_data"
DATA_DIR          = BASE_DIR / "data"
INPUT_FILE        = BASE_DIR / "leads_enriched.json"
ALL_OPERATORS_FILE = BASE_DIR / "operators_target_list.json"
OUTPUT_FILE       = BASE_DIR / "leads_catchment.json"

POP_FILE     = ABS_DIR / "Population and People Database.xlsx"
INCOME_FILE  = ABS_DIR / "Income Database.xlsx"
SEIFA_FILE   = ABS_DIR / "Family and Community Database.xlsx"
CONCORDANCE  = ABS_DIR / "postcode_to_sa2_concordance.csv"

ABS_HEADER_ROW = 6

# Confirmed exact column names
POP_0_4_COL  = "Persons - 0-4 years (no.)"
INCOME_COL   = "Median equivalised total household income (weekly) ($)"
IRSD_COL     = "SEIFA Index of relative socio-economic disadvantage (IRSD) - rank within Australia (decile)"
IRSAD_COL    = "SEIFA Index of relative socio-economic advantage and disadvantage (IRSAD) - rank within Australia (decile)"

# CAGR periods
POP_BASE_YEAR   = "2020"
POP_END_YEAR    = "2024"
INC_BASE_YEAR   = "2016"   # Census year
INC_END_YEAR    = "2021"   # Census year (income only updates every 5 years)

# CCS income thresholds (2024-25 rates, weekly household income)
# Source: Services Australia CCS rate table
CCS_RATE_TABLE = [
    (0,      769,   1.00),   # $0 - $40k annual: 90% CCS (capped at 90%)
    (769,    1346,  0.90),   # $40k - $70k: 90% tapering to ~80%
    (1346,   1923,  0.80),   # $70k - $100k
    (1923,   2692,  0.72),   # $100k - $140k
    (2692,   3654,  0.60),   # $140k - $190k
    (3654,   4808,  0.50),   # $190k - $250k
    (4808,   5769,  0.35),   # $250k - $300k
    (5769,   9615,  0.20),   # $300k - $500k
    (9615,   99999, 0.00),   # $500k+: no subsidy
]
CCS_HOURLY_CAP = 14.29   # 2024-25 LDC hourly cap ($/hr)
HOURS_PER_DAY  = 10.5    # standard LDC day

FUZZY_THRESHOLD = 75

RATIO_TIERS = {
    "undersupplied": (0.0,  0.35),
    "balanced":      (0.35, 0.55),
    "supplied":      (0.55, 0.75),
    "oversupplied":  (0.75, 99.0),
}

# NFP identifier keywords in provider legal name
NFP_KEYWORDS = [
    "incorporated", " inc ", "association", "community", "council",
    "church", "diocese", "parish", "ymca", "salvation", "catholic",
    "anglican", "uniting", "baptist", "lutheran", "presbyterian",
    "limited by guarantee", "cooperative", "co-operative",
    "neighbourhood", "aboriginal", "indigenous", "trust",
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# CCS SUBSIDY CALCULATOR
# ─────────────────────────────────────────────

def estimate_ccs_rate(weekly_household_income: float) -> float:
    """
    Estimate CCS subsidy rate (0.0-1.0) for a given weekly household income.
    Uses 2024-25 Services Australia rate table.
    """
    for lo, hi, rate in CCS_RATE_TABLE:
        if lo <= weekly_household_income < hi:
            return rate
    return 0.0


def estimate_gap_fee(daily_fee: float, ccs_rate: float) -> float:
    """
    Estimate family out-of-pocket gap fee per day.
    CCS is applied to the lower of: actual hourly fee or CCS hourly cap.
    """
    hourly_fee = daily_fee / HOURS_PER_DAY
    subsidised_hourly = min(hourly_fee, CCS_HOURLY_CAP)
    subsidy_per_day = subsidised_hourly * HOURS_PER_DAY * ccs_rate
    return round(daily_fee - subsidy_per_day, 2)


def fee_sensitivity_label(irsd_decile: Optional[int], ccs_rate: float) -> str:
    """
    Classify fee sensitivity based on IRSD decile and CCS rate.
    IRSD decile 1 = most disadvantaged, 10 = least disadvantaged.
    """
    if irsd_decile is None:
        return "unknown"
    if irsd_decile <= 3:
        return "high"       # disadvantaged catchment, very price sensitive
    if irsd_decile <= 6:
        return "moderate"
    if ccs_rate < 0.35:
        return "low"        # affluent, minimal subsidy, can absorb fee rises
    return "moderate"


# ─────────────────────────────────────────────
# ABS DATA LOADER — multi-year timeseries
# ─────────────────────────────────────────────

def load_abs_timeseries(filepath: Path, value_col: str) -> pd.DataFrame:
    """
    Load ABS Data by Region Excel file as a wide timeseries.
    Returns DataFrame indexed by SA2_CODE with year columns + SA2_NAME.
    """
    if not filepath.exists():
        log.warning(f"ABS file not found: {filepath.name}")
        return pd.DataFrame()

    try:
        df = pd.read_excel(
            filepath,
            sheet_name="Table 1",
            header=ABS_HEADER_ROW,
            dtype=str,
            engine="openpyxl",
        )
        df.columns = [str(c).strip() for c in df.columns]

        if "Code" not in df.columns:
            log.warning(f"'Code' column not found in {filepath.name}")
            return pd.DataFrame()

        if value_col not in df.columns:
            log.warning(f"Column not found in {filepath.name}: '{value_col}'")
            return pd.DataFrame()

        df["Code"] = df["Code"].astype(str).str.strip()
        df = df[df["Code"].str.match(r"^\d{9}$")].copy()
        df["Year"] = df["Year"].astype(str).str.strip()
        df[value_col] = pd.to_numeric(df[value_col], errors="coerce")

        years = sorted(df["Year"].dropna().unique())
        log.info(f"{filepath.name}: years = {years}")

        pivot = (
            df[df[value_col].notna()]
              .pivot_table(index="Code", columns="Year", values=value_col, aggfunc="first")
        )
        pivot.index.name = "SA2_CODE"

        # Add SA2 name
        latest_yr = years[-1]
        name_map = (
            df[df["Year"] == latest_yr]
              .drop_duplicates("Code")
              .set_index("Code")["Label"]
        )
        pivot["SA2_NAME"] = name_map
        log.info(f"{filepath.name}: {len(pivot):,} SA2 areas loaded")
        return pivot

    except Exception as e:
        log.warning(f"Failed to load {filepath.name}: {e}")
        return pd.DataFrame()


def load_abs_single_year(filepath: Path, value_cols: list, year: str = "2021") -> pd.DataFrame:
    """
    Load a single year of ABS data for multiple columns.
    Returns DataFrame indexed by SA2_CODE.
    """
    if not filepath.exists():
        log.warning(f"ABS file not found: {filepath.name}")
        return pd.DataFrame()

    try:
        df = pd.read_excel(
            filepath,
            sheet_name="Table 1",
            header=ABS_HEADER_ROW,
            dtype=str,
            engine="openpyxl",
        )
        df.columns = [str(c).strip() for c in df.columns]
        df["Code"] = df["Code"].astype(str).str.strip()
        df = df[df["Code"].str.match(r"^\d{9}$")].copy()
        df["Year"] = df["Year"].astype(str).str.strip()

        # Find best year with real data
        available_cols = [c for c in value_cols if c in df.columns]
        if not available_cols:
            log.warning(f"None of {value_cols} found in {filepath.name}")
            return pd.DataFrame()

        # Try requested year, fall back to most recent with data
        test_yr = year
        if test_yr not in df["Year"].unique():
            years_with_data = sorted(df["Year"].unique())
            test_yr = years_with_data[-1]

        sub = df[df["Year"] == test_yr].copy()
        for c in available_cols:
            sub[c] = pd.to_numeric(sub[c], errors="coerce")

        sub = sub.dropna(subset=available_cols, how="all")
        result = sub.set_index("Code")[available_cols + ["Label"]]
        result.index.name = "SA2_CODE"
        log.info(f"{filepath.name}: {len(result):,} SA2s loaded (year={test_yr})")
        return result

    except Exception as e:
        log.warning(f"Failed to load {filepath.name}: {e}")
        return pd.DataFrame()


def get_latest_value(ts: pd.DataFrame, sa2_code: str) -> tuple:
    """Get most recent non-null value. Returns (value, year) or (None, None)."""
    if ts.empty or sa2_code not in ts.index:
        return None, None
    row = ts.loc[sa2_code]
    year_cols = sorted([c for c in ts.columns if str(c).isdigit()], reverse=True)
    for yr in year_cols:
        val = row.get(yr)
        if pd.notna(val):
            return float(val), yr
    return None, None


def calc_cagr(ts: pd.DataFrame, sa2_code: str, base_year: str, end_year: str) -> Optional[float]:
    """Calculate CAGR % between two years for an SA2."""
    if ts.empty or sa2_code not in ts.index:
        return None
    row = ts.loc[sa2_code]
    base_val = pd.to_numeric(row.get(base_year), errors="coerce")
    end_val  = pd.to_numeric(row.get(end_year),  errors="coerce")
    if pd.isna(base_val) or pd.isna(end_val) or base_val <= 0:
        return None
    n = int(end_year) - int(base_year)
    if n <= 0:
        return None
    return round(((end_val / base_val) ** (1 / n) - 1) * 100, 2)


def growth_arrow(cagr: Optional[float]) -> str:
    if cagr is None: return ""
    if cagr >= 3.0:  return f"▲▲ +{cagr:.1f}% p.a."
    if cagr >= 1.0:  return f"▲ +{cagr:.1f}% p.a."
    if cagr >= -1.0: return f"-> {cagr:+.1f}% p.a."
    return f"▼ {cagr:+.1f}% p.a."


def growth_label(cagr: Optional[float]) -> str:
    if cagr is None: return "unknown"
    if cagr >= 3.0:  return "strong_growth"
    if cagr >= 1.0:  return "growth"
    if cagr >= -1.0: return "stable"
    return "declining"


# ─────────────────────────────────────────────
# CONCORDANCE
# ─────────────────────────────────────────────

def load_concordance() -> pd.DataFrame:
    if not CONCORDANCE.exists():
        log.warning(f"Concordance not found: {CONCORDANCE}")
        log.warning("Run build_concordance.py first to generate it.")
        return pd.DataFrame()
    try:
        df = pd.read_csv(CONCORDANCE, dtype=str)
        log.info(f"Concordance: {len(df):,} postcodes loaded")
        return df
    except Exception as e:
        log.warning(f"Could not load concordance: {e}")
        return pd.DataFrame()


def postcode_to_sa2(postcode: str, concordance: pd.DataFrame) -> dict:
    if concordance.empty or not postcode:
        return {}
    pc = str(postcode).strip().zfill(4)
    row = concordance[concordance["POSTCODE"] == pc]
    if row.empty:
        return {}
    r = row.iloc[0]
    code = r.get("SA2_CODE")
    name = r.get("SA2_NAME")
    if pd.isna(code) or not code:
        return {}
    return {"sa2_code": str(code).strip(), "sa2_name": str(name).strip()}


# ─────────────────────────────────────────────
# SUPPLY + NFP RATIOS FROM ACECQA
# ─────────────────────────────────────────────

def is_nfp(provider_name: str) -> bool:
    """Detect NFP operator from legal name keywords."""
    name = str(provider_name).lower()
    return any(kw in name for kw in NFP_KEYWORDS)


def compute_supply_and_nfp(concordance: pd.DataFrame) -> dict:
    """
    Compute per-SA2 LDC supply stats, NFP ratio, and full centre list.
    Returns: {sa2_code: {total_centres, total_places, nfp_count, nfp_ratio, centres[]}}
    Each centre in centres[]: name, operator, address, phone, places, nqs, approval_no
    """
    snap_path = DATA_DIR / "services_snapshot.csv"
    if not snap_path.exists():
        log.warning("services_snapshot.csv not found")
        return {}

    try:
        svc = pd.read_csv(snap_path, dtype=str, low_memory=False)
        svc.columns = [c.strip().lower() for c in svc.columns]

        if "long_day_care" in svc.columns:
            svc = svc[svc["long_day_care"].str.upper() == "YES"]

        svc["postcode"] = svc["postcode"].astype(str).str.strip().str.zfill(4)
        svc["places"] = pd.to_numeric(
            svc.get("numberofapprovedplaces", pd.Series(dtype=str)),
            errors="coerce"
        ).fillna(0)

        svc["is_nfp"] = svc.get("providerlegalname", pd.Series(dtype=str)).apply(is_nfp)

        # Kinder approval flag
        svc["has_kinder"] = (
            (svc.get("preschool/kindergarten_-_stand_alone", pd.Series(dtype=str))
                .fillna("").str.upper() == "YES") |
            (svc.get("preschool/kindergarten_-_part_of_a_school", pd.Series(dtype=str))
                .fillna("").str.upper() == "YES")
        )

        merged = svc.merge(
            concordance[["POSTCODE", "SA2_CODE"]].dropna(),
            left_on="postcode", right_on="POSTCODE", how="left"
        )

        supply = {}
        for sa2, grp in merged.groupby("SA2_CODE"):
            if pd.isna(sa2) or not sa2:
                continue
            total     = len(grp)
            nfp_count = int(grp["is_nfp"].sum())

            # Build centre list — sorted by places descending
            centres = []
            for _, row in grp.sort_values("places", ascending=False).iterrows():
                phone = str(row.get("phone", "") or "").strip()
                # Clean phone — remove .0 suffix from float conversion
                if phone.endswith(".0"):
                    phone = phone[:-2]
                centres.append({
                    "service_name":      str(row.get("servicename", "") or "").strip(),
                    "operator_name":     str(row.get("providerlegalname", "") or "").strip(),
                    "service_address":   str(row.get("serviceaddress", "") or "").strip(),
                    "suburb":            str(row.get("suburb", "") or "").strip(),
                    "state":             str(row.get("state", "") or "").strip(),
                    "postcode":          str(row.get("postcode", "") or "").strip(),
                    "phone":             phone,
                    "approved_places":   int(row["places"]),
                    "nqs_rating":        str(row.get("overallrating", "") or "").strip(),
                    "service_approval":  str(row.get("serviceapprovalnumber", "") or "").strip(),
                    "is_nfp":            bool(row["is_nfp"]),
                    "has_kinder":        bool(row.get("has_kinder", False)),
                    "matched_contacts":  [],  # filled in enrich step
                })

            kinder_count = int(grp["has_kinder"].sum()) if "has_kinder" in grp.columns else 0
            supply[str(sa2)] = {
                "total_centres":  total,
                "total_places":   int(grp["places"].sum()),
                "nfp_count":      nfp_count,
                "nfp_ratio":      round(nfp_count / total, 3) if total > 0 else 0,
                "kinder_count":   kinder_count,
                "kinder_ratio":   round(kinder_count / total, 3) if total > 0 else 0,
                "centres":        centres,
            }

        log.info(f"Supply map: {len(supply):,} SA2 areas")
        return supply

    except Exception as e:
        log.warning(f"Failed to compute supply/NFP: {e}")
        return {}


# ─────────────────────────────────────────────
# CONTACT MATCHING
# ─────────────────────────────────────────────

def load_contact_databases() -> pd.DataFrame:
    frames = []
    apollo = ABS_DIR / "childcare-contacts-australia.csv"
    industry = ABS_DIR / "Childcare Contact List_041225.xlsx"

    if apollo.exists():
        try:
            df = pd.read_csv(apollo, dtype=str)
            df.columns = [c.strip() for c in df.columns]
            df["source"] = "apollo"
            df = df.rename(columns={
                "First Name": "first_name", "Last Name": "last_name",
                "Title": "title", "Company Name": "company_name",
                "Email": "email", "Mobile Phone": "mobile",
                "Work Direct Phone": "work_phone",
                "Person Linkedin Url": "linkedin",
                "City": "suburb", "State": "state",
            })
            frames.append(df)
            log.info(f"Apollo contacts: {len(df):,}")
        except Exception as e:
            log.warning(f"Apollo CSV: {e}")

    if industry.exists():
        try:
            df = pd.read_excel(industry, dtype=str, engine="openpyxl")
            df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
            df["source"] = "industry"
            frames.append(df)
            log.info(f"Industry contacts: {len(df):,}")
        except Exception as e:
            log.warning(f"Industry XLS: {e}")

    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def match_contacts(operator_name: str, suburb: str, contacts_df: pd.DataFrame) -> list:
    if contacts_df.empty or not operator_name:
        return []
    company_col = next(
        (c for c in ["company_name", "company", "organisation"] if c in contacts_df.columns), None
    )
    if not company_col:
        return []
    suburb_col = next(
        (c for c in ["suburb", "city", "location"] if c in contacts_df.columns), None
    )
    pool = contacts_df
    if suburb_col and suburb:
        mask = contacts_df[suburb_col].fillna("").str.lower().str.contains(suburb.lower(), na=False)
        if mask.sum() > 0:
            pool = contacts_df[mask]

    names   = pool[company_col].fillna("").tolist()
    matches = process.extract(operator_name, names, scorer=fuzz.token_set_ratio, limit=5)
    KEEP = ["first_name","last_name","title","company_name","email",
            "mobile","work_phone","linkedin","source","match_score"]
    results = []
    for _, score, idx in matches:
        if score < FUZZY_THRESHOLD:
            continue
        row = pool.iloc[idx].to_dict()
        row["match_score"] = score
        results.append({k: v for k, v in row.items() if k in KEEP and v and str(v) != "nan"})
    return results


# ─────────────────────────────────────────────
# STARTINGBLOCKS (STUB)
# ─────────────────────────────────────────────

def scrape_startingblocks_fees(service_name: str, suburb: str) -> dict:
    """Stub — returns None. Replace with live scraper when ready."""
    return {"sb_daily_fee": None, "sb_vacancy": None, "sb_url": None}


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def supply_tier(ratio: Optional[float]) -> str:
    if ratio is None: return "unknown"
    for label, (lo, hi) in RATIO_TIERS.items():
        if lo <= ratio < hi:
            return label
    return "oversupplied"


def seifa_label(decile: Optional[int]) -> str:
    if decile is None: return "unknown"
    if decile <= 2:  return "highly_disadvantaged"
    if decile <= 4:  return "disadvantaged"
    if decile <= 6:  return "average"
    if decile <= 8:  return "advantaged"
    return "highly_advantaged"


def format_qikreport(lead: dict) -> str:
    c = lead.get("catchment", {})
    pop_cagr = c.get("pop_0_4_cagr")
    inc_cagr = c.get("income_cagr")
    ratio    = c.get("supply_ratio")
    irsd     = c.get("irsd_decile")
    irsad    = c.get("irsad_decile")
    ccs_rate = c.get("est_ccs_rate")
    gap_fee  = c.get("est_gap_fee_per_day")
    nfp_pct  = c.get("nfp_ratio")

    lines = [
        f"-- CATCHMENT REPORT: {lead.get('service_name', 'Unknown')} --",
        f"  Suburb:          {lead.get('suburb', '?')}, {lead.get('state', '?')}",
        f"  SA2:             {c.get('sa2_name', 'n/a')}  [{c.get('sa2_code', '?')}]",
        f"",
        f"  DEMAND",
        f"  Under-5 pop:     {_fmt_int(c.get('pop_0_4'))} ({c.get('pop_year','?')})  "
            f"{growth_arrow(pop_cagr)} [{growth_label(pop_cagr).upper()}]",
        f"  Median income:   {_fmt_dollar(c.get('median_income_weekly_annual'))} p.a. "
            f"({c.get('income_year','?')})  {growth_arrow(inc_cagr)}",
        f"",
        f"  CCS & FEE SENSITIVITY",
        f"  Est. CCS rate:   {f'{ccs_rate*100:.0f}%' if ccs_rate is not None else 'n/a'} at median income",
        f"  Est. gap fee:    {_fmt_dollar(gap_fee)}/day  "
            f"[{c.get('fee_sensitivity','?').upper()} sensitivity]",
        f"  IRSD decile:     {irsd or 'n/a'}/10  [{seifa_label(irsd).upper()}]",
        f"  IRSAD decile:    {irsad or 'n/a'}/10",
        f"",
        f"  SUPPLY",
        f"  Centres (SA2):   {c.get('total_centres', 'n/a')} LDC  "
            f"({f'{nfp_pct*100:.0f}%' if nfp_pct is not None else '?'} NFP  |  "
            f"{f"{c.get('kinder_ratio',0)*100:.0f}%" if c.get('kinder_ratio') is not None else '?'} kinder-approved)",
        f"  Lead kinder:     {'Yes' if c.get('lead_has_kinder') else 'No'}",
        f"  Licensed places: {_fmt_int(c.get('total_licensed_places'))}",
        f"  Supply ratio:    {_fmt_ratio(ratio)}x  [{supply_tier(ratio).upper()}]",
        f"",
        f"  Avg daily fee:   {_fmt_dollar(c.get('avg_daily_fee'))}",
        f"  Contacts found:  {len(lead.get('matched_contacts', []))}",
    ]
    return "\n".join(lines)


def _fmt_int(v) -> str:
    try: return f"{int(v):,}"
    except: return "n/a"

def _fmt_dollar(v) -> str:
    try: return f"${int(v):,}"
    except: return "n/a"

def _fmt_ratio(v) -> str:
    try: return f"{float(v):.2f}"
    except: return "n/a"


# ─────────────────────────────────────────────
# ENRICH SINGLE LEAD
# ─────────────────────────────────────────────

def enrich_lead_catchment(
    lead: dict,
    concordance: pd.DataFrame,
    pop_ts: pd.DataFrame,
    inc_ts: pd.DataFrame,
    seifa_df: pd.DataFrame,
    supply_map: dict,
    contacts_df: pd.DataFrame,
    avg_daily_fee: Optional[float] = None,
    dry_run: bool = True,
) -> dict:
    postcode = str(lead.get("postcode", "") or "").strip()
    suburb   = str(lead.get("suburb", "") or "").strip()
    operator = str(lead.get("operator_name", "") or lead.get("service_name", "") or "").strip()

    # SA2 lookup
    sa2_info = postcode_to_sa2(postcode, concordance)
    sa2_code = sa2_info.get("sa2_code", "")
    sa2_name = sa2_info.get("sa2_name", "")

    # Population + CAGR
    pop_0_4, pop_year   = get_latest_value(pop_ts, sa2_code)
    pop_cagr            = calc_cagr(pop_ts, sa2_code, POP_BASE_YEAR, POP_END_YEAR)

    # Income + CAGR
    inc_weekly, inc_year = get_latest_value(inc_ts, sa2_code)
    inc_cagr             = calc_cagr(inc_ts, sa2_code, INC_BASE_YEAR, INC_END_YEAR)
    inc_annual           = (float(inc_weekly) * 52) if inc_weekly is not None else None

    # SEIFA
    irsd_decile  = None
    irsad_decile = None
    if not seifa_df.empty and sa2_code and sa2_code in seifa_df.index:
        row = seifa_df.loc[sa2_code]
        irsd_val  = row.get(IRSD_COL)
        irsad_val = row.get(IRSAD_COL)
        if pd.notna(irsd_val):
            irsd_decile  = int(float(irsd_val))
        if pd.notna(irsad_val):
            irsad_decile = int(float(irsad_val))

    # CCS estimate at median income
    ccs_rate = None
    est_gap  = None
    if inc_weekly is not None:
        ccs_rate = estimate_ccs_rate(float(inc_weekly))
        fee_to_use = avg_daily_fee or lead.get("daily_fee") or 143.0
        est_gap  = estimate_gap_fee(float(fee_to_use), ccs_rate)

    fee_sensitivity = fee_sensitivity_label(irsd_decile, ccs_rate or 0)

    # Supply + NFP
    supply        = supply_map.get(sa2_code, {})
    total_centres = supply.get("total_centres")
    total_places  = supply.get("total_places")
    nfp_count     = supply.get("nfp_count")
    nfp_ratio     = supply.get("nfp_ratio")

    # Supply ratio
    ratio = None
    if pop_0_4 and total_places and float(pop_0_4) > 0:
        ratio = float(total_places) / float(pop_0_4)

    # StartingBlocks
    sb = {} if dry_run else scrape_startingblocks_fees(operator, suburb)

    # Contacts for the lead itself
    contacts = match_contacts(operator, suburb, contacts_df)

    # Match contacts for competing centres in the catchment
    competing_centres = supply.get("centres", [])
    for centre in competing_centres:
        centre_matches = match_contacts(
            centre.get("operator_name", ""),
            centre.get("suburb", ""),
            contacts_df,
        )
        centre["matched_contacts"] = centre_matches

    catchment = {
        # Geography
        "sa2_code":                    sa2_code or None,
        "sa2_name":                    sa2_name or None,
        # Population
        "pop_0_4":                     int(pop_0_4) if pop_0_4 is not None else None,
        "pop_year":                    pop_year,
        "pop_0_4_cagr":                pop_cagr,
        "pop_growth_label":            growth_label(pop_cagr),
        # Income
        "median_income_weekly":        round(float(inc_weekly), 0) if inc_weekly is not None else None,
        "median_income_weekly_annual": round(float(inc_annual), 0) if inc_annual is not None else None,
        "income_year":                 inc_year,
        "income_cagr":                 inc_cagr,
        # CCS & Fee Sensitivity
        "est_ccs_rate":                round(ccs_rate, 2) if ccs_rate is not None else None,
        "est_gap_fee_per_day":         est_gap,
        "fee_sensitivity":             fee_sensitivity,
        # SEIFA
        "irsd_decile":                 irsd_decile,
        "irsad_decile":                irsad_decile,
        "irsd_label":                  seifa_label(irsd_decile),
        # Supply
        "total_centres":               total_centres,
        "total_licensed_places":       total_places,
        "nfp_count":                   nfp_count,
        "nfp_ratio":                   nfp_ratio,
        "kinder_count":                supply.get("kinder_count"),
        "kinder_ratio":                supply.get("kinder_ratio"),
        "lead_has_kinder":             lead.get("has_kinder", False),
        "competing_centres":           competing_centres,
        "supply_ratio":                round(ratio, 3) if ratio is not None else None,
        "supply_tier":                 supply_tier(ratio),
        # Fees
        "avg_daily_fee":               sb.get("sb_daily_fee"),
        "sb_vacancy":                  sb.get("sb_vacancy"),
        "sb_url":                      sb.get("sb_url"),
        "data_timestamp":              datetime.now(timezone.utc).isoformat(),
    }

    lead = lead.copy()
    lead["catchment"]        = catchment
    lead["matched_contacts"] = contacts
    lead["qikreport"]        = format_qikreport(lead)
    return lead


# ─────────────────────────────────────────────
# MAIN RUNNER
# ─────────────────────────────────────────────

def normalise_operator_to_leads(operators: list) -> list:
    """
    Explode operators_target_list.json (operator-level) into service-level
    lead records compatible with enrich_lead_catchment().

    Each operator has a 'centres' list. We create one lead record per centre,
    carrying through the operator-level fields needed for enrichment.
    """
    leads = []
    for op in operators:
        centres = op.get("centres", [])
        if not centres:
            # Operator with no centre detail — skip, can't enrich without postcode
            continue
        for centre in centres:
            lead = {
                # Service-level identity
                "service_name":          centre.get("service_name", op.get("legal_name", "")),
                "operator_name":         op.get("legal_name", ""),
                "suburb":                centre.get("suburb", ""),
                "state":                 centre.get("state", ""),
                "postcode":              str(centre.get("postcode", "") or "").strip(),
                "approved_places":       centre.get("places"),
                "service_approval_number": centre.get("approval_number", ""),
                "overall_rating":        centre.get("nqs_rating", ""),
                # Operator-level signals (carried through for dashboard use)
                "priority_tier":         op.get("priority_tier", ""),
                "score":                 op.get("score"),
                "product_fit":           op.get("product_fit", ""),
                "is_nfp":                op.get("is_nfp", False),
                "has_kinder":            op.get("has_kinder", False),
                "n_centres":             op.get("n_centres"),
                "total_places":          op.get("total_places"),
                "states":                op.get("states", []),
                "growing":               op.get("growing", False),
            }
            leads.append(lead)
    return leads


def run(dry_run: bool = True, use_all_operators: bool = False):
    log.info("=" * 55)
    log.info(f"module2b_catchment  [dry_run={dry_run}]  [all_operators={use_all_operators}]")
    log.info("=" * 55)

    if use_all_operators:
        if not ALL_OPERATORS_FILE.exists():
            log.error(f"operators_target_list.json not found: {ALL_OPERATORS_FILE}")
            sys.exit(1)
        with open(ALL_OPERATORS_FILE) as f:
            operators = json.load(f)
        log.info(f"Input: {len(operators)} operator groups from {ALL_OPERATORS_FILE.name}")
        leads = normalise_operator_to_leads(operators)
        log.info(f"Exploded to {len(leads)} individual centre records for enrichment")
    else:
        if not INPUT_FILE.exists():
            log.error(f"Input not found: {INPUT_FILE}")
            sys.exit(1)
        with open(INPUT_FILE) as f:
            leads = json.load(f)
        log.info(f"Input: {len(leads)} leads from {INPUT_FILE.name}")

    concordance = load_concordance()
    pop_ts      = load_abs_timeseries(POP_FILE, POP_0_4_COL)
    inc_ts      = load_abs_timeseries(INCOME_FILE, INCOME_COL)
    seifa_df    = load_abs_single_year(SEIFA_FILE, [IRSD_COL, IRSAD_COL], year="2021")
    supply_map  = compute_supply_and_nfp(concordance)
    contacts_df = load_contact_databases()

    log.info("Reference data summary:")
    log.info(f"  Concordance:  {len(concordance):,} postcodes")
    log.info(f"  Population:   {len(pop_ts):,} SA2s")
    log.info(f"  Income:       {len(inc_ts):,} SA2s")
    log.info(f"  SEIFA:        {len(seifa_df):,} SA2s")
    log.info(f"  Supply map:   {len(supply_map):,} SA2s")
    log.info(f"  Contacts:     {len(contacts_df):,} records")

    enriched = []
    for i, lead in enumerate(leads, 1):
        name = lead.get("service_name", lead.get("name", f"Lead {i}"))
        log.info(f"[{i}/{len(leads)}] {name}")
        try:
            el = enrich_lead_catchment(
                lead=lead,
                concordance=concordance,
                pop_ts=pop_ts,
                inc_ts=inc_ts,
                seifa_df=seifa_df,
                supply_map=supply_map,
                contacts_df=contacts_df,
                dry_run=dry_run,
            )
            enriched.append(el)
            print(el.get("qikreport", ""))
            print()
        except Exception as e:
            log.warning(f"  Error: {e}")
            import traceback
            log.warning(traceback.format_exc())
            lead.update({"catchment": {}, "matched_contacts": [], "qikreport": ""})
            enriched.append(lead)

        if not dry_run:
            time.sleep(2)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(enriched, f, indent=2, default=str)

    n = len(enriched)
    log.info("=" * 55)
    log.info(f"Output: {n} leads -> {OUTPUT_FILE.name}")
    log.info(f"  SA2 resolved:       {sum(1 for l in enriched if l.get('catchment',{}).get('sa2_code'))}/{n}")
    log.info(f"  Pop + CAGR:         {sum(1 for l in enriched if l.get('catchment',{}).get('pop_0_4_cagr') is not None)}/{n}")
    log.info(f"  Income + CAGR:      {sum(1 for l in enriched if l.get('catchment',{}).get('income_cagr') is not None)}/{n}")
    log.info(f"  SEIFA loaded:       {sum(1 for l in enriched if l.get('catchment',{}).get('irsd_decile') is not None)}/{n}")
    log.info(f"  CCS estimated:      {sum(1 for l in enriched if l.get('catchment',{}).get('est_ccs_rate') is not None)}/{n}")
    log.info(f"  Growing catchments: {sum(1 for l in enriched if l.get('catchment',{}).get('pop_growth_label') in ('growth','strong_growth'))}/{n}")
    log.info(f"  Undersupplied:      {sum(1 for l in enriched if l.get('catchment',{}).get('supply_tier')=='undersupplied')}/{n}")
    log.info(f"  Contacts matched:   {sum(1 for l in enriched if l.get('matched_contacts'))}/{n}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remara module2b -- catchment enrichment")
    parser.add_argument("--live", action="store_true", help="Enable live StartingBlocks scraping")
    parser.add_argument("--all",  action="store_true", help="Process all operators from operators_target_list.json (not just leads_enriched.json)")
    args = parser.parse_args()
    run(dry_run=not args.live, use_all_operators=args.all)
