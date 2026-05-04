# Roadmap

*Last updated: 2026-05-05 (end of OI-36 session). The on-disk version supersedes the project-knowledge monolith if they disagree.*

---

## 1. V1 launch scope

**V1 is at HEAD `bcdf84c`.** All blocking V1 items shipped 2026-05-03 evening.

### COMPLETE through 2026-05-05

- Layer 0–4.1 foundations
- **Layer 2.5** — Catchment cache populator (2026-04-30)
- **Layer 4.3** — All 9 sub-passes (2026-04-29 → 2026-04-30)
- **Layer 4.2** — Centre page renderer (V1)
- **Layer 4.4** — A2 NES end-to-end (2026-05-04)
- **OI-34 close** — C3 absolute-change rendering (2026-05-04, commit `f47a0ba`)
- **V1.5 scoping doc** — `CENTRE_PAGE_V1.5_ROADMAP.md` (2026-05-04, commit `f92b517`)
- **A1 dissolution** — ABS source publishes `'-'` for pre-2019 SA2 under-5 (2026-05-04)
- **A2 end-to-end** — NES share ingest + unit fix + populator wire (2026-05-04, commits `fdc85bd` + `49ce9f1` + `bb21f66`)
- **B2** — `sa2_nes_share` banded into `layer3_sa2_metric_banding` (2026-05-04, commit `d02e26e`; 2,417 rows)
- **C2-NES (data side)** — `sa2_nes_share` registered in `LAYER3_METRIC_META` + INTENT_COPY + TRAJECTORY_SOURCE (2026-05-04, commit `3ddcf18`)
- **OI-36 close** — `sa2_nes_share` renders in Catchment Position card + delta badge on Lite rows (2026-05-05, commit `430009a`)
- **STD-35 hygiene catch-up** — Tier-2 docs regenerated for 2026-05-04 EOD content (2026-05-05, commit `9d49be9`)

### REMAINING (V1 launch path)

Nothing blocking. V1 ships at `bcdf84c`.

---

## 2. V1.5 path (~2.7 sessions remaining)

**Canonical:** `CENTRE_PAGE_V1.5_ROADMAP.md` (the centre-page V1.5 source of truth).

| Phase | Items | Effort |
|---|---|---|
| **A10 + C8 (next-session priority)** | Demographic Mix bundle (T07 ATSI + T08 country of birth + T19 single-parent households + Community Profile panel) | **~1.0 sess** |
| Phase A core remaining | A3 + A4 + A5 + A6 | ~1.4 sess |
| Phase B core | B1 + B3 + B4 + B5 | ~0.9 sess |
| Phase C core remaining | C2-other + C6 | ~0.4 sess |
| **V1.5 core total** | | **~2.7 sess** |

---

## 3. Priority polish (when ready)

| Item | Effort | Notes |
|---|---|---|
| **OI-31** | ~1.0 sess | Click-on-event detail (popup with centre names + place changes when clicking a vertical event line). Substantial renderer feature; explicitly deferred from V1.5 ship slice. |
| **OI-26** | ~0.2 sess | demand_supply post-launch threshold review under DEC-77. |

---

## 4. Layer 4.3 design decisions — closure status

All Layer 4.3 design decisions resolved by 2026-04-29 closure session and shipped through 4.3.x sub-passes by 2026-04-30:

- DEC-74 (perspective toggle on reversible ratio pairs) — AMENDED 2026-05-03
- DEC-75 (visual weight by data depth) — LIVE; **extended in spirit 2026-05-05** with delta badge surfacing first-to-last change for Lite rows
- DEC-76 (Workforce supply context block) — LIVE
- STD-34 (calibration discipline) — LIVE; NES nudge live since 2026-05-04
- DEC-77 (Industry-absolute threshold framework) — LOCKED 2026-05-03

---

## 5. Parallel work streams

### Daily-rate centre-page integration

STD-36+ holds for daily-rate work. Integration into centre page deferred until daily-rate metric set is stable. A8 / B7 / C7 in CENTRE_PAGE_V1.5_ROADMAP track this dependency.

### Industry view

`training_completions` data is ready. Editorial disposition kept at Industry view per DEC-36.

### Operator page

Operator-page work explicitly out of CENTRE_PAGE_V1.5_ROADMAP scope. Needs separate scoping pass when picked up.

---

## 6. Housekeeping items

- **OI-12** — DB backup pruning. **CRITICAL** at ~8.5 GB cumulative (carries from 2026-05-04; no new backups this session). Keep policy needs relaxation. ~0.2 sess to relax-and-apply.
- **OI-35** — `layer3_apply.py` wholesale-rebuild bug. Workaround in place; real fix ~0.5 sess.
- **OI-13** — Frontend file backups gitignore tightening (+3 new `pre_oi36*` backups this session). 30-second fix.
- **OI-14** — Backfill audit for DD/MM/YYYY date parsing.
- **OI-15** — Backfill audit for ARIA+ format mismatch.
- **OI-10** — `provider_management_type` enum normalisation.
- **OI-28** — `populate_service_catchment_cache.py` cosmetic banner mismatch (5 sec).
- **STD-37 candidate** — "search project knowledge before probing" mint.
- **Recon probe sweep** — root probes → `recon/probes/` (additionally, several `pre_oi36*` backup files in repo root + `docs/` need either gitignore or sweep).

---

## 7. Doc set housekeeping

The 2026-04-28 restructure produced the 12-doc set, since extended with `CENTRE_PAGE_V1.5_ROADMAP.md`. Update history:

- 2026-04-29c+d → 2026-04-30 → 2026-05-03 AM → 2026-05-03 PM → 2026-05-03 evening (V1 ship at `bcdf84c`)
- 2026-05-04 (full day): V1.5 scoping + C3 + A1 dissolution + A2 + B2 + C2-NES (data side) + OI-34 closed + OI-35 / OI-36 minted. End-of-session commit `7e1ab91` landed only `CENTRE_PAGE_V1.5_ROADMAP.md` + monolith; rest of Tier-2 caught up next session.
- **2026-05-05 (this session):** STD-35 catch-up `9d49be9` + OI-36 close `430009a` + end-of-session doc refresh (this commit, landing now). Tier-2 docs current at 2026-05-05 EOD content.

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
9. **Patcher pattern** STD-10 + STD-12 + STD-28
10. **Always run `layer3_x_catchment_metric_banding.py` after `layer3_apply.py`** until OI-35 real fix lands
11. **Surgical-vs-refactor decision is output of probe, not Phase 0 input** (banked 2026-05-05 from OI-36 experience — first probe over-counted touchpoints; reading the actual code revealed the surgical fix was much smaller than the auto-counter suggested)

---

## 9. What the next session should pick up

**Recommended first piece: A10 + C8 (Demographic Mix bundle, ~1.0 sess).** Per CENTRE_PAGE_V1.5_ROADMAP §"Recommended next session start":

- **A10 ingest pass** — three TSP tables (T07 ATSI, T08 country of birth, T19 single-parent households) all from `2021_TSP_SA2_for_AUS_short-header.zip` already on disk from A2. Same processing pattern. ~0.5 sess.
- **B-pass for the three new metrics** — register in `layer3_apply.py` METRICS, run banding. ~0.1 sess each.
- **C8 panel build** — new Community Profile panel on centre page. Renderer pattern is well-trodden post-OI-36. ~0.5 sess.
- **End-of-session doc refresh.**

**Pre-A10 housekeeping** (optional, opportunistic):
- OI-12 backup pruning if disk pressure noticed
- OI-13 gitignore tightening (3 new untracked backups added this session)

**After A10/C8 lands, evaluate:** continue Phase A (A3 parent-cohort 25-44, then A4 schools, A5 subtype-correct denominators, A6 SALM-extension), then Phase B core, then Phase C core remaining.
