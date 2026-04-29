# Project Status

The current state of the Kintell project. What has shipped, what is in flight, what is next. Refreshed every session that ships work.

This document is present-tense. For forward-looking scope, see `ROADMAP.md`. For session history, see `recon/PHASE_LOG.md`. For known issues, see `OPEN_ITEMS.md`.

**Last updated:** 2026-04-29 (sub-pass 4.3.4 calibration function shipped)
**Current phase:** Phase 2.5 (Centre page buyer's-lens enhancement)
**Active layer:** Layer 4.3 (sub-passes 4.3.1 + 4.3.4 + 4.3.6 + 4.3.7 + 4.3.8 + 4.3.9 SHIPPED; 4.3.2 + 4.3.3 PROBE COMPLETE; 1 sub-pass remaining: 4.3.5)

---

## Centre page — current state

`centre_page.py` v8 (Python backend) + `centre.html` v3.9 (renderer) + payload schema `centre_payload_v4`.

The centre page renders the three-temporal-mood pattern (DEC-32) at the leaf level:

- **NOW block:** NQS rating + cadence (five-state classification per DEC-34); places + service sub-type + management type; **kinder recognition** (composite block with ACECQA flag + service-name regex match + four-state derived headline; mirrors operator-page treatment); catchment context (SEIFA + ARIA + SA2); tenure (greenfield/brownfield + transfer history).
- **POSITION block:** 10 Layer 3-backed metrics across two cards (Population, Labour Market). Visual treatment is per-metric per DEC-75 — `row_weight: "full" | "lite" | "context"` on the metric registry switches the renderer:
  - **Full** (7 metrics — under-5 count, total population, births, unemployment, income trio): trajectory chart (Chart.js) + cohort distribution histogram (bespoke SVG) + gradient decile strip + low/mid/high band chips + inline intent copy + DER+COM badges.
  - **Lite** (3 metrics — LFP triplet): decile strip + chips + "as at YYYY" stamp + inline intent copy + DER+COM badges. No trajectory chart, no cohort histogram. Honest absence (P-2) — 3 Census points is not a trajectory.
  - **Context-only** (1 metric — `jsa_vacancy_rate`): single-fact line + state-level stamp + inline intent copy. Branch wired but currently dormant — the metric is `status='deferred'` and relocates to the Workforce supply context block in sub-pass 4.3.9 (DEC-76).
- **Workforce supply context block** (sub-pass 4.3.9, DEC-76): default-open page-level section between Labour Market and QA cards. Four rows — Child carer vacancy index (ANZSCO 4211, JSA IVI state-monthly), ECT vacancy index (ANZSCO 2411, JSA IVI), ECEC Award minimum rates (Fair Work, national), Three-Day Guarantee policy (national, effective Jan 2026). Each row carries scope stamp + intent copy. JSA IVI rows render with state-level sparkline when data is live; render as deferred when the IVI table-name wire-up is pending (one-line follow-up).
- **Perspective toggle infrastructure** (sub-pass 4.3.7, DEC-74): renderer hooks for reversible ratio pairs. Reads four optional fields on metric registry (`reversible`, `pair_with`, `default_perspective`, `perspective_labels`); locked band-copy templates per direction. **Dormant in V1** — no metric currently carries `reversible: true`. Activates per row when catchment ratios arrive in Layer 4.2-A.3 with no further renderer changes.
- **Inline intent copy** (sub-pass 4.3.8): one-sentence interpretive prose per metric, italic muted-color, beneath the band chips. Tells the credit-lens reader why the metric matters for THIS centre's risk picture. Powered by the `LAYER3_METRIC_INTENT_COPY` constant in `centre_page.py` (22 entries: 10 live Position metrics + 6 catchment-ratio entries dormant for Layer 4.2-A.3 + 4 workforce supply entries live in 4.3.9 block).
- **Trend window:** global 3Y/5Y/10Y/All button strip applied per-metric relative to each series' most recent point (DEC-73). The bar renders at page level above both Position cards (sub-pass 4.3.6 fix for OI-23). The unemployment row carries per-chart 1Y/2Y override buttons (sub-pass 4.3.1) — click-to-toggle; falls back to the global window when cleared.
- **Trend-window % change** (sub-pass 4.3.8, prominence bumped 4.3.bundled-round): each Full-weight chart shows a `+X.X% since YYYY` label top-right (13px, value semibold), plus the running % from window-start in the Chart.js hover tooltip (12.5px body). Both update live when any range button changes. Lite rows do NOT carry the label (P-2: keeps with the no-trajectory framing).
- **Empty-state copy:** unemployment rows for SA2s where SALM does not publish render a named small-population-suppression note rather than a silent em-dash (sub-pass 4.3.1).

What is **not** yet on the centre page: catchment-level supply ratio, competitor density, the four catchment ratios from the Layer 4.2-A scope. All on the Layer 4.2-A implementation queue (gated on 4.3.4 calibration function landing + Layer 2.5 cache build).

---

## Phase 2.5 — status by layer

| Layer | Status |
|---|---|
| Layer 1 — Recon + silent-bug audit | COMPLETE 2026-04-26 |
| Layer 2 — Data ingest (Steps 1–8 + 1b + 1c) | COMPLETE through Step 1c |
| Layer 2.5 — Catchment cache build | NOT STARTED — gated on Layer 4.3 calibration function landing |
| Layer 3 — Banding (`sa2_cohort` + `layer3_sa2_metric_banding`) | COMPLETE 2026-04-28 — 23,946 rows |
| Layer 3.x — Catchment metric banding | NOT STARTED — gated on Layer 2.5 |
| Layer 4 — Centre page Now + Position | COMPLETE through 4.2-B-fix2 |
| Layer 4.1 — Cohort scope inline (DEC-69) | COMPLETE 2026-04-28b |
| Layer 4.2-B — Trajectory + histogram + gradient | COMPLETE 2026-04-28b |
| Layer 4.2-B-fix — Chart.js trajectory swap (DEC-71) | COMPLETE 2026-04-28b |
| Layer 4.2-B-fix2 — Global trend window buttons (DEC-73) | COMPLETE 2026-04-28b |
| Layer 4.2-A — Catchment data on centre page | DESIGNED, awaiting Layer 4.3 + Layer 2.5 |
| **Layer 4.3 — Design v1.1** | **CLOSED 2026-04-29 — all decisions resolved (DEC-74, DEC-75, DEC-76; STD-34 locked; OI-19/20/21/22 logged)** |
| **Layer 4.3 sub-pass 4.3.1 — Thread A (per-chart range buttons + SALM-missing empty-state)** | **SHIPPED 2026-04-29 — `centre.html` v3.3** |
| **Layer 4.3 sub-pass 4.3.6 — DEC-75 row-weight reclassification (LFP triplet to Lite, jsa_vacancy_rate to Context-only) + OI-23 fix** | **SHIPPED 2026-04-29 — `centre_page.py` v5 + `centre.html` v3.4** |
| **Layer 4.3 sub-pass 4.3.8 — Inline intent copy + trend-window % change display (bundled)** | **SHIPPED 2026-04-29 — `centre_page.py` v6 + `centre.html` v3.5** |
| **Layer 4.3 sub-pass 4.3.9 — Workforce supply context block (DEC-76)** | **SHIPPED 2026-04-29 — `centre_page.py` v8 + `centre.html` v3.9** |
| **Layer 4.3 sub-pass 4.3.7 — Perspective toggle infrastructure (DEC-74)** | **SHIPPED 2026-04-29 — `centre_page.py` v8 + `centre.html` v3.9 (dormant — activates with 4.2-A.3)** |
| **Layer 4.3 sub-pass 4.3.2 — SALM LFP probe (Thread B)** | **PROBE COMPLETE 2026-04-29 — conditional positive; SALM-extension ingest deferred to V1.5 (bundled with OI-19). LFP triplet stays LITE for V1; promotes LFP-persons to FULL when V1.5 SALM-extension ships.** |
| **Layer 4.3 sub-pass 4.3.3 — NCVER VET enrolments probe (Thread D)** | **PROBE COMPLETE 2026-04-29 — data exists in DB at `training_completions` (768 rows, state × remoteness × qualification × year, 2019–2024); kept at Industry view per DEC-36 (state-level data without current-tightness immediacy). OI-20 NCVER bullet closed.** |
| **Layer 4.3 sub-pass 4.3.4 — Calibration function (`catchment_calibration.py`)** | **SHIPPED 2026-04-29 — `catchment_calibration.py` v1, STD-34 implementation. Standalone module; 13 hermetic unit tests pass. Sits ready for Layer 4.2-A.3 to consume.** |
| Layer 4.3 — Implementation (sub-passes 4.3.4 + 4.3.5) | IN PROGRESS — 2 sub-passes remaining, ~0.4 sessions (see ROADMAP.md §1) |
| Layer 4.4 — New ingests (NES, parent-cohort, schools) | DEFERRED to V1.5 (OI-19) |
| Layer 5 — Doc restructuring | COMPLETE 2026-04-28 |

---

## What's next

In recommended order:

1. **Layer 4.3 implementation** — 1 sub-pass remaining per the revised ROADMAP §1. Total ~0.1 sessions remaining.
   - 4.3.1 Thread A — **SHIPPED 2026-04-29**
   - 4.3.6 DEC-75 row-weight + OI-23 fix — **SHIPPED 2026-04-29**
   - 4.3.8 Inline intent copy + trend-% change (bundled) — **SHIPPED 2026-04-29**
   - 4.3.9 DEC-76 Workforce supply context block — **SHIPPED 2026-04-29**
   - 4.3.7 DEC-74 perspective toggle infrastructure — **SHIPPED 2026-04-29 (dormant; activates with 4.2-A.3)**
   - 4.3.2 Thread B SALM LFP probe — **PROBE COMPLETE 2026-04-29; SALM-extension queued for V1.5 with OI-19**
   - 4.3.3 Thread D NCVER probe — **PROBE COMPLETE 2026-04-29; data kept at Industry view per DEC-36; OI-20 NCVER bullet closed**
   - 4.3.4 Calibration function — **SHIPPED 2026-04-29 — `catchment_calibration.py` v1**
   - 4.3.5 Schema migration (7 new columns on `service_catchment_cache`) — **next**
2. **Layer 4.2-A implementation** (~2.2 sessions). Gated only on Layer 2.5 cache build now that 4.3.4 has shipped. Will activate the perspective toggle infrastructure shipped earlier this session.
3. **Layer 4.4 + V1.5 ingests** (~2.0 sessions, V1.5 — OI-19 + SALM-extension). NES + parent-cohort + schools, plus the SALM-extension ingest that promotes LFP-persons from LITE to FULL. Bundled because they share the "pure deepening" framing.

V1 path remaining: ~4.7 sessions if all of Layer 4.3 (remainder) + 4.2-A + V1.5 ingests land. V1 ships without V1.5 if needed.

---

## Database state

`data/kintell.db`: 35 tables. `audit_log`: 137 rows. `centre_payload` schema: v4. See `DATA_INVENTORY.md` for the full table list and refresh policy.

Cumulative backups in `data/`: ~5.0 GB. Pruning is now a P1.5 housekeeping task — see OI-12.

No DB mutations this session — design closure only, recorded in the doc set.

---

## Git state

Branch: `master`. Working tree expected clean after this session's commit lands. Recent commits in chronological order:
- Layer 4 (centre_page.py v3 + centre.html v2)
- Layer 4.1 (centre.html v2.1 cohort scope inline)
- Layer 2 Step 1c (overwrite rebuild + scripts + recon)
- Layer 4.2 pre-work (probe + design doc)
- Layer 4.2-B + B-fix + B-fix2 combined commit
- 2026-04-28 doc restructure (12-doc set)
- 2026-04-29 Layer 4.3 design closure: `recon/layer4_3_design.md` v1.1 + DEC-74 + DEC-75 + DEC-76 + STD-34 locked + OI-19 through OI-22 + ROADMAP/PROJECT_STATUS/PHASE_LOG updated
- 2026-04-29 Layer 4.3 sub-pass 4.3.1 (Thread A) apply: `centre.html` v3.3 + `recon/layer4_3_thread_a_probe.md` + OPEN_ITEMS.md (OI-23) + PROJECT_STATUS.md update
- 2026-04-29 Layer 4.3 sub-pass re-sequence: ROADMAP.md (re-ordered §1.3; daily-rate centre-page integration flagged in §4) + DECISIONS.md (DEC-65 amended) + OPEN_ITEMS.md (OI-24) + PROJECT_STATUS.md update
- 2026-04-29 Layer 4.3 sub-pass 4.3.6 (DEC-75 row-weight) apply: `centre_page.py` v5 + `centre.html` v3.4 + `recon/layer4_3_sub_pass_4_3_6_probe.md` + OPEN_ITEMS.md (OI-23 closed) + ROADMAP.md (4.3.6 SHIPPED) + PROJECT_STATUS.md update

All pushed to origin (assumed once this session's commit lands).

---

## Parallel work streams

A separate chat is finalising daily-rate data acquisition (vacancy availability + daily-rate pricing + adjacent feeds). When merged, it will likely add: a working standard around scrape cadence / vendor selection (STD-36+), a decision tree on the daily-rate ingest pipeline (DEC-77+), new Layer 2 step entries, and a centre-page integration point — likely a new metric registry entry or a dedicated block following the DEC-76 Workforce-supply pattern. Render slot is set up by Layer 4.3 sub-passes 2–5 (re-sequenced) with no retrofit needed.

Starting Blocks pilot is production-ready in isolation. Integration into `kintell.db` is Phase 8, sequenced as: lift folder off Google Drive → identity resolution → scale stress-test → multi-source posture decision. See `ROADMAP.md` §4.

---

## Open items summary

See `OPEN_ITEMS.md` for the full list. Headlines:

- **OI-12 (Medium):** backup pruning needed — cumulative ~5.0 GB approaching git-timeout threshold.
- **OI-19 (Medium, new 2026-04-29):** Layer 4.4 ingests deferred to V1.5; NES required to close calibration function's documented gap.
- **OI-20 (Low, new 2026-04-29):** Workforce supply context enrichments — SEEK-by-SA2, NCVER probe, advertised wages.
- **OI-23 CLOSED 2026-04-29:** trend-window bar promoted to page level above both Position cards in sub-pass 4.3.6.
- **OI-24 (Tracking, new 2026-04-29):** sub-pass dependency-ordering pass missing from design-closure protocol. Closed structurally by the DEC-65 amendment. Marker for traceability; close at next consolidation.
- **OI-04 (Medium):** ~20 services with bad lat/lng (0,0) need geocoding fix; deferred per DEC-63.
- **OI-18 closed 2026-04-29:** Layer 4.3 design decisions G1–G4 + §9.4 resolved.

---

## Doc set

The 12-document set produced by the 2026-04-28 restructure. The 2026-04-29 Layer 4.3 closure session touched 7 of these (PROJECT_STATUS, DECISIONS, STANDARDS, OPEN_ITEMS, ROADMAP, recon/PHASE_LOG, plus regenerated `recon/layer4_3_design.md` v1.1).

| File | Purpose | Last touched |
|---|---|---|
| `README.md` | Index and navigation | 2026-04-28 |
| `PROJECT_STATUS.md` | This file | 2026-04-29 |
| `PRINCIPLES.md` | Stable design principles | 2026-04-28 |
| `STANDARDS.md` | Categorised working standards 1–35 | 2026-04-29 (STD-34 locked, STD-35 added) |
| `DECISIONS.md` | ADR-style decisions 1–76 | 2026-04-29 (DEC-65 amended; DEC-74/75/76 added) |
| `ARCHITECTURE.md` | Visual systems, palette, page topology, layer architecture | 2026-04-28 |
| `DATA_INVENTORY.md` | Source files, DB tables, refresh policy | 2026-04-28 |
| `ROADMAP.md` | V1 scope, deferred work, sequencing | 2026-04-29 (sub-pass re-sequence; daily-rate centre-page integration flagged) |
| `OPEN_ITEMS.md` | Known bugs, deferred fixes, residuals | 2026-04-29 (OI-19/20/21/22/23/24 added; OI-18 closed) |
| `GLOSSARY.md` | Terms and acronyms | 2026-04-28 |
| `recon/PHASE_LOG.md` | Append-only session history | 2026-04-29 (entry appended) |
| `CONSOLIDATION_LOG.md` | One-time record of merges in the 2026-04-28 restructure | 2026-04-28 |

The earlier `remara_project_status_*.txt` monolith chain remains in place for historical reference. It is no longer authoritative.
