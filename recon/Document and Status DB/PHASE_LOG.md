## 2026-04-29 — Layer 4.3 design closure

**Session type:** Decision closure + doc-set update. No code, no DB mutation.

**Context entering session.** Layer 4.3 design v1.0 (`recon/layer4_3_design.md`, committed 2026-04-28b) had surfaced four decisions G1–G4 + §9.4 plus three implementation threads A/B/C. Closure was tracked as OI-18, gating Layer 4.3 implementation.

**Work shipped this session.**

**1. Layer 4.3 design closures.** Worked through all five threads:
- **G1 + G2 merged → DEC-74** (Perspective toggle on reversible ratio pairs). Recognised that supply_ratio/child_to_place and demand_supply/demand_supply_inv form two interpretive pairs. Per-row toggle pill swaps primary metric, band-copy template, and intent-copy line; preserves underlying decile. Default = credit lens. Supersedes DEC-72 by promoting its conventions into the toggle pattern.
- **G3 → STD-34 locked.** Calibration discipline moved from STAGED to locked. `catchment_calibration.py` is the named module. `calibrate_participation_rate()` signature locked: `(income_decile, female_lfp_pct, nes_share_pct, aria_band) → (rate, rule_text)`. Default 0.50, range [0.43, 0.55], ±0.02 nudges.
- **G4 → OI-19.** Layer 4.4 ingests (NES, parent-cohort 25–44, schools) deferred to V1.5. Documented gap on calibration function's NES nudge; promote immediately post-V1.
- **G5 added → DEC-75** (Visual weight by data depth). Three row weights: Full / Lite / Context-only. LFP triplet reclassified Lite (3 Census points isn't a trajectory); `jsa_vacancy_rate` reclassified Context-only and moves to the new Workforce supply context block.
- **Thread D added → DEC-76** (Workforce supply context block). New Position-level block alongside Population and Labour Market. Default open per credit-lens user. V1 rows: JSA IVI ANZSCO 4211 + 2411 (state-level vacancy), ECEC Award rates (national), Three-Day Guarantee policy (national). Each row has explicit "state-level — no SA2 peer cohort" stamp.
- **§9.4** implicitly resolved by 2026-04-28 doc restructure landing.

**2. Discipline call-out and corrective regen.** Mid-session, the user flagged two discipline gaps in how the closures were initially captured:
- The first attempt produced `recon/layer4_3_design_amendment_v1_1.md` as a separate file alongside the v1.0 design doc. Per STD-02 + STD-03/DEC-30, the correct artefact is `recon/layer4_3_design.md` with `v1.1` in the header — one design doc per layer, version-tracked.
- The closures were not promoted into the canonical structured docs in the same session.

The corrective work in this session: regenerated `recon/layer4_3_design.md` as v1.1 (replacing the amendment file, which is to be deleted in this session's commit), and fully updated DECISIONS.md, STANDARDS.md, OPEN_ITEMS.md, ROADMAP.md, PROJECT_STATUS.md to land the closures in the canonical doc set.

**Files touched:**
- `recon/layer4_3_design.md` v1.1 (replaces v1.0)
- `recon/layer4_3_design_amendment_v1_1.md` (deleted — superseded by v1.1)
- `recon/Document and Status DB/DECISIONS.md` (DEC-74, DEC-75, DEC-76 added; DEC-72 marked superseded; DEC-23, DEC-32, DEC-36 cross-references updated)
- `recon/Document and Status DB/STANDARDS.md` (STD-34 promoted from STAGED to locked)
- `recon/Document and Status DB/OPEN_ITEMS.md` (OI-18 closed; OI-19, OI-20, OI-21, OI-22 added; OI-06, OI-07, OI-11, OI-17 updated)
- `recon/Document and Status DB/ROADMAP.md` (Layer 4.3 effort 1.7 → 2.5 sessions; sub-passes revised; §3 closures logged; V1 path 5.4 → 6.2 sessions)
- `recon/Document and Status DB/PROJECT_STATUS.md` (refreshed for 2026-04-29)
- `recon/PHASE_LOG.md` (this entry)

**Effort estimates revised:**
- Layer 4.3: 1.7 → 2.5 sessions (+0.8 for DEC-74 toggle, DEC-75 row-weight, DEC-76 block, NCVER probe)
- Layer 4.2-A: unchanged at ~2.2 sessions
- Layer 4.4: unchanged at ~1.5 sessions (deferred per OI-19)
- V1 path remaining: 5.4 → 6.2 sessions

**No DB mutation.** No code shipped. No `audit_log` rows added.

**State at session end.** Layer 4.3 design v1.1 closed. Implementation now unblocked. Next session: Layer 4.3 sub-pass 4.3.1 (Thread A — per-chart range buttons on unemployment) per ROADMAP §1.

---

## 2026-04-29 — Layer 4.3 design closure

**Session type:** Decision closure + doc-set update. No code, no DB mutation.

**Context entering session.** Layer 4.3 design v1.0 (`recon/layer4_3_design.md`, committed 2026-04-28b) had surfaced four decisions G1–G4 + §9.4 plus three implementation threads A/B/C. Closure was tracked as OI-18, gating Layer 4.3 implementation.

**Work shipped this session.**

**1. Layer 4.3 design closures.** Worked through all five threads:
- **G1 + G2 merged → DEC-74** (Perspective toggle on reversible ratio pairs). Recognised that supply_ratio/child_to_place and demand_supply/demand_supply_inv form two interpretive pairs. Per-row toggle pill swaps primary metric, band-copy template, and intent-copy line; preserves underlying decile. Default = credit lens. Supersedes DEC-72 by promoting its conventions into the toggle pattern.
- **G3 → STD-34 locked.** Calibration discipline moved from STAGED to locked. `catchment_calibration.py` is the named module. `calibrate_participation_rate()` signature locked: `(income_decile, female_lfp_pct, nes_share_pct, aria_band) → (rate, rule_text)`. Default 0.50, range [0.43, 0.55], ±0.02 nudges.
- **G4 → OI-19.** Layer 4.4 ingests (NES, parent-cohort 25–44, schools) deferred to V1.5. Documented gap on calibration function's NES nudge; promote immediately post-V1.
- **G5 added → DEC-75** (Visual weight by data depth). Three row weights: Full / Lite / Context-only. LFP triplet reclassified Lite (3 Census points isn't a trajectory); `jsa_vacancy_rate` reclassified Context-only and moves to the new Workforce supply context block.
- **Thread D added → DEC-76** (Workforce supply context block). New Position-level block alongside Population and Labour Market. Default open per credit-lens user. V1 rows: JSA IVI ANZSCO 4211 + 2411 (state-level vacancy), ECEC Award rates (national), Three-Day Guarantee policy (national). Each row has explicit "state-level — no SA2 peer cohort" stamp.
- **§9.4** implicitly resolved by 2026-04-28 doc restructure landing.

**2. Discipline call-out and corrective regen.** Mid-session, the user flagged two discipline gaps in how the closures were initially captured:
- The first attempt produced `recon/layer4_3_design_amendment_v1_1.md` as a separate file alongside the v1.0 design doc. Per STD-02 + STD-03/DEC-30, the correct artefact is `recon/layer4_3_design.md` with `v1.1` in the header — one design doc per layer, version-tracked.
- The closures were not promoted into the canonical structured docs in the same session.

The corrective work in this session: regenerated `recon/layer4_3_design.md` as v1.1 (replacing the amendment file, which is to be deleted in this session's commit), and fully updated DECISIONS.md, STANDARDS.md, OPEN_ITEMS.md, ROADMAP.md, PROJECT_STATUS.md to land the closures in the canonical doc set.

**Files touched:**
- `recon/layer4_3_design.md` v1.1 (replaces v1.0)
- `recon/layer4_3_design_amendment_v1_1.md` (deleted — superseded by v1.1)
- `recon/Document and Status DB/DECISIONS.md` (DEC-74, DEC-75, DEC-76 added; DEC-72 marked superseded; DEC-23, DEC-32, DEC-36 cross-references updated)
- `recon/Document and Status DB/STANDARDS.md` (STD-34 promoted from STAGED to locked)
- `recon/Document and Status DB/OPEN_ITEMS.md` (OI-18 closed; OI-19, OI-20, OI-21, OI-22 added; OI-06, OI-07, OI-11, OI-17 updated)
- `recon/Document and Status DB/ROADMAP.md` (Layer 4.3 effort 1.7 → 2.5 sessions; sub-passes revised; §3 closures logged; V1 path 5.4 → 6.2 sessions)
- `recon/Document and Status DB/PROJECT_STATUS.md` (refreshed for 2026-04-29)
- `recon/PHASE_LOG.md` (this entry)

**Effort estimates revised:**
- Layer 4.3: 1.7 → 2.5 sessions (+0.8 for DEC-74 toggle, DEC-75 row-weight, DEC-76 block, NCVER probe)
- Layer 4.2-A: unchanged at ~2.2 sessions
- Layer 4.4: unchanged at ~1.5 sessions (deferred per OI-19)
- V1 path remaining: 5.4 → 6.2 sessions

**No DB mutation.** No code shipped. No `audit_log` rows added.

**State at session end.** Layer 4.3 design v1.1 closed. Implementation now unblocked. Next session: Layer 4.3 sub-pass 4.3.1 (Thread A — per-chart range buttons on unemployment) per ROADMAP §1.

---


## 2026-04-29 (continued) — Layer 4.3 sub-pass 4.3.1 (Thread A) + STD-35

**Context:** Resumed from the 2026-04-29 design-closure session. Implemented the first sub-pass of Layer 4.3 implementation. Surfaced and resolved a structural memory gap: project knowledge in claude.ai and the git repo are independent stores; without explicit synchronisation, every session starts blind. Codified the fix as STD-35.

**Shipped:**
- `docs/centre.html` v3.2 → v3.3 — Layer 4.3 sub-pass 4.3.1 (Thread A): per-chart range buttons (1Y/2Y) on the unemployment metric (`sa2_unemployment_rate`), and improved empty-state copy for SALM-missing SA2s.
- `recon/layer4_3_thread_a_probe.md` — probe + apply artefact, decisions A1–A6 closed in-line.

**Code mechanics:**
- New globals on `centre.html`: `_TRAJECTORY_OVERRIDE_YEARS` (per-metric override map), `_PER_CHART_RANGE_OPTIONS` (lookup, currently `{sa2_unemployment_rate: [1, 2]}`).
- New helpers: `_getEffectiveRangeYears(metric)`, `_setPerChartRange(metric, years, btnEl)`, `_renderPerChartRangeBar(metric)`.
- `_renderTrajectory(metric, p)` rewired to read effective range via `_getEffectiveRangeYears()`; per-chart bar emitted on both normal and empty-state returns.
- `renderPositionRow` `unavailable` branch extended: unemployment row gets a named SALM-suppression note instead of the silent em-dash; other metrics retain the em-dash.
- Net delta: +87 lines, all additive. No deletions, no payload-schema bump, no `centre_page.py` change.

**Decisions:**
- A1–A6 closed (per-chart state model, button placement, click-to-toggle semantics, metric-keyed lookup, SALM-missing copy, override scope). Recorded in `recon/layer4_3_thread_a_probe.md` §3 — implementation choices within DEC-73's scope, not new architectural decisions; no entries added to `DECISIONS.md`.

**Standards:**
- STD-35 (Process category) — Cross-session continuity via end-of-session monolith. Codifies the three-tiered project-knowledge / git-repo synchronisation discipline. Range bumped 1–34 → 1–35 in `STANDARDS.md`.

**Open items:**
- OI-23 raised (Low) — global trend-window bar disappears when Population card has no live data; Thread A makes the brittleness more material. Fix slotted for sub-pass 4.3.6 layout work. Recorded in `OPEN_ITEMS.md`.

**Doc updates this turn:**
- `STANDARDS.md` — STD-35 added; footer numbering note updated.
- `OPEN_ITEMS.md` — OI-23 added.
- `PROJECT_STATUS.md` — `centre.html` v3.3 stamped; sub-pass 4.3.1 marked SHIPPED; remaining sub-pass count updated; OI-23 added to summary; doc-set table STANDARDS row bumped (1–35, STD-35 added); V1 path remaining 6.2 → 5.9 sessions.
- `recon/PHASE_LOG.md` — this entry.

**Not yet done (carry forward):**
- Re-upload of the structured doc set to project knowledge — this session's regenerated docs (`STANDARDS.md`, `OPEN_ITEMS.md`, `PROJECT_STATUS.md`) need to land in claude.ai project knowledge before next session starts, otherwise the next chat opens with the same gap STD-35 was created to close.
- End-of-session Tier-2 monolith per STD-35 — should be produced now (or at next session close).

**Files committed this session (cumulative across both halves of 2026-04-29):**
- `recon/Document and Status DB/DECISIONS.md` (DEC-74, 75, 76)
- `recon/Document and Status DB/STANDARDS.md` (STD-34 locked; STD-35 added)
- `recon/Document and Status DB/OPEN_ITEMS.md` (OI-19, 20, 21, 22, 23 added; OI-18 closed)
- `recon/Document and Status DB/ROADMAP.md`
- `recon/Document and Status DB/PROJECT_STATUS.md`
- `recon/Document and Status DB/PHASE_LOG.md` (this entry + design-closure entry)
- `recon/layer4_3_design.md` v1.1 (closure session, retired post-consolidation)
- `recon/layer4_3_thread_a_probe.md` (apply session)
- `docs/centre.html` v3.3

