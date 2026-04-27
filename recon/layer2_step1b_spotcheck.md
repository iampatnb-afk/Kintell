# Layer 2 Step 1b — Spotcheck

Generated: 2026-04-27T21:36:33
DB: `data/kintell.db` (read-only)

Read-only post-apply validation. No mutations.

## 1. NULL `sa2_code` count vs audit_log expectation

- Total services: **18,223**
- With `sa2_code`: **18,203** (99.89%)
- NULL `sa2_code`: **20** (0.11%)

audit_log row found: audit_id=**133**, action=`sa2_polygon_backfill_v1`, actor=`layer2_step1b_apply`, occurred_at=`2026-04-27 11:33:23`

after_json payload:

```json
{
  "assigned": 867,
  "coverage": 0.998902,
  "hit_rate": 0.997699,
  "method": "sjoin within (EPSG:4326 -> EPSG:7844)",
  "missed": 2,
  "null_sa2": 20,
  "sa2_features": 2473,
  "source_gpkg": "abs_data/ASGS_2021_Main_Structure_GDA2020.gpkg",
  "source_layer": "SA2_2021_AUST_GDA2020",
  "with_sa2": 18203
}
```

- ✓ **audit_log row exists and is parseable**
- ✓ **NULL count post-apply matches audit_log expectation (expected 20, observed 20)**
- ✓ **assigned count in audit_log: 867**
- ✓ **hit_rate in audit_log: 0.9977**

## 2. Distribution by state

| state | total | with sa2_code | NULL sa2_code | coverage |
|---|---:|---:|---:|---:|
| NSW | 6,158 | 6,156 | 2 | 99.97% |
| VIC | 5,032 | 5,025 | 7 | 99.86% |
| QLD | 3,329 | 3,324 | 5 | 99.85% |
| WA | 1,525 | 1,523 | 2 | 99.87% |
| SA | 1,324 | 1,321 | 3 | 99.77% |
| ACT | 372 | 372 | 0 | 100.00% |
| TAS | 242 | 242 | 0 | 100.00% |
| NT | 235 | 235 | 0 | 100.00% |
| (NULL) | 6 | 5 | 1 | 83.33% |

- ✓ **ACT NULL count is 0 (was 0 pre-apply)**

## 3. Polygon re-projection check (10 random services)

For each sampled service: independently compute the SA2 via point-in-polygon and verify it matches the stored `services.sa2_code`. Validates the entire column, not just newly-assigned rows.

| service_id | lat | lng | stored sa2 | computed sa2 | name | match |
|---|---:|---:|---|---|---|:-:|
| 2246 | -27.70781 | 153.04646 | 311031311 | 311031311 | Boronia Heights - Park Ridge | ✓ |
| 7068 | -37.86391 | 145.07763 | 207011146 | 207011146 | Ashburton (Vic.) | ✓ |
| 10368 | -34.17259 | 150.6138 | 123031447 | 123031447 | Picton - Tahmoor - Buxton | ✓ |
| 14964 | -33.72321 | 151.0932 | 121021579 | 121021406 | Normanhurst - Thornleigh - Westleigh | ✗ |
| 4886 | -27.48865 | 153.03412 | 303021058 | 303021058 | Woolloongabba | ✓ |
| 8471 | -33.82536 | 151.19671 | 121041414 | 121011401 | St Leonards - Naremburn | ✗ |
| 1500 | -37.55359 | 143.81921 | 201011008 | 201011002 | Ballarat | ✗ |
| 18089 | -35.09065 | 138.55673 | 403041086 | 403041086 | Reynella | ✓ |
| 15345 | -38.19485 | 145.49268 | 212011548 | 212011548 | Koo Wee Rup | ✓ |
| 10093 | -33.43038 | 149.57678 | 318021480 | 103011612 | Bathurst - South | ✗ |

Sample match rate: **6/10**
- ✗ **All 10 sample services: stored sa2_code matches polygon-computed** — 4 mismatch(es)

## 4. Cross-table coverage

How many services now join to downstream SA2-keyed tables.

| Downstream table | Description | services with joinable SA2 | coverage |
|---|---|---:|---:|
| `abs_sa2_unemployment_quarterly` | SALM (Step 5) | 18,025 | 98.91% |
| `abs_sa2_socioeconomic_annual` | Income (Step 5b) | 18,203 | 99.89% |
| `abs_sa2_erp_annual` | ERP (Step 6) | 18,203 | 99.89% |
| `abs_sa2_education_employment_annual` | Education+Employment (Step 5b-prime) | 18,174 | 99.73% |

## 5. Residual NULL services (post-apply)

- Total NULL: **20**
  - No lat/lng (unrecoverable here, future fix): **18**
  - With lat/lng but no SA2 polygon (offshore/null-island): **2**

Residual NULL services with lat/lng (post-apply misses):

| service_id | lat | lng | state |
|---|---:|---:|---|
| 8623 | 0.0 | 0.0 | QLD |
| 13163 | 0.0 | 0.0 |  |

- ✓ **Expected residuals: 18 lat/lng-less + 2 null-island = 20** — observed: 20 (18 no-latlng + 2 unmatched)

## Summary

- Checks passed: **6**
- Checks failed: **1**

**✗ 1 CHECK(S) FAILED — investigate before proceeding.**

---
End of spotcheck.