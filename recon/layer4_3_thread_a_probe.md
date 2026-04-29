# Layer 4.3 sub-pass 4.3.1 (Thread A) — probe and apply

**Status:** apply complete · **Date:** 2026-04-29 · **File touched:** `docs/centre.html` v3.2 → v3.3

This document captures the probe-before-code work for Layer 4.3 sub-pass 4.3.1 per DEC-65. It is a recon working artefact (sits in `recon/`); it should be retired and absorbed into `DECISIONS.md` / `OPEN_ITEMS.md` once the next consolidation pass runs, per the pattern established for `recon/layer4_3_design.md` v1.1.

---

## 1. Scope

Two deliverables in one sub-pass:

1. **Per-chart range buttons (1Y / 2Y) on the unemployment metric.** Override the global trend-window (DEC-73) on the `sa2_unemployment_rate` row only. Falls back to the global window when not pressed.
2. **Improved empty-state for SALM-missing SA2s.** Replace the silent em-dash on the unemployment row with a named cause when `confidence === "unavailable"`.

Effort: ~0.3 session per ROADMAP §1. Renderer-only — no schema or payload changes.

---

## 2. Probe

`docs/centre.html` v3.2 surface relevant to Thread A:

| Symbol | Line (v3.2) | Role |
|---|---|---|
| `_TRAJECTORY_RANGE_YEARS` | 866 | Global window state, default `0` = "All" |
| `_LAST_CENTRE` | 867 | Captured by `render()` to enable re-render on state change |
| `_setTrajectoryRange(years, btnEl)` | 869 | Global setter; re-renders the page |
| `_renderTrajectoryRangeBar()` | 880 | Emits the global 3Y/5Y/10Y/All bar at top of Population card |
| `_filterTrajectoryByRange(points, years)` | 907 | Per-series filter, relative to series' last point |
| `_renderTrajectory(metric, p)` | 1053 | Sole chart-emission point; receives `metric`, can branch on it |
| `renderPositionRow(metric, p)` `unavailable` branch | 1252–1261 | Currently renders silent em-dash |
| `.range-btn` CSS | 425 | Already styled to Palette A — Patrick locked design coherence |

`centre_page.py` v4 — confirmed unchanged need. Trajectory data already arrives in the payload (`p.trajectory`), confidence already arrives (`p.confidence`). No payload-schema bump.

The unemployment series in DB has 61 quarterly points (2010-Q4 through 2025-Q4) per the 2026-04-28b probe. 1Y ≈ 4 quarters, 2Y ≈ 8 quarters — the lowest-cadence-the-ABS-publishes framing per Patrick (2026-04-29 chat).

---

## 3. Decisions closed (A1–A6)

Surfaced before code; recorded here for traceability. None create new entries in `DECISIONS.md` — they are renderer-implementation choices within DEC-73's scope, not new architecture decisions.

| ID | Decision | Resolution |
|---|---|---|
| **A1** | Per-chart state model | Add per-metric override map (`_TRAJECTORY_OVERRIDE_YEARS`, keyed by metric) alongside the existing global. Missing key / `null` = "use global". Existing `_TRAJECTORY_RANGE_YEARS` retained as the fallback. |
| **A2** | Button placement | Right-aligned, inside `_renderTrajectory`, above the canvas. Reuses the `.range-btn` class — design coherence locked per Patrick (no new visual language for Layer 4.3). |
| **A3** | Button set + reset semantics | `1Y / 2Y` only. Click-to-toggle: clicking the active per-chart button clears the override; otherwise sets it. No third "Use global" button. Quarterly cadence is the lowest ABS publication for SALM, so 1Y/2Y are the meaningful sub-global windows. |
| **A4** | Helper key | Metric-keyed lookup (`_PER_CHART_RANGE_OPTIONS`). Today the lookup contains only `sa2_unemployment_rate: [1, 2]`. Forward-compatible with Thread B (SALM-LFP) and any future short-cadence series. |
| **A5** | SALM-missing copy | `"SALM does not publish at this SA2 (small-population suppression)"` — italic, applied only when `metric === "sa2_unemployment_rate"` AND `confidence === "unavailable"`. Other unavailable metrics retain the em-dash; their missing-data causes differ (Census-only series, deferred metrics) and warrant per-metric copy when those rows are next revisited. |
| **A6** | Override scope | Trajectory chart only. Cohort histogram and decile strip are point-in-time per DEC-71's boundary rule — range buttons are meaningless for them. Same scope as the global window. |

---

## 4. Apply

`docs/centre.html` v3.3 = v3.2 + 5 surgical edits:

1. **Header bump** (line 2). v3.2 → v3.3 with Thread A annotation per STD-03.
2. **State + lookup additions** (after line 867). New globals `_TRAJECTORY_OVERRIDE_YEARS` (mutable map) and `_PER_CHART_RANGE_OPTIONS` (constant lookup). Three new helpers: `_getEffectiveRangeYears(metric)`, `_setPerChartRange(metric, years, btnEl)`, `_renderPerChartRangeBar(metric)`.
3. **`_renderTrajectory` rewire**. Replaces direct `_TRAJECTORY_RANGE_YEARS` read with `_getEffectiveRangeYears(metric)`. Prepends `_renderPerChartRangeBar(metric)` to both the empty-state return and the canvas-wrapper return.
4. **Empty-state extension in `renderPositionRow` `unavailable` branch.** Branches on `metric === "sa2_unemployment_rate"`; emits the SALM-suppression copy for unemployment only.

Net delta: +87 lines, all additive. No deletions. No payload-schema change. No `centre_page.py` change.

Validation: `grep` confirms all five edit symbols present and all four references to the original `_TRAJECTORY_RANGE_YEARS` are intentional (declaration, global setter, fallback in `_getEffectiveRangeYears`, active-state read in `_renderTrajectoryRangeBar`).

---

## 5. Open item raised

### OI-23 — Global trend-window bar disappears when Population card has no live data
**Severity:** Low · **Opened:** 2026-04-29 · **Decision:** none

The global trend-window bar (DEC-73) renders only inside `renderPopulationCard`, gated by `hasAny === false` for that card's metrics. Post–Thread A, an SA2 with unemployment data but no live Population metrics presents the unemployment row with only its per-chart 1Y/2Y override buttons — the global window control is unreachable.

In practice this is rare: Population covers under-5 / total / births, which have effectively universal SA2 coverage via ABS ERP and Births. But Thread A makes the brittleness more material because clearing a per-chart override falls back to a control the user can no longer see.

**Fix path:** when next opening `centre.html` for any Population/Labour-Market layout work (e.g., Layer 4.3 sub-pass 4.3.6 row-weight reclassification), promote `_renderTrajectoryRangeBar()` to render at the page level (above both cards) rather than inside `renderPopulationCard`. ~10 lines of code; trivial when next in the file.

---

## 6. References

- `recon/layer4_3_design.md` v1.1 (referenced via DECISIONS.md DEC-74/75/76, OPEN_ITEMS.md OI-19, STANDARDS.md STD-34) — Thread A scope as carved out in Layer 4.3 design.
- DEC-65 — probe-before-code pattern.
- DEC-73 — global trajectory window UX (extended by Thread A).
- DEC-71 — System A / System B boundary; trends use Chart.js, position indicators use SVG. Thread A's per-chart bar sits on the trend side (Chart.js territory), so range buttons are admissible there.
- STD-02, STD-03 — full-file regen + version-marker bump.
- P-2 (PRINCIPLES) — honest absence over imputed presence; the named SALM-missing copy realises this for the unemployment row.
