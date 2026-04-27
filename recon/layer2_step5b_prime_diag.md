# Layer 2 Step 5b-prime — Diagnostic v4 (multi-year)

**Workbook:** `abs_data\Education and employment database.xlsx`  
**Generated:** 2026-04-27T19:42:58

Long-format workbook (Code | Label | Year | metric cols).
Samples drawn from SA2-level rows for **every available year** so
Census-only metrics (publish 2011/2016/2021 only) are visible.

## Sheet: `Table 1` (kind: sa2)

- max_row: 26195, max_col: 93
- geography breakdown: {'AUS': 9, 'STATE': 81, 'GCCSA': 144, 'SA4': 801, 'SA3': 3060, 'SA2': 22086, 'OTHER': 7}
- years seen: [2011, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]
- SA2 rows (total): 22086

### Summary — one row per candidate column

| Col | Letter | Group (row 6) | Metric (row 7) | Matched | Cadence | Overall kind | Years w/ data |
|----:|:-------|:--------------|:---------------|:--------|:--------|:-------------|:--------------|
| 4 | D | Children enrolled in a preschool or preschool  | 4 year olds enrolled in preschool or preschool | preschool | annual | ambiguous | 2018,2019,2020,2021,2022,2023 |
| 5 | E |  | 5 year olds enrolled in preschool or preschool | preschool | annual | pct_or_small_count_AMBIG | 2018,2019,2020,2021,2022,2023 |
| 6 | F |  | Children enrolled in preschool (no.) | preschool | annual | pct_or_small_count_AMBIG | 2018,2019,2020,2021,2022,2023 |
| 7 | G |  | Children enrolled in preschool program within  | preschool | annual | ambiguous | 2018,2019,2020,2021,2022,2023 |
| 8 | H |  | Children enrolled across more than one provide | preschool | annual | pct_or_small_count_AMBIG | 2018,2019,2020,2021,2022,2023 |
| 9 | I |  | Children enrolled in a preschool or preschool  | preschool | annual | ambiguous | 2018,2019,2020,2021,2022,2023 |
| 10 | J | Children attending a preschool or preschool pr | Children attending preschool for less than 15  | preschool | annual | pct_or_small_count_AMBIG | 2018,2019,2020,2022,2023 |
| 11 | K |  | Children attending preschool for 15 hours or m | preschool | annual | ambiguous | 2018,2019,2020,2022,2023 |
| 12 | L | Highest year of school completed - Persons age | Completed year 12 or equivalent (%) | educational_attain | census | pct_likely | 2011,2016,2021 |
| 19 | S | Non-school qualifications - Persons aged 15 ye | Total persons with non-school qualification(s) | educational_attain | census | pct_likely | 2011,2016,2021 |
| 20 | T |  | Postgraduate degree (%) | educational_attain | census | pct_likely | 2011,2016,2021 |
| 21 | U |  | Graduate diploma/graduate certificate (%) | educational_attain | census | pct_likely | 2011,2016,2021 |
| 22 | V |  | Bachelor degree (%) | educational_attain | census | pct_likely | 2011,2016,2021 |
| 23 | W |  | Advanced diploma/diploma (%) | educational_attain | census | pct_likely | 2011,2016,2021 |
| 24 | X |  | Certificate (%) | educational_attain | census | pct_likely | 2011,2016,2021 |
| 25 | Y |  | Non-school qualification inadequately describe | educational_attain | census | pct_likely | 2011,2016,2021 |
| 26 | Z |  | Non-school qualification not stated (%) | educational_attain | census | pct_likely | 2011,2016,2021 |
| 27 | AA | Non-school qualification: field of study - Per | Natural and physical sciences (%) | educational_attain | census | pct_likely | 2011,2016,2021 |
| 51 | AY | Labour force status - Persons aged 15 years an | Employed (no.) | employment | census | count_likely | 2011,2016,2021 |
| 52 | AZ |  | Unemployed (no.) | employment,unemployment | census | ambiguous | 2011,2016,2021 |
| 54 | BB |  | Unemployment rate (%) | employment,unemployment | census | pct_likely | 2011,2016,2021 |
| 55 | BC |  | Participation rate (%) | labour_force_partic | census | pct_likely | 2011,2016,2021 |
| 60 | BH | Jobs in Australia - year ended 30 June | Number of jobs held by females | female,male | annual | count_likely | 2018,2019,2020,2021,2022 |
| 61 | BI |  | Number of jobs held by males | male | annual | count_likely | 2018,2019,2020,2021,2022 |
| 83 | CE | Occupation of employed persons - Persons aged  | Managers (%) | occupation,employment | census | pct_likely | 2011,2016,2021 |
| 91 | CM |  | Occupation inadequately described or not state | occupation | census | pct_likely | 2011,2016,2021 |

### Detail — per-year classification (n > 0 only)

| Col | Letter | Metric | Year | n | Kind | Mean | Min | Max | Sample |
|----:|:-------|:-------|-----:|--:|:-----|-----:|----:|----:|:-------|
| 4 | D | 4 year olds enrolled in preschool or presc | 2018 | 12 | ambiguous | 78.5 | 22 | 205 | 41, 90, 118, 46 |
| 4 | D | 4 year olds enrolled in preschool or presc | 2019 | 12 | ambiguous | 80.25 | 21 | 219 | 52, 82, 110, 52 |
| 4 | D | 4 year olds enrolled in preschool or presc | 2020 | 12 | ambiguous | 81.25 | 18 | 245 | 44, 82, 113, 54 |
| 4 | D | 4 year olds enrolled in preschool or presc | 2021 | 11 | ambiguous | 89.55 | 29 | 274 | 54, 79, 98, 54 |
| 4 | D | 4 year olds enrolled in preschool or presc | 2022 | 11 | ambiguous | 97.82 | 35 | 329 | 40, 86, 103, 50 |
| 4 | D | 4 year olds enrolled in preschool or presc | 2023 | 11 | ambiguous | 93.0 | 39 | 179 | 39, 92, 102, 56 |
| 5 | E | 5 year olds enrolled in preschool or presc | 2018 | 12 | pct_or_small_count_AMBIG | 21.75 | 5 | 58 | 6, 24, 19, 9 |
| 5 | E | 5 year olds enrolled in preschool or presc | 2019 | 12 | pct_or_small_count_AMBIG | 29.92 | 4 | 81 | 11, 31, 35, 13 |
| 5 | E | 5 year olds enrolled in preschool or presc | 2020 | 12 | pct_or_small_count_AMBIG | 28.42 | 7 | 69 | 15, 27, 41, 16 |
| 5 | E | 5 year olds enrolled in preschool or presc | 2021 | 11 | ambiguous | 32.55 | 9 | 113 | 9, 22, 28, 12 |
| 5 | E | 5 year olds enrolled in preschool or presc | 2022 | 11 | ambiguous | 28.82 | 10 | 106 | 16, 22, 28, 13 |
| 5 | E | 5 year olds enrolled in preschool or presc | 2023 | 11 | pct_or_small_count_AMBIG | 31.09 | 8 | 68 | 12, 20, 26, 8 |
| 6 | F | Children enrolled in preschool (no.) | 2018 | 12 | pct_or_small_count_AMBIG | 40.58 | 9 | 92 | 38, 42, 58, 21 |
| 6 | F | Children enrolled in preschool (no.) | 2019 | 12 | pct_or_small_count_AMBIG | 43.0 | 7 | 100 | 52, 50, 50, 26 |
| 6 | F | Children enrolled in preschool (no.) | 2020 | 12 | pct_or_small_count_AMBIG | 40.08 | 9 | 94 | 44, 38, 62, 37 |
| 6 | F | Children enrolled in preschool (no.) | 2021 | 11 | ambiguous | 43.73 | 11 | 103 | 39, 33, 49, 19 |
| 6 | F | Children enrolled in preschool (no.) | 2022 | 11 | ambiguous | 47.45 | 14 | 144 | 43, 43, 52, 24 |
| 6 | F | Children enrolled in preschool (no.) | 2023 | 10 | pct_or_small_count_AMBIG | 47.7 | 26 | 80 | 35, 42, 54, 26 |
| 7 | G | Children enrolled in preschool program wit | 2018 | 12 | ambiguous | 45.92 | 3 | 148 | 6, 54, 53, 22 |
| 7 | G | Children enrolled in preschool program wit | 2019 | 11 | ambiguous | 56.64 | 8 | 167 | 9, 45, 82, 22 |
| 7 | G | Children enrolled in preschool program wit | 2020 | 12 | ambiguous | 55.0 | 3 | 185 | 8, 48, 76, 29 |
| 7 | G | Children enrolled in preschool program wit | 2021 | 11 | ambiguous | 61.36 | 10 | 228 | 10, 46, 54, 38 |
| 7 | G | Children enrolled in preschool program wit | 2022 | 11 | ambiguous | 57.27 | 10 | 215 | 10, 39, 53, 29 |
| 7 | G | Children enrolled in preschool program wit | 2023 | 11 | ambiguous | 58.82 | 8 | 147 | 8, 51, 45, 36 |
| 8 | H | Children enrolled across more than one pro | 2018 | 12 | pct_or_small_count_AMBIG | 12.75 | 3 | 35 | 3, 20, 21, 5 |
| 8 | H | Children enrolled across more than one pro | 2019 | 12 | pct_or_small_count_AMBIG | 13.75 | 3 | 31 | 5, 15, 16, 12 |
| 8 | H | Children enrolled across more than one pro | 2020 | 12 | pct_or_small_count_AMBIG | 14.25 | 4 | 36 | 5, 20, 17, 7 |
| 8 | H | Children enrolled across more than one pro | 2021 | 11 | pct_or_small_count_AMBIG | 17.09 | 3 | 56 | 13, 14, 23, 9 |
| 8 | H | Children enrolled across more than one pro | 2022 | 11 | pct_or_small_count_AMBIG | 22.27 | 8 | 73 | 8, 24, 22, 13 |
| 8 | H | Children enrolled across more than one pro | 2023 | 10 | pct_or_small_count_AMBIG | 24.1 | 5 | 49 | 5, 18, 25, 5 |
| 9 | I | Children enrolled in a preschool or presch | 2018 | 12 | ambiguous | 100.5 | 28 | 257 | 49, 109, 138, 56 |
| 9 | I | Children enrolled in a preschool or presch | 2019 | 12 | ambiguous | 108.83 | 25 | 298 | 66, 107, 148, 58 |
| 9 | I | Children enrolled in a preschool or presch | 2020 | 12 | ambiguous | 108.75 | 33 | 316 | 58, 102, 152, 70 |
| 9 | I | Children enrolled in a preschool or presch | 2021 | 11 | ambiguous | 123.36 | 42 | 390 | 63, 102, 128, 66 |
| 9 | I | Children enrolled in a preschool or presch | 2022 | 11 | ambiguous | 127.45 | 47 | 437 | 57, 105, 127, 70 |
| 9 | I | Children enrolled in a preschool or presch | 2023 | 11 | ambiguous | 123.55 | 49 | 234 | 49, 105, 128, 65 |
| 10 | J | Children attending preschool for less than | 2018 | 12 | pct_or_small_count_AMBIG | 17.75 | 3 | 46 | 15, 12, 19, 4 |
| 10 | J | Children attending preschool for less than | 2019 | 12 | pct_or_small_count_AMBIG | 17.67 | 4 | 56 | 15, 18, 16, 10 |
| 10 | J | Children attending preschool for less than | 2020 | 12 | pct_or_small_count_AMBIG | 16.5 | 4 | 49 | 16, 12, 20, 8 |
| 10 | J | Children attending preschool for less than | 2022 | 11 | pct_or_small_count_AMBIG | 20.82 | 8 | 79 | 11, 13, 19, 9 |
| 10 | J | Children attending preschool for less than | 2023 | 11 | pct_or_small_count_AMBIG | 14.64 | 4 | 39 | 8, 6, 11, 4 |
| 11 | K | Children attending preschool for 15 hours  | 2018 | 12 | ambiguous | 82.83 | 18 | 211 | 31, 102, 117, 49 |
| 11 | K | Children attending preschool for 15 hours  | 2019 | 12 | ambiguous | 90.42 | 21 | 234 | 49, 94, 132, 50 |
| 11 | K | Children attending preschool for 15 hours  | 2020 | 12 | ambiguous | 90.25 | 26 | 261 | 37, 92, 134, 61 |
| 11 | K | Children attending preschool for 15 hours  | 2022 | 11 | ambiguous | 103.91 | 37 | 345 | 45, 96, 101, 58 |
| 11 | K | Children attending preschool for 15 hours  | 2023 | 11 | ambiguous | 108.18 | 44 | 199 | 44, 101, 111, 61 |
| 12 | L | Completed year 12 or equivalent (%) | 2011 | 11 | pct_likely | 45.5 | 30.2 | 62.6 | 44.4, 45.5, 48.1, 55.9 |
| 12 | L | Completed year 12 or equivalent (%) | 2016 | 12 | pct_likely | 50.28 | 32.9 | 70.7 | 44.7, 48.6, 53.4, 60.4 |
| 12 | L | Completed year 12 or equivalent (%) | 2021 | 12 | pct_likely | 55.81 | 37.2 | 76.8 | 51.4, 53.7, 61.1, 65.3 |
| 19 | S | Total persons with non-school qualificatio | 2011 | 11 | pct_likely | 57.05 | 45 | 65 | 59.5, 51.2, 56.5, 60.7 |
| 19 | S | Total persons with non-school qualificatio | 2016 | 12 | pct_likely | 62.24 | 51 | 73.1 | 66.8, 53.4, 60.7, 62.8 |
| 19 | S | Total persons with non-school qualificatio | 2021 | 12 | pct_likely | 64.34 | 54.1 | 74.4 | 68.2, 57.2, 63.2, 66.6 |
| 20 | T | Postgraduate degree (%) | 2011 | 11 | pct_likely | 3.47 | 1 | 6.6 | 4.3, 2.5, 4.3, 5.3 |
| 20 | T | Postgraduate degree (%) | 2016 | 12 | pct_likely | 4.25 | 0.9 | 7.6 | 5.2, 2.9, 5.1, 7.2 |
| 20 | T | Postgraduate degree (%) | 2021 | 12 | pct_likely | 6.13 | 1.7 | 10.3 | 6.1, 4.6, 9.2, 9.4 |
| 21 | U | Graduate diploma/graduate certificate (%) | 2011 | 11 | pct_likely | 1.97 | 1.1 | 3.8 | 2.8, 1.5, 1.9, 2.2 |
| 21 | U | Graduate diploma/graduate certificate (%) | 2016 | 12 | pct_likely | 2.2 | 1 | 3.6 | 2.4, 1.9, 2.3, 2.2 |
| 21 | U | Graduate diploma/graduate certificate (%) | 2021 | 12 | pct_likely | 2.62 | 1.6 | 4.1 | 3.2, 2, 2.5, 2.8 |
| 22 | V | Bachelor degree (%) | 2011 | 11 | pct_likely | 10.94 | 6.3 | 15.2 | 12.4, 8.3, 12.1, 14.6 |
| 22 | V | Bachelor degree (%) | 2016 | 12 | pct_likely | 12.6 | 6.8 | 21 | 12.9, 8.7, 14, 16 |
| 22 | V | Bachelor degree (%) | 2021 | 12 | pct_likely | 14.4 | 7.6 | 22.2 | 14.8, 10.6, 15.8, 17.3 |
| 23 | W | Advanced diploma/diploma (%) | 2011 | 11 | pct_likely | 7.85 | 5.7 | 10.9 | 7.7, 7.4, 6.8, 9.6 |
| 23 | W | Advanced diploma/diploma (%) | 2016 | 12 | pct_likely | 9.27 | 6.8 | 14.1 | 8.4, 8.4, 8.8, 9.6 |
| 23 | W | Advanced diploma/diploma (%) | 2021 | 12 | pct_likely | 9.58 | 6.6 | 14.1 | 9.6, 9.1, 9.2, 9.5 |
| 24 | X | Certificate (%) | 2011 | 11 | pct_likely | 20.9 | 18 | 24.8 | 20.1, 20.4, 18.7, 18 |
| 24 | X | Certificate (%) | 2016 | 12 | pct_likely | 21.94 | 19 | 28.2 | 21.4, 22.3, 19.4, 19.2 |
| 24 | X | Certificate (%) | 2021 | 12 | pct_likely | 22.32 | 18.8 | 26.4 | 23.2, 22.3, 18.8, 20.4 |
| 25 | Y | Non-school qualification inadequately desc | 2011 | 11 | pct_likely | 1.45 | 1.1 | 1.9 | 1.5, 1.2, 1.1, 1.4 |
| 25 | Y | Non-school qualification inadequately desc | 2016 | 12 | pct_likely | 0.67 | 0.3 | 1 | 0.9, 0.6, 0.8, 0.6 |
| 25 | Y | Non-school qualification inadequately desc | 2021 | 12 | pct_likely | 0.58 | 0.4 | 0.8 | 0.4, 0.4, 0.6, 0.6 |
| 26 | Z | Non-school qualification not stated (%) | 2011 | 11 | pct_likely | 10.51 | 5.6 | 16.3 | 10.7, 9.8, 11.6, 9.7 |
| 26 | Z | Non-school qualification not stated (%) | 2016 | 12 | pct_likely | 11.31 | 5.6 | 16.7 | 15.6, 8.6, 10.4, 7.9 |
| 26 | Z | Non-school qualification not stated (%) | 2021 | 12 | pct_likely | 8.7 | 4.4 | 11.8 | 10.8, 8.2, 7.2, 6.4 |
| 27 | AA | Natural and physical sciences (%) | 2011 | 11 | pct_likely | 2.85 | 1.4 | 4.9 | 3.8, 2.3, 3.1, 4.2 |
| 27 | AA | Natural and physical sciences (%) | 2016 | 12 | pct_likely | 2.82 | 1.3 | 4.4 | 3.8, 2.4, 2.9, 4.1 |
| 27 | AA | Natural and physical sciences (%) | 2021 | 12 | pct_likely | 2.93 | 1.7 | 4.6 | 3.1, 2.4, 3.3, 3.7 |
| 51 | AY | Employed (no.) | 2011 | 11 | count_likely | 3718.09 | 1095 | 7815 | 1550, 4546, 5425, 2711 |
| 51 | AY | Employed (no.) | 2016 | 12 | count_likely | 3499.0 | 904 | 7906 | 1644, 4185, 5608, 2647 |
| 51 | AY | Employed (no.) | 2021 | 12 | count_likely | 4098.58 | 1104 | 9023 | 2013, 4315, 6247, 2922 |
| 52 | AZ | Unemployed (no.) | 2011 | 11 | ambiguous | 126.64 | 41 | 213 | 67, 158, 197, 88 |
| 52 | AZ | Unemployed (no.) | 2016 | 12 | ambiguous | 150.5 | 15 | 310 | 71, 204, 310, 143 |
| 52 | AZ | Unemployed (no.) | 2021 | 12 | ambiguous | 132.92 | 45 | 270 | 68, 198, 270, 108 |
| 54 | BB | Unemployment rate (%) | 2011 | 11 | pct_likely | 3.66 | 2.1 | 7.7 | 4.1, 3.4, 3.5, 3.1 |
| 54 | BB | Unemployment rate (%) | 2016 | 12 | pct_likely | 4.17 | 1.6 | 8.3 | 4.1, 4.6, 5.2, 5.1 |
| 54 | BB | Unemployment rate (%) | 2021 | 12 | pct_likely | 3.3 | 1.6 | 5.5 | 3.3, 4.4, 4.1, 3.6 |
| 55 | BC | Participation rate (%) | 2011 | 11 | pct_likely | 64.15 | 44.7 | 79 | 59.3, 69.4, 64.9, 71.6 |
| 55 | BC | Participation rate (%) | 2016 | 12 | pct_likely | 63.39 | 42.8 | 82.5 | 53.1, 66.3, 64.5, 70 |
| 55 | BC | Participation rate (%) | 2021 | 12 | pct_likely | 64.94 | 44.8 | 84.7 | 57.3, 65.4, 67.9, 70.6 |
| 60 | BH | Number of jobs held by females | 2018 | 12 | count_likely | 3083.67 | 999 | 6772 | 1538, 3410, 4487, 2265 |
| 60 | BH | Number of jobs held by females | 2019 | 12 | count_likely | 3195.75 | 1014 | 6957 | 1627, 3438, 4613, 2260 |
| 60 | BH | Number of jobs held by females | 2020 | 12 | count_likely | 3204.5 | 1061 | 6948 | 1709, 3409, 4630, 2184 |
| 60 | BH | Number of jobs held by females | 2021 | 12 | count_likely | 3371.08 | 1137 | 7108 | 1779, 3407, 4894, 2262 |
| 60 | BH | Number of jobs held by females | 2022 | 12 | count_likely | 3616.83 | 1250 | 7474 | 1896, 3632, 5379, 2394 |
| 61 | BI | Number of jobs held by males | 2018 | 12 | count_likely | 3249.08 | 1274 | 6933 | 1628, 3665, 5102, 2478 |
| 61 | BI | Number of jobs held by males | 2019 | 12 | count_likely | 3315.17 | 1157 | 7081 | 1701, 3732, 5143, 2461 |
| 61 | BI | Number of jobs held by males | 2020 | 12 | count_likely | 3375.08 | 1303 | 7051 | 1740, 3664, 5196, 2489 |
| 61 | BI | Number of jobs held by males | 2021 | 12 | count_likely | 3519.67 | 1250 | 7286 | 1786, 3737, 5683, 2622 |
| 61 | BI | Number of jobs held by males | 2022 | 12 | count_likely | 3783.42 | 1269 | 7499 | 1850, 3950, 6604, 3062 |
| 83 | CE | Managers (%) | 2011 | 11 | pct_likely | 17.09 | 10.1 | 27.5 | 23.2, 10.1, 10.4, 12.2 |
| 83 | CE | Managers (%) | 2016 | 12 | pct_likely | 17.0 | 10.8 | 27.3 | 22.4, 10.8, 11.1, 12.1 |
| 83 | CE | Managers (%) | 2021 | 12 | pct_likely | 17.89 | 11.8 | 24.9 | 22.1, 11.8, 12.6, 14.1 |
| 91 | CM | Occupation inadequately described or not s | 2011 | 11 | pct_likely | 2.09 | 1.5 | 3 | 1.7, 2.3, 3, 2.5 |
| 91 | CM | Occupation inadequately described or not s | 2016 | 12 | pct_likely | 2.24 | 1.6 | 3 | 3, 2.2, 2.5, 1.9 |
| 91 | CM | Occupation inadequately described or not s | 2021 | 12 | pct_likely | 2.13 | 1.8 | 2.5 | 2, 2.2, 2.3, 2 |

## Sheet: `Table 2` (kind: lga) — skipped from detail (no SA2 rows)

## Manual review checklist

1. Pick 6-10 target metrics for ingest. Likely shortlist:
   - Annual preschool: cols 4 (4yo enrolled), 9 (total enrolled),
     11 (15h+/week attendance)
   - Census educational attainment: col 12 (Year 12+%),
     col 22 (Bachelor%)
   - Census labour: col 54 (Unemployment rate %),
     col 55 (Participation rate %)
   - Female-specific: TBD — check if col 60/61 (jobs by sex)
     gives a usable signal at SA2, or whether female LFP is
     not actually published at SA2 in this workbook.
2. Schema: new table `abs_sa2_education_employment_annual` with
   columns (sa2_code, year, metric_name, value).
3. Sanity checks per metric type — Standard 25.