# Centre Page V1.5 Roadmap

*Last updated: 2026-05-10 (A10 + C8 Demographic Mix bundle CLOSED end-to-end; TSP table-mapping correction locked as DEC-80). The on-disk version supersedes the project-knowledge monolith if they disagree.*

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
| Demographic Mix bundle | A10 + C8 (T06 ATSI + T08 COB + T14 family + T10 language top-N) | shipped 2026-05-10 | **CLOSED — see §A10 + §C8** |
| Phase A core | A3 + A4 + A5 + A6 | ~1.4 sess | open |
| Phase B core | B1 + B3 + B4 + B5 | ~0.9 sess | open |
| Phase C core | C2 (other B-pass promotions) + C6 | ~0.4 sess | open |
| **V1.5 core remaining** | | **~2.7 sess** | |

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

### A10 — Demographic Mix bundle ✅
**CLOSED 2026-05-10.** Three Census TSP tables ingested, plus two display-only top-N tables. Probe at session start surfaced that the roadmap's table-number assignment was wrong (T07 is fertility / children-ever-born × age; T19 is tenure type / landlord). Locked-in mapping (DEC-80):

- **T06** — Indigenous status → `census_atsi_share_pct` ✅
- **T08** — Country of birth → `census_overseas_born_share_pct` ✅ + `abs_sa2_country_of_birth_top_n` (top-3, 2021)
- **T14** — Family composition → `census_single_parent_family_share_pct` ✅
- **T10A+T10B** — Language at home (follow-up bundled mid-session) → `abs_sa2_language_at_home_top_n` (top-3, 2021)

All three banded percentages stored 0–100 per DEC-78. Banding cohort: `state_x_remoteness` (mirrors NES). Calibration deferred — neutral-framing Lite rows. National 2021 totals: ATSI 3.20%, OS-born 27.71%, single-parent 15.79% — all within ABS-published bands.

ATSI display framing resolved: raw % with neutral "Aboriginal and Torres Strait Islander share" copy (consistent with NES neutral-framing precedent).

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

### C8 — Demographic Mix sub-panel ✅
**CLOSED 2026-05-10.** Implemented as a sub-panel inside Catchment Position card, NOT a separate card (per DEC-80 #4 + DEC-11 additive overlay). The C2 NES patcher author (2026-05-04) had already anticipated this placement.

Render structure (`renderCatchmentPositionCard()` in `centre.html` v3.29):
- Credit-signal block: supply ratio, demand vs supply, child-to-place, adjusted demand, demand share state
- Dashed-divider with "Demographic mix" sub-panel header
- Lite rows: NES → ATSI → overseas-born → single-parent family share
- Top-N context lines via shared `_renderTopNContext` helper:
  - Below NES → "Top languages at home (2021)" (T10A+T10B)
  - Below overseas-born → "Top countries of birth (2021)" (T08)

Backend: `_build_community_profile(conn, sa2_code)` populates `centre.community_profile.{country_of_birth_top_n, language_at_home_top_n}` lists on the payload.

Sparkline glyph on Lite rows considered + rejected mid-session (too busy at that visual budget). Delta badge remains canonical for Lite-row trajectory representation. Captured as a feedback memory.

---

## Items deliberately NOT in this roadmap

- **Operator page V1.5 work** — needs separate scoping pass.
- **Industry view daily-rate integration** — depends on daily-rate metric set stability.
- **Quality elements tab** (OI-21) and **Ownership/corporate detail tab** (OI-22) — V2 candidates.
- **Click-to-detail event overlay** (OI-31) — explicitly deferred from V1.5 ship slice; ~1 sess.

---

## Recommended next session start

**Begin A3 — Parent-cohort 25-44 SA2 series, bundled with Stream C extensions (T05 marital status, T07 fertility/children-ever-born).** Order:

1. Probe T05 + T07 column shapes (already partially banked from A10 probe — both validated as living in same TSP zip)
2. Stream C scope decision (DEC candidate) — which marital + fertility cuts ship as Lite rows in Catchment Position sub-panel vs context-only?
3. ABS ERP age slice for 25-44 alongside existing 0-4 (A3 core) — affects calibration via parent cohort weighting; affects Population card via new "parent cohort" row
4. B-pass banding entry for sa2_parent_cohort_25_44_share + any new marital/fertility metrics
5. C-pass: extend Demographic mix sub-panel with Stream C rows where banded; new context lines if appropriate
6. End-of-session doc refresh

Total estimated: ~0.7 sess (A3 ~0.4 + Stream C extension ~0.3, amortised by shared TSP-zip ingest pass).

After A3 + Stream C lands, evaluate A4 (schools at SA2) next.

---

## Sequencing rules (V1.5-specific)

In addition to platform-wide rules in ROADMAP.md §8:

1. **Always run `layer3_x_catchment_metric_banding.py` after `layer3_apply.py`** until OI-35 real fix lands
2. **Unit conventions explicit at scoping time** (banked from 2026-05-04 A2 v2/v3 incident; SA2 percentages stored 0-100, fractions only at calibration boundary)
3. **C-pass renderer changes** — patcher approach surgical-by-default; refactor only when probe data shows existing dynamic pattern to conform to (per OI-36 scoping decision)
