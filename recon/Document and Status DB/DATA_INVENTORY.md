# Data Inventory

Source data files, database tables, refresh policy, and provenance per dataset. This document is the authoritative inventory of what data the project holds. Standard 27 prohibits requesting a download without first checking this file.

Last updated: 2026-04-28b.

---

## 1. Source files (`abs_data/`)

All files are local-disk copies of public ABS or government data, downloaded by the operator. Files are gitignored (large). Filename, size, and source are recorded here.

### Geographic reference data

| File | Size | Source | Use |
|---|---|---|---|
| `ASGS_2021_Main_Structure_GDA2020.gpkg` | 931 MB | ABS ASGS Edition 3 (2021) | SA2 polygon spatial joins (Step 1b, Step 1c, sa2_cohort) |
| `ASGS_Ed3_2021_RA_GDA2020.gpkg` | 40 MB | ABS ASGS Edition 3 (2021) Remoteness Areas | SA2 → RA assignment in `sa2_cohort` |
| `meshblock-correspondence-file-asgs-edn3.xlsx` | small | ABS | QLD-only (STD-33). Held but not used for national lookup. |

### Demographic data (ABS Data by Region — WIDE format, STD-22)

| File | Size | Source | Use |
|---|---|---|---|
| `Population and People Database.xlsx` | medium | ABS Cat 1410.0.55.001 | ERP, total population, fertility (TFR) |
| `Income Database.xlsx` | medium | ABS Cat 1410.0.55.001 | Median employee/household/total income at SA2 |
| `Education and employment database.xlsx` | medium | ABS Cat 1410.0.55.001 | LONG format (DEC-58, STD-23). Persons LFP, employment status |

### Births (per-state-split TRI-METRIC layout, STD-29, DEC-64)

| File | Size | Source | Use |
|---|---|---|---|
| `Births_SA2_2011_2024.xlsx` | 928 KB | ABS Cat 3301.0 Table 2 | Annual SA2-level births. 8 sheets per state. |

### Labour-market data

| File | Size | Source | Use |
|---|---|---|---|
| `SALM Smoothed SA2 Datafiles ... .xlsx` | medium | JSA SALM (Small Area Labour Markets) | Quarterly smoothed unemployment, SA2 level |
| `internet_vacancies_anzsco4_*.xlsx` (×2) | small | JSA Internet Vacancy Index | ECEC workforce demand signal (ANZSCO 4211, 2411) |

### Census 2021

| File | Size | Source | Use |
|---|---|---|---|
| `census_tsp_*.zip` (extracted) | 45 MB compressed | ABS Census 2021 Time Series Profile | Sex-disaggregated LFP via T33A–H (DEC-60) |

### Workforce

| File | Size | Source | Use |
|---|---|---|---|
| `ncver_training_completions_*.xlsx` | small | NCVER | Training completions by ANZSCO ECEC codes, state-level |

---

## 2. Database tables (`data/kintell.db`)

35 tables as of 2026-04-28b. Grouped by family.

### Identity and ownership

| Table | Rows | Purpose |
|---|---|---|
| `groups` | ~13K | Group-level (highest in hierarchy DEC-1) |
| `entities` | ~16K | Legal entity per (provider approval × state) |
| `services` | ~18.2K | Centre-level. Includes `lat`/`lng` (DEC-46), `sa2_code` (DEC-70), `sa2_name`, `aria_plus`, NQS fields |
| `accepted_merges` | ~9K | Merge decisions accepted via review tool |
| `proposed_merges` | ~12K | Pending merge proposals (read-only by review tool) |
| `brand_*` | mixed | Brand prefix tables for the linker (DEC-6 signal 1) |

### Quality and regulatory

| Table | Rows | Purpose | Source |
|---|---|---|---|
| `nqs_history` | 807,526 | Quarterly NQS ratings 2014–2026 | NQAITS quarterly extract |
| `nqaits_ingest_run` | 1+ | Provenance row per NQAITS ingest (DEC-21) | — |

### Workforce

| Table | Rows | Purpose | Source |
|---|---|---|---|
| `model_assumptions` | 13+ | Single source of truth for assumption values (P-3) | Hand-curated, DB-resident |
| `metric_definitions` | 6+ | Definitions for metric IDs used across pages | Hand-curated |
| `training_completions` | 768 | NCVER training completions by ANZSCO/state/year | NCVER |
| `training_completions_ingest_run` | 1+ | Provenance + qualification-transition caveat (DEC-24) | — |

### Demographic (Phase 2.5 Layer 2)

| Table | Rows | Purpose | Source |
|---|---|---|---|
| `abs_sa2_erp_annual` | 88,344 | Annual ERP at SA2, 2,454 SA2s, 9 years, 4 age groups | ABS Cat 3218.0 / Population Database |
| `abs_sa2_births_annual` | ~34,300 | Annual SA2 births, 2011–2024 | ABS Cat 3301.0 Table 2 |
| `abs_sa2_unemployment_quarterly` | substantial | Smoothed unemployment, quarterly, 2010-Q4 → 2025-Q4 | JSA SALM |
| `abs_sa2_education_employment_annual` | 203,527 | LONG-format from EE Database | ABS Data by Region |
| `abs_sa2_income_annual` | substantial | Median employee/household/total income | ABS Income Database |
| `census_lfp_females`, `census_lfp_males` | per-SA2 | Sex-disaggregated LFP from Census 2021 TSP T33 (DEC-60) | Census 2021 TSP |
| `jsa_ivi_*` | small | Internet Vacancy Index by ANZSCO/state | JSA |

### Banding (Phase 2.5 Layer 3)

| Table | Rows | Purpose | Source |
|---|---|---|---|
| `sa2_cohort` | 2,473 | SA2 → state, RA, ra_band; centroid-in-RA spatial join (DEC-66) | ABS RA GeoPackage + Main Structure GeoPackage |
| `layer3_sa2_metric_banding` | 23,946 | Latest-year banding per (sa2, metric); long format (STD-32, DEC-68) | Computed from `abs_sa2_*` tables |

### Catchment

| Table | Rows | Purpose |
|---|---|---|
| `service_catchment_cache` | **0** | Schema in place; population is Layer 2.5 work, gated on Layer 4.3 calibration function |

### Audit

| Table | Rows | Purpose |
|---|---|---|
| `audit_log` | 137 | One row per mutation; schema per DEC-62 |

---

## 3. Refresh policy

| Source | Cadence | Trigger | Manual or scripted |
|---|---|---|---|
| ABS ERP | Annual | New ABS release (~quarterly into a new year) | Manual download → re-run Step 6 apply |
| ABS Births | Annual | New ABS Cat 3301.0 release | Manual download → re-run Step 8 apply |
| ABS Income / EE / Population Database | Annual + on Census release | New Data by Region edition | Manual download → re-run Step 5b/5b'/5c apply |
| Census 2021 TSP | Per Census cycle (next: 2026) | New Census release | Re-verify table numbering (DEC-60), re-run Step 5b' |
| JSA SALM | Quarterly | New SALM publication | Manual download → re-run Step 5 apply |
| JSA IVI | Monthly+ | New IVI publication | Manual download → re-run Step 5c apply |
| NCVER training-completions | Annual | New NCVER release | Manual download → re-run Phase 1.5 |
| NQAITS | Quarterly | Operator-initiated (no automated feed) | Manual extract → re-run nqaits_ingest |

After any source refresh: re-run the corresponding apply script (idempotent per P-6); re-run `layer3_apply.py` if a banded source table changed (DEC-68 "refresh pattern").

---

## 4. Provenance per dataset

Every ingest writes one row to `audit_log` (P-6, DEC-62). Every ingest also writes one row to its `*_ingest_run` table where the table exists (DEC-21), capturing source identifier, ingest timestamp, row counts, and run-specific caveats.

Caveats currently captured in `*_ingest_run` rows:
- NCVER training-completions: qualification-transition trough at 2023 (DEC-24)
- ABS confidentialization: derived rates may exceed 100 in low-population SA2s (DEC-59)
- Cross-product Census rates: `ee_lfp_persons_pct` vs T33-derived persons LFP differ; do not reconcile (DEC-61)

---

## 5. Backups

Cumulative DB backups in `data/`, all gitignored under `data/kintell.db.backup_*`:

| Backup | Size | Anchor |
|---|---|---|
| `kintell.db.backup_pre_step6_20260427_163342` | 467 MB | Pre-Step 6 (ABS ERP ingest) |
| `kintell.db.backup_pre_step5_20260427_171439` | 477 MB | Pre-Step 5 (SALM unemployment) |
| `kintell.db.backup_pre_step5c_20260427_172338` | 489 MB | Pre-Step 5c (JSA IVI) |
| `kintell.db.backup_pre_step5b_20260427_180757` | 490 MB | Pre-Step 5b (Census income subset) |
| `kintell.db.backup_pre_step5b_prime_20260427_204131` | 519 MB | Pre-Step 5b' (Census LFP) |
| `kintell.db.backup_pre_step1b_20260427_213320` | 524 MB | Pre-Step 1b (NULL sa2_code fill) |
| `kintell.db.backup_pre_step8_<ts>` | ~524 MB | Pre-Step 8 (births ingest) |
| `kintell.db.backup_pre_sa2_cohort_20260428_120804` | 526 MB | Pre-sa2_cohort build (DEC-66) |
| `kintell.db.backup_pre_layer3_20260428_122241` | 527 MB | Pre-Layer 3 banding |
| `kintell.db.backup_pre_step1c_20260428_165521` | 531 MB | Pre-Step 1c (SA2 polygon overwrite, DEC-70) |

**Total: ~5.0 GB.** Pruning older backups is a P1.5 housekeeping task — the cumulative size approaches the threshold where a single git operation can time out. Recommend retaining the most recent 3 backups plus the pre-major-mutation anchors (pre_sa2_cohort, pre_layer3, pre_step1c).

Frontend file backups in `docs/`, also gitignored under `*.v?_backup_*`:
- `docs/operator.html.v6_backup_*`, `v7_backup_*` — accumulated from patcher runs (DEC-28)

---

## 6. Standalone artefacts (not in main DB)

### Starting Blocks pilot
A separate SQLite DB sits in `G:\My Drive\Patrick's Playground\childcare_market_spike\` with 4 tables (`pilot_target`, `raw_payload`, `centre`, `centre_fee`) and ~11K `centre_fee` rows across 130 centres in 3 pilot SA2s. **Schema version `v1.0-pilot`.**

This is not integrated into `kintell.db`. Integration is gated on identity resolution work (Phase 8 — `MODULE_SUMMARY_Childcare_Market_Data_Capability.md` records details). The pilot DB must be moved off Google Drive before scaling — SQLite + Drive sync produced a transient write loss on 1/130 rows during the pilot.

---

## 7. Open data quality items

See `OPEN_ITEMS.md` for the live list. Summary at last update:

- 18 services with no lat/lng need geocoding fix (DEC-63)
- 2 services at lat=0,lng=0 need manual cleanup (DEC-63)
- 9 cross-state SA2 mismatches remain post-Step-1c (boundary enclaves like Jervis Bay; DEC-70)
- `service_catchment_cache` is empty (Layer 2.5 work pending)
- LFP source is Census-only (3 points 2011/2016/2021); SALM probe in Layer 4.3 may upgrade to ~60 quarterly points
- `participation_rate` not measured at SA2 — calibration function required (STD-34 staged)
