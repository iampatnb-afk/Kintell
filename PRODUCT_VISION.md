# Product Vision — Novara Intelligence

*Last updated: 2026-05-09. Tier-2 strategic doc. Authoritative source for product framing, audience, positioning, and the V1 → V2 → V3 horizon. Locked by DEC-79.*

---

## 1. What we're building

**Novara Intelligence** is an Australian childcare asset & portfolio intelligence platform. It turns the structural, demographic, regulatory, workforce, and property dimensions of the Australian childcare sector into auditable, explainable, institutional-grade decision-support intelligence.

It is not a mapping tool. It is not a CRM. Mapping tools (GapMaps, Qikmaps) and childcare management systems (OWNA, Storypark, Procare) operate below this layer. Novara Intelligence sits *above* them and serves the people making decisions on assets, portfolios, capital allocation, and policy.

The single biggest meta-theme we will hold to:

> **Avoid building a bloated feature-heavy childcare app. Build a clean, explainable intelligence system that institutions trust.**

---

## 2. Who it's for

| Audience | Decision they make | What they need |
|---|---|---|
| Lenders (banks, non-banks, private credit) | Origination, pricing, monitoring, refinance | Catchment supply/demand, operator track record, NQS trajectory, fee sustainability, workforce risk, PropCo confidence |
| Institutional investors / PE | Acquisition, portfolio allocation | Operator quality, market saturation, deal comps, growth pipeline, sponsor benchmarks |
| Large operators (FP + NFP) | Site selection, expansion, M&A, operations | Competitor scan, catchment depth, demographic fit, workforce constraints, community context |
| Valuation firms | Going-concern + freehold + leasehold valuations | Fee comps, occupancy comps, transaction comps, regulatory standing |
| Property funds | Property acquisition, portfolio management | PropCo / OpCo separation, lease covenants, on-market monitoring, transaction intelligence |
| Debt providers | Credit screen, monitoring | Same as lenders, with deeper covenant/watchlist focus |
| Advisory professionals | Strategy, transactions, capital raising | All of the above, packaged for client work |

The product is **the same product** for all of these audiences. Different audiences see the same data through audience-relevant lenses, not different product experiences.

**Not the audience:** parents looking for childcare. Educators. Government policy desks (though they may use it). Children. The product is decision infrastructure for institutional and commercial market participants.

---

## 3. Positioning

**Core positioning statement:** "The most complete childcare asset & portfolio intelligence system in Australia."

**Reference point:** GapMaps and Qikmaps are at ~$1,500/user/month. They are mapping tools. We are not. The institutional decision-support frame is what we trade on.

**What we are:**
- A structured, auditable, explainable intelligence layer over the sector
- Per-centre, per-catchment, per-operator, per-property views
- Cross-cutting dimensions: structural, demographic, regulatory, workforce, property, commercial
- Institutional-grade exports — workbook-ready intelligence, not dashboard screenshots
- Confidence-aware (no false certainty; verified vs disclosed vs inferred vs unknown)

**What we are NOT:**
- A mapping tool (maps are supporting context, not primary UI — DEC-71 architecture stands)
- A childcare CRM
- A consumer-facing site
- A scoring product or ranking product
- An advocacy platform
- A general business intelligence dashboard

---

## 4. Build philosophy

Locked by DEC-79. These are non-negotiable framing rules for every decision we make:

1. **Institutional decision infrastructure from day one.** ISO 27001 / SOC 2 readiness artefacts in V1; certification deferred to V2.
2. **Auditability and explainability are first-class properties.** Every metric and signal traceable to source. The DER tooltip pattern (DEC-12, DEC-17, STD-34) extends to every new surface.
3. **Objective measures only.** ABS-derived where possible. Calibration nudges only (per STD-34). Calibration must always surface its rule_text.
4. **No opaque scoring. No subjective rankings. No moralised language.** This is not a credit-rating product. It is not an advocacy product.
5. **Honest absence over imputed presence (P-2).** When the data isn't there, render silent absence. Never fake a value.
6. **Extend existing structures.** Avoid feature sprawl. The additive overlay default (DEC-11) and the three-temporal-mood architecture (DEC-32) absorb most new work.
7. **Confidence is visible.** When we infer, we say so. When we verify, we say so. When we don't know, we say that too.
8. **Probe before code (DEC-65).** Non-trivial work starts with recon → design doc → decision closure → code.

---

## 5. Pricing model (V1)

**Two tiers initially:**

| Tier | Audience | Approx pricing | What's included |
|---|---|---|---|
| Entry / Replacement | Operators, advisors, smaller lenders | (TBD — undercut GapMaps/Qikmaps) | Centre, Catchment, Group surfaces; standard demographic/workforce/regulatory overlays; basic Excel export |
| Institutional | Lenders, PE, valuers, property funds | Premium tier | Everything in Entry + PropCo Property Intelligence + on-market intelligence + portfolio-level lenses + advanced Excel exports + audit-ready provenance |

PropCo Property Intelligence is the institutional moat. Strong commercial opener.

Pricing decisions deferred to commercial readiness pass closer to V1 ship.

---

## 6. The five new streams (locked into V1 and V2)

Captured here as the architectural overlay over the existing layered architecture (Phase 0–4 from the earlier project arc).

### Stream A — Educator visa / overseas educator supply (V1)

**Type:** extension of the existing Workforce layer, NOT a new module.

**Purpose:** strengthen Novara's understanding of educator supply constraints and regional workforce resilience.

**Geography:** SA4 / state (or whatever government data supports defensibly).

**Outputs:**
- Sponsored educator share
- Workforce dependency signal
- Training pipeline vs workforce demand
- Workforce resilience signal

**Integration points:**
- Existing Workforce supply context block on centre page (DEC-76)
- Operator-level workforce summaries
- Centre Summary workforce signal where data supports

**Discipline:**
- Objective, explainable, institutionally framed
- No speculative behavioural assumptions
- No direct centre-level attribution unless data genuinely supports it
- No politically loaded language

**Sequencing:** recon first — review existing workforce structures, identify integration point, assess government data granularity (Home Affairs visa stats, JSA labour-market data, ABS occupation tables), propose lightweight implementation before coding. Likely a Layer 4.5 or Workforce-extension scope item.

### Stream B — NFP perspectives integrated into existing structure (V1)

**Type:** extension of existing analytical framework, NOT a separate NFP module / page / homepage.

**Purpose:** describe community complexity, inclusion exposure, service intensity, social impact context — using objective and explainable data — across the same surfaces commercial users see.

**Inputs (already in or coming):**
- SEIFA (already in)
- NES / language diversity (NES in via A2; language coming)
- ATSI (T07 in A10, next session)
- Single-parent households (T19 in A10, next session)
- Workforce constraints (DEC-76 + Stream A)
- Regional access considerations (ARIA+)

**Derived signals (proposed):**
- Inclusion intensity
- Community complexity
- High-access-need catchments
- Workforce-constrained communities
- Culturally diverse service areas

**What NOT to build:**
- "NFP scores"
- Subjective rankings
- Separate workflows for NFPs
- Duplicate demand/supply logic
- Political or advocacy-style language

**Integration points:**
- Centre page panels (Catchment Position, Community Profile new in C8)
- Operator-level summaries
- Existing derived signal framework

**Sequencing:** recon first — identify where signals naturally fit in existing pages, identify overlap with current signals, propose lightest implementation.

### Stream C — Childbearing-age cohort + marital-status depth (V1)

**Type:** demographic extension; partly already on the V1.5 plan.

**Purpose:** address gaps in centre-page / catchment-page demographic depth around reproductive-age and household composition.

**Already on the V1.5 plan:**
- Parent cohort 25–44 SA2 series (A3) — covers reproductive-age population
- Single-parent household share (T19, in A10) — covers part of marital status

**Genuinely new under Stream C:**
- Marital status beyond single-parent share (married with dependents, de facto, separated)
- Forward-looking fertility / reproductive-age share as a demand indicator distinct from current 0–4 population
- Household composition (couples-with-children share, etc.)

**Sources:** Census TSP tables (T01-T03 family composition; T07-T08 already in A10; T05 marital status).

**Integration points:**
- Catchment Position card (additional Lite rows or Community Profile panel)
- Future Catchment page

### Stream D — PropCo / Property Intelligence Module (V1, premium tier)

**Type:** new schema layer — 7 tables — integrated into existing entity / operator / service graph.

**Purpose:** national childcare property ownership intelligence with confidence levels — who owns the real estate, who operates the centre, whether OpCo and PropCo are related, ownership type (institutional/private/NFP/government/unknown), on-market status, transaction history.

**Strategic principle:** evidence-based, multi-source. Public/low-cost evidence first. Inferred ownership where evidence supports. Targeted title searches only for high-value or unresolved assets. Evidence accumulates over time. Confidence visible.

**Confidence categories:** Verified / Disclosed / High-confidence inferred / Low-confidence inferred / Unknown.

**Schema (per Patrick's planning brief, subject to recon):**
1. `property_assets` — master record per physical property
2. `service_property_links` — links services to properties (with confidence + dates)
3. `property_owner_candidates` — possible PropCo owners (with current_flag + supersession)
4. `property_owner_evidence` — multi-source evidence supporting/challenging ownership
5. `property_title_verifications` — paid title-search results (used selectively)
6. `property_transactions` — sale, listing, on-market events
7. `propco_opco_relationships` — landlord/tenant/related-party links

**V1 scope (per Patrick's brief):**
- Schema design + migration
- Manual CSV import pathway
- Validation queries
- Centre / Operator query outputs
- Excel-export compatibility

**V1 NOT scope:**
- Web scraping
- Automated inference engine
- Paid title-search integration
- CoreLogic / Cotality integration
- Parcel geometry
- Map UI
- On-market alerting automation
- Valuation engine

**UI surfaces (V1):**
- Centre page: ownership confidence row (verified / disclosed / inferred / unknown), owner type, evidence count, latest evidence date, on-market flag, recent sale flag, PropCo / OpCo relationship type
- Operator page: linked properties count, % with known owner, landlord concentration, institutional landlord exposure, related-party PropCo exposure, unknown ownership share, on-market assets in portfolio
- Excel export: dedicated workbook sheets per table

**Cross-cuts with existing structures:**
- Reuse the merge-review evidence-and-candidates pattern (DEC-6/7/8, `propose_merges.py`)
- Confidence model maps to OBS/DER/COM (DEC-12)
- SA2 alignment via `services.sa2_code` (already polygon-backfilled per DEC-70)
- Audit-log discipline (STD-11, DEC-62) covers all 7 tables
- Manual CSV import follows the Layer-2 ingest pattern (Step 1 / Step 5 / Step 8 precedents)

**Sequencing (per Patrick's brief — planning only, no code yet):** recon → schema design → migration plan → manual import pathway → validation plan → centre/operator query outputs → Excel-export hooks. Decision before code. Becomes DEC-80 candidate when locked.

### Stream E — SA2 Border Exposure V1 proxy (V1)

**Type:** new table + Python build module + centre-page CONTEXT row.

**Purpose:** quantify whether a centre sits meaningfully within a single SA2 or spans multiple SA2s. V1 proxy — geometric only, NOT a true catchment model. Flags when SA2-based metrics may be misleading.

**Method (V1):**
- 2 km buffer around each service (lat/lng)
- Intersect with ABS SA2 polygons (ASGS_2021, already on disk)
- Compute per-SA2 share by area
- Classify into LOW / MEDIUM / HIGH / MULTI_SA2 bands

**Outputs (per service):**
- home_sa2_code, home_sa2_share_pct, dominant_sa2, dominant_sa2_share_pct, second_sa2, second_sa2_share_pct, number_of_sa2s_over_10pct, total_sa2s_intersected, border_exposure_band, calculation_method, calculated_at

**New table:** `service_sa2_border_exposure` (single row per service, rerunnable).

**Naming convention rule:** do NOT use "catchment" in new field names. Use `sa2_exposure` / `sa2_overlap` / `boundary_exposure`. Reserve "catchment" for V2 true catchment outputs. Existing `service_catchment_cache` is grandfathered.

**Centre page integration:** new CONTEXT row in Catchment Position card. Label "SA2 boundary exposure". Tooltip explicitly flags it as a simple geographic proxy with V2 catchment modelling coming.

**Cross-cuts:**
- Complementary to OI-30 / OI-33 (SA2 coverage outliers — small inner-city slivers and rural boundaries are often the same SA2s flagged HIGH or MULTI_SA2 here)
- `shapely` / `geopandas` already in venv (used in Step 1c polygon overwrite)
- ABS polygon already on disk
- Becomes DEC-81 candidate when locked

**V1 deliverable (per Patrick's brief — implementation-grade):**
- `build_service_sa2_border_exposure.py`
- `service_sa2_border_exposure` table + indexes
- Idempotent execution (DELETE + INSERT)
- Sample output for 3 services (log/print)
- Centre page CONTEXT row

---

## 7. Cross-cutting V1 work

These are not "streams" but they cut across the streams and need explicit V1 scope:

### Excel Export Framework (V1, DEC-candidate)

Institutions need portable intelligence, not just dashboards. V1 deliverable.

**Scope:**
- Repeatable workbook structures
- Standardised templates per object type (Centre, Operator, Catchment, Group, PropCo)
- Transaction-ready outputs
- Audit-friendly (provenance row per fact, source citation column)
- Avoid screenshot-and-extract workflows

**Will be locked as DEC when scoped.**

### Catchment Page (V1)

Cascades from centre page metrics. New surface. Reuse Position card patterns. Should absorb Stream C demographic depth, Stream B NFP overlay signals, and Stream E border exposure summary.

### Group Page (V1)

Sits above catchment. Operator-network views, exposure summaries, portfolio lens. Picks up Stream D PropCo portfolio signals and Stream A workforce dependency signal at portfolio level.

### Brand identity rename pass (V1, OI-NEW-6)

Visible "Novara Intelligence" everywhere — README, doc headers, code comments, page titles. Filesystem and DB names stay (`kintell.db`, `remara-agent/`) for now. Brand identity ≠ filesystem identity for this pass.

### Institutional readiness foundations (V1)

Not certification — readiness artefacts. Audit trail (already strong via STD-11/30/DEC-62). Methodology documentation (extend GLOSSARY.md / DATA_INVENTORY.md to be customer-readable). Privacy governance baseline. Multi-tenancy / auth design pass for V2 deployment.

---

## 8. V1 → V2 → V3 horizon

### V1 — target ~Sept 2026 (3–4 months from 2026-05-09)

**Centre page completion:**
- A10 + C8 Demographic Mix bundle (next session)
- A3 parent cohort 25–44, A4 schools, A5 subtype-correct denominators, A6 SALM-extension
- B-pass banding for new metrics
- C2-other / C6 render polish
- Stream C demographic depth extensions (marital status / fertility)

**New surfaces:**
- Catchment page
- Group page

**New layers / overlays:**
- Stream A — Educator visa / overseas educator supply
- Stream B — NFP overlay framework (derived signals on existing pages)
- Stream D — PropCo Property Intelligence (manual evidence pathway)
- Stream E — SA2 Border Exposure V1 proxy
- Demand-intelligence overlays (WFH, country of origin, language diversity — extends A10 / T08)

**Cross-cutting V1:**
- Excel export framework
- Brand identity rename pass
- Institutional readiness foundations
- Multi-tenancy / auth design (architecture only; deployment in V2)

### V2 — fast-follow (post-V1)

- True centre-level catchment model (supersedes Stream E V1 proxy — drive-time polygons, population-weighted overlays, competitive gravity, integrated with `service_catchment_cache`)
- DA / pipeline tracking
- Operator change tracking + quality timeline history (OI-21 evolved)
- Acquisition quality analysis
- Property transaction intelligence (Stream D extensions — automated inference engine, on-market alerting)
- Workforce dependency modelling deeper
- Competition overlays (per-centre competitive gravity)
- Valuation overlays
- Map UI as supporting context (DEC-71 honoured — bespoke SVG primary, Chart.js for trends, maps as supplementary visualisation)
- Multi-tenancy / hosted infrastructure deployment
- ISO 27001 / SOC 2 formal readiness pass

### V3 — 12+ months horizon

- On-market childcare assets monitoring (live data feeds)
- Selective paid title-search integration (premium feature)
- CoreLogic / Cotality integration (commercial dataset)
- Multi-industry positioning expansion — Novara Intelligence as broader analytics platform (aged care? early learning? other regulated services?)

---

## 9. Cross-cutting risks (tracked, sequenced)

| Risk | Impact | Sequencing implication |
|---|---|---|
| 2026 Census, Aug 2026 (data release Jun 2027) | SA2 boundaries WILL change | Plan a Q3 2027 data refresh project (OI-NEW-3) |
| Workforce funding cliff Nov 2026 | Operators face simultaneous subsidy step-down + ~27% wage step-up | Model pricing scenarios pre-Nov 2026 (OI-NEW-2) |
| Strengthening Regulation Bill 2025 (CCS revocation as live risk from 31 Jul 2025) | Single-name credit risk has changed shape | NQS rating trajectory becomes a leading credit indicator — already surfaces in centre page; verify visual prominence |
| ABS Community Profiles retiring | Code dependent on it will break | Audit Layer 2 for dependencies (OI-NEW-4) |
| SEEK / Indeed anti-scraping hardened | If `module5_news.py` or workforce ingests pull directly, expect maintenance | Audit (OI-NEW-5) |
| Starting Blocks scraper drift | Algolia method may shift or harden | Smoke test before next production run (OI-NEW-4) |
| "70% break-even" anchor mis-cited to PC | DEC-77 cites PC + Strategic Insights + Credit Brief; the 70% number is industry benchmark, not PC | Provenance correction (OI-NEW-1) |

---

## 10. Demand-intelligence framing (strategic discipline)

The platform's demographic and behavioural overlays must respect the discipline Patrick has set:

**Childcare demand is fundamentally influenced by:**
- workforce participation
- household structure
- cultural behaviours
- migration patterns
- income and affordability
- local labour-market dynamics
- work-from-home behaviour
- social inclusion characteristics

—not simply population counts.

**The discipline:**
- Objective ABS-derived measures
- Descriptive, not speculative
- Institutionally defensible
- Calibration nudges only — never opaque "risk" scores
- No moralised language
- Avoid speculative behavioural scoring
- Avoid subjective modelling

**Specific guards:**
- **NES / migration** — community context, not behavioural prediction. Future country-of-origin overlays remain descriptive initially.
- **ATSI** — inclusion intensity and community complexity, not "risk". Community composition framing, not demographic risk scoring.
- **WFH** — behavioural overlay, not primary demand metric. Treat as elasticity context.
- **Female LFP** — strong objective demand indicator. Most institutionally defensible single signal.
- **Single parents** — childcare-dependency proxy with reduced informal-care availability. Contextual, descriptive.
- **Fertility / reproductive-age cohort** — forward demand signal distinct from current 0-4 population.

---

## 11. What we deliberately do not build

- Mapping as primary UI
- Composite scores or rankings
- Subjective behavioural / "risk" metrics
- Speculative demographic modelling (e.g. ethnicity-based behavioural scoring)
- Web scraping in production without explicit DEC
- Paid title-search integration in V1
- A separate NFP product experience (Stream B integrates instead)
- Feature sprawl — extend existing surfaces before adding new ones
- Anything new for the legacy `module5_digest.py` / `module6_news.py` email pipeline

---

## 12. Sequencing rule for major scope changes

When something genuinely new lands (a new stream, a new audience, a major regulatory shift), follow this sequence:

1. **Probe** — recon the existing structure for natural integration points (DEC-65)
2. **Decide** — write a new DEC capturing the framing, scope, and consequences
3. **Plan** — update PRODUCT_VISION.md (this doc) and ROADMAP.md
4. **Sequence** — dependency-ordering pass (DEC-65 amendment)
5. **Implement** — additive overlay pattern (DEC-11), patcher discipline (STD-10), pre-mutation backup (STD-08), audit-log INSERT (STD-11)
6. **Verify** — STD-30 invariants, spotcheck, browser smoke test
7. **Refresh docs** — STD-35 end-of-session monolith

This is the same discipline that has held the project together through 79 DECs and 35 STDs. Don't break it for shortcuts.
