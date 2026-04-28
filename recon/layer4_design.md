# Layer 4 — Centre Page v2 Design (v2)

**Status:** pre-work artefact, written before any code generation (Decision 65 precedent).
**Inputs:** `recon/layer4_design_probe.md`, `recon/layer4_consistency_probe.md`,
the CENTRE-LEVEL PANEL DESIGN block in `remara_project_status_2026-04-28.txt`,
and the shipped operator SEIFA primitive (`operator_page.py:720–774` +
`docs/operator.html:2056–2148`).
**Out of scope here:** any code change. Layer 4 implementation begins after this doc.
**Decisions closed:** D1 = (a) suppress; D2 = `LAYER3_METRIC_META` in `centre_page.py`,
neutral palette; D3 = direct read.
**v2 changes vs v1:** added §11 Consistency Inheritance derived from the consistency
probe; tightened §5 colour-palette sub-question to a truly neutral cell tone after
seeing what Palette A actually offers; added a hygiene follow-up in §8 for the
`n/a` vs em-dash inconsistency in `catchment_html.py`.

---

## 1. Existing surface — what we're building on

### 1.1 `centre_page.py` (16.7 KB, 11 functions)

The file is organised by suffix convention — `_compute_*` (DER/OBS), `_qa_scores`
(OBS), `get_centre_payload` (entry), `_commentary_lines` (COM). Layer 4 should
preserve this shape.

**Banding touchpoint = `get_centre_payload`, lines 242–405.**

The probe found only three banding-adjacent keyword hits in the whole file:

| line | what it is |
|---|---|
| 45  | comment about ARIA+ band labels |
| 145 | docstring on `_compute_remoteness` |
| 363 | comment marker `# --- CATCHMENT block (SEIFA + ARIA) ---` inside `get_centre_payload` |

Layer 4 adds a sibling block:

```
# --- CATCHMENT block (SEIFA + ARIA) ---           <-- existing
# --- POSITION block (Layer 3 banding) ---         <-- NEW
```

The new block calls one helper `_layer3_position(con, sa2_code)` that does a
single indexed read against `layer3_sa2_metric_banding` and returns the
structured payload that `docs/centre.html` will render.

### 1.2 `docs/centre.html` (28 KB, 888 lines)

JS-rendered with template literals — same idiom as operator.html, not Jinja.
Card-class element count is 0; the page uses an h3-section idiom. Existing h3
sections in document order:

```
NQS Rating
Places & Service Type
Catchment              <-- SEIFA single-value lives here (renderCatchmentCard)
Quality Assessment Areas
Tenure
```

Proposed v2 section order:

```
NQS Rating
Places & Service Type
Catchment              (existing — SEIFA single-value stays)
Population             NEW — Now / Trajectory / Position
Labour market          NEW — Now / Trajectory / Position
Quality Assessment Areas
Tenure
```

Now/Trajectory/Position is a **within-card** structure, not a page-level reorg.

### 1.3 The SEIFA primitive — visual reuse target

**Python (`operator_page.py:720–774`):** `_seifa_band(decile)` (cuts at ≤3, ≤6,
else); builds `seifa_block` with `weighted_decile`, `histogram`, `band_counts`,
`band_places`, `populated_count`, `total_services`, `source`.

**JS (`docs/operator.html:2056–2148`, function `renderCatchment`):**
- h3 headline `Portfolio catchment profile <span class="note">SEIFA · places-weighted</span>`
- `.fact` row: `Weighted SEIFA decile`
- 1–10 horizontal histogram with per-bar tooltip `Decile X: N centres`
- low/mid/high band-split chips
- "Will show:" placeholder when not populated

**Adaptation problem.** At operator level the histogram is a distribution across
many centres. At centre level we have one SA2, one metric, one decile. A literal
decile-count histogram would be 9 empty bars + 1 bar of height 1 — degenerate.

**Adapted primitive — "you-are-here decile strip":** 10 cells representing
deciles 1..10, the SA2's cell highlighted with `var(--accent)`, headline reading
e.g. "**Decile 6** · mid · vs other Major Cities NSW (cohort n=155)", low/mid/high
band chips below carrying the **interpretation copy** per metric (per §5). Same
JS function shape as operator's `renderCatchment` SEIFA block. Concrete cell
styling defined in §11.2.

---

## 2. Layer 4 read pattern

### 2.1 Direct read, no joined view

```sql
SELECT metric, year, period_label, cohort_def, cohort_key, cohort_n,
       raw_value, percentile, decile, band
  FROM layer3_sa2_metric_banding
 WHERE sa2_code = ?
```

23,946 rows total, indexed on `(sa2_code)`. Returns ~10 rows per centre in <1ms.
No joined view needed. Trajectory sparklines read raw values directly from
source tables (`abs_sa2_*`) at render time per Decision 68.

### 2.2 Helper shape (no code yet — just the contract)

`_layer3_position(con, sa2_code) -> dict`:
- runs the point-read above
- runs a sibling read against `sa2_cohort` for `state_name`, `ra_name`, `ra_band`
- returns a dict keyed by metric name; each value contains: `decile`, `band`,
  `percentile`, `raw_value`, `cohort_n`, `cohort_def`, `cohort_key`,
  `cohort_label` (e.g. "Major Cities of NSW"), `confidence` (`normal` |
  `low` | `insufficient` — see §3)
- never raises; returns `{}` if SA2 has no Layer 3 rows (synthetic SA2)

`get_centre_payload` adds `payload["position"] = {"population": {...},
"labour_market": {...}}`.

### 2.3 Performance — sanity check

23,946 rows × ~70 bytes ≈ 1.6 MB. With `idx_l3_sa2`, point lookups are O(log n).
**Layer 5 precompute is unnecessary for V1.**

---

## 3. cohort_n display rule (D1 closed: suppress)

| cohort_n | confidence | display |
|---|---|---|
| ≥ 20 | normal       | full decile-strip + headline + band copy |
| 10–19 | low         | full decile-strip + "low confidence" hint pill in headline (`--amber-bg`) |
| < 10  | insufficient | suppress decile-strip; show "*insufficient peer cohort (n=X)*" in `--text-mute` italic |

### 3.1 Actual incidence (probe-derived)

| metric                       | cohort_def           | rows | cn<10 | cn 10-19 | normal |
|---|---|---:|---:|---:|---:|
| sa2_under5_count             | state                | 2347 | 4   | 0   | 99.8% |
| sa2_unemployment_rate        | state                | 2336 | 0   | 0   | 100%  |
| sa2_median_employee_income   | remoteness           | 2398 | 0   | 0   | 100%  |
| sa2_median_household_income  | remoteness           | 2411 | 0   | 0   | 100%  |
| sa2_median_total_income      | remoteness           | 2402 | 0   | 0   | 100%  |
| sa2_total_population         | state_x_remoteness   | 2418 | 49  | 62  | 95.4% |
| sa2_births_count             | state_x_remoteness   | 2450 | 46  | 62  | 95.6% |
| sa2_lfp_persons              | state_x_remoteness   | 2401 | 49  | 62  | 95.4% |
| sa2_lfp_females              | state_x_remoteness   | 2386 | 49  | 62  | 95.4% |
| sa2_lfp_males                | state_x_remoteness   | 2397 | 48  | 62  | 95.4% |

Suppression only bites on state_x_remoteness metrics, ~2% of rows each.

---

## 4. Position card structure (Now / Trajectory / Position bands)

### 4.1 Population card

```
Population
├── NOW
│   • Under-5 population, latest year (raw + period)
│   • Total population, latest year
│   • Births, latest year
├── TRAJECTORY
│   • Under-5 5y CAGR + 10y sparkline
│   • Births trend sparkline
│   • Total population sparkline
└── POSITION (Layer 3)
    • Under-5 vs same state                  [under5_count, cohort_def=state]
    • Births vs same state-x-remoteness      [births_count, cohort_def=state_x_remoteness]
    • Total population vs same state-x-rem.  [total_population, cohort_def=state_x_remoteness]
    • Under-5 growth vs same remoteness      [DEFERRED — sa2_under5_growth_5y not in Layer 3]
```

### 4.2 Labour market card

```
Labour market
├── NOW
│   • SA2 unemployment rate, latest quarter
│   • SA2 median household income (equivalised)
│   • SA2 median employee income
│   • SA2 median total income excl. govt pensions
│   • State educator vacancy count + State ECT vacancy count
├── TRAJECTORY
│   • Unemployment 12-month delta + 36-month sparkline
│   • Income trio decadal trajectory
│   • LFP triplet decadal trajectory
│   • JSA vacancy 12-month trend
└── POSITION (Layer 3)
    • Unemployment vs same state             [unemployment_rate, cohort_def=state]
    • Median employee income vs same remot.  [median_employee_income, cohort_def=remoteness]
    • Median household income vs same remot. [median_household_income, cohort_def=remoteness]
    • Median total income vs same remoteness [median_total_income, cohort_def=remoteness]
    • LFP persons vs same state-x-remoteness [lfp_persons, cohort_def=state_x_remoteness]
    • LFP females vs same state-x-remoteness [lfp_females, cohort_def=state_x_remoteness]
    • LFP males vs same state-x-remoteness   [lfp_males, cohort_def=state_x_remoteness]
    • JSA vacancy rate vs national           [DEFERRED — JSA is state-level]
```

10 of 12 Position rows are direct Layer 3 reads. Two deferred rows ship as
"_(coming next)_" placeholders in the same visual style.

---

## 5. Per-metric metadata (D2 closed: `LAYER3_METRIC_META`)

Lives in `centre_page.py` as the `LAYER3_METRIC_META` constant (NOT in DB —
keeps Std 32 clean). Each entry carries:

1. **display** — human label
2. **direction** — `high_is_positive` | `high_is_concerning`
3. **cohort phrase template** — e.g. `"vs other {ra_name} SA2s in {state_name}"`
4. **band-copy triple** — three short interpretive labels (low/mid/high)

Proposed v1 copy:

| metric | display | direction | low band copy | mid band copy | high band copy |
|---|---|---|---|---|---|
| sa2_under5_count            | Under-5 population        | high=demand-positive  | thin demand pool     | average demand pool      | deep demand pool |
| sa2_total_population        | Total population          | high=demand-positive  | small SA2            | mid-sized SA2            | large SA2 |
| sa2_births_count            | Births (leading demand)   | high=demand-positive  | low forward demand   | average forward demand   | strong forward demand |
| sa2_unemployment_rate       | Unemployment rate         | **high=concerning**   | tight labour market  | typical labour market    | loose labour market — fee-sensitivity flag |
| sa2_median_employee_income  | Median employee income    | high=price-tolerant   | price-sensitive      | typical                  | price-tolerant |
| sa2_median_household_income | Median household income   | high=price-tolerant   | price-sensitive      | typical                  | price-tolerant |
| sa2_median_total_income     | Median total income       | high=price-tolerant   | price-sensitive      | typical                  | price-tolerant |
| sa2_lfp_persons             | Labour force participation| high=demand-positive  | low workforce demand | typical workforce demand | high workforce demand |
| sa2_lfp_females             | LFP — females             | high=demand-positive  | low                  | typical                  | high (dual-income signal) |
| sa2_lfp_males               | LFP — males               | high=demand-positive  | low                  | typical                  | high |

The **direction** column flips the rendering for `unemployment_rate` only
through copy — the visual treatment stays neutral per D2 (concrete cell tones
in §11.2).

---

## 6. Suggested payload shape

```
payload["position"] = {
  "population": {
    "under5_count": {
      "display": "Under-5 population",
      "raw_value": 208.0, "year": 2024, "period_label": null,
      "decile": 1, "band": "low", "percentile": 7.12,
      "cohort_def": "state", "cohort_key": "1", "cohort_n": 625,
      "cohort_label": "other SA2s in NSW",
      "direction": "high_is_positive",
      "band_copy": "thin demand pool",
      "confidence": "normal"
    },
    "births_count":  { ... },
    "total_population": { ... },
    "under5_growth_5y": { "status": "deferred" }
  },
  "labour_market": {
    "unemployment_rate": { ..., "direction": "high_is_concerning", ... },
    "median_employee_income":  { ... },
    "median_household_income": { ... },
    "median_total_income":     { ... },
    "lfp_persons": { ... },
    "lfp_females": { ... },
    "lfp_males":   { ... },
    "jsa_vacancy_rate": { "status": "deferred" }
  }
}
```

---

## 7. Decisions — closed

- **D1: suppress for cn<10**, "low confidence" pill for cn 10–19, normal for cn≥20.
- **D2: `LAYER3_METRIC_META` in `centre_page.py`, neutral palette** (no
  red/green valence in cells; semantics carried in band-copy text only). See
  §11.2 for concrete tones.
- **D3: direct read** for trajectory; Layer 5 precompute deferred unless QA
  shows perf drift.

---

## 8. Open follow-ups (not blocking)

1. **`sa2_under5_growth_5y`** — descoped from Layer 3 (~30 lines in
   `layer3_apply.py` + re-run when needed). Position payload reserves the slot.
2. **JSA vacancy rate Position row** — JSA is state-level; compute per-state
   rank at Layer 4 read time (lighter than adding to Layer 3).
3. **Existing Catchment-block SEIFA stays.** Layer 4 does not duplicate it in
   the Position section.
4. **Commentary integration** — Phase 7 (commentary engine) is the formal home;
   Layer 4 leaves `_commentary_lines` untouched and carries band-copy in the
   Position card itself.
5. **Cross-tab stitching.** The Position payload shape can drive a future
   "Centres in this SA2" cross-link from catchment.html. Out of Layer 4 scope.
6. **Hygiene: `n/a` vs em-dash inconsistency.** `catchment_html.py:240` uses
   "n/a"; centre.html and operator.html use em-dash `—`. Layer 4 adopts em-dash
   per §11.6. Fix `catchment_html.py` in a future hygiene sweep, not as part
   of Layer 4.

---

## 9. Effort estimate

| step | effort |
|---|---|
| `_layer3_position` helper + `LAYER3_METRIC_META` constant | 0.3 sessions |
| `get_centre_payload` extension + payload contract | 0.2 sessions |
| docs/centre.html v2 — `renderPopulationCard` + `renderLabourMarketCard` + `renderPositionRow` | 0.5 sessions |
| Local QA against 5 sample SA2s (Banksmeadow, Alderley, Hughesdale, Braidwood, Norfolk Island) | 0.2 sessions |
| **Total Layer 4 implementation** | **1.0–1.5 sessions** |

Pre-work (this artefact + the two probe scripts) closes at ~0.3 sessions.

---

## 10. Next action

Implementation, in this order:

1. `centre_page.py` extension — `_layer3_position` helper, `LAYER3_METRIC_META`
   constant, POSITION block in `get_centre_payload`.
2. `docs/centre.html` v2 — add `renderPopulationCard`, `renderLabourMarketCard`,
   `renderPositionRow` per §11 conventions. Wire into the `render()`
   orchestration after `renderCatchmentCard`, before `renderQaCard`.
3. Visual QA on five sample SA2s from `recon/layer3_spotcheck.md`.
4. `recon/layer4_apply.md` write-up + commit + push.
5. Pause for "we'll know once we see it on the UI" review (per
   layer3_decisions.md iteration posture) before Layer 5.

---

## 11. Consistency Inheritance (from `recon/layer4_consistency_probe.md`)

This section locks the visual and structural conventions Layer 4 must inherit
from what is already shipped. Anything not listed here stays as it is in
docs/centre.html.

### 11.1 Palette — Palette A wholesale

The repo has two CSS palettes. Probe-confirmed:

- **Palette A** — `docs/centre.html`, `docs/operator.html`, `docs/review.html`
  (18 variables, **identical sets** in all three files).
- **Palette B** — `docs/dashboard.html`, `docs/index.html` (16 different variables;
  different surface).

Layer 4 lives on centre.html and uses **Palette A only**. The 18 tokens:

```
--accent: #4a9eff      headline / SA2-decile-cell highlight
--text: #e6e8eb        primary value text
--text-dim: #9aa4b1    cohort label / contextual text
--text-mute: #6b7684   "/10" suffix, italic null indicators
--bg: #0f1419          page background (do not override)
--panel: #1a1f26       outermost card
--panel-2: #232933     decile-strip cell background
--panel-3: #2a313c     nested panels
--border: #2d343f      cell separators
--green / --green-bg   reserved (see §11.2 — NOT used in decile-strip)
--red / --red-bg       reserved (see §11.2 — NOT used in decile-strip)
--amber / --amber-bg   low-confidence hint pill (cohort_n 10–19)
--purple / --purple-bg reserved
--grey                 reserved
```

**No new CSS variables.** Layer 4 is restricted to these 18 tokens.

### 11.2 Decile-strip cell colours — truly neutral per D2

The strip is direction-agnostic. Cell tone communicates **structure** (which
cells fall in which band) but never **valence** (good/bad). All 10 cells share
the same neutral background; band membership shows through subtle band-divider
treatment and the band-copy chips below.

```
all cells (1..10)         background: var(--panel-2)
                          border: 1px solid var(--border)
                          height: 28px

band dividers             between cells 3↔4 and 6↔7:
                          margin-left: 4px (slight gap)

SA2's decile cell         border: 2px solid var(--accent)
                          box-shadow: inset 0 0 0 1px var(--accent)
                          (raised z-index optional)
```

Below the strip, three band-copy chips (low / mid / high). The SA2's-band chip
gets `color: var(--text)` emphasis; the other two are `color: var(--text-dim)`.

This keeps `unemployment_rate` visually identical to `under5_count` — the
interpretive flip lives entirely in band-copy text per §5.

`--green/-bg` and `--red/-bg` stay reserved for explicit warning treatments
(e.g. cn<10 suppression notice could optionally use `--red-bg`, but neutral
italic is preferred per §11.6). `--amber-bg` is the cohort_n confidence pill.

### 11.3 Reused CSS classes — already shipped, do not redefine

```
.fact          existing label/value primitive in centre.html and operator.html.
               Markup: <div class="fact"><span class="k">label</span><b>value</b></div>
               Layer 4 NOW values use this exact pattern.
               (Operator uses it for "Weighted under-5 population" at line 2167;
                centre.html uses it for "SEIFA decile" at line 722.)

.chip          band-split chip primitive. Layer 4 band-copy chips reuse it.
.chip-inline   inline variant for tighter layouts.
.brand-chip    operator-brand variant — irrelevant to Layer 4.
```

The decile-strip cells are new visual elements but use **inline styles only**
(consistent with `docs/operator.html:2098` SEIFA histogram bars, which also
use inline styles). **No new class definitions added to docs/centre.html.**

### 11.4 JS function naming — match shipped centre.html convention

Existing centre.html renderers (probe-confirmed):
`renderHeader`, `renderNqsCard`, `renderPlacesCard`, `renderCatchmentCard`,
`renderQaCard`, `renderTenureCard`, `renderMethodologyLegend`,
`renderCommentary`, `renderBadge`.

Layer 4 adds three:

```
renderPopulationCard(centre)        Population NOW + TRAJECTORY + POSITION
renderLabourMarketCard(centre)      Labour market NOW + TRAJECTORY + POSITION
renderPositionRow(position, meta)   shared decile-strip primitive (one per metric)
```

Slot order in centre.html `render()` orchestration (insertion points marked):

```
renderHeader()
renderNqsCard()
renderPlacesCard()
renderCatchmentCard()              // existing — keeps SEIFA single-value
renderPopulationCard()             // NEW (Layer 4)
renderLabourMarketCard()           // NEW (Layer 4)
renderQaCard()
renderTenureCard()
renderMethodologyLegend()
renderCommentary()
```

### 11.5 Methodology badges — every value gets one

centre.html attaches a methodology badge to every rendered value via
`renderBadge("OBS"|"DER"|"COM", { source: "..." }, true)`. Layer 4 honours
the convention exactly:

| value type | badge | source string template |
|---|---|---|
| NOW raw values (under-5 pop, raw income, raw unemployment, ...) | OBS | `"ABS SA2 ERP / SALM / EE DB / Births"` (per metric) |
| TRAJECTORY (5y CAGR, sparkline, decadal trajectory) | DER | `"Computed from <source-table>"` |
| POSITION (decile / band / percentile) | DER | `"layer3_sa2_metric_banding (cohort: <def>)"` |
| Band-copy interpretive text | COM | `"Rule-based, see LAYER3_METRIC_META"` |

This is not optional — it's the M3 methodology convention shipped across
operator.html and centre.html for every shipped value.

### 11.6 Null / missing-value display

centre.html line 722 establishes the convention: em-dash `—` (U+2014) for
missing values, **NOT** the string "n/a". Layer 4 follows this.

The cohort_n suppression message renders as `*insufficient peer cohort (n=X)*`
in italic, colour `var(--text-mute)`.

(Note: `catchment_html.py:240` currently uses "n/a" — inconsistent. Flagged
in §8 as a future hygiene task; out of scope for Layer 4.)

### 11.7 Number formatting — use shipped helpers

centre.html and operator.html both import `fmtN()`. Layer 4 uses it for all
numeric formatting. No new formatters.

```
raw counts (under-5, total pop, births)   fmtN(value)
percentages (unemployment_rate, lfp_*)    `${value.toFixed(1)}%`
currency (income trio)                    `$${fmtN(value)}`
percentile display                        `${pct.toFixed(0)}th percentile`
```

### 11.8 What NOT to introduce

- No new CSS variables (Palette A is a closed set).
- No new top-level CSS classes in centre.html.
- No new JS files or modules — all renderers live inline in `docs/centre.html`
  per the existing pattern.
- No "n/a" strings.
- No background colours outside Palette A.
- No font-size jumps that diverge from the operator/centre h3-section idiom.
- No alternative number formatters (use `fmtN`).
- No bypassing `renderBadge` — every rendered value carries OBS / DER / COM.
- No valence colour in decile-strip cells (red for low, green for high) —
  semantics live in band-copy text only.
