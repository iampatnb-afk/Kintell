# Layer 4.2 Pre-Work Probe — 2026-04-28T17:26:30

Repo root: `C:\Users\Patrick Bell\remara-agent`
DB: `C:\Users\Patrick Bell\remara-agent\data\kintell.db` (read-only)

## A. Catchment surface

### A.1 Catchment-flavoured Python files (3)


#### `catchment_html.py` (12448 bytes)

Functions:

| name | lines | first-line doc |
|---|---|---|
| `_sb_url` | 9–13 | Google search scoped to startingblocks.gov.au for the exact centre. |
| `_google_url` | 16–20 | Google search URL for operator website. |
| `_clean` | 23–26 | Return empty string for None/nan values. |
| `_fmt_phone` | 29–38 | Format Australian phone number for display. |
| `nqs_badge` | 41–53 |  |
| `kinder_badge` | 56–59 |  |
| `nfp_badge` | 62–65 |  |
| `render_centre_row` | 68–137 | Render a single centre as a table row. |
| `render_catchment_block` | 140–280 | Render full catchment section as HTML for email digest. |
| `fmt_cagr` | 172–177 |  |

Keyword hits (first 40):

```
    2: catchment_html.py — HTML renderer for catchment data in email digest.
    4:     from catchment_html import render_catchment_block
   29: def _fmt_phone(phone: str) -> str:
   68: def render_centre_row(c: dict, is_lead: bool = False) -> str:
   69:     """Render a single centre as a table row."""
   76:     phone_fmt  = _fmt_phone(phone_raw)
  107:     if phone_fmt and phone_raw:
  108:         phone_cell = f"<a href='tel:{phone_raw}' style='color:#2c3e50;text-decoration:none'>{phone_fmt}</a>"
  140: def render_catchment_block(lead: dict) -> str:
  141:     """Render full catchment section as HTML for email digest."""
  142:     c = lead.get("catchment", {})
  154:     irsd      = c.get("irsd_decile")
  159:     ratio        = c.get("supply_ratio")
  172:     def fmt_cagr(cagr, positive_color="#27ae60", negative_color="#c0392b"):
  203:         centre_rows += render_centre_row(ctr, is_lead=is_lead_centre)
  233:         Catchment: {sa2} [{sa2_code}]
  241:                     {fmt_cagr(pop_cagr)}
  248:                     {fmt_cagr(inc_cagr)}
  260:                     IRSD: <b>{irsd or "n/a"}/10</b> &nbsp;|&nbsp; IRSAD: <b>{irsad or "n/a"}/10</b>
```

#### `module2b_catchment.py` (29674 bytes)

Functions:

| name | lines | first-line doc |
|---|---|---|
| `estimate_ccs_rate` | 118–126 | Estimate CCS subsidy rate (0.0-1.0) for a given weekly household income. |
| `estimate_gap_fee` | 129–137 | Estimate family out-of-pocket gap fee per day. |
| `fee_sensitivity_label` | 140–153 | Classify fee sensitivity based on IRSD decile and CCS rate. |
| `load_abs_timeseries` | 160–214 | Load ABS Data by Region Excel file as a wide timeseries. |
| `load_abs_single_year` | 217–263 | Load a single year of ABS data for multiple columns. |
| `get_latest_value` | 266–276 | Get most recent non-null value. Returns (value, year) or (None, None). |
| `calc_cagr` | 279–291 | Calculate CAGR % between two years for an SA2. |
| `growth_arrow` | 294–299 |  |
| `growth_label` | 302–307 |  |
| `load_concordance` | 314–325 |  |
| `postcode_to_sa2` | 328–340 |  |
| `is_nfp` | 347–350 | Detect NFP operator from legal name keywords. |
| `compute_supply_and_nfp` | 353–402 | Compute per-SA2 LDC supply stats and NFP ratio. |
| `load_contact_databases` | 409–442 |  |
| `match_contacts` | 445–473 |  |
| `scrape_startingblocks_fees` | 480–482 | Stub — returns None. Replace with live scraper when ready. |
| `supply_tier` | 489–494 |  |
| `seifa_label` | 497–503 |  |
| `format_qikreport` | 506–544 |  |
| `_fmt_int` | 547–549 |  |
| `_fmt_dollar` | 551–553 |  |
| `_fmt_ratio` | 555–557 |  |
| `enrich_lead_catchment` | 564–673 |  |
| `run` | 680–749 |  |

Keyword hits (first 40):

```
    2: module2b_catchment.py — Catchment & Market Context Enrichment
    6: OUTPUT: leads_catchment.json (enriched lead cards with catchment data)
    8: Catchment block includes:
   13:   - SEIFA IRSD + IRSAD deciles (socio-economic indicators)
   27:   python module2b_catchment.py
   28:   python module2b_catchment.py --live
   51: OUTPUT_FILE  = BASE_DIR / "leads_catchment.json"
   55: SEIFA_FILE   = ABS_DIR / "Family and Community Database.xlsx"
   63: IRSD_COL     = "SEIFA Index of relative socio-economic disadvantage (IRSD) - rank within Australia (decile)"
   64: IRSAD_COL    = "SEIFA Index of relative socio-economic advantage and disadvantage (IRSAD) - rank within Australia (decile)"
  109:     datefmt="%H:%M:%S",
  140: def fee_sensitivity_label(irsd_decile: Optional[int], ccs_rate: float) -> str:
  142:     Classify fee sensitivity based on IRSD decile and CCS rate.
  143:     IRSD decile 1 = most disadvantaged, 10 = least disadvantaged.
  145:     if irsd_decile is None:
  147:     if irsd_decile <= 3:
  148:         return "high"       # disadvantaged catchment, very price sensitive
  149:     if irsd_decile <= 6:
  497: def seifa_label(decile: Optional[int]) -> str:
  507:     c = lead.get("catchment", {})
  510:     ratio    = c.get("supply_ratio")
  511:     irsd     = c.get("irsd_decile")
  518:         f"-- CATCHMENT REPORT: {lead.get('service_name', 'Unknown')} --",
  523:         f"  Under-5 pop:     {_fmt_int(c.get('pop_0_4'))} ({c.get('pop_year','?')})  "
  525:         f"  Median income:   {_fmt_dollar(c.get('median_income_weekly_annual'))} p.a. "
  530:         f"  Est. gap fee:    {_fmt_dollar(gap_fee)}/day  "
  532:         f"  IRSD decile:     {irsd or 'n/a'}/10  [{seifa_label(irsd).upper()}]",
  538:         f"  Licensed places: {_fmt_int(c.get('total_licensed_places'))}",
  539:         f"  Supply ratio:    {_fmt_ratio(ratio)}x  [{supply_tier(ratio).upper()}]",
  541:         f"  Avg daily fee:   {_fmt_dollar(c.get('avg_daily_fee'))}",
  547: def _fmt_int(v) -> str:
  551: def _fmt_dollar(v) -> str:
  555: def _fmt_ratio(v) -> str:
  564: def enrich_lead_catchment(
  569:     seifa_df: pd.DataFrame,
  593:     # SEIFA
  594:     irsd_decile  = None
  596:     if not seifa_df.empty and sa2_code and sa2_code in seifa_df.index:
  597:         row = seifa_df.loc[sa2_code]
  598:         irsd_val  = row.get(IRSD_COL)
```

#### `module2c_targeting.py` (23634 bytes)

Functions:

| name | lines | first-line doc |
|---|---|---|
| `is_nfp` | 94–109 |  |
| `normalise_name` | 112–127 | Normalise operator name for matching. |
| `extract_ho_address` | 130–136 | Extract a normalised HO address key (street + suburb). |
| `days_since` | 139–149 | Days since a date string (dd/mm/yyyy or similar). |
| `infer_groups` | 156–296 | Infer operator groups from ACECQA data using tiered matching. |
| `score_group` | 303–485 | Score an operator group against Remara target criteria. |
| `run` | 492–592 |  |

Keyword hits (first 40):

```
   85:     datefmt="%H:%M:%S",
  143:     for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y"]:
  145:             d = datetime.strptime(str(date_str).strip(), fmt).date()
```

### A.2 Catchment-flavoured HTML files (0)

_(no docs/catchment.html or similar — Layer 4.2 will need to invent the visual primitives, but inherit from operator.html / centre.html)_

## B. DB tables

### B.1 Catchment-flavoured tables


#### `service_catchment_cache`

```
  service_id                   INTEGER    pk=1 notnull=0
  sa2_code                     TEXT       pk=0 notnull=0
  sa2_name                     TEXT       pk=0 notnull=0
  u5_pop                       INTEGER    pk=0 notnull=0
  median_income                REAL       pk=0 notnull=0
  seifa_irsd                   INTEGER    pk=0 notnull=0
  unemployment_pct             REAL       pk=0 notnull=0
  supply_ratio                 REAL       pk=0 notnull=0
  supply_band                  TEXT       pk=0 notnull=0
  supply_ratio_4q_change       REAL       pk=0 notnull=0
  is_deteriorating             INTEGER    pk=0 notnull=0
  competing_centres_count      INTEGER    pk=0 notnull=0
  new_competitor_12m           INTEGER    pk=0 notnull=0
  ccs_dependency_pct           REAL       pk=0 notnull=0
  as_of_date                   TEXT       pk=0 notnull=0
  created_at                   TEXT       pk=0 notnull=0
  updated_at                   TEXT       pk=0 notnull=0
```

Row count: **0**

### B.2 `services` table — catchment-relevant columns

```
  sa2_code
  sa2_name
  lat
  lng
  aria_plus
  seifa_decile
```

## C. Trajectory data — source-table inventory

Sample SA2 = `506031124` (Bentley - Wilson - St James, the corrected SA2 for service 246 after Step 1c).


### sa2_under5_count

Source table: `abs_sa2_erp_annual`  (kind: annual)

- Total rows: **88,344**
- Period range: **2011 → 2024**, 9 distinct periods
- Filter applied: `age_group = 'under_5_persons'`

- Sample trajectory for SA2 `506031124` (9 points):

```
        2011  None
        2016  None
        2018  None
        2019  1082
        2020  1087
        2021  1072
        2022  1079
        2023  1072
        2024  1080
```

### sa2_total_population

Source table: `abs_sa2_erp_annual`  (kind: annual)

- Total rows: **88,344**
- Period range: **2011 → 2024**, 9 distinct periods
- Filter applied: `age_group = 'total_persons'`

- Sample trajectory for SA2 `506031124` (9 points):

```
        2011  None
        2016  None
        2018  None
        2019  21092
        2020  21616
        2021  21462
        2022  21541
        2023  22928
        2024  23893
```

### sa2_births_count

Source table: `abs_sa2_births_annual`  (kind: annual)

- Total rows: **34,300**
- Period range: **2011 → 2024**, 14 distinct periods

- Sample trajectory for SA2 `506031124` (14 points):

```
        2011  294
        2012  263
        2013  281
        2014  276
        2015  255
        2016  273
        2017  238
        2018  223
        2019  266
        2020  262
        2021  239
        2022  222
        2023  249
        2024  204
```

### sa2_unemployment_rate

Source table: `abs_sa2_unemployment_quarterly`  (kind: quarterly)

- Total rows: **142,496**
- Period range: **2010-Q4 → 2025-Q4**, 61 distinct periods

- Sample trajectory for SA2 `506031124` (61 points):

```
     2010-Q4  4.8
     2011-Q1  5.1
     2011-Q2  5.8
     2011-Q3  6.0
     2011-Q4  6.2
     2012-Q1  6.0
     2012-Q2  5.4
     2012-Q3  5.3
     2012-Q4  5.2
     2013-Q1  5.3
     2013-Q2  5.7
     2013-Q3  5.8
     2013-Q4  5.3
     2014-Q1  5.5
     2014-Q2  5.8
     2014-Q3  6.3
     2014-Q4  7.1
     2015-Q1  7.4
     2015-Q2  7.3
     2015-Q3  6.9
     2015-Q4  6.5
     2016-Q1  6.3
     2016-Q2  6.4
     2016-Q3  6.5
     2016-Q4  6.7
     2017-Q1  6.7
     2017-Q2  6.6
     2017-Q3  6.6
     2017-Q4  6.7
     2018-Q1  6.7
     2018-Q2  6.6
     2018-Q3  7.1
     2018-Q4  7.4
     2019-Q1  7.7
     2019-Q2  8.3
     2019-Q3  8.1
     2019-Q4  7.4
     2020-Q1  6.8
     2020-Q2  6.7
     2020-Q3  7.0
     2020-Q4  7.7
     2021-Q1  8.3
     2021-Q2  7.7
     2021-Q3  6.9
     2021-Q4  5.8
     2022-Q1  5.0
     2022-Q2  4.5
     2022-Q3  4.3
     2022-Q4  4.4
     2023-Q1  4.6
     2023-Q2  4.7
     2023-Q3  4.8
     2023-Q4  4.7
     2024-Q1  4.6
     2024-Q2  4.6
     2024-Q3  4.5
     2024-Q4  4.1
     2025-Q1  3.9
     2025-Q2  4.0
     2025-Q3  3.9
     2025-Q4  4.1
```

### Long-format metric tables (income trio + LFP triplet)


#### `abs_sa2_education_employment_annual`  (cols: sa2_code, year, metric_name, value)

Period column guess: `year`

| metric_name | rows | distinct periods | min | max |
|---|---:|---:|---|---|
| census_emp_to_pop_females_pct | 7,175 | 3 | 2011 | 2021 |
| census_emp_to_pop_males_pct | 7,225 | 3 | 2011 | 2021 |
| census_lfp_females_pct | 7,175 | 3 | 2011 | 2021 |
| census_lfp_males_pct | 7,225 | 3 | 2011 | 2021 |
| census_unemp_females_pct | 7,149 | 3 | 2011 | 2021 |
| census_unemp_males_pct | 7,202 | 3 | 2011 | 2021 |
| ee_bachelor_degree_pct | 7,066 | 3 | 2011 | 2021 |
| ee_clerical_admin_pct | 7,032 | 3 | 2011 | 2021 |
| ee_jobs_admin_support_count | 11,821 | 5 | 2018 | 2022 |
| ee_jobs_females_count | 11,985 | 5 | 2018 | 2022 |
| ee_jobs_finance_count | 11,688 | 5 | 2018 | 2022 |
| ee_jobs_info_media_count | 11,400 | 5 | 2018 | 2022 |
| ee_jobs_professional_scientific_count | 11,794 | 5 | 2018 | 2022 |
| ee_jobs_total_count | 12,067 | 5 | 2018 | 2022 |
| ee_lfp_persons_pct | 7,183 | 3 | 2011 | 2021 |
| ee_managers_pct | 7,066 | 3 | 2011 | 2021 |
| ee_preschool_15h_plus_count | 12,255 | 6 | 2018 | 2023 |
| ee_preschool_4yo_count | 13,896 | 6 | 2018 | 2023 |
| ee_preschool_total_count | 13,903 | 6 | 2018 | 2023 |
| ee_professionals_pct | 7,056 | 3 | 2011 | 2021 |
| ee_unemployment_rate_persons_pct | 7,003 | 3 | 2011 | 2021 |
| ee_year12_completion_pct | 7,161 | 3 | 2011 | 2021 |

Sample trajectory for SA2 `506031124`:


- **ee_lfp_persons_pct** (3 points):

```
        2011  52.0
        2016  54.2
        2021  61.3
```

- **census_lfp_females_pct** (3 points):

```
        2011  50.23
        2016  52.57
        2021  60.59
```

- **census_lfp_males_pct** (3 points):

```
        2011  64.91
        2016  65.74
        2021  72.9
```

#### `abs_sa2_socioeconomic_annual`  (cols: sa2_code, year, metric_name, value)

Period column guess: `year`

| metric_name | rows | distinct periods | min | max |
|---|---:|---:|---|---|
| median_employee_income_annual | 26,994 | 11 | 2011 | 2025 |
| median_equiv_household_income_weekly | 26,994 | 11 | 2011 | 2025 |
| median_investment_income_annual | 26,994 | 11 | 2011 | 2025 |
| median_own_business_income_annual | 26,994 | 11 | 2011 | 2025 |
| median_superannuation_income_annual | 26,994 | 11 | 2011 | 2025 |
| median_total_income_excl_pensions_annual | 26,994 | 11 | 2011 | 2025 |

Sample trajectory for SA2 `506031124`:


- **median_employee_income_annual** (11 points):

```
        2011  None
        2016  None
        2017  None
        2018  40910.0
        2019  41796.0
        2020  43660.0
        2021  47787.0
        2022  51445.0
        2023  None
        2024  None
        2025  None
```

- **median_equiv_household_income_weekly** (11 points):

```
        2011  621.0
        2016  727.0
        2017  None
        2018  None
        2019  None
        2020  None
        2021  952.0
        2022  None
        2023  None
        2024  None
        2025  None
```

- **median_total_income_excl_pensions_annual** (11 points):

```
        2011  None
        2016  None
        2017  None
        2018  37002.0
        2019  37990.0
        2020  39624.0
        2021  44991.0
        2022  49297.0
        2023  None
        2024  None
        2025  None
```

## D. Open questions for the design doc

Questions surfaced by this probe (to be closed in the design note):

1. **Supply-ratio source.** Probe section A.1 will reveal whether `module2b_catchment.py` already computes per-centre supply ratio, and whether it's stored anywhere (`service_catchment_cache`?) or recomputed per render.
2. **Competitor density definition.** Centres within X km? Within same SA2? Within ABS Distance to Service shape? — pick one before building.
3. **Cohort-distribution histogram bin count.** 10 bins (decile-aligned) or finer (20–30 for shape visibility)?
4. **Sparse-trajectory rendering.** Income trio + LFP triplet have only 3–4 data points. Render as small connected-dot trajectory rather than sparkline. Probe section C confirms exact point counts.
5. **Catchment-data placement on centre page.** New `Catchment metrics` section after Catchment / before Population? Or rolled into Catchment card?
