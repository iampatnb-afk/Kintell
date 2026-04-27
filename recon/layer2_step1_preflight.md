# Layer 2 Step 1 — SA2 Backfill Preflight (read-only)
_Generated: 2026-04-26T14:59:29_

## services schema (columns relevant to backfill)
  - service_id                     INTEGER    pk=1 notnull=0
  - service_approval_number        TEXT       pk=0 notnull=0
  - postcode                       TEXT       pk=0 notnull=0
  - sa2_code                       TEXT       pk=0 notnull=0
  - sa2_name                       TEXT       pk=0 notnull=0
  - lat                            REAL       pk=0 notnull=0
  - lng                            REAL       pk=0 notnull=0
  - long_day_care                  INTEGER    pk=0 notnull=0
  - is_active                      INTEGER    pk=0 notnull=0

## Coverage on active services
  postcode                        18217/18223 (100.0%)
  lat                             17882/18223 ( 98.1%)
  lng                             17882/18223 ( 98.1%)
  sa2_code (current)                  0/18223 (  0.0%)
  sa2_name (current)                  0/18223 (  0.0%)

## Concordance load
  unique postcodes in concordance: 1,983
    0800 -> ('701011001', 'DARWIN AIRPORT')
    0801 -> ('701011008', 'STUART PARK')
    0810 -> ('701021025', 'NIGHTCLIFF')
    0812 -> ('701021020', 'LEANYER')
    0814 -> ('701021025', 'NIGHTCLIFF')

## Simulated join: services.postcode -> concordance.SA2_CODE
  total active services         : 18,223
  matched on postcode           : 18,216 (99.96%)
  no postcode populated         : 6
  orphan (postcode not in conc) : 1

  sample matches:
    service_id=1 pc=2605 -> sa2=('801091102', 'GARRAN')
    service_id=2 pc=2607 -> sa2=('801091106', 'MAWSON')
    service_id=3 pc=2607 -> sa2=('801091106', 'MAWSON')

## Orphan postcodes (top 20 by service count)
  0834        1 services  e.g. service_id=2584 lat=-12.53622 lng=131.028

## Apply-script projected effect
  UPDATE services SET sa2_code, sa2_name on  : 18,216 active services
  Will leave NULL on                          : 7 (postcode missing or orphan)
  Coverage after backfill                     : 99.96% active services
  Gap from 100% requires lat/lng polygon lookup (deferred — no SA2 polygon file in abs_data)
