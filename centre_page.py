"""
centre_page.py — Phase 2 backend helper for centre.html
Version: v24 (2026-05-12) — DEC-84 Centre v2 payload schema v7. Additive overlay (DEC-11): v6 keys preserved unchanged; v7 adds 4 top-level keys (`dec83`, `executive`, `matrix`, `drawer`) populated by 3 new builders + 1 substrate fetcher. New functions: `_build_dec83_state(conn, service_id)` reads DEC-83 substrate (large_provider, regulatory_snapshot, conditions, enforcement, vacancy, fees, capture_meta) defensively per-table; `_build_executive(r, position, dec83_state)` produces Layer 2 (5 signal tiles + max-2 flags + composed headline per DEC-84 #2 + #3); `_build_matrix(r, position, workforce_supply, community_profile, dec83_state)` produces Layer 5 row list (~52 rows V1, 9 categories per DEC-84 #5) using `_matrix_rows_from_position` flattener + per-category builders for new DEC-83-only categories (Pricing / Quality / Operator / Operations); `_build_drawer(...)` produces Layer 6 special drawer content keyed by drawer key (DEC-83-specific only; position-derived drawers derived by renderer from existing position entries). Legacy v6 renderer at `/centres/{id}` (centre.html v3.31) continues to work unchanged. New /centre_v2/{id} renderer (centre_v2.html, future) consumes v7 keys. Imports `timedelta` for 24mo enforcement-event window.

Version: v21 (2026-05-05) — OI-36 close: sa2_nes_share added to POSITION_CARD_ORDER["catchment_position"] for Python-side consistency with centre.html's render order. Data-side registration was already complete at v20 (LAYER3_METRIC_META + INTENT_COPY + TRAJECTORY_SOURCE in commit 3ddcf18); the metric was being emitted by _layer3_position but not rendered because centre.html L2349 hardcoded its own order array excluding NES. Surgical scope. Refactor to drive JS render order from the POSITION_CARD_ORDER payload (eliminating the JS-side array entirely) banked as separate housekeeping OI. Companion centre.html v3.26 in same commit.

Version: v20 (2026-05-03) — OI-32 polish round 3 (operator review of v19 INDUSTRY label semantics + about_data first-line overreach). Two changes on sa2_demand_supply: (a) INDUSTRY_BAND_THRESHOLDS parallel-framed across all 4 bands in supply-vs-demand language only — "below break-even" / "near break-even" replaced with "supply heavy" / "supply leaning" / "approaching balance" / "demand leading" because break-even is a profitability conclusion that the demand/supply ratio alone cannot support (depends on price, cost base, ramp curve, mix). The thresholds (0.40 / 0.55 / 0.85) still derive from break-even/target occupancy maths but the LABEL no longer asserts the conclusion. (b) about_data first line tightened from "the occupancy ramp-up expectation for a centre here" to "a key input to occupancy ramp expectations" — same category-error fix at the descriptive level. Companion centre.html v3.23 -> v3.24 (cohort histogram explainer + SEIFA mini decile strip).

v19 (2026-05-03) — OI-32 polish round 2 (operator screenshot review of v18 missed surfaces). Round-1 cleaned about_data + INDUSTRY_BAND_THRESHOLDS notes; this round cleans the remaining visible "fill" / "soft" terminology in (a) LAYER3_METRIC_META.sa2_demand_supply.band_copy chips ("soft catchment — fill risk" / "demand pull — strong fill expected"), (b) LAYER3_METRIC_INTENT_COPY sa2-prefixed entries for sa2_demand_supply, sa2_supply_ratio, and sa2_adjusted_demand, and (c) INDUSTRY_BAND_THRESHOLDS sa2_demand_supply soft-band LABEL ("soft ramp-up" -> "below break-even"). Band KEY stays "soft" because centre.html cautionKeys references it for the cautionary pill colour. Renderer-side: no change. Unprefixed duplicate INTENT_COPY entries left alone — kept for backward reference per existing comment, not read by _layer3_position.

v18 (2026-05-03) — OI-32 polish round (operator review of v17). Two text edits on sa2_demand_supply: (a) LAYER3_METRIC_ABOUT_DATA copy reframed from "fill expectation / fill risk" to industry-standard "occupancy ramp-up / trade-up risk" terminology — credit readers use these terms, "fill" reads as colloquial; (b) INDUSTRY_BAND_THRESHOLDS rewritten to remove the generic "below 70% break-even at typical 85% occupancy" note (operator: too generic; said nothing band-specific) and replace "fill" in band labels/notes with occupancy-ramp / trade-up language across all 4 bands. No structural change; banding logic + thresholds + STD-34 calibration trace unchanged. Renderer half ships as centre.html v3.22 -> v3.23 in same commit (font bump on the about_data panel only).

v17 (2026-05-03) — OI-32 close (Bug 4): catchment metric explainer text. New module-level constant LAYER3_METRIC_ABOUT_DATA carries longer plain-language "what is this metric?" copy for the 4 catchment_position Full-weight metrics (sa2_supply_ratio, sa2_child_to_place, sa2_demand_supply, sa2_adjusted_demand). Each entry is a plain string with \n\n paragraph breaks. _layer3_position propagates p.about_data onto every entry it emits (stub + populated) via LAYER3_METRIC_ABOUT_DATA.get(metric_name) — same shape as intent_copy propagation. Missing key = silent absence per P-2; non-catchment metrics see no change. Renderer half ships as centre.html v3.21 -> v3.22 in the same commit (verified together; DEC-22 collapse precedent).

v16 (2026-05-03) — Layer 4.2-A.3c Bug 2 fix (DEC-74 amendment): perspective toggle fields (reversible, pair_with, default_perspective, perspective_labels) removed from the 3 catchment metrics that had them (sa2_supply_ratio, sa2_child_to_place, sa2_demand_supply). With these metrics now Full row_weight (v15), the inverse views are shown as separate rows in the same card — toggling would just swap to data already visible (supply_ratio / child_to_place are mathematical inverses, displayed side by side). For demand_supply, the natural 'fill' framing is the credit reader's preferred view; inverse 'spare capacity' framing adds little value. Renderer (centre.html line 1749) gates toggle render on p.reversible — with reversible: True removed from META, _layer3_position propagates reversible: False (default), and the toggle silently doesn't render. No renderer change needed for this fix; companion v3.20 ships separately for Bug 1 (year regex).

v15 changes (2026-05-03, Layer 4.2-A.3c Part 3a): catchment metrics promoted from Lite to Full row_weight (sa2_supply_ratio, sa2_child_to_place, sa2_adjusted_demand, sa2_demand_supply). Each now ships a quarterly trajectory derived from docs/sa2_history.json (v2 multi-subtype build) plus a per-subtype centre_events array for the renderer overlay. New module-level cache _SA2_HISTORY_CACHE + _load_sa2_history() (~13 MB held once per process). New helper _catchment_trajectory(sa2_code, metric_name, subtype, calibrated_rate) returns (points, kind, events) — same shape as _metric_trajectory plus events. _layer3_position signature gains optional service_sub_type parameter; dispatches to _catchment_trajectory for any metric in CATCHMENT_TRAJECTORY_METRICS frozenset. Single call site in get_centre_payload updated to pass r.get('service_sub_type'). Subtype fallback to LDC for null/Other centres. Calibrated_rate held constant across historical quarters for adjusted_demand / demand_supply (honest as 'supply trajectory adjusted for current demand structure' — renderer surfaces in helper text). Renderer half ships separately as centre.html v3.18 -> v3.19 per DEC-22.

v14 changes (2026-05-03, OI-29 close): sa2_median_household_income reclassified to Lite weight per DEC-75. Three Census points (2011/2016/2021) is not a trajectory; same logic the LFP triplet got in DEC-75. Renderer-only behavioural change at runtime: _renderLiteRow drops the trajectory chart, keeps decile strip + band chips + intent copy + as-at stamp (reads "2021" from the most recent non-null point). sa2_median_employee_income and sa2_median_total_income stay Full (annual cadence, 5 dense points 2018-2022).

v14 changes (2026-05-03, OI-29 close): sa2_median_household_income reclassified to Lite weight per DEC-75. Three Census points (2011/2016/2021) is not a trajectory; same logic the LFP triplet got in DEC-75. Renderer-only behavioural change at runtime: _renderLiteRow drops the trajectory chart, keeps decile strip + band chips + intent copy + as-at stamp (reads "2021" from the most recent non-null point). sa2_median_employee_income and sa2_median_total_income stay Full (annual cadence, 5 dense points 2018-2022).

v13 changes (2026-05-03, Layer 4.2-A.4): STD-34 calibration metadata surfaced on the 3 catchment_position metrics that derive from the participation_rate calibration (sa2_adjusted_demand, sa2_demand_supply, sa2_demand_share_state). New _read_calibration_meta helper reads calibrated_rate + rule_text from service_catchment_cache once per SA2; attached per-entry where meta.uses_calibration=True. Renderer half ships separately (centre.html v3.17 -> v3.18) per DEC-22 two-commit pattern. Other catchment metrics (sa2_supply_ratio, sa2_child_to_place) are pure ratios and correctly do NOT receive this metadata.

v12 changes (2026-04-30, Layer 4.2-A.3a-fix iter 4 (F1-β)): JSA IVI methodology lifted out of hover-gated OBS tooltip into a new about_data field on IVI rows. Renderer surfaces it as a permanent visible block under the chart so credit readers don't need to discover the OBS hover affordance. OBS source string now carries full methodology one-liner (what the IVI is, where it comes from); intent_copy tightened to credit-relevant framing only. Reader hovers OBS for data provenance, reads inline copy for credit signal.

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

import json
import re
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

DB_PATH = str(Path(__file__).resolve().parent / "data" / "kintell.db")

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
        # v20: parallel-framed labels in supply-vs-demand language only.
        # The thresholds still derive from break-even/target occupancy
        # maths but the LABEL no longer asserts a profitability
        # conclusion the ratio alone cannot support (operator review:
        # break-even depends on price/cost/ramp/mix, not on the ratio).
        # Band keys unchanged — centre.html cautionKeys references
        # them for the cautionary pill colour. Notes parallel the
        # labels in factual supply-vs-demand language.
        (0.40, "soft",     "supply heavy",
         "demand well short of available capacity"),
        (0.55, "near_be",  "supply leaning",
         "demand below available capacity"),
        (0.85, "viable",   "approaching balance",
         "demand and supply broadly aligned"),
        (float("inf"), "strong", "demand leading",
         "demand exceeds available capacity"),
    ],
}

# Layer 4.2-A.3c: catchment metrics whose trajectory is read from
# docs/sa2_history.json (per-subtype) rather than from a SQL table via
# _metric_trajectory. Membership in this set causes _layer3_position
# to dispatch to _catchment_trajectory instead.
CATCHMENT_TRAJECTORY_METRICS = frozenset({
    "sa2_supply_ratio",
    "sa2_child_to_place",
    "sa2_adjusted_demand",
    "sa2_demand_supply",
})


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
        "row_weight": "lite",  # v14 (OI-29): 3 Census points is not a trajectory; per DEC-75
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
        "row_weight": "full",  # v15 (Layer 4.2-A.3c): trajectory from sa2_history.json + centre_events overlay
        "industry_thresholds": True,  # v10
        "source": "ACECQA approved places ÷ ABS ERP under-5 population",
        # v16 (Layer 4.2-A.3c amendment to DEC-74): perspective toggle removed.
        # Inverse view (children per place) is shown as a separate row in
        # the same card; toggling here would just swap to data already visible.
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
        "row_weight": "full",  # v15 (Layer 4.2-A.3c): trajectory from sa2_history.json (1/supply_ratio per quarter)
        "industry_thresholds": True,  # v10
        "source": "ABS ERP under-5 population ÷ ACECQA approved places",
        # v16 (Layer 4.2-A.3c amendment to DEC-74): perspective toggle removed.
        # Inverse view (supply ratio) is shown as a separate row in the
        # same card; toggling here would just swap to data already visible.
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
        "row_weight": "full",  # v15 (Layer 4.2-A.3c): trajectory = pop_0_4 × current_calibrated_rate × 0.6 per quarter
        "source": "ABS ERP under-5 × calibrated participation rate × 0.6 attendance factor",
        "uses_calibration": True,  # v13 — opts in to STD-34 metadata
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
        "row_weight": "full",  # v15 (Layer 4.2-A.3c): trajectory = adjusted_demand_per_quarter / places_per_quarter
        "industry_thresholds": True,  # v10
        "source": "Adjusted demand estimate ÷ ACECQA approved places",
        "uses_calibration": True,  # v13 — derives transitively via adjusted_demand
        # v16 (Layer 4.2-A.3c amendment to DEC-74): perspective toggle removed.
        # The natural "fill" framing (high = strong demand vs supply) is
        # what credit readers actually use; the inverse "spare capacity"
        # framing adds little value for the credit-decision use case.
        "band_copy": {
            "low":  "supply outweighs demand — trade-up risk",
            "mid":  "in balance",
            "high": "demand outweighs supply — fast occupancy ramp",
        },
    },
    "sa2_demand_share_state": {
        "display": "Share of state demand",
        "card": "catchment_position",
        "value_format": "percent_share",
        "direction": "high_is_positive",
        "row_weight": "context",  # rank-by-construction; no banding
        "source": "This SA2's adjusted demand ÷ state-wide adjusted demand",
        "uses_calibration": True,  # v13 — derives transitively via adjusted_demand
        "band_copy": {
            "low": "—", "mid": "—", "high": "—",
        },
    },
    "sa2_nes_share": {
        "display": "Non-English-speaking share",
        "card": "catchment_position",
        "value_format": "percent",
        "direction": "high_is_positive",  # neutral framing; credit signal lives in calibration nudge
        "row_weight": "lite",  # 3 Census points (2011/2016/2021) per DEC-75
        "source": "ABS Census 2021 T10A+T10B (census_nes_share_pct)",
        "band_copy": {
            "low":  "predominantly English-speaking",
            "mid":  "moderate language diversity",
            "high": "high cultural-linguistic diversity",
        },
    },
    # Layer 4.4 A10 — Demographic Mix bundle (3 Lite rows). Neutral framing
    # consistent with NES precedent; calibration deferred per design D-A1.
    "sa2_atsi_share": {
        "display": "Aboriginal and Torres Strait Islander share",
        "card": "catchment_position",
        "value_format": "percent",
        "direction": "high_is_positive",  # neutral framing
        "row_weight": "lite",
        "source": "ABS Census 2021 T06 (census_atsi_share_pct)",
        "band_copy": {
            "low":  "low Aboriginal and Torres Strait Islander population share",
            "mid":  "moderate Aboriginal and Torres Strait Islander population share",
            "high": "high Aboriginal and Torres Strait Islander population share",
        },
    },
    "sa2_overseas_born_share": {
        "display": "Overseas-born share",
        "card": "catchment_position",
        "value_format": "percent",
        "direction": "high_is_positive",  # neutral framing
        "row_weight": "lite",
        "source": "ABS Census 2021 T08 (census_overseas_born_share_pct)",
        "band_copy": {
            "low":  "predominantly Australian-born",
            "mid":  "moderate share born overseas",
            "high": "high share born overseas",
        },
    },
    "sa2_single_parent_family_share": {
        "display": "Single-parent family share",
        "card": "catchment_position",
        "value_format": "percent",
        "direction": "high_is_positive",  # neutral framing
        "row_weight": "lite",
        "source": "ABS Census 2021 T14 (census_single_parent_family_share_pct)",
        "band_copy": {
            "low":  "low one-parent-family share among family households",
            "mid":  "moderate one-parent-family share among family households",
            "high": "high one-parent-family share among family households",
        },
    },
    # Layer 4.4 A3 + Stream C — Parent-cohort + marital + fertility bundle
    # (4 Lite rows). Neutral framing per A10 precedent; calibration deferred.
    "sa2_parent_cohort_25_44_share": {
        "display": "Parent-cohort (25-44) share",
        "card": "catchment_position",
        "value_format": "percent",
        "direction": "high_is_positive",  # neutral framing
        "row_weight": "lite",
        "source": "ABS ERP (erp_parent_cohort_25_44_share_pct)",
        "band_copy": {
            "low":  "low share of 25-44 year-olds in resident population",
            "mid":  "moderate share of 25-44 year-olds in resident population",
            "high": "high share of 25-44 year-olds in resident population",
        },
    },
    "sa2_partnered_25_44_share": {
        "display": "Partnered (25-44) share",
        "card": "catchment_position",
        "value_format": "percent",
        "direction": "high_is_positive",  # neutral framing
        "row_weight": "lite",
        "source": "ABS Census 2021 T05 (census_partnered_25_44_share_pct)",
        "band_copy": {
            "low":  "low share of 25-44s in registered or de-facto partnerships",
            "mid":  "moderate share of 25-44s in registered or de-facto partnerships",
            "high": "high share of 25-44s in registered or de-facto partnerships",
        },
    },
    "sa2_women_35_44_with_child_share": {
        "display": "Share of women aged 35 to 44 with at least one child",
        "card": "catchment_position",
        "value_format": "percent",
        "direction": "high_is_positive",  # neutral framing
        "row_weight": "lite",
        "source": "ABS Census 2021 T07 (census_women_35_44_with_child_share_pct)",
        "band_copy": {
            "low":  "low share of women 35-44 with at least one child",
            "mid":  "moderate share of women 35-44 with at least one child",
            "high": "high share of women 35-44 with at least one child",
        },
    },
    "sa2_women_25_34_with_child_share": {
        "display": "Share of women aged 25 to 34 with at least one child",
        "card": "catchment_position",
        "value_format": "percent",
        "direction": "high_is_positive",  # neutral framing
        "row_weight": "lite",
        "source": "ABS Census 2021 T07 (census_women_25_34_with_child_share_pct)",
        "band_copy": {
            "low":  "low share of women 25-34 with at least one child",
            "mid":  "moderate share of women 25-34 with at least one child",
            "high": "high share of women 25-34 with at least one child",
        },
    },
    # Layer 4.4 A4 — Schools at SA2 (DEC-82 first direct-primary-source ingest).
    # 3 metrics rendered in V1 via the new "Education infrastructure" card.
    # The other 5 banded ACARA metrics (sector breakdowns by school count and
    # by enrolment) sit in the DB ready for V2 / Excel export / group page.
    "sa2_school_count_total": {
        "display": "Schools in catchment",
        "card": "education_infrastructure",
        "value_format": "int",
        "direction": "high_is_positive",
        "row_weight": "lite",
        "source": "ACARA School Profile 2008-2025 + School Location 2025 (acara_school_count_total)",
        "band_copy": {
            "low":  "few schools in this catchment",
            "mid":  "moderate school presence",
            "high": "high school presence",
        },
    },
    "sa2_school_enrolment_total": {
        "display": "Total student enrolment",
        "card": "education_infrastructure",
        "value_format": "int",
        "direction": "high_is_positive",
        "row_weight": "lite",
        "source": "ACARA School Profile 2008-2025 (acara_school_enrolment_total)",
        "band_copy": {
            "low":  "low total student enrolment",
            "mid":  "moderate total student enrolment",
            "high": "high total student enrolment",
        },
    },
    "sa2_school_enrolment_govt_share": {
        "display": "Government-school enrolment share",
        "card": "education_infrastructure",
        "value_format": "percent",
        "direction": "high_is_positive",  # neutral framing — public/private mix
        "row_weight": "lite",
        "source": "ACARA School Profile 2008-2025 (acara_school_enrolment_govt_share_pct)",
        "band_copy": {
            "low":  "low government-school share (private-dominant catchment)",
            "mid":  "balanced public/private mix",
            "high": "high government-school share",
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
        # ── Demographic mix sub-panel (renderer inserts a divider above
        # sa2_nes_share; payload-assembly side just lists rows in order).
        "sa2_nes_share",
        "sa2_atsi_share",
        "sa2_overseas_born_share",
        "sa2_single_parent_family_share",
        # Layer 4.4 A3 + Stream C — appended 2026-05-10
        "sa2_parent_cohort_25_44_share",
        "sa2_partnered_25_44_share",
        "sa2_women_35_44_with_child_share",
        "sa2_women_25_34_with_child_share",
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
    # Layer 4.4 A4 — Education infrastructure card (DEC-82 first direct-primary-source ingest).
    # New top-level Position card themed around school context. Future home for
    # preschool series + tertiary/VET. 3 V1 rows; 5 sector breakdowns banked
    # in DB but not rendered in V1.
    "education_infrastructure": [
        "sa2_school_count_total",
        "sa2_school_enrolment_total",
        "sa2_school_enrolment_govt_share",
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
        "occupancy build, low values flag undersupplied catchments "
        "with opportunity.",
    "sa2_child_to_place":
        "Children per place inverts supply ratio — frames the same "
        "data as demand-headroom; high values flag strong demand per "
        "place, low values flag thin demand per place.",
    "sa2_adjusted_demand":
        "Adjusted demand is the calibrated demand estimate after "
        "participation rate and attendance factor — the realistic "
        "demand the catchment can actually absorb.",
    "sa2_demand_supply":
        "Demand-supply ratio (adjusted demand / places) frames the "
        "occupancy ramp-up expectation — high values flag demand "
        "pull and fast ramp, low values flag supply-heavy catchments "
        "and extended trade-up risk.",
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
    "sa2_nes_share":
        "Share of residents speaking a language other than English at home — "
        "a proxy for cultural-linguistic diversity. Historically, ECEC "
        "engagement is lower in high-NES catchments due to language barriers "
        "and cultural preferences for family-based care.",
    "sa2_atsi_share":
        "Aboriginal and Torres Strait Islander population share — sourced "
        "directly from ABS Census Indigenous status. Higher shares indicate "
        "communities where culturally responsive ECEC programs and family-led "
        "care models are more material to engagement.",
    "sa2_overseas_born_share":
        "Share of residents born overseas — a proxy for immigrant-density "
        "distinct from the language signal in NES. Recent-arrival communities "
        "often display lower formal-ECEC participation in early years; "
        "established migrant communities trend the opposite way.",
    "sa2_single_parent_family_share":
        "Share of family households that are single-parent — a structural "
        "signal of CCS-eligible utilisation pressure, full-time-care intensity, "
        "and reduced flexibility for family-based alternatives.",
    "sa2_parent_cohort_25_44_share":
        "Share of residents aged 25-44 — the population window where active "
        "parenting of 0-5 year olds is concentrated. A higher share signals a "
        "deeper natural demand pool for ECEC services in this catchment.",
    "sa2_partnered_25_44_share":
        "Share of 25-44 year-olds in a registered or de-facto partnership — "
        "a community-structure context signal alongside the parent cohort. "
        "Catchments with lower partnered shares often correlate with "
        "later-fertility profiles and shifted ECEC demand timing.",
    "sa2_women_35_44_with_child_share":
        "Share of women aged 35-44 who have had at least one child — a "
        "completed-fertility proxy. By this age the cohort's lifetime "
        "fertility profile is largely settled; useful as a community-level "
        "indicator of fertility intensity rather than active timing.",
    "sa2_women_25_34_with_child_share":
        "Share of women aged 25-34 who have had at least one child — the "
        "more directly childcare-relevant fertility cut. Tracks active "
        "parenting timing for the cohort most likely to have children "
        "currently in the 0-5 ECEC window.",
    "sa2_school_count_total":
        "Number of currently-operating schools located in this SA2. Includes "
        "Government, Catholic, and Independent across primary, secondary, "
        "and combined sectors. A higher count signals broader school "
        "infrastructure and — particularly relevant for OSHC investment — "
        "more candidate sites for school-attached after-school programs.",
    "sa2_school_enrolment_total":
        "Total student enrolment summed across all schools located in this "
        "catchment. Indicates the active school-aged population served by "
        "schools located here. Note: students cross SA2 borders to attend "
        "school, so this measures 'enrolment AT schools in this SA2', not "
        "'school-aged kids living in this SA2'.",
    "sa2_school_enrolment_govt_share":
        "Share of student enrolment in government schools within this "
        "catchment. Captures the public-private school mix in a single "
        "number — low values signal Catholic / Independent school dominance "
        "and typically correlate with higher catchment SES, while high "
        "values indicate predominantly public-school communities.",
}


# ─────────────────────────────────────────────────────────────────────
# v17 (OI-32) — Layer 3 metric "About this measure" copy
# ─────────────────────────────────────────────────────────────────────
# Longer plain-language explainer per metric. Renderer surfaces this
# as a permanent visible "About this measure" panel below the intent
# copy in _renderFullRow. Currently populated for the 4 Full-weight
# catchment metrics; other metrics get silent absence.
#
# Format conventions:
#   - Plain text only (no HTML); renderer applies htmlEscape
#   - "\n\n" separates paragraphs (renders as a visual gap)
#   - "\n" within a paragraph renders as a tight line break (<br>)
#
# Editorial: keep brief. What it measures, the formula in plain words,
# what high vs low means. Calculations and calibration trace live in
# the DER badge tooltip — do not duplicate here.
LAYER3_METRIC_ABOUT_DATA = {
    "sa2_supply_ratio":
        "Licensed LDC places per child under five in this catchment.\n\n"
        "Formula: total places ÷ children under five.\n\n"
        "High: more places than children — supply-rich, competition tighter.\n"
        "Low: fewer places than children — undersupplied, opportunity to fill demand.",

    "sa2_child_to_place":
        "Children under five per licensed LDC place — the inverse view of supply ratio.\n\n"
        "Formula: children under five ÷ total places.\n\n"
        "High: many children chasing each place — strong demand per place.\n"
        "Low: each place serves few children — thin demand per place.",

    "sa2_demand_supply":
        "How supply compares to realistic demand — a key input to occupancy ramp expectations.\n\n"
        "Formula: adjusted demand ÷ total places.\n\n"
        "High: demand outweighs supply — fast occupancy ramp expected.\n"
        "Low: supply outweighs demand — slow ramp-up, trade-up risk.",

    "sa2_adjusted_demand":
        "The realistic number of children expected to attend formal LDC in this catchment, after adjusting for who actually participates and how often.\n\n"
        "Formula: children under five × participation rate × attendance factor.\n\n"
        "High: deep demand pool — supports more capacity.\n"
        "Low: shallow demand pool — limits absorbable capacity.",
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
    "sa2_nes_share": {
        "table":         "abs_sa2_education_employment_annual",
        "value_col":     "value",
        "period_col":    "year",
        "filter_clause": "metric_name = 'census_nes_share_pct'",
        "kind":          "annual",
    },
    "sa2_atsi_share": {
        "table":         "abs_sa2_education_employment_annual",
        "value_col":     "value",
        "period_col":    "year",
        "filter_clause": "metric_name = 'census_atsi_share_pct'",
        "kind":          "annual",
    },
    "sa2_overseas_born_share": {
        "table":         "abs_sa2_education_employment_annual",
        "value_col":     "value",
        "period_col":    "year",
        "filter_clause": "metric_name = 'census_overseas_born_share_pct'",
        "kind":          "annual",
    },
    "sa2_single_parent_family_share": {
        "table":         "abs_sa2_education_employment_annual",
        "value_col":     "value",
        "period_col":    "year",
        "filter_clause": "metric_name = 'census_single_parent_family_share_pct'",
        "kind":          "annual",
    },
    # Layer 4.4 A3 + Stream C — appended 2026-05-10
    "sa2_parent_cohort_25_44_share": {
        "table":         "abs_sa2_education_employment_annual",
        "value_col":     "value",
        "period_col":    "year",
        "filter_clause": "metric_name = 'erp_parent_cohort_25_44_share_pct'",
        "kind":          "annual",
    },
    "sa2_partnered_25_44_share": {
        "table":         "abs_sa2_education_employment_annual",
        "value_col":     "value",
        "period_col":    "year",
        "filter_clause": "metric_name = 'census_partnered_25_44_share_pct'",
        "kind":          "annual",
    },
    "sa2_women_35_44_with_child_share": {
        "table":         "abs_sa2_education_employment_annual",
        "value_col":     "value",
        "period_col":    "year",
        "filter_clause": "metric_name = 'census_women_35_44_with_child_share_pct'",
        "kind":          "annual",
    },
    "sa2_women_25_34_with_child_share": {
        "table":         "abs_sa2_education_employment_annual",
        "value_col":     "value",
        "period_col":    "year",
        "filter_clause": "metric_name = 'census_women_25_34_with_child_share_pct'",
        "kind":          "annual",
    },
    # Layer 4.4 A4 — Schools at SA2 (DEC-82 direct ACARA ingest).
    # Annual 18-point trajectory 2008-2025 — richest trajectory in the build.
    "sa2_school_count_total": {
        "table":         "abs_sa2_education_employment_annual",
        "value_col":     "value",
        "period_col":    "year",
        "filter_clause": "metric_name = 'acara_school_count_total'",
        "kind":          "annual",
    },
    "sa2_school_enrolment_total": {
        "table":         "abs_sa2_education_employment_annual",
        "value_col":     "value",
        "period_col":    "year",
        "filter_clause": "metric_name = 'acara_school_enrolment_total'",
        "kind":          "annual",
    },
    "sa2_school_enrolment_govt_share": {
        "table":         "abs_sa2_education_employment_annual",
        "value_col":     "value",
        "period_col":    "year",
        "filter_clause": "metric_name = 'acara_school_enrolment_govt_share_pct'",
        "kind":          "annual",
    },
}


# Layer 4.2-A.3c: module-level cache of docs/sa2_history.json.
# ~13 MB held in memory; keyed by sa2_code for O(1) lookup. Loaded
# lazily on first call to _load_sa2_history(); shared across all
# get_centre_payload() invocations within a single Python process.
_SA2_HISTORY_CACHE = None  # type: ignore[assignment]


def _load_sa2_history() -> dict:
    """DER. Load and cache docs/sa2_history.json once per process.

    Returns dict keyed by sa2_code -> SA2 entry from the JSON. Returns
    {} if the file is missing or unreadable (degrades to no-trajectory
    on catchment metrics; other metrics unaffected).
    """
    global _SA2_HISTORY_CACHE
    if _SA2_HISTORY_CACHE is not None:
        return _SA2_HISTORY_CACHE

    path = Path(__file__).parent / "docs" / "sa2_history.json"
    if not path.exists():
        _SA2_HISTORY_CACHE = {}
        return _SA2_HISTORY_CACHE

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        _SA2_HISTORY_CACHE = {}
        return _SA2_HISTORY_CACHE

    _SA2_HISTORY_CACHE = {s["sa2_code"]: s for s in data.get("sa2s", [])}
    return _SA2_HISTORY_CACHE


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


def _catchment_trajectory(sa2_code,
                          metric_name,
                          subtype,
                          calibrated_rate):
    """DER. Build per-quarter trajectory + centre_events for a catchment metric.

    Reads docs/sa2_history.json (cached singleton). Returns the trajectory
    in the standard {period, value} shape (consistent with _metric_trajectory)
    plus the per-subtype centre_events array.

    Subtype handling: looks up by_subtype[<subtype>]; falls back to LDC if
    subtype is None or not in {LDC, OSHC, PSK, FDC}. LDC is the V1 focus —
    OSHC/PSK/FDC trajectories use the same pop_0_4 denominator as a known
    documented simplification (subtype-correct denominators are V1.5+).

    Calibration semantics: adjusted_demand and demand_supply use the
    centre's CURRENT calibrated_rate held constant across all historical
    quarters. This shows supply-side trajectory adjusted for current
    demand structure (income/LFP/NES/ARIA as they are now). Renderer
    helper text surfaces this explicitly.

    Methodology note: trajectory uses SA2-level pop_0_4 / places. The
    point-in-time current value in service_catchment_cache uses
    catchment-polygon-clipped pop. Numbers won't match exactly at the
    most recent quarter — trajectory is for shape/trend, current value
    is for credit decision.

    Returns (points, kind, events):
      - points = list of {period, value} dicts; empty if no data
      - kind   = "quarterly" if SA2 found, else None
      - events = list of centre_events from by_subtype.<subtype>; empty
                 if no events recorded
    """
    if not sa2_code:
        return [], None, []

    history = _load_sa2_history()
    sa2 = history.get(sa2_code)
    if not sa2:
        return [], None, []

    # Subtype lookup with LDC fallback for null/Other.
    subtype_key = (subtype or "").upper()
    if subtype_key not in ("LDC", "OSHC", "PSK", "FDC"):
        subtype_key = "LDC"

    bs = sa2.get("by_subtype", {}).get(subtype_key)
    if not bs:
        return [], "quarterly", []

    quarters = sa2.get("quarters", [])
    if not quarters:
        return [], "quarterly", []

    n = len(quarters)
    sr_arr     = bs.get("supply_ratio", [])
    places_arr = bs.get("places", [])
    pop_arr    = sa2.get("pop_0_4", [])

    def _get(arr, i):
        return arr[i] if i < len(arr) else None

    points = []
    raw_events = bs.get("centre_events", []) or []

    # Name-rename dedup (Patrick 2026-05-12: same centres appearing in
    # both +new and -closed lists). build_sa2_history.py identifies
    # churn via set-difference on service_id keys, but NQAITS rotates
    # service_id keys across quarters even when the physical centre is
    # unchanged. When a name appears in BOTH new_names and removed_names
    # of the same event it's a key-rename, not an open/close — strip it
    # from both lists and adjust the centre counts. Net_centres stays
    # correct (same name on both sides cancels) but places_change is
    # left as-is since per-centre place attribution isn't carried here.
    events: list = []
    for ev in raw_events:
        new_names = list(ev.get("new_names") or [])
        removed_names = list(ev.get("removed_names") or [])
        # Case-fold + collapse whitespace for matching; preserve original
        # casing in the output.
        def _norm(s):
            return " ".join(str(s).split()).casefold()
        new_norm_to_name = {_norm(n): n for n in new_names}
        removed_norm_to_name = {_norm(n): n for n in removed_names}
        overlap = set(new_norm_to_name.keys()) & set(removed_norm_to_name.keys())
        if overlap:
            new_names = [n for n in new_names if _norm(n) not in overlap]
            removed_names = [n for n in removed_names if _norm(n) not in overlap]
        new_n = len(new_names)
        removed_n = len(removed_names)
        if new_n == 0 and removed_n == 0:
            continue  # pure-rename event — no real open/close, drop entirely
        events.append({
            **ev,
            "new_names":       new_names,
            "removed_names":   removed_names,
            "new_centres":     new_n,
            "removed_centres": removed_n,
            "net_centres":     new_n - removed_n,
        })

    if metric_name == "sa2_supply_ratio":
        for i, q in enumerate(quarters):
            v = _get(sr_arr, i)
            if v is not None:
                points.append({"period": q, "value": v})

    elif metric_name == "sa2_child_to_place":
        for i, q in enumerate(quarters):
            v = _get(sr_arr, i)
            if v is not None and v > 0:
                points.append({"period": q, "value": round(1.0 / v, 3)})

    elif metric_name == "sa2_adjusted_demand":
        if calibrated_rate is None:
            return [], "quarterly", events
        # Source convention (per LAYER3_METRIC_META.sa2_adjusted_demand.source):
        # adjusted_demand = u5 × calibrated_rate × 0.6
        for i, q in enumerate(quarters):
            pop = _get(pop_arr, i)
            if pop is not None and pop > 0:
                points.append({
                    "period": q,
                    "value":  int(round(pop * calibrated_rate * 0.6)),
                })

    elif metric_name == "sa2_demand_supply":
        if calibrated_rate is None:
            return [], "quarterly", events
        # demand_supply = adjusted_demand / places
        for i, q in enumerate(quarters):
            pop    = _get(pop_arr, i)
            places = _get(places_arr, i)
            if pop is not None and pop > 0 and places is not None and places > 0:
                adjusted = pop * calibrated_rate * 0.6
                points.append({
                    "period": q,
                    "value":  round(adjusted / places, 3),
                })

    return points, "quarterly", events


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


def _read_calibration_meta(con: sqlite3.Connection,
                            sa2_code: Optional[str]
                            ) -> Optional[dict]:
    """DER. Read calibrated_rate + rule_text from service_catchment_cache
    for any service in this SA2.

    The cache broadcasts SA2-level calibration facts to every active
    service in that SA2 (calibrated_rate and rule_text are SA2 properties,
    not service properties), so any row's values are canonical for the SA2.
    Returns None if the SA2 has no active service in the cache, or if the
    cache row has NULL calibration fields.

    Mirrors _read_demand_share_state pattern. Layer 4.2-A.4 (STD-34
    surfacing).
    """
    if not sa2_code:
        return None
    try:
        row = con.execute(
            "SELECT calibrated_rate, rule_text FROM service_catchment_cache"
            " WHERE sa2_code = ? AND calibrated_rate IS NOT NULL"
            " LIMIT 1",
            (sa2_code,),
        ).fetchone()
    except sqlite3.OperationalError:
        return None
    if not row:
        return None
    return {
        "calibrated_rate": row[0],
        "rule_text":       row[1],
    }

def _layer3_position(con: sqlite3.Connection, sa2_code: Optional[str], service_sub_type: Optional[str] = None) -> dict:
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
        "catchment_position":      {},
        "population":              {},
        "labour_market":           {},
        # Layer 4.4 A4 — new top-level card per DEC-82 (direct ACARA ingest)
        "education_infrastructure": {},
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
            # v17 (OI-32): about_data — longer plain-language explainer.
            # Silent absence per P-2 when key missing.
            "about_data": LAYER3_METRIC_ABOUT_DATA.get(metric_name),
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

    # Layer 4.2-A.4 (v13): calibration metadata for opted-in metrics
    # (uses_calibration=True). Read once per SA2; attached per-entry below.
    calib_meta = _read_calibration_meta(con, sa2_code)

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
                # v13 (Layer 4.2-A.4): attach calibration metadata.
                if meta.get("uses_calibration") and calib_meta:
                    stub["calibrated_rate"] = calib_meta.get("calibrated_rate")
                    stub["rule_text"]       = calib_meta.get("rule_text")
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
            # v17 (OI-32): about_data — longer plain-language explainer.
            "about_data": LAYER3_METRIC_ABOUT_DATA.get(metric_name),
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

        # Layer 4.2-A.4 (v13): calibration metadata propagation.
        # For metrics that derive from the participation_rate calibration
        # (uses_calibration=True), attach calibrated_rate + rule_text from
        # service_catchment_cache so the renderer can surface them in the
        # DER tooltip per STD-34. Other metrics see no change.
        if meta.get("uses_calibration") and calib_meta:
            entry["calibrated_rate"] = calib_meta.get("calibrated_rate")
            entry["rule_text"]       = calib_meta.get("rule_text")

        # Layer 4.2-B: trajectory + cohort distribution.
        # Only populate for normal/low confidence — for insufficient,
        # the strip is suppressed anyway, and rendering a histogram or
        # a single-point trajectory would be misleading.
        # Layer 4.2-A.3c (v15): catchment metrics dispatch to
        # _catchment_trajectory (reads sa2_history.json per subtype) and
        # also receive a centre_events overlay. Other metrics keep the
        # existing _metric_trajectory path (reads SQL).
        if confidence in ("normal", "low"):
            if metric_name in CATCHMENT_TRAJECTORY_METRICS:
                cal_rate = calib_meta.get("calibrated_rate") if calib_meta else None
                traj_points, traj_kind, traj_events = _catchment_trajectory(
                    sa2_code, metric_name, service_sub_type, cal_rate,
                )
                if traj_points:
                    entry["trajectory"] = traj_points
                    entry["trajectory_kind"] = traj_kind
                if traj_events:
                    entry["centre_events"] = traj_events
            else:
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


# ─────────────────────────────────────────────────────────────────────
# DEC-84 — Centre v2 builders (payload schema v7)
# ─────────────────────────────────────────────────────────────────────
# Three top-level builders surface the v2 6-layer architecture into the
# payload alongside the existing v6 keys (which stay live until v2 cut-
# over via /centre_v2/{id} verifies). v7 = v6 + dec83 + executive +
# matrix + drawer. Existing v6 keys unchanged; new keys ADDITIVE per
# DEC-11. Renderer can consume v6 (legacy /centres/{id}) or v7 (new
# /centre_v2/{id}) without payload-shape branching.
#
# DEC-83 substrate fetcher feeds Layer 1 enrichments + Layer 2 flags +
# Layer 5 Pricing/Quality/Operations/Operator categories + Layer 6
# special drawer content. Defensive: every query try/except OperationalError
# so v24 ships safely on DBs missing one or more DEC-83 tables.

# Drawer-key namespacing per DEC-84 #6:
#   "metric:<metric_name>"      -> generic drawer; renderer derives content
#                                  from position.<card>.<metric_name>
#   "dec83:<topic>"             -> special drawer; payload carries full
#                                  content here (daily_rate / conditions /
#                                  enforcement / operator_group / nqs /
#                                  vacancy / top_n_cob / top_n_lang)


def _build_dec83_state(conn, service_id: int) -> dict:
    """DEC-83 substrate for a single service. Returns a dict with keys:
      large_provider, regulatory_snapshot, conditions, enforcement,
      vacancy, fees, capture_meta. Empty/None when data absent.

    Each substrate piece is read defensively (try/except OperationalError)
    so missing tables don't break payload assembly. Caller may also receive
    None values inside a present-key dict when the service has no data on
    that table even though the table exists.
    """
    out: dict = {
        "large_provider":       None,
        "regulatory_snapshot":  None,
        "conditions":           {"service_count": 0, "provider_count": 0, "active_count": 0, "rows": []},
        "enforcement":          {"total_count": 0, "recent_24mo_count": 0, "rows": []},
        "vacancy":              {"by_age_band": [], "latest_observed_at": None, "all_no_vacancies_published": None},
        "fees":                 {"by_age_band_session": [], "latest_as_of_date": None},
        "capture_meta":         None,
    }

    # 1. Large provider chain (services.large_provider_id -> large_provider)
    try:
        lp_row = conn.execute("""
            SELECT lp.large_provider_id, lp.name, lp.slug,
                   lp.first_observed_at, lp.last_observed_at,
                   (SELECT COUNT(*) FROM large_provider_provider_link
                     WHERE large_provider_id = lp.large_provider_id) AS provider_count,
                   (SELECT COUNT(*) FROM services
                     WHERE large_provider_id = lp.large_provider_id
                       AND is_active = 1) AS service_count
              FROM services s
              JOIN large_provider lp ON s.large_provider_id = lp.large_provider_id
             WHERE s.service_id = ?
        """, (service_id,)).fetchone()
        if lp_row is not None:
            d = _row_to_dict(lp_row)
            out["large_provider"] = {
                "large_provider_id": d.get("large_provider_id"),
                "name":              d.get("name"),
                "slug":              d.get("slug"),
                "first_observed_at": d.get("first_observed_at"),
                "last_observed_at":  d.get("last_observed_at"),
                "provider_count":    int(d.get("provider_count") or 0),
                "service_count":     int(d.get("service_count") or 0),
            }
    except sqlite3.OperationalError:
        pass

    # 2. Latest regulatory snapshot
    try:
        snap_row = conn.execute("""
            SELECT *
              FROM service_regulatory_snapshot
             WHERE service_id = ?
             ORDER BY snapshot_date DESC, snapshot_id DESC
             LIMIT 1
        """, (service_id,)).fetchone()
        if snap_row is not None:
            d = _row_to_dict(snap_row)
            # Hours rollup: derive a single-line summary like "Mon–Fri 7:00am–6:00pm"
            # or "Mon–Fri 7:00am–6:00pm; Sat 8:00am–1:00pm" if Saturday differs.
            hours_summary = _hours_summary(d)
            out["regulatory_snapshot"] = {
                "snapshot_date":         d.get("snapshot_date"),
                "ccs_data_received":     _to_bool(d.get("ccs_data_received")),
                "ccs_revoked_by_ea":     _to_bool(d.get("ccs_revoked_by_ea")),
                "is_closed":             _to_bool(d.get("is_closed")),
                "temporarily_closed":    _to_bool(d.get("temporarily_closed")),
                "last_regulatory_visit": d.get("last_regulatory_visit"),
                "enforcement_count":     d.get("enforcement_count"),
                "nqs_prev_overall":      d.get("nqs_starting_blocks_prev_overall"),
                "nqs_prev_issued":       d.get("nqs_starting_blocks_prev_issued"),
                "provider_status":       d.get("provider_status"),
                "provider_approval_date": d.get("provider_approval_date"),
                "provider_ccs_revoked_by_ea": _to_bool(d.get("provider_ccs_revoked_by_ea")),
                "provider_trade_name":   d.get("provider_trade_name"),
                "hours_summary":         hours_summary,
                "hours_by_day": {
                    day: {"open": d.get(f"hours_{day}_open"), "close": d.get(f"hours_{day}_close")}
                    for day in ("monday", "tuesday", "wednesday", "thursday",
                                "friday", "saturday", "sunday")
                },
                "website_url":           d.get("website_url"),
                "phone":                 d.get("phone"),
                "email":                 d.get("email"),
            }
    except sqlite3.OperationalError:
        pass

    # 3. Conditions (service-level + provider-level via provider_approval_number)
    try:
        # Service-level conditions
        svc_cond_rows = conn.execute("""
            SELECT condition_id, condition_text, level, source,
                   first_observed_at, last_observed_at, still_active
              FROM service_condition
             WHERE service_id = ? AND level = 'service'
             ORDER BY first_observed_at DESC
        """, (service_id,)).fetchall()
        # Provider-level conditions: join via services.provider_approval_number
        prv_cond_rows = conn.execute("""
            SELECT sc.condition_id, sc.condition_text, sc.level, sc.source,
                   sc.first_observed_at, sc.last_observed_at, sc.still_active
              FROM service_condition sc
              JOIN services s2 ON s2.service_id = sc.service_id
              JOIN services s1 ON s1.service_id = ?
             WHERE sc.level = 'provider'
               AND s2.provider_approval_number = s1.provider_approval_number
             GROUP BY sc.condition_id, sc.level, sc.source
        """, (service_id,)).fetchall()
        all_rows = [_row_to_dict(r) for r in svc_cond_rows] + [_row_to_dict(r) for r in prv_cond_rows]
        active_count = sum(1 for r in all_rows if r.get("still_active"))
        svc_count = len(svc_cond_rows)
        prv_count = len(prv_cond_rows)
        out["conditions"] = {
            "service_count":  svc_count,
            "provider_count": prv_count,
            "active_count":   active_count,
            "rows":           all_rows,
        }
    except sqlite3.OperationalError:
        pass

    # 4. Enforcement events from regulatory_events (subject_type='service', subject_id=service_id)
    try:
        ev_rows = conn.execute("""
            SELECT event_id, event_type, event_date, detail, severity, regulator, source_url
              FROM regulatory_events
             WHERE subject_type = 'service' AND subject_id = ?
             ORDER BY event_date DESC
        """, (service_id,)).fetchall()
        all_evs = [_row_to_dict(r) for r in ev_rows]
        # Recent-24mo count from event_date string (YYYY-MM-DD or similar)
        cutoff = (datetime.now(timezone.utc) - timedelta(days=730)).date().isoformat()
        recent = sum(1 for e in all_evs if (e.get("event_date") or "") >= cutoff)
        out["enforcement"] = {
            "total_count":        len(all_evs),
            "recent_24mo_count":  recent,
            "rows":               all_evs,
        }
    except (sqlite3.OperationalError, NameError):
        # NameError catches missing timedelta import as a defensive measure
        pass

    # 5. Latest vacancy snapshot per age_band
    try:
        vac_rows = conn.execute("""
            SELECT v.age_band, v.observed_at, v.vacancy_status, v.vacancy_detail_json
              FROM service_vacancy v
              JOIN (
                  SELECT age_band, MAX(observed_at) AS max_obs
                    FROM service_vacancy
                   WHERE service_id = ?
                   GROUP BY age_band
              ) latest
                ON v.age_band = latest.age_band
               AND v.observed_at = latest.max_obs
             WHERE v.service_id = ?
             ORDER BY v.age_band
        """, (service_id, service_id)).fetchall()
        rows = [_row_to_dict(r) for r in vac_rows]
        latest = max((r.get("observed_at") or "" for r in rows), default=None) or None
        # All published "no_vacancies_published"? (Layer 2 informational flag trigger)
        statuses = [r.get("vacancy_status") for r in rows]
        all_none = bool(rows) and all(s == "no_vacancies_published" for s in statuses if s)
        out["vacancy"] = {
            "by_age_band":                   rows,
            "latest_observed_at":            latest,
            "all_no_vacancies_published":    all_none if rows else None,
        }
    except sqlite3.OperationalError:
        pass

    # 6. Fee rows: latest year median per (age_band, session_type) +
    #    annual trajectory for the headline pair (full_day × 36m-preschool
    #    or service-subtype-discriminated equivalent — Layer 3 chart 7).
    try:
        # Find latest as_of_date year for this service
        latest_year_row = conn.execute("""
            SELECT MAX(as_of_date) AS max_dt
              FROM service_fee
             WHERE service_id = ?
        """, (service_id,)).fetchone()
        latest_dt = latest_year_row[0] if latest_year_row else None
        if latest_dt:
            latest_year = (latest_dt or "")[:4]
            # Patrick 2026-05-12: align the L1 daily-rate tile value with
            # the L1.5 competitive-positioning chart. Both must use the
            # most-recent snapshot per (age × session) — previously this
            # query averaged across the whole latest YEAR, which produced
            # a different value to the L1.5 chart's latest-snapshot-only
            # aggregation. Now consistent.
            fee_rows = conn.execute("""
                SELECT sf.age_band, sf.session_type,
                       AVG(sf.fee_aud) AS median_fee_aud,
                       COUNT(*) AS n_obs,
                       MAX(sf.as_of_date) AS most_recent
                  FROM service_fee sf
                 WHERE sf.service_id = ?
                   AND sf.as_of_date = (
                         SELECT MAX(as_of_date) FROM service_fee sf2
                          WHERE sf2.service_id = sf.service_id
                            AND sf2.age_band = sf.age_band
                            AND sf2.session_type = sf.session_type
                       )
                 GROUP BY sf.age_band, sf.session_type
                 ORDER BY sf.age_band, sf.session_type
            """, (service_id,)).fetchall()
            # Annual trajectory for the headline pair: median per (year)
            # for the most-populated (age_band, session_type) cell. Layer 3
            # chart 7 reads this; sparkline in matrix continues to use the
            # last-N-points compressed view.
            traj_rows = conn.execute("""
                SELECT substr(as_of_date, 1, 4) AS yr,
                       age_band, session_type,
                       AVG(fee_aud) AS median_fee_aud,
                       COUNT(*) AS n_obs
                  FROM service_fee
                 WHERE service_id = ?
                 GROUP BY yr, age_band, session_type
                 ORDER BY yr, age_band, session_type
            """, (service_id,)).fetchall()
            traj_dicts = [_row_to_dict(r) for r in traj_rows]
            out["fees"] = {
                "by_age_band_session": [
                    {
                        "age_band":     r["age_band"],
                        "session_type": r["session_type"],
                        "median_fee":   round(float(r["median_fee_aud"]), 2) if r["median_fee_aud"] is not None else None,
                        "n_obs":        int(r["n_obs"] or 0),
                        "most_recent":  r["most_recent"],
                    }
                    for r in fee_rows
                ],
                "latest_as_of_date": latest_dt,
                "year":              latest_year,
                "annual_trajectory": [
                    {
                        "year":         t.get("yr"),
                        "age_band":     t.get("age_band"),
                        "session_type": t.get("session_type"),
                        "median_fee":   round(float(t["median_fee_aud"]), 2) if t.get("median_fee_aud") is not None else None,
                        "n_obs":        int(t.get("n_obs") or 0),
                    }
                    for t in traj_dicts
                ],
            }
    except sqlite3.OperationalError:
        pass

    # 7. External capture meta (latest fetch timestamp, source)
    try:
        cap_row = conn.execute("""
            SELECT source, fetched_at, http_status, payload_sha256, extractor_version
              FROM service_external_capture
             WHERE service_id = ?
             ORDER BY fetched_at DESC
             LIMIT 1
        """, (service_id,)).fetchone()
        if cap_row is not None:
            out["capture_meta"] = _row_to_dict(cap_row)
    except sqlite3.OperationalError:
        pass

    return out


# ─────────────────────────────────────────────────────────────────────
# Peer-cohort helpers (Centre v2 Bundle B #1 — within-SA2 cohort viz)
# ─────────────────────────────────────────────────────────────────────


def _percentile(sorted_values, q: float):
    """Linear-interpolation percentile of an already-sorted numeric list."""
    if not sorted_values:
        return None
    n = len(sorted_values)
    if n == 1:
        return sorted_values[0]
    pos = q * (n - 1)
    lo = int(pos)
    hi = min(lo + 1, n - 1)
    frac = pos - lo
    return sorted_values[lo] + frac * (sorted_values[hi] - sorted_values[lo])


def _comparable_subtype_group(subject_subtype: Optional[str]) -> tuple:
    """Returns the SQL IN-list of subtype strings that count as comparable
    market peers for the subject. Patrick refinement 2026-05-12: like-for-
    like only — OSHC competes only with OSHC, LDC + Preschool cluster,
    FDC separate. Used by Layer 1 places + daily-rate cohorts AND by
    Layer 1.5 competitive positioning (single source of truth)."""
    s = (subject_subtype or "").upper()
    if "OSHC" in s or "OUTSIDE" in s:
        return ("OSHC",)
    if "FAMILY" in s:
        return ("FDC", "Family Day Care", "FAMILY DAY CARE")
    return ("LDC", "Long Day Care", "LONG DAY CARE", "Preschool", "PRESCHOOL", "PS")


def _cohort_for_places(conn, sa2_code: Optional[str],
                       subject_subtype: Optional[str] = None) -> dict:
    """Approved-places peer cohort within the same SA2, filtered to the
    subject's comparable subtype group (Patrick 2026-05-12: "Layer 1
    should obviously just compare to like for like at the top there.").
    Includes the subject centre so the marker sits naturally within
    the distribution.

    Returns {"n", "min", "p25", "median", "p75", "max", "values", "meaningful"}
    where meaningful=False when n<3 or all values identical — the renderer
    should drop the range bar in that case.
    """
    out = {"n": 0, "min": None, "p25": None, "median": None,
           "p75": None, "max": None, "values": [], "meaningful": False}
    if not sa2_code:
        return out
    comparable = _comparable_subtype_group(subject_subtype)
    placeholders = ",".join("?" * len(comparable))
    try:
        rows = conn.execute(
            f"""
            SELECT approved_places
              FROM services
             WHERE sa2_code = ?
               AND COALESCE(is_active, 1) = 1
               AND approved_places IS NOT NULL
               AND approved_places > 0
               AND service_sub_type IN ({placeholders})
            """,
            (sa2_code, *comparable),
        ).fetchall()
    except sqlite3.OperationalError:
        return out
    values = sorted(int(r[0]) for r in rows)
    if not values:
        return out
    out["n"] = len(values)
    out["values"] = values
    out["min"] = values[0]
    out["max"] = values[-1]
    out["median"] = round(_percentile(values, 0.5), 1)
    out["p25"] = round(_percentile(values, 0.25), 1)
    out["p75"] = round(_percentile(values, 0.75), 1)
    out["meaningful"] = (len(values) >= 3) and (values[-1] > values[0])
    return out


def _cohort_for_daily_rate(conn, sa2_code: Optional[str],
                           subject_subtype: Optional[str] = None) -> dict:
    """Daily-rate peer cohort within the same SA2 by (age_band, session_type),
    filtered to comparable subtype group (Patrick refinement 2026-05-12).
    Reads each service's latest snapshot per cell from `service_fee` and
    groups by cell. Returns dict keyed "{age_band}|{session_type}" with the
    same shape as _cohort_for_places.

    Pilot small-n caveat: 130 services across 3 SA2s — per-SA2 cohorts run
    3-40 services depending on density. Renderer surfaces cohort n in the
    range-bar caption so the reader sees the sample size.
    """
    by_cell: dict = {}
    if not sa2_code:
        return by_cell
    comparable = _comparable_subtype_group(subject_subtype)
    placeholders = ",".join("?" * len(comparable))
    try:
        rows = conn.execute(
            f"""
            SELECT sf.service_id, sf.age_band, sf.session_type, sf.fee_aud
              FROM service_fee sf
              JOIN services s ON s.service_id = sf.service_id
             WHERE s.sa2_code = ?
               AND COALESCE(s.is_active, 1) = 1
               AND s.service_sub_type IN ({placeholders})
               AND sf.fee_aud IS NOT NULL
               AND sf.fee_aud > 0
               AND sf.as_of_date = (
                     SELECT MAX(as_of_date) FROM service_fee sf2
                      WHERE sf2.service_id = sf.service_id
                        AND sf2.age_band = sf.age_band
                        AND sf2.session_type = sf.session_type
                   )
            """,
            (sa2_code, *comparable),
        ).fetchall()
    except sqlite3.OperationalError:
        return by_cell
    # Aggregate per service in case the latest-as_of_date filter still
    # yields multiple rows (different fee_type variants).
    from collections import defaultdict
    per_service = defaultdict(list)
    for r in rows:
        per_service[(int(r[0]), r[1], r[2])].append(float(r[3]))
    cells = defaultdict(list)
    for (_svc, age_band, session_type), vals in per_service.items():
        cells[(age_band, session_type)].append(sum(vals) / len(vals))
    for (age_band, session_type), vals in cells.items():
        v = sorted(vals)
        cell = {
            "age_band":     age_band,
            "session_type": session_type,
            "n":            len(v),
            "min":          round(v[0], 2),
            "max":          round(v[-1], 2),
            "median":       round(_percentile(v, 0.5), 2),
            "p25":          round(_percentile(v, 0.25), 2),
            "p75":          round(_percentile(v, 0.75), 2),
            "values":       [round(x, 2) for x in v],
            "meaningful":   (len(v) >= 3) and (v[-1] > v[0]),
        }
        by_cell[f"{age_band}|{session_type}"] = cell
    return by_cell


# ─────────────────────────────────────────────────────────────────────
# Learning environment substrate — Bundle 2-prep additions 2026-05-12.
# Patrick: rename Education category and add (a) school enrolment YoY
# leading indicator for ECEC demand, (b) asymmetric cross-subtype care
# counts (LDC subject sees OSHC competition, OSHC subject sees LDC feeder
# pipeline). Spatial OSHC-school-attached check deferred to OI-NEW-19
# pending ACARA per-school location ingest at table level.
# ─────────────────────────────────────────────────────────────────────


def _compute_school_enrolment_trend(conn, sa2_code: Optional[str]) -> dict:
    """Returns the latest annual school enrolment for the SA2 plus the
    3-year change vs that latest year. Smoother than YoY for a leading-
    indicator read (year-on-year noise can swing a lot at SA2 scale).
    Reads `abs_sa2_education_employment_annual` long-format table for
    `acara_school_enrolment_total` metric."""
    out = {
        "latest_year":   None,
        "latest_value":  None,
        "value_3y_ago":  None,
        "year_3y_ago":   None,
        "change_3y_pct": None,
        "trajectory":    [],
        "tag":           TAG_OBS,
        "source":        "ACARA School Profile 2008-2025 (acara_school_enrolment_total)",
    }
    if not sa2_code:
        return out
    try:
        rows = conn.execute(
            """
            SELECT year, value
              FROM abs_sa2_education_employment_annual
             WHERE sa2_code = ?
               AND metric_name = 'acara_school_enrolment_total'
               AND value IS NOT NULL
             ORDER BY year ASC
            """,
            (sa2_code,),
        ).fetchall()
    except sqlite3.OperationalError:
        return out
    if not rows:
        return out
    points = [{"year": int(r[0]), "value": float(r[1])} for r in rows]
    out["trajectory"] = points
    out["latest_year"] = points[-1]["year"]
    out["latest_value"] = points[-1]["value"]
    # 3-year change — find the year exactly 3 years prior to latest if
    # present; fallback to closest available point >= 3 years back.
    target_year = out["latest_year"] - 3
    historic = [p for p in points if p["year"] <= target_year]
    if historic:
        ref = historic[-1]  # closest to target_year from below
        out["value_3y_ago"] = ref["value"]
        out["year_3y_ago"] = ref["year"]
        if ref["value"] > 0:
            out["change_3y_pct"] = ((out["latest_value"] - ref["value"]) / ref["value"]) * 100.0
    return out


def _compute_cross_subtype_competition(conn, sa2_code: Optional[str],
                                       subject_subtype: Optional[str]) -> dict:
    """Asymmetric cross-subtype care counts per Patrick 2026-05-12: an LDC
    subject wants to see OSHC competition (transition pathway signal); an
    OSHC subject wants to see LDC feeder pipeline (where its kids come
    from). FDC subject sees both as low-relevance.

    Returns a dict with `target_subtype` (OSHC|LDC|None), `count`,
    `total_places`, and a one-line `framing` string for the matrix row
    commentary. Empty dict shape when subject subtype isn't recognised."""
    out = {
        "subject_subtype":   subject_subtype,
        "target_subtype":    None,
        "target_label":      None,
        "count":             0,
        "total_places":      0,
        "framing":           None,
        "tag":               TAG_OBS,
    }
    if not sa2_code:
        return out
    subtype_uc = (subject_subtype or "").upper()
    if "OSHC" in subtype_uc or "OUTSIDE" in subtype_uc:
        # OSHC subject → show LDC feeder pipeline
        out["target_subtype"] = "LDC"
        out["target_label"] = "Long Day Care (feeder pipeline)"
        out["framing"] = ("Long Day Care services in this catchment — the "
                          "feeder pipeline for school-age transition. "
                          "Higher counts indicate a stronger upstream "
                          "cohort entering school age.")
        target_subtypes = ("LDC", "Long Day Care", "LONG DAY CARE")
    elif "FAMILY" in subtype_uc:
        # FDC: low cross-subtype relevance; surface nothing
        return out
    else:
        # LDC / Preschool subject → show OSHC competition / transition pathway
        out["target_subtype"] = "OSHC"
        out["target_label"] = "OSHC (transition pathway)"
        out["framing"] = ("Outside School Hours Care services in this "
                          "catchment — the transition destination once "
                          "this centre's children enter school age. "
                          "Stronger OSHC supply supports retained "
                          "family-relationship value at the school transition.")
        target_subtypes = ("OSHC",)
    placeholders = ",".join("?" * len(target_subtypes))
    try:
        row = conn.execute(
            f"""
            SELECT COUNT(*), COALESCE(SUM(approved_places), 0)
              FROM services
             WHERE sa2_code = ?
               AND COALESCE(is_active, 1) = 1
               AND service_sub_type IN ({placeholders})
            """,
            (sa2_code, *target_subtypes),
        ).fetchone()
    except sqlite3.OperationalError:
        return out
    out["count"] = int(row[0] or 0)
    out["total_places"] = int(row[1] or 0)
    # Per-service detail for the drawer (Bundle 2 rich-content drawer
    # 2026-05-12 — Patrick: "when you click on OSHC services in catchment
    # it should bring up the services underneath — names, places, daily
    # rate etc."). Pulls latest fee from service_fee for the headline pair
    # appropriate to the TARGET subtype (OSHC → before_school × school-age;
    # LDC → full_day × 36m-preschool).
    if "OSHC" in target_subtypes:
        target_age, target_session = "school-age", "before_school"
    else:
        target_age, target_session = "36m-preschool", "full_day"
    try:
        service_rows = conn.execute(
            f"""
            SELECT
              s.service_id,
              s.service_name,
              s.approved_places,
              s.overall_nqs_rating,
              s.service_sub_type,
              s.large_provider_id,
              lp.name AS large_provider_name,
              (
                SELECT AVG(sf.fee_aud)
                  FROM service_fee sf
                 WHERE sf.service_id = s.service_id
                   AND sf.age_band = ?
                   AND sf.session_type = ?
                   AND sf.fee_aud IS NOT NULL
                   AND sf.fee_aud > 0
                   AND sf.as_of_date = (
                         SELECT MAX(as_of_date) FROM service_fee sf2
                          WHERE sf2.service_id = sf.service_id
                            AND sf2.age_band = sf.age_band
                            AND sf2.session_type = sf.session_type
                       )
              ) AS fee_aud
              FROM services s
              LEFT JOIN large_provider lp
                     ON lp.large_provider_id = s.large_provider_id
             WHERE s.sa2_code = ?
               AND COALESCE(s.is_active, 1) = 1
               AND s.service_sub_type IN ({placeholders})
             ORDER BY s.approved_places DESC, s.service_name ASC
            """,
            (target_age, target_session, sa2_code, *target_subtypes),
        ).fetchall()
    except sqlite3.OperationalError:
        service_rows = []
    out["services"] = [
        {
            "service_id":          int(r[0]),
            "service_name":        r[1],
            "places":              int(r[2] or 0) or None,
            "nqs_overall":         (r[3] or "").strip() or None,
            "subtype":             r[4],
            "large_provider_id":   r[5],
            "large_provider_name": r[6],
            "fee":                 round(float(r[7]), 2) if r[7] is not None else None,
        }
        for r in service_rows
    ]
    # School-attached detection for OSHC services (Patrick 2026-05-12).
    # Now that acara_schools carries per-school lat/lng, do a proximity
    # match: each OSHC service's lat/lng vs schools in the same SA2 plus a
    # ~300m buffer. An OSHC service co-located with a school is the most
    # common arrangement; standalone OSHC indicates a different ops model.
    if "OSHC" in target_subtypes and out["services"]:
        try:
            # Pull every school's lat/lng in the SA2 + service lat/lngs
            schools = conn.execute(
                """
                SELECT acara_sml_id, school_name, sector, school_type, lat, lng
                  FROM acara_schools
                 WHERE sa2_code = ?
                   AND lat IS NOT NULL AND lng IS NOT NULL
                """,
                (sa2_code,),
            ).fetchall()
            svc_ids = [s["service_id"] for s in out["services"]]
            placeholders_s = ",".join("?" * len(svc_ids))
            svc_coords = conn.execute(
                f"""
                SELECT service_id, lat, lng FROM services
                 WHERE service_id IN ({placeholders_s})
                """,
                svc_ids,
            ).fetchall()
            svc_latlng = {r[0]: (r[1], r[2]) for r in svc_coords if r[1] is not None and r[2] is not None}
            # Cheap haversine approximation (small distances, equirectangular)
            def _dist_m(lat1, lng1, lat2, lng2):
                import math as _m
                dlat = _m.radians(lat2 - lat1)
                dlng = _m.radians(lng2 - lng1)
                x = dlng * _m.cos(_m.radians((lat1 + lat2) / 2))
                y = dlat
                return _m.sqrt(x * x + y * y) * 6371000.0
            ATTACH_THRESHOLD_M = 300.0
            n_attached = 0
            for svc in out["services"]:
                ll = svc_latlng.get(svc["service_id"])
                svc["school_attached"] = None
                svc["nearest_school"] = None
                svc["nearest_school_distance_m"] = None
                if not ll:
                    continue
                best = None
                best_dist = None
                for sch in schools:
                    d = _dist_m(ll[0], ll[1], sch[4], sch[5])
                    if best_dist is None or d < best_dist:
                        best_dist = d
                        best = sch
                if best is not None:
                    svc["nearest_school"] = {
                        "acara_sml_id":  best[0],
                        "school_name":   best[1],
                        "sector":        best[2],
                        "school_type":   best[3],
                    }
                    svc["nearest_school_distance_m"] = round(best_dist, 1)
                    if best_dist <= ATTACH_THRESHOLD_M:
                        svc["school_attached"] = True
                        n_attached += 1
                    else:
                        svc["school_attached"] = False
            out["n_school_attached"] = n_attached
            out["attach_threshold_m"] = ATTACH_THRESHOLD_M
        except sqlite3.OperationalError:
            # acara_schools table not present → skip detection silently.
            pass
    return out


def _compute_education_supply_events(conn, sa2_code: Optional[str]) -> list:
    """Build a centre_events-shaped list for the school enrolment chart
    showing 'new education environments arriving' per year (Patrick
    2026-05-12). Two event sources:
      1. New schools — YoY delta in acara_school_count_total
      2. New OSHC services — services.approval_granted_date in that year
         + sa2_code match + subtype=OSHC
    Returns the same shape as catchment centre_events (quarter, net_centres,
    places_change, new_names, removed_names) so the existing
    _kintellEventAnnotation plugin can render it. `quarter` is the year as
    a string (e.g. "2019") since school data is annual cadence.
    """
    if not sa2_code:
        return []
    events_by_year: dict = {}

    # 1. New schools per year — derived from YoY count delta in long-format
    #    abs_sa2_education_employment_annual.
    try:
        rows = conn.execute(
            """
            SELECT year, value FROM abs_sa2_education_employment_annual
             WHERE sa2_code = ? AND metric_name = 'acara_school_count_total'
               AND value IS NOT NULL
             ORDER BY year ASC
            """,
            (sa2_code,),
        ).fetchall()
        prev = None
        for r in rows:
            yr = int(r[0])
            cur_count = int(r[1])
            if prev is not None and cur_count > prev:
                added = cur_count - prev
                events_by_year.setdefault(str(yr), {
                    "quarter": str(yr),
                    "net_centres": 0,
                    "new_centres": 0,
                    "places_change": 0,
                    "new_names": [],
                    "removed_centres": 0,
                    "removed_names": [],
                })
                events_by_year[str(yr)]["net_centres"] += added
                events_by_year[str(yr)]["new_centres"] += added
                events_by_year[str(yr)]["new_names"].append(
                    f"{added} new school{'s' if added != 1 else ''} (ACARA count delta)"
                )
            elif prev is not None and cur_count < prev:
                removed = prev - cur_count
                events_by_year.setdefault(str(yr), {
                    "quarter": str(yr),
                    "net_centres": 0,
                    "new_centres": 0,
                    "places_change": 0,
                    "new_names": [],
                    "removed_centres": 0,
                    "removed_names": [],
                })
                events_by_year[str(yr)]["net_centres"] -= removed
                events_by_year[str(yr)]["removed_centres"] += removed
                events_by_year[str(yr)]["removed_names"].append(
                    f"{removed} school{'s' if removed != 1 else ''} closed (ACARA count delta)"
                )
            prev = cur_count
    except sqlite3.OperationalError:
        pass

    # 2. New OSHC services per year — from services.approval_granted_date.
    #    Date format is DD/MM/YYYY per ACECQA convention.
    try:
        rows = conn.execute(
            """
            SELECT service_name, approval_granted_date, approved_places
              FROM services
             WHERE sa2_code = ?
               AND COALESCE(is_active, 1) = 1
               AND service_sub_type = 'OSHC'
               AND approval_granted_date IS NOT NULL
            """,
            (sa2_code,),
        ).fetchall()
        for r in rows:
            raw = r[1] or ""
            m = re.match(r"^\d{1,2}/\d{1,2}/(\d{4})$", raw)
            if not m:
                m = re.search(r"(\d{4})", raw)
            if not m:
                continue
            yr = m.group(1)
            events_by_year.setdefault(yr, {
                "quarter": yr,
                "net_centres": 0,
                "new_centres": 0,
                "places_change": 0,
                "new_names": [],
                "removed_centres": 0,
                "removed_names": [],
            })
            events_by_year[yr]["net_centres"] += 1
            events_by_year[yr]["new_centres"] += 1
            events_by_year[yr]["places_change"] += int(r[2] or 0)
            events_by_year[yr]["new_names"].append(
                f"{r[0]} (OSHC, {int(r[2] or 0)} places)"
            )
    except sqlite3.OperationalError:
        pass

    return sorted(events_by_year.values(), key=lambda e: e["quarter"])


def _build_schools_in_catchment(conn, sa2_code: Optional[str]) -> dict:
    """Returns per-school detail for every school in the SA2. Drives
    Bundle 2 schools-in-catchment drawer enrichment (Patrick 2026-05-12).
    Names + sector + type + enrolments + ICSEA per school. Sorted by
    enrolment descending so the dominant schools head the list."""
    out = {"sa2_code": sa2_code, "n_schools": 0, "schools": [], "tag": TAG_OBS}
    if not sa2_code:
        return out
    try:
        rows = conn.execute(
            """
            SELECT acara_sml_id, school_name, sector, school_type,
                   suburb, postcode, enrolments_total, icsea, lat, lng
              FROM acara_schools
             WHERE sa2_code = ?
             ORDER BY enrolments_total DESC NULLS LAST, school_name ASC
            """,
            (sa2_code,),
        ).fetchall()
    except sqlite3.OperationalError:
        return out
    out["schools"] = [
        {
            "acara_sml_id":     int(r[0]),
            "school_name":      r[1],
            "sector":           r[2],
            "school_type":      r[3],
            "suburb":           r[4],
            "postcode":         r[5],
            "enrolments_total": int(r[6]) if r[6] is not None else None,
            "icsea":            int(r[7]) if r[7] is not None else None,
            "lat":              r[8],
            "lng":              r[9],
        }
        for r in rows
    ]
    out["n_schools"] = len(out["schools"])
    return out


# ─────────────────────────────────────────────────────────────────────
# Competitive positioning — Layer 1.5 panel showing every centre in the
# same SA2 on a daily-fee × NQS axis with subject centre emphasised.
# Patrick 2026-05-12: "shows commercial + operational positioning within
# the competitive ecosystem at a glance". Lives between Layer 1 (identity)
# and Layer 2 (intelligence). Data shape per centre: name, fee, places,
# nqs, last assessment date, operator group, is_subject flag.
# ─────────────────────────────────────────────────────────────────────


def _build_competitive_positioning(conn, subject_service_id: int,
                                   sa2_code: Optional[str],
                                   subject_subtype: Optional[str]) -> dict:
    """Returns competitive-positioning payload for the subject centre's SA2.
    Includes only services with a usable headline daily fee in the same
    age × session pair the subject centre uses (LDC/Preschool/FDC →
    full_day × 36m-preschool; OSHC → before_school × school-age).

    Shape:
      {
        "sa2_code": str,
        "subject_service_id": int,
        "n_centres": int,
        "headline_pair": {"age_band", "session_type"},
        "ccs_hourly_cap_aud": float,
        "operating_hours_assumed": int,
        "ccs_daily_cap_aud": float,
        "centres": [
          {
            "service_id", "service_name", "fee", "places",
            "nqs_overall", "last_assessed_at", "large_provider_id",
            "large_provider_name", "subtype", "is_subject"
          },
          ...
        ]
      }
    """
    out = {
        "sa2_code":               sa2_code,
        "subject_service_id":     subject_service_id,
        "n_centres":              0,
        "headline_pair":          None,
        "subject_subtype":        subject_subtype,
        "comparable_group_label": None,
        "ccs_hourly_cap_aud":     13.73,   # July 2024-25 Centre-Based Day Care cap
        "operating_hours_assumed": 10,
        "ccs_daily_cap_aud":      137.30,  # 13.73 × 10
        "centres":                [],
    }
    if not sa2_code:
        return out
    subtype_uc = (subject_subtype or "").upper()
    is_oshc = ("OSHC" in subtype_uc) or ("OUTSIDE" in subtype_uc)
    is_fdc = "FAMILY" in subtype_uc
    age_band = "school-age" if is_oshc else "36m-preschool"
    session_type = "before_school" if is_oshc else "full_day"
    out["headline_pair"] = {"age_band": age_band, "session_type": session_type}

    # Comparable-subtype group — Patrick 2026-05-12 framing: only compare
    # apples with apples. Single source of truth in
    # `_comparable_subtype_group`; this builder just attaches the human
    # label for the methodology line in the renderer.
    comparable_subtypes = _comparable_subtype_group(subject_subtype)
    if is_oshc:
        out["comparable_group_label"] = "Outside School Hours Care (school-age)"
    elif is_fdc:
        out["comparable_group_label"] = "Family Day Care (in-home, all ages)"
    else:
        out["comparable_group_label"] = "Comparable long day care centres (0–5 years)"

    # SQL IN-list placeholder
    placeholders = ",".join("?" * len(comparable_subtypes))
    try:
        rows = conn.execute(
            f"""
            SELECT
              s.service_id,
              s.service_name,
              s.approved_places,
              s.overall_nqs_rating,
              s.large_provider_id,
              s.service_sub_type,
              lp.name AS large_provider_name,
              (
                SELECT AVG(sf.fee_aud)
                  FROM service_fee sf
                 WHERE sf.service_id = s.service_id
                   AND sf.age_band = ?
                   AND sf.session_type = ?
                   AND sf.fee_aud IS NOT NULL
                   AND sf.fee_aud > 0
                   AND sf.as_of_date = (
                         SELECT MAX(as_of_date) FROM service_fee sf2
                          WHERE sf2.service_id = sf.service_id
                            AND sf2.age_band = sf.age_band
                            AND sf2.session_type = sf.session_type
                       )
              ) AS fee_aud,
              (
                SELECT srs.last_regulatory_visit
                  FROM service_regulatory_snapshot srs
                 WHERE srs.service_id = s.service_id
                 ORDER BY srs.snapshot_date DESC
                 LIMIT 1
              ) AS last_assessed_at
              FROM services s
              LEFT JOIN large_provider lp
                     ON lp.large_provider_id = s.large_provider_id
             WHERE s.sa2_code = ?
               AND COALESCE(s.is_active, 1) = 1
               AND s.service_sub_type IN ({placeholders})
            """,
            (age_band, session_type, sa2_code, *comparable_subtypes),
        ).fetchall()
    except sqlite3.OperationalError:
        return out

    centres = []
    for row in rows:
        d = _row_to_dict(row)
        fee = d.get("fee_aud")
        if fee is None or fee <= 0:
            continue  # only include centres with a usable headline fee
        centres.append({
            "service_id":          d.get("service_id"),
            "service_name":        d.get("service_name"),
            "fee":                 round(float(fee), 2),
            "places":              int(d.get("approved_places") or 0) or None,
            "nqs_overall":         (d.get("overall_nqs_rating") or "").strip() or None,
            "last_assessed_at":    d.get("last_assessed_at"),
            "large_provider_id":   d.get("large_provider_id"),
            "large_provider_name": d.get("large_provider_name"),
            "subtype":             d.get("service_sub_type"),
            "is_subject":          int(d.get("service_id") or -1) == subject_service_id,
        })
    centres.sort(key=lambda c: c["fee"])
    out["n_centres"] = len(centres)
    out["centres"] = centres
    return out


# ─────────────────────────────────────────────────────────────────────
# CCS Coverage Ratio — % of catchment households estimated to receive
# the full CCS benefit, derived from SA2 median household income.
# Lognormal-distribution model on the income side (empirically reasonable
# for AU household income, σ≈0.5 nationally). V1 single-threshold against
# the current ~$80K full-benefit cutoff; bands surface methodology
# transparency in about_data per DEC-69 OBS/DER discipline.
# ─────────────────────────────────────────────────────────────────────

import math as _math

_CCS_FULL_BENEFIT_THRESHOLD = 80000   # AU dollars, annual family income (~2026 figure)
_CCS_INCOME_SIGMA = 0.5               # σ of lognormal on annual AU household income; nationally typical
_CCS_WEEKLY_TO_ANNUAL = 52            # ABS publishes household income weekly; convert for threshold compare


def _normal_cdf(z: float) -> float:
    """Standard normal CDF via erf — sufficient precision for percentile output."""
    return 0.5 * (1.0 + _math.erf(z / _math.sqrt(2.0)))


def _compute_ccs_coverage(median_weekly_household_income: Optional[float]) -> dict:
    """Estimate the fraction of households below the CCS full-benefit threshold.
    Returns a payload-shaped dict:
      {
        "value_pct":  float|None,  # 0..100 (or None when median absent)
        "band":       str,         # qualitative band for matrix Signal column
        "methodology": str,        # rendered in drawer about_data
        "threshold_aud": int,      # the threshold used (transparency)
        "median_weekly_aud": float,
        "median_annual_aud": float,
        "tag": "DER",
      }
    """
    out = {
        "value_pct":          None,
        "band":               None,
        "methodology":        ("CCS Coverage Ratio = estimated share of catchment households below the "
                                f"CCS full-benefit family income threshold (~A${_CCS_FULL_BENEFIT_THRESHOLD:,}/yr; "
                                "current Australian Childcare Subsidy income test). Derived from ABS Census "
                                "SA2 median weekly household income via a lognormal model with σ≈0.5 (AU "
                                "household income distribution shape, nationally calibrated). Three Day "
                                "Guarantee (Jan 2026) overlays minimum 3-day subsidised access regardless of "
                                "activity test, so this ratio reads as fee-headroom signal, not access cap."),
        "threshold_aud":      _CCS_FULL_BENEFIT_THRESHOLD,
        "median_weekly_aud":  None,
        "median_annual_aud":  None,
        "tag":                TAG_DER,
    }
    if median_weekly_household_income is None or median_weekly_household_income <= 0:
        return out
    mwk = float(median_weekly_household_income)
    mann = mwk * _CCS_WEEKLY_TO_ANNUAL
    out["median_weekly_aud"] = round(mwk, 2)
    out["median_annual_aud"] = round(mann, 2)
    # Lognormal CDF at threshold: P(income < T) where median = exp(μ).
    mu = _math.log(mann)
    z = (_math.log(_CCS_FULL_BENEFIT_THRESHOLD) - mu) / _CCS_INCOME_SIGMA
    pct = _normal_cdf(z) * 100.0
    # Pin to plausible 0-100 range against numerical edges
    pct = max(0.0, min(100.0, pct))
    out["value_pct"] = round(pct, 1)
    # Banding mirrors signal-matrix shape — high / mid / low (no industry band
    # because this is catchment affordability, not a centre-level metric).
    if pct >= 75:
        out["band"] = "high"
    elif pct >= 50:
        out["band"] = "mid-high"
    elif pct >= 30:
        out["band"] = "mid"
    elif pct > 0:
        out["band"] = "low"
    else:
        out["band"] = None
    return out


def _hours_summary(snap: dict) -> Optional[str]:
    """Compose a one-line operating-hours summary from the 14 hours_* cols
    of a regulatory snapshot dict. Returns 'Mon–Fri 7:00am–6:00pm' shape
    when weekday hours are uniform; falls back to 'See details' if mixed.
    Returns None when no hours data at all."""
    days = ("monday", "tuesday", "wednesday", "thursday", "friday")
    weekend = ("saturday", "sunday")

    def _fmt(t: Optional[str]) -> Optional[str]:
        if not t:
            return None
        # Accept "07:00" / "7:00" / "07:00:00"; render as "7:00am" / "6:00pm"
        s = str(t).strip()
        try:
            h, m = s.split(":")[:2]
            hi = int(h)
            mi = int(m)
            am = hi < 12
            hh = hi % 12 or 12
            return f"{hh}:{mi:02d}{'am' if am else 'pm'}"
        except (ValueError, IndexError):
            return s

    weekday_pairs = []
    for d in days:
        o = snap.get(f"hours_{d}_open")
        c = snap.get(f"hours_{d}_close")
        if o and c:
            weekday_pairs.append((_fmt(o), _fmt(c)))
    weekend_pairs = []
    for d in weekend:
        o = snap.get(f"hours_{d}_open")
        c = snap.get(f"hours_{d}_close")
        if o and c:
            weekend_pairs.append((d, _fmt(o), _fmt(c)))

    if not weekday_pairs and not weekend_pairs:
        return None

    parts = []
    if weekday_pairs:
        if all(p == weekday_pairs[0] for p in weekday_pairs):
            o, c = weekday_pairs[0]
            parts.append(f"Mon–Fri {o}–{c}")
        else:
            parts.append("Mon–Fri (varies)")
    for d, o, c in weekend_pairs:
        parts.append(f"{d.capitalize()[:3]} {o}–{c}")
    return "; ".join(parts) if parts else None


def _to_bool(v) -> Optional[bool]:
    """Coerce SQLite 0/1/None/'true'/'false' to Python bool/None."""
    if v is None:
        return None
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return bool(v)
    s = str(v).strip().lower()
    if s in ("1", "true", "t", "yes", "y"):
        return True
    if s in ("0", "false", "f", "no", "n", ""):
        return False
    return None


# ─────────────────────────────────────────────────────────────────────
# Layer 2 — Executive interpretation (DEC-84 #2 + #3)
# ─────────────────────────────────────────────────────────────────────


def _build_executive(r: dict, position: dict, dec83_state: dict,
                     community_profile: Optional[dict] = None) -> dict:
    """Returns Layer 2 payload: 5 signal tiles + flag bar (max 2 + spillover)
    + composed headline. Each signal tile has a links_to pointer to the
    relevant Layer 5 matrix category for click-through. Flag triggers per
    DEC-84 #3 severity hierarchy. community_profile (added Turn 3 polish)
    feeds the Community signal with top-2 languages alongside the NES band.
    """
    catchment = position.get("catchment_position", {}) or {}
    pop = position.get("population", {}) or {}
    lab = position.get("labour_market", {}) or {}

    # Helper: pull display + band + decile + raw_value summary from a position entry
    def _summarise(card_dict, metric_key):
        e = card_dict.get(metric_key) or {}
        return {
            "metric":     metric_key,
            "raw_value":  e.get("raw_value"),
            "decile":     e.get("decile"),
            "band":       e.get("band"),
            "industry_band":       e.get("industry_band"),
            "industry_band_label": e.get("industry_band_label"),
            "confidence": e.get("confidence"),
        }

    # ── 5 signal tiles ───────────────────────────────────────────────
    demand_src = _summarise(catchment, "sa2_adjusted_demand")
    supply_src = _summarise(catchment, "sa2_supply_ratio")
    nqs_overall = (r.get("overall_nqs_rating") or "").strip() or None
    nqs_prev = ((dec83_state.get("regulatory_snapshot") or {}).get("nqs_prev_overall") or "").strip() or None
    lfp_f = _summarise(lab, "sa2_lfp_females")
    unemp = _summarise(lab, "sa2_unemployment_rate")
    nes = _summarise(catchment, "sa2_nes_share")

    # ── Sub-metric depth (Layer 2 upgrade 2026-05-13) ───────────────
    # Each tile carries 2-3 sub-metric rows beneath the headline summary.
    # Sub-rows surface the composition of the signal at a glance so the
    # reader sees the underlying drivers without scrolling to the matrix.
    pop = position.get("population", {}) or {}
    submetrics = {
        "demand": [
            _submetric_row(catchment, "sa2_adjusted_demand", "Adjusted demand"),
            _submetric_row(catchment, "sa2_demand_supply",   "Demand vs supply"),
            _submetric_row(catchment, "sa2_child_to_place",  "Children per place"),
        ],
        "supply": [
            _submetric_row(catchment, "sa2_supply_ratio",    "Supply ratio"),
            _submetric_row(catchment, "sa2_demand_share_state", "State demand share"),
            _submetric_row(pop,       "sa2_under5_count",    "Under-5 catchment"),
        ],
        "workforce": [
            _submetric_row(lab, "sa2_lfp_females",     "Female LFP"),
            _submetric_row(lab, "sa2_unemployment_rate", "Unemployment"),
            _submetric_row(lab, "sa2_lfp_persons",     "LFP persons"),
        ],
        "quality": _quality_submetrics(nqs_overall, dec83_state),
        "community": [
            _submetric_row(catchment, "sa2_nes_share",   "NES share"),
            _submetric_row(catchment, "sa2_atsi_share",  "ATSI share"),
            _submetric_row(catchment, "sa2_overseas_born_share", "Overseas-born"),
        ],
        "population": [
            _submetric_row(pop, "sa2_under5_count",          "Under-5 count"),
            _submetric_row(pop, "sa2_births_count",          "Annual births"),
            _submetric_row(catchment, "sa2_parent_cohort_25_44_share", "Parents 25-44"),
        ],
    }

    signals = [
        {
            "id":      "demand",
            "label":   "Demand",
            "summary": _signal_summary_demand(demand_src),
            "links_to": "matrix:demand",
            "source":  demand_src,
            "sub_metrics": [s for s in submetrics["demand"] if s],
        },
        {
            "id":      "supply",
            "label":   "Supply",
            "summary": _signal_summary_supply(supply_src),
            "links_to": "matrix:supply",
            "source":  supply_src,
            "sub_metrics": [s for s in submetrics["supply"] if s],
        },
        {
            "id":      "population",
            "label":   "Population",
            "summary": _signal_summary_population(pop),
            "links_to": "matrix:population",
            "source":  pop.get("sa2_under5_count") or {},
            "sub_metrics": [s for s in submetrics["population"] if s],
        },
        {
            "id":      "workforce",
            "label":   "Workforce",
            "summary": _signal_summary_workforce(lfp_f, unemp),
            "links_to": "matrix:workforce",
            "source":  {"lfp_females": lfp_f, "unemployment": unemp},
            "sub_metrics": [s for s in submetrics["workforce"] if s],
        },
        {
            "id":      "quality",
            "label":   "Quality",
            "summary": _signal_summary_quality(nqs_overall, nqs_prev, dec83_state),
            "links_to": "matrix:quality",
            "source":  {"nqs_overall": nqs_overall, "nqs_prev": nqs_prev},
            "sub_metrics": [s for s in submetrics["quality"] if s],
        },
        {
            "id":      "community",
            "label":   "Community",
            "summary": _signal_summary_community(nes, catchment, dec83_state, community_profile),
            "links_to": "matrix:community",
            "source":  nes,
            "sub_metrics": [s for s in submetrics["community"] if s],
        },
    ]

    # ── Flag bar ─────────────────────────────────────────────────────
    flags = _compute_flags(dec83_state, nqs_overall)

    # ── Headline composer (rule-based) ──────────────────────────────
    headline = _compose_headline(supply_src, demand_src, nqs_overall, nes, dec83_state)

    return {
        "headline": headline,
        "signals":  signals,
        "flags":    flags,  # may include _spillover key when >2 triggered
    }


def _submetric_row(card_dict: dict, metric_key: str, display_name: str) -> Optional[dict]:
    """Build a Layer 2 sub-metric row for a position entry. Returns None
    when the entry is absent or has no usable value — caller filters Nones."""
    e = (card_dict or {}).get(metric_key) or {}
    raw = e.get("raw_value")
    if raw is None:
        return None
    fmt = e.get("value_format")
    # Compact value display — Layer 2 prefers terse numerics with units
    if fmt == "percent" or fmt == "percent_share":
        v_display = f"{raw:.1f}%"
    elif fmt == "ratio_x":
        v_display = f"{raw:.2f}×"
    elif fmt == "int":
        v_display = f"{int(round(raw)):,}"
    elif fmt == "currency_annual":
        v_display = f"${int(round(raw)):,}"
    elif fmt == "currency_weekly":
        v_display = f"${int(round(raw)):,}/wk"
    else:
        v_display = f"{raw:.2f}" if isinstance(raw, float) else str(raw)
    # Band class for the pill — collapse industry_band and band to canonical
    # high/mid/low/no_rating tier used by the frontend CSS pill classes.
    band_raw = (e.get("industry_band_label") or e.get("band") or "").lower()
    if not band_raw:
        band_class = "no-rating"
    elif any(k in band_raw for k in ("high", "above", "elevated", "tight", "premium", "strong")):
        band_class = "high"
    elif any(k in band_raw for k in ("low", "below", "soft", "loose", "cheaper")):
        band_class = "low"
    else:
        band_class = "mid"
    return {
        "name":         display_name,
        "metric":       metric_key,
        "value_display": v_display,
        "band":         e.get("band"),
        "band_class":   band_class,
        "decile":       e.get("decile"),
    }


def _signal_summary_population(pop_card: dict) -> str:
    """Quick descriptive summary for the Population signal tile — under-5
    count (catchment scale) + growth direction if available."""
    u5 = (pop_card or {}).get("sa2_under5_count") or {}
    u5_raw = u5.get("raw_value")
    if u5_raw is None:
        return "Pending demographic ingest"
    u5_int = int(round(u5_raw))
    band = u5.get("band") or "mid"
    return f"{u5_int:,} under-5 · {band}"


def _quality_submetrics(nqs_overall: Optional[str], dec83_state: dict) -> list:
    """Sub-metric rows for the Quality tile — NQS rating + active conditions
    count + recent enforcement count. Hand-assembled because these aren't
    standard position-card metrics, they live across r + dec83_state."""
    rows = []
    if nqs_overall:
        rating_lc = nqs_overall.lower()
        # Map full NQS rating into short band labels so the pill doesn't
        # duplicate the value column.
        if "exceeding" in rating_lc:
            band_class, band_label = "high", "above"
        elif "meeting" in rating_lc:
            band_class, band_label = "mid", "at"
        elif "working" in rating_lc or "significant" in rating_lc:
            band_class, band_label = "low", "below"
        else:
            band_class, band_label = "mid", "—"
        rows.append({
            "name":         "NQS overall",
            "metric":       "nqs_overall",
            "value_display": nqs_overall,
            "band":         band_label,
            "band_class":   band_class,
            "decile":       None,
        })
    cond_active = (dec83_state.get("conditions") or {}).get("active_count")
    if cond_active is not None:
        rows.append({
            "name":         "Active conditions",
            "metric":       "service_conditions",
            "value_display": str(int(cond_active)),
            "band":         "amber" if cond_active > 0 else "clear",
            "band_class":   "low" if cond_active > 0 else "no-rating",
            "decile":       None,
        })
    enf_recent = (dec83_state.get("enforcement") or {}).get("recent_24mo_count")
    if enf_recent is not None:
        rows.append({
            "name":         "Recent enforcement (24mo)",
            "metric":       "enforcement_recent",
            "value_display": str(int(enf_recent)),
            "band":         "amber" if enf_recent > 0 else "clear",
            "band_class":   "low" if enf_recent > 0 else "no-rating",
            "decile":       None,
        })
    return rows[:3]  # cap at 3 per Patrick's 2-3 guidance


def _signal_summary_demand(s):
    band = s.get("industry_band_label") or s.get("band") or "—"
    dec = s.get("decile")
    if s.get("confidence") in (None, "unavailable", "deferred") or dec is None:
        return "Pending data"
    return f"{band.capitalize()} · decile {dec}"


def _signal_summary_supply(s):
    band = s.get("industry_band_label") or s.get("band") or "—"
    dec = s.get("decile")
    if s.get("confidence") in (None, "unavailable", "deferred") or dec is None:
        return "Pending data"
    return f"{band.capitalize()} · decile {dec}"


def _signal_summary_workforce(lfp_f, unemp=None):
    """Female LFP band + decile, plus inline unemployment value when populated
    (Bundle B #2 enrichment 2026-05-13). Unemployment is a demand-pool signal
    for the workforce supply lens — high unemployment means more potential
    labour pool, low unemployment means tight labour competition."""
    if lfp_f.get("confidence") in (None, "unavailable", "deferred") or lfp_f.get("decile") is None:
        base = "Pending V1.5 A6/A7 wire-up"
    else:
        band = lfp_f.get("band") or "mid"
        base = f"Female LFP {band} · D{lfp_f.get('decile')}"
    if unemp and unemp.get("confidence") not in (None, "unavailable", "deferred"):
        u_raw = unemp.get("raw_value")
        if isinstance(u_raw, (int, float)):
            base = f"{base} · Unemp {u_raw:.1f}%"
    return base


def _signal_summary_quality(nqs_overall, nqs_prev, dec83_state=None):
    """NQS rating with prev-overall qualifier, plus conditions / recent
    enforcement count when triggered (Bundle B #2 enrichment 2026-05-13).
    Mirrors flag-bar severity hierarchy in tile copy: conditions and
    enforcement are already AMBER flags per DEC-84 #3, but surfacing
    counts inline gives the reader instant scale of the regulatory
    exposure without needing the flag-pill spillover view."""
    if not nqs_overall:
        base = "Not yet rated"
    else:
        prev_clean = (nqs_prev or "").strip()
        if prev_clean and prev_clean.upper() not in ("NONE", "NULL", "—") and prev_clean != nqs_overall:
            base = f"{nqs_overall} (prev {prev_clean})"
        else:
            base = nqs_overall
    if dec83_state:
        cond = (dec83_state.get("conditions") or {}).get("active_count") or 0
        enf_recent = (dec83_state.get("enforcement") or {}).get("recent_24mo_count") or 0
        extras = []
        if cond > 0:
            extras.append(f"{cond} active cond")
        if enf_recent > 0:
            extras.append(f"{enf_recent} recent enforcement")
        if extras:
            base = f"{base} · {' · '.join(extras)}"
    return base


def _signal_summary_community(nes_src, catchment, dec83_state, community_profile=None):
    # Quick descriptive flavour; rule-based, no scoring.
    nes_v = nes_src.get("raw_value") if isinstance(nes_src, dict) else None
    nes_dec = nes_src.get("decile") if isinstance(nes_src, dict) else None
    atsi = (catchment.get("sa2_atsi_share") or {}).get("raw_value")
    if nes_v is None:
        return "Pending demographic ingest"
    parts = []
    if isinstance(nes_v, (int, float)):
        if nes_v >= 50:
            parts.append("high NES")
        elif nes_v >= 25:
            parts.append("moderate NES")
        else:
            parts.append("low NES")
    if isinstance(atsi, (int, float)) and atsi >= 10:
        parts.append("high ATSI")
    if nes_dec and nes_dec >= 8:
        parts.append("culturally diverse")
    base = " / ".join(parts) if parts else "Standard catchment mix"
    # Top-2 languages spoken at home for additional community context per
    # Turn 3 polish — surfaces actual languages instead of a generic
    # "culturally diverse" descriptor so the reader sees which languages
    # are present without scrolling to the matrix.
    if community_profile:
        langs = community_profile.get("language_at_home_top_n") or []
        names = []
        for item in langs[:2]:
            name = item.get("language") if isinstance(item, dict) else None
            if name:
                names.append(name)
        if names:
            return f"{base} · {', '.join(names)}"
    return base


def _compute_flags(dec83_state: dict, nqs_overall: Optional[str]) -> dict:
    """Severity hierarchy per DEC-84 #3. Returns {visible: [...], spillover_count: N}."""
    snap = dec83_state.get("regulatory_snapshot") or {}
    cond = dec83_state.get("conditions") or {}
    enf = dec83_state.get("enforcement") or {}
    vac = dec83_state.get("vacancy") or {}

    triggered = []

    # RED flags
    if snap.get("ccs_revoked_by_ea") is True:
        triggered.append({"severity": "red", "id": "ccs_revoked", "label": "CCS revoked by EA",
                          "links_to": "drawer:dec83:nqs"})
    if snap.get("is_closed") is True:
        triggered.append({"severity": "red", "id": "closed", "label": "Service closed",
                          "links_to": "matrix:operations"})
    if snap.get("temporarily_closed") is True:
        triggered.append({"severity": "red", "id": "temp_closed", "label": "Temporarily closed",
                          "links_to": "matrix:operations"})

    # AMBER flags
    if (cond.get("active_count") or 0) > 0:
        triggered.append({"severity": "amber", "id": "active_conditions",
                          "label": f"{cond['active_count']} active condition" + ("s" if cond["active_count"] != 1 else ""),
                          "links_to": "drawer:dec83:conditions"})
    if nqs_overall in ("Working Towards NQS", "Significant Improvement Required", "Provisional"):
        triggered.append({"severity": "amber", "id": "sub_meeting_nqs",
                          "label": f"NQS: {nqs_overall}",
                          "links_to": "drawer:dec83:nqs"})
    if (enf.get("recent_24mo_count") or 0) > 0:
        triggered.append({"severity": "amber", "id": "recent_enforcement",
                          "label": f"{enf['recent_24mo_count']} enforcement event" + ("s" if enf["recent_24mo_count"] != 1 else "") + " (24mo)",
                          "links_to": "drawer:dec83:enforcement"})

    # INFORMATIONAL flags
    if vac.get("all_no_vacancies_published") is True:
        triggered.append({"severity": "info", "id": "no_vacancies",
                          "label": "No vacancies published",
                          "links_to": "drawer:dec83:vacancy"})

    # Severity ordering: red first, amber, info
    severity_order = {"red": 0, "amber": 1, "info": 2}
    triggered.sort(key=lambda f: severity_order.get(f["severity"], 3))

    visible = triggered[:2]
    spillover = max(0, len(triggered) - 2)
    return {"visible": visible, "spillover_count": spillover, "all_triggered": triggered}


def _compose_headline(supply_src, demand_src, nqs_overall, nes_src, dec83_state) -> str:
    """Rule-based composition: '[supply band] · [demand band] · [demographic flavour] · [quality posture]'."""
    parts = []
    s_band = supply_src.get("industry_band_label") or supply_src.get("band")
    if s_band:
        parts.append(f"{s_band.capitalize()} supply")
    d_band = demand_src.get("industry_band_label") or demand_src.get("band")
    if d_band:
        parts.append(f"{d_band.capitalize()} demand")
    nes_v = nes_src.get("raw_value") if isinstance(nes_src, dict) else None
    if isinstance(nes_v, (int, float)):
        flavour = "high-NES catchment" if nes_v >= 40 else ("moderate-NES catchment" if nes_v >= 20 else "low-NES catchment")
        parts.append(flavour)
    if nqs_overall:
        parts.append(nqs_overall)
    return " / ".join(parts) if parts else "—"


# ─────────────────────────────────────────────────────────────────────
# Layer 5 — Institutional signal matrix (DEC-84 #5)
# ─────────────────────────────────────────────────────────────────────


def _build_matrix(r: dict, position: dict, workforce_supply: dict,
                  community_profile: dict, dec83_state: dict) -> list:
    """Layer 5 matrix as a list of row dicts. ~52 rows V1, 9 categories
    in display order (Demand / Supply / Pricing & Fees / Quality / Workforce
    / Community / Education / Operator-Group / Operations / Population /
    Labour Market). Each row carries the 8-column matrix structure per
    DEC-84 #5. Sorting V1 = fixed display order matching POSITION_CARD_ORDER
    + new entries appended per category.
    """
    rows: list = []
    catchment = position.get("catchment_position", {}) or {}
    pop = position.get("population", {}) or {}
    lab = position.get("labour_market", {}) or {}
    edu = position.get("education_infrastructure", {}) or {}

    # ── DEMAND (3) ───────────────────────────────────────────────────
    rows.extend(_matrix_rows_from_position(catchment, [
        "sa2_adjusted_demand", "sa2_demand_supply", "sa2_demand_share_state",
    ], "demand"))

    # ── SUPPLY (2 + DEC-83 vacancy posture) ──────────────────────────
    rows.extend(_matrix_rows_from_position(catchment, [
        "sa2_supply_ratio", "sa2_child_to_place",
    ], "supply"))
    # V1.5 stub for subtype-correct supply ratio (A5)
    rows.append(_matrix_stub_row("sa2_supply_ratio_per_subtype", "supply",
        "Supply ratio per subtype", "Pending V1.5 A5"))
    # DEC-83 vacancy posture row
    rows.append(_matrix_dec83_vacancy_row(dec83_state))

    # ── PRICING & FEES (NEW DEC-83) ─────────────────────────────────
    # 5 rows for LDC/FDC/Preschool: full_day per age band; OSHC swaps to
    # before/after_school × school-age. Half-day / hourly / before-after
    # for non-OSHC live in drawer only per DEC-84 #9.
    rows.extend(_matrix_pricing_rows(r, dec83_state))

    # ── QUALITY (NEW DEC-83) ────────────────────────────────────────
    rows.extend(_matrix_quality_rows(r, dec83_state))

    # ── WORKFORCE (4 rows; mostly deferred wire-up) ─────────────────
    rows.extend(_matrix_workforce_rows(workforce_supply))
    # V1.5 stub for B1 JSA banding
    rows.append(_matrix_stub_row("sa2_jsa_vacancy_rate", "workforce",
        "SA2 JSA vacancy rate", "Pending V1.5 B1"))

    # ── COMMUNITY (8 demographic + top-N preview) ───────────────────
    rows.extend(_matrix_rows_from_position(catchment, [
        "sa2_nes_share", "sa2_atsi_share", "sa2_overseas_born_share",
        "sa2_single_parent_family_share", "sa2_parent_cohort_25_44_share",
        "sa2_partnered_25_44_share", "sa2_women_35_44_with_child_share",
        "sa2_women_25_34_with_child_share",
    ], "community", community_preview=community_profile))
    # Median household income lives in community (affordability lens)
    rows.extend(_matrix_rows_from_position(lab, ["sa2_median_household_income"], "community"))

    # ── EDUCATION (3 V1 + 5 banked sector breakdowns) ───────────────
    rows.extend(_matrix_rows_from_position(edu, [
        "sa2_school_count_total",
        "sa2_school_enrolment_total",
        "sa2_school_enrolment_govt_share",
    ], "education"))
    # 5 banked ACARA sector breakdowns — surface as Pending V1.5 stubs
    # until they're rendered in the matrix; the data IS in the DB but
    # POSITION_CARD_ORDER doesn't include them so they don't appear in
    # `position.education_infrastructure`. V1.5 follow-up to expose.
    for stub_metric, stub_label in [
        ("sa2_school_count_govt", "Govt school share by count"),
        ("sa2_school_count_catholic", "Catholic school share by count"),
        ("sa2_school_count_independent", "Independent school share by count"),
        ("sa2_school_enrolment_catholic_share", "Catholic enrolment share"),
        ("sa2_school_enrolment_independent_share", "Independent enrolment share"),
    ]:
        rows.append(_matrix_stub_row(stub_metric, "education", stub_label,
                                     "Pending V1.5 (banked from A4)"))

    # ── OPERATOR / GROUP IDENTITY (NEW DEC-83) ──────────────────────
    rows.extend(_matrix_operator_rows(r, dec83_state))

    # ── OPERATIONS (NEW DEC-83) ─────────────────────────────────────
    rows.extend(_matrix_operations_rows(r, dec83_state))

    # ── POPULATION (3 charted + 1 deferred) ─────────────────────────
    rows.extend(_matrix_rows_from_position(pop, [
        "sa2_under5_count", "sa2_total_population", "sa2_births_count",
        "sa2_under5_growth_5y",
    ], "population"))

    # ── LABOUR MARKET (8 minus median_household_income which moved to community) ──
    rows.extend(_matrix_rows_from_position(lab, [
        "sa2_unemployment_rate", "sa2_median_employee_income",
        "sa2_median_total_income", "sa2_lfp_persons", "sa2_lfp_females",
        "sa2_lfp_males", "jsa_vacancy_rate",
    ], "labour_market"))

    return rows


def _matrix_rows_from_position(card_dict: dict, metric_keys: list, category: str,
                                community_preview: Optional[dict] = None) -> list:
    """Flatten a list of position metric entries into matrix rows under a
    given category. community_preview (when provided) injects top-N preview
    text into the Commentary column for nes_share / overseas_born_share.
    """
    out = []
    for mk in metric_keys:
        e = card_dict.get(mk)
        if not e:
            continue
        # Sparkline = compressed last-N points from trajectory
        traj = e.get("trajectory") or []
        sparkline = traj[-12:] if len(traj) > 12 else traj  # last 12 points
        # Commentary preview: first sentence of intent_copy + community preview if applicable
        commentary = _truncate_sentence(e.get("intent_copy"))
        if community_preview:
            if mk == "sa2_nes_share":
                preview = _format_top_n(community_preview.get("language_at_home_top_n"), "Top languages")
                if preview:
                    commentary = f"{commentary} {preview}".strip() if commentary else preview
            elif mk == "sa2_overseas_born_share":
                preview = _format_top_n(community_preview.get("country_of_birth_top_n"), "Top countries")
                if preview:
                    commentary = f"{commentary} {preview}".strip() if commentary else preview
        confidence = e.get("confidence")
        v15_pending = None
        if confidence == "deferred":
            v15_pending = "Pending data wire-up"
        out.append({
            "category":         category,
            "metric":           mk,
            "display":          e.get("display"),
            "current_value":    e.get("raw_value"),
            "value_format":     e.get("value_format"),
            "period":           e.get("period_label") or (str(e.get("year")) if e.get("year") else None),
            "sparkline":        sparkline,
            "decile":           e.get("decile"),
            "cohort_n":         e.get("cohort_n"),
            "band":             e.get("band"),
            "industry_band":    e.get("industry_band_label") or e.get("band"),
            "signal":           e.get("industry_band_label") or e.get("band") or "—",
            "commentary":       commentary,
            "drawer_key":       f"metric:{mk}",
            "obs_der_com":      _badges_for(e),
            "v15_pending":      v15_pending,
            "confidence":       confidence,
        })
    return out


def _matrix_stub_row(metric: str, category: str, display: str, status_pill: str) -> dict:
    """V1.5 pending-ingest stub row per DEC-84 #10. The commentary line
    explains what the row will become once the ingest pass lands so the
    reader isn't left with an empty descriptor cell next to a status pill."""
    return {
        "category":      category,
        "metric":        metric,
        "display":       display,
        "current_value": None,
        "value_format":  None,
        "period":        None,
        "sparkline":     [],
        "decile":        None,
        "cohort_n":      None,
        "band":          None,
        "industry_band": None,
        "signal":        status_pill,
        "commentary":    f"Awaiting ingest ({status_pill}). This row will populate with a peer-banded value, decile, and trajectory once the data pass lands.",
        "drawer_key":    f"metric:{metric}",
        "obs_der_com":   [],
        "v15_pending":   status_pill,
        "confidence":    "deferred",
    }


def _seifa_decile_description(decile) -> Optional[str]:
    """Short plain-English descriptor for the SEIFA IRSD decile so the
    "5/10" tile in Layer 1 communicates what the score means without
    forcing the reader to look up the index. Index of Relative Socio-
    Economic Disadvantage — lower decile = more disadvantaged area;
    higher decile = more advantaged."""
    if decile is None:
        return None
    try:
        d = int(decile)
    except (TypeError, ValueError):
        return None
    table = {
        1:  "Bottom 10% — most disadvantaged",
        2:  "Lower band — disadvantaged",
        3:  "Lower-middle band",
        4:  "Lower-middle band",
        5:  "Mid-band — national midpoint",
        6:  "Upper-middle band",
        7:  "Upper-middle band",
        8:  "Upper band — advantaged",
        9:  "Highly advantaged",
        10: "Top 10% — most advantaged",
    }
    return table.get(d)


def _matrix_dec83_vacancy_row(dec83_state: dict) -> dict:
    vac = dec83_state.get("vacancy") or {}
    rows = vac.get("by_age_band") or []
    if not rows:
        return _matrix_stub_row("dec83_vacancy_posture", "supply",
                                "Vacancy posture (per age band)", "Pending DEC-83 ingest")
    has = sum(1 for x in rows if (x.get("vacancy_status") or "").startswith("has_") or x.get("vacancy_status") not in (None, "no_vacancies_published"))
    none = sum(1 for x in rows if x.get("vacancy_status") == "no_vacancies_published")
    if vac.get("all_no_vacancies_published"):
        signal = "All age bands: no vacancies published"
    elif has and not none:
        signal = "Vacancies posted across all age bands"
    else:
        signal = f"{has} with vacancies / {none} no vacancies posted"
    return {
        "category":      "supply",
        "metric":        "dec83_vacancy_posture",
        "display":       "Vacancy posture (per age band)",
        "current_value": f"{has} / {len(rows)}",
        "value_format":  "ratio_x_of_y",
        "period":        vac.get("latest_observed_at"),
        "sparkline":     [],
        "decile":        None,
        "cohort_n":      None,
        "band":          None,
        "industry_band": None,
        "signal":        signal,
        "commentary":    "Forward-looking demand-side signal: published vacancy state across age bands.",
        "drawer_key":    "dec83:vacancy",
        "obs_der_com":   [TAG_OBS],
        "v15_pending":   None,
        "confidence":    "live",
    }


def _matrix_pricing_rows(r: dict, dec83_state: dict) -> list:
    fees = (dec83_state.get("fees") or {}).get("by_age_band_session") or []
    if not fees:
        return [_matrix_stub_row(f"dec83_fee_{ab}", "pricing",
                                 f"Daily-rate full_day × {ab}", "Pending DEC-83 ingest")
                for ab in ("0-12m", "13-24m", "25-35m", "36m-preschool", "school-age")]
    sub_type = (r.get("service_sub_type") or "").upper()
    is_oshc = "OSHC" in sub_type or "OUT" in sub_type or "OUTSIDE" in sub_type
    out = []
    if is_oshc:
        # OSHC discriminator per DEC-84 #9: before/after_school × school-age
        for session in ("before_school", "after_school"):
            row = next((f for f in fees if f["age_band"] == "school-age" and f["session_type"] == session), None)
            out.append(_matrix_pricing_row(row, "school-age", session))
    else:
        # LDC / FDC / Preschool: full_day per age band
        for ab in ("0-12m", "13-24m", "25-35m", "36m-preschool", "school-age"):
            row = next((f for f in fees if f["age_band"] == ab and f["session_type"] == "full_day"), None)
            out.append(_matrix_pricing_row(row, ab, "full_day"))
    return out


def _matrix_pricing_row(fee_row: Optional[dict], age_band: str, session_type: str) -> dict:
    drawer_key = f"dec83:daily_rate"
    metric_key = f"dec83_fee_{session_type}_{age_band}"
    display = f"Daily rate {session_type} × {age_band}"
    if not fee_row:
        return _matrix_stub_row(metric_key, "pricing", display, "No fee published for this combo")
    return {
        "category":      "pricing",
        "metric":        metric_key,
        "display":       display,
        "current_value": fee_row.get("median_fee"),
        "value_format":  "currency_daily",
        "period":        fee_row.get("most_recent"),
        "sparkline":     [],   # full history in drawer
        "decile":        None, # peer cohort comparison: V1 deferred (small-n; surfaces in drawer)
        "cohort_n":      None,
        "band":          None,
        "industry_band": None,
        "signal":        f"${fee_row.get('median_fee'):.2f}/day" if fee_row.get('median_fee') is not None else "—",
        "commentary":    f"{fee_row.get('n_obs')} observation(s) in {fee_row.get('most_recent', '')[:4] if fee_row.get('most_recent') else 'latest year'}.",
        "drawer_key":    drawer_key,
        "obs_der_com":   [TAG_OBS],
        "v15_pending":   None,
        "confidence":    "live",
    }


def _matrix_quality_rows(r: dict, dec83_state: dict) -> list:
    out = []
    snap = dec83_state.get("regulatory_snapshot") or {}
    cond = dec83_state.get("conditions") or {}
    enf = dec83_state.get("enforcement") or {}
    nqs_overall = (r.get("overall_nqs_rating") or "").strip() or None

    # NQS overall + prev (pill ladder, no decile/sparkline)
    out.append({
        "category": "quality", "metric": "dec83_nqs_overall",
        "display": "NQS overall rating",
        "current_value": nqs_overall, "value_format": "text",
        "period": r.get("rating_issued_date"),
        "sparkline": [], "decile": None, "cohort_n": None,
        "band": None, "industry_band": None,
        "signal": _signal_summary_quality(nqs_overall, snap.get("nqs_prev_overall")),
        "commentary": "ACECQA quarterly assessment; trajectory in drawer.",
        "drawer_key": "dec83:nqs", "obs_der_com": [TAG_OBS],
        "v15_pending": None, "confidence": "live" if nqs_overall else "unavailable",
    })
    # Active conditions count (only render if substrate present)
    out.append({
        "category": "quality", "metric": "dec83_active_conditions",
        "display": "Active conditions",
        "current_value": cond.get("active_count") or 0,
        "value_format": "int",
        "period": None, "sparkline": [], "decile": None, "cohort_n": None,
        "band": None, "industry_band": None,
        "signal": (f"{cond.get('active_count') or 0} active" + (" (see detail)" if (cond.get('active_count') or 0) > 0 else "")),
        "commentary": "Service-level + provider-level conditions on this approval.",
        "drawer_key": "dec83:conditions", "obs_der_com": [TAG_OBS],
        "v15_pending": None,
        "confidence": "live" if cond.get("rows") is not None else "unavailable",
    })
    # Enforcement events 24mo
    out.append({
        "category": "quality", "metric": "dec83_enforcement_24mo",
        "display": "Enforcement events (24mo)",
        "current_value": enf.get("recent_24mo_count") or 0,
        "value_format": "int",
        "period": None, "sparkline": [], "decile": None, "cohort_n": None,
        "band": None, "industry_band": None,
        "signal": f"{enf.get('recent_24mo_count') or 0} recent / {enf.get('total_count') or 0} total",
        "commentary": "ACECQA enforcement actions (compliance notices etc.).",
        "drawer_key": "dec83:enforcement", "obs_der_com": [TAG_OBS],
        "v15_pending": None,
        "confidence": "live" if enf.get("rows") is not None else "unavailable",
    })
    # CCS revoked flag (only if 1)
    if snap.get("ccs_revoked_by_ea") is True:
        out.append({
            "category": "quality", "metric": "dec83_ccs_revoked",
            "display": "CCS revoked by EA",
            "current_value": True, "value_format": "bool",
            "period": snap.get("snapshot_date"),
            "sparkline": [], "decile": None, "cohort_n": None,
            "band": None, "industry_band": None,
            "signal": "🔴 Active",
            "commentary": "Live credit-direct flag: CCS approval revoked by Education Authority.",
            "drawer_key": "dec83:nqs", "obs_der_com": [TAG_OBS],
            "v15_pending": None, "confidence": "live",
        })
    # NQS area breakdown (V1.5 pending — nqs_history check would surface area cols)
    out.append(_matrix_stub_row("dec83_nqs_area_breakdown", "quality",
        "NQS 7-area breakdown", "Pending nqs_history area-col surface"))
    # Last regulatory visit
    out.append({
        "category": "quality", "metric": "dec83_last_visit",
        "display": "Last regulatory visit",
        "current_value": snap.get("last_regulatory_visit"),
        "value_format": "date",
        "period": None, "sparkline": [], "decile": None, "cohort_n": None,
        "band": None, "industry_band": None,
        "signal": snap.get("last_regulatory_visit") or "—",
        "commentary": "Most recent ACECQA / Regulator visit on record.",
        "drawer_key": "dec83:nqs", "obs_der_com": [TAG_OBS],
        "v15_pending": None,
        "confidence": "live" if snap.get("last_regulatory_visit") else "unavailable",
    })
    return out


def _matrix_workforce_rows(workforce_supply: dict) -> list:
    """Convert the existing workforce_supply rows into matrix-format rows."""
    out = []
    rows = workforce_supply.get("rows") or workforce_supply.get("supply", []) or []
    if isinstance(workforce_supply, dict) and not rows:
        # Fall back: workforce_supply itself may be the dict-of-rows shape per current builder
        for k in ("jsa_ivi_4211_child_carer", "jsa_ivi_2411_ect", "ecec_award_rates", "three_day_guarantee"):
            entry = workforce_supply.get(k)
            if entry is not None:
                rows.append(entry)
    for entry in rows:
        if not isinstance(entry, dict):
            continue
        # JSA IVI rows carry r.latest = {period, value}; Three-Day Guarantee
        # carries r.fact = "policy statement". v3.31's _renderWorkforceSupplyRow
        # surfaces these as the value column — matrix must do the same to
        # avoid a regression where Workforce rows render "—".
        latest = entry.get("latest") or {}
        current_value = (
            entry.get("raw_value")
            or entry.get("value")
            or latest.get("value")
            or entry.get("fact")
        )
        period = (
            entry.get("period_label")
            or entry.get("period")
            or latest.get("period")
        )
        # Three-Day Guarantee's "value" is a sentence, format as text rather
        # than numeric so the renderer doesn't try to apply percent/int formatting.
        value_format = entry.get("value_format")
        if value_format is None and entry.get("fact"):
            value_format = "text"
        # 3-year trend % for JSA IVI rows — Patrick 2026-05-12: "difficult
        # to know if those numbers... are historically high or low. Probably
        # changed in the last three years in percentages, could be one way
        # of doing it." Appended to commentary so the reader sees direction
        # + magnitude of change without a chart.
        traj = entry.get("trajectory") or []
        trend3y = None
        if len(traj) >= 36:
            try:
                latest_v = float(traj[-1].get("value"))
                # 36 monthly points back = 3 years; clip to start if shorter
                back_idx = max(0, len(traj) - 37)
                back_v = float(traj[back_idx].get("value"))
                if back_v > 0:
                    trend3y = ((latest_v - back_v) / back_v) * 100.0
            except (TypeError, ValueError):
                trend3y = None
        # Trend now surfaces in the value column below the period
        # (relocated 2026-05-12 per Patrick) — keeps the commentary
        # column focused on intent. trend3y_pct on the row payload is
        # consumed by the frontend renderer.
        commentary = _truncate_sentence(entry.get("intent_copy")) or ""
        out.append({
            "category":      "workforce",
            "metric":        entry.get("metric"),
            "display":       entry.get("display"),
            "current_value": current_value,
            "value_format":  value_format,
            "period":        period,
            "sparkline":     (entry.get("trajectory") or [])[-12:],
            "decile":        None,
            "cohort_n":      None,
            "band":          None,
            "industry_band": None,
            "signal":        entry.get("scope_stamp") or "—",
            "commentary":    commentary,
            "drawer_key":    f"metric:{entry.get('metric')}",
            "obs_der_com":   [TAG_OBS],
            "v15_pending":   ("Pending V1.5 A7 wire-up"
                              if entry.get("confidence") == "deferred"
                              else None),
            "confidence":    entry.get("confidence"),
            "status_note":   entry.get("status_note"),
            "trend3y_pct":   trend3y,
        })
    return out


def _matrix_operator_rows(r: dict, dec83_state: dict) -> list:
    out = []
    lp = dec83_state.get("large_provider")
    snap = dec83_state.get("regulatory_snapshot") or {}
    if lp:
        out.append({
            "category":      "operator",
            "metric":        "dec83_large_provider",
            "display":       "Operator group affiliation",
            "current_value": lp.get("name"),
            "value_format":  "text",
            "period":        lp.get("last_observed_at"),
            "sparkline":     [], "decile": None, "cohort_n": None,
            "band":          None, "industry_band": None,
            "signal":        f"{lp.get('provider_count', 0)} provider{'s' if (lp.get('provider_count', 0) != 1) else ''} / {lp.get('service_count', 0)} service{'s' if (lp.get('service_count', 0) != 1) else ''}",
            "commentary":    "Starting Blocks-published operator-group identity (DEC-83 substrate).",
            "drawer_key":    "dec83:operator_group",
            "obs_der_com":   [TAG_OBS],
            "v15_pending":   None,
            "confidence":    "live",
        })
    # Provider state
    if snap:
        prov_status = snap.get("provider_status")
        out.append({
            "category":      "operator",
            "metric":        "dec83_provider_state",
            "display":       "Provider state",
            "current_value": prov_status,
            "value_format":  "text",
            "period":        snap.get("provider_approval_date"),
            "sparkline":     [], "decile": None, "cohort_n": None,
            "band":          None, "industry_band": None,
            "signal":        prov_status or "—",
            "commentary":    f"Approval date: {snap.get('provider_approval_date') or '—'}; CCS revoked: {snap.get('provider_ccs_revoked_by_ea')}.",
            "drawer_key":    "dec83:operator_group",
            "obs_der_com":   [TAG_OBS],
            "v15_pending":   None,
            "confidence":    "live" if prov_status else "unavailable",
        })
    return out


def _matrix_operations_rows(r: dict, dec83_state: dict) -> list:
    snap = dec83_state.get("regulatory_snapshot") or {}
    out = []
    # Operating hours summary
    out.append({
        "category":      "operations",
        "metric":        "dec83_hours_summary",
        "display":       "Operating hours",
        "current_value": snap.get("hours_summary"),
        "value_format":  "text",
        "period":        snap.get("snapshot_date"),
        "sparkline":     [], "decile": None, "cohort_n": None,
        "band":          None, "industry_band": None,
        "signal":        snap.get("hours_summary") or "—",
        "commentary":    "Per-day hours in drawer.",
        "drawer_key":    "dec83:operations",
        "obs_der_com":   [TAG_OBS],
        "v15_pending":   None,
        "confidence":    "live" if snap.get("hours_summary") else "unavailable",
    })
    # Service status (open/temp/closed)
    if snap.get("is_closed") is True:
        status = "Closed"
    elif snap.get("temporarily_closed") is True:
        status = "Temporarily closed"
    elif snap:
        status = "Open"
    else:
        status = None
    out.append({
        "category":      "operations",
        "metric":        "dec83_service_status",
        "display":       "Service status",
        "current_value": status,
        "value_format":  "text",
        "period":        snap.get("snapshot_date"),
        "sparkline":     [], "decile": None, "cohort_n": None,
        "band":          None, "industry_band": None,
        "signal":        status or "—",
        "commentary":    None,
        "drawer_key":    "dec83:operations",
        "obs_der_com":   [TAG_OBS],
        "v15_pending":   None,
        "confidence":    "live" if status else "unavailable",
    })
    # CCS data received
    out.append({
        "category":      "operations",
        "metric":        "dec83_ccs_data_received",
        "display":       "CCS data received",
        "current_value": snap.get("ccs_data_received"),
        "value_format":  "bool",
        "period":        snap.get("snapshot_date"),
        "sparkline":     [], "decile": None, "cohort_n": None,
        "band":          None, "industry_band": None,
        "signal":        "Yes" if snap.get("ccs_data_received") is True else ("No" if snap.get("ccs_data_received") is False else "—"),
        "commentary":    None,
        "drawer_key":    "dec83:operations",
        "obs_der_com":   [TAG_OBS],
        "v15_pending":   None,
        "confidence":    "live" if snap else "unavailable",
    })
    return out


def _badges_for(entry: dict) -> list:
    """Return list of OBS/DER/COM tags applicable to this position entry."""
    tags = [TAG_OBS]
    if entry.get("uses_calibration") or entry.get("calibrated_rate") is not None:
        tags.append(TAG_DER)
    if entry.get("band_copy"):
        tags.append(TAG_COM)
    return tags


def _format_top_n(top_n_list: Optional[list], label_prefix: str) -> Optional[str]:
    """Format top-3 list for matrix Commentary preview per DEC-84 #6.
    Includes share_pct alongside each name so the reader sees the actual
    distribution, e.g. "Mandarin 7.2% · Cantonese 2.2% · Indonesian 2.1%"."""
    if not top_n_list:
        return None
    items = []
    for item in (top_n_list or [])[:3]:
        name = item.get("country") or item.get("language")
        if not name:
            continue
        share = item.get("share_pct")
        if share is not None:
            items.append(f"{name} {float(share):.1f}%")
        else:
            items.append(name)
    if not items:
        return None
    return f"{label_prefix}: {' · '.join(items)}"


def _truncate_sentence(text: Optional[str]) -> Optional[str]:
    """First ~2 sentences (or first 240 chars) for matrix Commentary column.
    Widened from 120 chars in Turn 1 of Centre v2 rebuild — descriptor column
    grew when 24px sparklines were retired."""
    if not text:
        return None
    s = str(text).strip()
    if len(s) <= 240:
        return s
    # Try to break on the 2nd sentence
    cut = s[:240]
    for sep in (". ", "; "):
        i = cut.rfind(sep)
        if i > 80:
            return s[:i + 1]
    return cut.rstrip() + "…"


# ─────────────────────────────────────────────────────────────────────
# Layer 6 — Detail side-drawer (DEC-84 #6)
# ─────────────────────────────────────────────────────────────────────


def _build_drawer(r: dict, position: dict, workforce_supply: dict,
                  community_profile: dict, dec83_state: dict) -> dict:
    """DEC-83 special drawer content keyed by drawer key. Position-derived
    drawers (`metric:<key>`) are rendered by looking up position.<card>.<metric>
    in the renderer; no payload duplication. Only DEC-83-specific drawers
    surface here per DEC-84 #6.
    """
    out: dict = {}

    # daily_rate drawer — full age × session × year grid
    fees = (dec83_state.get("fees") or {})
    if fees.get("by_age_band_session"):
        out["dec83:daily_rate"] = {
            "title":    "Daily rate detail",
            "year":     fees.get("year"),
            "as_of":    fees.get("latest_as_of_date"),
            "grid":     fees.get("by_age_band_session"),  # full age×session grid latest year
            "methodology": (
                "Median fee in $AUD per (age band × session type) for the latest year. "
                "Source: Starting Blocks per-service fee schedules (DEC-83 Commercial Layer V1). "
                "Peer cohort comparison surfaces in Layer 5 matrix; full historical series available "
                "via service_fee table for V2 trajectory render."
            ),
        }

    # conditions drawer — full text per condition
    cond = dec83_state.get("conditions") or {}
    if cond.get("rows"):
        out["dec83:conditions"] = {
            "title":          "Conditions on approval",
            "service_count":  cond.get("service_count", 0),
            "provider_count": cond.get("provider_count", 0),
            "active_count":   cond.get("active_count", 0),
            "rows":           cond.get("rows", []),
            "methodology": (
                "Conditions imposed on this service or its provider's approval. "
                "Source: Starting Blocks (DEC-83 substrate). 'Active' indicates the condition was "
                "still observed in the latest refresh; reconciled across snapshots via condition_id."
            ),
        }

    # enforcement drawer — chronological event log
    enf = dec83_state.get("enforcement") or {}
    if enf.get("rows"):
        out["dec83:enforcement"] = {
            "title":             "Enforcement event log",
            "total_count":       enf.get("total_count", 0),
            "recent_24mo_count": enf.get("recent_24mo_count", 0),
            "events":            enf.get("rows", []),
            "methodology": (
                "ACECQA enforcement actions on this service. Each row shows action_type / event_date / regulator. "
                "Source: regulatory_events table (DEC-83 reused scaffold)."
            ),
        }

    # operator_group drawer — chain detail
    lp = dec83_state.get("large_provider")
    if lp:
        out["dec83:operator_group"] = {
            "title":             f"Operator group: {lp.get('name')}",
            "large_provider_id": lp.get("large_provider_id"),
            "name":              lp.get("name"),
            "slug":              lp.get("slug"),
            "first_observed_at": lp.get("first_observed_at"),
            "last_observed_at":  lp.get("last_observed_at"),
            "provider_count":    lp.get("provider_count", 0),
            "service_count":     lp.get("service_count", 0),
            "methodology": (
                "Operator-group identity from Starting Blocks (DEC-83). The chain links N provider entities "
                "to M services as one operator group. Future Group page (OI-NEW-17) provides portfolio-level lens."
            ),
        }

    # nqs drawer — overall rating + prev + 7-area (when nqs_history populated)
    snap = dec83_state.get("regulatory_snapshot") or {}
    out["dec83:nqs"] = {
        "title":             "NQS detail",
        "overall_rating":    r.get("overall_nqs_rating"),
        "rating_issued_date": r.get("rating_issued_date"),
        "prev_overall":      snap.get("nqs_prev_overall"),
        "prev_issued":       snap.get("nqs_prev_issued"),
        "ccs_revoked_by_ea": snap.get("ccs_revoked_by_ea"),
        "last_regulatory_visit": snap.get("last_regulatory_visit"),
        "methodology": (
            "NQS overall rating per ACECQA quarterly assessment. Rating ladder: Provisional → "
            "Working Towards NQS → Meeting NQS → Exceeding NQS → Excellent. Prior rating + issue date "
            "from Starting Blocks regulatory snapshot. 7-area breakdown surfaces from nqs_history when "
            "area cols are populated (V1.5 follow-up)."
        ),
    }

    # vacancy drawer — age-band breakdown + sentinel methodology
    vac = dec83_state.get("vacancy") or {}
    if vac.get("by_age_band"):
        out["dec83:vacancy"] = {
            "title":              "Vacancy posture",
            "latest_observed_at": vac.get("latest_observed_at"),
            "all_no_vacancies_published": vac.get("all_no_vacancies_published"),
            "by_age_band":        vac.get("by_age_band"),
            "methodology": (
                "Vacancy snapshots from Starting Blocks (DEC-83). 'no_vacancies_published' is a sentinel "
                "state — it does NOT guarantee the service is full; it indicates no published vacancy detail "
                "at this snapshot. Longitudinal history will accrue from weekly refresh cadence (DEC-83 #6)."
            ),
        }

    # operations drawer — full per-day hours + provider sub-block + contact
    out["dec83:operations"] = {
        "title":              "Operations detail",
        "snapshot_date":      snap.get("snapshot_date"),
        "is_closed":          snap.get("is_closed"),
        "temporarily_closed": snap.get("temporarily_closed"),
        "ccs_data_received":  snap.get("ccs_data_received"),
        "hours_by_day":       snap.get("hours_by_day"),
        "hours_summary":      snap.get("hours_summary"),
        "website_url":        snap.get("website_url"),
        "phone":              snap.get("phone"),
        "email":              snap.get("email"),
        "methodology": (
            "Operating hours, contact, and operational status per Starting Blocks regulatory snapshot. "
            "Hours are point-in-time at last refresh; service may publish updates between snapshots."
        ),
    }

    # top_n_cob + top_n_lang drawers (community profile detail with methodology)
    if community_profile and community_profile.get("country_of_birth_top_n"):
        out["metric:sa2_overseas_born_share"] = {
            "title":    "Country-of-birth detail",
            "rows":     community_profile.get("country_of_birth_top_n"),
            "methodology": "Top-3 country of birth from Census 2021 TSP T08, share of total resident population in this SA2.",
        }
    if community_profile and community_profile.get("language_at_home_top_n"):
        out["metric:sa2_nes_share"] = {
            "title":    "Language-at-home detail",
            "rows":     community_profile.get("language_at_home_top_n"),
            "methodology": "Top-3 language at home from Census 2021 TSP T10A+T10B, share of total population in this SA2.",
        }

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

        # Approved-places peer cohort within the same SA2, filtered to the
        # subject's comparable subtype (Patrick 2026-05-12: Layer 1 should
        # compare like-for-like only). Subject centre included; renderer
        # drops bar when cohort.meaningful=False.
        approved_places_cohort = _cohort_for_places(
            conn, r.get("sa2_code"), r.get("service_sub_type")
        )

        # ACECQA service-offerings breakdown (Patrick 2026-05-12) — pull
        # latest nqs_history row per service_approval_number for the five
        # service-type flags. "Other" isn't in our DB; renderer surfaces
        # it as not-captured. Defensive try/except so a missing column
        # doesn't break the payload.
        service_offerings = {
            "preschool_in_school":   None,
            "preschool_standalone":  None,
            "oshc_before_school":    None,
            "oshc_after_school":     None,
            "oshc_vacation_care":    None,
            "other":                 None,   # not in nqs_history
            "snapshot_quarter":      None,
            "source":                "ACECQA NQAITS quarterly snapshot",
            "tag":                   TAG_OBS,
        }
        try:
            san = r.get("service_approval_number")
            if san:
                offering_row = conn.execute(
                    """
                    SELECT quarter, preschool_in_school, preschool_standalone,
                           oshc_before_school, oshc_after_school, oshc_vacation_care
                      FROM nqs_history
                     WHERE service_approval_number = ?
                     ORDER BY quarter DESC
                     LIMIT 1
                    """,
                    (san,),
                ).fetchone()
                if offering_row:
                    service_offerings["snapshot_quarter"]     = offering_row[0]
                    service_offerings["preschool_in_school"]  = offering_row[1]
                    service_offerings["preschool_standalone"] = offering_row[2]
                    service_offerings["oshc_before_school"]   = offering_row[3]
                    service_offerings["oshc_after_school"]    = offering_row[4]
                    service_offerings["oshc_vacation_care"]   = offering_row[5]
        except sqlite3.OperationalError:
            pass

        places = {
            "approved_places": {
                "tag": TAG_OBS,
                "value": r.get("approved_places"),
                "cohort": approved_places_cohort,
            },
            "service_sub_type": subtype,
            "long_day_care_flag": bool(r.get("long_day_care")) if r.get("long_day_care") is not None else None,
            "service_offerings": service_offerings,
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
                "description": _seifa_decile_description(r.get("seifa_decile")),
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
        position = _layer3_position(conn, r.get("sa2_code"), r.get("service_sub_type"))

        # Propagate centre_events from catchment metrics onto population
        # entries so the v2 chart 5 (under-5 + births) and the inline-
        # expand on population matrix rows show the same supply-change
        # overlay (vertical dashed lines) that the catchment charts do.
        # Events are per-SA2-per-subtype; one shared array applies across
        # all population entries since they share the SA2 + subtype scope.
        _catch = position.get("catchment_position") or {}
        _shared_events = None
        for _m in ("sa2_supply_ratio", "sa2_demand_supply",
                   "sa2_child_to_place", "sa2_adjusted_demand"):
            _e = _catch.get(_m)
            if isinstance(_e, dict) and _e.get("centre_events"):
                _shared_events = _e["centre_events"]
                break
        if _shared_events:
            _pop = position.get("population") or {}
            for _k, _entry in _pop.items():
                if isinstance(_entry, dict) and "centre_events" not in _entry:
                    _entry["centre_events"] = _shared_events

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

        # --- COMMUNITY PROFILE (Layer 4.4 A10/C8) ---
        community_profile = _build_community_profile(conn, r.get("sa2_code"))

        # --- DEC-83 SUBSTRATE (Centre v2 Layer 1 / 2 / 5 / 6 inputs) ---
        # Single fetch; used by all three v2 builders below + Layer 1 enrichments.
        dec83_state = _build_dec83_state(conn, service_id)

        # Daily-rate peer cohort within the same SA2 (Bundle B #1). Attached
        # to dec83.fees as cohort_by_age_band_session; renderer uses the
        # headline pair cell (full_day × 36m-preschool default) for the
        # Layer 1 daily-rate tile range bar and per-row matrix bars.
        try:
            dec83_state["fees"]["cohort_by_age_band_session"] = (
                _cohort_for_daily_rate(
                    conn, r.get("sa2_code"), r.get("service_sub_type")
                )
            )
        except KeyError:
            # _build_dec83_state always populates fees as a dict; this guards
            # against a future shape change without crashing payload assembly.
            pass

        # --- PROVIDER APPROVAL SCALE (operator-level rollup) ---
        # Count of OTHER active services operating under the same ACECQA
        # provider approval number. Patrick correction 2026-05-12:
        # service_approval_number is 1:1 with a service (each service has
        # its own SAN); the meaningful operator-scale signal is the
        # provider approval (PR-XXXX) — one approved provider can run
        # many services. Surfaced in Layer 5 Operations matrix row.
        pan = r.get("provider_approval_number")
        shared_pan_others = 0
        shared_pan_names: list = []
        if pan:
            try:
                shared_rows = conn.execute(
                    """
                    SELECT service_id, service_name
                      FROM services
                     WHERE provider_approval_number = ?
                       AND service_id != ?
                       AND COALESCE(is_active, 1) = 1
                    """,
                    (pan, service_id),
                ).fetchall()
                shared_pan_others = len(shared_rows)
                shared_pan_names = [
                    {"service_id": x[0], "service_name": x[1]}
                    for x in shared_rows
                ]
            except sqlite3.OperationalError:
                pass
        provider_scale = {
            "tag":           TAG_OBS,
            "provider_approval_number": pan,
            "other_count":   shared_pan_others,
            "other_services": shared_pan_names,
        }

        # --- LEARNING ENVIRONMENT additions (Bundle 2-prep 2026-05-12) ---
        # School enrolment 3y trend (ECEC demand leading indicator) +
        # asymmetric cross-subtype care counts (LDC subject sees OSHC
        # competition / transition; OSHC subject sees LDC feeder pipeline).
        school_enrolment_trend = _compute_school_enrolment_trend(
            conn, r.get("sa2_code")
        )
        # Supply-change overlay events for the school enrolment chart —
        # Patrick 2026-05-12: "supply change horizontal lines there as
        # well for new education environments arriving, OSH or the
        # others." Same payload shape as catchment centre_events so the
        # existing _kintellEventAnnotation plugin can render it.
        school_enrolment_trend["centre_events"] = (
            _compute_education_supply_events(conn, r.get("sa2_code"))
        )
        cross_subtype_competition = _compute_cross_subtype_competition(
            conn, r.get("sa2_code"), r.get("service_sub_type")
        )
        schools_in_catchment = _build_schools_in_catchment(
            conn, r.get("sa2_code")
        )

        # --- COMPETITIVE POSITIONING (Layer 1.5 panel) ---
        # Every centre in the same SA2 on a daily-fee × NQS axis with
        # subject centre emphasised. Patrick 2026-05-12 framing.
        competitive_positioning = _build_competitive_positioning(
            conn, service_id, r.get("sa2_code"), r.get("service_sub_type")
        )

        # --- CCS COVERAGE RATIO (catchment affordability signal) ---
        # Estimated % of households in catchment receiving the CCS full
        # benefit; derived from SA2 median weekly household income via a
        # lognormal model. Rendered in Layer 1 (percentage tile) and Layer 5
        # matrix Pricing & Fees category per Patrick's framing 2026-05-13.
        _hh_inc_entry = (position.get("labour_market") or {}).get("sa2_median_household_income") or {}
        _median_weekly_hh = _hh_inc_entry.get("raw_value")
        ccs_coverage = _compute_ccs_coverage(_median_weekly_hh)

        # --- CENTRE V2 BUILDERS (DEC-84 — payload schema v7) ---
        # Additive overlay (DEC-11): v6 keys preserved unchanged; v7 adds
        # dec83 / executive / matrix / drawer top-level keys. Existing
        # /centres/{id} renderer continues to consume v6; new
        # /centre_v2/{id} renderer (centre_v2.html, future) consumes v7.
        executive_block = _build_executive(r, position, dec83_state, community_profile)
        matrix_block = _build_matrix(r, position, workforce_supply, community_profile, dec83_state)
        drawer_block = _build_drawer(r, position, workforce_supply, community_profile, dec83_state)

        # --- ASSEMBLE ---
        payload = {
            "schema_version": "centre_payload_v7",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "header": header,
            "nqs": nqs,
            "places": places,
            "catchment": catchment,
            "position": position,
            "workforce_supply": workforce_supply,
            "community_profile": community_profile,
            "qa_scores": qa_scores,
            "tenure": tenure,
            "commentary": _commentary_lines(header, nqs, places, tenure, subtype),
            # Centre v2 (DEC-84) — additive top-level keys
            "dec83":         dec83_state,
            "executive":     executive_block,
            "matrix":        matrix_block,
            "drawer":        drawer_block,
            "ccs_coverage":              ccs_coverage,
            "provider_scale":            provider_scale,
            "competitive_positioning":   competitive_positioning,
            "school_enrolment_trend":    school_enrolment_trend,
            "cross_subtype_competition": cross_subtype_competition,
            "schools_in_catchment":      schools_in_catchment,
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


def _build_community_profile(conn, sa2_code: Optional[str]) -> dict:
    """Layer 4.4 A10/C8 — top-3 country-of-birth + top-3 language-at-home
    context for the centre's SA2.

    Reads from `abs_sa2_country_of_birth_top_n` and
    `abs_sa2_language_at_home_top_n` (2021 census only). Returns:
      { "country_of_birth_top_n":  [ {rank, country,  count, share_pct}, ... ],
        "language_at_home_top_n":  [ {rank, language, count, share_pct}, ... ] }.
    Empty lists when a table is missing or the SA2 has no rows (P-2 silent
    absence). Display-only context per design D-A2.
    """
    out = {"country_of_birth_top_n": [], "language_at_home_top_n": []}
    if not sa2_code:
        return out
    try:
        cob_rows = conn.execute(
            "SELECT rank, country_name, count, share_pct "
            "FROM abs_sa2_country_of_birth_top_n "
            "WHERE sa2_code = ? AND census_year = 2021 "
            "ORDER BY rank ASC",
            (str(sa2_code),),
        ).fetchall()
        out["country_of_birth_top_n"] = [
            {
                "rank": int(r[0]),
                "country": r[1],
                "count": int(r[2]) if r[2] is not None else None,
                "share_pct": float(r[3]) if r[3] is not None else None,
            }
            for r in cob_rows
        ]
    except sqlite3.OperationalError:
        pass
    try:
        lang_rows = conn.execute(
            "SELECT rank, language, count, share_pct "
            "FROM abs_sa2_language_at_home_top_n "
            "WHERE sa2_code = ? AND census_year = 2021 "
            "ORDER BY rank ASC",
            (str(sa2_code),),
        ).fetchall()
        out["language_at_home_top_n"] = [
            {
                "rank": int(r[0]),
                "language": r[1],
                "count": int(r[2]) if r[2] is not None else None,
                "share_pct": float(r[3]) if r[3] is not None else None,
            }
            for r in lang_rows
        ]
    except sqlite3.OperationalError:
        pass
    return out


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
