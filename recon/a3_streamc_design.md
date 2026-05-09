# A3 + Stream C — Parent-cohort + marital + fertility: design doc

*Created 2026-05-10. RATIFIED 2026-05-10 (D-B1 amended to 4 metrics; D-B2/3/4/5 ratified as proposed). Bundle pattern follows A10 + C8.*

## RATIFIED SUMMARY (2026-05-10)

**V1 ships 4 new metrics** (sub-panel grows 4 rows → 8 rows total in Demographic mix; Catchment Position card grows from 9 to 13 total rows):

1. `sa2_parent_cohort_25_44_share_pct` — ABS ERP, annual trajectory 2011→2024
2. `census_partnered_25_44_share_pct` — TSP T05 (Mar_RegM + Mar_DFM, 25-44 P), Census 3-point. **Sharp 25-44 window** (matches parent-cohort window — coherent story).
3. `census_women_35_44_with_child_share_pct` — TSP T07, women 35-44 with NCB ≥ 1 (label: "Share of women aged 35 to 44 with at least one child"). Census 3-point.
4. `census_women_25_34_with_child_share_pct` — TSP T07, women 25-34 with NCB ≥ 1 (label: "Share of women aged 25 to 34 with at least one child"). Census 3-point. **Patrick rationale:** 35-44 alone "feels old" for childcare relevance — the under-cohort 25-34 is more directly indexed to active childcare years and reads as "additionally interesting" institutional context.

All 4 stored as percentage 0-100 per DEC-78. All banded `state_x_remoteness` per DEC-67. All neutral framing per DEC-75 (no calibration nudge).

Density tradeoff (D-B2 in original framing): card height bumps to ~13 rows. Patrick acknowledged the density concern but accepted it — both fertility cohorts read as load-bearing for childcare-asset framing.

Render order (D-B3 ratified): parent-cohort → partnered → 35-44 fertility → 25-34 fertility, appended after `single_parent_family_share`.

## 1. What's banked from the column probe

`recon/probes/probe_a3_streamc_columns.py` (run 2026-05-10) confirmed:

### ABS ERP — Population and People Database.xlsx, sheet "Table 1" (164 cols)

The existing Layer 2 Step 6 ingest reads cols `0` (sa2_code), `1` (label), `2` (year), `12/48/84` (under-5 M/F/P), and `121` (total_persons). The probe enumerates 18 5-year age-band columns per sex × 3 sexes — all already in the workbook and on disk.

| Cohort | Persons col(s) | Confirmed label |
|---|---|---|
| Persons 25-29 | 89 | "Persons - 25-29 years (no.)" |
| Persons 30-34 | 90 | "Persons - 30-34 years (no.)" |
| Persons 35-39 | 91 | "Persons - 35-39 years (no.)" |
| Persons 40-44 | 92 | "Persons - 40-44 years (no.)" |
| **Sum cols 89..92** | — | **Parent-cohort 25-44 (Persons)** |
| Total persons | 121 | "Estimated resident population - Persons" (existing) |

ERP year coverage already in `abs_sa2_erp_annual` table: 2011, 2016, 2018, 2019, 2020, 2021, 2022, 2023, 2024 (forward-only annual; pre-2019 SA2 detail is `'-'` per A1 dropped finding).

### Census TSP — 2021_TSP_SA2_for_AUS_short-header.zip

**T05 — Social marital status × age × sex**, split A/B/C by census year + age range.

Column shape: `C{yr}_{age_lo}_{age_hi}_{cat}_{sex}` where:
- `yr` ∈ {11, 16, 21}
- age bands: `15_19, 20_24, 25_29, 30_34, 35_39, 40_44, 45_49, ..., 80_84, 85ov` (15 bands; "Persons aged 15+")
- `cat` ∈ **{`Mar_RegM` (registered marriage), `Mar_DFM` (de facto marriage), `N_mar` (never married), `Tot`}**
- `sex` ∈ {M, F, P}

Verification SA2 spot, 2021 ages 20-24 row:
- 211011251 Bayswater Vic — RegM_P unrequested in this slice but `Mar_DFM_P=106`, `N_mar_P=580`, `Tot_M=356, Tot_F=345`
- 506031124 Bentley-Wilson WA — student-heavy SA2; `N_mar_M=1152, N_mar_F=832` shows >85% never-married at 20-24 as expected

NB: T05 only carries 3 explicit categories (RegM, DFM, N_mar). Separated/Divorced/Widowed are absent — they fold into `Tot − (RegM + DFM + N_mar)` if needed, but per ABS Census 2021 TSP DataPack T05 docs the separation+divorce+widow share is captured under "Not married" derivation. **Cleanest read: T05 supports a "partnered" cut (RegM + DFM) and a "never married" cut.**

**T07 — Children ever born × age (women only — AP = "All Persons aged X" but T07 is restricted to females in Census 2021 TSP)**, split A/B/C by census year + age range.

Column shape: `C{yr}_AP_{age_lo}_{age_hi}_NCB_{count}` where:
- age bands: `15_19, 20_24, ..., 80_84, 85ov`
- `count` ∈ **{`0, 1, 2, 3, 4, 5, 6mor, NS, Tot`}** (NCB = number of children born; `6mor` = 6 or more; `NS` = not stated)

Verification SA2 spot, 2021 75-79 women: data flows cleanly across all 4 SA2s with `Tot` non-trivial.

T07 supports cuts:
- **Childlessness rate by age:** `NCB_0 / Tot` (informative for 35-44 — completed-fertility proxy)
- **Mean children-ever-born by age:** weighted average (informative for 35-44; population-level fertility intensity)
- **High-fertility share:** `(NCB_4 + NCB_5 + NCB_6mor) / Tot` (informative for community profile context)

---

## 2. Scope summary

This bundle ships **inside the same Demographic mix sub-panel** that A10 + C8 introduced. Three new metrics, all stored as percentage 0-100 per DEC-78, all peer-banded state×remoteness per DEC-67 (NES precedent), all neutral-framing Lite rows per DEC-75 (calibration deferred — same playbook as A10).

**A3 — Parent-cohort 25-44 share** is single-source (ABS ERP, annual cadence). Trajectory potential: full annual series 2011→2024 (Lite-row delta is unusually informative here because there ARE multiple data points unlike the 3 Census points).

**Stream C cuts (T05 + T07)** are Census-only (3 points: 2011/2016/2021). Same delta-badge mechanics as the A10 cohort.

---

## 3. Decisions to ratify (D-B1 through D-B5)

### D-B1 — Three metrics shipped, naming, banding cohort

**Decision (proposed):**

| Metric | Source | Formula (per SA2 per year) | Storage | Band cohort |
|---|---|---|---|---|
| `sa2_parent_cohort_25_44_share_pct` | ABS ERP `abs_sa2_erp_annual` | sum(persons 25-29..40-44) / total_persons × 100 | percentage 0-100 | state_x_remoteness |
| `census_partnered_25_44_share_pct` | TSP T05 (RegM+DFM, age 25-44, P) | (sum RegM_P + DFM_P over 25-29..40-44) / sum(Tot_P over 25-29..40-44) × 100 | percentage 0-100 | state_x_remoteness |
| `census_completed_fertility_35_44_share_pct` | TSP T07 (women 35-44 with NCB ≥ 1) | (Tot − NCB_0 − NCB_NS) / (Tot − NCB_NS) over 35-39 + 40-44 × 100 | percentage 0-100 | state_x_remoteness |

**Why these three (not e.g. raw fertility intensity / never-married share):**
1. Parent-cohort share — the institutional-credit-relevant primary variable for childcare demand timing. Already requested in CENTRE_PAGE_V1_5_ROADMAP §A3.
2. Partnered share is the cleanest Stream C marital cut. Single number, story is intuitive ("X% of 25-44s in this SA2 are in registered or de facto partnerships"). Avoids the awkward "never married vs. separated/divorced/widowed" carve-up that Census short-header T05 doesn't expose cleanly.
3. Completed-fertility proxy at 35-44 is the cleanest Stream C fertility cut. By age 40-44 women's completed fertility is 95%+ stable. Captures *whether* people have kids, not how many — which is the institutional-relevant variable for childcare demand intensity.

**Reject:**
- Mean children-ever-born — useful but harder to communicate (decimals like "1.87" with no obvious peer band). The 0-100% cut reads cleaner in a Lite row.
- Never-married share — high covariance with partnered share (≈ inverse). Adds noise without adding signal.
- Workforce-style age cuts (15-64, 25-54) — outside scope; LFP triplet already covers prime-age workforce.
- T05 separated/divorced/widowed — Census 2021 TSP short-header `T05` does not break these out; would need full-detail GCP. Defer to V2 if ever requested.

**NS (not-stated) handling:** matches NES + ATSI + OS-born convention. Numerator excludes NS; denominator excludes NS (not includes-as-other). Stricter than the OS-born NS-as-Australia convention but appropriate here because NS in marital/fertility is non-trivial (~3-5%).

**Direction (calibration):** all three NEUTRAL — none enters STD-34 calibration. Demographic mix rows are context; calibration coefficients live with credit-direct metrics. (A10 set this precedent; D-B1 follows it.)

### D-B2 — Trajectory cadence

**Decision (proposed):** parent-cohort 25-44 ships with **annual ERP cadence (2011, 2016, 2018-2024 → 9 points)** to fully exploit the Lite delta badge ("+5.3pp from 2011 to 2024" reads as material trajectory rather than just three census snapshots). The other two metrics ride the Census 3-point series like NES + ATSI + OS-born + 1PF.

**Why:** ERP IS annual and we already have it. There's no reason to throttle it down to Census-only just for symmetry. The delta badge already handles "first to last" framing year-agnostically (year stamps are unit-aware in `_renderLiteDelta`).

**Implication for renderer:** parent-cohort row uses `LAYER3_METRIC_TRAJECTORY_SOURCE.kind = "annual"` (existing pattern from `sa2_pop_under5` etc.). Marital + fertility rows use `kind = "census_three_point"` matching NES/ATSI/etc.

### D-B3 — Render placement and ordering

**Decision (proposed):** extend the Demographic mix sub-panel inside Catchment Position card. Final row order:

```
Catchment position
├── sa2_supply_ratio                      (Full)
├── sa2_demand_supply                     (Full)
├── sa2_child_to_place                    (Full)
├── sa2_adjusted_demand                   (Full)
├── sa2_demand_share_state                (Context)
│
│ ── Demographic mix ──
├── sa2_nes_share                              (Lite)
├── sa2_atsi_share                             (Lite)
├── sa2_overseas_born_share                    (Lite, + top-3 CoB context line)
├── sa2_single_parent_family_share             (Lite)
├── sa2_parent_cohort_25_44_share              (Lite, NEW — annual trajectory)
├── census_partnered_25_44_share               (Lite, NEW — Census 3pt)
└── census_completed_fertility_35_44_share     (Lite, NEW — Census 3pt)
```

**Why:**
- DEC-11 additive overlay default. C8 sub-panel already exists; extending it is the path of least UI sprawl.
- Reading flow: NES/ATSI/OS-born/1PF describe *who lives there*; the new three describe *what life-stage they're in*. Group reads naturally bottom of the sub-panel.
- DEC-75 visual weight: 3 more Lite rows ≈ 1 more Full row of vertical real estate. Card grows from ~10 rows to ~13. Acceptable.

**Top-N context lines this bundle adds:** none. Marital and fertility don't have a sensible top-N companion. If Stream C grows in V2 with country-of-marital-status type cuts that's a separate decision.

**Reject:** putting parent-cohort 25-44 share in a separate "Population" card. It IS demographic context; placing it elsewhere fragments the sub-panel theme and contradicts the C8 pattern.

### D-B4 — Verification SA2s + sanity expectations

**Decision (proposed):** keep the 4 verification SA2s from A10 unchanged (Bayswater, Bondi Junction, Bentley-Wilson, Outback NT). Sanity bounds:

| Metric | National 2021 expected | Source |
|---|---|---|
| `sa2_parent_cohort_25_44_share_pct` | ~28-30% | ABS ERP 2021 |
| `census_partnered_25_44_share_pct` | ~58-65% | ABS Census 2021 published cross-tab |
| `census_completed_fertility_35_44_share_pct` | ~75-82% | ABS Census 2021 children-ever-born tabs |

If national-weighted total falls outside ±3pp of these, halt and re-probe column selection.

**Spot expectations on the 4 verifying SA2s:**
- Bondi Junction-Waverly NSW (urban high-income, late-partnering): partnered % below national; completed fertility % below national; parent cohort share low.
- Bayswater Vic (suburban family belt): partnered % near or above national; completed fertility near national; parent cohort share elevated.
- Bentley-Wilson WA (student-heavy): partnered % well below national; parent cohort share LOW (lots of 18-24); completed fertility likely above national among those 35-44 because the 35-44 women remaining there self-select.
- Outback NT (remote / Indigenous): partnered % well below national (de facto more common but registered marriage less); high completed-fertility (early-fertility population).

These spot expectations are bankable as `[INFO]` log lines next to the verification print, not as failure-flags.

### D-B5 — Bundle into a single ingest script vs. split

**Decision (proposed):** **single script** `layer4_4_step_a3_streamc_apply.py` that ingests:
1. `sa2_parent_cohort_25_44_share_pct` (ERP source — re-reads Population workbook)
2. `census_partnered_25_44_share_pct` (T05 source)
3. `census_completed_fertility_35_44_share_pct` (T07 source)

All four into the same long-format `abs_sa2_education_employment_annual` table.

**Why:**
- Atomic. Three audit_log rows but one backup, one apply pass.
- Mirrors A10's bundling of T06+T08+T14 into one `layer4_4_step_a10_apply.py`.
- Per-metric idempotency via existing `--replace` semantics.
- Avoids the failure mode where parent-cohort lands but Stream C halts mid-way and sub-panel ships partial.

**Reject:** splitting into A3 (ERP) + A3-streamc (TSP). Adds ceremony without isolating risk — both sources are well-trodden.

---

## 4. Risks / unknowns banked for ingest time

- **T05 NS/separated/divorced/widowed**: not in TSP short-header T05. We will compute `partnered_pct` only and note its complement is "never married + separated + divorced + widowed combined" rather than just "never married". Document in the ingest script docstring.
- **T07 restricted to females**: confirmed by AP = All Persons (aged X, female) per ABS T07 documentation. Probe shows 2021 75-79 NCB_Tot values in the same range as expected female counts. Will assert this in `read_t07()`.
- **ERP age-band null rows**: pre-2019 SA2 = `'-'` is already established (A1 finding). Use the same `to_int` guard as A2/A10.
- **T05 file split**: T05A holds C11 + start of C16, T05B holds C16 + start of C21, T05C holds rest of C21. Per-year filename map needed (clone A10's `ATSI_COLS["file_idx"]` pattern).
- **T07 file split**: same A/B/C pattern; ingest needs per-year per-age-band file lookup.
- **Census 2021 TSP table-number verification**: per DEC-80 — surface T05 + T07 description from the TSP DataPack TableID_Description CSV as a hard precondition before ingest. (Same discipline that caught the T07/T19 swap in A10.)

---

## 5. Implementation sequence (post-ratification)

Three commits per DEC-22 collapsed pattern:

### Commit 1 — A3 + Stream C ingest + B-pass banding
1. New script `layer4_4_step_a3_streamc_apply.py` — clones `layer4_4_step_a10_apply.py` skeleton; adds ERP + T05 + T07 readers and 3 metric derivations.
2. `python layer4_4_step_a3_streamc_apply.py` (dry-run) — verify SA2 counts, national totals, 4 verifying SA2s.
3. STD-30 pre-mutation `db_inventory.md` snapshot.
4. `python layer4_4_step_a3_streamc_apply.py --apply` — backup + INSERT + 3 audit_log rows.
5. Patcher `patch_b2_layer3_add_a3_streamc.py` (3 entries appended to `METRICS = [...]` in `layer3_apply.py`, all `state_x_remoteness` cohort, neutral-framing).
6. `python patch_b2_layer3_add_a3_streamc.py --apply`.
7. `python layer3_apply.py --apply` (lands banding).
8. **OI-35 workaround:** `python layer3_x_catchment_metric_banding.py --apply`.
9. Spotcheck verification SA2s against expected ranges.

### Commit 2 — C-pass render
1. Surgical edit to `centre_page.py`:
   - 3 entries appended to `LAYER3_METRIC_META`
   - 3 entries appended to `LAYER3_METRIC_INTENT_COPY`
   - 3 entries appended to `LAYER3_METRIC_TRAJECTORY_SOURCE` (1 annual, 2 census-3pt)
   - 3 entries appended to `POSITION_CARD_ORDER["catchment_position"]` after `single_parent_family_share`
   - Possibly an `_build_*` helper if Stream C exposes anything richer than a banded Lite row (probably not for v1)
2. Surgical edit to `centre.html` `renderCatchmentPositionCard()` — extend `order` array. (No new render helper needed; existing Lite-row + `_renderLiteDelta` handle both annual and 3-point trajectories transparently.)
3. Restart `review_server.py`.
4. Hard-refresh centre page (Ctrl+F5) for each verification SA2.
5. Visual spotcheck — Patrick.

### Commit 3 — End-of-session doc refresh
1. Update `PROJECT_STATUS.md`, `CENTRE_PAGE_V1_5_ROADMAP.md` (A3 + Stream C closed), `OPEN_ITEMS.md` (OI-NEW-12 close), `PHASE_LOG.md`.
2. Mint **DEC-81** to lock the partnered-share + completed-fertility-proxy framing decisions (Stream C V1 scope).
3. Regenerate end-of-session monolith per STD-35.

---

## 6. Verification plan (Patrick-facing)

After Commit 1:
- DB has 3 new audit_log rows: `census_partnered_25_44_share_ingest_v1`, `census_completed_fertility_35_44_share_ingest_v1`, `sa2_parent_cohort_25_44_share_ingest_v1`.
- 4 verification SA2s produce values within sanity bands and consistent with the spot-expectation matrix (D-B4).

After Commit 2:
- Hard-refresh centre page → Catchment Position card sub-panel shows 7 Lite rows (NES + ATSI + OS-born + 1PF + parent-cohort + partnered + completed-fertility).
- Each row shows delta badge — parent-cohort row will show "+/- Xpp from 2011 to 2024", others "+/- Xpp from 2011 to 2021".

After Commit 3:
- Tier-2 docs updated; monolith regenerated.

---

## 7. Decision request (Patrick)

Ratify (or amend):
- **D-B1** — three metrics: parent-cohort 25-44 share + partnered 25-44 share + completed-fertility-proxy 35-44 share. All percentages 0-100, state_x_remoteness banding cohort, neutral framing (no calibration).
- **D-B2** — parent-cohort uses annual ERP trajectory; the other two use Census 3-point.
- **D-B3** — extend C8 sub-panel; row order parent-cohort → partnered → completed-fertility appended after single-parent-family.
- **D-B4** — keep 4 verification SA2s from A10; sanity bounds as in the table.
- **D-B5** — single ingest script `layer4_4_step_a3_streamc_apply.py`.

Questions Patrick may want to raise before ratifying:
- **Naming:** "completed-fertility 35-44 share" reads OK to you? Alternatives: "share of women 35-44 with at least one child", "ever-mother share 35-44", "non-childless share 35-44".
- **Whether to ship completed-fertility at all vs. just A3 + partnered.** Adding a 3rd sub-panel row beyond what A10 added bumps the card from 10 → 13 rows. Reasonable to defer the fertility cut to V2 if you want to budget the visual real estate.
- **Whether the partnered cut should default to age 25-44 or the broader 15+ TSP cut.** The 25-44 cut is sharper — same age window as parent cohort, so the three rows tell a coherent story. The broader 15+ cut is the headline national stat (~50%) but masks early adulthood.

Once ratified, sequence in §5 starts. No code until then.
