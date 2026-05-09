# Project Status

*Last updated: 2026-05-09 (commercial repositioning + planning + handover doc set). The on-disk version supersedes the project-knowledge monolith if they disagree.*

## Headline (2026-05-09)

**Project repositioned. Patrick Bell owns the IP. Brand: Novara Intelligence (working).** This session was a planning-only pass — no code changes, no DB mutations. Commercial repositioning locked as DEC-79. Audience expands from Remara-credit-team to broader institutional decision-support market participants (lenders, investors, operators FP+NFP, valuers, property funds, debt providers, advisors). Five new work streams locked into the V1 plan (PRODUCT_VISION.md): A) Educator visa / overseas educator supply, B) NFP perspectives integrated, C) Childbearing-age + marital-status depth, D) PropCo Property Intelligence (V1 premium tier — not V2), E) SA2 Border Exposure V1 proxy. V1 ship target redefined to **~Sept 2026** (3-4 months), incorporating the original V1.0 centre-page tool (already shipped) plus V1.5 ingests + Catchment page + Group page + the five new streams + Excel export framework + brand identity rename pass.

**This session's deliverables (all landed on disk):**
- DEC-79 appended to canonical DECISIONS.md
- New `CLAUDE.md` at repo root (orientation for every future Claude Code session)
- New `PRODUCT_VISION.md` at repo root (strategic frame, audience, 5 streams, V1/V2/V3 horizon)
- ROADMAP.md updated for new V1 horizon and stream sequencing
- OPEN_ITEMS.md updated with OI-NEW-1 through OI-NEW-18 (provenance corrections, risks, brand rename, doc moves, 5 streams, new surfaces, Excel export, institutional readiness)
- 9 memory entries in `~/.claude/projects/.../memory/` (user role, collaboration style, project context, project state, project Remara relationship, no-bash-paths feedback, doc-discipline feedback, extend-don't-sprawl feedback, doc-locations reference)
- `.gitignore` updated for OI-13 (single-? pattern fix) + OI-NEW-9 (recon/patchers_*) + `*.pre_*` patterns

**Operational change locked:** Patrick drives strategy / UI / industry depth / data depth / commercial risk. Claude drives technical architecture / schema / code / build sequencing / doc discipline. Patrick's input on coding architecture is intentionally limited.

**Cross-cutting risks now tracked:** 2026 Census Aug 2026 (SA2 boundary refresh Q3 2027), workforce funding cliff Nov 2026, Strengthening Regulation Bill 2025 (CCS revocation as live credit indicator), Starting Blocks Algolia drift, ABS Community Profiles retirement, "70% break-even" anchor provenance.

---

## Headline (2026-05-05 — preserved for traceability)

**V1.0 is at HEAD `bcdf84c`. V1.5 first piece (OI-36) is at `430009a`.** This session closed OI-36 cleanly: NES row now visible in Catchment Position card across all 3 verification SA2s, plus a generic delta badge on all Lite rows surfacing first-to-last Census-point change ("+9.5pp from 2011 to 2021" on Bayswater NES; "+$291/week from 2011 to 2021" on Bayswater median household income). Three commits this session: doc-set catch-up (`9d49be9`), OI-36 close (`430009a`), and end-of-session doc refresh (this commit landing).

*Note 2026-05-09: "V1" in this 2026-05-05 entry refers to the original V1.0 centre-page credit-decision tool. Per DEC-79 the term V1 has been redefined to the broader Novara Intelligence release targeting ~Sept 2026.*

## Centre page — current state

`centre_page.py` v21 (Python backend) + `centre.html` v3.28 (renderer) + payload schema `centre_payload_v6` (unchanged this session — OI-36 work was render-side only, no payload schema rev).

### Catchment Position card — current shape

| Metric | Weight | Trajectory | Events overlay | INDUSTRY band | About panel | Calibration in DER | NES delta badge |
|---|---|---|---|---|---|---|---|
| `sa2_supply_ratio` | FULL | quarterly per subtype | YES (subtype-matched) | 7 levels | YES | — | n/a |
| `sa2_demand_supply` | FULL | quarterly (cal_rate held) | YES | 4 levels (parallel-framed) | YES | YES | n/a |
| `sa2_child_to_place` | FULL | quarterly (1/supply_ratio) | YES | 5 levels | YES | — | n/a |
| `sa2_adjusted_demand` | FULL | quarterly (cal_rate held) | YES | NO (decile only) | YES | YES | n/a |
| `sa2_demand_share_state` | CONTEXT | n/a | n/a | n/a | n/a | YES | n/a |
| `sa2_nes_share` | LITE | 3 Census points | n/a | n/a | n/a | YES (live nudge) | **YES** |

NES row now rendering correctly across all verification SA2s:
- Bayswater Vic (id=2358 / sa2 211011251): 31.1% (2021), Decile 5 mid, +9.5pp from 2011 to 2021, calibration nudge −0.02 firing
- Bondi Junction-Waverly NSW (id=103 / sa2 118011341): 23.6%, Decile 5 mid, +2.1pp from 2011 to 2021, no nudge
- Bentley-Wilson WA (id=246 / sa2 506031124): 37.6%, Decile 10 high, +Xpp from 2011 to 2021, calibration nudge −0.02 firing

### Delta badge (new this session)

Generic `_renderLiteDelta(p)` helper in centre.html v3.27 + currency-format fix in v3.28. Reads `p.trajectory` and emits a small first-to-last delta badge inside the Lite row template, alongside the existing "as at YYYY" stamp. Unit-aware via `p.value_format`:

- `percent` / `percent_share` → "+9.5pp from 2011 to 2021"
- `currency_weekly` → "+$291/week from 2011 to 2021"
- `currency_annual` → "+$1,234 from 2011 to 2021"
- `ratio_x` → "+0.04× from 2011 to 2021"
- else → plain numeric

Always-show variant (P1). P-2 silent absence for <2 numeric points / unreadable years / zero delta. Affects all Lite rows: NES, LFP triplet, median household income.

**Window-aware variant (P2) declined this session** — operator chose to keep complexity out. Existing `_setTrajectoryRange` doesn't trigger Lite re-render anyway, so window-awareness on Lite rows would need new event-subscription wiring beyond OI-36 scope.

---

## Phase 2.5 — status by layer

| Layer | Description | Status |
|---|---|---|
| 0 / 1 / 2 | Foundations | COMPLETE |
| 2.5 | Catchment cache populator | COMPLETE 2026-04-30 |
| 3 / 4.1 | Layer 3 banding 14 metrics | COMPLETE; **+1 metric (sa2_nes_share, B2 closed 2026-05-04)** |
| 4.2 | Centre page renderer | COMPLETE for V1; **+OI-36 close 2026-05-05** |
| 4.3 | Centre page polish + workforce | COMPLETE |
| 4.4 | V1.5 ingests | A2 done 2026-05-04; A3-A6 + A10 remaining; tracked in CENTRE_PAGE_V1.5_ROADMAP.md |

---

## What's next

**V1 path remaining: ~0 sessions.** No mandatory work.

**V1.5 next-session priority (operator-elevated 2026-05-05):** **A10 + C8 — Demographic Mix bundle (~1.0 sess).** Three Census TSP tables (T07 ATSI, T08 country of birth, T19 single-parent households) all from the same TSP zip already on disk + new Community Profile narrative panel. Closes the Demographic Mix scope question raised during NES integration.

**V1.5 path remaining (~2.7 sess):**
- **A10 + C8** (~1.0 sess) — Demographic Mix bundle (next-session priority)
- **A3, A4, A5, A6** (~1.4 sess) — Phase A core remaining
- **B1, B3, B4, B5** (~0.9 sess) — Phase B core
- **C2-other + C6** (~0.4 sess) — Phase C core remaining

See **CENTRE_PAGE_V1_5_ROADMAP.md** for the canonical V1.5 dependency-ordered queue and **ROADMAP.md** for the parent dependency view.

**Optional housekeeping (low priority, anytime):**
- **OI-12** — DB backup pruning. **CRITICAL** at ~8.5 GB cumulative. Keep policy needs relaxation.
- **OI-35** — `layer3_apply.py` real fix (~0.5 sess).
- **OI-13** — Frontend file backups gitignore tightening (~30 sec; +3 new `pre_oi36*` backups this session).
- **OI-14 / OI-15** — Date parsing + ARIA+ format codebase scans.
- **OI-10** — `provider_management_type` enum normalisation.
- **OI-28** — `populate_service_catchment_cache.py` cosmetic banner (5 sec).
- **STD-37 candidate** — "search project knowledge before probing" mint.
- **Recon probe sweep** — root probes → `recon/probes/`.

---

## Database state

Path: `data\kintell.db` (~565 MB). 36 tables. **`audit_log: 149 rows`** (unchanged this session — OI-36 was renderer-only, no DB mutations).

**No new DB backups this session** (renderer-only work). Cumulative ~8.5 GB across 41+ files unchanged.

`docs/sa2_history.json`: v2 multi-subtype, 13.2 MB, 50 quarters, 1,267 SA2s, 4 subtype buckets. Tracked in git. Unchanged this session.

---

## Git state

V1 ship: `bcdf84c` (2026-05-03 evening).

This session's commits, chronological:

1. `9d49be9` — Catch-up regen of Tier-2 docs to 2026-05-04 EOD (closes STD-35 hygiene gap from `7e1ab91`)
2. `430009a` — OI-36 close: sa2_nes_share renders in Catchment Position card + delta badge on Lite rows (centre.html v3.25→v3.28 + centre_page.py v20→v21)
3. End-of-session doc refresh (this commit, landing now)

**HEAD: `<this commit's sha>`.** Origin/master is at `7e1ab91`; will need a push at end of session.

### centre.html v3.25 → v3.28 sub-history

- v3.25 → v3.26 (commit `430009a` part 1) — added `sa2_nes_share` to `renderCatchmentPositionCard.order` array
- v3.26 → v3.27 (commit `430009a` part 2) — added `_renderLiteDelta(p)` helper + wired into `_renderLiteRow` template
- v3.27 → v3.28 (commit `430009a` part 3) — currency branch fix: matched actual `currency_weekly` / `currency_annual` formats (v3.27 mistakenly matched `currency_aud` which doesn't exist in this codebase)

All three sub-versions in one commit per DEC-22 (verified together).

---

## Standards / decisions

**No new STDs locked this session.**

**No new DECs locked this session.**

Banked items unchanged from 2026-05-04: STD-37 candidate (search project knowledge before probing), DEC-78 candidate (NES storage convention).

---

## Open items summary

See OPEN_ITEMS.md for full text.

**Closed this session:**
- **OI-36** — centre.html / centre_page.py hardcode catchment-position rows. Closed in commit `430009a` (surgical render-order patch + bonus delta badge on all Lite rows).

**Opened this session:** none.

**Carried (unchanged):** OI-01–04, OI-06–10, OI-12–17, OI-19, OI-20–22, OI-24, OI-26, OI-28, OI-31, OI-33, OI-35.

---

## Doc set

The 2026-04-28 restructure produced the 12-doc set, since extended with `CENTRE_PAGE_V1.5_ROADMAP.md` (2026-05-04). Update history:

- 2026-04-29c+d → 2026-04-30 → 2026-05-03 morning → 2026-05-03 PM → 2026-05-03 evening (V1 ship at `bcdf84c`)
- 2026-05-04 (full day) — V1.5 scoping pass + C3 ship + A1 dissolution + A2 end-to-end + B2 + C2-NES (data side) + OI-34 closed + OI-35 + OI-36 minted. End-of-session commit `7e1ab91` landed only `CENTRE_PAGE_V1.5_ROADMAP.md` + monolith.
- **2026-05-05 (this session)** — Catch-up regen of stale Tier-2 docs (`9d49be9`) + OI-36 close (`430009a`) + end-of-session doc refresh (this commit, landing now). Tier-2 docs all current at 2026-05-05 EOD content.
