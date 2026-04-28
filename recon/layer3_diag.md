# Layer 3 Diagnostic

_Generated: 2026-04-28T11:00:12_

Read-only design probe ahead of `layer3_apply.py`. References:
- `recon/layer3_decisions.md` (D1-D4 closed)
- `recon/layer3_precedent_survey.md` (raw evidence)
- `recon/db_inventory.md` (Standard 28 snapshot)

**Goal of this artefact:** answer the open design questions so the apply
script can be written cleanly, with no ambiguity about data sources,
metric definitions, cohort logic, or banding cutoffs.

---

## 1. SA2 cohort lookup source

Layer 3 banding requires a per-SA2 cohort assignment: `(state, remoteness)`. State is trivially derivable from the first digit of `sa2_code` (ABS convention). Remoteness is the open question.

### 1.1 State-from-SA2-prefix validation

First digit of `services.sa2_code` (ABS convention: 1=NSW 2=VIC 3=QLD 4=SA 5=WA 6=TAS 7=NT 8=ACT 9=OT):

| Prefix | Implied state | Service rows |
|:-:|---|---:|
| 1 | NSW | 6,112 |
| 2 | VIC | 4,913 |
| 3 | QLD | 3,558 |
| 4 | SA | 1,156 |
| 5 | WA | 1,463 |
| 6 | TAS | 248 |
| 7 | NT | 248 |
| 8 | ACT | 476 |
| 9 | OT | 29 |

### 1.2 Distinct SA2 counts across candidate cohort sources

| Source | Distinct SA2s |
|---|---:|
| `services` (centres with assigned SA2) | 1,422 |
| `abs_sa2_erp_annual` | 2,454 |
| `abs_sa2_births_annual` | 2,450 |

_SA2s present in `abs_sa2_erp_annual` but with NO matching services row: **1,032**_  
These SA2s would NOT receive remoteness assignment if we use a services-derived approach — important constraint to consider.

### 1.3 Services-derived remoteness distribution

If we derive SA2 remoteness as the most-common `services.aria_plus` within each SA2:

| ARIA+ category | SA2 count |
|---|---:|
| Major Cities of Australia | 795 |
| Inner Regional Australia | 335 |
| Outer Regional Australia | 207 |
| Very Remote Australia | 42 |
| Remote Australia | 41 |

### 1.4 ABS GeoPackage probe

GeoPackage: `abs_data/ASGS_2021_Main_Structure_GDA2020.gpkg` (exists=True)

**GeoPackage probe error:** fiona not installed (pip install fiona)

### 1.5 RECOMMENDATION (for Patrick to confirm)

**State:** derive from `SUBSTR(sa2_code, 1, 1)` per the ABS convention. No table needed.

**Remoteness:** see Section 1.4 above. If the GeoPackage contains remoteness fields, use those (cleanest). If NOT, two paths:

  - **Path A (preferred if data available):** download the ABS Remoteness Areas GeoPackage (separate file, ~free from ABS) and build a one-off `sa2_cohort` lookup table via SA1 -> RA join. Cleanest but adds a small data-sourcing step.

  - **Path B (pragmatic fallback):** derive SA2 remoteness as the most-common `services.aria_plus` within each SA2 (Section 1.3 shows this works for SA2s with services). For SA2s with NO services (Section 1.2 count above), backfill by nearest-SA2 in the same state, OR mark as `null` cohort and exclude from banding.

Either way, write a `sa2_cohort` table with columns: `(sa2_code, state_code, state_name, remoteness, remoteness_band INTEGER 1..5)` and store as a Layer-3-prep step.

---

## 2. Source-metric inventory

### 2.1 `abs_sa2_erp_annual` — age groups present

| age_group | Rows | Distinct SA2 | Year range | NULL persons |
|---|---:|---:|---|---:|
| `total_persons` | 22,086 | 2,454 | 2011-2024 | 7,574 |
| `under_5_females` | 22,086 | 2,454 | 2011-2024 | 7,997 |
| `under_5_males` | 22,086 | 2,454 | 2011-2024 | 8,020 |
| `under_5_persons` | 22,086 | 2,454 | 2011-2024 | 7,966 |

### 2.2 `abs_sa2_socioeconomic_annual` — distinct metrics

| metric_name | Rows | Distinct SA2 | Years | NULLs | Avg value |
|---|---:|---:|---|---:|---:|
| `median_employee_income_annual` | 26,994 | 2,454 | 2011-2025 | 14,998 | 54,576.65 |
| `median_equiv_household_income_weekly` | 26,994 | 2,454 | 2011-2025 | 19,789 | 944.33 |
| `median_investment_income_annual` | 26,994 | 2,454 | 2011-2025 | 15,605 | 179.02 |
| `median_own_business_income_annual` | 26,994 | 2,454 | 2011-2025 | 15,198 | 11,737.30 |
| `median_superannuation_income_annual` | 26,994 | 2,454 | 2011-2025 | 15,360 | 21,586.61 |
| `median_total_income_excl_pensions_annual` | 26,994 | 2,454 | 2011-2025 | 14,976 | 51,659.35 |

### 2.3 `abs_sa2_education_employment_annual` — distinct metrics

| metric_name | Rows | Distinct SA2 | Years | NULLs | Avg value |
|---|---:|---:|---|---:|---:|
| `census_emp_to_pop_females_pct` | 7,175 | 2,412 | 2011-2021 | 0 | 57.17 |
| `census_emp_to_pop_males_pct` | 7,225 | 2,430 | 2011-2021 | 0 | 65.61 |
| `census_lfp_females_pct` | 7,175 | 2,412 | 2011-2021 | 0 | 60.53 |
| `census_lfp_males_pct` | 7,225 | 2,430 | 2011-2021 | 0 | 69.75 |
| `census_unemp_females_pct` | 7,149 | 2,406 | 2011-2021 | 0 | 5.75 |
| `census_unemp_males_pct` | 7,202 | 2,424 | 2011-2021 | 0 | 6.06 |
| `ee_bachelor_degree_pct` | 7,066 | 2,378 | 2011-2021 | 0 | 14.66 |
| `ee_clerical_admin_pct` | 7,032 | 2,361 | 2011-2021 | 0 | 13.37 |
| `ee_jobs_admin_support_count` | 11,821 | 2,382 | 2018-2022 | 0 | 742.08 |
| `ee_jobs_females_count` | 11,985 | 2,415 | 2018-2022 | 0 | 4,189.13 |
| `ee_jobs_finance_count` | 11,688 | 2,353 | 2018-2022 | 0 | 334.46 |
| `ee_jobs_info_media_count` | 11,400 | 2,325 | 2018-2022 | 0 | 116.65 |
| `ee_jobs_professional_scientific_count` | 11,794 | 2,374 | 2018-2022 | 0 | 585.71 |
| `ee_jobs_total_count` | 12,067 | 2,424 | 2018-2022 | 0 | 8,543.15 |
| `ee_lfp_persons_pct` | 7,183 | 2,412 | 2011-2021 | 0 | 60.97 |
| `ee_managers_pct` | 7,066 | 2,379 | 2011-2021 | 0 | 14.07 |
| `ee_preschool_15h_plus_count` | 12,255 | 2,340 | 2018-2023 | 0 | 112.70 |
| `ee_preschool_4yo_count` | 13,896 | 2,341 | 2018-2023 | 0 | 115.52 |
| `ee_preschool_total_count` | 13,903 | 2,344 | 2018-2023 | 0 | 144.83 |
| `ee_professionals_pct` | 7,056 | 2,374 | 2011-2021 | 0 | 21.15 |
| `ee_unemployment_rate_persons_pct` | 7,003 | 2,351 | 2011-2021 | 0 | 6.01 |
| `ee_year12_completion_pct` | 7,161 | 2,411 | 2011-2021 | 0 | 52.16 |

### 2.4 `abs_sa2_births_annual` — yearly profile

| year | Rows | Distinct SA2 | NULLs | National total |
|---:|---:|---:|---:|---:|
| 2011 | 2,450 | 2,450 | 0 | 300,889 |
| 2012 | 2,450 | 2,450 | 0 | 308,709 |
| 2013 | 2,450 | 2,450 | 0 | 306,917 |
| 2014 | 2,450 | 2,450 | 0 | 298,163 |
| 2015 | 2,450 | 2,450 | 0 | 303,021 |
| 2016 | 2,450 | 2,450 | 0 | 309,022 |
| 2017 | 2,450 | 2,450 | 0 | 307,131 |
| 2018 | 2,450 | 2,450 | 0 | 313,330 |
| 2019 | 2,450 | 2,450 | 0 | 304,367 |
| 2020 | 2,450 | 2,450 | 0 | 293,172 |
| 2021 | 2,450 | 2,450 | 0 | 309,097 |
| 2022 | 2,450 | 2,450 | 0 | 299,825 |
| 2023 | 2,450 | 2,450 | 0 | 285,891 |
| 2024 | 2,450 | 2,450 | 0 | 291,330 |

### 2.5 `abs_sa2_unemployment_quarterly` — recent quarters

| year_qtr | Rows | Distinct SA2 | NULL rate | Avg rate (%) |
|---|---:|---:|---:|---:|
| `2025-Q4` | 2,336 | 2,336 | 0 | 4.37 |
| `2025-Q3` | 2,336 | 2,336 | 0 | 4.31 |
| `2025-Q2` | 2,336 | 2,336 | 0 | 4.25 |
| `2025-Q1` | 2,336 | 2,336 | 0 | 4.20 |
| `2024-Q4` | 2,336 | 2,336 | 0 | 4.15 |
| `2024-Q3` | 2,336 | 2,336 | 0 | 4.14 |
| `2024-Q2` | 2,336 | 2,336 | 0 | 4.03 |
| `2024-Q1` | 2,336 | 2,336 | 293 | 3.93 |

### 2.6 `jsa_ivi_state_monthly` — recent months

| year_month | Rows |
|---|---:|
| `2026-03` | 18 |
| `2026-02` | 18 |
| `2026-01` | 18 |
| `2025-12` | 18 |
| `2025-11` | 18 |
| `2025-10` | 18 |

---

## 3. Banding cutoff conventions in shipped UI

Searching shipped UI files for `low/mid/high decile` cutoffs to ensure Layer 3 band thresholds match the existing convention (Decision 65 / Visual Consistency Principle).

_33 candidate hit(s) found across UI files:_

| File | Line | Snippet |
|---|---:|---|
| `catchment_html.py` | 187 | `        "high":     "#c0392b",` |
| `catchment_html.py` | 189 | `        "low":      "#27ae60",` |
| `docs/_op_chunks/part3.txt` | 374 | `        <span class="will-show">Will show: <b>weighted SEIFA decile headline</b>,` |
| `docs/_op_chunks/part3.txt` | 375 | `        a <b>1â€“10 decile histogram</b>, a <b>low/mid/high band split</b>,` |
| `docs/_op_chunks/part3.txt` | 403 | `          <div title="Decile ${d}: ${n} centre${n===1?'':'s'}"` |
| `docs/_op_chunks/part3.txt` | 415 | `    if (wd <= 3.5)      wdBandLabel = '<span style="color:var(--danger,#e66);">low-SES catchment mix</span>';` |
| `docs/_op_chunks/part3.txt` | 416 | `    else if (wd <= 6.5) wdBandLabel = '<span style="color:var(--amber,#d8b050);">mid-SES catchment mix</span>';` |
| `docs/_op_chunks/part3.txt` | 430 | `    <div class="fact"><span class="k">Weighted SEIFA decile</span>` |
| `docs/_op_chunks/part3.txt` | 435 | `        <span>SEIFA decile distribution</span>` |
| `docs/centre.html` | 722 | `        <span class="k">SEIFA decile</span>` |
| `docs/centre.html` | 724 | `          <b>${c.seifa_decile.value ?? "—"}</b>` |
| `docs/centre.html` | 725 | `          ${c.seifa_decile.value != null ? '<span style="color:var(--text-mute);font-size:11px;">/10</span>' : ""}` |
| `docs/index.html` | 2723 | `                <div class="stat-value" style="font-size:20px">${sa2.irsd_decile ? sa2.irsd_decile + '/10' : 'n/a'}</div>` |
| `docs/operator.html` | 2069 | `        <span class="will-show">Will show: <b>weighted SEIFA decile headline</b>,` |
| `docs/operator.html` | 2070 | `        a <b>1–10 decile histogram</b>, a <b>low/mid/high band split</b>,` |
| `docs/operator.html` | 2098 | `          <div title="Decile ${d}: ${n} centre${n===1?'':'s'}"` |
| `docs/operator.html` | 2110 | `    if (wd <= 3.5)      wdBandLabel = '<span style="color:var(--danger,#e66);">low-SES catchment mix</span>';` |
| `docs/operator.html` | 2111 | `    else if (wd <= 6.5) wdBandLabel = '<span style="color:var(--amber,#d8b050);">mid-SES catchment mix</span>';` |
| `docs/operator.html` | 2125 | `    <div class="fact"><span class="k">Weighted SEIFA decile</span>` |
| `docs/operator.html` | 2130 | `        <span>SEIFA decile distribution</span>` |
| `generate_dashboard.py` | 3045 | `                <div class="stat-value" style="font-size:20px">${{sa2.irsd_decile ? sa2.irsd_decile + '/10' : 'n/a'}}</div>` |
| `module2b_catchment.py` | 140 | `def fee_sensitivity_label(irsd_decile: Optional[int], ccs_rate: float) -> str:` |
| `module2b_catchment.py` | 147 | `    if irsd_decile <= 3:` |
| `module2b_catchment.py` | 149 | `    if irsd_decile <= 6:` |
| `module2b_catchment.py` | 497 | `def seifa_label(decile: Optional[int]) -> str:` |
| `module2b_catchment.py` | 499 | `    if decile <= 2:  return "highly_disadvantaged"` |
| `module2b_catchment.py` | 500 | `    if decile <= 4:  return "disadvantaged"` |
| `module2b_catchment.py` | 501 | `    if decile <= 6:  return "average"` |
| `module2b_catchment.py` | 502 | `    if decile <= 8:  return "advantaged"` |
| `operator_page.py` | 84 | `VALUATION_LOW_PER_PLACE  = 25_000` |
| `operator_page.py` | 85 | `VALUATION_HIGH_PER_PLACE = 40_000` |
| `operator_page.py` | 738 | `    band_counts = {"low": 0, "mid": 0, "high": 0, "unknown": 0}` |
| `operator_page.py` | 739 | `    band_places = {"low": 0, "mid": 0, "high": 0, "unknown": 0}` |

**RECOMMENDATION (subject to confirmation by code review):**  
Use the conventional decile-based split:  
  - `low`  = decile 1-3  
  - `mid`  = decile 4-7  
  - `high` = decile 8-10  

This matches typical ABS / Remara-style 30/40/30 partitioning. If the shipped UI uses different cutoffs, Layer 3 should match those exactly per Decision 65. Decision needed before apply.

---

## 4. Initial metric set proposal

Based on the Layer 4 design block in the project status doc and the cohort overrides documented in `recon/layer3_decisions.md` D3:

| Metric (canonical name) | Source | Column / formula | Filter / note | Default cohort |
|---|---|---|---|---|
| `sa2_under5_count` | `abs_sa2_erp_annual` | persons | age_group = '0-4' | state |
| `sa2_total_population` | `abs_sa2_erp_annual` | persons | age_group = 'All ages' | state_x_remoteness |
| `sa2_under5_growth_5y` | `abs_sa2_erp_annual (derived)` | persons | age_group = '0-4'; (year_t - year_t-5) / year_t-5 | remoteness |
| `sa2_births_count` | `abs_sa2_births_annual` | births_count | (none) | state_x_remoteness |
| `sa2_unemployment_rate` | `abs_sa2_unemployment_quarterly` | rate | latest year_qtr | state |
| `sa2_median_employee_income` | `abs_sa2_socioeconomic_annual` | value where metric_name = 'median_employee_income' (verify) | (verify metric_name) | remoteness |
| `sa2_median_total_income_excl_govt` | `abs_sa2_socioeconomic_annual` | value where metric_name = 'median_total_income_excl_govt' (verify) | (verify metric_name) | remoteness |
| `sa2_lfp_persons` | `abs_sa2_education_employment_annual` | value where metric_name = 'ee_lfp_persons_pct' (verify) | (verify metric_name; canonical per Decision 61) | state_x_remoteness |
| `sa2_lfp_females` | `abs_sa2_education_employment_annual or census-derived` | value where metric_name = 'census_lfp_females_pct' (verify) | (verify metric_name; T33-derived per Decision 61) | state_x_remoteness |
| `sa2_lfp_males` | `abs_sa2_education_employment_annual or census-derived` | value where metric_name = 'census_lfp_males_pct' (verify) | (verify metric_name; T33-derived per Decision 61) | state_x_remoteness |
| `seifa_decile_sa2` | `(SA2-level lookup; derived or external)` | seifa_decile aggregated to SA2 mode | (decision needed: derive from services or import ABS SEIFA) | national |

_Several `metric_name` strings above are placeholders — the diagnostic Section 2.2 / 2.3 above lists the actual values present in `abs_sa2_socioeconomic_annual` and `abs_sa2_education_employment_annual`. Apply script must use the exact strings from those tables; this proposal must be reconciled against Section 2 before code is written._

---

## 5. Expected row counts for `layer3_sa2_metric_banding`

- Distinct SA2s (estimate): **2,450**
- Proposed metric count: **11**
- Year coverage: 1 year (latest-only metrics) to ~14 years (births / ERP)

Cardinality envelope:
- Lower bound (latest-year only across all metrics): ~26,950
- Mid estimate (5-year average history): ~134,750
- Upper bound (full 14-year history all metrics): ~377,300

Per-cohort dimension multiplies these by 1-3 (default cohort + any per-metric overrides).

---

## 6. Open decisions before apply

**O1.** Remoteness assignment path: **A** (download ABS Remoteness Areas GeoPackage, separate one-off ingest) or **B** (services-derived most-common ARIA+ per SA2, with backfill rule for SA2s lacking services)?

**O2.** Banding cutoffs: confirm low/mid/high split. Default proposal `1-3 / 4-7 / 8-10` — confirm matches shipped UI.

**O3.** Metric set: review Section 4 against Section 2 actuals; reconcile placeholder `metric_name` strings.

**O4.** Year coverage scope per metric: latest-year-only, full-history, or per-metric configurable?

**O5.** SEIFA: include in `layer3_sa2_metric_banding` as a national-cohort passthrough, OR leave as raw `services.seifa_decile` and not duplicate?

---

_End of diag._