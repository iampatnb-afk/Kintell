# Layer 2 Step 1c — Apply Report

Generated: 2026-04-28T16:55:25
Mode: **APPLY**

Backup: `data/kintell.db.backup_pre_step1c_20260428_165521`
audit_id: **137**

## Pre-state (services table)

- Active services: **18,223**
- With lat/lng: **17,882** (candidate set)
- Without lat/lng (untouched): **341**
- With sa2_code populated: **18,203**
- Cross-state mismatches (services.state vs sa2_cohort.state_name): **1,435**

## Polygon derivation

- SA2 features: **2,473**
- Assigned: **17,839**
- Missed: **43** (offshore points / null-island)
- Hit rate: **99.76%** (threshold: 99%)

- Rows where sa2_code CHANGES: **8,132**
- Rows where sa2_code unchanged: **9,707**

✓ All pre-apply invariants pass.

## Post-state (after COMMIT)

- Cross-state mismatches: **9** (was 1,435, cap is < 50)
- Net cross-state corrections: **1,426**

## Misses (43 services with no SA2 match)

Typically offshore points (Norfolk Island, Christmas Island, Cocos), or services with bad lat/lng. Their existing sa2_code is left unchanged.

| service_id | lat | lng | state |
|---:|---:|---:|---|
| 974 | 0.0 | 0.0 | VIC |
| 1638 | 0.0 | 0.0 | NSW |
| 1907 | 0.0 | 0.0 | VIC |
| 2702 | 0.0 | 0.0 | NSW |
| 3257 | 0.0 | 0.0 | SA |
| 3494 | 0.0 | 0.0 | QLD |
| 3556 | 0.0 | 0.0 | WA |
| 5146 | 0.0 | 0.0 | QLD |
| 5154 | 0.0 | 0.0 | VIC |
| 5157 | 0.0 | 0.0 | WA |
| 6211 | 0.0 | 0.0 | QLD |
| 6572 | 0.0 | 0.0 | NSW |
| 6574 | 0.0 | 0.0 | NSW |
| 6715 | 0.0 | 0.0 | NT |
| 6882 | 0.0 | 0.0 | QLD |
| 7524 | 0.0 | 0.0 | QLD |
| 7798 | 0.0 | 0.0 | QLD |
| 8287 | 0.0 | 0.0 | NSW |
| 8623 | 0.0 | 0.0 | QLD |
| 8664 | 0.0 | 0.0 | NSW |
_+23 more_

## Sample of changed rows (first 30 of 8,132)

| service_id | state | old_sa2_code | old_sa2_name | new_sa2_code | new_sa2_name | new_sa2_state |
|---:|---|---|---|---|---|---|
| 1 | ACT | 801091102 | GARRAN | 801091103 | Hughes | Australian Capital Territory |
| 3 | ACT | 801091106 | MAWSON | 801091108 | Pearce | Australian Capital Territory |
| 5 | ACT | 801011004 | CHARNWOOD | 801011019 | Macgregor (ACT) | Australian Capital Territory |
| 6 | ACT | 801051054 | DICKSON | 801051061 | Watson | Australian Capital Territory |
| 7 | ACT | 801011002 | BELCONNEN | 801011007 | Evatt | Australian Capital Territory |
| 9 | ACT | 801011004 | CHARNWOOD | 801011022 | Melba | Australian Capital Territory |
| 10 | ACT | 801081094 | HOLDER | 801081098 | Weston | Australian Capital Territory |
| 12 | ACT | 801011002 | BELCONNEN | 801011003 | Bruce | Australian Capital Territory |
| 13 | ACT | 801011002 | BELCONNEN | 801011003 | Bruce | Australian Capital Territory |
| 14 | ACT | 801061063 | FORREST | 801061069 | Red Hill (ACT) | Australian Capital Territory |
| 20 | ACT | 801061062 | DEAKIN | 801061129 | Barton | Australian Capital Territory |
| 21 | ACT | 801071073 | CALWELL | 801071088 | Theodore | Australian Capital Territory |
| 22 | ACT | 801091106 | MAWSON | 801091110 | Torrens | Australian Capital Territory |
| 24 | ACT | 801011002 | BELCONNEN | 801011011 | Giralang | Australian Capital Territory |
| 25 | ACT | 801071084 | MONASH | 801071079 | Gowrie (ACT) | Australian Capital Territory |
| 26 | ACT | 801011002 | BELCONNEN | 801011016 | Kaleen | Australian Capital Territory |
| 27 | ACT | 801011004 | CHARNWOOD | 801011017 | Latham | Australian Capital Territory |
| 29 | ACT | 801051054 | DICKSON | 801051127 | Reid | Australian Capital Territory |
| 30 | ACT | 801091106 | MAWSON | 801091108 | Pearce | Australian Capital Territory |
| 32 | ACT | 801011001 | ARANDA | 801011026 | Weetangera | Australian Capital Territory |
| 33 | ACT | 801011001 | ARANDA | 801011013 | Hawker | Australian Capital Territory |
| 34 | ACT | 801011004 | CHARNWOOD | 801011015 | Holt | Australian Capital Territory |
| 35 | ACT | 801051054 | DICKSON | 801051057 | Lyneham | Australian Capital Territory |
| 36 | ACT | 801011001 | ARANDA | 801011020 | Macquarie | Australian Capital Territory |
| 37 | ACT | 801051124 | CAMPBELL | 801051060 | Turner | Australian Capital Territory |
| 38 | ACT | 801061062 | DEAKIN | 801061070 | Yarralumla | Australian Capital Territory |
| 39 | ACT | 801061062 | DEAKIN | 801061068 | Parkes (ACT) - South | Australian Capital Territory |
| 40 | ACT | 801011002 | BELCONNEN | 801011003 | Bruce | Australian Capital Territory |
| 42 | ACT | 801011004 | CHARNWOOD | 801011025 | Spence | Australian Capital Territory |
| 44 | ACT | 801051054 | DICKSON | 801051057 | Lyneham | Australian Capital Territory |

## Top 20 SA2s by service count (post-apply)

| sa2_code | sa2_name | services |
|---|---|---:|
| 212011546 | Beaconsfield - Officer | 32 |
| 213051468 | Werribee - West | 31 |
| 115021297 | Dural - Kenthurst - Wisemans Ferry | 30 |
| 125031714 | Merrylands - Holroyd | 28 |
| 116031317 | Mount Druitt - Whalan | 27 |
| 125041493 | Toongabbie - Constitution Hill | 26 |
| 119011354 | Bass Hill - Georges Hall | 26 |
| 111011209 | Glendale - Cardiff - Hillsborough | 26 |
| 122031429 | Freshwater - Brookvale | 25 |
| 114011278 | Nowra | 25 |
| 125041489 | North Parramatta | 25 |
| 317011456 | Toowoomba - Central | 24 |
| 123031447 | Picton - Tahmoor - Buxton | 24 |
| 214011374 | Langwarrin | 24 |
| 128021535 | Menai - Lucas Heights - Woronora | 24 |
| 124031464 | Penrith | 24 |
| 116021630 | Riverstone | 24 |
| 116021563 | Quakers Hill | 23 |
| 118011341 | Bondi Junction - Waverly | 23 |
| 119021362 | Belmore - Belfield | 23 |

## Audit log

Inserted: action=`sa2_polygon_overwrite_v1`, audit_id=**137**

---
End of report.
