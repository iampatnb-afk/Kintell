# Project Status

*Last updated: 2026-05-10 PM session 2 close — A4 Schools at SA2 shipped (DEC-82 first direct-primary-source ingest). Trajectory regression Patrick spotted during visual review confirmed pre-existing data gap (sa2_history.json covers 1,267/~2,400 SA2s); minted as OI-NEW-21 — V1-priority HIGH for next session per Patrick. The on-disk version supersedes the project-knowledge monolith if they disagree.*

> **NEXT-SESSION HEADLINE:** start with **OI-NEW-21 — Catchment trajectory coverage gap** (V1 priority HIGH per Patrick). See OPEN_ITEMS.md for the full investigation path + fix-shape estimates. Address before A5/A6/B/C remaining work.

## Headline (2026-05-10 PM session 2)

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

**HIGHEST V1 PRIORITY — OI-NEW-21: Catchment trajectory coverage gap.** Surfaced during A4 visual review on 2026-05-10 PM session 2: `docs/sa2_history.json` covers 1,267 of ~2,400 Australian SA2s; the 1,133 absent SA2s render no catchment-position trajectories. Two of the four verifying SA2s (Bentley-Wilson WA, Outback NT) are in the gap. Patrick: this **must** be fixed for V1 — a ~47% national coverage gap on the headline credit-direct trajectory rendering is unacceptable for a commercial product. **Address before A5 / A6 / B / C remaining work.** ~0.3-0.7 sess depending on root cause (filter, structural, or missing-denominator). Probe first per DEC-65 — read `build_sa2_history.py` to identify the SA2 coverage filter, then decide between relaxing the filter, building a fallback trajectory path, or adding upstream ingest for missing denominators. Full investigation path + likely fix shape detailed in OI-NEW-21 (OPEN_ITEMS.md).

**V1.5 next-session priority** (after OI-NEW-21 closes): **A5 — Subtype-correct denominators (~0.3 sess)** OR **A6 — SALM extension (~0.2 sess)**. A5 is more impactful (refines `sa2_supply_ratio` per LDC/FDC/OSHC subtype — credit-direct metric); A6 is faster (promotes LFP triplet from Lite to Full row weight). Either can be picked first; both are independent.

**V1.5 path remaining (~0.5-0.7 sess + OI-NEW-21 ~0.3-0.7 sess = ~0.8-1.4 sess):**
- **OI-NEW-21** (~0.3-0.7 sess) — **HIGH** Catchment trajectory coverage gap fix
- **A5** (~0.3 sess) — Subtype-correct denominators (LDC/FDC/OSHC distinct catchment populations)
- **A6** (~0.2 sess) — SALM extension (promotes LFP triplet from Lite to Full)
- **B1, B3, B4** (~0.7 sess) — Phase B core (B1 = `sa2_jsa_vacancy_rate` peer banding; B3 = schools-derived banding [partially done with A4]; B4 = subtype-aware banding depends on A5)
- **C2-other + C6** (~0.4 sess) — Phase C core remaining (depend on B-pass)

See **CENTRE_PAGE_V1_5_ROADMAP.md** for the canonical V1.5 dependency-ordered queue and **ROADMAP.md** for the parent dependency view.

**Optional housekeeping (low priority, anytime):**
- **OI-12** — DB backup pruning. **CRITICAL** at ~8.5 GB cumulative. Keep policy needs relaxation.
- **OI-35** — `layer3_apply.py` real fix (~0.5 sess).
- **OI-13** — Frontend file backups gitignore tightening (~30 sec; +3 new `pre_oi36*` backups this session).
- **OI-14 / OI-15** — Date parsing + ARIA+ format codebase scans.
- **OI-10** — `provider_management_type` enum normalisation.
- **OI-28** — `populate_service_catchment_cache.py` cosmetic banner (5 sec).
- **STD-37 candidate** — "search project knowledge before probing" mint.
- **Recon probe sweep** — root probes → `recon/probes/`.

---

## Database state

Path: `data\kintell.db` (~565 MB). 36 tables. **`audit_log: 149 rows`** (unchanged this session — OI-36 was renderer-only, no DB mutations).

**No new DB backups this session** (renderer-only work). Cumulative ~8.5 GB across 41+ files unchanged.

`docs/sa2_history.json`: v2 multi-subtype, 13.2 MB, 50 quarters, 1,267 SA2s, 4 subtype buckets. Tracked in git. Unchanged this session.

---

## Git state

V1 ship: `bcdf84c` (2026-05-03 evening).

This session's commits, chronological:

1. `9d49be9` — Catch-up regen of Tier-2 docs to 2026-05-04 EOD (closes STD-35 hygiene gap from `7e1ab91`)
2. `430009a` — OI-36 close: sa2_nes_share renders in Catchment Position card + delta badge on Lite rows (centre.html v3.25→v3.28 + centre_page.py v20→v21)
3. End-of-session doc refresh (this commit, landing now)

**HEAD: `<this commit's sha>`.** Origin/master is at `7e1ab91`; will need a push at end of session.

### centre.html v3.25 → v3.28 sub-history

- v3.25 → v3.26 (commit `430009a` part 1) — added `sa2_nes_share` to `renderCatchmentPositionCard.order` array
- v3.26 → v3.27 (commit `430009a` part 2) — added `_renderLiteDelta(p)` helper + wired into `_renderLiteRow` template
- v3.27 → v3.28 (commit `430009a` part 3) — currency branch fix: matched actual `currency_weekly` / `currency_annual` formats (v3.27 mistakenly matched `currency_aud` which doesn't exist in this codebase)

All three sub-versions in one commit per DEC-22 (verified together).

---

## Standards / decisions

**No new STDs locked this session.**

**No new DECs locked this session.**

Banked items unchanged from 2026-05-04: STD-37 candidate (search project knowledge before probing), DEC-78 candidate (NES storage convention).

---

## Open items summary

See OPEN_ITEMS.md for full text.

**Closed this session:**
- **OI-36** — centre.html / centre_page.py hardcode catchment-position rows. Closed in commit `430009a` (surgical render-order patch + bonus delta badge on all Lite rows).

**Opened this session:** none.

**Carried (unchanged):** OI-01–04, OI-06–10, OI-12–17, OI-19, OI-20–22, OI-24, OI-26, OI-28, OI-31, OI-33, OI-35.

---

## Doc set

The 2026-04-28 restructure produced the 12-doc set, since extended with `CENTRE_PAGE_V1.5_ROADMAP.md` (2026-05-04). Update history:

- 2026-04-29c+d → 2026-04-30 → 2026-05-03 morning → 2026-05-03 PM → 2026-05-03 evening (V1 ship at `bcdf84c`)
- 2026-05-04 (full day) — V1.5 scoping pass + C3 ship + A1 dissolution + A2 end-to-end + B2 + C2-NES (data side) + OI-34 closed + OI-35 + OI-36 minted. End-of-session commit `7e1ab91` landed only `CENTRE_PAGE_V1.5_ROADMAP.md` + monolith.
- **2026-05-05 (this session)** — Catch-up regen of stale Tier-2 docs (`9d49be9`) + OI-36 close (`430009a`) + end-of-session doc refresh (this commit, landing now). Tier-2 docs all current at 2026-05-05 EOD content.
