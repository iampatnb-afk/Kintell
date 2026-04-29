# Layer 4.3 sub-pass 4.3.8 — inline intent copy + trend-window % change probe

**Date:** 2026-04-29
**Operator:** Patrick Bell
**Sub-pass:** 4.3.8 (third of nine in re-sequenced Layer 4.3 implementation; second renderer-best-practice pass after 4.3.6)
**Effort estimate:** ~0.4–0.5 session (bundled at operator request — see 4.3.6 PHASE_LOG entry)
**Decision drivers:** DEC-73 (Trajectory window UX) + DEC-75 (visual weight) + Layer 4.3 design intent-copy thread

---

## Scope

Two renderer-only enhancements bundled into one round per the 4.3.6 session-end scope adjustment:

1. **Inline intent copy.** New `LAYER3_METRIC_INTENT_COPY` constant in `centre_page.py` with one-sentence interpretive prose per metric. Surfaced on the centre page beneath the band chips in all three row-weight branches (Full / Lite / Context-only). Tells the credit-lens reader why the metric matters for THIS centre's risk picture, not the metric in the abstract.

2. **Trend-window % change display.** For each Full-weight chart on the centre page: a signed `+X.X% since YYYY` label sits top-right alongside any per-chart range buttons; the Chart.js hover tooltip extends with a running % from window-start to that point. Both update live when the user changes the trend window (global 3Y/5Y/10Y/All or per-chart 1Y/2Y override). Lite rows do NOT carry the label — P-2 honest absence; LFP's Lite weight specifically dropped the chart because "3 Census points is not a trajectory" and a "% change since 2011" label would re-import trajectory framing through the back door.

Neither piece needs payload schema changes. Trajectory data is already in `p.trajectory`; intent copy is a new field on `p` derived from the constant.

Versions: `centre_page.py` v5 → v6. `centre.html` v3.4 → v3.5.

No new DEC. Both pieces are renderer-implementation choices within DEC-73 (Trajectory window UX) scope — same pattern as Thread A's per-chart overrides, where the implementation was treated as a renderer choice within DEC-73 rather than a separate decision.

---

## Sequencing pass (DEC-65 amendment)

Trivial — bundled single-pass sub-pass. Recorded for protocol completeness:

- **Depends on:** the metric registry shape (existing) + trajectory data already in payload (existing). Nothing else.
- **Downstream depends on this how?** Sub-pass 4.3.7 (perspective toggle) reads intent copy via `p.intent_copy`; the constant carries entries for the reversible ratio pairs (`supply_ratio` + `child_to_place`, `demand_supply` + `demand_supply_inv`) so the toggle picks the right copy per active perspective. Sub-pass 4.3.9 (workforce supply context block) reads the workforce entries from the same constant. Sub-pass 4.2-A.3 (catchment row renderer) reads the catchment entries. Landing the constant now means none of those sub-passes need to retrofit copy.
- **Visible value:** every Position row gets a single sentence of credit-lens framing. Every Full-weight chart shows the period-over-period change without forcing the reader to mentally diff the start and end points.

Position in the re-sequenced order is unchanged: 4.3.8 is sub-pass 3 of 9, after 4.3.6.

---

## Decisions confirmed before code

Operator confirmed defaults D1=a, D2=a, D3=a, D4=a, drafting approach=a.

### D1 — Intent copy slot placement

**Confirmed: below band chips, above DER+COM badges.**

For Full and Lite rows: the slot sits between `_renderBandChips(p)` and the badges row. For Lite rows specifically, the order is: chips → "as at YYYY" stamp → intent copy → badges. The "as at" stamp is a temporal qualifier on the data; the intent copy is interpretive prose; both live in the small-italic-muted register and read in sequence naturally.

For Context-only rows: the slot sits below the "state-level — no SA2 peer cohort" stamp.

The reader scans the data signal first (chips for Full/Lite, single-fact line for Context), then reads the framing. Intent copy answers "why does this matter for this centre" after the chip has answered "what's the band".

### D2 — Missing intent copy behaviour

**Confirmed: silent — no slot rendered if the constant has no entry for that metric.**

`LAYER3_METRIC_INTENT_COPY.get(metric_name)` returns `None` for missing entries; `_layer3_position` propagates `None` onto the entry; `_renderIntentCopy(p)` returns `""` for null/missing copy. P-2 honest absence — the slot doesn't pretend something is there when it isn't, and future metrics pick up copy automatically by adding to the constant.

### D3 — Trend-% start anchor

**Confirmed: first point IN the filtered window.**

Implemented as `_computeTrendPctChange(points)` reading `points[0]` and `points[points.length - 1]`. The label says `since YYYY` where YYYY is the year extracted from `points[0].period`. If the window is 10Y but the earliest available point in the filtered window is 2017, the label says "since 2017" — honest about what the % is computed against.

This means a 10Y window on a 5-year-old metric and an "All" window on the same metric will show the same label and the same %. That's correct: there's no more data to include than what's there.

### D4 — Tooltip format

**Confirmed: two-line tooltip via Chart.js `afterLabel` callback.**

- Line 1: `<metric label>: <formatted value>` (existing format, preserved by overriding the `label` callback to apply value formatting per `p.value_format`).
- Line 2: `+X.X% since YYYY` (new; emitted via `afterLabel` callback).
- First point in window has no line 2 (it IS the start; no change to display from itself).

Implementation: the chart-init closure captures `windowStartValue`, `windowStartPeriod`, and `valueFormat` from the outer scope; the callbacks read those at hover time. Re-rendering on range-button click rebuilds the chart with new captured values, so the tooltip stays in sync with the active window.

### Drafting approach for intent copy prose

**Confirmed: I drafted all entries based on existing band-copy and metric semantics. Operator reviews inline as part of `centre_page.py` v6 — edit on the fly if anything reads wrong; no pre-approval in chat needed.**

22 entries written, covering:
- 10 currently-rendered Position metrics (all live in v3.5)
- 6 catchment-ratio entries (DEC-74's 2 reversible pairs × 2 perspectives + 2 absolute = 6; sit dormant until sub-pass 4.2-A.3)
- 4 Workforce supply context entries (DEC-76; sit dormant until sub-pass 4.3.9)

Prose is one sentence per metric, focused on the credit-lens reading: what the metric tells the underwriter about THIS centre's risk picture. Avoids restating the band chip text. The chip is "what the band says"; the intent line is "why it matters".

---

## Implementation defaults (documented; no operator confirmation needed)

- **Per-chart bar layout when both label and buttons exist (unemployment row):** flex row with `justify-content: space-between` — trend-% label on the LEFT, per-chart range buttons on the RIGHT.
- **Per-chart bar layout when only label exists:** `justify-content: flex-end` (label sits alone right-aligned).
- **Per-chart bar layout when only buttons exist (preserves v3.4 layout):** unchanged from before.
- **Precision:** 1 decimal (e.g. `+12.3%`).
- **Sign convention:** explicit `+` for positive, Unicode en-dash `−` (U+2212) for negative, `+0.0%` for zero. Matches design palette discipline (no red/green valence; signed prefix carries the direction).
- **Edge case — <2 points in window:** no label, no tooltip extension. The chart's existing empty-state copy handles the visual.
- **Edge case — Full row with no trajectory data at all:** no label. Matches existing silent-empty-chart behaviour.
- **Edge case — start value is 0 or null:** % change is undefined; `_computeTrendPctChange` returns `null` and the label suppresses. Tooltip's `afterLabel` returns `null` for the same reason.
- **"All" window:** uses the earliest point in the unfiltered series. Same logic as any other range, since `_filterTrajectoryByRange(points, 0)` returns all points.
- **Backward compatibility:** the original `_renderPerChartRangeBar(metric)` function is preserved as a thin wrapper around the new `_renderPerChartRangeBarButtons(metric)` helper, so any external caller (none currently, but if added) continues to work unchanged.

---

## What changes visibly

For an SA2 with full data coverage:

| Element | Before (v3.4) | After (v3.5) |
|---|---|---|
| Each Full row | trajectory + chips + DER/COM badges | trajectory + label `+X.X% since YYYY` top-right of chart + chips + intent copy line + DER/COM badges |
| Each Lite row | chips + "as at YYYY" stamp + DER/COM badges | chips + "as at YYYY" stamp + intent copy line + DER/COM badges |
| Hover on any Full chart point (other than the first in window) | tooltip shows `<metric>: <value>` | tooltip shows `<metric>: <value>` AND `+X.X% since YYYY` |
| Hover on the first point in window | tooltip shows `<metric>: <value>` | tooltip shows `<metric>: <value>` (unchanged — this point IS the window-start) |
| Click a range button (3Y/5Y/10Y/All or 1Y/2Y) | chart re-renders with new window | chart re-renders + label updates + tooltip running-% updates |

Visual treatment of intent copy: 11.5px italic, `var(--text-mute)` (matches the existing "as at YYYY" stamp register), full-width below band chips with 8px top margin.

Visual treatment of trend label: 11px, `var(--text-mute)`, tabular-nums (so the % aligns when label appears across multiple charts in the same column). Positioned top-right of the chart area.

---

## Files touched

| File | Before | After | Change |
|---|---|---|---|
| `centre_page.py` | v5 | v6 | New `LAYER3_METRIC_INTENT_COPY` constant (22 entries); `_layer3_position` propagates `intent_copy` onto every entry (stub + populated); `_stub` signature accepts `metric_name` |
| `docs/centre.html` | v3.4 | v3.5 | New `_yearOfPeriod` / `_formatTrendPct` / `_computeTrendPctChange` helpers; refactored `_renderPerChartRangeBar` into a buttons-only emit + thin wrapper; rewrote `_renderTrajectory` to compose label + buttons in a single top-strip row, capture window-start for the tooltip, and extend Chart.js tooltip with running-% via `afterLabel` callback; new `_renderIntentCopy` helper; intent-copy slot added to `_renderFullRow`, `_renderLiteRow`, and `_renderContextRow` |
| `recon/Document and Status DB/PROJECT_STATUS.md` | — | — | Centre page section updated with intent-copy + trend-% bullets; versions bumped; sub-pass table marks 4.3.8 SHIPPED; What's Next reflects 4.3.9 as next |
| `recon/Document and Status DB/ROADMAP.md` | — | — | §1.3 sub-pass table marks 4.3.8 SHIPPED |
| `recon/Document and Status DB/OPEN_ITEMS.md` | — | — | Untouched |
| `recon/Document and Status DB/DECISIONS.md` | — | — | Untouched. No new DEC; renderer-implementation choice within DEC-73 scope (same as Thread A's per-chart overrides) |

---

## Out of scope (explicitly)

- The stale `<div class="placeholder">Trajectory band (...) arriving in the next Layer 4 pass</div>` placeholders inside `renderPopulationCard` and `renderLabourMarketCard` are still present from pre-trajectory days. Untouched in this sub-pass — separate cleanup.
- The `as at YYYY · static snapshot, no trajectory` stamp on Lite rows still uses the LFP triplet's most-recent trajectory point as the year. This is correct for current Lite rows (where the trajectory data is in payload but not rendered as a chart). Keeps in sync with the trend-% label's start-anchor handling for consistency.
- The catchment row renderer (sub-pass 4.2-A.3), Workforce supply context block (sub-pass 4.3.9), and perspective toggle (sub-pass 4.3.7) all read `p.intent_copy` from this sub-pass's wiring. They will pick up the dormant entries automatically when they ship.

---

## Verification plan

1. **Payload smoke-test:** import `centre_page` and call `get_centre_payload(<sid>)`. Confirm every Position entry has `intent_copy` populated for the 10 live metrics; missing for any future metric.
2. **Visual: Full row with full data coverage** (e.g. service 1, under-5 count). Confirm:
   - Trend label `+X.X% since YYYY` renders top-right of chart.
   - Hover any non-first point — tooltip shows two lines.
   - Hover the first point in window — tooltip shows one line.
   - Italic intent copy renders below band chips.
3. **Visual: Lite row** (LFP). Confirm:
   - No trend label on the chart area (chart is suppressed anyway).
   - "as at 2021 · static snapshot, no trajectory" stamp renders.
   - Italic intent copy renders below the stamp.
4. **Visual: Context-only / deferred row** (jsa_vacancy_rate). Confirm:
   - "(coming next)" stub still renders (status='deferred').
   - When the metric's status flips post-4.3.9, the Context branch renders the state-level stamp + intent copy.
5. **Interactivity: range button click.** Click 3Y on the global bar. Confirm every Full chart's label updates; tooltips on next hover reflect the new window. Click 1Y on unemployment. Confirm only that chart's label updates; others keep their global window.
6. **Edge: SA2 with sparse data.** Open a centre where some Full metrics have <2 points after windowing. Confirm those charts show no label and no tooltip extension; no console errors.
