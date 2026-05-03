# Project Status

*Last updated: 2026-05-03 (end of afternoon session). The on-disk version supersedes the project-knowledge monolith if they disagree.*

## Headline

**V1 is at HEAD.** All blocking V1 work shipped. The remaining items in the V1 queue (4.2-A.3c, OI-29, OI-12, STD-13) all landed this session. What remains is V1.5 polish + the deferred Bug 4 (helper text length / explainer copy) which Patrick will handle when he sees a third screenshot.

## Centre page — current state

`centre_page.py` v16 (Python backend) + `centre.html` v3.21 (renderer) + payload schema `centre_payload_v6` (unchanged this session — v15/v16 added fields, no schema rev).

Major Layer 4.2-A.3c shipment lands the catchment-trajectory feature end-to-end:
- All 4 banded catchment metrics (sa2_supply_ratio, sa2_child_to_place, sa2_demand_supply, sa2_adjusted_demand) promoted Lite→Full
- Quarterly trajectories rendered with same chart treatment as Population/Labour Market (dot points, crosshair, external readout)
- Per-subtype centre_events overlay (vertical dashed coloured lines): green for additions, red for removals, grey for net-zero churn
- Centre page now drives all subtype-specific data from `docs/sa2_history.json` (v2, multi-subtype build, 13.2 MB)

**POSITION block — Catchment position card (after Layer 4.2-A.3c):**

| Metric | Weight | Trajectory | Events overlay | Industry band | Calibration in DER |
|---|---|---|---|---|---|
| `sa2_supply_ratio` | FULL | quarterly per subtype | YES (subtype-matched) | 7 levels | — |
| `sa2_demand_supply` | FULL | quarterly (cal_rate held constant) | YES | 4 levels | YES (4.2-A.4) |
| `sa2_child_to_place` | FULL | quarterly (1/supply_ratio) | YES | 5 levels | — |
| `sa2_adjusted_demand` | FULL | quarterly (cal_rate held constant) | YES | NO (decile only) | YES (4.2-A.4) |
| `sa2_demand_share_state` | CONTEXT | n/a | n/a | n/a | YES (4.2-A.4) |

**DEC-74 amendment:** perspective toggle removed from the 3 reversible catchment metrics. Once both inverse views (supply_ratio ↔ child_to_place) render as separate Full rows in the same card, the toggle just swapped to data already visible.

**Subtype handling.** The centre's `service_sub_type` (LDC / OSHC / PSK / FDC) drives which `by_subtype.<>` block in sa2_history.json gets read. Null/Other subtypes fall back to LDC view. LDC is the V1 focus (53% of platform); OSHC/PSK/FDC trajectories use the same `pop_0_4` denominator across all subtypes (documented known simplification — subtype-correct denominators are V1.5+).

**Calibration semantics.** `adjusted_demand` and `demand_supply` use the centre's CURRENT `calibrated_rate` held constant across all historical quarters. Honest framing: "supply trajectory adjusted for current demand structure." Will surface explicitly in helper text once Bug 4 explainer copy lands.

**Workforce Supply Context block, Population, Labour Market** — unchanged this session.

---

## Phase 2.5 — status by layer

| Layer | Description | Status |
|---|---|---|
| 0 / 1 / 2 | Foundations | COMPLETE |
| 2.5 | Catchment cache populator | COMPLETE 2026-04-30 |
| 3 / 4.1 | Layer 3 banding existing 14 metrics + render-side | COMPLETE |
| **4.2** | **Centre page renderer** | **COMPLETE** — all sub-passes shipped (4.2-A.3, 4.2-A.3a-fix, 4.2-A.3b, 4.2-A.4, 4.2-A.3c) |
| 4.3 | Centre page polish + workforce | COMPLETE — all 9 sub-passes |
| 4.4 | V1.5 ingests (NES + parent-cohort + schools + SALM-ext) | DEFERRED to V1.5 |

---

## What's next

V1 path remaining: **~0 sessions.** Optional polish below.

**Priority polish (when Patrick is ready):**
1. **Bug 4 (explainer text)** — currently deferred per "Patrick will recall later". Larger explainer per metric, especially adjusted_demand. Renderer-only, ~10-30 min depending on copy provided.
2. **OI-30 (Bayswater data sparsity)** — investigate ABS pop_0_4 SA2 code coverage. Bayswater 211011251 only has data Q3 2019+; pre-2019 data lives under different ASGS code. Build script needs ASGS concordance step. Real V1.5 ingest fix; estimate ~0.3 session probe + ~0.5 session build script change.

**V1.5 path (~3 sessions):**
- **OI-31 (click-on-event detail)** — interactive overlay showing centre names + place changes when clicking a vertical event line. Substantial feature; ~1 session of renderer work.
- **OI-32 (absolute change alongside %)** — show "+12 places, +1 centre" alongside trend %. ~30 min if scoped narrow.
- **Layer 4.4 ingests** — NES + parent-cohort + schools + SALM-extension bundle. ~2 sessions.

See ROADMAP.md for full dependency-ordered queue.

---

## Database state

Path: `data\kintell.db` (~565 MB). 36 tables. `audit_log: 142 rows` (no DB mutations this session).

`docs/sa2_history.json` rebuilt to v2 multi-subtype shape: 13.2 MB (was 5.2 MB v1), 50 quarters, 1,267 SA2s, 4 subtype buckets. Tracked in git (`docs/` is not gitignored). Future rebuilds land as deltas.

**OI-12 status update:** backup inventory (`recon/db_backup_inventory_2026-05-03.md`) committed `bbac24f` provides queryable record of all 36 backups (audit_log + table+rowcount per backup). Deletion deferred — disk pressure is not currently biting; if it becomes an issue, deletion is now safely reversible.

---

## Git state

HEAD: `bcdf84c` (Layer 4.2-A.3c Part 3). Branch in sync with origin.

Today's commits in two phases:

**Morning (a4104b6 → 16f7e18):**
1. `a4104b6` — 30/04 doc set landing (closed prior-session doc-discipline gap)
2. `6d30d33` — OI-25 closed by probe (premise dissolved); OI-29 opened (Lite weight reclassification per DEC-75)
3. `528f9be` — Layer 4.2-A.4: STD-34 calibration metadata in DER tooltip
4. `16f7e18` — 03/05 morning doc regen

**Afternoon (6a7fe8a → bcdf84c):**
5. `6a7fe8a` — OI-29 closed: sa2_median_household_income → Lite weight (centre_page.py v13→v14)
6. `bbac24f` — OI-12 inventory: read-only audit_log + table snapshot of all 36 data/ backups
7. `1f72226` — STD-13 helper module: `proc_helpers.py` with query_python_processes() + std13_self_check() (Win11-safe; replaces deprecated WMIC)
8. `c70e942` — STD-13 extended in STANDARDS.md: mutation-script variant subsection documents proc_helpers.py as canonical pattern
9. `36c2f78` — Layer 4.2-A.3c Part 2 (build): build_sa2_history.py v2 — LDC-first multi-subtype rebuild
10. `bcdf84c` — Layer 4.2-A.3c Part 3 (renderer wiring + bug fixes): centre_page.py v14→v16 + centre.html v3.18→v3.21

Plus this end-of-session doc commit landing the regenerated Tier-2 docs and the 03/05 PM monolith.

---

## Standards / decisions

**No new STDs/DECs this session.** Two changes to existing:

- **STD-13 extended** (commit `c70e942`): mutation-script variant subsection added documenting `proc_helpers.py` as the canonical orphan-Python detection helper. Historical scripts (4 files: populate_service_catchment_cache.py, layer3_x_catchment_metric_banding.py, migrate_4_3_5_*.py) intentionally NOT retrofitted — already shipped, idempotency-guarded.

- **DEC-74 amended** (this session): perspective toggle removed for the 3 reversible catchment metrics post-Lite→Full promotion. Inverse views now visible as separate rows. Recorded as appended amendment block in DECISIONS.md.

**STD-35 reinforcement candidate** (carried from morning): the 30/04→03/05 doc-discipline gap demonstrated "regenerate at session end" is necessary but not sufficient — "land on disk + upload to project knowledge" needs explicit verification. This session honoured the discipline (this very regen). Worth a 2-line addition to STD-35 at next consolidation.

**STD-13 follow-on observation:** when patcher anchors include line endings, use `\n` not `\r\n` even on Windows source files. Python's text mode normalises to `\n` on read. The v15 patcher initially failed all 8 multi-line anchor checks for this reason; one-line fix worked. Worth a 1-line addition to STD-10 (Patcher pattern) at next consolidation.

---

## Open items summary

See OPEN_ITEMS.md for full text.

**Closed this session:**
- **OI-25** (morning) — Census income trajectory single-point bug. Premise dissolved by probe; backend + renderer correct.
- **OI-29** (afternoon) — sa2_median_household_income reclassified to Lite per DEC-75. Three Census points is not a trajectory.
- **OI-27** (afternoon, by Layer 4.2-A.3c) — sa2_history.json subtype tagging requirement. v2 build delivers per-subtype `centre_events` arrays; renderer consumes them.

**Opened this session:**
- **OI-30** — Bayswater (and likely other 2021-ASGS) SA2 codes have incomplete pre-2019 ABS coverage. Build script needs concordance step to map newer ASGS codes to older ASGS data. Affects trajectory completeness for ~unknown number of SA2s. V1.5 ingest scope.
- **OI-31** — Catchment trajectory event lines should support click → popup showing quarter, net change, list of centre names with places. Substantial renderer feature; V1.5 polish.
- **OI-32** — Catchment metrics need longer "what is this metric?" explainer text in the centre page UI. Especially for `adjusted_demand`. Renderer + content; Patrick to provide copy.

**Carried (unchanged):** OI-01–OI-04 (data quality), OI-06–OI-22 (assorted), OI-24 (DEC-65 protocol traceability), OI-26 (demand_supply industry threshold post-launch review), OI-28 (populator banner cosmetic), OI-12 (status updated: inventory landed, deletion deferred).

---

## Doc set

The 2026-04-28 restructure produced the 12-doc set. Update history:
- 2026-04-29c+d: Layer 4.3 design closure + 8 of 9 sub-passes shipped
- 2026-04-30: Layer 4.3 closeout + Layer 2.5 ship + Layer 4.2-A.3 / 3a-fix / 3b. Doc artefacts produced but not landed until 03/05.
- 2026-05-03 morning: doc-discipline catch-up (30/04 set landed) + Layer 4.2-A.4 + OI-25 dissolution + OI-29 add. Monolith `kintell_project_status_2026-05-03.txt`.
- **2026-05-03 afternoon: OI-29 close + OI-12 inventory + STD-13 helper + Layer 4.2-A.3c (Part 1+2+3) + DEC-74 amendment.** This session regenerated PROJECT_STATUS, ROADMAP, OPEN_ITEMS, appended PHASE_LOG, amended DECISIONS, produced new monolith `kintell_project_status_2026-05-03_pm.txt`.

This doc set reflects state as of HEAD `bcdf84c` (and the doc commit immediately following).
