# Project Status

*Last updated: 2026-05-03. The on-disk version supersedes the project-knowledge monolith if they disagree.*

## Centre page — current state

`centre_page.py` v13 (Python backend) + `centre.html` v3.18 (renderer) + payload schema `centre_payload_v6` (unchanged this session — v13 added fields, no schema rev).

The centre page renders the three-temporal-mood pattern (DEC-32) at the leaf level, with the **2026-04-30 page-level reorder** putting credit-lens content first:

**Page order (top to bottom):**
1. Header (centre name + key facts)
2. Trend window bar (3Y / 5Y / 10Y / All; applies to Population / Labour / Catchment trajectories only)
3. **Credit block** (signals first):
   - Catchment position card (5 rows; HEADLINE CREDIT SIGNAL)
   - Population card (4 rows; 1 deferred)
   - Labour Market card (7 rows; 1 deferred)
   - Workforce Supply Context (4 rows; own window selector)
4. Visible horizontal divider
5. **Operational block** (facts second):
   - NQS rating + Places (side-by-side)
   - Catchment-meta + Tenure (side-by-side)
   - Quality Assessment Areas
   - Commentary

**NOW block** (operational, now in lower half of page):
- NQS rating + cadence (DEC-34 five-state classification)
- Places + service sub-type + management type
- Kinder recognition (3-row composite: ACECQA flag + name match + four-state derived headline; mirrors operator-page treatment; always renders)
- Catchment context (SEIFA + ARIA + SA2)
- Tenure (greenfield / brownfield + transfer history)

**POSITION block — Catchment position card (sub-pass 4.2-A.3, 4.2-A.3b, 4.2-A.4):**

| Metric | Weight | Reversibility | Industry band | Calibration in DER |
|---|---|---|---|---|
| `sa2_supply_ratio` | LITE | reversible ↔ `sa2_child_to_place` | 7 levels (desert / undersupplied / below_bench / at_bench / well_served / at_target / saturated) | — (pure ratio) |
| `sa2_demand_supply` | LITE | reversible ↔ `demand_supply_inv` (HTML-level) | 4 levels (soft / near_be / viable / strong) | YES (4.2-A.4) |
| `sa2_child_to_place` | LITE | reversible ↔ `sa2_supply_ratio` | 5 levels (excess_capacity / balanced / tight / constrained / severe) | — (pure ratio) |
| `sa2_adjusted_demand` | LITE | not reversible | NO industry band (decile only) | YES (4.2-A.4) |
| `sa2_demand_share_state` | CONTEXT | n/a | n/a (rank-by-construction; reads cache directly) | YES (4.2-A.4) |

Two reversible pairs activate the DEC-74 perspective toggle (live in V1).

**STD-34 calibration metadata now surfaces in the DER tooltip** on the three calibration-using rows (4.2-A.4 ship 2026-05-03). Tooltip carries `calibrated_rate=X.XX — <rule_text>` where `rule_text` traces every nudge applied (e.g. `default 0.50; +0.02 income decile 10 (high); +0.02 female LFP top quartile (67.7% ≥ 67.2%); NES share not yet ingested (OI-19; nudge dormant); ARIA band 1 unrecognised (no nudge)`). `_renderContextRow` now ships a conditional DER badge (didn't exist before 4.2-A.4) so `sa2_demand_share_state` carries the surface.

Each Lite catchment row renders: title + value + decile strip + low/mid/high band chips + INDUSTRY band line (when populated) + intent copy + DER+COM badges.

**POSITION block — Population (4 metrics, 1 deferred):**
- `sa2_under5_count` FULL — band against same-state cohort
- `sa2_total_population` FULL — band against state-x-remoteness
- `sa2_births_count` FULL — band against state-x-remoteness
- `sa2_under5_growth_5y` DEFERRED (placeholder; OI-09)

**POSITION block — Labour Market (7 metrics, 1 deferred):**
- `sa2_unemployment_rate` FULL — band against same-state cohort
- `sa2_median_employee_income` FULL — band against same-remoteness (5 dense annual points 2018-2022)
- `sa2_median_household_income` FULL — band against same-remoteness (3 sparse Census points; **OI-29 queued: should be Lite per DEC-75**)
- `sa2_median_total_income` FULL — band against same-remoteness (5 dense annual points 2018-2022)
- `sa2_lfp_persons` LITE — 3 Census points (SALM-extension V1.5)
- `sa2_lfp_females` LITE — 3 Census points (permanent)
- `sa2_lfp_males` LITE — 3 Census points (permanent)
- `jsa_vacancy_rate` CONTEXT — moved to Workforce supply block (DEC-76)

**Workforce Supply Context block** (sub-pass 4.3.9 + 4.2-A.3a-fix iter 3-4):
- Own local window selector: **6M / 1Y / 2Y / 5Y / All** (default 2Y)
- Y-axis: `beginAtZero=false`, padded min/max so monthly variance is readable
- Trajectory polish: dot points, vertical crosshair on hover, external HTML readout above each chart (matches Catchment / Population / Labour treatment)
- 4 rows:
  - Child carer vacancy index (ANZSCO 4211) — JSA IVI live + permanent **About this measure** explainer
  - ECT vacancy index (ANZSCO 2411) — JSA IVI live + permanent About this measure explainer
  - ECEC Award rates — pending (Fair Work ingest)
  - 3-Day Guarantee policy — live (national policy fact)

**Trajectory chart polish** (4.2-A.3a-fix):
- Sparkline trajectories show visible dot points at every period
- Vertical dashed crosshair tracks cursor and snaps to nearest data index
- Chart.js native tooltip replaced with external HTML readout in a fixed slot above each canvas — period + value + since-window-start trend %
- Sparkline X-axis labels show with `maxTicksLimit=5`, `autoSkip=true`

**Empty-state copy** — unemployment row in SALM-suppressed SA2s renders a named small-population-suppression note (Thread A 4.3.1).

**Standalone module ready for Layer 4.2-A consumption:**
- `catchment_calibration.py` v1 (sub-pass 4.3.4) — STD-34 calibration function. Now actively consumed: per-SA2 calibrated_rate + rule_text in `service_catchment_cache`, propagated into payload via centre_page.py v13 `_read_calibration_meta`, surfaced in DER tooltip via centre.html v3.18 `_buildCalibrationRow`.

**What is NOT yet on the centre page:**
- Subtype-aware new-centre overlay on `sa2_supply_ratio` trajectory (sub-pass 4.2-A.3c, queued; ~1.0 session; locked design D6=c — only supply_ratio gets a trajectory chart, the other 3 banded ratios stay histogram-only by intent per data-honesty principle P-2)

---

## Phase 2.5 — status by layer

| Layer | Description | Status |
|---|---|---|
| 0 | Operator + corporate identity | COMPLETE |
| 1 | Service NOW slice | COMPLETE |
| 2 | SA2 cohort + remoteness | COMPLETE |
| 2.5 | Catchment cache populator | COMPLETE 2026-04-30 (sub-passes 2.5.1 + 2.5.2 shipped; 18,203 cache rows, 9,035 layer3 banding rows) |
| 3 | Layer 3 banding (existing 14 metrics) | COMPLETE |
| 4.1 | Layer 3 banding render-side | COMPLETE |
| **4.2** | **Centre page renderer** | **In flight** — 4.2-A.3 + 4.2-A.3a-fix + 4.2-A.3b + 4.2-A.4 SHIPPED; **only 4.2-A.3c remains** (subtype-aware overlay, ~1.0 session) |
| 4.3 | Centre page polish + workforce | COMPLETE — all 9 sub-passes shipped |
| 4.4 | V1.5 ingests (NES + parent-cohort + schools + SALM-ext) | DEFERRED to V1.5 |

---

## What's next

V1 path remaining: **~1.3 sessions** if Layer 4.2-A.3c lands. V1.5 path adds ~2.0 sessions (Layer 4.4 ingests bundle).

**Recommended next-session order** (per ROADMAP § 8):
1. **OI-29** (~0.1 session) — reclassify `sa2_median_household_income` to Lite weight per DEC-75. Trivial. Can interleave anywhere.
2. **4.2-A.3c** (~1.0 session) — subtype-aware new-centre overlay on supply_ratio trajectory. Largest visible UX upgrade remaining. Requires `build_sa2_history.py` rebuild for subtype tagging.
3. **OI-12** (~0.1 session) — backup pruning. `data/` >5.8 GB and growing.
4. **STD-13** (~0.1 session) — WMIC → Get-CimInstance Win32_Process rewrite. Falls through with warning every invocation.

See ROADMAP.md for full dependency-ordered queue.

---

## Database state

Path: `data\kintell.db` (~565 MB).

36 tables. No DB mutations this session — Layer 4.2-A.4 was a code-only ship (backend reads from existing cache columns; renderer reads from existing payload fields).

`audit_log` unchanged at 142 rows (no new mutations).

**OI-12 backup pruning is now status-critical.** Cumulative backups in `data/` exceed 5.8 GB. Approaching the threshold where a single git operation (which scans the working tree) can time out.

---

## Git state

HEAD: `528f9be` (Layer 4.2-A.4: STD-34 calibration metadata surfaced in DER tooltip).
`origin/master`: `528f9be` (in sync after this session's pushes).

Today's commits (chronological):
1. `a4104b6` — 2026-04-30 doc set landing (PROJECT_STATUS + ROADMAP + OPEN_ITEMS regen + PHASE_LOG append). Closed the doc-discipline gap from the prior session.
2. `6d30d33` — OI-25 closed (premise dissolved by probe), OI-29 opened (Lite weight reclassification per DEC-75).
3. `528f9be` — Layer 4.2-A.4: STD-34 calibration metadata surfaced in DER tooltip (centre_page.py v12→v13 + centre.html v3.17→v3.18, two-commit DEC-22 pattern collapsed).

Plus the doc-set regen commit landing this monolith and the regenerated Tier-2 docs (separate commit; reference at end of PHASE_LOG).

Untracked (gitignored): patch scripts, recon probe artefacts, frontend backups in `docs/`. The `*.v?_backup_*` ignore pattern uses single `?` so `v3_3` doesn't match — minor gitignore tightening worth a 30-second pass at the next consolidation.

---

## Parallel work streams

**Daily-rate centre-page integration** — flagged but no progress. STD-36+ note holds.

**Industry view (training_completions)** — data ready (768 rows; CHC30113/30121/50113/50121 across 2019-2024). Editorial disposition: kept at Industry view per DEC-36.

**SALM extension** — SALM source publishes participation_rate at SA2; ingest scope can be extended (~0.5–0.6 session). Bundled with V1.5 OI-19.

---

## Open items summary

See OPEN_ITEMS.md for full text.

**Closed this session (2026-05-03):**
- **OI-25** — `sa2_median_household_income` trajectory shows single point. Probe (`probe_oi25_income_trajectory.py`, read-only, Patcher pattern per STD-10) confirmed backend correctness: DB has 11 rows for the metric on test SA2 118011341; backend `_metric_trajectory` returns 3 non-null points (2011, 2016, 2021); renderer draws 3 dots when Trend Window is "All". The "single point" symptom was visible only on shorter Trend Windows where Census 5-year cadence + window clipping leaves 2021 alone. No backend bug; no renderer bug. Real residual issue → tracked as OI-29.

**Opened this session (2026-05-03):**
- **OI-29** — `sa2_median_household_income` should be Lite weight per DEC-75. Three Census points is not a trajectory; same logic LFP triplet got. ~0.1 session, renderer-only (set `row_weight: "lite"` on the metric in `LAYER3_METRIC_META`). Note the asymmetry inside the income triplet: `sa2_median_employee_income` and `sa2_median_total_income` have annual cadence (5 dense points 2018-2022) and stay Full.

**Carried (unchanged):** OI-01–OI-04 (data quality), OI-06–OI-22 (assorted), OI-24 (DEC-65 protocol traceability), OI-26 (demand_supply industry threshold post-launch review), OI-27 (sa2_history.json subtype rebuild for 4.2-A.3c), OI-28 (populator banner cosmetic).

---

## Doc set

The 2026-04-28 restructure produced the 12-doc set. Update history:
- 2026-04-29c+d: Layer 4.3 design closure + 8 of 9 sub-passes shipped
- 2026-04-30: Layer 4.3 closeout (4.3.5 + 4.3.5b) + Layer 2.5 ship + Layer 4.2-A.3 + 4.2-A.3a-fix + 4.2-A.3b. **Doc updates regenerated but not landed** until 2026-05-03 (the doc-discipline gap that triggered this session's STD-35 enforcement work).
- **2026-05-03: doc-discipline catch-up + Layer 4.2-A.4 + OI-25 dissolution + OI-29 add.** This session regenerated PROJECT_STATUS, ROADMAP, OPEN_ITEMS (already landed via 30/04 patcher path); appended PHASE_LOG entry; produced the 2026-05-03 monolith.

STANDARDS and DECISIONS unchanged this session (no new STDs / DECs). DEC-77 candidate (industry threshold framework) flagged for next-session lock pending operator-use validation.

**STD-35 reinforcement candidate (not yet a STD addition):** the 30/04 → 03/05 doc-discipline gap demonstrated that "regenerate the artefacts at session end" is necessary but not sufficient — the artefacts also need to make it onto disk and into project knowledge. Worth a 2-line addition to STD-35 (or a new STD) requiring an explicit "files moved to disk + monolith uploaded to project knowledge" verification step before declaring session-end. Note for the next consolidation pass.
