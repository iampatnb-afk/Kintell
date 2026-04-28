"""
centre_page.py — Phase 2 backend helper for centre.html
Version: v4 (2026-04-28) — Layer 4.2-B: trajectory + cohort histogram

Provides get_centre_payload(service_id) -> dict
Returns full single-centre detail: service + entity + group + brand,
with OBS/DER/COM treatment matching operator_page.py conventions.

v4 changes (2026-04-28, Layer 4.2-B):
  - New constant LAYER3_METRIC_TRAJECTORY_SOURCE — maps each Layer 4 metric
    to its trajectory source (abs_sa2_erp_annual, abs_sa2_births_annual,
    abs_sa2_unemployment_quarterly, abs_sa2_socioeconomic_annual,
    abs_sa2_education_employment_annual). Probed in
    recon/layer4_2_probe.md before this build.
  - New helper _metric_trajectory(con, sa2_code, metric_name): reads the
    metric's source table for this SA2, returns the historical series
    suitable for sparkline / dot-trajectory rendering. Drops NULL/empty
    points so the chart shows only real data.
  - New helper _cohort_distribution(con, metric, cohort_def, cohort_key,
    n_bins=20): reads all raw_value rows for the cohort from
    layer3_sa2_metric_banding, bins them into 20 equal-width bins,
    returns the bin counts plus this SA2's bin index. Surfaces shape
    (skew, modality) rather than the artificially-uniform decile
    distribution.
  - _layer3_position now augments each populated entry with
    "trajectory", "trajectory_kind", "cohort_distribution".
    Suppressed for confidence in {insufficient, unavailable, deferred}.

v3 changes (2026-04-28, Layer 4 NOW + POSITION):
  - LAYER3_METRIC_META / COHORT_LABEL_TEMPLATES / RA_BAND_SHORT_LABELS /
    STATE_SHORT_LABELS for the 12 Layer 4 metrics.
  - _layer3_position helper, payload["position"] block.

v2 fixes (2026-04-26):
  - aria_plus column stores label strings, not codes.
  - _parse_date() recognises DD/MM/YYYY.

Read-only. No DB mutations.
"""

import sqlite3
from datetime import datetime, timezone
from typing import Optional

DB_PATH = "data/kintell.db"

# OBS = observed (raw from source), DER = derived (computed),
# COM = commentary (rule-based text). Same convention as operator_page.py.
TAG_OBS = "OBS"
TAG_DER = "DER"
TAG_COM = "COM"

# Stale-rating threshold (years). Aligned with operator_page.py v5+.
STALE_RATING_YEARS = 2
DUE_SOON_MONTHS = 18

# Ownership-type label map (Decision 9). Same as operator_page.py.
OWNERSHIP_LABELS = {
    "private": "Private (for profit)",
    "nfp": "Not-for-profit",
    "government": "Government",
    "independent_school": "Independent school",
    "catholic_school": "Catholic school",
    "unknown": "Not classified",
}

# ARIA+ remoteness band labels. The aria_plus column stores label strings
# in this DB (e.g. "Major Cities of Australia"), not numeric codes. We
# accept both forms and normalise to a short canonical label.
ARIA_LABELS = {
    # Label-form keys (case-insensitive match below)
    "major cities of australia": "Major city",
    "inner regional australia": "Inner regional",
    "outer regional australia": "Outer regional",
    "remote australia": "Remote",
    "very remote australia": "Very remote",
    # Code-form keys (kept for backward compatibility)
    "0": "Major city",
    "1": "Inner regional",
    "2": "Outer regional",
    "3": "Remote",
    "4": "Very remote",
}

# ─────────────────────────────────────────────────────────────────────
# Layer 4 — POSITION block constants
# ─────────────────────────────────────────────────────────────────────

# Short labels for ABS Remoteness Area bands (sa2_cohort.ra_band).
# Kept short to fit cleanly in cohort phrases like
# "vs other Major Cities SA2s in NSW".
RA_BAND_SHORT_LABELS = {
    1: "Major Cities",
    2: "Inner Regional",
    3: "Outer Regional",
    4: "Remote",
    5: "Very Remote",
}

# Short state labels for cohort phrasing (NSW vs "New South Wales").
STATE_SHORT_LABELS = {
    "New South Wales": "NSW",
    "Victoria": "Vic",
    "Queensland": "Qld",
    "South Australia": "SA",
    "Western Australia": "WA",
    "Tasmania": "Tas",
    "Northern Territory": "NT",
    "Australian Capital Territory": "ACT",
    "Other Territories": "Other Territories",
}

# Cohort-phrase templates. Keys match layer3_sa2_metric_banding.cohort_def.
COHORT_LABEL_TEMPLATES = {
    "state":              "vs other SA2s in {state_name}",
    "remoteness":         "vs other {ra_name} SA2s nationwide",
    "state_x_remoteness": "vs other {ra_name} SA2s in {state_name}",
    "national":           "vs all SA2s nationwide",
}

# Per-metric metadata for Layer 4 POSITION rendering.
# - display:       human label
# - card:          'population' | 'labour_market' (UI grouping)
# - value_format:  'int' | 'percent' | 'currency_annual' | 'currency_weekly'
# - direction:     'high_is_positive' | 'high_is_concerning'
#                  (semantics carried in band_copy text only — visual
#                   palette stays neutral per Layer 4 design §11.2)
# - status:        optional 'deferred' for metrics not yet in Layer 3
# - source:        OBS-badge attribution string for the raw value
# - band_copy:     {'low': ..., 'mid': ..., 'high': ...} interpretive text
LAYER3_METRIC_META = {
    # ── Population card ─────────────────────────────────────────────
    "sa2_under5_count": {
        "display": "Under-5 population",
        "card": "population",
        "value_format": "int",
        "direction": "high_is_positive",
        "source": "ABS ERP at SA2 (abs_sa2_erp_annual)",
        "band_copy": {
            "low":  "thin demand pool",
            "mid":  "average demand pool",
            "high": "deep demand pool",
        },
    },
    "sa2_total_population": {
        "display": "Total population",
        "card": "population",
        "value_format": "int",
        "direction": "high_is_positive",
        "source": "ABS ERP at SA2 (abs_sa2_erp_annual)",
        "band_copy": {
            "low":  "small SA2",
            "mid":  "mid-sized SA2",
            "high": "large SA2",
        },
    },
    "sa2_births_count": {
        "display": "Births (leading demand)",
        "card": "population",
        "value_format": "int",
        "direction": "high_is_positive",
        "source": "ABS Births at SA2 (abs_sa2_births_annual)",
        "band_copy": {
            "low":  "low forward demand",
            "mid":  "average forward demand",
            "high": "strong forward demand",
        },
    },
    "sa2_under5_growth_5y": {
        "display": "Under-5 5y growth",
        "card": "population",
        "value_format": "percent",
        "direction": "high_is_positive",
        "status": "deferred",
        "source": "Derived from abs_sa2_erp_annual (Layer 3 patch pending)",
        "band_copy": {"low": "—", "mid": "—", "high": "—"},
    },
    # ── Labour market card ──────────────────────────────────────────
    "sa2_unemployment_rate": {
        "display": "Unemployment rate",
        "card": "labour_market",
        "value_format": "percent",
        "direction": "high_is_concerning",
        "source": "ABS SALM SA2 (abs_sa2_unemployment_quarterly)",
        "band_copy": {
            "low":  "tight labour market",
            "mid":  "typical labour market",
            "high": "loose labour market — fee-sensitivity flag",
        },
    },
    "sa2_median_employee_income": {
        "display": "Median employee income",
        "card": "labour_market",
        "value_format": "currency_annual",
        "direction": "high_is_positive",
        "source": "ABS Income at SA2 (median_employee_income_annual)",
        "band_copy": {
            "low":  "price-sensitive",
            "mid":  "typical",
            "high": "price-tolerant",
        },
    },
    "sa2_median_household_income": {
        "display": "Median household income",
        "card": "labour_market",
        "value_format": "currency_weekly",
        "direction": "high_is_positive",
        "source": "ABS Census 2021 (median_equiv_household_income_weekly)",
        "band_copy": {
            "low":  "price-sensitive",
            "mid":  "typical",
            "high": "price-tolerant",
        },
    },
    "sa2_median_total_income": {
        "display": "Median total income (excl. pensions)",
        "card": "labour_market",
        "value_format": "currency_annual",
        "direction": "high_is_positive",
        "source": "ABS Income at SA2 (median_total_income_excl_pensions_annual)",
        "band_copy": {
            "low":  "price-sensitive",
            "mid":  "typical",
            "high": "price-tolerant",
        },
    },
    "sa2_lfp_persons": {
        "display": "Labour force participation",
        "card": "labour_market",
        "value_format": "percent",
        "direction": "high_is_positive",
        "source": "ABS Education + Employment SA2 (ee_lfp_persons_pct)",
        "band_copy": {
            "low":  "low workforce demand",
            "mid":  "typical workforce demand",
            "high": "high workforce demand",
        },
    },
    "sa2_lfp_females": {
        "display": "LFP — females",
        "card": "labour_market",
        "value_format": "percent",
        "direction": "high_is_positive",
        "source": "ABS Census 2021 T33 (census_lfp_females_pct)",
        "band_copy": {
            "low":  "low",
            "mid":  "typical",
            "high": "high (dual-income signal)",
        },
    },
    "sa2_lfp_males": {
        "display": "LFP — males",
        "card": "labour_market",
        "value_format": "percent",
        "direction": "high_is_positive",
        "source": "ABS Census 2021 T33 (census_lfp_males_pct)",
        "band_copy": {
            "low":  "low",
            "mid":  "typical",
            "high": "high",
        },
    },
    "jsa_vacancy_rate": {
        "display": "JSA vacancy rate",
        "card": "labour_market",
        "value_format": "percent",
        "direction": "high_is_positive",
        "status": "deferred",
        "source": "JSA IVI (state-level, computed at read time — pending)",
        "band_copy": {"low": "—", "mid": "—", "high": "—"},
    },
}

# Display order within each card (drives section order in the UI).
POSITION_CARD_ORDER = {
    "population": [
        "sa2_under5_count",
        "sa2_total_population",
        "sa2_births_count",
        "sa2_under5_growth_5y",
    ],
    "labour_market": [
        "sa2_unemployment_rate",
        "sa2_median_employee_income",
        "sa2_median_household_income",
        "sa2_median_total_income",
        "sa2_lfp_persons",
        "sa2_lfp_females",
        "sa2_lfp_males",
        "jsa_vacancy_rate",
    ],
}

# ─────────────────────────────────────────────────────────────────────
# Layer 4.2-B — trajectory source mapping
# ─────────────────────────────────────────────────────────────────────
# Each entry maps a Layer 4 metric to its historical source table. The
# trajectory helper reads the SA2's series for sparkline / dot-trajectory
# rendering. Probed in recon/layer4_2_probe.md before this constant was
# written; column names are confirmed against actual schema.
#
# kind = "annual" | "quarterly" — controls the JS x-axis treatment.
#
# Long-format tables (abs_sa2_socioeconomic_annual,
# abs_sa2_education_employment_annual) need a metric_name filter as well.
LAYER3_METRIC_TRAJECTORY_SOURCE = {
    "sa2_under5_count": {
        "table":         "abs_sa2_erp_annual",
        "value_col":     "persons",
        "period_col":    "year",
        "filter_clause": "age_group = 'under_5_persons'",
        "kind":          "annual",
    },
    "sa2_total_population": {
        "table":         "abs_sa2_erp_annual",
        "value_col":     "persons",
        "period_col":    "year",
        "filter_clause": "age_group = 'total_persons'",
        "kind":          "annual",
    },
    "sa2_births_count": {
        "table":         "abs_sa2_births_annual",
        "value_col":     "births_count",
        "period_col":    "year",
        "filter_clause": None,
        "kind":          "annual",
    },
    "sa2_unemployment_rate": {
        "table":         "abs_sa2_unemployment_quarterly",
        "value_col":     "rate",
        "period_col":    "year_qtr",
        "filter_clause": None,
        "kind":          "quarterly",
    },
    "sa2_median_employee_income": {
        "table":         "abs_sa2_socioeconomic_annual",
        "value_col":     "value",
        "period_col":    "year",
        "filter_clause": "metric_name = 'median_employee_income_annual'",
        "kind":          "annual",
    },
    "sa2_median_household_income": {
        "table":         "abs_sa2_socioeconomic_annual",
        "value_col":     "value",
        "period_col":    "year",
        "filter_clause": "metric_name = 'median_equiv_household_income_weekly'",
        "kind":          "annual",
    },
    "sa2_median_total_income": {
        "table":         "abs_sa2_socioeconomic_annual",
        "value_col":     "value",
        "period_col":    "year",
        "filter_clause": "metric_name = 'median_total_income_excl_pensions_annual'",
        "kind":          "annual",
    },
    "sa2_lfp_persons": {
        "table":         "abs_sa2_education_employment_annual",
        "value_col":     "value",
        "period_col":    "year",
        "filter_clause": "metric_name = 'ee_lfp_persons_pct'",
        "kind":          "annual",
    },
    "sa2_lfp_females": {
        "table":         "abs_sa2_education_employment_annual",
        "value_col":     "value",
        "period_col":    "year",
        "filter_clause": "metric_name = 'census_lfp_females_pct'",
        "kind":          "annual",
    },
    "sa2_lfp_males": {
        "table":         "abs_sa2_education_employment_annual",
        "value_col":     "value",
        "period_col":    "year",
        "filter_clause": "metric_name = 'census_lfp_males_pct'",
        "kind":          "annual",
    },
    # sa2_under5_growth_5y, jsa_vacancy_rate — deferred metrics, no
    # trajectory source yet. Their LAYER3_METRIC_META entry already has
    # status='deferred', so _layer3_position never reaches the trajectory
    # branch for them.
}


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _row_to_dict(row) -> Optional[dict]:
    if row is None:
        return None
    return {k: row[k] for k in row.keys()}


def _parse_date(s: Optional[str]) -> Optional[datetime]:
    """Parse YYYY-MM-DD, ISO8601, 'Mon-YYYY', or DD/MM/YYYY.

    services.approval_granted_date uses DD/MM/YYYY (e.g. '29/09/2010');
    operator_page.py v5 pattern handled the others.
    """
    if not s:
        return None
    s = str(s).strip()
    for fmt in (
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y",
        "%b-%Y",
        "%B-%Y",
    ):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def _months_since(s: Optional[str]) -> Optional[int]:
    d = _parse_date(s)
    if not d:
        return None
    now = datetime.now()
    return (now.year - d.year) * 12 + (now.month - d.month)


def _compute_inspection_cadence(rating_issued_date: Optional[str],
                                overall_rating: Optional[str]) -> dict:
    """
    DER. Inspection cadence flag derived from rating_issued_date.
    Matches operator_page.py v5: stale at 24 months, due_soon at 18 months.
    """
    months = _months_since(rating_issued_date)
    if months is None:
        return {
            "tag": TAG_DER,
            "status": "no_rating",
            "label": "No rating on record",
            "months_since": None,
        }
    if months >= STALE_RATING_YEARS * 12:
        return {
            "tag": TAG_DER,
            "status": "stale",
            "label": f"Stale ({months} months since last rating)",
            "months_since": months,
        }
    if months >= DUE_SOON_MONTHS:
        return {
            "tag": TAG_DER,
            "status": "due_soon",
            "label": f"Due soon ({months} months since last rating)",
            "months_since": months,
        }
    return {
        "tag": TAG_DER,
        "status": "current",
        "label": f"Current ({months} months since last rating)",
        "months_since": months,
    }


def _compute_remoteness(aria_plus: Optional[str]) -> dict:
    """OBS. ARIA+ band lookup. v2: handles both label-form and code-form."""
    if aria_plus is None or aria_plus == "":
        return {"tag": TAG_OBS, "code": None, "label": "Not classified"}
    raw = str(aria_plus).strip()
    key = raw.lower()
    if key in ARIA_LABELS:
        return {"tag": TAG_OBS, "code": raw, "label": ARIA_LABELS[key]}
    # Unknown form: pass through the raw value as label (preserves info,
    # avoids the misleading 'Unknown ARIA+ code' wording for non-code data).
    return {"tag": TAG_OBS, "code": raw, "label": raw}


def _compute_brownfield(approval_granted_date: Optional[str],
                        last_transfer_date: Optional[str]) -> dict:
    """
    DER. Brownfield = a transfer date exists and post-dates the original
    approval date. Greenfield = no transfer, or transfer == approval.
    """
    approval = _parse_date(approval_granted_date)
    transfer = _parse_date(last_transfer_date)
    if transfer and approval and transfer > approval:
        months = _months_since(last_transfer_date)
        return {
            "tag": TAG_DER,
            "status": "brownfield",
            "label": "Brownfield acquisition",
            "transfer_date": last_transfer_date,
            "months_since_transfer": months,
        }
    if transfer and not approval:
        return {
            "tag": TAG_DER,
            "status": "brownfield",
            "label": "Brownfield acquisition (no original approval date)",
            "transfer_date": last_transfer_date,
            "months_since_transfer": _months_since(last_transfer_date),
        }
    return {
        "tag": TAG_DER,
        "status": "greenfield",
        "label": "Greenfield (original operator)",
        "transfer_date": None,
        "months_since_transfer": None,
    }


def _compute_subtype(service_sub_type: Optional[str]) -> dict:
    """OBS. service_sub_type with the Harmony-exclusion handling."""
    if not service_sub_type:
        return {
            "tag": TAG_OBS,
            "code": None,
            "label": "Not classified",
            "excluded_from_workforce": True,
            "exclusion_reason": "service_sub_type is NULL (Harmony exclusion)",
        }
    code = str(service_sub_type).strip().upper()
    label_map = {
        "LDC": "Long Day Care",
        "OSHC": "Outside School Hours Care",
        "PSK": "Preschool / Kindergarten",
        "FDC": "Family Day Care",
    }
    excluded = code in ("FDC",) or code not in label_map
    reason = None
    if code == "FDC":
        reason = "FDC excluded from workforce computation"
    elif code not in label_map:
        reason = f"Unknown subtype: {code}"
    return {
        "tag": TAG_OBS,
        "code": code,
        "label": label_map.get(code, code),
        "excluded_from_workforce": excluded,
        "exclusion_reason": reason,
    }


def _qa_scores(service_row: dict) -> list:
    """OBS. Quality assessment area scores qa1..qa7, only those populated."""
    qa_labels = {
        "qa1": "Educational program and practice",
        "qa2": "Children's health and safety",
        "qa3": "Physical environment",
        "qa4": "Staffing arrangements",
        "qa5": "Relationships with children",
        "qa6": "Collaborative partnerships with families and communities",
        "qa7": "Governance and leadership",
    }
    out = []
    for k, label in qa_labels.items():
        v = service_row.get(k)
        if v is not None and str(v).strip() != "":
            out.append({"key": k, "label": label, "rating": str(v).strip(), "tag": TAG_OBS})
    return out


# ─────────────────────────────────────────────────────────────────────
# Layer 4 — POSITION block helpers
# ─────────────────────────────────────────────────────────────────────


def _confidence_for_cohort_n(n: Optional[int]) -> str:
    """DER. Cohort_n display rule (D1, design §3).

    n  < 10   -> 'insufficient' (suppress decile-strip; show "insufficient
                                  peer cohort (n=N)")
    n 10-19   -> 'low'          (full strip + low-confidence pill)
    n >= 20   -> 'normal'       (standard render)
    n is None -> 'unavailable'  (no row for this metric/SA2)
    """
    if n is None:
        return "unavailable"
    if n < 10:
        return "insufficient"
    if n < 20:
        return "low"
    return "normal"


def _build_cohort_label(cohort_def: Optional[str], cohort_row: Optional[dict]) -> str:
    """COM. Human-readable cohort phrase from cohort_def + sa2_cohort row."""
    if not cohort_def:
        return "vs peer cohort"
    cohort_row = cohort_row or {}
    state_name = cohort_row.get("state_name") or ""
    state_short = STATE_SHORT_LABELS.get(state_name, state_name or "—")
    ra_band = cohort_row.get("ra_band")
    ra_short = RA_BAND_SHORT_LABELS.get(
        ra_band, cohort_row.get("ra_name") or "—"
    )
    template = COHORT_LABEL_TEMPLATES.get(cohort_def, "vs peer cohort")
    try:
        return template.format(state_name=state_short, ra_name=ra_short)
    except (KeyError, IndexError):
        return template


def _metric_trajectory(con: sqlite3.Connection,
                       sa2_code: str,
                       metric_name: str) -> tuple[list[dict], Optional[str]]:
    """
    DER. Read this SA2's historical series for `metric_name` from the
    appropriate source table per LAYER3_METRIC_TRAJECTORY_SOURCE.

    Returns (points, kind) where:
      - points = list of {"period": <year|year_qtr>, "value": <number>}
                 sorted ascending by period, NULL/empty values dropped
      - kind   = "annual" | "quarterly" | None (None if no source mapping)

    Returns ([], None) if the metric isn't in the trajectory source map.
    Returns ([], <kind>) if the source is mapped but the SA2 has no rows.
    Never raises on missing tables — returns empty list instead.
    """
    src = LAYER3_METRIC_TRAJECTORY_SOURCE.get(metric_name)
    if not src:
        return [], None
    table = src["table"]
    value_col = src["value_col"]
    period_col = src["period_col"]
    filter_clause = src["filter_clause"]
    kind = src["kind"]

    where_parts = ["sa2_code = ?"]
    if filter_clause:
        where_parts.append(filter_clause)
    where_sql = " AND ".join(where_parts)

    sql = (
        f"SELECT {period_col} AS period, {value_col} AS value "
        f"  FROM {table} "
        f" WHERE {where_sql} "
        f" ORDER BY {period_col}"
    )
    try:
        rows = con.execute(sql, (sa2_code,)).fetchall()
    except sqlite3.OperationalError:
        return [], kind

    points: list[dict] = []
    for r in rows:
        v = r["value"]
        if v is None:
            continue
        # Coerce numeric strings to numbers where possible
        try:
            v = float(v)
        except (TypeError, ValueError):
            continue
        points.append({"period": r["period"], "value": v})
    return points, kind


def _cohort_distribution(con: sqlite3.Connection,
                         metric: str,
                         cohort_def: str,
                         cohort_key: str,
                         self_value: Optional[float],
                         n_bins: int = 20) -> Optional[dict]:
    """
    DER. Build a 20-bin distribution of raw_value for the cohort.

    Reads layer3_sa2_metric_banding for all rows matching (metric,
    cohort_def, cohort_key). Bins their raw_values into n_bins
    equal-width bins between cohort min and max. Returns:

      {
        "bins": [{"bin_min": ..., "bin_max": ..., "count": ...}, ...],
        "self_bin": <int 0..n_bins-1>,
        "cohort_n": <int>,
        "min": <float>,
        "max": <float>,
      }

    Returns None if cohort has < 5 rows (too sparse to bin meaningfully)
    or on any DB error.

    n_bins=20 per Decision D2 — equal-width on raw_value, not decile-
    aligned. Decile-aligned bins are uniform by construction (NTILE) and
    don't surface skew/modality, which is the new information here.
    """
    try:
        rows = con.execute(
            "SELECT raw_value FROM layer3_sa2_metric_banding "
            " WHERE metric = ? AND cohort_def = ? AND cohort_key = ? "
            "   AND raw_value IS NOT NULL",
            (metric, cohort_def, cohort_key),
        ).fetchall()
    except sqlite3.OperationalError:
        return None

    values = []
    for r in rows:
        try:
            values.append(float(r["raw_value"]))
        except (TypeError, ValueError):
            continue
    n = len(values)
    if n < 5:
        return None

    vmin = min(values)
    vmax = max(values)
    if vmin == vmax:
        # Degenerate cohort (every member has the same value).
        return {
            "bins": [{"bin_min": vmin, "bin_max": vmax, "count": n}],
            "self_bin": 0,
            "cohort_n": n,
            "min": vmin,
            "max": vmax,
        }

    width = (vmax - vmin) / n_bins
    counts = [0] * n_bins
    for v in values:
        # Last bin is right-inclusive so vmax doesn't fall outside.
        if v >= vmax:
            idx = n_bins - 1
        else:
            idx = int((v - vmin) / width)
            if idx >= n_bins:
                idx = n_bins - 1
            elif idx < 0:
                idx = 0
        counts[idx] += 1

    self_bin: Optional[int] = None
    if self_value is not None:
        try:
            sv = float(self_value)
            if sv >= vmax:
                self_bin = n_bins - 1
            elif sv <= vmin:
                self_bin = 0
            else:
                self_bin = int((sv - vmin) / width)
                if self_bin >= n_bins:
                    self_bin = n_bins - 1
        except (TypeError, ValueError):
            self_bin = None

    bins = [
        {
            "bin_min": vmin + i * width,
            "bin_max": vmin + (i + 1) * width,
            "count":   counts[i],
        }
        for i in range(n_bins)
    ]
    return {
        "bins":     bins,
        "self_bin": self_bin,
        "cohort_n": n,
        "min":      vmin,
        "max":      vmax,
    }


def _layer3_position(con: sqlite3.Connection, sa2_code: Optional[str]) -> dict:
    """
    DER. Read Layer 3 banding rows for this SA2 + sa2_cohort row for cohort
    labelling. Organises by card (population / labour_market) per
    LAYER3_METRIC_META. Always returns a dict with both card keys; metrics
    not in the DB (or whose SA2 has no row) get confidence='unavailable';
    metrics flagged 'deferred' in LAYER3_METRIC_META get confidence='deferred'.
    Per-row confidence drives the cohort_n display rule (D1).

    Returns:
        {
          "population":    {metric_name: position_entry, ...},
          "labour_market": {metric_name: position_entry, ...},
        }

    Each populated entry contains: display, value_format, direction, card,
    raw_value, year, period_label, decile, band, percentile, cohort_def,
    cohort_key, cohort_n, cohort_label, band_copy (full triple), confidence,
    source.
    """
    out: dict = {"population": {}, "labour_market": {}}

    # Helper to seed a metric slot with status (deferred / unavailable)
    def _stub(meta: dict, confidence: str) -> dict:
        return {
            "display": meta["display"],
            "card": meta["card"],
            "value_format": meta.get("value_format"),
            "direction": meta.get("direction"),
            "confidence": confidence,
            "source": meta.get("source"),
            "band_copy": meta.get("band_copy", {}),
        }

    # If no SA2, every metric is 'unavailable' or 'deferred'
    if not sa2_code:
        for metric_name, meta in LAYER3_METRIC_META.items():
            confidence = "deferred" if meta.get("status") == "deferred" else "unavailable"
            out[meta["card"]][metric_name] = _stub(meta, confidence)
        return out

    # Sibling read: sa2_cohort for cohort labelling (state, ra_band)
    try:
        cohort_row = con.execute(
            "SELECT state_code, state_name, ra_code, ra_name, ra_band "
            "  FROM sa2_cohort WHERE sa2_code = ?",
            (sa2_code,),
        ).fetchone()
        cohort_dict = _row_to_dict(cohort_row) or {}
    except sqlite3.OperationalError:
        cohort_dict = {}

    # Main read: all Layer 3 rows for this SA2
    try:
        rows = con.execute(
            "SELECT metric, year, period_label, cohort_def, cohort_key, "
            "       cohort_n, raw_value, percentile, decile, band "
            "  FROM layer3_sa2_metric_banding "
            " WHERE sa2_code = ?",
            (sa2_code,),
        ).fetchall()
    except sqlite3.OperationalError:
        rows = []  # Table doesn't exist (pre-Layer-3 DB)

    by_metric = {r["metric"]: _row_to_dict(r) for r in rows}

    for metric_name, meta in LAYER3_METRIC_META.items():
        card = meta["card"]
        if meta.get("status") == "deferred":
            out[card][metric_name] = _stub(meta, "deferred")
            continue

        row = by_metric.get(metric_name)
        if not row:
            out[card][metric_name] = _stub(meta, "unavailable")
            continue

        confidence = _confidence_for_cohort_n(row.get("cohort_n"))
        band = row.get("band") or "mid"

        entry = {
            "display": meta["display"],
            "card": card,
            "value_format": meta.get("value_format"),
            "direction": meta.get("direction"),
            "raw_value": row.get("raw_value"),
            "year": row.get("year"),
            "period_label": row.get("period_label"),
            "decile": row.get("decile"),
            "band": band,
            "percentile": row.get("percentile"),
            "cohort_def": row.get("cohort_def"),
            "cohort_key": row.get("cohort_key"),
            "cohort_n": row.get("cohort_n"),
            "cohort_label": _build_cohort_label(row.get("cohort_def"), cohort_dict),
            "band_copy": meta["band_copy"],  # full triple; JS picks via band
            "confidence": confidence,
            "source": meta["source"],
        }

        # Layer 4.2-B: trajectory + cohort distribution.
        # Only populate for normal/low confidence — for insufficient,
        # the strip is suppressed anyway, and rendering a histogram or
        # a single-point trajectory would be misleading.
        if confidence in ("normal", "low"):
            traj_points, traj_kind = _metric_trajectory(con, sa2_code, metric_name)
            if traj_points:
                entry["trajectory"] = traj_points
                entry["trajectory_kind"] = traj_kind

            dist = _cohort_distribution(
                con,
                metric_name,
                row.get("cohort_def"),
                row.get("cohort_key"),
                row.get("raw_value"),
                n_bins=20,
            )
            if dist:
                entry["cohort_distribution"] = dist

        out[card][metric_name] = entry

    return out


def get_centre_payload(service_id: int) -> Optional[dict]:
    """
    Top-level entry point. Returns a fully-hydrated centre payload, or
    None if service_id not found.
    """
    conn = _connect()
    try:
        # Single-row fetch for the service joined to entity, group, brand.
        row = conn.execute("""
            SELECT
                s.*,
                e.legal_name             AS entity_legal_name,
                e.abn                    AS entity_abn,
                e.acn                    AS entity_acn,
                e.entity_type            AS entity_type,
                e.is_propco              AS entity_is_propco,
                e.is_opco                AS entity_is_opco,
                e.is_fgc                 AS entity_is_fgc,
                e.is_notional            AS entity_is_notional,
                g.group_id               AS group_id,
                g.canonical_name         AS group_canonical_name,
                g.display_name           AS group_display_name,
                g.ownership_type         AS group_ownership_type,
                g.head_office_state      AS group_head_office_state,
                g.is_listed              AS group_is_listed,
                g.asx_code               AS group_asx_code,
                b.brand_id               AS brand_id,
                b.name                   AS brand_name,
                b.service_name_prefix    AS brand_prefix
            FROM services s
            LEFT JOIN entities e ON s.entity_id = e.entity_id
            LEFT JOIN groups   g ON e.group_id  = g.group_id
            LEFT JOIN brands   b ON s.brand_id  = b.brand_id
            WHERE s.service_id = ?
              AND s.is_active = 1
        """, (service_id,)).fetchone()

        if row is None:
            return None

        r = _row_to_dict(row)

        # --- HEADER block ---
        ownership_raw = r.get("group_ownership_type") or "unknown"
        header = {
            "service_id": r["service_id"],
            "service_name": r.get("service_name"),
            "service_approval_number": r.get("service_approval_number"),
            "provider_approval_number": r.get("provider_approval_number"),
            "address": {
                "address_line": r.get("address_line"),
                "suburb": r.get("suburb"),
                "state": r.get("state"),
                "postcode": r.get("postcode"),
            },
            "lat": r.get("lat"),
            "lng": r.get("lng"),
            "parent_group": {
                "group_id": r.get("group_id"),
                "name": r.get("group_canonical_name") or r.get("group_display_name"),
                "ownership_type_code": ownership_raw,
                "ownership_type_label": OWNERSHIP_LABELS.get(ownership_raw, ownership_raw),
                "head_office_state": r.get("group_head_office_state"),
                "is_listed": bool(r.get("group_is_listed")) if r.get("group_is_listed") is not None else None,
                "asx_code": r.get("group_asx_code"),
            },
            "entity": {
                "entity_id": r.get("entity_id"),
                "legal_name": r.get("entity_legal_name"),
                "abn": r.get("entity_abn"),
                "acn": r.get("entity_acn"),
                "entity_type": r.get("entity_type"),
                "is_propco": bool(r.get("entity_is_propco")) if r.get("entity_is_propco") is not None else False,
                "is_opco": bool(r.get("entity_is_opco")) if r.get("entity_is_opco") is not None else False,
                "is_fgc": bool(r.get("entity_is_fgc")) if r.get("entity_is_fgc") is not None else False,
                "is_notional": bool(r.get("entity_is_notional")) if r.get("entity_is_notional") is not None else False,
            },
            "brand": {
                "brand_id": r.get("brand_id"),
                "name": r.get("brand_name"),
                "prefix": r.get("brand_prefix"),
            } if r.get("brand_id") else None,
        }

        # --- NQS RATING block ---
        cadence = _compute_inspection_cadence(
            r.get("rating_issued_date"),
            r.get("overall_nqs_rating"),
        )
        nqs = {
            "overall_rating": {
                "tag": TAG_OBS,
                "value": r.get("overall_nqs_rating"),
            },
            "rating_issued_date": {
                "tag": TAG_OBS,
                "value": r.get("rating_issued_date"),
            },
            "inspection_cadence": cadence,
        }

        # --- PLACES & SUBTYPE block ---
        subtype = _compute_subtype(r.get("service_sub_type"))
        places = {
            "approved_places": {
                "tag": TAG_OBS,
                "value": r.get("approved_places"),
            },
            "service_sub_type": subtype,
            "long_day_care_flag": bool(r.get("long_day_care")) if r.get("long_day_care") is not None else None,
            "kinder_approved": {
                "tag": TAG_OBS,
                "value": bool(r.get("kinder_approved")) if r.get("kinder_approved") is not None else None,
                "source": r.get("kinder_source"),
            },
            "provider_management_type": {
                "tag": TAG_OBS,
                "value": r.get("provider_management_type"),
            },
        }

        # --- CATCHMENT block (SEIFA + ARIA) ---
        catchment = {
            "seifa_decile": {
                "tag": TAG_OBS,
                "value": r.get("seifa_decile"),
            },
            "remoteness": _compute_remoteness(r.get("aria_plus")),
            "sa2": {
                "code": r.get("sa2_code"),
                "name": r.get("sa2_name"),
            },
            "service_catchment_cache": {
                "tag": TAG_DER,
                "status": "pending",
                "note": "Catchment cache not yet populated (Tier 3 ingest).",
            },
        }

        # --- POSITION block (Layer 3 banding) ---
        position = _layer3_position(conn, r.get("sa2_code"))

        # --- QA SCORES block ---
        qa_scores = _qa_scores(r)

        # --- BROWNFIELD / TENURE block ---
        tenure = _compute_brownfield(
            r.get("approval_granted_date"),
            r.get("last_transfer_date"),
        )
        tenure["approval_granted_date"] = r.get("approval_granted_date")

        # --- ASSEMBLE ---
        payload = {
            "schema_version": "centre_payload_v4",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "header": header,
            "nqs": nqs,
            "places": places,
            "catchment": catchment,
            "position": position,
            "qa_scores": qa_scores,
            "tenure": tenure,
            "commentary": _commentary_lines(header, nqs, places, tenure, subtype),
        }
        return payload
    finally:
        conn.close()


def _commentary_lines(header, nqs, places, tenure, subtype) -> list:
    """COM. Rule-based commentary lines. Conservative: skip if data missing."""
    lines = []
    rating = (nqs["overall_rating"]["value"] or "").strip()
    if rating in ("Working Towards NQS", "Significant Improvement Required"):
        lines.append({
            "tag": TAG_COM,
            "severity": "amber" if rating == "Working Towards NQS" else "red",
            "text": f"Centre is currently rated '{rating}'.",
        })
    elif rating in ("Excellent", "Exceeding NQS"):
        lines.append({
            "tag": TAG_COM,
            "severity": "green",
            "text": f"Centre holds a strong NQS rating ('{rating}').",
        })

    cadence = nqs["inspection_cadence"]
    if cadence["status"] == "stale":
        lines.append({
            "tag": TAG_COM,
            "severity": "amber",
            "text": "Rating is stale — re-inspection overdue.",
        })
    elif cadence["status"] == "due_soon":
        lines.append({
            "tag": TAG_COM,
            "severity": "info",
            "text": "Rating approaches its 2-year refresh window.",
        })

    if subtype["excluded_from_workforce"]:
        lines.append({
            "tag": TAG_COM,
            "severity": "info",
            "text": f"Excluded from workforce model: {subtype['exclusion_reason']}",
        })

    if tenure["status"] == "brownfield" and tenure.get("months_since_transfer") is not None:
        if tenure["months_since_transfer"] <= 18:
            lines.append({
                "tag": TAG_COM,
                "severity": "info",
                "text": f"Recent acquisition — {tenure['months_since_transfer']} months under current ownership.",
            })

    return lines


# CLI smoke test
if __name__ == "__main__":
    import json
    import sys
    sid = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    payload = get_centre_payload(sid)
    if payload is None:
        print(f"No active service with service_id={sid}")
        sys.exit(1)
    print(json.dumps(payload, indent=2, default=str))
