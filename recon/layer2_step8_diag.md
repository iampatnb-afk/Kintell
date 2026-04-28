# Layer 2 Step 8 — Births SA2 Diagnostic

Generated: 2026-04-27T21:42:40
Source: `abs_data/Births_SA2_2011_2024.xlsx` (927 KB)
Sheets: 10 — 'Contents', 'Table 1', 'Table 2', 'Table 3', 'Table 4', 'Table 5', 'Table 6', 'Table 7', 'Table 8', 'Further information'

Read-only diagnostic. No mutations.

## Sheet: `Contents`

- max_row: **23**, max_col: **2**
- read first 8 rows for header analysis

### Raw header rows

| row | c1 | c2 |
|---|---|---|
| 1 | This tab outlines the contents of the datacube. It ranges... |  |
| 2 | Australian Bureau of Statistics |  |
| 3 | Registered births and summary statistics, Statistical Are... |  |
| 4 | Births, Australia 2024 |  |
| 5 | Released at 11:30am (Canberra time) 15 October 2025 |  |
| 6 | Contents |  |
| 7 | Tab | Description |
| 8 | Table 1 | Births, Summary, Statistical Areas Level 2, New South Wal... |

### Format detection

- Detected format: **unknown** (WIDE per Std 19 vs LONG per Std 26)

### SA2-level row detection

- (No 9-digit SA2 code found in first 200 rows)
---

## Sheet: `Table 1`

- max_row: **834**, max_col: **49**
- read first 8 rows for header analysis

### Raw header rows

| row | c1 | c2 | c3 | c4 | c5 | c6 | c7 | c8 | c9 | c10 | c11 | c12 | c13 | c14 | c15 | c16 | c17 | c18 | c19 | c20 | c21 | c22 | c23 | c24 | c25 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | This tab has one table with the estimated resident popula... |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 2 | Australian Bureau of Statistics |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 3 | Table 1: Births, Summary, Statistical Areas Level 2, New ... |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 4 | Births, Australia, 2024 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 5 | Place of Usual Residence |  | 2011 |  |  | 2012 |  |  | 2013 |  |  | 2014 |  |  | 2015 |  |  | 2016 |  |  | 2017 |  |  | 2018 |  |
| 6 |  |  | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births |
| 7 | 2021 ASGS Code | 2021 GCCSA,SA4,SA3,SA2 | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. |
| 8 | 102011028 | Avoca Beach - Copacabana | 7289 | 76 | np | 7362 | 75 | np | 7428 | 75 | 1.82 | 7502 | 70 | 1.76 | 7562 | 73 | 1.77 | 7626 | 71 | 1.76 | 7646 | 79 | 1.84 | 7655 | 80 |

### Format detection

- Detected format: **wide** (WIDE per Std 19 vs LONG per Std 26)
- Probable header row: **5**
- Year-like column count: 14
- Year span: 2011 → 2024
- Year columns (0-based, value): 2=2011, 5=2012, 8=2013, 11=2014, 14=2015, 17=2016, 20=2017, 23=2018, 26=2019, 29=2020, 32=2021, 35=2022, 38=2023, 41=2024

### SA2-level row detection

- First row with 9-digit SA2 code: **row 8**

### Sample SA2-level rows (rows 8–15)

| row | c1 | c2 | c3 | c4 | c5 | c6 | c7 | c8 | c9 | c10 | c11 | c12 | c13 | c14 | c15 | c16 | c17 | c18 | c19 | c20 | c21 | c22 | c23 | c24 | c25 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 8 | 102011028 | Avoca Beach - Copacabana | 7289 | 76 | np | 7362 | 75 | np | 7428 | 75 | 1.82 | 7502 | 70 | 1.76 | 7562 | 73 | 1.77 | 7626 | 71 | 1.76 | 7646 | 79 | 1.84 | 7655 | 80 |
| 9 | 102011029 | Box Head - MacMasters Beach | 10699 | 96 | np | 10748 | 89 | np | 10810 | 108 | 2.09 | 10871 | 90 | 2.04 | 10933 | 111 | 2.14 | 10995 | 92 | 2.01 | 11037 | 92 | 1.99 | 11087 | 97 |
| 10 | 102011030 | Calga - Kulnura | 4578 | 52 | np | 4632 | 34 | np | 4691 | 38 | 1.85 | 4746 | 45 | 1.7 | 4799 | 45 | 1.83 | 4858 | 41 | 1.83 | 4842 | 46 | 1.81 | 4833 | 52 |
| 11 | 102011031 | Erina - Green Point | 14072 | 121 | np | 14122 | 103 | np | 14186 | 100 | 1.81 | 14243 | 95 | 1.61 | 14285 | 111 | 1.62 | 14342 | 106 | 1.63 | 14499 | 89 | 1.58 | 14666 | 122 |
| 12 | 102011032 | Gosford - Springfield | 18748 | 262 | np | 18932 | 255 | np | 18998 | 269 | 1.89 | 19046 | 264 | 1.9 | 19194 | 245 | 1.88 | 19382 | 260 | 1.85 | 19705 | 243 | 1.77 | 20013 | 289 |
| 13 | 102011033 | Kariong | 6669 | 113 | np | 6640 | 76 | np | 6643 | 96 | 2.28 | 6633 | 59 | 1.88 | 6607 | 99 | 2.1 | 6586 | 61 | 1.83 | 6578 | 88 | 2.08 | 6577 | 104 |
| 14 | 102011034 | Kincumber - Picketts Valley | 7339 | 66 | np | 7365 | 72 | np | 7400 | 63 | 1.91 | 7425 | 60 | 1.83 | 7448 | 65 | 1.75 | 7483 | 55 | 1.67 | 7527 | 67 | 1.72 | 7582 | 76 |
| 15 | 102011035 | Narara | 6725 | 79 | np | 6747 | 79 | np | 6779 | 89 | 1.93 | 6798 | 63 | 1.83 | 6822 | 80 | 1.82 | 6848 | 80 | 1.72 | 6925 | 78 | 1.81 | 6996 | 89 |

### National aggregate sanity check

- SA2 rows aggregated: **642**

| year | SA2-sum | ABS published | delta | within ±5%? |
|---:|---:|---:|---:|:-:|
| 2011 | 7,218,529 | 297,900 | +6,920,629 (+2323.1%) | ⚠ |
| 2012 | 7,304,244 | 309,600 | +6,994,644 (+2259.3%) | ⚠ |
| 2013 | 7,404,032 | 308,100 | +7,095,932 (+2303.1%) | ⚠ |
| 2014 | 7,508,353 | 299,700 | +7,208,653 (+2405.3%) | ⚠ |
| 2015 | 7,616,168 | 305,400 | +7,310,768 (+2393.8%) | ⚠ |
| 2016 | 7,732,858 | 311,100 | +7,421,758 (+2385.7%) | ⚠ |
| 2017 | 7,855,316 | 309,100 | +7,546,216 (+2441.4%) | ⚠ |
| 2018 | 7,954,476 | 315,100 | +7,639,376 (+2424.4%) | ⚠ |
| 2019 | 8,046,748 | 305,800 | +7,740,948 (+2531.4%) | ⚠ |
| 2020 | 8,110,610 | 294,400 | +7,816,210 (+2655.0%) | ⚠ |
| 2021 | 8,097,062 | 309,900 | +7,787,162 (+2512.8%) | ⚠ |
| 2022 | 8,166,704 | 300,700 | +7,866,004 (+2615.9%) | ⚠ |
| 2023 | 8,341,199 | 286,900 | +8,054,299 (+2807.4%) | ⚠ |
| 2024 | 8,479,314 | 292,500 | +8,186,814 (+2798.9%) | ⚠ |

Tolerance: ±5% vs ABS Cat 3301.0 Table 1.
Misses larger than tolerance suggest column mis-detection or double-counting (state/national rows leaking into SA2 sum).

---

## Sheet: `Table 2`

- max_row: **649**, max_col: **50**
- read first 8 rows for header analysis

### Raw header rows

| row | c1 | c2 | c3 | c4 | c5 | c6 | c7 | c8 | c9 | c10 | c11 | c12 | c13 | c14 | c15 | c16 | c17 | c18 | c19 | c20 | c21 | c22 | c23 | c24 | c25 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | This tab has one table with the estimated resident popula... |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 2 | Australian Bureau of Statistics |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 3 | Table 2: Births, Summary, Statistical Areas Level 2, Vict... |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 4 | Births, Australia, 2024 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 5 | Place of Usual Residence |  | 2011 |  |  | 2012 |  |  | 2013 |  |  | 2014 |  |  | 2015 |  |  | 2016 |  |  | 2017 |  |  | 2018 |  |
| 6 |  |  | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births |
| 7 | 2021 ASGS Code | 2021 GCCSA,SA4,SA3,SA2 | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. |
| 8 | 206011106 | Brunswick East | 8966 | 102 | np | 9208 | 116 | np | 9870 | 105 | 0.96 | 10439 | 112 | 0.94 | 11062 | 122 | 0.89 | 11716 | 151 | 0.96 | 12154 | 141 | 0.99 | 12392 | 126 |

### Format detection

- Detected format: **wide** (WIDE per Std 19 vs LONG per Std 26)
- Probable header row: **5**
- Year-like column count: 14
- Year span: 2011 → 2024
- Year columns (0-based, value): 2=2011, 5=2012, 8=2013, 11=2014, 14=2015, 17=2016, 20=2017, 23=2018, 26=2019, 29=2020, 32=2021, 35=2022, 38=2023, 41=2024

### SA2-level row detection

- First row with 9-digit SA2 code: **row 8**

### Sample SA2-level rows (rows 8–15)

| row | c1 | c2 | c3 | c4 | c5 | c6 | c7 | c8 | c9 | c10 | c11 | c12 | c13 | c14 | c15 | c16 | c17 | c18 | c19 | c20 | c21 | c22 | c23 | c24 | c25 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 8 | 206011106 | Brunswick East | 8966 | 102 | np | 9208 | 116 | np | 9870 | 105 | 0.96 | 10439 | 112 | 0.94 | 11062 | 122 | 0.89 | 11716 | 151 | 0.96 | 12154 | 141 | 0.99 | 12392 | 126 |
| 9 | 206011107 | Brunswick West | 13864 | 180 | np | 13963 | 199 | np | 14057 | 184 | 1.3 | 14192 | 157 | 1.25 | 14344 | 196 | 1.24 | 14523 | 192 | 1.25 | 14556 | 186 | 1.28 | 14695 | 156 |
| 10 | 206011109 | Pascoe Vale South | 9860 | 145 | np | 9954 | 135 | np | 10038 | 121 | 1.93 | 10122 | 122 | 1.84 | 10251 | 119 | 1.75 | 10465 | 139 | 1.78 | 10698 | 138 | 1.79 | 10834 | 109 |
| 11 | 206011495 | Brunswick - North | 11981 | 192 | np | 12254 | 173 | np | 12548 | 167 | 1.39 | 12922 | 188 | 1.32 | 13225 | 161 | 1.25 | 13581 | 166 | 1.22 | 13728 | 187 | 1.2 | 13928 | 156 |
| 12 | 206011496 | Brunswick - South | 12006 | 159 | np | 12402 | 153 | np | 12836 | 165 | 1.08 | 13233 | 147 | 1.03 | 13574 | 170 | 1.03 | 13854 | 166 | 1.02 | 13984 | 174 | 1.07 | 14200 | 153 |
| 13 | 206011497 | Coburg - East | 12236 | 181 | np | 12483 | 191 | np | 12655 | 163 | 1.51 | 12852 | 185 | 1.48 | 13023 | 192 | 1.46 | 13286 | 170 | 1.44 | 13332 | 188 | 1.42 | 13379 | 167 |
| 14 | 206011498 | Coburg - West | 13998 | 226 | np | 14057 | 243 | np | 14188 | 196 | 1.84 | 14275 | 202 | 1.8 | 14397 | 191 | 1.64 | 14516 | 221 | 1.7 | 14629 | 224 | 1.75 | 14698 | 190 |
| 15 | 20601 | Brunswick - Coburg | 82911 | 1185 | np | 84321 | 1210 | np | 86192 | 1101 | 1.36 | 88035 | 1113 | 1.31 | 89876 | 1151 | 1.26 | 91941 | 1205 | 1.27 | 93081 | 1238 | 1.29 | 94126 | 1057 |

### National aggregate sanity check

- SA2 rows aggregated: **522**

| year | SA2-sum | ABS published | delta | within ±5%? |
|---:|---:|---:|---:|:-:|
| 2011 | 5,537,817 | 297,900 | +5,239,917 (+1759.0%) | ⚠ |
| 2012 | 5,651,091 | 309,600 | +5,341,491 (+1725.3%) | ⚠ |
| 2013 | 5,772,669 | 308,100 | +5,464,569 (+1773.6%) | ⚠ |
| 2014 | 5,894,917 | 299,700 | +5,595,217 (+1866.9%) | ⚠ |
| 2015 | 6,022,322 | 305,400 | +5,716,922 (+1871.9%) | ⚠ |
| 2016 | 6,173,172 | 311,100 | +5,862,072 (+1884.3%) | ⚠ |
| 2017 | 6,302,608 | 309,100 | +5,993,508 (+1939.0%) | ⚠ |
| 2018 | 6,423,038 | 315,100 | +6,107,938 (+1938.4%) | ⚠ |
| 2019 | 6,537,305 | 305,800 | +6,231,505 (+2037.8%) | ⚠ |
| 2020 | 6,615,046 | 294,400 | +6,320,646 (+2147.0%) | ⚠ |
| 2021 | 6,547,822 | 309,900 | +6,237,922 (+2012.9%) | ⚠ |
| 2022 | 6,630,631 | 300,700 | +6,329,931 (+2105.1%) | ⚠ |
| 2023 | 6,816,241 | 286,900 | +6,529,341 (+2275.8%) | ⚠ |
| 2024 | 6,978,719 | 292,500 | +6,686,219 (+2285.9%) | ⚠ |

Tolerance: ±5% vs ABS Cat 3301.0 Table 1.
Misses larger than tolerance suggest column mis-detection or double-counting (state/national rows leaking into SA2 sum).

---

## Sheet: `Table 3`

- max_row: **660**, max_col: **45**
- read first 8 rows for header analysis

### Raw header rows

| row | c1 | c2 | c3 | c4 | c5 | c6 | c7 | c8 | c9 | c10 | c11 | c12 | c13 | c14 | c15 | c16 | c17 | c18 | c19 | c20 | c21 | c22 | c23 | c24 | c25 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | This tab has one table with the estimated resident popula... |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 2 | Australian Bureau of Statistics |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 3 | Table 3: Births, Summary, Statistical Areas Level 2, Quee... |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 4 | Births, Australia, 2024 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 5 | Place of Usual Residence |  | 2011 |  |  | 2012 |  |  | 2013 |  |  | 2014 |  |  | 2015 |  |  | 2016 |  |  | 2017 |  |  | 2018 |  |
| 6 |  |  | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births |
| 7 | 2021 ASGS Code | 2021 GCCSA,SA4,SA3,SA2 | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. |
| 8 | 301011001 | Alexandra Hills | 17308 | 249 | np | 17238 | 227 | np | 17235 | 204 | 1.86 | 17175 | 212 | 1.78 | 17029 | 205 | 1.74 | 16906 | 226 | 1.83 | 16956 | 210 | 1.82 | 16989 | 234 |

### Format detection

- Detected format: **wide** (WIDE per Std 19 vs LONG per Std 26)
- Probable header row: **5**
- Year-like column count: 14
- Year span: 2011 → 2024
- Year columns (0-based, value): 2=2011, 5=2012, 8=2013, 11=2014, 14=2015, 17=2016, 20=2017, 23=2018, 26=2019, 29=2020, 32=2021, 35=2022, 38=2023, 41=2024

### SA2-level row detection

- First row with 9-digit SA2 code: **row 8**

### Sample SA2-level rows (rows 8–15)

| row | c1 | c2 | c3 | c4 | c5 | c6 | c7 | c8 | c9 | c10 | c11 | c12 | c13 | c14 | c15 | c16 | c17 | c18 | c19 | c20 | c21 | c22 | c23 | c24 | c25 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 8 | 301011001 | Alexandra Hills | 17308 | 249 | np | 17238 | 227 | np | 17235 | 204 | 1.86 | 17175 | 212 | 1.78 | 17029 | 205 | 1.74 | 16906 | 226 | 1.83 | 16956 | 210 | 1.82 | 16989 | 234 |
| 9 | 301011002 | Belmont - Gumdale | 7764 | 86 | np | 7770 | 75 | np | 7799 | 76 | 1.7 | 7783 | 71 | 1.63 | 7776 | 72 | 1.65 | 7748 | 83 | 1.73 | 7731 | 80 | 1.81 | 7741 | 62 |
| 10 | 301011003 | Birkdale | 14914 | 180 | np | 15094 | 178 | np | 15235 | 149 | 1.94 | 15307 | 162 | 1.84 | 15367 | 149 | 1.71 | 15394 | 154 | 1.72 | 15599 | 166 | 1.72 | 15603 | 174 |
| 11 | 301011004 | Capalaba | 17557 | 249 | np | 17675 | 253 | np | 17727 | 233 | 2.04 | 17731 | 212 | 1.94 | 18044 | 227 | 1.85 | 18271 | 229 | 1.81 | 18663 | 236 | 1.82 | 18765 | 246 |
| 12 | 301011005 | Thorneside | 3672 | 55 | np | 3709 | 51 | np | 3754 | 53 | 2 | 3841 | 64 | 2.13 | 3827 | 54 | 2.18 | 3884 | 53 | 2.2 | 3901 | 51 | 2.07 | 3931 | 46 |
| 13 | 301011006 | Wellington Point | 11397 | 120 | np | 11657 | 121 | np | 11759 | 110 | 1.78 | 11805 | 95 | 1.65 | 11980 | 130 | 1.73 | 12097 | 110 | 1.75 | 12167 | 121 | 1.9 | 12208 | 101 |
| 14 | 30101 | Capalaba | 72612 | 939 | np | 73143 | 905 | np | 73509 | 825 | 1.9 | 73642 | 816 | 1.81 | 74023 | 837 | 1.77 | 74300 | 855 | 1.79 | 75017 | 864 | 1.81 | 75237 | 863 |
| 15 | 301021007 | Cleveland | 15033 | 121 | np | 15204 | 125 | np | 15365 | 111 | 1.57 | 15467 | 113 | 1.51 | 15248 | 120 | 1.51 | 15344 | 106 | 1.52 | 15558 | 103 | 1.49 | 15751 | 109 |

### National aggregate sanity check

- SA2 rows aggregated: **546**

| year | SA2-sum | ABS published | delta | within ±5%? |
|---:|---:|---:|---:|:-:|
| 2011 | 4,476,778 | 297,900 | +4,178,878 (+1402.8%) | ⚠ |
| 2012 | 4,568,687 | 309,600 | +4,259,087 (+1375.7%) | ⚠ |
| 2013 | 4,652,824 | 308,100 | +4,344,724 (+1410.2%) | ⚠ |
| 2014 | 4,719,653 | 299,700 | +4,419,953 (+1474.8%) | ⚠ |
| 2015 | 4,777,692 | 305,400 | +4,472,292 (+1464.4%) | ⚠ |
| 2016 | 4,845,152 | 311,100 | +4,534,052 (+1457.4%) | ⚠ |
| 2017 | 4,926,380 | 309,100 | +4,617,280 (+1493.8%) | ⚠ |
| 2018 | 5,006,623 | 315,100 | +4,691,523 (+1488.9%) | ⚠ |
| 2019 | 5,088,847 | 305,800 | +4,783,047 (+1564.1%) | ⚠ |
| 2020 | 5,165,613 | 294,400 | +4,871,213 (+1654.6%) | ⚠ |
| 2021 | 5,215,814 | 309,900 | +4,905,914 (+1583.1%) | ⚠ |
| 2022 | 5,320,941 | 300,700 | +5,020,241 (+1669.5%) | ⚠ |
| 2023 | 5,460,477 | 286,900 | +5,173,577 (+1803.3%) | ⚠ |
| 2024 | 5,583,833 | 292,500 | +5,291,333 (+1809.0%) | ⚠ |

Tolerance: ±5% vs ABS Cat 3301.0 Table 1.
Misses larger than tolerance suggest column mis-detection or double-counting (state/national rows leaking into SA2 sum).

---

## Sheet: `Table 4`

- max_row: **245**, max_col: **46**
- read first 8 rows for header analysis

### Raw header rows

| row | c1 | c2 | c3 | c4 | c5 | c6 | c7 | c8 | c9 | c10 | c11 | c12 | c13 | c14 | c15 | c16 | c17 | c18 | c19 | c20 | c21 | c22 | c23 | c24 | c25 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | This tab has one table with the estimated resident popula... |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 2 | Australian Bureau of Statistics |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 3 | Table 4: Births, Summary, Statistical Areas Level 2, Sout... |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 4 | Births, Australia, 2024 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 5 | Place of Usual Residence |  | 2011 |  |  | 2012 |  |  | 2013 |  |  | 2014 |  |  | 2015 |  |  | 2016 |  |  | 2017 |  |  | 2018 |  |
| 6 |  |  | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births |
| 7 | 2021 ASGS Code | 2021 GCCSA,SA4,SA3,SA2 | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. |
| 8 | 401011001 | Adelaide | 13875 | 86 | np | 14423 | 96 | np | 14952 | 85 | 0.77 | 15397 | 81 | 0.75 | 15840 | 106 | 0.72 | 16285 | 103 | 0.73 | 16954 | 92 | 0.73 | 17499 | 99 |

### Format detection

- Detected format: **wide** (WIDE per Std 19 vs LONG per Std 26)
- Probable header row: **5**
- Year-like column count: 14
- Year span: 2011 → 2024
- Year columns (0-based, value): 2=2011, 5=2012, 8=2013, 11=2014, 14=2015, 17=2016, 20=2017, 23=2018, 26=2019, 29=2020, 32=2021, 35=2022, 38=2023, 41=2024

### SA2-level row detection

- First row with 9-digit SA2 code: **row 8**

### Sample SA2-level rows (rows 8–15)

| row | c1 | c2 | c3 | c4 | c5 | c6 | c7 | c8 | c9 | c10 | c11 | c12 | c13 | c14 | c15 | c16 | c17 | c18 | c19 | c20 | c21 | c22 | c23 | c24 | c25 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 8 | 401011001 | Adelaide | 13875 | 86 | np | 14423 | 96 | np | 14952 | 85 | 0.77 | 15397 | 81 | 0.75 | 15840 | 106 | 0.72 | 16285 | 103 | 0.73 | 16954 | 92 | 0.73 | 17499 | 99 |
| 9 | 401011002 | North Adelaide | 7045 | 43 | np | 7114 | 63 | np | 7191 | 50 | 1.04 | 7227 | 58 | 1.15 | 7245 | 39 | 1.02 | 7267 | 39 | 0.95 | 7234 | 36 | 0.78 | 7189 | 46 |
| 10 | 40101 | Adelaide City | 20920 | 129 | np | 21537 | 159 | np | 22143 | 135 | 0.85 | 22624 | 139 | 0.86 | 23085 | 145 | 0.8 | 23552 | 142 | 0.79 | 24188 | 128 | 0.74 | 24688 | 145 |
| 11 | 401021003 | Adelaide Hills | 6973 | 61 | np | 6969 | 47 | np | 6958 | 51 | 1.8 | 6941 | 46 | 1.61 | 6927 | 52 | 1.66 | 6914 | 50 | 1.68 | 6957 | 45 | 1.66 | 7026 | 70 |
| 12 | 401021004 | Aldgate - Stirling | 17869 | 175 | np | 17891 | 168 | np | 17903 | 165 | 1.91 | 17922 | 164 | 1.89 | 17938 | 155 | 1.85 | 17966 | 162 | 1.83 | 18013 | 160 | 1.81 | 18080 | 164 |
| 13 | 401021005 | Hahndorf - Echunga | 4355 | 37 | np | 4382 | 33 | np | 4417 | 40 | 1.87 | 4465 | 30 | 1.76 | 4509 | 38 | 1.83 | 4550 | 42 | 1.87 | 4609 | 34 | 1.87 | 4653 | 43 |
| 14 | 401021006 | Lobethal - Woodside | 9235 | 101 | np | 9207 | 110 | np | 9181 | 110 | 2.15 | 9156 | 122 | 2.37 | 9127 | 83 | 2.22 | 9101 | 103 | 2.21 | 9139 | 83 | 1.96 | 9214 | 88 |
| 15 | 401021007 | Mount Barker | 15228 | 213 | np | 15700 | 215 | np | 16058 | 237 | 2.11 | 16659 | 234 | 2.11 | 17203 | 223 | 2.08 | 17639 | 216 | 1.95 | 18278 | 222 | 1.86 | 19029 | 217 |

### National aggregate sanity check

- SA2 rows aggregated: **174**

| year | SA2-sum | ABS published | delta | within ±5%? |
|---:|---:|---:|---:|:-:|
| 2011 | 1,639,614 | 297,900 | +1,341,714 (+450.4%) | ⚠ |
| 2012 | 1,656,725 | 309,600 | +1,347,125 (+435.1%) | ⚠ |
| 2013 | 1,671,488 | 308,100 | +1,363,388 (+442.5%) | ⚠ |
| 2014 | 1,686,945 | 299,700 | +1,387,245 (+462.9%) | ⚠ |
| 2015 | 1,700,668 | 305,400 | +1,395,268 (+456.9%) | ⚠ |
| 2016 | 1,712,843 | 311,100 | +1,401,743 (+450.6%) | ⚠ |
| 2017 | 1,728,673 | 309,100 | +1,419,573 (+459.3%) | ⚠ |
| 2018 | 1,746,137 | 315,100 | +1,431,037 (+454.2%) | ⚠ |
| 2019 | 1,767,395 | 305,800 | +1,461,595 (+478.0%) | ⚠ |
| 2020 | 1,790,355 | 294,400 | +1,495,955 (+508.1%) | ⚠ |
| 2021 | 1,802,601 | 309,900 | +1,492,701 (+481.7%) | ⚠ |
| 2022 | 1,821,215 | 300,700 | +1,520,515 (+505.7%) | ⚠ |
| 2023 | 1,852,972 | 286,900 | +1,566,072 (+545.9%) | ⚠ |
| 2024 | 1,878,011 | 292,500 | +1,585,511 (+542.1%) | ⚠ |

Tolerance: ±5% vs ABS Cat 3301.0 Table 1.
Misses larger than tolerance suggest column mis-detection or double-counting (state/national rows leaking into SA2 sum).

---

## Sheet: `Table 5`

- max_row: **345**, max_col: **48**
- read first 8 rows for header analysis

### Raw header rows

| row | c1 | c2 | c3 | c4 | c5 | c6 | c7 | c8 | c9 | c10 | c11 | c12 | c13 | c14 | c15 | c16 | c17 | c18 | c19 | c20 | c21 | c22 | c23 | c24 | c25 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | This tab has one table with the estimated resident popula... |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 2 | Australian Bureau of Statistics |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 3 | Table 5: Births, Summary, Statistical Areas Level 2, West... |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 4 | Births, Australia, 2024 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 5 | Place of Usual Residence |  | 2011 |  |  | 2012 |  |  | 2013 |  |  | 2014 |  |  | 2015 |  |  | 2016 |  |  | 2017 |  |  | 2018 |  |
| 6 |  |  | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births |
| 7 | 2021 ASGS Code | 2021 GCCSA,SA4,SA3,SA2 | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. |
| 8 | 502011021 | Dawesville - Bouvard | 5815 | 84 | np | 6192 | 79 | np | 6489 | 63 | 2.25 | 6743 | 80 | 2.1 | 7034 | 87 | 2.08 | 7337 | 71 | 2.07 | 7554 | 79 | 1.99 | 7910 | 68 |

### Format detection

- Detected format: **wide** (WIDE per Std 19 vs LONG per Std 26)
- Probable header row: **5**
- Year-like column count: 14
- Year span: 2011 → 2024
- Year columns (0-based, value): 2=2011, 5=2012, 8=2013, 11=2014, 14=2015, 17=2016, 20=2017, 23=2018, 26=2019, 29=2020, 32=2021, 35=2022, 38=2023, 41=2024

### SA2-level row detection

- First row with 9-digit SA2 code: **row 8**

### Sample SA2-level rows (rows 8–15)

| row | c1 | c2 | c3 | c4 | c5 | c6 | c7 | c8 | c9 | c10 | c11 | c12 | c13 | c14 | c15 | c16 | c17 | c18 | c19 | c20 | c21 | c22 | c23 | c24 | c25 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 8 | 502011021 | Dawesville - Bouvard | 5815 | 84 | np | 6192 | 79 | np | 6489 | 63 | 2.25 | 6743 | 80 | 2.1 | 7034 | 87 | 2.08 | 7337 | 71 | 2.07 | 7554 | 79 | 1.99 | 7910 | 68 |
| 9 | 502011022 | Falcon - Wannanup | 7812 | 79 | np | 8297 | 98 | np | 8769 | 87 | 1.98 | 8876 | 128 | 2.21 | 8975 | 85 | 2.04 | 9060 | 98 | 2.13 | 9247 | 95 | 1.94 | 9308 | 90 |
| 10 | 502011023 | Greenfields | 10400 | 133 | np | 10323 | 138 | np | 10266 | 154 | 2.24 | 10211 | 136 | 2.28 | 10182 | 119 | 2.21 | 10139 | 119 | 2.07 | 10082 | 123 | 2.04 | 10025 | 101 |
| 11 | 502011024 | Halls Head - Erskine | 18047 | 200 | np | 18487 | 192 | np | 18816 | 186 | 1.94 | 19002 | 210 | 1.91 | 19092 | 199 | 1.92 | 19145 | 194 | 1.99 | 19349 | 189 | 1.96 | 19584 | 176 |
| 12 | 502011025 | Mandurah | 9065 | 109 | np | 9237 | 140 | np | 9373 | 116 | 2.2 | 9459 | 156 | 2.41 | 9502 | 108 | 2.2 | 9491 | 103 | 2.14 | 9537 | 120 | 1.93 | 9708 | 110 |
| 13 | 502011026 | Mandurah - East | 5150 | 51 | np | 5312 | 49 | np | 5513 | 43 | 2.07 | 5703 | 37 | 1.79 | 5868 | 53 | 1.71 | 6019 | 63 | 1.84 | 6177 | 56 | 1.97 | 6358 | 65 |
| 14 | 502011027 | Mandurah - North | 13071 | 180 | np | 14528 | 207 | np | 15795 | 236 | 2.05 | 16803 | 245 | 2.04 | 17556 | 260 | 2.04 | 18251 | 279 | 2.05 | 19005 | 313 | 2.13 | 19797 | 301 |
| 15 | 502011028 | Mandurah - South | 9735 | 114 | np | 10052 | 132 | np | 10338 | 109 | 2.23 | 10361 | 108 | 2.14 | 10394 | 107 | 1.96 | 10397 | 118 | 2.06 | 10627 | 105 | 2.06 | 10865 | 111 |

### National aggregate sanity check

- SA2 rows aggregated: **265**

| year | SA2-sum | ABS published | delta | within ±5%? |
|---:|---:|---:|---:|:-:|
| 2011 | 2,353,409 | 297,900 | +2,055,509 (+690.0%) | ⚠ |
| 2012 | 2,425,507 | 309,600 | +2,115,907 (+683.4%) | ⚠ |
| 2013 | 2,486,944 | 308,100 | +2,178,844 (+707.2%) | ⚠ |
| 2014 | 2,517,608 | 299,700 | +2,217,908 (+740.0%) | ⚠ |
| 2015 | 2,540,672 | 305,400 | +2,235,272 (+731.9%) | ⚠ |
| 2016 | 2,555,978 | 311,100 | +2,244,878 (+721.6%) | ⚠ |
| 2017 | 2,585,720 | 309,100 | +2,276,620 (+736.5%) | ⚠ |
| 2018 | 2,617,792 | 315,100 | +2,302,692 (+730.8%) | ⚠ |
| 2019 | 2,659,625 | 305,800 | +2,353,825 (+769.7%) | ⚠ |
| 2020 | 2,712,912 | 294,400 | +2,418,512 (+821.5%) | ⚠ |
| 2021 | 2,749,365 | 309,900 | +2,439,465 (+787.2%) | ⚠ |
| 2022 | 2,791,794 | 300,700 | +2,491,094 (+828.4%) | ⚠ |
| 2023 | 2,883,762 | 286,900 | +2,596,862 (+905.1%) | ⚠ |
| 2024 | 2,965,078 | 292,500 | +2,672,578 (+913.7%) | ⚠ |

Tolerance: ±5% vs ABS Cat 3301.0 Table 1.
Misses larger than tolerance suggest column mis-detection or double-counting (state/national rows leaking into SA2 sum).

---

## Sheet: `Table 6`

- max_row: **154**, max_col: **52**
- read first 8 rows for header analysis

### Raw header rows

| row | c1 | c2 | c3 | c4 | c5 | c6 | c7 | c8 | c9 | c10 | c11 | c12 | c13 | c14 | c15 | c16 | c17 | c18 | c19 | c20 | c21 | c22 | c23 | c24 | c25 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | This tab has one table with the estimated resident popula... |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 2 | Australian Bureau of Statistics |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 3 | Table 6: Births, Summary, Statistical Areas Level 2, Tasm... |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 4 | Births, Australia, 2024 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 5 | Place of Usual Residence |  | 2011 |  |  | 2012 |  |  | 2013 |  |  | 2014 |  |  | 2015 |  |  | 2016 |  |  | 2017 |  |  | 2018 |  |
| 6 |  |  | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births |
| 7 | 2021 ASGS Code | 2021 GCCSA,SA4,SA3,SA2 | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. |
| 8 | 601011001 | Bridgewater - Gagebrook | 7616 | 190 | np | 7573 | 166 | np | 7517 | 150 | 2.91 | 7465 | 152 | 2.79 | 7413 | 144 | 2.72 | 7362 | 133 | 2.65 | 7453 | 153 | 2.63 | 7576 | 124 |

### Format detection

- Detected format: **wide** (WIDE per Std 19 vs LONG per Std 26)
- Probable header row: **5**
- Year-like column count: 14
- Year span: 2011 → 2024
- Year columns (0-based, value): 2=2011, 5=2012, 8=2013, 11=2014, 14=2015, 17=2016, 20=2017, 23=2018, 26=2019, 29=2020, 32=2021, 35=2022, 38=2023, 41=2024

### SA2-level row detection

- First row with 9-digit SA2 code: **row 8**

### Sample SA2-level rows (rows 8–15)

| row | c1 | c2 | c3 | c4 | c5 | c6 | c7 | c8 | c9 | c10 | c11 | c12 | c13 | c14 | c15 | c16 | c17 | c18 | c19 | c20 | c21 | c22 | c23 | c24 | c25 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 8 | 601011001 | Bridgewater - Gagebrook | 7616 | 190 | np | 7573 | 166 | np | 7517 | 150 | 2.91 | 7465 | 152 | 2.79 | 7413 | 144 | 2.72 | 7362 | 133 | 2.65 | 7453 | 153 | 2.63 | 7576 | 124 |
| 9 | 601011002 | Brighton - Pontville | 4842 | 70 | np | 4986 | 62 | np | 5076 | 82 | 2.06 | 5194 | 69 | 2 | 5345 | 89 | 2.2 | 5492 | 88 | 2.18 | 5657 | 70 | 2.12 | 5840 | 82 |
| 10 | 601011003 | Old Beach - Otago | 3794 | 54 | np | 3904 | 56 | np | 4005 | 50 | 2.21 | 4106 | 51 | 2.12 | 4235 | 70 | 2.2 | 4373 | 66 | 2.29 | 4511 | 54 | 2.23 | 4671 | 68 |
| 11 | 60101 | Brighton | 16252 | 314 | np | 16463 | 284 | np | 16598 | 282 | 2.54 | 16765 | 272 | 2.41 | 16993 | 303 | 2.45 | 17227 | 287 | 2.43 | 17621 | 277 | 2.4 | 18087 | 274 |
| 12 | 601021004 | Bellerive - Rosny | 5964 | 57 | np | 5972 | 56 | np | 5979 | 55 | 1.75 | 5990 | 62 | 1.78 | 5995 | 52 | 1.74 | 6007 | 50 | 1.68 | 6121 | 53 | 1.55 | 6282 | 52 |
| 13 | 601021005 | Cambridge | 7348 | 96 | np | 7424 | 78 | np | 7534 | 80 | 2.25 | 7622 | 83 | 2.09 | 7683 | 59 | 1.94 | 7761 | 71 | 1.85 | 7875 | 78 | 1.8 | 8014 | 76 |
| 14 | 601021006 | Geilston Bay - Risdon | 3232 | 47 | np | 3237 | 41 | np | 3245 | 37 | 2.16 | 3252 | 49 | 2.17 | 3253 | 45 | 2.22 | 3255 | 50 | 2.39 | 3291 | 33 | 2.08 | 3331 | 39 |
| 15 | 601021007 | Howrah - Tranmere | 9809 | 125 | np | 9974 | 111 | np | 10112 | 105 | 2.04 | 10293 | 94 | 1.83 | 10454 | 103 | 1.78 | 10565 | 109 | 1.77 | 10793 | 103 | 1.8 | 11054 | 110 |

### National aggregate sanity check

- SA2 rows aggregated: **99**

| year | SA2-sum | ABS published | delta | within ±5%? |
|---:|---:|---:|---:|:-:|
| 2011 | 511,483 | 297,900 | +213,583 (+71.7%) | ⚠ |
| 2012 | 511,724 | 309,600 | +202,124 (+65.3%) | ⚠ |
| 2013 | 512,231 | 308,100 | +204,131 (+66.3%) | ⚠ |
| 2014 | 513,621 | 299,700 | +213,921 (+71.4%) | ⚠ |
| 2015 | 515,117 | 305,400 | +209,717 (+68.7%) | ⚠ |
| 2016 | 517,514 | 311,100 | +206,414 (+66.3%) | ⚠ |
| 2017 | 526,762 | 309,100 | +217,662 (+70.4%) | ⚠ |
| 2018 | 537,291 | 315,100 | +222,191 (+70.5%) | ⚠ |
| 2019 | 547,841 | 305,800 | +242,041 (+79.2%) | ⚠ |
| 2020 | 557,578 | 294,400 | +263,178 (+89.4%) | ⚠ |
| 2021 | 567,239 | 309,900 | +257,339 (+83.0%) | ⚠ |
| 2022 | 571,051 | 300,700 | +270,351 (+89.9%) | ⚠ |
| 2023 | 573,738 | 286,900 | +286,838 (+100.0%) | ⚠ |
| 2024 | 575,496 | 292,500 | +282,996 (+96.8%) | ⚠ |

Tolerance: ±5% vs ABS Cat 3301.0 Table 1.
Misses larger than tolerance suggest column mis-detection or double-counting (state/national rows leaking into SA2 sum).

---

## Sheet: `Table 7`

- max_row: **92**, max_col: **51**
- read first 8 rows for header analysis

### Raw header rows

| row | c1 | c2 | c3 | c4 | c5 | c6 | c7 | c8 | c9 | c10 | c11 | c12 | c13 | c14 | c15 | c16 | c17 | c18 | c19 | c20 | c21 | c22 | c23 | c24 | c25 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | This tab has one table with the estimated resident popula... |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 2 | Australian Bureau of Statistics |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 3 | Table 7: Births, Summary, Statistical Areas Level 2, Nort... |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 4 | Births, Australia, 2024 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 5 | Place of Usual Residence |  | 2011 |  |  | 2012 |  |  | 2013 |  |  | 2014 |  |  | 2015 |  |  | 2016 |  |  | 2017 |  |  | 2018 |  |
| 6 |  |  | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births |
| 7 | 2021 ASGS Code | 2021 GCCSA,SA4,SA3,SA2 | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. |
| 8 | 701011001 | Darwin Airport | 469 | 3 | np | 469 | 5 | np | 466 | 48 | np | 18 | 3 | np | 17 | 0 | np | 16 | 0 | np | 17 | 0 | np | 18 | 0 |

### Format detection

- Detected format: **wide** (WIDE per Std 19 vs LONG per Std 26)
- Probable header row: **5**
- Year-like column count: 14
- Year span: 2011 → 2024
- Year columns (0-based, value): 2=2011, 5=2012, 8=2013, 11=2014, 14=2015, 17=2016, 20=2017, 23=2018, 26=2019, 29=2020, 32=2021, 35=2022, 38=2023, 41=2024

### SA2-level row detection

- First row with 9-digit SA2 code: **row 8**

### Sample SA2-level rows (rows 8–15)

| row | c1 | c2 | c3 | c4 | c5 | c6 | c7 | c8 | c9 | c10 | c11 | c12 | c13 | c14 | c15 | c16 | c17 | c18 | c19 | c20 | c21 | c22 | c23 | c24 | c25 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 8 | 701011001 | Darwin Airport | 469 | 3 | np | 469 | 5 | np | 466 | 48 | np | 18 | 3 | np | 17 | 0 | np | 16 | 0 | np | 17 | 0 | np | 18 | 0 |
| 9 | 701011002 | Darwin City | 5053 | 51 | np | 5412 | 58 | np | 5862 | 60 | 0.98 | 6288 | 49 | 0.93 | 7056 | 73 | 0.88 | 7591 | 83 | 0.85 | 7917 | 100 | 0.93 | 7786 | 72 |
| 10 | 701011003 | East Point | 44 | 0 | np | 38 | 0 | np | 32 | 0 | np | 26 | 0 | np | 20 | 0 | np | 14 | 0 | np | 11 | 0 | np | 8 | 0 |
| 11 | 701011004 | Fannie Bay - The Gardens | 3518 | 36 | np | 3606 | 42 | np | 3687 | 41 | 1.41 | 3679 | 47 | 1.5 | 3667 | 50 | 1.55 | 3640 | 44 | 1.55 | 3713 | 48 | 1.5 | 3720 | 52 |
| 12 | 701011005 | Larrakeyah | 3501 | 38 | np | 3653 | 43 | np | 3784 | 43 | 1.3 | 3919 | 50 | 1.32 | 3954 | 59 | 1.4 | 4019 | 66 | 1.53 | 4109 | 54 | 1.52 | 4056 | 44 |
| 13 | 701011006 | Ludmilla - The Narrows | 3102 | 59 | np | 3040 | 51 | np | 3020 | 65 | 2.34 | 2938 | 37 | 2.12 | 2837 | 34 | 1.94 | 2746 | 48 | 1.82 | 2709 | 35 | 1.82 | 2681 | 38 |
| 14 | 701011007 | Parap | 2138 | 20 | np | 2302 | 32 | np | 2495 | 40 | 1.35 | 2644 | 51 | 1.66 | 2844 | 34 | 1.6 | 3007 | 31 | 1.41 | 3113 | 37 | 1.19 | 3100 | 34 |
| 15 | 701011008 | Stuart Park | 4091 | 51 | np | 4240 | 72 | np | 4372 | 71 | 1.47 | 4447 | 59 | 1.46 | 4495 | 54 | 1.29 | 4517 | 68 | 1.25 | 4519 | 74 | 1.34 | 4398 | 54 |

### National aggregate sanity check

- SA2 rows aggregated: **68**

| year | SA2-sum | ABS published | delta | within ±5%? |
|---:|---:|---:|---:|:-:|
| 2011 | 231,292 | 297,900 | -66,608 (-22.4%) | ⚠ |
| 2012 | 235,915 | 309,600 | -73,685 (-23.8%) | ⚠ |
| 2013 | 241,722 | 308,100 | -66,378 (-21.5%) | ⚠ |
| 2014 | 242,894 | 299,700 | -56,806 (-19.0%) | ⚠ |
| 2015 | 244,692 | 305,400 | -60,708 (-19.9%) | ⚠ |
| 2016 | 245,678 | 311,100 | -65,422 (-21.0%) | ⚠ |
| 2017 | 247,412 | 309,100 | -61,688 (-20.0%) | ⚠ |
| 2018 | 247,095 | 315,100 | -68,005 (-21.6%) | ⚠ |
| 2019 | 246,559 | 305,800 | -59,241 (-19.4%) | ⚠ |
| 2020 | 247,428 | 294,400 | -46,972 (-16.0%) | ⚠ |
| 2021 | 248,151 | 309,900 | -61,749 (-19.9%) | ⚠ |
| 2022 | 250,228 | 300,700 | -50,472 (-16.8%) | ⚠ |
| 2023 | 253,062 | 286,900 | -33,838 (-11.8%) | ⚠ |
| 2024 | 255,069 | 292,500 | -37,431 (-12.8%) | ⚠ |

Tolerance: ±5% vs ABS Cat 3301.0 Table 1.
Misses larger than tolerance suggest column mis-detection or double-counting (state/national rows leaking into SA2 sum).

---

## Sheet: `Table 8`

- max_row: **236**, max_col: **52**
- read first 8 rows for header analysis

### Raw header rows

| row | c1 | c2 | c3 | c4 | c5 | c6 | c7 | c8 | c9 | c10 | c11 | c12 | c13 | c14 | c15 | c16 | c17 | c18 | c19 | c20 | c21 | c22 | c23 | c24 | c25 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | This tab has one table with the estimated resident popula... |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 2 | Australian Bureau of Statistics |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 3 | Table 8: Births, Summary, Statistical Areas Level 2, Aust... |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 4 | Births, Australia, 2024 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 5 | Place of Usual Residence |  | 2011 |  |  | 2012 |  |  | 2013 |  |  | 2014 |  |  | 2015 |  |  | 2016 |  |  | 2017 |  |  | 2018 |  |
| 6 |  |  | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births | Total fertility rate | Estimated resident population | Births |
| 7 | 2021 ASGS Code | 2021 GCCSA,SA4,SA3,SA2 | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. | rate | persons | no. |
| 8 | 801011001 | Aranda | 2554 | 32 | np | 2532 | 29 | np | 2498 | 22 | 1.92 | 2477 | 22 | 1.66 | 2460 | 28 | 1.65 | 2447 | 16 | 1.56 | 2485 | 21 | 1.57 | 2502 | 21 |

### Format detection

- Detected format: **wide** (WIDE per Std 19 vs LONG per Std 26)
- Probable header row: **5**
- Year-like column count: 14
- Year span: 2011 → 2024
- Year columns (0-based, value): 2=2011, 5=2012, 8=2013, 11=2014, 14=2015, 17=2016, 20=2017, 23=2018, 26=2019, 29=2020, 32=2021, 35=2022, 38=2023, 41=2024

### SA2-level row detection

- First row with 9-digit SA2 code: **row 8**

### Sample SA2-level rows (rows 8–15)

| row | c1 | c2 | c3 | c4 | c5 | c6 | c7 | c8 | c9 | c10 | c11 | c12 | c13 | c14 | c15 | c16 | c17 | c18 | c19 | c20 | c21 | c22 | c23 | c24 | c25 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 8 | 801011001 | Aranda | 2554 | 32 | np | 2532 | 29 | np | 2498 | 22 | 1.92 | 2477 | 22 | 1.66 | 2460 | 28 | 1.65 | 2447 | 16 | 1.56 | 2485 | 21 | 1.57 | 2502 | 21 |
| 9 | 801011002 | Belconnen | 4667 | 57 | np | 5275 | 90 | np | 5979 | 93 | 1.28 | 6332 | 96 | 1.36 | 6529 | 103 | 1.27 | 6743 | 97 | 1.24 | 7331 | 114 | 1.22 | 7882 | 98 |
| 10 | 801011003 | Bruce | 6751 | 69 | np | 6869 | 81 | np | 6941 | 89 | 1.37 | 7010 | 83 | 1.41 | 7071 | 88 | 1.43 | 7147 | 67 | 1.2 | 7415 | 110 | 1.28 | 7653 | 74 |
| 11 | 801011004 | Charnwood | 3157 | 54 | np | 3138 | 72 | np | 3106 | 52 | 2.19 | 3074 | 57 | 2.31 | 3039 | 45 | 2.06 | 3004 | 43 | 2.06 | 2989 | 47 | 1.94 | 2959 | 45 |
| 12 | 801011005 | Cook | 3027 | 47 | np | 3008 | 35 | np | 2984 | 35 | 1.56 | 2949 | 32 | 1.43 | 2919 | 34 | 1.51 | 2902 | 23 | 1.36 | 2902 | 45 | 1.57 | 2888 | 36 |
| 13 | 801011006 | Dunlop | 7268 | 162 | np | 7279 | 142 | np | 7278 | 165 | 2.36 | 7273 | 131 | 2.27 | 7258 | 120 | 2.25 | 7253 | 125 | 2.15 | 7275 | 111 | 2.13 | 7243 | 100 |
| 14 | 801011007 | Evatt | 5584 | 83 | np | 5555 | 83 | np | 5472 | 70 | 1.88 | 5379 | 83 | 1.89 | 5354 | 70 | 1.81 | 5366 | 79 | 1.95 | 5435 | 83 | 1.99 | 5479 | 61 |
| 15 | 801011008 | Florey | 5241 | 67 | np | 5197 | 63 | np | 5147 | 75 | 1.78 | 5065 | 59 | 1.74 | 4971 | 68 | 1.82 | 4893 | 41 | 1.57 | 4856 | 64 | 1.65 | 4836 | 52 |

### National aggregate sanity check

- SA2 rows aggregated: **134**

| year | SA2-sum | ABS published | delta | within ±5%? |
|---:|---:|---:|---:|:-:|
| 2011 | 367,985 | 297,900 | +70,085 (+23.5%) | ⚠ |
| 2012 | 376,539 | 309,600 | +66,939 (+21.6%) | ⚠ |
| 2013 | 383,257 | 308,100 | +75,157 (+24.4%) | ⚠ |
| 2014 | 388,799 | 299,700 | +89,099 (+29.7%) | ⚠ |
| 2015 | 395,813 | 305,400 | +90,413 (+29.6%) | ⚠ |
| 2016 | 403,104 | 311,100 | +92,004 (+29.6%) | ⚠ |
| 2017 | 415,046 | 309,100 | +105,946 (+34.3%) | ⚠ |
| 2018 | 426,081 | 315,100 | +110,981 (+35.2%) | ⚠ |
| 2019 | 435,730 | 305,800 | +129,930 (+42.5%) | ⚠ |
| 2020 | 444,903 | 294,400 | +150,503 (+51.1%) | ⚠ |
| 2021 | 452,508 | 309,900 | +142,608 (+46.0%) | ⚠ |
| 2022 | 456,915 | 300,700 | +156,215 (+52.0%) | ⚠ |
| 2023 | 466,359 | 286,900 | +179,459 (+62.6%) | ⚠ |
| 2024 | 473,855 | 292,500 | +181,355 (+62.0%) | ⚠ |

Tolerance: ±5% vs ABS Cat 3301.0 Table 1.
Misses larger than tolerance suggest column mis-detection or double-counting (state/national rows leaking into SA2 sum).

---

## Sheet: `Further information`

- max_row: **15**, max_col: **8**
- read first 8 rows for header analysis

### Raw header rows

| row | c1 | c2 | c3 | c4 | c5 | c6 | c7 | c8 |
|---|---|---|---|---|---|---|---|---|
| 1 | This tab contains relevant methodology information and li... |  |  |  |  |  |  |  |
| 2 | Australian Bureau of Statistics |  |  |  |  |  |  |  |
| 3 | Further information |  |  |  |  |  |  |  |
| 4 | Births, Australia 2024 |  |  |  |  |  |  |  |
| 5 | For more detail |  |  |  |  |  |  |  |
| 6 | This data comes from Births, Australia 2024 |  |  |  |  |  |  |  |
| 7 | Visit Births, Australia Methodology to understand more ab... |  |  |  |  |  |  |  |
| 8 | Explanatory Notes |  |  |  |  |  |  |  |

### Format detection

- Detected format: **unknown** (WIDE per Std 19 vs LONG per Std 26)

### SA2-level row detection

- (No 9-digit SA2 code found in first 200 rows)
---

## Recommended apply phase

**Target table** (proposed):

```sql
CREATE TABLE abs_sa2_births_annual (
  sa2_code     TEXT NOT NULL,
  year         INTEGER NOT NULL,
  births_count INTEGER,
  PRIMARY KEY (sa2_code, year)
);
CREATE INDEX idx_abs_sa2_births_annual_sa2  ON abs_sa2_births_annual(sa2_code);
CREATE INDEX idx_abs_sa2_births_annual_year ON abs_sa2_births_annual(year);
```

**Audit log row** (action='abs_sa2_births_ingest_v1', subject_type='abs_sa2_births_annual').

**Backup**: `data/kintell.db.backup_pre_step8_<ts>` before mutation (Std 8).

**Invariants** (apply phase):

- distinct SA2 count between 2,000 and 2,500
- year coverage 2011-2024 (or whatever the workbook contains)
- per-year national sum within ±5% of ABS Cat 3301.0 Table 1
- no births_count < 0; no SA2 codes outside abs_sa2_erp_annual

---
End of diagnostic.