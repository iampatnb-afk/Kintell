# Phase 2.5 Layer 2 Step 4 — NQAITS Preflight
_Generated: 2026-04-26T15:36:38_

## Data sheets
  total: 50
  range: Q32013data -> Q42025data

## Header drift across all 50 data sheets
  unique column names across all sheets: 48

  column -> sheet count (cols not in all 50 are drifters):
     50/50  'Final Report Sent Date'
     50/50  'Latitude'
     50/50  'Long Day Care'
     50/50  'Longitude'
     50/50  'Managing Jurisdiction'
     50/50  'Maximum total places'
     50/50  'NQS Version'
     50/50  'Nature Care Other'
     50/50  'OSHC After School'
     50/50  'OSHC Vacation Care'
     50/50  'Postcode'
     50/50  'Provider ID'
     50/50  'Provider Management Type'
     50/50  'Provider Name'
     50/50  'SEIFA'
     50/50  'Service Name'
     50/50  'Service Type'
     46/50  'Overall Rating' <-- DRIFT
     46/50  'Quality Area 1' <-- DRIFT
     46/50  'Quality Area 2' <-- DRIFT
     46/50  'Quality Area 3' <-- DRIFT
     46/50  'Quality Area 4' <-- DRIFT
     46/50  'Quality Area 5' <-- DRIFT
     46/50  'Quality Area 6' <-- DRIFT
     46/50  'Quality Area 7' <-- DRIFT
     42/50  'PreschoolKindergarten Part of a School' <-- DRIFT
     39/50  'ARIA+' <-- DRIFT
     36/50  'Approval Date' <-- DRIFT
     33/50  'OSHC BeforeSchool' <-- DRIFT
     33/50  'PreschoolKindergarten Stand Alone' <-- DRIFT
     33/50  'Service ID' <-- DRIFT
     33/50  'Service sub-type (ordered counting method)' <-- DRIFT
     17/50  'OSHC Before School' <-- DRIFT
     17/50  'Service Approval Number' <-- DRIFT
     17/50  'Service Sub Type' <-- DRIFT
     14/50  'ApprovalDate' <-- DRIFT
     11/50  'ARIA' <-- DRIFT
      9/50  'Preschool/Kindergarten Stand Alone' <-- DRIFT
      8/50  'Preschool/\nKindergarten Part of a School' <-- DRIFT
      8/50  'Preschool/\nKindergarten Stand Alone' <-- DRIFT
      4/50  'OverallRating' <-- DRIFT
      4/50  'Q1' <-- DRIFT
      4/50  'Q2' <-- DRIFT
      4/50  'Q3' <-- DRIFT
      4/50  'Q4' <-- DRIFT
      4/50  'Q5' <-- DRIFT
      4/50  'Q6' <-- DRIFT
      4/50  'Q7' <-- DRIFT

## Service ID column position consistency
  Service ID position distribution: {0: 33}

  WARN: sheet Q42025data missing Service ID
  WARN: sheet Q32025data missing Service ID
  WARN: sheet Q22025data missing Service ID
  WARN: sheet Q12025data missing Service ID
  WARN: sheet Q42024data missing Service ID
  WARN: sheet Q32024data missing Service ID
  WARN: sheet Q22024data missing Service ID
  WARN: sheet Q12024data missing Service ID
  WARN: sheet Q42023data missing Service ID
  WARN: sheet Q32023data missing Service ID
  WARN: sheet Q22023data missing Service ID
  WARN: sheet Q12023data missing Service ID
  WARN: sheet Q42022data missing Service ID
  WARN: sheet Q32022data missing Service ID
  WARN: sheet Q22022data missing Service ID
  WARN: sheet Q12022data missing Service ID
  WARN: sheet Q42021data missing Service ID
## Cross-quarter coverage of Service IDs
  unique Service IDs across all 50 quarters: 20,078
  distribution of services by quarter-count present:
     33 quarters:  11550 services
     32 quarters:    444 services
     31 quarters:    272 services
     30 quarters:    189 services
     29 quarters:    158 services
     28 quarters:    179 services
     27 quarters:    275 services
     26 quarters:    169 services
     25 quarters:    193 services
     24 quarters:    210 services
     23 quarters:    267 services
     22 quarters:    211 services
     21 quarters:    209 services
     20 quarters:    203 services
     19 quarters:    317 services

  Service IDs present in ALL 50 quarters: 0

## Provider ID change analysis (PA chain reconstruction)
  services with >1 distinct Provider ID across quarters: 4,173
  (20.8% of all services)

  sample PA-chain changers:
    SE-00009638 touched 2 provider IDs
      Q42020data -> PR-40017687
      Q42019data -> PR-40017687
      Q42018data -> PR-40017687
      Q42017data -> PR-00005850
      Q42016data -> PR-00005850
      Q42015data -> PR-00005850
    SE-00009647 touched 2 provider IDs
      Q42020data -> PR-00005811
      Q42019data -> PR-00005811
      Q42018data -> PR-00005811
      Q42017data -> PR-00005811
      Q42016data -> PR-00005811
      Q42015data -> PR-00005811
    SE-00009650 touched 2 provider IDs
      Q42020data -> PR-00005811
      Q42019data -> PR-00005811
      Q42018data -> PR-00005811
      Q42017data -> PR-00005811
      Q42016data -> PR-00005811
      Q42015data -> PR-00005811
    SE-00009651 touched 3 provider IDs
      Q42020data -> PR-00002539
      Q42019data -> PR-00002539
      Q42018data -> PR-00002539
      Q42017data -> PR-00002539
      Q42016data -> PR-00002539
      Q42015data -> PR-00002539
    SE-00009668 touched 2 provider IDs
      Q42020data -> PR-00005883
      Q42019data -> PR-00005883
      Q42018data -> PR-00005883
      Q42017data -> PR-00005883
      Q42016data -> PR-00005883
      Q42015data -> PR-00005824

## Join check: NQAITS Service ID vs services.service_approval_number
  services in DB           : 18,223
  unique sids in NQAITS     : 20,078
  matched (DB ∩ NQAITS)    : 15,085  (82.78% of DB)
  in DB but not NQAITS      : 3,138
  in NQAITS but not DB      : 4,993

  sample DB-only (5):
    'SE-00016826'
    'SE-40022482'
    'SE-40027477'
    'SE-00017504'
    'SE-40025040'
  sample NQAITS-only (5):
    'SE-00003104'
    'SE-40005895'
    'SE-00003642'
    'SE-40020035'
    'SE-40004748'

## Sample value checks
  sampling sid: 'SE-00012646'
  in NQAITS quarters: 33 of 50
  provider history: 1 distinct provider(s)

## Ingest volume estimate
  total (sid, quarter) pairs across all sheets: 510,397
  avg quarters per service: 25.4
