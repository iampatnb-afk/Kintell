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
