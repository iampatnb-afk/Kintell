# Open Items

*Last updated: 2026-05-09 (commercial repositioning per DEC-79; new OIs added for Streams A-E, brand rename, doc moves, gitignore fixes, and cross-cutting risks). The on-disk version supersedes the project-knowledge monolith if they disagree.*

OI ID is global. Closed items kept for traceability. Severity tags: CRITICAL / Medium / Low / Cosmetic / Tracking.

---

## OPEN — NEW (2026-05-09 commercial repositioning)

### OI-NEW-1 — "70% break-even" anchor provenance correction in DEC-77
*Origin: 2026-05-09. Status: open; ~0.1 sess.*

DEC-77 cites Credit Committee Brief break-even (70%) + target (85%) occupancy as one source for `sa2_demand_supply` thresholds. The 70% figure is industry benchmark and present in Remara's Childcare Credit Committee Briefing Paper as a derived/implied number, but is **not** a Productivity Commission statement. The DEC-77 attribution as written is correct (it cites the Credit Committee Brief, not PC). Provenance is fine but worth a 1-line clarification in DEC-77 stating that 70% is industry-derived, not PC-published, to remove any future risk of misattribution.

### OI-NEW-2 — Workforce funding cliff Nov 2026 — pricing scenario pass
*Origin: 2026-05-09. Status: open; ~0.5 sess.*

Federal Worker Retention Payment (15% above-award) ends 30 Nov 2026. Fair Work Commission gender-undervaluation determination (10 Dec 2025) added a permanent ~12% on top of the original 15% — cumulative ~27% wage uplift over old baseline, rolling out from 1 March 2026. **Implication for any forward operator EBITDA modelling:** late 2026 sees simultaneous subsidy step-down + permanent wage step-up. Pricing scenarios on the operator + lender + investor surfaces should reflect this cliff. Recommended action: a modelling pass before Nov 2026 to surface the impact and provide pre/post-cliff comparison views.

### OI-NEW-3 — 2026 Census Aug 2026 / SA2 boundary refresh project Q3 2027
*Origin: 2026-05-09. Status: tracking until 2027.*

2026 Census on 11 August 2026; first data release June 2027 in three phases. **SA2 boundaries WILL change** between ASGS 2021 and ASGS 2026. Plan a Q3 2027 data refresh project: re-run Step 1c polygon backfill, re-band Layer 3, refresh `sa2_history.json`, validate `service_catchment_cache`. Touches Stream E (border exposure) too. Long-tail tracking; not blocking V1.

### OI-NEW-4 — Starting Blocks Algolia smoke test + Community Profiles retirement audit
*Origin: 2026-05-09. Status: open; ~0.2 sess.*

Two related risks:
- **Starting Blocks** — pilot at `G:\My Drive\Patrick's Playground\childcare_market_spike\` uses Algolia search method (locked architectural decision). Worth a network-tab inspection before next production run to confirm the Algolia index is still live and credentials still work.
- **ABS Community Profiles** is being retired by ABS. Audit Layer 2 / module2*/scrape code for any dependency on Community Profiles URLs or page structures.

### OI-NEW-5 — SEEK / Indeed anti-scraping audit
*Origin: 2026-05-09. Status: open; ~0.2 sess.*

Both platforms have hardened anti-scraping in 2025. If `module5_news.py` / `module6_news.py` / workforce ingests pull directly from SEEK or Indeed (or rely on third-party APIs that scrape them), expect ongoing arms-race maintenance. Audit current dependencies and document fallback paths.

### OI-NEW-6 — Brand identity rename pass: Novara Intelligence visible everywhere
*Origin: 2026-05-09. Status: open; ~0.5 sess. V1 deliverable per DEC-79.*

Per DEC-79, the working brand is **Novara Intelligence**. Surface this in:
- README.md (currently 2 lines saying "Kintell")
- Doc headers across PROJECT_STATUS / ROADMAP / OPEN_ITEMS / PHASE_LOG (where they reference "Kintell" generically)
- Code comments / page titles in centre.html, operator.html, index.html, dashboard.html, review.html
- centre_page.py / operator_page.py / generate_dashboard.py module docstrings
- Any user-facing copy

**Filesystem and DB names remain unchanged** (`kintell.db`, `remara-agent/`, key Python modules). This pass is brand-identity only, not filesystem rename. Filesystem rename is a separate non-trivial operation deferred indefinitely (would break venv, Python paths, claude-code project state, git worktree).

### OI-NEW-7 — Move Tier-1 docs from `recon/Document and Status DB/` to repo root
*Origin: 2026-05-09. Status: open; ~0.3 sess.*

Currently the Tier-1 / Tier-2 doc layout is split:
- **At repo root:** PROJECT_STATUS.md, ROADMAP.md, OPEN_ITEMS.md, PHASE_LOG.md, CENTRE_PAGE_V1_5_ROADMAP.md, CLAUDE.md (new), PRODUCT_VISION.md (new)
- **At `recon/Document and Status DB/` only:** ARCHITECTURE.md, PRINCIPLES.md, GLOSSARY.md, DATA_INVENTORY.md, CONSOLIDATION_LOG.md, README.md (recon-flavour), **DECISIONS.md (canonical)**, **STANDARDS.md (canonical)**

DECISIONS.md and STANDARDS.md being only at `recon/Document and Status DB/` is the most material gap — they're Tier-2 docs that should be at repo root for visibility (CLAUDE.md cross-references them by repo-root path).

**Action:** move Tier-1 docs (ARCHITECTURE, PRINCIPLES, GLOSSARY, DATA_INVENTORY, CONSOLIDATION_LOG, the canonical DECISIONS and STANDARDS) to repo root. Update STD-35 doc-tier wording to reflect new locations. Update CLAUDE.md cross-refs.

### OI-NEW-8 — Delete stale CENTRE_PAGE_V1.5_ROADMAP.md (dot version)
*Origin: 2026-05-09. Status: open; ~0.05 sess.*

Two roadmap files at repo root:
- `CENTRE_PAGE_V1.5_ROADMAP.md` — dated 2026-05-04, **STALE**
- `CENTRE_PAGE_V1_5_ROADMAP.md` — dated 2026-05-05 with OI-36 close + Demographic Mix expansion, **CANONICAL**

Delete the stale dot version. Confirm no doc references the dot path before deleting.

### OI-NEW-9 — `recon/patchers_*/` evades `patch_*.py` gitignore rule
*Origin: 2026-05-09. Status: open; ~0.05 sess.*

The `recon/patchers_2026-05-03/` directory contains `patch_oi32_*.py`, `apply_session_docs.py`, `cleanup_session_2026-05-03.py`, `add_std36_session_start.py` — all patchers that should be gitignored per STD-10 / DEC-30 ("patchers are mechanism, not artefact"). The `patch_*.py` ignore rule doesn't match because they live under `recon/`. Add `recon/patchers_*/` to `.gitignore`.

### OI-NEW-10 — Stream A scoping: Educator visa / overseas educator supply
*Origin: 2026-05-09. Status: open; ~0.5 sess (recon + scoping).*

Per DEC-79 and PRODUCT_VISION.md Stream A. Recon required:
1. Review existing workforce structures already in the app (workforce supply context block per DEC-76; `jsa_ivi_state_monthly`; ANZSCO 4211/2411)
2. Determine the best integration point (extend Workforce supply context block; or new Workforce Resilience sub-block; or operator-level summary?)
3. Assess available government data granularity (Home Affairs sponsored-visa data; JSA labour-market data; ABS occupation tables; sector-specific visa data via DAMA / regional visa programs)
4. Propose lightweight implementation approach before coding

Output: design doc in `recon/`, then DEC for the framework.

### OI-NEW-11 — Stream B scoping: NFP perspectives integrated into existing structure
*Origin: 2026-05-09. Status: open; ~0.5 sess (recon + scoping).*

Per DEC-79 and PRODUCT_VISION.md Stream B. Recon required:
1. Identify where inclusion-intensity / community-complexity / high-access-need / workforce-constrained / culturally-diverse signals naturally fit in existing pages
2. Identify overlap with current SEIFA / NES / ATSI / single-parent / workforce metrics (avoid duplication)
3. Propose lightest implementation approach — likely derived signals on Catchment Position card + new Community Profile panel rows
4. Avoid UI expansion where existing panels can absorb

Output: design doc in `recon/`, then DEC for the derived-signal framework.

### OI-NEW-12 — Stream C scoping: Childbearing-age + marital-status depth
*Origin: 2026-05-09. Status: open; ~0.3 sess (extends A3 + T19).*

Per DEC-79 and PRODUCT_VISION.md Stream C. A3 (parent cohort 25-44) and T19 (single-parent household share, in A10) cover part of this. New extensions:
- Marital status beyond single-parent share (married with dependents, de facto, separated) — Census TSP T05
- Forward-looking fertility / reproductive-age share as demand indicator
- Household composition (couples-with-children share)

Bundle into A3 ingest pass to amortise TSP workbook reading.

### OI-NEW-13 — Stream D recon: PropCo Property Intelligence schema design
*Origin: 2026-05-09. Status: open; ~1.0 sess (recon + design + DEC). DEC-80 candidate.*

Per Patrick's planning brief (PRODUCT_VISION.md Stream D — PropCo). Schema covers 7 tables (`property_assets`, `service_property_links`, `property_owner_candidates`, `property_owner_evidence`, `property_title_verifications`, `property_transactions`, `propco_opco_relationships`). Recon required before coding:
1. Inventory existing tables: `services`, `entities`, `groups`, audit_log, anything property-flavoured
2. Determine if any existing `properties` or `service_tenures` tables exist; if yes how to extend; if no the lowest-risk additive migration path
3. Confirm key IDs: service_id, entity_id, group_id, property_id, provider_approval, service_approval
4. Confirm address structure (services.address, suburb, state, postcode, lat, lng, sa2_code already verified — DEC-70 polygon-backfilled)
5. Audit pattern compliance (STD-08, STD-30, STD-11, DEC-62)
6. Safest implementation sequence

**Output:** schema review + final table design + migration approach + manual import approach + validation plan + naming alignment to existing conventions + risks / open questions + minimal first coding sequence — landed as a recon doc, then DEC-80 to lock the framework. NO CODE until DEC-80 is locked.

### OI-NEW-14 — Stream E build: SA2 Border Exposure V1 proxy
*Origin: 2026-05-09. Status: open; ~1.0-1.5 sess. DEC-81 candidate.*

Per PRODUCT_VISION.md Stream E. Patrick's brief is implementation-grade but planning gates apply (DEC-65). Sequencing:
1. **DEC-81 lock** — capture: V1 proxy method, naming convention rule (no "catchment" in new field names), V2 forward compatibility (drive-time / population-weighted upgrade path)
2. Build `build_service_sa2_border_exposure.py` with the prescribed top-of-file V1-proxy disclaimer block
3. Create `service_sa2_border_exposure` table + indexes
4. Centre page CONTEXT row integration (sa2_boundary_exposure, NOT sa2_catchment_exposure)
5. Spotcheck 3 services (low / medium / high / multi_sa2 cases)

Cross-cuts with OI-30 / OI-33 (SA2 coverage outliers).

### OI-NEW-15 — Excel Export Framework — V1 deliverable scoping
*Origin: 2026-05-09. Status: open; ~2-3 sess. DEC-candidate.*

Per DEC-79 #10. V1 deliverable. Recon required:
1. Survey existing export points (catchment_html, generate_prospecting_page, etc.)
2. Choose underlying library (openpyxl already in venv; xlsxwriter alternative)
3. Define standardised templates per object type (Centre, Operator, Catchment, Group, PropCo)
4. Audit-friendly column conventions (provenance row, source citation column)
5. Repeatable workbook structures
6. Branded headers (Novara Intelligence)

**Output:** design doc → DEC → first workbook template → integration hooks per surface.

### OI-NEW-16 — Catchment page (V1)
*Origin: 2026-05-09. Status: open; ~3-4 sess. V1 deliverable.*

New surface cascading from centre page. Reuse Position card patterns. Absorbs Stream B/C/E signals at catchment level. Operator-level rollups via `service_catchment_cache`. Renderer pattern well-trodden post-OI-36. Scoping doc → design → ingest hooks (mostly read-only over existing tables) → render → polish.

### OI-NEW-17 — Group page (V1)
*Origin: 2026-05-09. Status: open; ~3-4 sess. V1 deliverable.*

Sits above catchment. Operator-network views, exposure summaries, portfolio lens. Picks up Stream D PropCo portfolio signals (landlord concentration, institutional landlord exposure, related-party PropCo exposure, on-market portfolio assets) and Stream A workforce dependency at portfolio level. Aggregates over Group → Portfolio → Brand → Entity → Service hierarchy (DEC-1).

### OI-NEW-18 — Institutional readiness foundations
*Origin: 2026-05-09. Status: open; ~1-2 sess. V1 deliverable.*

V1 readiness artefacts (not certification — that's V2). Includes:
- Methodology documentation (extend GLOSSARY.md / DATA_INVENTORY.md to be customer-readable)
- Privacy governance baseline document
- Data-handling policy outline
- Audit-trail visibility (already strong via STD-11 + DEC-62; surface to customers in Excel export provenance rows)
- Multi-tenancy / auth architecture design pass (deployment in V2; design only in V1)

---

## OPEN — EXISTING (carried)

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
