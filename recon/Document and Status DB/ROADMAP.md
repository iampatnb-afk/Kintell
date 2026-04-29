# Roadmap

The forward-looking view of work scope and sequencing. `PROJECT_STATUS.md` is present-tense ("what is the current state"); this document is forward-looking ("what is V1, what is P2, what is the path").

This document changes when scope changes or a phase moves. It does not log session work — that's in `recon/PHASE_LOG.md`.

Last updated: 2026-04-29 (bundled round shipped + JSA IVI wire-up + 4.3.2/4.3.3 probe dispositions resolved).

---

## 1. V1 launch scope

V1 is the commercial-launch-ready scope. The ordering below is by *current state*, not by sequence.

### Already shipped or in flight

| Surface | Current state |
|---|---|
| **Industry tab** (`index.html`) | Shipped. Chart.js + Palette B (System B). |
| **Catchment tab** | Deprecated. Catchment data moves onto the centre page (Layer 4.2 design); no standalone catchment surface. |
| **Operator tab** + relationship/merge-review tool | Shipped. Includes brand-cluster review UX (DEC-7), bulk-accept variants. |
| **Centre tab v3.2** (`centre.html`) | Shipped 2026-04-28b. NOW: NQS, Places, Catchment context, Tenure. POSITION: 10 Layer 3-backed metrics with trajectory + cohort histogram + gradient decile strip + band chips. Chart.js trends matching industry-page conventions. Global 3Y/5Y/10Y/All trend window buttons. |
| **Layer 4.2-A** — catchment data on the centre page | Designed; scope expanded by Layer 4.3 to include 4 core ratios. Implementation pending Layer 4.3 calibration function landing + Layer 2.5 cache build. |
| **Layer 4.3 design v1.1** | Closed 2026-04-29. G1+G2 merged (DEC-74), G3 locks STD-34, G4 closed (OI-19), G5 added (DEC-75), Thread D added (DEC-76). Implementation now unblocked. |

### V1 path remaining

Total: ~6.2 sessions of work. L4.4 is pure deepening; V1 ships without it if needed.

| Phase | Effort | Status | Gating |
|---|---|---|---|
| **Layer 4.3** — calibration + intent copy + per-chart buttons + perspective toggle + row-weight reclassification + workforce supply context block | ~2.5 sessions | Designed and decisions closed (v1.1 amendment 2026-04-29); ready for implementation | None |
| **Layer 4.2-A** — catchment data on centre page | ~2.2 sessions | Designed | Gated on Layer 4.3 calibration function landing + Layer 2.5 cache build |
| **Layer 4.4** — new ingests (NES, parent-cohort 25–44, schools) | ~1.5 sessions | Deferred to V1.5 (OI-19) | Post-V1; pure deepening but NES is required to close the calibration function's documented gap (`nes_share_pct` input) |

### Layer 4.3 sub-passes (revised 2026-04-29)

The closures from the 2026-04-29 design session (DEC-74, DEC-75, DEC-76) reshape the Layer 4.3 implementation sequence. Total effort grew from ~1.7 to ~2.5 sessions.

**Re-sequenced 2026-04-29 (continued)** to put renderer best-practice before data plumbing. Renderer sub-passes (row-weight, intent copy, workforce supply block, perspective toggle) depend only on the metric-registry shape, not on the calibration function or schema migration. Re-sequencing brings visible "best-practice" centre page forward by ~2.3 sessions and means catchment ratios in Layer 4.2-A drop into a render slot that is already wired with the perspective toggle, eliminating retrofit. Original ordering preserved in git history. See OI-24 — the missed dependency check is the protocol-level gap; DEC-65 amended to include a sequencing pass at design closure.

| Order | Sub-pass | Description | Effort | Rationale for position |
|---|---|---|---|---|
| 1 | 4.3.1 — Thread A | Per-chart range buttons on unemployment + improved empty-state | ~0.3 session | **SHIPPED 2026-04-29** |
| 2 | 4.3.6 — DEC-75 row-weight | `row_weight` field on metric registry. Reclassify LFP triplet to Lite, `jsa_vacancy_rate` to Context-only. Render switch in `centre.html`. Closes OI-23 in the same edit (trend-window bar promoted to page level). | ~0.2 session | **SHIPPED 2026-04-29 — `centre_page.py` v5 + `centre.html` v3.4** |
| 3 | 4.3.8 — Intent copy + trend-% display | (a) `LAYER3_METRIC_INTENT_COPY` constant — inline prose for all 10 existing + 6 catchment-ratio entries (covering DEC-74's two reversible pairs + 2 absolute ratios) + 4 Workforce supply context rows. Renderer reads `p.intent_copy` and renders silently if missing — catchment + workforce entries sit dormant until those sub-passes wire the rows. (b) Trend-window % change on each Full-weight chart — signed `+X.X% since YYYY` label top-right of the chart, plus running % from window-start in the Chart.js hover tooltip. Both update live when any range button changes (global or per-chart). Renderer-implementation choice within DEC-73 scope, same pattern as Thread A's per-chart overrides. Lite rows do NOT get the label (P-2: keeps with the no-trajectory framing). Neutral colour, no green/red valence. | ~0.4–0.5 session | **SHIPPED 2026-04-29 — `centre_page.py` v6 + `centre.html` v3.5** |
| 4 | 4.3.9 — DEC-76 Workforce supply context block | Render JSA IVI 4211 + 2411 + (NCVER if probe positive) + ECEC Award rates + Three-Day Guarantee. Default open. | ~0.3 session | **SHIPPED 2026-04-29 — `centre_page.py` v7 + `centre.html` v3.6.** JSA IVI rows defensive on table-name; renders deferred until wire-up follow-up. |
| 5 | 4.3.7 — DEC-74 perspective toggle | `reversible` + `pair_with` + `default_perspective` + `perspective_labels` fields. Render-time swap. Locked band-copy templates. | ~0.3 session | **SHIPPED 2026-04-29 — `centre_page.py` v7 + `centre.html` v3.6 (dormant; activates with 4.2-A.3).** |
| 6 | 4.3.2 — Thread B | SALM probe for LFP. Probe ~0.2 session; if positive, ingest ~0.5 session | ~0.7 session | **PROBE COMPLETE 2026-04-29 — conditional positive. SALM source publishes participation_rate alongside existing series; ingest scope can be extended (~0.5 session). LFP not blocking V1; SALM-extension deferred to V1.5 bundled with OI-19.** |
| 7 | 4.3.3 — Thread D probe | Confirm NCVER VET enrolments DB state (whether already ingested from earlier panel3 work) | ~0.1 session | **PROBE COMPLETE 2026-04-29 — data exists in `training_completions` (768 rows, state × remoteness × qualification × year, 2019–2024). Editorial disposition: DEC-36 stands; data kept at Industry view (state-level lacks current-tightness immediacy that DEC-76 admission requires). OI-20 NCVER bullet closed.** |
| 8 | 4.3.4 — Calibration function | `catchment_calibration.py` with `calibrate_participation_rate()`. STD-34 already locked. | ~0.3 session | Data plumbing for Layer 4.2-A. Cannot ship before this lands. |
| 9 | 4.3.5 — Schema migration | 7 new columns on `service_catchment_cache` (ratio metrics + calibration metadata) | ~0.1 session | Data plumbing. Trivial migration. |

### Layer 4.2-A sub-passes (unchanged)

| Sub-pass | Effort |
|---|---|
| 4.2-A.1 — `layer2_5_catchment_cache_apply.py` populates ALL columns including the four ratios | ~1.3 sessions |
| 4.2-A.2 — `layer3_x_catchment_metric_banding.py` bands the four new metrics | ~0.4 session |
| 4.2-A.3 — `centre.html renderCatchmentMetricsCard()` — full Position-row treatment for the four metrics, with perspective toggle on the two reversible pairs (DEC-74) and Full row-weight (DEC-75) | ~0.5 session |

### Promoted from Phase 2 (already locked into V1)

| Item | Origin | State |
|---|---|---|
| Births data ingest (Layer 2 Step 8) | 2026-04-26b | COMPLETE |
| Layer 2 Step 5b (Census 2021 income subset) — Adjustment 2 | 2026-04-27 | COMPLETE |
| Layer 2 Step 5c (JSA Internet Vacancy Index) — Adjustment 3 | 2026-04-27 | COMPLETE |
| Layer 2 Step 1c (SA2 polygon overwrite) | 2026-04-28b | COMPLETE — closes systemic data-quality bug affecting ~8,000 services |
| Visual consistency audit (DEC-71) | 2026-04-28b | COMPLETE |
| Compliance cadence formalisation (Phase 4) | 2026-04-26b | PENDING |
| Commentary engine (Phase 7) | 2026-04-26b | PENDING |
| Starting Blocks via commercial scraping vendor (Phase 8) | 2026-04-26b | PILOT COMPLETE; integration pending |

---

## 2. Deferred (P2 / V1.5)

| Phase | Description | Reason for deferral | Tracked as |
|---|---|---|---|
| **Layer 4.4** | NES, parent-cohort 25–44, schools ingests at SA2 | Pure deepening; V1 ships without. NES required for participation-rate calibration's NES nudge. | **OI-19** — promote immediately post-V1 |
| **Workforce supply context enrichments** | SEEK-by-SA2 vacancy density + salary; NCVER VET enrolments at SA2/remoteness; ANZSCO 4211/2411 advertised wages | V1 Workforce supply context block (DEC-76) starts with state-level JSA IVI; deeper data is V1.5 enrichment | **OI-20** |
| **Centre-page tab: quality elements** | NQS quality detail + regulatory history move from inline-NOW to a dedicated tab | Inline-NOW remains workable for V1; tab requires tabbing-model review | **OI-21** |
| **Centre-page tab: ownership / corporate detail** | Cross-reference into operator graph as a dedicated tab | Operator-page link suffices for V1; tab requires tabbing-model review | **OI-22** |
| Phase 3 — Industry view + Module 1 Market | Multi-series sector dashboard | Not blocking centre/operator V1 ship | — |
| Phase 5 — Pricing module proper | Real pricing data and Now/Trajectory/Position rendering | Pricing data sourcing depends on Phase 8 commercial scraper | — |
| Phase 6 — Excel export endpoints | Per-page export | Not blocking V1 | — |
| Layer 3b — RWCI composite | Regional Workforce Constraint Index | DEC-65 D2 deferred | — |
| Adjustment 1 (SA4 SALM extension) | Local-vs-Regional gap signal | DEC-52 — JSA SALM does not publish at SA4; ABS Cat 6202.0 path is P2 | — |
| JSA IVI Northern Australia sheet | Geographic granularity addition | DEC-55 — marginal V1 value | — |
| Cross-product Census rate reconciliation | Reconcile `ee_lfp_persons_pct` with T33-derived | DEC-61 — methodologically distinct, intentionally not reconciled | — |

### Withdrawn from V1

| Item | Origin | Reason |
|---|---|---|
| **Phase 1.7 Kintell → Novara rebrand** | DEC-29 (original) | Withdrawn 2026-04-28b. The project's framing has shifted; the rebrand decision is not active. See DEC-29. |

---

## 3. Layer 4.3 design decisions — closure status

The Layer 4.3 design extension surfaced four decisions plus §9.4. As of 2026-04-29, all are closed. The recon design doc has been regenerated as `recon/layer4_3_design.md` v1.1 absorbing the closures.

| Decision | Closure | Detail |
|---|---|---|
| G1 (supply_ratio vs child_to_place rendering) | Merged with G2 → **DEC-74** | Perspective-toggle pattern on reversible ratio pairs |
| G2 (demand_supply direction) | Merged with G1 → **DEC-74** | Same toggle mechanism |
| G3 (calibration as working standard) | **STD-34 locked** | Calibration discipline; `catchment_calibration.py` is the named module |
| G4 (Layer 4.4 deferral) | Closed → **OI-19** | NES + parent-cohort + schools ingests deferred to V1.5 |
| G5 (added during closure session — visual weight by data depth) | → **DEC-75** | Three row weights: Full / Lite / Context-only |
| Thread D (added during closure session — workforce supply context) | → **DEC-76** | New Position-level block; default open; state-level rows only |
| §9.4 (project doc restructuring) | Implicitly resolved | The 2026-04-28 restructure produced this doc set |

---

## 4. Parallel work streams

### Daily-rate data acquisition (separate chat)
A parallel work stream is finalising daily-rate data acquisition (vacancy availability, daily-rate pricing, and adjacent feeds). Expected outputs:
- A new working standard around scrape cadence / vendor selection formalisation
- A new decision tree on the daily-rate ingest pipeline
- New Layer 2 step entries
- **A centre-page integration point** — daily-rate data renders somewhere on the centre page (likely a new metric registry entry plus a Position-row slot, or a dedicated block similar in pattern to the Workforce supply context block per DEC-76). Specific render shape to be designed when the data lands; the renderer-best-practice infrastructure shipped by Layer 4.3 sub-passes 2–5 (re-sequenced) sets up the slot without retrofit.

When that work merges back, its standards and decisions enter `STANDARDS.md` and `DECISIONS.md` with the next sequential IDs (STD-36+, DEC-77+ — STD-35 already taken by the cross-session continuity standard added 2026-04-29 continued). A consolidation pass will reconcile any overlap with existing entries and decide where the centre-page integration sits in the sub-pass / phase ordering (probably a new Layer 4.5 or a Phase 5 promotion from V1.5).

### Starting Blocks integration
The Starting Blocks pilot (separate `MODULE_SUMMARY_*.md`) is production-ready in isolation. Integration into `kintell.db` requires four steps in order:
1. Lift the pilot folder onto local disk (off Google Drive). ~½ day.
2. Run identity resolution against `services` to produce a join coverage report. ~½ day.
3. Stress-test the pipeline at scale (one high-density SA2). ~½ day.
4. Decide multi-source posture (Starting Blocks alone for V1, or commission Care for Kids reconnaissance now).

These are scheduled within Phase 8.

---

## 5. Housekeeping items

These are not phases but tracked work. Promoted to P1.5 / P2 as appropriate.

| Item | Priority | Notes |
|---|---|---|
| Backup pruning in `data/` | P1.5 | Cumulative ~5.0 GB; approaching git-operation timeout threshold (OI-12) |
| Backfill audit for DD/MM/YYYY date parsing fix | P2 | Open question whether other code paths besides `centre_page.py` had the same bug (OI-14) |
| Backfill audit for ARIA+ format mismatch | P2 | Same — any other code consuming `aria_plus` (OI-15) |
| 18 services with no lat/lng — geocoding fix | P2 (deferred per DEC-63) | ~½ session if attempted (OI-01) |
| 2 null-island services — manual cleanup | P2 (deferred per DEC-63) | Triage in one sitting (OI-02) |
| `provider_management_type` enum normalisation | P2 | "Independent schools" (plural, ambiguous) appears alongside cleaner values (OI-10) |
| `recon/layer4_3_design.md` v1.0/v1.1 reconciliation | P2 | Diff v1.1 unchanged sections against v1.0 in git history when next opening repo (OI-17) |

---

## 6. Doc set housekeeping

The 2026-04-28 restructure produced the 12-doc set. The 2026-04-29 closure session updated DECISIONS, STANDARDS, OPEN_ITEMS, ROADMAP, PROJECT_STATUS, and PHASE_LOG to reflect Layer 4.3 design closure.

Outstanding (low priority):
- DEC-29 verbatim text recovery if a recoverable monolith surfaces (OI-16).
- `recon/layer4_3_design.md` v1.0/v1.1 unchanged-section reconciliation (OI-17).

---

## 7. Sequencing rule of thumb

When in doubt, the order is:
1. Probe (read-only inspection)
2. Design doc (decisions surfaced)
3. Decision closure (entries in `DECISIONS.md`)
4. Apply scripts (mutating; dry-run default)
5. Validation / spotcheck
6. Render (page surface code)
7. Doc update

Any layer or sub-pass that skips probe/design risks the rework cost that DEC-65 was created to prevent. P-1 (Probe before code) is the operative principle.
