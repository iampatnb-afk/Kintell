# Roadmap

*Last updated: 2026-04-30. The on-disk version supersedes the project-knowledge monolith if they disagree.*

---

## 1. V1 launch scope

V1 path remaining: **~3.5 sessions** if Layer 4.2-A.3c + Layer 4.4 V1.5 ingests land. V1 ships without 4.2-A.3c if needed.

### COMPLETE (as of 2026-04-30)

- Layer 0–4.1 (operator + service slice + SA2 cohort + Layer 3 banding existing 14 metrics + render-side)
- **Layer 2.5** — Catchment cache populator (sub-passes 2.5.1 + 2.5.2 shipped 2026-04-30)
  - `service_catchment_cache` populated with 18,203 rows
  - 4 new catchment metrics banded into `layer3_sa2_metric_banding` (9,035 rows)
- **Layer 4.3** — All 9 sub-passes shipped
  - 4.3.1 Thread A unemployment range buttons (2026-04-29 morning)
  - 4.3.6 row-weight reclassification (2026-04-29c)
  - 4.3.8 intent copy + trend % (2026-04-29c)
  - 4.3.9 Workforce supply context block (2026-04-29c)
  - 4.3.7 perspective toggle infrastructure (2026-04-29c)
  - 4.3.2 / 4.3.3 probe dispositions resolved (2026-04-29d)
  - 4.3.4 calibration function (2026-04-29d)
  - 4.3.5 + 4.3.5b schema migration + column rename (2026-04-30)
- **Layer 4.2-A.3** — Catchment ratios wired into centre page (2026-04-30)
  - 5 catchment metrics rendered as new "Catchment position" card
  - Page reorder per option α: credit block top, operational below
  - DEC-74 perspective toggle live (2 reversible pairs activated)
- **Layer 4.2-A.3a-fix** — Trajectory chart polish (2026-04-30)
  - 4 chained centre.html iterations (v3.10 → v3.13a)
  - Sparkline dot points, vertical crosshair, external HTML readout
  - Workforce sparklines extended same treatment (v3.15)
  - Workforce-section local trend-window selector (v3.16)
- **Layer 4.2-A.3b** — Industry-absolute thresholds (2026-04-30)
  - Threshold table grounded in PC + RSI + CHC sources
  - 3 catchment metrics opt in via `industry_thresholds=True`
  - INDUSTRY band line renders below decile chips
- **Layer 4.2-A.3a-fix iter 4** — JSA IVI explainer (2026-04-30)
  - Permanent visible "About this measure" panel on IVI rows

### REMAINING (V1 launch path)

| Sub-pass | Description | Effort | Notes |
|---|---|---|---|
| **commit** | Composite commit for the uncommitted 4.2-A.3b + 4.2-A.3a-fix iter 3+4 work | ~1 min | centre_page.py v9→v12 + centre.html v3.13a→v3.17 |
| **OI-25 fix** | `_layer3_position` trajectory builder single-point bug on Census-source income metrics | ~0.3 session | Backend; affects 3 metrics (median_employee/household/total income) |
| **4.2-A.3c** | Subtype-aware new-centre overlay on supply_ratio trajectory | ~1.0 session | Requires sa2_history.json rebuild with subtype tagging on centre_events; reuses dashboard.html plugin pattern; promotes 4 banded catchment metrics LITE→FULL so histograms render |
| **4.2-A.4** | DER tooltip surface for `rule_text` per STD-34 | ~0.2 session | Renderer-only; data ready in cache |
| **OI-12** | Backup pruning interactive script | ~0.1 session | Standalone; `data/` >5.8 GB |
| **STD-13 cross-platform fix** | WMIC → Get-CimInstance Win32_Process rewrite | ~0.1 session | All current sessions hit the WMIC-unavailable path |

**V1 ships at HEAD** = 4.2-A.4 done + OI-25 fixed. 4.2-A.3c is enrichment but visually impactful; recommend including if bandwidth allows.

---

## 2. Deferred (P2 / V1.5)

### Layer 4.4 — V1.5 ingests (~2.0 sessions)

Bundled per OI-19 + SALM-extension:
- **NES** (non-English-speaking-background share) — closes the calibration function's documented `nes_share_pct` gap. Currently dormant in V1.
- **Parent-cohort 25-44 population at SA2** — improves calibrated_rate accuracy for the relevant age band.
- **Schools at SA2** — feeds the kinder-eligibility path and OSHC sub-types.
- **SALM-extension** — re-run SALM ingest pulling participation_rate, Layer 3 banding, switch row_weight LITE→FULL on `sa2_lfp_persons`, switch trajectory source to SALM (Census 3-point → SALM monthly/quarterly).
- **SEEK + advertised-wage** (residual from 4.3.3 NCVER probe disposition) — workforce supply enrichment.

### Future centre-page tabs

- **OI-21** — Quality elements tab (deeper NQS / regulatory detail per centre)
- **OI-22** — Ownership and corporate detail tab (parent group navigation)

### Industry view enhancements

- **NCVER pipeline visualisation** — training_completions data ready; multi-year sector pipeline rendering with DEC-24 transition trough labelled. Lives in industry view per DEC-36.

---

## 3. Layer 4.3 design decisions — closure status

All Layer 4.3 design decisions resolved by 2026-04-29 closure session and shipped through 4.3.x sub-passes by 2026-04-30:

- DEC-74 (perspective toggle on reversible ratio pairs) — LIVE in V1
- DEC-75 (visual weight by data depth) — LIVE
- DEC-76 (Workforce supply context block) — LIVE
- STD-34 (calibration discipline) — LIVE
- OI-18 (Layer 4.3 design closure) — CLOSED 2026-04-29c

**DEC-77 candidate** — Industry-absolute threshold framework. Sources locked (PC + RSI + CHC); table operator-approved as drafted. Lock in next session if happy with operator-use experience after V1.

---

## 4. Parallel work streams

### Daily-rate centre-page integration

STD-36+ holds for daily-rate work. No progress this session. Integration into centre page deferred until daily-rate metric set is stable.

### Industry view

`training_completions` data is ready to consume (768 rows; CHC30113/30121/50113/50121 across 2019-2024). Editorial disposition kept at Industry view per DEC-36.

### Operator page (parent operator detail)

Operator-page kinder treatment was mirrored into centre page during 4.3.6 bundled round. No further operator-page work pending in V1 scope.

---

## 5. Housekeeping items

- **OI-12 backup pruning** — STATUS-CRITICAL; 6 new backups today; total >5.8 GB.
- **OI-13 frontend backups** in `docs/` — gitignored; non-blocking.
- **OI-14 backfill audit for DD/MM/YYYY date parsing** — third occurrence today; recommend codebase scan.
- **STD-13 cross-platform** — WMIC path falls through with warning every invocation.
- **OI-28 cosmetic** — populator banner mismatch.

---

## 6. Doc set housekeeping

The 2026-04-28 restructure produced the 12-doc set. Post-restructure update history:
- 2026-04-29c+d: Layer 4.3 design closure + 8 of 9 sub-passes shipped
- **2026-04-30: Layer 4.3 closeout (4.3.5 + 4.3.5b) + Layer 2.5 ship + Layer 4.2-A.3 + 4.2-A.3a-fix + 4.2-A.3b**

This session regenerated PROJECT_STATUS, ROADMAP, OPEN_ITEMS. STANDARDS and DECISIONS unchanged (no new STDs/DECs; DEC-77 flagged for next-session lock).

End-of-session monolith: `kintell_project_status_2026-04-30.txt` per STD-35.

---

## 7. Sequencing rule of thumb

Renderer-best-practice ahead of plumbing (locked 2026-04-29 from sub-pass re-sequencing). Probe before code per DEC-65. STD-30 pre-mutation discipline for any DB write. Visual feedback loops on the centre page have been tight this run; expect 2–3 iterations on UX rounds and bank each one before the next.

---

## 8. What the next session should pick up

In recommended order:
1. **Commit** the uncommitted v9→v12 + v3.13a→v3.17 work (~1 min).
2. **OI-25** — Census income trajectory single-point bug. Backend, well-bounded, broad impact.
3. **4.2-A.3c** — Subtype-aware new-centre overlay. Largest visual upgrade remaining.
4. **4.2-A.4** — DER rule_text tooltip surface.

If pivoting elsewhere (parallel streams, V1.5 prep, housekeeping): consult this ROADMAP and PROJECT_STATUS for full context.
