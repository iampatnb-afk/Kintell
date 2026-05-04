# Open Items

*Last updated: 2026-05-04 (end of full-day session). The on-disk version supersedes the project-knowledge monolith if they disagree.*

OI ID is global. Closed items kept for traceability. Severity tags: CRITICAL / Medium / Low / Cosmetic / Tracking.

---

## OPEN

### OI-36 — `centre.html` / `centre_page.py` hardcode catchment-position rows; new metrics don't auto-render
*Origin: 2026-05-04 (afternoon). Status: open; ~0.3 session. **Recommended first piece next session.** Blocks visible-on-page for `sa2_nes_share`.*

C2-NES (commit `3ddcf18`) registered `sa2_nes_share` in `centre_page.py`'s three Layer 3 registries: `LAYER3_METRIC_META` (card='catchment_position'), `LAYER3_METRIC_INTENT_COPY`, `LAYER3_METRIC_TRAJECTORY_SOURCE`. Server restart and Ctrl+F5 didn't surface a new row in the Catchment Position card.

Inspection found `centre_page.py` has 14 references to `sa2_supply_ratio` (and similar counts for the other catchment metrics), suggesting the renderer iterates a hardcoded list of catchment metrics in the row template — not a generic "all `card='catchment_position'` entries" loop. Adding a new `card='catchment_position'` entry to `LAYER3_METRIC_META` is necessary but not sufficient; `centre.html` (or `centre_page.py`'s payload assembly for the catchment card) needs an explicit entry for the new metric.

**Fix shape.** Probe `centre.html` and `centre_page.py`'s catchment-card assembly path to find where the 5 existing catchment metrics are listed; add `sa2_nes_share` alongside; verify rendering. Restart `review_server.py` per Python module cache (STD-13 + STD-14).

**Two approaches** (Phase 1 probe data picks one):
- **Surgical**: add NES row alongside existing 5 metrics in centre.html / centre_page.py. Lowest risk.
- **Refactor**: convert the catchment-card assembly to iterate `LAYER3_METRIC_META.card='catchment_position'` (more invasive, fixes the hardcoding root cause permanently). Saves ~0.6-0.9 sess across upcoming A3/A4/B1/B5 follow-on render work.

**Effort.** ~0.3 sess for surgical; ~0.6 sess for refactor (probe-dependent).

**Verification SA2s already known:**

| SA2 | Name | NES | Expected band | Expected nudge |
|---|---|---|---|---|
| 211011251 | Bayswater Vic | 31.07% | high | yes (−0.02) |
| 118011341 | Bondi Junction-Waverly NSW | 23.58% | mid | no |
| 506031124 | Bentley-Wilson WA | 37.55% | high | yes (−0.02) |

### OI-35 — `layer3_apply.py` wholesale-rebuilds `layer3_sa2_metric_banding`, wiping catchment metrics
*Origin: 2026-05-04 (afternoon). Status: open; workaround in place; real fix ~0.5 session.*

Discovered when running `layer3_apply.py --apply` after the B2 patcher (audit 145, 03:41). The script does a wholesale `DELETE FROM layer3_sa2_metric_banding` followed by INSERT-only-its-own-metrics. The 4 catchment metrics (`sa2_supply_ratio`, `sa2_demand_supply`, `sa2_child_to_place`, `sa2_adjusted_demand`) are banded by a SEPARATE script (`layer3_x_catchment_metric_banding.py`, action `layer3_catchment_banding_v1`, originally audit 142 from 2026-04-30) and were collateral damage in the wipe. Result: 9,035 catchment-banding rows missing; centre page rendered the 4 catchment rows as em-dashes.

**Recovery this session.** Re-ran `layer3_x_catchment_metric_banding.py` (audit 149); 9,035 rows restored; page back to working state. Backup of pre-recovery DB at `data\kintell.db.backup_pre_2_5_2_20260504_142735`.

**Workaround going forward.** Always run `layer3_x_catchment_metric_banding.py --apply` immediately after `layer3_apply.py --apply`. Documented in `recon/layer3_apply.md` and in CENTRE_PAGE_V1.5_ROADMAP §"Sequencing rules". Better future state: a one-line `refresh_layer3.ps1` (or `.sh`) that runs both.

**Real fix.** Refactor `layer3_apply.py` to do per-metric DELETE rather than table-wide DELETE. Metrics outside its `METRICS = [...]` list should be untouched. Estimated ~0.5 session including probe, surgical patcher, dual-run smoke test. Mid-priority — workaround is reliable and documented.

### OI-33 — 25 SA2s with zero or sparse pop_0_4 coverage
*Origin: 2026-05-03 evening (split from OI-30 probe). Status: tracking.*

OI-30 probe (`probe_oi30_asgs_coverage.py`) found that 98.9% of catchment-anchored SA2s (2,269 / 2,294) sit in the same 6-11 year coverage bucket — the platform-wide 2019-onwards window driven by the current ABS ERP ingest scope. The remaining 25 SA2s are outliers: **16 with zero pop_0_4 coverage**, **9 with sparse 1-5 year coverage**.

These could be (a) genuinely missing from ABS ERP at SA2 level, (b) 2021-ASGS new codes not yet appearing in any ingest year, or (c) a combination. List of all 25 codes is in `recon/oi30_asgs_coverage_probe.md`.

**Disposition.** Tracking only. None of these 25 SA2s are blocking — supply_ratio etc. silently render as None per P-2. Worth revisiting only if any of these 25 SA2s gain centre-anchor activity that warrants investigation, or as part of the OI-19 V1.5 ingest bundle if a more thorough ABS coverage audit becomes warranted.

### OI-31 — Click-to-detail on event overlay lines (Bug 6)
*Origin: 2026-05-03 PM. Status: open; ~1.0 session.*

Layer 4.2-A.3c added vertical dashed lines to the catchment trajectory charts at quarters when centres of the matching subtype opened or closed in the SA2 (color-coded green/red/grey). The data behind each line includes centre names + place changes (already in `p.centre_events`), but currently is not interactively exposed.

**Fix shape.** Click on a line → popup showing quarter, net change, list of new centre names + their places, list of removed centre names. Same data as the operator-page event detail. The `p.centre_events` array already carries everything needed; this is purely a renderer feature.

**Effort.** Substantial because event lines are drawn by Chart.js plugin (canvas pixels), not DOM elements — needs an overlay layer translating mouse coords to event matches. Likely ~1 session of careful renderer work. Explicitly deferred from V1.5 ship slice.

### OI-28 — `populate_service_catchment_cache.py` cosmetic banner mismatch
*Origin: 2026-04-30. Status: open; cosmetic.*

Script's print banner says "v2" while the actual script is at v5. No functional impact (idempotency-guarded; won't re-run). 5-second fix at next touch.

### OI-26 — `demand_supply` industry threshold post-launch review
*Origin: 2026-04-30. Status: open; tracking; under DEC-77.*

Mathematically grounded but may register false positives in saturated catchments. Review post-launch.

### OI-24 — Sub-pass dependency-ordering pass — DEC-65 amended
*Origin: 2026-04-29. Status: open; tracking.*

DEC-65 (probe-before-code) extended in spirit to "design before implement when ordering matters." Pure tracking; no specific deliverable.

### OI-22 — Future centre-page tab: ownership and corporate detail
*Origin: 2026-04-28. Status: tracking; deferred to V1.5+.*

Parent-group navigation, ownership chain detail. Out of V1 scope.

### OI-21 — Future centre-page tab: quality elements
*Origin: 2026-04-28. Status: tracking; deferred to V1.5+.*

Deeper NQS / regulatory detail per centre. Out of V1 scope.

### OI-20 — Workforce supply context enrichments
*Origin: 2026-04-28. Status: low priority; tracking.*

Additional workforce indicators beyond the 4 currently on the Workforce supply block. SEEK, advertised wages, etc. Bundled with V1.5 OI-19 / A6 / A7.

### OI-19 — Layer 4.4 V1.5 ingests bundle
*Origin: 2026-04-28. Status: open; partially shipped.*

NES + parent-cohort 25-44 + schools + SALM-extension + (optionally) SEEK/advertised wages. Bundled to amortise ABS workbook reading + concordance work.

**A2 (NES) closed 2026-05-04** — see CENTRE_PAGE_V1.5_ROADMAP. Remaining: A3 (parent-cohort 25-44), A4 (schools), A5 (subtype-correct denominators), A6 (SALM-extension). ~1.4 sess.

**OI-30 finding folds in here:** `abs_sa2_erp_annual` ingest extends backward beyond 2019 to widen pop_0_4 coverage from the current 6-year window. Adds ~0.3 session to the bundle.

### OI-17 — `layer4_3_design.md` v1.0/v1.1 reconciliation
*Origin: 2026-04-28. Status: tracking.*

Two versions in `recon/` that differ in places. Reconcile before referencing in future design work.

### OI-16 — DEC-29 verbatim text not recovered
*Origin: 2026-04-28. Status: tracking.*

DECISIONS.md has DEC-29 entry but original text unrecovered from chat history. Re-derive if revisited.

### OI-15 — Backfill audit for ARIA+ format mismatch
*Origin: 2026-04-28. Status: low priority.*

Some old records use "ARIA+" with different bracketing. Codebase scan candidate.

### OI-14 — Backfill audit for DD/MM/YYYY date parsing fix
*Origin: 2026-04-28. Status: low priority; multiple recent occurrences.*

Recommend codebase scan. Several places parse approval_date inconsistently.

### OI-13 — Frontend file backups accumulate in `docs/`
*Origin: 2026-04-28. Status: low; gitignore pattern uses single `?` so `v3_3` doesn't match.*

7+ backup files currently untracked. 30-second gitignore tightening fix at next housekeeping pass.

### OI-12 — DB backup pruning
*Origin: 2026-04-28. Status: **CRITICAL**. Inventory landed (commit `bbac24f`); deletion deferred. Updated 2026-05-04: cumulative backup size now ~8.5 GB across 41 files, +2.7 GB this session.*

5 new backups created in 2026-05-04 session per STD-30 pre-mutation discipline:
- `pre_layer4_4_step_a2_20260504_123214.db` (~540 MB)
- `pre_layer4_4_step_a2_v3_20260504_140128.db` (~540 MB)
- `kintell.db.backup_pre_2_5_1_20260504_140136` (~567 MB)
- `kintell.db.backup_pre_layer3_20260504_134117` (~541 MB)
- `kintell.db.backup_pre_2_5_2_20260504_142735` (~567 MB)

**Cumulative ~8.5 GB across 41 files.** Disk pressure now real. Keep policy needs relaxation.

**Prune dry-run finding (2026-05-03 evening, still relevant).** `prune_db_backups.py` ran in dry-run mode; reported 0 files to delete under current keep policy (default-conservative: keeps all `pre_*` named milestone anchors + 3 most recent timestamped). To actually free space, the keep policy needs relaxing (e.g. cap pre-anchor retention to N most recent per milestone family, or drop large legacy `pre_step*`/`pre_layer3` anchors that are now historically inert).

**When to actually delete.** Patrick decides keep-policy. Either re-run `prune_db_backups.py --apply` after relaxing keep policy, or delete specific large legacy anchors manually using the inventory as the queryable record.

### OI-10 — `provider_management_type` enum normalisation
*Origin: 2026-04-28. Status: low.*

Some values are inconsistently capitalised. Cleanup candidate.

### OI-09 — `sa2_under5_growth_5y` descoped from Layer 3
*Origin: 2026-04-28. Status: low; deferred.*

Currently rendered as "deferred" placeholder on the centre page. Revisit in V1.5+ if growth metric is requested.

### OI-08 — 19 synthetic SA2s with NULL ra_band
*Origin: 2026-04-28. Status: acceptable.*

Documented oddity; no fix needed.

### OI-07 — `participation_rate` not measured at SA2
*Origin: 2026-04-28. STD-34 LIVE.*

Tracked. STD-34 calibration discipline is the workaround.

### OI-06 — LFP source Census-only (3 pts)
*Origin: 2026-04-28. Status: low; Thread B (V1.5 SALM-extension / A6) may upgrade.*

DEC-75 reclassified LFP triplet to Lite per this exact rationale. SALM-extension would promote back to Full with monthly/quarterly cadence.

### OI-04 — 43 services unchanged by Step 1c, lat/lng (0,0)
*Origin: 2026-04-28. Status: medium; overlaps with OI-01/02.*

### OI-03 — 9 cross-state SA2 mismatches post-Step 1c
*Origin: 2026-04-28. Status: low; documented.*

### OI-02 — 2 null-island services (lat/lng = 0,0)
*Origin: 2026-04-28. Status: medium per DEC-63.*

### OI-01 — 18 services without lat/lng need geocoding
*Origin: 2026-04-28. Status: medium per DEC-63.*

---

## CLOSED THIS SESSION (2026-05-04)

- **OI-34** — Absolute change rendered alongside trend % on catchment trajectory charts (commit `f47a0ba`, centre.html v3.24 → v3.25). Opened+closed same morning.

## DROPPED THIS SESSION (2026-05-04)

- **A1** (CENTRE_PAGE_V1.5_ROADMAP scope, not an OI) — ABS ERP backward extension. Dissolved by probe trail; ABS source publishes `'-'` for pre-2019 SA2 under-5. Three forward paths exist if pre-2019 SA2 under-5 figures become required: Census 2011/2016 SA2 age tables as separate ingest; demographic derivation from births × cohort-survival; ABS TableBuilder pull. None V1.5-critical.

## CLOSED PRIOR SESSIONS (kept for traceability)

- **OI-32** — Catchment metric explainer text. Closed 2026-05-03 evening across 3 polish rounds.
- **OI-30** — Pre-2019 pop_0_4 coverage gap. Closed 2026-05-03 evening by probe; real fix folds into OI-19.
- **OI-29** — `sa2_median_household_income` Lite reclassification. Closed 2026-05-03 PM.
- **OI-25** — Closed 2026-05-03 (premise dissolved by probe).
- **OI-23** — Closed 2026-04-30 (caption fix in workforce window selector).
- **OI-18** — Layer 4.3 design closure. Closed 2026-04-29c.
- **OI-11** — `jsa_vacancy_rate` in Workforce block. Closed 2026-04-29c by DEC-76.
- **OI-05** — `service_catchment_cache` populated. Closed 2026-04-30 (Layer 2.5 sub-pass 2.5.1).
