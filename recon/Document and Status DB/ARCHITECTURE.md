# Architecture

The Kintell platform's structural design — visual systems, page topology, data layer, and the boundaries between them. This document changes when architecture changes; it is not a session log.

---

## 1. Page topology

The platform is a multi-page web application served by `review_server.py`. Pages share a common dark-theme styling base but split into two visual systems (see §2). Each page is a static `docs/*.html` file rendered server-side from a JSON payload.

| Page | File | Purpose | Visual system |
|---|---|---|---|
| Industry | `docs/index.html` | Sector-level dashboard. Trend intelligence on workforce, demand, supply. | System B |
| Dashboard | `docs/dashboard.html` | Trend dashboard surface. | System B |
| Operator | `docs/operator.html` | Operator (group) summary. Quality, workforce, catchment context. | System A |
| Centre | `docs/centre.html` | Single-centre detail page. Now / Trajectory / Position per metric. | System A + Chart.js bridge |
| Review | `docs/review.html` | Merge-review tool with brand-cluster cards. | System A |

The Catchment surface is **deprecated**. Catchment data lives on the centre page (Layer 4.2-A) and the operator page rather than as a standalone tab.

### Cross-page navigation

- Operator page → Centre page: each row in the operator's centres table opens `centre.html?id=<service_id>` in a new tab (operator.html v9, DEC-30 audit comment).
- Centre page → Operator page: header link from centre name to parent group's operator page.
- Review page → Operator page: cluster card links navigate to operator detail.

---

## 2. Visual systems

Two visual systems coexist by design (DEC-71). The boundary is functional, not aesthetic.

### System A — operator family
- **Files:** `centre.html`, `operator.html`, `review.html`
- **Palette:** Palette A. Accent `#4a9eff`. 18 tokens. See §3.
- **Charts:** bespoke inline SVG.
- **Used for:** dense fact rows, decile strips, position indicators, chip strips, cohort histograms — drilldown and detail surfaces.

### System B — dashboard family
- **Files:** `dashboard.html`, `index.html` (the industry page)
- **Palette:** Palette B. Accent `#3d7eff`, accent2 `#00c9a7`, hot `#e05c3a`. 16 tokens. See §3.
- **Charts:** Chart.js 4.4.0 from CDN (`cdn.jsdelivr.net/npm/chart.js@4.4.0`).
- **Helpers:** `makeDataset`, `makeLine`, `makeOpts`, `trimNulls`, `makeCompactPlugin`, `makeFullPlugin`.
- **Used for:** trend visualisation, multi-series, time-range filtering — industry intelligence surfaces.

### The bridge: centre.html
The centre page (`centre.html`) bridges the two systems. It imports Chart.js for trend rendering only. Decile strips, cohort histograms, chip strips, decision strips remain bespoke SVG.

**Boundary rule (DEC-71):** trends use Chart.js; position indicators use SVG.

The bespoke `_kintell_makeOpts` and `_kintell_makeLine` helpers in `centre.html` are verbatim from `index.html`, so trajectory chart behaviour matches the industry page exactly. `_CHART_INSTANCES` and `_CHART_PENDING` registries handle the string-template render → DOM-insert → chart-init sequence.

### Stroke colour conventions (System B trends and the bridge)
Per-metric stroke colour follows the `index.html chart-catch-combined` convention:

| Metric family | Colour |
|---|---|
| Population (under-5, total, births) | `#00c9a7` teal (accent2) |
| Unemployment | `#e05c3a` hot |
| Income trio | `#3d7eff` blue (accent) |
| LFP triplet | `#9b59b6` purple |

Stroke colour does NOT carry valence (DEC-71, DEC-72). Direction of "good vs concerning" lives only in band-copy text per STD-34.

### Why two systems persist
The visual consistency audit (`recon/visual_consistency_audit.md`) considered three options:
1. Chart.js on `centre.html` for trends only — chosen.
2. Whole-repo migration to one system — rejected (no payback; the systems serve different functional purposes).
3. Keep bespoke, restyle to match Chart.js — rejected (commercial framing strengthens the case for standard-library charts).

---

## 3. Palette tokens

### Palette A (System A)
Accent `#4a9eff`. The 18 tokens cover background, surface, panel, divider, text-primary, text-secondary, text-muted, accent, accent-soft, accent-outline, success, warn, danger, info, severity-low, severity-mid, severity-high, severity-critical.

The decile-strip gradient on Palette A is single-hue blue, with saturation steps at:
- Deciles 1–3: 6% saturation (low band)
- Deciles 4–6: 13% saturation (mid band)
- Deciles 7–10: 20% saturation (high band)
- Self cell (the SA2 being viewed): 32% saturation + accent outline

### Palette B (System B)
Accent `#3d7eff`, accent2 `#00c9a7`, hot `#e05c3a`. The 16 tokens cover similar concerns plus the trend-stroke palette referenced in §2.

---

## 4. Centre page composition

The centre page is the most complex surface and the canonical example of the three-temporal-mood pattern (DEC-32).

### NOW block — point-in-time observations
- NQS rating + inspection cadence (five-state classification per DEC-34)
- Places + service sub-type + management type
- Catchment context (SEIFA + ARIA + SA2 — single facts, no peer position)
- Tenure (acquisition type + original approval + last transfer)

### POSITION block — peer-relative position
Currently 10 Layer 3-backed metrics in two cards:

**Population card (4 metrics, 1 deferred):**
- `sa2_under5_count` — banded against same-state cohort
- `sa2_total_population` — banded against state×remoteness
- `sa2_births_count` — banded against state×remoteness
- `sa2_under5_growth_5y` — DEFERRED (placeholder)

**Labour Market card (7 metrics, 1 deferred):**
- `sa2_unemployment_rate` — banded against same-state cohort
- `sa2_median_employee_income` — banded against same-remoteness cohort
- `sa2_median_household_income` — banded against same-remoteness cohort
- `sa2_median_total_income` — banded against same-remoteness cohort
- `sa2_lfp_persons` — banded against state×remoteness
- `sa2_lfp_females` — banded against state×remoteness
- `sa2_lfp_males` — banded against state×remoteness
- `jsa_vacancy_rate` — DEFERRED (state-level, not SA2)

### Per-row UI (each Position metric)
```
┌─ Title with cohort scope inline ───────── value · period · OBS
│  e.g. "Under-5 population (vs WA)"            1,080 (2024) [OBS]
├─ Trajectory chart (Chart.js; sparkline ≥7 pts, dot trajectory <7)
├─ Headline: Decile X · band · n=N
├─ Cohort distribution histogram (20 raw_value bins, self-bin highlighted)
├─ Gradient decile strip (10 cells, single-hue blue ramp, you-are-here)
├─ Low / Mid / High band chips (active band highlighted)
└─ DER + COM badges (provenance + commentary rule)
```

### Global trend window
Above the Population card sits a global button strip:
```
TREND WINDOW: [3Y] [5Y] [10Y] [All]   (default: All)
```
The window is applied per-metric relative to that series' most recent point — so the same "5Y" click renders different absolute date ranges for unemployment (ending 2025-Q4) vs LFP (ending 2021). DEC-73.

### Catchment metrics card (Layer 4.2-A — designed, not yet shipped)
A new `renderCatchmentMetricsCard` will render four catchment ratios with the same Position-row treatment:
- `child_to_place` — children per place (high_is_positive)
- `adjusted_demand` — demand per child × attendance × participation
- `capture_rate` — modelled capture share
- `demand_supply` — adjusted demand / places (high_is_positive)

The four ratios depend on a calibration function (`catchment_calibration.py`, STD-34 staged) that returns per-SA2 `participation_rate` with documented rule text.

---

## 5. Layer architecture (Phase 2.5 pipeline)

The Phase 2.5 work — centre page buyer's-lens enhancement — runs in five layers. Each layer has its own scripts, recon artefacts, and audit trail.

| Layer | Purpose | Status |
|---|---|---|
| Layer 1 | Schema reconnaissance + silent-bug audit | COMPLETE 2026-04-26 |
| Layer 2 | Historical data ingest (Steps 1, 1b, 1c, 2, 3, 4, 5, 5b, 5b', 5c, 6, 8) | COMPLETE through Step 1c |
| Layer 2.5 | Catchment cache build (population) | NOT STARTED — gated on Layer 4.3 calibration |
| Layer 3 | Banding infrastructure (`sa2_cohort` + `layer3_sa2_metric_banding`) | COMPLETE 2026-04-28 |
| Layer 3.x | Catchment metric banding | NOT STARTED — gated on Layer 2.5 |
| Layer 4 | Centre page Now + Position rendering | COMPLETE through 4.2-B-fix2 |
| Layer 4.1 | Cohort scope inline (DEC-69) | COMPLETE |
| Layer 4.2-B | Trajectory + cohort histogram + gradient strip | COMPLETE |
| Layer 4.2-B-fix | Chart.js trajectory swap (DEC-71 implementation) | COMPLETE |
| Layer 4.2-B-fix2 | Global trend-window buttons (DEC-73) | COMPLETE |
| Layer 4.2-A | Catchment data on centre page | DESIGNED — gated on Layer 4.3 + Layer 2.5 |
| Layer 4.3 | Calibration + intent copy + per-chart buttons | DESIGNED — awaiting decision closure |
| Layer 4.4 | New ingests (NES, parent-cohort, schools) | DEFERRED |
| Layer 5 | Doc restructuring (this work) | COMPLETE 2026-04-28 |

See `ROADMAP.md` for the V1 path remaining.

### Layer-to-table mapping

| Layer | Tables / artefacts |
|---|---|
| Layer 2 | `services` (mutation), `abs_sa2_*_*` (multiple ingests), `nqs_history`, `audit_log` |
| Layer 2.5 | `service_catchment_cache` (currently empty) |
| Layer 3 | `sa2_cohort`, `layer3_sa2_metric_banding` |
| Layer 4 | `centre_payload_v4` schema (computed at request time, not stored) |

### The Decision-65 pattern in this architecture
Every layer follows P-1: probe → design → decide → code. Each layer's `recon/` artefacts are the visible expression of this:
- `layer<N>_<step>_probe.py` (read-only) → `recon/<step>_probe.md`
- `recon/<step>_design.md` (decisions documented)
- `layer<N>_<step>_diag.py` (pre-flight invariants) → `recon/<step>_diag.md`
- `layer<N>_<step>_apply.py` (mutating, dry-run default)
- `layer<N>_<step>_spotcheck.py` (post-mutation validation)

---

## 6. Data layer

### Database
SQLite. Single file: `data/kintell.db`. 35 tables as of 2026-04-28b.

### Major table families

**Identity and ownership (Phase 0a–1):**
`groups`, `entities`, `services`, `accepted_merges`, `proposed_merges`, `brand_*`

**Quality and regulatory (Phase 1):**
`nqs_history` (807,526 rows, 2014–2026 quarterly), `services.qa1`–`qa7`, `nqaits_ingest_run`

**Workforce (Phase 1 Module 2):**
`model_assumptions` (educator ratios, calibration constants), `metric_definitions`, `training_completions`, `training_completions_ingest_run`

**Demographic and labour (Phase 2.5 Layer 2):**
`abs_sa2_erp_annual`, `abs_sa2_births_annual`, `abs_sa2_unemployment_quarterly`, `abs_sa2_education_employment_annual`, `abs_sa2_income_annual`, `census_lfp_*`, `jsa_ivi_*`, `salm_sa2_*`

**Banding (Phase 2.5 Layer 3):**
`sa2_cohort` (2,473 rows), `layer3_sa2_metric_banding` (23,946 rows; one row per (sa2, metric) for latest year — DEC-68)

**Audit:**
`audit_log` (137 rows as of 2026-04-28b — see `DATA_INVENTORY.md` for current count)

### Centre payload schema
The centre page is rendered from a computed JSON payload `centre_payload_v4`. Schema versioning (`v3` → `v4` etc.) follows STD-03; the version string is embedded in the payload and checked by the renderer.

### Data sourcing convention (DEC-35)
- Annual ERP at SA2 → time-series of children aged 0–5
- Census 2021 → static enrichment (income, family, education/employment)
- Births by SA2 → leading-indicator demand signal (annual; ABS Cat 3301.0)
- SALM Smoothed → quarterly unemployment at SA2

Each becomes an SA2-keyed annual or quarterly table joined to services via `services.sa2_code`.

---

## 7. Audit and recovery

### audit_log (DEC-62, STD-11)
Every mutation produces one row. Schema fully specified in DEC-62. INSERT pattern hardcoded 7-column per STD-11. `actor` is the script name; `action` follows `<source>_<verb>_v1`; `subject_type` is the table name; `subject_id` is the row PK or the table name for whole-table events.

### Backups (STD-08, DEC-31)
Two layers of backup:
1. **Session-level** — taken once per session before any mutation
2. **Step-level** — taken by every apply script before its mutation, even if a session backup exists

Filename pattern: `data/kintell.db.backup_pre_<step>_<ts>`. All gitignored under `*.v?_backup_*` and `data/kintell.db.backup_*`. Cumulative size as of 2026-04-28b: ~5.0 GB. Pruning of older backups is a P1.5 housekeeping task.

### Recovery
Single-command revert: `Copy-Item data\kintell.db.backup_pre_<step>_<ts> data\kintell.db -Force`.

For frontend file revert (DEC-28): `Copy-Item docs\<file>.v?_backup_<ts> docs\<file> -Force`.

---

## 8. External dependencies

- **Chart.js 4.4.0** — `cdn.jsdelivr.net/npm/chart.js@4.4.0`. Used by System B and the centre page bridge.
- **ASGS 2021 Main Structure GeoPackage** — `abs_data/ASGS_2021_Main_Structure_GDA2020.gpkg` (931 MB). Used for SA2 polygon spatial joins (Step 1c, sa2_cohort build).
- **ABS Remoteness Areas GeoPackage** — `abs_data/ASGS_Ed3_2021_RA_GDA2020.gpkg` (40 MB). Used for SA2 → RA assignment.
- **SQLite** — bundled with Python. No server runtime.
- **Python (Windows, PowerShell idioms)** — see STD-01, STD-05, STD-09.
