# Roadmap

*Last updated: 2026-05-04 (end of full-day session). The on-disk version supersedes the project-knowledge monolith if they disagree.*

---

## 1. V1 launch scope

**V1 is at HEAD `bcdf84c`** (V1 ship). Subsequent commits are V1.5 polish + scoping (current HEAD `3ddcf18` after 7 commits today).

### COMPLETE (V1 ship 2026-05-03 evening)

- Layer 0–4.1 foundations
- **Layer 2.5** — Catchment cache populator (2026-04-30)
- **Layer 4.3** — All 9 sub-passes (2026-04-29 → 2026-04-30)
- **Layer 4.2-A.3** — Catchment ratios wired into centre page
- **Layer 4.2-A.3a-fix** — Trajectory chart polish
- **Layer 4.2-A.3b** — Industry-absolute thresholds
- **Layer 4.2-A.4** — STD-34 calibration metadata in DER tooltip
- **Layer 4.2-A.3c** — Catchment trajectories + new-centre overlay (2026-05-03 PM)
- **OI-32 close** + **DEC-77 mint** + **OI-30 close** by probe (2026-05-03 evening)

### SHIPPED POST-V1 (2026-05-04, 7 commits)

- **`f92b517`** — `CENTRE_PAGE_V1.5_ROADMAP.md` created (V1.5 centre-page scoping doc).
- **`f47a0ba`** — C3: absolute-change ("+N places · +M centres") alongside trend % on catchment trajectory charts. centre.html v3.24 → v3.25.
- **`fdc85bd`** — A2 NES share ingest v2 (fraction storage; 7,272 rows; national 22.28%).
- **`bb21f66`** — A2 wire: populator reads NES, calibration nudge live (Bayswater 0.50 → 0.48; Bentley 0.48 → 0.46).
- **`49ce9f1`** — A2 v3 unit fix: storage convention switched to percentage per `census_*_pct` family; wire divides by 100 before calibration.
- **`d02e26e`** — B2: NES added to `layer3_apply.py METRICS`; banded into `layer3_sa2_metric_banding` (2,417 rows).
- **`3ddcf18`** — C2-NES (data-side): NES registered in centre_page.py three Layer 3 registries. Render-side deferred (OI-36).

**Plus dropped:** A1 (ABS ERP backward extension) — dissolved by probe trail; ABS source publishes `'-'` for pre-2019 SA2 under-5.

### REMAINING (V1 launch path)

Nothing. V1 is at HEAD-ready since 2026-05-03 evening; subsequent commits are V1.5 progress.

---

## 2. Priority polish (when ready)

| Item | Effort | Notes |
|---|---|---|
| **OI-36** | ~0.3 sess | C2-NES render-side. centre.html hardcodes catchment rows; NES row needs explicit addition. **Recommended first piece next session — closes visible-on-page gap from this session.** |
| **OI-31** | ~1.0 sess | Click-on-event-overlay detail. Substantial standalone renderer feature. |
| **OI-26** | ~0.2 sess | demand_supply industry threshold post-launch review. Trigger criterion in `CENTRE_PAGE_V1.5_ROADMAP.md` §"Open questions". |

---

## 3. V1.5 path (~2.6 sessions remaining)

**Centre-page V1.5 work tracked in `CENTRE_PAGE_V1.5_ROADMAP.md` (source of truth).** End-of-day status:

- **Phase A (ingest)** — A1 dissolved, A2 closed end-to-end. A3 (parent-cohort 25-44) + A4 (schools) + A5 (subtype-correct denominators) + A6 (SALM-extension) remaining ~1.4 sess.
- **Phase B (banding)** — B2 (NES) closed. B1 (LFP triplet promote) + B3 (parent-cohort) + B4 (schools) + B5 (OSHC re-band) remaining ~0.9 sess.
- **Phase C (render)** — C3 done. C2-NES data-side done; render-side **OI-36** ~0.3 sess. C2 for other metrics + C6 (growth) ~0.2 sess.

**Phase 2 (NES work continuation):** banked from today's scoping — T08 country-of-birth narrative summary at top of new "Demographic Mix" panel within Catchment card. Estimated ~0.5 sess once NES row is rendering. Out of V1.5 critical path; opportunistic.

**Recommended ship slice remaining: ~2.6 sess** to close the main V1.5 set.

### Operator-page V1.5 (separate program)

Out of scope for `CENTRE_PAGE_V1.5_ROADMAP.md`. Needs its own scoping pass when prioritised.

### Industry view enhancements

- **NCVER pipeline visualisation** — `training_completions` data ready (768 rows). Lives in industry view per DEC-36.

---

## 4. Layer 4.3 design decisions — closure status

All Layer 4.3 design decisions resolved by 2026-04-29 closure session and shipped through 4.3.x sub-passes by 2026-04-30:

- DEC-74 (perspective toggle) — **AMENDED 2026-05-03**: removed for catchment metrics; inverse views now visible as separate rows
- DEC-75 (visual weight by data depth) — LIVE
- DEC-76 (Workforce supply context block) — LIVE
- STD-34 (calibration discipline) — LIVE; surfaced in DER tooltip via Layer 4.2-A.4
- DEC-77 (industry-absolute threshold framework) — LIVE; locked 2026-05-03 evening

**DEC-78 candidate (2026-05-04):** NES storage convention at SA2 = percentage (0–100) per `census_*_pct` family; wire boundary handles fraction conversion for `calibrate_participation_rate()`. **Not yet promoted** — wait for A3/A4/A5 convention check.

---

## 5. Parallel work streams

### Daily-rate centre-page integration

STD-36+ holds for daily-rate work. No progress this session. Centre-page integration tracked in `CENTRE_PAGE_V1.5_ROADMAP.md` as A8 / B7 / C7 (gated on parallel-stream stability).

### Industry view

`training_completions` data ready (768 rows). Editorial disposition kept at Industry view per DEC-36.

### Operator page

V1.5 operator-page work needs its own scoping pass. Not started.

---

## 6. Housekeeping items

- **OI-12 backup pruning** — STATUS-CRITICAL. Cumulative `data/` backups now ~8.5 GB after today's 5 new backups (~2.7 GB added). Keep policy needs relaxation.
- **OI-35** — `layer3_apply.py` real fix (wholesale-rebuild → per-metric DELETE). Workaround in place. ~0.5 sess.
- **OI-13** — Frontend file backups gitignore tightening (~30 sec).
- **OI-14 backfill audit for DD/MM/YYYY date parsing** — multiple recent occurrences; codebase scan candidate.
- **OI-28 cosmetic** — populator banner mismatch.
- **STANDARDS.md addition candidate** — "search project knowledge before probing" (banked from today's A1 lesson). Worth a 30-second STD-37 mint at next consolidation.
- **`recon/probes/` sweep** — multiple session probes (root + recon/probes/) worth consolidating. Candidate for next housekeeping pass.
- **`recon/a1_dissolution_audit.md`** — consolidation candidate. The 4 A1 probe scripts form the audit trail; a markdown summary would replace them as the durable artefact.

---

## 7. Doc set housekeeping

The 2026-04-28 restructure produced the 12-doc set. Update history:

- 2026-04-29c+d → 2026-04-30 → 2026-05-03 (V1 ship + doc-discipline catch-up).
- **2026-05-04 (full day)**: V1.5 scoping pass (`CENTRE_PAGE_V1.5_ROADMAP.md`) + C3 + A1 dissolution + A2 (v2→v3 with unit fix) + A2-wire + B2 + C2-NES (data side) + OI-35/OI-36 minted + recovery from layer3_apply wipe.

---

## 8. Sequencing rule of thumb

- **Search project knowledge before probing.** Lesson banked 2026-05-04 (A1 finding was foreshadowed in 2026-04-28b status). Add to STANDARDS as STD-37 candidate at next housekeeping pass.
- **Renderer-best-practice ahead of plumbing** (locked 2026-04-29).
- **Probe before code** per DEC-65. Demonstrated repeatedly: OI-25 dissolved, A1 dissolved, NES wire correctly scoped before code.
- **Unit conventions explicit at scoping time** — banked 2026-05-04 (A2 v2/v3 epilogue). For any cross-layer value, the unit at each layer (storage / wire / calibration / render) should be explicit before code.
- **STD-30 pre-mutation discipline** for any DB write.
- **STD-35** — every session that materially changes Tier-2 state ships an end-of-session monolith AND lands the regenerated docs on disk AND uploads the monolith to project knowledge.
- **STD-36** — session-start uploads of the Tier-2 docs + relevant code files.
- **Two-commit DEC-22 pattern** for "supply data, then UI" — collapsable to single commit when verified together.
- **Patcher-pattern STD-10 + STD-13** — mature; many shipped today (centre.html v3.25 patcher, A2 wire patcher, A2 wire-v2 unit fix patcher, B2 layer3 patcher, C2-NES patcher).
- **Bundling discipline:** read-only probes bundled freely; same-file edits in one logical concern bundled; DB writes never bundled (each gets its own backup + audit_log row); cross-concern changes split; doc updates bundled at end-of-session per STD-35.

---

## 9. What the next session should pick up

**No mandatory work.**

V1.5 first piece (recommended): **OI-36 — C2-NES render-side**. Probe centre.html catchment-row assembly; surgical patch to add NES row; restart server; verify visible. Closes the visible-on-page gap from this session. ~0.3 sess.

Then evaluate appetite:
- **Phase 2 of NES work** — T08 country-of-birth narrative panel (~0.5 sess). Depends on NES row rendering first.
- **Continue Phase A ingest** — A3 parent-cohort 25-44 (~0.3 sess), A4 schools (~0.4 sess), A5 subtype-correct denominators (~0.3 sess), A6 SALM-extension (~0.4 sess).

Either path valid. Phase 2 narrative gives a fast visible win after OI-36. Continuing Phase A keeps building the calibration-input set.

If pivoting elsewhere (parallel streams, industry view): consult this ROADMAP, `CENTRE_PAGE_V1.5_ROADMAP.md`, and `PROJECT_STATUS.md` for full context.
