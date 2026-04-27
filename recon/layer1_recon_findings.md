# Phase 2.5 Layer 1 — Recon Findings

_Generated: 2026-04-26 (session)_
_Scope: read-only inventory; no DB or file mutations._
_Inputs: `recon\layer1_db_findings.md`, `recon\layer1_files_findings.md`._

---

## 1. Executive summary

Layer 1 surfaces three changes vs the assumed shape in the 2026-04-26
plan and one foundational gap. Layer 2 sequence below is reordered
accordingly. No failure-condition trigger — the plan is workable but
the join key, schema home, and SA2 backfill prerequisite are all
different from what the plan assumed.

Headlines:

- **NQAITS is rich and complete** (50 quarterly sheets, 32 cols, all
  the way back to Q3 2013) — but the join key is `Service ID`
  (`SE-XXXXXXXX`), not "Service Approval Number". Same identifier,
  renamed across ACECQA sources. Plan ingest pattern stands; column
  spelling does not.
- **Foundational SA2 gap.** `services.sa2_code` is populated for
  0 / 18,223 active services. Every banding/catchment helper in
  Layer 3 depends on it. Layer 2 must backfill SA2 before any
  SA2-keyed ingest is useful.
- **`service_snapshots` does not exist.** Plan said
  "backfill `service_snapshots` _or_ new `nqs_history` table — pick
  one in recon". Decision: new `nqs_history` table. `service_history`
  also exists and is empty; reserved for non-NQS service-level
  history (transfers, status changes).
- **`financials` does not exist** — but `service_financials` and
  `entity_financials` do (both empty). Naming drift in plan; doesn't
  block anything because Phase 5 is far out.
- **One ABS workbook is corrupted** (`Population and People
  Database.xlsx` — missing `externalLinks` rels). Repair before
  ingest.
- **Births file is absent.** Re-source or defer.

---

## 2. DB state — snapshot/history table inventory

| Table | Rows | Status | Notes |
|---|---:|---|---|
| `service_snapshots` | — | **DOES NOT EXIST** | Plan-named; create as `nqs_history` instead |
| `service_history` | 0 | empty | Schema present; reserve for non-NQS service events |
| `entity_snapshots` | 0 | empty | 8 cols incl `nqs_profile_json` |
| `group_snapshots` | 0 | empty | 41 cols — fully spec'd, none populated |
| `regulatory_events` | 0 | empty | 10 cols; ingest source (per-state regulator scrape) is Phase 8 |
| `service_catchment_cache` | 0 | empty | 17 cols; populated by Tier 3 build |
| `service_tenures` | 0 | empty | 10 cols; carries property/lease (Tier 5) |
| `properties` | 0 | empty | 10 cols; freehold/lease detail |
| `people` | 0 | empty | 7 cols; director/PSC ingest (Phase 8-adjacent) |
| `person_roles` | 0 | empty | 9 cols |
| `financials` | — | **DOES NOT EXIST** | Schema uses `service_financials` + `entity_financials` (both 0 rows) |

For completeness — populated tables in DB:

| Table | Rows | Use |
|---|---:|---|
| `services` | 18,223 | Live snapshot (Tier 2 NQS Q4 2025) |
| `entities` | 7,143 | Provider entities |
| `groups` | 4,187 | Ownership graph parents |
| `portfolios` | 4,187 | Operator portfolio shells |
| `evidence` | 10,263 | Merge-decision evidence rows |
| `link_candidates` | 823 | Pending merge proposals |
| `brands` | 349 | Discovered brands |
| `audit_log` | 124 | All schema/ingest mutations to date |
| `training_completions` | 768 | NCVER ECEC ingest (Phase 1.5) |

Net: every snapshot/history/regulatory table that Phase 2.5 wants to
read from is empty. Layer 2 has to populate them, not augment them.

---

## 3. Silent-bug audit scope

| Bug | Scope | Implication |
|---|---:|---|
| `sa2_code` NULL on active services | **18,223 / 18,223** | **FOUNDATIONAL.** No service has SA2. Backfill from postcode_to_sa2_concordance + lat/lng disambiguation is Step 1 of Layer 2 |
| `seifa_decile` NULL on active services | **828 / 18,223** | 4.5% — modest gap. Likely services in SA2s missing from the SEIFA-decile lookup. Inspect after SA2 backfill |
| `last_transfer_date` populated | 5,826 / 18,223 | 32% of active services have a transfer date. Brownfield-detection re-audit candidate set is **5,826 services**. Operator-page brownfield counts likely understated wherever the buggy YYYY-MM-DD parser was used |
| Entities with active services and `group_id IS NULL` | **2,320 entities** | Self-group backfill candidate set. Includes Radford College Limited and similar independent-school operators. Plan: one entity = one group, `ownership_type='independent_school'` (or appropriate enum) |

---

## 4. Raw-file readiness — `abs_data\`

| File | Size | Status | Layer 2 readiness |
|---|---:|---|---|
| `NQAITS Quarterly Data Splits (Q3 2013 - Q4 2025).xlsx` | 138 MB | **READY** with caveats | 50 data sheets, 32 cols each. Per-sheet header normalisation required (column-name drift across years). Join key is `Service ID` not "Service Approval Number". |
| `SALM Smoothed SA2 Datafiles - December quarter 2025.xlsx` | 2.4 MB | **READY** | 3 sheets (rate, count, labour-force). Headers on row 3, data from row 4. SA2 Code (2021 ASGS) is the join key. Wide format, 61 quarterly columns Dec-2010 → Dec-2025. ETL to long format on ingest. |
| `SA2_2021_AUST.xlsx` | 0.25 MB | **READY** | Clean; `SA2_CODE_2021`+name+SA3/SA4/GCCSA/state hierarchy. |
| `POA_2021_AUST.xlsx` | 18 MB | **READY** | Meshblock→postcode boundaries. Use only if the existing concordance proves lossy. |
| `postcode_to_sa2_concordance.csv` | 51 KB | **READY** with caveats | Simple POSTCODE→SA2_CODE. **1:1 mapping** — real postcodes spanning multiple SA2s will be assigned arbitrarily. SA2 backfill should fall back to lat/lng for multi-SA2 postcodes. |
| `meshblock-correspondence-file-asgs-edn3.xlsx` | 14.6 MB | READY | ASGS edition 3 crosswalks. Likely overkill for current scope; defer. |
| `Family and Community Database.xlsx` | 15.6 MB | READY | ABS Data by Region 2011–25, 3 sheets (Contents + 2 tables) |
| `Income Database.xlsx` | 12.7 MB | READY | ABS Data by Region 2011–25, 4 sheets (Contents + 3 tables) |
| `Education and employment database.xlsx` | 14.3 MB | READY | ABS Data by Region 2011–25, 3 sheets (Contents + 2 tables) |
| `Population and People Database.xlsx` | 28.3 MB | **CORRUPTED** | openpyxl errors on missing `externalLink2.xml.rels`. Repair: open in Excel, break external links, save-as. Or use `xlrd`/`pandas` with engine fallback. |
| `Economic and Industry Database.csv` | 2.7 KB | **MISSING DATA** | File contains the Contents page only. The actual `.xlsx` was not downloaded. Re-fetch from ABS. |
| `NQS Data Q4 2025.XLSX` | 10.7 MB | INGESTED | Tier 2 source — already in DB |
| `NCVER_ECEC_Completions_2019-2024.xlsx` | 15 KB | INGESTED | Phase 1.5 — already in DB |
| **Births data (ABS Cat 3301.0)** | — | **ABSENT** | Not in `abs_data\`, repo root, `data\`, or `Downloads`. Either re-fetch (TableBuilder Pro likely required for SA2 detail) or defer. |
| `module2b_catchment.py` | 30 KB | **MISPLACED** | Production script — postcode→SA2, SEIFA, supply ratio enrichment for `run_daily.py` chain. Move to repo root or `pipeline/`. **Logic is reusable for Layer 3 banding helpers.** |

---

## 5. NQAITS — schema deep dive (the big unlock)

50 data sheets (`Q42025data` … `Q32013data`), 32 columns each.
3 metadata sheets (`Contents`, `Data Descriptions`, `Explanatory Notes`).

Columns present every quarter (canonical names — normalise on ingest):

| Field | Notes |
|---|---|
| Service ID | `SE-XXXXXXXX`. Centre-following identifier. **The join key.** |
| Service Name | Display name |
| Provider ID | `PR-XXXXXXXX`. Captures PA chain — when this changes between quarters for the same Service ID, that's an ownership transfer |
| Provider Name | |
| Provider Management Type | Raw ACECQA (needs the same enum mapping flagged for Decision 9) |
| Managing Jurisdiction | NB. trailing space in Q3 2013 sheet. Strip whitespace on ingest |
| Service Type | "Centre-Based Care" etc |
| Approval Date / ApprovalDate | Real datetime. Spelling drift between quarters |
| SEIFA | Decile (numeric or string) |
| ARIA / ARIA+ | Label string. Spelling drift — Q3 2013 uses `ARIA+`, Q1 2020 uses `ARIA`. Tier 2 already saw both code and label forms in the live NQS file |
| Maximum total places | |
| NQS Version | "NQS (2012)" etc |
| Final Report Sent Date | Real datetime |
| Overall Rating | "Meeting NQS" / "Working Towards NQS" / etc — full strings |
| Quality Area 1..7 | Full rating strings |
| Service sub-type (ordered counting method) | "OSHC" / "LDC" / etc |
| Long Day Care / PreschoolKindergarten Stand Alone / PreschoolKindergarten Part of a School / OSHC BeforeSchool / OSHC After School / OSHC Vacation Care / Nature Care Other | Yes/No flags per service-type indicator |
| Postcode | |
| Latitude / Longitude | Decimal degrees |

**Header-normalisation map** (build once, apply per-sheet):

```
'ARIA' -> aria
'ARIA+' -> aria
'ApprovalDate' -> approval_date
'Approval Date' -> approval_date
'Managing Jurisdiction' -> managing_jurisdiction  # strip trailing space
'Managing Jurisdiction ' -> managing_jurisdiction
... (rest 1:1 lower_snake)
```

**Verification step before bulk ingest:** spot-check that NQAITS
`Service ID` values join cleanly to `services.service_approval_number`
on at least 95% of Q4 2025 NQAITS rows. Tier 2 hit 98.1% on the NQS
Q4 file matching the same column; expect parity. If not, replan join
(could need a fuzzy lookup on Service Name + Postcode).

---

## 6. Sequenced Layer 2 ingest plan with effort

Reordered from the plan to put SA2 backfill first. Effort in
Patrick-sessions (1 session ≈ 2-3 hours focused work).

| # | Step | Effort | Depends on | Output |
|---|---|---:|---|---|
| 1 | **SA2 backfill of `services.sa2_code`** via `postcode_to_sa2_concordance.csv`, with lat/lng fallback for postcodes spanning multiple SA2s | 0.25 | — | services.sa2_code populated for ~99% of 18,223 active services. Audit query post-ingest. |
| 2 | Self-group backfill for 2,320 orphan entities (one entity → one group, ownership_type by heuristic) | 0.25 | — | groups +2,320 rows; entities.group_id 100% populated |
| 3 | Brownfield re-classification audit — re-parse `last_transfer_date` (DD/MM/YYYY) across the 5,826 candidate services and any operator/centre-page derived field that consumed it | 0.5 | — | Audit row + corrected operator-page brownfield counts |
| 4 | **NQAITS quarterly historical ingest** — 50 quarters → new `nqs_history` table, keyed on (service_id, quarter). Captures `provider_id` per row so the PA chain is materialisable. ~½M rows. Standard ingest pattern (dry-run, transaction, audit_log, invariant check). | 1.0 | step 1 (so SA2 enrichment can be cross-checked) | nqs_history populated; PA-chain queryable |
| 5 | SALM unemployment ingest → `abs_sa2_unemployment_quarterly` (sa2_code, year_qtr, unemployment_rate, unemployment_count, labour_force) | 0.25 | step 1 | Quarterly SA2 unemployment, 2010-Q4 through 2025-Q4 |
| 6 | ABS ERP at SA2 ingest → `abs_sa2_erp_annual`. Requires identifying which sheet inside `Population and People Database.xlsx` carries the ERP age × sex breakdown — and **fixing the corrupted workbook** before ingest | 0.5 | step 1; corrupted-workbook repair | Annual under-5 cohort series per SA2 |
| 7 | Census 2021 static enrichment (Family / Income / Education-Employment) → either single normalised table or extension of `service_catchment_cache` (deferred until Tier 3 cache is built) | 0.5 | step 1 | Demographic enrichment per SA2 |
| 8 | Births by SA2 — **BLOCKED** until file sourced | — | re-fetch from ABS | abs_sa2_births_annual |
| 9 | Economic and Industry data — **BLOCKED** until full .xlsx sourced (current `.csv` is metadata only) | — | re-fetch from ABS | (defer) |

**Total in-scope Layer 2 effort: ~3.0 sessions** (vs the plan's 1-2,
because SA2 backfill, self-group backfill, brownfield audit, and the
ABS workbook repair all add up).

---

## 7. Decisions needed from Patrick before Layer 2 starts

1. **Confirm `nqs_history` as the new table name** (vs hijacking
   `service_history` — recommend keeping `service_history` reserved
   for non-NQS event log).
2. **Births and Economic and Industry datasets**: re-fetch this
   session, or defer to a later phase? Both are currently blockers
   if needed for Layer 3+.
3. **Independent-school self-group backfill**: confirm
   `ownership_type='independent_school'` is the right default for
   the 2,320 orphan entities, or whether they should be classified
   case-by-case via name-pattern heuristics first.
4. **Corrupted Population and People workbook**: repair via Excel
   round-trip is fastest (open, "break links", save-as) — Patrick
   to run that on the desktop, or attempt programmatic repair?

---

## 8. Process notes for next session

- `module2b_catchment.py` should move out of `abs_data\` to repo root
  (or a `pipeline/` folder). Lift its postcode→SA2 logic into the
  Layer 2 step 1 backfill script directly — don't re-derive.
- ABS Data by Region workbooks all share the same template (Contents
  + Table N sheets, header on a non-first row). One reader helper
  covers all four.
- Layer 2 step 4 NQAITS read should use `openpyxl` `read_only=True`;
  the 138MB file is fine but slow — budget ~2 minutes per full pass.
- Consider committing the recon outputs (`recon\layer1_*.md`) so
  the findings are versioned alongside the ingest scripts that act
  on them.

---

_End Layer 1 recon._
