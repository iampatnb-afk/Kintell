-- ════════════════════════════════════════════════════════════════════
--  KINTELL OWNERSHIP GRAPH — SQLite schema v0.2 (draft)
-- ════════════════════════════════════════════════════════════════════
--
--  v0.2 changes:
--    - group_snapshots: catchment-aggregation fields added (weighted
--      demographic averages, supply-band exposure using Panel 3
--      thresholds, deteriorating-catchment and opportunity flags).
--    - NEW table service_catchment_cache: per-service SA2 metrics
--      cached for fast roll-up queries.
--    - Roll-up notes expanded to cover brand/portfolio/state views
--      as computed queries (same filter pattern, no extra tables).
-- ════════════════════════════════════════════════════════════════════
--
--  Purpose:
--    Single canonical graph of Australian childcare ownership,
--    linking groups → portfolios → brands → entities → services,
--    with full evidence provenance, time-series, and freeform
--    intelligence notes.
--
--  Audiences served from same graph:
--    - Lenders (Remara): group exposure, correlation, regulatory risk
--    - M&A: structural roll-up, brand value, portfolio composition
--    - Operators/developers: competitive positioning, catchment supply
--
--  Design principles:
--    1. Five levels, but Portfolio is optional (collapses to "default"
--       for the ~95% of groups that run a single go-to-market).
--    2. Every substantive fact carries provenance (source, confidence,
--       timestamp, evidence_type). No unattributed data in the tool.
--    3. Time-series tables exist from day one; they may be sparse
--       early on and denser later as snapshots accumulate.
--    4. Financial fields exist but are nullable. Phase 2 data sources
--       (fees, EBITDA proxies) light them up over time.
--    5. Manual actions (link, unlink, note) are first-class, audited,
--       reversible. Human industry knowledge is evidence.
--    6. Soft-delete only (is_active flag + deactivated_at) so audit
--       trail is never broken.
-- ════════════════════════════════════════════════════════════════════


-- ─── 1. CORE HIERARCHY ──────────────────────────────────────────────

CREATE TABLE groups (
    group_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    canonical_name        TEXT    NOT NULL,        -- "Sparrow Group"
    display_name          TEXT,                    -- commercial/marketing name
    slug                  TEXT    UNIQUE,          -- "sparrow-group" (URL-safe)
    is_for_profit         INTEGER,                 -- bool, NULL = unknown
    is_listed             INTEGER,                 -- bool, ASX-listed
    asx_code              TEXT,                    -- if listed
    primary_domain        TEXT,                    -- "sparrowelearning.com.au"
    head_office_state     TEXT,
    ownership_type        TEXT,                    -- 'family','pe','listed','nfp','unknown'
    is_active             INTEGER DEFAULT 1,
    created_at            TEXT    DEFAULT (datetime('now')),
    updated_at            TEXT    DEFAULT (datetime('now')),
    deactivated_at        TEXT
);

CREATE TABLE portfolios (
    portfolio_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id              INTEGER NOT NULL REFERENCES groups(group_id),
    name                  TEXT    NOT NULL,        -- "G8 Premium", "G8 Community"
    positioning           TEXT,                    -- 'premium','mid','value','mixed'
    is_default            INTEGER DEFAULT 0,       -- true for groups with one portfolio
    notes                 TEXT,
    is_active             INTEGER DEFAULT 1,
    created_at            TEXT    DEFAULT (datetime('now')),
    updated_at            TEXT    DEFAULT (datetime('now'))
);

CREATE TABLE brands (
    brand_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    portfolio_id          INTEGER REFERENCES portfolios(portfolio_id),
    group_id              INTEGER NOT NULL REFERENCES groups(group_id),
    name                  TEXT    NOT NULL,        -- "Sparrow Early Learning"
    service_name_prefix   TEXT,                    -- prefix used for brand-match
    domain                TEXT,
    logo_url              TEXT,
    first_centre_opened   TEXT,                    -- ISO date, derived
    pricing_tier          TEXT,                    -- 'premium','mid','value' (when known)
    is_active             INTEGER DEFAULT 1,
    created_at            TEXT    DEFAULT (datetime('now')),
    updated_at            TEXT    DEFAULT (datetime('now'))
);

CREATE TABLE entities (
    entity_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id              INTEGER REFERENCES groups(group_id),   -- nullable: unlinked entities exist
    legal_name            TEXT    NOT NULL,
    normalised_name       TEXT,                    -- lowercase/stripped for matching
    abn                   TEXT    UNIQUE,
    acn                   TEXT,
    entity_type           TEXT,                    -- 'company','trust','partnership','individual'
    registered_state      TEXT,
    registered_postcode   TEXT,
    incorporation_date    TEXT,
    is_trustee            INTEGER,                 -- bool
    trust_name            TEXT,
    is_propco             INTEGER,                 -- bool (freehold holding)
    is_opco               INTEGER,                 -- bool (operating)
    is_fgc                INTEGER,                 -- bool (freehold going concern flag)
    is_active             INTEGER DEFAULT 1,
    created_at            TEXT    DEFAULT (datetime('now')),
    updated_at            TEXT    DEFAULT (datetime('now')),
    deactivated_at        TEXT
);

CREATE TABLE services (
    service_id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id                    INTEGER REFERENCES entities(entity_id),
    brand_id                     INTEGER REFERENCES brands(brand_id),
    service_approval_number      TEXT    UNIQUE,       -- ACECQA SAP (post-Q12022)
    provider_approval_number     TEXT,                 -- ACECQA PA#
    service_name                 TEXT    NOT NULL,
    address_line                 TEXT,
    suburb                       TEXT,
    state                        TEXT,
    postcode                     TEXT,
    sa2_code                     TEXT,                 -- ABS SA2 (when concorded)
    sa2_name                     TEXT,
    lat                          REAL,
    lng                          REAL,
    approved_places              INTEGER,
    approval_granted_date        TEXT,
    last_transfer_date           TEXT,                 -- ACECQA last service approval transfer
    overall_nqs_rating           TEXT,                 -- 'Excellent','Exceeding','Meeting','Working Towards','Significant Improvement Required'
    rating_issued_date           TEXT,
    kinder_approved              INTEGER,              -- bool
    kinder_source                TEXT,                 -- 'acecqa','name','state_dept','manual'
    long_day_care                INTEGER DEFAULT 1,
    is_active                    INTEGER DEFAULT 1,    -- false once deregistered
    created_at                   TEXT    DEFAULT (datetime('now')),
    updated_at                   TEXT    DEFAULT (datetime('now'))
);


-- ─── 2. EVIDENCE & PROVENANCE ───────────────────────────────────────

-- Every substantive field value has an evidence trail. Not every read
-- surface needs to show it, but every UI "i" tooltip reads from here.
--
-- subject_type/subject_id identifies what the evidence is about
--   (e.g. 'entity_group_link' for "this entity belongs to this group")
-- field_name is what was asserted
--   (e.g. 'group_id' on entity, or 'brand_id' on service)

CREATE TABLE evidence (
    evidence_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_type          TEXT    NOT NULL,        -- 'group','entity','service','link'
    subject_id            INTEGER NOT NULL,
    field_name            TEXT,                    -- NULL when evidence supports whole record
    asserted_value        TEXT,                    -- stringified value being evidenced
    source_type           TEXT    NOT NULL,        -- see below
    source_url            TEXT,                    -- specific link if available
    source_detail         TEXT,                    -- "Accessed 2026-04-21; cached snapshot at..."
    confidence            REAL    NOT NULL,        -- 0.0–1.0
    asserted_by           TEXT,                    -- 'system','patrick','<user>'
    asserted_at           TEXT    DEFAULT (datetime('now')),
    superseded_at         TEXT,                    -- set when newer evidence replaces
    notes                 TEXT
);

-- Permitted source_type values (documented, not enforced):
--   'acecqa_snapshot'        PA/SAP/centre facts
--   'acecqa_history'         transfer date, rating history
--   'abr_lookup'             ABN/ACN/entity structure
--   'asic_extract'           director data
--   'operator_website'       scraped centres list
--   'trade_mark_register'    IP Australia
--   'news_article'           press release / media
--   'linkedin'               profile-level employer disclosure
--   'fuzzy_legal_name'       existing linker name-similarity
--   'shared_phone'           existing phone_related link
--   'shared_email_domain'
--   'shared_postal_address'
--   'shared_director'
--   'brand_prefix_match'     service_name starts with brand prefix
--   'manual_link'            user-created link
--   'industry_knowledge'     user-entered intelligence
--   'sale_listing'           business broker disclosure


-- ─── 3. LINK CANDIDATES & REVIEW QUEUE ──────────────────────────────

-- When the auto-linker proposes a relationship, it lands here first.
-- Human review (or auto-accept above threshold) moves it to the graph.

CREATE TABLE link_candidates (
    candidate_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    link_type             TEXT    NOT NULL,        -- 'entity_to_group','service_to_brand','entity_merge'
    from_type             TEXT    NOT NULL,
    from_id               INTEGER NOT NULL,
    to_type               TEXT    NOT NULL,
    to_id                 INTEGER NOT NULL,
    composite_confidence  REAL    NOT NULL,        -- 0.0–1.0
    evidence_json         TEXT    NOT NULL,        -- list of evidence items + weights
    status                TEXT    DEFAULT 'pending', -- 'pending','accepted','rejected','superseded'
    priority              INTEGER DEFAULT 0,       -- higher = reviewed first (hot targets)
    proposed_at           TEXT    DEFAULT (datetime('now')),
    reviewed_at           TEXT,
    reviewed_by           TEXT,
    review_note           TEXT
);


-- ─── 4. AUDIT LOG ───────────────────────────────────────────────────

-- Every state-changing action is logged. Never deleted.

CREATE TABLE audit_log (
    audit_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    actor                 TEXT    NOT NULL,        -- 'system','patrick',etc.
    action                TEXT    NOT NULL,        -- 'create','update','link','unlink','merge','split','note','accept','reject'
    subject_type          TEXT    NOT NULL,
    subject_id            INTEGER NOT NULL,
    before_json           TEXT,
    after_json            TEXT,
    reason                TEXT,
    occurred_at           TEXT    DEFAULT (datetime('now'))
);


-- ─── 5. TIME-SERIES SNAPSHOTS ───────────────────────────────────────

-- Point-in-time aggregates so "what's changed since last visit"
-- and "group trajectory over 3 years" both work. Populated by a
-- scheduled job (weekly for services, quarterly for higher levels).

CREATE TABLE group_snapshots (
    snapshot_id               INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id                  INTEGER NOT NULL REFERENCES groups(group_id),
    as_of_date                TEXT    NOT NULL,
    entity_count              INTEGER,
    brand_count               INTEGER,
    portfolio_count           INTEGER,
    service_count             INTEGER,
    total_places              INTEGER,
    states_covered            INTEGER,
    provider_approval_count   INTEGER,           -- distinct PA#s
    -- NQS distribution
    nqs_excellent             INTEGER,
    nqs_exceeding             INTEGER,
    nqs_meeting               INTEGER,
    nqs_working_towards       INTEGER,
    nqs_sir                   INTEGER,
    nqs_unrated               INTEGER,
    -- derived structural risk signals
    concentration_top_sa2_pct REAL,              -- % places in group's top SA2
    concentration_top_state_pct REAL,
    single_pa_share           REAL,              -- largest PA's share of group places
    regulatory_stress_pct     REAL,              -- % Working Towards or SIR
    kinder_approved_share     REAL,
    avg_centre_age_years      REAL,
    growth_12m_services       INTEGER,           -- net new services last 12 months
    growth_12m_places         INTEGER,
    -- catchment coverage and demographics (places-weighted except where noted)
    catchments_covered        INTEGER,           -- distinct SA2s
    total_catchment_u5_pop    INTEGER,           -- sum across distinct SA2s
    weighted_avg_u5_pop_per_centre  REAL,        -- avg SA2 u5 pop, weighted by places
    weighted_avg_median_income      REAL,
    weighted_avg_seifa_irsd         REAL,
    weighted_avg_supply_ratio       REAL,        -- places-weighted
    -- supply exposure bands (Panel 3 thresholds)
    --   balanced    : supply ratio  <  0.55x   (green)
    --   supplied    : supply ratio  0.55-1.0x  (amber)
    --   oversupplied: supply ratio  >  1.0x    (red)
    places_in_balanced_pct          REAL,
    places_in_supplied_pct          REAL,
    places_in_oversupplied_pct      REAL,
    places_in_no_catchment_data_pct REAL,        -- unmatched SA2 (~22% concordance gap)
    centres_in_balanced             INTEGER,
    centres_in_supplied             INTEGER,
    centres_in_oversupplied         INTEGER,
    -- deterioration + opportunity signals
    centres_in_deteriorating_catchments INTEGER, -- supply ratio rising >0.1x over trailing 4q
    centres_near_new_competitor_12m     INTEGER, -- new competitor approval in same SA2 last 12m
    opportunity_catchments_count        INTEGER, -- strong demographics, group under-represented
    created_at                TEXT DEFAULT (datetime('now'))
);

CREATE TABLE entity_snapshots (
    snapshot_id               INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id                 INTEGER NOT NULL REFERENCES entities(entity_id),
    as_of_date                TEXT    NOT NULL,
    service_count             INTEGER,
    total_places              INTEGER,
    nqs_profile_json          TEXT,              -- serialized rating breakdown
    has_compliance_action     INTEGER,           -- bool
    created_at                TEXT DEFAULT (datetime('now'))
);

CREATE TABLE service_history (
    history_id                INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id                INTEGER NOT NULL REFERENCES services(service_id),
    as_of_date                TEXT    NOT NULL,
    approved_places           INTEGER,
    overall_nqs_rating        TEXT,
    entity_id                 INTEGER,           -- which entity held it on that date
    brand_id                  INTEGER,
    is_active                 INTEGER,
    created_at                TEXT DEFAULT (datetime('now'))
);


-- Per-service catchment snapshot. Single row per service, overwritten
-- when catchment data is refreshed. Exists so group/brand/state roll-ups
-- are a single join rather than a multi-file traversal of the existing
-- catchments.json + sa2_history.json. Historical catchment values live
-- in sa2_history.json as before; this is a query-speed cache.

CREATE TABLE service_catchment_cache (
    service_id                INTEGER PRIMARY KEY REFERENCES services(service_id),
    sa2_code                  TEXT,
    sa2_name                  TEXT,
    u5_pop                    INTEGER,
    median_income             REAL,
    seifa_irsd                INTEGER,
    unemployment_pct          REAL,              -- stub until SALM integrated
    supply_ratio              REAL,              -- places per child under 5, x format
    supply_band               TEXT,              -- 'balanced','supplied','oversupplied','unknown'
    supply_ratio_4q_change    REAL,              -- trailing 4-quarter delta
    is_deteriorating          INTEGER,           -- bool: supply_ratio_4q_change > 0.1
    competing_centres_count   INTEGER,           -- centres in same SA2 excluding this one
    new_competitor_12m        INTEGER,           -- bool: new approval in SA2 last 12 months
    ccs_dependency_pct        REAL,              -- estimated, from catchments.json
    as_of_date                TEXT,
    created_at                TEXT DEFAULT (datetime('now')),
    updated_at                TEXT DEFAULT (datetime('now'))
);


-- ─── 6. INTELLIGENCE NOTES (FIRST-CLASS HUMAN KNOWLEDGE) ────────────

-- Freeform, timestamped, attached to any entity in the graph.
-- Searchable. This is where industry knowledge that no data source
-- can produce lives.

CREATE TABLE intelligence_notes (
    note_id               INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_type          TEXT    NOT NULL,        -- 'group','entity','service','brand','portfolio'
    subject_id            INTEGER NOT NULL,
    body                  TEXT    NOT NULL,
    tags                  TEXT,                    -- comma-separated
    author                TEXT    NOT NULL,
    source                TEXT,                    -- 'meeting','conference','rumour','article','other'
    event_date            TEXT,                    -- when the referenced event happened
    is_pinned             INTEGER DEFAULT 0,
    is_confidential       INTEGER DEFAULT 0,
    created_at            TEXT    DEFAULT (datetime('now'))
);


-- ─── 7. FINANCIAL FIELDS (Phase 2 — nullable in v1) ─────────────────

-- These tables exist so v2 data arrival doesn't require schema change.
-- All rows sparse in v1; one or two early pilots populated manually.

CREATE TABLE service_financials (
    financial_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id            INTEGER NOT NULL REFERENCES services(service_id),
    as_of_date            TEXT    NOT NULL,
    daily_fee             REAL,                    -- A$, from Careforkids or direct
    ccs_dependency_pct    REAL,                    -- derived from catchment
    estimated_occupancy   REAL,                    -- % (proxy from catchment)
    estimated_revenue_pp  REAL,                    -- per-place p.a., A$
    estimated_ebitda_pp   REAL,                    -- per-place p.a., A$
    rent_to_revenue_pct   REAL,                    -- when known
    wages_to_revenue_pct  REAL,                    -- when known
    source_type           TEXT,                    -- 'careforkids','vendor_disclosure','modelled'
    confidence            REAL,
    created_at            TEXT    DEFAULT (datetime('now'))
);

CREATE TABLE entity_financials (
    financial_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id             INTEGER NOT NULL REFERENCES entities(entity_id),
    as_of_date            TEXT    NOT NULL,
    fy_ended              TEXT,
    revenue               REAL,
    ebitda                REAL,
    ebitda_margin_pct     REAL,
    source_type           TEXT,                    -- 'asic_extract','borrower_disclosure'
    confidence            REAL,
    created_at            TEXT    DEFAULT (datetime('now'))
);


-- ─── 8. DIRECTORS & KEY PEOPLE (for signal 10 / group linkage) ──────

CREATE TABLE people (
    person_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name             TEXT    NOT NULL,
    normalised_name       TEXT,
    dob_year              INTEGER,                 -- when known; not full DOB for privacy
    is_disqualified       INTEGER,                 -- ASIC flag
    created_at            TEXT    DEFAULT (datetime('now')),
    updated_at            TEXT    DEFAULT (datetime('now'))
);

CREATE TABLE person_roles (
    role_id               INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id             INTEGER NOT NULL REFERENCES people(person_id),
    entity_id             INTEGER REFERENCES entities(entity_id),
    service_id            INTEGER REFERENCES services(service_id),
    role_type             TEXT    NOT NULL,        -- 'director','shareholder','nominated_supervisor','responsible_person'
    start_date            TEXT,
    end_date              TEXT,
    ownership_pct         REAL,                    -- when known
    created_at            TEXT    DEFAULT (datetime('now'))
);


-- ─── 9. REGULATORY EVENTS ───────────────────────────────────────────

-- NQS changes, compliance actions, enforcement notices, show-cause
-- notices, suspensions, cancellations. All point-in-time with source.

CREATE TABLE regulatory_events (
    event_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_type          TEXT    NOT NULL,        -- 'service','entity' (PA-level)
    subject_id            INTEGER NOT NULL,
    event_type            TEXT    NOT NULL,        -- 'nqs_rating','compliance_notice','show_cause','suspension','cancellation','investigation'
    event_date            TEXT    NOT NULL,
    detail                TEXT,
    severity              TEXT,                    -- 'info','watch','material','critical'
    regulator             TEXT,                    -- 'ACECQA','NSW DE','VIC DET','QLD DESBT',etc.
    source_url            TEXT,
    created_at            TEXT    DEFAULT (datetime('now'))
);


-- ─── 10. PROPERTY (OpCo / PropCo separation, lease, FGC flag) ──────

-- Owned real property connected to services. Supports PropCo detection
-- and freehold-going-concern flag the existing pipeline already computes.

CREATE TABLE properties (
    property_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_entity_id       INTEGER REFERENCES entities(entity_id),
    address_line          TEXT,
    suburb                TEXT,
    state                 TEXT,
    postcode              TEXT,
    lot_plan              TEXT,
    title_reference       TEXT,
    is_freehold           INTEGER,                 -- bool
    created_at            TEXT    DEFAULT (datetime('now'))
);

CREATE TABLE service_tenures (
    tenure_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id            INTEGER NOT NULL REFERENCES services(service_id),
    property_id           INTEGER REFERENCES properties(property_id),
    tenure_type           TEXT,                    -- 'leasehold','freehold_going_concern','freehold_passive'
    lease_start           TEXT,
    lease_term_years      INTEGER,
    options_remaining     INTEGER,
    rent_annual           REAL,                    -- A$ when known
    rent_to_revenue_pct   REAL,                    -- derived when possible
    created_at            TEXT    DEFAULT (datetime('now'))
);


-- ─── INDEXES ────────────────────────────────────────────────────────

CREATE INDEX ix_entities_group          ON entities(group_id);
CREATE INDEX ix_entities_abn            ON entities(abn);
CREATE INDEX ix_entities_norm_name      ON entities(normalised_name);

CREATE INDEX ix_services_entity         ON services(entity_id);
CREATE INDEX ix_services_brand          ON services(brand_id);
CREATE INDEX ix_services_sap            ON services(service_approval_number);
CREATE INDEX ix_services_pap            ON services(provider_approval_number);
CREATE INDEX ix_services_sa2            ON services(sa2_code);
CREATE INDEX ix_services_state_suburb   ON services(state, suburb);

CREATE INDEX ix_brands_group            ON brands(group_id);
CREATE INDEX ix_portfolios_group        ON portfolios(group_id);

CREATE INDEX ix_evidence_subject        ON evidence(subject_type, subject_id);
CREATE INDEX ix_links_status_priority   ON link_candidates(status, priority DESC);

CREATE INDEX ix_group_snapshots         ON group_snapshots(group_id, as_of_date);
CREATE INDEX ix_entity_snapshots        ON entity_snapshots(entity_id, as_of_date);
CREATE INDEX ix_service_history         ON service_history(service_id, as_of_date);
CREATE INDEX ix_service_catchment_sa2   ON service_catchment_cache(sa2_code);
CREATE INDEX ix_service_catchment_band  ON service_catchment_cache(supply_band);

CREATE INDEX ix_notes_subject           ON intelligence_notes(subject_type, subject_id);

CREATE INDEX ix_person_roles_entity     ON person_roles(entity_id);
CREATE INDEX ix_person_roles_person     ON person_roles(person_id);

CREATE INDEX ix_reg_events_subject      ON regulatory_events(subject_type, subject_id, event_date);
CREATE INDEX ix_reg_events_date         ON regulatory_events(event_date);


-- ════════════════════════════════════════════════════════════════════
--  NOTES ON ROLL-UP BEHAVIOUR
-- ════════════════════════════════════════════════════════════════════
--
--  The aggregates at each level (counts, distributions, correlations,
--  catchment exposure) are NOT stored on groups/portfolios/brands
--  directly. At group level, they live in group_snapshots keyed by
--  date. At brand, portfolio, and state level, they are computed on
--  demand by running the same roll-up logic with a different filter.
--
--  Rationale:
--    - Current-state aggregates are always derivable from services +
--      links + service_catchment_cache. Storing them directly means
--      keeping two sources of truth in sync.
--    - Historical aggregates are the whole point of snapshots.
--    - Brand/portfolio/state views share the aggregation function with
--      the group view; only the WHERE clause differs. No extra tables.
--
--  For UI:
--    "current group view"     = latest group_snapshots row
--    "group trajectory"       = full group_snapshots series
--    "what's changed"         = diff between latest two rows
--    "brand view"             = computed roll-up filtered by brand_id
--    "group × state view"     = computed roll-up filtered by group_id
--                               and state (cross-tab)
--    "group × brand view"     = computed roll-up filtered by group_id
--                               and brand_id
--
--  service_catchment_cache is a query-speed cache of per-service SA2
--  metrics. Source of truth remains catchments.json + sa2_history.json
--  (refreshed in the existing weekly pipeline). The cache is
--  overwritten on each refresh and indexed for fast joins. Historical
--  catchment values stay in sa2_history.json and are read from there
--  when building snapshots, not from the cache.
--
--  A refresh routine computes and inserts a new row for each group
--  whenever the catchment cache refreshes or a link changes. Called
--  on demand and by the weekly pipeline.
-- ════════════════════════════════════════════════════════════════════
