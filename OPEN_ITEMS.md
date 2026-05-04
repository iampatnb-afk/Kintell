# Open Items

*Last updated: 2026-05-05 (OI-36 closed; Demographic Mix bundle elevated). The on-disk version supersedes the project-knowledge monolith if they disagree.*

OI ID is global. Closed items kept for traceability. Severity tags: CRITICAL / Medium / Low / Cosmetic / Tracking.

---

## OPEN

### OI-19 — Layer 4.4 V1.5 ingests bundle (NEXT-SESSION PRIORITY) ⭐
*Origin: 2026-04-28. Status: open; partially shipped. **Demographic Mix bundle (A10) elevated to next-session priority 2026-05-05.***

Original scope: NES + parent-cohort 25-44 + schools + SALM-extension + (optionally) SEEK/advertised wages. Bundled to amortise ABS workbook reading + concordance work.

**Closed 2026-05-04:** A2 (NES) end-to-end. **Closed 2026-05-05:** OI-36 (NES render + Lite delta badge).

**Remaining bundle, with Demographic Mix elevated:**

- **A10 + C8 — Demographic Mix bundle (next session, ~1.0 sess).** Three Census TSP tables (T07 ATSI, T08 country of birth, T19 single-parent households) all from the same TSP zip already on disk + new Community Profile narrative panel. **EXPANDED 2026-05-05** from T08-only to full bundle per operator review.
- A3 (parent-cohort 25-44, ~0.4 sess)
- A4 (schools at SA2, ~0.5 sess)
- A5 (subtype-correct denominators, ~0.3 sess)
- A6 (SALM-extension, ~0.2 sess)

OI-30 finding folds in: `abs_sa2_erp_annual` ingest extends backward beyond 2019 — adds ~0.3 sess.

### OI-35 — `layer3_apply.py` wholesale-rebuilds `layer3_sa2_metric_banding`, wiping catchment metrics
*Origin: 2026-05-04. Status: open; workaround in place; real fix ~0.5 session.*

Discovered when running `layer3_apply.py --apply` after the B2 patcher. Script does a wholesale `DELETE FROM layer3_sa2_metric_banding` + INSERT-only-its-own-metrics. The 4 catchment metrics banded by `layer3_x_catchment_metric_banding.py` were collateral damage in the wipe. Result: 9,035 catchment-banding rows missing; centre page rendered the 4 catchment rows as em-dashes.

**Recovery 2026-05-04.** Re-ran `layer3_x_catchment_metric_banding.py` (audit 149); 9,035 rows restored.

**Workaround.** Always run `layer3_x_catchment_metric_banding.py --apply` immediately after `layer3_apply.py --apply`. Documented in `recon/layer3_apply.md` and CENTRE_PAGE_V1.5_ROADMAP §"Sequencing rules".

**Real fix.** Refactor `layer3_apply.py` to per-metric DELETE rather than table-wide DELETE. Estimated ~0.5 session. Mid-priority — workaround is reliable and documented.

### OI-33 — 25 SA2s with zero or sparse pop_0_4 coverage
*Origin: 2026-05-03. Status: tracking.*

98.9% of catchment-anchored SA2s sit in the 6-11 year coverage bucket. The remaining 25 are outliers: 16 with zero coverage, 9 with sparse 1-5 year coverage. Disposition tracking only — none are blocking; supply_ratio etc. silently render as None per P-2.

### OI-31 — Click-to-detail on event overlay lines
*Origin: 2026-05-03 PM. Status: open; ~1.0 session.*

Vertical event lines on catchment trajectory charts. Click on a line → popup with quarter, net change, list of new centre names + their places, list of removed centre names. `p.centre_events` array already carries everything needed. Substantial because event lines are drawn by Chart.js plugin (canvas pixels), not DOM elements. Explicitly deferred from V1.5 ship slice.

### OI-28 — `populate_service_catchment_cache.py` cosmetic banner mismatch
*Origin: 2026-04-30. Status: open; cosmetic.*

Banner says "v2" while script is at v5. No functional impact. 5-second fix at next touch.

### OI-26 — `demand_supply` industry threshold post-launch review
*Origin: 2026-04-30. Status: open; tracking; under DEC-77.*

Mathematically grounded but may register false positives in saturated catchments. Review post-launch.

### OI-24 — Sub-pass dependency-ordering pass
*Origin: 2026-04-29. Status: open; tracking.*

DEC-65 extended in spirit to "design before implement when ordering matters." Pure tracking.

### OI-22 — Future centre-page tab: ownership and corporate detail
*Origin: 2026-04-28. Status: tracking; deferred to V1.5+.*

### OI-21 — Future centre-page tab: quality elements
*Origin: 2026-04-28. Status: tracking; deferred to V1.5+.*

### OI-20 — Workforce supply context enrichments
*Origin: 2026-04-28. Status: low priority; tracking. Bundled with OI-19 / A6 / A7.*

### OI-17 — `layer4_3_design.md` v1.0/v1.1 reconciliation
*Origin: 2026-04-28. Status: tracking.*

### OI-16 — DEC-29 verbatim text not recovered
*Origin: 2026-04-28. Status: tracking.*

### OI-15 — Backfill audit for ARIA+ format mismatch
*Origin: 2026-04-28. Status: low priority. Codebase scan candidate.*

### OI-14 — Backfill audit for DD/MM/YYYY date parsing fix
*Origin: 2026-04-28. Status: low priority. Codebase scan candidate.*

### OI-13 — Frontend file backups accumulate in `docs/`
*Origin: 2026-04-28. Status: low; gitignore pattern uses single `?` so `v3_3` doesn't match.*

7+ backup files currently untracked, plus three new `centre.html.pre_oi36*` backups added 2026-05-05. 30-second gitignore tightening fix.

### OI-12 — DB backup pruning
*Origin: 2026-04-28. Status: **CRITICAL**. Cumulative backup size now ~8.5 GB across 41+ files.*

No new DB backups 2026-05-05 (renderer-only work). Status carries from 2026-05-04. Keep policy needs relaxation. When ready: re-run `prune_db_backups.py --apply` after relaxing keep policy, or delete specific large legacy anchors manually.

### OI-10 — `provider_management_type` enum normalisation
*Origin: 2026-04-28. Status: low.*

### OI-09 — `sa2_under5_growth_5y` descoped from Layer 3
*Origin: 2026-04-28. Status: low; deferred.*

### OI-08 — 19 synthetic SA2s with NULL ra_band
*Origin: 2026-04-28. Status: acceptable.*

### OI-07 — `participation_rate` not measured at SA2
*Origin: 2026-04-28. STD-34 LIVE as workaround.*

### OI-06 — LFP source Census-only (3 pts)
*Origin: 2026-04-28. Status: low; OI-19 / A6 may upgrade.*

### OI-04 — 43 services unchanged by Step 1c, lat/lng (0,0)
*Origin: 2026-04-28. Status: medium; overlaps with OI-01/02.*

### OI-03 — 9 cross-state SA2 mismatches post-Step 1c
*Origin: 2026-04-28. Status: low; documented.*

### OI-02 — 2 null-island services (lat/lng = 0,0)
*Origin: 2026-04-28. Status: medium per DEC-63.*

### OI-01 — 18 services without lat/lng need geocoding
*Origin: 2026-04-28. Status: medium per DEC-63.*

---

## CLOSED THIS SESSION (2026-05-05)

- **OI-36** — `centre.html` / `centre_page.py` hardcode catchment-position rows; new metrics don't auto-render. **Closed in commit `430009a`** (centre.html v3.25 → v3.28 + centre_page.py v20 → v21). Surgical patch to render order arrays in both files. Bonus delta badge on all Lite rows reading first-to-last Census-point change ("+9.5pp from 2011 to 2021" for Bayswater NES; "+$291/week from 2011 to 2021" for Bayswater median household income). Unit-aware per `value_format` (percent / percent_share → 'pp'; currency_weekly → '$/week'; currency_annual → '$'; ratio_x → '×'; else plain numeric). Generic helper applies to all Lite metrics — NES, LFP triplet, median household income.

## CLOSED 2026-05-04

- **OI-34** — Absolute change rendered alongside trend % on catchment trajectory charts (commit `f47a0ba`).

## DROPPED 2026-05-04

- **A1** (CENTRE_PAGE_V1.5_ROADMAP scope) — ABS ERP backward extension. Dissolved by probe trail.

## CLOSED PRIOR SESSIONS

- **OI-32** — Catchment metric explainer text. Closed 2026-05-03 evening.
- **OI-30** — Pre-2019 pop_0_4 coverage gap. Closed 2026-05-03 evening (real fix folds into OI-19).
- **OI-29** — `sa2_median_household_income` Lite reclassification. Closed 2026-05-03 PM.
- **OI-25** — Closed 2026-05-03 (premise dissolved by probe).
- **OI-23** — Closed 2026-04-30 (caption fix in workforce window selector).
- **OI-18** — Layer 4.3 design closure. Closed 2026-04-29c.
- **OI-11** — `jsa_vacancy_rate` in Workforce block. Closed 2026-04-29c by DEC-76.
- **OI-05** — `service_catchment_cache` populated. Closed 2026-04-30.
