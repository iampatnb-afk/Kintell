# Layer 2 Step 6 — Diagnostic

## 1. Workbook structure (first 12 rows)

- Total columns: **164**

## 2. Rows 1-12, columns 0-15 (metadata block)

```
Row  1:             Australi | · | · | · | · | · | · | · | · | · | · | · | · | · | · | ·
Row  2: Data by region, 2011 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | ·
Row  3: Released at 11.30am  | · | · | · | · | · | · | · | · | · | · | · | · | · | · | ·
Row  4: Table 1 POPULATION A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | ·
Row  5: · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | ·
Row  6: · | · | · | Estimated resident p | · | · | · | · | · | · | · | · | Estimated resident p | · | · | ·
Row  7: Code | Label | Year | Estimated resident p | Population density ( | Estimated resident p | Estimated resident p | Median age - males ( | Median age - females | Median age - persons | Working age populati | Working age populati | Males - 0-4 years (n | Males - 5-9 years (n | Males - 10-14 years  | Males - 15-19 years 
Row  8: AUS | Australia | 2011 | - | - | - | - | - | - | - | - | - | - | - | - | -
Row  9: AUS | Australia | 2016 | - | - | - | - | - | - | - | - | - | - | - | - | -
Row 10: AUS | Australia | 2018 | - | - | - | - | - | - | - | - | - | - | - | - | -
Row 11: AUS | Australia | 2019 | 25334826 | 3.3 | 12577221 | 12757605 | 36.7 | 38.4 | 37.5 | 16570435 | 65.4 | 799652 | 829903 | 803493 | 769691
Row 12: AUS | Australia | 2020 | 25649248 | 3.3 | 12728639 | 12920609 | 37 | 38.7 | 37.9 | 16704135 | 65.1 | 789571 | 832349 | 824582 | 766260
```

## 3. Year column detection

- col[2]: years seen = `[2011, 2016, 2018, 2019, 2020]`
- **Best guess year column: `2`**

## 5. Row 6 spanning headers (non-null only)

```
col[  3]: Estimated resident population - year ended 30 June
col[ 12]: Estimated resident population - Males - year ended 30 June
col[ 48]: Estimated resident population - Females - year ended 30 June
col[ 84]: Estimated resident population - Persons - year ended 30 June
col[120]: Births and deaths - year ended 31 December
col[124]: Internal and overseas migration - year ended 30 June
col[130]: Aboriginal and Torres Strait Islander Peoples - Census
col[132]: Overseas born population - Census
col[143]: Religious affiliation - Census
col[151]: Australian citizenship - Census
col[157]: Speaks a language other than English at home - Census
col[159]: Australian Defence Force service - Persons aged 15 years and over - Census
```

## 6. Total / all-ages column candidates

- row 7, col[121]: `Total fertility rate (births per female) (rate)`
- row 7, col[141]: `Total born overseas (no.)`
- row 7, col[142]: `Total born overseas (%)`
- **Best guess total_persons column: `121`**

## 7. First 5 SA2-shaped data rows

```
row  4103: sa2=101021007 label=Braidwood                 year=2011 u5m=- u5f=- u5p=- tot=-
row  4104: sa2=101021007 label=Braidwood                 year=2016 u5m=- u5f=- u5p=- tot=-
row  4105: sa2=101021007 label=Braidwood                 year=2018 u5m=- u5f=- u5p=- tot=2.17
row  4106: sa2=101021007 label=Braidwood                 year=2019 u5m=144 u5f=101 u5p=245 tot=2.1
row  4107: sa2=101021007 label=Braidwood                 year=2020 u5m=135 u5f=97 u5p=232 tot=1.94
```

## 8. audit_log schema (for apply step)

| cid | name | type | notnull | dflt | pk |
|---:|---|---|:-:|---|:-:|
| 0 | `audit_id` | `INTEGER` | 0 | `None` | 1 |
| 1 | `actor` | `TEXT` | 1 | `None` | 0 |
| 2 | `action` | `TEXT` | 1 | `None` | 0 |
| 3 | `subject_type` | `TEXT` | 1 | `None` | 0 |
| 4 | `subject_id` | `INTEGER` | 1 | `None` | 0 |
| 5 | `before_json` | `TEXT` | 0 | `None` | 0 |
| 6 | `after_json` | `TEXT` | 0 | `None` | 0 |
| 7 | `reason` | `TEXT` | 0 | `None` | 0 |
| 8 | `occurred_at` | `TEXT` | 0 | `datetime('now')` | 0 |

- `abs_sa2_erp_annual` does not exist (apply will create).

- Last `audit_id`: **127** (next: **128**)

## 9. Column map (written to JSON)

```json
{
  "sa2_code": 0,
  "region_label": 1,
  "year_column": 2,
  "under_5_males": 12,
  "under_5_females": 48,
  "under_5_persons": 84,
  "total_persons": 121
}
```

⚠️ **Verify the column map before running apply.** If `year_column` or `total_persons` shows `null`, review sections 3–6 above and edit the JSON manually.