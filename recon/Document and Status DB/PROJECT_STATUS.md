# Project Status

The current state of the Kintell project. What has shipped, what is in flight, what is next. Refreshed every session that ships work.

This document is present-tense. For forward-looking scope, see `ROADMAP.md`. For session history, see `recon/PHASE_LOG.md`. For known issues, see `OPEN_ITEMS.md`.

**Last updated:** 2026-04-29
**Current phase:** Phase 2.5 (Centre page buyer's-lens enhancement)
**Active layer:** Layer 4.3 (sub-pass 4.3.1 Thread A shipped; 8 sub-passes remaining)

---

## Centre page — current state

`centre_page.py` v4 (Python backend) + `centre.html` v3.3 (renderer) + payload schema `centre_payload_v4`.

The centre page renders the three-temporal-mood pattern (DEC-32) at the leaf level:

- **NOW block:** NQS rating + cadence (five-state classification per DEC-34); places + service sub-type + management type; catchment context (SEIFA + ARIA + SA2); tenure (greenfield/brownfield + transfer history).
- **POSITION block:** 10 Layer 3-backed metrics across two cards (Population, Labour Market). Each row currently shows trajectory chart (Chart.js), cohort distribution histogram (bespoke SVG), gradient decile strip, low/mid/high band chips, and DER+COM badges.
- **Trend window:** global 3Y/5Y/10Y/All button strip applied per-metric relative to each series' most recent point (DEC-73). The unemployment row carries per-chart 1Y/2Y override buttons (Layer 4.3 sub-pass 4.3.1 Thread A) — click-to-toggle; falls back to the global window when cleared.
- **Empty-state copy:** unemployment rows for SA2s where SALM does not publish render a named small-population-suppression note rather than a silent em-dash (Layer 4.3 sub-pass 4.3.1 Thread A).

What is **not** yet on the centre page: catchment-level supply ratio, competitor density, the four catchment ratios from the Layer 4.2-A scope, the Workforce supply context block (DEC-76), the perspective toggle on reversible ratios (DEC-74), the row-weight reclassification of the LFP triplet to Lite (DEC-75), and the inline `LAYER3_METRIC_INTENT_COPY` constant. All of these are the Layer 4.3 sub-passes 4.3.2–4.3.9 + Layer 4.2-A implementation queue.

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
| Layer 4.3 — Implementation (sub-passes 4.3.2–4.3.9) | IN PROGRESS — 8 sub-passes remaining, ~2.2 sessions (see ROADMAP.md §1) |
| Layer 4.4 — New ingests (NES, parent-cohort, schools) | DEFERRED to V1.5 (OI-19) |
| Layer 5 — Doc restructuring | COMPLETE 2026-04-28 |

---

## What's next

In recommended order:

1. **Layer 4.3 implementation** — 8 sub-passes remaining per the revised ROADMAP §1. Total ~2.2 sessions remaining. Sub-pass ordering:
   - 4.3.1 Thread A (per-chart range buttons on unemployment) — **SHIPPED 2026-04-29**
   - 4.3.2 Thread B (SALM probe for LFP) — **next**
   - 4.3.3 Thread D probe (NCVER VET enrolments DB state — could promote OI-20's NCVER row to V1)
   - 4.3.4 Calibration function (`catchment_calibration.py`)
   - 4.3.5 Schema migration (7 new columns on `service_catchment_cache`)
   - 4.3.6 DEC-75 row-weight reclassification (LFP triplet to Lite)
   - 4.3.7 DEC-74 perspective toggle on reversible ratios
   - 4.3.8 `LAYER3_METRIC_INTENT_COPY` constant + render slot
   - 4.3.9 DEC-76 Workforce supply context block (default open)
2. **Layer 4.2-A implementation** (~2.2 sessions). Gated on 4.3 calibration function landing + Layer 2.5 cache build.
3. **Layer 4.4** (~1.5 sessions, V1.5 — OI-19) — NES + parent-cohort + schools ingests. Closes the calibration function's documented `nes_share_pct` gap.

V1 path remaining: ~5.9 sessions if all of Layer 4.3 (remainder) + 4.2-A + 4.4 land. L4.4 is pure deepening; V1 ships without it if needed.

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

All pushed to origin (assumed once this session's commit lands).

---

## Parallel work streams

A separate chat is finalising daily-rate data acquisition. When merged, it will likely add: a working standard around scrape cadence / vendor selection (STD-35), a decision tree on the daily-rate ingest pipeline (DEC-77+), new Layer 2 step entries.

Starting Blocks pilot is production-ready in isolation. Integration into `kintell.db` is Phase 8, sequenced as: lift folder off Google Drive → identity resolution → scale stress-test → multi-source posture decision. See `ROADMAP.md` §4.

---

## Open items summary

See `OPEN_ITEMS.md` for the full list. Headlines:

- **OI-12 (Medium):** backup pruning needed — cumulative ~5.0 GB approaching git-timeout threshold.
- **OI-19 (Medium, new 2026-04-29):** Layer 4.4 ingests deferred to V1.5; NES required to close calibration function's documented gap.
- **OI-20 (Low, new 2026-04-29):** Workforce supply context enrichments — SEEK-by-SA2, NCVER probe, advertised wages.
- **OI-23 (Low, new 2026-04-29):** global trend-window bar disappears when Population card has no live data; Thread A makes the brittleness more material. Fix in next Population/Labour-Market layout work (likely sub-pass 4.3.6).
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
| `DECISIONS.md` | ADR-style decisions 1–76 | 2026-04-29 (DEC-74/75/76 added) |
| `ARCHITECTURE.md` | Visual systems, palette, page topology, layer architecture | 2026-04-28 |
| `DATA_INVENTORY.md` | Source files, DB tables, refresh policy | 2026-04-28 |
| `ROADMAP.md` | V1 scope, deferred work, sequencing | 2026-04-29 |
| `OPEN_ITEMS.md` | Known bugs, deferred fixes, residuals | 2026-04-29 (OI-19/20/21/22 added; OI-18 closed) |
| `GLOSSARY.md` | Terms and acronyms | 2026-04-28 |
| `recon/PHASE_LOG.md` | Append-only session history | 2026-04-29 (entry appended) |
| `CONSOLIDATION_LOG.md` | One-time record of merges in the 2026-04-28 restructure | 2026-04-28 |

The earlier `remara_project_status_*.txt` monolith chain remains in place for historical reference. It is no longer authoritative.
