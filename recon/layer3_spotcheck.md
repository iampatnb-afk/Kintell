# Layer 3 spotcheck

_Generated: 2026-04-28T12:27:36_

Read-only post-apply validation of `sa2_cohort` and `layer3_sa2_metric_banding` against 10 invariants.

## Invariants — 10 of 10 pass

| # | Invariant | Result | Detail |
|---:|---|:-:|---|
| 1 | Total row count > 10,000 | PASS | layer3_sa2_metric_banding rows = 23,946 |
| 2 | PK (sa2_code, metric, year, cohort_def) is unique | PASS | duplicate PK tuples: 0 |
| 3 | percentile in [0,100], decile in [1,10], band in {low,mid,high} | PASS | percentile out of range: 0; decile out of range: 0; band invalid: 0 |
| 4 | Core fields all populated (percentile/decile/band/cohort/raw) | PASS | NULLs - percentile: 0; decile: 0; band: 0; cohort_key: 0; cohort_n: 0; raw_value: 0 |
| 5 | band consistent with decile (1-3 low / 4-6 mid / 7-10 high) | PASS | inconsistent rows: 0 |
| 6 | cohort_n matches actual cohort size in layer3 table | PASS | mismatched (metric x cohort_key) groups: 0 |
| 7 | Every layer3 sa2_code present in sa2_cohort | PASS | orphan sa2_codes: 0 |
| 8 | Decile distribution balanced within cohort (cohort_n>=20) | PASS | imbalanced (metric x cohort_key x decile) groups: 0 |
| 9 | Band distribution per metric is ~30/30/40 (+/-3pp) | PASS | metrics outside tolerance: 0 |
| 10 | audit_log row 136 well-formed | PASS | actor=layer3_apply, action=layer3_banding_v1, subj=layer3_sa2_metric_banding, after={"rows": 23946} |

## Per-metric headlines

| metric | year | rows | cohorts | min cohort | max cohort |
|---|---:|---:|---:|---:|---:|
| `sa2_births_count` | 2024 | 2,450 | 33 | 2 | 417 |
| `sa2_lfp_females` | 2021 | 2,386 | 35 | 1 | 411 |
| `sa2_lfp_males` | 2021 | 2,397 | 35 | 1 | 414 |
| `sa2_lfp_persons` | 2021 | 2,401 | 35 | 1 | 416 |
| `sa2_median_employee_income` | 2022 | 2,398 | 5 | 60 | 1447 |
| `sa2_median_household_income` | 2021 | 2,411 | 5 | 63 | 1447 |
| `sa2_median_total_income` | 2022 | 2,402 | 5 | 60 | 1450 |
| `sa2_total_population` | 2024 | 2,418 | 35 | 1 | 416 |
| `sa2_under5_count` | 2024 | 2,347 | 9 | 4 | 625 |
| `sa2_unemployment_rate` | 2025 | 2,336 | 8 | 62 | 623 |

## Sample SA2 profiles

### `101021007` — Braidwood

| metric | year | period | cohort | key | n | raw | pctile | dec | band |
|---|---:|---|---|---|---:|---:|---:|---:|---|
| `sa2_births_count` | 2024 |  | state_x_remoteness | `1_2` | 155 | 35.00 | 13.2 | 2 | low |
| `sa2_lfp_females` | 2021 |  | state_x_remoteness | `1_2` | 151 | 58.59 | 54.6 | 6 | mid |
| `sa2_lfp_males` | 2021 |  | state_x_remoteness | `1_2` | 153 | 65.92 | 59.8 | 6 | mid |
| `sa2_lfp_persons` | 2021 |  | state_x_remoteness | `1_2` | 153 | 57.30 | 52.6 | 6 | mid |
| `sa2_median_employee_income` | 2022 |  | remoteness | `2` | 505 | 55,072.00 | 56.3 | 6 | mid |
| `sa2_median_household_income` | 2021 |  | remoteness | `2` | 511 | 952.00 | 54.5 | 6 | mid |
| `sa2_median_total_income` | 2022 |  | remoteness | `2` | 505 | 48,324.00 | 36.1 | 4 | mid |
| `sa2_total_population` | 2024 |  | state_x_remoteness | `1_2` | 155 | 4,484.00 | 10.0 | 1 | low |
| `sa2_under5_count` | 2024 |  | state | `1` | 625 | 208.00 | 7.1 | 1 | low |
| `sa2_unemployment_rate` | 2025 | 2025-Q4 | state | `1` | 623 | 2.50 | 25.4 | 3 | low |

### `901041004` — Norfolk Island

| metric | year | period | cohort | key | n | raw | pctile | dec | band |
|---|---:|---|---|---|---:|---:|---:|---:|---|
| `sa2_lfp_females` | 2021 |  | state_x_remoteness | `9_5` | 3 | 71.25 | 50.0 | 4 | mid |
| `sa2_lfp_males` | 2021 |  | state_x_remoteness | `9_5` | 3 | 72.28 | 83.3 | 7 | high |
| `sa2_lfp_persons` | 2021 |  | state_x_remoteness | `9_5` | 3 | 63.70 | 83.3 | 7 | high |
| `sa2_median_household_income` | 2021 |  | remoteness | `5` | 63 | 850.00 | 54.8 | 6 | mid |
| `sa2_total_population` | 2024 |  | state_x_remoteness | `9_5` | 3 | 2,200.00 | 83.3 | 7 | high |
| `sa2_under5_count` | 2024 |  | state | `9` | 4 | 63.00 | 62.5 | 6 | mid |

### `305031120` — Alderley

| metric | year | period | cohort | key | n | raw | pctile | dec | band |
|---|---:|---|---|---|---:|---:|---:|---:|---|
| `sa2_births_count` | 2024 |  | state_x_remoteness | `3_1` | 302 | 52.00 | 15.4 | 2 | low |
| `sa2_lfp_females` | 2021 |  | state_x_remoteness | `3_1` | 297 | 77.49 | 96.5 | 10 | high |
| `sa2_lfp_males` | 2021 |  | state_x_remoteness | `3_1` | 299 | 80.92 | 91.5 | 10 | high |
| `sa2_lfp_persons` | 2021 |  | state_x_remoteness | `3_1` | 299 | 76.80 | 96.8 | 10 | high |
| `sa2_median_employee_income` | 2022 |  | remoteness | `1` | 1447 | 73,465.00 | 86.8 | 9 | high |
| `sa2_median_household_income` | 2021 |  | remoteness | `1` | 1447 | 1,570.00 | 86.4 | 9 | high |
| `sa2_median_total_income` | 2022 |  | remoteness | `1` | 1450 | 73,735.00 | 90.2 | 10 | high |
| `sa2_total_population` | 2024 |  | state_x_remoteness | `3_1` | 300 | 7,218.00 | 20.2 | 3 | low |
| `sa2_under5_count` | 2024 |  | state | `3` | 531 | 373.00 | 32.7 | 4 | mid |
| `sa2_unemployment_rate` | 2025 | 2025-Q4 | state | `3` | 529 | 4.40 | 63.2 | 7 | high |

### `208021180` — Hughesdale

| metric | year | period | cohort | key | n | raw | pctile | dec | band |
|---|---:|---|---|---|---:|---:|---:|---:|---|
| `sa2_births_count` | 2024 |  | state_x_remoteness | `2_1` | 349 | 91.00 | 18.8 | 2 | low |
| `sa2_lfp_females` | 2021 |  | state_x_remoteness | `2_1` | 346 | 67.57 | 71.0 | 8 | high |
| `sa2_lfp_males` | 2021 |  | state_x_remoteness | `2_1` | 347 | 74.49 | 63.5 | 7 | high |
| `sa2_lfp_persons` | 2021 |  | state_x_remoteness | `2_1` | 347 | 68.60 | 71.0 | 8 | high |
| `sa2_median_employee_income` | 2022 |  | remoteness | `1` | 1447 | 65,045.00 | 64.9 | 7 | high |
| `sa2_median_household_income` | 2021 |  | remoteness | `1` | 1447 | 1,292.00 | 65.8 | 7 | high |
| `sa2_median_total_income` | 2022 |  | remoteness | `1` | 1450 | 61,845.00 | 63.8 | 7 | high |
| `sa2_total_population` | 2024 |  | state_x_remoteness | `2_1` | 347 | 8,088.00 | 10.2 | 2 | low |
| `sa2_under5_count` | 2024 |  | state | `2` | 512 | 390.00 | 23.1 | 3 | low |
| `sa2_unemployment_rate` | 2025 | 2025-Q4 | state | `2` | 510 | 5.20 | 69.5 | 7 | high |

### `117011320` — Banksmeadow

| metric | year | period | cohort | key | n | raw | pctile | dec | band |
|---|---:|---|---|---|---:|---:|---:|---:|---|
| `sa2_births_count` | 2024 |  | state_x_remoteness | `1_1` | 417 | 17.00 | 3.0 | 1 | low |
| `sa2_lfp_females` | 2021 |  | state_x_remoteness | `1_1` | 411 | 75.48 | 97.4 | 10 | high |
| `sa2_lfp_males` | 2021 |  | state_x_remoteness | `1_1` | 414 | 83.33 | 97.9 | 10 | high |
| `sa2_lfp_persons` | 2021 |  | state_x_remoteness | `1_1` | 416 | 64.00 | 65.0 | 7 | high |
| `sa2_median_employee_income` | 2022 |  | remoteness | `1` | 1447 | 84,866.00 | 97.5 | 10 | high |
| `sa2_median_household_income` | 2021 |  | remoteness | `1` | 1447 | 1,661.00 | 90.8 | 10 | high |
| `sa2_median_total_income` | 2022 |  | remoteness | `1` | 1450 | 81,419.00 | 96.9 | 10 | high |
| `sa2_total_population` | 2024 |  | state_x_remoteness | `1_1` | 416 | 645.00 | 2.3 | 1 | low |
| `sa2_under5_count` | 2024 |  | state | `1` | 625 | 31.00 | 0.6 | 1 | low |
| `sa2_unemployment_rate` | 2025 | 2025-Q4 | state | `1` | 623 | 2.50 | 26.6 | 3 | low |
