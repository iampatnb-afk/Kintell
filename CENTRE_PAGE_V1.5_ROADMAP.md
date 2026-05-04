# Centre Page V1.5 Roadmap

*Last updated: 2026-05-04 (end of full-day session). Source of truth for centre-page V1.5 scope. The on-disk version supersedes any project-knowledge copy if they disagree.*

## Purpose

Single source of truth for **centre-page** V1.5 work. Consolidates known OIs, scraper-derived fields, subtype-correct denominators, DEC follow-ups, and renderer polish into a dependency-ordered queue: ingest → banding → render. Parent ROADMAP.md references this doc but does not duplicate it.

**Out of scope:** operator-page work (separate program), industry view (DEC-36), the daily-rate parallel stream itself (only its centre-page integration is referenced).

## V1 baseline

V1 shipped 2026-05-03 evening (HEAD `bcdf84c`). End-of-day 2026-05-04 (HEAD `3ddcf18`):

- `centre_page.py` v20 + `centre.html` v3.25 + payload schema `centre_payload_v6`.
- 4 catchment metrics at FULL weight + 1 at CONTEXT.
- Industry-absolute thresholds (DEC-77) live on 3 of 4 catchment ratios.
- About-this-measure panels on each catchment Full row.
- DER tooltip surfaces calibration metadata (Layer 4.2-A.4) — **NES nudge now firing** post-A2 (closed STD-34 calibration dormancy).
- Workforce Supply Context block live with 4 indicators.
- Absolute-change ("+N places · +M centres") rendered alongside trend % on catchment trajectory charts (C3).
- `sa2_nes_share` registered in centre_page.py Layer 3 registries (data-side); **render-side OI-36 deferred to next session**.
- 25 outlier SA2s with zero/sparse pop_0_4 coverage tracked as OI-33.

## Scope assumptions

1. **LDC-first.** V1.5 closes LDC gaps. OSHC lifted where the data lift is cheap (subtype-correct denominator via the schools ingest already in OI-19).
2. **Daily-rate is scoped but gated.** STD-36+ parallel stream; render integration sequenced behind stabilisation.
3. **Probe before code (DEC-65).** Every Phase A item names its probe gate.
4. **Renderer touch = server restart** (Python module cache).
5. **Unit conventions explicit at scoping time.** Lesson banked from A2 v2/v3 epilogue.

## Phase A — Ingest (Layer 4.4 bundle + adjacencies)

| ID | Item | Origin | Effort | Probe gate (DEC-65) | Status |
|---|---|---|---|---|---|
| ~~A1~~ | ~~ABS ERP backward extension (pre-2019 `pop_0_4`)~~ | OI-30 | ~~~0.3 sess~~ | — | **DISSOLVED 2026-05-04** — see below |
| A2 | NES share at SA2 | OI-19 | ~0.5 sess | T10A+T10B from Census 2021 TSP | **CLOSED 2026-05-04** (commits `fdc85bd` v2 + `49ce9f1` v3 unit-fix) |
| A2-wire | NES into calibration via populate_service_catchment_cache.py | A2 | ~0.2 sess | populate_service_catchment_cache.py probe | **CLOSED 2026-05-04** (commit `bb21f66`) |
| A3 | Parent-cohort 25-44 population at SA2 | OI-19 | ~0.3 sess | Source probe: ABS ERP age-band extract availability at SA2 | open |
| A4 | Schools at SA2 | OI-19 | ~0.4 sess | Source probe: ACARA at school level vs state-DE enrolment files; SA2 attribution method | open |
| A5 | Subtype-correct denominators | Standing item | ~0.3 sess | Probe whether `pop_0_4` is wrong for FDC / PSK or only OSHC | open |
| A6 | SALM-extension (participation rate) | OI-19, OI-06 | ~0.4 sess | Source probe: SALM monthly/quarterly availability | open |
| A7 | SEEK + advertised wages | OI-19, OI-20 | ~0.3 sess | Opportunistic; pull in if A3-A6 ships under budget | open |
| A8 | Daily-rate scraper integration | Standing parallel | gated | Gated on STD-36+ stability | gated |
| A9 | Under-5 growth (5y) data prep | OI-09 | ~0.2 sess | Only if growth metric requested post-V1 | open |
| A10 | T08 Country of Birth at SA2 | 2026-05-04 scoping | ~0.3 sess | T08 from same TSP zip (already on disk) | **PHASE 2 — opportunistic post-NES render** |

### A1 dissolution note (2026-05-04)

Read-only probes (`probe_a1_pop04_coverage.py`, `probe_a1_filter_source.py`, `probe_a1_scoping.py`, `probe_a1_sources.py`) established that:

- `abs_sa2_erp_annual` already has rows for 2011/2016/2018, but the source Excel (`abs_data/Population and People Database.xlsx`) publishes `'-'` (suppressed/unavailable) for column `Persons - 0-4 years (no.)` in those years. The DB NULL rows are honest reflections of the ABS source, not a code defect.
- 6 dense annual points for `pop_0_4` is the actual source ceiling, not a 6-year window imposed in code. Documented in Layer 4.2 probe (2026-04-28b) — rediscovery cost ~30 min and triggered the "search project knowledge before probing" lesson.
- `abs_sa2_births_annual` provides 14 continuous annual points (2011–2024) — the existing continuous-historical signal at the centre level.
- Per DEC-75, ≥5 dense series points qualifies for Full weight; the under-5 row is already correctly rendered as Full.

**Disposition:** A1 dropped from V1.5 ship slice. If pre-2019 SA2 under-5 figures become required, three forward paths exist (Census 2011/2016 SA2 age tables as separate ingest; demographic derivation from births × cohort-survival; ABS TableBuilder pull). None V1.5-critical.

### A2 closure note (2026-05-04)

A2 shipped end-to-end:
- **Source:** Census 2021 TSP `2021_TSP_SA2_for_AUS_short-header.zip` (already on disk). Tables T10A (`Uses_Engl_only_*`) + T10B (`Tot_*`, `Lang_used_home_NS_*`).
- **Formula:** `nes_pct = ((Tot - Uses_Engl_only - Lang_used_home_NS) / Tot) * 100`
- **Storage:** `abs_sa2_education_employment_annual.census_nes_share_pct` as percentage (0-100) per `census_*_pct` convention. v2 stored as fraction; corrected to percentage in v3 (commit `49ce9f1`) to match render expectations.
- **Wire:** `populate_service_catchment_cache.py` reads value from DB, divides by 100, passes to `calibrate_participation_rate()` (which preserves STD-34 fraction thresholds). Calibration nudge live: high-NES catchments get −0.02 nudge.
- **National 2021:** 22.28% (matches published ABS 22-24% band).
- **Verification SA2s:** Bayswater Vic 31.07% (rate 0.50→0.48), Bondi Junction-Waverly NSW 23.58% (rate 0.54 unchanged, mid no-nudge), Bentley-Wilson-St James WA 37.55% (rate 0.48→0.46).

**DEC-78 candidate flagged**: NES storage convention at SA2 = percentage; wire boundary divides for calibration. Not promoted yet — confirm convention with A3/A4/A5 next session.

**Phase A core (A3–A6, post-A1 dissolution + A2 done):** ~1.4 sess.

## Phase B — Banding

| ID | Item | Depends on | Effort | Notes | Status |
|---|---|---|---|---|---|
| B1 | Promote LFP triplet to FULL weight | A6 | ~0.2 sess | Per DEC-75. Reverses V1 Lite reclassification once SALM monthly/quarterly data lands. | open |
| B2 | Band NES share | A2 | ~0.2 sess | New Layer 3 metric. Cohort=state_x_remoteness. | **CLOSED 2026-05-04** (commit `d02e26e`; 2,417 rows) |
| B3 | Band parent-cohort 25-44 | A3 | ~0.2 sess | open |
| B4 | Band school-supply ratios at SA2 | A4 | ~0.3 sess | New metric family. | open |
| B5 | Re-band OSHC `supply_ratio` with subtype-correct denominator | A5 | ~0.2 sess | open |
| B6 | Industry-threshold review for `sa2_demand_supply` | OI-26 (open under DEC-77) | ~0.2 sess | Trigger criterion in §"Open questions". | open |
| B7 | Band daily-rate metrics | A8 | TBD | Only when A8 lands. | gated |

**Phase B core (B1, B3-B5, post-B2 done):** ~0.9 sess.

## Phase C — Render

| ID | Item | Depends on | Effort | Notes | Status |
|---|---|---|---|---|---|
| C1 | OI-31 click-to-detail on event overlay | None (V1 plumbing in `p.centre_events`) | ~1.0 sess | Largest renderer piece. Independent of A/B. | open |
| C2 | New Full rows for promoted/added metrics | B1–B5 | ~0.4 sess | LFP (Full), school-supply, OSHC reweighted. Reuses existing `_renderFullRow` machinery. | open |
| C2-NES | NES row in Catchment Position card | B2 | ~0.3 sess | **Data-side closed 2026-05-04** (commit `3ddcf18`). **Render-side OI-36 OPEN.** centre.html hardcodes catchment rows; needs explicit NES row addition. | partial |
| C3 | Absolute-change alongside trend % on trajectory chart | None | ~0.5 hr | Show "+N places · +M centres" alongside trend %. OI-34. | **CLOSED 2026-05-04** (commit `f47a0ba`, centre.html v3.24 → v3.25) |
| C4 | Quality elements tab | OI-21 | ~1.0 sess | New tab structure. Deferred V2 candidate. | deferred |
| C5 | Ownership / corporate tab | OI-22 | ~1.0 sess | New tab structure. Deferred V2 candidate. | deferred |
| C6 | OI-09 growth metric render | A9 + B-pass | ~0.2 sess | Replace deferred placeholder with real Full row. | open |
| C7 | Daily-rate render integration | A8, B7 | TBD | Gated on STD-36+ stability. | gated |
| C8 | Demographic Mix narrative panel (T08 country of birth) | A10 | ~0.4 sess | **PHASE 2** — narrative summary at top of Catchment card. Depends on C2-NES rendering first. | banked |

**Phase C minimum remaining (OI-36 + C2 other metrics + C6):** ~0.9 sess.

## Recommended V1.5 ship slice (~2.6 sessions remaining)

Updated end-of-day 2026-05-04:

- **A3–A6** (~1.4 sess) — Phase A core (post-A1 dissolution + A2 done)
- **B1, B3–B5** (~0.9 sess) — Phase B core (post-B2 done)
- **OI-36 + C2 other** (~0.6 sess) — visible NES row + new Full rows for B-pass

**Total V1.5 remaining: ~2.6 sess.**

**Phase 2 (post-V1.5 critical path):**
- **A10 + C8** (~0.7 sess) — T08 country-of-birth ingest + Demographic Mix narrative panel. Depends on C2-NES rendering first.

**Deferred from V1.5 ship slice:**
- **C1 (OI-31)** — substantial standalone renderer feature; ship as V1.5+ once V1.5 core lands.
- **C4 / C5 (OI-21, OI-22)** — new-tab work; V2 candidates.
- **A7 (SEEK + wages)** — opportunistic.
- **A8 / B7 / C7 (daily rate)** — gated on parallel stream.
- **A9 / C6 (growth)** — opportunistic; gated on operator demand.

## First-piece recommendation (next session)

**OI-36 — C2-NES render-side.** Reasons:
- Closes the visible-on-page gap from this session (NES data is registered + banded + wired but invisible).
- Small, well-bounded (~0.3 sess).
- Makes the calibration nudge real and visible to the operator (rule_text on DER tooltip already shows it; the metric row gives standalone context).
- Unblocks Phase 2 (C8 narrative panel which builds on the NES row).

After OI-36, evaluate: continue Phase A (A3 next) or pivot to Phase 2 (A10 + C8) for fast visible enrichment.

## Open questions (resolve before code in each phase)

1. **A4 schools data source.** ACARA at school level vs state-DE enrolment by school — confirm SA2 attribution method.
2. **A5 FDC / PSK denominators.** Probe whether `pop_0_4` is wrong for these or only OSHC.
3. **B6 review trigger.** Agreed criterion for "saturated-catchment false positive" — propose: trigger after first operator complaint OR after manual review of ~10 saturated centres, whichever first.
4. **OI-36 render approach.** centre.html surgical patch to add catchment row, OR refactor catchment-card assembly to iterate `LAYER3_METRIC_META.card='catchment_position'` (more invasive, fixes the hardcoding root cause). Recommend the surgical patch for OI-36 and bank refactor as a separate housekeeping item.

## Acceptance criteria

- **Phase A items:** new ingest table populated; `audit_log` row landed per STD-30; row count matches probe expectation; backup taken pre-mutation.
- **Phase B items:** Layer 3 banding produces decile + band assignments; cohort sizes sane; `LAYER3_METRIC_META` entry committed.
- **Phase C items:** new metric appears at expected page position; trajectory + cohort histogram + decile strip + band chips render; about_data panel renders if explainer copy supplied; `centre.html` version bumped; `review_server.py` restarted; smoke-tested on at least one LDC service in a populous SA2 and one in a sparse SA2.

## Sequencing rules (inherited)

- **Search project knowledge before probing** (banked 2026-05-04 — STD-37 candidate).
- Probe before code (DEC-65).
- Renderer-best-practice ahead of plumbing.
- STD-30 pre-mutation discipline for any DB write.
- STD-10 patcher anchors use `\n` not `\r\n`.
- STD-12 line-ending detection at runtime.
- STD-13 Win11-safe orphan-Python detection for any process work.
- STD-35 end-of-session monolith + on-disk doc refresh + project-knowledge upload.
- STD-36 session-start uploads.
- Two-commit DEC-22 pattern for ingest → render pairs.
- `centre_page.py` change → `review_server.py` restart.
- **Unit conventions explicit at scoping time** (banked 2026-05-04).
- **Always run `layer3_x_catchment_metric_banding.py` after `layer3_apply.py`** until OI-35 real fix lands.

## Items deliberately NOT in this roadmap

- Operator-page work (separate program).
- Industry view / NCVER pipeline (DEC-36).
- STD-36+ daily-rate parallel stream itself (only its centre-page integration is A8 / B7 / C7).
- Pure housekeeping: OI-13, OI-14, OI-15, OI-16, OI-17, OI-24, OI-28.
- DB backup pruning (OI-12).
- DEC-77 framework changes — DEC-77 is locked.

## Doc-set integration

This document is the centre-page V1.5 source of truth. Update protocol:

- Parent `ROADMAP.md` references this doc but does not duplicate scope.
- `PROJECT_STATUS.md` notes the V1.5 phase pointer here.
- STD-35 end-of-session refresh applies — when a V1.5 piece ships, this doc updates first.
- DEC follow-ups (e.g. OI-26 under DEC-77) tracked here under the relevant Phase B item.

## Change log

- **2026-05-04 (end of day)** — Full-day session. C3 closed (`f47a0ba`). A1 dissolved. A2 closed end-to-end (v2 `fdc85bd` + v3 unit-fix `49ce9f1` + wire `bb21f66`). B2 closed (`d02e26e`). C2-NES partial — data-side `3ddcf18`, render-side held over as OI-36. OI-34 minted+closed; OI-35 + OI-36 minted; A10 + C8 banked as Phase 2.
- **2026-05-04 morning** — A1 dissolved (probe-driven); C3 closed. OI-34 minted+closed. *(Earlier creation — this update supersedes.)*
- **2026-05-04 (creation)** — initial V1.5 scoping pass, commit `f92b517`.
