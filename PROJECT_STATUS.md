# Project Status

*Last updated: 2026-05-04 (end of full-day session). The on-disk version supersedes the project-knowledge monolith if they disagree.*

## Headline

**V1 is at HEAD `bcdf84c`.** The full-day 2026-05-04 session shipped V1.5 first-piece work end-to-end on the data side: V1.5 scoping doc created, C3 absolute-change render shipped (closing OI-34), A1 dissolved by probe trail, A2 NES-share ingest closed across three commits (v2 ingest, v3 unit-fix to percentage, populator wire), B2 banding closed, and C2-NES registered on the data side. Two new OIs minted: **OI-35** (`layer3_apply.py` wholesale-rebuild bug — wiped 9,035 catchment banding rows mid-session, recovered via re-run of catchment banding script) and **OI-36** (centre.html / centre_page.py hardcode catchment rows so the new NES metric is invisible until render-side patch lands). Calibration nudge live for high-NES SA2s (Bayswater 0.50→0.48, Bentley 0.48→0.46).

## Centre page — current state

`centre_page.py` v20 (Python backend) + `centre.html` v3.25 (renderer) + payload schema `centre_payload_v6` (unchanged this session — the data-side C2-NES registration added registry entries, no schema rev).

### Catchment Position card — current shape

| Metric | Weight | Trajectory | Events overlay | INDUSTRY band | About panel | Calibration in DER |
|---|---|---|---|---|---|---|
| `sa2_supply_ratio` | FULL | quarterly per subtype | YES (subtype-matched) | 7 levels | YES | — |
| `sa2_demand_supply` | FULL | quarterly (cal_rate held) | YES | 4 levels (parallel-framed) | YES | YES |
| `sa2_child_to_place` | FULL | quarterly (1/supply_ratio) | YES | 5 levels | YES | — |
| `sa2_adjusted_demand` | FULL | quarterly (cal_rate held) | YES | NO (decile only) | YES | YES |
| `sa2_demand_share_state` | CONTEXT | n/a | n/a | n/a | n/a | YES |
| **`sa2_nes_share`** | **LITE** | **registered (data side)** | n/a | NO (deciles+chip only) | TBD | **YES (live nudge)** |

The NES row's data-side registration is complete (commit `3ddcf18`); the row itself is **not yet visible on the page** because centre.html / centre_page.py hardcode the catchment-card rows rather than iterating from `LAYER3_METRIC_META.card='catchment_position'`. Tracked as OI-36; recommended first piece next session.

**C3 trajectory chart label format** (since 2026-05-04 morning):

`"+51.4% since 2020 · +303 places · +3 centres"`

Rendered alongside the trend % on each catchment trajectory chart.

**Calibration nudge end-state** (since A2 wire 2026-05-04):

Rule_text now shows NES on every SA2 with data; high-NES catchments (NES ≥ 30%) receive a −0.02 nudge. Verification SA2s end-state:

| SA2 | Name | NES % | Rate | Rule text |
|---|---|---|---|---|
| 211011251 | Bayswater Vic | 31.07 | 0.48 | default 0.50; income decile 4 (mid, no nudge); female LFP 62.1% (mid, no nudge); −0.02 high NES share (0.31); ARIA band 1 unrecognised (no nudge) |
| 118011341 | Bondi Junction-Waverly NSW | 23.58 | 0.54 | default 0.50; +0.02 income decile 10 (high); +0.02 female LFP top quartile (67.7% ≥ 67.2%); NES share 0.24 (mid, no nudge); ARIA band 1 unrecognised (no nudge) |
| 506031124 | Bentley-Wilson WA | 37.55 | 0.46 | default 0.50; −0.02 income decile 3 (low); female LFP 60.6% (mid, no nudge); −0.02 high NES share (0.38); ARIA band 1 unrecognised (no nudge) |

**National 2021 NES share:** 22.28% (matches published ABS 22-24% band).

**DEC-74 amendment, About panels, Cohort histogram, SEIFA mini decile strip, Workforce / Population / Labour Market blocks** — unchanged from 2026-05-03 evening.

---

## Phase 2.5 — status by layer

| Layer | Description | Status |
|---|---|---|
| 0 / 1 / 2 | Foundations | COMPLETE |
| 2.5 | Catchment cache populator | COMPLETE 2026-04-30 |
| 3 / 4.1 | Layer 3 banding existing 14 metrics + render-side | COMPLETE; **+1 metric (sa2_nes_share, B2 closed 2026-05-04)** |
| **4.2** | **Centre page renderer** | **COMPLETE for V1**; OI-36 open for V1.5 NES row |
| 4.3 | Centre page polish + workforce | COMPLETE |
| **4.4** | **V1.5 ingests** | **A2 done 2026-05-04**; A3-A6 remaining; tracked in CENTRE_PAGE_V1.5_ROADMAP.md |

---

## What's next

V1 path remaining: **~0 sessions.** No mandatory work.

**V1.5 first piece (next session):** **OI-36 — C2-NES render-side** (~0.3 sess). Closes the visible-on-page gap from this session.

**V1.5 path remaining (~2.6 sess):**
- **A3–A6** (~1.4 sess) — Phase A core (post-A1 dissolution + A2 done)
- **B1, B3–B5** (~0.9 sess) — Phase B core (post-B2 done)
- **OI-36 + C2 other** (~0.6 sess) — visible NES row + new Full rows for B-pass

**Phase 2 (post-V1.5):** A10 + C8 (~0.7 sess) — T08 country-of-birth + Demographic Mix narrative panel. Depends on C2-NES render first.

See **CENTRE_PAGE_V1.5_ROADMAP.md** for the canonical V1.5 dependency-ordered queue and **ROADMAP.md** for the parent dependency view.

**Optional housekeeping (low priority, anytime):**
- **OI-12** — DB backup pruning. **CRITICAL** at ~8.5 GB cumulative (+2.7 GB this session across 5 backups). Keep policy needs relaxation — operator decision pending.
- **OI-35** — `layer3_apply.py` real fix (~0.5 sess). Workaround in place: always run `layer3_x_catchment_metric_banding.py` after `layer3_apply.py`.
- **OI-13** — Frontend file backups gitignore tightening (~30 sec).
- **OI-14 / OI-15** — Date parsing + ARIA+ format codebase scans.
- **OI-10** — `provider_management_type` enum normalisation.
- **OI-28** — `populate_service_catchment_cache.py` cosmetic banner (5 sec).
- **STD-37 candidate** — "search project knowledge before probing" mint at next consolidation.
- **Recon probe sweep** — root probes → recon/probes/.

---

## Database state

Path: `data\kintell.db` (~565 MB). 36 tables. **`audit_log: 149 rows`** (was 142 at start of 2026-05-04; **+7 mutations this session**).

Today's audit_log additions:

| audit_id | action | description |
|---|---|---|
| 143 | `census_nes_share_ingest_v2` | A2 v2 ingest |
| 144 | `service_catchment_cache_populate_v1` | Populator first re-run |
| 145 | `layer3_banding_v1` | B2 layer3 — wiped catchment as side effect |
| 146 | `census_nes_share_ingest_v3` | A2 v3 unit-fix replace |
| 147 | `service_catchment_cache_populate_v1` | Populator re-run with /100 |
| 148 | `layer3_banding_v1` | layer3 with percentage |
| 149 | `layer3_catchment_banding_v1` | Recovery from OI-35 wipe |

**Backups added today (5 files, ~2.7 GB):**
- `data\pre_layer4_4_step_a2_20260504_123214.db` (~540 MB)
- `data\pre_layer4_4_step_a2_v3_20260504_140128.db` (~540 MB)
- `data\kintell.db.backup_pre_2_5_1_20260504_140136` (~567 MB)
- `data\kintell.db.backup_pre_layer3_20260504_134117` (~541 MB)
- `data\kintell.db.backup_pre_2_5_2_20260504_142735` (~567 MB)

**Cumulative `data\` backups: ~8.5 GB across 41 files. OI-12 status critical.**

`docs/sa2_history.json`: v2 multi-subtype, 13.2 MB, 50 quarters, 1,267 SA2s, 4 subtype buckets. Tracked in git. Unchanged this session.

---

## Git state

V1 ship: `bcdf84c` (2026-05-03 evening).

This session's commits, chronological:

1. `f92b517` — Add `CENTRE_PAGE_V1.5_ROADMAP.md` (V1.5 scoping pass)
2. `f47a0ba` — centre.html v3.24 → v3.25 (C3): absolute-change alongside trend % on catchment trajectory charts
3. `fdc85bd` — A2 NES share ingest from 2021 TSP T10A+T10B (v2; fraction)
4. `bb21f66` — A2 wire: `populate_service_catchment_cache.py` reads NES; calibration nudge live
5. `49ce9f1` — A2 v3 unit fix: percentage storage; wire divides by 100
6. `d02e26e` — B2: add `sa2_nes_share` to `layer3_apply.py` METRICS
7. `3ddcf18` — C2-NES (data side): register `sa2_nes_share` in 3 registries
8. `7e1ab91` — Doc refresh end-of-session 2026-05-04 (this commit; landed only `CENTRE_PAGE_V1_5_ROADMAP.md` + monolith — the other Tier-2 regens were missing from this commit and are being caught up next session)

**HEAD: `7e1ab91`** (origin/master caught up to HEAD post-commit).

---

## Standards / decisions

**No new STDs locked this session.**

**No new DECs locked this session.**

**STD-37 candidate** banked: "Search project knowledge before probing." The A1 dissolution this session re-discovered a finding already documented in 2026-04-28b status, costing ~30 min. Worth a 30-second STD mint at next consolidation pass.

**Unit-convention scoping check** banked (not yet a STD): For any cross-layer value, the unit at each layer (storage, wire, calibration, render) should be explicit in the scoping note before code. The A2 v2-as-fraction storage was technically correct for the calibration but would have shipped as "0.31%" if C2-NES rendering had landed without unit reconciliation.

**DEC-78 candidate** flagged (not promoted): NES storage convention at SA2 = percentage (0-100) per `census_*_pct` family. Wire boundary divides by 100 before passing to `calibrate_participation_rate()`. Promote formally if A3/A4/A5 (next session ingests) confirm the convention generalises.

---

## Open items summary

See OPEN_ITEMS.md for full text.

**Closed this session:**
- **OI-34** — Absolute change rendered alongside trend % on catchment trajectory charts (commit `f47a0ba`; opened+closed same morning).

**Opened this session:**
- **OI-35** — `layer3_apply.py` wholesale-rebuild bug. Workaround in place; real fix ~0.5 sess.
- **OI-36** — `centre.html` / `centre_page.py` hardcode catchment-position rows. New metrics in `LAYER3_METRIC_META` don't auto-render. Recommended first piece next session. ~0.3 sess.

**Dropped this session:**
- **A1** (CENTRE_PAGE_V1.5_ROADMAP scope) — ABS ERP backward extension. Dissolved by probe trail; ABS source publishes `'-'` for pre-2019 SA2 under-5.

**Status updated this session:**
- **OI-12** — Backup pruning critical at ~8.5 GB cumulative (+2.7 GB today across 5 new backups).

**Carried (unchanged):** OI-01–04, OI-06–10, OI-13–17, OI-19, OI-20–22, OI-24, OI-26, OI-28, OI-31, OI-33.

---

## Doc set

The 2026-04-28 restructure produced the 12-doc set, since extended with `CENTRE_PAGE_V1.5_ROADMAP.md` (2026-05-04). Update history:

- 2026-04-29c+d → 2026-04-30 → 2026-05-03 morning → 2026-05-03 PM → 2026-05-03 evening (V1 ship at `bcdf84c`)
- **2026-05-04 (full day)** — V1.5 scoping pass + C3 ship + A1 dissolution + A2 end-to-end + B2 + C2-NES (data side) + OI-34 closed + OI-35 + OI-36 minted + recovery from layer3_apply wipe.

**STD-35 hygiene note:** End-of-session commit `7e1ab91` landed only `CENTRE_PAGE_V1_5_ROADMAP.md` and the new monolith. The regenerated `PROJECT_STATUS.md` / `ROADMAP.md` / `OPEN_ITEMS.md` did not make it into the commit. **This file (and the matching ROADMAP.md / OPEN_ITEMS.md regens) are the catch-up landing.**
