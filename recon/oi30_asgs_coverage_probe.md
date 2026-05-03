# OI-30 probe — pop_0_4 coverage across catchment SA2s

*Run: 2026-05-03T17:48:29. Read-only probe per DEC-65.*

## Headline

- Distinct SA2s in `service_catchment_cache`: **2294**
- partial (6-11 years): **2269** (98.9%)
- zero: **16** (0.7%)
- sparse (1-5 years): **9** (0.4%)

## Earliest-year-of-data distribution

When does pop_0_4 data start for SA2s where it exists?

| First year | Count | % of covered SA2s |
|---|---|---|
| 2019 | 2275 | 99.9% |
| 2020 | 1 | 0.0% |
| 2021 | 1 | 0.0% |
| 2022 | 1 | 0.0% |

## Anchor verification

- `211011251`: **6 years**, range 2019-2024 — Sparrow Bayswater LDC (svc 2358) — known sparse
- `118011341`: **6 years**, range 2019-2024 — Bondi Junction-Waverly (svc 103) — likely full

## Sparse SA2s (1-11 years) — top 30 of 2278

| SA2 code | Years | First year | Last year |
|---|---|---|---|
| `127021521` | 1 | 2021 | 2021 |
| `125031486` | 2 | 2019 | 2020 |
| `701011001` | 2 | 2019 | 2020 |
| `801031114` | 2 | 2019 | 2020 |
| `801061130` | 2 | 2019 | 2020 |
| `505021091` | 3 | 2022 | 2024 |
| `403041082` | 4 | 2019 | 2022 |
| `210051248` | 5 | 2019 | 2023 |
| `114011275` | 5 | 2020 | 2024 |
| `101021007` | 6 | 2019 | 2024 |
| `101021008` | 6 | 2019 | 2024 |
| `101021009` | 6 | 2019 | 2024 |
| `101021010` | 6 | 2019 | 2024 |
| `101021012` | 6 | 2019 | 2024 |
| `101021610` | 6 | 2019 | 2024 |
| `101021611` | 6 | 2019 | 2024 |
| `101031013` | 6 | 2019 | 2024 |
| `101031014` | 6 | 2019 | 2024 |
| `101031015` | 6 | 2019 | 2024 |
| `101031016` | 6 | 2019 | 2024 |
| `101041017` | 6 | 2019 | 2024 |
| `101041018` | 6 | 2019 | 2024 |
| `101041019` | 6 | 2019 | 2024 |
| `101041020` | 6 | 2019 | 2024 |
| `101041021` | 6 | 2019 | 2024 |
| `101041023` | 6 | 2019 | 2024 |
| `101041024` | 6 | 2019 | 2024 |
| `101041025` | 6 | 2019 | 2024 |
| `101041026` | 6 | 2019 | 2024 |
| `101041027` | 6 | 2019 | 2024 |

## Zero-coverage SA2s (16 total)

First 20 listed:

| SA2 code |
|---|
| `107011133` |
| `116031318` |
| `208031192` |
| `210011227` |
| `302031036` |
| `310041298` |
| `311031315` |
| `402041042` |
| `404031104` |
| `504031063` |
| `506021121` |
| `506031126` |
| `506031130` |
| `507011150` |
| `801051128` |
| `801061068` |

## Hypothesis assessment

If 2021-ASGS codes lack pre-2019 ABS data, expect:

- A meaningful cluster of SA2s with first_year >= 2019
- Bayswater (211011251) in that cluster
- Sparse SA2 codes follow 2021-ASGS patterns

Reader: cross-reference the first-year distribution. If most sparse SA2s start at 2019 or later, hypothesis is supported and the V1.5 fix is an ASGS concordance step in `build_sa2_history.py`.
