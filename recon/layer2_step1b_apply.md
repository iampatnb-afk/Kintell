# Layer 2 Step 1b — Apply (APPLIED)

Generated: 2026-04-27T21:33:23
Mode: **apply**
Backup: `data/kintell.db.backup_pre_step1b_20260427_213320`

## Summary

- Services total: **18,223**
- NULL `sa2_code` pre-apply: **887**
  - Unrecoverable (no lat/lng): **18**
  - Step 1b candidates: **869**
- Assigned: **867**
- Missed: **2**
- Hit rate: **99.77%** (threshold 99%)
- Expected NULL `sa2_code` post-apply: **20** (unrecoverable 18 + missed 2)
- Net SA2 coverage post-apply: **99.89%**

## Invariants

✓ All invariants pass.
- hit_rate 99.77% ≥ 99%
- canonical-universe orphans: 0 (all assigned sa2_codes present in `abs_sa2_erp_annual`)

## Distribution of assignments by state

| state | services | distinct SA2s |
|---|---:|---:|
| VIC | 258 | 76 |
| NSW | 220 | 77 |
| SA | 149 | 46 |
| QLD | 137 | 47 |
| WA | 54 | 28 |
| NT | 34 | 15 |
| TAS | 10 | 8 |
| nan | 5 | 5 |

## Top 20 SA2s by assignment count

| sa2_code | sa2_name | services |
|---|---|---:|
| 113031271 | Wagga Wagga Surrounds | 14 |
| 109011175 | Albury Surrounds | 12 |
| 316081549 | Noosa Hinterland | 11 |
| 312031359 | Airlie - Whitsundays | 11 |
| 211051286 | Yarra Valley | 11 |
| 402051054 | Redwood Park | 11 |
| 310021280 | Lockyer Valley - East | 10 |
| 405021119 | Wakefield - Barunga West | 9 |
| 402051053 | Modbury Heights | 9 |
| 215011394 | Yarriambiack | 9 |
| 214021379 | Hastings - Somers | 8 |
| 209041224 | Wallan | 8 |
| 204021067 | Wangaratta Surrounds | 8 |
| 214021385 | Somerville | 8 |
| 104021089 | Sawtell - Boambee | 8 |
| 404021102 | The Parks | 7 |
| 112011237 | Ballina Surrounds | 7 |
| 205031091 | Phillip Island | 7 |
| 110041205 | Tamworth Surrounds | 7 |
| 214021383 | Point Nepean | 7 |

## Misses (services that did not match any SA2 polygon)

| service_id | lat | lng | state |
|---|---:|---:|---|
| 8623 | 0.0 | 0.0 | QLD |
| 13163 | 0.0 | 0.0 |  |

## Sample assignments (first 30 by service_id)

| service_id | lat | lng | state | sa2_code | sa2_name | sa2_state |
|---|---:|---:|---|---|---|---|
| 198 | -31.33295 | 148.47629 | NSW | 105011094 | Coonamble | New South Wales |
| 260 | -34.39228 | 119.38013 | WA | 509011229 | Gnowangerup | Western Australia |
| 308 | -42.79366 | 147.52462 | TAS | 601061035 | Sorell - Richmond | Tasmania |
| 319 | -35.98738 | 146.00673 | NSW | 109031181 | Corowa Surrounds | New South Wales |
| 322 | -42.80239 | 147.52757 | TAS | 601061035 | Sorell - Richmond | Tasmania |
| 323 | -35.7859 | 137.26268 | SA | 407011145 | Kangaroo Island | South Australia |
| 334 | -32.79529 | 149.97283 | NSW | 103031073 | Mudgee Surrounds - East | New South Wales |
| 342 | -32.52392 | 115.73221 | WA | 502011025 | Mandurah | Western Australia |
| 346 | -25.90714 | 153.07986 | QLD | 319031511 | Cooloola | Queensland |
| 348 | -34.55254 | 138.74565 | SA | 402011025 | Gawler - North | South Australia |
| 365 | -29.66671 | 153.10656 | NSW | 104011081 | Grafton Surrounds | New South Wales |
| 367 | -29.81658 | 153.23915 | NSW | 104011081 | Grafton Surrounds | New South Wales |
| 376 | -34.76811 | 137.59842 | SA | 405041127 | Yorke Peninsula - North | South Australia |
| 380 | -34.20571 | 150.57697 | NSW | 123031447 | Picton - Tahmoor - Buxton | New South Wales |
| 386 | -31.34897 | 150.65158 | NSW | 110041201 | Quirindi | New South Wales |
| 396 | -34.45391 | 138.81598 | SA | 405011111 | Light | South Australia |
| 409 | -33.78494 | 138.22203 | SA | 405021119 | Wakefield - Barunga West | South Australia |
| 462 | -34.82006 | 138.71894 | SA | 402051055 | St Agnes - Ridgehaven | South Australia |
| 470 | -32.79817 | 134.20114 | SA | 406011134 | West Coast (SA) | South Australia |
| 471 | -32.79845 | 134.2114 | SA | 406011134 | West Coast (SA) | South Australia |
| 477 | -34.80158 | 138.71047 | SA | 402051054 | Redwood Park | South Australia |
| 478 | -34.80155 | 138.71088 | SA | 402051054 | Redwood Park | South Australia |
| 479 | -34.80002 | 138.71233 | SA | 402051054 | Redwood Park | South Australia |
| 481 | -34.5727 | 139.60164 | SA | 407031164 | Mannum | South Australia |
| 486 | -35.25239 | 139.45685 | SA | 407031169 | The Coorong | South Australia |
| 490 | -34.82148 | 138.72776 | SA | 402051055 | St Agnes - Ridgehaven | South Australia |
| 501 | -38.45628 | 145.24257 | VIC | 205031091 | Phillip Island | Victoria |
| 503 | -26.58426 | 149.18526 | QLD | 307011177 | Roma Surrounds | Queensland |
| 514 | -23.78803 | 150.92208 | QLD | 308051535 | Gladstone Hinterland | Queensland |
| 519 | -16.34142 | 145.41257 | QLD | 306041164 | Daintree | Queensland |

## Audit log

Inserted: action=`sa2_polygon_backfill_v1`, audit_id=**133**

---
End of report.
