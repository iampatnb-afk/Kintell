# Roadmap

*Last updated: 2026-05-04 (end of full-day session). The on-disk version supersedes the project-knowledge monolith if they disagree.*

---

## 1. V1 launch scope

**V1 is at HEAD `bcdf84c`.** All blocking V1 items shipped 2026-05-03 evening. No mandatory V1 work remaining.

### COMPLETE (as of 2026-05-04 end of day)

- Layer 0–4.1 foundations
- **Layer 2.5** — Catchment cache populator (2026-04-30)
- **Layer 4.3** — All 9 sub-passes (2026-04-29 → 2026-04-30)
- **Layer 4.2-A.3** — Catchment ratios wired into centre page (2026-04-30)
- **Layer 4.2-A.3a-fix** — Trajectory chart polish (2026-04-30)
- **Layer 4.2-A.3b** — Industry-absolute thresholds (2026-04-30)
- **Layer 4.2-A.4** — STD-34 calibration metadata in DER tooltip (2026-05-03 AM)
- **Layer 4.2-A.3c** — Catchment trajectories + new-centre overlay (2026-05-03 PM)
- **OI-29 close** — `sa2_median_household_income` reclassified to Lite per DEC-75 (2026-05-03 PM)
- **OI-12 inventory** — read-only audit_log + table snapshot of all backups (2026-05-03 PM)
- **STD-13 helper** — `proc_helpers.py` with Get-CimInstance Win32_Process pattern (2026-05-03 PM)
- **OI-32 close** — Catchment metric explainer text shipped across 3 polish rounds (2026-05-03 evening)
- **OI-30 close** — pre-2019 pop_0_4 coverage gap closed by probe (2026-05-03 evening; real fix folds into OI-19)
- **DEC-77 mint** — Industry-absolute threshold framework formalised (2026-05-03 evening)
- **C3 (OI-34)** — Absolute-change rendered alongside trend % on trajectory charts (commit `f47a0ba`, 2026-05-04 morning)
- **V1.5 scoping doc** — `CENTRE_PAGE_V1.5_ROADMAP.md` (commit `f92b517`, 2026-05-04 morning)
- **A1 dissolution** — ABS source publishes `'-'` for pre-2019 SA2 under-5 (probe-driven 2026-05-04 morning)
- **A2 end-to-end** — NES share ingest + unit fix + populator wire (commits `fdc85bd` + `49ce9f1` + `bb21f66`, 2026-05-04)
- **B2** — `sa2_nes_share` added to `layer3_apply.py` METRICS, banded into `layer3_sa2_metric_banding` (commit `d02e26e`, 2026-05-04 PM; 2,417 rows)
- **C2-NES (data side)** — `sa2_nes_share` registered in `LAYER3_METRIC_META` + INTENT_COPY + TRAJECTORY_SOURCE (commit `3ddcf18`, 2026-05-04 PM)

### REMAINING (V1 launch path)

Nothing blocking. V1 ships at `bcdf84c`.

---

## 2. V1.5 path (~2.6 sessions remaining)

**Canonical:** `CENTRE_PAGE_V1.5_ROADMAP.md` (the centre-page V1.5 source of truth).

| Phase | Items | Effort |
|---|---|---|
| Phase A core | A3 + A4 + A5 + A6 | ~1.4 sess |
| Phase B core | B1 + B3 + B4 + B5 | ~0.9 sess |
| Phase C core | OI-36 + C2 (other) + C6 | ~0.6 sess (OI-36 = recommended first piece, ~0.3 sess) |
| **V1.5 core total** | | **~2.6 sess** |
| Phase 2 (banked, post-V1.5) | A10 + C8 (T08 + Demographic Mix narrative panel) | ~0.7 sess |

---

## 3. Priority polish (when ready)

| Item | Effort | Notes |
|---|---|---|
| **OI-36** | ~0.3 sess | C2-NES render-side. **RECOMMENDED FIRST PIECE next session.** Closes the visible-on-page gap from 2026-05-04. |
| **OI-31** | ~1.0 sess | Click-on-event detail (popup with centre names + place changes when clicking a vertical event line). Substantial renderer feature; explicitly deferred from V1.5 ship slice. |
| **OI-26** | ~0.2 sess | demand_supply post-launch threshold review under DEC-77. |

---

## 4. Layer 4.3 design decisions — closure status

All Layer 4.3 design decisions resolved by 2026-04-29 closure session and shipped through 4.3.x sub-passes by 2026-04-30:

- DEC-74 (perspective toggle on reversible ratio pairs) — AMENDED 2026-05-03; removed for catchment metrics post-Lite→Full promotion.
- DEC-75 (visual weight by data depth) — LIVE.
- DEC-76 (Workforce supply context block) — LIVE.
- STD-34 (calibration discipline) — LIVE; **NES nudge now firing** post-A2.
- DEC-77 (Industry-absolute threshold framework) — LOCKED 2026-05-03 evening.

---

## 5. Parallel work streams

### Daily-rate centre-page integration

STD-36+ holds for daily-rate work. Integration into centre page deferred until daily-rate metric set is stable. A8 / B7 / C7 in CENTRE_PAGE_V1.5_ROADMAP track this dependency.

### Industry view

`training_completions` data is ready (768 rows). Editorial disposition kept at Industry view per DEC-36.

### Operator page

Operator-page work explicitly out of CENTRE_PAGE_V1.5_ROADMAP scope. Needs separate scoping pass when picked up.

---

## 6. Housekeeping items

- **OI-12** — DB backup pruning. **CRITICAL** at ~8.5 GB cumulative (+2.7 GB this session across 5 new backups). Keep policy needs relaxation. ~0.2 sess to relax-and-apply.
- **OI-35** — `layer3_apply.py` wholesale-rebuild bug. Workaround in place; real fix ~0.5 sess.
- **OI-13** — Frontend file backups gitignore tightening. 30-second fix.
- **OI-14** — Backfill audit for DD/MM/YYYY date parsing. Codebase scan candidate.
- **OI-15** — Backfill audit for ARIA+ format mismatch. Codebase scan candidate.
- **OI-10** — `provider_management_type` enum normalisation.
- **OI-28** — `populate_service_catchment_cache.py` cosmetic banner mismatch (5 sec).
- **STD-37 candidate** — "search project knowledge before probing" mint.
- **Recon probe sweep** — root probes → `recon/probes/`.
- **STD-35 hygiene catch-up** — three Tier-2 regens missing from `7e1ab91` doc-refresh commit (PROJECT_STATUS, ROADMAP, OPEN_ITEMS); landing in next session's first commit.

---

## 7. Doc set housekeeping

The 2026-04-28 restructure produced the 12-doc set, since extended with `CENTRE_PAGE_V1.5_ROADMAP.md`. Update history:

- 2026-04-29c+d → 2026-04-30 → 2026-05-03 AM → 2026-05-03 PM → 2026-05-03 evening (V1 ship at `bcdf84c`)
- **2026-05-04 (full day):** V1.5 scoping pass + C3 + A1 dissolution + A2 end-to-end + B2 + C2-NES (data side) + OI-34 closed + OI-35 / OI-36 minted. End-of-session commit `7e1ab91` landed `CENTRE_PAGE_V1_5_ROADMAP.md` + monolith only; PROJECT_STATUS / ROADMAP / OPEN_ITEMS regens missing from that commit and being caught up next session.

---

## 8. Sequencing rules

1. **Search project knowledge before probing** (banked 2026-05-04 — STD-37 candidate)
2. **Renderer-best-practice ahead of plumbing** (locked 2026-04-29)
3. **Probe before code** (DEC-65)
4. **Unit conventions explicit at scoping time** (banked 2026-05-04)
5. **STD-30 pre-mutation discipline** for any DB write
6. **STD-35** end-of-session monolith + on-disk doc refresh + project-knowledge upload
7. **STD-36** session-start uploads
8. **Two-commit DEC-22 pattern** (collapsable when verified together)
9. **Patcher pattern** STD-10 + STD-12 + STD-13
10. **Always run `layer3_x_catchment_metric_banding.py` after `layer3_apply.py`** until OI-35 real fix lands

---

## 9. What the next session should pick up

**Recommended first piece: OI-36 (C2-NES render-side, ~0.3 sess).** Per CENTRE_PAGE_V1.5_ROADMAP §"First-piece recommendation":

- Closes the visible-on-page gap from 2026-05-04 (NES is registered + banded + wired but invisible).
- Small, well-bounded.
- Makes the calibration nudge real and standalone-visible to the operator.
- Unblocks Phase 2 (C8 narrative panel which builds on the NES row).

**After OI-36, evaluate:**
1. Continue Phase A (A3 parent-cohort 25-44, then A4 schools, A5 subtype-correct denominators, A6 SALM-extension)
2. OR pivot to Phase 2 (A10 + C8 — T08 country-of-birth + Demographic Mix narrative panel) for fast visible enrichment

**Pre-OI-36 housekeeping** (optional, opportunistic):
- Land the catch-up Tier-2 doc regens (this file, PROJECT_STATUS, OPEN_ITEMS) before any code work — closes the STD-35 gap from 2026-05-04
- OI-12 backup pruning if disk pressure noticed
