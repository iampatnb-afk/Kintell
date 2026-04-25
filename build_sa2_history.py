"""
build_sa2_history.py
Extracts per-SA2 quarterly supply history from NQAITS data.
Outputs: data/sa2_history.json

For each SA2, produces aligned quarterly arrays:
  - quarters, dates
  - places:        licensed places per quarter
  - services:      LDC service count per quarter
  - supply_ratio:  places per child under 5 (x format, from Q3 2019)
  - pop_0_4:       SA2 under-5 population (ABS annual, interpolated quarterly)
  - income:        SA2 median income annual (Census years only)
  - centre_events: list of {quarter, new_centres, removed_centres,
                             places_change, new_names[], removed_names[]}

Centre tracking:
  - Pre-Q12022: use "Service Name|Postcode" as unique key (no approval number)
  - Q12022+:    use "Service Approval Number" as unique key
  This gives full event history back to Q3 2013.

Run: python build_sa2_history.py   (~8-12 minutes)
"""

import pandas as pd
import json
import warnings
from pathlib import Path

BASE_DIR    = Path(__file__).parent
DATA_DIR    = BASE_DIR / "data"
ABS_DIR     = BASE_DIR / "abs_data"
NQS_FILE    = ABS_DIR / "NQAITS Quarterly Data Splits (Q3 2013 - Q4 2025).xlsx"
ABS_POP     = ABS_DIR / "Population and People Database.xlsx"
ABS_INCOME  = ABS_DIR / "Income Database.xlsx"
CONCORDANCE = ABS_DIR / "postcode_to_sa2_concordance.csv"
OUT_FILE    = DATA_DIR / "sa2_history.json"

POP_COL    = "Persons - 0-4 years (no.)"
INCOME_COL = "Median equivalised total household income (weekly) ($)"
ABS_HEADER = 6

QUARTER_SHEETS = [
    "Q32013","Q42013","Q12014","Q22014","Q32014","Q42014",
    "Q12015","Q22015","Q32015","Q42015","Q12016","Q22016","Q32016","Q42016",
    "Q12017","Q22017","Q32017","Q42017","Q12018","Q22018","Q32018","Q42018",
    "Q12019","Q22019","Q32019","Q42019","Q12020","Q22020","Q32020","Q42020",
    "Q12021","Q22021","Q32021","Q42021","Q12022","Q22022","Q32022","Q42022",
    "Q12023","Q22023","Q32023","Q42023","Q12024","Q22024","Q32024","Q42024",
    "Q12025","Q22025","Q32025","Q42025",
]

# Q12022 is when Service Approval Number first appears
APPROVAL_NUM_FROM = "Q12022"


def quarter_label(q):
    return f"Q{q[1]} {q[2:]}"

def quarter_to_date(q):
    qnum = int(q[1])
    year = int(q[2:])
    month = {1: 3, 2: 6, 3: 9, 4: 12}[qnum]
    return f"{year}-{month:02d}-01"

def quarter_year(q):
    return int(q[1]), int(q[2:])

def frac_year_for_quarter(q):
    qnum, year = quarter_year(q)
    return year + {1: 0.25, 2: 0.5, 3: 0.75, 4: 1.0}[qnum]

def use_approval_number(q):
    """Return True if this quarter has Service Approval Number column."""
    # Compare quarters chronologically
    qnum, year = quarter_year(q)
    tnum, tyear = quarter_year(APPROVAL_NUM_FROM)
    return (year, qnum) >= (tyear, tnum)


def load_abs_sa2_timeseries(filepath, value_col):
    if not filepath.exists():
        print(f"  WARNING: {filepath.name} not found")
        return pd.DataFrame()
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df = pd.read_excel(filepath, sheet_name="Table 1",
                               header=ABS_HEADER, dtype=str, engine="openpyxl")
        df.columns = [str(c).strip() for c in df.columns]
        if "Code" not in df.columns or value_col not in df.columns:
            print(f"  WARNING: columns not found in {filepath.name}")
            return pd.DataFrame()
        df["Code"] = df["Code"].astype(str).str.strip()
        df = df[df["Code"].str.match(r"^\d{9}$")].copy()
        df["Year"] = df["Year"].astype(str).str.strip()
        df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
        years = sorted(df["Year"].dropna().unique())
        pivot = (df[df[value_col].notna()]
                 .pivot_table(index="Code", columns="Year", values=value_col, aggfunc="first"))
        pivot.index.name = "SA2_CODE"
        print(f"  {filepath.name}: {len(pivot):,} SA2s, years {years}")
        return pivot
    except Exception as e:
        print(f"  WARNING: {filepath.name}: {e}")
        return pd.DataFrame()


def interpolate_sa2_value(ts, sa2_code, frac_yr):
    if ts.empty or sa2_code not in ts.index:
        return None
    row = ts.loc[sa2_code]
    year_cols = sorted([c for c in ts.columns if str(c).isdigit()])
    pop_by_frac = {}
    for yr in year_cols:
        val = pd.to_numeric(row.get(yr), errors="coerce")
        if pd.notna(val):
            pop_by_frac[int(yr) + 0.5] = float(val)
    if not pop_by_frac:
        return None
    fracs = sorted(pop_by_frac.keys())
    if frac_yr < fracs[0] or frac_yr > fracs[-1] + 0.5:
        return None
    lower = upper = None
    for f in fracs:
        if f <= frac_yr: lower = f
        if f >= frac_yr and upper is None: upper = f
    if lower is None: return pop_by_frac[upper]
    if upper is None or upper == lower: return pop_by_frac[lower]
    t = (frac_yr - lower) / (upper - lower)
    return pop_by_frac[lower] + t * (pop_by_frac[upper] - pop_by_frac[lower])


def load_concordance():
    if not CONCORDANCE.exists():
        print(f"  ERROR: Concordance not found")
        return {}
    df = pd.read_csv(CONCORDANCE, dtype=str)
    mapping = {}
    for _, row in df.iterrows():
        pc = str(row.get("POSTCODE", "") or "").strip().zfill(4)
        code = str(row.get("SA2_CODE", "") or "").strip()
        name = str(row.get("SA2_NAME", "") or "").strip()
        if pc and code and code != "nan":
            mapping[pc] = (code, name)
    print(f"  Concordance: {len(mapping):,} postcodes")
    return mapping


def process_sheet_sa2(df, concordance, q):
    """
    Process one NQAITS sheet. Returns per-SA2 data including service identity sets.
    Uses Service Approval Number from Q12022+, otherwise Service Name|Postcode.
    """
    df.columns = [str(c).strip() for c in df.columns]

    # Filter LDC
    ldc_col = next((c for c in df.columns if "long day" in c.lower()), None)
    if ldc_col:
        df = df[df[ldc_col].astype(str).str.upper().isin(["YES", "Y", "TRUE", "1"])]
    if df.empty:
        return {}

    pc_col     = next((c for c in df.columns if c.strip() == "Postcode"), None)
    places_col = next((c for c in df.columns
                       if "maximum total places" in c.lower() or "approved places" in c.lower()), None)
    name_col   = next((c for c in df.columns if c.strip() == "Service Name"), None)

    # Service Approval Number — present from Q12022
    appr_col = None
    if use_approval_number(q):
        appr_col = next((c for c in df.columns
                         if c.strip() == "Service Approval Number"), None)

    # Approval date — handle both "Approval Date" and "ApprovalDate"
    date_col = next((c for c in df.columns
                     if c.strip().lower().replace(" ", "") == "approvaldate"), None)

    if not pc_col:
        return {}

    sa2_data = {}
    for _, row in df.iterrows():
        pc = str(row.get(pc_col, "") or "").strip().zfill(4)
        if not pc or pc == "0000":
            continue
        sa2_info = concordance.get(pc)
        if not sa2_info:
            continue
        sa2_code, sa2_name = sa2_info

        places = 0
        if places_col:
            try:
                places = int(float(str(row.get(places_col, 0) or 0)))
            except (ValueError, TypeError):
                places = 0

        svc_name = str(row.get(name_col, "") or "").strip() if name_col else ""
        appr_num = str(row.get(appr_col, "") or "").strip() if appr_col else ""
        appr_date = str(row.get(date_col, "") or "").strip() if date_col else ""

        # Unique service key: approval number if available, else name|postcode
        if appr_num:
            svc_key = appr_num
        elif svc_name and pc:
            svc_key = f"{svc_name}|{pc}"
        else:
            continue

        if sa2_code not in sa2_data:
            sa2_data[sa2_code] = {
                "sa2_name": sa2_name,
                "places": 0,
                "services": 0,
                "service_map": {},   # key -> {name, places, date}
            }

        sa2_data[sa2_code]["places"]   += places
        sa2_data[sa2_code]["services"] += 1
        sa2_data[sa2_code]["service_map"][svc_key] = {
            "name":   svc_name,
            "places": places,
            "date":   appr_date,
        }

    return sa2_data


def build():
    print("=== Building SA2-level quarterly history ===")

    if not NQS_FILE.exists():
        print(f"ERROR: {NQS_FILE} not found")
        return

    concordance = load_concordance()
    if not concordance:
        return

    pop_ts    = load_abs_sa2_timeseries(ABS_POP,    POP_COL)
    income_ts = load_abs_sa2_timeseries(ABS_INCOME, INCOME_COL)

    xl = pd.ExcelFile(NQS_FILE)
    sheet_lookup = {s.upper().replace("DATA", ""): s
                    for s in xl.sheet_names if s.startswith("Q")}
    print(f"  NQAITS sheets: {len(sheet_lookup)}")

    sa2_history = {}
    prev_maps   = {}   # sa2_code -> previous quarter's service_map
    processed_qs = []

    for q in QUARTER_SHEETS:
        sheet_name = sheet_lookup.get(q.upper())
        if not sheet_name:
            continue

        frac_yr = frac_year_for_quarter(q)

        try:
            df = pd.read_excel(NQS_FILE, sheet_name=sheet_name, dtype=str)
            sa2_data = process_sheet_sa2(df, concordance, q)
            processed_qs.append(q)
            seen = set()

            for sa2_code, data in sa2_data.items():
                if sa2_code not in sa2_history:
                    n_prev = len(processed_qs) - 1
                    sa2_history[sa2_code] = {
                        "sa2_name":      data["sa2_name"],
                        "places":        [None] * n_prev,
                        "services":      [None] * n_prev,
                        "supply_ratio":  [None] * n_prev,
                        "pop_0_4":       [None] * n_prev,
                        "income":        [None] * n_prev,
                        "centre_events": [],
                    }
                    prev_maps[sa2_code] = {}

                h = sa2_history[sa2_code]
                curr_map = data["service_map"]
                prev_map = prev_maps.get(sa2_code, {})

                # Detect entries and exits
                new_keys     = set(curr_map.keys()) - set(prev_map.keys())
                removed_keys = set(prev_map.keys()) - set(curr_map.keys())

                if new_keys or removed_keys:
                    prev_places  = h["places"][-1] if h["places"] else 0
                    places_delta = data["places"] - (prev_places or 0)
                    new_names     = [curr_map[k]["name"] for k in new_keys]
                    removed_names = [prev_map[k]["name"] for k in removed_keys]
                    h["centre_events"].append({
                        "quarter":         quarter_label(q),
                        "new_centres":     len(new_keys),
                        "removed_centres": len(removed_keys),
                        "net_centres":     len(new_keys) - len(removed_keys),
                        "places_change":   places_delta,
                        "new_names":       sorted(new_names),
                        "removed_names":   sorted(removed_names),
                    })

                prev_maps[sa2_code] = curr_map

                # SA2-level pop for supply ratio
                sa2_pop = interpolate_sa2_value(pop_ts, sa2_code, frac_yr)
                sa2_pop_int = int(round(sa2_pop)) if sa2_pop is not None else None
                ratio = None
                if sa2_pop and sa2_pop > 0 and data["places"] > 0:
                    ratio = round(data["places"] / sa2_pop, 3)

                sa2_income_w = interpolate_sa2_value(income_ts, sa2_code, frac_yr)
                sa2_income_a = round(sa2_income_w * 52) if sa2_income_w is not None else None

                h["places"].append(data["places"])
                h["services"].append(data["services"])
                h["supply_ratio"].append(ratio)
                h["pop_0_4"].append(sa2_pop_int)
                h["income"].append(sa2_income_a)
                seen.add(sa2_code)

            # SA2s not in this quarter
            for sa2_code in sa2_history:
                if sa2_code not in seen:
                    h = sa2_history[sa2_code]
                    h["places"].append(None)
                    h["services"].append(None)
                    h["supply_ratio"].append(None)
                    h["pop_0_4"].append(None)
                    h["income"].append(None)

            n_events = sum(len(d.get("centre_events",[])) for d in sa2_history.values())
            print(f"  {quarter_label(q)}: {len(sa2_data):,} SA2s  (total events so far: {n_events})")

        except Exception as e:
            import traceback
            print(f"  ERROR {q}: {e}")
            traceback.print_exc()
            for sa2_code in sa2_history:
                for key in ["places","services","supply_ratio","pop_0_4","income"]:
                    sa2_history[sa2_code][key].append(None)
            processed_qs.append(q)

    print(f"\nProcessed {len(processed_qs)} quarters, {len(sa2_history):,} SA2s")

    output_sa2s = []
    for sa2_code, h in sa2_history.items():
        output_sa2s.append({
            "sa2_code":      sa2_code,
            "sa2_name":      h["sa2_name"],
            "quarters":      [quarter_label(q) for q in processed_qs],
            "dates":         [quarter_to_date(q) for q in processed_qs],
            "places":        h["places"],
            "services":      h["services"],
            "supply_ratio":  h["supply_ratio"],
            "pop_0_4":       h["pop_0_4"],
            "income":        h["income"],
            "centre_events": h["centre_events"],
        })

    out = {
        "generated": str(pd.Timestamp.now().date()),
        "quarters":  [quarter_label(q) for q in processed_qs],
        "dates":     [quarter_to_date(q) for q in processed_qs],
        "sa2_count": len(output_sa2s),
        "sa2s":      output_sa2s,
    }

    DATA_DIR.mkdir(exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, separators=(",", ":"))

    mb = OUT_FILE.stat().st_size / 1024 / 1024
    print(f"Saved: {OUT_FILE} ({mb:.1f} MB), {len(output_sa2s):,} SA2s")

    # Sample event coverage
    total_events = sum(len(h["centre_events"]) for h in sa2_history.values())
    sa2s_with_events = sum(1 for h in sa2_history.values() if h["centre_events"])
    print(f"Centre events: {total_events:,} total across {sa2s_with_events:,} SA2s")


if __name__ == "__main__":
    build()
