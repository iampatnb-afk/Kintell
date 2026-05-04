# Project Status

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

**About this measure panels.** `_renderAboutData` helper renders longer plain-language explainer text on each catchment Full row (between intent_copy and DER/COM badges). Copy lives in `LAYER3_METRIC_ABOUT_DATA` constant in `centre_page.py`. Format: `\n\n` for paragraph breaks, `\n` for tight line breaks within a paragraph. Font 12.5px italic in subtle left-bordered panel. Silent absence per P-2 for non-catchment metrics.

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

Path: `data\kintell.db` (~565 MB). 36 tables. `audit_log: 142 rows` (no DB mutations this evening).

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
- STD-10 patcher pattern: anchors must use `\n` not `\r\n` even on Windows source files (Python text mode normalises on read).

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
