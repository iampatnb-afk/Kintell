# Roadmap

*Last updated: 2026-05-09 (commercial repositioning per DEC-79; V1 horizon redefined to ~Sept 2026 with five new streams). The on-disk version supersedes the project-knowledge monolith if they disagree.*

**Note 2026-05-09:** Up to and including 2026-05-05, "V1" referred to the original centre-page credit-decision tool (shipped at HEAD `bcdf84c` on 2026-05-03). With DEC-79 the product has been repositioned as Novara Intelligence — Patrick Bell's commercial product. V1 is now redefined to the broader institutional decision-support release targeting ~Sept 2026. The earlier-V1 milestone is preserved as **"V1.0 (centre-page credit tool)"** for traceability. New V1 = "V1.0-shipped + V1.5 ingests + Catchment page + Group page + 5 new streams + Excel export + brand identity rename".

**See `PRODUCT_VISION.md` for strategic frame and the five new streams in detail.**

---

## 1. Original V1 (centre-page credit tool) — COMPLETE

**Shipped at HEAD `bcdf84c`, 2026-05-03 evening.** All blocking V1.0 items shipped.

### COMPLETE through 2026-05-05

- Layer 0–4.1 foundations
- **Layer 2.5** — Catchment cache populator (2026-04-30)
- **Layer 4.3** — All 9 sub-passes (2026-04-29 → 2026-04-30)
- **Layer 4.2** — Centre page renderer (V1.0)
- **Layer 4.4** — A2 NES end-to-end (2026-05-04)
- **OI-34 close** — C3 absolute-change rendering (2026-05-04, commit `f47a0ba`)
- **V1.5 scoping doc** — `CENTRE_PAGE_V1_5_ROADMAP.md` (2026-05-04, commit `f92b517`)
- **A1 dissolution** — ABS source publishes `'-'` for pre-2019 SA2 under-5 (2026-05-04)
- **A2 end-to-end** — NES share ingest + unit fix + populator wire (2026-05-04, commits `fdc85bd` + `49ce9f1` + `bb21f66`)
- **B2** — `sa2_nes_share` banded into `layer3_sa2_metric_banding` (2026-05-04, commit `d02e26e`; 2,417 rows)
- **C2-NES (data side)** — `sa2_nes_share` registered in `LAYER3_METRIC_META` + INTENT_COPY + TRAJECTORY_SOURCE (2026-05-04, commit `3ddcf18`)
- **OI-36 close** — `sa2_nes_share` renders in Catchment Position card + delta badge on Lite rows (2026-05-05, commit `430009a`)
- **STD-35 hygiene catch-up** — Tier-2 docs regenerated (2026-05-05, commit `9d49be9`)

---

## 2. V1 (Novara Intelligence — broader release, target ~Sept 2026)

**Per DEC-79.** V1 ship target: 3–4 months from 2026-05-09 (i.e. ~Sept 2026). Comprises:

### 2.1 V1.5 ingests (centre-page completion) — ~2.7 sessions
*Canonical: `CENTRE_PAGE_V1_5_ROADMAP.md`*

| Phase | Items | Effort |
|---|---|---|
| **A10 + C8 (next-session priority)** | Demographic Mix bundle (T07 ATSI + T08 country of birth + T19 single-parent households + Community Profile panel) | **~1.0 sess** |
| Phase A core remaining | A3 + A4 + A5 + A6 | ~1.4 sess |
| Phase B core | B1 + B3 + B4 + B5 | ~0.9 sess |
| Phase C core remaining | C2-other + C6 | ~0.4 sess |

### 2.2 Stream extensions (per DEC-79 / PRODUCT_VISION.md) — V1 scope

| Stream | Description | Effort estimate | Sequencing |
|---|---|---|---|
| **Stream A** | Educator visa / overseas educator supply (Workforce extension) | ~2-3 sess (planning + ingest + render) | After V1.5 ingests; recon required |
| **Stream B** | NFP perspectives integrated (existing surfaces) | ~1-2 sess | After Stream C demographic completion; recon required |
| **Stream C** | Childbearing-age + marital-status depth | ~1-2 sess | Extends A3 + T19; concurrent with A10/C8 ingests |
| **Stream D** | PropCo Property Intelligence (manual evidence pathway) | ~4-6 sess (schema + import + render + Excel hooks) | Standalone track; recon → schema design → manual import → centre/operator render |
| **Stream E** | SA2 Border Exposure V1 proxy | ~1-1.5 sess | Standalone; can run concurrent with V1.5 |

**Effort total for Streams A-E: ~9-14 sessions.**

### 2.3 New surfaces — V1 scope

- **Catchment page** — cascades from centre page; reuse Position card patterns; absorbs Stream B/C/E signals. ~3-4 sess.
- **Group page** — sits above catchment; portfolio-level operator + PropCo lenses. Picks up Stream A workforce dependency at portfolio level. ~3-4 sess.

### 2.4 Cross-cutting V1 deliverables

- **Excel export framework** — repeatable workbook structures, audit-friendly, transaction-ready. ~2-3 sess. DEC-candidate when scoped.
- **Brand identity rename pass (OI-NEW-6)** — Novara Intelligence visible in README, doc headers, code comments, page titles. Filesystem unchanged. ~0.5 sess.
- **Institutional readiness foundations** — methodology documentation, customer-readable GLOSSARY/DATA_INVENTORY, privacy governance baseline, multi-tenancy architecture (design only — deployment in V2). ~1-2 sess.

### 2.5 V1 effort summary

| Track | Effort |
|---|---|
| V1.5 ingests | ~2.7 sess |
| Streams A-E | ~9-14 sess |
| Catchment page | ~3-4 sess |
| Group page | ~3-4 sess |
| Excel export framework | ~2-3 sess |
| Brand identity rename | ~0.5 sess |
| Institutional readiness | ~1-2 sess |
| **V1 TOTAL** | **~22-33 sess** |

3-4 months @ 5-8 sessions/week is achievable but tight. Sequencing matters.

### 2.6 Suggested V1 sequencing

**Block 1 — V1.5 ingests + early infra (4–6 weeks):**
- A10 + C8 Demographic Mix bundle
- Stream C marital/fertility additions (extends A3 + T19; minimal extra ingest)
- A3 / A4 / A5 / A6 V1.5 remainder
- B-pass banding for new metrics
- C2-other / C6 render
- **Stream E SA2 Border Exposure** (standalone, minimal dependency, good early ship)
- **Brand identity rename pass** (low-risk, builds momentum)

**Block 2 — PropCo + Workforce (4–6 weeks):**
- **Stream D PropCo** schema + manual import + centre/operator render
- **Stream A Educator visa / overseas supply** recon → ingest → render
- **Stream B NFP overlays** — derived signals on existing pages (after Stream C metrics land)

**Block 3 — New surfaces + export + readiness (3–4 weeks):**
- Catchment page
- Group page
- Excel export framework
- Institutional readiness foundations

This sequencing is provisional; first sub-block decisions get locked in their own DECs as we approach them.

---

## 3. V2 (fast-follow, post-V1)

- True centre-level catchment model (supersedes Stream E V1 proxy)
- DA / pipeline tracking
- Operator change tracking + quality timeline history (OI-21 evolved)
- Acquisition quality analysis
- Property transaction intelligence (Stream D extensions — automated inference engine, on-market alerting)
- Workforce dependency modelling deeper
- Competition overlays (per-centre competitive gravity)
- Valuation overlays
- Map UI as supporting context (DEC-71 honoured)
- Multi-tenancy / hosted infrastructure deployment
- ISO 27001 / SOC 2 formal readiness pass

---

## 4. V3 (12+ months horizon)

- On-market childcare assets monitoring (live feeds)
- Selective paid title-search integration (premium)
- CoreLogic / Cotality integration
- Multi-industry positioning expansion (Novara Intelligence as broader analytics platform)

---

## 5. Cross-cutting risks (tracked)

| Risk | Sequencing implication |
|---|---|
| 2026 Census Aug 2026 (data release Jun 2027) | SA2 refresh project Q3 2027 (OI-NEW-3) |
| Workforce funding cliff Nov 2026 | Pricing scenario pass before Nov 2026 (OI-NEW-2) |
| Strengthening Regulation Bill 2025 — CCS revocation live | NQS trajectory as leading credit indicator (already on centre page) |
| ABS Community Profiles retirement | Layer 2 dependency audit (OI-NEW-4) |
| SEEK/Indeed anti-scraping | Audit module5/6 dependencies (OI-NEW-5) |
| Starting Blocks Algolia drift | Smoke test before next production run (OI-NEW-4) |
| "70% break-even" mis-cited to PC | Provenance correction in DEC-77 (OI-NEW-1) |

---

## 6. Layer 4.3 design decisions — closure status

All Layer 4.3 design decisions resolved by 2026-04-29 closure session and shipped through 4.3.x sub-passes by 2026-04-30:

- DEC-74 (perspective toggle) — AMENDED 2026-05-03
- DEC-75 (visual weight by depth) — LIVE; extended 2026-05-05 with delta badge
- DEC-76 (Workforce supply context block) — LIVE
- STD-34 (calibration discipline) — LIVE; NES nudge live since 2026-05-04
- DEC-77 (Industry-absolute thresholds) — LOCKED 2026-05-03

---

## 7. Parallel work streams

### Daily-rate centre-page integration

STD-36+ holds for daily-rate work. Integration deferred until daily-rate metric set is stable. A8 / B7 / C7 in CENTRE_PAGE_V1_5_ROADMAP track this dependency.

### Industry view

`training_completions` data is ready. Editorial disposition kept at Industry view per DEC-36.

### Operator page

Operator-page work explicitly out of CENTRE_PAGE_V1_5_ROADMAP scope. Stream D PropCo introduces new operator-page surfaces (linked properties, landlord concentration, etc.) — those land via Stream D, not via standalone operator-page work.

---

## 8. Housekeeping items (always-open)

- **OI-12** — DB backup pruning. **CRITICAL** at ~8.5 GB cumulative. ~0.2 sess to relax-and-apply.
- **OI-35** — `layer3_apply.py` wholesale-rebuild bug. Workaround in place; real fix ~0.5 sess.
- **OI-13** — Frontend file backups gitignore tightening. **30-second fix** — addressed in 2026-05-09 housekeeping pass below.
- **OI-NEW-9** — `recon/patchers_*/` directories evade `patch_*.py` ignore rule. Add to .gitignore.
- **OI-14** — DD/MM/YYYY date parsing audit.
- **OI-15** — ARIA+ format mismatch audit.
- **OI-10** — `provider_management_type` enum normalisation.
- **OI-28** — `populate_service_catchment_cache.py` cosmetic banner mismatch (5 sec).
- **OI-NEW-6** — Brand identity rename pass (Novara Intelligence visible everywhere).
- **OI-NEW-7** — Move Tier-1 docs from `recon/Document and Status DB/` to repo root.
- **OI-NEW-8** — Stale `CENTRE_PAGE_V1.5_ROADMAP.md` (dot version) — delete; underscore version is canonical.
- **STD-37 candidate** — "search project knowledge before probing" mint.
- **Recon probe sweep** — root probes → `recon/probes/`.

---

## 9. Doc set housekeeping

The 2026-04-28 restructure produced the 12-doc set. As of 2026-05-09:

- **Tier-1 docs** still at `recon/Document and Status DB/` — to move to repo root (OI-NEW-7)
- **DECISIONS.md and STANDARDS.md** missing from repo root (only canonical copies are in `recon/Document and Status DB/`) — to move (OI-NEW-7)
- **Tier-2 docs at repo root:** PROJECT_STATUS, ROADMAP, OPEN_ITEMS, PHASE_LOG, CENTRE_PAGE_V1_5_ROADMAP, plus new this session: **CLAUDE.md** + **PRODUCT_VISION.md**
- **`CENTRE_PAGE_V1.5_ROADMAP.md`** (dot version) — STALE, delete (OI-NEW-8)

---

## 10. Sequencing rules

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
11. **Surgical-vs-refactor decision is output of probe** (banked 2026-05-05)
12. **NEW: New stream → DEC + PRODUCT_VISION + ROADMAP update before code** (banked 2026-05-09 from this session's planning pass)
13. **NEW: Avoid Bash for path-bearing operations** when project path contains a space; use Read/Glob/Grep/Edit (banked 2026-05-09 from Windows-spaced-path productivity tax)

---

## 11. What the next session should pick up

**Recommended first piece: A10 + C8 (Demographic Mix bundle, ~1.0 sess).** Per CENTRE_PAGE_V1_5_ROADMAP §"Recommended next session start":

- **A10 ingest pass** — three TSP tables (T07 ATSI, T08 country of birth, T19 single-parent households) all from `2021_TSP_SA2_for_AUS_short-header.zip` already on disk. Same processing pattern. ~0.5 sess.
- **B-pass for the three new metrics** — register in `layer3_apply.py` METRICS, run banding. ~0.1 sess each.
- **C8 panel build** — new Community Profile panel on centre page. ~0.5 sess.
- **End-of-session doc refresh.**

**Pre-A10 housekeeping** (this session, 2026-05-09):
- ✅ DEC-79 commercial repositioning — landed
- ✅ CLAUDE.md — landed
- ✅ Memory entries — landed
- ✅ PRODUCT_VISION.md — landed
- ✅ ROADMAP.md (this doc) — being landed now
- ⏭ OPEN_ITEMS.md update with new OIs — next
- ⏭ PROJECT_STATUS.md reframing entry — next
- ⏭ CENTRE_PAGE_V1_5_ROADMAP.md cross-reference to new streams — next
- ⏭ .gitignore fix (OI-13 + OI-NEW-9) — next

**After A10/C8 lands, evaluate Block 1 sequencing per §2.6.**
