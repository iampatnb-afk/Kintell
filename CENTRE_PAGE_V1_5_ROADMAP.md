# Centre Page V1.5 Roadmap

*Last updated: 2026-05-09 (commercial repositioning per DEC-79; this doc remains canonical for centre-page V1.5 ingest queue). The on-disk version supersedes the project-knowledge monolith if they disagree.*

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
| **First piece (just shipped)** | OI-36 (NES render-side + delta badge) | shipped 2026-05-05 | **CLOSED `430009a`** |
| Phase A core | A3 + A4 + A5 + A6 | ~1.4 sess | open |
| Phase B core | B1 + B3 + B4 + B5 | ~0.9 sess | open |
| Phase C core | C2 (other B-pass promotions) + C6 | ~0.4 sess | open |
| **V1.5 core remaining** | | **~2.7 sess** | |
| Phase 2 (next-session priority) | A10 + C8 — Demographic Mix bundle (T07 + T08 + T19) | ~1.0 sess | banked, **elevated** |

---

## Phase A — V1.5 ingests

### A1 — ABS ERP backward extension
**DROPPED 2026-05-04.** Probe trail confirmed ABS publishes `'-'` for pre-2019 SA2 under-5. Forward paths exist (Census 2011/2016 SA2 age tables, demographic derivation, ABS TableBuilder) but none V1.5-critical.

### A2 — Census NES share
**CLOSED 2026-05-04** (commits `fdc85bd` + `49ce9f1` + `bb21f66`). Stored as percentage (0-100); wire boundary divides by 100 before passing to calibration.

### A3 — Parent-cohort 25-44 SA2 series
**Open. ~0.4 sess.** ABS ERP age slice for 25-44 alongside existing 0-4. Affects calibration via parent cohort weighting; affects Population card via new "parent cohort" row.

### A4 — Schools at SA2 (preschool counts already in place)
**Open. ~0.5 sess.** ACARA SA2-level enrolment counts. Currently only `ee_preschool_*_count` series are in the table.

### A5 — Subtype-correct denominators
**Open. ~0.3 sess.** Catchment ratios currently use a single under-5 denominator. LDC/FDC/OSHC subtypes have different age-band catchment populations. Refines `sa2_supply_ratio` per subtype.

### A6 — SALM extension
**Open. ~0.2 sess.** Promote LFP triplet from Lite to Full once SALM monthly cadence is wired in. Replaces the 3 Census points with continuous monthly series.

### A10 — Demographic Mix bundle (NEXT-SESSION PRIORITY) ⭐
**Open. ~0.5 sess. EXPANDED 2026-05-05.**

Originally scoped as T08 country of birth only. Per operator review of NES render and second-round demographic doc, scope expanded to bundle three Census TSP tables that all live in `2021_TSP_SA2_for_AUS_short-header.zip` (already on disk from A2):

- **T07** — Indigenous status (ATSI population at SA2 level)
- **T08** — Country of birth (top-N parser, 5 most common per SA2)
- **T19** — Family composition (single-parent household share)

Same TSP zip + same processing pattern as A2 v3 = low marginal cost over single-table A10. Storage in `abs_sa2_education_employment_annual` long-format table per existing convention.

**Open question for A10 ingest pass:**
- ATSI display framing: raw % vs ratio to national? Sensitivity is real; lean towards plain % with neutral copy ("Aboriginal and Torres Strait Islander population share") consistent with NES neutral-framing precedent.

### Future ingests (banked)
- A7 — SEEK / advertised wages (workforce supply enrichment)
- A8 — Daily-rate centre-page integration (depends on daily-rate metric stability)

---

## Phase B — V1.5 banding

### B1 — `sa2_jsa_vacancy_rate` peer banding
**Open. ~0.2 sess.** JSA already in payload; banding registry entry needed.

### B2 — `sa2_nes_share` peer banding
**CLOSED 2026-05-04** (commit `d02e26e`). 2,417 banding rows shipped. State × remoteness peer cohort per DEC-67.

### B3 — Schools-derived metrics banding
**Depends on A4.** Per-SA2 school enrolment metrics need their own peer cohort logic.

### B4 — Subtype-aware metric banding
**Depends on A5.** Catchment ratios per subtype need separate banding rows.

### B5 — `sa2_parent_cohort_25_44_share` banding
**Depends on A3.** Parent cohort share by SA2.

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

### C8 — Demographic Mix narrative panel (NEXT-SESSION PRIORITY) ⭐
**Open. ~0.5 sess. EXPANDED 2026-05-05.**

Single panel below Population card. Combines NES (already rendering) + new A10 bundle (ATSI + country of birth + single-parent households) into one demographic-context section. Neutral framing throughout per the NES precedent.

Phases:
1. Backend: register 3 new metrics in `LAYER3_METRIC_META` (card='community_profile' or similar)
2. Frontend: new `renderCommunityProfileCard()` function modelled on `renderCatchmentPositionCard()` post-OI-36
3. Top-3 country of birth handling (special-case: not a single value, a list with shares)

**Open question for C8 panel:**
- Card placement — between Catchment Position and Population? Inside Population? Separate card below Workforce? Decide at scoping time per render-best-practice.

---

## Items deliberately NOT in this roadmap

- **Operator page V1.5 work** — needs separate scoping pass.
- **Industry view daily-rate integration** — depends on daily-rate metric set stability.
- **Quality elements tab** (OI-21) and **Ownership/corporate detail tab** (OI-22) — V2 candidates.
- **Click-to-detail event overlay** (OI-31) — explicitly deferred from V1.5 ship slice; ~1 sess.

---

## Recommended next session start

**Begin A10 + C8 (Demographic Mix bundle).** Order:

1. Phase A: A10 ingest pass — three TSP tables in one ingest (~0.5 sess)
2. Phase B: register 3 new banding entries (~0.1 sess each)
3. Phase C: C8 panel build (~0.5 sess)
4. End-of-session doc refresh

Total estimated: ~1.0-1.2 sess depending on country-of-birth display polish.

After A10/C8 lands, evaluate next priority among A3/A4/A5/A6.

---

## Sequencing rules (V1.5-specific)

In addition to platform-wide rules in ROADMAP.md §8:

1. **Always run `layer3_x_catchment_metric_banding.py` after `layer3_apply.py`** until OI-35 real fix lands
2. **Unit conventions explicit at scoping time** (banked from 2026-05-04 A2 v2/v3 incident; SA2 percentages stored 0-100, fractions only at calibration boundary)
3. **C-pass renderer changes** — patcher approach surgical-by-default; refactor only when probe data shows existing dynamic pattern to conform to (per OI-36 scoping decision)
