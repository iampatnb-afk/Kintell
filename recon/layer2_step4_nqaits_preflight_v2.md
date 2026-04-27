# Phase 2.5 Layer 2 Step 4 — NQAITS Preflight v2
_Generated: 2026-04-26T15:42:41_

## Canonical column resolution per sheet
  total canonical fields wanted: 32
  sheets with ALL canonical fields resolved: 50/50

## service_id resolution: 50/50 sheets

## Cross-quarter coverage (all 50 sheets)
  unique service_ids across all quarters: 23,439
  distribution of services by quarter-count:
     50 quarters:  10618 services
     49 quarters:    480 services
     48 quarters:    287 services
     47 quarters:    192 services
     46 quarters:    186 services
     45 quarters:    179 services
     44 quarters:    242 services
     43 quarters:    139 services
     42 quarters:    164 services
     41 quarters:    180 services
     40 quarters:    219 services
     39 quarters:    165 services
     38 quarters:    146 services
     37 quarters:    161 services
     36 quarters:    256 services
  services present in ALL 50 quarters: 10,618

## PA chain analysis (50-sheet coverage)
  services with >1 distinct provider_id: 6,155 (26.3%)
    2 distinct providers: 4,685
    3+ distinct providers: 1,470

  sample chain changers (5):
    SE-00009638 touched 2 provider(s)
      Q42025data -> PR-40017687
      Q42024data -> PR-40017687
      Q42023data -> PR-40017687
      Q42022data -> PR-40017687
      Q42021data -> PR-40017687
      Q42020data -> PR-40017687
      Q42019data -> PR-40017687
      Q42018data -> PR-40017687
    SE-00009641 touched 2 provider(s)
      Q42025data -> PR-00005876
      Q42024data -> PR-00005876
      Q42023data -> PR-00005802
      Q42022data -> PR-00005802
      Q42021data -> PR-00005802
      Q42020data -> PR-00005802
      Q42019data -> PR-00005802
      Q42018data -> PR-00005802
    SE-00009647 touched 2 provider(s)
      Q42025data -> PR-00005811
      Q42024data -> PR-00005811
      Q42023data -> PR-00005811
      Q42022data -> PR-00005811
      Q42021data -> PR-00005811
      Q42020data -> PR-00005811
      Q42019data -> PR-00005811
      Q42018data -> PR-00005811
    SE-00009650 touched 2 provider(s)
      Q42025data -> PR-00005811
      Q42024data -> PR-00005811
      Q42023data -> PR-00005811
      Q42022data -> PR-00005811
      Q42021data -> PR-00005811
      Q42020data -> PR-00005811
      Q42019data -> PR-00005811
      Q42018data -> PR-00005811
    SE-00009651 touched 3 provider(s)
      Q42025data -> PR-00002539
      Q42024data -> PR-00002539
      Q42023data -> PR-00002539
      Q42022data -> PR-00002539
      Q42021data -> PR-00002539
      Q42020data -> PR-00002539
      Q42019data -> PR-00002539
      Q42018data -> PR-00002539

## Join check: NQAITS service_id vs services.service_approval_number
  DB total                 : 18,223
  DB active                : 18,223
  DB inactive              : 0
  NQAITS unique sids       : 23,439
  matched (DB ∩ NQAITS)    : 17,925  (98.36% of DB)
    of DB active matched   : 17,925  (98.36% of DB active)
    of DB inactive matched : 0
  in DB but not NQAITS     : 298
  in NQAITS but not DB     : 5,514

  sample DB-active not in NQAITS (5):
    'SE-00016706'
    'SE-00016946'
    'SE-00016951'
    'SE-00017000'
    'SE-00017396'
  sample NQAITS not in DB (5):
    'SE-00000016'
    'SE-00000024'
    'SE-00000033'
    'SE-00000039'
    'SE-00000053'

## Ingest volume estimate
  total (sid, quarter) pairs across all sheets: 807,526
  avg quarters per service: 34.5
