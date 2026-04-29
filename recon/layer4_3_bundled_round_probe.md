# Layer 4.3 — bundled round (6 items, 2026-04-29 continued)

**Date:** 2026-04-29
**Operator:** Patrick Bell
**Bundle:** UI prominence fix + kinder mirroring + sub-pass 4.3.9 + sub-pass 4.3.7 + sub-pass 4.3.2 probe + sub-pass 4.3.3 probe
**Effort estimate:** ~1.0–1.2 sessions
**Decision drivers:** DEC-74 (perspective toggle) + DEC-75 (visual weight) + DEC-76 (workforce supply context) + Patrick screenshot review of v3.5

---

## Why bundle

Six items across this round at operator request, accepting slightly larger bisect-window risk in exchange for one apply / commit / push cycle instead of six. Items are all renderer-only or read-only Python (probes). No DB mutations. All additive per DEC-11. Bundle structurally low-risk.

Sequencing pass: items are independent. Bundle order is execution-friendly (UI fix and kinder are visible immediately; workforce block is a new section appearing on every page; perspective toggle is dormant infrastructure; probes produce recon-only output). No item depends on or blocks any other.

---

## Items

### 1. UI prominence fix — trend-window % change label and Chart.js tooltip

**Origin:** Patrick screenshot review of v3.5 — "the size of those labels for the changes is not prominent enough in either the hover or the set text." Plus a noted minus-sign rendering issue at small size on dark background.

**Changes (centre.html v3.5 → v3.6):**

- Trend-% label: 11px → 13px; color `--text-mute` → `--text-dim`; `+X.X%` value rendered semibold (font-weight 600 in `var(--text)`); `since YYYY` qualifier stays in `--text-mute`. Result: the headline % reads as headline; the year reads as qualifier.
- Chart.js tooltip: `bodyFont.size` 11 → 12.5; `titleFont.size` 11 → 12. Whole tooltip becomes more readable.
- Unicode minus sign `−` (U+2212) retained — at 13px in `--text-dim` it renders cleanly. The earlier rendering issue was a function of small-size + low-contrast, both of which are now resolved.

No new DEC. Renderer-implementation choice within DEC-73 scope.

### 2. Kinder mirroring (centre page) from operator-page treatment

**Origin:** Operator request — kinder recognition on the centre page should match the rigour of the operator-page treatment, where ACECQA flag and service-name regex are surfaced as two independent signals because they don't always agree.

**Decisions (D1–D4 confirmed):**

| | Decision |
|---|---|
| **D1** | Four-state headline mapping: confirmed_both / confirmed_acecqa / likely_name_only / not_flagged |
| **D2** | **Originally shipped (v3.6):** Render all three rows when there's any signal; hide the entire block only when ACECQA is null AND name doesn't match. **Revised (v3.7, 2026-04-29 continued):** Always render the block. The original gate hid the block on the dominant LDC case (ACECQA null, no name match), which made the kinder check effectively invisible — the not-flagged result is information worth showing. Block now hides only when the entire payload subtree is missing (defensive against pre-v7 payloads). |
| **D3** | DER tooltip on name-match badge shows the regex pattern + the matched substring + a caveat ("name evidence, not an official kinder approval record") |
| **D4** | `kinder_summary.signals` is an open list — future detection methods append entries; renderer reads from the array rather than hardcoding two signals |

**Changes (centre_page.py v6 → v7):**

- New `KINDER_PAT` constant (`re.compile(r'\b(kinder(garten)?|pre-?school)\b', re.I)`). Deliberately duplicated from `operator_page.py` with a comment marking that file as canonical. Pragmatic over a shared utility module.
- `places` block extended:
  - `kinder_approved` — unchanged, OBS, the existing field.
  - `kinder_name_match` — new, DER, with `value` / `matched_text` / `rule` / `pattern` / `caveat`.
  - `kinder_summary` — new, DER, with `state` / `headline` / `any_signal` / `signals[]`. Headline mapping per D1.

**Changes (centre.html v3.5 → v3.6):**

- `_renderKinderBlock(p)` — new function, renders the 3-row composite in a panel-2 background block beneath the long-day-care fact in the Places card. Hidden when ACECQA is null AND name doesn't match.
- The previous single-line `Kinder approved: Yes/No` is removed; the block above replaces it.

### 3. Sub-pass 4.3.9 — Workforce supply context block (DEC-76)

**Origin:** DEC-76. New page-level section alongside Population and Labour Market cards.

**Changes (centre_page.py v6 → v7):**

- New `_build_workforce_supply(conn, state_value)` helper. Returns a section with 4 rows:
  - Child carer vacancy index (ANZSCO 4211) — JSA IVI Step 5c, state-monthly
  - Early childhood teacher vacancy index (ANZSCO 2411) — JSA IVI Step 5c, state-monthly
  - ECEC Award minimum rates — Fair Work, national
  - Three-Day Guarantee policy — national policy fact (Jan 2026)
- The two JSA IVI rows query through a candidate-table-name list (`_IVI_TABLE_CANDIDATES`) tolerantly: if the actual table name in the DB matches one of the candidates AND has the expected column shape, the row goes live with a sparkline; otherwise the row renders as deferred with a "wire-up follow-up" note.
- The ECEC Award row renders deferred with a Fair Work pointer (rates change annually 1 July; ingest is a separate small task).
- The Three-Day Guarantee row renders live with the policy fact (national constant).

**Changes (centre.html v3.5 → v3.6):**

- New `renderWorkforceSupplyCard(centre)` — page-level section with `default open` framing, rendered between Labour Market and QA cards.
- Each row: title + value (latest-or-fact) + state/national stamp + intent copy + optional sparkline (only on live JSA IVI rows). All rows carry the OBS badge; status notes render below the value when the row is deferred.
- Sparklines use the same Chart.js queue pattern as Position-row trajectories — registered in `_CHART_PENDING`, instantiated by `_flushPendingCharts()` after `main.innerHTML` is set.

**Wire-up follow-up:**

This bundle ships the structure with defensive querying. To activate the JSA IVI rows live:

1. Confirm the actual table name in `kintell.db` (likely candidates: `jsa_ivi_state_monthly`, `abs_jsa_ivi_state_monthly`, `jsa_internet_vacancy_index_state_monthly`).
2. If the actual table name isn't in `_IVI_TABLE_CANDIDATES`, add it (one line in centre_page.py).
3. If column names diverge from the probe's expectations (`period`/`period_label`, `vacancy_index`/`ivi`/`value`, `anzsco_code`/`anzsco`, `state`/`state_code`), extend the column-resolution lookups in `_try_query_ivi`.

This wire-up is a ~10-line follow-up sub-pass; not blocking V1.

### 4. Sub-pass 4.3.7 — Perspective toggle infrastructure (DEC-74)

**Origin:** DEC-74. The four catchment ratios (supply_ratio, child_to_place, demand_supply, demand_supply_inv) are reversible pairs that need a per-row toggle to swap between perspectives at render time.

**Status: infrastructure-only in V1.** No metric in the registry currently carries `reversible: true`. The four catchment ratios will arrive with sub-pass 4.2-A.3, at which point the toggle activates per row with no further renderer changes.

**Changes (centre_page.py v6 → v7):**

- `LAYER3_METRIC_META` contract docstring extended to describe four optional fields per DEC-74:
  - `reversible: bool`
  - `pair_with: str` (registry key of inverse metric)
  - `default_perspective: str` ('forward' | 'inverse')
  - `perspective_labels: dict` (toggle button labels)
- `_layer3_position` propagates these fields onto every entry (stub + populated). Default `False` / `None`. The renderer reads `p.reversible` directly without a fallback path.

**Changes (centre.html v3.5 → v3.6):**

- `_PERSPECTIVE_STATE` — module-local memory keyed by metric. No persistence across page loads in V1.
- `_PERSPECTIVE_BAND_COPY_TEMPLATES` — locked band-copy templates per DEC-74, keyed by direction (`high_is_concerning`, `high_is_positive`).
- `_activePerspective(metric, p)` — returns 'forward' | 'inverse'.
- `_togglePerspective(metric, ev)` — flips the state and re-renders via `_LAST_CENTRE`. Same single-shot render path used by the global trend-window bar; clean re-render.
- `_renderPerspectiveToggle(metric, p)` — emits the toggle button pair (Forward / Inverse) on rows with `reversible: true`. Returns empty string for non-reversible rows.
- `_bandCopyForPerspective(metric, p)` — for non-reversible metrics returns `p.band_copy` unchanged; for reversible metrics in inverse perspective returns the locked template for the inverted direction.
- `_renderBandChips` updated to take `(metric, p)` and call `_bandCopyForPerspective` instead of reading `p.band_copy` directly. Both call sites in `_renderFullRow` and `_renderLiteRow` updated.
- Toggle wired into `_renderFullRow` title row alongside the OBS badge. Hidden on non-reversible rows so existing behaviour is unchanged.

### 5. Sub-pass 4.3.2 — SALM LFP at SA2 probe (Thread B)

Read-only Python script + recon artefact template. See `layer4_3_sub_pass_4_3_2_probe.md`. Operator runs the script during apply; pastes output into the artefact; disposition resolves to either an LFP-ingest follow-up (if SALM publishes LFP at SA2) or a permanent LITE classification for the LFP triplet (if not).

### 6. Sub-pass 4.3.3 — NCVER VET enrolments DB-state probe (Thread D)

Read-only Python script + recon artefact template. See `layer4_3_sub_pass_4_3_3_probe.md`. Operator runs the script; pastes output into the artefact; disposition resolves to either an immediate workforce-block wire-up (if NCVER data is already ingested) or a V1.5 enrichment via OI-20 (if not).

---

## Decisions to surface

All confirmed by operator before code. No new decisions surface during implementation.

### Implementation defaults (no operator confirmation needed)

- **Kinder block visual treatment:** panel-2 background (`var(--panel-2)`) with 1px border, 4px radius. Tightly bounded so it reads as a sub-block within the Places card rather than a peer card.
- **Workforce block visual treatment:** standard `op-section` with `note` subhead "state & national signals · default open". Same row separators (1px dashed border-bottom) as Position rows.
- **Workforce sparkline:** 42px height (smaller than Position trajectory's 48–56px), no x-axis labels, no point markers, hover shows period+value via Chart.js native tooltip.
- **Perspective toggle visual treatment:** two `range-btn` buttons separated by `/`, sits in the row title area to the LEFT of the rawValue + OBS badge. Active button has the filled style; click on either flips to that perspective.
- **Probe scripts location:** `recon/probes/` directory. Both scripts are runnable as `python recon/probes/<script>.py` from repo root.

---

## Files touched

| File | Before | After | Change |
|---|---|---|---|
| `centre_page.py` | v6 | v7 | `import re`, `KINDER_PAT` constant, kinder payload extension, `_build_workforce_supply` + helpers + `_IVI_TABLE_CANDIDATES`, perspective fields on `LAYER3_METRIC_META` contract + propagation through `_layer3_position` |
| `docs/centre.html` | v3.5 | v3.6 | UI prominence fix on trend-% label + tooltip; `_renderKinderBlock` + integration into `renderPlacesCard`; `renderWorkforceSupplyCard` + helpers + integration into `render()`; perspective toggle infrastructure + integration into `_renderFullRow` + `_renderBandChips` signature change |
| `recon/probes/probe_salm_lfp_sa2.py` | — | new | SALM LFP probe (read-only) |
| `recon/probes/probe_ncver_vet_enrolments.py` | — | new | NCVER VET enrolments probe (read-only) |
| `recon/layer4_3_sub_pass_4_3_2_probe.md` | — | new | SALM probe recon artefact (template; operator fills in script output) |
| `recon/layer4_3_sub_pass_4_3_3_probe.md` | — | new | NCVER probe recon artefact (template) |
| `recon/Document and Status DB/PROJECT_STATUS.md` | — | — | Centre page section updated, sub-pass table updated, What's Next reflects 3 sub-passes remaining |
| `recon/Document and Status DB/ROADMAP.md` | — | — | §1.3 marks 4.3.7 + 4.3.9 SHIPPED; §1.3 marks 4.3.2 + 4.3.3 PROBE SHIPPED |

---

## Verification plan

### Pre-apply (operator side)

1. Run both probe scripts (Items 5+6) — capture output. Output goes into the two probe recon artefacts.

### Post-apply

1. **Payload smoke-test:** import `centre_page` and call `get_centre_payload(<sid>)`. Confirm:
   - `places.kinder_summary.state` matches the four-state mapping.
   - `places.kinder_name_match.matched_text` is populated when name matches.
   - `workforce_supply.rows` has 4 entries; the JSA IVI rows show `confidence: "deferred"` (likely; actual table name may not be in candidate list yet).
   - Position metrics carry the four perspective fields (all `False` / `None` in V1).

2. **Visual: Places card kinder block.** Open a centre with kinder name match, confirm the 3-row block renders with the correct headline. Open a centre WITHOUT kinder name match and ACECQA flag false — confirm the block is hidden entirely (not just empty).

3. **Visual: Workforce supply context block.** Confirm:
   - The block renders between Labour Market and QA cards.
   - All 4 rows render (deferred or live).
   - Three-Day Guarantee row shows the policy fact.
   - JSA IVI rows show "pending" with status note (assuming wire-up follow-up not yet done).

4. **Visual: trend-% label prominence.** Confirm the label is now visibly larger and the value is bold. Confirm the Chart.js tooltip is more readable on hover.

5. **Visual: perspective toggle dormancy.** Confirm no toggle button appears anywhere (no V1 metric is reversible). Inspect HTML — confirm `_renderPerspectiveToggle` returns empty string everywhere.

6. **Edge: SA2 with SALM-suppressed unemployment.** Confirm the SALM-missing empty-state still renders correctly (Thread A behaviour preserved through the bundle).

---

## Cross-references

- **DEC-74** — Perspective toggle on reversible ratio pairs
- **DEC-75** — Visual weight by data depth
- **DEC-76** — Workforce supply context block
- **DEC-73** — Trajectory window UX (extends with v3.6 prominence fix)
- **DEC-11** — Additive overlay pattern as default
- **OI-06** — LFP source is Census-only (subject of Thread B probe)
- **OI-20** — Workforce supply context enrichments (NCVER bullet subject of Thread D probe)
- `recon/layer4_3_sub_pass_4_3_8_probe.md` — predecessor (intent copy + trend-% display)
- `recon/layer4_3_sub_pass_4_3_2_probe.md` — companion (SALM probe recon)
- `recon/layer4_3_sub_pass_4_3_3_probe.md` — companion (NCVER probe recon)
