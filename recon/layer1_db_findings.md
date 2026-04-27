# Phase 2.5 Layer 1 — DB Recon Findings
_Generated: 2026-04-26T14:25:00_
_DB: `data\kintell.db`_

## All tables in DB
Total tables: 25
  - audit_log
  - brands
  - entities
  - entity_financials
  - entity_snapshots
  - evidence
  - group_snapshots
  - groups
  - intelligence_notes
  - link_candidates
  - metric_definitions
  - model_assumptions
  - people
  - person_roles
  - portfolios
  - properties
  - regulatory_events
  - service_catchment_cache
  - service_financials
  - service_history
  - service_tenures
  - services
  - sqlite_sequence
  - training_completions
  - training_completions_ingest_run

## Inventory of snapshot/history/regulatory tables

### `service_snapshots`
  STATUS: TABLE DOES NOT EXIST

### `entity_snapshots`
  rowcount: 0
  columns (8):
    - snapshot_id                         INTEGER         pk=1 notnull=0
    - entity_id                           INTEGER         pk=0 notnull=1
    - as_of_date                          TEXT            pk=0 notnull=1
    - service_count                       INTEGER         pk=0 notnull=0
    - total_places                        INTEGER         pk=0 notnull=0
    - nqs_profile_json                    TEXT            pk=0 notnull=0
    - has_compliance_action               INTEGER         pk=0 notnull=0
    - created_at                          TEXT            pk=0 notnull=0

### `group_snapshots`
  rowcount: 0
  columns (41):
    - snapshot_id                         INTEGER         pk=1 notnull=0
    - group_id                            INTEGER         pk=0 notnull=1
    - as_of_date                          TEXT            pk=0 notnull=1
    - entity_count                        INTEGER         pk=0 notnull=0
    - brand_count                         INTEGER         pk=0 notnull=0
    - portfolio_count                     INTEGER         pk=0 notnull=0
    - service_count                       INTEGER         pk=0 notnull=0
    - total_places                        INTEGER         pk=0 notnull=0
    - states_covered                      INTEGER         pk=0 notnull=0
    - provider_approval_count             INTEGER         pk=0 notnull=0
    - nqs_excellent                       INTEGER         pk=0 notnull=0
    - nqs_exceeding                       INTEGER         pk=0 notnull=0
    - nqs_meeting                         INTEGER         pk=0 notnull=0
    - nqs_working_towards                 INTEGER         pk=0 notnull=0
    - nqs_sir                             INTEGER         pk=0 notnull=0
    - nqs_unrated                         INTEGER         pk=0 notnull=0
    - concentration_top_sa2_pct           REAL            pk=0 notnull=0
    - concentration_top_state_pct         REAL            pk=0 notnull=0
    - single_pa_share                     REAL            pk=0 notnull=0
    - regulatory_stress_pct               REAL            pk=0 notnull=0
    - kinder_approved_share               REAL            pk=0 notnull=0
    - avg_centre_age_years                REAL            pk=0 notnull=0
    - growth_12m_services                 INTEGER         pk=0 notnull=0
    - growth_12m_places                   INTEGER         pk=0 notnull=0
    - catchments_covered                  INTEGER         pk=0 notnull=0
    - total_catchment_u5_pop              INTEGER         pk=0 notnull=0
    - weighted_avg_u5_pop_per_centre      REAL            pk=0 notnull=0
    - weighted_avg_median_income          REAL            pk=0 notnull=0
    - weighted_avg_seifa_irsd             REAL            pk=0 notnull=0
    - weighted_avg_supply_ratio           REAL            pk=0 notnull=0
    - places_in_balanced_pct              REAL            pk=0 notnull=0
    - places_in_supplied_pct              REAL            pk=0 notnull=0
    - places_in_oversupplied_pct          REAL            pk=0 notnull=0
    - places_in_no_catchment_data_pct     REAL            pk=0 notnull=0
    - centres_in_balanced                 INTEGER         pk=0 notnull=0
    - centres_in_supplied                 INTEGER         pk=0 notnull=0
    - centres_in_oversupplied             INTEGER         pk=0 notnull=0
    - centres_in_deteriorating_catchments INTEGER         pk=0 notnull=0
    - centres_near_new_competitor_12m     INTEGER         pk=0 notnull=0
    - opportunity_catchments_count        INTEGER         pk=0 notnull=0
    - created_at                          TEXT            pk=0 notnull=0

### `regulatory_events`
  rowcount: 0
  columns (10):
    - event_id                            INTEGER         pk=1 notnull=0
    - subject_type                        TEXT            pk=0 notnull=1
    - subject_id                          INTEGER         pk=0 notnull=1
    - event_type                          TEXT            pk=0 notnull=1
    - event_date                          TEXT            pk=0 notnull=1
    - detail                              TEXT            pk=0 notnull=0
    - severity                            TEXT            pk=0 notnull=0
    - regulator                           TEXT            pk=0 notnull=0
    - source_url                          TEXT            pk=0 notnull=0
    - created_at                          TEXT            pk=0 notnull=0

### `service_catchment_cache`
  rowcount: 0
  columns (17):
    - service_id                          INTEGER         pk=1 notnull=0
    - sa2_code                            TEXT            pk=0 notnull=0
    - sa2_name                            TEXT            pk=0 notnull=0
    - u5_pop                              INTEGER         pk=0 notnull=0
    - median_income                       REAL            pk=0 notnull=0
    - seifa_irsd                          INTEGER         pk=0 notnull=0
    - unemployment_pct                    REAL            pk=0 notnull=0
    - supply_ratio                        REAL            pk=0 notnull=0
    - supply_band                         TEXT            pk=0 notnull=0
    - supply_ratio_4q_change              REAL            pk=0 notnull=0
    - is_deteriorating                    INTEGER         pk=0 notnull=0
    - competing_centres_count             INTEGER         pk=0 notnull=0
    - new_competitor_12m                  INTEGER         pk=0 notnull=0
    - ccs_dependency_pct                  REAL            pk=0 notnull=0
    - as_of_date                          TEXT            pk=0 notnull=0
    - created_at                          TEXT            pk=0 notnull=0
    - updated_at                          TEXT            pk=0 notnull=0

### `service_tenures`
  rowcount: 0
  columns (10):
    - tenure_id                           INTEGER         pk=1 notnull=0
    - service_id                          INTEGER         pk=0 notnull=1
    - property_id                         INTEGER         pk=0 notnull=0
    - tenure_type                         TEXT            pk=0 notnull=0
    - lease_start                         TEXT            pk=0 notnull=0
    - lease_term_years                    INTEGER         pk=0 notnull=0
    - options_remaining                   INTEGER         pk=0 notnull=0
    - rent_annual                         REAL            pk=0 notnull=0
    - rent_to_revenue_pct                 REAL            pk=0 notnull=0
    - created_at                          TEXT            pk=0 notnull=0

### `properties`
  rowcount: 0
  columns (10):
    - property_id                         INTEGER         pk=1 notnull=0
    - owner_entity_id                     INTEGER         pk=0 notnull=0
    - address_line                        TEXT            pk=0 notnull=0
    - suburb                              TEXT            pk=0 notnull=0
    - state                               TEXT            pk=0 notnull=0
    - postcode                            TEXT            pk=0 notnull=0
    - lot_plan                            TEXT            pk=0 notnull=0
    - title_reference                     TEXT            pk=0 notnull=0
    - is_freehold                         INTEGER         pk=0 notnull=0
    - created_at                          TEXT            pk=0 notnull=0

### `people`
  rowcount: 0
  columns (7):
    - person_id                           INTEGER         pk=1 notnull=0
    - full_name                           TEXT            pk=0 notnull=1
    - normalised_name                     TEXT            pk=0 notnull=0
    - dob_year                            INTEGER         pk=0 notnull=0
    - is_disqualified                     INTEGER         pk=0 notnull=0
    - created_at                          TEXT            pk=0 notnull=0
    - updated_at                          TEXT            pk=0 notnull=0

### `person_roles`
  rowcount: 0
  columns (9):
    - role_id                             INTEGER         pk=1 notnull=0
    - person_id                           INTEGER         pk=0 notnull=1
    - entity_id                           INTEGER         pk=0 notnull=0
    - service_id                          INTEGER         pk=0 notnull=0
    - role_type                           TEXT            pk=0 notnull=1
    - start_date                          TEXT            pk=0 notnull=0
    - end_date                            TEXT            pk=0 notnull=0
    - ownership_pct                       REAL            pk=0 notnull=0
    - created_at                          TEXT            pk=0 notnull=0

### `financials`
  STATUS: TABLE DOES NOT EXIST

## Silent-bug audit queries

### seifa_decile / sa2_code coverage on active services
```sql
SELECT COUNT(*) AS total,
               COUNT(seifa_decile) AS with_seifa,
               COUNT(sa2_code) AS with_sa2
        FROM services WHERE is_active = 1;
```
Result:
  total | with_seifa | with_sa2
  18223 | 17395 | 0

### transfer_date population on active services
```sql
SELECT COUNT(*) AS active_services,
               SUM(CASE WHEN last_transfer_date IS NOT NULL
                          AND last_transfer_date != ''
                        THEN 1 ELSE 0 END) AS with_transfer
        FROM services WHERE is_active = 1;
```
Result:
  active_services | with_transfer
  18223 | 5826

### entities with active services but group_id IS NULL
```sql
SELECT COUNT(DISTINCT e.entity_id) AS orphan_entities
        FROM entities e
        JOIN services s ON s.entity_id = e.entity_id
        WHERE s.is_active = 1
          AND e.group_id IS NULL;
```
Result:
  orphan_entities
  2320

## Other tables in DB (not in scope but listed for completeness)
  - audit_log                                rowcount=124
  - brands                                   rowcount=349
  - entities                                 rowcount=7143
  - entity_financials                        rowcount=0
  - evidence                                 rowcount=10263
  - groups                                   rowcount=4187
  - intelligence_notes                       rowcount=0
  - link_candidates                          rowcount=823
  - metric_definitions                       rowcount=6
  - model_assumptions                        rowcount=13
  - portfolios                               rowcount=4187
  - service_financials                       rowcount=0
  - service_history                          rowcount=0
  - services                                 rowcount=18223
  - sqlite_sequence                          rowcount=10
  - training_completions                     rowcount=768
  - training_completions_ingest_run          rowcount=1