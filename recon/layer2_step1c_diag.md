# Layer 2 Step 1c — Diagnostic (overwrite rebuild)

Generated: 2026-04-28T16:47:34
DB: `data/kintell.db` (read-only)
GPKG: `abs_data/ASGS_2021_Main_Structure_GDA2020.gpkg`

Read-only diagnostic. No DB or GPKG mutations.

**Premise.** Step 1 used a postcode→SA2 concordance which is 1:1, so for postcodes spanning multiple SA2s the publisher chose arbitrarily. Step 1b corrected only the 887 NULLs, not the 17,336 already-populated (potentially wrong) rows. The May 2026 cross-state-mismatch probe found ~1,435 services whose `services.state` disagrees with their currently-assigned SA2's state. Step 1c is the OVERWRITE rebuild: every active service with lat/lng gets its sa2_code re-derived by point-in-polygon, regardless of the existing value.

## 1. Candidate set

- Active services: **18,223**
- With lat/lng (Step 1c will touch these): **17,882**
- With sa2_code populated: **18,203**
- Without lat/lng (untouchable here, retained as-is): **341**

## 2. Cross-state mismatch baseline (current state)

Services where `services.state` disagrees with the state of their currently-assigned SA2 via `sa2_cohort`. These are the rows Step 1c is intended to correct.

**Total cross-state mismatches: 1,435** (out of 17,882 candidates with lat/lng — 8.02%)

| services.state | sa2_cohort.state_name | services |
|---|---|---:|
| VIC | New South Wales | 276 |
| NSW | Queensland | 140 |
| NSW | Victoria | 117 |
| SA | New South Wales | 79 |
| NSW | Australian Capital Territory | 67 |
| VIC | Queensland | 67 |
| NSW | South Australia | 63 |
| SA | Victoria | 63 |
| SA | Queensland | 60 |
| WA | Victoria | 60 |
| QLD | Victoria | 48 |
| WA | Queensland | 45 |
| NSW | Western Australia | 38 |
| QLD | New South Wales | 31 |
| NT | Queensland | 26 |
| NSW | Other Territories | 25 |
| SA | Western Australia | 25 |
| VIC | Tasmania | 23 |
| QLD | Northern Territory | 21 |
| SA | Australian Capital Territory | 16 |
| WA | New South Wales | 16 |
| TAS | Queensland | 14 |
| VIC | Northern Territory | 12 |
| VIC | South Australia | 11 |
| WA | Australian Capital Territory | 11 |
| NSW | Tasmania | 10 |
| SA | Northern Territory | 10 |
| TAS | New South Wales | 10 |
| QLD | South Australia | 8 |
| TAS | Western Australia | 7 |
| QLD | Australian Capital Territory | 5 |
| QLD | Tasmania | 4 |
| QLD | Western Australia | 4 |
| VIC | Western Australia | 4 |
| WA | South Australia | 4 |
| VIC | Australian Capital Territory | 3 |
| ACT | Other Territories | 2 |
| NT | New South Wales | 2 |
| SA | Tasmania | 2 |
| TAS | Australian Capital Territory | 2 |
| TAS | Victoria | 2 |
| NT | Victoria | 1 |
| WA | Other Territories | 1 |

**Within-state remoteness mismatches** (services.aria_plus != sa2_cohort.ra_name): **1,249**

## 3. GeoPackage SA2 layer

- Layer: `SA2_2021_AUST_GDA2020`
- Features: **2,473**
- CRS: `EPSG:7844`
- Authority: **EPSG:7844**
- File size: **888.0 MB**

## 4. Sample of 10 cross-state mismatches (before / after)

For each, the existing `sa2_code` (from postcode-derived Step 1) is shown alongside the polygon-derived SA2 from the service's lat/lng. If Step 1c is right, every row should show the after-state matching `services.state`.

| service_id | name (truncated) | svc_state | postcode | old_sa2_code | old_sa2_state | new_sa2_code | new_sa2_state | fixes? |
|---:|---|---|---|---|---|---|---|---|
| 73 | One Tree Defence Childcare Unit  | ACT | 2540 | 901031003 | Other Territories | 901031003 | Other Territories | ✗ |
| 103 | Kool HQ Waverley | NSW | 2024 | 212051321 | Victoria | 118011341 | New South Wales | ✓ |
| 137 | Discovery Kids Early Learning Ce | WA | 6021 | 801081096 | Australian Capital Territory | 505021084 | Western Australia | ✓ |
| 146 | Rise Early Learning Abbotsford | NSW | 2046 | 206071139 | Victoria | 120011386 | New South Wales | ✓ |
| 154 | Nido Early School Balcatta | WA | 6021 | 801081096 | Australian Capital Territory | 505021084 | Western Australia | ✓ |
| 163 | Amiga Montessori Burwood | VIC | 3125 | 120031678 | New South Wales | 207031165 | Victoria | ✓ |
| 165 | Little Pioneers Early Learning C | WA | 6112 | 206061135 | Victoria | 506011115 | Western Australia | ✓ |
| 176 | Waratah OSHClub | NSW | 2298 | 604031096 | Tasmania | 111031234 | New South Wales | ✓ |
| 178 | Grow Early Education Kelso | NSW | 2795 | 318021480 | Queensland | 103011059 | New South Wales | ✓ |
| 183 | Maroondah Occasional Care | VIC | 3136 | 120031679 | New South Wales | 211031450 | Victoria | ✓ |

**Fixes-state in sample: 9/10**

## 5. Sample of 10 currently-correct rows (regression check)

These are services whose `services.state` already matches the state of their assigned SA2. After polygon derivation the new `sa2_code` may or may not differ — but if it does differ, the new SA2 must still be in the same state. Any row where new_state != svc_state would mean the polygon math is breaking known-good data.

| service_id | svc_state | old_sa2_code | new_sa2_code | new_sa2_state | same_code | same_state |
|---:|---|---|---|---|---|---|
| 1 | ACT | 801091102 | 801091103 | Australian Capital Territory | ✗ | ✓ |
| 2 | ACT | 801091106 | 801091106 | Australian Capital Territory | ✓ | ✓ |
| 3 | ACT | 801091106 | 801091108 | Australian Capital Territory | ✗ | ✓ |
| 4 | ACT | 801071090 | 801071090 | Australian Capital Territory | ✓ | ✓ |
| 5 | ACT | 801011004 | 801011019 | Australian Capital Territory | ✗ | ✓ |
| 6 | ACT | 801051054 | 801051061 | Australian Capital Territory | ✗ | ✓ |
| 7 | ACT | 801011002 | 801011007 | Australian Capital Territory | ✗ | ✓ |
| 8 | ACT | 801071084 | 801071084 | Australian Capital Territory | ✓ | ✓ |
| 9 | ACT | 801011004 | 801011022 | Australian Capital Territory | ✗ | ✓ |
| 10 | ACT | 801081094 | 801081098 | Australian Capital Territory | ✗ | ✓ |

**Same-code in sample: 3/10** (some-code-changes are EXPECTED — postcode-correct rows can still be on the wrong side of an SA2 boundary inside the right state)
**Same-state in sample: 10/10** (should be 100% — anything less is a regression risk)

## 6. Service 246 — the original symptom

- Service: **Sparrow Early Learning Bentley** (BENTLEY, WA 6102)
- lat/lng: **-32.01192, 115.91707**
- Current sa2_code: **306021144** (`BENTLEY PARK`, sa2_cohort.state_name=`Queensland`)
- **New sa2_code (polygon-derived): 506031124** (`Bentley - Wilson - St James`, state=`Western Australia`)

## 7. Apply preview (what Step 1c will do)

- For each of the **~17,880 services with lat/lng**, derive sa2_code via point-in-polygon against the SA2 GeoPackage.
- For matches, **UPDATE services SET sa2_code = ?, sa2_name = ?** (both, because sa2_name was also being shown wrongly).
- Untouched: services without lat/lng (~340), polygon misses (expected: a handful of offshore points).
- Pre-state captured into `audit_log.before_json`; post-state into `after_json`.
- Apply-mode invariants:
  - hit rate ≥ 99% on candidate set
  - cross-state mismatches drop from current 1,435 to **< 50** (a handful expected from genuine boundary cases / NQAITS lat/lng errors)
  - every assigned sa2_code present in `abs_sa2_erp_annual` (canonical-universe check, same as Step 1b)
- Audit action: `sa2_polygon_overwrite_v1`. New backup file: `data/kintell.db.backup_pre_step1c_<ts>`.
