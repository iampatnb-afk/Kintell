# Roadmap

*Last updated: 2026-05-03. The on-disk version supersedes the project-knowledge monolith if they disagree.*

---

## 1. V1 launch scope

V1 path remaining: **~1.3 sessions** if Layer 4.2-A.3c lands. V1 ships at HEAD without 4.2-A.3c if needed (it's enrichment, visually impactful but not blocking).

### COMPLETE (as of 2026-05-03)

- Layer 0–4.1 (operator + service slice + SA2 cohort + Layer 3 banding existing 14 metrics + render-side)
- **Layer 2.5** — Catchment cache populator (sub-passes 2.5.1 + 2.5.2 shipped 2026-04-30)
  - `service_catchment_cache` populated with 18,203 rows
  - 4 new catchment metrics banded into `layer3_sa2_metric_banding` (9,035 rows)
- **Layer 4.3** — All 9 sub-passes shipped (2026-04-29 → 2026-04-30)
- **Layer 4.2-A.3** — Catchment ratios wired into centre page (2026-04-30)
  - 5 catchment metrics rendered as new "Catchment position" card
  - Page reorder per option α: credit block top, operational below
  - DEC-74 perspective toggle live (2 reversible pairs activated)
- **Layer 4.2-A.3a-fix** — Trajectory chart polish (2026-04-30; 4 chained iterations v3.10 → v3.13a, plus workforce extension v3.15, plus workforce-section local trend-window selector v3.16)
- **Layer 4.2-A.3b** — Industry-absolute thresholds on 3 catchment metrics (2026-04-30)
- **Layer 4.2-A.3a-fix iter 4** — JSA IVI permanent "About this measure" explainer (2026-04-30)
- **Layer 4.2-A.4** — STD-34 calibration metadata in DER tooltip (2026-05-03)
  - Backend (centre_page.py v12 → v13): `_read_calibration_meta` helper; `uses_calibration: True` opt-in field on 3 metric entries; per-entry attachment of `calibrated_rate` + `rule_text` to catchment_position metrics
  - Renderer (centre.html v3.17 → v3.18): `renderBadge` gains calibration field handler; `_buildCalibrationRow` helper; wired into Full + Lite + Context row DER badges; `_renderContextRow` gains conditional DER (didn't exist before)
  - Two-commit DEC-22 pattern collapsed to single commit since both files were verified together
  - Verified end-to-end on service_id=103 (Bondi Junction-Waverly)
- **OI-25 dissolved + OI-29 opened** (2026-05-03)
  - Probe (`probe_oi25_income_trajectory.py`, read-only) confirmed backend + renderer correct; "single point" was Trend Window clipping behaviour on Census-cadence data
  - Real residual (Lite-weight reclassification per DEC-75) tracked as OI-29
- **Doc-discipline catch-up** (2026-05-03)
  - 2026-04-30 doc set landed (commit `a4104b6`) — closed the gap between session work and indexed Tier-2 state
  - Project knowledge monolith swap: `kintell_project_status_2026-04-29d.txt` removed; `kintell_project_status_2026-04-30.txt` uploaded
  - 2026-05-03 doc set regenerated this session (this regen)

### REMAINING (V1 launch path)

| Sub-pass | Description | Effort | Notes |
|---|---|---|---|
| **OI-29** | Reclassify `sa2_median_household_income` to Lite weight per DEC-75 | ~0.1 session | Renderer-only; set `row_weight: "lite"` in `LAYER3_METRIC_META`. Trivial. |
| **4.2-A.3c** | Subtype-aware new-centre overlay on `sa2_supply_ratio` trajectory | ~1.0 session | Requires `build_sa2_history.py` rebuild with subtype tagging on `centre_events`; reuses dashboard.html plugin pattern (`makeFullPlugin` / `makeCompactPlugin`); per locked D6=c only `sa2_supply_ratio` gets a trajectory chart, the other 3 banded ratios stay histogram-only by intent. Closes OI-27. |
| **OI-12** | Backup pruning interactive script | ~0.1 session | Standalone; `data/` >5.8 GB. Status-critical. |
| **STD-13** | Cross-platform fix: WMIC → Get-CimInstance Win32_Process rewrite | ~0.1 session | All current sessions hit the WMIC-unavailable path with warning. |

**V1 ships at HEAD = OI-29 done + 4.2-A.3c done.** OI-12 and STD-13 are housekeeping; can interleave anywhere.

---

## 2. Deferred (V1.5)

### Layer 4.4 — V1.5 ingests (~2.0 sessions)

Bundled per OI-19 + SALM-extension:
- **NES** (non-English-speaking-background share) — closes the calibration function's documented `nes_share_pct` gap. Currently dormant in V1; the calibration's NES nudge branch never fires. Source: Census 2021 TSP T13 or equivalent.
- **Parent-cohort 25-44 population at SA2** — improves `calibrated_rate` accuracy for the relevant age band.
- **Schools at SA2** — feeds the kinder-eligibility path and OSHC sub-types.
- **SALM-extension** — re-run SALM ingest pulling participation_rate, Layer 3 banding, switch row_weight LITE→FULL on `sa2_lfp_persons`, switch trajectory source to SALM (Census 3-point → SALM monthly/quarterly). Promotes LFP triplet from sparse to dense.
- **SEEK + advertised-wage** (residual from 4.3.3 NCVER probe disposition) — workforce supply enrichment.

### Future centre-page tabs

- **OI-21** — Quality elements tab (deeper NQS / regulatory detail per centre)
- **OI-22** — Ownership and corporate detail tab (parent group navigation)

### Industry view enhancements

- **NCVER pipeline visualisation** — training_completions data ready (768 rows); multi-year sector pipeline rendering with DEC-24 transition trough labelled. Lives in industry view per DEC-36.

---

## 3. Layer 4.3 design decisions — closure status

All Layer 4.3 design decisions resolved by 2026-04-29 closure session and shipped through 4.3.x sub-passes by 2026-04-30:

- DEC-74 (perspective toggle on reversible ratio pairs) — LIVE in V1
- DEC-75 (visual weight by data depth) — LIVE; OI-29 will extend coverage to `sa2_median_household_income`
- DEC-76 (Workforce supply context block) — LIVE
- STD-34 (calibration discipline) — LIVE; surfaced in DER tooltip via Layer 4.2-A.4
- OI-18 (Layer 4.3 design closure) — CLOSED 2026-04-29c

**DEC-77 candidate** — Industry-absolute threshold framework. Sources locked (PC + RSI + CHC); table operator-approved as drafted. Lock in next session if happy with operator-use experience after V1 launch.

---

## 4. Parallel work streams

### Daily-rate centre-page integration

STD-36+ holds for daily-rate work. No progress this session. Integration into centre page deferred until daily-rate metric set is stable.

### Industry view

`training_completions` data is ready to consume (768 rows). Editorial disposition kept at Industry view per DEC-36.

### Operator page (parent operator detail)

Operator-page kinder treatment was mirrored into centre page during 4.3.6 bundled round. No further operator-page work pending in V1 scope.

---

## 5. Housekeeping items

- **OI-12 backup pruning** — STATUS-CRITICAL; cumulative `data/` backups >5.8 GB.
- **OI-13 frontend backups** in `docs/` — gitignored intent, but the `*.v?_backup_*` pattern uses single `?` so `v3_3` doesn't match. 7 backup files currently untracked. 30-second gitignore tightening fix.
- **OI-14 backfill audit for DD/MM/YYYY date parsing** — multiple recent occurrences; recommend codebase scan.
- **STD-13 cross-platform** — WMIC path falls through with warning every invocation.
- **OI-28 cosmetic** — populator banner mismatch.
- **`recon/probes/` and `recon/layer4_3_sub_pass_4_3_6_probe.md`** — untracked recon artefacts that may be real work worth tracking. End-of-session sweep candidate.
- **"Remara" pre-anonymization hangover in `centre_page.py` v10 changelog block** — internal code comment, not user-visible. Worth a 30-second cleanup at next consolidation.

---

## 6. Doc set housekeeping

The 2026-04-28 restructure produced the 12-doc set. Post-restructure update history:
- 2026-04-29c+d: Layer 4.3 design closure + 8 of 9 sub-passes shipped
- 2026-04-30: Layer 4.3 closeout + Layer 2.5 ship + Layer 4.2-A.3 + 4.2-A.3a-fix + 4.2-A.3b. Doc artefacts produced but not landed until next session.
- **2026-05-03: doc-discipline catch-up (30/04 set landed) + Layer 4.2-A.4 + OI-25 dissolution + OI-29 add.** This session regenerated PROJECT_STATUS, ROADMAP. OPEN_ITEMS already updated via in-place patcher (OI-25 closed, OI-29 added). PHASE_LOG appended.

This session's monolith: `kintell_project_status_2026-05-03.txt` per STD-35.

---

## 7. Sequencing rule of thumb

- **Renderer-best-practice ahead of plumbing** (locked 2026-04-29 from sub-pass re-sequencing).
- **Probe before code** per DEC-65. Demonstrated this session: OI-25 probe dissolved a wrongly-framed bug claim, saving ~0.3 session of misdirected backend work.
- **STD-30 pre-mutation discipline** for any DB write.
- **STD-35** — every session that materially changes Tier-2 state ships an end-of-session monolith AND lands the regenerated docs on disk AND uploads the monolith to project knowledge. (Reinforcement: the 30/04→03/05 gap demonstrated steps 2 and 3 are not optional.)
- **Two-commit DEC-22 pattern** for "supply data, then UI" — can collapse to single commit when both files are verified together (as Layer 4.2-A.4 did this session).
- Visual feedback loops on the centre page have been tight; expect 2-3 iterations on UX rounds and bank each one before the next.

---

## 8. What the next session should pick up

In recommended order:
1. **OI-29** — reclassify `sa2_median_household_income` to Lite. ~0.1 session. Trivial; can be run interleaved.
2. **4.2-A.3c** — subtype-aware new-centre overlay on supply_ratio. ~1.0 session. Largest visible UX upgrade remaining. Closes OI-27.
3. **OI-12** — backup pruning. ~0.1 session. Status-critical for git operation reliability.
4. **STD-13** — WMIC rewrite. ~0.1 session. Tidies a recurring noise warning.

After all four land, V1 is at HEAD-ready. V1.5 path (Layer 4.4 ingests bundle, ~2.0 sessions) is the next major scope.

If pivoting elsewhere (parallel streams, V1.5 prep): consult this ROADMAP and PROJECT_STATUS for full context.
