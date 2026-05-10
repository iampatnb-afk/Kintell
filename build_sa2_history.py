"""
build_sa2_history.py v3 (2026-05-10)
====================================

Extracts per-SA2 quarterly supply history from NQAITS data.
Outputs: data/sa2_history.json

V3 — Polygon-first SA2 attribution (OI-NEW-21)
----------------------------------------------
v2 attributed each NQAITS service row to an SA2 via postcode-only lookup
through `postcode_to_sa2_concordance.csv`. That mechanism is structurally
one-postcode -> one-SA2, while reality is many-to-many. Failure modes seen:
  - Cross-state name collisions (PC 6102 -> QLD "Bentley Park" not WA "Bentley")
  - Postcode covers multiple SA2s and concordance picks one
  - Postcode missing from concordance entirely (e.g. PC 0822 NT)

Result: 1,267 of ~2,400 SA2s covered; 1,043 services-anchored SA2s missing
from output; 39.2% of services attributed to wrong SA2 or dropped silently.

v3 switches primary attribution to polygon-derived `services.sa2_code`
(DEC-70 Step 1c polygon backfill, 99.89% coverage). NQAITS rows are joined
via Service Approval Number to the live `services` table; postcode-concordance
remains as fallback for closed/de-registered services and pre-Q12022 quarters
where Service Approval Number doesn't yet appear in NQAITS.

V2 — LDC-first multi-subtype support
------------------------------------
Preserves the v1 LDC-only top-level arrays for back-compat (dashboard.html
and any other consumer of `places`/`services`/`supply_ratio`/`centre_events`
keeps working unchanged) AND adds a per-subtype block with parallel arrays
for LDC, OSHC, PSK, FDC.

**LDC is the V1 focus.** The build processes LDC first per quarter and
populates BOTH the top-level arrays AND `by_subtype.LDC` with identical
data. OSHC, PSK, FDC populate `by_subtype.<subtype>` only — they are
best-effort enrichment so non-LDC centre pages are not visually empty.

Subtype filtering uses the `Service Sub Type` column (canonical; values
LDC / OSHC / PSK / FDC) where present. Older NQAITS quarters that predate
this column fall back to the legacy `Long Day Care` Yes/No flag, yielding
LDC-only data for those quarters; OSHC/PSK/FDC histories begin when
`Service Sub Type` first appears in the source data.

**Known simplification.** `supply_ratio` uses `pop_0_4` (under-5 population)
as the denominator for ALL subtypes:
  - Semantically right for LDC (the V1 focus).
  - Less right for OSHC (school-aged), PSK (3-5), FDC (mixed).
The single denominator is kept across subtypes to (a) preserve cross-subtype
comparability on the centre page and (b) match the existing
`service_catchment_cache` calculation. Subtype-correct denominators are
V1.5+ work — they need an ABS school-age population ingest at SA2 that
isn't built yet.

Output structure (per SA2):
  {
    "sa2_code", "sa2_name", "quarters", "dates",

    # v1 top-level arrays (LDC-only, back-compat):
    "places", "services", "supply_ratio", "centre_events",

    # SA2-level demographics (subtype-independent):
    "pop_0_4", "income",

    # v2 per-subtype block (new):
    "by_subtype": {
      "LDC":  {"places", "services", "supply_ratio", "centre_events"},
      "OSHC": {"places", "services", "supply_ratio", "centre_events"},
      "PSK":  {"places", "services", "supply_ratio", "centre_events"},
      "FDC":  {"places", "services", "supply_ratio", "centre_events"}
    }
  }

Centre tracking (per subtype):
  - Pre-Q12022: use "Service Name|Postcode" as unique key (no approval number)
  - Q12022+:    use "Service Approval Number" as unique key

Run: python build_sa2_history.py   (~15-25 minutes for v2)
"""

import json
import sqlite3
import traceback
import warnings
from pathlib import Path

import pandas as pd

BASE_DIR    = Path(__file__).parent
DATA_DIR    = BASE_DIR / "data"
ABS_DIR     = BASE_DIR / "abs_data"
NQS_FILE    = ABS_DIR / "NQAITS Quarterly Data Splits (Q3 2013 - Q4 2025).xlsx"
ABS_POP     = ABS_DIR / "Population and People Database.xlsx"
ABS_INCOME  = ABS_DIR / "Income Database.xlsx"
CONCORDANCE = ABS_DIR / "postcode_to_sa2_concordance.csv"
OUT_FILE    = DATA_DIR / "sa2_history.json"
DB_FILE     = DATA_DIR / "kintell.db"

POP_COL    = "Persons - 0-4 years (no.)"
INCOME_COL = "Median equivalised total household income (weekly) ($)"
ABS_HEADER = 6

# Subtype config — LDC is the canonical subtype that mirrors into top-level
# arrays for back-compat. Other subtypes appear only under `by_subtype`.
SUBTYPES = ["LDC", "OSHC", "PSK", "FDC"]
LDC_SUBTYPE = "LDC"

QUARTER_SHEETS = [
    "Q32013", "Q42013",
    "Q12014", "Q22014", "Q32014", "Q42014",
    "Q12015", "Q22015", "Q32015", "Q42015",
    "Q12016", "Q22016", "Q32016", "Q42016",
    "Q12017", "Q22017", "Q32017", "Q42017",
    "Q12018", "Q22018", "Q32018", "Q42018",
    "Q12019", "Q22019", "Q32019", "Q42019",
    "Q12020", "Q22020", "Q32020", "Q42020",
    "Q12021", "Q22021", "Q32021", "Q42021",
    "Q12022", "Q22022", "Q32022", "Q42022",
    "Q12023", "Q22023", "Q32023", "Q42023",
    "Q12024", "Q22024", "Q32024", "Q42024",
    "Q12025", "Q22025", "Q32025", "Q42025",
]

# Q12022 is when Service Approval Number first appears
APPROVAL_NUM_FROM = "Q12022"


# ---------------------------------------------------------------------------
# Helpers (unchanged from v1)
# ---------------------------------------------------------------------------

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
        if f <= frac_yr:
            lower = f
        if f >= frac_yr and upper is None:
            upper = f
    if lower is None:
        return pop_by_frac[upper]
    if upper is None or upper == lower:
        return pop_by_frac[lower]
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


def load_polygon_sa2_lookup():
    """Read services table; return dict[service_approval_number -> (sa2_code, sa2_name)].

    Polygon-derived SA2 attribution per DEC-70 (Step 1c polygon backfill, 99.89%
    coverage). Used by process_sheet_sa2 in preference to postcode-concordance
    lookup, which has known failure modes (cross-state name collisions, multi-SA2
    postcodes, missing postcodes — see v3 docstring header).

    Falls back to postcode-concordance for NQAITS rows whose Service Approval
    Number isn't in the live services table (closed/de-registered centres) or
    for pre-Q12022 quarters where the column doesn't yet appear in NQAITS.
    """
    if not DB_FILE.exists():
        print(f"  WARNING: {DB_FILE} not found; polygon SA2 lookup empty")
        return {}
    con = sqlite3.connect(str(DB_FILE))
    cur = con.cursor()
    cur.execute(
        "SELECT service_approval_number, sa2_code, sa2_name "
        "FROM services WHERE sa2_code IS NOT NULL AND sa2_code != ''"
    )
    rows = cur.fetchall()
    con.close()
    lookup = {}
    for san, code, name in rows:
        if san:
            lookup[san.strip()] = (code.strip(), (name or "").strip())
    print(f"  Polygon SA2 lookup: {len(lookup):,} services (DEC-70)")
    return lookup


# ---------------------------------------------------------------------------
# v2 subtype filter
# ---------------------------------------------------------------------------

def filter_df_by_subtype(df, subtype):
    """Return a filtered view of df containing only rows for the given subtype.

    Uses the canonical 'Service Sub Type' column if present (values: LDC, OSHC,
    PSK, FDC). Falls back for older NQAITS quarters that predate this column:
      - LDC: uses legacy 'Long Day Care' Yes/No flag.
      - OSHC, PSK, FDC: returns empty df (no legacy single-flag column).

    Does not mutate df.
    """
    df.columns = [str(c).strip() for c in df.columns]
    sst_col = next((c for c in df.columns if c.strip() == "Service Sub Type"), None)
    if sst_col:
        mask = df[sst_col].astype(str).str.strip().str.upper() == subtype.upper()
        return df[mask]
    # Legacy fallback (older quarters)
    if subtype == LDC_SUBTYPE:
        ldc_col = next((c for c in df.columns if "long day" in c.lower()), None)
        if ldc_col:
            mask = df[ldc_col].astype(str).str.upper().isin(["YES", "Y", "TRUE", "1"])
            return df[mask]
    return df.iloc[0:0]


# ---------------------------------------------------------------------------
# Per-sheet processor (refactored to take subtype parameter)
# ---------------------------------------------------------------------------

def process_sheet_sa2(df, concordance, polygon_lookup, q, subtype):
    """Process one NQAITS sheet for one subtype.

    Returns dict[sa2_code -> {sa2_name, places, services, service_map}].
    Empty dict if no rows for this subtype in this quarter.
    """
    df = filter_df_by_subtype(df, subtype)
    if df.empty:
        return {}

    pc_col = next((c for c in df.columns if c.strip() == "Postcode"), None)
    places_col = next((c for c in df.columns
                       if "maximum total places" in c.lower() or "approved places" in c.lower()), None)
    name_col = next((c for c in df.columns if c.strip() == "Service Name"), None)

    appr_col = None
    if use_approval_number(q):
        appr_col = next((c for c in df.columns
                         if c.strip() == "Service Approval Number"), None)

    date_col = next((c for c in df.columns
                     if c.strip().lower().replace(" ", "") == "approvaldate"), None)

    if not pc_col:
        return {}

    sa2_data = {}
    for _, row in df.iterrows():
        pc = str(row.get(pc_col, "") or "").strip().zfill(4)
        if not pc or pc == "0000":
            continue
        # Polygon-derived SA2 first (DEC-70). Concordance is fallback for
        # closed services or pre-Q12022 NQAITS rows missing SAN.
        appr_num_for_sa2 = ""
        if appr_col:
            appr_num_for_sa2 = str(row.get(appr_col, "") or "").strip()
        sa2_info = polygon_lookup.get(appr_num_for_sa2) if appr_num_for_sa2 else None
        if not sa2_info:
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

        if appr_num:
            svc_key = appr_num
        elif svc_name and pc:
            svc_key = f"{svc_name}|{pc}"
        else:
            continue

        if sa2_code not in sa2_data:
            sa2_data[sa2_code] = {
                "sa2_name":    sa2_name,
                "places":      0,
                "services":    0,
                "service_map": {},
            }

        sa2_data[sa2_code]["places"] += places
        sa2_data[sa2_code]["services"] += 1
        sa2_data[sa2_code]["service_map"][svc_key] = {
            "name":   svc_name,
            "places": places,
            "date":   appr_date,
        }

    return sa2_data


# ---------------------------------------------------------------------------
# History entry initialisation
# ---------------------------------------------------------------------------

def _init_history_entry(sa2_name, n_prev):
    """Fresh history entry padded with n_prev None placeholders for prior quarters."""
    return {
        "sa2_name":      sa2_name,
        # Top-level (LDC, back-compat with v1)
        "places":        [None] * n_prev,
        "services":      [None] * n_prev,
        "supply_ratio":  [None] * n_prev,
        "centre_events": [],
        # SA2-level demographics (subtype-independent)
        "pop_0_4":       [None] * n_prev,
        "income":        [None] * n_prev,
        # Per-subtype (v2 addition)
        "by_subtype": {
            st: {
                "places":        [None] * n_prev,
                "services":      [None] * n_prev,
                "supply_ratio":  [None] * n_prev,
                "centre_events": [],
            }
            for st in SUBTYPES
        },
    }


def _append_none_for_quarter(h):
    """Append None to every per-quarter array on a history entry. Use when
    an SA2 has no data this quarter (or when a quarter's sheet read failed)."""
    h["places"].append(None)
    h["services"].append(None)
    h["supply_ratio"].append(None)
    h["pop_0_4"].append(None)
    h["income"].append(None)
    for st in SUBTYPES:
        bs = h["by_subtype"][st]
        bs["places"].append(None)
        bs["services"].append(None)
        bs["supply_ratio"].append(None)


# ---------------------------------------------------------------------------
# Main build loop (refactored for multi-subtype)
# ---------------------------------------------------------------------------

def build():
    print("=== Building SA2-level quarterly history (v2 — LDC-first multi-subtype) ===")

    if not NQS_FILE.exists():
        print(f"ERROR: {NQS_FILE} not found")
        return

    concordance = load_concordance()
    if not concordance:
        return

    polygon_lookup = load_polygon_sa2_lookup()

    pop_ts    = load_abs_sa2_timeseries(ABS_POP, POP_COL)
    income_ts = load_abs_sa2_timeseries(ABS_INCOME, INCOME_COL)

    xl = pd.ExcelFile(NQS_FILE)
    sheet_lookup = {s.upper().replace("DATA", ""): s
                    for s in xl.sheet_names if s.startswith("Q")}
    print(f"  NQAITS sheets: {len(sheet_lookup)}")

    sa2_history = {}
    # prev_maps[sa2_code][subtype] = previous quarter's service_map for that subtype
    prev_maps = {}
    processed_qs = []

    for q in QUARTER_SHEETS:
        sheet_name = sheet_lookup.get(q.upper())
        if not sheet_name:
            continue

        frac_yr = frac_year_for_quarter(q)

        try:
            df = pd.read_excel(NQS_FILE, sheet_name=sheet_name, dtype=str)
            processed_qs.append(q)

            # Process each subtype separately, collect into per-subtype dicts.
            per_subtype_sa2_data = {
                st: process_sheet_sa2(df, concordance, polygon_lookup, q, st) for st in SUBTYPES
            }

            # Union of SA2s with data in any subtype this quarter.
            all_seen_sa2s = set()
            for data in per_subtype_sa2_data.values():
                all_seen_sa2s.update(data.keys())

            # Initialise history entries for newly-seen SA2s.
            for sa2_code in all_seen_sa2s:
                if sa2_code not in sa2_history:
                    sa2_name = next(
                        (data[sa2_code]["sa2_name"]
                         for data in per_subtype_sa2_data.values()
                         if sa2_code in data),
                        sa2_code,
                    )
                    n_prev = len(processed_qs) - 1
                    sa2_history[sa2_code] = _init_history_entry(sa2_name, n_prev)
                    prev_maps[sa2_code] = {st: {} for st in SUBTYPES}

            # Process each known SA2 for this quarter.
            for sa2_code in sa2_history:
                h = sa2_history[sa2_code]
                is_seen = sa2_code in all_seen_sa2s

                # SA2-level demographics first (subtype-independent).
                if is_seen:
                    sa2_pop = interpolate_sa2_value(pop_ts, sa2_code, frac_yr)
                    sa2_pop_int = int(round(sa2_pop)) if sa2_pop is not None else None
                    h["pop_0_4"].append(sa2_pop_int)

                    sa2_income_w = interpolate_sa2_value(income_ts, sa2_code, frac_yr)
                    sa2_income_a = round(sa2_income_w * 52) if sa2_income_w is not None else None
                    h["income"].append(sa2_income_a)
                else:
                    h["pop_0_4"].append(None)
                    h["income"].append(None)

                # Per-subtype processing.
                for subtype in SUBTYPES:
                    sa2_data = per_subtype_sa2_data[subtype]
                    data = sa2_data.get(sa2_code)
                    bs = h["by_subtype"][subtype]
                    prev_map = prev_maps[sa2_code][subtype]

                    if data is None:
                        # SA2 has no services of this subtype this quarter.
                        bs["places"].append(None)
                        bs["services"].append(None)
                        bs["supply_ratio"].append(None)
                        if subtype == LDC_SUBTYPE:
                            h["places"].append(None)
                            h["services"].append(None)
                            h["supply_ratio"].append(None)
                        # If there WERE services of this subtype last quarter and
                        # now there aren't, that's a removal event.
                        if prev_map:
                            removed_names = sorted([prev_map[k]["name"] for k in prev_map])
                            event = {
                                "quarter":         quarter_label(q),
                                "new_centres":     0,
                                "removed_centres": len(prev_map),
                                "net_centres":     -len(prev_map),
                                "places_change":   -sum(v["places"] for v in prev_map.values()),
                                "new_names":       [],
                                "removed_names":   removed_names,
                            }
                            bs["centre_events"].append(event)
                            if subtype == LDC_SUBTYPE:
                                h["centre_events"].append(event)
                        prev_maps[sa2_code][subtype] = {}
                        continue

                    curr_map = data["service_map"]

                    # Detect entries and exits.
                    new_keys     = set(curr_map.keys()) - set(prev_map.keys())
                    removed_keys = set(prev_map.keys()) - set(curr_map.keys())

                    if new_keys or removed_keys:
                        prev_places = bs["places"][-1] if bs["places"] else 0
                        places_delta = data["places"] - (prev_places or 0)
                        new_names     = [curr_map[k]["name"] for k in new_keys]
                        removed_names = [prev_map[k]["name"] for k in removed_keys]
                        event = {
                            "quarter":         quarter_label(q),
                            "new_centres":     len(new_keys),
                            "removed_centres": len(removed_keys),
                            "net_centres":     len(new_keys) - len(removed_keys),
                            "places_change":   places_delta,
                            "new_names":       sorted(new_names),
                            "removed_names":   sorted(removed_names),
                        }
                        bs["centre_events"].append(event)
                        if subtype == LDC_SUBTYPE:
                            h["centre_events"].append(event)

                    prev_maps[sa2_code][subtype] = curr_map

                    # Supply ratio uses pop_0_4 (already appended above).
                    sa2_pop = h["pop_0_4"][-1]
                    ratio = None
                    if sa2_pop and sa2_pop > 0 and data["places"] > 0:
                        ratio = round(data["places"] / sa2_pop, 3)

                    bs["places"].append(data["places"])
                    bs["services"].append(data["services"])
                    bs["supply_ratio"].append(ratio)
                    if subtype == LDC_SUBTYPE:
                        h["places"].append(data["places"])
                        h["services"].append(data["services"])
                        h["supply_ratio"].append(ratio)

            # Quarter print: per-subtype counts.
            counts = " ".join(
                f"{st}={len(per_subtype_sa2_data[st]):,}" for st in SUBTYPES
            )
            event_counts = " ".join(
                f"{st}={sum(len(h['by_subtype'][st]['centre_events']) for h in sa2_history.values()):,}"
                for st in SUBTYPES
            )
            print(f"  {quarter_label(q)}: SA2s [{counts}]  events-so-far [{event_counts}]")

        except Exception as e:
            print(f"  ERROR {q}: {e}")
            traceback.print_exc()
            for sa2_code in sa2_history:
                _append_none_for_quarter(sa2_history[sa2_code])
            processed_qs.append(q)

    print(f"\nProcessed {len(processed_qs)} quarters, {len(sa2_history):,} SA2s")

    # Build output structure.
    output_sa2s = []
    for sa2_code, h in sa2_history.items():
        output_sa2s.append({
            "sa2_code":      sa2_code,
            "sa2_name":      h["sa2_name"],
            "quarters":      [quarter_label(q) for q in processed_qs],
            "dates":         [quarter_to_date(q) for q in processed_qs],
            # v1 top-level (LDC, back-compat)
            "places":        h["places"],
            "services":      h["services"],
            "supply_ratio":  h["supply_ratio"],
            "centre_events": h["centre_events"],
            # SA2-level demographics
            "pop_0_4":       h["pop_0_4"],
            "income":        h["income"],
            # v2 per-subtype
            "by_subtype":    h["by_subtype"],
        })

    out = {
        "generated":   str(pd.Timestamp.now().date()),
        "schema":      "v2",  # v2: by_subtype block added; v1 top-level preserved
        "quarters":    [quarter_label(q) for q in processed_qs],
        "dates":       [quarter_to_date(q) for q in processed_qs],
        "sa2_count":   len(output_sa2s),
        "subtypes":    SUBTYPES,
        "ldc_subtype": LDC_SUBTYPE,
        "sa2s":        output_sa2s,
    }

    DATA_DIR.mkdir(exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, separators=(",", ":"))

    mb = OUT_FILE.stat().st_size / 1024 / 1024
    print(f"\nSaved: {OUT_FILE} ({mb:.1f} MB), {len(output_sa2s):,} SA2s")

    # Also copy to docs/ — that's where review_server.py serves sa2_history.json
    # from for centre.html / dashboard.html consumption. Without this copy the
    # served file goes stale relative to the source-of-truth in data/.
    docs_out = BASE_DIR / "docs" / "sa2_history.json"
    if docs_out.parent.exists():
        import shutil
        shutil.copy2(OUT_FILE, docs_out)
        print(f"Copied to:  {docs_out}  (served by review_server.py)")
    else:
        print(f"WARNING: {docs_out.parent} not found; skipping docs/ copy.")

    # Per-subtype event coverage summary.
    print("\nCentre events by subtype:")
    for st in SUBTYPES:
        total_events = sum(len(h["by_subtype"][st]["centre_events"]) for h in sa2_history.values())
        sa2s_with_events = sum(
            1 for h in sa2_history.values()
            if h["by_subtype"][st]["centre_events"]
        )
        print(f"  {st:<5}  {total_events:>8,} events across {sa2s_with_events:>5,} SA2s")
    total_top = sum(len(h["centre_events"]) for h in sa2_history.values())
    sa2s_top = sum(1 for h in sa2_history.values() if h["centre_events"])
    print(f"  (top-level mirrors LDC: {total_top:,} events across {sa2s_top:,} SA2s)")


if __name__ == "__main__":
    build()
