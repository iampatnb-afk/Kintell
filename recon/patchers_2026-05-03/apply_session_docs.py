"""
apply_session_docs.py — single-shot doc updater for 2026-05-03 evening session.

What this script does:
  - REPLACE recon/Document and Status DB/OPEN_ITEMS.md       (full)
  - REPLACE recon/Document and Status DB/PROJECT_STATUS.md   (full)
  - APPEND  recon/Document and Status DB/PHASE_LOG.md        (new session block)
  - APPEND  recon/Document and Status DB/DECISIONS.md        (DEC-77 entry)
  - APPEND  recon/Document and Status DB/ROADMAP.md          (small session update)

Discipline:
  - STD-08: timestamped backup of every file before modify
  - Idempotency: each append checks for a unique sentinel; aborts that
    append cleanly if already present (so re-running is safe)
  - Read-only existence check before any mutation
"""

import shutil
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent
DOCS = REPO / "recon" / "Document and Status DB"

OPEN_ITEMS    = DOCS / "OPEN_ITEMS.md"
PROJECT_STAT  = DOCS / "PROJECT_STATUS.md"
PHASE_LOG     = DOCS / "PHASE_LOG.md"
DECISIONS     = DOCS / "DECISIONS.md"
ROADMAP       = DOCS / "ROADMAP.md"

STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")


# Idempotency sentinels — unique strings checked against existing file
SENTINEL_PHASE_LOG = "## 2026-05-03 (evening) — OI-32 close + DEC-77 mint + OI-30 probe + OI-12 dry-run"
SENTINEL_DECISIONS = "## DEC-77 — Industry-absolute threshold framework for catchment ratios"
SENTINEL_ROADMAP   = "## Updates — 2026-05-03 evening session"


# ─────────────────────────────────────────────────────────────────────
# CONTENT — full files
# ─────────────────────────────────────────────────────────────────────

OPEN_ITEMS_CONTENT = '''# Open Items

*Last updated: 2026-05-03 (end of evening session). The on-disk version supersedes the project-knowledge monolith if they disagree.*

OI ID is global. Closed items kept for traceability. Severity tags: CRITICAL / Medium / Low / Cosmetic / Tracking.

---

## OPEN

### OI-33 — 25 SA2s with zero or sparse pop_0_4 coverage
*Origin: 2026-05-03 evening (split from OI-30 probe). Status: tracking.*

OI-30 probe (`probe_oi30_asgs_coverage.py`) found that 98.9% of catchment-anchored SA2s (2,269 / 2,294) sit in the same 6-11 year coverage bucket — the platform-wide 2019-onwards window driven by the current ABS ERP ingest scope. The remaining 25 SA2s are outliers: **16 with zero pop_0_4 coverage**, **9 with sparse 1-5 year coverage**.

These could be (a) genuinely missing from ABS ERP at SA2 level, (b) 2021-ASGS new codes not yet appearing in any ingest year, or (c) a combination. List of all 25 codes is in `recon/oi30_asgs_coverage_probe.md` (zero-coverage table + sparse top-30 table).

**Disposition.** Tracking only. None of these 25 SA2s are blocking — supply_ratio etc. silently render as None per P-2. Worth revisiting only if any of these 25 SA2s gain centre-anchor activity that warrants investigation, or as part of the OI-19 V1.5 ingest bundle if a more thorough ABS coverage audit becomes warranted.

### OI-31 — Click-to-detail on event overlay lines (Bug 6)
*Origin: 2026-05-03 PM. Status: open; ~1.0 session.*

Layer 4.2-A.3c added vertical dashed lines to the catchment trajectory charts at quarters when centres of the matching subtype opened or closed in the SA2 (color-coded green/red/grey). The data behind each line includes centre names + place changes (already in `p.centre_events`), but currently is not interactively exposed.

**Fix shape.** Click on a line → popup showing quarter, net change, list of new centre names + their places, list of removed centre names. Same data as the operator-page event detail. The `p.centre_events` array already carries everything needed; this is purely a renderer feature.

**Effort.** Substantial because event lines are drawn by Chart.js plugin (canvas pixels), not DOM elements — needs an overlay layer translating mouse coords to event matches. Likely ~1 session of careful renderer work.

### OI-28 — `populate_service_catchment_cache.py` cosmetic banner mismatch
*Origin: 2026-04-30. Status: open; cosmetic.*

Script's print banner says "v2" while the actual script is at v5. No functional impact (idempotency-guarded; won't re-run). 5-second fix at next touch.

### OI-26 — `demand_supply` industry threshold post-launch review
*Origin: 2026-04-30. Status: open; tracking.*

Mathematically grounded but may register false positives in saturated catchments. Review post-launch.

### OI-24 — Sub-pass dependency-ordering pass — DEC-65 amended
*Origin: 2026-04-29. Status: open; tracking.*

DEC-65 (probe-before-code) extended in spirit to "design before implement when ordering matters." Pure tracking; no specific deliverable.

### OI-22 — Future centre-page tab: ownership and corporate detail
*Origin: 2026-04-28. Status: tracking; deferred to V1.5+.*

Parent-group navigation, ownership chain detail. Out of V1 scope.

### OI-21 — Future centre-page tab: quality elements
*Origin: 2026-04-28. Status: tracking; deferred to V1.5+.*

Deeper NQS / regulatory detail per centre. Out of V1 scope.

### OI-20 — Workforce supply context enrichments
*Origin: 2026-04-28. Status: low priority; tracking.*

Additional workforce indicators beyond the 4 currently on the Workforce supply block. SEEK, advertised wages, etc. Bundled with V1.5 OI-19.

### OI-19 — Layer 4.4 V1.5 ingests bundle
*Origin: 2026-04-28. Status: open; ~2.0 sessions.*

NES + parent-cohort 25-44 + schools + SALM-extension + (optionally) SEEK/advertised wages. Bundled to amortise ABS workbook reading + concordance work. Largest V1.5 piece.

**OI-30 finding folds in here:** `abs_sa2_erp_annual` ingest extends backward beyond 2019 to widen pop_0_4 coverage from the current 6-year window. ABS publishes ERP back to at least 2001; just need to pull the historical years. Adds ~0.3 session to the bundle.

### OI-17 — `layer4_3_design.md` v1.0/v1.1 reconciliation
*Origin: 2026-04-28. Status: tracking.*

Two versions in recon/ that differ in places. Reconcile before referencing in future design work.

### OI-16 — DEC-29 verbatim text not recovered
*Origin: 2026-04-28. Status: tracking.*

DECISIONS.md has DEC-29 entry but original text unrecovered from chat history. Re-derive if revisited.

### OI-15 — Backfill audit for ARIA+ format mismatch
*Origin: 2026-04-28. Status: low priority.*

Some old records use "ARIA+" with different bracketing. Codebase scan candidate.

### OI-14 — Backfill audit for DD/MM/YYYY date parsing fix
*Origin: 2026-04-28. Status: low priority; multiple recent occurrences.*

Recommend codebase scan. Several places parse approval_date inconsistently.

### OI-13 — Frontend file backups accumulate in `docs/`
*Origin: 2026-04-28. Status: low; gitignore pattern uses single `?` so `v3_3` doesn't match.*

7+ backup files currently untracked. 30-second gitignore tightening fix at next housekeeping pass.

### OI-12 — DB backup pruning
*Origin: 2026-04-28. Status: inventory landed (commit `bbac24f`); deletion deferred. Updated 2026-05-03 evening.*

Cumulative `data/` backups now 7.7 GB across 36 files. Inventory probe (`inventory_db_backups.py`) committed read-only audit_log + table+rowcount snapshot per backup to `recon/db_backup_inventory_2026-05-03.md`. **Deletion is now safely reversible** — even if all binary backups were removed, the inventory preserves the queryable record.

**Prune dry-run finding (2026-05-03 evening).** `prune_db_backups.py` ran in dry-run mode; reported **0 files to delete** under current keep policy (default-conservative: keeps all `pre_*` named milestone anchors + 3 most recent timestamped). All 36 backups in current set qualify under one of these rules: 34 are `pre_*` anchors; 2 are within most-recent-3 timestamped. To actually free space, the keep policy would need relaxing (e.g. cap pre-anchor retention to N most recent per milestone family, or drop large legacy `pre_step*`/`pre_layer3` anchors that are now historically inert). Operator decision on policy relaxation deferred — disk pressure not currently biting per prior assessment.

**When to actually delete.** Patrick decides disk pressure is real. Either re-run `prune_db_backups.py --apply` after relaxing keep policy, or delete specific large legacy anchors manually using the inventory as the queryable record.

### OI-11 — `jsa_vacancy_rate` in Workforce block
*Origin: 2026-04-28. Closed: 2026-04-29c by DEC-76.*

### OI-10 — `provider_management_type` enum normalisation
*Origin: 2026-04-28. Status: low.*

Some values are inconsistently capitalised. Cleanup candidate.

### OI-09 — `sa2_under5_growth_5y` descoped from Layer 3
*Origin: 2026-04-28. Status: low; deferred.*

Currently rendered as "deferred" placeholder on the centre page. Revisit in V1.5+ if growth metric is requested.

### OI-08 — 19 synthetic SA2s with NULL ra_band
*Origin: 2026-04-28. Status: acceptable.*

Documented oddity; no fix needed.

### OI-07 — `participation_rate` not measured at SA2
*Origin: 2026-04-28. STD-34 LIVE.*

Tracked. STD-34 calibration discipline is the workaround.

### OI-06 — LFP source Census-only (3 pts)
*Origin: 2026-04-28. Status: low; Thread B (V1.5 SALM-extension) may upgrade.*

DEC-75 reclassified LFP triplet to Lite per this exact rationale. SALM-extension would promote back to Full with monthly/quarterly cadence.

### OI-05 — `service_catchment_cache` populated
*Origin: 2026-04-28. Closed: 2026-04-30 (Layer 2.5 sub-pass 2.5.1).*

### OI-04 — 43 services unchanged by Step 1c, lat/lng (0,0)
*Origin: 2026-04-28. Status: medium; overlaps with OI-01/02.*

### OI-03 — 9 cross-state SA2 mismatches post-Step 1c
*Origin: 2026-04-28. Status: low; documented.*

### OI-02 — 2 null-island services (lat/lng = 0,0)
*Origin: 2026-04-28. Status: medium per DEC-63.*

### OI-01 — 18 services without lat/lng need geocoding
*Origin: 2026-04-28. Status: medium per DEC-63.*

---

## CLOSED THIS SESSION (2026-05-03 evening)

- **OI-32** — Catchment metric explainer text (Bug 4). Shipped in 3 rounds across 3 commits:
  - **Round 1+2** (`1a90bf7`, centre_page.py v16->v18 + centre.html v3.21->v3.23): new `LAYER3_METRIC_ABOUT_DATA` constant + `_renderAboutData` helper rendering "About this measure" panel inside `_renderFullRow`; reuses workforce-row about_data visual pattern (v3.17). DEC-22 collapsed: panel font 11.5px->12.5px; `sa2_demand_supply` about_data + INDUSTRY_BAND_THRESHOLDS reframed from "fill expectation/risk" to occupancy-ramp / trade-up terminology; generic "70% break-even at 85% occupancy" note removed.
  - **Polish r2** (`83738ac`, centre_page.py v18->v19): operator screenshot review caught remaining "fill"/"soft" in band_copy chips, INTENT_COPY italic lines, INDUSTRY_BAND label. Cleaned across `sa2_demand_supply` band_copy + sa2-prefixed INTENT_COPY for `sa2_demand_supply` / `sa2_supply_ratio` / `sa2_adjusted_demand`; INDUSTRY soft-band label "soft ramp-up" → "below break-even".
  - **v20 bundle** (centre_page.py v19->v20 + centre.html v3.23->v3.24): operator review of v19 INDUSTRY label semantics. Parallel-framed all 4 `sa2_demand_supply` band labels in supply-vs-demand language only ("supply heavy" / "supply leaning" / "approaching balance" / "demand leading") because break-even is a profitability conclusion the ratio alone cannot support. about_data first line tightened to match. Cohort distribution histogram gains centred italic explainer text + cohort-note alignment switched to centre. New `_renderMiniDecileStrip` helper used inline for SEIFA decile fact (chosen over colour-coding because SES has no valence in LDC credit). DEC-77 minted to formalise the industry-absolute threshold framework.

- **OI-30** — Bayswater (and assumed other 2021-ASGS) SA2s have incomplete pre-2019 ABS coverage. Closed by probe (`probe_oi30_asgs_coverage.py`, read-only). Probe **refuted** the original 2021-ASGS-concordance hypothesis: Bondi Junction-Waverly (118011341 — established 2016-ASGS area) has the same 6-year coverage (2019-2024) as Bayswater (211011251). 98.9% of catchment-anchored SA2s sit in the same 6-11 year bucket; the issue is platform-wide, not code-specific. Real fix: extend `abs_sa2_erp_annual` ingest backward — folds into OI-19 V1.5 ingest bundle. 25 outlier SA2s (16 zero + 9 sparse coverage) split out as **OI-33**.
'''


PROJECT_STATUS_CONTENT = '''# Project Status

*Last updated: 2026-05-03 (end of evening session). The on-disk version supersedes the project-knowledge monolith if they disagree.*

## Headline

**V1 is at HEAD.** All blocking V1 work shipped. The previously-deferred Bug 4 (catchment metric explainer text, OI-32) closed this evening across 3 polish rounds. Industry-absolute threshold framework formalised as **DEC-77** after the round-3 label review. OI-30 closed by probe (hypothesis refuted; real fix folds into OI-19). New tracking item OI-33 opened for the 25 SA2 outliers the probe surfaced.

## Centre page — current state

`centre_page.py` v20 (Python backend) + `centre.html` v3.24 (renderer) + payload schema `centre_payload_v6` (unchanged this evening — v17/18/19/20 added fields, no schema rev).

### Catchment Position card — final V1 shape

Layer 4.2-A.3c (afternoon, commit `bcdf84c`) shipped the catchment-trajectory feature end-to-end. This evening's polish (commits `1a90bf7` + `83738ac` + v20 commit) completed the operator-facing copy, visuals, and threshold framing:

| Metric | Weight | Trajectory | Events overlay | INDUSTRY band | About panel | Calibration in DER |
|---|---|---|---|---|---|---|
| `sa2_supply_ratio` | FULL | quarterly per subtype | YES (subtype-matched) | 7 levels | YES | — |
| `sa2_demand_supply` | FULL | quarterly (cal_rate held) | YES | 4 levels (parallel-framed v20) | YES | YES (4.2-A.4) |
| `sa2_child_to_place` | FULL | quarterly (1/supply_ratio) | YES | 5 levels | YES | — |
| `sa2_adjusted_demand` | FULL | quarterly (cal_rate held) | YES | NO (decile only) | YES | YES (4.2-A.4) |
| `sa2_demand_share_state` | CONTEXT | n/a | n/a | n/a | n/a | YES (4.2-A.4) |

**INDUSTRY band labels for `sa2_demand_supply`** now read in supply-vs-demand language only (v20 / DEC-77):

| Threshold | Key | Label | Note |
|---|---|---|---|
| ≤0.40 | soft | supply heavy | demand well short of available capacity |
| ≤0.55 | near_be | supply leaning | demand below available capacity |
| ≤0.85 | viable | approaching balance | demand and supply broadly aligned |
| >0.85 | strong | demand leading | demand exceeds available capacity |

Keys retained because `centre.html` cautionKeys/positiveKeys reference them for visual treatment.

**About this measure panels.** `_renderAboutData` helper renders longer plain-language explainer text on each catchment Full row (between intent_copy and DER/COM badges). Copy lives in `LAYER3_METRIC_ABOUT_DATA` constant in `centre_page.py`. Format: `\\n\\n` for paragraph breaks, `\\n` for tight line breaks within a paragraph. Font 12.5px italic in subtle left-bordered panel. Silent absence per P-2 for non-catchment metrics.

**Cohort distribution histogram** now ships a centred italic explainer line below the bars ("Distribution of values across the peer cohort. The highlighted bar shows where this SA2 sits; the decile strip below converts that position to the 1–10 scale.") plus the existing cohort-note line switched from right-aligned to centre.

**SEIFA decile fact** (Catchment section, NOW block) renders an inline mini decile strip via new `_renderMiniDecileStrip` helper — same colour grammar as `_renderDecileStrip` (per-decile tones 6%/13%/20%, accent + outline on active cell, structural gaps between bands). Compact: 6px cells, 10px tall, no number labels. Chosen over colour-coding because SES has no valence in LDC credit. Helper is reusable for any future "decile-as-fact" surface.

**DEC-77 (NEW this session).** Industry-absolute threshold framework formalised. Three catchment metrics opt in via `industry_thresholds: True` on their `LAYER3_METRIC_META` entry. Bands derived from PC universal-access target / RSI v4.2 distribution / Credit Committee Brief break-even+target occupancy. Renderer reads `p.industry_band` (key, drives pill colour), `p.industry_band_label` (visible text), `p.industry_band_note` (descriptor). `sa2_adjusted_demand` is intentionally not banded (count not ratio). v20 finalised the `sa2_demand_supply` labels in supply-vs-demand language only — break-even is a profitability conclusion the ratio alone cannot support.

**Subtype handling** (unchanged from afternoon). Centre's `service_sub_type` (LDC / OSHC / PSK / FDC) drives which `by_subtype.<>` block in sa2_history.json gets read. Null/Other → LDC fallback. LDC is V1 focus (53% of platform). OSHC/PSK/FDC use shared `pop_0_4` denominator (subtype-correct denominators are V1.5).

**Calibration semantics** (unchanged). `adjusted_demand` and `demand_supply` use the centre's CURRENT `calibrated_rate` held constant across all historical quarters. Surfaced now in the about_data: "the realistic demand the catchment can actually absorb" / "a key input to occupancy ramp expectations".

**DEC-74 amendment** (afternoon). Perspective toggle removed from the 3 reversible catchment metrics. Inverse views render as separate Full rows in the same card; toggle was redundant by construction.

**Workforce Supply Context block, Population, Labour Market** — unchanged this evening.

---

## Phase 2.5 — status by layer

| Layer | Description | Status |
|---|---|---|
| 0 / 1 / 2 | Foundations | COMPLETE |
| 2.5 | Catchment cache populator | COMPLETE 2026-04-30 |
| 3 / 4.1 | Layer 3 banding existing 14 metrics + render-side | COMPLETE |
| **4.2** | **Centre page renderer** | **COMPLETE** — all sub-passes shipped; OI-32 polish closed evening of 2026-05-03 |
| 4.3 | Centre page polish + workforce | COMPLETE — all 9 sub-passes |
| 4.4 | V1.5 ingests (NES + parent-cohort + schools + SALM-ext + ABS ERP backward extension) | DEFERRED to V1.5; OI-30 finding folds in |

---

## What's next

V1 path remaining: **~0 sessions.** No mandatory work.

**V1.5 path (~3 sessions):**
- **OI-19** — Layer 4.4 ingests bundle (NES + parent-cohort + schools + SALM-extension + ABS ERP backward extension per OI-30 finding). ~2 sessions.
- **OI-31** — Click-on-event detail (popup with centre names + place changes when clicking a vertical event line). Substantial renderer feature; ~1 session.

**Optional housekeeping (low priority):**
- **OI-13** — Frontend file backups gitignore tightening (~30 sec).
- **OI-12** — DB backup pruning. Dry-run run this evening: 0 deletions under current default-conservative keep policy. Operator decision needed on relaxing policy (legacy `pre_step*`/`pre_layer3` anchors are now historically inert and dominate the 7.7 GB).
- **OI-14 / OI-15** — Date parsing + ARIA+ format codebase scans.
- **OI-10** — `provider_management_type` enum normalisation.
- **OI-28** — `populate_service_catchment_cache.py` cosmetic banner mismatch (5-second fix).

See ROADMAP.md for full dependency-ordered queue.

---

## Database state

Path: `data\\kintell.db` (~565 MB). 36 tables. `audit_log: 142 rows` (no DB mutations this evening).

`docs/sa2_history.json`: v2 multi-subtype, 13.2 MB, 50 quarters, 1,267 SA2s, 4 subtype buckets. Tracked in git.

`data/` backups: 36 files, 7.7 GB. OI-12 prune dry-run reported 0 deletions under current keep policy — see OPEN_ITEMS.md OI-12 for keep-policy detail and operator-decision pending.

---

## Git state

This evening's commits (chronological from afternoon HEAD `bc52f3c`):

1. `1a90bf7` — OI-32 close (Bug 4) rounds 1+2 (centre_page.py v16→v18 + centre.html v3.21→v3.23). New `LAYER3_METRIC_ABOUT_DATA` constant + `_renderAboutData` helper. Round 2: panel font 11.5px→12.5px; sa2_demand_supply about_data + INDUSTRY_BAND_THRESHOLDS reframed from "fill" terminology.
2. `83738ac` — OI-32 polish r2 (centre_page.py v18→v19). Operator screenshot review caught remaining "fill"/"soft" in band_copy chips + INTENT_COPY italic + INDUSTRY soft-band label. Cleaned across `sa2_demand_supply` band_copy + sa2-prefixed INTENT_COPY for 3 catchment metrics; INDUSTRY label "soft ramp-up" → "below break-even".
3. `<v20-commit>` — OI-32 v20 bundle (centre_page.py v19→v20 + centre.html v3.23→v3.24). INDUSTRY parallel-framing per DEC-77 review; about_data first-line tightening; cohort histogram explainer + center alignment; `_renderMiniDecileStrip` helper for SEIFA fact.
4. `<doc-commit>` — End-of-session doc refresh + OI-30 probe artefact (this commit).

---

## Standards / decisions

**One new DEC this session:** **DEC-77** (Industry-absolute threshold framework for catchment ratios). Formalises the framework that Layer 4.2-A.3b shipped on 2026-04-30 and the v20 polish round finalised. Recorded in DECISIONS.md.

**No STD changes this session.**

**Carried observations** (unchanged from afternoon — worth a 1-line addition each at next consolidation):
- STD-35 reinforcement: "regenerate at session end" needs explicit "land on disk + upload to project knowledge" verification.
- STD-10 patcher pattern: anchors must use `\\n` not `\\r\\n` even on Windows source files (Python text mode normalises on read).

---

## Open items summary

See OPEN_ITEMS.md for full text.

**Closed this session (evening):**
- **OI-32** — Catchment metric explainer text. Closed across 3 commits (`1a90bf7` + `83738ac` + v20 commit).
- **OI-30** — Pre-2019 pop_0_4 coverage gap. Probe refuted original ASGS-concordance hypothesis (Bondi has same 6-year window as Bayswater). Real fix folds into OI-19.

**Opened this session (evening):**
- **OI-33** — 25 SA2s with zero or sparse pop_0_4 coverage (16 zero + 9 sparse, 1.1% of platform-anchored SA2s). Tracking only; revisit if any gain centre-anchor activity.

**Carried (unchanged):** OI-01–04, OI-06–10, OI-12 (status updated with prune dry-run finding), OI-13–17, OI-19 (OI-30 finding folds in), OI-20–22, OI-24, OI-26, OI-28, OI-31.

---

## Doc set

The 2026-04-28 restructure produced the 12-doc set. Update history:
- 2026-04-29c+d → 2026-04-30 → 2026-05-03 morning → 2026-05-03 PM (HEAD `bc52f3c` regen).
- **2026-05-03 evening:** OI-32 closed across 3 polish rounds, DEC-77 minted, OI-30 closed by probe, OI-33 opened, OI-12 status updated. This session's doc commit lands updated PROJECT_STATUS / OPEN_ITEMS / PHASE_LOG / ROADMAP / DECISIONS plus the new `recon/oi30_asgs_coverage_probe.md` artefact.
'''


# ─────────────────────────────────────────────────────────────────────
# CONTENT — append blocks
# ─────────────────────────────────────────────────────────────────────

PHASE_LOG_APPEND = '''

---

## 2026-05-03 (evening) — OI-32 close + DEC-77 mint + OI-30 probe + OI-12 dry-run

Continuation session. V1 was at HEAD `bc52f3c` at session start. Ended at `<doc-commit>` after the polish + doc bundle. 4 commits this evening (3 code + 1 doc).

### Session shape

Polish round on the catchment-position card surfaces, driven by operator visual review. Three iterative polish rounds on the same OI-32 deliverable plus a hypothesis-refuting probe (OI-30) and a deferred-decision dry-run (OI-12). Pattern: probe → propose copy → ship → operator visual review → repeat. Each round caught regressions or category errors the previous round didn't see — the "below break-even" fix in particular was a category error (asserting profitability conclusion from a supply/demand ratio) that only became visible after the "fill" cleanup landed.

### Block 1 — OI-32 round 1+2 (commit `1a90bf7`)

`patch_oi32_about_data.py` + `patch_oi32_polish.py` bundled into single commit per DEC-22 collapse pattern.

**Backend (centre_page.py v16 → v18, 7 mutations across 2 patchers):**

v17 (about_data field added):
- New module-level constant `LAYER3_METRIC_ABOUT_DATA` carrying plain-language "what is this metric?" copy for the 4 Full-weight catchment metrics
- `_layer3_position` propagates `p.about_data` onto stub + populated entries via `LAYER3_METRIC_ABOUT_DATA.get(metric_name)` — same shape as `intent_copy` propagation

v18 (operator review of v17 visuals):
- Panel font 11.5px → 12.5px in `_renderAboutData`
- `sa2_demand_supply` about_data text reframed from "fill expectation / fill risk" to "occupancy ramp-up / trade-up risk"
- INDUSTRY_BAND_THRESHOLDS sa2_demand_supply: replaced "fill" terminology in band labels/notes; removed generic "below 70% break-even at typical 85% occupancy" note

**Renderer (centre.html v3.21 → v3.23, 5 mutations across 2 patchers):**

v3.22:
- New `_renderAboutData(p)` helper rendering p.about_data as permanent visible "About this measure" panel (uppercase label, left-border, muted background, splits on `\\n\\n` for paragraphs and `\\n` within paragraphs for line breaks)
- Inserted call inside `_renderFullRow` between `_renderIntentCopy(p)` and the DER/COM badge row
- Reuses visual pattern from workforce-row about_data block (v3.17)

v3.23:
- Font bump 11.5px → 12.5px in the About panel container

### Block 2 — OI-32 polish r2 (commit `83738ac`)

`patch_oi32_polish_r2.py`. Operator screenshot review caught remaining "fill"/"soft" surfaces that round-1 didn't cover.

**Backend (centre_page.py v18 → v19, 6 mutations):**

- `band_copy` chips on `sa2_demand_supply` reframed: "soft catchment — fill risk" → "supply outweighs demand — trade-up risk"; "demand pull — strong fill expected" → "demand outweighs supply — fast occupancy ramp"
- `LAYER3_METRIC_INTENT_COPY` sa2-prefixed entries cleaned: `sa2_demand_supply`, `sa2_supply_ratio`, `sa2_adjusted_demand` all had visible "fill" terminology in the italic intent line
- INDUSTRY_BAND soft-band label "soft ramp-up" → "below break-even" (key stays "soft" because centre.html cautionKeys references it for visual treatment)
- Unprefixed duplicate INTENT_COPY entries left alone (kept for backward reference per existing comment, not read by `_layer3_position`)

**Diagnosis interlude.** Operator's first screenshot post-Block 1 showed unchanged old text. Initially diagnosed as browser cache. Probe of `centre.html` revealed the page fetches `/api/...` from `review_server.py` — a long-running Python process that imports `centre_page` at module load. Python module cache prevents on-disk `centre_page.py` changes from taking effect until server restart. Operator restarted server (multiple instances had to be killed first via Win11-safe `Get-CimInstance Win32_Process` filter); v17/v18 changes then visible. Worth banking as a reminder for any future centre_page.py mutation.

### Block 3 — OI-32 v20 bundle

`patch_oi32_v20_bundle.py`. Operator review of v19 surfaced two more issues:

1. The INDUSTRY label "below break-even" makes a profitability claim the demand/supply ratio alone cannot support (break-even depends on price, cost base, ramp curve, mix). Same category-error fix at the about_data level: "the occupancy ramp-up expectation for a centre here" overreaches similarly.
2. Cohort histogram needs explainer text + horizontal centering. SEIFA decile would benefit from a visual position indicator (mini decile strip chosen over colour-coding because SES has no valence in LDC credit).

**Backend (centre_page.py v19 → v20, 3 mutations):**

- INDUSTRY_BAND_THRESHOLDS sa2_demand_supply parallel-framed in supply-vs-demand language only:
  - soft → "supply heavy" / "demand well short of available capacity"
  - near_be → "supply leaning" / "demand below available capacity"
  - viable → "approaching balance" / "demand and supply broadly aligned"
  - strong → "demand leading" / "demand exceeds available capacity"
- about_data first line tightened: "How supply compares to realistic demand — a key input to occupancy ramp expectations"

**Renderer (centre.html v3.23 → v3.24, 4 mutations):**

- `_renderCohortHistogram` ships centred italic explainer text below the bars; cohort-note alignment switched from right to centre
- New `_renderMiniDecileStrip(decile)` helper — compact 10-cell horizontal strip, same colour grammar as `_renderDecileStrip` (per-decile tones 6%/13%/20%, accent + outline on active cell, structural gaps between bands), inline-sized (6px wide cells, 10px tall, no number labels)
- SEIFA decile fact in Catchment section gains inline `_renderMiniDecileStrip` call

### Block 4 — DEC-77 mint

Industry-absolute threshold framework formalised. Layer 4.2-A.3b shipped (2026-04-30) the framework; v20 round finalised the demand_supply labels. Now operator-validated and locked. DEC-77 entry recorded in DECISIONS.md.

### Block 5 — OI-30 probe (read-only; recon artefact)

`probe_oi30_asgs_coverage.py`. Per DEC-65, probe-before-design.

**Result: hypothesis refuted.** Bondi Junction-Waverly (118011341 — established 2016-ASGS area, no expected concordance issue) shows the same 6-year coverage (2019-2024) as Bayswater (211011251). 98.9% of catchment-anchored SA2s (2,269 / 2,294) sit in the same 6-11 year coverage bucket. The issue is platform-wide: `abs_sa2_erp_annual` ingest covers 2019-2024 across the entire dataset, not a code-mismatch between ASGS editions.

**Disposition:**
- OI-30 closed (probe complete; hypothesis refuted; real fix is platform-wide ABS ERP ingest extension that folds into OI-19 V1.5 bundle).
- 25 outlier SA2s (16 zero + 9 sparse) split out as new OI-33 for tracking.
- Probe artefact written to `recon/oi30_asgs_coverage_probe.md`.

### Block 6 — OI-12 prune dry-run

`prune_db_backups.py` (no `--apply`). Reported **0 deletions** under current default-conservative keep policy: all 36 backups in current set qualify as either `pre_*` named milestone anchors (34) or within most-recent-3 timestamped (2).

**Disposition:** OI-12 status updated with this finding. Operator decision needed on relaxing keep policy if disk pressure becomes real (legacy `pre_step*`/`pre_layer3` anchors dominate the 7.7 GB and are now historically inert). No deletion executed this session.

### Open items movement this session (evening)

**Closed:**
- **OI-32** (Catchment metric explainer text, Bug 4) — 3 polish rounds shipped via Blocks 1-3
- **OI-30** (pre-2019 pop_0_4 coverage gap) — closed by Block 5 probe; real fix folds into OI-19

**Opened:**
- **OI-33** — 25 outlier SA2s with zero/sparse pop_0_4 coverage (split from OI-30 probe finding). Tracking only.

**Updated:**
- **OI-12** status note: prune dry-run reported 0 deletions; operator decision on policy relaxation deferred
- **OI-19** scope expanded: ABS ERP backward extension folds in (~0.3 session added to bundle)

### Standards / decisions

**New:** **DEC-77** — Industry-absolute threshold framework for catchment ratios. Recorded in DECISIONS.md.

**No STD changes.**

### What's banked for next session

V1 is shippable and at HEAD. Optional polish queue:
- Various housekeeping (gitignore tightening OI-13, OI-28 cosmetic banner, codebase scans OI-14/OI-15)
- OI-12 keep-policy relaxation decision (only if disk pressure bites)

V1.5 path:
- OI-19 V1.5 ingest bundle (NES + parent-cohort + schools + SALM-extension + ABS ERP backward extension per OI-30 finding) — ~2 sessions
- OI-31 click-on-event detail — ~1 session

### Session shape note

Iterative polish on a single OI took 3 rounds because each round surfaced category errors the previous round didn't see. The pattern (operator screenshot → I propose fix → ship → operator screenshot → repeat) is the right mode for visual/copy work — caught issues that abstract review would have missed (notably the "below break-even" profitability overreach which only became visible once the cruder "fill"/"soft" cleanup made room to read the surface critically). DEC-65 probe-before-code earned its keep at OI-30 — refuted the original hypothesis before any concordance code was written, saving ~0.5 session.
'''


DECISIONS_APPEND = '''

---

## DEC-77 — Industry-absolute threshold framework for catchment ratios
Status: Active
Date: 2026-05-03

Context: Layer 4.2-A.3b shipped (2026-04-30) an industry-absolute band line beneath the per-cohort decile chips for the three catchment ratio metrics with meaningful industry-grounded thresholds. The framework had been operating in production for 3 days. The 2026-05-03 evening v20 polish round reframed the demand-supply band labels in supply-vs-demand language only after operator review caught that the original "below break-even" labels asserted a profitability conclusion the demand/supply ratio alone cannot support (break-even depends on price, cost base, ramp curve, mix). The framework is now operator-validated; locking the design.

Decision: Three catchment metrics opt in to industry-absolute banding via `industry_thresholds: True` on their `LAYER3_METRIC_META` entry. Bands derived from three locked sources:

- **`sa2_supply_ratio`** — 7 levels. Productivity Commission universal-access target (1.0 places/child = all children, three days/week) anchors the upper bound. Low/mid/high tiers grounded in the absolute supply landscape (desert / undersupplied / below_bench / at_bench / well_served / at_target / saturated).
- **`sa2_child_to_place`** — 5 levels (excess_capacity / balanced / tight / constrained / severe). Derived from Remara Strategic Insights v4.2 real distribution by SES + remoteness.
- **`sa2_demand_supply`** — 4 levels. Thresholds (0.40 / 0.55 / 0.85) inherit Credit Committee Brief break-even (70%) + target (85%) occupancy maths. **Labels reframed in supply-vs-demand language only — break-even is a profitability conclusion the ratio alone cannot support, and the label must not assert it.** v20 final labels: "supply heavy" / "supply leaning" / "approaching balance" / "demand leading" with parallel-framed notes.

`sa2_adjusted_demand` is intentionally NOT banded (decile-only) because it is a count not a ratio.

Renderer: `_renderIndustryBand` reads `p.industry_band` (band key, drives cautionary/positive pill colour via `cautionKeys` / `positiveKeys`), `p.industry_band_label` (visible text inside the pill), `p.industry_band_note` (descriptor next to the pill). Silent absence per P-2 when metric not opted in or raw_value is null. Band keys are stable identifiers — relabel the visible text without changing the key, otherwise the pill colour treatment breaks.

Consequences: Industry-absolute bands now operate as a first-class lens on top of the per-cohort decile lens. Future ratio metrics can opt in by adding to `INDUSTRY_BAND_THRESHOLDS` and setting `industry_thresholds: True`. Any future label work must respect the supply-vs-demand discipline established by v20: visible labels describe what the ratio measures, not what it implies for downstream financials. OI-26 (post-launch review of demand_supply thresholds in saturated catchments) remains active under this DEC.
'''


ROADMAP_APPEND = '''

---

## Updates — 2026-05-03 evening session

**Closed:**
- **OI-32** (Catchment metric explainer text) — 3 polish rounds shipped, see PHASE_LOG.md evening block.
- **OI-30** (pre-2019 pop_0_4 coverage gap) — closed by probe (`probe_oi30_asgs_coverage.py`). 2021-ASGS hypothesis refuted; the issue is platform-wide ABS ERP ingest scope, not code-specific. Real fix folds into OI-19 V1.5 ingest bundle (~0.3 session added).

**Opened:**
- **OI-33** — 25 outlier SA2s (16 zero + 9 sparse pop_0_4 coverage). Tracking only.

**New decision:**
- **DEC-77** — Industry-absolute threshold framework for catchment ratios. LIVE (mint 2026-05-03 evening; formalises framework that Layer 4.2-A.3b shipped 2026-04-30 and v20 polish round finalised in supply-vs-demand language only).

**Status updates:**
- **OI-12** — Prune dry-run this session reported 0 deletions under current default-conservative keep policy. Operator decision deferred on policy relaxation.
- **OI-19** — Scope expanded by OI-30 finding (ABS ERP backward extension folds in).
'''


# ─────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────

def backup_and_write(path: Path, new_content: str, label: str) -> None:
    """Backup existing file then overwrite with new content."""
    if not path.exists():
        raise FileNotFoundError(f"{label} not found at {path}")
    backup = path.with_name(f"{path.name}.bak_{STAMP}")
    shutil.copy2(path, backup)
    print(f"  [{label}] backup: {backup.name}")
    path.write_text(new_content, encoding="utf-8", newline="")
    print(f"  [{label}] written ({len(new_content)} chars)")


def backup_and_append(path: Path, append_content: str, sentinel: str, label: str) -> None:
    """Backup existing file then append, but only if sentinel not already present."""
    if not path.exists():
        raise FileNotFoundError(f"{label} not found at {path}")
    existing = path.read_text(encoding="utf-8")
    if sentinel in existing:
        print(f"  [{label}] SKIP: sentinel already present (idempotent — already applied)")
        return
    backup = path.with_name(f"{path.name}.bak_{STAMP}")
    shutil.copy2(path, backup)
    print(f"  [{label}] backup: {backup.name}")
    with path.open("a", encoding="utf-8", newline="") as f:
        f.write(append_content)
    print(f"  [{label}] appended ({len(append_content)} chars)")


# ─────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 64)
    print("Doc applier — 2026-05-03 evening session")
    print("=" * 64)

    # Pre-flight: every target file must exist
    targets = [
        (OPEN_ITEMS,   "OPEN_ITEMS.md"),
        (PROJECT_STAT, "PROJECT_STATUS.md"),
        (PHASE_LOG,    "PHASE_LOG.md"),
        (DECISIONS,    "DECISIONS.md"),
        (ROADMAP,      "ROADMAP.md"),
    ]
    missing = [label for path, label in targets if not path.exists()]
    if missing:
        print(f"\nERROR: missing target file(s): {missing}")
        print(f"Expected at: {DOCS}")
        sys.exit(1)

    print(f"\nAll 5 target files found at: {DOCS}\n")

    print("Replacing full files:")
    backup_and_write(OPEN_ITEMS,   OPEN_ITEMS_CONTENT,    "OPEN_ITEMS.md")
    backup_and_write(PROJECT_STAT, PROJECT_STATUS_CONTENT,"PROJECT_STATUS.md")

    print("\nAppending to existing files (idempotent):")
    backup_and_append(PHASE_LOG, PHASE_LOG_APPEND, SENTINEL_PHASE_LOG, "PHASE_LOG.md")
    backup_and_append(DECISIONS, DECISIONS_APPEND, SENTINEL_DECISIONS, "DECISIONS.md")
    backup_and_append(ROADMAP,   ROADMAP_APPEND,   SENTINEL_ROADMAP,   "ROADMAP.md")

    print("\n" + "=" * 64)
    print("DONE.")
    print("Next:")
    print("  1. Review changes if you want:")
    print("     git diff --stat \"recon/Document and Status DB/\"")
    print("  2. Stage + commit (see commit command in chat)")
    print("=" * 64)


if __name__ == "__main__":
    main()
