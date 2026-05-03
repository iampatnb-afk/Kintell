# Project Status

*Last updated: 2026-04-30. The on-disk version supersedes the project-knowledge monolith if they disagree.*

## Centre page — current state

`centre_page.py` v12 (Python backend) + `centre.html` v3.17 (renderer) + payload schema `centre_payload_v6`.

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

**POSITION block — Catchment position card (NEW; sub-pass 4.2-A.3, 4.2-A.3b):**

| Metric | Weight | Reversibility | Industry band |
|---|---|---|---|
| `sa2_supply_ratio` | LITE | reversible ↔ `sa2_child_to_place` | 7 levels (desert / undersupplied / below_bench / at_bench / well_served / at_target / saturated) |
| `sa2_demand_supply` | LITE | reversible ↔ `demand_supply_inv` (HTML-level) | 4 levels (soft / near_be / viable / strong) |
| `sa2_child_to_place` | LITE | reversible ↔ `sa2_supply_ratio` | 5 levels (excess_capacity / balanced / tight / constrained / severe) |
| `sa2_adjusted_demand` | LITE | not reversible | NO industry band (decile only) |
| `sa2_demand_share_state` | CONTEXT | n/a | n/a (rank-by-construction; reads cache directly) |

Two reversible pairs activate the DEC-74 perspective toggle (live in V1).

Each Lite catchment row renders: title + value + decile strip + low/mid/high band chips + INDUSTRY band line (when populated) + intent copy + DER+COM badges.

**POSITION block — Population (4 metrics, 1 deferred):**
- `sa2_under5_count` FULL — band against same-state cohort
- `sa2_total_population` FULL — band against state-x-remoteness
- `sa2_births_count` FULL — band against state-x-remoteness
- `sa2_under5_growth_5y` DEFERRED (placeholder; OI-09)

**POSITION block — Labour Market (7 metrics, 1 deferred):**
- `sa2_unemployment_rate` FULL — band against same-state cohort
- `sa2_median_employee_income` FULL — band against same-remoteness
- `sa2_median_household_income` FULL — band against same-remoteness
- `sa2_median_total_income` FULL — band against same-remoteness
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
- `catchment_calibration.py` v1 (sub-pass 4.3.4) — STD-34 calibration function. Now actively consumed: per-SA2 calibrated_rate + rule_text in `service_catchment_cache`.

**What is NOT yet on the centre page:**
- Subtype-aware new-centre overlay on `sa2_supply_ratio` trajectory (sub-pass 4.2-A.3c, queued)
- Histograms on the 4 banded catchment metrics (deferred to 4.2-A.3c bundle: promote LITE→FULL on those metrics, histograms auto-render via existing `_renderCohortHistogram`)
- DER tooltip surface for `rule_text` per STD-34 (sub-pass 4.2-A.4)

---

## Phase 2.5 — status by layer

| Layer | Description | Status |
|---|---|---|
| 0 | Operator + corporate identity | COMPLETE |
| 1 | Service NOW slice | COMPLETE |
| 2 | SA2 cohort + remoteness | COMPLETE |
| **2.5** | **Catchment cache populator** | **COMPLETE 2026-04-30** (sub-passes 2.5.1 + 2.5.2 shipped; 18,203 cache rows, 9,035 layer3 banding rows) |
| 3 | Layer 3 banding (existing 14 metrics) | COMPLETE |
| 4.1 | Layer 3 banding render-side | COMPLETE |
| **4.2** | **Centre page renderer** | **In flight** — 4.2-A.3 + 4.2-A.3a-fix + 4.2-A.3b SHIPPED; 4.2-A.3c (subtype-aware overlay) NEXT; 4.2-A.4 (DER rule_text surface) QUEUED |
| **4.3** | **Centre page polish + workforce** | **COMPLETE** — all 9 sub-passes shipped (4.3.5 + 4.3.5b closed today) |
| 4.4 | V1.5 ingests (NES + parent-cohort + schools + SALM-ext) | DEFERRED to V1.5 |

---

## What's next

V1 path remaining: ~3.5 sessions if Layer 4.2-A.3c + Layer 4.4 V1.5 ingests land. V1 ships without 4.2-A.3c if needed (it's enrichment, not blocking).

**Immediate next (mechanical):** commit the uncommitted 4.2-A.3b + 4.2-A.3a-fix iter 3+4 work (composite commit covering centre_page.py v9→v12 + centre.html v3.13a→v3.17).

See ROADMAP.md for full dependency-ordered queue.

---

## Database state

Path: `data\kintell.db` (~565 MB; was ~557 MB at session start)

36 tables. Notable populated additions today:
- `service_catchment_cache` — 18,203 rows (was 0; OI-05 closed)
- `layer3_sa2_metric_banding` — +9,035 rows (4 catchment metrics added, 1 unbanded by design)
- `audit_log` — 138 → 142 (5 new rows from this session's mutations)

6 backups created today in `data/`. OI-12 backup-pruning is now status-critical.

---

## Git state

HEAD: `beb7bbe` (Layer 4.2-A.3a-fix: trajectory chart polish).
`origin/master`: `2f95a70` (prior session's HEAD).
Local ahead of origin: **7 commits**.

Today's commits (chronological):
1. `8e944d9` — Layer 4.3 sub-pass 4.3.5: schema migration on `service_catchment_cache`
2. `5eec075` — Layer 4.3 sub-pass 4.3.5b: rename `capture_rate` → `demand_share_state`
3. `a65ee57` — Layer 2.5 sub-pass 2.5.1: populate `service_catchment_cache`
4. `4d49516` — Layer 2.5 sub-pass 2.5.1 v5: fix three null-coverage bugs in populator
5. `b924524` — Layer 2.5 sub-pass 2.5.2: Layer 3.x catchment metric banding
6. `d12da0b` — Layer 4.2-A.3: catchment ratios wired into centre page + credit-block reorder
7. `beb7bbe` — Layer 4.2-A.3a-fix: trajectory chart polish (tooltip + dots + crosshair + external readout)

**Uncommitted on disk** (one composite commit pending, draft in chat):
- `centre_page.py` v9 → v12
- `docs/centre.html` v3.13a → v3.17

Untracked (gitignored): patch scripts, recon probe artefacts, frontend backups.

---

## Parallel work streams

**Daily-rate centre-page integration** — flagged but no progress this session. STD-36+ note holds.

**Industry view (training_completions)** — data ready (768 rows; CHC30113/30121/50113/50121 across 2019-2024). Editorial disposition: kept at Industry view per DEC-36.

**SALM extension** — SALM source publishes participation_rate at SA2; ingest scope can be extended (~0.5–0.6 session). Bundled with V1.5 OI-19.

---

## Open items summary

See OPEN_ITEMS.md for full text. New this session (OI-25 through OI-28):
- **OI-25** — `sa2_median_household_income` trajectory shows single point (2021) instead of three Census years. Backend bug in `_layer3_position` trajectory builder. Affects all Census-source income metrics.
- **OI-26** — `demand_supply` industry thresholds need post-launch calibration review (mathematically grounded but may register false positives in saturated catchments).
- **OI-27** — 4.2-A.3c subtype-aware new-centre overlay requires `sa2_history.json` rebuild with subtype tagging on centre_events.
- **OI-28** — `populate_service_catchment_cache.py` cosmetic banner mismatch (says v2 in print, file is v5; no functional impact).

Closed this session:
- **OI-05** — `service_catchment_cache` populated (sub-pass 2.5.1).
- **OI-23** — Global trend-window bar empty-state caption corrected.

---

## Doc set

The 2026-04-28 restructure produced the 12-doc set. The 2026-04-29c+d closure sessions reflected Layer 4.3 design closure + 8 of 9 sub-passes. **The 2026-04-30 session updated PROJECT_STATUS, ROADMAP, OPEN_ITEMS, PHASE_LOG to reflect Layer 4.3 closeout, Layer 2.5 ship, and the 4.2-A.3 + 4.2-A.3a-fix + 4.2-A.3b run.** STANDARDS and DECISIONS unchanged this session (no new STDs / DECs; DEC-77 candidate flagged for next-session lock if industry thresholds prove themselves in operator use).
