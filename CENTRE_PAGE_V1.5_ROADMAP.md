# Centre Page V1.5 Roadmap

*Last updated: 2026-05-04 (session start). Source of truth for centre-page V1.5 scope. The on-disk version supersedes any project-knowledge copy if they disagree.*

## Purpose

Single source of truth for **centre-page** V1.5 work. Consolidates known OIs, scraper-derived fields, subtype-correct denominators, DEC follow-ups, and renderer polish into a dependency-ordered queue: ingest → banding → render. Parent ROADMAP.md references this doc but does not duplicate it.

**Out of scope:** operator-page work (separate program; needs its own scoping pass), industry view (DEC-36), the daily-rate parallel stream itself (only its centre-page integration is referenced).

## V1 baseline

V1 shipped 2026-05-03 evening. HEAD: `bcdf84c` (pending operator confirmation via `git log --oneline -1`). Centre-page state at HEAD:

- `centre_page.py` v20 + `centre.html` v3.24 + payload schema `centre_payload_v6`.
- 4 catchment metrics at FULL weight with quarterly trajectories and event overlays.
- Industry-absolute thresholds (DEC-77) live on 3 of 4 catchment ratios in supply-vs-demand language.
- About-this-measure panels on each catchment Full row.
- DER tooltip surfaces calibration metadata (Layer 4.2-A.4).
- Workforce Supply Context block live with 4 indicators.
- 25 outlier SA2s with zero/sparse pop_0_4 coverage tracked as OI-33 (no V1.5 action unless they gain centre-anchor activity).

## Scope assumptions

1. **LDC-first.** V1.5 closes LDC gaps. OSHC lifted where the data lift is cheap (subtype-correct denominator via the schools ingest already in OI-19). PSK / FDC stay on shared `pop_0_4` denominator until V2 unless an ingest covers them for free.
2. **Daily-rate is scoped but gated.** Treated as a parallel stream per ROADMAP §5. Render integration sequenced behind STD-36+ stabilisation; does not block Phase B/C of this roadmap.
3. **Probe before code (DEC-65).** Every Phase A item names its probe gate.
4. **Renderer touch = server restart.** Any `centre_page.py` change requires `review_server.py` restart (Python module cache).

## Phase A — Ingest (Layer 4.4 bundle + adjacencies)

| ID | Item | Origin | Effort | Probe gate (DEC-65) |
|---|---|---|---|---|
| A1 | ABS ERP backward extension (pre-2019 `pop_0_4`) | OI-30 folded into OI-19 | ~0.3 sess | ASGS-edition concordance probe: confirm 2011/2016/2021 ASGS treatment for SA2 codes pre-2019; concordance step required if codes shifted. |
| A2 | NES share at SA2 | OI-19 | ~0.4 sess | Source probe: Census 2021 TSP T13 vs equivalent table; SA2-level granularity confirmed. |
| A3 | Parent-cohort 25-44 population at SA2 | OI-19 | ~0.3 sess | Source probe: ABS ERP age-band extract availability at SA2. |
| A4 | Schools at SA2 | OI-19 | ~0.4 sess | Source probe: ACARA at school level vs state-DE enrolment files; SA2 attribution method (school geocode → SA2). |
| A5 | Subtype-correct denominators | Standing item | ~0.3 sess | Probe whether `pop_0_4` is wrong for FDC / PSK or only OSHC. OSHC clearly wants school-age pop (depends on A4); FDC is in-home (catchment match may be genuine); PSK age-band shifts. |
| A6 | SALM-extension (participation rate) | OI-19, OI-06 | ~0.4 sess | Source probe: SALM monthly/quarterly availability for participation_rate at SA2. |
| A7 | SEEK + advertised wages | OI-19, OI-20 | ~0.3 sess | Residual from 4.3.3 NCVER probe. Opportunistic; pull in if A1–A6 ships under budget. |
| A8 | Daily-rate scraper integration | Standing parallel | gated | Gated on STD-36+ parallel-stream stability. Out of V1.5 critical path. |
| A9 | Under-5 growth (5y) data prep | OI-09 | ~0.2 sess | Only if growth metric requested by operator post-V1. Currently a deferred placeholder. |

**Phase A core (A1–A6):** ~2.1 sess. Aligns with parent ROADMAP V1.5 estimate.

## Phase B — Banding

| ID | Item | Depends on | Effort | Notes |
|---|---|---|---|---|
| B1 | Promote LFP triplet to FULL weight | A6 | ~0.2 sess | Per DEC-75. Reverses V1 Lite reclassification once SALM monthly/quarterly data lands. |
| B2 | Band NES share | A2 | ~0.2 sess | New Layer 3 metric. Cohort-only initially; industry threshold candidacy TBD. |
| B3 | Band parent-cohort 25-44 | A3 | ~0.2 sess | Primary use is calibration input; may render as Lite or Context-only depending on cohort fit. |
| B4 | Band school-supply ratios at SA2 | A4 | ~0.3 sess | New metric family. Cohort + industry-band candidacy review. |
| B5 | Re-band OSHC `supply_ratio` with subtype-correct denominator | A5 | ~0.2 sess | Distribution shifts under new denominator; existing thresholds may need re-derivation. |
| B6 | Industry-threshold review for `sa2_demand_supply` | OI-26 (open under DEC-77) | ~0.2 sess | Watch for saturated-catchment false positives. Trigger criterion in §"Open questions". |
| B7 | Band daily-rate metrics | A8 | TBD | Only when A8 lands. |

**Phase B core (B1–B5):** ~1.1 sess.

## Phase C — Render

| ID | Item | Depends on | Effort | Notes |
|---|---|---|---|---|
| C1 | OI-31 click-to-detail on event overlay | None (V1 plumbing in `p.centre_events`) | ~1.0 sess | Canvas-pixel → DOM overlay translation. Largest renderer piece. Independent of A/B. |
| C2 | New Full rows for promoted/added metrics | B1–B5 | ~0.4 sess | LFP (Full), NES, school-supply, OSHC reweighted. Reuses existing `_renderFullRow` machinery. |
| C3 | Absolute-change alongside trend % on trajectory chart | None (renderer-only) | ~0.5 hr | Show "+12 places, +1 centre" alongside trend %. Orphaned in stale parent-ROADMAP §3 as "OI-32"; that ID is now taken by closed explainer-text item — needs fresh OI ID at next consolidation. |
| C4 | Quality elements tab | OI-21 | ~1.0 sess | New tab structure. Deferred V2 candidate; included here for visibility. |
| C5 | Ownership / corporate tab | OI-22 | ~1.0 sess | New tab structure. Deferred V2 candidate; included here for visibility. |
| C6 | OI-09 growth metric render | A9 + B-pass | ~0.2 sess | Replace deferred placeholder with real Full row. |
| C7 | Daily-rate render integration | A8, B7 | TBD | Gated on STD-36+ stability. |

**Phase C minimum (C2 + C3):** ~0.5 sess. With OI-31: ~1.5 sess.

## Recommended V1.5 ship slice (~3.3 sessions)

V1.5 budget per parent ROADMAP §3 = ~3 sessions. Tight but workable:

- **A1–A6** (~2.1 sess) — full Phase A core
- **B1–B5** (~1.1 sess) — full Phase B core
- **C2 + C3** (~0.5 sess) — minimum render to surface new metrics

**Total:** ~3.3 sess.

**Deferred from V1.5 ship slice:**

- **C1 (OI-31)** — substantial standalone renderer feature; ship as V1.5+ once V1.5 core lands.
- **C4 / C5 (OI-21, OI-22)** — new-tab work; V2 candidates.
- **A7 (SEEK + wages)** — opportunistic; pull in if A1–A6 lands under budget.
- **A8 / B7 / C7 (daily rate)** — gated on parallel stream.
- **A9 / C6 (growth)** — opportunistic; gated on operator demand.

## First-piece recommendation

**A1 — ABS ERP backward extension probe.** Reasons:
- Probe-first per DEC-65; lowest-cost path into Phase A.
- OI-30 already raised the question; probe artefact (`recon/oi30_asgs_coverage_probe.md`) has the working set.
- Backward extension widens `pop_0_4` coverage for trajectory charts already shipped in V1, so any uplift visibly improves V1 surfaces.
- ASGS-edition concordance pattern reused by A4 (schools) — invest the discipline once.

## Open questions (resolve before code in each phase)

1. **A1 concordance approach.** ABS publishes ERP under different ASGS editions (2011 / 2016 / 2021). Probe required before ingest scaffolding.
2. **A4 schools data source.** ACARA at school level vs state-DE enrolment by school — confirm SA2 attribution method.
3. **A5 FDC / PSK denominators.** Probe whether `pop_0_4` is wrong for these or only OSHC.
4. **B6 review trigger.** Agreed criterion for "saturated-catchment false positive" — propose: trigger after first operator complaint OR after manual review of ~10 saturated centres, whichever first.
5. **C3 OI assignment.** Mint new OI ID at next consolidation. Acceptance: trajectory chart shows "+N places, +M centres" alongside the existing trend % across all 4 catchment metrics where event-overlay data exists.

## Acceptance criteria (where obvious)

- **Phase A items:** new ingest table populated; `audit_log` row landed per STD-30; row count matches probe expectation; backup taken pre-mutation.
- **Phase B items:** Layer 3 banding produces decile + band assignments for the new metric across all qualifying SA2s; cohort sizes sane; `LAYER3_METRIC_META` entry committed.
- **C2 (new Full rows):** new metric appears at expected page position; trajectory + cohort histogram + decile strip + band chips all render; about_data panel renders if explainer copy supplied; `centre.html` version bumped; `review_server.py` restarted; smoke-tested on at least one LDC service in a populous SA2 and one in a sparse SA2.

## Sequencing rules (inherited)

- Probe before code (DEC-65) — applies hardest to A1, A4, A5.
- Renderer-best-practice ahead of plumbing.
- STD-30 pre-mutation discipline for any DB write.
- STD-10 patcher anchors use `\n` not `\r\n`.
- STD-12 line-ending detection at runtime.
- STD-13 Win11-safe orphan-Python detection for any process work.
- STD-35 end-of-session monolith + on-disk doc refresh + project-knowledge upload.
- STD-36 session-start uploads (added 2026-05-04).
- Two-commit DEC-22 pattern for ingest → render pairs unless verified together.
- `centre_page.py` change → `review_server.py` restart (Python module cache).

## Items deliberately NOT in this roadmap

- Operator-page work (separate program).
- Industry view / NCVER pipeline (DEC-36).
- STD-36+ daily-rate parallel stream itself (only its centre-page integration is referenced as A8 / B7 / C7).
- Pure housekeeping: OI-13, OI-14, OI-15, OI-16, OI-17, OI-24, OI-28.
- DB backup pruning (OI-12).
- DEC-77 framework changes — DEC-77 is locked; only its OI-26 follow-up is in scope (B6).
- OI-32 — closed (explainer text). The orphan "absolute change alongside %" carry-over from stale parent-ROADMAP §3 is C3 here, awaiting fresh OI ID.

## Doc-set integration

This document is the centre-page V1.5 source of truth. Update protocol:

- Parent `ROADMAP.md` references this doc but does not duplicate scope.
- `PROJECT_STATUS.md` notes the V1.5 phase pointer here.
- STD-35 end-of-session refresh applies — when a V1.5 piece ships, this doc updates first, then the Tier-2 docs reflect the change.
- DEC follow-ups (e.g. OI-26 under DEC-77) are tracked here under the relevant Phase B item rather than duplicated in DECISIONS.md.
