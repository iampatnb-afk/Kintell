# SA2 Cohort Apply (Layer 3 prep) - DRY-RUN

_Generated: 2026-04-28T12:03:46_

Method: spatial join SA2 centroid -> RA polygon (EPSG:3577 metric).
Sources:
- `abs_data/ASGS_2021_Main_Structure_GDA2020.gpkg` (SA2 polygons)
- `abs_data/ASGS_Ed3_2021_RA_GDA2020.gpkg` (RA polygons)

Total cohort rows: 2,473

## State distribution

| State | SA2 count |
|---|---:|
| New South Wales | 644 |
| Queensland | 548 |
| Victoria | 524 |
| Western Australia | 267 |
| South Australia | 176 |
| Australian Capital Territory | 136 |
| Tasmania | 101 |
| Northern Territory | 70 |
| Other Territories | 6 |
| Outside Australia | 1 |

## Remoteness distribution

| RA name | SA2 count |
|---|---:|
| Major Cities of Australia | 1,474 |
| Inner Regional Australia | 515 |
| Outer Regional Australia | 338 |
| Remote Australia | 64 |
| Very Remote Australia | 63 |
| nan | 19 |

## RA band distribution (1=Major Cities .. 5=Very Remote)

| Band | SA2 count |
|---:|---:|
| 1 | 1,474 |
| 2 | 515 |
| 3 | 338 |
| 4 | 64 |
| 5 | 63 |
| _(null)_ | 19 |

## Coverage check vs `abs_sa2_erp_annual`

- ERP distinct SA2:    2,454
- Cohort distinct SA2: 2,473
- Overlap:             2,454
- ERP not in cohort:   0
- Cohort not in ERP:   19

**Cohort-only SA2s (likely synthetic / no usual address, max 20):**

- `197979799`
- `199999499`
- `297979799`
- `299999499`
- `397979799`
- `399999499`
- `497979799`
- `499999499`
- `597979799`
- `599999499`
- `697979799`
- `699999499`
- `797979799`
- `799999499`
- `897979799`
- `899999499`
- `997979799`
- `999999499`
- `ZZZZZZZZZ`

## Cross-check vs `services.aria_plus`

- Pairs compared:  1,420
- Matches:         1,268 (89.30%)
- Mismatches:      152

**Sample mismatches (first 30):**

| sa2_code | services.aria_plus | cohort.ra_name |
|---|---|---|
| `101021610` | Inner Regional Australia | Major Cities of Australia |
| `101031015` | Outer Regional Australia | Inner Regional Australia |
| `101061544` | Inner Regional Australia | Outer Regional Australia |
| `102021044` | Outer Regional Australia | Major Cities of Australia |
| `102021051` | Major Cities of Australia | Inner Regional Australia |
| `103021062` | Outer Regional Australia | Remote Australia |
| `103021064` | Inner Regional Australia | Outer Regional Australia |
| `103031073` | Inner Regional Australia | Outer Regional Australia |
| `103041079` | Outer Regional Australia | Inner Regional Australia |
| `104011081` | Inner Regional Australia | Outer Regional Australia |
| `104021083` | Inner Regional Australia | Outer Regional Australia |
| `104021087` | Inner Regional Australia | Outer Regional Australia |
| `105011093` | Remote Australia | Very Remote Australia |
| `105011095` | Outer Regional Australia | Remote Australia |
| `105021098` | Very Remote Australia | Remote Australia |
| `106021615` | Major Cities of Australia | Inner Regional Australia |
| `106031123` | Major Cities of Australia | Inner Regional Australia |
| `106041129` | Inner Regional Australia | Outer Regional Australia |
| `107031138` | Major Cities of Australia | Inner Regional Australia |
| `107041147` | Major Cities of Australia | Inner Regional Australia |
| `108021156` | Inner Regional Australia | Outer Regional Australia |
| `108041165` | Inner Regional Australia | Outer Regional Australia |
| `108051167` | Inner Regional Australia | Outer Regional Australia |
| `109021177` | Outer Regional Australia | Remote Australia |
| `109021179` | Outer Regional Australia | Remote Australia |
| `109031181` | Inner Regional Australia | Outer Regional Australia |
| `109031185` | Inner Regional Australia | Outer Regional Australia |
| `110011187` | Inner Regional Australia | Outer Regional Australia |
| `110011188` | Inner Regional Australia | Outer Regional Australia |
| `110021190` | Inner Regional Australia | Outer Regional Australia |

## Sample cohort rows (first 10)

| sa2_code | sa2_name | state | ra_name | ra_band |
|---|---|---|---|---:|
| `101021007` | Braidwood | New South Wales | Inner Regional Australia | 2 |
| `101021008` | Karabar | New South Wales | Major Cities of Australia | 1 |
| `101021009` | Queanbeyan | New South Wales | Major Cities of Australia | 1 |
| `101021010` | Queanbeyan - East | New South Wales | Major Cities of Australia | 1 |
| `101021012` | Queanbeyan West - Jerrabomberra | New South Wales | Major Cities of Australia | 1 |
| `101021610` | Googong | New South Wales | Major Cities of Australia | 1 |
| `101021611` | Queanbeyan Surrounds | New South Wales | Inner Regional Australia | 2 |
| `101031013` | Bombala | New South Wales | Outer Regional Australia | 3 |
| `101031014` | Cooma | New South Wales | Inner Regional Australia | 2 |
| `101031015` | Cooma Surrounds | New South Wales | Inner Regional Australia | 2 |
