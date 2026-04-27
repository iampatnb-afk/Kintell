# Layer 2 Step 5b-prime — Preflight
Generated: 2026-04-27T20:23:14

## File checks
  ✓ DB: `data\kintell.db` (519,094,272 bytes)
  ✓ EE Database: `abs_data\Education and employment database.xlsx` (14,325,582 bytes)
  ✓ T33 derived CSV: `recon\layer2_step5b_prime_t33_derived.csv` (1,332,815 bytes)

## DB tables (32 total)

  - abs_sa2_erp_annual (88,344 rows)
  - abs_sa2_socioeconomic_annual (161,964 rows)
  - abs_sa2_unemployment_quarterly (142,496 rows)
  - audit_log (131 rows)
  - brands (349 rows)
  - entities (7,143 rows)
  - entity_financials (0 rows)
  - entity_snapshots (0 rows)
  - evidence (10,263 rows)
  - group_snapshots (0 rows)
  - groups (6,507 rows)
  - intelligence_notes (0 rows)
  - jsa_ivi_remoteness_monthly (348 rows)
  - jsa_ivi_state_monthly (4,338 rows)
  - jsa_sa4_remoteness_concordance (88 rows)
  - link_candidates (823 rows)
  - metric_definitions (6 rows)
  - model_assumptions (13 rows)
  - nqs_history (807,526 rows)
  - people (0 rows)
  - person_roles (0 rows)
  - portfolios (4,187 rows)
  - properties (0 rows)
  - regulatory_events (0 rows)
  - service_catchment_cache (0 rows)
  - service_financials (0 rows)
  - service_history (0 rows)
  - service_tenures (0 rows)
  - services (18,223 rows)
  - sqlite_sequence (11 rows)
  - training_completions (768 rows)
  - training_completions_ingest_run (1 rows)

✓ Target table `abs_sa2_education_employment_annual` does not yet exist (expected).

## audit_log schema

```sql
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
)
```

Columns:

| cid | name | type | notnull | dflt | pk |
|----:|:-----|:-----|--------:|:-----|---:|
| 0 | audit_id | INTEGER | 0 | None | 1 |
| 1 | actor | TEXT | 1 | None | 0 |
| 2 | action | TEXT | 1 | None | 0 |
| 3 | subject_type | TEXT | 1 | None | 0 |
| 4 | subject_id | INTEGER | 1 | None | 0 |
| 5 | before_json | TEXT | 0 | None | 0 |
| 6 | after_json | TEXT | 0 | None | 0 |
| 7 | reason | TEXT | 0 | None | 0 |
| 8 | occurred_at | TEXT | 0 | datetime('now') | 0 |

## Last 5 audit_log entries

```
  audit_id: 131
  actor: layer2_step5b_apply
  action: abs_sa2_socioeconomic_ingest_v1
  subject_type: abs_sa2_socioeconomic_annual
  subject_id: 0
  before_json: {"rows": 0}
  after_json: {"rows": 161964, "payload": {"rows_inserted": 161964, "distinct_sa2": 2454, "metrics_count": 6, "metric_names": ["median_equiv_household_income_weekly", "median_employee_income_annual", "median_own_bu...
  reason: Layer 2 Step 5b: SA2 socioeconomic time series (6 income metrics, mixed annual + Census cadence)
  occurred_at: 2026-04-27T18:08:10.029397
```

```
  audit_id: 130
  actor: layer2_step5c_apply
  action: jsa_ivi_ingest_v1
  subject_type: jsa_ivi_state_monthly
  subject_id: 0
  before_json: {"state": 0, "remoteness": 0, "concordance": 0}
  after_json: {"state": 4338, "remoteness": 348, "concordance": 88, "payload": {"state_rows_inserted": 4338, "remoteness_rows_inserted": 348, "concordance_rows_inserted": 88, "target_anzsco_codes": ["2411", "4211"]...
  reason: Layer 2 Step 5c: JSA IVI ingest (ANZSCO 4211 + 2411, state + remoteness)
  occurred_at: 2026-04-27T17:23:43.789708
```

```
  audit_id: 129
  actor: layer2_step5_apply
  action: salm_sa2_ingest_v1
  subject_type: abs_sa2_unemployment_quarterly
  subject_id: 0
  before_json: {"rows": 0}
  after_json: {"rows": 142496, "payload": {"rows_inserted": 142496, "distinct_sa2": 2336, "distinct_quarters": 61, "first_quarter": "2010-Q4", "last_quarter": "2025-Q4", "non_null_rate": 121424, "non_null_count": 1...
  reason: Layer 2 Step 5: SALM SA2 unemployment ingest
  occurred_at: 2026-04-27T17:14:43.720449
```

```
  audit_id: 128
  actor: layer2_step6_apply_v2
  action: sa2_erp_ingest_v1
  subject_type: abs_sa2_erp_annual
  subject_id: 0
  before_json: {"rows": 0}
  after_json: {"rows": 88344, "payload": {"rows_inserted": 88344, "distinct_sa2": 2454, "distinct_years": 9, "years_list": [2011, 2016, 2018, 2019, 2020, 2021, 2022, 2023, 2024], "age_groups": ["total_persons", "un...
  reason: Layer 2 Step 6: ABS ERP at SA2 ingest (long format)
  occurred_at: 2026-04-27T16:34:03.576805
```

```
  audit_id: 127
  actor: layer2_step4_nqaits_ingest_v1
  action: nqaits_ingest_v1
  subject_type: nqs_history
  subject_id: 0
  before_json: {"nqs_history_exists": false, "expected_volume_estimate": 807526}
  after_json: {"nqs_history_rowcount": 807526, "unique_service_ids": 23439, "sheets_ingested": 50, "pa_chain_changers": 6155}
  reason: Phase 2.5 Layer 2 Step 4 — NQAITS quarterly historical ingest. Created nqs_history table + 3 indexes, ingested 807,526 rows across 50 quarterly sheets (Q32013data -> Q42025data). 23,439 unique service...
  occurred_at: 2026-04-26 05:55:58
```

## SA2 reference counts (sanity)

  - ERP table (Step 6): 2,454 distinct SA2 codes in `abs_sa2_erp_annual`
  - Socioeconomic (Step 5b): 2,454 distinct SA2 codes in `abs_sa2_socioeconomic_annual`