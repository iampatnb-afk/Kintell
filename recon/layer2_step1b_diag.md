# Layer 2 Step 1b — Diagnostic A

Generated: 2026-04-27T21:17:11
DB: `data/kintell.db` (read-only)
GPKG: `abs_data/ASGS_2021_Main_Structure_GDA2020.gpkg`
Services columns detected: id=`service_id`, sa2=`sa2_code`, lat=`lat`, lng=`lng`, state=`state`

Read-only diagnostic. No DB or GPKG mutations.

## 1. `services` table — NULL `sa2_code` analysis

- Total services: **18,223**
- With `sa2_code`: **17,336** (95.13%)
- NULL `sa2_code`: **887** (4.87%)
  - With `lat/lng` (Step 1b candidates): **869**
  - Without lat/lng (unrecoverable here): **18**

Doc-stated expectation: ~887 candidates. Observed: 869. ✓ matches

Bounds of candidate lat/lng:
- lat: -43.16855 → 0.0
- lng: 0.0 → 153.57204

⚠ Suspicious points:
- 2 candidate(s) at (0, 0) — null-island, won't match
- 2 candidate(s) outside AU rough bbox (lat -45..-8, lng 95..170)

### Candidates by `state`

| state | total | null_sa2 | null_sa2_with_latlng |
|---|---:|---:|---:|
| NSW | 6,158 | 222 | 220 |
| VIC | 5,032 | 265 | 258 |
| QLD | 3,329 | 142 | 138 |
| WA | 1,525 | 56 | 54 |
| SA | 1,324 | 152 | 149 |
| ACT | 372 | 0 | 0 |
| TAS | 242 | 10 | 10 |
| NT | 235 | 34 | 34 |
| (NULL) | 6 | 6 | 6 |

## 2. GeoPackage probe

Path: `abs_data/ASGS_2021_Main_Structure_GDA2020.gpkg`
Size: 888.0 MB

Layers found: 8

| Layer | Geometry |
|---|---|
| `MB_2021_AUST_GDA2020` | Unknown |
| `SA2_2021_AUST_GDA2020` | Unknown |
| `SA1_2021_AUST_GDA2020` | Unknown |
| `SA3_2021_AUST_GDA2020` | Unknown |
| `SA4_2021_AUST_GDA2020` | Unknown |
| `GCCSA_2021_AUST_GDA2020` | Unknown |
| `STE_2021_AUST_GDA2020` | Unknown |
| `AUS_2021_AUST_GDA2020` | Unknown |

Selected SA2 layer: **`SA2_2021_AUST_GDA2020`**

SA2 features: **2,473**
SA2 columns: SA2_CODE_2021, SA2_NAME_2021, CHANGE_FLAG_2021, CHANGE_LABEL_2021, SA3_CODE_2021, SA3_NAME_2021, SA4_CODE_2021, SA4_NAME_2021, GCCSA_CODE_2021, GCCSA_NAME_2021, STATE_CODE_2021, STATE_NAME_2021, AUS_CODE_2021, AUS_NAME_2021, AREA_ALBERS_SQKM, ASGS_LOCI_URI_2021, geometry
SA2 CRS: `EPSG:7844`
  - Authority: **EPSG:7844**

SA2 attribute mapping: code=`SA2_CODE_2021`, name=`SA2_NAME_2021`, state=`STATE_NAME_2021`

## 3. Sample manual SA2 derivation (5 services)

| service_id | lat | lng | service_state | derived_sa2 | derived_name | sa2_state |
|---|---:|---:|---|---|---|---|
| 198 | -31.33295 | 148.47629 | NSW | 105011094 | Coonamble | New South Wales |
| 260 | -34.39228 | 119.38013 | WA | 509011229 | Gnowangerup | Western Australia |
| 308 | -42.79366 | 147.52462 | TAS | 601061035 | Sorell - Richmond | Tasmania |
| 319 | -35.98738 | 146.00673 | NSW | 109031181 | Corowa Surrounds | New South Wales |
| 322 | -42.80239 | 147.52757 | TAS | 601061035 | Sorell - Richmond | Tasmania |

Sample hit rate: **5/5** (0 miss).

## 4. Sanity / expectations for apply phase

- Doc-stated expectation: ~99% hit rate on the full 869-candidate set.
- Misses likely from offshore/external-territory services (Norfolk Island, Christmas Island, Cocos (Keeling), Ashmore & Cartier).
- Apply phase will:
  1. Take timestamped backup `data/kintell.db.backup_pre_step1b_<ts>` (Standard 8)
  2. Build spatial index over SA2 polygons (shapely STRtree or rtree)
  3. Reproject service points (EPSG:4326) → SA2 CRS
  4. UPDATE services SET sa2_code = ? WHERE service_id = ?
  5. Sanity invariants:
     - hit rate ≥ 99%
     - every assigned `sa2_code` present in `abs_sa2_erp_annual.sa2_code`
  6. audit_log row: `sa2_polygon_backfill_v1`

## 5. Manual review checklist before apply

- [ ] Candidate count (869) is within tolerance of doc-stated 887
- [ ] No suspicious bbox outliers (see §1; null-island=2, outside-AU=2)
- [ ] SA2 layer CRS confirmed: `EPSG:7844`
- [ ] All sample services produced sensible SA2 matches (see §3)
- [ ] Sample-derived `sa2_state` matches `services.state` where present (visual cross-check)

---
End of diagnostic.
