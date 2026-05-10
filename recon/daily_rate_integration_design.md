# Daily-Rate (Pricing & Regulatory) Integration: design doc

*Created 2026-05-11 (next-session pickup after Centre v2 redesign sequencing memo locked daily-rate ahead of v2 design pass). Probe-first per DEC-65. **Status: DRAFT — pending Patrick ratification of D-1 through D-9. DEC-83 candidate substrate.***

*Expanded 2026-05-11 — Patrick raised "are we capturing all valuable Starting Blocks data" before locking. Source-payload re-inspection surfaced significant institutional-value fields being left unextracted. Scope expanded from narrow daily-rate to full commercial-layer capture (regulatory state, enforcement actions, conditions, large-provider operator-group identity, vacancies, fee-type classification, operating hours, website, NQS area breakdown + trajectory). Patrick ratified expansion. Revised effort ~1.7 sess (was 1.1).*

---

## RATIFIED SUMMARY (2026-05-11)

**DEC-83 minted in canonical DECISIONS.md.** Decision batch D-1 through D-9 ratified by Patrick post-payload-inspection scope expansion. Source-payload re-inspection surfaced significant institutional-value fields beyond the original narrow daily-rate scope; Patrick approved expansion to capture all HIGH and MEDIUM priority fields (regulatory state, enforcement actions, conditions, large-provider operator-group identity, vacancies, fee-type classification, NQS area breakdown + trajectory, operating hours, website) on capture-once-use-anywhere economics.

**V1 ships (AMENDED 2026-05-11 same session, post-precedent-check):**
- **6 new tables** in `kintell.db`: `service_fee`, `service_regulatory_snapshot` (slimmed — NQS area cols dropped, `nqs_history` is canonical), `service_condition`, `service_vacancy`, `large_provider`, `large_provider_provider_link`, `service_external_capture`
- **Pre-existing `regulatory_events` scaffold reused** for service-level + provider-level enforcement actions (instead of creating parallel `service_enforcement_action`)
- 1 column added to existing `services` table: `large_provider_id` (FK to `large_provider`)
- Identity resolution via `substr(SAN, 1, 11)` join (verified 129/130 pilot match)
- V1 discovery: services-table-driven; Algolia for reconciliation only (defers national driver to V2)
- Three-tier refresh cadence: weekly fees / monthly regulatory / quarterly Algolia reconcile
- Full STD-08 + STD-11 + DEC-62 audit discipline; `commercial_layer_*_v1` action naming
- Pilot folder decommissioned post-port (closes Google Drive write-loss risk)
- Centre page surface deferred to Centre v2 design pass (Layer 5 institutional signal matrix)
- Algolia smoke test on every refresh (closes Algolia portion of OI-NEW-4)

**V2 banked:** Care for Kids second source, per-source authority weighting reconciliation, national geographic discovery driver, refresh automation (cron / Task Scheduler), large-provider name change tracking.

**Effort:** ~1.6-1.7 sess from this point.
- Schema migration patcher: 0.3 sess (this session — coming next)
- `commercial_layer_fetch.py` + `commercial_layer_extract.py` expanded port: 0.7 sess
- 130-centre proof load + validate: 0.2 sess
- `algolia_reconcile.py`: 0.2 sess
- End-of-session monolith STD-35: 0.1 sess
- DEC-83 mint: 0.1 sess (DONE)

**Cross-effects unlocked:**
- **Strengthening Regulation Bill 2025 risk** (PRODUCT_VISION §9): live data signal via `ccs_revoked_by_ea` + `service_enforcement_action` (previously tracked-but-uncaptured)
- **Group page (OI-NEW-17) + Stream D PropCo (OI-NEW-13)**: `large_provider` + link table give operator-group identity; Guardian / Goodstart / G8 / Affinity etc. become first-class portfolio entities
- **Child-safety surface (Centre v2 Layer 6)**: seeded by `service_condition` + `service_enforcement_action` + 7-area NQS breakdown
- **OI-NEW-4** Algolia portion closed; Community Profiles retirement audit remains separate
- **Daily-rate centre-page integration** (ROADMAP §7 deferred work) unblocked
- **Centre v2 design pass** can now run with daily-rate data in hand

---

## 0. Why this work, why now

The Starting Blocks pilot (`G:\My Drive\Patrick's Playground\childcare_market_spike\`) shipped end-to-end on 2026-04-28. 130 centres, 8,244 fee rows, 2018-05-29 → 2026-04-27 history, all 8 invariants pass. Standalone SQLite at `startingblocks_pilot.sqlite` (~10 MB). Algolia discovery method locked architecturally per `MODULE_SUMMARY_Childcare_Market_Data_Capability.md` and pre-emptive Strategic Insights.

Centre v2 redesign locked daily-rate as Layer-5 institutional-signal-matrix content (per `project_centre_v2_redesign.md`). Cannot ratify the v2 content map until daily-rate data is in `kintell.db` — hence sequencing pulls daily-rate forward of the v2 design pass.

Strategic positioning for the broader V1 (DEC-79):
- Daily-rate is the headline missing institutional signal — fee position vs catchment peer cohort is one of the most-asked institutional questions in childcare credit / acquisition / valuation
- The infrastructure also brings regulatory-snapshot data (NQS rating + CCS approval + last-visit + enforcement count) for free — directly feeds the **Strengthening Regulation Bill 2025** "CCS revocation as live credit indicator" risk tracked under `PRODUCT_VISION.md` cross-cutting risks
- Establishes the multi-source commercial-layer pattern needed for V1 PropCo (Stream D) and V2 multi-source reconciliation

---

## 1. Probe findings (2026-05-11)

### 1.1 Pilot DB state — healthy

| Table | Rows | Note |
|---|---|---|
| `pilot_target` | 130 | Algolia hits, 3 SA2s |
| `raw_payload` | 130 | Provenance layer |
| `centre` | 130 | 1:1 with pilot_target |
| `centre_fee` | 8,244 | 110 centres with fee data; 20 with no published fees (FDC / Vacation Care / Preschool) |
| `schema_meta` | 1 | v1.0-pilot, created 2026-04-28 |

DB size: 10 MB. Fee date range 2018-05-29 to 2026-04-27 (8 years). All 8 invariants PASS. Zero-fee rows: 180 (sessions offered without published prices — preserved per validate.py convention).

Fee distribution by session type: full_day 4,668 / after_school 1,410 / before_school 1,363 / hourly 545 / half_day 258. Fee distribution by age band: 36m-preschool 1,775 / 25-35m 1,704 / 13-24m 1,686 / 0-12m 1,625 / school-age 1,454. Even spread across the 5 age bands and 5 session types — confirms scope coverage isn't biased.

### 1.2 Identity-resolution: SAN format mismatch (resolved)

The pilot's `service_approval_no` and main DB's `service_approval_number` use different conventions:

| Source | Format | Length | Example |
|---|---|---|---|
| Main `services` | `SE-XXXXXXXX` (8-digit numeric) | always 11 | `SE-00009686` |
| Pilot `centre` | `SE-XXXXXXXX<base64-suffix>` | mixed: 17 short / 112 long / 1 unprefixed | `SE-00012223MQA5ADAAMAAxADcANgAwADQAVAA=` |

**Join rule confirmed empirically:** `substr(pilot.service_approval_no, 1, 11) = main.service_approval_number` matches **129 of 130 pilot centres against main DB.** The 1 unmatched is an unprefixed base64-only row (`MQA5ADAAMAAxADEANwA1ADMAQgA=` → "Redfern Occasional Child Care Centre, NSW") — a single Occasional Care service that lacks an SE- prefix in the source payload. For 1 row, manual fallback (name + suburb match) is trivial.

This is a clean join. Identity resolution is not a project — it's a `LEFT(11)` rule.

### 1.3 Main DB readiness

- 18,223 services, all SE-prefixed length-11 SANs
- 18,203 services have `sa2_code` populated (post-OI-NEW-21 99.89% coverage)
- 17,882 services have lat/lng populated
- audit_log latest action: `sa2_history_rebuild_v3` (audit_id 175, 2026-05-10 PM s3)
- Services table has 36 columns (full identity / regulatory / geographic state). New tables join via `service_id` (PK), with `service_approval_number` as cross-source resolution key

### 1.4 Algolia discovery is overkill for V1

Pilot used Algolia for SA2-centroid radius discovery (3 SA2s, 130 centres). Production-scale equivalent would mean iterating thousands of SA2 centroids — but main DB **already knows about all 18,223 services**. Algolia's value at production scale is:
- Catching NEW centres (registered after the last NQAITS pull)
- Catching CLOSED centres (de-registrations)
- Confirming current state (slug + name + lat/lng for fetch URL construction)

This is reconciliation, not discovery. Most simple production-V1 path: drive `fetch.py` directly off main `services` table for centres already known, run **lightweight Algolia reconciliation pass** (single national query or SA4-loop) at refresh time to catch new / closed centres. Defers the geographic-discovery-driver build to V2.

### 1.5 Known operational risks (from MODULE_SUMMARY)

- **Google-Drive SQLite write-loss footprint: 1/130 (0.77%)** during pilot run. Production must run on local disk. Pilot folder needs to come into the main repo or live elsewhere on local disk.
- **Algolia credentials are public values from JS bundle.** ACECQA can rotate. Refresh procedure documented in pilot's STAGE2_DESIGN.md (5-min DevTools sweep).
- **Quota / rate-limit risk.** ACECQA pays for the Algolia tier; we consume their quota. Pilot scope invisible. National-scale ongoing scraping is a different conversation per MODULE_SUMMARY §3 — flagged as ethics consideration before refresh-scheduling at scale.
- **No audit_log integration in pilot** — pilot uses `raw_payload.fetch_id` as its provenance chain. Production must adopt STD-11 / DEC-62 audit_log discipline.

---

## 2. Decision points (D-1 through D-9)

Per session-density preference: all 9 decisions surfaced together with my recommendation; Patrick ratifies as a batch (or objects to specific ones).

### D-1 — Schema namespace in `kintell.db`

**Options:**
- **(A)** Verbatim port of pilot tables (`pilot_target / raw_payload / centre / centre_fee`). Risk: `centre` collides with `services` semantically; "pilot" is misleading once production.
- **(B)** Source-prefixed (`sb_target / sb_raw_payload / sb_centre / sb_fee`). Clear lineage but couples to one source.
- **(C)** Generic commercial-layer with `source` discriminator column (`service_fee / service_external_capture / service_regulatory_snapshot / service_external_target`). Future-fits Care for Kids, scraped fee aggregators, manual disclosed fees.

**Recommendation: (C).** Aligns with MODULE_SUMMARY §3 forward-compat note ("Multi-source columns — One ALTER TABLE later when Care for Kids enters scope") and with main-DB convention (existing tables: `service_catchment_cache`, `services_quarterly_snapshot`, etc.). The `source` column is mandatory NOT NULL TEXT, populated `'startingblocks'` on initial load. Reserves `'careforkids'`, `'manual'`, `'scraped'` for V2.

**Proposed table set (EXPANDED 2026-05-11 post-payload-inspection):**

**Core ingest tables:**
- `service_fee` — long format, one row per (service_id, age_band, session_type, as_of_date, source). Joins to `services.service_id`. Zero-fee permitted (sentinel for offered-without-price). PK includes source for cross-source dedup. **NEW columns:** `fee_type` (TEXT — e.g. 'ZCDC' fee classification from `historicalFees[*].type`), `inclusions` (TEXT — for currentFees-derived rows).
- `service_regulatory_snapshot` — one row per (service_id, snapshot_date, source). Append-only; supports NQS trajectory analysis. **EXPANDED columns:**
  - Regulatory: `nqs_overall_rating`, `nqs_overall_issued`, `nqs_prev_overall`, `nqs_prev_issued` (trajectory), `nqs_area_1` … `nqs_area_7` (7 quality area ratings — child-safety surface substrate)
  - CCS state: `ccs_data_received` (BOOL), `ccs_revoked_by_ea` (BOOL — **CCS revocation as live credit indicator** per PRODUCT_VISION §9 / Strengthening Regulation Bill 2025)
  - Operational state: `is_closed` (BOOL), `temporarily_closed` (BOOL), `last_regulatory_visit` (TEXT, MM/YYYY), `last_transfer_date_starting_blocks` (TEXT — vs `services.last_transfer_date` for cross-validation)
  - Provider sub-block (denormalised at snapshot for trajectory traceability): `provider_status`, `provider_approval_date`, `provider_ccs_revoked_by_ea`, `provider_trade_name`
  - Operating hours (sparse but cheap): `hours_<monday|tuesday|…|sunday>_open` + `hours_<day>_close` (14 columns; NULL when closed that day)
  - Web/contact enrichment: `website_url`, `phone`, `email` (current-as-of-snapshot)
- `service_enforcement_action` (NEW table) — long format, one row per (service_id, action_id, level, source) where `level` ∈ {'service', 'provider'}. Columns: `action_id` (Starting Blocks integer ID), `action_date`, `action_type` (e.g. 'Compliance notice issued'), `level`, `source`, `first_observed_at`, `last_observed_at`. Append-only; idempotent on (action_id, level, source). Both service-level enforcementActions[] and provider-level enforcementActions[] flow into this table.
- `service_condition` (NEW table) — long format, one row per (service_id, condition_id, level, source). Columns: `condition_id` (Starting Blocks 'CON-XXXXX' ID), `condition_text` (TEXT — full text per "objects not placed in a manner that may allow a child to climb..." example), `level` ∈ {'service', 'provider'}, `first_observed_at`, `last_observed_at`. Same idempotency.
- `service_vacancy` (NEW table) — vacancy snapshots, long format. One row per (service_id, age_band, observed_at, source). Columns: `vacancy_status` (TEXT — captures both populated detail and 'no_vacancies_published' sentinel), `vacancy_detail_json` (TEXT — full sub-payload preserved for V2 if vacancy shape varies). Append-only; longitudinal across the weekly refresh cadence (D-4) — first forward-looking demand-side signal at centre level.

**Operator-group identity (NEW capability):**
- `large_provider` (NEW table) — operator-group dimension. PK `large_provider_id` (Starting Blocks group `_id`). Columns: `large_provider_id`, `name` (e.g. 'Guardian Early Learning'), `slug`, `first_observed_at`, `last_observed_at`, `source`.
- `large_provider_provider_link` (NEW table) — many-to-many link between Starting Blocks `largeProvider` groups and `provider_approval_number`. Columns: `large_provider_id`, `provider_approval_number`, `provider_name_at_observation`, `first_observed_at`, `last_observed_at`. Closes the gap that current `services` / `entities` / `groups` cannot resolve "Guardian operates 12 provider entities + N services nationally as one operator group".
- New column on `services`: `large_provider_id` (TEXT, NULL where service not part of a Starting Blocks large provider group). FK to `large_provider`. Populated at ingest time via service's payload. Enables Group page (OI-NEW-17) operator-network rollups. Marginal schema change to existing `services`; STD-08 backup discipline applies.

**Provenance / discovery:**
- `service_external_capture` — provenance / raw payload. One row per (service_id, source, fetched_at). SHA-256 dedup against latest. Stores full `__NEXT_DATA__` JSON verbatim per pilot pattern.
- `service_external_target` — discovery layer. One row per (algolia_object_id, source, discovered_at). Optional in production (drive fetch off `services` directly), but kept for reconciliation runs.

**Total new tables in `kintell.db`: 8** (service_fee, service_regulatory_snapshot, service_enforcement_action, service_condition, service_vacancy, large_provider, large_provider_provider_link, service_external_capture, service_external_target — 9 if you count both capture + target separately; service_fee/regulatory/external_capture are evolved-from-pilot, the other 5+ are net-new).

**Schema mutation on existing `services`:** +1 column `large_provider_id` (TEXT NULL).

### D-2 — Identity-resolution rule

**Recommendation: Two-stage resolution at extract time.**
1. Primary: `substr(source.service_approval_no, 1, 11)` matches `services.service_approval_number`. Covers 129/130 of the pilot data. Hard-coded SQL rule, not a fuzzy match.
2. Fallback: name + suburb + postcode match against `services` for SAN-less rows. Covers the 1 pilot edge case (Redfern Occasional Child Care). Manual review queue at first run; 1 row → trivial.
3. UNRESOLVED rows go into `service_external_target` with `service_id IS NULL` — surfaces gracefully without breaking the ingest.

Banks the SAN convention divergence (`service_approval_no` ↔ `service_approval_number`) — new tables use **`service_approval_number`** to match main DB.

### D-3 — Geographic discovery driver

**Recommendation: V1 drives off main `services` table; Algolia is reconciliation, not discovery.**

- V1 ingest pass iterates `services` rows, constructs `slug` from `service_name`, calls `fetch_into_db` with `(service_approval_number, slug)`, writes provenance to `service_external_capture`.
- A separate `algolia_reconcile.py` runs a national lat/lng-radius sweep periodically — surfaces (a) Algolia centres not in main DB (new registrations) → manual review, (b) main-DB services not in Algolia (potential closures or Algolia-index gaps) → tracking row.
- **Defers** the build of a "national geographic discovery driver" (postcode-loop or SA2-centroid-loop) to V2. Saves ~1-2 sess of V1 work for no V1 functional loss.

### D-4 — Refresh cadence

**Recommendation:** Three-tier refresh disciplined by audit_log:
- **Weekly fees** — `service_fee_refresh.py` runs against all 18,223 services. ~7-8 hours runtime at 1.5s polite pacing — runs overnight Saturday. Skips unchanged via SHA-256 dedup; expect ~80-90% unchanged on most weeks.
- **Monthly regulatory** — `service_regulatory_refresh.py` captures NQS / CCS / enforcement state. Append-only snapshots; NQS trajectory analysis works off this.
- **Quarterly Algolia reconciliation** — `algolia_reconcile.py` catches new centres + closures. National coverage; surfaces a delta report.

Each refresh writes audit_log rows per STD-11 / DEC-62 canonical schema. Action naming `commercial_layer_<verb>_v1` (e.g. `commercial_layer_fee_refresh_v1`).

### D-5 — Audit_log + STD-08 discipline

**Recommendation:**
- Every schema migration writes audit_log row + pre-mutation STD-08 backup (`data/pre_commercial_layer_<step>_<ts>.db`)
- Every ingest run writes one audit_log row per source per refresh-batch (rolls up the per-row activity into a single high-level audit entry; per-row provenance lives in `service_external_capture`)
- Every refresh run writes a START + END audit_log pair so the duration / counts are visible
- audit_log row counter starts at the next available id (post-OI-NEW-21 = 175; this work likely lands at 176-180+ depending on scope)

### D-6 — Centre page integration deferred to v2

**Recommendation:** Ship the data infrastructure now; defer render placement to the **Centre v2 joint design pass** that follows this work. Per `project_centre_v2_redesign.md`, Centre v2 Layer 5 (institutional signal matrix) is the natural home for daily-rate as a peer signal alongside other metrics. Forcing it into Centre v1's existing layout would duplicate work when v2 lands soon.

**Caveat:** if the v2 design pass slips, ship a minimal Centre v1 surface for daily-rate as a Lite row in the Catchment Position card (current pattern) under a CONTEXT row weight. Don't over-invest.

### D-7 — Pilot folder migration off Google Drive

**Recommendation:** Migrate the pilot folder onto local disk **as part of this work**. Two paths:
- **(a)** Copy `G:\My Drive\Patrick's Playground\childcare_market_spike\` → `C:\Users\Patrick Bell\remara-agent\commercial_layer\` and reference scripts from the main repo. Pro: pilot pattern preserved as reference. Con: duplicates code that's about to be replaced.
- **(b)** Decommission the pilot DB once the main-DB ingest lands. Reusable code (`fetch.py`, `extract.py` payload-mapping logic) gets ported into a new `commercial_layer_fetch.py` / `commercial_layer_extract.py` in the main repo. Pilot folder archived to local disk for traceability.

**Recommendation: (b).** The pilot served its scoping purpose; production code should live in the main repo with full `proc_helpers.py` / STD-11 / STD-30 integration, not parallel-copied. Archive the pilot folder to `C:\Users\Patrick Bell\childcare_pilot_archive_2026-05-11\` as snapshot.

### D-8 — Algolia credential management

**Recommendation:** Inherit pilot pattern. Hardcoded constants at the top of `commercial_layer_fetch.py` (or wherever the discovery code lands), with refresh procedure documented in module docstring. **Smoke test before each refresh run** — first call probes Algolia, expects HTTP 200 + non-zero hits; aborts if HTTP 403 or empty result with clear log message pointing to the refresh procedure. Closes OI-NEW-4.

Why not env-var: the Algolia keys are public values from the JS bundle, not secrets. Hard-coding them is honest about what they are. STD-9 PYTHONIOENCODING discipline still applies for the script runs.

### D-9 — Stream framing / DEC numbering

**Options for framing:**
- **(A)** "Daily Rate Integration" (per Patrick's session pickup framing) — narrow, accurate to the headline use
- **(B)** "Stream F — Pricing & Regulatory" (peer to A-E from DEC-79) — frames it as the sixth strategic stream, matches the cross-cutting nature of the underlying data
- **(C)** "Commercial Layer V1" (per MODULE_SUMMARY framing) — broadest, captures fees + regulatory + future PropCo evidence

**Recommendation: hybrid label — DEC-83 = "Commercial Layer V1: Daily-Rate Integration (Pricing & Regulatory Snapshot from Starting Blocks)".** Headline "daily-rate" preserves Patrick's framing for v2 design ratification. "Commercial Layer V1" honours MODULE_SUMMARY's positioning and forward-compat for Care for Kids / future sources. "Pricing & Regulatory Snapshot" makes the regulatory data piggyback explicit (otherwise it's invisible to readers expecting just fee data).

DEC-83 is the next available number (DEC-82 minted 2026-05-10 PM s2 for primary-source-first principle).

---

## 3. Effort estimate (post-ratification)

Assuming D-1=(C), D-2=stage-1+fallback, D-3=services-driven, D-4=three-tier, D-5=full STD-11+STD-08, D-6=defer-to-v2, D-7=(b), D-8=smoke-test pattern, D-9=DEC-83:

| Step | Effort | Notes |
|---|---|---|
| DEC-83 mint + design doc finalise | 0.1 sess | Append to canonical DECISIONS.md; ratify this doc |
| Schema migration script (`migrate_commercial_layer_schema.py`) — 8-9 new tables + indexes + 1 column on `services` + audit_log row | 0.3 sess | Patcher pattern STD-10; pre-mutation STD-08 |
| `commercial_layer_fetch.py` + `commercial_layer_extract.py` (port pilot logic; wire to main DB; STD-11 integration; expanded extraction across all HIGH+MEDIUM fields + vacancy snapshots + largeProvider block + enforcement/conditions detail) | 0.7 sess | Significant expansion vs pilot extract.py — 8 destination tables, idempotency rules per table, level discriminators, hours unwrap |
| Initial production ingest (130 pilot centres → main DB; full validate; spotcheck across rich-data centres incl. Guardian large-provider) | 0.2 sess | Confirms join rule + extraction completeness across all 8 tables |
| `algolia_reconcile.py` (lightweight, V1 surface only) | 0.2 sess | Single national-radius query; delta report |
| End-of-session monolith STD-35 + commit | 0.1 sess | |
| **TOTAL** | **~1.6-1.7 sess** | (was 1.1 pre-expansion) |

National scale-up (running ingest against all 18,223 services, weekly refresh wiring) is **deferred — V1 ships with the 130-centre proof and infrastructure**. National scale-up = +0.5 sess later when refresh discipline is tested.

After this lands → Centre v2 joint design pass runs with daily-rate data in hand.

---

## 4. Risk register

| Risk | Likelihood | Mitigation |
|---|---|---|
| Algolia key rotated mid-build | Low | Smoke test pattern (D-8); 5-min refresh procedure documented |
| SAN join rule misses edge cases beyond Redfern | Low | Full-scale ingest against 18,223 services validates rule empirically; manual review queue for unmatched |
| Pilot fee data is stale (last fetched 2026-04-28) by national-scale rerun | Certain | Re-fetch all 130 + new ones; idempotent SHA-256 dedup means no harm |
| Google-Drive write-loss recurs during this session's verification | Medium | Run any writes from local disk only; never touch G: drive in production code |
| Centre v2 design pass slips | Low-Medium | D-6 caveat: minimal Centre v1 surface as fallback |
| ACECQA shifts position on programmatic Algolia use | Low | Pilot scope was acceptable per MODULE_SUMMARY §3; production-scale refresh-scheduling is the threshold to revisit. Bank as risk; don't pre-emptively engage |
| audit_log row count balloons with per-row provenance | Low | D-5 design rolls up into batch audit rows; per-row provenance lives in `service_external_capture`, not audit_log |

---

## 5. What this DEC-83 does NOT decide

- **Care for Kids second source.** Forward-compat designed in (D-1 source column), but actual integration is V2.
- **National refresh scheduling automation** (cron / Windows Task Scheduler integration). Manual run for V1; automation V2.
- **Excel export of fee data.** OI-NEW-15 Excel export framework is the home; `service_fee` becomes one of its source tables.
- **Centre v2 institutional signal matrix layout.** This work supplies the data; v2 design pass decides the surface.
- **Per-source authority weighting** for multi-source reconciliation. Single source for V1.

---

## 6. Open questions for Patrick (please ratify or object)

| ID | Question | My recommendation |
|---|---|---|
| D-1 | Schema namespace? | (C) Generic commercial-layer with `source` discriminator |
| D-2 | Identity-resolution rule? | Stage-1 LEFT(11) match + Stage-2 fuzzy fallback for 1 edge case |
| D-3 | Geographic discovery driver V1? | Drive off `services` table; Algolia for reconciliation only |
| D-4 | Refresh cadence? | Weekly fees / monthly regulatory / quarterly Algolia reconcile |
| D-5 | Audit_log + STD-08 discipline? | Full per STD-11 / DEC-62 / STD-08 canonical patterns |
| D-6 | Centre page integration? | Defer to Centre v2 joint design pass; v1 fallback if v2 slips |
| D-7 | Pilot folder disposition? | Decommission; archive to local disk; port reusable code into main repo |
| D-8 | Algolia credential management? | Inherit pilot pattern; smoke-test on every refresh run; closes OI-NEW-4 |
| D-9 | DEC-83 framing? | "Commercial Layer V1: Daily-Rate Integration (Pricing & Regulatory Snapshot from Starting Blocks)" |

Once D-1 through D-9 are closed, RATIFIED SUMMARY at top gets populated and DEC-83 mint follows the precedent of DEC-82 (canonical DECISIONS.md append + cross-references in PRODUCT_VISION.md / ROADMAP.md / CENTRE_PAGE_V1_5_ROADMAP.md / OPEN_ITEMS.md).

---

## 7. Appendix — probe data

**Pilot DB schema (verbatim from `_init_db.py` + Stage 3 amendment):**
- `pilot_target` (ulid PK, pilot_sa2_label, name, slug, suburb, state, postcode, lat, lng, distance_m, discovered_at, algolia_index, algolia_query_params, raw_hit_json) — composite PK (ulid, pilot_sa2_label)
- `raw_payload` (fetch_id PK auto, ulid, source_url, fetched_at, http_status, payload_json, payload_sha256, extractor_version)
- `centre` (ulid PK, service_approval_no, provider_approval_no, name, address_full, suburb, state, postcode, lat, lng, phone, email, service_type, ccs_approved, nqs_overall_rating, nqs_rating_date, last_regulatory_visit, enforcement_count_2y, pilot_sa2_label, fetch_id_latest)
- `centre_fee` (ulid, age_band, session_type, fee_aud, as_of_date, inclusions, fetch_id) — PK (ulid, age_band, session_type, as_of_date)
- `schema_meta` (schema_version, created_at, notes)

**Code mappings inherited (no change for V1 main-DB tables):**
- Age bands: `0-12m`, `13-24m`, `25-35m`, `36m-preschool`, `school-age`
- Session types: `full_day`, `half_day`, `before_school`, `after_school`, `hourly`, `session`, `weekly`, `daily` (last 3 observed-but-rare)
- NQS ratings: `Meeting NQS`, `Exceeding NQS`, `Working Towards NQS`, `Significant Improvement Required`, `Provisional`, `Not yet rated`, `Out of scope`, `Not rated`

**Pilot DB invariants — verified PASS at 2026-05-11 probe:**
1. Every centre has a ULID — PASS (0 missing)
2. Every centre has a name — PASS (0 missing)
3. Every fee non-negative — PASS (0 negative; 180 zero-fee preserved as sentinel)
4. Every centre_fee row's ULID exists in centre — PASS (0 orphans)
5. Every centre.fetch_id_latest resolves to raw_payload — PASS (0 orphans)
6. All age_band codes mapped — PASS (0 unmapped)
7. All session_type codes mapped — PASS (0 unmapped)
8. All NQS rating codes mapped — PASS (0 unmapped)

**Algolia configuration (preserved from `discover.py`, public values):**
- ALGOLIA_APP_ID = "CGQW4YLCUR"
- ALGOLIA_API_KEY = "59d33900544ce513400031e6bff95522"
- ALGOLIA_INDEX = "production_services"
- HITS_PER_PAGE = 25
- POLITE_SLEEP_S = 0.5

**Main DB pre-DEC-83 state:**
- 36 user tables, ~570 MB, audit_log latest row 175 (`sa2_history_rebuild_v3`)
- 18,223 services, 18,203 with sa2_code (99.89%), 17,882 with lat/lng
- All SANs in canonical SE-XXXXXXXX form, length 11
- ~30 timestamped backups in `data/` (~8.5 GB cumulative — OI-12 still open)

---

*End of design doc. Patrick: please ratify D-1 to D-9 (or object to specific items) so we can mint DEC-83 and proceed to schema migration.*
