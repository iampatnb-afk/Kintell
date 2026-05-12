# Layer 4.3 sub-pass 4.3.6 — DEC-75 row-weight probe

**Date:** 2026-04-29
**Operator:** Patrick Bell
**Sub-pass:** 4.3.6 (second of nine in re-sequenced Layer 4.3 implementation)
**Effort estimate:** ~0.2 session
**Decision driver:** DEC-75 (visual weight by data depth)
**Closes alongside:** OI-23 (global trend-window bar visibility)

---

## Scope

Two concerns shipped in a single edit, per the OI-23 fix path's dependency on Population/Labour-Market layout work:

1. **DEC-75 row-weight reclassification.** Add `row_weight: "full" | "lite" | "context"` field to the Layer 4 metric registry in `centre_page.py`. Reclassify the LFP triplet (`sa2_lfp_persons` / `_females` / `_males`) to Lite. Reclassify `jsa_vacancy_rate` to Context-only. Render switch in `centre.html renderPositionRow` selects the visual treatment. Closes G5 of `recon/layer4_3_design.md`.
2. **OI-23 fix.** Promote `_renderTrajectoryRangeBar()` from inside `renderPopulationCard` to page level above both Position cards. The bar's visibility is now gated on "any Full-weight row on the page has trajectory data" — Lite and Context rows do not vote toward the gate.

Renderer-only. No DB mutations. No payload schema bump (existing `period_label` / `year` fields supply the "as at YYYY" stamp; existing `trajectory` field is preserved for Lite metrics even though the chart isn't rendered).

---

## Sequencing pass (DEC-65 amendment)

Single-pass sub-pass, so the dependency-ordering check is trivial. Recorded for protocol completeness:

- **Depends on:** the metric registry shape in `centre_page.py` (existing). Nothing else.
- **Downstream depends on this how?** Sub-pass 4.3.8 (intent copy) adds the inline-prose slot uniformly across all three weights and must know which weight each row will use. Sub-pass 4.3.7 (perspective toggle) adds reversibility fields to *catchment* metrics, not the existing 10 — independent of row_weight, but the renderer's per-row switch should not have been written assuming a single template, so this pass must land first. Sub-pass 4.3.9 (workforce supply context block) renders `jsa_vacancy_rate` in its new home; the `row_weight: "context"` field is the registry-level signal that lets the workforce block consume metrics without re-classifying them.
- **Visible value:** LFP rows visibly drop the trajectory chart and cohort histogram, with an explicit "as at YYYY · static snapshot, no trajectory" stamp in their place. P-2 (honest absence over imputed presence) is now applied at the visual layer, not just in copy.

Position in the re-sequenced order is unchanged: 4.3.6 is sub-pass 2 of 9, immediately after 4.3.1 Thread A.

---

## Decisions surfaced and confirmed before code

Five micro-decisions were surfaced in the probe turn before any code was written. All five recommended defaults were accepted by the operator without amendment.

### D1 — `jsa_vacancy_rate` render location during 4.3.6
**Confirmed: render in-place in the Labour Market card with Context-only treatment until sub-pass 4.3.9 relocates it.**

In practice the metric is `status='deferred'` so the only visible effect this pass is that `row_weight: "context"` is now wired on the registry. The `_renderContextRow` branch is dormant in the Position-row code path until either (a) data lands and confidence flips to normal/low, or (b) sub-pass 4.3.9 moves the metric to the Workforce supply context block (DEC-76).

### D2 — Intent copy slot in this pass
**Confirmed: row-weight branches render WITHOUT an intent-copy slot. Sub-pass 4.3.8 adds the slot uniformly across all three weights.**

4.3.8 is the natural touch-every-row pass and adds the `LAYER3_METRIC_INTENT_COPY` constant + the per-row slot in one motion. Adding a placeholder slot in 4.3.6 would mean two passes touching every row instead of one.

### D3 — Future daily-rate row class accommodation
**Confirmed: `row_weight` typed as a string. Renderer's switch has explicit branches for `full` / `lite` / `context` and a default-to-`full` fallback. Daily-rate adds a 4th branch — pure addition, no retrofit.**

The contract is: registry sets a string; renderer reads `p.row_weight || "full"`. Unknown values render as Full rather than crashing or showing nothing. The parallel daily-rate stream (flagged in `ROADMAP.md` §4) will add a 4th weight value when its centre-page integration is designed at merge-back.

### D4 — OI-23 bar visibility gate after promotion
**Confirmed: render the bar whenever ANY Full-weight row on the page has trajectory data.**

Implemented as `_pageHasFullTrajectory(centre)` — walks both Position cards, checks `e.row_weight === "full" && e.trajectory && e.trajectory.length`. Returns true on first hit. The honest gate per P-2: Lite and Context rows have no trajectory by design, so they cannot make the bar reachable on their own. If no Full row has data, the bar correctly hides — there is nothing for it to control.

### D5 — "as at YYYY" stamp source for Lite
**Confirmed: derive from the most recent point in the trajectory series (`p.trajectory[p.trajectory.length - 1].period`), with fallback to `period_label` / `year` on the entry. No new payload field.**

The trajectory data is still flowing through the payload for Lite metrics (LFP has 3 Census points: 2011/2016/2021); the Lite render simply doesn't show the chart. Reading the most recent point's period gives the cleanest stamp ("as at 2021") because it reflects the actual most-recent data, which may differ from the Layer 3 banding row's year if banding ran on a different vintage.

---

## What changes visibly

For an SA2 with a typical data profile (Full population coverage + SALM unemployment + Census income + Census LFP):

| Row | Before (v3.3) | After (v3.4) |
|---|---|---|
| Under-5 / total / births / unemployment / income trio (7 metrics) | Full template | Full template — unchanged |
| LFP triplet (3 metrics) | Full template (with a 3-point dot trajectory + cohort histogram) | Lite template (decile strip + chips + "as at 2021" stamp) |
| `jsa_vacancy_rate` (1 metric) | "(coming next)" stub | "(coming next)" stub — unchanged (status=deferred, registry has `row_weight: "context"` now wired) |
| Trend-window bar | Inside Population card, gated on Population having data | Above both Position cards, gated on any Full row having trajectory data |

For an SA2 missing Population data but with unemployment data (the OI-23 case): the trend-window bar now renders above both cards regardless of which card has data, so the unemployment row's per-chart 1Y/2Y override buttons sit beneath a globally-reachable control.

---

## Files touched

| File | Before | After | Change |
|---|---|---|---|
| `centre_page.py` | v4 | v5 | `row_weight` added to all 12 entries in `LAYER3_METRIC_META`; `_layer3_position` propagates field on stub + populated entries |
| `centre.html` | v3.3 | v3.4 | `renderPositionRow` switches on `row_weight` (3 explicit branches + default-to-Full); new `_renderFullRow` / `_renderLiteRow` / `_renderContextRow` helpers; new `_pageHasFullTrajectory` helper; `_renderTrajectoryRangeBar()` call moved from `renderPopulationCard` to `render()` page level |
| `recon/Document and Status DB/PROJECT_STATUS.md` | — | — | 4.3.6 marked SHIPPED; centre.html and centre_page.py versions bumped; OI-23 headline marked closed; POSITION block description updated to describe Full / Lite / Context |
| `recon/Document and Status DB/OPEN_ITEMS.md` | — | — | OI-23 moved from active to Closed with resolution note |
| `recon/Document and Status DB/ROADMAP.md` | — | — | §1.3 sub-pass table marks 4.3.6 SHIPPED |
| `recon/Document and Status DB/DECISIONS.md` | — | — | Untouched. DEC-75 is the operative decision; no new entries |

---

## Out of scope (explicitly)

- The `<div class="placeholder">Trajectory band (5y CAGR, 10y sparkline, births trend) arriving in the next Layer 4 pass</div>` and equivalent in `renderLabourMarketCard` are stale placeholders from the pre-trajectory era. They were not removed in this sub-pass — separate cleanup, no decision attached.
- Sub-pass 4.3.8 will add the intent-copy slot to all three row-weight branches. The current Lite and Context renderers leave a clean place for the slot to land between the band chips / single-fact line and the DER+COM badges.
- Sub-pass 4.3.9 will move `jsa_vacancy_rate` from the Labour Market card to the new Workforce supply context block (DEC-76). The `row_weight: "context"` field on the registry is the signal the workforce block will read.

---

## Verification plan

1. Open the centre page for an SA2 with full data coverage (e.g. service in a Major Cities NSW SA2). Confirm:
   - Trend-window bar renders ABOVE the Population card heading, not inside the card.
   - 7 Full rows render unchanged (trajectory + histogram + decile strip + chips).
   - 3 LFP rows render without trajectory and without histogram, with "as at 2021 · static snapshot, no trajectory" beneath the band chips.
   - `jsa_vacancy_rate` row continues to show "(coming next)".
2. Open the centre page for an SA2 with missing Population data but live unemployment data (an SA2 where SALM publishes but ERP coverage is absent — rare but possible). Confirm the trend-window bar still renders at page level. (If no such SA2 exists in the DB, this case is dormant but the gate logic is correct by inspection.)
3. Click the unemployment per-chart 1Y / 2Y buttons; confirm they still toggle. Click an active button to clear; confirm the chart falls back to the global window. Confirm the global bar is visually reachable throughout.
4. Inspect the payload (`python centre_page.py <service_id> | python -m json.tool | grep row_weight`) — confirm every Position entry has the field with the expected value.
