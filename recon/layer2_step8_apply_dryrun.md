# Layer 2 Step 8 — Apply (DRY RUN)

Generated: 2026-04-27T21:49:29
Mode: **dry-run**

## Summary

- Source: `abs_data/Births_SA2_2011_2024.xlsx`
- Source sheets read: 8
- Total records extracted: **34,300**
- With numeric births_count: **34,300**
- 'np' (confidentialized): 0
- NULL: 0
- Unparseable: 0
- Distinct SA2 codes: **2,450** (invariant: 2,000–2,500)
- Years covered: **[2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]**
- Negative births_count values: 0
- Canonical universe (abs_sa2_erp_annual): 2,454 SA2s
- Orphan SA2s (not in canonical): 0

## Invariants

✓ All invariants pass.
- distinct SA2 count: 2450 ∈ [2000, 2500]
- years exactly cover 2011..2024
- 0 orphan SA2s
- 0 negative births
- per-year national sum within ±5% of ABS

## Per-year national sum vs ABS Cat 3301.0

| year | SA2-sum | ABS published | delta | within ±5%? |
|---:|---:|---:|---:|:-:|
| 2011 | 300,889 | 297,900 | +2,989 (+1.0%) | ✓ |
| 2012 | 308,709 | 309,600 | -891 (-0.3%) | ✓ |
| 2013 | 306,917 | 308,100 | -1,183 (-0.4%) | ✓ |
| 2014 | 298,163 | 299,700 | -1,537 (-0.5%) | ✓ |
| 2015 | 303,021 | 305,400 | -2,379 (-0.8%) | ✓ |
| 2016 | 309,022 | 311,100 | -2,078 (-0.7%) | ✓ |
| 2017 | 307,131 | 309,100 | -1,969 (-0.6%) | ✓ |
| 2018 | 313,330 | 315,100 | -1,770 (-0.6%) | ✓ |
| 2019 | 304,367 | 305,800 | -1,433 (-0.5%) | ✓ |
| 2020 | 293,172 | 294,400 | -1,228 (-0.4%) | ✓ |
| 2021 | 309,097 | 309,900 | -803 (-0.3%) | ✓ |
| 2022 | 299,825 | 300,700 | -875 (-0.3%) | ✓ |
| 2023 | 285,891 | 286,900 | -1,009 (-0.4%) | ✓ |
| 2024 | 291,330 | 292,500 | -1,170 (-0.4%) | ✓ |

## Per-state table breakdown

| sheet | SA2 rows | records | year columns detected |
|---|---:|---:|---:|
| `Table 1` | 642 | 8,988 | 14 |
| `Table 2` | 522 | 7,308 | 14 |
| `Table 3` | 546 | 7,644 | 14 |
| `Table 4` | 174 | 2,436 | 14 |
| `Table 5` | 265 | 3,710 | 14 |
| `Table 6` | 99 | 1,386 | 14 |
| `Table 7` | 68 | 952 | 14 |
| `Table 8` | 134 | 1,876 | 14 |

### Births column detection (sample: `Table 1`)

Year → 0-based column index of Births

| year | births_col | year_col |
|---:|---:|---:|
| 2011 | 3 | 2 |
| 2012 | 6 | 5 |
| 2013 | 9 | 8 |
| 2014 | 12 | 11 |
| 2015 | 15 | 14 |
| 2016 | 18 | 17 |
| 2017 | 21 | 20 |
| 2018 | 24 | 23 |
| 2019 | 27 | 26 |
| 2020 | 30 | 29 |
| 2021 | 33 | 32 |
| 2022 | 36 | 35 |
| 2023 | 39 | 38 |
| 2024 | 42 | 41 |

## Sample records (first 10 by SA2 / year)

| sa2_code | year | births_count |
|---|---:|---:|
| 101021007 | 2011 | 35 |
| 101021007 | 2012 | 34 |
| 101021007 | 2013 | 34 |
| 101021007 | 2014 | 31 |
| 101021007 | 2015 | 50 |
| 101021007 | 2016 | 32 |
| 101021007 | 2017 | 44 |
| 101021007 | 2018 | 36 |
| 101021007 | 2019 | 34 |
| 101021007 | 2020 | 33 |

## Audit log

Would insert: action=`abs_sa2_births_ingest_v1`, actor=`layer2_step8_apply`, subject_type=`abs_sa2_births_annual`

Simulated INSERT:

```sql
INSERT INTO audit_log (actor, action, subject_type, subject_id, before_json, after_json, reason) VALUES (?, ?, ?, ?, ?, ?, ?)
```

Params:

```
  [0] layer2_step8_apply
  [1] abs_sa2_births_ingest_v1
  [2] abs_sa2_births_annual
  [3] 0
  [4] {"payload": {"table": "abs_sa2_births_annual", "table_existed_pre": false}, "rows": 0}
  [5] {"payload": {"distinct_sa2": 2450, "method": "openpyxl iter_rows; year-col + sub-header 'Births' match", "national_sum_by_year": {"2011": 300889, "2012": 308709, "2013": 306917, "2014": 298163, "2015": 303021, "2016": 309022, "2017": 307131, "2018": 313330, "2019": 304367, "2020": 293172, "2021":...
  [6] Layer 2 Step 8: SA2 births annual ingest. 34,300 records (34,300 with numeric values, 0 confidentialized) across 2,450 SA2s and 14 years (2011-2024). Source: abs_data/Births_SA2_2011_2024.xlsx (Tables 1-8, per-state). Per-year national sums within ±5% of ABS Cat 3301.0.
```

---
End of report.
