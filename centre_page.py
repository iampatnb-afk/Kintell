"""
centre_page.py — Phase 2 backend helper for centre.html
Version: v12 (2026-04-30) — Layer 4.2-A.3a-fix iter 4 (F1-β): JSA IVI methodology lifted out of hover-gated OBS tooltip into a new about_data field on IVI rows. Renderer surfaces it as a permanent visible block under the chart so credit readers don't need to discover the OBS hover affordance. OBS source string now carries full methodology one-liner (what the IVI is, where it comes from); intent_copy tightened to credit-relevant framing only. Reader hovers OBS for data provenance, reads inline copy for credit signal.

v10 changes (2026-04-30, Layer 4.2-A.3b):
  - INDUSTRY_BAND_THRESHOLDS — declarative table of
    absolute industry thresholds for the 3 catchment
    ratios with meaningful industry bands. Sources: PC
    universal-access target (1.0 places/child = all
    children, 3 days/week); Remara Strategic Insights
    v4.2 real distribution by SES + remoteness; Credit
    Committee Brief break-even (70%) + target (85%)
    occupancy. Bands are ordered low->high; each entry
    is (max_exclusive, key, label, note).
  - _industry_band_for(metric, raw_value) helper resolves
    a raw value to the matching band entry, or None if
    the metric isn't in the thresholds table.
  - LAYER3_METRIC_META: industry_thresholds=True added
    on sa2_supply_ratio / sa2_child_to_place /
    sa2_demand_supply. Renderer reads this flag to
    decide whether to surface the industry band line.
  - _layer3_position emits industry_band /
    industry_band_label / industry_band_note on every
    populated entry; None on stubs (deferred /
    unavailable).
  - schema_version: centre_payload_v5 -> v6.

v9 changes (2026-04-30, Layer 4.2-A.3):
  - LAYER3_METRIC_META: 5 catchment entries added —
    sa2_supply_ratio + sa2_child_to_place (reversible
    pair, DEC-74), sa2_adjusted_demand (absolute),
    sa2_demand_supply (reversible <-> demand_supply_inv
    rendered at HTML level), sa2_demand_share_state
    (context-only weight, unbanded — rank-by-construction
    per Layer 2.5 sub-pass 2.5.2). Card key:
    "catchment_position". Band copy per layer4_3_design
    §4.6. Reversibility infrastructure (v7) is now
    activated for the two pairs.
  - LAYER3_METRIC_INTENT_COPY: capture_rate -> 
    demand_share_state key rename (4.3.5b cleanup).
    sa2_-prefixed copies added so the registry's
    canonical metric names resolve.
  - _layer3_position: third card key catchment_position
    in returned dict. Special-case branch for
    sa2_demand_share_state — reads raw from
    service_catchment_cache (no Layer 3 banding row
    exists; rank-by-construction).
  - POSITION_CARD_ORDER: catchment_position list added.
  - schema_version: centre_payload_v4 -> v5.

Provides get_centre_payload(service_id) -> dict
Returns full single-centre detail: service + entity + group + brand,
with OBS/DER/COM treatment matching operator_page.py conventions.

v8 changes (2026-04-29, post-bundle wire-up):
  - JSA IVI Workforce supply rows now go live. The actual table in
    Patrick's DB (jsa_ivi_state_monthly) uses column `vacancy_count`
    for the numeric value, which wasn't in v7's _try_query_ivi value-
    column candidate list. v8 adds it. State column is `state_code`
    (already in v7 candidate list); period column is `year_month`
    (already in v7 candidate list). The two ANZSCO-state-monthly
    rows in workforce_supply now query the actual table and return
    a live trajectory.

v7 changes (2026-04-29, bundled round after 4.3.8):
  - KINDER MIRRORING: KINDER_PAT regex (deliberately duplicated from
    operator_page.py — see comment near constant for canonical-source
    note). New `kinder_name_match` and `kinder_summary` blocks under
    `places`. Three signals composed into a derived headline state
    (confirmed both / confirmed ACECQA / likely name-only / not flagged).
    The signals array is open — future detection methods append.
  - WORKFORCE SUPPLY CONTEXT (DEC-76, sub-pass 4.3.9): new top-level
    payload section `workforce_supply` with 4 rows — Child Carer
    vacancy index (ANZSCO 4211), ECT vacancy index (ANZSCO 2411), ECEC
    Award minimum rates, Three-Day Guarantee. Rows render gracefully
    as deferred placeholders when source data isn't ingested. Block
    renders default-open in centre.html. State for the first two rows
    is read from the centre's address.
  - PERSPECTIVE TOGGLE INFRASTRUCTURE (DEC-74, sub-pass 4.3.7): four
    new optional fields on the metric registry contract — `reversible`,
    `pair_with`, `default_perspective`, `perspective_labels`. The
    fields are documented in the LAYER3_METRIC_META docstring; no
    existing metric carries `reversible: true` because the four
    catchment ratios from Layer 4.2-A scope aren't in the registry
    yet. Renderer infrastructure in centre.html v3.6 picks up these
    fields when catchment metrics ship.

v6 changes (2026-04-29, Layer 4.3 sub-pass 4.3.8):
  - New LAYER3_METRIC_INTENT_COPY constant — one-sentence interpretive
    prose per metric, surfaced inline beneath the band chips on the
    centre page (renderer side in centre.html v3.5). Covers all 10
    currently-rendered Position metrics + the 4 catchment ratios from
    the Layer 4.2-A scope (DEC-74) + 4 Workforce supply context rows
    from DEC-76. Catchment + workforce entries sit dormant until their
    respective sub-passes (4.2-A.3 and 4.3.9) wire the rows; centre.html
    reads the constant via p.intent_copy and renders silently if the
    field is missing (P-2 honest absence).
  - _layer3_position propagates intent_copy onto every entry it emits
    (stub + populated). Renderer reads p.intent_copy; missing field =
    no slot rendered.
  - This sub-pass is BUNDLED with the trend-window % change feature
    (centre.html v3.4 -> v3.5), which is renderer-only and needs no
    Python-side changes. Operator-requested bundle to ship both
    renderer enhancements in one round.

v5 changes (2026-04-29, Layer 4.3 sub-pass 4.3.6):
  - New `row_weight` field on every LAYER3_METRIC_META entry per DEC-75:
      "full"    — trajectory + cohort histogram + decile strip + chips
      "lite"    — decile strip + chips + "as at YYYY" stamp (no
                  trajectory, no cohort histogram). For metrics with an
                  SA2 peer cohort but <5 dense series points.
      "context" — single-fact line (optional state-level sparkline).
                  For state-level / national metrics with no SA2 peer
                  cohort.
    Reclassifications applied:
      sa2_lfp_persons / _females / _males  → "lite"
      jsa_vacancy_rate                     → "context"
      All other Position metrics           → "full"
    The renderer in centre.html switches on this field. Field shape is
    a string with explicit branches + default-to-"full" fallback in the
    renderer; future row classes (e.g. daily-rate) add a 4th value
    without retrofit. Closes G5 of recon/layer4_3_design.md.
  - _layer3_position now propagates row_weight onto every entry it
    emits, including stubs (deferred / unavailable). Renderer reads
    p.row_weight.

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

import re
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

# Regex matching "kindergarten" / "kinder" / "preschool" / "pre-school"
# in service names (case-insensitive, word-boundary). DELIBERATELY
# DUPLICATED from operator_page.py — that file is the canonical source
# (where it was first defined and where the operator-level
# kinder_by_name aggregate consumes it). If the regex ever drifts
# between the two files, operator_page.py's version is authoritative.
# The duplication is preferred over a shared utility module here
# because the pattern is small and stable, and a shared module would
# be heavier than the problem.
KINDER_PAT = re.compile(r'\b(kinder(garten)?|pre-?school)\b', re.I)

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
# - row_weight:    'full' | 'lite' | 'context' per DEC-75 — controls
#                  visual treatment in centre.html renderPositionRow.
#                    full    = trajectory + cohort histogram + decile
#                              strip + chips
#                    lite    = decile strip + chips + "as at YYYY"
#                    context = single-fact line
#                  Renderer falls back to 'full' for any unknown value;
#                  future row classes (daily-rate) add a 4th branch.
# - status:        optional 'deferred' for metrics not yet in Layer 3
# - source:        OBS-badge attribution string for the raw value
# - band_copy:     {'low': ..., 'mid': ..., 'high': ...} interpretive text
#
# ── Perspective toggle fields (DEC-74, sub-pass 4.3.7) ──────────────
# Optional. Present only on metrics that have a meaningful inverse
# (the canonical V1 cases are the four Layer 4.2-A catchment ratios:
# supply_ratio ↔ child_to_place, demand_supply ↔ demand_supply_inv).
# When present, centre.html's renderer surfaces a per-row "perspective"
# toggle button that swaps the active perspective at render time.
#
# - reversible:           bool — true if this metric has an inverse pair
# - pair_with:            str — registry key of the inverse metric
# - default_perspective:  str — which perspective renders first ('forward' | 'inverse')
# - perspective_labels:   {'forward': '...', 'inverse': '...'} — toggle button labels
#
# Locked band-copy templates (DEC-74): each direction has a fixed
# template lookup — high_is_concerning vs high_is_positive — so when
# the renderer swaps the perspective, the band copy swaps with it
# rather than reading stale text. Templates live in centre.html
# alongside the toggle infrastructure.
#
# In V1, NO metric in this registry carries reversible:true. The four
# catchment ratios (which will) ship with sub-pass 4.2-A.3. The toggle
# infrastructure in centre.html sits inert until those rows arrive —
# zero retrofit cost on the renderer side at that point.
# ─────────────────────────────────────────────────────────────
# Layer 4.2-A.3b — industry-absolute threshold table.
# ─────────────────────────────────────────────────────────────
# For the 3 catchment ratios with meaningful absolute bounds,
# this table maps raw values to industry bands. Renders BELOW
# the existing decile band chips on the centre page so credit
# readers see both lenses: "where this SA2 sits vs same-state
# same-remoteness peers" (decile) AND "where this SA2 sits in
# absolute industry terms" (industry_band).
#
# Source synthesis:
#   - PC universal-access target = 1.0 places/child = "all
#     children, 3 days/week" (Productivity Commission report
#     v1, fig 11). Australian markets capped at 1.0 in PC
#     analysis; majority well below.
#   - Real Australian distribution (Remara Strategic Insights
#     v4.2 p.5): high-SES 33.5/100, mid-SES 24/100, low-SES
#     19.7/100; major cities 34.2/100, regional 22.9/100,
#     remote 24.9/100. So real values cluster 0.20-0.35 with
#     metro outliers reaching 1.0+ in dense employment hubs.
#   - Break-even occupancy = 70% (Credit Committee Brief p.14
#     "Localised Oversupply"). Target occupancy = 85%
#     (Established loan key consideration, p.1).
#
# Each band entry is (max_exclusive, key, label, note). The
# band a value falls into is the FIRST entry whose
# max_exclusive > value. Last entry uses float("inf").
INDUSTRY_BAND_THRESHOLDS = {
    "sa2_supply_ratio": [
        (0.10, "desert",        "childcare desert",
         "PC: well below universal access; access constrained"),
        (0.20, "undersupplied", "undersupplied",
         "below low-SES Australian average (~0.20)"),
        (0.30, "below_bench",   "below benchmark",
         "approaching mid-SES Australian average (~0.24)"),
        (0.40, "at_bench",      "at benchmark",
         "near high-SES major-cities average (~0.34)"),
        (1.00, "well_served",   "well served",
         "above benchmark; approaching universal access"),
        (1.50, "at_target",     "at universal-access target",
         "PC target: 1.0 places per child = 3 days/week for all"),
        (float("inf"), "saturated", "saturated",
         ">1.0 places per child; possible oversupply"),
    ],
    "sa2_child_to_place": [
        (1.00, "excess_capacity", "excess capacity",
         "supply matches universal-access target"),
        (2.50, "balanced",        "balanced",
         "near at-benchmark for Australia"),
        (5.00, "tight",           "tight",
         "demand pressure; saturation pressure (inverted)"),
        (10.00, "constrained",    "constrained",
         "significant access limitation"),
        (float("inf"), "severe",  "severe constraint",
         "effectively zero choice"),
    ],
    "sa2_demand_supply": [
        (0.40, "soft",     "soft fill risk",
         "below 70% break-even at typical 85% occupancy"),
        (0.55, "near_be",  "near break-even",
         "approaching 70% break-even occupancy threshold"),
        (0.85, "viable",   "viable",
         "comfortable fill expectation"),
        (float("inf"), "strong", "strong fill",
         "demand pull; growth-supportive"),
    ],
}

def _industry_band_for(metric_name, raw_value):
    """DER. Resolve a raw value to the matching industry band
    entry per INDUSTRY_BAND_THRESHOLDS. Returns dict with key
    / label / note, or None if metric has no thresholds or
    raw_value is None.
    """
    if raw_value is None:
        return None
    bands = INDUSTRY_BAND_THRESHOLDS.get(metric_name)
    if not bands:
        return None
    try:
        v = float(raw_value)
    except (TypeError, ValueError):
        return None
    for max_excl, key, label, note in bands:
        if v < max_excl:
            return {"key": key, "label": label, "note": note}
    return None


LAYER3_METRIC_META = {
    # ── Population card ─────────────────────────────────────────────
    "sa2_under5_count": {
        "display": "Under-5 population",
        "card": "population",
        "value_format": "int",
        "direction": "high_is_positive",
        "row_weight": "full",
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
        "row_weight": "full",
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
        "row_weight": "full",
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
        "row_weight": "full",
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
        "row_weight": "full",
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
        "row_weight": "full",
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
        "row_weight": "full",
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
        "row_weight": "full",
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
        "row_weight": "lite",
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
        "row_weight": "lite",
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
        "row_weight": "lite",
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
        "row_weight": "context",
        "status": "deferred",
        "source": "JSA IVI (state-level, computed at read time — pending)",
        "band_copy": {"low": "—", "mid": "—", "high": "—"},
    },

    # ── Catchment position card (Layer 4.2-A.3) ─────────────────
    # 5 metrics surfaced from service_catchment_cache + layer3
    # banding (sub-pass 2.5.2). Two reversible pairs activate
    # the DEC-74 perspective toggle (renderer-side, v7 fields).
    # demand_supply_inv is NOT in this registry — it is rendered
    # at HTML level by inverting demand_supply's raw_value when
    # the perspective toggle is in inverse state. Templates for
    # the inverse direction live in centre.html v3.6+.
    "sa2_supply_ratio": {
        "display": "Supply ratio",
        "card": "catchment_position",
        "value_format": "ratio_x",
        "direction": "high_is_concerning",
        "row_weight": "lite",  # point-in-time data; no trajectory
        "industry_thresholds": True,  # v10
        "source": "service_catchment_cache (places / under-5 pop)",
        "reversible": True,
        "pair_with": "sa2_child_to_place",
        "default_perspective": "forward",
        "perspective_labels": {
            "forward": "competition",
            "inverse": "demand",
        },
        "band_copy": {
            "low":  "undersupplied — opportunity",
            "mid":  "balanced supply",
            "high": "saturated — competition risk",
        },
    },
    "sa2_child_to_place": {
        "display": "Children per place",
        "card": "catchment_position",
        "value_format": "ratio_x",
        "direction": "high_is_positive",
        "row_weight": "lite",
        "industry_thresholds": True,  # v10
        "source": "service_catchment_cache (under-5 pop / places)",
        "reversible": True,
        "pair_with": "sa2_supply_ratio",
        "default_perspective": "forward",
        "perspective_labels": {
            "forward": "demand-per-place",
            "inverse": "competition",
        },
        "band_copy": {
            "low":  "thin demand per place",
            "mid":  "balanced demand per place",
            "high": "strong demand per place",
        },
    },
    "sa2_adjusted_demand": {
        "display": "Adjusted demand",
        "card": "catchment_position",
        "value_format": "int",
        "direction": "high_is_positive",
        "row_weight": "lite",
        "source": "service_catchment_cache (u5 × calibrated_rate × 0.6)",
        "band_copy": {
            "low":  "thin calibrated demand",
            "mid":  "average calibrated demand",
            "high": "deep calibrated demand",
        },
    },
    "sa2_demand_supply": {
        "display": "Demand vs supply",
        "card": "catchment_position",
        "value_format": "ratio_x",
        "direction": "high_is_positive",
        "row_weight": "lite",
        "industry_thresholds": True,  # v10
        "source": "service_catchment_cache (adjusted_demand / places)",
        "reversible": True,
        "pair_with": "sa2_demand_supply",  # inverse rendered at HTML level
        "default_perspective": "forward",
        "perspective_labels": {
            "forward": "fill",
            "inverse": "spare capacity",
        },
        "band_copy": {
            "low":  "soft catchment — fill risk",
            "mid":  "in balance",
            "high": "demand pull — strong fill expected",
        },
    },
    "sa2_demand_share_state": {
        "display": "Share of state demand",
        "card": "catchment_position",
        "value_format": "percent_share",
        "direction": "high_is_positive",
        "row_weight": "context",  # rank-by-construction; no banding
        "source": "service_catchment_cache (this SA2's adjusted_demand / state total)",
        "band_copy": {
            "low": "—", "mid": "—", "high": "—",
        },
    },
}

# Display order within each card (drives section order in the UI).
POSITION_CARD_ORDER = {
    # Catchment position is the headline credit signal —
    # rendered first in centre.html render() per Layer 4.2-A.3.
    "catchment_position": [
        "sa2_supply_ratio",
        "sa2_demand_supply",
        "sa2_child_to_place",
        "sa2_adjusted_demand",
        "sa2_demand_share_state",
    ],
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
# Layer 4.3 sub-pass 4.3.8 — inline intent copy per DEC-75 / Layer 4.3
# design.
# ─────────────────────────────────────────────────────────────────────
# One-sentence interpretive prose per metric, rendered inline beneath
# the band chips on the centre page. Tells the credit-lens reader what
# the metric means for THIS centre's risk picture, not the metric in
# the abstract. Avoid restating the band chip text; the chip is "what
# the band says", the intent line is "why it matters".
#
# Coverage:
#   - All 10 currently-rendered Position metrics (Population + Labour
#     Market cards). Live in centre.html v3.5 today.
#   - 6 catchment-ratio entries covering the 4 ratios in the Layer 4.2-A
#     scope: supply_ratio + its reversible inverse child_to_place,
#     demand_supply + its reversible inverse demand_supply_inv,
#     adjusted_demand, capture_rate (2 reversible pairs + 2 absolute).
#     Sit dormant until sub-pass 4.2-A.3 wires the catchment row
#     renderer; centre.html reads p.intent_copy and renders silently
#     if the row entry is absent, so no retrofit needed when those
#     rows ship.
#   - 4 Workforce supply context rows per DEC-76. Sit dormant until
#     sub-pass 4.3.9 wires the workforce block. The block has its own
#     renderer (DEC-76) which will read these entries.
#
# Total: 22 entries across the three groups.
#
# Reversible-pair entries (DEC-74) — supply_ratio ↔ child_to_place and
# demand_supply ↔ demand_supply_inv — each carry their own intent copy.
# Sub-pass 4.3.7 wires the perspective toggle; the renderer there will
# pick the appropriate entry based on the active perspective.
#
# Metrics not in this map render no intent slot (P-2 honest absence).
LAYER3_METRIC_INTENT_COPY = {
    # ── Population card ────────────────────────────────────────────
    "sa2_under5_count":
        "Under-5 count is the immediate addressable demand pool; "
        "deeper pools support more places per centre and absorb local "
        "competition without occupancy stress.",
    "sa2_total_population":
        "Total population sets the macro context for catchment depth "
        "and adjacent-service traffic; small SA2s carry thinner "
        "fallback demand if the under-5 pool weakens.",
    "sa2_births_count":
        "Births are the leading indicator for under-5 demand 0–4 years "
        "out; a falling births trend is an early warning even when "
        "current under-5 numbers look healthy.",
    "sa2_under5_growth_5y":
        "Five-year under-5 growth shows whether the demand pool is "
        "expanding, holding, or contracting; flagged as a leading "
        "signal for catchment trajectory.",
    # ── Labour market card ─────────────────────────────────────────
    "sa2_unemployment_rate":
        "Unemployment rate is a fee-sensitivity signal — high "
        "unemployment correlates with parents' price sensitivity and "
        "with softer demand on premium price points.",
    "sa2_median_employee_income":
        "Employee income proxies the day-to-day spending power of the "
        "earning parent cohort; higher income tolerates higher daily "
        "rates without the catchment falling away.",
    "sa2_median_household_income":
        "Household income captures dual-income capacity; relevant for "
        "fee tolerance on full-time placements where two earners "
        "carry the cost.",
    "sa2_median_total_income":
        "Total income (excl. pensions) is the broadest fee-tolerance "
        "signal — it includes investment and self-employment income "
        "that employee-income alone misses.",
    "sa2_lfp_persons":
        "Labour-force participation is the workforce-demand baseline; "
        "high LFP means more parents in paid work and more demand for "
        "structured childcare hours.",
    "sa2_lfp_females":
        "Female LFP is the dominant driver of childcare demand; in "
        "Australian data, mothers' return-to-work rates set most of "
        "the demand-side variation.",
    "sa2_lfp_males":
        "Male LFP rounds out the dual-income signal — high female + "
        "high male LFP indicates dual-earner households with full-time "
        "childcare needs.",
    "jsa_vacancy_rate":
        "JSA vacancy rate is a state-level workforce-tightness signal; "
        "high vacancy rates flag staffing pressure even where local "
        "demand is healthy.",

    # ── Catchment ratios (Layer 4.2-A scope; DEC-74) — dormant in V1
    # until sub-pass 4.2-A.3 wires the renderer. Reversible-pair
    # entries each carry their own intent copy; sub-pass 4.3.7 will
    # pick the appropriate one based on the active perspective.
    # ──────────────────────────────────────────────────────────────
    "supply_ratio":
        "Supply ratio (places per child) measures local competition "
        "intensity; high values flag saturation risk and pressure on "
        "fill rates, low values flag undersupplied catchments with "
        "opportunity.",
    "child_to_place":
        "Child-to-place ratio is supply ratio inverted — frames the "
        "same data as demand-headroom; high values flag strong demand "
        "per place, low values flag thin demand per place.",
    "adjusted_demand":
        "Adjusted demand is the calibrated demand estimate after "
        "participation rate and attendance factor — the realistic "
        "demand the catchment can actually fill.",
    "demand_share_state":
        "Share of state demand puts this catchment's demand pool "
        "in state-wide context — high values flag concentration of "
        "demand in this SA2, low values flag a long-tail catchment "
        "in a state-wide distribution.",
    "demand_supply":
        "Demand-supply ratio (adjusted demand / places) is the fill "
        "expectation — high values flag demand pull and strong "
        "expected fill, low values flag soft catchments.",
    "demand_supply_inv":
        "Demand-supply ratio inverted frames the same data as "
        "spare-capacity headroom; high values flag abundant capacity, "
        "low values flag tight capacity vs demand.",

    # ── Catchment intent copy keyed by registry name (Layer 4.2-A.3) ──
    # The unprefixed keys above (supply_ratio, child_to_place, etc.) are
    # the original Layer 4.3 sub-pass 4.3.8 entries, kept for
    # backward reference. The sa2_-prefixed copies below are
    # what _layer3_position actually reads (registry-canonical
    # metric_name).
    "sa2_supply_ratio":
        "Supply ratio (places per child) measures local competition "
        "intensity; high values flag saturation risk and pressure on "
        "fill rates, low values flag undersupplied catchments with "
        "opportunity.",
    "sa2_child_to_place":
        "Children per place inverts supply ratio — frames the same "
        "data as demand-headroom; high values flag strong demand per "
        "place, low values flag thin demand per place.",
    "sa2_adjusted_demand":
        "Adjusted demand is the calibrated demand estimate after "
        "participation rate and attendance factor — the realistic "
        "demand the catchment can actually fill.",
    "sa2_demand_supply":
        "Demand-supply ratio (adjusted demand / places) is the fill "
        "expectation — high values flag demand pull and strong "
        "expected fill, low values flag soft catchments.",
    "sa2_demand_share_state":
        "Share of state demand puts this catchment in state-wide "
        "context — high values flag concentrated demand here, low "
        "values flag a long-tail position in the state distribution.",

    # ── Workforce supply context (DEC-76; sub-pass 4.3.9) — dormant
    # in V1 until the workforce block renderer ships.
    # ──────────────────────────────────────────────────────────────
    "jsa_ivi_4211_child_carer":
        "Child carer (ANZSCO 4211) vacancy intensity — leading "
        "indicator of educator-supply pressure regardless of local "
        "demand. Rising counts flag wage-cost risk and "
        "staffing-driven occupancy risk.",
    "jsa_ivi_2411_ect":
        "Early childhood teacher (ANZSCO 2411) vacancy intensity — "
        "ECT shortfalls can disqualify centres from quality ratings "
        "and drive regulatory exposure. Sustained elevated counts "
        "here are a leading indicator of compliance-cost and "
        "refinanceability risk.",
    "ecec_award_rates":
        "ECEC Award minimum rates set the wage floor across CIII / "
        "Diploma / ECT classifications; rate increases compress "
        "operator margins where fees can't move freely.",
    "three_day_guarantee":
        "Three-Day Guarantee (Jan 2026) entitles every child to three "
        "subsidised days — shifts demand floor upward across all "
        "catchments and rewires the family-payment model.",
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


def _read_demand_share_state(con: sqlite3.Connection,
                              sa2_code: Optional[str]
                              ) -> Optional[float]:
    """DER. Read demand_share_state for any service in this SA2.

    The cache broadcasts the SA2-level value to every active
    service in that SA2, so any row's value is canonical for
    the SA2. Returns None if the SA2 has no active services or
    if the cache has no row for it.
    """
    if not sa2_code:
        return None
    try:
        row = con.execute(
            "SELECT demand_share_state FROM service_catchment_cache"
            " WHERE sa2_code = ? AND demand_share_state IS NOT NULL"
            " LIMIT 1",
            (sa2_code,),
        ).fetchone()
    except sqlite3.OperationalError:
        return None
    return row[0] if row else None


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
    out: dict = {
        "catchment_position": {},
        "population":         {},
        "labour_market":      {},
    }

    # Helper to seed a metric slot with status (deferred / unavailable).
    # Takes metric_name so we can look up intent_copy from the
    # LAYER3_METRIC_INTENT_COPY constant.
    def _stub(metric_name: str, meta: dict, confidence: str) -> dict:
        return {
            "display": meta["display"],
            "card": meta["card"],
            "value_format": meta.get("value_format"),
            "direction": meta.get("direction"),
            "row_weight": meta.get("row_weight", "full"),
            "intent_copy": LAYER3_METRIC_INTENT_COPY.get(metric_name),
            # Sub-pass 4.3.7 perspective fields (DEC-74). Optional —
            # propagated unconditionally so renderer reads p.reversible
            # without needing a fallback. None / missing = no toggle.
            "reversible":          meta.get("reversible", False),
            "pair_with":           meta.get("pair_with"),
            "default_perspective": meta.get("default_perspective"),
            "perspective_labels":  meta.get("perspective_labels"),
            "confidence": confidence,
            "source": meta.get("source"),
            "band_copy": meta.get("band_copy", {}),
            # v10: industry-absolute band fields. Always None
            # on stubs (no raw value to evaluate).
            "industry_band":       None,
            "industry_band_label": None,
            "industry_band_note":  None,
        }

    # If no SA2, every metric is 'unavailable' or 'deferred'
    if not sa2_code:
        for metric_name, meta in LAYER3_METRIC_META.items():
            confidence = "deferred" if meta.get("status") == "deferred" else "unavailable"
            out[meta["card"]][metric_name] = _stub(metric_name, meta, confidence)
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

    # Layer 4.2-A.3: sa2_demand_share_state is unbanded
    # (rank-by-construction); read raw from cache.
    cache_share = _read_demand_share_state(con, sa2_code)

    for metric_name, meta in LAYER3_METRIC_META.items():
        card = meta["card"]
        if meta.get("status") == "deferred":
            out[card][metric_name] = _stub(metric_name, meta, "deferred")
            continue

        # Special-case: demand_share_state has no Layer 3 row.
        if metric_name == "sa2_demand_share_state":
            if cache_share is None:
                out[card][metric_name] = _stub(metric_name, meta, "unavailable")
            else:
                stub = _stub(metric_name, meta, "normal")
                stub["raw_value"] = cache_share
                stub["period_label"] = "as at 2026-04-30"
                out[card][metric_name] = stub
            continue

        row = by_metric.get(metric_name)
        if not row:
            out[card][metric_name] = _stub(metric_name, meta, "unavailable")
            continue

        confidence = _confidence_for_cohort_n(row.get("cohort_n"))
        band = row.get("band") or "mid"

        entry = {
            "display": meta["display"],
            "card": card,
            "value_format": meta.get("value_format"),
            "direction": meta.get("direction"),
            "row_weight": meta.get("row_weight", "full"),
            "intent_copy": LAYER3_METRIC_INTENT_COPY.get(metric_name),
            # Sub-pass 4.3.7 perspective fields (DEC-74).
            "reversible":          meta.get("reversible", False),
            "pair_with":           meta.get("pair_with"),
            "default_perspective": meta.get("default_perspective"),
            "perspective_labels":  meta.get("perspective_labels"),
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

        # v10: industry-absolute band lookup for opted-in
        # metrics (industry_thresholds=True).
        if meta.get("industry_thresholds"):
            ib = _industry_band_for(metric_name, entry["raw_value"])
            entry["industry_band"]       = ib["key"]   if ib else None
            entry["industry_band_label"] = ib["label"] if ib else None
            entry["industry_band_note"]  = ib["note"]  if ib else None
        else:
            entry["industry_band"]       = None
            entry["industry_band_label"] = None
            entry["industry_band_note"]  = None

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

        # Kinder recognition (mirrors operator_page.py portfolio-level
        # treatment). Three signals:
        #   - acecqa_flag: services.kinder_approved (bool|None)
        #   - name_match:  KINDER_PAT regex against services.service_name
        #   - (future)     other detection methods append to signals[]
        # Headline mapping in centre.html reads kinder_summary.signals
        # and produces a four-state headline (confirmed both / confirmed
        # ACECQA / likely name-only / not flagged). Treats ACECQA=null
        # the same as ACECQA=False for the headline (matches operator-
        # page kinder_by_flag aggregate convention) but keeps the null
        # state visible in the evidence row for provenance.
        kinder_acecqa_raw = r.get("kinder_approved")
        kinder_acecqa = (
            None if kinder_acecqa_raw is None
            else bool(kinder_acecqa_raw)
        )
        service_name = r.get("service_name") or ""
        name_match = KINDER_PAT.search(str(service_name))
        kinder_name_match_value = bool(name_match)
        kinder_name_match_text = name_match.group(0) if name_match else None

        # Compose signals array — order matters for headline preference
        # (ACECQA listed first as the primary/official signal). Future
        # detection methods append after these two.
        kinder_signals = [
            {
                "key":      "acecqa",
                "label":    "ACECQA flag",
                "positive": bool(kinder_acecqa),  # None coerces to False
                "source":   r.get("kinder_source") or "ACECQA national register",
                "tag":      TAG_OBS,
            },
            {
                "key":      "name_match",
                "label":    "Name match",
                "positive": kinder_name_match_value,
                "source":   "Regex on services.service_name",
                "tag":      TAG_DER,
                "matched_text": kinder_name_match_text,
            },
        ]
        any_positive = any(s["positive"] for s in kinder_signals)
        positive_keys = [s["key"] for s in kinder_signals if s["positive"]]

        # Four-state headline mapping per D1.
        if "acecqa" in positive_keys and "name_match" in positive_keys:
            kinder_headline = "Kinder: confirmed (ACECQA + name match)"
            kinder_state = "confirmed_both"
        elif "acecqa" in positive_keys:
            kinder_headline = "Kinder: confirmed (ACECQA)"
            kinder_state = "confirmed_acecqa"
        elif "name_match" in positive_keys:
            kinder_headline = "Kinder: likely (name match only — not in ACECQA)"
            kinder_state = "likely_name_only"
        else:
            kinder_headline = "Not flagged"
            kinder_state = "not_flagged"

        places = {
            "approved_places": {
                "tag": TAG_OBS,
                "value": r.get("approved_places"),
            },
            "service_sub_type": subtype,
            "long_day_care_flag": bool(r.get("long_day_care")) if r.get("long_day_care") is not None else None,
            "kinder_approved": {
                "tag": TAG_OBS,
                "value": kinder_acecqa,
                "source": r.get("kinder_source"),
            },
            "kinder_name_match": {
                "tag": TAG_DER,
                "value": kinder_name_match_value,
                "matched_text": kinder_name_match_text,
                "rule": r"regex \b(kinder(garten)?|pre-?school)\b on services.service_name (case-insensitive, word-boundary)",
                "pattern": KINDER_PAT.pattern,
                "caveat": "Name evidence, not an official kinder approval record.",
            },
            "kinder_summary": {
                "tag": TAG_DER,
                "state": kinder_state,
                "headline": kinder_headline,
                "any_signal": any_positive,
                "signals": kinder_signals,
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

        # --- WORKFORCE SUPPLY CONTEXT (DEC-76, sub-pass 4.3.9) ---
        workforce_supply = _build_workforce_supply(conn, r.get("state"))

        # --- ASSEMBLE ---
        payload = {
            "schema_version": "centre_payload_v6",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "header": header,
            "nqs": nqs,
            "places": places,
            "catchment": catchment,
            "position": position,
            "workforce_supply": workforce_supply,
            "qa_scores": qa_scores,
            "tenure": tenure,
            "commentary": _commentary_lines(header, nqs, places, tenure, subtype),
        }
        return payload
    finally:
        conn.close()


# ─────────────────────────────────────────────────────────────────────
# Layer 4.3 sub-pass 4.3.9 — Workforce supply context block (DEC-76)
# ─────────────────────────────────────────────────────────────────────
# Returns the workforce_supply payload section: 4 rows rendered in the
# new default-open block on the centre page. State-level rows depend on
# JSA IVI Step 5c data (ANZSCO 4211 + 2411). National rows are static
# facts (ECEC Award rates, Three-Day Guarantee policy).
#
# DEFENSIVE: the JSA IVI table name is not known to this code at write
# time. The query attempts a likely table name and tolerates absence
# (sqlite3.OperationalError) or empty results — in either case the row
# renders as deferred. The probe artefact for this bundle includes a
# step for the operator to confirm the IVI table name; once confirmed,
# the literal in _IVI_TABLE_CANDIDATES below is the only line to change
# (or the candidate ordering becomes the lookup chain).
#
# Intent copy for these rows comes from LAYER3_METRIC_INTENT_COPY
# (4 entries seeded in v6 sub-pass 4.3.8 — see jsa_ivi_4211_child_carer,
# jsa_ivi_2411_ect, ecec_award_rates, three_day_guarantee).

# Likely table names for JSA IVI state-monthly data. The query tries
# each in order; first one that exists and returns rows wins. None
# matching = row renders as deferred with a "data not yet wired" note.
_IVI_TABLE_CANDIDATES = (
    "jsa_ivi_state_monthly",
    "abs_jsa_ivi_state_monthly",
    "jsa_internet_vacancy_index_state_monthly",
    "jsa_ivi_anzsco_state_monthly",
)

# State name → standard 2/3-letter abbrev for the JSA IVI 'state'
# column, which typically uses short codes. Lookup is case-insensitive
# at use time.
_STATE_TO_CODE = {
    "new south wales": "NSW",
    "victoria": "VIC",
    "queensland": "QLD",
    "south australia": "SA",
    "western australia": "WA",
    "tasmania": "TAS",
    "northern territory": "NT",
    "australian capital territory": "ACT",
}


def _try_query_ivi(conn, anzsco_code: str, state_value: Optional[str]):
    """Try each candidate IVI table for a state-monthly series.

    Returns dict with {trajectory: [...], latest: {...}, table_used: str}
    or None if no candidate yielded data.
    """
    if not state_value:
        return None
    state_short = _STATE_TO_CODE.get(str(state_value).strip().lower(), str(state_value).strip())

    for table in _IVI_TABLE_CANDIDATES:
        try:
            # We don't know exact column names — try a flexible probe.
            # Common shape would be (state, anzsco_code, period_year, period_month, vacancy_index)
            # or a single 'period' (YYYY-MM) column.
            cur = conn.execute(
                f"SELECT name FROM sqlite_master WHERE type='table' AND name=? LIMIT 1",
                (table,),
            )
            if not cur.fetchone():
                continue

            # Inspect columns to figure out the period field
            cols = {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
            period_col = None
            for cand in ("period", "period_label", "year_month", "yyyymm"):
                if cand in cols:
                    period_col = cand
                    break
            value_col = None
            for cand in ("vacancy_index", "ivi", "value", "index_value", "vacancy_count"):
                if cand in cols:
                    value_col = cand
                    break
            if not period_col or not value_col:
                # Table exists but column shape doesn't match expectations —
                # surface that in the probe rather than guess.
                continue

            anzsco_col = "anzsco_code" if "anzsco_code" in cols else (
                "anzsco" if "anzsco" in cols else None
            )
            state_col = "state" if "state" in cols else (
                "state_code" if "state_code" in cols else None
            )
            if not anzsco_col or not state_col:
                continue

            rows = conn.execute(
                f"SELECT {period_col}, {value_col} FROM {table} "
                f"WHERE {state_col}=? AND {anzsco_col}=? "
                f"ORDER BY {period_col} ASC",
                (state_short, anzsco_code),
            ).fetchall()
            if not rows:
                continue

            traj = [{"period": r[0], "value": r[1]} for r in rows if r[1] is not None]
            if not traj:
                continue
            return {
                "trajectory": traj,
                "latest": traj[-1],
                "table_used": table,
            }
        except sqlite3.OperationalError:
            # Table doesn't exist or column shape is unexpected — try next.
            continue
        except Exception:
            # Anything else, fall through and try next candidate.
            continue
    return None


def _ivi_row(conn, metric_key: str, anzsco_code: str, display_label: str, state_value: Optional[str]) -> dict:
    """Build a single workforce_supply row for a JSA IVI ANZSCO code."""
    intent_copy = LAYER3_METRIC_INTENT_COPY.get(metric_key)
    base = {
        "metric": metric_key,
        "display": display_label,
        "scope": "state",
        "anzsco_code": anzsco_code,
        "intent_copy": intent_copy,
        "row_weight": "context",
        # Compact label for the OBS pill tooltip.
        "source": "Jobs and Skills Australia IVI",
        # Full methodology rendered as a permanent
        # visible block below the chart (centre.html
        # v3.17 _renderWorkforceSupplyRow). v12 split:
        # OBS pill carries just the source name; the
        # about_data field is the new explainer home.
        "about_data": (
            "Jobs and Skills Australia's Internet Vacancy "
            "Index (IVI) — monthly count of online job "
            "advertisements for this ANZSCO occupation, "
            "compiled from postings on SEEK, CareerOne "
            "and Australian JobSearch at month-end. "
            "State-level series; no SA2 disaggregation."
        ),
        "scope_stamp": f"state-level ({state_value or 'unknown'}) — no SA2 peer cohort",
    }
    data = _try_query_ivi(conn, anzsco_code, state_value)
    if data is None:
        base["confidence"] = "deferred"
        base["status_note"] = (
            "JSA IVI ingest table name not confirmed in this build — "
            "wire-up follow-up required. See bundle probe artefact."
        )
        return base
    base["confidence"] = "live"
    base["latest"] = data["latest"]
    base["trajectory"] = data["trajectory"]
    base["_table_used"] = data["table_used"]
    return base


def _build_workforce_supply(conn, state_value: Optional[str]) -> dict:
    """Assemble the workforce_supply block. 4 rows per DEC-76."""
    rows = [
        _ivi_row(
            conn,
            metric_key="jsa_ivi_4211_child_carer",
            anzsco_code="4211",
            display_label="Child carer vacancy index (ANZSCO 4211)",
            state_value=state_value,
        ),
        _ivi_row(
            conn,
            metric_key="jsa_ivi_2411_ect",
            anzsco_code="2411",
            display_label="Early childhood teacher vacancy index (ANZSCO 2411)",
            state_value=state_value,
        ),
        # ECEC Award minimum rates — national, static. The numeric
        # values come from the Fair Work Modern Award; exact rates can
        # be wired in once a Fair Work source table is ingested.
        # Until then, render the row with a "see Fair Work" pointer.
        {
            "metric":      "ecec_award_rates",
            "display":     "ECEC Award minimum rates (CIII / Diploma / ECT)",
            "scope":       "national",
            "intent_copy": LAYER3_METRIC_INTENT_COPY.get("ecec_award_rates"),
            "row_weight":  "context",
            "source":      "Fair Work Modern Award (annual minimum rates)",
            "scope_stamp": "national — no SA2 peer cohort",
            "confidence":  "deferred",
            "status_note": "Awaits Fair Work rates ingest. Rates change annually on 1 July.",
        },
        # Three-Day Guarantee — national policy fact, effective Jan 2026.
        {
            "metric":      "three_day_guarantee",
            "display":     "Three-Day Guarantee policy",
            "scope":       "national",
            "intent_copy": LAYER3_METRIC_INTENT_COPY.get("three_day_guarantee"),
            "row_weight":  "context",
            "source":      "Australian Government policy (effective Jan 2026)",
            "scope_stamp": "national — no SA2 peer cohort",
            "confidence":  "live",
            "fact":        "Effective Jan 2026: every child entitled to three subsidised days, irrespective of activity test.",
        },
    ]
    return {
        "tag": TAG_DER,
        "default_open": True,
        "rows": rows,
    }


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
