# Open Items

*Last updated: 2026-05-03 (end of afternoon session). The on-disk version supersedes the project-knowledge monolith if they disagree.*

OI ID is global. Closed items kept for traceability. Severity tags: CRITICAL / Medium / Low / Cosmetic / Tracking.

---

## OPEN

### OI-32 — Catchment metric explainer text (Bug 4)
*Origin: 2026-05-03 PM. Status: open; ~10-30 min depending on copy.*

Operator visual review of Layer 4.2-A.3c surfaced that the existing helper text under each catchment metric is too small and insufficiently explanatory, particularly for `sa2_adjusted_demand`. The current `intent_copy` (one-liner) and `band_copy` (3 short phrases) don't tell a credit reader what the metric actually measures.

**Fix shape.** Add a "what is this metric?" longer explainer per metric. Likely a new `LAYER3_METRIC_META` field (e.g. `explainer_text`) that the renderer surfaces below the title or near the source line. Font size on existing helper text may also need a bump.

**Status.** Patrick confirmed he'll provide the copy. Renderer scaffold deferred until copy is in hand to avoid building a placeholder we'd then refactor.

### OI-31 — Click-to-detail on event overlay lines (Bug 6)
*Origin: 2026-05-03 PM. Status: open; ~1.0 session.*

Layer 4.2-A.3c added vertical dashed lines to the catchment trajectory charts at quarters when centres of the matching subtype opened or closed in the SA2 (color-coded green/red/grey). The data behind each line includes centre names + place changes (already in `p.centre_events`), but currently is not interactively exposed.

**Fix shape.** Click on a line → popup showing quarter, net change, list of new centre names + their places, list of removed centre names. Same data as the operator-page event detail. The `p.centre_events` array already carries everything needed; this is purely a renderer feature.

**Effort.** Substantial because event lines are drawn by Chart.js plugin (canvas pixels), not DOM elements — needs an overlay layer translating mouse coords to event matches. Likely ~1 session of careful renderer work.

### OI-30 — Bayswater (and likely other 2021-ASGS) SA2s have incomplete pre-2019 ABS coverage
*Origin: 2026-05-03 PM. Status: open; ~0.3 session probe + ~0.5 session build script change.*

Probe of Bayswater (SA2 211011251) during Layer 4.2-A.3c verification revealed that `pop_0_4` data only exists from Q3 2019 onwards. Pre-2019 quarters return None from the interpolation function because the SA2 code isn't in the ABS Population and People Database for years 2011/2016/2018. NQAITS data IS present for all 50 quarters, but supply_ratio (which requires both places AND pop_0_4) is None for the 27 pre-2019 quarters.

**Likely cause.** Bayswater 211011251 is a 2021-ASGS code. Pre-2019 ABS data uses 2016-ASGS codes — the same suburb has a different SA2 code there. Need an ASGS concordance step in the build to map newer codes to older code data.

**Scope.** Unknown how many SA2s are affected. Bayswater is one example; likely there are many. Worth a probe before designing a fix.

**V1 disposition.** Accepted as known limitation; trajectory still meaningful at 23 quarters for affected SA2s. Real fix is V1.5 ingest scope.

### OI-28 — `populate_service_catchment_cache.py` cosmetic banner mismatch
*Origin: 2026-04-30. Status: open; cosmetic.*

Script's print banner says "v2" while the actual script is at v5. No functional impact (idempotency-guarded; won't re-run). 5-second fix at next touch.

### OI-27 — Subtype tagging on `sa2_history.json` for new-centre overlay
*Origin: 2026-04-30. Closed: 2026-05-03 PM (by Layer 4.2-A.3c Part 2).*

**Resolution.** `build_sa2_history.py` v2 ships per-subtype `centre_events` arrays under `by_subtype.<LDC|OSHC|PSK|FDC>.centre_events`. Renderer (centre.html v3.19+) consumes them via the `_kintellEventAnnotation` plugin. Subtype-matched lines render correctly on both LDC (Sparrow Bayswater) and OSHC (Kool HQ Waverley) verification centres.

### OI-26 — `demand_supply` industry threshold post-launch review
*Origin: 2026-04-30. Status: open; tracking.*

Mathematically grounded but may register false positives in saturated catchments. Review post-launch.

### OI-25 — `sa2_median_household_income` trajectory shows single point
*Origin: 2026-05-03 AM. Closed: 2026-05-03 AM (premise dissolved by probe).*

Probe (`probe_oi25_income_trajectory.py`, read-only) confirmed backend + renderer behaving correctly. The "single point" symptom was Trend Window clipping on Census 5-year-cadence data — when global Trend Window is set to "All" the chart correctly shows 3 dots (2011, 2016, 2021). No bug. Real residual issue (3-point Census trajectory rendered as Full weight is visually misleading) tracked as OI-29 (now also closed).

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

7 backup files currently untracked. 30-second gitignore tightening fix at next housekeeping pass.

### OI-12 — DB backup pruning
*Origin: 2026-04-28. Status: inventory landed (commit `bbac24f`); deletion deferred.*

Cumulative `data/` backups now 7.7 GB across 36 files. Inventory probe (`inventory_db_backups.py`) committed read-only audit_log + table+rowcount snapshot per backup to `recon/db_backup_inventory_2026-05-03.md`. **Deletion is now safely reversible** — even if all binary backups were removed, the inventory preserves the queryable record needed to answer "what mutations had run as of pre_step5b" type questions.

**Why deletion was deferred.** Disk pressure not currently biting. Backups are gitignored, so they don't slow git operations directly. The OPEN_ITEMS originally framed this as "approaching git-timeout threshold" — that turned out to be overstated.

**When to actually delete.** When Patrick decides disk pressure is real. The `prune_db_backups.py` script is in place (default-conservative: keep all `pre_*` named anchors + 3 most recent). Re-run with `--apply` whenever ready.

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

## CLOSED THIS SESSION (2026-05-03)

- **OI-29** — `sa2_median_household_income` reclassified to Lite weight per DEC-75 (centre_page.py v14, commit `6a7fe8a`)
- **OI-27** — sa2_history.json subtype tagging shipped via Layer 4.2-A.3c Part 2 (commit `36c2f78`); renderer wired in Part 3 (commit `bcdf84c`)
- **OI-25** — Census income trajectory single-point bug. Premise dissolved by probe (commit `6d30d33`)
