# Centre payload schema v6 — staked 2026-05-12

This document captures the payload-schema state as of the v1 stake (`centre-v1-stake-2026-05-12`, on commit `212b597`). Used as reference if v2 cut-over needs rollback.

## Schema name
`centre_payload_v6` (introduced in earlier 4.4 sub-pass; unchanged through DEC-83 ship since the daily-rate render was deferred to v2).

## Top-level structure

```
{
  "centre": { ...identity, header, subtype, ARIA, ... },
  "position": {
    "catchment_position": { rows: [...] },     # 13 rows (5 credit + 8 demographic)
    "population": { rows: [...] },              # 4 rows
    "education_infrastructure": { rows: [...] },# 3 rows V1 (5 banked)
    "labour_market": { rows: [...] },           # 8 rows
    "workforce_supply": { rows: [...] },        # 4 rows (all deferred wire-up)
  },
  "community_profile": {
    "country_of_birth_top_n": [...],            # T08, top-3 typically
    "language_at_home_top_n": [...],            # T10A+T10B, top-3 typically
  },
  ...
}
```

## Per-row structure (within position card)

Each row carries:
- `metric` — registry key (e.g. `sa2_supply_ratio`)
- `display` — display label (from `LAYER3_METRIC_META[metric].display`)
- `weight` — `"full" | "lite" | "context"`
- `confidence` — `"live" | "low" | "unavailable" | "deferred"`
- `raw_value` — numeric or string
- `value_format` — `"percent" | "percent_share" | "currency_weekly" | "currency_annual" | "ratio_x" | "int" | ...`
- `period_label` / `period` — display stamp
- `decile` — 1–10 (within cohort)
- `band` — `"low" | "mid" | "high"` or band-specific keys
- `cohort_def` — definition string for tooltip
- `cohort_n` — cohort size
- `cohort_dist_pct` — decile distribution for histogram (Full only)
- `industry_band` — { label, key, note } or null (3 metrics: supply_ratio, child_to_place, demand_supply)
- `intent_copy` — italic credit-lens line (22 entries in registry)
- `about_data` — methodology text (4 entries: 4 catchment Full metrics)
- `trajectory` — list of {period, value} dicts; cadence varies (quarterly / annual / 3pt-Census / 18yr-annual)
- `events` — center events overlay (catchment metrics only)
- `uses_calibration` — bool (3 metrics use STD-34 calibration)
- `calibrated_rate` / `rule_text` — STD-34 calibration metadata
- `source` — OBS attribution string
- `pair_with` / `reversible` / `default_perspective` / `perspective_labels` — DEC-74 perspective toggle (registered, inert in V1)

## Rendering helpers (in centre.html v3.31)
- `_renderFullRow(p, ctx)`, `_renderLiteRow(p, ctx)`, `_renderContextRow(p, ctx)` — weight dispatchers
- `_renderTrajectory(metric, p)` — Chart.js canvas + window control + event overlay
- `_renderIntentCopy(p)` — italic credit-lens line
- `_renderIndustryBand(p)` — pill below band chips
- `_renderAboutData(p)` — paragraph block (Full only)
- `_renderTopNContext(list, label, key)` — Top-3 list display
- `_renderDecileStrip(decile)`, `_renderBandChips(metric, p)`, `_renderCohortHistogram(p)`
- `_renderLiteDelta(p)` — first-to-last change badge
- `_renderTrajectoryRangeBar()`, `_renderWfsRangeBar()` — window controls
- Badges: `renderBadge("OBS", ...)`, `renderBadge("DER", ...)`, `renderBadge("COM", ...)`

## Card render order (in centre.html v3.31)
1. Header (breadcrumb + service name)
2. Trajectory range bar
3. Catchment Position card (`renderCatchmentPositionCard`) — 5 credit rows + Demographic mix sub-panel (8 Lite rows + 2 top-N context lines)
4. Population card (`renderPopulationCard`)
5. Education Infrastructure card (`renderEducationInfrastructureCard`)
6. Labour Market card (`renderLabourMarketCard`)
7. Workforce Supply Context card (`renderWorkforceSupplyCard`)

## What v2 (per DEC-84) supersedes

v2 schema name will be `centre_payload_v7`. New top-level keys:
- `executive` — Layer 2 signal tiles + flag bar + headline
- `matrix` — Layer 5 row list (~52 rows V1)
- `drawer` — Layer 6 detail content keyed by metric (templates per drawer type)

The v6 `position.*` cards will continue to populate during v2 transition until cut-over; they're consumed by the v1 renderer at `/centres/{id}`. After cut-over, `position.*` becomes a derived view of the matrix payload — the matrix is canonical.

## Stake purpose

This file lives in the v1 final stake bundle so that if v2 cut-over needs reversion, the v6 payload contract is documented alongside the v3.31 renderer and v23 backend. Combined with `ROLLBACK.md`, the recovery path is:

```
git checkout centre-v1-stake-2026-05-12 -- centre_page.py docs/centre.html
```

Plus: revert any payload-shape changes that broke v6 contract. See `ROLLBACK.md` for detail.
