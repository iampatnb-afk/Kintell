# Open Items

*Last updated: 2026-04-30. The on-disk version supersedes the project-knowledge monolith if they disagree.*

This file tracks active open items (work not yet done) and a closed list (resolved items, kept for traceability). New items get the next OI-NN number; closed items move to the Closed section with a one-line resolution note.

---

## Active — data quality

### OI-01 — 18 services without lat/lng need geocoding fix
*Origin: 2026-04-22 audit. Status: open.*

Geocoding pass needed. Bundled with the next data-quality round.

### OI-02 — 2 services at lat=0, lng=0 (null-island)
*Origin: 2026-04-22 audit. Status: open.*

Bundled with OI-01.

### OI-03 — 9 cross-state SA2 mismatches remain post-Step-1c
*Origin: 2026-04-22 audit. Status: open.*

Geocoding pass placed services in the wrong state. Flagged for manual review.

### OI-04 — 43 services unchanged by Step 1c due to lat/lng (0,0)
*Origin: 2026-04-22 audit. Status: open.*

Bundled with OI-02.

### OI-06 — LFP source is Census-only (3 points)
*Origin: 2026-04-22. Status: open until V1.5 SALM-extension lands per OI-19.*

`sa2_lfp_persons` will be promoted LITE → FULL when SALM extension ships. `sa2_lfp_females` and `sa2_lfp_males` stay LITE permanently (SALM is persons-only at SA2; sex split is Census 3-point).

### OI-07 — `participation_rate` not measured at SA2
*Origin: 2026-04-22. Status: addressed by STD-34 calibration function (sub-pass 4.3.4); reviewed at every Layer 4 ship.*

`catchment_calibration.py` v1 implements the calibration discipline. Per-SA2 calibrated_rate + rule_text now live in `service_catchment_cache` (sub-pass 2.5.1).

### OI-08 — 19 synthetic SA2s in `sa2_cohort` have NULL ra_band
*Origin: 2026-04-22. Status: open.*

Synthetic SA2s for offshore / migratory / no-usual-address need an ra_band assignment policy.

---

## Active — product surface

### OI-09 — `sa2_under5_growth_5y` derived metric not in initial Layer 3 set
*Origin: 2026-04-23. Status: open.*

Placeholder slot in the Population card; renders as deferred today.

### OI-10 — `provider_management_type` enum normalisation pending
*Origin: 2026-04-24. Status: open.*

`services.management_type` has free-text variations needing canonical mapping. Bundled with the next provider-side cleanup round.

### OI-11 — `jsa_vacancy_rate` admitted to centre page in Context-only weight
*Origin: 2026-04-29. Status: addressed by DEC-76 + sub-pass 4.3.9.*

Resolved by relocation: jsa_vacancy_rate moved from Labour Market card to the Workforce supply context block per DEC-76. Rendered via dedicated workforce row pattern, not the Position-row template.

---

## Active — operational

### OI-12 — Backup pruning needed in `data/`
*Origin: 2026-04-22. Status: STATUS-CRITICAL as of 2026-04-30.*

`data/` directory contains accumulated `.backup_pre_*` files from STD-08 backups. **6 new backups added today** (2026-04-30); total directory size now >5.8 GB. Pruning script needed — keep last 2 per layer, archive or delete older. Run interactively next session.

Today's backups:
- `kintell.db.backup_pre_4_3_5_20260430_101700`
- `kintell.db.backup_pre_4_3_5b_20260430_110004`
- `kintell.db.backup_pre_2_5_1_20260430_114306`
- `kintell.db.backup_pre_2_5_1_20260430_115717`
- `kintell.db.backup_pre_2_5_2_20260430_144707`
- (One earlier backup not in this run; verify on disk.)

### OI-13 — Frontend file backups accumulate in `docs/`
*Origin: 2026-04-28. Status: gitignored; non-blocking.*

`docs/centre.v3_*_backup_*.html` files from in-place patcher runs. Gitignored; not pushed. Operator can delete locally when comfortable.

### OI-14 — Backfill audit for DD/MM/YYYY date parsing fix
*Origin: 2026-04-25. Status: ESCALATED 2026-04-30.*

Third occurrence of this date-format mismatch this session (sub-pass 2.5.1 v5 fix on `services.approval_granted_date`). SQLite `julianday()` requires ISO 8601; `services.*` date columns are stored as DD/MM/YYYY strings. Recommend a one-pass codebase scan for any other `julianday()` calls on `services.*` date columns and fix-or-document them all in a single round.

### OI-15 — Backfill audit for ARIA+ format mismatch
*Origin: 2026-04-26. Status: open.*

Mixed-format ARIA codes in upstream sources need consistent normalisation.

### OI-28 — `populate_service_catchment_cache.py` cosmetic banner mismatch
*Origin: 2026-04-30. Status: open; non-blocking.*

Banner says "v2" in the `print()` output even though the file has been patched to v5. The patcher only updated the docstring banner, not the runtime print statement. No functional impact. Fix opportunistically.

---

## Active — restructuring residuals

### OI-16 — DEC-29 verbatim text not recovered
*Origin: 2026-04-28 restructure. Status: open.*

DEC-29 was referenced in pre-restructure docs but its verbatim text wasn't captured during consolidation. Need archaeology pass on git history if the decision text becomes load-bearing.

### OI-17 — `recon/layer4_3_design.md` v1.0 source verification
*Origin: 2026-04-28 restructure. Status: open; v1.1 superseded v1.0.*

v1.0 was retired during the 4.3 closure pass. v1.1 also retired post-2026-04-29d consolidation. Both archived in git history.

---

## Active — Layer 4.3 / 4.4 forward work (added 2026-04-29)

### OI-19 — Layer 4.4 ingests deferred (NES, parent-cohort 25–44, schools)
*Origin: 2026-04-29. Status: V1.5 bundle.*

Three ingests deferred to V1.5. NES required to close the calibration function's documented `nes_share_pct` gap (currently dormant). Parent-cohort 25-44 improves calibrated_rate accuracy for the relevant age band. Schools at SA2 feeds kinder-eligibility and OSHC sub-types.

Bundled with SALM-extension per 2026-04-29d.

### OI-20 — Workforce supply context enrichments
*Origin: 2026-04-29. Status: NCVER bullet closed (kept at Industry view per DEC-36); SEEK and advertised-wage residual.*

ECEC Award rates row (Fair Work ingest) still pending — only deferred row in the Workforce supply context block. Other 3 rows (4211, 2411, 3-Day Guarantee) are live. Today's 4.2-A.3a-fix iter 4 added "About this measure" explainer panels on the IVI rows; ECEC Award row will get the same when it goes live.

### OI-21 — Future centre-page tab: quality elements
*Origin: 2026-04-29. Status: V2.*

Deeper NQS / regulatory detail per centre. Out of V1 scope.

### OI-22 — Future centre-page tab: ownership and corporate detail
*Origin: 2026-04-29. Status: V2.*

Parent group navigation. Out of V1 scope.

### OI-24 — Sub-pass dependency-ordering pass missing from design-closure protocol
*Origin: 2026-04-29. Status: open; protocol amendment proposed but not adopted.*

DEC-65 amended to include sequencing-pass check. Worth a follow-up STD if the issue recurs.

---

## Active — added 2026-04-30

### OI-25 — `sa2_median_household_income` trajectory shows single point
*Origin: 2026-04-30. Status: open; ~0.3 session.*

The chart for Median household income on the centre page shows only the latest Census year (2021). The data has 3 Census points (2011, 2016, 2021) — confirmed via diagnostic query against `abs_sa2_socioeconomic_annual` during 2026-04-30 session. The trajectory series reaching the renderer apparently contains only the latest period.

Likely root cause: backend bug in `_layer3_position` trajectory builder; either fetches latest period only when it should fetch all years for the metric, OR filters too aggressively (e.g., requires non-null in every year of a continuous range).

Affects all Census-source income metrics: `sa2_median_employee_income`, `sa2_median_household_income`, `sa2_median_total_income`. Other Census metrics likely affected too (e.g., `sa2_lfp_persons`, `sa2_lfp_females`, `sa2_lfp_males` — although those are deliberately Lite weight so the bug is hidden).

Investigation step 1: query `_layer3_position()` payload directly for service 103, inspect the `trajectory` array on a Census-source metric, compare to the raw query output of `abs_sa2_socioeconomic_annual` for that SA2 + metric.

### OI-26 — `demand_supply` industry thresholds need post-launch calibration review
*Origin: 2026-04-30. Status: open; review window 4-6 weeks of operator use.*

The industry threshold framework (sub-pass 4.2-A.3b) defines `demand_supply` bands as soft <0.40 / near_be <0.55 / viable <0.85 / strong >=0.85, mathematically derived from CHC's 70% break-even and 85% target occupancy. For service 103 (Bondi, demand_supply=0.14), the threshold renders "soft fill risk" — but the SA2 has 22 active centres operating successfully, suggesting the calibrated demand model underestimates real demand in saturated catchments (multi-day-per-week + waiting lists not captured by `attendance_factor=0.6`).

Acceptable directionally for V1 launch. After 4-6 weeks of operator use across diverse SA2s, review:
- Do "soft fill risk" classifications correlate with actual fill problems?
- Is there a systematic bias against saturated catchments?
- Should `attendance_factor` increase or should demand_supply thresholds be wider?

Lock as DEC-77 once thresholds are post-launch validated.

### OI-27 — 4.2-A.3c new-centre overlay requires `sa2_history.json` rebuild
*Origin: 2026-04-30. Status: gating sub-pass 4.2-A.3c.*

The new-centre overlay on `sa2_supply_ratio` trajectory (sub-pass 4.2-A.3c) needs subtype-tagged centre_events to support like-for-like filtering (LDC-vs-LDC competition, not LDC-vs-OSHC).

Current `sa2_history.json` (1,193 SA2s; quarterly Q3 2013 → present) has `centre_events` arrays with `new_centres`, `removed_centres`, `new_names[]` but NO subtype field. Per D5=b lock from 2026-04-30: rebuild `build_sa2_history.py` to add subtype tagging on each event plus per-subtype rollups (`new_centres_ldc / oshc / preschool`).

Bundled with sub-pass 4.2-A.3c implementation.

---

## Closed

### OI-05 — `service_catchment_cache` is empty (0 rows)
*Origin: 2026-04-22 audit. CLOSED 2026-04-30.*

Resolution: sub-pass 2.5.1 populator shipped 2026-04-30 (commits `a65ee57` + `4d49516`). 18,203 rows now populated covering all active SA2-assigned services. Subsequent sub-pass 2.5.2 banded the 4 new catchment metrics into `layer3_sa2_metric_banding`.

### OI-18 — Layer 4.3 design decisions G1–G4 + §9.4 awaiting closure
*Origin: 2026-04-25. Closed: 2026-04-29.*

Resolution: design closure session shipped DEC-74, DEC-75, DEC-76, STD-34 lock. Closure document `recon/layer4_3_design.md` v1.1 produced as artefact, then retired post-consolidation.

### OI-23 — Global trend-window bar disappears when Population card has no live data
*Origin: 2026-04-29. Closed: 2026-04-30.*

Resolution: closed by 4.2-A.3a-fix iter 3 (centre.html v3.16). The global bar caption was corrected ("applies to Population, Labour, Catchment trajectories") and its visibility logic was unchanged — it now correctly stays absent when no full-trajectory data exists, which is the intended behaviour. Original 2026-04-29 OI was a misread; the bar was correctly suppressed by `_pageHasFullTrajectory` per design.

---

## Closed (pre-restructure)

These items were closed in 2026-04-22 → 2026-04-27 sessions before the doc restructure. Kept for traceability only.

- (none currently visible in pre-restructure ledger; items were rolled into resolutions)

---

## How to use this file

- New open items go to the appropriate Active section with the next OI-NN number.
- When closed, an item moves to Closed with a one-line resolution note and a date.
- Every item has Origin date and Status. Status changes are dated.
- This file is regenerated, not hand-edited (per STD-02). End-of-session regen is triggered by any session that materially changes the open-item set.
