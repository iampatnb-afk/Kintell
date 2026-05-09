## 2026-05-10 PM — Layer 4.4 A3 + Stream C bundle ship

**Session type:** Probe → design → ratify → ingest → banding → render → smoke-test → tier-2 doc refresh. End-to-end V1.5 close in one session.

**Context entering session.** A10 + C8 Demographic Mix bundle had shipped this morning (audit_id 158). The roadmap (`CENTRE_PAGE_V1_5_ROADMAP.md`) flagged A3 + Stream C as the next priority — bundled because both share the 2021 TSP zip + the existing ABS ERP workbook. Patrick green-lit autonomous execution past the design ratification gate.

**Work shipped this session.**

**1. Probe (DEC-65).** New probe `recon/probes/probe_a3_streamc_columns.py` confirmed:
- T05 marital column shape: `C{yr}_{age}_{Mar_RegM,Mar_DFM,N_mar,Tot}_{M,F,P}` across 16 age bands × 3 sexes × 3 census years. No Sep/Div/Wid in TSP short-header — complement of "partnered" is NSDW combined, not just never-married. T05A/B/C split by year.
- T07 fertility column shape: `C{yr}_AP_{age}_NCB_{0..6mor,NS,Tot}` (women only — AP = aged persons female). 15 age bands × 9 NCB cuts × 3 census years. T07A/B/C split.
- ERP `Population and People Database.xlsx` Table 1: Persons 25-29..40-44 sit at cols 89-92 (one column per 5-year band). Total persons at col 3 (NOT col 121 as the original Layer-2-step-6 diag mis-guessed; col 121 is fertility rate decimal). Locked in DEC-81 #6.

**2. Design doc + scope ratification.** `recon/a3_streamc_design.md` drafted with D-B1 through D-B5. Patrick ratified with one amendment: 35-44 fertility cohort "feels old" for childcare relevance — added a parallel 25-34 cohort as the active-childcare-timing signal. Sub-panel grows from 4 to 8 Lite rows; total Catchment Position card now 13 rows. Density tradeoff acknowledged.

**3. Ingest (`layer4_4_step_a3_streamc_apply.py`).** Single bundled script ingesting 4 metrics into `abs_sa2_education_employment_annual`:
- `erp_parent_cohort_25_44_share_pct` — 14,120 rows, annual 2019-2024
- `census_partnered_25_44_share_pct` — 7,063 rows, Census 3-point
- `census_women_35_44_with_child_share_pct` — 7,072 rows, Census 3-point
- `census_women_25_34_with_child_share_pct` — 7,069 rows, Census 3-point

Pre-mutation `recon/db_inventory.md` snapshot per STD-30. Single backup `data/pre_layer4_4_step_a3_streamc_20260510_005147.db` (548.1 MB). audit_id 159-162 written. Dry-run caught the col-121 bug before any write — re-run with col 3 produced sane national totals (28.20% / 65.56% / 78.43% / 41.19%).

**4. B-pass banding (`patch_b2_layer3_add_a3_streamc.py`).** 4 entries appended to `layer3_apply.py` METRICS list, all `state_x_remoteness` cohort. `layer3_apply.py --apply` lands ~9,420 banded rows; `layer3_x_catchment_metric_banding.py --apply` rebuilds catchment metrics per OI-35 workaround. audit_id 163 + 164.

**5. C-pass render.** 4 surgical edits to `centre_page.py` v22 (LAYER3_METRIC_META, LAYER3_METRIC_INTENT_COPY, LAYER3_METRIC_TRAJECTORY_SOURCE, POSITION_CARD_ORDER each gain 4 entries) + 1 surgical edit to `docs/centre.html` v3.30 (`demoMetrics` array gains 4 keys). No new render helpers — existing `_renderLiteRow` + `_renderLiteDelta` handle both annual (parent-cohort 6-point) and 3-point (Census) trajectories transparently.

**6. Smoke-test capture.** `docs/a10_c8_review.html` rebuilt covering all 4 verifying SA2s; payload spot-check confirms all 13 catchment-position rows render with bands, deciles, and trajectories. Bondi Junction-Waverly NSW shows the urban late-fertility profile (parent-cohort 39%, partnered 62%, w35-44 60.9%, w25-34 just 11.3%) — clean separation from Outback NT (32%, 47%, 84.5%, 72.1%).

**7. DEC-81 minted.** Locks 6 things: (1) the 4-metric V1 scope; (2) sharp 25-44 partnered window matching parent cohort; (3) two fertility cohorts not one — 25-34 active vs 35-44 completed; (4) NS-handling: numerator + denominator both exclude `NCB_NS`; (5) NSDW caveat for partnered (T05 short-header limitation); (6) ERP `total_persons` at col 3.

**State at session end.** A3 + Stream C closed end-to-end. Demographic mix sub-panel locked at 8 rows. V1.5 path remaining ~2.1 sess (A4 schools next). audit_log 158 → 164.

---

## 2026-04-29 — Layer 4.3 design closure

**Session type:** Decision closure + doc-set update. No code, no DB mutation.

**Context entering session.** Layer 4.3 design v1.0 (`recon/layer4_3_design.md`, committed 2026-04-28b) had surfaced four decisions G1–G4 + §9.4 plus three implementation threads A/B/C. Closure was tracked as OI-18, gating Layer 4.3 implementation.

**Work shipped this session.**

**1. Layer 4.3 design closures.** Worked through all five threads:
- **G1 + G2 merged → DEC-74** (Perspective toggle on reversible ratio pairs). Recognised that supply_ratio/child_to_place and demand_supply/demand_supply_inv form two interpretive pairs. Per-row toggle pill swaps primary metric, band-copy template, and intent-copy line; preserves underlying decile. Default = credit lens. Supersedes DEC-72 by promoting its conventions into the toggle pattern.
- **G3 → STD-34 locked.** Calibration discipline moved from STAGED to locked. `catchment_calibration.py` is the named module. `calibrate_participation_rate()` signature locked: `(income_decile, female_lfp_pct, nes_share_pct, aria_band) → (rate, rule_text)`. Default 0.50, range [0.43, 0.55], ±0.02 nudges.
- **G4 → OI-19.** Layer 4.4 ingests (NES, parent-cohort 25–44, schools) deferred to V1.5. Documented gap on calibration function's NES nudge; promote immediately post-V1.
- **G5 added → DEC-75** (Visual weight by data depth). Three row weights: Full / Lite / Context-only. LFP triplet reclassified Lite (3 Census points isn't a trajectory); `jsa_vacancy_rate` reclassified Context-only and moves to the new Workforce supply context block.
- **Thread D added → DEC-76** (Workforce supply context block). New Position-level block alongside Population and Labour Market. Default open per credit-lens user. V1 rows: JSA IVI ANZSCO 4211 + 2411 (state-level vacancy), ECEC Award rates (national), Three-Day Guarantee policy (national). Each row has explicit "state-level — no SA2 peer cohort" stamp.
- **§9.4** implicitly resolved by 2026-04-28 doc restructure landing.

**2. Discipline call-out and corrective regen.** Mid-session, the user flagged two discipline gaps in how the closures were initially captured:
- The first attempt produced `recon/layer4_3_design_amendment_v1_1.md` as a separate file alongside the v1.0 design doc. Per STD-02 + STD-03/DEC-30, the correct artefact is `recon/layer4_3_design.md` with `v1.1` in the header — one design doc per layer, version-tracked.
- The closures were not promoted into the canonical structured docs in the same session.

The corrective work in this session: regenerated `recon/layer4_3_design.md` as v1.1 (replacing the amendment file, which is to be deleted in this session's commit), and fully updated DECISIONS.md, STANDARDS.md, OPEN_ITEMS.md, ROADMAP.md, PROJECT_STATUS.md to land the closures in the canonical doc set.

**Files touched:**
- `recon/layer4_3_design.md` v1.1 (replaces v1.0)
- `recon/layer4_3_design_amendment_v1_1.md` (deleted — superseded by v1.1)
- `recon/Document and Status DB/DECISIONS.md` (DEC-74, DEC-75, DEC-76 added; DEC-72 marked superseded; DEC-23, DEC-32, DEC-36 cross-references updated)
- `recon/Document and Status DB/STANDARDS.md` (STD-34 promoted from STAGED to locked)
- `recon/Document and Status DB/OPEN_ITEMS.md` (OI-18 closed; OI-19, OI-20, OI-21, OI-22 added; OI-06, OI-07, OI-11, OI-17 updated)
- `recon/Document and Status DB/ROADMAP.md` (Layer 4.3 effort 1.7 → 2.5 sessions; sub-passes revised; §3 closures logged; V1 path 5.4 → 6.2 sessions)
- `recon/Document and Status DB/PROJECT_STATUS.md` (refreshed for 2026-04-29)
- `recon/PHASE_LOG.md` (this entry)

**Effort estimates revised:**
- Layer 4.3: 1.7 → 2.5 sessions (+0.8 for DEC-74 toggle, DEC-75 row-weight, DEC-76 block, NCVER probe)
- Layer 4.2-A: unchanged at ~2.2 sessions
- Layer 4.4: unchanged at ~1.5 sessions (deferred per OI-19)
- V1 path remaining: 5.4 → 6.2 sessions

**No DB mutation.** No code shipped. No `audit_log` rows added.

**State at session end.** Layer 4.3 design v1.1 closed. Implementation now unblocked. Next session: Layer 4.3 sub-pass 4.3.1 (Thread A — per-chart range buttons on unemployment) per ROADMAP §1.

---

## 2026-04-29 — Layer 4.3 design closure

**Session type:** Decision closure + doc-set update. No code, no DB mutation.

**Context entering session.** Layer 4.3 design v1.0 (`recon/layer4_3_design.md`, committed 2026-04-28b) had surfaced four decisions G1–G4 + §9.4 plus three implementation threads A/B/C. Closure was tracked as OI-18, gating Layer 4.3 implementation.

**Work shipped this session.**

**1. Layer 4.3 design closures.** Worked through all five threads:
- **G1 + G2 merged → DEC-74** (Perspective toggle on reversible ratio pairs). Recognised that supply_ratio/child_to_place and demand_supply/demand_supply_inv form two interpretive pairs. Per-row toggle pill swaps primary metric, band-copy template, and intent-copy line; preserves underlying decile. Default = credit lens. Supersedes DEC-72 by promoting its conventions into the toggle pattern.
- **G3 → STD-34 locked.** Calibration discipline moved from STAGED to locked. `catchment_calibration.py` is the named module. `calibrate_participation_rate()` signature locked: `(income_decile, female_lfp_pct, nes_share_pct, aria_band) → (rate, rule_text)`. Default 0.50, range [0.43, 0.55], ±0.02 nudges.
- **G4 → OI-19.** Layer 4.4 ingests (NES, parent-cohort 25–44, schools) deferred to V1.5. Documented gap on calibration function's NES nudge; promote immediately post-V1.
- **G5 added → DEC-75** (Visual weight by data depth). Three row weights: Full / Lite / Context-only. LFP triplet reclassified Lite (3 Census points isn't a trajectory); `jsa_vacancy_rate` reclassified Context-only and moves to the new Workforce supply context block.
- **Thread D added → DEC-76** (Workforce supply context block). New Position-level block alongside Population and Labour Market. Default open per credit-lens user. V1 rows: JSA IVI ANZSCO 4211 + 2411 (state-level vacancy), ECEC Award rates (national), Three-Day Guarantee policy (national). Each row has explicit "state-level — no SA2 peer cohort" stamp.
- **§9.4** implicitly resolved by 2026-04-28 doc restructure landing.

**2. Discipline call-out and corrective regen.** Mid-session, the user flagged two discipline gaps in how the closures were initially captured:
- The first attempt produced `recon/layer4_3_design_amendment_v1_1.md` as a separate file alongside the v1.0 design doc. Per STD-02 + STD-03/DEC-30, the correct artefact is `recon/layer4_3_design.md` with `v1.1` in the header — one design doc per layer, version-tracked.
- The closures were not promoted into the canonical structured docs in the same session.

The corrective work in this session: regenerated `recon/layer4_3_design.md` as v1.1 (replacing the amendment file, which is to be deleted in this session's commit), and fully updated DECISIONS.md, STANDARDS.md, OPEN_ITEMS.md, ROADMAP.md, PROJECT_STATUS.md to land the closures in the canonical doc set.

**Files touched:**
- `recon/layer4_3_design.md` v1.1 (replaces v1.0)
- `recon/layer4_3_design_amendment_v1_1.md` (deleted — superseded by v1.1)
- `recon/Document and Status DB/DECISIONS.md` (DEC-74, DEC-75, DEC-76 added; DEC-72 marked superseded; DEC-23, DEC-32, DEC-36 cross-references updated)
- `recon/Document and Status DB/STANDARDS.md` (STD-34 promoted from STAGED to locked)
- `recon/Document and Status DB/OPEN_ITEMS.md` (OI-18 closed; OI-19, OI-20, OI-21, OI-22 added; OI-06, OI-07, OI-11, OI-17 updated)
- `recon/Document and Status DB/ROADMAP.md` (Layer 4.3 effort 1.7 → 2.5 sessions; sub-passes revised; §3 closures logged; V1 path 5.4 → 6.2 sessions)
- `recon/Document and Status DB/PROJECT_STATUS.md` (refreshed for 2026-04-29)
- `recon/PHASE_LOG.md` (this entry)

**Effort estimates revised:**
- Layer 4.3: 1.7 → 2.5 sessions (+0.8 for DEC-74 toggle, DEC-75 row-weight, DEC-76 block, NCVER probe)
- Layer 4.2-A: unchanged at ~2.2 sessions
- Layer 4.4: unchanged at ~1.5 sessions (deferred per OI-19)
- V1 path remaining: 5.4 → 6.2 sessions

**No DB mutation.** No code shipped. No `audit_log` rows added.

**State at session end.** Layer 4.3 design v1.1 closed. Implementation now unblocked. Next session: Layer 4.3 sub-pass 4.3.1 (Thread A — per-chart range buttons on unemployment) per ROADMAP §1.

---


## 2026-04-29 (continued) — Layer 4.3 sub-pass 4.3.1 (Thread A) + STD-35

**Context:** Resumed from the 2026-04-29 design-closure session. Implemented the first sub-pass of Layer 4.3 implementation. Surfaced and resolved a structural memory gap: project knowledge in claude.ai and the git repo are independent stores; without explicit synchronisation, every session starts blind. Codified the fix as STD-35.

**Shipped:**
- `docs/centre.html` v3.2 → v3.3 — Layer 4.3 sub-pass 4.3.1 (Thread A): per-chart range buttons (1Y/2Y) on the unemployment metric (`sa2_unemployment_rate`), and improved empty-state copy for SALM-missing SA2s.
- `recon/layer4_3_thread_a_probe.md` — probe + apply artefact, decisions A1–A6 closed in-line.

**Code mechanics:**
- New globals on `centre.html`: `_TRAJECTORY_OVERRIDE_YEARS` (per-metric override map), `_PER_CHART_RANGE_OPTIONS` (lookup, currently `{sa2_unemployment_rate: [1, 2]}`).
- New helpers: `_getEffectiveRangeYears(metric)`, `_setPerChartRange(metric, years, btnEl)`, `_renderPerChartRangeBar(metric)`.
- `_renderTrajectory(metric, p)` rewired to read effective range via `_getEffectiveRangeYears()`; per-chart bar emitted on both normal and empty-state returns.
- `renderPositionRow` `unavailable` branch extended: unemployment row gets a named SALM-suppression note instead of the silent em-dash; other metrics retain the em-dash.
- Net delta: +87 lines, all additive. No deletions, no payload-schema bump, no `centre_page.py` change.

**Decisions:**
- A1–A6 closed (per-chart state model, button placement, click-to-toggle semantics, metric-keyed lookup, SALM-missing copy, override scope). Recorded in `recon/layer4_3_thread_a_probe.md` §3 — implementation choices within DEC-73's scope, not new architectural decisions; no entries added to `DECISIONS.md`.

**Standards:**
- STD-35 (Process category) — Cross-session continuity via end-of-session monolith. Codifies the three-tiered project-knowledge / git-repo synchronisation discipline. Range bumped 1–34 → 1–35 in `STANDARDS.md`.

**Open items:**
- OI-23 raised (Low) — global trend-window bar disappears when Population card has no live data; Thread A makes the brittleness more material. Fix slotted for sub-pass 4.3.6 layout work. Recorded in `OPEN_ITEMS.md`.

**Doc updates this turn:**
- `STANDARDS.md` — STD-35 added; footer numbering note updated.
- `OPEN_ITEMS.md` — OI-23 added.
- `PROJECT_STATUS.md` — `centre.html` v3.3 stamped; sub-pass 4.3.1 marked SHIPPED; remaining sub-pass count updated; OI-23 added to summary; doc-set table STANDARDS row bumped (1–35, STD-35 added); V1 path remaining 6.2 → 5.9 sessions.
- `recon/PHASE_LOG.md` — this entry.

**Not yet done (carry forward):**
- Re-upload of the structured doc set to project knowledge — this session's regenerated docs (`STANDARDS.md`, `OPEN_ITEMS.md`, `PROJECT_STATUS.md`) need to land in claude.ai project knowledge before next session starts, otherwise the next chat opens with the same gap STD-35 was created to close.
- End-of-session Tier-2 monolith per STD-35 — should be produced now (or at next session close).

**Files committed this session (cumulative across both halves of 2026-04-29):**
- `recon/Document and Status DB/DECISIONS.md` (DEC-74, 75, 76)
- `recon/Document and Status DB/STANDARDS.md` (STD-34 locked; STD-35 added)
- `recon/Document and Status DB/OPEN_ITEMS.md` (OI-19, 20, 21, 22, 23 added; OI-18 closed)
- `recon/Document and Status DB/ROADMAP.md`
- `recon/Document and Status DB/PROJECT_STATUS.md`
- `recon/Document and Status DB/PHASE_LOG.md` (this entry + design-closure entry)
- `recon/layer4_3_design.md` v1.1 (closure session, retired post-consolidation)
- `recon/layer4_3_thread_a_probe.md` (apply session)
- `docs/centre.html` v3.3


## 2026-04-30 — Layer 4.3 closeout + Layer 2.5 ship + Layer 4.2-A.3 catchment ratios + 4.2-A.3a-fix polish + 4.2-A.3b industry thresholds

**Shipped:** 7 commits + 5 patches uncommitted-pending-composite-commit.

**Layer 4.3 closeout:**
- `8e944d9` Sub-pass 4.3.5: schema migration on `service_catchment_cache` (7 cols added; audit_id 138)
- `5eec075` Sub-pass 4.3.5b: rename capture_rate → demand_share_state (audit_id 139)

**Layer 2.5 ship:**
- `a65ee57` Sub-pass 2.5.1: populate `service_catchment_cache` (18,203 rows; audit_id 140)
- `4d49516` Sub-pass 2.5.1 v5: three null-coverage fixes (median_income year selection, seifa_irsd from services.seifa_decile, new_competitor_12m DD/MM/YYYY date parsing; audit_id 141)
- `b924524` Sub-pass 2.5.2: Layer 3.x catchment metric banding (9,035 rows for 4 metrics; audit_id 142)

**Layer 4.2-A.3:**
- `d12da0b` Catchment ratios wired into centre page + credit-block reorder (centre_page.py v8→v9, centre.html v3.9→v3.10, schema_version v4→v5; option α reorder)

**Layer 4.2-A.3a-fix (trajectory chart polish):**
- `beb7bbe` 4 chained centre.html iterations (v3.10→v3.13a): tooltip flip via external HTML readout, sparkline dot points, vertical crosshair plugin, X-axis label restoration, defensive readout parser

**Uncommitted (composite commit pending):**
- centre_page.py v9→v12: 4.2-A.3b industry thresholds (INDUSTRY_BAND_THRESHOLDS table) + F1/F1-β JSA IVI explainer (about_data field)
- docs/centre.html v3.13a→v3.17: industry band line render, workforce sparkline polish (v3.15), workforce-section local trend-window selector (v3.16), about_data render (v3.17)

**Open items new:** OI-25 (Census income trajectory single-point bug), OI-26 (demand_supply industry threshold post-launch calibration), OI-27 (sa2_history.json subtype rebuild for 4.2-A.3c), OI-28 (populator banner cosmetic).

**Open items closed:** OI-05 (service_catchment_cache populated), OI-23 (trend-window bar caption corrected — original framing was a misread).

**Standards / decisions:** No new STDs or DECs. DEC-77 candidate (industry threshold framework) flagged for next-session lock pending operator-use validation.

---

## 2026-05-03 — Doc-discipline catch-up + Layer 4.2-A.4 + OI-25 dissolution

Session opened with a stale framing in the kickoff message: "7 commits ahead of origin, uncommitted v9→v12 + v3.13a→v3.17 on disk". Reality (verified via `git status`): working tree clean, branch in sync with origin. The 4.2-A.3 work was already committed and pushed during the prior session (2026-04-30). The doc work, however, was NOT — the 30/04 session produced the regenerated artefacts but never moved them from `/mnt/user-data/outputs/` to disk OR uploaded the new monolith to project knowledge. This was the doc-discipline gap that defined the session.

### Block 1 — Doc-discipline catch-up

Located the 2026-04-30 artefacts in Patrick's Downloads folder (still there, timestamps 30/04 6:51 PM):
- `kintell_project_status_2026-04-30.txt`
- `PROJECT_STATUS.md`
- `ROADMAP.md`
- `OPEN_ITEMS.md`
- `PHASE_LOG_entry_2026-04-30.md`

Moved the four Tier-2 docs to `recon/Document and Status DB/` (overwriting the 29/04-era versions on disk). Appended PHASE_LOG entry. Committed as `a4104b6` — "2026-04-30 doc set landing". Synchronously updated project knowledge: deleted `kintell_project_status_2026-04-29d.txt`, uploaded `kintell_project_status_2026-04-30.txt`. Tier-2 .md files deleted from project knowledge as side-effect of the swap; flagged for re-upload at session end.

### Block 2 — OI-25 probe + dissolution

Per DEC-65 probe-before-code, wrote `probe_oi25_income_trajectory.py` (read-only, Patcher pattern STD-10) before touching `_layer3_position`. Probe reproduced the exact SQL `_metric_trajectory` runs against `abs_sa2_socioeconomic_annual` for the 3 Census-source income metrics on verification SA2 118011341 (Bondi Junction-Waverly), with NULL-coercion analysis matching the helper's behaviour.

Probe output: 11 rows in DB for `metric_name = 'median_equiv_household_income_weekly'`. 3 non-null (2011, 2016, 2021); 8 NULL (placeholder rows by ingest design). Backend `_metric_trajectory` correctly returns the 3 valid points and drops the NULLs. Visual confirmation on `centre.html?id=103` with Trend Window set to "All": 3 dots visible on the household income chart.

OI-25 dissolved. The "single point" symptom Patrick observed was almost certainly visible only because the Trend Window default clips Census 5-year-cadence data to the most recent point on shorter windows (3Y window cuts at 2018; only 2021 remains).

Real residual issue identified: a 3-point Census trajectory rendered as a Full-weight row is visually misleading (smooth interpolation over a decade implies more granularity than exists) and trend-window-fragile. Same shape as DEC-75's logic for the LFP triplet. Opened OI-29 for Lite-weight reclassification.

Patcher `patch_oi25_close_oi29_open.py`: 3 substitutions (close OI-25 in place with full resolution note; insert OI-29 after OI-28; bump last-updated). All pre-flight verified for exact-1 match. Committed as `6d30d33`.

### Block 3 — Layer 4.2-A.4 (STD-34 calibration metadata in DER tooltip)

Two-patcher sequence per DEC-22 (data first, then UI), collapsed to a single commit since both files were verified together.

**Backend** (`patch_centre_page_v12_to_v13.py`, 6 mutations):
- Added `_read_calibration_meta(con, sa2_code) -> Optional[dict]` helper, mirrors `_read_demand_share_state` pattern. Reads `calibrated_rate` + `rule_text` from `service_catchment_cache` once per SA2.
- Added `uses_calibration: True` to 3 metric entries in `LAYER3_METRIC_META`: `sa2_adjusted_demand`, `sa2_demand_supply`, `sa2_demand_share_state`. The other 2 catchment metrics (`sa2_supply_ratio`, `sa2_child_to_place`) are pure ratios and correctly do NOT opt in.
- Wired `calib_meta` read into `_layer3_position` after `cache_share` read.
- Per-entry attachment (with `meta.get("uses_calibration") and calib_meta` guard) in both the regular metric loop and the `sa2_demand_share_state` special-case branch.
- Bumped version v12 → v13.

Smoke test (`smoke_test_v13_calib.py`, written via heredoc to avoid PowerShell f-string mangling per STD-05): `schema_version=centre_payload_v6`; 3 catchment_position metrics carry `rule_text` + `calibrated_rate=0.54`; 2 don't, as expected.

**Renderer** (`patch_centre_html_v3_17_to_v3_18.py`, 6 mutations):
- Extended `renderBadge` with a `calibration` field handler (renders as "Calibration" key/value row in the tooltip; placed between Inputs and Threshold per semantic order).
- Added `_buildCalibrationRow(p)` helper — formats `<code>calibrated_rate=X.XX</code> — <htmlEscape rule_text>` when `p.rule_text` is set; returns `null` otherwise.
- Wired into `_renderFullRow` and `_renderLiteRow` DER badge calls (additive — silent absence on rows without `rule_text`).
- Structural change to `_renderContextRow`: added a conditional DER badge that didn't exist before. Carries source + calibration only (no cohort/decile fields — Context has no peer cohort by design). When `_buildCalibrationRow(p)` returns null, no DER badge renders, preserving the prior minimal Context look.
- Bumped version v3.17 → v3.18.

Visual check on `centre.html?id=103`: DER tooltips on Demand vs supply, Adjusted demand, Share of state demand all carry the new "Calibration" row with the full rule_text trace. Supply ratio and Children per place correctly do not.

Committed as `528f9be` — "Layer 4.2-A.4: STD-34 calibration metadata surfaced in DER tooltip".

### Block 4 — Doc-set regen (this regen)

Per STD-35: PROJECT_STATUS.md and ROADMAP.md regenerated to reflect Layer 4.2-A.4 ship + OI-25 dissolution + OI-29 add + doc-discipline gap closure. OPEN_ITEMS.md already current via the OI-25 patcher. This PHASE_LOG entry appended. New monolith `kintell_project_status_2026-05-03.txt` produced for project knowledge upload.

### Open items movement this session

**Closed:**
- OI-25 (sa2_median_household_income trajectory shows single point) — premise dissolved by probe; backend + renderer correct; "single point" was Trend Window clipping behaviour.

**Opened:**
- OI-29 (sa2_median_household_income should be Lite weight per DEC-75) — three Census points is not a trajectory, same logic LFP triplet got. ~0.1 session, renderer-only.

### Standards / decisions

No new STDs or DECs. DEC-77 candidate (industry threshold framework) still flagged for next-session lock.

**STD-35 reinforcement candidate:** the 30/04 → 03/05 doc-discipline gap demonstrated that "regenerate at session end" is necessary but not sufficient; "land on disk + upload to project knowledge" needs explicit verification. Worth a 2-line addition to STD-35 at next consolidation.

### Mood note for future sessions

This session opened with a stale framing in the kickoff message — wrong git state, wrong file versions. Probe-before-code (DEC-65) caught it: rather than executing the kickoff blindly, ran `git status` first and found the inconsistency. Same discipline saved a misdirected fix on OI-25 (probed first, dissolved the bug claim, rather than diving into `_layer3_position`). The substrate work (doc landing) ate ~1/3 of the session but was the right call — without it, every subsequent session would have re-paid the orientation tax. Patrick's pull-up midway ("have you done a full review of all the documents?") was the corrective intervention that triggered the substrate audit.

---

## 2026-05-03 PM — Layer 4.2-A.3c end-to-end ship + housekeeping cluster

Continuation of the 2026-05-03 morning session. 6 commits this afternoon delivering the largest remaining V1 piece (Layer 4.2-A.3c catchment trajectories) plus three planned housekeeping items (OI-29, OI-12, STD-13).

**Headline: V1 is at HEAD `bcdf84c`.** All blocking V1 items shipped.

### Block 1 — OI-29 close (commit `6a7fe8a`)

Single-line patcher flipping `row_weight: "lite"` on `sa2_median_household_income` in `LAYER3_METRIC_META`, plus version bump v13 → v14, plus closing OI-29 in OPEN_ITEMS.md atomically. Smoke test confirmed asymmetry preserved: household income (Census, 3 sparse points) now Lite/static; employee + total income (annual, 5 dense points 2018-2022) stay Full with charts.

### Block 2 — OI-12 inventory (commit `bbac24f`)

Patrick raised legitimate "what if we need this data later" concern when initial dry-run of `prune_db_backups.py` showed all 36 backups would be deleted. Wrote `inventory_db_backups.py` (read-only probe; opens each backup with SQLite mode=ro URI, captures audit_log + table+rowcount per backup). Output `recon/db_backup_inventory_2026-05-03.md` (2.97 MB, 6,129 lines). Result: deletion is now safely reversible — even if all binary backups go, the inventory preserves the queryable record. Disk space NOT reclaimed; deletion deferred until disk pressure becomes real.

### Block 3 — STD-13 helper (commit `1f72226`)

Wrote `proc_helpers.py` (Get-CimInstance Win32_Process via PowerShell shell-out) as the canonical Win11-safe replacement for the deprecated WMIC pattern in 4 historical mutation scripts. Self-test detected 3 real orphan python processes — confirmed the helper works correctly. Historical scripts intentionally NOT retrofitted (already shipped, idempotency-guarded; the harmless WMIC-skip warning doesn't block them).

### Block 4 — STD-13 doc extension (commit `c70e942`)

Patcher to STANDARDS.md adding "Mutation-script variant" subsection to STD-13 documenting `proc_helpers.py` as the canonical pattern for new mutation scripts. Original STD-13 (prophylactic kill before review_server) preserved; new subsection covers the orphan-detection variant.

### Block 5 — Layer 4.2-A.3c Part 2 (commit `36c2f78`)

Wholesale replacement of `build_sa2_history.py` (v1 → v2). Multi-subtype rebuild:
- Filter switches from `Long Day Care = Yes` flag to `Service Sub Type IN (LDC, OSHC, PSK, FDC)` column (with legacy fallback for older quarters)
- Per-quarter loop iterates over 4 subtypes; LDC processed first and mirrors into v1 top-level arrays for back-compat
- New `by_subtype` block per SA2 with parallel arrays per subtype + per-subtype `centre_events`
- `pop_0_4` / `income` stay top-level (subtype-independent); `supply_ratio` uses same `pop_0_4` denominator across subtypes (documented known simplification)
- Auto-copy from `data/sa2_history.json` to `docs/sa2_history.json` added (review_server serves docs/)

Build runtime: ~17 min on Patrick's machine (within the 15-25 min estimate). Output: 13.2 MB (was 5.2 MB v1), 50 quarters, 1,267 SA2s, all 4 subtype buckets populated. OSHC/PSK/FDC histories begin Q4 2021 (when `Service Sub Type` column first appears in NQAITS source); LDC has full 50-quarter coverage where ABS pop data exists.

**Design probes inverted prior framing.** The locked D5=b decision had assumed sa2_history.json events were "all-subtype" needing subtype filtering. Probe revealed the inverse: events were already LDC-only (filtered at the top of `process_sheet_sa2`), and we needed to EXPAND to multi-subtype, not filter down. Plus the verification centre service_id=103 was OSHC, which would have rendered empty under the original LDC-only design. Patrick's clarification ("LDC at the centre of its thinking") locked the LDC-first principle.

### Block 6 — Layer 4.2-A.3c Part 3 (commit `bcdf84c`)

Largest patcher work of the session. Two patchers (centre_page.py + centre.html) bundled into one commit per DEC-22 collapse pattern. Plus iterative bug fixes on visual review.

**Backend (centre_page.py v14 → v16, 11+4 mutations):**

v14 → v15:
- Added `import json` + `from pathlib import Path` (caught after first run)
- New `CATCHMENT_TRAJECTORY_METRICS = frozenset({...})` set
- New `_SA2_HISTORY_CACHE` module-level + `_load_sa2_history()` lazy-cached singleton
- New `_catchment_trajectory(sa2_code, metric_name, subtype, calibrated_rate)` helper returning `(points, kind, events)` matching `_metric_trajectory` shape plus events
- `_layer3_position` signature gains `service_sub_type` parameter; dispatches catchment metrics to new helper
- Single call site in `get_centre_payload` updated
- 4 catchment row_weights flipped Lite → Full

v15 → v16:
- DEC-74 perspective toggle removed from 3 reversible catchment metrics (post-promotion-to-Full, the toggle just swapped to data already visible as separate rows)

**Renderer (centre.html v3.18 → v3.21, 3+2+2 mutations):**

v3.19: New `_kintellEventAnnotation` Chart.js plugin (vertical dashed lines at centre entry/exit quarters; green=add, red=remove, grey=churn); wired into `_renderTrajectory` chart instantiation; data-driven via `opts.plugins.kintellEventAnnotation = {events}` (silently no-ops on Population/Labour charts that don't carry events).

v3.20: Bug 1 fix — `_yearOfPeriod` regex un-anchored to handle quarter format ("Q3 2013") that was returning NaN.

v3.21: Bug 1b fix — found a SECOND copy of the same regex inside `_filterTrajectoryByRange`. v3.20 fixed only the trend-label copy; this caused the trend window buttons (3Y/5Y/10Y/All) to have NO effect on catchment charts because the filter saw NaN and bailed out. With both fixed, trend window now works.

**Verified visually on:**
- Sparrow Early Learning Bayswater (svc 2358, LDC, VIC) — primary V1 path
- Kool HQ Waverley (svc 103, OSHC, NSW) — secondary subtype path

### DEC-74 amendment

Recorded as appended block in DECISIONS.md. Original DEC-74 design (perspective toggle on reversible ratio pairs) made sense for Lite-weight rows where the toggle saved the credit reader from mental math. Post-promotion to Full, the inverse views render as separate rows in the same card — toggle becomes redundant by construction. Toggle fields removed from META; renderer gates on `p.reversible` so removal cleanly hides the toggle without renderer change.

### Open items movement this session (PM)

**Closed:**
- **OI-29** (Lite reclassification of household income per DEC-75) — landed via Block 1
- **OI-27** (sa2_history.json subtype tagging for new-centre overlay) — landed via Block 5 (build) + Block 6 (renderer wiring)

**Opened:**
- **OI-30** — Bayswater (and likely other 2021-ASGS SA2s) have incomplete pre-2019 ABS coverage. Discovered during Layer 4.2-A.3c verification: only 23/50 quarters have supply_ratio for SA2 211011251 because ABS `pop_0_4` only exists Q3 2019+. Likely an ASGS-version concordance issue. V1.5 build script work.
- **OI-31** — Click-to-detail on event overlay lines (Bug 6 deferred from visual review). Vertical lines render correctly; clicking should show centre names + place changes. Substantial renderer feature; ~1 session.
- **OI-32** — Catchment metric explainer text (Bug 4 deferred from visual review). Patrick will provide copy.

### Patcher pattern observation worth banking

The v15 patcher (11 mutations including 8 multi-line anchors) initially failed all 8 multi-line anchor checks because the `OLD` strings used `\r\n` line endings. Python's text mode normalises `\r\n` to `\n` on read, so the literal anchors didn't match the in-memory text. One-line bash sed fix on the patcher (`\r\n` → `\n` in OLD literals) made all anchors hit. Worth a 1-line addition to STD-10 (Patcher pattern): "anchors must use `\n` even on Windows source files."

### Session shape

Long session (started morning, continued afternoon). 10 commits total today plus end-of-session doc commit. V1 at HEAD. Patrick's pull-up at the start of the afternoon ("the buttons aren't working — re-render but data doesn't change") triggered the second regex bug discovery that v3.20 had missed. Without that visual verification, the Bug 1b would have shipped as a silent regression in the trend window machinery for catchment metrics.

DEC-65 probe-before-code earned its keep this session: at start (OI-25 dissolved before any wasted backend work), at Layer 4.2-A.3c Part 1 (probes inverted the build's data shape assumption), at OI-30 discovery (Bayswater sparsity diagnosed before any "fix" attempt), and at Bug 1b (probed the regex twice, found two copies, fixed both).

### What's banked for next session

V1 is shippable. Optional polish queue (~ small / negotiable):
- Bug 4 (explainer text — needs Patrick's copy)
- OI-30 probe (ASGS coverage scope)
- DEC-77 lock (industry threshold framework)
- Various housekeeping (gitignore, untracked sweep, "Remara" hangover)

V1.5 path queued:
- OI-31 (click-on-event detail)
- OI-32 (absolute change alongside %)
- Layer 4.4 ingests bundle (NES + parent-cohort + schools + SALM-ext)
- Subtype-correct denominators (folds into Layer 4.4)


---

## 2026-05-03 (evening) — OI-32 close + DEC-77 mint + OI-30 probe + OI-12 dry-run

Continuation session. V1 was at HEAD `bc52f3c` at session start. Ended at `54bacfe` after the polish + doc bundle. 4 commits this evening (3 code + 1 doc).

### Session shape

Polish round on the catchment-position card surfaces, driven by operator visual review. Three iterative polish rounds on the same OI-32 deliverable plus a hypothesis-refuting probe (OI-30) and a deferred-decision dry-run (OI-12). Pattern: probe → propose copy → ship → operator visual review → repeat. Each round caught regressions or category errors the previous round didn't see — the "below break-even" fix in particular was a category error (asserting profitability conclusion from a supply/demand ratio) that only became visible after the "fill" cleanup landed.

### Block 1 — OI-32 round 1+2 (commit `1a90bf7`)

`patch_oi32_about_data.py` + `patch_oi32_polish.py` bundled into single commit per DEC-22 collapse pattern.

**Backend (centre_page.py v16 → v18, 7 mutations across 2 patchers):**

v17 (about_data field added):
- New module-level constant `LAYER3_METRIC_ABOUT_DATA` carrying plain-language "what is this metric?" copy for the 4 Full-weight catchment metrics
- `_layer3_position` propagates `p.about_data` onto stub + populated entries via `LAYER3_METRIC_ABOUT_DATA.get(metric_name)` — same shape as `intent_copy` propagation

v18 (operator review of v17 visuals):
- Panel font 11.5px → 12.5px in `_renderAboutData`
- `sa2_demand_supply` about_data text reframed from "fill expectation / fill risk" to "occupancy ramp-up / trade-up risk"
- INDUSTRY_BAND_THRESHOLDS sa2_demand_supply: replaced "fill" terminology in band labels/notes; removed generic "below 70% break-even at typical 85% occupancy" note

**Renderer (centre.html v3.21 → v3.23, 5 mutations across 2 patchers):**

v3.22:
- New `_renderAboutData(p)` helper rendering p.about_data as permanent visible "About this measure" panel (uppercase label, left-border, muted background, splits on `\n\n` for paragraphs and `\n` within paragraphs for line breaks)
- Inserted call inside `_renderFullRow` between `_renderIntentCopy(p)` and the DER/COM badge row
- Reuses visual pattern from workforce-row about_data block (v3.17)

v3.23:
- Font bump 11.5px → 12.5px in the About panel container

### Block 2 — OI-32 polish r2 (commit `83738ac`)

`patch_oi32_polish_r2.py`. Operator screenshot review caught remaining "fill"/"soft" surfaces that round-1 didn't cover.

**Backend (centre_page.py v18 → v19, 6 mutations):**

- `band_copy` chips on `sa2_demand_supply` reframed: "soft catchment — fill risk" → "supply outweighs demand — trade-up risk"; "demand pull — strong fill expected" → "demand outweighs supply — fast occupancy ramp"
- `LAYER3_METRIC_INTENT_COPY` sa2-prefixed entries cleaned: `sa2_demand_supply`, `sa2_supply_ratio`, `sa2_adjusted_demand` all had visible "fill" terminology in the italic intent line
- INDUSTRY_BAND soft-band label "soft ramp-up" → "below break-even" (key stays "soft" because centre.html cautionKeys references it for visual treatment)
- Unprefixed duplicate INTENT_COPY entries left alone (kept for backward reference per existing comment, not read by `_layer3_position`)

**Diagnosis interlude.** Operator's first screenshot post-Block 1 showed unchanged old text. Initially diagnosed as browser cache. Probe of `centre.html` revealed the page fetches `/api/...` from `review_server.py` — a long-running Python process that imports `centre_page` at module load. Python module cache prevents on-disk `centre_page.py` changes from taking effect until server restart. Operator restarted server (multiple instances had to be killed first via Win11-safe `Get-CimInstance Win32_Process` filter); v17/v18 changes then visible. Worth banking as a reminder for any future centre_page.py mutation.

### Block 3 — OI-32 v20 bundle

`patch_oi32_v20_bundle.py`. Operator review of v19 surfaced two more issues:

1. The INDUSTRY label "below break-even" makes a profitability claim the demand/supply ratio alone cannot support (break-even depends on price, cost base, ramp curve, mix). Same category-error fix at the about_data level: "the occupancy ramp-up expectation for a centre here" overreaches similarly.
2. Cohort histogram needs explainer text + horizontal centering. SEIFA decile would benefit from a visual position indicator (mini decile strip chosen over colour-coding because SES has no valence in LDC credit).

**Backend (centre_page.py v19 → v20, 3 mutations):**

- INDUSTRY_BAND_THRESHOLDS sa2_demand_supply parallel-framed in supply-vs-demand language only:
  - soft → "supply heavy" / "demand well short of available capacity"
  - near_be → "supply leaning" / "demand below available capacity"
  - viable → "approaching balance" / "demand and supply broadly aligned"
  - strong → "demand leading" / "demand exceeds available capacity"
- about_data first line tightened: "How supply compares to realistic demand — a key input to occupancy ramp expectations"

**Renderer (centre.html v3.23 → v3.24, 4 mutations):**

- `_renderCohortHistogram` ships centred italic explainer text below the bars; cohort-note alignment switched from right to centre
- New `_renderMiniDecileStrip(decile)` helper — compact 10-cell horizontal strip, same colour grammar as `_renderDecileStrip` (per-decile tones 6%/13%/20%, accent + outline on active cell, structural gaps between bands), inline-sized (6px wide cells, 10px tall, no number labels)
- SEIFA decile fact in Catchment section gains inline `_renderMiniDecileStrip` call

### Block 4 — DEC-77 mint

Industry-absolute threshold framework formalised. Layer 4.2-A.3b shipped (2026-04-30) the framework; v20 round finalised the demand_supply labels. Now operator-validated and locked. DEC-77 entry recorded in DECISIONS.md.

### Block 5 — OI-30 probe (read-only; recon artefact)

`probe_oi30_asgs_coverage.py`. Per DEC-65, probe-before-design.

**Result: hypothesis refuted.** Bondi Junction-Waverly (118011341 — established 2016-ASGS area, no expected concordance issue) shows the same 6-year coverage (2019-2024) as Bayswater (211011251). 98.9% of catchment-anchored SA2s (2,269 / 2,294) sit in the same 6-11 year coverage bucket. The issue is platform-wide: `abs_sa2_erp_annual` ingest covers 2019-2024 across the entire dataset, not a code-mismatch between ASGS editions.

**Disposition:**
- OI-30 closed (probe complete; hypothesis refuted; real fix is platform-wide ABS ERP ingest extension that folds into OI-19 V1.5 bundle).
- 25 outlier SA2s (16 zero + 9 sparse) split out as new OI-33 for tracking.
- Probe artefact written to `recon/oi30_asgs_coverage_probe.md`.

### Block 6 — OI-12 prune dry-run

`prune_db_backups.py` (no `--apply`). Reported **0 deletions** under current default-conservative keep policy: all 36 backups in current set qualify as either `pre_*` named milestone anchors (34) or within most-recent-3 timestamped (2).

**Disposition:** OI-12 status updated with this finding. Operator decision needed on relaxing keep policy if disk pressure becomes real (legacy `pre_step*`/`pre_layer3` anchors dominate the 7.7 GB and are now historically inert). No deletion executed this session.

### Open items movement this session (evening)

**Closed:**
- **OI-32** (Catchment metric explainer text, Bug 4) — 3 polish rounds shipped via Blocks 1-3
- **OI-30** (pre-2019 pop_0_4 coverage gap) — closed by Block 5 probe; real fix folds into OI-19

**Opened:**
- **OI-33** — 25 outlier SA2s with zero/sparse pop_0_4 coverage (split from OI-30 probe finding). Tracking only.

**Updated:**
- **OI-12** status note: prune dry-run reported 0 deletions; operator decision on policy relaxation deferred
- **OI-19** scope expanded: ABS ERP backward extension folds in (~0.3 session added to bundle)

### Standards / decisions

**New:** **DEC-77** — Industry-absolute threshold framework for catchment ratios. Recorded in DECISIONS.md.

**No STD changes.**

### What's banked for next session

V1 is shippable and at HEAD. Optional polish queue:
- Various housekeeping (gitignore tightening OI-13, OI-28 cosmetic banner, codebase scans OI-14/OI-15)
- OI-12 keep-policy relaxation decision (only if disk pressure bites)

V1.5 path:
- OI-19 V1.5 ingest bundle (NES + parent-cohort + schools + SALM-extension + ABS ERP backward extension per OI-30 finding) — ~2 sessions
- OI-31 click-on-event detail — ~1 session

### Session shape note

Iterative polish on a single OI took 3 rounds because each round surfaced category errors the previous round didn't see. The pattern (operator screenshot → I propose fix → ship → operator screenshot → repeat) is the right mode for visual/copy work — caught issues that abstract review would have missed (notably the "below break-even" profitability overreach which only became visible once the cruder "fill"/"soft" cleanup made room to read the surface critically). DEC-65 probe-before-code earned its keep at OI-30 — refuted the original hypothesis before any concordance code was written, saving ~0.5 session.

---

## 2026-05-04 (full day) — V1.5 scoping + C3 + A1 dissolution + A2 end-to-end + B2 + C2-NES (data side)

V1 was at HEAD `bcdf84c` at session start (with `d9b109e` STD-36 archive commit on top). Ended at `3ddcf18` after 7 commits this session (plus the doc-refresh commit landing this entry).

### Session shape

Long single-day session split into morning and afternoon halves. Morning shipped the V1.5 scoping pass + C3 polish + A2 NES ingest end-to-end. Afternoon discovered a unit-convention issue in A2 (storage as fraction vs project's `census_*_pct` percentage convention) and corrected it via v3 ingest + wire-fix patcher; then added NES to layer3 banding (B2) and registered it in centre_page.py (C2-NES data side). Hit a `layer3_apply.py` wholesale-rebuild bug that wiped catchment banding rows; recovered. Render-side of C2-NES held over to next session as OI-36 — `centre.html` hardcodes catchment rows so a new card='catchment_position' meta entry doesn't auto-render.

Two key process lessons banked: **(1) search project knowledge before probing** (operator nudge after the A1 probe trail re-discovered findings already in 2026-04-28b status); **(2) unit conventions matter early** — the v2-as-fraction storage in A2 would have rendered as "0.31%" if we'd shipped C2-NES rendering without catching the convention mismatch.

### Block 1 — V1.5 centre-page scoping pass (commit `f92b517`)

Produced `CENTRE_PAGE_V1.5_ROADMAP.md` as a single source of truth for V1.5 centre-page work. Three phases: Phase A (ingest), Phase B (banding), Phase C (render). Recommended ship slice ~3.3 sess. Out of scope: operator-page work, industry view (DEC-36), the daily-rate parallel stream itself.

### Block 2 — A1 probe trail and dissolution

Per DEC-65, A1 (ABS ERP backward extension for pre-2019 `pop_0_4`) gated on probe. Four read-only probes (`recon/probes/probe_a1_*.py`) established that:

1. `abs_sa2_erp_annual` already has rows for 2011/2016/2018 but NULL persons values for `under_5_persons` (label is `under_5_persons` not `0-4`).
2. `build_sa2_history.py` reads from `abs_data/Population and People Database.xlsx` (Excel), not the DB table. The DB NULL rows are placeholders from an earlier ingest pattern.
3. The Excel source itself publishes `'-'` (suppressed/unavailable) for `Persons - 0-4 years (no.)` in 2011/2016/2018. Verified for both Bayswater (211011251) and Bondi Junction-Waverly (118011341).
4. The 6-point series is the actual ABS source ceiling, not a code-side filter.

**Cross-reference with prior knowledge** (per operator nudge): the 2026-04-28b Layer 4.2 probe had already documented this finding — "Under-5 / Total pop: 6 dense annual points 2019-2024 (3 NULLs in 2011/2016/2018)". The A1 framing in `CENTRE_PAGE_V1.5_ROADMAP.md` v1 had treated this as an extensible code constraint; the probes confirmed it is a source-data constraint.

**Disposition:** A1 dissolved. Forward paths (Census 2011/2016 SA2 age tables; demographic derivation from births × cohort-survival; ABS TableBuilder pull) are real but not V1.5-critical.

### Block 3 — C3 ship (commit `f47a0ba`)

Pivoted from A1 to C3 (absolute-change alongside trend % on catchment trajectory charts). Renderer-only, single-file edit.

**Approach:** STD-10 patcher pattern. `patch_centre_html_v3_24_to_v3_25.py` — idempotent, dry-run-by-default, STD-12 line-ending detection at runtime.

**Edits:** centre.html v3.24 → v3.25.
- New helper `_computeEventAbsChange(events, startPeriod)` aggregates `centre_events.places_change` and `centre_events.net_centres` for events at or after the active trend-window startPeriod.
- `trendLabel` template extended to interpolate the abs-change suffix.
- Format: `±N.N% since YYYY · +N places · +M centres` (singular when |M|=1, sign always shown).

Silent absence per P-2 when `p.centre_events` absent or empty.

**Smoke test:** Sparrow Early Learning Bayswater (svc 2358). Supply ratio reads `+51.4% since 2020 · +303 places · +3 centres`. Tracked as **OI-34** (minted+closed same session).

### Block 4 — A2 v2 NES share ingest (commit `fdc85bd`)

Layer 4.4 first piece. NES (Non-English Speaking) household share at SA2.

**Source discovery (Block 4a — probes).** Four probes establishing:
1. Project DB has 6 metric_name slots in `abs_sa2_socioeconomic_annual` (income only) and 22 in `abs_sa2_education_employment_annual` (LFP, employment, education, no NES). No NES anywhere in the DB.
2. Calibration interface is clean: `catchment_calibration.py:198` takes `nes_share_pct: Optional[float]` with thresholds at 0.30 and 0.05 (these are FRACTIONS despite the `_pct` suffix — STD-34 inconsistency noted).
3. Source on disk: `abs_data/2021_TSP_SA2_for_AUS_short-header.zip` (43.8 MB). No fresh ABS pull required.
4. Census 2021 TSP zip contains 35 T-tables. Metadata Excel maps T08 → Country of Birth, T09 → Ancestry, T10 → Language used at home, T11 → Proficiency in spoken English, etc.
5. T10 split into T10A + T10B. T10A has `Uses_Engl_only_*` per Census year. T10B has `Tot_*` (denominator) and `Lang_used_home_NS_*` (Language not stated).

**Initial formula error (caught by sanity check).** v1 formula `(total - english_only) / total` produced national 2021 share of 28.0%, vs published ABS ~22%. The ~6 percentage-point gap was because v1 used T01's total (broader scope) and treated "Language not stated" as NES. Fixed in v2.

**v2 formula.** `(Tot - Uses_Engl_only - Lang_used_home_NS) / Tot` from T10B + T10A. Excludes "not stated" from numerator; uses T10's own scope as denominator. National 2021 = 22.28% — bang in published 22-24% band.

**Storage:** `abs_sa2_education_employment_annual` table, `metric_name='census_nes_share_pct'`, value as fraction (0-1) to match calibration's threshold conventions. **This unit choice was reverted later in the session** — see Block 7.

**Apply:** 7,272 rows (2,432 SA2s × 3 census years 2011/2016/2021); 144 zero-pop skips; 30 DEC-59 clamps. audit_id 143. Backup `data\pre_layer4_4_step_a2_20260504_123214.db`.

### Block 5 — A2 wire (commit `bb21f66`)

Per project pattern, the calibration is consumed by `populate_service_catchment_cache.py`. Probed it: line 39 imports `calibrate_participation_rate`, line 437-450 contains the calibration loop, line 448 had `nes_share_pct=None,` (the dormant placeholder). Mirrors `flpf_map` pattern at lines 425-435.

**STD-10 patcher.** Two surgical edits:
1. Insert NES-map build block before the calibration loop (mirror flpf_map structure: SELECT MAX(year) → SELECT sa2_code, value → populate map).
2. Replace `nes_share_pct=None,` with `nes_share_pct=nes_map.get(sa2),`.

**Re-ran populator.** Cache repopulated (audit 144). Rule_text now shows NES on every SA2 with data:
- High NES (≥0.30): `−0.02 high NES share (0.31)` → Bayswater rate 0.50 → 0.48
- Mid: `NES share 0.24 (mid, no nudge)` → Bondi rate stays 0.54
- High: `−0.02 high NES share (0.38)` → Bentley rate 0.48 → 0.46

End-to-end calibration nudge live.

### Block 6 — Country-of-birth scoping conversation (no commit)

Operator asked whether nationality detail (origin of birth) is available and worth ingesting. Probed metadata: Census 2021 TSP has T08 (Country of Birth), T09 (Ancestry), T06 (Indigenous Status). Confirmed availability at SA2 level.

**Recommendation banked, not actioned this session:** option B with NES as a banded row + country-of-birth as narrative text summary at the top of a new "Demographic Mix" panel within the Catchment card. Phase 1 = NES row only (the work we then continued with). Phase 2 = T08 country-of-birth narrative (deferred to next session).

### Block 7 — A2 v3 unit fix (commit `49ce9f1`)

After C2-NES scoping (next block), realised the storage convention mismatch: A2 stored NES as fraction (0-1) to match calibration thresholds, but `value_format: "percent"` rendering would display fraction-stored values as e.g. "0.31%" instead of "31%". Project convention from `census_lfp_*_pct` family is percentage (0-100).

**Path A (chosen):** flip storage to percentage; wire divides by 100 on read before passing to calibration. Calibration thresholds (STD-34 locked) stay at fraction values (0.30, 0.05).

Two changes:
- `layer4_4_step_a2_apply.py` v2 → v3. Multiply by 100 in `derive_nes()`. Sanity-check thresholds adjusted for percentage. Action bumped to `census_nes_share_ingest_v3`. Re-ran with `--replace --apply` (audit 146).
- `populate_service_catchment_cache.py` wire fix patcher. Single-line edit: `nes_map[sa2] = float(v) / 100.0 if v is not None else None`. Re-ran populator (audit 147) — calibrated_rate values identical to pre-fix (storage*100/100 = same fraction into calibration), confirming the fix is unit-only.

**DEC-78 candidate flagged**: NES storage at SA2 = percentage; wire boundary handles fraction conversion. Not promoted yet — wait for A3/A4/A5 to confirm convention generalises.

### Block 8 — B2 layer3 add (commit `d02e26e`)

Probed `layer3_apply.py`. Found `METRICS = [...]` registry at L66+ following same shape across 11 entries (canonical, source_table, value_column, filter_clause, year_column, cohort_def). New entry mirrors `sa2_lfp_females` (Census-source with state_x_remoteness cohort).

**STD-10 patcher.** Bracket-depth tracking finds the closing `]` of `METRICS = [` and inserts the new entry before it. Char delta +287.

**Re-ran layer3_apply.py.** Banded `sa2_nes_share` (period=2021, rows=2417, skipped=15). audit 145. Backup `data\kintell.db.backup_pre_layer3_20260504_134117`.

### Block 9 — `layer3_apply.py` wholesale-rebuild bug (OI-35) + recovery

**Discovery.** After running `layer3_apply.py --apply`, hard-refreshed centre page expecting NES to appear (it didn't, see OI-36) but ALSO noticed the 4 catchment metric rows now showed em-dashes. Underlying values were intact in `service_catchment_cache` (probed); culprit was missing rows in `layer3_sa2_metric_banding`.

**Root cause.** `layer3_apply.py` does `DELETE FROM layer3_sa2_metric_banding` before INSERT. The 4 catchment metrics (sa2_supply_ratio, sa2_demand_supply, sa2_child_to_place, sa2_adjusted_demand) are banded by a separate script (`layer3_x_catchment_metric_banding.py`, action `layer3_catchment_banding_v1`, originally audit 142) that wasn't run after layer3_apply. Wholesale wipe → catchment metrics become collateral.

**Recovery.** Located `layer3_x_catchment_metric_banding.py` via filesystem probe (21,137 bytes). Ran `python layer3_x_catchment_metric_banding.py` (script defaults to apply mode unlike most others — `--help` was ignored). 9,035 rows inserted across the 4 metrics. audit 149. Backup `data\kintell.db.backup_pre_2_5_2_20260504_142735`.

**Workaround banked as OI-35.** Always run catchment-banding script after layer3_apply. Real fix (per-metric DELETE in layer3_apply) deferred — ~0.5 sess.

### Block 10 — C2-NES data-side registration (commit `3ddcf18`)

STD-10 patcher with brace-depth tracking. Three insertions in centre_page.py:
1. `LAYER3_METRIC_META` — new sa2_nes_share entry. card='catchment_position', value_format='percent', direction='high_is_positive' (neutral framing — credit signal lives in calibration nudge, not band chips), row_weight='lite' (3 Census points per DEC-75), band_copy non-stigmatising.
2. `LAYER3_METRIC_INTENT_COPY` — new intent line.
3. `LAYER3_METRIC_TRAJECTORY_SOURCE` — new entry mirroring sa2_lfp_females (table=abs_sa2_education_employment_annual, filter_clause for census_nes_share_pct).

Char delta +1,200 across 3 dicts. Marker count 3 (one per dict).

Restarted review_server.py, hard-refreshed centre page. **NES row did not appear.** Investigation found `centre_page.py` has 14 references to sa2_supply_ratio, suggesting catchment-card row assembly is hardcoded, not iterated from `LAYER3_METRIC_META.card='catchment_position'`. **Tracked as OI-36** — render-side held over to next session.

### Open items movement this session

**Opened + closed:** OI-34 (C3 absolute change).

**New:** OI-35 (layer3_apply wipe), OI-36 (centre.html hardcoded rows).

**Dropped:** A1 (CENTRE_PAGE_V1.5_ROADMAP scope) — dissolved by probe trail.

**Updated:** OI-12 (5 new backups added today, ~2.7 GB; cumulative ~8.5 GB; status critical).

### Standards / decisions

**No new STDs locked.**

**No new DECs locked.** **DEC-78 candidate**: NES storage convention (percentage at SA2; wire divides for calibration). Not promoted; wait for A3/A4/A5 convention check.

### What's banked for next session

V1 path: nothing.

V1.5 path next first piece: **OI-36 — C2-NES render-side**. Probe centre.html catchment-row assembly; surgical patch to add NES row; restart server; verify visible. Estimated ~0.3 sess.

Then evaluate appetite: **Phase 2 of NES work (T08 country-of-birth narrative panel)** vs **continue Phase A ingest (A3 parent-cohort, A4 schools, A5 subtype-correct denominators, A6 SALM-extension)**.

Optional housekeeping at any time: gitignore tightening (OI-13), recon probe sweep (move root probes into `recon/probes/`), OI-12 backup pruning (now critical), OI-35 real fix.

### Session shape note

Two big lessons:
1. **Search project knowledge before probing.** The A1 finding was already documented in 2026-04-28b status (the "6 dense annual points 2019-2024 (3 NULLs)" line). Re-discovering it cost ~30 min of probe scripts. Operator's nudge — "search the work we've already done" — is worth promoting to a working norm in STANDARDS.md next consolidation pass.
2. **Unit conventions matter early.** A2 v2 stored as fraction; would have shipped a broken-looking "0.31%" if C2-NES rendering had landed. Caught only because Path A scoping made me trace the value flow from storage through render. **Bank a check at scoping time: "what's the unit at each layer (storage, wire, calibration, render), and is each layer's expectation explicit?"**

Bundling discipline this session was reasonable — same-file edits collapsed into single patchers, DB writes never bundled (each got its own backup + audit_log row), cross-concern changes split. The 3-commit pattern in Phase 1 of doc-refresh (A2-v3-unit-fix, B2, C2-NES-data) was clean.

The session was longer than ideal. ~7 substantive commits + 4 doc commits is a heavy day. Next session should aim for 2-3 commits + clean doc refresh.

---

## 2026-05-10 — A10 + C8 Demographic Mix bundle (end-to-end)

**Session type:** Layer 4.4 ingest + Layer 4.2 register + render + design doc + DEC mint. DB-mutating (5 schema/data mutations across two ingest scripts, 9 audit_log rows). Probe-first per DEC-65.

**Context entering session.** OI-19 Layer 4.4 V1.5 ingests bundle had A10 + C8 elevated to next-session priority on 2026-05-05. Roadmap named source TSP tables as T07/T08/T19. DEC-78 was reserved (NES storage convention). Worktree-vs-main-repo problem flagged early (worktree on a stale branch missing CLAUDE.md, kintell.db, the TSP zip, and current code) and resolved by working from the main repo path via absolute paths.

**Probe finding banked early.** Inspection of column headers in `2021_TSP_SA2_for_AUS_short-header.zip` showed two of three roadmap table numbers were wrong:
- T06 (`C{yr}_Tot_Indig_P` etc.) is Indigenous status, NOT T07.
- T07 is fertility (`AP_*_NCB_*` = Age × Number of Children Born), not ATSI.
- T14 (`SH_FH_CF_*_One_PFam` etc.) is family composition, NOT T19.
- T19 is tenure type / landlord (`REA / ST_HA / Co_ho_pr` columns).
- T08 = country of birth confirmed correct.
- Bonus: T05 marital status + T07 fertility validated for Stream C future ingest pass.

Surfaced to Patrick mid-probe; corrected mapping locked into the design doc + DEC-80 §2 (TSP-table-number verification discipline as a permanent guardrail).

**Design doc.** `recon/a10_c8_design.md` — corrected mapping + 4 ratifiable decisions (D-A1 metrics + naming + cohort, D-A2 top-N display tables, D-A3 sub-panel placement, D-A4 verification SA2s). All four ratified mid-session.

**Work shipped this session.**

1. **`layer4_4_step_a10_apply.py`** — Reads T06A/B/C, T08A+B, T14A/B/C from the TSP zip. Three percentage metrics (ATSI, overseas-born, single-parent family) ingested into `abs_sa2_education_employment_annual` (long-format) per DEC-78. New table `abs_sa2_country_of_birth_top_n` created and populated with top-3 countries per SA2 for 2021. Audit_id 150 → 154. Backup: `data/pre_layer4_4_step_a10_20260509_234058.db` (541.4 MB).

2. **B-pass banding** — `patch_b2_layer3_add_demographic_mix.py` + `layer3_apply.py --apply` + OI-35 workaround (`layer3_x_catchment_metric_banding.py --apply`). 33,571 banding rows produced (3 new metrics × ~7,200 each = ~21,600 new banded rows); 9,035 catchment-banding rows restored. Audit_id 155 + 156.

3. **`layer4_4_step_a10b_languages_apply.py`** (mid-session follow-up after Patrick asked about language-at-home). New table `abs_sa2_language_at_home_top_n`, 7,060 rows from T10A+T10B (top-3 languages per SA2 for 2021, excluding English-only / language-not-stated / aggregate buckets). Audit_id 157 (schema create) + 158 (ingest). Backup: `data/pre_layer4_4_step_a10b_20260510_000826.db` (547.7 MB).

4. **`centre_page.py`** — 6 surgical edits via Edit tool (no patcher artefact). LAYER3_METRIC_META + LAYER3_METRIC_INTENT_COPY + LAYER3_METRIC_TRAJECTORY_SOURCE each gained 3 entries. POSITION_CARD_ORDER["catchment_position"] extended. New function `_build_community_profile(conn, sa2_code)` reads both top-N tables and returns a `community_profile` dict on the centre payload.

5. **`docs/centre.html` v3.28 → v3.29.** `renderCatchmentPositionCard()` rewritten with credit-signal block + dashed divider + "Demographic mix" sub-panel header + 4 Lite rows. `renderDemoRow` interleave inserts top-N context lines below NES (languages) and overseas-born (countries). Shared `_renderTopNContext(list, label, key)` helper. Sparkline glyph for Lite rows added then removed mid-session (Patrick rejected as "too busy"; saved as `feedback_lite_row_density.md` memory). CSS variable name fix: `--text-dim` (not `--muted`).

6. **`build_a10_c8_review_capture.py`** — offline static-HTML capture script. Inlines payloads + fetch-interceptor stub so Patrick reviews the rendered page without `review_server.py`. Two iterations to fix the response-shape (api() helper expects `{ok: true, centre: payload}` wrapper). Output `docs/a10_c8_review.html` gitignored as a one-shot artifact.

7. **DEC-78 promoted Reserved → Active** (Census 0–100 storage convention now load-bearing across NES + 3 demographic-mix metrics).

8. **DEC-80 minted** — Census top-N display tables convention + TSP-table-number verification discipline + Demographic Mix scope lock + sub-panel-not-new-card ratification.

9. **End-of-session doc refresh.** PROJECT_STATUS, CENTRE_PAGE_V1_5_ROADMAP, OPEN_ITEMS, this PHASE_LOG entry, monolith regen.

**Verification.** National 2021 totals: ATSI 3.20% (ABS published ~3.2%) ✓, overseas-born 27.71% (ABS ~27.6%) ✓, single-parent family 15.79% (ABS ~16%) ✓. Four verification SA2s — 211011251 (Bayswater Vic), 118011341 (Bondi Junction-Waverly NSW), 506031124 (Bentley-Wilson WA), 702041063 (Outback NT high-ATSI). High-ATSI test 702041063: ATSI 91.1%, OS-born 1.8%, single-parent 31.4%, top language at home Australian Indigenous languages 89.2% — validates UOL_Aus_In_La inclusion.

**Open questions resolved.**
- ATSI display framing → raw % with neutral "Aboriginal and Torres Strait Islander share" copy.
- T08 top-N storage → separate small table `abs_sa2_country_of_birth_top_n` per DEC-80 §1.
- C8 panel placement → sub-panel inside Catchment Position card per DEC-80 §4 + DEC-11.
- Sparkline glyph on Lite rows → tried and rejected mid-session as too busy. Banked as feedback memory.

**Items banked but not in scope this session.**
- Promoting demographic-mix metrics to Full row weight (would need denser source data than 3 Census points; pathway is the same as A6 LFP promotion via SALM monthly).
- Calibration nudges for ATSI / overseas-born / single-parent (waiting on banding-distribution review; tracked as a future scoping pass).
- Stream C T05 marital + T07 fertility ingest (validated and banked into A3 next-session bundle).

**Commits.** 3 commits per DEC-22 collapse: data layer (ingest + banding + languages top-N), render layer (centre_page.py + centre.html + design doc + review-capture script), end-of-session doc refresh (Tier-2 + DEC-78 promote + DEC-80 mint + monolith).
