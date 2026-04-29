# Decisions

Architecture Decision Records (ADRs) for the Kintell project. Every material decision lives here with a stable global ID, a status, and the context behind it.

## Format

Each entry uses this template:

```
## DEC-N — Title
Status: Active | Superseded by DEC-X | Withdrawn | Deferred
Date: YYYY-MM-DD
Supersedes: DEC-Y (if applicable)

Context: …
Decision: …
Consequences: …
```

## ID discipline

IDs are global and stable. They originate from the historical numbering in the monolith chain (1–73 as of 2026-04-28b). When two decisions are consolidated, the canonical ID is retained and the merged one is marked `Status: Superseded by DEC-X`. IDs are never re-used. The `CONSOLIDATION_LOG.md` records the merges performed during the 2026-04-28 restructure.

## Index

Decisions 1–10 are foundational architecture and the original session set. Decisions 11–28 cover the operator-page and workforce-card era. Decisions 29–49 cover Phase 2 (centre.html drillthrough) and the Phase 2.5 layer plan. Decisions 50–68 cover Layer 2 data ingest and Layer 3 banding. Decisions 69–73 cover Layer 4 (centre page v2) and the visual consistency audit. Decisions 74–76 cover the Layer 4.3 design closure (perspective toggle, visual weight by depth, workforce supply context).

---

## DEC-1 — Five-level entity hierarchy
Status: Active
Date: 2026-04-22

Context: The platform needs a stable representation of the relationship between legal entities, brands, and centres for both display and merge-review purposes.

Decision: Adopt a five-level hierarchy: Group → Portfolio → Brand → Entity → Service. Portfolio collapses to "default" for ~95% of operators.

Consequences: All aggregation logic (group view, brand view, group×state) is computed over this hierarchy. The portfolio level is structurally present but rarely populated.

---

## DEC-2 — Brand views as computed slices, not snapshot tables
Status: Active
Date: 2026-04-22

Context: A brand-level view could be modelled as a stored aggregate or as a query over the entity graph.

Decision: Brand views are computed slices over services + entities + groups. Same aggregation logic serves group, brand, portfolio, and group×state.

Consequences: One implementation, four uses. No snapshot-staleness risk. Compute cost is borne at view time and is acceptable at current data volumes.

---

## DEC-3 — Catchment aggregation joins via service_catchment_cache
Status: Active
Date: 2026-04-22

Context: Per-service SA2-level catchment metrics must roll up to brand and group levels.

Decision: Aggregation joins via `service_catchment_cache` (per-service SA2 metrics). The join logic is identical at group and brand level.

Consequences: One join pattern across all aggregation tiers. The cache is the single source of truth for per-service catchment data.

---

## DEC-4 — Joint ventures and watchlist flags excluded from V1
Status: Active
Date: 2026-04-22

Context: Joint-venture relationships and watchlist annotation were considered for V1.

Decision: Both are excluded from V1 scope. They are deferred to a later phase.

Consequences: V1 entity model is simpler. Joint-venture handling will require a many-to-many relationship layer when added.

---

## DEC-5 — Confidence thresholds use Panel 3 colours
Status: Active
Date: 2026-04-22

Context: Catchment supply-ratio thresholds need consistent visual encoding.

Decision: Confidence thresholds use Panel 3 colours throughout: balanced <0.55× supply ratio, supplied 0.55–1.0×, oversupplied >1.0×.

Consequences: Visual consistency across catchment surfaces. Threshold values are the single canonical convention; downstream code references them via shared constants.

---

## DEC-6 — Operator-related signals reviewed for the linker
Status: Active
Date: 2026-04-22

Context: The merge-review tool needs a hierarchy of signals for proposing operator-level merges.

Decision: Signals in priority order are: (1) brand prefix in service_name (free, near-decisive when present), (2) shared Provider Approval number (free, hard link), (3) shared phone / email domain / postal address (free), (4) ABR director / registered office overlap, (5) website "Our Centres" scrape, (6) industry knowledge / direct user input, (7) news/press release search via AI, (8) LinkedIn employer disclosure, (9) ASIC director extracts, (10) trademark register, (11) domain WHOIS / shared hosting, (12) social media handle commonality.

Consequences: Only signals 1, 2, and partial 3+4 are wired into `propose_merges.py` today. Others remain as candidate signals to add when the cheap ones plateau.

---

## DEC-7 — Review UX as brand-cluster cards, not per-card individual review
Status: Active
Date: 2026-04-22

Context: Initial review UX presented every individual entity for separate approval. With 31 individual Aspire approvals queued, this was confirmed as pure busywork.

Decision: Review UX is brand-cluster cards with per-entity checkboxes. Bulk-accept variants are supported.

Consequences: Materially reduced reviewer load. Approve-all-in-cluster is the common path; per-entity granularity is preserved for edge cases.

---

## DEC-8 — Raw JSON evidence panel replaced
Status: Active
Date: 2026-04-22

Context: The original "evidence" panel exposed raw JSON, which was unfit for purpose.

Decision: Replace with plain-language reasoning + external tool buttons + (later) the operator pop-out side-drawer.

Consequences: Reviewers can act on the evidence without parsing JSON. External tool buttons (ACECQA, ABR, ASIC, Starting Blocks, Google) provide one-click verification routes.

---

## DEC-9 — Six-value ownership_type enum
Status: Active
Date: 2026-04-23

Context: Ownership classification needed a stable representation that distinguishes regulatorily-relevant categories without losing extensibility.

Decision: `ownership_type` uses a six-value enum: `private` → "Private (for profit)", `nfp` → "Not-for-profit", `government` → "Government", `independent_school` → "Independent school", `catholic_school` → "Catholic school", `unknown` → "Not classified". The DB stores raw TEXT so new values can be added without schema change. Independent and Catholic schools are split out from `nfp` because their operating model (LDC/OSHC under a school's legal entity) is distinct enough to matter for credit framing.

Consequences: UI mapping happens at render time. New ownership categories can be added by extending the application-level map without a schema migration.

---

## DEC-10 — Tier 2 ingest pattern
Status: Active
Date: 2026-04-23

Context: Tier 2 data ingests (e.g. NQAITS, NCVER) needed a repeatable pattern that preserves existing data and provides a recovery path.

Decision: Tier 2 ingest pattern: schema migration takes its own backup and writes one audit_log row; ingest runs UPDATE-only inside a single transaction with pre/post invariant check on `accepted_merges + entities + groups counts`; dry-run is mandatory before real run; `COALESCE(?, existing_value)` is used so existing data is preserved when source is NULL; `rating` and `overall_nqs` are the only fields always-overwritten (refreshed from the authoritative ACECQA source).

Consequences: Pattern is reusable for Tier 3 and Tier 4 ingests. Forms the basis of `STANDARDS.md` § Data lifecycle entries on backups and audit_log discipline.

---

## DEC-11 — Additive overlay pattern as default
Status: Active
Date: 2026-04-25

Context: The platform needs to add modules and metrics without disturbing shipped surfaces.

Decision: Additive overlay is the project's default pattern. New modules layer over existing data and surfaces; existing surfaces are not modified to accommodate them where the addition can be made non-invasively.

Consequences: Lower regression risk. Higher discipline burden — additive scaffolding may accumulate over time and require periodic consolidation.

---

## DEC-12 — OBS / DER / COM classification
Status: Active
Date: 2026-04-25

Context: Page surfaces mix observed values, derived values, and rule-based commentary. Reviewers need to distinguish these to assess provenance.

Decision: Cross-cutting OBS / DER / COM classification applies to all surfaced fields and rows. OBS = observed (direct from source). DER = derived (computed from observed inputs with a documented rule). COM = commentary (rule-based narrative line).

Consequences: Every page renders OBS / DER / COM badges. DER values expose their rule via tooltip. COM lines are severity-coloured.

---

## DEC-13 — model_assumptions table as single source of truth
Status: Active
Date: 2026-04-25

Context: Project assumptions (educator ratios, target margins, calibration constants) were at risk of being scattered across code as magic numbers.

Decision: The `model_assumptions` table is the single source of truth for assumption values. Code references rows by canonical key. Magic numbers in code are prohibited.

Consequences: Assumption changes are one-row updates with audit trail. Per-SA2 calibrated values (introduced in DEC-65 and the staged STD-34) follow this principle via a named module rather than scattered constants.

---

## DEC-14 — Module 2 Workforce ships in two tranches
Status: Active
Date: 2026-04-25

Context: The Workforce module has both demand-side (operator level) and supply-side (industry level) components. Shipping both at once was not necessary for V1.

Decision: Module 2 ships in two tranches. Demand half (operator card) ships first. Supply half (industry view) is deferred to Phase 3.

Consequences: V1 operator surface includes the workforce demand block. Supply-side rendering is part of the Industry view scope.

---

## DEC-15 — Pricing placeholder built honestly
Status: Active
Date: 2026-04-25

Context: Pricing data is not yet available. The page surface needs a placeholder.

Decision: The pricing placeholder is built honestly. Module 4 surfaces the placeholder as such; no synthetic numbers are shown.

Consequences: Page composition is complete; pricing values are clearly absent until the data layer arrives via Phase 5 / Phase 8.

---

## DEC-16 — Starting Blocks scraper writes to dedicated tables only
Status: Active
Date: 2026-04-25

Context: The Starting Blocks scraper (Phase 8) needs a target schema in the main DB.

Decision: The Starting Blocks scraper writes only to dedicated tables. It does not mutate `services`, `centre`, or other shipped tables. Identity resolution against existing tables is a separate downstream step.

Consequences: Scraper failure cannot regress shipped data. Pilot work performed in a standalone DB (see `MODULE_SUMMARY_Childcare_Market_Data_Capability.md`) confirms the pattern.

---

## DEC-17 — Methodology tooltip convention
Status: Active
Date: 2026-04-25b

Context: Hover tooltips on derived values needed a consistent format.

Decision: Methodology tooltip content has a fixed structure: short rule statement, then inputs with values, then citation/source where applicable.

Consequences: Hover content is predictable across modules. DER tooltips on the centre and operator pages follow this structure.

---

## DEC-18 — Module-constant fallbacks pattern
Status: Active
Date: 2026-04-25b

Context: Where existing module constants encode an assumption, code that references them should fall back to the module value rather than re-declaring it locally.

Decision: Module-constant fallbacks are the canonical pattern. Local re-declaration is prohibited.

Consequences: Single point of truth per assumption. Reduces drift.

---

## DEC-19 — COM badge rendering rule
Status: Active
Date: 2026-04-25b

Context: Commentary (COM) lines need a consistent visual treatment.

Decision: Commentary lines render as severity-coloured rows: green (positive), amber (caution), red (negative), info (neutral).

Consequences: Reviewers parse the page by colour. Severity is set by the commentary rule, not the data value directly.

---

## DEC-20 — Validation tolerance for rounded sources
Status: Active
Date: 2026-04-25c

Context: ABS and other rounded-source data may not sum exactly. Strict equality checks fail.

Decision: Validation tolerance pattern: rounded-source aggregates are compared with a documented tolerance (typically ±0.5 percentage points for percentages, ±1% for counts). Out-of-tolerance results trigger investigation; in-tolerance results pass.

Consequences: Validation does not false-fail on legitimate rounding. The tolerance is itself a documented convention, not arbitrary.

---

## DEC-21 — Provenance row + caveat capture pattern
Status: Active
Date: 2026-04-25c

Context: Every ingest produces metadata that callers need: source identifier, run timestamp, run-specific caveats.

Decision: Every ingest produces one provenance row in the appropriate `*_ingest_run` table, capturing source, date, row counts, and any caveats specific to the run (e.g. NCVER qualification-transition trough).

Consequences: Downstream consumers can render caveat text alongside data. Cross-session reproducibility is preserved.

---

## DEC-22 — Two-commit pattern for "supply data, then UI"
Status: Active
Date: 2026-04-25c

Context: Shipping a UI change that depends on new data risks broken pages between the data commit and the UI commit.

Decision: Two-commit pattern: first commit lands the data (ingest, schema, audit). Second commit lands the UI consumer. Both can be deployed independently and the page does not regress.

Consequences: Slower than a single-commit ship but safer. Used routinely for Layer 2 + Layer 4 work.

---

## DEC-23 — Operator-level vs industry-level metric separation
Status: Active
Date: 2026-04-25d

Context: Some metrics describe what an operator can influence; others describe the wider sector. Mixing them on operator cards muddles the credit lens.

Decision: Operator cards stay focused on operator-controllable signals. Industry context lives in the Industry view. State-level training-completions data is the canonical example: an operator with 60 centres in QLD does not compete for all of QLD's 6,085 graduates; the right framing is "your demand vs your share of state supply" — itself a derived metric layered over an industry-level base.

Consequences: Page composition reflects agency. Workforce supply rendering is Industry-view scope, not operator-card scope (DEC-14). Reaffirmed by DEC-36. Note: DEC-76 (workforce supply context block) admits state-level supply metrics onto the centre page in a Context-only weight (DEC-75) where the data informs an operator's catchment-specific staffing risk; this is a refinement of P-7 (operator agency determines surface placement), not a contradiction of DEC-23 — the framing remains "this is state-level information bearing on your centre", not "this is your centre's operator-controllable workforce metric".

---

## DEC-24 — NCVER qualification-transition caveat
Status: Active
Date: 2026-04-25d

Context: NCVER training-completions span both superseded codes (CHC30113 Cert III, CHC50113 Diploma) and current codes (CHC30121, CHC50121). The transition spans 2022–2024. 2023 is the artificial trough.

Decision: Single-year YoY comparisons against 2023 are misleading and prohibited as a default. Multi-year baselines (e.g. 2024 vs 2022, or rolling 3-year averages) are the correct comparison. The `training_completions_ingest_run` row captures this caveat. The Workforce card placeholder explains it. The Industry view will show the qualification-transition curve explicitly with the trough labelled.

Consequences: Workforce supply commentary on the Industry view will reference the transition explicitly. Naive YoY percentage changes against 2023 are excluded.

---

## DEC-25 — Children-per-educator as canonical convention
Status: Active
Date: 2026-04-25d

Context: Educator ratios were originally seeded as `educators-per-child` (1/N). Children-per-educator (4, 5, 6.5, 11, 15) is the regulatory and operational convention.

Decision: `value_numeric` for `educator_ratio_*` rows in `model_assumptions` holds the count of children per educator. `units='children_per_educator'`. Downstream consumers compute `required_educators = approved_places / value_numeric`. The educators-per-child convention used by Phase 0a is now historical; `migrate_ratio_convention_to_cpe.py` converted all Phase 0a-seeded rows.

Consequences: Future `educator_ratio_*` rows must follow this convention or be flagged explicitly with a different units string and handled distinctly by consumers.

---

## DEC-26 — audit_log NOT NULL contract
Status: Superseded by DEC-62
Date: 2026-04-25d

Context: Three rounds of script v1/v2 burned discovering one NOT NULL column at a time (`action`, then `subject_type`).

Decision: Four NOT NULL columns: `actor`, `action`, `subject_type`, `subject_id`. `subject_id` is declared INTEGER but stores TEXT via SQLite affinity (per row 121 convention: 'training_completions'). Any future DB-mutating script writes audit rows with this exact column set, plus optional `before_json` / `after_json` / `reason` / `occurred_at`.

Consequences: Superseded by DEC-62, which provides the complete canonical audit_log schema and the corresponding hardcoded INSERT pattern (STD-30). The NOT NULL contract from this decision is preserved within DEC-62.

---

## DEC-27 — Line-ending detection for byte-level patchers
Status: Superseded by STD-12
Date: 2026-04-25d

Context: Files in this repo vary CRLF vs LF (likely from `autocrlf` misconfiguration; `operator.html` is LF, several other repo files are CRLF). Hardcoded `\r\n` anchors fail silently on LF files.

Decision: Patchers must detect the predominant line ending on read (count `\r\n` vs orphan `\n`) and rebuild every anchor + replacement with that ending before applying replacements. Source-of-truth anchors stored as LF-only in the script; runtime helper `with_le(s_lf, le)` converts.

Consequences: Established in `patch_operator_html_to_v7.py v3` after v1+v2 burned a session round each. Promoted to a working standard (STD-12). This decision now serves as the historical record; the operative rule lives in `STANDARDS.md`.

---

## DEC-28 — Two-version backup pattern for risky frontend patches
Status: Active
Date: 2026-04-25d

Context: Patcher runs occasionally fail mid-mutation. A timestamped pre-mutation backup of the patched file enables single-command revert.

Decision: Each patcher run creates a timestamped backup (`<file>.v<N>_backup_<ts>`) before mutating. Backup files are gitignored under `*.v?_backup_*`. Single-command revert: `Copy-Item .\docs\<file>.v?_backup_<ts> .\docs\<file> -Force`.

Consequences: Backups accumulate; periodic manual purge of `data/` is required. Pattern complements STD-13 (timestamped DB backup before any DB mutation).

---

## DEC-29 — Kintell → Novara rebrand (Phase 1.7)
Status: Withdrawn
Date: 2026-04-26 (original); withdrawn 2026-04-28

Context: A renaming of the platform from Kintell to Novara was scheduled as Phase 1.7. Original-text body of this decision was not preserved in the recovered monolith chain; references in the 2026-04-26 and 2026-04-27c monoliths confirm the intent. The user's working memory has since redirected the project's framing away from the prior Remara-based identity and toward a generic childcare-industry positioning; the rebrand decision is not active.

Decision: The Phase 1.7 rebrand is withdrawn from V1 scope. Naming is treated as a roadmap item; no rebrand work is scheduled.

Consequences: The repo and DB filename `kintell.db` remain as-is. No code-base-wide rename is undertaken at this time. Future rebranding, if pursued, will be re-scoped as a fresh decision.

---

## DEC-30 — Patchers are mechanism, not artefact
Status: Active
Date: 2026-04-26

Context: Standard 3 (bump version markers in file headers) and the `.gitignore` pattern `patch_*.py` (which excludes patcher scripts from git) appeared to contradict each other on whether patchers form part of the audit trail.

Decision: Patchers (`patch_*.py`) are mechanism, not artefact. Version comments embedded in the patched file (e.g. `<!-- operator.html v9 -->`) are the canonical audit trail. The `.gitignore` rule `patch_*.py` stands; patcher scripts are not committed.

Consequences: Resolves the contradiction between Standard 3 and the existing gitignore policy. Standard 3 is amended to specify that the version comment in the patched file is the audit trail.

---

## DEC-31 — Generic gitignore for versioned backups
Status: Active
Date: 2026-04-26

Context: Versioned backups were previously covered only by `docs/operator.html.v?_backup_*`, leaving e.g. `review_server.py.v5_backup_*` visible to git.

Decision: Generic `.gitignore` pattern `*.v?_backup_*` added to cover all versioned backups across all files.

Consequences: Pattern matches `v3_backup`, `v5_backup`, `v8_backup`, etc. across any path. Future backup files do not require separate `.gitignore` entries.

---

## DEC-32 — Centre page architectural pattern: three temporal moods
Status: Active
Date: 2026-04-26

Context: The centre page needs an organising principle that scales across all centre-level metrics.

Decision: Every centre-level metric supports three views: NOW (current state), PAST (trajectory / history / trend), and RELATIVE (banding within catchment / industry slice). The operator page does NOW + RELATIVE-via-aggregate. The Industry view does PAST + RELATIVE-via-distribution. The centre page does all three at the leaf level.

Consequences: Forms the spine of Phase 2.5 Layer 4. Centre page renders Now/Trajectory/Position cards per metric. Implementation matches this taxonomy throughout. DEC-75 refines the per-metric application: the full Now/Trajectory/Position treatment is applied where data depth supports it, with Lite and Context-only weights for shallower/coarser metrics.

---

## DEC-33 — First-inspection threshold: 9 months
Status: Active
Date: 2026-04-26

Context: New centres need a threshold for "expected" first NQS rating timing. No empirical distribution is available yet.

Decision: First-inspection threshold for new centres is 9 months. Stored as `inspection_first_rating_expected_months` in `model_assumptions`. To be replaced with an empirical distribution (median months from `approval_granted_date` to first `rating_issued_date`, by state and subtype) once the Industry view ingests historical NQS snapshots.

Consequences: Phase 2.5 ships with this static threshold. Replacement is deferred to Phase 3 work, not blocking V1.

---

## DEC-34 — Five-state NQS+cadence classification
Status: Active
Date: 2026-04-26

Context: V1's binary rated/unrated classification masks the difference between a stale rating, a recent rating, a brownfield carryover, and a genuinely new centre.

Decision: Five-state classification:
- A. Established current — rated, ≤18m since rating
- B. Established stale — rated, >18m
- C. New in-window — unrated, opened ≤9m, no transfer
- D. New late — unrated, opened >9m, no transfer
- E. Brownfield carryover — unrated, transfer date present

Consequences: Lands in `centre.html` v2 (Phase 2.5) and propagates to the operator-page centres table for congruence.

---

## DEC-35 — ABS demographic data sourcing
Status: Active
Date: 2026-04-26

Context: Demographic data has multiple sources with different cadences and granularities. Selection needed.

Decision:
- Annual ERP at SA2 → time-series of children aged 0–5 (preferred over Census for currency)
- Census 2021 → static enrichment (income, family, education/employment)
- Births by SA2 → leading-indicator demand signal (annual; ABS Cat 3301.0)
- SALM Smoothed → quarterly unemployment at SA2

Consequences: Each source becomes a SA2-keyed annual or quarterly table joined to services via `services.sa2_code`. Census 2021 static fields layer over `service_catchment_cache` when that table is built (gated on Layer 2.5).

---

## DEC-36 — NCVER training-completions stays at Industry view only
Status: Active
Date: 2026-04-26
Supersedes: (reaffirms DEC-23)

Context: When the centre page enhancement scope was being defined, the question of whether to render training-completions on the centre page came up.

Decision: NCVER training-completions stays at Industry view only. State/remoteness granularity is structurally industry-level; no operator agency.

Consequences: Doubles down on DEC-23. No change to existing implementation. Note: DEC-76 admits state-level workforce supply metrics (JSA IVI ANZSCO 4211 / 2411) into the centre page Workforce supply context block in Context-only weight; NCVER specifically remains Industry-view per this decision unless the OI-20 probe confirms NCVER-by-SA2/remoteness is already ingested and useful for centre-level rendering.

---

## DEC-37 — nqs_history is the canonical NQS time-series table
Status: Active
Date: 2026-04-26b

Context: The NQAITS quarterly ingest produces a substantial time-series table. Naming needed to be unambiguous.

Decision: `nqs_history` is the canonical NQS time-series table name. `service_history` is reserved for non-NQS service-level events (transfers, status changes).

Consequences: Future ingests follow this naming. Cross-table joins use `nqs_history` for rating/quality time-series and `service_history` for life-cycle events.

---

## DEC-38 — Self-group convention for orphan entities
Status: Active
Date: 2026-04-26b

Context: Some entities (e.g. independent schools running their own ECEC service) have no parent group, breaking the operator-page cross-link.

Decision: For orphan entities, create one new group per entity (one entity = one group). Use `ownership_type='independent_school'` (or appropriate value) for the self-group.

Consequences: Backfilled retroactively for affected entities. Future ingests apply the self-group convention automatically when an active service has no group_id.

---

## DEC-39 — ownership_type derivation for self-groups
Status: Active
Date: 2026-04-26b

Context: Self-groups need an `ownership_type` value; the derivation rule must be explicit.

Decision: Map self-group `ownership_type` from the entity's known characteristics: independent school → `independent_school`; Catholic school → `catholic_school`; otherwise `unknown` until classified.

Consequences: Self-groups carry meaningful ownership classification from creation rather than defaulting to `unknown`.

---

## DEC-40 — is_for_profit derivation
Status: Active
Date: 2026-04-26b

Context: `is_for_profit` is computed from `ownership_type` rather than stored independently.

Decision: `is_for_profit` derivation: `ownership_type='private'` → True; all other values → False (not-for-profit, government, school, unknown all map to False).

Consequences: Single rule, deterministic. Changes to ownership classification automatically propagate to for-profit status.

---

## DEC-41 — NQAITS ingest scope: all 23,439 SE-prefixed services
Status: Active
Date: 2026-04-26b

Context: NQAITS publishes data for both currently-active and historically-active services. Scope decision needed.

Decision: NQAITS ingest scope includes all 23,439 SE-prefixed services from the historical published data. Closed/withdrawn services are retained for time-series completeness.

Consequences: `nqs_history` rowcount is 807,526 across 50 quarters and 23,439 unique service IDs. PA chain changes (6,155 observed) are recoverable from the historical record.

---

## DEC-42 — ABS publishes SA2-level births for free
Status: Superseded by DEC-42 (corrected)
Date: 2026-04-26b (original); 2026-04-27 (corrected)

Context: Original 2026-04-26b wording said Step 8 (births by SA2) "may require TableBuilder Pro custom request" with cost $300–1500. This was incorrect.

Decision (corrected): ABS publishes SA2-level births for free in their standard data cubes (Cat 3301.0 Table 2). No paid request needed. File on disk at `abs_data/Births_SA2_2011_2024.xlsx` (928 KB). Step 8 effort estimate unchanged at 0.5 sessions but the cost blocker is removed.

Consequences: Step 8 is unblocked. Births data lands in Phase 2.5 Layer 2.

Further note (2026-04-28b): Postcode-derived `sa2_code` was systematically wrong for postcodes spanning multiple SA2s (DEC-70). The "approximate concordance" caveat originally attached to this decision is itself superseded by DEC-70's polygon-based overwrite. Postcode-derived `sa2_code` is now fallback-only.

---

## DEC-43 — Quarter-end date convention for nqs_history
Status: Active
Date: 2026-04-26b

Context: Quarterly NQAITS data needs a normalised date representation.

Decision: Quarter-end date convention for `nqs_history`: store as the last day of the quarter (YYYY-03-31, YYYY-06-30, YYYY-09-30, YYYY-12-31).

Consequences: Date arithmetic and ordering work cleanly. Joins to other quarterly series (e.g. SALM) use the same convention.

---

## DEC-44 — provider_name in nqs_history is per-row
Status: Active
Date: 2026-04-26b

Context: Provider names change over time (re-naming, ownership transfer). Storing a single `provider_name` per service would lose history.

Decision: `provider_name` in `nqs_history` is a per-row value, not pulled from a parent table. Each row records the provider name as published at that quarter.

Consequences: PA chain reconstruction is faithful to the historical record. Cross-quarter aggregation requires explicit handling of name changes.

---

## DEC-45 — module2b_catchment.py relocated from abs_data/
Status: Active
Date: 2026-04-26b

Context: `module2b_catchment.py` was historically located in `abs_data/` despite being code, not data.

Decision: Relocate from `abs_data/` to the project root. `abs_data/` reserved for source data files only.

Consequences: Cleaner separation of code and data. Import paths updated accordingly.

---

## DEC-46 — services lat/lng column naming
Status: Active
Date: 2026-04-26b

Context: Column naming for spatial coordinates was previously inconsistent across scripts.

Decision: `services` lat/lng columns are named `lat` and `lng`. Not `latitude`/`longitude`, not `lat_dd`/`lng_dd`, not `y`/`x`.

Consequences: All downstream code references `lat`/`lng`. Spatial-join scripts (Step 1b, Step 1c) use this naming.

---

## DEC-47 — Starting Blocks ADR data: two-track approach
Status: Active
Date: 2026-04-26b

Context: Starting Blocks ADR (administrative data return) data is needed both for V1 (commercial-layer) and for ongoing refresh.

Decision: Two-track approach. Track 1: pilot scrape into a standalone DB to prove method (delivered as the Starting Blocks pilot). Track 2: production scraper into main `kintell.db` (Phase 8).

Consequences: Pilot DB stays standalone; integration into `kintell.db` is a separate, scheduled effort. See `MODULE_SUMMARY_Childcare_Market_Data_Capability.md` for pilot details.

---

## DEC-48 — Data-source tagging convention
Status: Active
Date: 2026-04-26b

Context: ADR-style fields (those derived from administrative-data-return scrapes) need explicit source tagging in the schema.

Decision: ADR-style fields carry an explicit source tag in column comments and schema docs (e.g. `-- src: starting_blocks_adr`). Multi-source fields carry a `_source` companion column where reconciliation logic exists.

Consequences: Provenance is queryable. Multi-source reconciliation has an explicit hook.

---

## DEC-49 — V1 launch scope: four phases promoted
Status: Active
Date: 2026-04-26b

Context: V1 scope had drifted; some Phase 2 / Phase 3 items were not actually V1 blockers.

Decision: V1 launch scope includes: Phase 4 (Compliance cadence formalisation), Phase 7 (Commentary engine), Phase 8 (Starting Blocks scraper). Phase 1.7 (rebrand) was originally also promoted but is now withdrawn (DEC-29). Phase 3 (Industry view) and Phase 5 (Pricing module proper) remain P2.

Consequences: V1 critical path is bounded. See `ROADMAP.md` for current V1 status.

---

## DEC-50 — Auto-detected columns must validate by sample value range
Status: Active
Date: 2026-04-27

Context: ABS Data by Region "Total fertility rate" column (idx 121 in `Population and People Database.xlsx`) shares the substring "Total" with population columns. Header-text matching alone shipped the wrong column in v1.

Decision: Auto-detected columns must validate by sample value range, not just header text. Reusable pattern: any auto-detected column has a sample-value sanity check appropriate to the expected data type (range, scale, internal consistency).

Consequences: Codified in STD-25. Catches the failure mode where ABS publishes different metric types under the same header.

---

## DEC-51 — Centre page Population and Labour Market cards: Now/Trajectory/Position
Status: Active
Date: 2026-04-27
Supersedes: (reaffirms DEC-32)

Context: The centre page's Population and Labour Market cards needed to confirm the three-temporal-mood pattern.

Decision: Population and Labour Market cards use Now/Trajectory/Position layout per DEC-32. Visual primitives are reused from operator page wherever data shape allows. Composite scores are prohibited (already implicit; now explicit). Geography is always labelled (SA2 vs SA4); never silently mixed.

Consequences: Implementation pattern is locked. No composite-score panels are introduced; layered position indicators (decile strip, chip strip, histogram) are the canonical alternative.

---

## DEC-52 — Adjustment 1 (SA4 SALM extension) deferred
Status: Deferred (P2)
Date: 2026-04-27

Context: Original plan called for SA4 SALM to complement SA2 SALM. JSA SALM only publishes at SA2 and LGA — there is no SA4 SALM file. SA4 unemployment is available from ABS Cat 6202.0 Labour Force survey but adds an extra ingest.

Decision: For V1, SALM SA2 alone is the higher-value signal (smoothed, ECEC-relevant catchment view). Local-vs-Regional Gap derived signal moves to optional P2 Step 5d. Adjustments 2 and 3 remain in V1.

Consequences: V1 ships with SA2 unemployment only. Codified the verification pattern that became STD-26.

---

## DEC-53 — SALM publishes only SA2s above a population threshold
Status: Active
Date: 2026-04-27

Context: Some recently-developed SA2s have no SALM data, or have data only from recent quarters forward.

Decision: Treat SALM coverage as bounded. Layer 4 reads handle SALM-missing SA2s with explicit empty-state copy. No imputation.

Consequences: Empty-state UI is part of the Layer 4 spec, not an afterthought.

---

## DEC-54 — SALM SA2 long tail: state-and-remoteness-stratified cohort
Status: Active
Date: 2026-04-27

Context: A naive Layer 4 percentile comparison against all SA2s pooled would put a small remote SA2 in a meaningless cohort.

Decision: Layer 4 percentile comparison uses a state-and-remoteness-stratified cohort, not all SA2s pooled. Also applies to RWCI banding (extended 2026-04-27b).

Consequences: Cohort definition `state_x_remoteness` is the default for many metrics. Locked the cohort taxonomy used in Layer 3.

---

## DEC-55 — JSA IVI Northern Australia sheet excluded from V1
Status: Deferred (P2)
Date: 2026-04-27

Context: The JSA Internet Vacancy Index "Northern Australia" sheet adds geographic complexity for marginal V1 value.

Decision: Northern Australia sheet excluded from V1 IVI ingest. Standard ANZSCO state-level rendering is sufficient.

Consequences: Step 5c ships without Northern Australia. Re-scope candidate for P2 if demand emerges.

---

## DEC-56 — JSA Remoteness publishes only 2 ECEC categories
Status: Active
Date: 2026-04-27

Context: For ECEC ANZSCO codes (4211, 2411), JSA Remoteness publishes only Major City and Regional — not the full 5-category Remoteness Area split.

Decision: Treat JSA Remoteness for ECEC as a 2-category signal (Major City / Regional). Code paths that consume RA-stratified data must handle this gracefully.

Consequences: ECEC workforce demand panels render the 2-category split; the full RA split is not available from JSA for these codes.

---

## DEC-57 — ABS Data by Region: same column header, different metric types per row
Status: Active
Date: 2026-04-27

Context: Income Database column 54 publishes "participation rate (%)" for AUST/State rows but a count for SA2 rows. Sample-value validation must come from SA2-level rows specifically.

Decision: Sample-value validation for ABS Data by Region columns must come from SA2-level rows, not the first 10 rows (which are AUST/State aggregates).

Consequences: Codified in STD-25. Diagnostic scripts sample rows 75+ in WIDE-format ABS workbooks.

---

## DEC-58 — Education and Employment Database is LONG format
Status: Active
Date: 2026-04-27b

Context: ABS Data by Region "Education and Employment Database" uses LONG format (Code|Label|Year|metric_cols), not the WIDE format of Income/Population databases.

Decision: Detection heuristic: if columns 1–3 are "Code", "Label", "Year" then LONG format. Header rows still follow STD-22 (row 6 spanning, row 7 sub-headers, row 8+ data). For LONG, no wide-to-long pivot is needed in apply — year is already a column.

Consequences: Codified in STD-23. Apply scripts detect format before pivoting.

---

## DEC-59 — ABS confidentialization tolerance for derived rates
Status: Active
Date: 2026-04-27b

Context: ABS confidentialization (independent random perturbation of small cell counts) can produce derived rates >100 in low-population SA2s. National aggregates and means remain accurate.

Decision: The right sanity invariant is AVG-in-expected-range per metric, not strict [0,100] bound on individual values. Outlier rate <0.15% across all percentage metrics is acceptable. Apply scripts that compute or consume Census rates must adopt this tolerant pattern.

Consequences: Strict per-row bounds are explicitly rejected as the validation approach for confidentialised metrics. Cohort-level invariants are the standard.

---

## DEC-60 — Female LFP rate at SA2: TSP-derived
Status: Active
Date: 2026-04-27b

Context: Female LFP rate at SA2 is not published in ABS Data by Region. Derivation from Census 2021 TSP T33A-H counts is required.

Decision: `LFP_F = F_Tot_Tot_labo_for / (F_Tot_Tot_labo_for + F_Tot_Not_LF)`. Note: TSP table numbering shifted between 2016 and 2021. T07 in 2021 TSP is "Number of Children Born by Age of Person" (fertility), not labour force. Labour force is T33 in 2021 TSP, split A–H by sex × age range. On Census 2026 release, re-verify table numbering before re-ingest.

Consequences: Sex-disaggregated LFP comes from T33-derived counts. Persons LFP comes from Data by Region. See DEC-61 for cross-product reconciliation policy.

---

## DEC-61 — Cross-product Census rates: do not reconcile or sum
Status: Active
Date: 2026-04-27b

Context: EE DB column 55 (`ee_lfp_persons_pct`) vs T33-derived persons LFP show median absolute difference of 3.57 pp, mean 4.36 pp. Both products are correctly published by ABS. Difference is methodological (Data by Region uses ERP-based 15+ population as denominator; TSP uses raw Census person count). National aggregates from both match published rates within 0.3 pp.

Decision:
- Persons LFP: use `ee_lfp_persons_pct` (canonical, the product underwriters compare against)
- Sex-disaggregated LFP: use `census_lfp_females_pct` and `census_lfp_males_pct` (T33-derived)
- Do not attempt to reconcile or sum F+M to P
- Layer 4 commentary footnote: "Sex-disaggregated LFP from Census 2021 TSP; persons LFP from Data by Region. Methodologies differ; rates not directly summable."

Consequences: Reconciliation deferred to P2. Page surfaces avoid the appearance of rigour where the data does not support it.

---

## DEC-62 — audit_log canonical schema
Status: Active
Date: 2026-04-27c
Supersedes: DEC-26

Context: The audit_log schema needed a single canonical reference. DEC-26 captured the NOT NULL contract; DEC-62 captures the complete schema and INSERT pattern.

Decision: Canonical schema:
```
audit_id     INTEGER PK autoincrement
actor        TEXT NOT NULL  — script name (e.g. 'layer2_step1b_apply')
action       TEXT NOT NULL  — '<source>_<verb>_v1' (e.g. 'sa2_polygon_backfill_v1')
subject_type TEXT NOT NULL  — table name being mutated
subject_id   INTEGER NOT NULL — 0 for whole-table mutations, otherwise PK of mutated row
before_json  TEXT  — {"rows": N, "payload": {...}}
after_json   TEXT  — {"rows": N, "payload": {...}}
reason       TEXT  — human-readable description
occurred_at  TEXT  default datetime('now')
```
Apply scripts INSERT mirroring this exact column set (STD-30). All ingest actions follow the `<source>_<verb>_v1` naming convention. `before_json` captures pre-state metrics (often `{"rows": 0}` for new tables); `after_json` captures post-state metrics with a "payload" dict of run-specific detail.

Consequences: Codified in STD-30. Generic discovery at runtime is prohibited.

---

## DEC-63 — services SA2-coverage residuals post-Step-1b
Status: Active
Date: 2026-04-27c

Context: After Step 1b (lat/lng polygon backfill), 20 services remain with NULL `sa2_code`.

Decision:
- 18 services have no lat/lng (unrecoverable via polygon lookup; fix requires per-service address geocoding or manual lookup; deferred to post-V1)
- 2 services have lat=0, lng=0 (null-island; clearly bad data; cleanup task — manual review or correction; small enough to triage in one sitting)

Net coverage 18,203 / 18,223 = 99.89% is acceptable for V1. Layer 3 banding excludes rows with NULL `sa2_code` from cohort calculations.

Consequences: Open items tracked in `OPEN_ITEMS.md`. No imputation; honest absence is preferred.

Further note (2026-04-28b): Step 1c overwrite added 43 services unchanged due to lat/lng (0,0). 25 of those overlap with the 18+2 tracked here; ~20 are new candidates for geocoding fix.

---

## DEC-64 — ABS Births workbook layout
Status: Active
Date: 2026-04-27c

Context: ABS Births workbook (Cat 3301.0 table 2) uses a per-state-split layout — Tables 1–8 covering NSW/VIC/QLD/SA/WA/TAS/NT/ACT separately. Each sheet has tri-metric-per-year layout: ERP | Births | TFR repeated for each year.

Decision: Detection MUST match Births sub-header text in row 6; must NOT use year-column offset. Apply must iterate all 8 state sheets to assemble the national dataset. National-sum sanity check is national-level, not per-state.

Consequences: Codified in STD-26. Per-state national-sum sanity check is incorrect (state births ≪ national births by ~30×).

---

## DEC-65 — Layer 3 schema and RWCI weighting: precedent survey first
Status: Active
Date: 2026-04-27c

Context: Layer 3 schema and RWCI weighting decisions risked redesigning conventions already shipped on the Industry, Catchment, Operator, and Centre v1 tabs.

Decision: Layer 3 schema and RWCI weighting decisions deferred pending precedent survey. Pre-work for Layer 3 (before any apply scripting):
- Survey existing pages for shipped percentile / banding / cohort conventions
- Document findings in `recon/layer3_precedent_survey.md`
- Make explicit decisions on: (a) table shape — wide vs long, (b) RWCI weighting — equal-weight z-scored / hand-calibrated / principal-component / other, (c) cohort definitions for each metric — state, remoteness band, state-x-remoteness, national
- Project lead approves before code is written

This is non-negotiable for Layer 3 even though it adds 0.5 sessions of pre-work; without it, banding choices made in isolation will likely conflict with conventions on shipped pages, forcing rework.

Consequences: Established the **Decision-65 pattern** — probe → design doc → decisions closed → code — as the project's standard approach for non-trivial work. Promoted to a principle in `PRINCIPLES.md`. RWCI composite deferred to P2 (Layer 3b); banding choices in Layer 3 follow shipped UI conventions (DEC-67 confirms).

---

## DEC-66 — sa2_cohort assignment via centroid-in-RA-polygon spatial join
Status: Active
Date: 2026-04-28

Context: SA2 → Remoteness Area mapping needed a defensible source. Five candidate sources were probed; four had fatal coverage gaps.

Decision: SA2 → RA computed via SA2 centroid → RA polygon spatial join (predicate=`within` in EPSG:3577, with intersect-fallback for centroid-on-boundary cases). Source: ABS Remoteness Areas GeoPackage.

Rejected alternatives:
- (a) services-derived (most-common `aria_plus` per SA2): only 1,422 of 2,454 SA2s covered. Fatal coverage gap.
- (b) `meshblock-correspondence-file-asgs-edn3.xlsx` already on disk: actually QLD-only (STD-29).
- (c) Census TSP zip: structure lists only, no SA2→RA mapping.
- (d) Population/Income Database table 3: aggregated AT remoteness level, not SA2-level lookup.

Cross-validation vs `services.aria_plus` produces 89.3% match rate; mismatches are diffuse boundary-straddle cases, not systematic. Treated as acceptable for V1 — services-level ARIA+ is correct for centre-point display, `sa2_cohort` is correct for SA2-level peer cohort.

Consequences: `sa2_cohort` table built with full coverage. Layer 3 banding uses `state_x_remoteness` cohort definition routinely.

---

## DEC-67 — Banding cutoffs locked: 1-3 / 4-6 / 7-10
Status: Active
Date: 2026-04-28

Context: Layer 3 banding cutoffs needed to honour shipped operator/catchment SEIFA UI conventions (DEC-65).

Decision: `decile 1-3 → band='low'`; `decile 4-6 → band='mid'`; `decile 7-10 → band='high'`.

Source: shipped operator/catchment SEIFA UI uses `wd <= 3.5` for 'low-SES catchment mix' and `wd <= 6.5` for 'mid-SES'. With discrete deciles, this maps to 1–3 / 4–6 / 7–10 (3 / 3 / 4 split). `module2b_catchment.py fee_sensitivity_label(irsd_decile, ccs_rate)` uses an identical 3 / 3 / 4 cut, confirming the convention.

Consequences: All 10 banded metrics use this cut. Per-metric distribution validated: all metrics are 30/30/40 ±0.5 pp (decile partitioning math working as intended).

---

## DEC-68 — Layer 3 latest-year-only banding
Status: Active
Date: 2026-04-28

Context: Per-year banding history would 10× the cardinality of `layer3_sa2_metric_banding` (~400K rows vs ~40K) without adding V1 capability.

Decision: For each metric, `layer3_sa2_metric_banding` stores ONE banding row per SA2 — for the latest year/period that has adequate coverage (≥500 SA2s populated; floor configurable). Trajectory cards on centre/operator pages read raw values directly from source tables (`abs_sa2_*`) at Layer 4 render time; Layer 3 does NOT store per-year banding history. Rationale: ~10× cardinality reduction without losing any V1 capability. Re-running `layer3_apply.py` after a source refresh is the "refresh" pattern.

Consequences: Layer 3 row count is ~24K. Layer 4 trajectory queries hit source tables directly. Re-banding on source refresh is a one-command operation.

---

## DEC-69 — Cohort scope visibility on the centre page
Status: Active
Date: 2026-04-28b

Context: Reviewers reported the cohort comparison was not visible enough at row level on the centre page.

Decision: Cohort scope appears inline in the metric title in brackets, not just in the headline. Format: "Under-5 population (vs WA)" or "Total population (vs Major Cities Qld)". The bracketed short-form is built from `cohort_def + sa2_cohort` row by `_buildCohortShortLabel(p)` JS helper. Long-form phrase ("vs other Outer Regional SA2s in WA") is preserved in the DER tooltip's Rule field. Headline collapses to "Decile X · band · n=N".

Consequences: Cohort scope is visible at every row without redundancy. Long-form context is one click away.

---

## DEC-70 — SA2 polygon overwrite supersedes postcode-derived sa2_code
Status: Active
Date: 2026-04-28b
Supersedes: DEC-42 (caveat portion)

Context: Step 1's 1:1 postcode→SA2 concordance was systematically wrong for postcodes spanning multiple SA2s — the publisher chose arbitrarily, sometimes including cross-state assignments. Step 1b only filled NULLs (887 services). Cross-state mismatch probe found ~1,435 active services where `services.state` disagreed with their assigned SA2's state. Step 1c re-derived `sa2_code` AND `sa2_name` for every active service with lat/lng (~17,880) via point-in-polygon spatial join against `ASGS_2021_Main_Structure_GDA2020.gpkg`.

Decision: SA2 polygon overwrite (Step 1c) supersedes postcode-derived `sa2_code` for any active service with lat/lng. Postcode-derived `sa2_code` is retained as fallback only for services without lat/lng (~340 services). Cross-state mismatches dropped from 1,435 to 9 (acceptable residual — boundary enclaves like Jervis Bay).

Consequences: Step 1's postcode concordance is no longer trusted as primary source. Step 1b's lat/lng polygon was correct methodology but only applied to NULL rows. Supersedes DEC-42's "approximate concordance" caveat — postcode concordance is now relegated to fallback-only.

---

## DEC-71 — Two-design-system architecture, formalised
Status: Active
Date: 2026-04-28b

Context: Visual consistency audit (`recon/visual_consistency_audit.md`) identified that two parallel visual systems coexist in the repo. The audit presented three options: (1) Chart.js on `centre.html` for trends only, (2) whole-repo migration to one system, (3) keep bespoke, restyle to match Chart.js.

Decision: The repo runs two parallel visual systems — System A (centre/operator/review with Palette A and bespoke SVG) and System B (dashboard/index with Palette B and Chart.js 4.4.0). `centre.html` bridges the two: imports Chart.js for trend rendering only; decile strips, cohort histograms, chip strips, decision strips remain bespoke SVG.

Boundary rule: trends use Chart.js; position indicators use SVG. Stroke colour per metric matches `index.html chart-catch-combined` convention. Stroke colour does NOT carry valence — direction of "good vs concerning" lives only in band-copy text per DEC-72 and STD-34.

Whole-repo migration to one system rejected (Option 2): doesn't pay back; the systems serve different purposes (drilldown detail vs trend intelligence). Bespoke-only rejected (Option 3): commercial framing strengthens the case for standard-library charts.

Consequences: Architecture-level visual decision is locked. Documented in `ARCHITECTURE.md`.

---

## DEC-72 — Supply-ratio direction working convention
Status: Superseded by DEC-74
Date: 2026-04-28b

Context: From the credit-lens user perspective, the same data has opposite framing depending on which ratio is shown.

Decision (original):
- `supply_ratio` (places/child) — `high_is_concerning`. Low band copy: "undersupplied catchment — opportunity"; mid: "balanced supply"; high: "saturated catchment — competition risk".
- `child_to_place` (children/place) — `high_is_positive`.
- `demand_supply` (adjusted_demand/places) — `high_is_positive`.

Already shipped on `index.html` as a hover note ("A rising supply ratio indicates increasing competition pressure, not opportunity") — extended this session to `centre.html` and locked as a project-wide convention.

Consequences: DEC-72 set the per-metric direction conventions. DEC-74 supersedes DEC-72 by promoting these conventions into the perspective-toggle pattern: the band-copy templates and direction markers locked here become the two states of a per-row toggle on the centre page. The original conventions remain valid as the *forward* default of each pair; DEC-74 adds the *reverse* lens for the two reversible pairs.

---

## DEC-73 — Trajectory window UX for centre page
Status: Active
Date: 2026-04-28b

Context: Reviewers wanted a similar group of buttons to the index/industry page that allows changing the time scale on trajectory charts.

Decision: Global "Trend Window" button strip at top of Population card, options 3Y / 5Y / 10Y / All. Default = All. Window applied per-metric relative to that series' most recent point (so the same "5Y" click means different absolute date ranges for unemployment vs LFP — honest given mixed-cadence data). Pattern lifted from `index.html #time-range-btns / setRange(n, el)`. Per-chart override buttons for unemployment (1Y/2Y) are Layer 4.3 scope.

Consequences: Trajectory window UX is consistent between centre and industry surfaces. Per-chart overrides for short-data series are a Layer 4.3 deliverable.

---

## DEC-74 — Perspective toggle on reversible ratio pairs
Status: Active
Date: 2026-04-29
Supersedes: DEC-72 (promotes its per-metric conventions into the toggle pattern)

Context: The four catchment ratios in Layer 4.3 split into two interpretive pairs. The same data tells different stories depending on which direction the ratio is read. `supply_ratio` (places/child) frames *competition*; `child_to_place` (children/place) frames *demand-headroom*. `demand_supply` (adjusted_demand/places) frames *fill expectation*; its inverse frames *spare capacity*. Closes G1+G2 of `recon/layer4_3_design.md`.

Decision: Reversibility is a per-metric property surfaced via a per-row "perspective" toggle on the centre page. Two of the four catchment ratios are reversible:

- Supply intensity pair: `supply_ratio` ↔ `child_to_place`
- Demand absorption pair: `demand_supply` ↔ `demand_supply_inv` (1 / demand_supply)

`adjusted_demand` and `capture_rate` are absolute estimates over capacity, not ratios with a meaningful inverse. They do not carry a toggle.

Toggle behaviour: swaps which ratio renders as primary; swaps the band-copy template (`high_is_concerning` ↔ `high_is_positive`); swaps the inline intent-copy line below the title; *preserves* the underlying decile — the SA2's position does not change, only the framing changes.

Default: credit lens — `supply_ratio` forward (competition), `demand_supply` forward (fill expectation).

Band copy (locked):

| Metric | Direction | Low | Mid | High |
|---|---|---|---|---|
| `supply_ratio` | high_is_concerning | undersupplied — opportunity | balanced supply | saturated — competition risk |
| `child_to_place` | high_is_positive | thin demand per place | balanced demand per place | strong demand per place |
| `demand_supply` | high_is_positive | soft catchment — fill risk | in balance | demand pull — strong fill expected |
| `demand_supply_inv` | high_is_concerning | tight capacity vs demand | balance | abundant spare capacity |

Implementation: four new fields on each Layer 4 catchment metric in the metric registry — `reversible: bool`, `pair_with: str`, `default_perspective: str`, `perspective_labels: tuple`. Render switch in `centre.html`.

Consequences: Generalises ratio reversibility as a first-class property of metrics, applicable beyond the four catchment ratios to any future ratio metric with a meaningful inverse. The DEC-72 forward conventions are preserved as the default state of each toggle; the reverse state is now also a defensible render. Effort: ~0.3 session, additive within Layer 4.3 scope.

---

## DEC-75 — Visual weight by data depth (Full / Lite / Context-only)
Status: Active
Date: 2026-04-29

Context: The current centre-page Position-row template (trajectory + cohort histogram + decile strip + band chips) was applied uniformly to all 10 metrics. Several metrics don't have the data depth or geographic resolution to justify the full treatment. The LFP triplet has only 3 Census points; `jsa_vacancy_rate` is state-level with no SA2 peer cohort. Forcing them into the full template implies analytical depth that isn't there, breaking P-2 (honest absence over imputed presence). Closes G5 of `recon/layer4_3_design.md`.

Decision: Three row weights for centre-page metrics, assigned per-metric based on data depth and resolution:

| Weight | Components | When to use |
|---|---|---|
| **Full** | Trajectory chart + cohort histogram + gradient decile strip + band chips + inline intent copy | SA2 peer cohort exists AND ≥5 dense time-series points |
| **Lite** | Gradient decile strip + band chips + inline intent copy + "as at YYYY" stamp | SA2 peer cohort exists but <5 series points |
| **Context-only** | Single-fact line + inline intent copy (optional state-level sparkline) | No SA2 peer cohort (state/national data) |

Reclassifications applied to currently-rendered Position metrics:

- `sa2_lfp_persons`, `sa2_lfp_females`, `sa2_lfp_males` → **Lite** (3 Census points is not a trajectory)
- `jsa_vacancy_rate` → **Context-only** (state-level; moves to Workforce supply context block per DEC-76)
- All 7 other Position metrics → **Full** (unchanged)

Implementation: `row_weight: "full" | "lite" | "context"` field on each metric in the Layer 4 metric registry. `centre.html renderPositionRow` switches on the field.

Consequences: Visual treatment now matches analytical depth. Honest absence is applied at the visual layer, not just in copy. Refines DEC-32: the three-temporal-mood pattern still applies but with per-metric weighting in how each mood is rendered. Effort: ~0.2 session, additive to Layer 4.3 since intent copy already touches every row.

---

## DEC-76 — Workforce supply context block on the centre page
Status: Active
Date: 2026-04-29

Context: Educator and ECT workforce supply is a top-tier credit signal. The data is published by JSA at state level (Internet Vacancy Index for ANZSCO 4211 child carers and 2411 early childhood teachers). State-level data has no SA2 peer cohort, so it cannot render as a Position row with banding. But suppressing it from the centre page would soft-pedal a critical credit signal. Opens Thread D of `recon/layer4_3_design.md`.

Decision: Add a new Position-level block on the centre page — "Workforce supply context" — alongside Population and Labour Market cards. **Default open** (the credit-lens user should see workforce constraint at first read; collapsing it would soft-pedal the signal). Holds Context-only metrics per DEC-75 where the data is state-level.

V1 rows:

| Row | Source | Resolution | Render |
|---|---|---|---|
| Child Carer vacancy index (ANZSCO 4211) | JSA IVI Step 5c | State, monthly | Latest + state-level sparkline |
| ECT vacancy index (ANZSCO 2411) | JSA IVI Step 5c | State, monthly | Latest + state-level sparkline |
| ECEC Award minimum rates (Cert III, Diploma, ECT) | Fair Work Award data | National | Fact + annual update |
| Three-Day Guarantee policy effective Jan 2026 | Policy fact | National | Single-line |

Each row carries an explicit "state-level — no SA2 peer cohort" stamp (or "national" for Award/policy rows). Inline intent copy is one sentence per row. No band, no decile strip, no cohort histogram.

State-level sparklines render here because the trend in vacancy intensity is meaningful even where SA2 peer comparison is missing. What's absent is the peer band, not the trend.

Consequences: Workforce supply is visible on the centre page without faking SA2 resolution it doesn't have. The block becomes the canonical home for any future state/national Context-only metric. `jsa_vacancy_rate` moves here from its Position-deferred slot. V1.5 enrichments (direct SEEK-by-SA2 scrape, NCVER VET enrolments at SA2/remoteness, advertised-wage data) tracked as OI-20. Refines DEC-23 / DEC-36: state-level supply data is now admissible on the centre page in Context-only weight where it informs centre-specific staffing risk; the framing remains "this is state-level information bearing on your centre", consistent with P-7.
