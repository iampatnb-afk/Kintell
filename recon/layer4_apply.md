# Layer 4 — apply log (NOW + POSITION pass)

**Date:** 2026-04-28
**Inputs:** `recon/layer4_design.md` v2 (decisions D1/D2/D3 closed),
`recon/layer4_design_probe.md`, `recon/layer4_consistency_probe.md`.

## 1. Scope of this pass

This pass implements the **NOW + POSITION** bands of the Population and
Labour-market cards. The TRAJECTORY band ships as a documented placeholder
in both cards, awaiting a follow-up pass that extends the payload with
historical reads from `abs_sa2_*` source tables.

**Why the split.** TRAJECTORY needs 5–10 years of raw historical values per
metric per SA2, plus client-side sparkline rendering — meaningful new payload
size and new JS rendering. Shipping NOW+POSITION first lets us iterate on the
visual treatment (per the "we'll know once we see it on the UI" posture)
without coupling that feedback loop to TRAJECTORY's data plumbing.

## 2. What changed

### 2.1 `centre_page.py` — v2 → v3 (additive only)

New constants near the top of the file:

| constant | purpose |
|---|---|
| `RA_BAND_SHORT_LABELS` | maps `sa2_cohort.ra_band` 1..5 → "Major Cities" .. "Very Remote" |
| `STATE_SHORT_LABELS` | "New South Wales" → "NSW" etc. for cohort phrases |
| `COHORT_LABEL_TEMPLATES` | one phrase template per `cohort_def` |
| `LAYER3_METRIC_META` | display / direction / value_format / source / band_copy for 12 metrics |
| `POSITION_CARD_ORDER` | stable display order within each card |

New helpers (placed just before `get_centre_payload`):

| helper | role |
|---|---|
| `_confidence_for_cohort_n(n)` | encodes the D1 rule: `<10` → `insufficient`, `<20` → `low`, else `normal`, `None` → `unavailable` |
| `_build_cohort_label(cohort_def, cohort_row)` | renders e.g. "vs other Major Cities SA2s in NSW" |
| `_layer3_position(con, sa2_code)` | reads `layer3_sa2_metric_banding` + `sa2_cohort`, returns `{population: {...}, labour_market: {...}}` |

Modification to `get_centre_payload`:
- 1 new line in the body — call `_layer3_position(conn, r.get("sa2_code"))`
- 1 new key in the payload — `payload["position"] = position`
- `schema_version` bumped from `centre_payload_v1` to `centre_payload_v3`

`_commentary_lines` is **not** modified — Phase 7 (commentary engine) is the
formal home for Position interpretive text. The Position card renders its
own band-copy inline.

### 2.2 `docs/centre.html` — v1 → v2 (additive only)

Three new render functions added between `renderCommentary` and `render()`:

| function | purpose |
|---|---|
| `_formatPositionValue(p)` + `_formatPositionPeriod(p)` | private helpers, format raw_value per `value_format` and period per `year`/`period_label` |
| `_renderDecileStrip(decile)` | 10-cell horizontal "you-are-here" strip; all cells `--panel-2` background, only the SA2's cell carries `--accent` outline (truly neutral palette per design §11.2) |
| `_renderBandChips(p)` | low/mid/high chip strip with band-copy text; the SA2's-band chip gets `--text` + `--accent` border emphasis |
| `renderPositionRow(metric, p)` | the row primitive: NOW value (with OBS badge) + headline + decile strip + band chips + DER + COM badges. Branches on `p.confidence` (deferred / unavailable / insufficient / low / normal) |
| `renderPopulationCard(centre)` | wraps Population NOW+POSITION + TRAJECTORY placeholder |
| `renderLabourMarketCard(centre)` | wraps Labour market NOW+POSITION + TRAJECTORY placeholder |

Modification to `render()`:
- Two new lines in `main.innerHTML`: `${renderPopulationCard(centre)}` and
  `${renderLabourMarketCard(centre)}`, slotted between the
  `renderCatchmentCard` / `renderTenureCard` row and the `renderQaCard` call.

**Zero new CSS classes.** All new styling is inline (per design §11.3 — matches
the operator.html SEIFA-histogram convention). The 18 Palette A tokens are the
only colour source.

### 2.3 What deliberately did NOT change

- `_commentary_lines` — Phase 7 problem.
- `renderCatchmentCard` (the existing single-value SEIFA display) — kept as-is
  per design §8.3.
- `catchment_html.py:240` "n/a" string — flagged in design §8 as future hygiene,
  out of scope here.
- The 18 CSS variables in `centre.html` — closed set, no additions.

## 3. Visual QA — recommended SA2 sample

Five SA2s from `recon/layer3_spotcheck.md` with deliberately varied profiles.
For each, the operator should pick any one active service in the SA2 and load
`docs/centre.html?id=<service_id>` to eyeball the rendered Population +
Labour-market cards.

To find a service in each SA2, copy/paste this into a Python REPL or save as
a one-shot:

```sql
-- in sqlite3 data/kintell.db
SELECT service_id, service_name, suburb, sa2_code, sa2_name
  FROM services
 WHERE sa2_code IN (?, ?, ?, ?, ?)
   AND is_active = 1
 GROUP BY sa2_code
 ORDER BY sa2_code;
```

with the five SA2 codes from the spotcheck:

| SA2 | spotcheck profile | what to verify on the rendered page |
|---|---|---|
| Banksmeadow (NSW Major Cities) | mid-decile income, healthy LFP | most metrics rendering as `normal` confidence, `high` band on income |
| Alderley (QLD Major Cities) | high-income, advantaged | high-band copy on income trio reads "price-tolerant" |
| Hughesdale (VIC Major Cities) | high LFP, mid income | LFP triplet renders consistently; cohort phrase reads "vs other Major Cities SA2s in Vic" |
| Braidwood (NSW Outer Regional) | thin cohort possible on state_x_remoteness | watch for `low` confidence pill or `insufficient` suppression |
| Norfolk Island (Other Territories) | extreme synthetic SA2; many metrics likely missing | most rows render as `unavailable` (em-dash); deferred slots show "(coming next)" |

Sanity-check items:

1. The decile-strip cells are all the same neutral tone — no red/green
   valence. The SA2's cell is the only one with the `--accent` outline.
2. `unemployment_rate` (where high=concerning) has the same neutral cell
   colours as `under5_count` (where high=positive). The semantic flip lives
   only in the band-copy chip text ("tight labour market" vs "loose labour
   market — fee-sensitivity flag").
3. OBS badges on raw values show the metric's specific source (e.g. "ABS SALM
   SA2 (abs_sa2_unemployment_quarterly)" for unemployment, "ABS Births at SA2
   (abs_sa2_births_annual)" for births). DER badges on the decile strip show
   the cohort_def + cohort_key. COM badges on the band-copy chip show the
   `LAYER3_METRIC_META` rule reference.
4. The TRAJECTORY placeholder appears at the bottom of both cards in italic
   `--text-mute`, matching the existing Catchment-block "Will show:" idiom.
5. Em-dash `—` for any missing values, never "n/a".

## 4. Smoke test before opening the browser

Run the centre_page.py CLI directly to confirm the payload includes the new
`position` block before testing the rendered UI:

```powershell
$env:PYTHONIOENCODING = "utf-8"
python centre_page.py 1 | Select-String -Pattern '"position"' -Context 0,3
```

Expected: a JSON snippet showing `"position": {` followed by `"population":`.
If the output shows `"position": {"population": {}, "labour_market": {}}`,
the helper ran but the SA2 has no Layer 3 rows — pick a different
`service_id` known to live in a populated SA2.

## 5. Limitations / next-pass items

Carried into the next Layer 4 pass:

- **TRAJECTORY band** — placeholder only. Needs payload extension (e.g.
  `payload["trajectory"]`) sourced from `abs_sa2_*` historical reads, plus
  client-side sparkline rendering. Estimated 0.5 sessions.
- **`sa2_under5_growth_5y`** — deferred Layer 3 metric. Position slot
  reserved with `confidence='deferred'` ("coming next" placeholder). Adding
  this is ~30 lines in `layer3_apply.py` + a re-run.
- **`jsa_vacancy_rate`** — deferred. State-level read computed at Layer 4
  read time (no Layer 3 row needed). Estimated 0.25 sessions.
- **Commentary integration** — Position payload is now structured to feed the
  Phase 7 commentary engine when that ships. Out of scope here.
- **`catchment_html.py` n/a → em-dash hygiene** — flagged in design §8.6.
