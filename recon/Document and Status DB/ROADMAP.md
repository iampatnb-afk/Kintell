# Roadmap

*Last updated: 2026-05-03 (end of afternoon session). The on-disk version supersedes the project-knowledge monolith if they disagree.*

---

## 1. V1 launch scope

**V1 is at HEAD `bcdf84c`.** All blocking V1 items shipped this session.

### COMPLETE (as of 2026-05-03 afternoon)

- Layer 0–4.1 foundations
- **Layer 2.5** — Catchment cache populator (2026-04-30)
- **Layer 4.3** — All 9 sub-passes (2026-04-29 → 2026-04-30)
- **Layer 4.2-A.3** — Catchment ratios wired into centre page (2026-04-30)
- **Layer 4.2-A.3a-fix** — Trajectory chart polish (2026-04-30)
- **Layer 4.2-A.3b** — Industry-absolute thresholds (2026-04-30)
- **Layer 4.2-A.4** — STD-34 calibration metadata in DER tooltip (2026-05-03 AM)
- **Layer 4.2-A.3c** — Catchment trajectories + new-centre overlay (2026-05-03 PM)
  - Part 1: design probes confirmed sa2_history.json was LDC-only; agreed on multi-subtype expansion
  - Part 2 (build): build_sa2_history.py v2 — LDC-first multi-subtype rebuild; sa2_history.json 5.2 MB → 13.2 MB
  - Part 3 (wiring): centre_page.py v14→v16 (4 metrics promoted Lite→Full; new sa2_history cache + _catchment_trajectory helper; DEC-74 toggle removed); centre.html v3.18→v3.21 (eventAnnotationPlugin; year-regex bug fixed in 2 places)
  - Verified on Sparrow Bayswater LDC (svc 2358) + Kool HQ Waverley OSHC (svc 103)
- **OI-29 close** — sa2_median_household_income reclassified to Lite per DEC-75 (2026-05-03 PM)
- **OI-12 inventory** — read-only audit_log + table snapshot of all 36 backups (2026-05-03 PM); deletion deferred but now safely reversible
- **STD-13 helper** — proc_helpers.py with Get-CimInstance Win32_Process pattern; Win11-safe replacement for deprecated WMIC; canonical pattern documented in STANDARDS.md (2026-05-03 PM)
- **Doc-discipline catch-up** — 2026-04-30 doc set landed (was overdue); both AM and PM regens this session

### REMAINING (V1 launch path)

Nothing blocking. V1 ships at `bcdf84c`.

---

## 2. Priority polish (when ready)

Not V1 blockers but worth doing soon:

| Item | Effort | Notes |
|---|---|---|
| **Bug 4 (explainer text)** | ~10-30 min | Larger explainer per metric, especially adjusted_demand. Renderer-only; needs Patrick's copy. Currently deferred ("Patrick will recall later"). |
| **OI-30 (Bayswater data sparsity)** | ~0.3 + ~0.5 session | Probe ABS pop_0_4 SA2 code coverage; Bayswater 211011251 only has data Q3 2019+. Likely an ASGS version mismatch. Build script needs concordance step. |

---

## 3. V1.5 path (~3 sessions)

### Layer 4.4 — V1.5 ingests (~2.0 sessions)

Bundled per OI-19 + SALM-extension:
- **NES** (non-English-speaking-background share) — closes the calibration function's documented `nes_share_pct` gap
- **Parent-cohort 25-44 population at SA2** — improves calibrated_rate accuracy
- **Schools at SA2** — feeds kinder-eligibility path and OSHC sub-types
- **SALM-extension** — pulls participation_rate; promotes LFP triplet from Lite to Full; Census 3-point → SALM monthly/quarterly
- **SEEK + advertised-wage** (residual from 4.3.3 NCVER probe) — workforce supply enrichment

### V1.5 polish on the catchment trajectory feature

- **OI-31 (click-on-event detail)** — interactive overlay showing centre names + place changes when clicking a vertical event line. Substantial renderer feature; ~1 session.
- **OI-32 (absolute change alongside %)** — show "+12 places, +1 centre" alongside trend %. ~30 min if scoped narrow.
- **Subtype-correct denominators** — OSHC supply_ratio currently uses pop_0_4 (under-5 children) as denominator. Subtype-correct would use school-aged pop. Requires ABS school-age population ingest at SA2. Bundle with Layer 4.4.

### Future centre-page tabs

- **OI-21** — Quality elements tab (deeper NQS / regulatory detail per centre)
- **OI-22** — Ownership and corporate detail tab (parent group navigation)

### Industry view enhancements

- **NCVER pipeline visualisation** — `training_completions` data ready (768 rows). Lives in industry view per DEC-36.

---

## 4. Layer 4.3 design decisions — closure status

All Layer 4.3 design decisions resolved by 2026-04-29 closure session and shipped through 4.3.x sub-passes by 2026-04-30:

- DEC-74 (perspective toggle on reversible ratio pairs) — **AMENDED 2026-05-03**: removed for catchment metrics post-Lite→Full promotion; inverse views now visible as separate rows
- DEC-75 (visual weight by data depth) — LIVE; OI-29 closed by extending coverage to sa2_median_household_income
- DEC-76 (Workforce supply context block) — LIVE
- STD-34 (calibration discipline) — LIVE; surfaced in DER tooltip via Layer 4.2-A.4
- OI-18 (Layer 4.3 design closure) — CLOSED 2026-04-29c

**DEC-77 candidate** — Industry-absolute threshold framework. Sources locked (PC + RSI + CHC); table operator-approved as drafted. Lock in next session if happy with operator-use experience after V1.

---

## 5. Parallel work streams

### Daily-rate centre-page integration

STD-36+ holds for daily-rate work. No progress this session. Integration into centre page deferred until daily-rate metric set is stable.

### Industry view

`training_completions` data is ready (768 rows). Editorial disposition kept at Industry view per DEC-36.

### Operator page

Operator-page kinder treatment was mirrored into centre page during 4.3.6 bundled round. No further operator-page work pending in V1 scope.

---

## 6. Housekeeping items

- **OI-12 backup pruning** — inventory landed; deletion safely reversible whenever disk pressure becomes real
- **OI-13 frontend backups** — gitignore pattern uses single `?` so `v3_3` doesn't match. 30-second fix.
- **OI-14 backfill audit for DD/MM/YYYY date parsing** — multiple recent occurrences; recommend codebase scan
- **STD-13 helper** — landed; new mutation scripts use proc_helpers.py
- **OI-28 cosmetic** — populator banner mismatch (no functional impact)
- **`recon/probes/` and `recon/layer4_3_sub_pass_4_3_6_probe.md`** — untracked recon artefacts; sweep candidate
- **"Remara" pre-anonymization hangover in `centre_page.py` v10 changelog block** — internal code comment, not user-visible. 30-second cleanup.
- **Untracked artefacts in working tree from this session** — patcher backups, smoke tests, probe scripts. Cleanup sweep candidate before next session.

---

## 7. Doc set housekeeping

The 2026-04-28 restructure produced the 12-doc set. Post-restructure update history:
- 2026-04-29c+d: Layer 4.3 design closure + 8 of 9 sub-passes shipped
- 2026-04-30: Layer 4.3 closeout + Layer 2.5 ship + Layer 4.2-A.3 / 3a-fix / 3b
- 2026-05-03 AM: doc-discipline catch-up (30/04 set landed) + Layer 4.2-A.4 + OI-25 dissolution + OI-29 add
- **2026-05-03 PM: OI-29 close + OI-12 inventory + STD-13 helper + Layer 4.2-A.3c (Part 1+2+3) + DEC-74 amendment**

Two monoliths produced today: `kintell_project_status_2026-05-03.txt` (AM, swapped at AM doc landing) and `kintell_project_status_2026-05-03_pm.txt` (this end-of-session refresh, supersedes AM monolith).

---

## 8. Sequencing rule of thumb

- **Renderer-best-practice ahead of plumbing** (locked 2026-04-29).
- **Probe before code** per DEC-65. Demonstrated repeatedly today: OI-25 dissolved by probe (saved 0.3 session); Layer 4.2-A.3c Part 1 probes inverted the prior framing (sa2_history.json was LDC-only, not all-subtype); Bayswater data sparsity correctly diagnosed before any "fix" attempt.
- **STD-30 pre-mutation discipline** for any DB write.
- **STD-35** — every session that materially changes Tier-2 state ships an end-of-session monolith AND lands the regenerated docs on disk AND uploads the monolith to project knowledge. (Reinforced this session by the 30/04→03/05 gap.)
- **Two-commit DEC-22 pattern** for "supply data, then UI" — can collapse to single commit when both files are verified together (Layer 4.2-A.3c Part 3 used this).
- **Patcher-pattern STD-10 + STD-13** mature pattern; 11-mutation patcher (v15) and 4-mutation patcher (v16) both shipped cleanly today.
- **Patcher anchors must use `\n` not `\r\n`** — Python text mode normalises on read. Worth a 1-line addition to STD-10 at next consolidation.

---

## 9. What the next session should pick up

**No mandatory work.** V1 is at HEAD; ship is ready. Suggested order if continuing:

1. **Bug 4 (explainer text)** — quick win once Patrick provides copy; ~30 min ship
2. **OI-30 probe** — investigate ABS ASGS coverage; understand the actual scope before any fix
3. **DEC-77 lock** — confirm industry threshold framework after operator validation
4. **V1.5 prep** — Layer 4.4 ingest planning

Optional housekeeping anytime: gitignore tightening (OI-13), untracked recon sweep, "Remara" hangover cleanup, OI-12 deletion.

If pivoting elsewhere (parallel streams, industry view, operator page enhancements): consult this ROADMAP and PROJECT_STATUS for full context.
