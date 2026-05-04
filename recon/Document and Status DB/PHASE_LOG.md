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
