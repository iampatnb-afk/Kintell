# Layer 2 Step 5b-prime — Spotcheck
Generated: 2026-04-27T20:45:03

## 1. Schema + indexes

```sql
CREATE TABLE abs_sa2_education_employment_annual (
                sa2_code    TEXT    NOT NULL,
                year        INTEGER NOT NULL,
                metric_name TEXT    NOT NULL,
                value       REAL,
                PRIMARY KEY (sa2_code, year, metric_name)
            )
```

Indexes (2):
  - idx_abs_sa2_ee_metric
  - idx_abs_sa2_ee_year

Rows: 203,527 | metrics: 22 | distinct SA2s: 2,448

## 2. Sample SA2 trajectories

### SA2 `101021007` — (fallback sample)

**Census trajectory** (2011 → 2016 → 2021):

| Metric | 2011 | 2016 | 2021 |
|:-------|-----:|-----:|-----:|
| ee_year12_completion_pct | 44.40 | 44.70 | 51.40 |
| ee_bachelor_degree_pct | 12.40 | 12.90 | 14.80 |
| ee_lfp_persons_pct | 59.30 | 53.10 | 57.30 |
| ee_unemployment_rate_persons_pct | 4.10 | 4.10 | 3.30 |
| census_lfp_females_pct | 60.06 | 55.71 | 58.59 |
| census_lfp_males_pct | 66.67 | 64.82 | 65.92 |
| ee_managers_pct | 23.20 | 22.40 | 22.10 |
| ee_professionals_pct | 17.70 | 19.00 | 18.30 |
| ee_clerical_admin_pct | 11.50 | 11.50 | 10.90 |

**Annual trajectory** (preschool 4yo + total jobs):

| Year | preschool 4yo | total jobs | female jobs | info_media | finance | prof_sci |
|-----:|-------------:|----------:|-----------:|----------:|-------:|---------:|
| 2018 | 41 | 3,170 | 1,538 | 19 | 69 | 186 |
| 2019 | 52 | 3,326 | 1,627 | 22 | 84 | 191 |
| 2020 | 44 | 3,454 | 1,709 | 29 | 85 | 219 |
| 2021 | 54 | 3,571 | 1,779 | 17 | 82 | 222 |
| 2022 | 40 | 3,753 | 1,896 | 19 | 95 | 219 |

### SA2 `101021008` — (fallback sample)

**Census trajectory** (2011 → 2016 → 2021):

| Metric | 2011 | 2016 | 2021 |
|:-------|-----:|-----:|-----:|
| ee_year12_completion_pct | 45.50 | 48.60 | 53.70 |
| ee_bachelor_degree_pct | 8.30 | 8.70 | 10.60 |
| ee_lfp_persons_pct | 69.40 | 66.30 | 65.40 |
| ee_unemployment_rate_persons_pct | 3.40 | 4.60 | 4.40 |
| census_lfp_females_pct | 68.75 | 66.83 | 66.05 |
| census_lfp_males_pct | 77.90 | 74.24 | 73.47 |
| ee_managers_pct | 10.10 | 10.80 | 11.80 |
| ee_professionals_pct | 14.50 | 14.60 | 16.50 |
| ee_clerical_admin_pct | 21.20 | 20.00 | 17.40 |

**Annual trajectory** (preschool 4yo + total jobs):

| Year | preschool 4yo | total jobs | female jobs | info_media | finance | prof_sci |
|-----:|-------------:|----------:|-----------:|----------:|-------:|---------:|
| 2018 | 90 | 7,079 | 3,410 | 70 | 150 | 399 |
| 2019 | 82 | 7,173 | 3,438 | 60 | 150 | 397 |
| 2020 | 82 | 7,074 | 3,409 | 57 | 150 | 403 |
| 2021 | 79 | 7,145 | 3,407 | 52 | 180 | 435 |
| 2022 | 86 | 7,580 | 3,632 | 58 | 183 | 518 |

### SA2 `101021009` — (fallback sample)

**Census trajectory** (2011 → 2016 → 2021):

| Metric | 2011 | 2016 | 2021 |
|:-------|-----:|-----:|-----:|
| ee_year12_completion_pct | 48.10 | 53.40 | 61.10 |
| ee_bachelor_degree_pct | 12.10 | 14.00 | 15.80 |
| ee_lfp_persons_pct | 64.90 | 64.50 | 67.90 |
| ee_unemployment_rate_persons_pct | 3.50 | 5.20 | 4.10 |
| census_lfp_females_pct | 64.58 | 65.19 | 68.06 |
| census_lfp_males_pct | 76.27 | 74.51 | 75.64 |
| ee_managers_pct | 10.40 | 11.10 | 12.60 |
| ee_professionals_pct | 19.50 | 18.60 | 19.80 |
| ee_clerical_admin_pct | 19.50 | 17.70 | 16.70 |

**Annual trajectory** (preschool 4yo + total jobs):

| Year | preschool 4yo | total jobs | female jobs | info_media | finance | prof_sci |
|-----:|-------------:|----------:|-----------:|----------:|-------:|---------:|
| 2018 | 118 | 9,588 | 4,487 | 138 | 199 | 572 |
| 2019 | 110 | 9,756 | 4,613 | 145 | 202 | 623 |
| 2020 | 113 | 9,823 | 4,630 | 127 | 186 | 596 |
| 2021 | 98 | 10,587 | 4,894 | 120 | 184 | 654 |
| 2022 | 103 | 11,982 | 5,379 | 123 | 220 | 730 |

### SA2 `101021010` — (fallback sample)

**Census trajectory** (2011 → 2016 → 2021):

| Metric | 2011 | 2016 | 2021 |
|:-------|-----:|-----:|-----:|
| ee_year12_completion_pct | 55.90 | 60.40 | 65.30 |
| ee_bachelor_degree_pct | 14.60 | 16.00 | 17.30 |
| ee_lfp_persons_pct | 71.60 | 70.00 | 70.60 |
| ee_unemployment_rate_persons_pct | 3.10 | 5.10 | 3.60 |
| census_lfp_females_pct | 71.37 | 71.23 | 70.99 |
| census_lfp_males_pct | 81.34 | 77.89 | 77.56 |
| ee_managers_pct | 12.20 | 12.10 | 14.10 |
| ee_professionals_pct | 19.70 | 19.60 | 21.30 |
| ee_clerical_admin_pct | 18.80 | 17.50 | 16.10 |

**Annual trajectory** (preschool 4yo + total jobs):

| Year | preschool 4yo | total jobs | female jobs | info_media | finance | prof_sci |
|-----:|-------------:|----------:|-----------:|----------:|-------:|---------:|
| 2018 | 46 | 4,742 | 2,265 | 63 | 75 | 298 |
| 2019 | 52 | 4,722 | 2,260 | 55 | 64 | 311 |
| 2020 | 54 | 4,675 | 2,184 | 57 | 61 | 338 |
| 2021 | 54 | 4,887 | 2,262 | 58 | 93 | 325 |
| 2022 | 50 | 5,464 | 2,394 | 59 | 108 | 390 |

## 3. Female LFP distribution by state (2021)

State derived from SA2 code first digit (1=NSW, 2=VIC, 3=QLD, 4=SA, 5=WA, 6=TAS, 7=NT, 8=ACT, 9=Other Territories).

| State | n SA2s | min | p25 | median | p75 | max | mean |
|------:|------:|----:|----:|------:|----:|----:|-----:|
| NSW | 632 | 0.0 | 53.9 | 59.5 | 64.9 | 100.0 | 58.7 |
| VIC | 518 | 35.1 | 56.3 | 62.3 | 67.1 | 100.0 | 62.0 |
| QLD | 538 | 0.0 | 57.3 | 63.4 | 69.0 | 100.0 | 62.5 |
| SA | 168 | 35.5 | 55.7 | 60.0 | 63.9 | 100.0 | 59.5 |
| WA | 253 | 0.0 | 58.8 | 63.3 | 68.1 | 100.0 | 63.5 |
| TAS | 98 | 44.3 | 53.2 | 58.7 | 63.0 | 100.0 | 58.4 |
| NT | 66 | 27.3 | 59.9 | 69.9 | 77.7 | 100.0 | 65.6 |
| ACT | 120 | 10.7 | 63.8 | 68.2 | 76.5 | 100.0 | 70.3 |
| OT | 5 | 54.9 | 58.5 | 71.2 | 76.4 | 100.0 | 72.2 |

## 4. RWCI inputs — top 10 SA2s by occupation knowledge share (2021)

Occupation knowledge share = managers + professionals + clerical (%).
Inner-city / professional-services SA2s should dominate.

| SA2 | Mgr % | Prof % | Clerical % | Knowledge share % |
|:----|-----:|------:|----------:|----------------:|
| 114011275 | 37.5 | 33.3 | 16.7 | 87.5 |
| 801051125 | 73.1 | 11.3 | 2.2 | 86.6 |
| 801061129 | 24.7 | 46.5 | 12.0 | 83.2 |
| 801061063 | 26.5 | 42.5 | 12.4 | 81.4 |
| 801061131 | 25.1 | 45.0 | 11.3 | 81.4 |
| 118011347 | 23.6 | 48.8 | 8.7 | 81.1 |
| 121041417 | 23.2 | 46.4 | 11.5 | 81.1 |
| 120021387 | 26.4 | 44.0 | 10.1 | 80.5 |
| 121041414 | 21.5 | 46.8 | 12.1 | 80.4 |
| 206041119 | 20.0 | 49.2 | 11.1 | 80.3 |

## 5. RWCI inputs — top 10 SA2s by industry knowledge share (latest year)

Industry knowledge share = (info_media + finance + prof_sci + admin_support) / total_jobs.

Latest year: 2022

| SA2 | info | finance | prof_sci | admin | total | knowledge % |
|:----|-----:|-------:|--------:|------:|------:|-----------:|
| 125041717 | 296 | 1,083 | 3,054 | 2,447 | 15,621 | 44.0 |
| 121041417 | 605 | 1,395 | 2,366 | 1,007 | 12,794 | 42.0 |
| 121011401 | 584 | 1,408 | 2,102 | 906 | 12,140 | 41.2 |
| 206041118 | 400 | 1,398 | 3,635 | 2,146 | 18,534 | 40.9 |
| 117031644 | 375 | 1,567 | 1,854 | 1,610 | 13,390 | 40.4 |
| 118011650 | 485 | 982 | 1,448 | 722 | 9,046 | 40.2 |
| 117031333 | 1,025 | 1,712 | 3,248 | 2,258 | 21,059 | 39.1 |
| 117031336 | 1,167 | 1,459 | 2,879 | 2,020 | 19,243 | 39.1 |
| 118011345 | 798 | 1,497 | 2,564 | 1,055 | 15,182 | 39.0 |
| 121041416 | 775 | 1,747 | 2,780 | 1,257 | 16,858 | 38.9 |

## 6. Cross-source validation — EE DB col 55 vs T33-derived persons LFP

Both should report the same Census persons LFP rate per (SA2, year). Material divergence indicates a source mismatch.

Compared 7,178 (SA2, year) pairs in [0, 100] range.

- mean abs difference: 4.362 pp
- median abs diff:     3.570 pp
- p95 abs diff:        9.040 pp
- max abs diff:        70.000 pp
