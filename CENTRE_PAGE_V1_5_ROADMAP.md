# Centre Page V1.5 Roadmap

*Last updated: 2026-05-11 (DEC-83 Commercial Layer V1 ship — daily-rate / regulatory / operator-group identity ingested for 130 pilot centres; A8 dependency released. Centre v2 design pass next major work — daily-rate placement decisions made there per DEC-83 #8). Prior 2026-05-10 PM s2 lock established A4 Schools (DEC-82) close. The on-disk version supersedes the project-knowledge monolith if they disagree.*

This roadmap is the canonical V1.5 work queue for the centre page. PROJECT_STATUS.md and ROADMAP.md reference this doc for V1.5 detail.

## Note 2026-05-09 — broader V1 horizon redefined

**Per DEC-79, the term "V1" has been redefined.** Up to 2026-05-05 "V1" meant the original centre-page credit-decision tool (shipped at HEAD `bcdf84c`). With DEC-79, V1 now means the broader Novara Intelligence institutional decision-support release targeting ~Sept 2026. The V1.5 ingests in this doc are still the next-priority centre-page ingest queue, but they sit *inside* the bigger V1 alongside Catchment page, Group page, five new streams (PropCo property intelligence, SA2 border exposure, educator visa supply, NFP overlays, childbearing/marital depth), Excel export framework, and brand identity rename.

**Where this doc fits in the bigger V1 plan:**
- See `PRODUCT_VISION.md` for strategic frame and the five new streams (A through E)
- See `ROADMAP.md` §2 for the bigger V1 horizon and sequencing
- This doc remains the **dependency-ordered queue for centre-page V1.5 ingests** (A10 + C8 next; A3-A6 and B/C-pass to follow)
- **Stream C (OI-NEW-12)** — Childbearing-age + marital-status depth — extends A3 + T19 in this doc and adds Census TSP T05 marital status. Bundle into A3 ingest pass to amortise TSP workbook reading.
- **Stream B (OI-NEW-11)** — NFP perspectives overlay — derived signals on Community Profile panel rows once T07/T08/T19 (A10) and SEIFA-NES-ATSI-single-parent-workforce constraints all in.

The next-session priority (A10 + C8 Demographic Mix bundle) is unchanged.

---

## V1.5 status — current

| Phase | Items | Effort | Status |
|---|---|---|---|
| First piece | OI-36 (NES render-side + delta badge) | shipped 2026-05-05 | **CLOSED `430009a`** |
| Demographic Mix bundle | A10 + C8 (T06 ATSI + T08 COB + T14 family + T10 language top-N) | shipped 2026-05-10 AM | **CLOSED — see §A10 + §C8** |
| A3 + Stream C bundle | A3 (parent cohort 25-44) + T05 partnered 25-44 + T07 women-with-child 35-44 + T07 women-with-child 25-34 | shipped 2026-05-10 PM | **CLOSED — see §A3 + §C-A3-StreamC** |
| A4 Schools at SA2 | DEC-82 first direct-primary-source ingest; ACARA School Profile + Location; 8 metrics; new "Education infrastructure" card | shipped 2026-05-10 PM s2 | **CLOSED — see §A4** |
| Phase A core remaining | A5 + A6 | ~0.5 sess | open |
| Phase B core | B1 + B3 (partial — already done with A4) + B4 | ~0.5 sess | open |
| Phase C core | C2 (other B-pass promotions) + C6 | ~0.4 sess | open |
| **V1.5 core remaining** | | **~1.4 sess** | |

---

## Phase A — V1.5 ingests

### A1 — ABS ERP backward extension
**DROPPED 2026-05-04.** Probe trail confirmed ABS publishes `'-'` for pre-2019 SA2 under-5. Forward paths exist (Census 2011/2016 SA2 age tables, demographic derivation, ABS TableBuilder) but none V1.5-critical.

### A2 — Census NES share
**CLOSED 2026-05-04** (commits `fdc85bd` + `49ce9f1` + `bb21f66`). Stored as percentage (0-100); wire boundary divides by 100 before passing to calibration.

### A3 — Parent-cohort 25-44 SA2 series ✅
**CLOSED 2026-05-10 PM.** Bundled with Stream C (T05 partnered + T07 fertility) into a single `layer4_4_step_a3_streamc_apply.py` ingest pass — see §A3-Stream-C below. Parent-cohort metric `erp_parent_cohort_25_44_share_pct` lands as a Lite row in the Demographic mix sub-panel (NOT the Population card per D-B3 — the demographic-mix theming is the natural home given the A10 framing). 14,120 rows, annual cadence 2019-2024 per ABS ERP SA2-level coverage. National 2021: 28.20%.

### A4 — Schools at SA2 (DEC-82 direct ACARA ingest) ✅
**CLOSED 2026-05-10 PM session 2 (DEC-82).** First direct-primary-source ingest under the new strategic principle — ACARA School Profile 2008-2025 + School Location 2025 sourced directly from ACARA Data Access Service (instead of derivative ABS Data by Region). New top-level "Education infrastructure" Position card alongside Catchment / Population / Labour Market.

**Eight metrics ingested** (3 rendered V1, 5 banded for V2/Excel/group-page reuse):

| Metric | Render V1? | Cohort | Trajectory |
|---|---|---|---|
| `acara_school_count_total` | ✅ Lite row | state×rem | annual 2008-2025 (18pt) |
| `acara_school_enrolment_total` | ✅ Lite row | state×rem | annual 2008-2025 (18pt) |
| `acara_school_enrolment_govt_share_pct` | ✅ Lite row | state×rem | annual 2008-2025 (18pt) |
| `acara_school_govt_share_pct` (by school count) | banked | state×rem | 18pt |
| `acara_school_catholic_share_pct` (by school count) | banked | state×rem | 18pt |
| `acara_school_independent_share_pct` (by school count) | banked | state×rem | 18pt |
| `acara_school_enrolment_catholic_share_pct` | banked | state×rem | 18pt |
| `acara_school_enrolment_independent_share_pct` | banked | state×rem | 18pt |

**Spatial-join infrastructure:** new `geo_helpers.py` module with `point_to_sa2()` + `points_to_sa2()` + module-level GPKG cache. Reusable for V2 PropCo / hospital / transport ingests + the OI-NEW-19 OSHC-school adjacency derived flag.

**Cross-validation discipline (DEC-65 + Patrick ratification):** ACARA pre-computes SA2 in their Location 2025 file. The ingest cross-checks ACARA's mapping against `geo_helpers.points_to_sa2()` over all 11,039 schools — 99.93% match (8 mismatches all multi-campus schools where ACARA manually allocates campuses to specific delivery SA2s; centroid sjoin can't replicate). Within 1% threshold. ACARA's mapping used as canonical.

**Caveat (banked in metric copy):** SA2 enrolment is "enrolment AT schools located in this SA2", not "school-aged kids LIVING in this SA2 who attend school somewhere". Students cross SA2 borders. Same caveat already applies to `ee_preschool_total_count`.

National 2024 sanity: 9,736 schools, 4.18M enrolment, 63.7% govt-share-by-enrolment. All within ABS-published bands.

**V2 banked:**
- ICSEA + LBOTE (school-level SES + language-background) — captured in source files; V2 ingest extension
- NAPLAN, Senior Secondary Outcomes, Student Attendance — gated behind ACARA application form (Patrick to apply now if desired; lead times)
- Year-level enrolment breakdowns — separate ACARA file (Enrolments by Grade)
- OI-NEW-19 — OSHC-school adjacency derived flag (uses `geo_helpers.points_to_sa2` + proximity threshold; service-level metric)

### A4-legacy entry (superseded; preserved for traceability)
*Original A4 entry assumed ACARA SA2-level enrolment counts were quick to ingest. Reality: ACARA publishes per-school; SA2-level required spatial join + new infrastructure. Path B (full ACARA ingest) chosen 2026-05-10 PM with DEC-82 minted alongside.*

### A5 — Subtype-correct denominators
**Open. ~0.3 sess.** Catchment ratios currently use a single under-5 denominator. LDC/FDC/OSHC subtypes have different age-band catchment populations. Refines `sa2_supply_ratio` per subtype.

### A6 — SALM extension
**Open. ~0.2 sess.** Promote LFP triplet from Lite to Full once SALM monthly cadence is wired in. Replaces the 3 Census points with continuous monthly series.

### A10 — Demographic Mix bundle ✅
**CLOSED 2026-05-10.** Three Census TSP tables ingested, plus two display-only top-N tables. Probe at session start surfaced that the roadmap's table-number assignment was wrong (T07 is fertility / children-ever-born × age; T19 is tenure type / landlord). Locked-in mapping (DEC-80):

- **T06** — Indigenous status → `census_atsi_share_pct` ✅
- **T08** — Country of birth → `census_overseas_born_share_pct` ✅ + `abs_sa2_country_of_birth_top_n` (top-3, 2021)
- **T14** — Family composition → `census_single_parent_family_share_pct` ✅
- **T10A+T10B** — Language at home (follow-up bundled mid-session) → `abs_sa2_language_at_home_top_n` (top-3, 2021)

All three banded percentages stored 0–100 per DEC-78. Banding cohort: `state_x_remoteness` (mirrors NES). Calibration deferred — neutral-framing Lite rows. National 2021 totals: ATSI 3.20%, OS-born 27.71%, single-parent 15.79% — all within ABS-published bands.

ATSI display framing resolved: raw % with neutral "Aboriginal and Torres Strait Islander share" copy (consistent with NES neutral-framing precedent).

### A3-Stream-C — Parent-cohort + marital + fertility (Stream C V1 close) ✅
**CLOSED 2026-05-10 PM (DEC-81).** Four metrics in one ingest pass:

- `erp_parent_cohort_25_44_share_pct` — ABS ERP, annual 2019-2024 (6-point trajectory)
- `census_partnered_25_44_share_pct` — TSP T05 (Mar_RegM_P + Mar_DFM_P) over 25-44, Census 3-point
- `census_women_35_44_with_child_share_pct` — TSP T07, women 35-44 with NCB ≥ 1, Census 3-point. Display label: "Share of women aged 35 to 44 with at least one child"
- `census_women_25_34_with_child_share_pct` — TSP T07, women 25-34, Census 3-point. Display label: "Share of women aged 25 to 34 with at least one child"

All 4 stored 0-100 per DEC-78. Banded `state_x_remoteness` per DEC-67. Neutral-framing Lite rows; calibration deferred (Patrick V2 follow-up). National 2021 totals all in expected bands (28.2 / 65.6 / 78.4 / 41.2). Sub-panel grows from 4 to 8 Lite rows; Catchment Position card now 13 rows total. Density tradeoff acknowledged + accepted.

Key probe finding: ERP `total_persons` is at col **3** (not col 121 as the original Layer-2-step-6 diag mis-guessed). Locked in DEC-81.

NS-handling: numerator + denominator both exclude `NCB_NS` (stricter than NES NS-as-other convention; T07 NS is non-trivial at 3-5% nationally).

Stream C V1 close also retires OI-NEW-12 (childbearing-age + marital-status depth — V1 portion). V2 banked: full marital breakdown (Sep / Div / Wid via GCP DataPack), mean children-ever-born decimals, broader 15+ marital cuts.

### Future ingests (banked)
- A7 — SEEK / advertised wages (workforce supply enrichment)
- A8 — Daily-rate centre-page integration ✅ **DATA SHIPPED 2026-05-11 via DEC-83 Commercial Layer V1.** Schema (`service_fee` + `service_regulatory_snapshot` + `service_condition` + `service_vacancy` + `large_provider` + `large_provider_provider_link` + `service_external_capture`) + 130-centre proof load + Algolia reconcile. National scale-up to 18,223 services follow-up. Centre-page surface integration deferred to Centre v2 institutional signal matrix (Layer 5) per DEC-83 #8 — not implemented in V1.5 centre-page; Layer 5 design pass picks up render placement decisions.

---

## Phase B — V1.5 banding

### B1 — `sa2_jsa_vacancy_rate` peer banding
**Open. ~0.2 sess.** JSA already in payload; banding registry entry needed.

### B2 — `sa2_nes_share` peer banding
**CLOSED 2026-05-04** (commit `d02e26e`). 2,417 banding rows shipped. State × remoteness peer cohort per DEC-67.

### B3 — Schools-derived metrics banding ✅ (partial close)
**CLOSED 2026-05-10 PM s2 alongside A4.** All 8 ACARA metrics banded `state_x_remoteness` per DEC-67 (NES precedent) via `patch_b2_layer3_add_a4_schools.py`. Banding decisions for the 5 V2-banked sector metrics may revisit in V2 if Excel export framing demands different cohorts (e.g., metro vs regional comparison cohort).

### B4 — Subtype-aware metric banding
**Depends on A5.** Catchment ratios per subtype need separate banding rows.

### B5 — `sa2_parent_cohort_25_44_share` banding ✅
**CLOSED 2026-05-10 PM** (with A3 + Stream C ingest in `patch_b2_layer3_add_a3_streamc.py`). 4 banding entries appended (parent-cohort + partnered + 2 fertility cohorts). All `state_x_remoteness` cohort. ~9,420 banded rows added to `layer3_sa2_metric_banding`.

---

## Phase C — V1.5 render

### C2-NES — `sa2_nes_share` rendering (data side + render side)
**CLOSED 2026-05-05** (data side `3ddcf18`, render side `430009a`). Includes delta badge on Lite rows for first-to-last Census-point change visualisation.

### C2-other — render newly-banded B-pass metrics
**Depends on B1/B3/B4/B5.** Each new banded metric needs `LAYER3_METRIC_META` registration + `LAYER3_METRIC_INTENT_COPY` + `LAYER3_METRIC_ABOUT_DATA` entries + render order array entry. Pattern is now well-trodden post-OI-36.

### C3 — Absolute-change rendering on trajectory charts
**CLOSED 2026-05-04** (commit `f47a0ba`).

### C6 — Workforce supply enrichments rendering
**Depends on A7.** SEEK + advertised wages new rows.

### C8 — Demographic Mix sub-panel ✅
**CLOSED 2026-05-10 (extended 2026-05-10 PM with A3 + Stream C).** Implemented as a sub-panel inside Catchment Position card, NOT a separate card (per DEC-80 #4 + DEC-11 additive overlay). The C2 NES patcher author (2026-05-04) had already anticipated this placement.

Render structure (`renderCatchmentPositionCard()` in `centre.html` v3.30):
- Credit-signal block: supply ratio, demand vs supply, child-to-place, adjusted demand, demand share state
- Dashed-divider with "Demographic mix" sub-panel header
- Lite rows (8 total after A3 + Stream C):
  - NES → ATSI → overseas-born → single-parent family share (A10 ship)
  - parent-cohort 25-44 share → partnered 25-44 share → women 35-44 with at least one child → women 25-34 with at least one child (A3 + Stream C ship)
- Top-N context lines via shared `_renderTopNContext` helper:
  - Below NES → "Top languages at home (2021)" (T10A+T10B)
  - Below overseas-born → "Top countries of birth (2021)" (T08)

Backend: `_build_community_profile(conn, sa2_code)` populates `centre.community_profile.{country_of_birth_top_n, language_at_home_top_n}` lists on the payload.

Sparkline glyph on Lite rows considered + rejected at A10 ship (too busy at that visual budget). Delta badge remains canonical for Lite-row trajectory representation. Captured as a feedback memory.

### C-A3-StreamC — A3 + Stream C render extension ✅
**CLOSED 2026-05-10 PM.** Surgical render extension: `centre_page.py` v22 (LAYER3_METRIC_META + INTENT_COPY + TRAJECTORY_SOURCE + POSITION_CARD_ORDER each gain 4 entries) and `centre.html` v3.29 → v3.30 (`demoMetrics` array gains 4 keys after sa2_single_parent_family_share). No new render helpers — existing `_renderLiteRow` + `_renderLiteDelta` handle annual (parent-cohort 6-point 2019-2024) and Census 3-point trajectories transparently via `p.value_format` + `p.trajectory`.

Smoke-test capture rebuilt at `docs/a10_c8_review.html` covering all 13 catchment-position rows for the 4 verifying SA2s.

---

## Items deliberately NOT in this roadmap

- **Operator page V1.5 work** — needs separate scoping pass.
- **Industry view daily-rate integration** — depends on daily-rate metric set stability.
- **Quality elements tab** (OI-21) and **Ownership/corporate detail tab** (OI-22) — V2 candidates.
- **Click-to-detail event overlay** (OI-31) — explicitly deferred from V1.5 ship slice; ~1 sess.

---

## Recommended next session start

**Start with OI-NEW-21 — Catchment trajectory coverage gap.** **V1 priority HIGH per Patrick (2026-05-10 PM session 2 close).** Surfaced during A4 visual review: `docs/sa2_history.json` covers 1,267 of ~2,400 Australian SA2s; the 1,133 absent SA2s render no catchment-position trajectories. Two of four verifying SA2s (Bentley-Wilson WA, Outback NT) are affected. ~0.3-0.7 sess depending on root cause. Probe first per DEC-65: read `build_sa2_history.py` to identify the SA2 coverage filter, then decide whether to relax it, build a fallback trajectory path, or add an upstream ingest for missing denominators. Full investigation path in OPEN_ITEMS.md OI-NEW-21.

**After OI-NEW-21 closes:** **A5 — Subtype-correct denominators** (~0.3 sess). Refines `sa2_supply_ratio` per LDC/FDC/OSHC subtype — currently the 4 catchment ratios use a single under-5 denominator, but each subtype has different age-band catchment populations (LDC: 0-5, FDC: 0-13, OSHC: 5-12). Credit-direct metric refinement; more impactful than A6 (SALM extension which only promotes LFP triplet from Lite to Full).

Then evaluate A6 + B1 (`sa2_jsa_vacancy_rate` peer banding) + remaining C2 / C6. V1.5 path remaining ~1.4 sess after A4 close (with OI-NEW-21 + A5/A6/B/C).

---

## Sequencing rules (V1.5-specific)

In addition to platform-wide rules in ROADMAP.md §8:

1. **Always run `layer3_x_catchment_metric_banding.py` after `layer3_apply.py`** until OI-35 real fix lands
2. **Unit conventions explicit at scoping time** (banked from 2026-05-04 A2 v2/v3 incident; SA2 percentages stored 0-100, fractions only at calibration boundary)
3. **C-pass renderer changes** — patcher approach surgical-by-default; refactor only when probe data shows existing dynamic pattern to conform to (per OI-36 scoping decision)
