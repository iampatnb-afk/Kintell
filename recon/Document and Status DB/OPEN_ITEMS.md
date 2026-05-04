# Open Items

*Last updated: 2026-05-03 (end of evening session). The on-disk version supersedes the project-knowledge monolith if they disagree.*

OI ID is global. Closed items kept for traceability. Severity tags: CRITICAL / Medium / Low / Cosmetic / Tracking.

---

## OPEN

### OI-33 — 25 SA2s with zero or sparse pop_0_4 coverage
*Origin: 2026-05-03 evening (split from OI-30 probe). Status: tracking.*

OI-30 probe (`probe_oi30_asgs_coverage.py`) found that 98.9% of catchment-anchored SA2s (2,269 / 2,294) sit in the same 6-11 year coverage bucket — the platform-wide 2019-onwards window driven by the current ABS ERP ingest scope. The remaining 25 SA2s are outliers: **16 with zero pop_0_4 coverage**, **9 with sparse 1-5 year coverage**.

These could be (a) genuinely missing from ABS ERP at SA2 level, (b) 2021-ASGS new codes not yet appearing in any ingest year, or (c) a combination. List of all 25 codes is in `recon/oi30_asgs_coverage_probe.md` (zero-coverage table + sparse top-30 table).

**Disposition.** Tracking only. None of these 25 SA2s are blocking — supply_ratio etc. silently render as None per P-2. Worth revisiting only if any of these 25 SA2s gain centre-anchor activity that warrants investigation, or as part of the OI-19 V1.5 ingest bundle if a more thorough ABS coverage audit becomes warranted.

### OI-31 — Click-to-detail on event overlay lines (Bug 6)
*Origin: 2026-05-03 PM. Status: open; ~1.0 session.*

Layer 4.2-A.3c added vertical dashed lines to the catchment trajectory charts at quarters when centres of the matching subtype opened or closed in the SA2 (color-coded green/red/grey). The data behind each line includes centre names + place changes (already in `p.centre_events`), but currently is not interactively exposed.

**Fix shape.** Click on a line → popup showing quarter, net change, list of new centre names + their places, list of removed centre names. Same data as the operator-page event detail. The `p.centre_events` array already carries everything needed; this is purely a renderer feature.

**Effort.** Substantial because event lines are drawn by Chart.js plugin (canvas pixels), not DOM elements — needs an overlay layer translating mouse coords to event matches. Likely ~1 session of careful renderer work.

### OI-28 — `populate_service_catchment_cache.py` cosmetic banner mismatch
*Origin: 2026-04-30. Status: open; cosmetic.*

Script's print banner says "v2" while the actual script is at v5. No functional impact (idempotency-guarded; won't re-run). 5-second fix at next touch.

### OI-26 — `demand_supply` industry threshold post-launch review
*Origin: 2026-04-30. Status: open; tracking.*

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

Additional workforce indicators beyond the 4 currently on the Workforce supply block. SEEK, advertised wages, etc. Bundled with V1.5 OI-19.

### OI-19 — Layer 4.4 V1.5 ingests bundle
*Origin: 2026-04-28. Status: open; ~2.0 sessions.*

NES + parent-cohort 25-44 + schools + SALM-extension + (optionally) SEEK/advertised wages. Bundled to amortise ABS workbook reading + concordance work. Largest V1.5 piece.

**OI-30 finding folds in here:** `abs_sa2_erp_annual` ingest extends backward beyond 2019 to widen pop_0_4 coverage from the current 6-year window. ABS publishes ERP back to at least 2001; just need to pull the historical years. Adds ~0.3 session to the bundle.

### OI-17 — `layer4_3_design.md` v1.0/v1.1 reconciliation
*Origin: 2026-04-28. Status: tracking.*

Two versions in recon/ that differ in places. Reconcile before referencing in future design work.

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
*Origin: 2026-04-28. Status: inventory landed (commit `bbac24f`); deletion deferred. Updated 2026-05-03 evening.*

Cumulative `data/` backups now 7.7 GB across 36 files. Inventory probe (`inventory_db_backups.py`) committed read-only audit_log + table+rowcount snapshot per backup to `recon/db_backup_inventory_2026-05-03.md`. **Deletion is now safely reversible** — even if all binary backups were removed, the inventory preserves the queryable record.

**Prune dry-run finding (2026-05-03 evening).** `prune_db_backups.py` ran in dry-run mode; reported **0 files to delete** under current keep policy (default-conservative: keeps all `pre_*` named milestone anchors + 3 most recent timestamped). All 36 backups in current set qualify under one of these rules: 34 are `pre_*` anchors; 2 are within most-recent-3 timestamped. To actually free space, the keep policy would need relaxing (e.g. cap pre-anchor retention to N most recent per milestone family, or drop large legacy `pre_step*`/`pre_layer3` anchors that are now historically inert). Operator decision on policy relaxation deferred — disk pressure not currently biting per prior assessment.

**When to actually delete.** Patrick decides disk pressure is real. Either re-run `prune_db_backups.py --apply` after relaxing keep policy, or delete specific large legacy anchors manually using the inventory as the queryable record.

### OI-11 — `jsa_vacancy_rate` in Workforce block
*Origin: 2026-04-28. Closed: 2026-04-29c by DEC-76.*

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
*Origin: 2026-04-28. Status: low; Thread B (V1.5 SALM-extension) may upgrade.*

DEC-75 reclassified LFP triplet to Lite per this exact rationale. SALM-extension would promote back to Full with monthly/quarterly cadence.

### OI-05 — `service_catchment_cache` populated
*Origin: 2026-04-28. Closed: 2026-04-30 (Layer 2.5 sub-pass 2.5.1).*

### OI-04 — 43 services unchanged by Step 1c, lat/lng (0,0)
*Origin: 2026-04-28. Status: medium; overlaps with OI-01/02.*

### OI-03 — 9 cross-state SA2 mismatches post-Step 1c
*Origin: 2026-04-28. Status: low; documented.*

### OI-02 — 2 null-island services (lat/lng = 0,0)
*Origin: 2026-04-28. Status: medium per DEC-63.*

### OI-01 — 18 services without lat/lng need geocoding
*Origin: 2026-04-28. Status: medium per DEC-63.*

---

## CLOSED THIS SESSION (2026-05-03 evening)

- **OI-32** — Catchment metric explainer text (Bug 4). Shipped in 3 rounds across 3 commits:
  - **Round 1+2** (`1a90bf7`, centre_page.py v16->v18 + centre.html v3.21->v3.23): new `LAYER3_METRIC_ABOUT_DATA` constant + `_renderAboutData` helper rendering "About this measure" panel inside `_renderFullRow`; reuses workforce-row about_data visual pattern (v3.17). DEC-22 collapsed: panel font 11.5px->12.5px; `sa2_demand_supply` about_data + INDUSTRY_BAND_THRESHOLDS reframed from "fill expectation/risk" to occupancy-ramp / trade-up terminology; generic "70% break-even at 85% occupancy" note removed.
  - **Polish r2** (`83738ac`, centre_page.py v18->v19): operator screenshot review caught remaining "fill"/"soft" in band_copy chips, INTENT_COPY italic lines, INDUSTRY_BAND label. Cleaned across `sa2_demand_supply` band_copy + sa2-prefixed INTENT_COPY for `sa2_demand_supply` / `sa2_supply_ratio` / `sa2_adjusted_demand`; INDUSTRY soft-band label "soft ramp-up" → "below break-even".
  - **v20 bundle** (centre_page.py v19->v20 + centre.html v3.23->v3.24): operator review of v19 INDUSTRY label semantics. Parallel-framed all 4 `sa2_demand_supply` band labels in supply-vs-demand language only ("supply heavy" / "supply leaning" / "approaching balance" / "demand leading") because break-even is a profitability conclusion the ratio alone cannot support. about_data first line tightened to match. Cohort distribution histogram gains centred italic explainer text + cohort-note alignment switched to centre. New `_renderMiniDecileStrip` helper used inline for SEIFA decile fact (chosen over colour-coding because SES has no valence in LDC credit). DEC-77 minted to formalise the industry-absolute threshold framework.

- **OI-30** — Bayswater (and assumed other 2021-ASGS) SA2s have incomplete pre-2019 ABS coverage. Closed by probe (`probe_oi30_asgs_coverage.py`, read-only). Probe **refuted** the original 2021-ASGS-concordance hypothesis: Bondi Junction-Waverly (118011341 — established 2016-ASGS area) has the same 6-year coverage (2019-2024) as Bayswater (211011251). 98.9% of catchment-anchored SA2s sit in the same 6-11 year bucket; the issue is platform-wide, not code-specific. Real fix: extend `abs_sa2_erp_annual` ingest backward — folds into OI-19 V1.5 ingest bundle. 25 outlier SA2s (16 zero + 9 sparse coverage) split out as **OI-33**.
