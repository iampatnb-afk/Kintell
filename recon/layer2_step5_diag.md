# Layer 2 Step 5 — SALM SA2 Diagnostic

## 1. Workbook

- File: `SALM Smoothed SA2 Datafiles (ASGS 2021) - December quarter 2025.xlsx`
- Size: 2.25 MB

## 2. Sheets in workbook

- All sheets: `['Smoothed SA2 unemployment rate', 'Smoothed SA2 unemployment', 'Smoothed SA2 labour force']`

- `Smoothed SA2 unemployment rate` -> **rate**
- `Smoothed SA2 unemployment` -> **count**
- `Smoothed SA2 labour force` -> **labour_force**


## 3. Resolved sheet per metric

- rate: `Smoothed SA2 unemployment rate`
- count: `Smoothed SA2 unemployment`
- labour_force: `Smoothed SA2 labour force`

## 4.rate — sheet `Smoothed SA2 unemployment rate`

- Total columns: 63

```
Row  1: Smoothed Unemploym | · | · | · | · | · | · | ·
Row  2: Note: Cells contai | · | · | · | · | · | · | ·
Row  3: · | · | · | · | · | · | · | ·
Row  4: Statistical Area L | SA2 Code (2021 ASG | 2010-12-01 00:00:0 | 2011-03-01 00:00:0 | 2011-06-01 00:00:0 | 2011-09-01 00:00:0 | 2011-12-01 00:00:0 | 2012-03-01 00:00:0
Row  5: Braidwood | 101021007 | 3 | 2.3 | 2.1 | 2.1 | 2.3 | 2.5
Row  6: Karabar | 101021008 | 2.5 | 1.8 | 1.6 | 1.5 | 1.7 | 1.7
Row  7: Queanbeyan | 101021009 | 3.3 | 2.5 | 2.1 | 2 | 2.1 | 2.3
Row  8: Queanbeyan - East | 101021010 | 1.6 | 1.2 | 1.1 | 1 | 1.2 | 1.3
Row  9: Queanbeyan West -  | 101021012 | 1.2 | 0.8 | 0.6 | 0.5 | 0.6 | 0.6
Row 10: Googong | 101021610 | - | - | - | - | - | -
Row 11: Queanbeyan Surroun | 101021611 | - | - | - | - | - | -
Row 12: Bombala | 101031013 | 4 | 3.3 | 2.9 | 2.7 | 2.9 | 2.9
```

- SA2 code column: **1** (hits: 8)
- Header row: **None** (0 quarter cells)
- Quarter columns: **none detected**

## 4.count — sheet `Smoothed SA2 unemployment`

- Total columns: 63

```
Row  1: Smoothed Unemploym | · | · | · | · | · | · | ·
Row  2: Note: Cells contai | · | · | · | · | · | · | ·
Row  3: · | · | · | · | · | · | · | ·
Row  4: Statistical Area L | SA2 Code (2021 ASG | 2010-12-01 00:00:0 | 2011-03-01 00:00:0 | 2011-06-01 00:00:0 | 2011-09-01 00:00:0 | 2011-12-01 00:00:0 | 2012-03-01 00:00:0
Row  5: Braidwood | 101021007 | 53 | 42 | 38 | 39 | 44 | 47
Row  6: Karabar | 101021008 | 132 | 99 | 88 | 83 | 91 | 96
Row  7: Queanbeyan | 101021009 | 209 | 164 | 139 | 135 | 143 | 152
Row  8: Queanbeyan - East | 101021010 | 50 | 39 | 35 | 34 | 39 | 43
Row  9: Queanbeyan West -  | 101021012 | 97 | 66 | 51 | 45 | 47 | 50
Row 10: Googong | 101021610 | - | - | - | - | - | -
Row 11: Queanbeyan Surroun | 101021611 | - | - | - | - | - | -
Row 12: Bombala | 101031013 | 50 | 41 | 37 | 35 | 37 | 37
```

- SA2 code column: **1** (hits: 8)
- Header row: **None** (0 quarter cells)
- Quarter columns: **none detected**

## 4.labour_force — sheet `Smoothed SA2 labour force`

- Total columns: 63

```
Row  1: Smoothed Labour Fo | · | · | · | · | · | · | ·
Row  2: Note: Cells contai | · | · | · | · | · | · | ·
Row  3: · | · | · | · | · | · | · | ·
Row  4: Statistical Area L | SA2 Code (2021 ASG | 2010-12-01 00:00:0 | 2011-03-01 00:00:0 | 2011-06-01 00:00:0 | 2011-09-01 00:00:0 | 2011-12-01 00:00:0 | 2012-03-01 00:00:0
Row  5: Braidwood | 101021007 | 1761 | 1806 | 1832 | 1859 | 1885 | 1899
Row  6: Karabar | 101021008 | 5249 | 5363 | 5425 | 5475 | 5513 | 5501
Row  7: Queanbeyan | 101021009 | 6297 | 6459 | 6559 | 6648 | 6728 | 6748
Row  8: Queanbeyan - East | 101021010 | 3139 | 3223 | 3283 | 3330 | 3366 | 3365
Row  9: Queanbeyan West -  | 101021012 | 7974 | 8181 | 8314 | 8420 | 8502 | 8501
Row 10: Googong | 101021610 | - | - | - | - | - | -
Row 11: Queanbeyan Surroun | 101021611 | - | - | - | - | - | -
Row 12: Bombala | 101031013 | 1240 | 1261 | 1270 | 1278 | 1287 | 1286
```

- SA2 code column: **1** (hits: 8)
- Header row: **None** (0 quarter cells)
- Quarter columns: **none detected**

## 5. audit_log + target table

- audit_log columns: `['audit_id', 'actor', 'action', 'subject_type', 'subject_id', 'before_json', 'after_json', 'reason', 'occurred_at']`
- Last audit_id: 128 (next: 129)
- `abs_sa2_unemployment_quarterly`: does not exist (apply will create)


## 6. Column map (written to JSON)

```json
{
  "workbook": "abs_data\\SALM Smoothed SA2 Datafiles (ASGS 2021) - December quarter 2025.xlsx",
  "metrics": {
    "rate": {
      "sheet_name": "Smoothed SA2 unemployment rate",
      "header_row": null,
      "data_start_row": 1,
      "sa2_code_col": 1,
      "quarter_cols": {}
    },
    "count": {
      "sheet_name": "Smoothed SA2 unemployment",
      "header_row": null,
      "data_start_row": 1,
      "sa2_code_col": 1,
      "quarter_cols": {}
    },
    "labour_force": {
      "sheet_name": "Smoothed SA2 labour force",
      "header_row": null,
      "data_start_row": 1,
      "sa2_code_col": 1,
      "quarter_cols": {}
    }
  },
  "null_markers": [
    "-",
    "..",
    "np",
    "n.a.",
    "na",
    "NA",
    "NP",
    ""
  ],
  "audit_log_columns": [
    "audit_id",
    "actor",
    "action",
    "subject_type",
    "subject_id",
    "before_json",
    "after_json",
    "reason",
    "occurred_at"
  ],
  "target_table": "abs_sa2_unemployment_quarterly",
  "notes": [
    "Each metric (rate, count, labour_force) is on its own sheet.",
    "Each row is one SA2; each column is one quarter (wide format).",
    "Apply will pivot to long: (sa2_code, year_qtr, metric, value)."
  ]
}
```
