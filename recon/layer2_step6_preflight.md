# Layer 2 Step 6 — Preflight Findings

Read-only inventory of ABS ERP workbook before ingest.

## A. File presence

- OK: `Population and People Database.xlsx` present (20.82 MB)
- OK: DB present at `C:\Users\Patrick Bell\remara-agent\data\kintell.db`

## B. Open workbook Table 1

- Sheets in workbook: `['Contents', 'Table 1', 'Table 2', 'Table 3']`
- OK: opened sheet `Table 1`

## C. Header row & under-5 cohort columns

- Header row 6: 12 non-null columns of 164 total

### Key columns (first 6)

| idx | header |
|---:|---|
| 0 | `None` |
| 1 | `None` |
| 2 | `None` |
| 3 | `Estimated resident population - year ended 30 June` |
| 4 | `None` |
| 5 | `None` |

### Under-5 cohort columns (per status doc: indices 12, 48, 84)

| idx | header |
|---:|---|
| 12 | `Estimated resident population - Males - year ended 30 June` |
| 48 | `Estimated resident population - Females - year ended 30 June` |
| 84 | `Estimated resident population - Persons - year ended 30 June` |

## D. First 5 sample data rows (after header)

Showing column 0 (likely region code), column 1 (likely region name), and the 3 under-5 cohort columns.

| code | name | u5_a | u5_b | u5_c |
|---|---|---:|---:|---:|
| `Code` | `Label` | Males - 0-4 years (no.) | Females - 0-4 years (no.) | Persons - 0-4 years (no.) |
| `AUS` | `Australia` | - | - | - |
| `AUS` | `Australia` | - | - | - |
| `AUS` | `Australia` | - | - | - |
| `AUS` | `Australia` | 799652 | 754377 | 1554029 |

## E. Projected ingest volume

- Total data rows: **26,189**
- SA2 rows (9-digit code in col 0): **22,086**
- Non-SA2 rows (Australia/State/GCCSA aggregates): **4,099**
- Blank rows: **4**

Per status doc, expected ingest volume ~25K rows after filter to 9-digit SA2 codes.

## F. Overlap with `services.sa2_code` (post Step 1)

- Distinct `services.sa2_code` values (non-null): **1,268**
- Workbook distinct SA2 codes: **2,454**
- Service SA2 codes matched in workbook: **1,268**
- Service SA2 codes UNMATCHED in workbook: **0**

## G. Recommended schema (for review)

```
CREATE TABLE abs_sa2_erp_annual (
    sa2_code     TEXT    NOT NULL,
    year         INTEGER NOT NULL,
    age_group    TEXT    NOT NULL, -- 'persons' / 'males' / 'females'
    persons      INTEGER,
    PRIMARY KEY (sa2_code, year, age_group)
);
```

(Long format. Wide-format alternative deferred to ingest step decision.)
