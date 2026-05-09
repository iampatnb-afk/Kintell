# A4 — Schools at SA2: design doc

*Created 2026-05-10 PM (post A3 + Stream C ship). Probe-first per DEC-65. RATIFIED 2026-05-10 PM — **Path B (direct ACARA ingest)** chosen with sector-mix in V1; NAPLAN / ICSEA / year-level breakdowns deferred to V2. DEC-82 minted to lock direct-to-primary-source policy. OI-NEW-19 added for OSHC-school adjacency derived flag (V2 work; data infrastructure ships in V1.5).*

## RATIFIED SUMMARY (2026-05-10 PM)

**V1 ships (Path B — direct ACARA ingest with sector breakdown):**
- New table `abs_sa2_schools_annual` populated from ACARA School Profile + School Locations (CSVs sourced directly from ACARA Data Access Service or data.gov.au mirror — public, free, ~3 month publication lag)
- Spatial join: school point (lat/lon) → SA2 polygon via existing `ASGS_2021_Main_Structure_GDA2020.gpkg`
- Spatial-join helper `point_to_sa2(lat, lon, gpkg_path)` lives in `proc_helpers.py` (STD-13 home), reusable for V2 PropCo property locations / hospital catchments / transport stations / OSHC-school-adjacency proximity queries
- 4-6 V1 metrics: `acara_school_count_*` (total + per sector) + `acara_school_enrolment_*` (total + per sector). Optionally `acara_school_govt_share_pct` for sector-mix banding flavour.
- Sector dimension: Government / Catholic / Independent (basic ACARA attribute; zero marginal ingest cost once we're reading the file)
- Render placement TBD post-ingest — likely a small "Schools" sub-section in Catchment Position card or Lite-row addition to the existing Demographic mix sub-panel

**V2 banked (NOT in V1):**
- ICSEA (school-level SES, distinct from SA2 SEIFA — separate ACARA file)
- NAPLAN performance — separate ACARA file
- Year-level enrolment breakdowns (primary/secondary year groups)
- School sub-types (Special, Distance ed, etc.)
- **OI-NEW-19 — OSHC-school adjacency derived flag** (uses A4 spatial-join helper; service-level metric)
- Sub-item on OI-NEW-19: LDC-school adjacency for parental-convenience signal

**Strategic principle locked (DEC-82):** primary-source-first for new ingests; existing 16 derivative-sourced ABS DBR metrics tracked as V2 migration backlog (OI-NEW-20) but explicitly NOT V1 work.

**Effort estimate:** ~1.0 sess (spatial-join helper amortises across future point-feature ingests).

**Caveat to bank in metric labels:** SA2-level "school enrolment" measures "enrolment AT schools located in this SA2", not "kids LIVING in this SA2 who attend school somewhere". Students cross SA2 borders — same caveat already applies to `ee_preschool_total_count`. Will be explicit in `LAYER3_METRIC_INTENT_COPY`.

**Files Patrick to source:** ACARA School Profile + School Locations CSVs (latest year — likely 2024). Drop in `abs_data/` as `acara_school_profile_<year>.csv` and `acara_school_locations_<year>.csv` (or whatever ACARA names them — probe will adapt). Either consolidated in one file or split across two — either works.

---

## 1. Probe findings (`recon/probes/probe_a4_schools_columns.py`)

The probe scanned all five `abs_data/` workbooks for any column matching school / enrol / primary / secondary / pupil / student / kindergar / year_level keywords.

### 1.1 No ACARA-direct file in `abs_data/`

The roadmap assumed "ACARA SA2-level enrolment counts" were available. They are not — the ACARA workbooks publish **per-school** enrolment data, not SA2-level. To get SA2-level school enrolment, you need either:
- ACARA "School Locations" CSV (public) + spatial join (school point → SA2 polygon), OR
- ABS school enrolment series at SA2 (not present in current Data by Region workbooks)

Neither is on disk.

### 1.2 More preschool detail in `Education and employment database.xlsx`

Three preschool cuts already ingested (cols 4 / 9 / 11):
- `ee_preschool_4yo_count` — col 4 ("4 year olds enrolled in preschool or preschool program")
- `ee_preschool_total_count` — col 9 ("Children enrolled in a preschool or preschool program")
- `ee_preschool_15h_plus_count` — col 11 ("Children attending preschool for 15 hours or more")

Additional preschool cuts in the SAME workbook NOT yet ingested:
- col 5 — **5 year olds enrolled in preschool or preschool program**
- col 6 — Children enrolled in preschool (preschool-only — not "preschool program")
- col 7 — **Children enrolled in preschool program within centre based day care** ← directly relevant to LDC framing
- col 8 — Children enrolled across more than one provider type
- col 10 — Children attending preschool for less than 15 hours

The col 7 metric is materially important for LDC institutional context — it tells you "how many of this catchment's preschoolers are getting their preschool program inside an LDC vs in a standalone preschool". That's a credit-relevant signal because it disambiguates LDC demand from standalone-preschool demand.

### 1.3 Family-with-children counts in `Family and Community Database.xlsx`

Two cuts:
- col 8 — Couple families with children under 15 and/or dependent students
- col 11 — One parent families with children under 15 and/or dependent students

These are absolute counts (already partially covered as a share by `census_single_parent_family_share_pct`). The absolute counts could feed a "households with kids in this catchment" metric — but it's adjacent to the existing single-parent-family share, not a school metric per se.

### 1.4 No primary/secondary school data anywhere in current `abs_data/`

Searched all five workbooks. None carry primary or secondary enrolment at SA2 level.

---

## 2. Why this matters for V1.5

Original A4 scope assumed school data was a quick add. The scope reality is:
- (a) **Cheap path** — extend preschool detail using existing EE workbook columns. Ships in ~0.3 sess.
- (b) **Real ACARA ingest** — source ACARA file, do spatial join to SA2, build new table. Ships in ~1.0-1.5 sess (additional dataset acquisition + spatial join discipline).
- (c) **Drop A4 from V1.5** — defer to V2 when ACARA + spatial-join becomes part of a bigger streams plan.

The roadmap under-estimated A4. Even path (a) is below the original ~0.5 sess estimate.

---

## 3. Three paths to choose from

### Path A — Cheap preschool expansion (recommended for V1.5)

**Effort: ~0.3 sess.** Add 2-3 more preschool cuts from the existing EE workbook:

1. `ee_preschool_5yo_count` — col 5 (5 year olds enrolled). Pairs with existing `ee_preschool_4yo_count`. Captures the kinder year cohort.
2. `ee_preschool_in_cbdc_count` — col 7 (preschool program within centre based day care). **The LDC-relevant cut.** Tells you what fraction of preschool is happening inside LDC vs standalone.
3. *Optional:* `ee_preschool_under_15h_count` — col 10. Mirrors the existing 15h+ cut so the two together describe the full intensity distribution.

**Banded as shares** of `ee_preschool_total_count` to make the institutional context readable:
- `sa2_preschool_in_cbdc_share` = `ee_preschool_in_cbdc_count / ee_preschool_total_count × 100` — the LDC capture rate of preschool delivery
- `sa2_preschool_15h_share` = `ee_preschool_15h_plus_count / ee_preschool_total_count × 100` — already ingested as count; add the share

**Render placement:** these are NOT demographic mix — they're institutional / supply-side context. Likely candidates for a small new sub-section ("Preschool delivery profile") inside the **Catchment Position** card after the demographic mix sub-panel, OR as additions to the existing Population card.

### Path B — Full ACARA SA2 ingest (defer to V2 unless Patrick wants it now)

**Effort: ~1.0-1.5 sess.** Spans:
1. Download ACARA "School Locations" + "School Profile" CSVs (publicly available; ACARA Data Portal).
2. Spatial join: school lat/lon → SA2 (uses existing `ASGS_2021_Main_Structure_GDA2020.gpkg`).
3. New table `abs_sa2_schools_annual` — primary count, secondary count, combined count, enrolment total per SA2 per year.
4. Banding registry entries.
5. Render placement decisions (likely a new "Schools" sub-section in Catchment Position OR a dedicated card).

This is real V2-grade work. Not recommended for V1.5 unless Patrick wants the school context in V1.

### Path C — Drop A4 from V1.5 entirely

Move A4 to V2. Update the roadmap. This frees the V1.5 tail for A5 (subtype-correct denominators) + A6 (SALM extension) + B-pass + C-pass remaining items.

The argument for C: V1.5 is institutional decision-support already covering preschool counts (3 metrics) + the new demographic mix (8 rows) + the existing credit-direct catchment ratios. Adding school enrolment context is nice-to-have, not load-bearing for credit decisions.

---

## 4. Recommendation

**Path A — cheap preschool expansion**, with a particular focus on the `ee_preschool_in_cbdc_share` metric. Rationale:
- The col-7 metric is uniquely LDC-relevant — it's the only quantification of "how much of preschool delivery happens INSIDE LDC vs alongside it" at SA2 level.
- All data is already on disk in a workbook we already read.
- Banding pattern is a clone of existing share-style metrics.
- Path B (full ACARA ingest) is V2-grade and the A4 roadmap entry was over-promised. Document the gap in OI-NEW-* and move on.
- Path C is fine if Patrick wants to tighten V1.5 scope further; the institutional decision-support frame doesn't strictly require school context in V1.

---

## 5. Decision request (Patrick)

Choose one:

**A.** Path A — ship 2-3 preschool cuts from existing EE workbook. ~0.3 sess. (Recommended.)

**B.** Path B — source ACARA CSV + spatial join + new schools table. ~1.0-1.5 sess. (Material V1.5 scope expansion.)

**C.** Path C — drop A4, move to V2. Roadmap update only. ~0.05 sess.

**A+B (combined).** Ship A now, defer B to V2 with a tracked OI. ~0.3 sess + future commitment.

Sub-questions if you pick A:
- Ship 2 metrics (`5yo_count` + `preschool_in_cbdc_share`) or 3 (add `15h_share` too)?
- Render placement: extend Catchment Position card with a "Preschool delivery" mini-section, OR add to the existing Population card, OR ship as Lite rows in the existing demographic mix sub-panel?

No code until you ratify.
