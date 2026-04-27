# Phase 2.5 Layer 2 Step 3 — Brownfield Audit Findings
_Generated: 2026-04-26T15:28:31_

Read-only characterisation of date-format scope across the two
transfer/approval date columns that drive brownfield classification.
Source bug (this session): centre_page.py v1's `_parse_date()` only
recognised YYYY-MM-DD; DD/MM/YYYY values silently fell through and
brownfield centres were misclassified as greenfield.

## Column existence
  - last_transfer_date             PRESENT
  - approval_granted_date          PRESENT

## Active services total: 18,223

## `last_transfer_date`
  format distribution (active services):
    null_or_empty         12397  ( 68.0%)
    DD/MM/YYYY             5826  ( 32.0%)
  sample values per format:
    DD/MM/YYYY           ['03/02/2020', '22/04/2013', '01/01/2026']

## `approval_granted_date`
  format distribution (active services):
    DD/MM/YYYY            18222  (100.0%)
    null_or_empty             1  (  0.0%)
  sample values per format:
    DD/MM/YYYY           ['01/01/2012', '01/01/2012', '01/01/2012']

## Cross-tab: approval_granted_date format X last_transfer_date format
  approval_granted_date \ last_transfer_date
                              DD/MM/YYYY   null_or_empty
  DD/MM/YYYY                          5826           12396
  null_or_empty                          0               1

## Misclassification scope (if parser is YYYY-MM-DD-only)

Brownfield = service has a non-null transfer_date older than approval_granted.
A YYYY-MM-DD-only parser fails on DD/MM/YYYY values, treating them as null.
So: services with DD/MM/YYYY in last_transfer_date are mis-marked greenfield.

  active services with any last_transfer_date    : 5,826
  active services with DD/MM/YYYY last_transfer  : 5,826
  -> services likely mis-marked greenfield by buggy parser: 5,826

  active services with DD/MM/YYYY approval_granted: 18,222
  -> services with unparsed approval date by buggy parser: 18,222

## Sample of likely-misclassified services (showing 10)
  id=2      'Mawson Out of School Hours Care' transfer=03/02/2020 approval=01/01/2012
  id=3      'Kids Biz Holidays and Sports' transfer=22/04/2013 approval=01/01/2012
  id=4      'Bright Lights School Aged program' transfer=01/01/2026 approval=01/01/2012
  id=7      'YWCA Miles Franklin Out of School Hour C' transfer=02/02/2026 approval=01/01/2012
  id=15     'St Anthony's Parish Outside of School Ho' transfer=01/01/2025 approval=01/01/2012
  id=16     'St Clare of Assisi  Outside of School Ho' transfer=01/01/2025 approval=01/01/2012
  id=17     'St Francis of Assisi Outside of School H' transfer=01/01/2025 approval=01/01/2012
  id=18     'St Peter and Paul Out of School Hours Ca' transfer=06/01/2025 approval=01/01/2012
  id=19     'St Thomas Aquinas OSHClub' transfer=07/07/2016 approval=01/01/2012
  id=28     'TeamKids - Nicholls OSHC' transfer=13/01/2025 approval=01/01/2012
  (total candidates: 5,826)

## Code-path audit checklist

The data shows DD/MM/YYYY values exist; impact depends on parser robustness
in each consuming code path. Patrick to confirm format handling in:
  - operator_page.py        (uses last_transfer_date for brownfield logic)
  - generate_dashboard.py   (places-over-time, growth metrics)
  - centre_page.py v2       (already fixed — handles DD/MM/YYYY)
  - any module*.py that reads services date columns

Recommended grep:
  Get-ChildItem -Recurse -Filter *.py | Select-String 'last_transfer_date|approval_granted_date'
