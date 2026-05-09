# DB Inventory — `data/kintell.db`

Generated: 2026-05-10T02:20:15
DB size: 615.3 MB
Tables: 37 | Total rows: 1,977,211

Read-only snapshot. Pre-Step-1b reference.

## 1. Tables — row counts

| # | Table | Rows |
|---:|---|---:|
| 1 | `abs_sa2_births_annual` | 34,300 |
| 2 | `abs_sa2_country_of_birth_top_n` | 7,102 |
| 3 | `abs_sa2_education_employment_annual` | 584,630 |
| 4 | `abs_sa2_erp_annual` | 88,344 |
| 5 | `abs_sa2_language_at_home_top_n` | 7,060 |
| 6 | `abs_sa2_socioeconomic_annual` | 161,964 |
| 7 | `abs_sa2_unemployment_quarterly` | 142,496 |
| 8 | `audit_log` | 174 |
| 9 | `brands` | 349 |
| 10 | `entities` | 7,143 |
| 11 | `entity_financials` | 0 |
| 12 | `entity_snapshots` | 0 |
| 13 | `evidence` | 10,263 |
| 14 | `group_snapshots` | 0 |
| 15 | `groups` | 6,507 |
| 16 | `intelligence_notes` | 0 |
| 17 | `jsa_ivi_remoteness_monthly` | 348 |
| 18 | `jsa_ivi_state_monthly` | 4,338 |
| 19 | `jsa_sa4_remoteness_concordance` | 88 |
| 20 | `layer3_sa2_metric_banding` | 69,882 |
| 21 | `link_candidates` | 823 |
| 22 | `metric_definitions` | 6 |
| 23 | `model_assumptions` | 13 |
| 24 | `nqs_history` | 807,526 |
| 25 | `people` | 0 |
| 26 | `person_roles` | 0 |
| 27 | `portfolios` | 4,187 |
| 28 | `properties` | 0 |
| 29 | `regulatory_events` | 0 |
| 30 | `sa2_cohort` | 2,473 |
| 31 | `service_catchment_cache` | 18,203 |
| 32 | `service_financials` | 0 |
| 33 | `service_history` | 0 |
| 34 | `service_tenures` | 0 |
| 35 | `services` | 18,223 |
| 36 | `training_completions` | 768 |
| 37 | `training_completions_ingest_run` | 1 |
| | **TOTAL** | **1,977,211** |

## 2. Per-table schema, indexes, last-update

### `abs_sa2_births_annual`

Rows: **34,300**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `sa2_code` | TEXT | 1 |  | 1 |
| 1 | `year` | INTEGER | 1 |  | 2 |
| 2 | `births_count` | INTEGER | 0 |  | 0 |

Indexes:

- `idx_abs_sa2_births_annual_year` (c) on (year)
- `idx_abs_sa2_births_annual_sa2` (c) on (sa2_code)
- `sqlite_autoindex_abs_sa2_births_annual_1` UNIQUE (pk) on (sa2_code, year)

- `year` range: 2011 → 2024 (14 distinct)

### `abs_sa2_country_of_birth_top_n`

Rows: **7,102**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `sa2_code` | TEXT | 1 |  | 1 |
| 1 | `census_year` | INTEGER | 1 |  | 2 |
| 2 | `rank` | INTEGER | 1 |  | 3 |
| 3 | `country_name` | TEXT | 1 |  | 0 |
| 4 | `count` | INTEGER | 0 |  | 0 |
| 5 | `share_pct` | REAL | 0 |  | 0 |

Indexes:

- `sqlite_autoindex_abs_sa2_country_of_birth_top_n_1` UNIQUE (pk) on (sa2_code, census_year, rank)


### `abs_sa2_education_employment_annual`

Rows: **584,630**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `sa2_code` | TEXT | 1 |  | 1 |
| 1 | `year` | INTEGER | 1 |  | 2 |
| 2 | `metric_name` | TEXT | 1 |  | 3 |
| 3 | `value` | REAL | 0 |  | 0 |

Indexes:

- `idx_abs_sa2_ee_year` (c) on (year)
- `idx_abs_sa2_ee_metric` (c) on (metric_name)
- `sqlite_autoindex_abs_sa2_education_employment_annual_1` UNIQUE (pk) on (sa2_code, year, metric_name)

- `year` range: 2008 → 2025 (18 distinct)

### `abs_sa2_erp_annual`

Rows: **88,344**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `sa2_code` | TEXT | 1 |  | 1 |
| 1 | `year` | INTEGER | 1 |  | 2 |
| 2 | `age_group` | TEXT | 1 |  | 3 |
| 3 | `persons` | INTEGER | 0 |  | 0 |

Indexes:

- `ix_erp_age` (c) on (age_group)
- `ix_erp_year` (c) on (year)
- `sqlite_autoindex_abs_sa2_erp_annual_1` UNIQUE (pk) on (sa2_code, year, age_group)

- `year` range: 2011 → 2024 (9 distinct)

### `abs_sa2_language_at_home_top_n`

Rows: **7,060**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `sa2_code` | TEXT | 1 |  | 1 |
| 1 | `census_year` | INTEGER | 1 |  | 2 |
| 2 | `rank` | INTEGER | 1 |  | 3 |
| 3 | `language` | TEXT | 1 |  | 0 |
| 4 | `count` | INTEGER | 0 |  | 0 |
| 5 | `share_pct` | REAL | 0 |  | 0 |

Indexes:

- `sqlite_autoindex_abs_sa2_language_at_home_top_n_1` UNIQUE (pk) on (sa2_code, census_year, rank)


### `abs_sa2_socioeconomic_annual`

Rows: **161,964**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `sa2_code` | TEXT | 1 |  | 1 |
| 1 | `year` | INTEGER | 1 |  | 2 |
| 2 | `metric_name` | TEXT | 1 |  | 3 |
| 3 | `value` | REAL | 0 |  | 0 |

Indexes:

- `ix_socio_year` (c) on (year)
- `ix_socio_metric` (c) on (metric_name)
- `sqlite_autoindex_abs_sa2_socioeconomic_annual_1` UNIQUE (pk) on (sa2_code, year, metric_name)

- `year` range: 2011 → 2025 (11 distinct)

### `abs_sa2_unemployment_quarterly`

Rows: **142,496**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `sa2_code` | TEXT | 1 |  | 1 |
| 1 | `year_qtr` | TEXT | 1 |  | 2 |
| 2 | `rate` | REAL | 0 |  | 0 |
| 3 | `count` | INTEGER | 0 |  | 0 |
| 4 | `labour_force` | INTEGER | 0 |  | 0 |

Indexes:

- `ix_salm_year_qtr` (c) on (year_qtr)
- `sqlite_autoindex_abs_sa2_unemployment_quarterly_1` UNIQUE (pk) on (sa2_code, year_qtr)


### `audit_log`

Rows: **174**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `audit_id` | INTEGER | 0 |  | 1 |
| 1 | `actor` | TEXT | 1 |  | 0 |
| 2 | `action` | TEXT | 1 |  | 0 |
| 3 | `subject_type` | TEXT | 1 |  | 0 |
| 4 | `subject_id` | INTEGER | 1 |  | 0 |
| 5 | `before_json` | TEXT | 0 |  | 0 |
| 6 | `after_json` | TEXT | 0 |  | 0 |
| 7 | `reason` | TEXT | 0 |  | 0 |
| 8 | `occurred_at` | TEXT | 0 | datetime('now') | 0 |


### `brands`

Rows: **349**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `brand_id` | INTEGER | 0 |  | 1 |
| 1 | `portfolio_id` | INTEGER | 0 |  | 0 |
| 2 | `group_id` | INTEGER | 1 |  | 0 |
| 3 | `name` | TEXT | 1 |  | 0 |
| 4 | `service_name_prefix` | TEXT | 0 |  | 0 |
| 5 | `domain` | TEXT | 0 |  | 0 |
| 6 | `logo_url` | TEXT | 0 |  | 0 |
| 7 | `first_centre_opened` | TEXT | 0 |  | 0 |
| 8 | `pricing_tier` | TEXT | 0 |  | 0 |
| 9 | `is_active` | INTEGER | 0 | 1 | 0 |
| 10 | `created_at` | TEXT | 0 | datetime('now') | 0 |
| 11 | `updated_at` | TEXT | 0 | datetime('now') | 0 |

Indexes:

- `ix_brands_group` (c) on (group_id)

- `created_at` range: 2026-04-22 01:08:17 → 2026-04-22 01:08:17
- `updated_at` range: 2026-04-22 01:08:17 → 2026-04-22 01:08:17

### `entities`

Rows: **7,143**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `entity_id` | INTEGER | 0 |  | 1 |
| 1 | `group_id` | INTEGER | 0 |  | 0 |
| 2 | `legal_name` | TEXT | 1 |  | 0 |
| 3 | `normalised_name` | TEXT | 0 |  | 0 |
| 4 | `abn` | TEXT | 0 |  | 0 |
| 5 | `acn` | TEXT | 0 |  | 0 |
| 6 | `entity_type` | TEXT | 0 |  | 0 |
| 7 | `registered_state` | TEXT | 0 |  | 0 |
| 8 | `registered_postcode` | TEXT | 0 |  | 0 |
| 9 | `incorporation_date` | TEXT | 0 |  | 0 |
| 10 | `is_trustee` | INTEGER | 0 |  | 0 |
| 11 | `trust_name` | TEXT | 0 |  | 0 |
| 12 | `is_propco` | INTEGER | 0 |  | 0 |
| 13 | `is_opco` | INTEGER | 0 |  | 0 |
| 14 | `is_fgc` | INTEGER | 0 |  | 0 |
| 15 | `is_active` | INTEGER | 0 | 1 | 0 |
| 16 | `created_at` | TEXT | 0 | datetime('now') | 0 |
| 17 | `updated_at` | TEXT | 0 | datetime('now') | 0 |
| 18 | `deactivated_at` | TEXT | 0 |  | 0 |
| 19 | `is_notional` | INTEGER | 0 | 0 | 0 |

Indexes:

- `ix_entities_norm_name` (c) on (normalised_name)
- `ix_entities_abn` (c) on (abn)
- `ix_entities_group` (c) on (group_id)
- `sqlite_autoindex_entities_1` UNIQUE (u) on (abn)

- `created_at` range: 2026-04-22 01:01:59 → 2026-04-22 01:01:59
- `updated_at` range: 2026-04-22 01:01:59 → 2026-04-26 05:24:34

### `entity_financials`

Rows: **0**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `financial_id` | INTEGER | 0 |  | 1 |
| 1 | `entity_id` | INTEGER | 1 |  | 0 |
| 2 | `as_of_date` | TEXT | 1 |  | 0 |
| 3 | `fy_ended` | TEXT | 0 |  | 0 |
| 4 | `revenue` | REAL | 0 |  | 0 |
| 5 | `ebitda` | REAL | 0 |  | 0 |
| 6 | `ebitda_margin_pct` | REAL | 0 |  | 0 |
| 7 | `source_type` | TEXT | 0 |  | 0 |
| 8 | `confidence` | REAL | 0 |  | 0 |
| 9 | `created_at` | TEXT | 0 | datetime('now') | 0 |

- `created_at` range: None → None

### `entity_snapshots`

Rows: **0**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `snapshot_id` | INTEGER | 0 |  | 1 |
| 1 | `entity_id` | INTEGER | 1 |  | 0 |
| 2 | `as_of_date` | TEXT | 1 |  | 0 |
| 3 | `service_count` | INTEGER | 0 |  | 0 |
| 4 | `total_places` | INTEGER | 0 |  | 0 |
| 5 | `nqs_profile_json` | TEXT | 0 |  | 0 |
| 6 | `has_compliance_action` | INTEGER | 0 |  | 0 |
| 7 | `created_at` | TEXT | 0 | datetime('now') | 0 |

Indexes:

- `ix_entity_snapshots` (c) on (entity_id, as_of_date)

- `created_at` range: None → None

### `evidence`

Rows: **10,263**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `evidence_id` | INTEGER | 0 |  | 1 |
| 1 | `subject_type` | TEXT | 1 |  | 0 |
| 2 | `subject_id` | INTEGER | 1 |  | 0 |
| 3 | `field_name` | TEXT | 0 |  | 0 |
| 4 | `asserted_value` | TEXT | 0 |  | 0 |
| 5 | `source_type` | TEXT | 1 |  | 0 |
| 6 | `source_url` | TEXT | 0 |  | 0 |
| 7 | `source_detail` | TEXT | 0 |  | 0 |
| 8 | `confidence` | REAL | 1 |  | 0 |
| 9 | `asserted_by` | TEXT | 0 |  | 0 |
| 10 | `asserted_at` | TEXT | 0 | datetime('now') | 0 |
| 11 | `superseded_at` | TEXT | 0 |  | 0 |
| 12 | `notes` | TEXT | 0 |  | 0 |

Indexes:

- `ix_evidence_subject` (c) on (subject_type, subject_id)


### `group_snapshots`

Rows: **0**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `snapshot_id` | INTEGER | 0 |  | 1 |
| 1 | `group_id` | INTEGER | 1 |  | 0 |
| 2 | `as_of_date` | TEXT | 1 |  | 0 |
| 3 | `entity_count` | INTEGER | 0 |  | 0 |
| 4 | `brand_count` | INTEGER | 0 |  | 0 |
| 5 | `portfolio_count` | INTEGER | 0 |  | 0 |
| 6 | `service_count` | INTEGER | 0 |  | 0 |
| 7 | `total_places` | INTEGER | 0 |  | 0 |
| 8 | `states_covered` | INTEGER | 0 |  | 0 |
| 9 | `provider_approval_count` | INTEGER | 0 |  | 0 |
| 10 | `nqs_excellent` | INTEGER | 0 |  | 0 |
| 11 | `nqs_exceeding` | INTEGER | 0 |  | 0 |
| 12 | `nqs_meeting` | INTEGER | 0 |  | 0 |
| 13 | `nqs_working_towards` | INTEGER | 0 |  | 0 |
| 14 | `nqs_sir` | INTEGER | 0 |  | 0 |
| 15 | `nqs_unrated` | INTEGER | 0 |  | 0 |
| 16 | `concentration_top_sa2_pct` | REAL | 0 |  | 0 |
| 17 | `concentration_top_state_pct` | REAL | 0 |  | 0 |
| 18 | `single_pa_share` | REAL | 0 |  | 0 |
| 19 | `regulatory_stress_pct` | REAL | 0 |  | 0 |
| 20 | `kinder_approved_share` | REAL | 0 |  | 0 |
| 21 | `avg_centre_age_years` | REAL | 0 |  | 0 |
| 22 | `growth_12m_services` | INTEGER | 0 |  | 0 |
| 23 | `growth_12m_places` | INTEGER | 0 |  | 0 |
| 24 | `catchments_covered` | INTEGER | 0 |  | 0 |
| 25 | `total_catchment_u5_pop` | INTEGER | 0 |  | 0 |
| 26 | `weighted_avg_u5_pop_per_centre` | REAL | 0 |  | 0 |
| 27 | `weighted_avg_median_income` | REAL | 0 |  | 0 |
| 28 | `weighted_avg_seifa_irsd` | REAL | 0 |  | 0 |
| 29 | `weighted_avg_supply_ratio` | REAL | 0 |  | 0 |
| 30 | `places_in_balanced_pct` | REAL | 0 |  | 0 |
| 31 | `places_in_supplied_pct` | REAL | 0 |  | 0 |
| 32 | `places_in_oversupplied_pct` | REAL | 0 |  | 0 |
| 33 | `places_in_no_catchment_data_pct` | REAL | 0 |  | 0 |
| 34 | `centres_in_balanced` | INTEGER | 0 |  | 0 |
| 35 | `centres_in_supplied` | INTEGER | 0 |  | 0 |
| 36 | `centres_in_oversupplied` | INTEGER | 0 |  | 0 |
| 37 | `centres_in_deteriorating_catchments` | INTEGER | 0 |  | 0 |
| 38 | `centres_near_new_competitor_12m` | INTEGER | 0 |  | 0 |
| 39 | `opportunity_catchments_count` | INTEGER | 0 |  | 0 |
| 40 | `created_at` | TEXT | 0 | datetime('now') | 0 |

Indexes:

- `ix_group_snapshots` (c) on (group_id, as_of_date)

- `created_at` range: None → None

### `groups`

Rows: **6,507**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `group_id` | INTEGER | 0 |  | 1 |
| 1 | `canonical_name` | TEXT | 1 |  | 0 |
| 2 | `display_name` | TEXT | 0 |  | 0 |
| 3 | `slug` | TEXT | 0 |  | 0 |
| 4 | `is_for_profit` | INTEGER | 0 |  | 0 |
| 5 | `is_listed` | INTEGER | 0 |  | 0 |
| 6 | `asx_code` | TEXT | 0 |  | 0 |
| 7 | `primary_domain` | TEXT | 0 |  | 0 |
| 8 | `head_office_state` | TEXT | 0 |  | 0 |
| 9 | `ownership_type` | TEXT | 0 |  | 0 |
| 10 | `is_active` | INTEGER | 0 | 1 | 0 |
| 11 | `created_at` | TEXT | 0 | datetime('now') | 0 |
| 12 | `updated_at` | TEXT | 0 | datetime('now') | 0 |
| 13 | `deactivated_at` | TEXT | 0 |  | 0 |
| 14 | `parent_entity_id` | INTEGER | 0 |  | 0 |

Indexes:

- `ix_groups_parent_entity` (c) on (parent_entity_id)
- `sqlite_autoindex_groups_1` UNIQUE (u) on (slug)

- `created_at` range: 2026-04-22 01:01:59 → 2026-04-26 05:24:34
- `updated_at` range: 2026-04-22 01:01:59 → 2026-04-26 05:24:34

### `intelligence_notes`

Rows: **0**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `note_id` | INTEGER | 0 |  | 1 |
| 1 | `subject_type` | TEXT | 1 |  | 0 |
| 2 | `subject_id` | INTEGER | 1 |  | 0 |
| 3 | `body` | TEXT | 1 |  | 0 |
| 4 | `tags` | TEXT | 0 |  | 0 |
| 5 | `author` | TEXT | 1 |  | 0 |
| 6 | `source` | TEXT | 0 |  | 0 |
| 7 | `event_date` | TEXT | 0 |  | 0 |
| 8 | `is_pinned` | INTEGER | 0 | 0 | 0 |
| 9 | `is_confidential` | INTEGER | 0 | 0 | 0 |
| 10 | `created_at` | TEXT | 0 | datetime('now') | 0 |

Indexes:

- `ix_notes_subject` (c) on (subject_type, subject_id)

- `created_at` range: None → None

### `jsa_ivi_remoteness_monthly`

Rows: **348**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `remoteness` | TEXT | 1 |  | 1 |
| 1 | `year_month` | TEXT | 1 |  | 2 |
| 2 | `anzsco_code` | TEXT | 1 |  | 3 |
| 3 | `vacancy_count` | INTEGER | 0 |  | 0 |

Indexes:

- `ix_ivi_remote_anzsco` (c) on (anzsco_code)
- `sqlite_autoindex_jsa_ivi_remoteness_monthly_1` UNIQUE (pk) on (remoteness, year_month, anzsco_code)


### `jsa_ivi_state_monthly`

Rows: **4,338**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `state_code` | TEXT | 1 |  | 1 |
| 1 | `year_month` | TEXT | 1 |  | 2 |
| 2 | `anzsco_code` | TEXT | 1 |  | 3 |
| 3 | `vacancy_count` | INTEGER | 0 |  | 0 |

Indexes:

- `ix_ivi_state_ym` (c) on (year_month)
- `ix_ivi_state_anzsco` (c) on (anzsco_code)
- `sqlite_autoindex_jsa_ivi_state_monthly_1` UNIQUE (pk) on (state_code, year_month, anzsco_code)


### `jsa_sa4_remoteness_concordance`

Rows: **88**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `sa4_code` | TEXT | 1 |  | 1 |
| 1 | `sa4_name` | TEXT | 0 |  | 0 |
| 2 | `remoteness` | TEXT | 0 |  | 0 |
| 3 | `northern_aust` | INTEGER | 0 |  | 0 |

Indexes:

- `sqlite_autoindex_jsa_sa4_remoteness_concordance_1` UNIQUE (pk) on (sa4_code)


### `layer3_sa2_metric_banding`

Rows: **69,882**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `sa2_code` | TEXT | 1 |  | 1 |
| 1 | `metric` | TEXT | 1 |  | 2 |
| 2 | `year` | INTEGER | 1 |  | 3 |
| 3 | `period_label` | TEXT | 0 |  | 0 |
| 4 | `cohort_def` | TEXT | 1 |  | 4 |
| 5 | `cohort_key` | TEXT | 0 |  | 0 |
| 6 | `cohort_n` | INTEGER | 0 |  | 0 |
| 7 | `raw_value` | REAL | 0 |  | 0 |
| 8 | `percentile` | REAL | 0 |  | 0 |
| 9 | `decile` | INTEGER | 0 |  | 0 |
| 10 | `band` | TEXT | 0 |  | 0 |

Indexes:

- `idx_l3_band` (c) on (band)
- `idx_l3_metric` (c) on (metric)
- `idx_l3_sa2` (c) on (sa2_code)
- `sqlite_autoindex_layer3_sa2_metric_banding_1` UNIQUE (pk) on (sa2_code, metric, year, cohort_def)

- `year` range: 2021 → 2025 (4 distinct)

### `link_candidates`

Rows: **823**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `candidate_id` | INTEGER | 0 |  | 1 |
| 1 | `link_type` | TEXT | 1 |  | 0 |
| 2 | `from_type` | TEXT | 1 |  | 0 |
| 3 | `from_id` | INTEGER | 1 |  | 0 |
| 4 | `to_type` | TEXT | 1 |  | 0 |
| 5 | `to_id` | INTEGER | 1 |  | 0 |
| 6 | `composite_confidence` | REAL | 1 |  | 0 |
| 7 | `evidence_json` | TEXT | 1 |  | 0 |
| 8 | `status` | TEXT | 0 | 'pending' | 0 |
| 9 | `priority` | INTEGER | 0 | 0 | 0 |
| 10 | `proposed_at` | TEXT | 0 | datetime('now') | 0 |
| 11 | `reviewed_at` | TEXT | 0 |  | 0 |
| 12 | `reviewed_by` | TEXT | 0 |  | 0 |
| 13 | `review_note` | TEXT | 0 |  | 0 |

Indexes:

- `ix_links_status_priority` (c) on (status, priority)


### `metric_definitions`

Rows: **6**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `metric_key` | TEXT | 0 |  | 1 |
| 1 | `display_name` | TEXT | 1 |  | 0 |
| 2 | `classification` | TEXT | 1 |  | 0 |
| 3 | `formula` | TEXT | 0 |  | 0 |
| 4 | `source` | TEXT | 0 |  | 0 |
| 5 | `units` | TEXT | 0 |  | 0 |
| 6 | `description` | TEXT | 0 |  | 0 |
| 7 | `version` | TEXT | 1 | 'v1' | 0 |
| 8 | `created_at` | TEXT | 1 | datetime('now') | 0 |
| 9 | `updated_at` | TEXT | 0 |  | 0 |

Indexes:

- `ix_metric_def_classification` (c) on (classification)
- `sqlite_autoindex_metric_definitions_1` UNIQUE (pk) on (metric_key)

- `created_at` range: 2026-04-25 10:02:49 → 2026-04-25 10:02:49
- `updated_at` range: 2026-04-25T20:02:49 → 2026-04-25T20:02:49

### `model_assumptions`

Rows: **13**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `assumption_key` | TEXT | 0 |  | 1 |
| 1 | `display_name` | TEXT | 1 |  | 0 |
| 2 | `value_numeric` | REAL | 0 |  | 0 |
| 3 | `value_text` | TEXT | 0 |  | 0 |
| 4 | `units` | TEXT | 0 |  | 0 |
| 5 | `description` | TEXT | 0 |  | 0 |
| 6 | `source` | TEXT | 0 |  | 0 |
| 7 | `last_changed_by` | TEXT | 0 |  | 0 |
| 8 | `last_changed_at` | TEXT | 1 | datetime('now') | 0 |
| 9 | `is_active` | INTEGER | 1 | 1 | 0 |

Indexes:

- `ix_model_assumption_active` (c) on (is_active)
- `sqlite_autoindex_model_assumptions_1` UNIQUE (pk) on (assumption_key)


### `nqs_history`

Rows: **807,526**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `nqs_history_id` | INTEGER | 0 |  | 1 |
| 1 | `service_approval_number` | TEXT | 1 |  | 0 |
| 2 | `quarter` | TEXT | 1 |  | 0 |
| 3 | `quarter_end_date` | TEXT | 1 |  | 0 |
| 4 | `source_sheet` | TEXT | 1 |  | 0 |
| 5 | `service_name` | TEXT | 0 |  | 0 |
| 6 | `service_type` | TEXT | 0 |  | 0 |
| 7 | `service_sub_type` | TEXT | 0 |  | 0 |
| 8 | `provider_id` | TEXT | 0 |  | 0 |
| 9 | `provider_name` | TEXT | 0 |  | 0 |
| 10 | `provider_management_type` | TEXT | 0 |  | 0 |
| 11 | `managing_jurisdiction` | TEXT | 0 |  | 0 |
| 12 | `postcode` | TEXT | 0 |  | 0 |
| 13 | `latitude` | REAL | 0 |  | 0 |
| 14 | `longitude` | REAL | 0 |  | 0 |
| 15 | `aria` | TEXT | 0 |  | 0 |
| 16 | `seifa` | TEXT | 0 |  | 0 |
| 17 | `nqs_version` | TEXT | 0 |  | 0 |
| 18 | `overall_rating` | TEXT | 0 |  | 0 |
| 19 | `quality_area_1` | TEXT | 0 |  | 0 |
| 20 | `quality_area_2` | TEXT | 0 |  | 0 |
| 21 | `quality_area_3` | TEXT | 0 |  | 0 |
| 22 | `quality_area_4` | TEXT | 0 |  | 0 |
| 23 | `quality_area_5` | TEXT | 0 |  | 0 |
| 24 | `quality_area_6` | TEXT | 0 |  | 0 |
| 25 | `quality_area_7` | TEXT | 0 |  | 0 |
| 26 | `approval_date` | TEXT | 0 |  | 0 |
| 27 | `final_report_sent_date` | TEXT | 0 |  | 0 |
| 28 | `max_places` | INTEGER | 0 |  | 0 |
| 29 | `long_day_care` | TEXT | 0 |  | 0 |
| 30 | `preschool_standalone` | TEXT | 0 |  | 0 |
| 31 | `preschool_in_school` | TEXT | 0 |  | 0 |
| 32 | `oshc_before_school` | TEXT | 0 |  | 0 |
| 33 | `oshc_after_school` | TEXT | 0 |  | 0 |
| 34 | `oshc_vacation_care` | TEXT | 0 |  | 0 |
| 35 | `nature_care_other` | TEXT | 0 |  | 0 |
| 36 | `ingested_at` | TEXT | 1 | datetime('now') | 0 |

Indexes:

- `ix_nqs_history_provider` (c) on (provider_id)
- `ix_nqs_history_quarter` (c) on (quarter_end_date)
- `ix_nqs_history_san` (c) on (service_approval_number)
- `sqlite_autoindex_nqs_history_1` UNIQUE (u) on (service_approval_number, quarter)

- `ingested_at` range: 2026-04-26 05:53:06 → 2026-04-26 05:55:58

### `people`

Rows: **0**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `person_id` | INTEGER | 0 |  | 1 |
| 1 | `full_name` | TEXT | 1 |  | 0 |
| 2 | `normalised_name` | TEXT | 0 |  | 0 |
| 3 | `dob_year` | INTEGER | 0 |  | 0 |
| 4 | `is_disqualified` | INTEGER | 0 |  | 0 |
| 5 | `created_at` | TEXT | 0 | datetime('now') | 0 |
| 6 | `updated_at` | TEXT | 0 | datetime('now') | 0 |

- `created_at` range: None → None
- `updated_at` range: None → None

### `person_roles`

Rows: **0**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `role_id` | INTEGER | 0 |  | 1 |
| 1 | `person_id` | INTEGER | 1 |  | 0 |
| 2 | `entity_id` | INTEGER | 0 |  | 0 |
| 3 | `service_id` | INTEGER | 0 |  | 0 |
| 4 | `role_type` | TEXT | 1 |  | 0 |
| 5 | `start_date` | TEXT | 0 |  | 0 |
| 6 | `end_date` | TEXT | 0 |  | 0 |
| 7 | `ownership_pct` | REAL | 0 |  | 0 |
| 8 | `created_at` | TEXT | 0 | datetime('now') | 0 |

Indexes:

- `ix_person_roles_person` (c) on (person_id)
- `ix_person_roles_entity` (c) on (entity_id)

- `created_at` range: None → None

### `portfolios`

Rows: **4,187**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `portfolio_id` | INTEGER | 0 |  | 1 |
| 1 | `group_id` | INTEGER | 1 |  | 0 |
| 2 | `name` | TEXT | 1 |  | 0 |
| 3 | `positioning` | TEXT | 0 |  | 0 |
| 4 | `is_default` | INTEGER | 0 | 0 | 0 |
| 5 | `notes` | TEXT | 0 |  | 0 |
| 6 | `is_active` | INTEGER | 0 | 1 | 0 |
| 7 | `created_at` | TEXT | 0 | datetime('now') | 0 |
| 8 | `updated_at` | TEXT | 0 | datetime('now') | 0 |

Indexes:

- `ix_portfolios_group` (c) on (group_id)

- `created_at` range: 2026-04-22 01:01:59 → 2026-04-22 01:01:59
- `updated_at` range: 2026-04-22 01:01:59 → 2026-04-22 01:01:59

### `properties`

Rows: **0**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `property_id` | INTEGER | 0 |  | 1 |
| 1 | `owner_entity_id` | INTEGER | 0 |  | 0 |
| 2 | `address_line` | TEXT | 0 |  | 0 |
| 3 | `suburb` | TEXT | 0 |  | 0 |
| 4 | `state` | TEXT | 0 |  | 0 |
| 5 | `postcode` | TEXT | 0 |  | 0 |
| 6 | `lot_plan` | TEXT | 0 |  | 0 |
| 7 | `title_reference` | TEXT | 0 |  | 0 |
| 8 | `is_freehold` | INTEGER | 0 |  | 0 |
| 9 | `created_at` | TEXT | 0 | datetime('now') | 0 |

- `created_at` range: None → None

### `regulatory_events`

Rows: **0**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `event_id` | INTEGER | 0 |  | 1 |
| 1 | `subject_type` | TEXT | 1 |  | 0 |
| 2 | `subject_id` | INTEGER | 1 |  | 0 |
| 3 | `event_type` | TEXT | 1 |  | 0 |
| 4 | `event_date` | TEXT | 1 |  | 0 |
| 5 | `detail` | TEXT | 0 |  | 0 |
| 6 | `severity` | TEXT | 0 |  | 0 |
| 7 | `regulator` | TEXT | 0 |  | 0 |
| 8 | `source_url` | TEXT | 0 |  | 0 |
| 9 | `created_at` | TEXT | 0 | datetime('now') | 0 |

Indexes:

- `ix_reg_events_date` (c) on (event_date)
- `ix_reg_events_subject` (c) on (subject_type, subject_id, event_date)

- `created_at` range: None → None

### `sa2_cohort`

Rows: **2,473**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `sa2_code` | TEXT | 1 |  | 1 |
| 1 | `sa2_name` | TEXT | 0 |  | 0 |
| 2 | `state_code` | TEXT | 0 |  | 0 |
| 3 | `state_name` | TEXT | 0 |  | 0 |
| 4 | `ra_code` | TEXT | 0 |  | 0 |
| 5 | `ra_name` | TEXT | 0 |  | 0 |
| 6 | `ra_band` | INTEGER | 0 |  | 0 |

Indexes:

- `idx_sa2_cohort_ra_band` (c) on (ra_band)
- `idx_sa2_cohort_ra` (c) on (ra_code)
- `idx_sa2_cohort_state` (c) on (state_code)
- `sqlite_autoindex_sa2_cohort_1` UNIQUE (pk) on (sa2_code)


### `service_catchment_cache`

Rows: **18,203**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `service_id` | INTEGER | 0 |  | 1 |
| 1 | `sa2_code` | TEXT | 0 |  | 0 |
| 2 | `sa2_name` | TEXT | 0 |  | 0 |
| 3 | `u5_pop` | INTEGER | 0 |  | 0 |
| 4 | `median_income` | REAL | 0 |  | 0 |
| 5 | `seifa_irsd` | INTEGER | 0 |  | 0 |
| 6 | `unemployment_pct` | REAL | 0 |  | 0 |
| 7 | `supply_ratio` | REAL | 0 |  | 0 |
| 8 | `supply_band` | TEXT | 0 |  | 0 |
| 9 | `supply_ratio_4q_change` | REAL | 0 |  | 0 |
| 10 | `is_deteriorating` | INTEGER | 0 |  | 0 |
| 11 | `competing_centres_count` | INTEGER | 0 |  | 0 |
| 12 | `new_competitor_12m` | INTEGER | 0 |  | 0 |
| 13 | `ccs_dependency_pct` | REAL | 0 |  | 0 |
| 14 | `as_of_date` | TEXT | 0 |  | 0 |
| 15 | `created_at` | TEXT | 0 | datetime('now') | 0 |
| 16 | `updated_at` | TEXT | 0 | datetime('now') | 0 |
| 17 | `adjusted_demand` | REAL | 0 |  | 0 |
| 18 | `demand_share_state` | REAL | 0 |  | 0 |
| 19 | `demand_supply` | REAL | 0 |  | 0 |
| 20 | `child_to_place` | REAL | 0 |  | 0 |
| 21 | `calibrated_rate` | REAL | 0 |  | 0 |
| 22 | `rule_text` | TEXT | 0 |  | 0 |
| 23 | `calibration_run_at` | TEXT | 0 |  | 0 |

Indexes:

- `ix_service_catchment_band` (c) on (supply_band)
- `ix_service_catchment_sa2` (c) on (sa2_code)

- `created_at` range: 2026-05-04 04:01:36 → 2026-05-04 04:01:37
- `updated_at` range: 2026-05-04 04:01:36 → 2026-05-04 04:01:37

### `service_financials`

Rows: **0**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `financial_id` | INTEGER | 0 |  | 1 |
| 1 | `service_id` | INTEGER | 1 |  | 0 |
| 2 | `as_of_date` | TEXT | 1 |  | 0 |
| 3 | `daily_fee` | REAL | 0 |  | 0 |
| 4 | `ccs_dependency_pct` | REAL | 0 |  | 0 |
| 5 | `estimated_occupancy` | REAL | 0 |  | 0 |
| 6 | `estimated_revenue_pp` | REAL | 0 |  | 0 |
| 7 | `estimated_ebitda_pp` | REAL | 0 |  | 0 |
| 8 | `rent_to_revenue_pct` | REAL | 0 |  | 0 |
| 9 | `wages_to_revenue_pct` | REAL | 0 |  | 0 |
| 10 | `source_type` | TEXT | 0 |  | 0 |
| 11 | `confidence` | REAL | 0 |  | 0 |
| 12 | `created_at` | TEXT | 0 | datetime('now') | 0 |

- `created_at` range: None → None

### `service_history`

Rows: **0**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `history_id` | INTEGER | 0 |  | 1 |
| 1 | `service_id` | INTEGER | 1 |  | 0 |
| 2 | `as_of_date` | TEXT | 1 |  | 0 |
| 3 | `approved_places` | INTEGER | 0 |  | 0 |
| 4 | `overall_nqs_rating` | TEXT | 0 |  | 0 |
| 5 | `entity_id` | INTEGER | 0 |  | 0 |
| 6 | `brand_id` | INTEGER | 0 |  | 0 |
| 7 | `is_active` | INTEGER | 0 |  | 0 |
| 8 | `created_at` | TEXT | 0 | datetime('now') | 0 |

Indexes:

- `ix_service_history` (c) on (service_id, as_of_date)

- `created_at` range: None → None

### `service_tenures`

Rows: **0**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `tenure_id` | INTEGER | 0 |  | 1 |
| 1 | `service_id` | INTEGER | 1 |  | 0 |
| 2 | `property_id` | INTEGER | 0 |  | 0 |
| 3 | `tenure_type` | TEXT | 0 |  | 0 |
| 4 | `lease_start` | TEXT | 0 |  | 0 |
| 5 | `lease_term_years` | INTEGER | 0 |  | 0 |
| 6 | `options_remaining` | INTEGER | 0 |  | 0 |
| 7 | `rent_annual` | REAL | 0 |  | 0 |
| 8 | `rent_to_revenue_pct` | REAL | 0 |  | 0 |
| 9 | `created_at` | TEXT | 0 | datetime('now') | 0 |

- `created_at` range: None → None

### `services`

Rows: **18,223**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `service_id` | INTEGER | 0 |  | 1 |
| 1 | `entity_id` | INTEGER | 0 |  | 0 |
| 2 | `brand_id` | INTEGER | 0 |  | 0 |
| 3 | `service_approval_number` | TEXT | 0 |  | 0 |
| 4 | `provider_approval_number` | TEXT | 0 |  | 0 |
| 5 | `service_name` | TEXT | 1 |  | 0 |
| 6 | `address_line` | TEXT | 0 |  | 0 |
| 7 | `suburb` | TEXT | 0 |  | 0 |
| 8 | `state` | TEXT | 0 |  | 0 |
| 9 | `postcode` | TEXT | 0 |  | 0 |
| 10 | `sa2_code` | TEXT | 0 |  | 0 |
| 11 | `sa2_name` | TEXT | 0 |  | 0 |
| 12 | `lat` | REAL | 0 |  | 0 |
| 13 | `lng` | REAL | 0 |  | 0 |
| 14 | `approved_places` | INTEGER | 0 |  | 0 |
| 15 | `approval_granted_date` | TEXT | 0 |  | 0 |
| 16 | `last_transfer_date` | TEXT | 0 |  | 0 |
| 17 | `overall_nqs_rating` | TEXT | 0 |  | 0 |
| 18 | `rating_issued_date` | TEXT | 0 |  | 0 |
| 19 | `kinder_approved` | INTEGER | 0 |  | 0 |
| 20 | `kinder_source` | TEXT | 0 |  | 0 |
| 21 | `long_day_care` | INTEGER | 0 | 1 | 0 |
| 22 | `is_active` | INTEGER | 0 | 1 | 0 |
| 23 | `created_at` | TEXT | 0 | datetime('now') | 0 |
| 24 | `updated_at` | TEXT | 0 | datetime('now') | 0 |
| 25 | `aria_plus` | TEXT | 0 |  | 0 |
| 26 | `seifa_decile` | INTEGER | 0 |  | 0 |
| 27 | `service_sub_type` | TEXT | 0 |  | 0 |
| 28 | `provider_management_type` | TEXT | 0 |  | 0 |
| 29 | `qa1` | TEXT | 0 |  | 0 |
| 30 | `qa2` | TEXT | 0 |  | 0 |
| 31 | `qa3` | TEXT | 0 |  | 0 |
| 32 | `qa4` | TEXT | 0 |  | 0 |
| 33 | `qa5` | TEXT | 0 |  | 0 |
| 34 | `qa6` | TEXT | 0 |  | 0 |
| 35 | `qa7` | TEXT | 0 |  | 0 |

Indexes:

- `ix_services_state_suburb` (c) on (state, suburb)
- `ix_services_sa2` (c) on (sa2_code)
- `ix_services_pap` (c) on (provider_approval_number)
- `ix_services_sap` (c) on (service_approval_number)
- `ix_services_brand` (c) on (brand_id)
- `ix_services_entity` (c) on (entity_id)
- `sqlite_autoindex_services_1` UNIQUE (u) on (service_approval_number)

- `created_at` range: 2026-04-22 01:02:00 → 2026-04-22 01:02:00
- `updated_at` range: 2026-04-22 01:02:00 → 2026-04-23 11:01:21

### `training_completions`

Rows: **768**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `completion_id` | INTEGER | 0 |  | 1 |
| 1 | `state_code` | TEXT | 1 |  | 0 |
| 2 | `state_name` | TEXT | 1 |  | 0 |
| 3 | `remoteness_band` | TEXT | 0 |  | 0 |
| 4 | `qualification_code` | TEXT | 1 |  | 0 |
| 5 | `qualification_name` | TEXT | 1 |  | 0 |
| 6 | `qualification_level` | TEXT | 1 |  | 0 |
| 7 | `qualification_era` | TEXT | 1 |  | 0 |
| 8 | `year` | INTEGER | 1 |  | 0 |
| 9 | `completions` | INTEGER | 1 | 0 | 0 |
| 10 | `ingest_run_id` | INTEGER | 1 |  | 0 |

Indexes:

- `ix_tc_run` (c) on (ingest_run_id)
- `ix_tc_level_year` (c) on (qualification_level, year)
- `ix_tc_state_year` (c) on (state_code, year)

- `year` range: 2019 → 2024 (6 distinct)

### `training_completions_ingest_run`

Rows: **1**

Columns:

| # | Name | Type | NotNull | Default | PK |
|---:|---|---|:-:|---|:-:|
| 0 | `run_id` | INTEGER | 0 |  | 1 |
| 1 | `source_file` | TEXT | 1 |  | 0 |
| 2 | `source_label` | TEXT | 0 |  | 0 |
| 3 | `publication_date` | TEXT | 0 |  | 0 |
| 4 | `filter_description` | TEXT | 0 |  | 0 |
| 5 | `caveats` | TEXT | 0 |  | 0 |
| 6 | `rows_ingested` | INTEGER | 1 | 0 | 0 |
| 7 | `ingested_at` | TEXT | 1 | datetime('now') | 0 |
| 8 | `ingested_by` | TEXT | 1 |  | 0 |

- `ingested_at` range: 2026-04-25 09:38:18 → 2026-04-25 09:38:18

## 3. Coverage stats — key dimensions

### 3a. SA2 coverage by table

Tables exposing an SA2 column. NULLs and distinct-SA2 cardinality both shown.

| Table | SA2 column | Distinct SA2s | NULL rows | Total |
|---|---|---:|---:|---:|
| `abs_sa2_births_annual` | `sa2_code` | 2,450 | 0 | 34,300 |
| `abs_sa2_country_of_birth_top_n` | `sa2_code` | 2,386 | 0 | 7,102 |
| `abs_sa2_education_employment_annual` | `sa2_code` | 2,452 | 0 | 584,630 |
| `abs_sa2_erp_annual` | `sa2_code` | 2,454 | 0 | 88,344 |
| `abs_sa2_language_at_home_top_n` | `sa2_code` | 2,374 | 0 | 7,060 |
| `abs_sa2_socioeconomic_annual` | `sa2_code` | 2,454 | 0 | 161,964 |
| `abs_sa2_unemployment_quarterly` | `sa2_code` | 2,336 | 0 | 142,496 |
| `layer3_sa2_metric_banding` | `sa2_code` | 2,454 | 0 | 69,882 |
| `sa2_cohort` | `sa2_code` | 2,473 | 0 | 2,473 |
| `service_catchment_cache` | `sa2_code` | 2,294 | 0 | 18,203 |
| `services` | `sa2_code` | 2,294 | 20 | 18,223 |

### 3b. Year coverage by table

| Table | Year col | Min | Max | Distinct |
|---|---|---:|---:|---:|
| `abs_sa2_births_annual` | `year` | 2011 | 2024 | 14 |
| `abs_sa2_education_employment_annual` | `year` | 2008 | 2025 | 18 |
| `abs_sa2_erp_annual` | `year` | 2011 | 2024 | 9 |
| `abs_sa2_socioeconomic_annual` | `year` | 2011 | 2025 | 11 |
| `layer3_sa2_metric_banding` | `year` | 2021 | 2025 | 4 |
| `training_completions` | `year` | 2019 | 2024 | 6 |

### 3c. `services` table — Step 1b focus

- Total services: **18,223**
- With `sa2_code` populated: **18,203** (99.89%)
- NULL `sa2_code`: **20** (0.11%)
- NULL SA2 **with** `lat/lng` (Step 1b candidates): **2**
- NULL SA2 **without** lat/lng (unrecoverable via polygon): **18**

By `state` (all services):

| state | Rows | NULL sa2 | NULL sa2 with lat/lng |
|---|---:|---:|---:|
| NSW | 6,158 | 2 | 0 |
| VIC | 5,032 | 7 | 0 |
| QLD | 3,329 | 5 | 1 |
| WA | 1,525 | 2 | 0 |
| SA | 1,324 | 3 | 0 |
| ACT | 372 | 0 | 0 |
| TAS | 242 | 0 | 0 |
| NT | 235 | 0 | 0 |
| (NULL) | 6 | 1 | 1 |

## 4. Foreign-key / orphan health

### 4a. Declared foreign keys

**`brands`**

- ✓ `group_id` → `groups.group_id` — orphans: 0
- ✓ `portfolio_id` → `portfolios.portfolio_id` — orphans: 0

**`entities`**

- ✓ `group_id` → `groups.group_id` — orphans: 0

**`entity_financials`**

- ✓ `entity_id` → `entities.entity_id` — orphans: 0

**`entity_snapshots`**

- ✓ `entity_id` → `entities.entity_id` — orphans: 0

**`group_snapshots`**

- ✓ `group_id` → `groups.group_id` — orphans: 0

**`groups`**

- ✓ `parent_entity_id` → `entities.entity_id` — orphans: 0

**`person_roles`**

- ✓ `service_id` → `services.service_id` — orphans: 0
- ✓ `entity_id` → `entities.entity_id` — orphans: 0
- ✓ `person_id` → `people.person_id` — orphans: 0

**`portfolios`**

- ✓ `group_id` → `groups.group_id` — orphans: 0

**`properties`**

- ✓ `owner_entity_id` → `entities.entity_id` — orphans: 0

**`service_catchment_cache`**

- ✓ `service_id` → `services.service_id` — orphans: 0

**`service_financials`**

- ✓ `service_id` → `services.service_id` — orphans: 0

**`service_history`**

- ✓ `service_id` → `services.service_id` — orphans: 0

**`service_tenures`**

- ✓ `property_id` → `properties.property_id` — orphans: 0
- ✓ `service_id` → `services.service_id` — orphans: 0

**`services`**

- ✓ `brand_id` → `brands.brand_id` — orphans: 0
- ✓ `entity_id` → `entities.entity_id` — orphans: 0

**`training_completions`**

- ✓ `ingest_run_id` → `training_completions_ingest_run.run_id` — orphans: 0

### 4b. Implicit reference checks

- ✓ Service SA2s present in canonical SA2 universe
  - `services.sa2_code` → `abs_sa2_erp_annual.sa2_code`
  - Orphan distinct SA2s: **0**
  - Orphan rows: **0**

## 5. Backups in `data/`

| File | Size (MB) | Modified |
|---|---:|---|
| `kintell.db.backup_20260422_170018` | 10.3 | 2026-04-22T15:53:49 |
| `kintell.db.backup_migrate_v04_20260423_205801` | 10.3 | 2026-04-22T18:29:13 |
| `kintell.db.backup_pre_tier2_20260423_204713` | 10.3 | 2026-04-22T18:29:13 |
| `kintell.db.backup_pre_restructure_20260425_175919` | 13.7 | 2026-04-23T21:01:21 |
| `kintell.db.backup_pre_schema_v0_5_20260425_181210` | 13.7 | 2026-04-23T21:01:21 |
| `kintell.db.backup_pre_schema_v0_5_20260425_181456` | 13.8 | 2026-04-25T18:12:10 |
| `kintell.db.backup_pre_seed_assumptions_20260425_181952` | 13.8 | 2026-04-25T18:14:56 |
| `kintell.db.backup_pre_commentary_threshold_20260425_182634` | 13.8 | 2026-04-25T18:19:52 |
| `kintell.db.backup_pre_training_completions_20260425_193045` | 13.8 | 2026-04-25T18:26:34 |
| `kintell.db.backup_pre_ncver_ingest_20260425_193818` | 13.8 | 2026-04-25T19:30:45 |
| `kintell.db.backup_pre_workforce_assumptions_20260425_195021` | 13.9 | 2026-04-25T19:38:18 |
| `kintell.db.backup_pre_workforce_assumptions_20260425_195108` | 13.9 | 2026-04-25T19:38:18 |
| `kintell.db.backup_pre_workforce_assumptions_20260425_195405` | 13.9 | 2026-04-25T19:38:18 |
| `kintell.db.backup_pre_audit_backfill_20260425_195659` | 13.9 | 2026-04-25T19:54:05 |
| `kintell.db.backup_pre_workforce_metrics_20260425_200249` | 13.9 | 2026-04-25T19:56:59 |
| `kintell.db.backup_pre_ratio_convention_migration_20260425_202511` | 13.9 | 2026-04-25T20:02:49 |
| `kintell.db.backup_pre_phase2_20260426_124242` | 13.9 | 2026-04-25T20:25:11 |
| `kintell.db.backup_pre_sa2_backfill_20260426_150639` | 13.9 | 2026-04-25T20:25:11 |
| `kintell.db.session_backup_20260426_150630` | 13.9 | 2026-04-25T20:25:11 |
| `kintell.db.backup_pre_sa2_backfill_20260426_151147` | 13.9 | 2026-04-26T15:06:39 |
| `kintell.db.backup_pre_self_group_backfill_20260426_152434` | 14.7 | 2026-04-26T15:11:47 |
| `kintell.db.session_backup_20260426_152425` | 14.7 | 2026-04-26T15:11:47 |
| `kintell.db.backup_pre_nqaits_ingest_20260426_155303` | 15.3 | 2026-04-26T15:24:34 |
| `kintell.db.session_backup_20260426_155257` | 15.3 | 2026-04-26T15:24:34 |
| `kintell.db.backup_pre_step6_20260427_163342` | 445.3 | 2026-04-26T15:55:58 |
| `kintell.db.backup_pre_step5_20260427_171439` | 455.1 | 2026-04-27T16:34:03 |
| `kintell.db.backup_pre_step5c_20260427_172338` | 466.6 | 2026-04-27T17:14:43 |
| `kintell.db.backup_pre_step5b_20260427_180757` | 467.1 | 2026-04-27T17:23:43 |
| `kintell.db.backup_pre_step5b_prime_20260427_204131` | 495.0 | 2026-04-27T20:40:17 |
| `kintell.db.backup_pre_step1b_20260427_213320` | 523.9 | 2026-04-27T21:33:22 |
| `kintell.db.backup_pre_step8_20260427_215012` | 524.0 | 2026-04-27T21:50:14 |
| `kintell.db.backup_pre_sa2_cohort_20260428_120804` | 526.5 | 2026-04-27T21:50:14 |
| `kintell.db.backup_pre_layer3_20260428_122241` | 526.8 | 2026-04-28T12:08:05 |
| `kintell.db.backup_pre_step1c_20260428_165521` | 531.5 | 2026-04-28T16:55:24 |
| `kintell.db.backup_pre_4_3_5_20260430_101700` | 531.6 | 2026-04-28T16:55:25 |
| `kintell.db.backup_pre_4_3_5b_20260430_110004` | 531.6 | 2026-04-30T10:17:01 |
| `kintell.db.backup_pre_2_5_1_20260430_114306` | 531.6 | 2026-04-30T11:00:04 |
| `kintell.db.backup_pre_2_5_1_20260430_115717` | 538.6 | 2026-04-30T11:43:07 |
| `kintell.db.backup_pre_2_5_2_20260430_144707` | 538.6 | 2026-04-30T11:57:17 |
| `kintell.db.backup_pre_2_5_1_20260504_125129` | 541.3 | 2026-05-04T12:32:15 |
| `kintell.db.backup_pre_layer3_20260504_134117` | 541.3 | 2026-05-04T12:51:30 |
| `kintell.db.backup_pre_2_5_1_20260504_140136` | 541.3 | 2026-05-04T14:01:28 |
| `kintell.db.backup_pre_layer3_20260504_142054` | 541.3 | 2026-05-04T14:01:37 |
| `kintell.db.backup_pre_2_5_2_20260504_142735` | 541.3 | 2026-05-04T14:20:55 |
| `kintell.db.backup_pre_layer3_20260509_234301` | 546.0 | 2026-05-09T23:41:00 |
| `kintell.db.backup_pre_2_5_2_20260509_234302` | 546.0 | 2026-05-09T23:43:02 |
| `kintell.db.backup_pre_layer3_20260510_005250` | 554.4 | 2026-05-10T00:51:48 |
| `kintell.db.backup_pre_2_5_2_20260510_005320` | 554.8 | 2026-05-10T00:52:51 |
| `kintell.db.backup_pre_layer3_20260510_020650` | 611.1 | 2026-05-10T02:05:52 |
| `kintell.db.backup_pre_2_5_2_20260510_020652` | 613.3 | 2026-05-10T02:06:52 |
| **TOTAL** | **14,092.5** | |

## 6. `audit_log` summary

Total rows: **174**
Columns: `audit_id`, `actor`, `action`, `subject_type`, `subject_id`, `before_json`, `after_json`, `reason`, `occurred_at`

### 6a. Counts by `action`

| action | Count |
|---|---:|
| `accept_merge` | 110 |
| `layer3_banding_v1` | 6 |
| `layer3_catchment_banding_v1` | 5 |
| `service_catchment_cache_populate_v1` | 4 |
| `rename_group` | 3 |
| `data_seed` | 2 |
| `service_catchment_cache_rename_column_v1` | 1 |
| `service_catchment_cache_extend_v1` | 1 |
| `self_group_backfill_v1` | 1 |
| `seed_model_assumptions` | 1 |
| `schema_migration_v0_5` | 1 |
| `schema_migration_v0_4` | 1 |
| `schema_migration_training_completions` | 1 |
| `salm_sa2_ingest_v1` | 1 |
| `sa2_polygon_overwrite_v1` | 1 |
| `sa2_polygon_backfill_v1` | 1 |
| `sa2_erp_ingest_v1` | 1 |
| `sa2_cohort_build_v1` | 1 |
| `sa2_backfill_v1` | 1 |
| `reverse_accept` | 1 |
| `nqs_ingest_q4_2025` | 1 |
| `nqaits_ingest_v1` | 1 |
| `language_at_home_top_n_ingest_v1` | 1 |
| `language_at_home_top_n_create_v1` | 1 |
| `jsa_ivi_ingest_v1` | 1 |
| `ingest_ncver_completions` | 1 |
| `erp_parent_cohort_25_44_share_ingest_v1` | 1 |
| `data_migration` | 1 |
| `country_of_birth_top_n_ingest_v1` | 1 |
| `country_of_birth_top_n_create_v1` | 1 |
| `census_women_35_44_with_child_share_ingest_v1` | 1 |
| `census_women_25_34_with_child_share_ingest_v1` | 1 |
| `census_single_parent_family_share_ingest_v1` | 1 |
| `census_partnered_25_44_share_ingest_v1` | 1 |
| `census_overseas_born_share_ingest_v1` | 1 |
| `census_nes_share_ingest_v3` | 1 |
| `census_nes_share_ingest_v2` | 1 |
| `census_atsi_share_ingest_v1` | 1 |
| `add_model_assumption` | 1 |
| `acara_school_independent_share_ingest_v1` | 1 |
| `acara_school_govt_share_ingest_v1` | 1 |
| `acara_school_enrolment_total_ingest_v1` | 1 |
| `acara_school_enrolment_independent_share_ingest_v1` | 1 |
| `acara_school_enrolment_govt_share_ingest_v1` | 1 |
| `acara_school_enrolment_catholic_share_ingest_v1` | 1 |
| `acara_school_count_total_ingest_v1` | 1 |
| `acara_school_catholic_share_ingest_v1` | 1 |
| `abs_sa2_socioeconomic_ingest_v1` | 1 |
| `abs_sa2_education_employment_ingest_v1` | 1 |
| `abs_sa2_births_ingest_v1` | 1 |

### 6b. All rows

| audit_id | actor | action | subject_type | subject_id | before_json | after_json | reason | occurred_at |
|---|---|---|---|---|---|---|---|---|
| 1 | patrick | accept_merge | link_candidate | 299 | {"source_group": {"group_id": 877, "canonical_name": "Sparrow Nest Early Learning No 1 Pty Ltd", ... | {"dest_group_id": 1887, "entities_moved": 9, "brands_moved": 0} |  | 2026-04-22 01:28:29 |
| 2 | patrick | accept_merge | link_candidate | 300 | {"source_group": {"group_id": 36, "canonical_name": "Sparrow Nest Early Learning 102 Pty Ltd", "i... | {"dest_group_id": 1887, "entities_moved": 5, "brands_moved": 0} |  | 2026-04-22 01:28:29 |
| 3 | patrick | accept_merge | link_candidate | 301 | {"source_group": {"group_id": 118, "canonical_name": "Sparrow Group Qld Pty Ltd", "is_active": 1,... | {"dest_group_id": 1887, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 01:28:29 |
| 4 | patrick | accept_merge | link_candidate | 302 | {"source_group": {"group_id": 761, "canonical_name": "PMI Ashgrove Pty Ltd", "is_active": 1, "ent... | {"dest_group_id": 1887, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 01:28:29 |
| 5 | patrick | accept_merge | link_candidate | 303 | {"source_group": {"group_id": 977, "canonical_name": "Pacific Pines Childcare Centre Pty Ltd", "i... | {"dest_group_id": 1887, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 01:28:29 |
| 6 | patrick | accept_merge | link_candidate | 305 | {"source_group": {"group_id": 2009, "canonical_name": "Ormeau Ridge Early Learning Centre Pty Ltd... | {"dest_group_id": 1887, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 01:28:29 |
| 7 | patrick | accept_merge | link_candidate | 304 | {"source_group": {"group_id": 1578, "canonical_name": "Jacobs Early Learning Centre Pty Ltd", "is... | {"dest_group_id": 1887, "entities_moved": 2, "brands_moved": 0} |  | 2026-04-22 01:52:13 |
| 8 | patrick | reverse_accept | audit_log | 7 | {"reversing": {"source_group": {"group_id": 1578, "canonical_name": "Jacobs Early Learning Centre... | {"source_group_restored": 1578, "entities_restored": 2, "brands_restored": 0} |  | 2026-04-22 01:52:51 |
| 9 | patrick | accept_merge | link_candidate | 304 | {"source_group": {"group_id": 1578, "canonical_name": "Jacobs Early Learning Centre Pty Ltd", "is... | {"dest_group_id": 1887, "entities_moved": 2, "brands_moved": 0} |  | 2026-04-22 01:53:07 |
| 10 | patrick | accept_merge | link_candidate | 61 | {"source_group": {"group_id": 718, "canonical_name": "Harmony Yarrabilba One Pty Ltd", "is_active... | {"dest_group_id": 236, "entities_moved": 2, "brands_moved": 0} |  | 2026-04-22 02:04:37 |
| 11 | patrick | accept_merge | link_candidate | 62 | {"source_group": {"group_id": 378, "canonical_name": "Harmony Ripley PTY LTD", "is_active": 1, "e... | {"dest_group_id": 236, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 02:04:37 |
| 12 | patrick | accept_merge | link_candidate | 63 | {"source_group": {"group_id": 379, "canonical_name": "HARMONY BULIMBA PTY LTD", "is_active": 1, "... | {"dest_group_id": 236, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 02:04:37 |
| 13 | patrick | accept_merge | link_candidate | 64 | {"source_group": {"group_id": 383, "canonical_name": "HARMONY GRIFFIN PTY LTD", "is_active": 1, "... | {"dest_group_id": 236, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 02:04:37 |
| 14 | patrick | accept_merge | link_candidate | 65 | {"source_group": {"group_id": 772, "canonical_name": "HARMONY BROADBEACH PTY LTD", "is_active": 1... | {"dest_group_id": 236, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 02:04:37 |
| 15 | patrick | accept_merge | link_candidate | 66 | {"source_group": {"group_id": 773, "canonical_name": "HARMONY EAST BRISBANE PTY LTD", "is_active"... | {"dest_group_id": 236, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 02:04:37 |
| 16 | patrick | accept_merge | link_candidate | 67 | {"source_group": {"group_id": 2036, "canonical_name": "HARMONY CURRUMBIN PTY LTD", "is_active": 1... | {"dest_group_id": 236, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 02:04:37 |
| 17 | patrick | accept_merge | link_candidate | 68 | {"source_group": {"group_id": 2037, "canonical_name": "Harmony Greenslopes Pty Ltd", "is_active":... | {"dest_group_id": 236, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 02:04:37 |
| 18 | patrick | accept_merge | link_candidate | 69 | {"source_group": {"group_id": 2038, "canonical_name": "HARMONY BARDON PTY LTD", "is_active": 1, "... | {"dest_group_id": 236, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 02:04:37 |
| 19 | patrick | accept_merge | link_candidate | 70 | {"source_group": {"group_id": 2039, "canonical_name": "Harmony Coorparoo Pty Ltd", "is_active": 1... | {"dest_group_id": 236, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 02:04:37 |
| 20 | patrick | accept_merge | link_candidate | 71 | {"source_group": {"group_id": 2168, "canonical_name": "Harmony Balmoral Pty Ltd", "is_active": 1,... | {"dest_group_id": 236, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 02:04:37 |
| 21 | patrick | accept_merge | link_candidate | 72 | {"source_group": {"group_id": 2260, "canonical_name": "HARMONY CORINDA PTY LTD", "is_active": 1, ... | {"dest_group_id": 236, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 02:04:37 |
| 22 | patrick | accept_merge | link_candidate | 73 | {"source_group": {"group_id": 2284, "canonical_name": "Harmony Lennox Head One Pty Ltd", "is_acti... | {"dest_group_id": 236, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 02:04:37 |
| 23 | patrick | accept_merge | link_candidate | 74 | {"source_group": {"group_id": 2318, "canonical_name": "HARMONY EVERTON PARK PTY LTD", "is_active"... | {"dest_group_id": 236, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 02:04:37 |
| 24 | patrick | accept_merge | link_candidate | 75 | {"source_group": {"group_id": 2344, "canonical_name": "HARMONY HOPE ISLAND PTY LTD", "is_active":... | {"dest_group_id": 236, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 02:04:37 |
| 25 | patrick | accept_merge | link_candidate | 76 | {"source_group": {"group_id": 2345, "canonical_name": "HARMONY SPRINGFIELD PTY LTD", "is_active":... | {"dest_group_id": 236, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 02:04:37 |
| 26 | patrick | accept_merge | link_candidate | 77 | {"source_group": {"group_id": 2363, "canonical_name": "HARMONY BANGALOW PTY LTD", "is_active": 1,... | {"dest_group_id": 236, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 02:04:37 |
| 27 | patrick | accept_merge | link_candidate | 78 | {"source_group": {"group_id": 2364, "canonical_name": "Harmony North Lakes PTY LTD", "is_active":... | {"dest_group_id": 236, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 02:04:37 |
| 28 | patrick | accept_merge | link_candidate | 79 | {"source_group": {"group_id": 2449, "canonical_name": "HARMONY BAHRS SCRUB PTY LTD", "is_active":... | {"dest_group_id": 236, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 02:04:37 |
| 29 | patrick | accept_merge | link_candidate | 80 | {"source_group": {"group_id": 2509, "canonical_name": "HARMONY VARSITY LAKES PTY LTD", "is_active... | {"dest_group_id": 236, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 02:04:37 |
| 30 | patrick | accept_merge | link_candidate | 1 | {"source_group": {"group_id": 68, "canonical_name": "ASPIRE EARLY LEARNING & KINDERGARTEN TARNEIT... | {"dest_group_id": 11, "entities_moved": 3, "brands_moved": 0} |  | 2026-04-22 05:41:10 |
| 31 | patrick | accept_merge | link_candidate | 2 | {"source_group": {"group_id": 202, "canonical_name": "ASPIRE EARLY EDUCATION & KINDERGARTEN CLYDE... | {"dest_group_id": 11, "entities_moved": 2, "brands_moved": 0} |  | 2026-04-22 05:41:10 |
| 32 | patrick | accept_merge | link_candidate | 3 | {"source_group": {"group_id": 239, "canonical_name": "ASPIRE EARLY EDUCATION WOLLERT PTY LTD", "i... | {"dest_group_id": 11, "entities_moved": 2, "brands_moved": 0} |  | 2026-04-22 05:41:10 |
| 33 | patrick | accept_merge | link_candidate | 4 | {"source_group": {"group_id": 467, "canonical_name": "Aspire Early Education & Kindergarten Baldi... | {"dest_group_id": 11, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:41:10 |
| 34 | patrick | accept_merge | link_candidate | 5 | {"source_group": {"group_id": 750, "canonical_name": "ASPIRE EARLY EDUCATION BENDIGO PTY LTD", "i... | {"dest_group_id": 11, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:41:10 |
| 35 | patrick | accept_merge | link_candidate | 6 | {"source_group": {"group_id": 396, "canonical_name": "ASPIRE EARLY EDUCATION & KINDERGARTEN CRANB... | {"dest_group_id": 11, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:41:10 |
| 36 | patrick | accept_merge | link_candidate | 7 | {"source_group": {"group_id": 397, "canonical_name": "ASPIRE EARLY EDUCATION & KINDERGARTEN ROCKB... | {"dest_group_id": 11, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:41:10 |
| 37 | patrick | accept_merge | link_candidate | 8 | {"source_group": {"group_id": 407, "canonical_name": "ASPIRE EARLY EDUCATION and KINDERGARTEN CRA... | {"dest_group_id": 11, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:41:10 |
| 38 | patrick | accept_merge | link_candidate | 9 | {"source_group": {"group_id": 805, "canonical_name": "ASPIRE EARLY EDUCATION & KINDERGARTEN, WEST... | {"dest_group_id": 11, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:41:10 |
| 39 | patrick | accept_merge | link_candidate | 10 | {"source_group": {"group_id": 808, "canonical_name": "ASPIRE EARLY EDUCATION & KINDERGARTEN DEANS... | {"dest_group_id": 11, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:41:10 |
| 40 | patrick | accept_merge | link_candidate | 11 | {"source_group": {"group_id": 851, "canonical_name": "ASPIRE EARLY EDUCATION & KINDERGARTEN BELLA... | {"dest_group_id": 11, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:41:10 |
| 41 | patrick | accept_merge | link_candidate | 12 | {"source_group": {"group_id": 852, "canonical_name": "ASPIRE EARLY EDUCATION & KINDERGARTEN DONNY... | {"dest_group_id": 11, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:41:10 |
| 42 | patrick | accept_merge | link_candidate | 13 | {"source_group": {"group_id": 856, "canonical_name": "ASPIRE EARLY EDUCATION & KINDERGARTEN KALKA... | {"dest_group_id": 11, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:41:10 |
| 43 | patrick | accept_merge | link_candidate | 14 | {"source_group": {"group_id": 1733, "canonical_name": "ASPIRE EARLY EDUCATION & KINDERGARTEN LUCA... | {"dest_group_id": 11, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:41:10 |
| 44 | patrick | accept_merge | link_candidate | 15 | {"source_group": {"group_id": 1755, "canonical_name": "ASPIRE EARLY EDUCATION & KINDERGARTEN WEIR... | {"dest_group_id": 11, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:41:10 |
| 45 | patrick | accept_merge | link_candidate | 16 | {"source_group": {"group_id": 1976, "canonical_name": "BERWICK WATERS EARLY LEARNING CENTRE PTY L... | {"dest_group_id": 11, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:41:11 |
| 46 | patrick | accept_merge | link_candidate | 17 | {"source_group": {"group_id": 2045, "canonical_name": "ASCOT EARLY LEARNING CENTRE PTY LTD", "is_... | {"dest_group_id": 11, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:41:11 |
| 47 | patrick | accept_merge | link_candidate | 18 | {"source_group": {"group_id": 2046, "canonical_name": "CRANBOURNE WEST EARLY LEARNING CENTRE PTY ... | {"dest_group_id": 11, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:41:11 |
| 48 | patrick | accept_merge | link_candidate | 19 | {"source_group": {"group_id": 2131, "canonical_name": "ATHERSTONE EARLY LEARNING CENTRE PTY LTD",... | {"dest_group_id": 11, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:41:11 |
| 49 | patrick | accept_merge | link_candidate | 20 | {"source_group": {"group_id": 2337, "canonical_name": "COBBLEBANK EARLY LEARNING CENTRE PTY LTD",... | {"dest_group_id": 11, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:41:11 |
| 50 | patrick | accept_merge | link_candidate | 21 | {"source_group": {"group_id": 2346, "canonical_name": "CLYDE NORTH EARLY LEARNING CENTRE PTY LTD"... | {"dest_group_id": 11, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:41:11 |
| 51 | patrick | accept_merge | link_candidate | 22 | {"source_group": {"group_id": 2379, "canonical_name": "ASPIRE EARLY EDUCATION & KINDERGARTEN WERR... | {"dest_group_id": 11, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:41:11 |
| 52 | patrick | accept_merge | link_candidate | 23 | {"source_group": {"group_id": 2383, "canonical_name": "Tarneit North Early Learning Centre PTY LT... | {"dest_group_id": 11, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:41:11 |
| 53 | patrick | accept_merge | link_candidate | 24 | {"source_group": {"group_id": 2393, "canonical_name": "ASPIRE EARLY EDUCATION & KINDERGARTEN THOR... | {"dest_group_id": 11, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:41:11 |
| 54 | patrick | accept_merge | link_candidate | 25 | {"source_group": {"group_id": 2564, "canonical_name": "ASPIRE EARLY EDUCATION and KINDERGARTEN AR... | {"dest_group_id": 11, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:41:11 |
| 55 | patrick | accept_merge | link_candidate | 26 | {"source_group": {"group_id": 2565, "canonical_name": "ASPIRE EARLY EDUCATION and KINDERGARTEN MA... | {"dest_group_id": 11, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:41:11 |
| 56 | patrick | accept_merge | link_candidate | 27 | {"source_group": {"group_id": 2578, "canonical_name": "ASPIRE EARLY EDUCATION & KINDERGARTEN MANO... | {"dest_group_id": 11, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:41:11 |
| 57 | patrick | accept_merge | link_candidate | 28 | {"source_group": {"group_id": 2579, "canonical_name": "ASPIRE EARLY EDUCATION & KINDERGARTEN SMIT... | {"dest_group_id": 11, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:41:11 |
| 58 | patrick | accept_merge | link_candidate | 29 | {"source_group": {"group_id": 2580, "canonical_name": "ASPIRE EARLY EDUCATION & KINDERGARTEN RIVE... | {"dest_group_id": 11, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:41:11 |
| 59 | patrick | accept_merge | link_candidate | 30 | {"source_group": {"group_id": 2581, "canonical_name": "ASPIRE EARLY EDUCATION & KINDERGARTEN EVER... | {"dest_group_id": 11, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:41:11 |
| 60 | patrick | accept_merge | link_candidate | 31 | {"source_group": {"group_id": 2684, "canonical_name": "ASPIRE EARLY EDUCATION & KINDERGARTEN BEVE... | {"dest_group_id": 11, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:41:11 |
| 61 | patrick | accept_merge | link_candidate | 244 | {"source_group": {"group_id": 265, "canonical_name": "Tick-Tock Services Pty Ltd", "is_active": 1... | {"dest_group_id": 3256, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:52:33 |
| 62 | patrick | accept_merge | link_candidate | 245 | {"source_group": {"group_id": 690, "canonical_name": "SLK TRADING POINT COOK PTY LTD", "is_active... | {"dest_group_id": 3256, "entities_moved": 2, "brands_moved": 0} |  | 2026-04-22 05:52:55 |
| 63 | patrick | accept_merge | link_candidate | 32 | {"source_group": {"group_id": 382, "canonical_name": "EDGE EARLY LEARNING QLD PTY LTD", "is_activ... | {"dest_group_id": 873, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:53:49 |
| 64 | patrick | accept_merge | link_candidate | 33 | {"source_group": {"group_id": 504, "canonical_name": "EDGE EARLY LEARNING ACT PTY LTD", "is_activ... | {"dest_group_id": 873, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:53:49 |
| 65 | patrick | accept_merge | link_candidate | 34 | {"source_group": {"group_id": 706, "canonical_name": "Edge Early Learning - Pimpama Pty Ltd", "is... | {"dest_group_id": 873, "entities_moved": 2, "brands_moved": 0} |  | 2026-04-22 05:53:49 |
| 66 | patrick | accept_merge | link_candidate | 35 | {"source_group": {"group_id": 729, "canonical_name": "Edge Early Learning Annerley Pty Ltd", "is_... | {"dest_group_id": 873, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:53:49 |
| 67 | patrick | accept_merge | link_candidate | 36 | {"source_group": {"group_id": 767, "canonical_name": "EDGE EARLY LEARNING KARANA DOWNS PTY LTD", ... | {"dest_group_id": 873, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:53:49 |
| 68 | patrick | accept_merge | link_candidate | 37 | {"source_group": {"group_id": 1975, "canonical_name": "Montague Road Early Learning Pty Ltd", "is... | {"dest_group_id": 873, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:53:49 |
| 69 | patrick | accept_merge | link_candidate | 38 | {"source_group": {"group_id": 2076, "canonical_name": "Edge Early Learning Tarragindi Operating C... | {"dest_group_id": 873, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:53:49 |
| 70 | patrick | accept_merge | link_candidate | 39 | {"source_group": {"group_id": 2077, "canonical_name": "Edge Early Learning Jane Street Pty Ltd", ... | {"dest_group_id": 873, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:53:49 |
| 71 | patrick | accept_merge | link_candidate | 40 | {"source_group": {"group_id": 2110, "canonical_name": "Edge Early Learning Strathpine Pty Ltd", "... | {"dest_group_id": 873, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:53:49 |
| 72 | patrick | accept_merge | link_candidate | 41 | {"source_group": {"group_id": 2115, "canonical_name": "Edge Early Learning Nundah Pty Ltd", "is_a... | {"dest_group_id": 873, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:53:49 |
| 73 | patrick | accept_merge | link_candidate | 42 | {"source_group": {"group_id": 2125, "canonical_name": "Edge Early Learning Kelvin Grove Pty Ltd",... | {"dest_group_id": 873, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:53:49 |
| 74 | patrick | accept_merge | link_candidate | 43 | {"source_group": {"group_id": 2126, "canonical_name": "Edge Early Learning Cannon Hill Pty Ltd", ... | {"dest_group_id": 873, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:53:49 |
| 75 | patrick | accept_merge | link_candidate | 44 | {"source_group": {"group_id": 2129, "canonical_name": "Edge Early Learning Bilinga Pty Ltd", "is_... | {"dest_group_id": 873, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:53:49 |
| 76 | patrick | accept_merge | link_candidate | 45 | {"source_group": {"group_id": 2130, "canonical_name": "Edge Early Learning Coomera Pty Ltd", "is_... | {"dest_group_id": 873, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:53:49 |
| 77 | patrick | accept_merge | link_candidate | 46 | {"source_group": {"group_id": 2133, "canonical_name": "Edge Early Learning Peregian Breeze Pty Lt... | {"dest_group_id": 873, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:53:49 |
| 78 | patrick | accept_merge | link_candidate | 47 | {"source_group": {"group_id": 2146, "canonical_name": "Edge Early Learning Marie Street Pty Ltd",... | {"dest_group_id": 873, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:53:49 |
| 79 | patrick | accept_merge | link_candidate | 48 | {"source_group": {"group_id": 2170, "canonical_name": "Edge Early Learning South Brisbane Pty Ltd... | {"dest_group_id": 873, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:53:49 |
| 80 | patrick | accept_merge | link_candidate | 49 | {"source_group": {"group_id": 2177, "canonical_name": "Edge Early Learning Wynnum Pty Ltd", "is_a... | {"dest_group_id": 873, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:53:49 |
| 81 | patrick | accept_merge | link_candidate | 50 | {"source_group": {"group_id": 2202, "canonical_name": "Edge Early Learning Ferny Grove Pty Ltd", ... | {"dest_group_id": 873, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:53:49 |
| 82 | patrick | accept_merge | link_candidate | 51 | {"source_group": {"group_id": 2203, "canonical_name": "Edge Early Learning Zillmere Pty Ltd", "is... | {"dest_group_id": 873, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:53:49 |
| 83 | patrick | accept_merge | link_candidate | 52 | {"source_group": {"group_id": 2204, "canonical_name": "Edge Early Learning North Harbour Pty Ltd"... | {"dest_group_id": 873, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:53:49 |
| 84 | patrick | accept_merge | link_candidate | 53 | {"source_group": {"group_id": 2205, "canonical_name": "Edge Early Learning Aroona Pty Ltd", "is_a... | {"dest_group_id": 873, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:53:49 |
| 85 | patrick | accept_merge | link_candidate | 54 | {"source_group": {"group_id": 2207, "canonical_name": "Edge Early Learning Marsden Pty Ltd", "is_... | {"dest_group_id": 873, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:53:49 |
| 86 | patrick | accept_merge | link_candidate | 55 | {"source_group": {"group_id": 2217, "canonical_name": "Edge Early Learning Elanora Pty Ltd", "is_... | {"dest_group_id": 873, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:53:49 |
| 87 | patrick | accept_merge | link_candidate | 56 | {"source_group": {"group_id": 2381, "canonical_name": "EDGE EARLY LEARNING WATERFORD PTY LTD", "i... | {"dest_group_id": 873, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:53:49 |
| 88 | patrick | accept_merge | link_candidate | 57 | {"source_group": {"group_id": 2388, "canonical_name": "EDGE EARLY LEARNING EAGLEBY PTY LTD", "is_... | {"dest_group_id": 873, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:53:49 |
| 89 | patrick | accept_merge | link_candidate | 58 | {"source_group": {"group_id": 2389, "canonical_name": "EDGE EARLY LEARNING BEAUDESERT PTY LTD", "... | {"dest_group_id": 873, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:53:49 |
| 90 | patrick | accept_merge | link_candidate | 60 | {"source_group": {"group_id": 3084, "canonical_name": "Edge Early Learning Peregian Springs Pty L... | {"dest_group_id": 873, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 05:53:49 |
| 91 | patrick | accept_merge | link_candidate | 59 | {"source_group": {"group_id": 2661, "canonical_name": "Edge Early Learning Bellbird Park Pty Ltd"... | {"dest_group_id": 873, "entities_moved": 2, "brands_moved": 0} |  | 2026-04-22 05:53:49 |
| 92 | patrick | rename_group | group | 1887 | {"display_name": null, "canonical_name": "Sparrow Group Vic Pty Ltd"} | {"display_name": "Sparrow", "canonical_name": "Sparrow Group Vic Pty Ltd"} |  | 2026-04-22 07:21:07 |
| 93 | patrick | rename_group | group | 1887 | {"display_name": "Sparrow", "canonical_name": "Sparrow Group Vic Pty Ltd"} | {"display_name": null, "canonical_name": "Sparrow Group Vic Pty Ltd"} |  | 2026-04-22 07:21:11 |
| 94 | patrick | accept_merge | link_candidate | 81 | {"source_group": {"group_id": 795, "canonical_name": "JML Trading Frankston North Pty Ltd", "is_a... | {"dest_group_id": 2660, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 07:23:24 |
| 95 | patrick | accept_merge | link_candidate | 82 | {"source_group": {"group_id": 803, "canonical_name": "JML Trading Essendon Pty Ltd", "is_active":... | {"dest_group_id": 2660, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 07:23:24 |
| 96 | patrick | accept_merge | link_candidate | 83 | {"source_group": {"group_id": 814, "canonical_name": "JML Trading Dandenong Pty Ltd", "is_active"... | {"dest_group_id": 2660, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 07:23:24 |
| 97 | patrick | accept_merge | link_candidate | 84 | {"source_group": {"group_id": 815, "canonical_name": "JML Trading Mt Cottrell Pty Ltd", "is_activ... | {"dest_group_id": 2660, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 07:23:24 |
| 98 | patrick | accept_merge | link_candidate | 85 | {"source_group": {"group_id": 816, "canonical_name": "JML Trading Boronia Pty Ltd", "is_active": ... | {"dest_group_id": 2660, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 07:23:24 |
| 99 | patrick | accept_merge | link_candidate | 86 | {"source_group": {"group_id": 839, "canonical_name": "JML Trading Clyde North Pty Ltd", "is_activ... | {"dest_group_id": 2660, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 07:23:24 |
| 100 | patrick | accept_merge | link_candidate | 87 | {"source_group": {"group_id": 1785, "canonical_name": "JML TRADING WALLAN PTY LTD", "is_active": ... | {"dest_group_id": 2660, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 07:23:24 |
| 101 | patrick | accept_merge | link_candidate | 88 | {"source_group": {"group_id": 2002, "canonical_name": "SLK TRADING ARMADALE PTY LTD", "is_active"... | {"dest_group_id": 2660, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 07:23:24 |
| 102 | patrick | accept_merge | link_candidate | 89 | {"source_group": {"group_id": 2082, "canonical_name": "SLK TRADING BRIGHTON EAST PTY LTD", "is_ac... | {"dest_group_id": 2660, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 07:23:24 |
| 103 | patrick | accept_merge | link_candidate | 90 | {"source_group": {"group_id": 2224, "canonical_name": "SLK TRADING WILLIAMS LANDING PTY LTD", "is... | {"dest_group_id": 2660, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 07:23:24 |
| 104 | patrick | accept_merge | link_candidate | 91 | {"source_group": {"group_id": 2233, "canonical_name": "JML TRADING WILLIAMSTOWN PTY LTD", "is_act... | {"dest_group_id": 2660, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 07:23:24 |
| 105 | patrick | accept_merge | link_candidate | 92 | {"source_group": {"group_id": 2268, "canonical_name": "SLK TRADING TARNEIT PTY LTD", "is_active":... | {"dest_group_id": 2660, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 07:23:24 |
| 106 | patrick | accept_merge | link_candidate | 93 | {"source_group": {"group_id": 2329, "canonical_name": "SLK TRADING NUNAWADING PTY LTD", "is_activ... | {"dest_group_id": 2660, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 07:23:24 |
| 107 | patrick | accept_merge | link_candidate | 94 | {"source_group": {"group_id": 2370, "canonical_name": "JML Trading Beaconsfield Pty Ltd", "is_act... | {"dest_group_id": 2660, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 07:23:24 |
| 108 | patrick | accept_merge | link_candidate | 95 | {"source_group": {"group_id": 2376, "canonical_name": "JML TRADING GREENVALE PTY LTD", "is_active... | {"dest_group_id": 2660, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 07:23:24 |
| 109 | patrick | accept_merge | link_candidate | 96 | {"source_group": {"group_id": 2403, "canonical_name": "JML TRADING MORNINGTON PTY LTD", "is_activ... | {"dest_group_id": 2660, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 07:23:24 |
| 110 | patrick | accept_merge | link_candidate | 97 | {"source_group": {"group_id": 2410, "canonical_name": "JML TRADING CROYDON PTY LTD", "is_active":... | {"dest_group_id": 2660, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 07:23:24 |
| 111 | patrick | accept_merge | link_candidate | 98 | {"source_group": {"group_id": 2411, "canonical_name": "JML Trading Ashwood Pty Ltd", "is_active":... | {"dest_group_id": 2660, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 07:23:24 |
| 112 | patrick | accept_merge | link_candidate | 99 | {"source_group": {"group_id": 2507, "canonical_name": "JML TRADING WERRIBEE PTY LTD", "is_active"... | {"dest_group_id": 2660, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 07:23:24 |
| 113 | patrick | accept_merge | link_candidate | 247 | {"source_group": {"group_id": 1089, "canonical_name": "SLK TRADING MAIDSTONE PTY LTD", "is_active... | {"dest_group_id": 3256, "entities_moved": 1, "brands_moved": 0} |  | 2026-04-22 07:24:33 |
| 114 | patrick | rename_group | group | 1887 | {"display_name": null, "canonical_name": "Sparrow Group Vic Pty Ltd"} | {"display_name": "Sparrow Group", "canonical_name": "Sparrow Group Vic Pty Ltd"} |  | 2026-04-22 08:29:13 |
| 115 | system | schema_migration_v0_4 | table | 0 | {"services_columns": ["address_line", "approval_granted_date", "approved_places", "brand_id", "cr... | {"services_columns": ["address_line", "approval_granted_date", "approved_places", "aria_plus", "b... | Added 11 columns to services: ['aria_plus', 'provider_management_type', 'qa1', 'qa2', 'qa3', 'qa4... | 2026-04-23 10:58:01 |
| 116 | system | nqs_ingest_q4_2025 | table | 0 |  | {"services_matched": 17882, "services_updated": 17882, "services_nqs_only": 145, "services_db_onl... | Updated 17882 services and 3663 group ownership_types from NQS Data Q4 2025.XLSX | 2026-04-23 11:01:21 |
| 117 | migrate_schema_v0_5.py | schema_migration_v0_5 | schema | metric_definitions+model_assumptions | {"table_count": 23, "tables_present": ["audit_log", "brands", "entities", "entity_financials", "e... | {"table_count": 23, "tables_added": [], "indexes_added": ["ix_metric_def_classification", "ix_mod... | Foundation for OBS/DER/COM classification + configurable-assumptions discipline (Phase 0a). See r... | 2026-04-25T18:14:56 |
| 118 | seed_model_assumptions.py | seed_model_assumptions | table | model_assumptions | {"row_count": 0} | {"row_count": 10, "inserted_keys": ["educator_ratio_0_24m", "educator_ratio_24_36m", "educator_ra... | Seed model_assumptions with 10 default values per project brief §6.2. Patrick confirmed defaults ... | 2026-04-25T18:19:52 |
| 119 | add_commentary_threshold.py | add_model_assumption | model_assumptions | commentary_inspection_threshold | {"row_count": 10} | {"row_count": 11, "inserted_key": "commentary_inspection_threshold", "no_op": false} | Add commentary_inspection_threshold (0.30) to model_assumptions. Required by Phase 0a Step 3 — Qu... | 2026-04-25T18:26:34 |
| 120 | migrate_training_completions_tables.py | schema_migration_training_completions | schema | training_completions+training_completions_ingest_run | {"table_count": 23, "tables_present": ["audit_log", "brands", "entities", "entity_financials", "e... | {"table_count": 25, "tables_added": ["training_completions", "training_completions_ingest_run"], ... | Phase 1.5 Step 1 — staging tables for NCVER training completions ingest. Will hold supply-side da... | 2026-04-25T19:30:45 |
| 121 | ingest_ncver_completions.py | ingest_ncver_completions | table | training_completions | {"deleted_prior_leaves": 0} | {"run_id": 1, "rows_ingested": 768, "source_file": "abs_data\\NCVER_ECEC_Completions_2019-2024.xl... | NCVER training-completions ingest. Phase 1.5 Step 2. Leaf rows only; aggregate rows in source ski... | 2026-04-25T19:38:18 |
| 122 | add_workforce_assumptions.py v2 | data_seed | table | model_assumptions | {"missing_keys": ["educator_ratio_ldc_blended", "educator_ratio_oshc"]} | {"inserted": ["educator_ratio_ldc_blended", "educator_ratio_oshc"], "skipped": []} | Phase 1 pre-step backfill. v2 of add_workforce_assumptions.py committed both rows to model_assump... | 2026-04-25T19:56:59 |
| 123 | seed_workforce_metrics.py v1 | data_seed | table | metric_definitions | {"existing_keys": []} | {"inserted": ["required_educators_centre", "required_educators_group", "workforce_growth_12m", "w... | Phase 1 Step A: seed six Workforce metric_definitions rows (required_educators_centre, required_e... | 2026-04-25T20:02:49 |
| 124 | migrate_ratio_convention_to_cpe.py v1 | data_migration | table | model_assumptions | {"educator_ratio_0_24m": {"value_numeric": 0.25, "value_text": "1:4", "units": "ratio"}, "educato... | {"converted": ["educator_ratio_0_24m", "educator_ratio_24_36m", "educator_ratio_36m_plus"], "skip... | Convert Phase 0a-seeded educator_ratio rows from educators-per-child (units='ratio') to children-... | 2026-04-25T20:25:11 |
| 125 | layer2_step1_sa2_backfill_v2 | sa2_backfill_v1 | services | 0 | {"services_sa2_populated": 0, "concordance_rows_loaded": 1547, "concordance_rows_skipped_blank": ... | {"services_sa2_populated": 17336, "unmatched_postcodes": 881, "no_postcode": 6, "coverage_pct_act... | Phase 2.5 Layer 2 Step 1 — postcode-keyed SA2 backfill via abs_data/postcode_to_sa2_concordance.c... | 2026-04-26 05:11:47 |
| 126 | layer2_step2_self_group_backfill_v1 | self_group_backfill_v1 | entities_groups | 0 | {"groups_total": 4187, "orphan_entity_count": 2320, "groups_with_parent_entity": 0} | {"groups_total_delta": 2320, "entities_linked": 2320, "ownership_distribution": {"private": 407, ... | Phase 2.5 Layer 2 Step 2 — orphan-entity self-group backfill. Created 2320 groups (one per orphan... | 2026-04-26 05:24:34 |
| 127 | layer2_step4_nqaits_ingest_v1 | nqaits_ingest_v1 | nqs_history | 0 | {"nqs_history_exists": false, "expected_volume_estimate": 807526} | {"nqs_history_rowcount": 807526, "unique_service_ids": 23439, "sheets_ingested": 50, "pa_chain_ch... | Phase 2.5 Layer 2 Step 4 — NQAITS quarterly historical ingest. Created nqs_history table + 3 inde... | 2026-04-26 05:55:58 |
| 128 | layer2_step6_apply_v2 | sa2_erp_ingest_v1 | abs_sa2_erp_annual | 0 | {"rows": 0} | {"rows": 88344, "payload": {"rows_inserted": 88344, "distinct_sa2": 2454, "distinct_years": 9, "y... | Layer 2 Step 6: ABS ERP at SA2 ingest (long format) | 2026-04-27T16:34:03.576805 |
| 129 | layer2_step5_apply | salm_sa2_ingest_v1 | abs_sa2_unemployment_quarterly | 0 | {"rows": 0} | {"rows": 142496, "payload": {"rows_inserted": 142496, "distinct_sa2": 2336, "distinct_quarters": ... | Layer 2 Step 5: SALM SA2 unemployment ingest | 2026-04-27T17:14:43.720449 |
| 130 | layer2_step5c_apply | jsa_ivi_ingest_v1 | jsa_ivi_state_monthly | 0 | {"state": 0, "remoteness": 0, "concordance": 0} | {"state": 4338, "remoteness": 348, "concordance": 88, "payload": {"state_rows_inserted": 4338, "r... | Layer 2 Step 5c: JSA IVI ingest (ANZSCO 4211 + 2411, state + remoteness) | 2026-04-27T17:23:43.789708 |
| 131 | layer2_step5b_apply | abs_sa2_socioeconomic_ingest_v1 | abs_sa2_socioeconomic_annual | 0 | {"rows": 0} | {"rows": 161964, "payload": {"rows_inserted": 161964, "distinct_sa2": 2454, "metrics_count": 6, "... | Layer 2 Step 5b: SA2 socioeconomic time series (6 income metrics, mixed annual + Census cadence) | 2026-04-27T18:08:10.029397 |
| 132 | layer2_step5b_prime_apply | abs_sa2_education_employment_ingest_v1 | abs_sa2_education_employment_annual | 0 | {"rows": 0} | {"rows": 203527, "payload": {"rows": 203527, "rows_ee": 160376, "rows_t33_derived": 43151, "disti... | Phase 2.5 Layer 2 Step 5b-prime: SA2 education + employment time series. 16 metrics from ABS Data... | 2026-04-27T10:41:52.526274 |
| 133 | layer2_step1b_apply | sa2_polygon_backfill_v1 | services | 0 | {"payload": {"candidates": 869, "null_sa2": 887, "unrecoverable_no_latlng": 18, "with_sa2": 17336... | {"payload": {"assigned": 867, "coverage": 0.998902, "hit_rate": 0.997699, "method": "sjoin within... | Layer 2 Step 1b: SA2 polygon point-in-polygon backfill. Assigned 867/869 candidates (99.77%). Mis... | 2026-04-27 11:33:23 |
| 134 | layer2_step8_apply | abs_sa2_births_ingest_v1 | abs_sa2_births_annual | 0 | {"payload": {"table": "abs_sa2_births_annual", "table_existed_pre": false}, "rows": 0} | {"payload": {"distinct_sa2": 2450, "method": "openpyxl iter_rows; year-col + sub-header 'Births' ... | Layer 2 Step 8: SA2 births annual ingest. 34,300 records (34,300 with numeric values, 0 confident... | 2026-04-27 11:50:14 |
| 135 | sa2_cohort_apply | sa2_cohort_build_v1 | sa2_cohort | 0 | {"rows": 0} | {"rows": 2473} | Build sa2_cohort lookup via SA2 centroid -> RA polygon spatial join; sources ASGS_2021_Main_Struc... | 2026-04-28 02:08:05 |
| 136 | layer3_apply | layer3_banding_v1 | layer3_sa2_metric_banding | 0 | {"rows": 0} | {"rows": 23946} | Layer 3 banding: percentile/decile/band per (metric x SA2 x latest-year x cohort). 23946 rows. 10... | 2026-04-28 02:22:42 |
| 137 | layer2_step1c_apply | sa2_polygon_overwrite_v1 | services | 0 | {"payload": {"active_services": 18223, "cross_state_mismatches": 1435, "with_latlng": 17882, "wit... | {"payload": {"assigned": 17839, "candidates_attempted": 17882, "cross_state_mismatches_post": 9, ... | Layer 2 Step 1c: SA2 polygon OVERWRITE rebuild. Re-derived sa2_code for 17,882 active services wi... | 2026-04-28 06:55:25 |
| 138 | layer4_3_5_apply | service_catchment_cache_extend_v1 | service_catchment_cache | 0 | {"columns": ["service_id", "sa2_code", "sa2_name", "u5_pop", "median_income", "seifa_irsd", "unem... | {"columns": ["service_id", "sa2_code", "sa2_name", "u5_pop", "median_income", "seifa_irsd", "unem... | Layer 4.3 sub-pass 4.3.5: schema extension on service_catchment_cache. Added 4 catchment ratio co... | 2026-04-30 00:17:01 |
| 139 | layer4_3_5b_apply | service_catchment_cache_rename_column_v1 | service_catchment_cache | 0 | {"columns": ["service_id", "sa2_code", "sa2_name", "u5_pop", "median_income", "seifa_irsd", "unem... | {"columns": ["service_id", "sa2_code", "sa2_name", "u5_pop", "median_income", "seifa_irsd", "unem... | Layer 4.3 sub-pass 4.3.5b: rename column capture_rate -> demand_share_state on service_catchment_... | 2026-04-30 01:00:04 |
| 140 | layer2_5_apply | service_catchment_cache_populate_v1 | service_catchment_cache | 0 | {"prior_rows": 0} | {"inserted_rows": 18203, "backup": "kintell.db.backup_pre_2_5_1_20260430_114306", "attendance_fac... | Layer 2.5 sub-pass 2.5.1: full populate of service_catchment_cache. Per-SA2 calibrated rate + rul... | 2026-04-30 01:43:07 |
| 141 | layer2_5_apply | service_catchment_cache_populate_v1 | service_catchment_cache | 0 | {"prior_rows": 18203} | {"inserted_rows": 18203, "backup": "kintell.db.backup_pre_2_5_1_20260430_115717", "attendance_fac... | Layer 2.5 sub-pass 2.5.1: full populate of service_catchment_cache. Per-SA2 calibrated rate + rul... | 2026-04-30 01:57:17 |
| 142 | layer3_x_catchment_apply | layer3_catchment_banding_v1 | layer3_sa2_metric_banding | 0 | {"prior_rows_for_metrics": 0} | {"inserted_rows": 9035, "metrics": ["sa2_supply_ratio", "sa2_child_to_place", "sa2_adjusted_deman... | Layer 2.5 sub-pass 2.5.2: Layer 3.x catchment metric banding. Bands 4 catchment metrics from serv... | 2026-04-30 04:47:08 |
| 143 | layer4_4_step_a2_apply | census_nes_share_ingest_v2 | abs_sa2_education_employment_annual | 0 | {"existing_rows_for_metric": 0, "max_audit_id": 142, "target_table_rows": 203527} | {"rows_inserted": 7272, "sa2_count": 2445, "years": [2011, 2016, 2021], "national_2011_share": 0.... | A2 NES share ingest (v2) from 2021 TSP T10A+T10B; closes nes_share_pct dormancy in calibrate_part... | 2026-05-04 02:32:15 |
| 144 | layer2_5_apply | service_catchment_cache_populate_v1 | service_catchment_cache | 0 | {"prior_rows": 18203} | {"inserted_rows": 18203, "backup": "kintell.db.backup_pre_2_5_1_20260504_125129", "attendance_fac... | Layer 2.5 sub-pass 2.5.1: full populate of service_catchment_cache. Per-SA2 calibrated rate + rul... | 2026-05-04 02:51:30 |
| 145 | layer3_apply | layer3_banding_v1 | layer3_sa2_metric_banding | 0 | {"rows": 0} | {"rows": 26363} | Layer 3 banding: percentile/decile/band per (metric x SA2 x latest-year x cohort). 26363 rows. 11... | 2026-05-04 03:41:18 |
| 146 | layer4_4_step_a2_apply | census_nes_share_ingest_v3 | abs_sa2_education_employment_annual | 0 | {"existing_rows_for_metric": 7272, "max_audit_id": 145, "target_table_rows": 210799} | {"rows_inserted": 7272, "sa2_count": 2445, "years": [2011, 2016, 2021], "national_2011_pct": 18.1... | A2 NES share ingest (v3) — UNIT FIX. Stores percentage (0-100) matching census_*_pct convention. ... | 2026-05-04 04:01:28 |
| 147 | layer2_5_apply | service_catchment_cache_populate_v1 | service_catchment_cache | 0 | {"prior_rows": 18203} | {"inserted_rows": 18203, "backup": "kintell.db.backup_pre_2_5_1_20260504_140136", "attendance_fac... | Layer 2.5 sub-pass 2.5.1: full populate of service_catchment_cache. Per-SA2 calibrated rate + rul... | 2026-05-04 04:01:37 |
| 148 | layer3_apply | layer3_banding_v1 | layer3_sa2_metric_banding | 0 | {"rows": 0} | {"rows": 26363} | Layer 3 banding: percentile/decile/band per (metric x SA2 x latest-year x cohort). 26363 rows. 11... | 2026-05-04 04:20:55 |
| 149 | layer3_x_catchment_apply | layer3_catchment_banding_v1 | layer3_sa2_metric_banding | 0 | {"prior_rows_for_metrics": 0} | {"inserted_rows": 9035, "metrics": ["sa2_supply_ratio", "sa2_child_to_place", "sa2_adjusted_deman... | Layer 2.5 sub-pass 2.5.2: Layer 3.x catchment metric banding. Bands 4 catchment metrics from serv... | 2026-05-04 04:27:36 |
| 150 | layer4_4_step_a10_apply | country_of_birth_top_n_create_v1 | schema | 0 | {"existed": false} | {"created_table": "abs_sa2_country_of_birth_top_n"} | A10 schema mutation: create table for top-3 country-of-birth display context (D-A2). New table no... | 2026-05-09 13:41:00 |
| 151 | layer4_4_step_a10_apply | census_atsi_share_ingest_v1 | abs_sa2_education_employment_annual | 0 | {"existing_rows_for_metric": 0} | {"rows_inserted": 7272, "sa2_count": 2445, "years": [2011, 2016, 2021], "national_2011_pct": 2.54... | A10 ATSI share ingest (v1). Stores percentage (0-100) matching census_*_pct convention. Formula: ... | 2026-05-09 13:41:00 |
| 152 | layer4_4_step_a10_apply | census_overseas_born_share_ingest_v1 | abs_sa2_education_employment_annual | 0 | {"existing_rows_for_metric": 0} | {"rows_inserted": 7272, "sa2_count": 2445, "years": [2011, 2016, 2021], "national_2011_pct": 24.5... | A10 overseas-born share ingest (v1). Stores percentage (0-100). Formula: (Tot - Aust - Country_bi... | 2026-05-09 13:41:00 |
| 153 | layer4_4_step_a10_apply | census_single_parent_family_share_ingest_v1 | abs_sa2_education_employment_annual | 0 | {"existing_rows_for_metric": 0} | {"rows_inserted": 7104, "sa2_count": 2387, "years": [2011, 2016, 2021], "national_2011_pct": 15.6... | A10 single-parent-family share ingest (v1). Stores percentage (0-100). Formula: Tot_FH_One_PFam /... | 2026-05-09 13:41:00 |
| 154 | layer4_4_step_a10_apply | country_of_birth_top_n_ingest_v1 | abs_sa2_country_of_birth_top_n | 0 | {"existing_rows": 0, "table_created_this_run": true} | {"rows_inserted": 7102, "sa2_count": 2386, "census_year": 2021, "top_n": 3, "backup": "data\\pre_... | A10 country-of-birth top-3 ingest (v1, 2021 only). Display-only context table accompanying census... | 2026-05-09 13:41:00 |
| 155 | layer3_apply | layer3_banding_v1 | layer3_sa2_metric_banding | 0 | {"rows": 0} | {"rows": 33571} | Layer 3 banding: percentile/decile/band per (metric x SA2 x latest-year x cohort). 33571 rows. 14... | 2026-05-09 13:43:02 |
| 156 | layer3_x_catchment_apply | layer3_catchment_banding_v1 | layer3_sa2_metric_banding | 0 | {"prior_rows_for_metrics": 0} | {"inserted_rows": 9035, "metrics": ["sa2_supply_ratio", "sa2_child_to_place", "sa2_adjusted_deman... | Layer 2.5 sub-pass 2.5.2: Layer 3.x catchment metric banding. Bands 4 catchment metrics from serv... | 2026-05-09 13:43:03 |
| 157 | layer4_4_step_a10b_languages_apply | language_at_home_top_n_create_v1 | schema | 0 | {"existed": false} | {"created_table": "abs_sa2_language_at_home_top_n"} | A10/C8 follow-up: create table for top-3 language-at-home display context. Parallel to abs_sa2_co... | 2026-05-09 14:08:27 |
| 158 | layer4_4_step_a10b_languages_apply | language_at_home_top_n_ingest_v1 | abs_sa2_language_at_home_top_n | 0 | {"existing_rows": 0, "table_created_this_run": true} | {"rows_inserted": 7060, "sa2_count": 2374, "census_year": 2021, "top_n": 3, "backup": "data\\pre_... | A10/C8 follow-up: top-3 languages spoken at home per SA2 (2021 only). Display-only context table ... | 2026-05-09 14:08:27 |
| 159 | layer4_4_step_a3_streamc_apply | erp_parent_cohort_25_44_share_ingest_v1 | abs_sa2_education_employment_annual | 0 | {"existing_rows_for_metric": 0} | {"rows_inserted": 14120, "sa2_count": 2363, "years": [2019, 2020, 2021, 2022, 2023, 2024], "natio... | A3 parent-cohort 25-44 share ingest (v1). Stores percentage (0-100). Formula: sum(persons 25_29..... | 2026-05-09 14:51:47 |
| 160 | layer4_4_step_a3_streamc_apply | census_partnered_25_44_share_ingest_v1 | abs_sa2_education_employment_annual | 0 | {"existing_rows_for_metric": 0} | {"rows_inserted": 7063, "sa2_count": 2379, "years": [2011, 2016, 2021], "national_pct_by_year": {... | Stream C partnered 25-44 share ingest (v1). Stores percentage (0-100). Formula: sum(Mar_RegM_P + ... | 2026-05-09 14:51:48 |
| 161 | layer4_4_step_a3_streamc_apply | census_women_35_44_with_child_share_ingest_v1 | abs_sa2_education_employment_annual | 0 | {"existing_rows_for_metric": 0} | {"rows_inserted": 7072, "sa2_count": 2380, "years": [2011, 2016, 2021], "national_pct_by_year": {... | Stream C women-35-44 with at least one child share ingest (v1). Stores percentage (0-100). Formul... | 2026-05-09 14:51:48 |
| 162 | layer4_4_step_a3_streamc_apply | census_women_25_34_with_child_share_ingest_v1 | abs_sa2_education_employment_annual | 0 | {"existing_rows_for_metric": 0} | {"rows_inserted": 7069, "sa2_count": 2375, "years": [2011, 2016, 2021], "national_pct_by_year": {... | Stream C women-25-34 with at least one child share ingest (v1). Stores percentage (0-100). Formul... | 2026-05-09 14:51:48 |
| 163 | layer3_apply | layer3_banding_v1 | layer3_sa2_metric_banding | 0 | {"rows": 0} | {"rows": 42992} | Layer 3 banding: percentile/decile/band per (metric x SA2 x latest-year x cohort). 42992 rows. 18... | 2026-05-09 14:52:51 |
| 164 | layer3_x_catchment_apply | layer3_catchment_banding_v1 | layer3_sa2_metric_banding | 0 | {"prior_rows_for_metrics": 0} | {"inserted_rows": 9035, "metrics": ["sa2_supply_ratio", "sa2_child_to_place", "sa2_adjusted_deman... | Layer 2.5 sub-pass 2.5.2: Layer 3.x catchment metric banding. Bands 4 catchment metrics from serv... | 2026-05-09 14:53:21 |
| 165 | layer4_4_step_a4_schools_apply | acara_school_count_total_ingest_v1 | abs_sa2_education_employment_annual | 0 | {"existing_rows_for_metric": 0} | {"rows_inserted": 39613, "sa2_count": 2233, "years": [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2... | School count per SA2 per year. Source: ACARA School Profile 2008-2025. Currently-operating school... | 2026-05-09 16:05:49 |
| 166 | layer4_4_step_a4_schools_apply | acara_school_enrolment_total_ingest_v1 | abs_sa2_education_employment_annual | 0 | {"existing_rows_for_metric": 0} | {"rows_inserted": 39613, "sa2_count": 2233, "years": [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2... | Total student enrolment per SA2 per year, summed across all schools in this catchment. Source: AC... | 2026-05-09 16:05:50 |
| 167 | layer4_4_step_a4_schools_apply | acara_school_govt_share_ingest_v1 | abs_sa2_education_employment_annual | 0 | {"existing_rows_for_metric": 0} | {"rows_inserted": 39613, "sa2_count": 2233, "years": [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2... | Government-sector share of school count per SA2 per year. Numerator: count of Government-sector s... | 2026-05-09 16:05:50 |
| 168 | layer4_4_step_a4_schools_apply | acara_school_catholic_share_ingest_v1 | abs_sa2_education_employment_annual | 0 | {"existing_rows_for_metric": 0} | {"rows_inserted": 39613, "sa2_count": 2233, "years": [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2... | Catholic-sector share of school count per SA2 per year. | 2026-05-09 16:05:50 |
| 169 | layer4_4_step_a4_schools_apply | acara_school_independent_share_ingest_v1 | abs_sa2_education_employment_annual | 0 | {"existing_rows_for_metric": 0} | {"rows_inserted": 39613, "sa2_count": 2233, "years": [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2... | Independent-sector share of school count per SA2 per year. | 2026-05-09 16:05:51 |
| 170 | layer4_4_step_a4_schools_apply | acara_school_enrolment_govt_share_ingest_v1 | abs_sa2_education_employment_annual | 0 | {"existing_rows_for_metric": 0} | {"rows_inserted": 39598, "sa2_count": 2231, "years": [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2... | Government-sector share of student enrolment per SA2 per year. Captures the public/private mix in... | 2026-05-09 16:05:51 |
| 171 | layer4_4_step_a4_schools_apply | acara_school_enrolment_catholic_share_ingest_v1 | abs_sa2_education_employment_annual | 0 | {"existing_rows_for_metric": 0} | {"rows_inserted": 39598, "sa2_count": 2231, "years": [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2... | Catholic-sector share of student enrolment per SA2 per year. | 2026-05-09 16:05:51 |
| 172 | layer4_4_step_a4_schools_apply | acara_school_enrolment_independent_share_ingest_v1 | abs_sa2_education_employment_annual | 0 | {"existing_rows_for_metric": 0} | {"rows_inserted": 39598, "sa2_count": 2231, "years": [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2... | Independent-sector share of student enrolment per SA2 per year. | 2026-05-09 16:05:52 |
| 173 | layer3_apply | layer3_banding_v1 | layer3_sa2_metric_banding | 0 | {"rows": 0} | {"rows": 60847} | Layer 3 banding: percentile/decile/band per (metric x SA2 x latest-year x cohort). 60847 rows. 26... | 2026-05-09 16:06:52 |
| 174 | layer3_x_catchment_apply | layer3_catchment_banding_v1 | layer3_sa2_metric_banding | 0 | {"prior_rows_for_metrics": 0} | {"inserted_rows": 9035, "metrics": ["sa2_supply_ratio", "sa2_child_to_place", "sa2_adjusted_deman... | Layer 2.5 sub-pass 2.5.2: Layer 3.x catchment metric banding. Bands 4 catchment metrics from serv... | 2026-05-09 16:06:53 |

---

End of inventory. Read-only; no DB writes performed.
