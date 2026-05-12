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
Amended: 2026-04-29 (continued) — added the dependency-ordered sequencing pass to the closure protocol; see "Amendment 2026-04-29" below.

Context: Layer 3 schema and RWCI weighting decisions risked redesigning conventions already shipped on the Industry, Catchment, Operator, and Centre v1 tabs.

Decision: Layer 3 schema and RWCI weighting decisions deferred pending precedent survey. Pre-work for Layer 3 (before any apply scripting):
- Survey existing pages for shipped percentile / banding / cohort conventions
- Document findings in `recon/layer3_precedent_survey.md`
- Make explicit decisions on: (a) table shape — wide vs long, (b) RWCI weighting — equal-weight z-scored / hand-calibrated / principal-component / other, (c) cohort definitions for each metric — state, remoteness band, state-x-remoteness, national
- Project lead approves before code is written

This is non-negotiable for Layer 3 even though it adds 0.5 sessions of pre-work; without it, banding choices made in isolation will likely conflict with conventions on shipped pages, forcing rework.

Consequences: Established the **Decision-65 pattern** — probe → design doc → decisions closed → code — as the project's standard approach for non-trivial work. Promoted to a principle in `PRINCIPLES.md`. RWCI composite deferred to P2 (Layer 3b); banding choices in Layer 3 follow shipped UI conventions (DEC-67 confirms).

### Amendment 2026-04-29 — sequencing pass at design closure

The Layer 4.3 design-closure session (2026-04-29) closed nine sub-passes but did not check whether their default ordering (roughly chronological with the design conversation) was dependency-optimised. The 2026-04-29 (continued) implementation session caught the gap when Patrick asked what came next — a renderer-only run could have shipped before any data-plumbing sub-pass, surfacing best-practice rendering ~2.3 sessions earlier and eliminating retrofit risk on downstream layers (Layer 4.2-A catchment ratios + the parallel daily-rate integration). See OI-24.

Closure protocol amended: a sub-pass dependency-ordering pass is now part of design closure, alongside the per-decision closures. The pass asks, for each sub-pass:

1. What does this depend on (data, schema, decisions, prior renderer state)?
2. Does anything downstream depend on this happening *before* something else, or only on it happening eventually?
3. If multiple sub-passes have no mutual dependency, which delivers visible value soonest? Which sets up the most downstream work without retrofit?

Output of the sequencing pass: an explicit ordering in `ROADMAP.md` with a one-line rationale per sub-pass position. Default-chronological-from-design-conversation is rejected as a sequencing strategy because it has no dependency basis.

Applies retroactively to any open multi-sub-pass plan: if sub-passes have not had a sequencing pass, run one before starting the next sub-pass. Layer 4.3 itself has been re-sequenced (ROADMAP §1.3) under this amendment.

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


---

## DEC-77 — Industry-absolute threshold framework for catchment ratios
Status: Active
Date: 2026-05-03

Context: Layer 4.2-A.3b shipped (2026-04-30) an industry-absolute band line beneath the per-cohort decile chips for the three catchment ratio metrics with meaningful industry-grounded thresholds. The framework had been operating in production for 3 days. The 2026-05-03 evening v20 polish round reframed the demand-supply band labels in supply-vs-demand language only after operator review caught that the original "below break-even" labels asserted a profitability conclusion the demand/supply ratio alone cannot support (break-even depends on price, cost base, ramp curve, mix). The framework is now operator-validated; locking the design.

Decision: Three catchment metrics opt in to industry-absolute banding via `industry_thresholds: True` on their `LAYER3_METRIC_META` entry. Bands derived from three locked sources:

- **`sa2_supply_ratio`** — 7 levels. Productivity Commission universal-access target (1.0 places/child = all children, three days/week) anchors the upper bound. Low/mid/high tiers grounded in the absolute supply landscape (desert / undersupplied / below_bench / at_bench / well_served / at_target / saturated).
- **`sa2_child_to_place`** — 5 levels (excess_capacity / balanced / tight / constrained / severe). Derived from Remara Strategic Insights v4.2 real distribution by SES + remoteness.
- **`sa2_demand_supply`** — 4 levels. Thresholds (0.40 / 0.55 / 0.85) inherit Credit Committee Brief break-even (70%) + target (85%) occupancy maths. **Labels reframed in supply-vs-demand language only — break-even is a profitability conclusion the ratio alone cannot support, and the label must not assert it.** v20 final labels: "supply heavy" / "supply leaning" / "approaching balance" / "demand leading" with parallel-framed notes.

`sa2_adjusted_demand` is intentionally NOT banded (decile-only) because it is a count not a ratio.

Renderer: `_renderIndustryBand` reads `p.industry_band` (band key, drives cautionary/positive pill colour via `cautionKeys` / `positiveKeys`), `p.industry_band_label` (visible text inside the pill), `p.industry_band_note` (descriptor next to the pill). Silent absence per P-2 when metric not opted in or raw_value is null. Band keys are stable identifiers — relabel the visible text without changing the key, otherwise the pill colour treatment breaks.

Consequences: Industry-absolute bands now operate as a first-class lens on top of the per-cohort decile lens. Future ratio metrics can opt in by adding to `INDUSTRY_BAND_THRESHOLDS` and setting `industry_thresholds: True`. Any future label work must respect the supply-vs-demand discipline established by v20: visible labels describe what the ratio measures, not what it implies for downstream financials. OI-26 (post-launch review of demand_supply thresholds in saturated catchments) remains active under this DEC.

---

## DEC-78 — Census percentage storage convention (long-format value column)
Status: Active
Date: 2026-05-04 (banked); promoted to Active 2026-05-10 (A10 ingest)

Context: Banked 2026-05-04 during the A2 NES v2→v3 unit fix, when `census_nes_share_pct` was discovered to be stored as a fraction (0–1) inconsistent with the existing `census_lfp_*_pct` family stored as percentage (0–100). v3 normalised storage to 0–100. The 2026-05-10 A10 Demographic Mix ingest (ATSI + overseas-born + single-parent family share) shipped three additional Census-derived `_pct` metrics through the same storage path, making the convention load-bearing across multiple ingests rather than a one-off NES handling.

Decision: All Census-derived percentage metrics in `abs_sa2_education_employment_annual.value` are stored as **percentage (0–100)**, not fraction (0–1). Naming convention: `census_<topic>_share_pct` for share metrics, `census_<topic>_pct` for proportion metrics. Where calibration consumes the value (currently NES via `calibrate_participation_rate`'s fraction thresholds), the wire layer (`populate_service_catchment_cache.py` for NES) divides by 100 at read time. The long-format target table is the canonical sink; new top-N or list-shaped data goes to dedicated tables instead (see DEC-80).

Consequences: Banding registry (`layer3_apply.py` METRICS list), centre-page registration (`LAYER3_METRIC_META[*].value_format = "percent"`), and renderer all assume 0–100 for `_pct` metrics. Any future Census-derived metric joining this table must follow this convention — ingest converts to percentage explicitly with a unit-test sanity bound (e.g., national weighted total within ABS-published ±2pp band), and `value_format` registration aligns with `percent` rather than `percent_share` (which is reserved for already-fraction inputs from elsewhere).

---

## DEC-84 — Centre v2 content map: 6-layer page architecture, matrix as center of gravity
Status: Active
Date: 2026-05-12 (locked at joint design pass close; supersedes V1 cards-stack page architecture for `/centres/{id}` once v2 build verifies)
Supersedes: DEC-71 (visual layer architecture remains; this layers the page on top)

Context: The centre page evolved from a credit-decision-tool layout (5 cards stacked vertically, 32 metrics across them) into a surface that absorbs an increasing breadth of institutional signals — V1.5 demographic-mix sub-panel grew the Catchment Position card from 9 → 13 rows on its own; A4 added a 6th top-level concept (Education Infrastructure); DEC-83 Commercial Layer V1 brought operator-group identity, daily-rate per (age × session) grid, regulatory state, conditions, vacancies, and enforcement events that have no clean home in the existing card structure. The original V1 layout pre-dated these breadths. Patrick's framing 2026-05-10: "the original design didn't contemplate such breadth and scale of information." The v2 redesign initiative was scoped against three reading speeds (30-sec executive view, 2-min trends view, 5-10-min comprehensive scan) with a fourth depth tier (drill-detail). Six-layer skeleton + locked decisions on detail-drawer / sparklines / histograms / measurement-tools / cut-order / old-page-preservation captured in `project_centre_v2_redesign.md` 2026-05-10 PM s3. Daily-rate substrate ingested 2026-05-11 via DEC-83 unblocked the joint design pass. Probe-first per DEC-65: surface inventory of v3.31 (32 metrics × 5 cards × 14 helpers) + DEC-83 new substrate compiled 2026-05-12 in `recon/centre_v2_design.md`. 12 decisions ratified by Patrick as a batch.

Decision:

1. **Page architecture: cards dissolve, matrix becomes center of gravity.** The v1 stack of 5 vertical cards (Catchment Position / Population / Education Infrastructure / Labour Market / Workforce Supply Context) is replaced by a 6-layer architecture: Layer 1 Header / Layer 2 Executive interpretation / Layer 3 Primary historical trends / Layer 4 Secondary historical trends accordion / Layer 5 Institutional signal matrix / Layer 6 Detail side-drawer. Every existing metric appears once in the matrix; if also charted, it appears in Layer 3 (primary, ~7 charts) or Layer 4 (secondary accordion). This is the load-bearing structural call — every layer-mechanic decision below assumes it.

2. **Layer 2 Executive interpretation: 5 signal tiles + 0-2 flags.** Signal tiles cover Demand / Supply / Workforce / Quality / Community — institutional decision frame. Each is a 1-line summary tile, click-through to relevant Layer 5 matrix section. Headline above tiles is rule-based composition from band keys: `[supply band] · [demand band] · [demographic flavour] · [quality posture]`; not free-form prose. Flag bar below shows max 2 flags with severity hierarchy: RED for `ccs_revoked_by_ea = 1`, `is_closed = 1`, `temporarily_closed = 1`; AMBER for active conditions (`service_condition.still_active = 1`), sub-Meeting NQS (`Working Towards / Significant Improvement Required / Provisional`), recent enforcement events (within 24 months); INFORMATIONAL for `no_vacancies_published`. Operator-group affiliation is NOT a flag (it's a Layer 1 chip). If >2 flags trigger, surface 2 highest-severity + a "+N more" pill that opens Layer 5 matrix Quality/Operations sections. Avoids flag soup.

3. **Layer 3 Primary historical trends: 7 charts.** (1) Supply ratio quarterly per subtype, (2) Demand vs supply parallel framing, (3) Adjusted demand half-pair, (4) Children-per-place half-pair, (5) Under-5 population + births overlay annual, (6) Female LFP + unemployment dual-axis (third overlay slot reserved for JSA IVI 4211 when wired), (7) Daily-rate full_day × 36m-preschool with peer-cohort overlay (NEW DEC-83). Existing window control (`_renderTrajectoryRangeBar`) stays at top of Layer 3. Chart heights cut from ~280px to ~180px and histogram below cut from ~140px to ~80px with decile strip + band chips inline rather than stacked — saves ~420px vertical reclaim across the 7 charts. The headline daily-rate pair = full_day × 36m-preschool because prep-year-equivalent fee is the most-asked institutional comp; OSHC services discriminate at render time and see before/after_school × school-age headline rows instead.

4. **Layer 4 Secondary historical trends: single accordion section, default-collapsed.** Five chart groups inside: Population context (total pop, parent-cohort, partnered) / Income context (employee income, total income, household income) / Workforce context (total LFP, male LFP, JSA vacancy when wired) / Demographic trend (NES, ATSI, OS-born, single-parent, women-with-child cohorts) / Education infrastructure (school count, total enrolment, govt-share). When expanded: 2-column half-width chart pairs, ~120-150px tall, 30px inline histogram. The 5 banked ACARA sector breakdowns from A4 don't get Layer 4 charts — Layer 5 matrix only.

5. **Layer 5 Institutional signal matrix: ~52 rows V1, 9 categories.** Row columns: Category tag (80px) / Metric name + OBS-DER-COM badges (flex) / Current value + period (100px) / Sparkline 24px (120px) / Decile strip + cohort_n (80px) / Signal band chip (120px) / Commentary intent_copy short (flex) / Drawer trigger `›` (32px). Categories in display order: Demand / Supply / Pricing & Fees (NEW) / Quality (NEW NQS+conditions+enforcement+CCS+area-breakdown+last-visit) / Workforce (4 deferred stubs pending V1.5 A6+A7 + B1) / Community / Education / Operator/Group identity (NEW) / Operations (NEW hours+status+CCS-data-received+vacancy posture) / Population / Labour Market. Total ~52 rows including ~9 "Pending V1.5" status-pill stubs. Sorting V1 = fixed display order matching POSITION_CARD_ORDER + new entries appended per category; signal-strength sort is V2 measurement-tools class.

6. **Layer 6 Detail side-drawer: slide-in from right, click-anywhere row + ESC + URL fragment shareable.** Single drawer at a time (opening a second replaces the first). Drawer template per metric: current value / why it matters (full intent_copy) / how it's computed (full about_data) / peer cohort (full histogram + decile + band chips + industry band rule_text + calibration rule_text) / trajectory chart / commentary band copy / V1.5 or V2 banked notes. Special drawer types for daily-rate (full age×session grid + fee_type + inclusions), conditions (full text per condition + first/last observed + level), enforcement events (chronological log), operator-group (chain name + provider list + service rollup), NQS (rating ladder + 7-area + history + last visit), top-N COB+language (full top-10 + methodology), vacancy (age-band breakdown + longitudinal + sentinel methodology). Existing `_renderAboutData` and `_renderTopNContext` move into drawer; preview text in matrix Commentary column gives 80% of inline value at 0% extra column width.

7. **Layer 1 Header refinements (existing surface preserved + 3 DEC-83 enrichments).** Existing: title + provider + identity row + subtype + ARIA+. New: operator-group chip (only when `services.large_provider_id IS NOT NULL` — sources `large_provider.name`); operating hours summary single-line ("Mon–Fri 7:00am–6:00pm" derived from latest snapshot's 14 hour cols); contact strip below identity row (website link / phone / email from `service_regulatory_snapshot.website_url|phone|email`). No metrics, no charts, no flags in Layer 1 — all status communication moves to Layer 2.

8. **Workforce Supply Context card dissolves.** v1's standalone Workforce Supply card (4 deferred rows: jsa_ivi_4211_child_carer, jsa_ivi_2411_ect, ecec_award_rates, three_day_guarantee) is absorbed: JSA IVI rows become Layer 5 Workforce matrix rows + Layer 3 chart 6 third overlay when wired (V1.5 A7); ECEC Award + Three-Day-Guarantee become Layer 5 Workforce fact rows (matrix-format-tolerable: n/a sparkline, value = current rate, period = "as at Jan 2026"). DEC-76's intent (workforce supply context block) survives via Layer 2 Workforce signal + Layer 5 category. The standalone-card pattern goes away. `_renderWfsRangeBar` retires; functionality absorbs into Layer 3 chart 6 page-level range bar.

9. **Daily-rate matrix density: 5 rows in Pricing & Fees + full grid in drawer.** Layer 5 Pricing rows = full_day × {0-12m, 13-24m, 25-35m, 36m-preschool, school-age} with median + decile vs catchment peer cohort. Half-day / hourly / before/after-school sparse data (~26% of pilot fees) lives in Layer 6 daily-rate drawer detail with full age×session grid + fee_type + inclusions. OSHC services swap headline rows to before_school + after_school × school-age. FDC follows LDC convention; Preschool follows LDC with `36m-preschool` only.

10. **V1.5 pending-ingest treatment: render row stubs with status pill.** Layer 5 matrix rows for V1.5-pending metrics (A5 subtype-correct denominators, A6 SALM extension, B1 `sa2_jsa_vacancy_rate` banding, A7 SEEK, etc.) render with "Pending V1.5 A5" / "Pending V1.5 A6" status pill instead of value/sparkline/decile. Same P-2 honest absence as v1's deferred workforce rows, but matrix-row-format. Keeps the layer plan stable as ingests land; users see what's coming.

11. **Histogram + decile sizing: 80px chart histograms / 24px matrix sparklines (locked).** Layer 3 charts get 80px-tall histograms below (cut from ~140px) with decile strip + band chips inline rather than stacked. Layer 5 matrix rows get 24px-tall inline sparklines (last-N data points, no axes) — visual minimum that still reads as a trend. Layer 6 drawer charts and histograms render at full v1 sizes for depth view.

12. **Excel export shape lock-in: Layer 5 matrix structure as primary export source.** Matrix payload exports as one row per metric with all 8 columns flattened (category / name / value / period / decile / cohort_n / signal / commentary). Layer 6 drawer detail becomes additional sheets per-metric or a single methodology sheet keyed by metric name. Doesn't bind us; just confirms the matrix shape is export-ready ahead of the Excel framework DEC-candidate (per ROADMAP §2.4). Excel framework sheet structure ratifies later.

Consequences:

- DEC-84 establishes the **Centre v2 page-architecture pattern** for `/centres/{id}`. The matrix-as-center-of-gravity framing carries forward to Catchment page, Group page, and the Child Safety + Competition satellite surfaces (per locked sequencing in `project_centre_v2_redesign.md`); each gets its own design pass but inherits the 6-layer skeleton + drawer interaction model.
- **Total v2 build effort: ~3.9 sess** from this point — within the 6-10 sess band locked in `project_centre_v2_redesign.md`. Breakdown: DEC-84 mint + design doc finalise 0.1 / v1 stake (git tag + bundle dir + ROLLBACK.md) 0.1 / `centre_page.py` v24 payload schema `centre_payload_v7` (new `_build_matrix` + `_build_executive` + `_build_drawer` + flag computation + headline composition) 1.0 / `docs/centre_v2.html` parallel renderer at `/centre_v2/{id}` 2.0 / verification capture 0.3 / smoke test 0.2 / cut-over 0.1 / monolith 0.1.
- **Existing renderer inventory survives unchanged.** `_renderFullRow`, `_renderLiteRow`, `_renderContextRow`, `_renderTrajectory`, `_renderIntentCopy`, `_renderIndustryBand`, `_renderDecileStrip`, `_renderBandChips`, `_renderCohortHistogram`, `_renderLiteDelta`, `_renderTrajectoryRangeBar` all reused. Two new render primitives: `MatrixRow` (compressed Lite-row variant with category column + 24px sparkline) and `DrawerPanel` (slide-in container). One new helper: `_buildExecutiveHeadline(payload)` rule-based composer. `_renderAboutData` and `_renderTopNContext` migrate into drawer rendering. `_renderWfsRangeBar` retires.
- **Old `/centres/{id}` preservation per locked decision:** git tag `centre-v1-stake-YYYY-MM-DD` on the v1 SHA + bundle directory `recon/v1_final_stake_YYYY-MM-DD/` containing `centre.html` v3.31, `centre_page.py` v23, payload-schema notes, and `ROLLBACK.md` recovery recipe. Created BEFORE v2 build starts (`centre_page.py` v24 first edit). v2 takes over `/centres/{id}` once verified; old route doesn't stay live in production. Recovery is `git checkout <tag> -- <files>` — trivial; document in ROLLBACK.md but no need to test live.
- **DEC-83 Commercial Layer V1 substrate fully placed.** Operator-group → Layer 1 chip + Layer 5 Operator/Group row + Layer 6 chain detail drawer. Daily-rate → Layer 3 chart 7 (full_day × 36m-preschool peer overlay) + Layer 5 Pricing 5-row category + Layer 6 full grid drawer. Regulatory snapshot → Layer 1 contact strip + Layer 1 hours summary + Layer 2 flags (CCS revoked, sub-Meeting NQS, closed) + Layer 5 Quality / Operations rows + Layer 6 NQS drawer. Conditions → Layer 2 AMBER flag + Layer 5 Quality count row + Layer 6 conditions drawer. Vacancies → Layer 2 informational flag (no-vacancies-published) + Layer 5 Operations row + Layer 6 vacancy drawer. Enforcement events (`regulatory_events`) → Layer 2 AMBER flag (recent within 24mo) + Layer 5 Quality count row + Layer 6 events drawer.
- **V1.5 ingest queue interaction.** A5 subtype-correct denominators, A6 SALM extension (LFP triplet → Full), B1 `sa2_jsa_vacancy_rate`, A7 SEEK, C2-other, C6 — all retain effort estimates from CENTRE_PAGE_V1_5_ROADMAP but their RENDER landing now defaults to Layer 5 matrix rows (with status-pill stubs in the meantime) rather than v1 card insertion. Reduces post-v2 ingest-render coupling work; ingest writes to existing tables and the matrix renderer surfaces the new metric automatically per registry pattern.
- **Mobile/narrow-screen behaviour V2.** V1 targets desktop institutional use. Below 1024px breakpoint, matrix row columns stack vertically (sparkline + decile strip become single mini-row below metric name). Mobile is V2 polish, not v1 blocker.
- **Drawer interaction is touch-tolerant.** Click-anywhere-on-row + `›` icon + ESC + URL fragment shareable. No hover-preview (avoids touch-screen complications — Patrick uses tablet for review per DEC-32 visual-design heritage).
- **Operator-group identity placement is decisive.** Layer 1 chip (always-visible on chained services), Layer 5 matrix row (with provider count + service count rollup), Layer 6 drawer (full chain detail with provider list and service rollup). NOT in Layer 2 signals — chain affiliation is metadata, not a "signal" per se. Critical substrate for Group page (OI-NEW-17) when that page lands; the Layer 6 drawer's chain detail seeds the Group page deep-link entry point.
- **Child Safety + Competition satellite pages get deep-link "coming soon" stubs in v2.** Layer 5 matrix rows for `service_condition` count, `regulatory_events` count, and competition-relevant aggregates link to satellite-page stubs that say "coming soon" with the substrate-already-ingested message. Maintains intellectual-honesty about scope while flagging where depth lands. Satellite full-page builds happen in their own design passes per locked cut order: Centre v2 → Child Safety → Competition.
- **Effort headroom against the locked 6-10 sess band:** ~3.9 sess for v2 build leaves ~2-6 sess headroom for v1-stake polish + capture-pattern variations + national commercial-layer scale-up if Patrick wants to bundle that into the v2 sequence. Otherwise the headroom is buffer.
- **Cross-references to update:** PROJECT_STATUS.md headline, ROADMAP.md §11 next-session pickup, OPEN_ITEMS.md (no new OIs minted; v2 build scope captured in this DEC), CENTRE_PAGE_V1_5_ROADMAP.md (V1.5 ingest render landing now defaults to v2 Layer 5 matrix), `project_centre_v2_redesign.md` memory (close design pass step; build sequence next), PHASE_LOG.md (this session's entry).
- **What this DEC does NOT decide** (separately tracked): Excel export framework actual sheet structure (separate DEC-candidate); Catchment page layout (cascades from v2 patterns but own design pass); Group page layout (sits above catchment; Stream D PropCo + Stream A workforce dependency at portfolio level); Child Safety + Competition page content (full surfaces, separate scoping passes); brand identity rename pass (OI-NEW-6, independent low-risk); PropCo Stream D / Stream A / Stream E render content (slots reserved in Layer 5; their content is V1-broader work, not this design pass); measurement tools (delta picker, decile-movement readout — V2 of v2); national commercial-layer scale-up (substrate work, not surface); refresh cadence of DEC-83 data (operational concern; v2 surfaces whatever's in `kintell.db` at render time).

**AMENDMENT 2026-05-13 (post-Turns-1-3 visual-iteration ratifications):** During the first three iteration turns on `docs/centre_v2.html` after build kick-off, sixteen sub-decisions surfaced and were ratified by Patrick line-by-line. They refine — they do not overturn — DEC-84's 12 numbered locks. Captured here so the original numbered decisions stay readable and the amendment trail is auditable.

1. **Matrix terminology rename (refines D-1, queue #11 closed).** The "Institutional signal matrix" heading is renamed to **Signal Matrix** in user-facing copy (header h2, intra-page jump labels, and category headings). DEC-84 #1's mechanic call (cards dissolve, matrix becomes center of gravity) is unchanged; only the surfaced label simplifies. Internal payload key (`matrix`) and code identifiers stay. Rationale: "institutional" reads as branding modifier rather than analytical descriptor; the matrix already implies analyst orientation by its content. Confirms `feedback_centre_top_identity.md`'s ambient direction (intelligence subtle, not labelled-as).

2. **Sparkline column retired (reverses D-11 for Layer 5; D-11 still applies to Layer 3 histograms).** The 24px inline sparkline column in Layer 5 matrix rows is removed entirely. DEC-84 #11 specified 24px sparklines as a locked sizing; this amendment reverses that decision for the matrix layer only. Rationale per `feedback_lite_row_density.md`: at 24px height with last-N data points, sparklines registered as visual noise rather than trend signal, especially adjacent to the decile strip + signal band chips which already carry strength encoding. Reclaimed column width (~120px) goes to the Commentary column, widened from `minmax(180px,3fr)` to `minmax(280px,5fr)`. Commentary text length cap widened from ~120 chars to ~240 chars / 2 sentences via `_truncate_sentence`. Layer 3 chart-below-histograms retain 80px sizing per original D-11.

3. **Layer 4 accordion retained (queue #2 de-queued; refines D-4 + queue #14).** Earlier banked direction (queue #14, design-doc post-v0.1 review item) proposed retiring the Layer 4 accordion entirely and folding all secondary charts into inline-expand-from-matrix-row. Patrick reversed at Turn 2: Layer 4 stays. Rationale: (a) the accordion gives a single overview surface for the 5 secondary chart groups when an analyst wants to scan rather than drill from a specific metric; (b) the inline-expand pattern (sub-decision #5 below) co-exists cleanly — Layer 4 accordion = overview by chart group; matrix inline-expand = drill from a specific row. Queue #2 ("Layer 4 accordion removal") is closed as superseded.

4. **Layer 4 acquires its own trend-window selector independent of Layer 3.** DEC-84 #4 implicitly inherited the Layer 3 page-level window control; Turn 2 split them. Layer 4 accordion section gains its own 6M/1Y/2Y/5Y/All selector. Rationale: secondary trends frequently warrant a different temporal lens than primary trends (e.g., reading parent-cohort against under-5 — Layer 3 5y default reads short for cohort context). The two selectors are independent state, not linked.

5. **Inline-row-click expand (queue #1 implemented; refines D-5).** Clicking a Layer 5 matrix row body (anywhere outside the `›` drawer icon) inline-expands a panel below the row containing the metric's trajectory chart + a per-metric local trend-window state (independent of Layer 3 and Layer 4 selectors). Drawer interaction (`›` icon → side panel) is reserved for deep methodology + rich-content drawers (full daily-rate grid, conditions list, school name list, enforcement event log, top-N detail). Trajectory-bearing position metrics get the inline-expand; static-snapshot rows get only the drawer trigger. State variable `_INLINE_RANGE_BY_METRIC` carries per-metric window overrides. Closes queue #1.

6. **Value-in-commentary pattern.** Layer 5 matrix Commentary column gains a leading bold value+period pair (e.g., "**5.8** as at Sep 2024 · sits above the state-level cohort midpoint at this point in the trajectory…") replacing the separate Current Value column-derived treatment that read sparsely after the sparkline column retired. The dedicated Value column persists (compact numeric + as-at stamp), but Commentary now opens with the same value re-stated to anchor the prose. Rationale: the reader's eye runs along the Commentary column; surfacing the value at the start of the sentence reduces scan distance between number and interpretation.

7. **Top-N percentages on demographic-mix rows (queue #9 implemented inline).** Demographic Lite rows in Layer 5 matrix (NES, COB, top languages, ATSI variants) get an inline Top-N context line in the Commentary column showing the top-2 or top-3 contributing categories with their share percentages (e.g., "Top languages: Spanish 2.7% · Mandarin 2.6% · Portuguese 2.5%"). This mirrors centre.html v3.31's inline `_renderTopNContext` treatment that DEC-84 #6 had migrated to the drawer; Turn 3 brings preview text back inline so the reader doesn't need a drawer click for the headline depth. Full top-10 + methodology stays in drawer per DEC-84 #6. Closes queue #9.

8. **Centre-event propagation to population trajectories.** DEC-84 #3 / chart 5 specified centre-events overlay on the 4 catchment metrics (`sa2_supply_ratio` / `sa2_child_to_place` / `sa2_demand_supply` / `sa2_adjusted_demand`). Turn 2 extends the same `centre_events` overlay to the under-5 + births trajectory (chart 5) and to the population/cohort charts in Layer 4. Rationale: centre opens/closes are demand-side context just as much as supply-side; reading a fall in under-5 alongside a centre closure quarter is interpretively richer than reading either alone. The `centre_events` payload is already populated by `_layer3_position` and was simply not wired through to the population renderers.

9. **Edge-event visibility nudge.** When a `centre_events` annotation sits at the very first or last quarter of the visible window, the event-line ticker is nudged ~6px inward so the badge does not get clipped by the chart's axis or container edge. Implementation per centre_v2.html L1629. Rationale: edge events are disproportionately likely to be the most-recent and most-relevant (e.g., a brand-new closure this quarter); clipping the annotation undermines the entire signal.

10. **Event-line annotation badge.** Centre-event vertical lines render with a small badge above the chart top axis containing the event type abbreviation (`+1` opening / `−1` closure) + quarter year. Replaces v1's bare dashed line which required hover discovery to surface what the line represented. Hover still reveals full centre name + provider in the readout per chart-polish (v1 register #10) — the badge is the at-a-glance label.

11. **DER badge colour-coding.** The OBS / DER / COM badge family (DEC-69 row metadata) gains a per-tag colour: OBS muted blue, DER muted purple, COM muted amber. Until Turn 2 all three badges rendered in the same neutral grey, which Patrick noted defeated the at-a-glance distinguishing purpose of the tag system. Colour values are subtle and meet WCAG AA against the panel background. No semantic re-binding — the categories themselves (Observed / Derived / Commercial) are unchanged per DEC-69.

12. **SEIFA descriptor on identity tile.** The SEIFA tile in Layer 1 identity row carries a one-word descriptor alongside the decile (e.g., "Decile 7 · advantaged"), not just the bare number. Mapping: D1-D2 "most disadvantaged" / D3-D4 "below median" / D5-D6 "around median" / D7-D8 "advantaged" / D9-D10 "most advantaged". Rationale: institutional readers parse the descriptor faster than the decile-to-descriptor mapping for a glance read; descriptor is universal across credit / acquisition / investment readers (decile is too technical for some lay readers).

13. **Layer 2 Community signal enrichment.** The Community signal tile composer was originally rule-based off the NES band only (DEC-84 #2). Turn 3 adds a `community_profile` substrate: the tile carries top-2 languages spoken at home alongside the NES band, surfacing specific community composition rather than a generic "culturally diverse" descriptor. Implementation: `_build_executive` consumes a new `community_profile` param fed by the top-2 language extraction in `_build_drawer`; the tile copy templates `[NES band] · [lang1] · [lang2]` when languages are present, falls back to NES-band-only otherwise.

14. **Quality category transitional note.** Layer 5 matrix Quality category renders an italic single-line caption beneath the category header noting that the Quality data substrate is still partial in V1 (Starting Blocks NQAITS snapshot covers ~129 of 130 pilot centres; national scale-up pending — DEC-83 banked V2 follow-up). Rationale: surfacing the "this row may be empty for centres outside pilot SA2s" caveat once at the category level avoids per-row P-2 silent-absence that reads as data error. Removed once national commercial-layer scale-up completes.

15. **Explicit SA2 line in Layer 1 identity row.** The SA2 name (and code) renders as its own identity-row fact chip (e.g., "SA2: Pyrmont — Ultimo (117031337)") rather than being implicit-only through the catchment metric source attributions. Rationale: the SA2 is the load-bearing analytical unit for the entire catchment lens; readers should see it as an identity fact alongside places / subtype / SEIFA / remoteness, not infer it from chart sources.

16. **Source-attribution hygiene sweep.** Pass across all Layer 3 + Layer 4 chart source lines and Layer 5 matrix row source lines to standardise attribution format: "[Publisher] [Series] [Year/Cadence]" (e.g., "ABS Education and employment database 2024 (annual)"; "Starting Blocks daily fee schedule (DEC-83 Commercial Layer V1; service_fee table; weekly refresh cadence)"). Cleans up inconsistent shorthand and ensures every chart + row carries source provenance per DEC-82 primary-source-first transparency principle. No data changes; copy only.

Consequences of the amendment:

- Queue items closed by Turns 1-3: #1 (inline-row-click expand), #2 (Layer 4 accordion removal — de-queued via reversal), #4 (matrix category reorder, via Turn 1's display-order rewrite to credit-analytical flow), #9 (Top-N inline context lines), #11 (matrix terminology rename). Remaining queue items stay open and form the next-session bundle candidate set per `recon/centre_v2_design.md`.
- DEC-84 #11 (sparkline locked at 24px in matrix rows) is partially reversed: matrix sparkline column retires; chart-below-histograms keep 80px. The locked sizing call now reads "80px chart-below histograms only".
- DEC-84 #2 (Layer 2 signal tiles) gains the `community_profile` substrate input not contemplated in the original locks. Composer rule for Community tile updates to `[NES band] · [top-2 languages]` with fallback. No new flag triggers; severity hierarchy unchanged.
- Centre-events overlay scope widens from 4 catchment metrics to 4 catchment + under-5/births + population/cohort charts. `_layer3_position` already emits the payload; only renderer wiring extends.
- DER badge palette adds new CSS variables (`--badge-obs` / `--badge-der` / `--badge-com`) in centre_v2.html — no centre.html v1 change (DEC-22 collapse precedent does not apply because v1 is frozen post-stake).
- Net file deltas: `centre_page.py` v24 (Turn 1: `_truncate_sentence` widened from 120 to 240 chars; Turn 3: `community_profile` substrate + top-2 language extraction in `_build_drawer` + `_build_executive` param); `docs/centre_v2.html` v0.5 → v0.7-band (Signal Matrix rename + category reorder + sparkline column retired + commentary widened + inline-row-click expand wiring + edge-event nudge + event-line badge + DER colour palette + SEIFA descriptor + SA2 fact chip + Quality category caption + source-attribution sweep). v0.x version numbering stays informal until first verification capture per DEC-84 effort breakdown.
- No DB mutations from Turns 1-3. No `audit_log` rows. `kintell.db` unchanged.

---

## DEC-83 — Commercial Layer V1: daily-rate integration from Starting Blocks (pricing + regulatory snapshot + operator-group identity)
Status: Active
Date: 2026-05-11 (locked post-payload-inspection scope expansion; AMENDED 2026-05-11 same session post-precedent-check to reuse pre-existing scaffolds rather than creating parallel structures)

Context: The Starting Blocks pilot (`G:\My Drive\Patrick's Playground\childcare_market_spike\`) shipped end-to-end on 2026-04-28 with 130 centres across 3 SA2s, 8,244 fee rows spanning 2018-2026, and all 8 invariants passing. Per Centre v2 redesign sequencing memo (`project_centre_v2_redesign.md`, 2026-05-10 PM s3), daily-rate data must land in `kintell.db` BEFORE the Centre v2 joint design pass — Layer 5 (institutional signal matrix) cannot be content-mapped without it. Probe of the pilot's `__NEXT_DATA__` source payload (2026-05-11) revealed significant institutional-value fields beyond the narrow daily-rate scope: provider-level regulatory state, enforcement actions, conditions, large-provider operator-group identity, vacancies, fee-type classification, NQS area-by-area breakdown, NQS prior-rating trajectory, and operating hours. Patrick ratified expanding scope to capture all HIGH and MEDIUM priority fields in the same ingest pass — capture-once-use-anywhere economics beat re-fetching 18,223 services later. The "daily rate" framing is preserved as the headline use-case but the underlying capability is the full commercial layer.

**Pre-build precedent check (DEC-65 discipline) surfaced existing scaffolds:** `regulatory_events` (0 rows, polymorphic event scaffold with `subject_type`/`subject_id`/`event_type`/`event_date`/`detail`/`severity`/`regulator`/`source_url` — exactly the shape originally proposed for `service_enforcement_action`); `nqs_history` (807,526 rows, canonical NQS quarterly state from NQAITS with `overall_rating` + `quality_area_1`-`7` + `provider_name` + `approval_date` + `max_places` per `(service_approval_number, quarter)`); `service_financials` (0 rows, scaffold with `daily_fee` REAL at service-date snapshot — different granularity than long-format per-(age_band,session_type) we need, complementary not duplicative). Schema plan amended to reuse `regulatory_events` for enforcement actions instead of creating a parallel `service_enforcement_action` table; NQS area columns and prior-rating columns dropped from `service_regulatory_snapshot` (single optional column retained for Starting-Blocks-vs-NQAITS cross-validation only). `service_fee` long format remains net-new — it's the granular source-of-truth that `service_financials.daily_fee` could derive a summary view from.

Decision:

1. **Schema namespace.** New tables in `kintell.db` use generic commercial-layer naming with a mandatory `source` discriminator column for forward multi-source compatibility (`'startingblocks'` populated at V1; `'careforkids'`, `'manual'`, `'scraped'` reserved for V2 per MODULE_SUMMARY §3). Aligns with existing main-DB convention (`service_catchment_cache`, `services_quarterly_snapshot`).

2. **Six new tables in `kintell.db` + reuse of one pre-existing scaffold:**
   - `service_fee` — long format, PK `(service_id, age_band, session_type, as_of_date, source)`. Joins to `services.service_id`. Includes `fee_type` (e.g. 'ZCDC' classification), `inclusions`, `fetched_at` provenance.
   - `service_regulatory_snapshot` — **slimmed (DEC-65 amendment)** — append-only snapshots, UNIQUE `(service_id, snapshot_date, source)`. Focuses on Starting-Blocks-unique state (NQAITS `nqs_history` is canonical for quarterly NQS rating + 7 quality areas). Captures: CCS state (`ccs_data_received`, `ccs_revoked_by_ea`), operational state (`is_closed`, `temporarily_closed`, `last_regulatory_visit`, `last_transfer_date_starting_blocks`), enforcement count (summary; details to `regulatory_events`), single optional cross-validation column `nqs_starting_blocks_prev_overall` + `nqs_starting_blocks_prev_issued` (Starting-Blocks-published prev rating; NOT a duplicate of `nqs_history`'s quarterly trajectory — captured solely for source-divergence checks), provider sub-block (`provider_status`, `provider_approval_date`, `provider_ccs_revoked_by_ea`, `provider_trade_name`), operating hours (14 columns: `hours_<day>_open`/`hours_<day>_close` for monday..sunday), contact enrichment (`website_url`, `phone`, `email`), `fetch_id` provenance link.
   - `service_condition` — long format, PK `(condition_id, level, source)`. Columns: `service_id`, `condition_id` (Starting Blocks 'CON-XXXXX' ID), `condition_text` (full text), `level` ∈ {'service', 'provider'}, `first_observed_at`, `last_observed_at`, `still_active` (1/0 — derivable from last_observed_at staleness on subsequent refreshes). Distinct from `regulatory_events` because conditions are persistent state requirements, not point-in-time events.
   - `service_vacancy` — vacancy snapshots, append-only, UNIQUE `(service_id, age_band, observed_at, source)`. Columns: `vacancy_status` (TEXT — captures both populated detail and 'no_vacancies_published' sentinel), `vacancy_detail_json` (TEXT — full sub-payload preserved), `fetch_id`. Becomes longitudinal demand-side signal across the weekly refresh cadence.
   - `large_provider` — operator-group dimension. PK `large_provider_id` (Starting Blocks group `_id`). Columns: `name` (e.g. 'Guardian Early Learning'), `slug`, `first_observed_at`, `last_observed_at`, `source`.
   - `large_provider_provider_link` — many-to-many between Starting Blocks `largeProvider` groups and `provider_approval_number`. PK `(large_provider_id, provider_approval_number, source)`. Closes the gap that current `services` / `entities` / `groups` cannot resolve "Guardian operates 12 provider entities + N services nationally as one operator group". Critical substrate for Group page (OI-NEW-17) and Stream D PropCo.
   - `service_external_capture` — provenance / raw payload. PK auto-increment `fetch_id`; UNIQUE `(service_id, source, payload_sha256)`. Stores full `__NEXT_DATA__` JSON verbatim per pilot pattern. `external_id` (Starting Blocks ulid) preserved alongside `service_id`.

**Reused pre-existing scaffold:**
   - `regulatory_events` (existing, 0 rows) — populated at extract time for enforcement actions: `subject_type` ∈ {'service', 'provider'}, `subject_id` = `services.service_id` (service level) or `entities.entity_id` resolved from `provider_approval_number` (provider level — falls back to service-level `subject_id` with `event_type='provider_enforcement_action'` if no entity match), `event_type='enforcement_action'`, `event_date` = action_date, `detail` = action_type (e.g. 'Compliance notice issued'), `regulator` = 'ACECQA' (or jurisdiction-specific where derivable), `source_url` = startingblocks detail-page URL. Idempotent on Starting Blocks `action.id` carried in `detail` JSON or appended to event row signature.

3. **One new column on existing `services` table:** `large_provider_id` (TEXT NULL, FK to `large_provider`). Populated at ingest time from the service's payload `largeProvider._id`. Enables Group-page rollups. Marginal ALTER TABLE; STD-08 backup discipline applies.

4. **Identity-resolution rule (load-bearing).** Pilot `service_approval_no` ↔ main `service_approval_number` join: `substr(pilot.service_approval_no, 1, 11) = services.service_approval_number`. Verified empirically — matches 129/130 pilot rows. Pilot's long-form SAN (`SE-XXXXXXXX<base64-suffix>`, length 39) is a Starting Blocks identifier extension; main DB uses canonical short SAN (`SE-XXXXXXXX`, length 11). Stage-2 fallback for SAN-less rows (1 case, "Redfern Occasional Child Care Centre"): name + suburb + postcode fuzzy match with manual review queue.

5. **V1 discovery driver: services-table-driven, not national rediscovery.** Production V1 drives `commercial_layer_fetch.py` directly off main `services` table (the 18,223 services we already know about). Algolia is reconciliation only — a lightweight `algolia_reconcile.py` runs national radius queries periodically to surface new centres + closures. Defers the build of a postcode-loop or SA2-centroid-loop national discovery driver to V2 — saves ~1-2 sess of V1 work for no V1 functional loss. Closes the geographic-discovery design question raised by MODULE_SUMMARY §7.

6. **Three-tier refresh cadence.** Weekly fees (`commercial_layer_fee_refresh.py` ~7-8h overnight Saturday at 1.5s polite pacing across 18,223 services, SHA-256 dedup skips ~80-90% unchanged). Monthly regulatory (`commercial_layer_regulatory_refresh.py` captures NQS / CCS / enforcement / conditions / vacancy snapshot). Quarterly Algolia reconciliation (`algolia_reconcile.py` catches new/closed centres). Each refresh writes audit_log START + END pair per STD-11 / DEC-62 (action naming `commercial_layer_<verb>_v1`). National-scale automation (cron / Windows Task Scheduler) is V2; manual run for V1.

7. **Audit + STD-08 discipline.** Schema migration takes pre-mutation `data/kintell.db` backup (STD-08) + writes audit_log mutation row. Each refresh run writes audit_log row(s); per-row provenance lives in `service_external_capture` via SHA-256 + `fetched_at`, not audit_log. Ingest rolls into batch audit rows so audit_log row count grows linearly with refreshes, not centres.

8. **Centre page integration deferred to Centre v2.** Daily-rate becomes a Lite row in the Centre v2 institutional signal matrix (Layer 5 per `project_centre_v2_redesign.md`) — the natural home for a peer signal. Forcing it into Centre v1's existing layout would duplicate work when v2 ships imminently (next-session-after-this). If v2 design pass slips materially, fall back to a minimal Centre v1 surface (Lite row in Catchment Position card under CONTEXT row weight); don't over-invest pre-v2.

9. **Pilot folder decommission.** Once the main-DB ingest lands and the 130-centre proof load validates, the pilot folder at `G:\My Drive\Patrick's Playground\childcare_market_spike\` is decommissioned. Reusable code (`fetch.py`, `extract.py` payload-mapping logic) gets ported into `commercial_layer_fetch.py` / `commercial_layer_extract.py` in main repo with full proc_helpers / STD-11 / STD-30 integration. Pilot folder archived to `C:\Users\Patrick Bell\childcare_pilot_archive_2026-05-11\` for traceability. Closes the Google-Drive SQLite write-loss footprint (1/130 observed in pilot).

10. **Algolia credentials = public values, hardcoded with smoke test.** Algolia application ID + search-only API key + index name are public values from the Starting Blocks JS bundle (not secrets). Hardcoded as constants at top of `commercial_layer_fetch.py` per pilot pattern. Smoke-test pre-each-refresh (single Algolia call probes for HTTP 200 + non-zero hits) aborts cleanly if ACECQA rotates the key, with log message pointing to the 5-min DevTools refresh procedure documented in module docstring. Closes OI-NEW-4.

Consequences:

- DEC-83 establishes the **commercial layer pattern** for `kintell.db`. Future commercial-layer sources (Care for Kids, scraped fee aggregators, manual disclosed fees) populate the same tables with different `source` values; cross-source reconciliation is a V2 problem (per-source authority weighting).
- **Total schema impact:** 6 new tables + 1 reused scaffold + 1 new column on `services`. Pre-mutation STD-08 backup mandatory. audit_log next id: 176.
- **Effort:** ~1.6-1.7 sess (was 1.1 pre-expansion). Schema migration patcher 0.3 sess + fetch/extract port 0.7 sess + initial 130-centre proof load 0.2 sess + Algolia reconcile 0.2 sess + monolith 0.1 sess + DEC-83 mint 0.1 sess.
- **Strengthening Regulation Bill 2025 risk** (cross-cutting risk per PRODUCT_VISION §9 / DEC-79 #6): `service_regulatory_snapshot.ccs_revoked_by_ea` + `service_enforcement_action` together provide the data signal previously tracked-but-uncaptured. NQS trajectory via `nqs_prev_overall` + `nqs_prev_issued` becomes a leading credit indicator with empirical history.
- **Group page (OI-NEW-17) + Stream D PropCo (OI-NEW-13)** unblocked: `large_provider` + `large_provider_provider_link` give operator-group identity that current `services` / `entities` / `groups` cannot resolve. Guardian Early Learning, Goodstart, G8, Affinity etc. all become first-class portfolio entities.
- **Child-safety surface (Centre v2 Layer 6)** seeded by `service_condition` + `service_enforcement_action` + 7 quality-area NQS breakdown — substantive content beyond Patrick's offline child-safety research.
- **OI-NEW-4** (Starting Blocks Algolia smoke test + Community Profiles retirement audit) — Algolia portion closed by smoke-test integration in #10. Community Profiles retirement audit remains separate.
- **Daily-rate centre-page integration** (legacy parallel work stream from ROADMAP.md §7) is now scoped + ratified. Removes the "deferred until daily-rate metric set is stable" dependency that blocked A8 / B7 / C7 in CENTRE_PAGE_V1_5_ROADMAP.
- **MODULE_SUMMARY_Childcare_Market_Data_Capability.md** §7 Integration Requirements addressed:
  - Schema migration: this DEC.
  - Identity resolution: #4 (LEFT(11) primary + name+suburb+postcode fallback).
  - Geographic discovery driver: #5 (services-table-driven + Algolia reconciliation).
  - Operational hardening: #9 (off-Google-Drive) + #6 (refresh cadence) + #7 (audit_log integration).
  - Stress-test at scale: deferred to first national refresh run (post-V1 schema lock).
  - Multi-source posture: forward-compat designed in via `source` column; second source actual integration is V2.
- The "daily rate" framing in user-facing copy is preserved (Patrick's anchor framing); under the hood the data substrate is the full commercial layer.

---

## DEC-82 — Direct to primary source for new ingests; track derivative-sourced metrics for V2 migration
Status: Active
Date: 2026-05-10 (locked at A4 design ratification)

Context: A4 design (Schools at SA2) surfaced that the existing `Education and employment database.xlsx` workbook from ABS Data by Region (DBR) is a **derivative source** — ABS bakes Census, ERP, ATO, ACARA, Jobs in Australia and other primary sources into one annual workbook. Convenient for breadth, but ties refresh cadence and provenance to ABS's release schedule rather than the upstream primary publishers'. Patrick's commercial-product framing made this load-bearing: data freshness and update independence are competitive differentiators against incumbents (GapMaps, Qikmaps at ~$1,500/user/month), and routing through derivative sources concedes both. The A4 alternative — direct ACARA ingest with spatial join to SA2 — has equivalent or better refresh cadence (ACARA publishes ~3 months post-school-year-end vs ABS DBR ~12-18 months), opens downstream metrics the workbook can never expose (NAPLAN, ICSEA, year-level breakdowns, sub-types), and builds reusable spatial-join infrastructure for V2 PropCo / hospital / transport ingests.

Decision:

1. **Primary-source-first policy for new ingests.** Any new SA2-level data ingest from this point forward MUST consider primary-source ingestion before falling back to a derivative source. Acceptable rationale to use a derivative source: (a) the primary publisher does not publish at SA2 resolution and ABS aggregates it (e.g., ATO median income, published at LGA only — ABS aggregates to SA2 for DBR); (b) the primary source is paywalled or licensing-restricted in a way that breaks the commercial model; (c) the derivative is materially better-maintained for the specific signal (rare but possible). Document the rationale in the ingest script docstring and in a tracked OI for periodic review.

2. **A4 ratified as the first direct-primary-source ingest.** ACARA School Profile + School Locations CSVs sourced directly from ACARA Data Access Service (or data.gov.au mirror). Spatial join (school point → SA2 polygon) via existing `ASGS_2021_Main_Structure_GDA2020.gpkg`. New table `abs_sa2_schools_annual` (SA2 × year × school sector × metric — likely sector breakdown via wide or extra column). Spatial-join helper lives in `proc_helpers.py` as `point_to_sa2(lat, lon, gpkg_path)` — reusable for V2 PropCo property location → SA2, hospital catchment area → SA2, transport station coverage → SA2.

3. **V2 migration backlog for existing derivative-sourced metrics.** The `abs_sa2_education_employment_annual` table currently holds 16 metrics ingested from ABS Data by Region (Education and employment database.xlsx via `layer2_step5b_prime_apply.py`):
   - Preschool series (3): `ee_preschool_4yo_count`, `ee_preschool_total_count`, `ee_preschool_15h_plus_count` — primary source: AEDC + state preschool registries (varies by state, harder to consolidate)
   - Education attainment (2): `ee_year12_completion_pct`, `ee_bachelor_degree_pct` — primary source: Census TSP T20/T22 (we already have the zip)
   - Employment (4): `ee_unemployment_rate_persons_pct`, `ee_lfp_persons_pct`, `ee_jobs_females_count`, `ee_jobs_total_count` — primary source: Census TSP (LFP) + ATO Jobs in Australia (jobs counts; not at SA2 directly)
   - Occupation/industry (7): `ee_managers_pct`, `ee_professionals_pct`, `ee_clerical_admin_pct`, `ee_jobs_info_media_count`, `ee_jobs_finance_count`, `ee_jobs_professional_scientific_count`, `ee_jobs_admin_support_count` — primary source: Census TSP (occupation %) + ATO Jobs in Australia (industry counts)

   These are NOT migrated in V1.5 — too much rework for limited freshness gain; ABS DBR refresh cadence is acceptable for the underlying metrics. Tracked as a V2 backlog OI (OI-NEW-20). Migration order if pursued: education attainment + LFP first (Census TSP already on disk, zero new acquisition); jobs/industry counts later (require ATO Jobs in Australia primary-source ingest); preschool series last (AEDC + state-by-state primary sources are fragmented).

4. **No retroactive renaming of derivative-sourced metrics.** Existing `ee_*` and `census_*` namespaces stay. Direct-primary-source new ingests use a clean naming convention (e.g., `acara_*` for ACARA, `aihw_*` for future AIHW ingests, etc.) so the DB is self-documenting about provenance without breaking existing renderer wiring.

5. **OSHC-school adjacency intelligence (related, V2-banked).** Once ACARA schools land with lat/lon, the same spatial-join helper enables a service-level derived flag: "is this OSHC service co-located with or adjacent to a school?" — a key institutional context signal for OSHC investment / credit decisions (per Patrick: "having a school attached to an after-school care facility is a key indicator of success in that industry"). Tracked as OI-NEW-19. V2 work; data infrastructure (ACARA ingest) ships in V1.5.

Consequences:

- A4 effort: ~1.0 sess. Spatial-join helper amortises across future point-feature ingests (PropCo, hospitals, transport).
- The `abs_sa2_schools_annual` table joins the data inventory as the first direct-primary-source SA2 table. Naming convention `acara_*` for any school-level metrics that aren't share-derived (e.g., `acara_school_count_govt`, `acara_school_enrolment_total`).
- DEC-82 is a strategic principle, not a hard architectural constraint — the documented rationale carve-out (item 1) gives flexibility where primary sources don't exist at our resolution.
- V2 migration of the 16 ABS DBR metrics is a tracked backlog (OI-NEW-20) but explicitly NOT V1 work; commercial-product readiness is achieved by going direct on NEW ingests, not by retroactively re-ingesting everything.
- Centre page provenance display (the existing `source` field in `LAYER3_METRIC_META`) is the first place this strategic principle becomes user-visible — when ACARA metrics ship, their source line will read "ACARA School Profile <year> + School Locations <year>" instead of "ABS Data by Region", giving Patrick a clean talking point for institutional buyers about freshness and data lineage.

---

## DEC-81 — Stream C V1 scope: parent-cohort 25-44 + partnered 25-44 + women-with-child fertility cuts (35-44 + 25-34)
Status: Active
Date: 2026-05-10 (locked at A3 + Stream C close)

Context: A3 (Parent-cohort 25-44 SA2 series) and Stream C (childbearing-age + marital-status depth, OI-NEW-12) were bundled into a single V1.5 ingest pass on 2026-05-10 because both share the 2021 TSP zip + the existing ABS ERP workbook. The probe (`recon/probes/probe_a3_streamc_columns.py`) confirmed T05 marital categories are limited to `Mar_RegM` (registered) + `Mar_DFM` (de facto) + `N_mar` (never married) + `Tot` — no separated/divorced/widowed in the short-header — and T07 fertility is shaped as `C{yr}_AP_{age}_NCB_{0..6mor,NS,Tot}` (women only). The ERP workbook's `Persons - 25-29..40-44 years (no.)` columns sit at indices 89-92 with `total_persons` at col 3 (NOT col 121, which is the fertility rate decimal — the original Layer-2-step-6 diag mis-guessed col 121; this DEC locks col 3 explicitly for any future ERP age-band ingest).

Decision:

1. **Four metrics ship in V1**, all stored as percentage 0-100 per DEC-78, all banded `state_x_remoteness` per DEC-67 (NES precedent), all neutral framing per DEC-75 — no calibration nudge in V1, parallel to the A10 metrics (calibration scoping is a follow-up after banding distributions are reviewed).

   | Metric (canonical) | metric_name in long-format | Source | Trajectory |
   |---|---|---|---|
   | `sa2_parent_cohort_25_44_share` | `erp_parent_cohort_25_44_share_pct` | ABS ERP cols 89..92 / col 3 | annual, 6 points 2019-2024 (workbook's SA2-level coverage starts 2019 per A1 finding) |
   | `sa2_partnered_25_44_share` | `census_partnered_25_44_share_pct` | TSP T05 (RegM_P + DFM_P over 25_29..40_44) / Tot_P | Census 3-point |
   | `sa2_women_35_44_with_child_share` | `census_women_35_44_with_child_share_pct` | TSP T07, women 35_39 + 40_44, (Tot − NCB_0 − NCB_NS) / (Tot − NCB_NS) | Census 3-point |
   | `sa2_women_25_34_with_child_share` | `census_women_25_34_with_child_share_pct` | TSP T07, women 25_29 + 30_34, same formula | Census 3-point |

2. **Sharp 25-44 window for partnered.** The partnered-share window matches the parent-cohort window (rather than the broader Census 15+ headline ~50% national). Rationale: the three rows tell a coherent story when they share the same age frame ("of the 25-44s in this catchment, X% are in partnerships"). Patrick ratified the sharp cut.

3. **Two fertility cohorts, not one.** The original D-B1 proposal shipped only the 35-44 "completed-fertility proxy" cut. Patrick's amendment: 35-44 alone "feels old" for childcare relevance — a woman in 35-44 with a child today may have the child already past the 0-5 ECEC window. The under-cohort 25-34 with at least one child indexes more directly to active ECEC parenting and is therefore additionally interesting institutional context. Both cuts ship; the 35-44 cut remains as a completed-fertility community-profile signal, the 25-34 cut as the active-timing signal. National 2021 references: 35-44 ~78%, 25-34 ~41%. Patrick acknowledged the density tradeoff (sub-panel grows from 4 to 8 rows; total Catchment Position card 9 → 13 rows) and accepted it.

4. **NS-handling convention for fertility.** Numerator AND denominator both exclude `NCB_NS`. Mirrors the NES + ATSI + single-parent NS-as-other convention but stricter — NS in fertility ranges from 3-5% nationally. Documented in the ingest script docstring.

5. **NSDW caveat for partnered.** TSP T05 short-header carries only RegM + DFM + N_mar + Tot. The complement of "partnered" in this metric is "never married + separated + divorced + widowed combined", not just "never married". Documented in the metric reason field. Full T05 detail (Sep / Div / Wid breakdown) requires the GCP DataPack and is deferred to V2 if ever requested.

6. **ERP `total_persons` at col 3 (definitively).** The Layer-2-step-6 v2 docstring corrected col 121 → col 3 but the column-map JSON still carried 121. Future ERP age-band ingests must use col 3 for total_persons. Documented in `layer4_4_step_a3_streamc_apply.py` with explicit constant comment.

Consequences:

- Stream C (OI-NEW-12) closes at this DEC for V1 purposes. V2 expansion targets banked: full marital breakdown (Sep/Div/Wid), mean children-ever-born (decimals), and broader 15+ marital cuts.
- Calibration scoping for the 4 new metrics + the existing 4 A10 metrics deferred to a single calibration pass once banding distributions are surveyed (`recon/calibration_review_post_a10_a3.md` candidate).
- Fertility metrics are female-only by construction (T07 = women only). For visualisation on a unisex card, label clarity is essential; "Share of women aged X to Y with at least one child" is the canonical phrasing per Patrick.
- The Catchment Position card now hosts 13 rows (5 credit + 8 demographic). DEC-75 visual-weight discipline keeps total card height modest because Lite rows are ~⅓ the height of Full rows. Revisit only if Patrick flags density during operator-review of the rendered page.
- The `_renderLiteDelta` helper handles the parent-cohort 6-point annual trajectory (badge reads "+/- Xpp from 2019 to 2024") and the Census 3-point trajectories transparently — no new render helpers needed for this bundle.

---

## DEC-80 — Census top-N display tables; TSP-table-mapping verification discipline
Status: Active
Date: 2026-05-10 (locked at A10 + C8 close)

Context: The A10 Demographic Mix bundle (Layer 4.4, 2026-05-10) added three SA2-level demographic metrics from Census TSP tables (T06 Indigenous status; T08 country of birth; T14 family composition) plus two **list-shaped** display contexts that the existing long-format `abs_sa2_education_employment_annual` table cannot accept: top-3 country of birth (T08) and top-3 language at home (T10A+T10B). The roadmap entering A10 had named the source tables as T07/T08/T19 — probe revealed T07 is fertility (children-ever-born × age) and T19 is tenure type / landlord, with the actual subjects sitting at T06 and T14. Both issues are recurring patterns worth locking as discipline rather than one-off fixes.

Decision:

1. **Top-N display tables convention.** Census list-shaped data (top-N countries, top-N languages, future top-N occupations / industries / etc.) lands in dedicated small tables, not the long-format `abs_sa2_education_employment_annual`. Naming: `abs_sa2_<topic>_top_n`. Schema: `(sa2_code TEXT, census_year INTEGER, rank INTEGER, <label_column> TEXT, count INTEGER, share_pct REAL, PRIMARY KEY (sa2_code, census_year, rank))`. Display-only — these tables do not feed banding (`layer3_sa2_metric_banding`) or calibration (`calibrate_participation_rate`). Rendering reads via a `_build_community_profile(conn, sa2_code)` helper that returns `{"<topic>_top_n": [...]}` lists on the centre payload's `community_profile` field. Currently shipping: `abs_sa2_country_of_birth_top_n` (D-A2), `abs_sa2_language_at_home_top_n` (A10/C8 follow-up). Default top-N = 3; tunable per ingest.

2. **TSP-table-number verification at probe time.** ABS Census TSP tables are numbered sequentially across data items, not by topic; numbering does NOT match GCP (General Community Profile) or other ABS products. Before any ingest pulls a TSP table by number, the probe must inspect the column headers and confirm the subject. A two-line probe is sufficient: read the first CSV row, print the second header column. If the column header doesn't match the expected subject keyword (e.g., "Indig" for Indigenous status, "Eng_only" for language at home, "Aust" for country of birth), halt and re-probe.

3. **Census Demographic Mix bundle scope (A10).** Three banded SA2-level percentage metrics ship together: ATSI share (T06), overseas-born share (T08, NS-excluded numerator), single-parent family share among family households (T14). Plus two display-only top-N tables (T08 countries, T10A+T10B languages). All four shipped 2026-05-10; backups `data/pre_layer4_4_step_a10_*.db` and `data/pre_layer4_4_step_a10b_*.db`; audit_id 150 → 158. Calibration influence deferred — the four bandable metrics (NES + 3 Demographic Mix) are neutral-framed Lite rows on the Catchment Position card sub-panel, with `direction="high_is_positive"` purely declarative (no calibration nudge applied). Calibration scoping is a follow-up once banding distributions are reviewed.

4. **Sub-panel inside Catchment Position card, not a new card.** The Demographic Mix sub-panel renders inside the existing Catchment Position card via a divider line + sub-panel header. Per DEC-11 (additive overlay) — extend existing surfaces before adding new ones. Anticipated by the C2 NES patcher author 2026-05-04. New `renderCommunityProfileCard()` was rejected on UI-coherence grounds (would force NES to move card mid-flight; proliferates renderer functions).

Consequences:

- Top-N tables proliferate ad-hoc as new Census list-shaped contexts join: each one is a small table, a new entry in `_build_community_profile`, and a new `_renderTopNContext` call site in the Lite-row interleave (`renderCatchmentPositionCard`'s `renderDemoRow`). The shared `_renderTopNContext(list, label, key)` helper in `centre.html` is the canonical render pattern.
- `abs_sa2_country_of_birth_top_n` and `abs_sa2_language_at_home_top_n` (2021-only) need to be re-ingested when the 2026 Census data lands (mid-2027). Add `census_year` parameter to schema future-proofs but doesn't auto-update.
- The TSP-mapping probe step is added to STD-37 candidate ("search project knowledge before probing") as a sub-rule when the probe is a Census ingest. Bank when STD-37 mints.
- Stream C (childbearing-age + marital-status depth, OI-NEW-12) is now well-positioned: T05 marital status and T07 fertility are both in the same TSP zip, both validated by this session's probe but deferred to A3 ingest pass.

---

## DEC-79 — Commercial repositioning: Novara Intelligence; Patrick Bell IP; childcare asset & portfolio intelligence
Status: Active
Date: 2026-05-09

Context: The platform began as an internal email-and-news tool informing Remara Capital Group staff about new service approvals (legacy still visible in `module5_digest.py`, `module6_news.py`, `da_leads.json`, `leads_enriched.json`). Through Phase 1.7 → Phase 2 → Phase 2.5 it evolved into a per-centre credit-decision-support system framed around Remara's underwriting needs, with Remara's Strategic Insights V1.3/V4.2, Credit Policy Short Form 14Jan25, Credit Policy For-Discussion-and-Draft, and Childcare Credit Committee Briefing Paper used as the domain anchor for thresholds, band copy, and DEC-77 industry thresholds. As of 2026-05-09 the project is repositioned: Patrick Bell owns the IP, the product is independent of Remara, and the audience expands to the broader Australian childcare market participant base. Reference incumbents (GapMaps, Qikmaps) charge ~$1,500/user/month; the institutional decision-support frame is the strategic moat.

Decision:

1. **Ownership.** Kintell/Novara is Patrick Bell's IP. Remara Capital Group is a domain-knowledge reference (their published documents informed early framing) but is not a stakeholder in the product. Remara-proprietary documents must not ship with the product; their language must not appear in user-facing copy.

2. **Audience.** Lenders, institutional investors, large operators (for-profit AND not-for-profit), valuation firms, property funds, debt providers, advisory professionals. Not credit-team-only. The product serves all participants in the childcare asset & portfolio decision space.

3. **Positioning.** Childcare asset & portfolio intelligence + institutional decision-support system. NOT a mapping tool. NOT a childcare CRM. Mapping is supporting context, not primary UI (DEC-71 stands; mapping additions in V2 are subordinate to structured intelligence).

4. **Brand.** Working name **Novara Intelligence**. Successor to "Kintell" (rejected — namespace collision with another AI business) and the "Remara" working name (used as the directory header due to project origin; rejected — collides with Remara Capital Group's trading name). Filesystem and DB names retain `kintell` / `remara` prefixes for now to avoid churn (the working directory `C:\Users\Patrick Bell\remara-agent\`, the database `data/kintell.db`, key Python modules). A brand identity rename pass is queued as housekeeping (OI-NEW-6).

5. **Pricing.** Two tiers initially: entry / replacement (cannibalising GapMaps, Qikmaps users) and institutional (premium PropCo / portfolio intelligence). Reference incumbents at ~$1,500/user/month.

6. **Build philosophy.** Institutional decision infrastructure from day one. ISO 27001 / SOC 2 readiness artefacts in V1; certification deferred to V2. Privacy governance baseline. Auditability and explainability are first-class properties of every metric and signal — no opaque scoring, no subjective rankings, no moralised language. All metrics objective, ABS-derived where possible, calibration nudges only (per STD-34). Avoid feature sprawl; extend existing structures rather than fragmenting the product.

7. **Operational split.** Patrick drives strategy, UI coherence, industry-specific depth, data depth, and commercial risk management. Claude drives technical architecture, schema design, code, build sequencing, and doc discipline. Patrick's input on coding architecture is intentionally limited.

8. **PropCo layer in V1.** The evidence-based property ownership intelligence module (Stream D — see PRODUCT_VISION.md) moves from V2 to V1 because the no-title-search design is cheap to build, defensible, and a strong commercial opener. Premium-tier feature.

9. **V1 ship target: 3–4 months from 2026-05-09 (i.e. ~Sept 2026).** V2 fast-follow.

10. **Excel export framework as V1 deliverable.** Institutions need portable intelligence, not just dashboards. Repeatable workbook structures, transaction-ready outputs (DEC candidate, to be locked when Excel work is scoped).

Consequences:

- All future framing in docs and user-facing copy uses "Novara Intelligence" as the brand. Filesystem stays unchanged for now.
- Remara-specific framings in legacy code (e.g. "credit reader" in DEC-72 band copy, "Credit Committee Brief" framing in DEC-77 source attribution) remain as historical context but are NOT extended into new surfaces. New framing is generic to market participants.
- The `module5_digest.py` / `module6_news.py` email pipeline is no longer first-class product surface. It can stay (works) but is not extended.
- Excel-export framework becomes a first-class V1 deliverable.
- Five new work streams locked into the roadmap (PRODUCT_VISION.md):
  - **Stream A** — Educator visa / overseas educator supply (Workforce extension)
  - **Stream B** — NFP perspectives integrated into existing structure (no separate NFP module)
  - **Stream C** — Childbearing-age cohort + marital-status depth (extends A3 + T19)
  - **Stream D** — PropCo Property Intelligence Module (now V1 per #8 above)
  - **Stream E** — SA2 Border Exposure V1 proxy
- Cross-cutting risks tracked: 2026 Census Aug 2026 → SA2 boundary refresh project Q3 2027; workforce funding cliff Nov 2026 (Worker Retention Payment ends, FWC permanent ~27% wage uplift takes hold); Strengthening Regulation Bill 2025 → CCS revocation as live early-warning credit indicator.
- Tier-1 docs at `recon/Document and Status DB/` (ARCHITECTURE, PRINCIPLES, GLOSSARY, DATA_INVENTORY, CONSOLIDATION_LOG) and Tier-2 docs missing from repo root (DECISIONS, STANDARDS) to be moved to repo root for visibility (OI-NEW-7 housekeeping).
- A new `CLAUDE.md` lands at repo root (this session) so every future Claude Code session has orientation.
- A new `PRODUCT_VISION.md` lands at repo root (this session) capturing the strategic frame and the five new streams.
- Discontinuities to expect: any legacy doc, comment, or copy still framed around "Remara credit team" should be read as historical, not authoritative for future work.
