# Centre v2 precedent audit — process for preventing regressions

*Created 2026-05-12 after Patrick's repeated regression complaints. Lives alongside `recon/centre_v2_design.md`. Run as a checklist before AND after every iteration on `docs/centre_v2.html` + `centre_page.py`.*

## Why this exists

The v2 build is line-by-line iterative. Each iteration accidentally drops functionality from previous iterations because changes to chart configs, payload shapes, and matrix builders have spillover effects. Patrick has called this out twice now:
- "we seem to be going a little bit three steps forward, two and a half back" (Bundle B + Option B)
- "you've now dropped off [X]" (post-shared-SAN bundle)
- "is there a chart for this?" + "is there a result that needs to be printed on this first page?" (post-shared-SAN bundle)

The rule (`feedback_no_iteration_regression.md`) is captured in memory. This doc is the concrete *process* that operationalises it.

## Before any code edit

Run this checklist for every surface the edit touches:

1. **Identify the surface(s) being changed** — Layer 1 tile, Layer 2 tile, Layer 3 chart config, Layer 4 chart panel, Layer 5 matrix row, Layer 6 drawer, payload key, helper function.
2. **Grep v3.31 `docs/centre.html` for the equivalent surface**. List every analytical element it renders. Treat that list as the floor.
3. **Grep current `docs/centre_v2.html` for the same surface**. Confirm each v3.31 element has a v2 equivalent. Note any pre-existing gaps.
4. **Identify the change being scoped**. Anything not on that list must survive untouched.

## After any code edit

1. **Re-render the touched surface in the preview**.
2. **Walk the v3.31 element list**. Confirm each element is still present, with values populating where v3.31 had values.
3. **Click into inline-row-click expands for affected matrix rows** if any. Confirm trajectory chart + register render.
4. **Hover the chart** to confirm the readout populates with both lines (value + running-%).
5. **Open drawers** that the change might have touched.
6. **If a regression is found, fix before moving on** — do not "fix forward" in the next bundle.

## Layer-specific element lists (the floor)

### Layer 1 — Header
- Service name (h2)
- Address (one line, suburb-state-postcode)
- Operator deep-link + ownership badge + brand badge + entity attribution
- Large-provider chip (when DEC-83 substrate present)
- Identity tiles row: Approved places · Daily rate · CCS coverage · Subtype · SEIFA decile · Remoteness · Tenure · Kinder (each tile carries label + value + descriptors as built up across iterations)
- Tag chips strip (acecqa SAN / abr legal name / google search lookup)
- Hours summary (when DEC-83 reg snapshot present)
- Contact strip (website / phone / email)
- Explicit Catchment SA2 line

### Layer 1.5 — Competitive positioning (NEW 2026-05-12; refined 2026-05-12 post-Patrick-spec)
Lives between L1 identity row and L2 intelligence bar. SVG bubble chart on daily-fee × NQS axis, plus 3-column commercial-positioning commentary block below.

**Panel header:**
- Title: "Competitive position — {SA2 name}"
- Subtitle: "{Comparable-group label} in SA2 {code}" — e.g. "Comparable long day care centres (0–5 years) in SA2 117031646"

**Methodology line (between header and chart, accent-purple left-border):**
- Lead label "Methodology"
- Body: "{comparable_group_label} only. We compare centres on the same care type to ensure like-for-like market analysis. Daily fee = {session_label} (10+ hours). Bubble size = approved places. Quality = current NQF rating."

**Toolbar:** retired post-refinement. Single curated default view (Patrick spec 2026-05-12). Underlying toggle code preserved but not surfaced.

**SVG chart canvas (320px standard):**
- 5 horizontal NQS bands at opacity 0.10 (darkened from 0.06 for better bubble contrast); muted institutional palette: Excellent #2d6a4f / Exceeding #52b788 / Meeting #5a8aa6 / Working Towards #e07a4f / Significant Improvement #bf4040
- Band labels left of chart
- X-axis daily-fee ticks at $10/$20 intervals + axis title showing session label
- Market average dashed vertical line (always on) at the cohort fee mean, labelled "Market average (SA2) $X"
- CCS hourly-cap × 10h reference line at ~$137 (dashed vertical, labelled)
- Bubbles per centre: r ∝ √places (capped 4.5–12px, reduced from 5–14 per refinement), fill = NQS colour, jittered ±7px within band when ≥2 share the band
- Subject centre: 1.5× larger, accent purple fill, 2px white outline, opacity 0.95
- All non-subject bubbles at opacity 0.78
- Bubble hover: stroke-width bumps; click → navigate to that centre's centre_v2 page

**Hover popover:** positioned near cursor; centre name (bold) + fee + places + NQS + last assessed + operator group (when present).

**Hover strip below chart (visible only on hover):**
- Header "vs {hovered centre name}:" + deltas vs subject (±$X fee · ±N places · same/higher/lower NQS · assessed Xmo more recently/earlier)
- Inferential read of the comparison (7 mappings)

**3-column commercial-positioning commentary (below hover strip, always visible):**
- **Column 1 — Positioning:**
  - Heading (one of: Premium positioning / Quality-led value positioning / Pricing outlier / Quality-led positioning / Larger-scale provider / Boutique operator / Mid-market positioning / Value positioning / Budget positioning) selected from price × quality × scale tier combo
  - 1-line summary
  - 3 supporting bullets with icons (◆ ▲ ●), each: short headline + optional caveat
- **Column 2 — Key position at a glance:**
  - 4 quantified facts vs cohort: fee vs market avg with absolute and % delta · quality tier vs cohort with "% in top N" framing · scale tier with "larger/smaller than X% of comparable centres" · assessment recency
  - Each row: icon glyph + "Above market average / Top quality tier / Larger scale offering / Recent assessment" headline + supporting line
- **Column 3 — Market context:**
  - 3 contextual reads from cohort distribution: quality-fee correlation in this SA2 · regulatory tail-risk count · CCS efficiency distribution (how many of the cohort sit above/below the CCS hourly-cap × 10h)
  - Each row: icon glyph (⚖ ✓ %) + headline + supporting line

**Coverage:** gated by DEC-83 pilot SA2 footprint; non-pilot SA2s render placeholder with methodology line preserved.

**Subtype filtering (Patrick refinement 2026-05-12):**
- Subject's subtype determines comparable cohort group:
  - LDC + Preschool clustered → "Comparable long day care centres (0–5 years)"
  - OSHC → "Outside School Hours Care (school-age)"
  - FDC → "Family Day Care (in-home, all ages)"
- Headline pair derived from subject subtype (LDC/Preschool/FDC → full_day × 36m-preschool; OSHC → before_school × school-age)
- Subject service excluded only if it has no fee in `service_fee` for the headline pair

### Layer 5 — Bundle 1 polish (2026-05-12)
- **Category order updated**: `demand → supply → population → pricing → community → labour_market → education → workforce → quality → operator → operations`. Population moved between Supply and Pricing & Fees per Patrick's framing (demand fundamental).
- **Static-snapshot stamps**: matrix rows with sparkline length ≤ 1 → "static snapshot" italic stamp under the period column. Rows with 3-point Census pattern (decade-class intervals around 2011/2016/2021) → "Census 3-pt" stamp. Detection in `_l5RowAnnotation` helper. CSS class `.l5-value .period-stamp`.
- **Workforce scope stamps**: matrix rows with `signal` text matching `/no SA2 peer cohort/i` and category=workforce render with dashed-italic `.l5-signal.scope-stamp` styling instead of the band signal pill — surfaces the "state-level (NSW) — no SA2 peer cohort" caveat prominently rather than as plain text in the signal column.

### Bundle 2 (2026-05-12) — rich-content drawers + ingest upstream
- **ACARA schools row-level ingest**: new `acara_schools` table (11,039 schools) joining School Location 2025 + School Profile 2025 on ACARA SML ID. Carries name, sector, type, sa2_code, lat/lng, total enrolments, ICSEA. Ingest script `ingest_acara_schools.py` is idempotent (drops + recreates table), takes STD-08 backup, writes audit_log row. Unlocks two downstream features below.
- **OSHC school-attached detection** in `_compute_cross_subtype_competition`: per-OSHC proximity match against `acara_schools` (300m threshold via cheap equirectangular haversine). Returns `school_attached`, `nearest_school` (name/sector/type), `nearest_school_distance_m` per service. Surfaced in the OSHC drawer with green "▣ At {school name}" callout per attached service + summary line ("3 of 3 services co-located with a school within 300m").
- **Schools-in-catchment drawer**: per-school list grouped by sector (Government / Catholic / Independent), each row: name + enrolment + type + sector + ICSEA + suburb. Sorted by enrolment desc within group. Backend helper `_build_schools_in_catchment` reads from `acara_schools`. Frontend `renderDrawerContent` handles `schools_in_catchment` drawer key. `renderMetricDrawer` routes `sa2_school_count_total` and `sa2_school_enrolment_total` › triggers to this drawer (the matrix rows still inline-expand on body click for the historical chart).
- **Right-column rich-content indicator**: matrix `›` trigger renders as a layered-stack SVG icon (vs plain chevron) when the drawer carries deeper data. Rich keys: dec83:* substrate + ccs_coverage + cross_subtype_* + schools_in_catchment + provider_approval_scale + metric:sa2_school_count_total + metric:sa2_school_enrolment_total + metric:sa2_nes_share + metric:sa2_overseas_born_share. Plain methodology drawers keep the chevron. Plus a one-line caption above the matrix explaining the icon affordance.

### Layer 5 — Bundle 2-prep additions (2026-05-12)
- **Category rename**: "Education" → **"Learning environment"** in `CATEGORY_LABELS`. Captures what learning ecosystem operates around the centre (schools + after-school care + transitions) rather than just education infrastructure.
- **Workforce 3y trend in commentary**: JSA IVI matrix rows now prepend `+X% over 3y` / `−X% over 3y` to the commentary so the reader sees direction + magnitude of vacancy-pressure change without needing the chart. Computed in `_matrix_workforce_rows` from the latest 37 monthly points. Stored on the row as `trend3y_pct` for downstream use.
- **School enrolment 3y trend row**: new matrix row in Learning environment category. Backend helper `_compute_school_enrolment_trend` reads `acara_school_enrolment_total` from `abs_sa2_education_employment_annual`. Surfaces latest value + 3y delta + 18-year sparkline. Commentary prefix "+X% over 3y" reads as ECEC demand leading indicator.
- **Cross-subtype care competition row**: asymmetric per subject subtype. LDC/Preschool subject → "OSHC services in catchment (transition pathway)" with count + total places. OSHC subject → "LDC services in catchment (feeder pipeline)". FDC subject → no row (low cross-subtype relevance). Backend helper `_compute_cross_subtype_competition`. The school-attached spatial check is deferred to OI-NEW-19 (needs per-school lat/lng table not yet ingested).

**`current` period sentinel**: synthetic count rows that aren't trajectory snapshots (provider scale / OSHC count / similar) carry `period: "current"`. The `_l5RowAnnotation` helper short-circuits on this sentinel so the row doesn't pick up the "static snapshot" stamp.

### Carryover block — analytical-priority reorder 2026-05-12
- Order: **Places & service type → Catchment meta → NQS rating → QA scores**. Was: NQS → Places → Catchment-meta → QA. Patrick queue #5: credit-analytical priority, operational identity leads, quality items cluster at the end.

### Chart 6 — refactored from dual-axis (2026-05-12)
- **Before:** Female LFP (Census, 3 points at 2011/2016/2021) + SALM unemployment (quarterly, 2024+ only for most SA2s) on a dual-axis chart. Unemployment line was always null because the period labels never matched and the underlying temporal coverage didn't overlap.
- **After:** Chart primarily plots SALM unemployment quarterly trajectory. Female LFP surfaced as a dated Census reference value in the chart head ("Female LFP {value}% (Census 2021)"). When SALM is missing for the SA2, falls back to LFP-only series. Title: "Unemployment rate (SALM quarterly)" or "Female labour-force participation" depending on which is primary.

### Layer 3 — Chart 7 (Daily rate) multi-age-band refactor 2026-05-12
Replaces the prior single-line headline-pair chart with a multi-line view showing all relevant age bands grouped by subject's care type:
- LDC / Preschool / FDC → 4 lines (0-12m / 13-24m / 25-35m / 36m-preschool) all full_day
- OSHC → 2 lines (before_school / after_school) at school-age
Each line has a distinct institutional colour swatch in the legend; latest-value chips show in chart head per series. Source line preserved. Custom Chart.js multi-dataset config; external readout shows hovered values across all series at the same period.

### Layer 2 — Executive interpretation
- Headline composer (rule-based 4-clause)
- Signal tiles (Demand · Supply · Population · Workforce · Quality · Community)
  - Each tile: label + headline summary + 2-3 sub-metric rows (name + value + band pill)
- Flag bar with severity hierarchy (RED / AMBER / INFORMATIONAL) + spillover pill

### Layer 3 — Primary historical trends (7 charts)
Every chart panel must render:
- Chart title + cohort suffix ("vs Major Cities WA") + current value + period + OBS badge
- Trend label ("−0.2% since Q1 2022 · +448 places · +6 centres")
- External readout slot (placeholder + populated on hover with two lines: value + running-%)
- Canvas with: line + fill + point markers + crosshair + centre-events overlay + reference line (where configured)
- Events legend (when events present)
- Cohort histogram below chart (20 bins, proportional bars, self-bin highlighted, italic caption, cohort meta line)
- Full register: headline (Decile X · band · n=NNN) + decile strip 1-10 + band chips with text + INDUSTRY band pill + note + intent_copy + ABOUT panel + source line + DER/COM badges

Chart-specific notes:
- Charts 5/6 (dual-axis: under-5+births, LFP+unemp) use custom renderers; must still produce all of the above as much as the dual-data shape allows.
- Chart 7 (daily rate) is DEC-83-derived; if data absent for centre's SA2, render pending fallback honestly.

### Layer 4 — Secondary trends accordion
- 5 chart groups (Population context / Income / Workforce / Demographic / Education infra)
- Each chart compact (smaller register) but must still carry trend label + source line + decile snapshot
- Own trend-window selector (independent of L3)

### Layer 5 — Signal Matrix (~52 rows × 11 categories)
For every row:
- Display name + OBS/DER/COM badges (colour-coded)
- Current value + period
- Decile strip (1-10) + band when ranked
- Band signal pill or stub state ("Pending V1.5 ...")
- Commentary (leading bold value · then sentence)
- `›` drawer trigger
- Inline-row-click expand for trajectory-bearing metrics; renders full register inline

### Layer 6 — Drawer
- Click anywhere on row or `›` icon → side drawer
- ESC closes; URL fragment shareable; single drawer at a time
- Special drawer types: daily-rate / conditions / enforcement / operator-group / NQS / vacancy / operations / ccs_coverage
- Generic metric drawer: full position entry detail

## Workforce-row specific element list (the one we kept regressing on)

Workforce rows in v3.31's `renderWorkforceSupplyCard` render:
- Display label
- Latest value when `confidence === "live" && r.latest` — `{value, period}` extracted to "237 (2026-03)" shape
- Fact text when `confidence === "live" && r.fact` — Three-Day Guarantee policy statement
- "— pending" placeholder when `confidence === "deferred"`
- OBS badge with source tooltip
- Scope stamp ("state-level (WA) — no SA2 peer cohort")
- Sparkline trajectory (when live + has trajectory)
- intent_copy
- about_data ("About this measure" panel)
- status_note (when deferred)

In v2 matrix, all of these must surface in the row (current_value, period, signal/scope, commentary, status_note) — and the inline-row-click expand must render the full trajectory + register for the live JSA IVI metrics. ECEC Award rates legitimately has no trajectory in V1 (Fair Work ingest banked); render "no trajectory" honest fallback. Three-Day Guarantee is a single policy fact — no chart, but the fact text MUST appear as the value.

## Update cadence

- After every iteration that touches a layer, update the layer's element list here with anything new that's been added.
- When a DEC-84 amendment is minted, mirror the relevant elements here.
- This doc lives in `recon/` alongside design docs — not Tier 2, not Tier 1, just a working operational checklist.
