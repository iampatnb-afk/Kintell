# Project Status

*Last updated: 2026-05-13 — Centre v2 build in progress; Turns 1-3 visual-iteration ratifications captured as DEC-84 amendment block. `centre_page.py` v24 + `docs/centre_v2.html` v0.5+ on disk; dev server running on :8001 for line-by-line iteration. Five queue items closed (#1 inline-row-click expand, #2 Layer 4 accordion-removal de-queued via reversal, #4 matrix category reorder, #9 top-N inline context, #11 matrix rename). The on-disk version supersedes the project-knowledge monolith if they disagree.*

> **NEXT-SESSION HEADLINE:** **Centre v2 build continues — line-by-line polish via banked queue.** Doc refresh done this session (DEC-84 amendment + PROJECT_STATUS + design-doc queue + memory bumps); no UI changes yet. Two strong bundle candidates ready for confirmation: **Bundle B (top-of-page strategic)** — peer-cohort range viz on places + daily rate / tenure relocation / Layer 2 ratings + unemployment + community detail / Stream E shorter version (SA2 border exposure proxy); **Small polish bundle** — hover-info / drawer enrichment for event lines (full centre names) / cosmetic SA2 name cleanup / ratio chart reference line / unemployment axis fix. Closer-to-v1-timeline items (N21 room mix probe; OSHC-school adjacency new ingest; user-customisable matrix queue #13; page-top show/hide selector) queued behind these. See `recon/centre_v2_design.md` outstanding queue for the full list and DEC-84 amendment in canonical DECISIONS.md for the 16 Turns 1-3 ratifications.

## Headline (2026-05-13 — Centre v2 Turns 1-3 doc refresh; banked queue carried forward)

**Doc refresh closes the Turns 1-3 paper trail.** Sixteen sub-decisions from the first three visual-iteration turns on `docs/centre_v2.html` ratified line-by-line by Patrick are now captured as a DEC-84 amendment block in canonical DECISIONS.md (refines — does not overturn — the 12 numbered locks from 2026-05-12). Five queue items close. PROJECT_STATUS + design-doc queue + memory all bumped. No UI changes this session; dev server still on :8001 with v0.5+ build state ready for next-bundle iteration.

**Sixteen Turns 1-3 sub-decisions captured (refer DECISIONS.md DEC-84 AMENDMENT 2026-05-13):**
1. Matrix terminology rename — "Institutional signal matrix" → **Signal Matrix** (D-1 confirmed; queue #11 closed)
2. Sparkline column retired from Layer 5 matrix (D-11 partially reversed; chart-below 80px histograms keep their size; reclaimed width reflows into Commentary)
3. Layer 4 accordion retained (queue #2 de-queued — earlier proposed removal reversed; accordion co-exists with inline-row-click expand)
4. Layer 4 acquires its own trend-window selector independent of Layer 3
5. Inline-row-click expand on Layer 5 matrix rows (queue #1 closed; trajectory chart + per-metric local window state)
6. Value-in-commentary pattern (leading bold value+period in Commentary column after sparkline retired)
7. Top-N percentages on demographic-mix rows inline in Commentary (queue #9 closed; full top-10 stays in drawer)
8. Centre-events overlay extends from 4 catchment metrics to under-5/births and population/cohort charts
9. Edge-event visibility nudge (~6px inward) so first/last-quarter annotations don't get clipped
10. Event-line annotation badge with type abbreviation (+1/−1) + quarter year above chart top axis
11. DER badge colour-coding (OBS blue / DER purple / COM amber — was uniform grey)
12. SEIFA descriptor word alongside decile in Layer 1 identity tile (D7-D8 "advantaged" etc.)
13. Layer 2 Community signal enrichment via top-2 languages substrate (DEC-84 #2 composer extended)
14. Quality category transitional note (italic caption — Starting Blocks pilot coverage only until national scale-up)
15. Explicit SA2 fact chip in Layer 1 identity row (was implicit-only through chart source attribution)
16. Source-attribution hygiene sweep across all Layer 3 + Layer 4 + Layer 5 source lines

**Queue items closed by Turns 1-3:** #1 inline-row-click expand · #2 Layer 4 accordion removal (de-queued via reversal) · #4 matrix category reorder (via Turn 1's credit-analytical flow display-order rewrite) · #9 Top-N inline context lines · #11 matrix terminology rename. Five of sixteen outstanding-queue items closed; eleven carried forward.

**Next-session bundle candidates** (Patrick to ratify which to pull first):
- **Bundle B — top-of-page strategic:** peer-cohort range visualisation on places + daily rate · tenure relocation · Layer 2 enrichments (ratings + unemployment + community detail) · Stream E shorter version (SA2 border exposure proxy)
- **Small polish bundle:** hover-info / drawer enrichment for event lines (full centre names propagating from the badge readout) · cosmetic SA2 name cleanup · ratio chart reference line · unemployment axis fix
- **Closer to V1 timeline** (queued behind): N21 Room mix / age cohort (probe needed first) · schools-with-attached-OSHC new ingest · user-customisable matrix view (queue #13) · page-top show/hide selector

**This session's deliverables (all on disk):**
- `recon/Document and Status DB/DECISIONS.md` — DEC-84 AMENDMENT 2026-05-13 block (16 sub-decisions + consequences)
- `PROJECT_STATUS.md` — this section
- `recon/centre_v2_design.md` — outstanding queue updated (Turns 1-3 items moved to ✅ Done; banked items restated for visibility)
- Memory: `project_state.md` bump to 2026-05-13; `project_centre_v2_redesign.md` updated to reflect build-step-2 mid-iteration state

**File state:**
- `centre_page.py` v24 (Turn 1 + Turn 3 patches: `_truncate_sentence` widened 120 → 240 chars; `community_profile` substrate via top-2 language extraction in `_build_drawer`; `_build_executive` extended with `community_profile` param)
- `docs/centre_v2.html` v0.5+ on disk (Signal Matrix rename + category reorder + sparkline column retired + commentary widened + inline-row-click expand wiring + edge-event nudge + event-line badge + DER colour palette + SEIFA descriptor + SA2 fact chip + Quality category caption + source-attribution sweep). Version numbering stays informal until first verification capture per DEC-84 effort breakdown.

**No DB mutations.** No `audit_log` rows. `kintell.db` unchanged.

**Worktree note.** Session ran from worktree `claude/jovial-kepler-0f9167` (predates DEC-83 + DEC-84 + Centre v2 build); all edits targeted main repo absolute paths per established Patrick workflow. Doc-only changes; no commits this session unless Patrick instructs.

---

## Headline (2026-05-12 — DEC-84 Centre v2 design pass closed — preserved for traceability)

**Centre v2 joint design pass ratified end-to-end in one session.** Probe → surface inventory of v3.31 (32 metrics × 5 cards × 14 helpers) → DEC-83 substrate placement → 6-layer content map proposal → batched 12-decision design ratification → DEC-84 mint → Tier-2 doc refresh. Probe-first per DEC-65; surface inventory delegated to Explore agent for parallel execution while precedent-doc + DEC-83 schema were read directly.

**Key architectural decisions (DEC-84 batch ratified):**
- **Cards dissolve; matrix becomes center of gravity.** v1's 5 vertical cards replaced by 6-layer architecture (Header / Executive interpretation / Primary trends / Secondary trends accordion / Institutional signal matrix / Detail side-drawer)
- **Layer 5 matrix ~52 rows V1, 9 categories** (Demand / Supply / Pricing & Fees NEW / Quality NEW / Workforce / Community / Education / Operator-Group NEW / Operations NEW / Population / Labour Market). Plus ~9 "Pending V1.5" status-pill stubs that auto-resolve as ingests land
- **Layer 3 = 7 primary charts.** Daily-rate full_day × 36m-preschool with peer-cohort overlay is the new headline chart; OSHC services discriminate at render to before/after_school × school-age
- **Layer 2 = 5 signal tiles + 0-2 flags.** Demand / Supply / Workforce / Quality / Community signal tiles. Flag severity hierarchy: RED for `ccs_revoked_by_ea` / closed; AMBER for active conditions / sub-Meeting NQS / recent enforcement; INFORMATIONAL for `no_vacancies_published`. Operator-group affiliation is a Layer 1 chip, not a flag
- **Layer 6 drawer = slide-in side panel,** click-anywhere-row + ESC + URL fragment shareable. Single drawer at a time. `_renderAboutData` and `_renderTopNContext` migrate into drawer rendering
- **Workforce Supply Context card dissolves** — JSA IVI rows absorb into Layer 5 Workforce + Layer 3 chart 6 third overlay when wired; ECEC Award + Three-Day-Guarantee become Layer 5 fact rows
- **Old `/centres/{id}` preserved** via git tag `centre-v1-stake-2026-05-12` on commit `212b597` (pre-v2-build SHA) + `recon/v1_final_stake_2026-05-12/` bundle dir + ROLLBACK.md, created BEFORE v2 build's first edit

**DEC-83 substrate fully placed.** Operator-group → Layer 1 chip + Layer 5 row + Layer 6 drawer. Daily-rate → Layer 3 chart 7 + Layer 5 5-row Pricing category + Layer 6 grid drawer. Regulatory snapshot → Layer 1 contact strip + Layer 1 hours + Layer 2 flags + Layer 5 Quality/Operations + Layer 6 NQS drawer. Conditions → Layer 2 flag + Layer 5 count + Layer 6 detail drawer. Vacancies → Layer 2 informational flag + Layer 5 row + Layer 6 drawer. Enforcement events → Layer 2 flag + Layer 5 count + Layer 6 chronological drawer.

**Existing renderer inventory survives.** All 14 v3.31 helpers reused (`_renderFullRow`, `_renderLiteRow`, `_renderContextRow`, `_renderTrajectory`, `_renderIntentCopy`, `_renderIndustryBand`, `_renderDecileStrip`, `_renderBandChips`, `_renderCohortHistogram`, `_renderLiteDelta`, `_renderTrajectoryRangeBar`). Two new render primitives (`MatrixRow`, `DrawerPanel`) + one new helper (`_buildExecutiveHeadline`). `_renderWfsRangeBar` retires.

**This session's deliverables (all on disk):**
- `recon/centre_v2_design.md` — design doc seed + RATIFIED SUMMARY post-batch (the canonical content map)
- `recon/Document and Status DB/DECISIONS.md` — DEC-84 minted (12 ratified decisions)
- Tier-2 docs refreshed: `PROJECT_STATUS.md` (this), `ROADMAP.md`, `CENTRE_PAGE_V1_5_ROADMAP.md`, `OPEN_ITEMS.md`, `PHASE_LOG.md`
- Memory updates: `project_centre_v2_redesign.md` (design pass step closed; build sequence next) + `project_state.md` (2026-05-12 bump)

**v1 stake — created this session pending Patrick's git tag command:**
- `recon/v1_final_stake_2026-05-12/` bundle dir with copies of `centre.html` v3.31, `centre_page.py` v23, `PAYLOAD_SCHEMA.md` notes
- `recon/v1_final_stake_2026-05-12/ROLLBACK.md` — recovery recipe (git checkout `<tag> -- <files>` + payload-schema downgrade notes)
- **PATRICK ACTION:** run `git tag centre-v1-stake-2026-05-12 212b597` from main repo terminal (worktree access not required) before kicking off `centre_page.py` v24

**No DB mutations this session.** No audit_log rows. `kintell.db` 619.x MB, 43 user tables, audit_log 177 rows — unchanged from 2026-05-11 EOD.

**Worktree note.** Session ran from stale worktree `claude/trusting-lehmann-b31fa0` (predates V1 + DEC-83); all edits targeted main repo absolute paths so worktree branch state is irrelevant. Work to be committed direct-on-master from main repo per Patrick's workflow.

---

## Headline (2026-05-11 — DEC-83 Commercial Layer V1 ship — preserved for traceability)

**DEC-83 Commercial Layer V1 (daily-rate + regulatory + operator-group identity) shipped end-to-end in one session.** Probe → batched 9-decision design ratification → schema migration (7 new tables + 1 reused scaffold + 1 ALTER on services + 12 indexes) → extract module + pilot loader → 130-centre proof load → Algolia reconcile tool → Tier-2 doc refresh. Pre-build precedent check (DEC-65) caught existing scaffolds (`regulatory_events`, `nqs_history`); schema plan amended pre-build to reuse rather than duplicate. Source-payload re-inspection mid-design surfaced significant institutional-value fields (provider regulatory state, enforcement detail, conditions, large-provider operator-group identity, vacancies, fee-type classification, NQS area breakdown, operating hours); Patrick ratified scope expansion on capture-once-use-anywhere economics.

**Key institutional capabilities now in `kintell.db`:**
- **Daily-rate per (service, age_band, session_type, as_of_date)** — 8,220 fee rows for 109 of 130 pilot centres, 2018-2026 history. Fee classifications (ZCDC/ZOSH/ZFDC) preserved.
- **Live CCS-revocation signal** via `service_regulatory_snapshot.ccs_revoked_by_ea` — addresses Strengthening Regulation Bill 2025 cross-cutting risk per PRODUCT_VISION §9 (previously tracked-but-uncaptured).
- **9 ACECQA enforcement actions** populated `regulatory_events` (existing scaffold; first non-zero rows on this table); action_id preserved in detail JSON.
- **76 service-level + 9 provider-level regulatory conditions** with full text — child-safety surface substrate (Centre v2 Layer 6).
- **13 operator-group chains identified** — first time the project has structured operator-group identity for ACECQA "Large Provider" chains (e.g. Goodstart 3 providers / Guardian 12 / KU 1 / OAC 8 / Story House 17 / Montessori Academy 41). Critical substrate for Group page (OI-NEW-17) + Stream D PropCo (OI-NEW-13). 37 services in pilot now flagged with `large_provider_id`.
- **486 vacancy snapshots** (352 has_vacancies + 134 no_vacancies_published) — first forward-looking demand-side signal at centre level. Vacancies populated for ~73% of pilot service×age_band combos.
- **Operating hours per day** — valuation context, OSHC vs LDC distinction.
- **Provider sub-block** (status / approval date / CCS-revoked / trade name) — provider-level posture for institutional credit work.

**This session's deliverables (all on disk):**
- `recon/daily_rate_integration_design.md` — probe-first design doc; ratified summary populated post-decision-batch
- `recon/Document and Status DB/DECISIONS.md` — DEC-83 minted + same-session amendment header
- `migrate_commercial_layer_schema.py` — schema migration patcher (STD-08 backup, audit_log row, idempotent)
- `commercial_layer_extract.py` — pure-function extract module (~500 lines)
- `commercial_layer_load_pilot.py` — V1 proof loader (reads pilot raw_payload, runs extract, writes audit_log row)
- `algolia_reconcile.py` — V1 reconciliation tool (smoke test + delta report)
- 2 fresh STD-08 backups: `pre_commercial_layer_schema_*.db`, `pre_commercial_layer_load_*.db`
- Tier-2 docs refreshed: `PROJECT_STATUS.md` (this), `OPEN_ITEMS.md`, `ROADMAP.md`, `CENTRE_PAGE_V1_5_ROADMAP.md`, `PHASE_LOG.md`

**DB state.** `kintell.db` 615.3 → 615.6 → 619.x MB (post-load). 36 → 43 user tables (+7). audit_log 175 → 177 (+2 rows: schema migration + load).

**Verification.** All 8 V1 invariants PASS: every fee row resolves to services / non-negative / capture rows have external_id / snapshot rows resolve / large_provider_id on services resolves / link rows resolve / no condition has empty text / vacancy_status valid. Identity resolution validated 129/130 against full 18,223-service main DB (1 unresolved is SAN-less Redfern OCC, captured-only with service_id=NULL per design). Algolia smoke test PASS (71 hits at Haymarket, matches pilot exactly); 130 pilot centres all reconcile cleanly via `external_capture` join.

**Worktree note.** Session ran from stale worktree `claude/priceless-goldstine-654f2a` (predated V1 ship); all edits and DB mutations targeted main repo absolute paths so worktree branch state is irrelevant. Work to be committed direct-on-master from main repo per Patrick's solo-developer workflow.

---

## Headline (2026-05-10 PM session 2 — preserved for traceability)

**A4 Schools at SA2 shipped end-to-end. New "Education infrastructure" Position card.** First direct-primary-source ingest (ACARA School Profile 2008-2025 + School Location 2025) per the new strategic principle DEC-82 ("primary-source-first for new ingests; track derivative-sourced ABS-DBR metrics for V2 migration"). Eight new metrics ingested into `abs_sa2_education_employment_annual` (316,859 rows across 18 years 2008-2025), three rendered in the V1 card (school count + total enrolment + govt-school enrolment share); the other five sector breakdowns sit in DB ready for V2 / Excel export / group page. New top-level Position card alongside Catchment / Population / Labour Market — future home for preschool series + tertiary/VET context. audit_id 164 → 174 (8 ingest + 1 layer3_apply + 1 catchment-rebanding).

**Spatial-join helper landed in `geo_helpers.py`** — generic `point_to_sa2()` + `points_to_sa2()` infrastructure reusable for V2 PropCo property locations, hospital catchments, transport stations, and the OI-NEW-19 OSHC-school adjacency derived flag. ACARA pre-computes SA2 in their Location 2025 file, so A4 used ACARA's SA2 mapping directly; the geo_helpers cross-validation (sjoin against same lat/lng) confirmed 99.93% match — 8 mismatches in 11,039 schools were all multi-campus institutions where ACARA manually allocates campuses to specific SA2s in a way a centroid sjoin can't replicate. Within tolerance.

**Verification SA2 institutional stories (2024):**
- Bayswater Vic — 5 schools, 1,058 students, 92% govt (suburban family belt, predominantly state schools)
- Bondi Junction NSW — 6 schools, 5,330 students, **4.9% govt** (eastern Sydney Catholic+Independent dominance — striking)
- Bentley-Wilson WA — 5 schools, 1,264 students, 69% govt (student-heavy mixed catchment)
- Outback NT — 10 schools, 1,573 students, 91% govt (remote, predominantly state)

**This session 2's deliverables (all on disk):**
- `recon/probes/probe_a4_schools_columns.py` (initial probe — surfaced no ACARA file present, drove design)
- `recon/probes/probe_a4_acara_files.py` (post-arrival probe — confirmed all V1 fields)
- `recon/a4_schools_design.md` (probe-first design doc; D-B1 path + sector mix + sanity check ratified)
- `geo_helpers.py` (new module — `point_to_sa2`, `points_to_sa2`, module-level GPKG cache)
- `layer4_4_step_a4_schools_apply.py` (8 metrics ingest + cross-validation, audit 165–172)
- `patch_b2_layer3_add_a4_schools.py` (8 banding entries appended to layer3_apply.py METRICS)
- 4 surgical edits to `centre_page.py` v23 (LAYER3_METRIC_META + INTENT_COPY + TRAJECTORY_SOURCE + POSITION_CARD_ORDER + `_layer3_position` `out` dict — 3+3+3+1+1 entries; new `education_infrastructure` card key)
- 2 surgical edits to `docs/centre.html` v3.31 (`renderEducationInfrastructureCard` function + page composition)
- DEC-82 minted in canonical DECISIONS.md
- OI-NEW-19 (OSHC-school adjacency derived flag, V2) + OI-NEW-20 (V2 migration backlog of 16 derivative-sourced ABS-DBR metrics) added to OPEN_ITEMS
- Smoke-test capture rebuilt at `docs/a10_c8_review.html` (4 SA2s) + new `docs/centre_a4_review_2358.html` (single-LDC view)

**DB state.** 1 fresh backup (`data/pre_layer4_4_step_a4_schools_*.db` 556.8 MB). 316,859 new long-format rows in `abs_sa2_education_employment_annual` (39,613 each for the 5 schools-count metrics + 39,598 each for the 3 enrolment-share metrics — 2,233 SA2s × 18 years). Plus banding rebuild: ~17,840 banded rows added to `layer3_sa2_metric_banding` (8 metrics × ~2,230 SA2s × 1 latest-period). audit_log 164 → 174 (10 new rows: 8 ingest + 1 layer3_apply + 1 catchment-rebanding).

**Verification.** National 2024 totals all within ABS-published bands: 9,736 schools (in 8k-12k band), 4.18M enrolment (in 3.5M-4.5M band), 63.7% govt-share-by-enrolment (in 60-68% band). 99.93% ACARA-vs-sjoin match (8 mismatches all multi-campus edge cases, manually verified as defensible). 18-point trajectories 2008-2025 — richest cadence in the build (vs parent-cohort 6pt, Census 3pt).

---

## Headline (2026-05-10 PM session 1 — preserved for traceability)

**A3 + Stream C bundle shipped end-to-end. Demographic mix sub-panel grows from 4 to 8 Lite rows.** Four new SA2-level metrics: parent-cohort 25-44 share (ERP, annual 6-point 2019-2024) + partnered 25-44 share (TSP T05, Census 3-point) + share of women 35-44 with at least one child (TSP T07, Census 3-point) + share of women 25-34 with at least one child (TSP T07, Census 3-point). audit_id 158 → 164 (4 ingest + 1 layer3_apply + 1 OI-35 catchment rebanding). DEC-81 minted to lock the V1 Stream C scope (sharp 25-44 partnered window; two fertility cohorts; NS-handling convention; ERP col 3 not 121 for total_persons). Probe-before-code (DEC-65) confirmed the column shapes; A10 had already banked T05 + T07 as sibling-tables which made this bundle a clean re-application of the A10 template.

**Patient-cohort framing locked**: the 25-34 "with at least one child" cohort is the active-childcare-timing signal; the 35-44 cohort is the completed-fertility community-profile signal. Patrick's framing question "what's your sense here that feels old as an age for child care?" surfaced the asymmetry — childcare demand is more directly indexed to 25-34 active parenting, whereas 35-44 captures completed fertility once the lifetime profile has settled. Both cuts ship.

**This session's deliverables (all on disk):**
- `recon/probes/probe_a3_streamc_columns.py` (read-only TSP zip + ERP column probe)
- `recon/a3_streamc_design.md` (probe-first design doc; D-B1..D-B5 ratified)
- `layer4_4_step_a3_streamc_apply.py` (4 metrics ingest, audit 159–162)
- `patch_b2_layer3_add_a3_streamc.py` (4 banding entries appended to `layer3_apply.py` METRICS)
- 4 surgical edits to `centre_page.py` (LAYER3_METRIC_META, LAYER3_METRIC_INTENT_COPY, LAYER3_METRIC_TRAJECTORY_SOURCE, POSITION_CARD_ORDER — 4 entries each)
- 1 surgical edit to `docs/centre.html` v3.29 → v3.30: `demoMetrics` array extended with 4 new keys (renderer transparently picks up annual + 3-point trajectories via existing `_renderLiteRow` + `_renderLiteDelta`)
- DEC-81 minted in canonical DECISIONS.md
- Re-built static-HTML capture `docs/a10_c8_review.html` for visual review of all 13 catchment-position rows across the 4 verifying SA2s

**DB state.** 1 fresh backup (`data/pre_layer4_4_step_a3_streamc_20260510_005147.db` 548.1 MB). 35,324 new long-format rows in `abs_sa2_education_employment_annual` (14,120 parent-cohort + 7,063 partnered + 7,072 women-35-44 + 7,069 women-25-34). Plus banding rebuild: layer3_sa2_metric_banding total ~42,992 rows (4 new metrics × ~2,353-2,358 rows each = ~9,420 banded rows added). audit_log 158 → 164 (6 new rows: 4 ingest + 1 layer3_apply + 1 OI-35 catchment rebanding).

**Verification.** National 2021 totals all within ABS-published bands: parent-cohort 28.20% (ABS ERP ~28-30%), partnered 25-44 65.56% (ABS ~58-65% — at upper end), women-35-44-with-child 78.43% (ABS ~75-82%), women-25-34-with-child 41.19% (in band 38-55, reflecting Australia's later-fertility shift). Four verifying SA2s render cleanly: Bondi Junction-Waverly NSW shows the urban late-fertility profile (parent-cohort 39%, partnered 62%, w35-44 60.9%, w25-34 just 11.3%) — clean separation from Outback NT's high-early-fertility profile (32%, 47%, 84.5%, 72.1%).

---

## Headline (2026-05-10 AM — preserved for traceability)

**A10 + C8 Demographic Mix bundle shipped end-to-end.** Three new SA2-level Census-derived metrics (ATSI share, overseas-born share, single-parent-family share) plus two new top-N display tables (top-3 country of birth; top-3 language at home) plus a "Demographic mix" sub-panel inside the Catchment Position card. Audit_id 150 → 158 (5 schema/ingest mutations across two scripts). Table-mapping correction banked: roadmap had T07/T08/T19 — actual subjects are T06 (ATSI), T08 (country of birth), T14 (family composition); T07 is fertility and T19 is tenure/landlord. Probe-before-code (DEC-65) caught it before any wrong data shipped. DEC-78 (Census 0–100 storage convention) promoted from Reserved → Active; DEC-80 minted to lock the top-N table convention + TSP-table-number verification discipline + Demographic Mix scope.

**Sparkline-on-Lite-rows considered and rejected** mid-session — too busy at that visual budget per Patrick. Delta badge remains canonical for Lite-row trajectory representation.

**This session's deliverables (all on disk):**
- `layer4_4_step_a10_apply.py` (3 metrics + COB top-N ingest, audit 150–154)
- `layer4_4_step_a10b_languages_apply.py` (language top-N ingest, audit 157–158)
- `patch_b2_layer3_add_demographic_mix.py` (3 banding entries appended to `layer3_apply.py` METRICS)
- 6 surgical edits to `centre_page.py` (LAYER3_METRIC_META, LAYER3_METRIC_INTENT_COPY, LAYER3_METRIC_TRAJECTORY_SOURCE, POSITION_CARD_ORDER, `_build_community_profile`, payload assembly)
- `docs/centre.html` v3.28 → v3.29: sub-panel divider, top-N COB + language renderers via shared `_renderTopNContext` helper
- `recon/a10_c8_design.md` (probe-first design doc with TSP table-mapping correction)
- `build_a10_c8_review_capture.py` (offline static HTML capture; `docs/a10_c8_review.html` not committed)
- DEC-78 promoted, DEC-80 minted in canonical DECISIONS.md
- `~/.claude/projects/.../memory/feedback_lite_row_density.md` — feedback memory locking the no-sparkline-on-Lite-rows preference

**DB state.** 2 fresh backups (`data/pre_layer4_4_step_a10_20260509_234058.db` 541.4 MB, `data/pre_layer4_4_step_a10b_20260510_000826.db` 547.7 MB). New table `abs_sa2_country_of_birth_top_n` (7,102 rows). New table `abs_sa2_language_at_home_top_n` (7,060 rows). New rows in `abs_sa2_education_employment_annual`: 7,272 ATSI + 7,272 OS-born + 7,104 single-parent = 21,648 long-format rows. New banding rows for the 3 metrics in `layer3_sa2_metric_banding` (~7,200 rows × 3 = ~21,600 banded rows). audit_log 149 → 158 (9 new rows: 5 ingest/banding + 1 layer3_apply + 1 OI-35 catchment rebanding + 2 language top-N).

**Verification.** National 2021 totals all within ABS-published bands: ATSI 3.20% (ABS ~3.2%), overseas-born 27.71% (ABS ~27.6%), single-parent-family 15.79% (ABS ~16%). Four verification SA2s (Bayswater Vic, Bondi Junction-Waverly NSW, Bentley-Wilson WA, Outback NT 702041063) all rendering correctly. Outback NT validates the high-ATSI test case at 91.1% ATSI share, 89.2% Australian Indigenous languages at home.

---

## Headline (2026-05-09 — preserved for traceability)

**Project repositioned. Patrick Bell owns the IP. Brand: Novara Intelligence (working).** This session was a planning-only pass — no code changes, no DB mutations. Commercial repositioning locked as DEC-79. Audience expands from Remara-credit-team to broader institutional decision-support market participants (lenders, investors, operators FP+NFP, valuers, property funds, debt providers, advisors). Five new work streams locked into the V1 plan (PRODUCT_VISION.md): A) Educator visa / overseas educator supply, B) NFP perspectives integrated, C) Childbearing-age + marital-status depth, D) PropCo Property Intelligence (V1 premium tier — not V2), E) SA2 Border Exposure V1 proxy. V1 ship target redefined to **~Sept 2026** (3-4 months), incorporating the original V1.0 centre-page tool (already shipped) plus V1.5 ingests + Catchment page + Group page + the five new streams + Excel export framework + brand identity rename pass.

**This session's deliverables (all landed on disk):**
- DEC-79 appended to canonical DECISIONS.md
- New `CLAUDE.md` at repo root (orientation for every future Claude Code session)
- New `PRODUCT_VISION.md` at repo root (strategic frame, audience, 5 streams, V1/V2/V3 horizon)
- ROADMAP.md updated for new V1 horizon and stream sequencing
- OPEN_ITEMS.md updated with OI-NEW-1 through OI-NEW-18 (provenance corrections, risks, brand rename, doc moves, 5 streams, new surfaces, Excel export, institutional readiness)
- 9 memory entries in `~/.claude/projects/.../memory/` (user role, collaboration style, project context, project state, project Remara relationship, no-bash-paths feedback, doc-discipline feedback, extend-don't-sprawl feedback, doc-locations reference)
- `.gitignore` updated for OI-13 (single-? pattern fix) + OI-NEW-9 (recon/patchers_*) + `*.pre_*` patterns

**Operational change locked:** Patrick drives strategy / UI / industry depth / data depth / commercial risk. Claude drives technical architecture / schema / code / build sequencing / doc discipline. Patrick's input on coding architecture is intentionally limited.

**Cross-cutting risks now tracked:** 2026 Census Aug 2026 (SA2 boundary refresh Q3 2027), workforce funding cliff Nov 2026, Strengthening Regulation Bill 2025 (CCS revocation as live credit indicator), Starting Blocks Algolia drift, ABS Community Profiles retirement, "70% break-even" anchor provenance.

---

## Headline (2026-05-05 — preserved for traceability)

**V1.0 is at HEAD `bcdf84c`. V1.5 first piece (OI-36) is at `430009a`.** This session closed OI-36 cleanly: NES row now visible in Catchment Position card across all 3 verification SA2s, plus a generic delta badge on all Lite rows surfacing first-to-last Census-point change ("+9.5pp from 2011 to 2021" on Bayswater NES; "+$291/week from 2011 to 2021" on Bayswater median household income). Three commits this session: doc-set catch-up (`9d49be9`), OI-36 close (`430009a`), and end-of-session doc refresh (this commit landing).

*Note 2026-05-09: "V1" in this 2026-05-05 entry refers to the original V1.0 centre-page credit-decision tool. Per DEC-79 the term V1 has been redefined to the broader Novara Intelligence release targeting ~Sept 2026.*

## Centre page — current state

`centre_page.py` v21 (Python backend) + `centre.html` v3.28 (renderer) + payload schema `centre_payload_v6` (unchanged this session — OI-36 work was render-side only, no payload schema rev).

### Catchment Position card — current shape

| Metric | Weight | Trajectory | Events overlay | INDUSTRY band | About panel | Calibration in DER | NES delta badge |
|---|---|---|---|---|---|---|---|
| `sa2_supply_ratio` | FULL | quarterly per subtype | YES (subtype-matched) | 7 levels | YES | — | n/a |
| `sa2_demand_supply` | FULL | quarterly (cal_rate held) | YES | 4 levels (parallel-framed) | YES | YES | n/a |
| `sa2_child_to_place` | FULL | quarterly (1/supply_ratio) | YES | 5 levels | YES | — | n/a |
| `sa2_adjusted_demand` | FULL | quarterly (cal_rate held) | YES | NO (decile only) | YES | YES | n/a |
| `sa2_demand_share_state` | CONTEXT | n/a | n/a | n/a | n/a | YES | n/a |
| `sa2_nes_share` | LITE | 3 Census points | n/a | n/a | n/a | YES (live nudge) | **YES** |

NES row now rendering correctly across all verification SA2s:
- Bayswater Vic (id=2358 / sa2 211011251): 31.1% (2021), Decile 5 mid, +9.5pp from 2011 to 2021, calibration nudge −0.02 firing
- Bondi Junction-Waverly NSW (id=103 / sa2 118011341): 23.6%, Decile 5 mid, +2.1pp from 2011 to 2021, no nudge
- Bentley-Wilson WA (id=246 / sa2 506031124): 37.6%, Decile 10 high, +Xpp from 2011 to 2021, calibration nudge −0.02 firing

### Delta badge (new this session)

Generic `_renderLiteDelta(p)` helper in centre.html v3.27 + currency-format fix in v3.28. Reads `p.trajectory` and emits a small first-to-last delta badge inside the Lite row template, alongside the existing "as at YYYY" stamp. Unit-aware via `p.value_format`:

- `percent` / `percent_share` → "+9.5pp from 2011 to 2021"
- `currency_weekly` → "+$291/week from 2011 to 2021"
- `currency_annual` → "+$1,234 from 2011 to 2021"
- `ratio_x` → "+0.04× from 2011 to 2021"
- else → plain numeric

Always-show variant (P1). P-2 silent absence for <2 numeric points / unreadable years / zero delta. Affects all Lite rows: NES, LFP triplet, median household income.

**Window-aware variant (P2) declined this session** — operator chose to keep complexity out. Existing `_setTrajectoryRange` doesn't trigger Lite re-render anyway, so window-awareness on Lite rows would need new event-subscription wiring beyond OI-36 scope.

---

## Phase 2.5 — status by layer

| Layer | Description | Status |
|---|---|---|
| 0 / 1 / 2 | Foundations | COMPLETE |
| 2.5 | Catchment cache populator | COMPLETE 2026-04-30 |
| 3 / 4.1 | Layer 3 banding 14 metrics | COMPLETE; **+1 metric (sa2_nes_share, B2 closed 2026-05-04)** |
| 4.2 | Centre page renderer | COMPLETE for V1; **+OI-36 close 2026-05-05** |
| 4.3 | Centre page polish + workforce | COMPLETE |
| 4.4 | V1.5 ingests | A2 done 2026-05-04; A3-A6 + A10 remaining; tracked in CENTRE_PAGE_V1.5_ROADMAP.md |

---

## What's next

**Centre v2 joint design pass — primary recommended next session.** Per `project_centre_v2_redesign.md` (memory): 6-layer structure (Header / Executive interpretation / Primary historical trends / Secondary historical trends / Institutional signal matrix / Detail side-drawer). The institutional signal matrix at Layer 5 is the natural home for daily-rate (now ingested), CCS revocation status, NQS area breakdown, fee-position vs catchment peer cohort, and operator-group identity. Joint design pass = content map for every existing piece + every new piece (daily-rate, regulatory state, conditions, vacancies, large-provider chain) assigned to its surface tier. Expected ~1.5-2 sess; produces a content-map DEC + the Layer 5/6 tile design before parallel renderer build (~3-5 sess). Old `/centres/{id}` route preserved via git tag `centre-v1-stake-YYYY-MM-DD` + `recon/v1_final_stake_YYYY-MM-DD/` bundle per the redesign memo.

**Alternative pickups (Patrick's choice):**
- **National commercial-layer scale-up** — extend `commercial_layer_load_pilot.py` pattern to drive off `services` table (18,223 rows × 1.5s polite pacing ≈ 7-8 hours overnight). ~0.5-1 sess of script work + monitoring overnight run + post-run validation. Closes the V1 "we have daily-rate data" claim across the full national fleet.
- **V1.5 ingest queue resumption** — A5 subtype-correct denominators (~0.3 sess), A6 SALM extension (~0.2 sess), B1 / B3 / B4 / B5 banding (~0.5 sess), C2-other + C6 render polish (~0.4 sess). Total ~1.4 sess. These are useful for the centre-page (v1) surface; arguably less useful if Centre v2 lands first since v1 surface gets superseded.
- **OI-NEW-22** Provider-level enforcement + conditions extraction (~0.5 sess) — bridging table + reconciliation against `entities`. Banked from this session.

**Recommended sequencing per session-density discipline:** Centre v2 design pass first (locks what V1 looks like → drives whether we still need V1.5 ingests at all or whether v2 institutional matrix absorbs them differently) → then national commercial-layer scale-up → then implementation.

**Optional housekeeping (low priority, anytime):**
- **OI-12** — DB backup pruning. **CRITICAL** at ~10+ GB cumulative (2 new STD-08 backups this session). Keep policy needs relaxation.
- **OI-35** — `layer3_apply.py` real fix (~0.5 sess).
- **OI-13** — Frontend file backups gitignore tightening.
- **OI-14 / OI-15** — Date parsing + ARIA+ format codebase scans.
- **OI-10** — `provider_management_type` enum normalisation.
- **OI-28** — `populate_service_catchment_cache.py` cosmetic banner.
- **STD-37 candidate** — "search project knowledge before probing" mint (still pending after multiple sessions).
- **Recon probe sweep** — root probes → `recon/probes/`.

---

## Database state

Path: `data\kintell.db` (~619 MB). **43 user tables (was 36 — +7 from DEC-83 schema).** `audit_log: 177 rows` (was 175 — +2 this session: schema migration audit_id 176, V1 proof load audit_id 177).

**2 new STD-08 backups this session** (~1.23 GB added):
- `data/pre_commercial_layer_schema_20260510_175758.db` (615.3 MB)
- `data/pre_commercial_layer_load_20260510_181447.db` (615.6 MB)

Cumulative DB backups now ~10+ GB across 43+ files. **OI-12 backup-pruning relevance growing** — keep-policy relaxation now genuinely overdue.

`docs/sa2_history.json`: v2-schema, 19.3 MB, 2,309 SA2s post-OI-NEW-21 polygon-first rebuild (2026-05-10 PM s3). Unchanged this session.

**New tables (DEC-83):** `service_external_capture` (130 rows), `large_provider` (13 rows), `large_provider_provider_link` (92 rows), `service_fee` (8,220 rows), `service_regulatory_snapshot` (129 rows), `service_condition` (85 rows: 76 service + 9 provider levels), `service_vacancy` (486 rows: 352 has_vacancies + 134 no_vacancies_published).

**Reused scaffold:** `regulatory_events` 0 → 9 rows (first non-zero rows on this previously-empty table; all "Compliance notice issued" by ACECQA, service-level only V1).

**Schema mutation:** `services` +1 column `large_provider_id` (TEXT, FK to large_provider). 37 services in pilot now flagged into chains (Goodstart 5 / Guardian 5 / KU 8 / OAC 4 / Story House 1 / Camp Australia 2 / Junior Adventures Group 1 / TheirCare 2 / TeamKids 4 / Sydney Catholic Early Childhood Services 2 / MACSEYE 1 / Montessori Academy 1 / PCYC Queensland 1).

---

## Git state

V1 ship: `bcdf84c` (2026-05-03 evening). Pre-DEC-83 master HEAD: `0dce69b` (2026-05-10 PM s3 — OI-NEW-21 close).

**This session: no commits yet.** All work landed on disk via Edit/Write tools targeting main repo absolute paths from a stale worktree session. Commit + push to be done from main repo terminal direct-on-master per Patrick's workflow.

**Files changed this session (uncommitted):**

| File | Status | Notes |
|---|---|---|
| `recon/Document and Status DB/DECISIONS.md` | modified | DEC-83 minted (with same-session amendment header for the regulatory_events scaffold reuse + slimmed regulatory_snapshot decision) |
| `recon/daily_rate_integration_design.md` | new | Probe-first design doc, ratified summary populated |
| `migrate_commercial_layer_schema.py` | new | Schema migration patcher |
| `commercial_layer_extract.py` | new | ~500-line extract module |
| `commercial_layer_load_pilot.py` | new | V1 proof loader |
| `algolia_reconcile.py` | new | Reconciliation tool with smoke test |
| `data/kintell.db` | modified | +7 tables, +1 column on services, +12 indexes, +9,184 commercial-layer rows, +9 regulatory_events rows, +37 services flagged with large_provider_id, +2 audit_log rows |
| `data/pre_commercial_layer_schema_20260510_175758.db` | new | STD-08 backup pre-schema-migration |
| `data/pre_commercial_layer_load_20260510_181447.db` | new | STD-08 backup pre-load |
| `PROJECT_STATUS.md` | modified | This entry |
| `OPEN_ITEMS.md` | modified | OI-NEW-4 Algolia portion closed; OI-NEW-22 + OI-NEW-23 minted |
| `ROADMAP.md` | modified | Daily-rate moved out of §7 deferred parallel work |
| `CENTRE_PAGE_V1_5_ROADMAP.md` | modified | A8 daily-rate context update |
| `PHASE_LOG.md` | modified | Session entry prepended |

**Suggested commit shape (3 commits, atomically grouped per DEC-22 collapsable pattern):**
1. **DEC-83 schema + extract + load + reconcile + design doc** — all the new code + design + DECISIONS.md + DB mutations (large; could be bundled or split into "schema migration" / "extract+load" / "reconcile" — Patrick's call)
2. **Tier-2 doc refresh** — PROJECT_STATUS, OPEN_ITEMS, ROADMAP, CENTRE_PAGE_V1_5_ROADMAP, PHASE_LOG (STD-35 hygiene)

DB backups (`pre_commercial_layer_*.db`) excluded from commits per existing `.gitignore` patterns covering `pre_*` files.

---

## Standards / decisions

**New DECs locked this session:**
- **DEC-83** — Commercial Layer V1: daily-rate integration from Starting Blocks (pricing + regulatory snapshot + operator-group identity). Includes same-session pre-build amendment to reuse `regulatory_events` scaffold and slim `service_regulatory_snapshot` (NQS area cols dropped — `nqs_history` is canonical from NQAITS).

**No new STDs locked this session.**

Banked items: STD-37 candidate (search project knowledge before probing — still pending mint), refresh-cadence-discipline candidate STD (could absorb DEC-83 #6 three-tier refresh discipline once cadence wired).

---

## Open items summary

See OPEN_ITEMS.md for full text.

**Closed this session:**
- **OI-NEW-4** (Algolia portion) — Starting Blocks Algolia smoke test integration shipped via `algolia_reconcile.py --smoke-test-only`. Refresh procedure documented in module docstring. Smoke test verified PASS this session (71 hits at Haymarket centroid, matching pilot's 2026-04-28 baseline exactly). Community Profiles retirement audit remains separate (open).

**Opened this session:**
- **OI-NEW-22** — Provider-level enforcement actions + conditions extraction deferred. Preserved in `service_external_capture.payload_json` but not extracted to structured rows pending provider→entity reconciliation work. ~0.5 sess when picked up.
- **OI-NEW-23** — FDC services Algolia-index gap. Family Day Care services don't appear in Starting Blocks Algolia (centre-based services only); reconciliation logic for FDC needs alternate discovery path. Tracking only; not blocking V1.

**Carried (unchanged):** OI-01–04, OI-06–10, OI-12–17, OI-19 (V1.5 partial close — daily-rate-integration A8 dependency now released; main remaining is A5/A6/B1/B3/B4/B5/C2-other/C6), OI-20–22, OI-24, OI-26, OI-28, OI-31, OI-33, OI-35, OI-NEW-1, OI-NEW-2, OI-NEW-3, OI-NEW-5 (Algolia portion now closed; Community Profiles + SEEK/Indeed audit remains), OI-NEW-6 through OI-NEW-21 (NEW-21 closed prior).

---

## Doc set

Update history:
- 2026-04-29c+d → 2026-04-30 → 2026-05-03 (V1.0 ship at `bcdf84c`)
- 2026-05-04 (V1.5 scoping + C3 + A1 + A2 + B2 + C2-NES) → 2026-05-05 (OI-36 close + delta badge)
- 2026-05-09 (DEC-79 commercial repositioning; CLAUDE.md + PRODUCT_VISION.md introduced)
- 2026-05-10 (A10 + C8 morning, A3 + StreamC PM, A4 Schools PM s2, OI-NEW-21 polygon-first rebuild PM s3)
- **2026-05-11 (this session)** — DEC-83 Commercial Layer V1 ship + Tier-2 monolith refresh. PROJECT_STATUS / OPEN_ITEMS / ROADMAP / CENTRE_PAGE_V1_5_ROADMAP / PHASE_LOG all updated. DECISIONS.md gains DEC-83 (with same-session amendment header). New design doc `recon/daily_rate_integration_design.md`.
