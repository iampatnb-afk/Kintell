# Visual consistency audit — five-page review

**Date:** 2026-04-28
**Trigger:** Centre page Layer 4.2-B trajectories shipped as bespoke SVG; user
flagged they don't match the existing industry/dashboard chart aesthetic.
**Scope:** All five live HTML pages — `centre.html`, `operator.html`,
`review.html`, `dashboard.html`, `index.html` (the industry page).

---

## 1. Two design systems coexist

The repo runs two parallel visual systems. Until today this was hidden because
the earlier consistency probe was scoped to centre/operator only. Both pages
share Palette A wholesale, so the probe came back clean — but it missed that
two of the five pages use a different system.

### System A — "operator family" (Palette A, bespoke SVG, inline styles)
- `centre.html`
- `operator.html`
- `review.html`

CSS variables (18 tokens, identical across the three files):
```
--accent: #4a9eff      --panel: #1a1f26        --green: #4ade80   --red: #f87171
--text:   #e6e8eb      --panel-2: #232933      --green-bg          --red-bg
--text-dim: #9aa4b1    --panel-3: #2a313c      --amber: #fbbf24   --grey
--text-mute: #6b7684   --border: #2d343f       --amber-bg          --purple, --purple-bg
--bg: #0f1419
```

Chart-rendering: **inline SVG / inline styles**. operator.html SEIFA histogram
is hand-built SVG. centre.html v3 trajectory is the same. No Chart.js
dependency.

### System B — "dashboard family" (Palette B, Chart.js, canvas-based)
- `dashboard.html`
- `index.html` (the industry page)

CSS variables (16 tokens, different set):
```
--accent: #3d7eff      --surface: #181c26      --bg: #0f1117
--accent2: #00c9a7     --surface2: #1e2333     --text: #e8eaf0
--hot: #e05c3a         --warm: #d4890a         --watch: #5a6480
--fgc: #9b59b6         --muted: #8890a8        --border: #2a2f3f
--display: 'Playfair Display', serif          --font: 'DM Sans', sans-serif
--mono: 'DM Mono', monospace                   --radius: 10px
```

Chart-rendering: **Chart.js 4.4.0 from CDN**. Helpers `makeDataset()`,
`makeLine()`, `trimNulls()`, `makeOpts()`, plus custom plugins
`makeCompactPlugin()` (compact ▲▼ event-tick markers) and `makeFullPlugin()`
(annotated combined chart with hover). Multi-coloured palette per series:
`#3d7eff` blue, `#00c9a7` teal, `#d4890a` amber, `#e05c3a` red,
`#9b59b6` purple.

### Why two systems

Best guess from the timeline:
- `dashboard.html` (16 Apr) and `index.html` (28 Apr) were built first as
  the "industry intelligence" surface — Chart.js was the natural choice
  for trend rendering at scale.
- `operator.html` v6→v8 (25-26 Apr), `review.html` (22 Apr), and
  `centre.html` (this session, 26-28 Apr) were built as the
  "drilldown / detail" surface — bespoke SVG and inline styles fit the
  decile-strip / fact-row idiom better than canvas-based Chart.js.

Neither choice is wrong. The split is between **trend visualisation** (where
Chart.js wins) and **dense fact / decile / chip-strip displays** (where
inline SVG wins). The problem is the boundary between them isn't crisp on
the centre page, which has both.

---

## 2. Concrete chart primitives shipped today

### System A primitives (operator/centre/review)
| primitive | file | function | what it does |
|---|---|---|---|
| Decile strip (10 cells, gradient) | centre.html | `_renderDecileStrip` | "you are here" on a 1–10 scale |
| Cohort histogram (20 bins, raw_value) | centre.html | `_renderCohortHistogram` | distribution shape with self-bin marked |
| Trajectory sparkline / dot trajectory | centre.html | `_renderTrajectory` | per-metric historical series — **bespoke SVG, my v3 work** |
| SEIFA portfolio histogram | operator.html | inline JS | distribution of operator's centres across SEIFA deciles |
| Decile-style band chips | centre.html, operator.html | `_renderBandChips`, `.chip` | low/mid/high copy chips |
| Fact rows with km-badges | all three | `.fact` + `renderBadge` | label / value / OBS-DER-COM affordance |

### System B primitives (industry / dashboard)
| primitive | file | function | what it does |
|---|---|---|---|
| Trend line chart | dashboard.html, index.html | `makeDataset` + `chart-services` etc. | quarterly history of a measure |
| Multi-series stacked / line | both | `makeDataset` (multiple) | NQS distribution over time, state share over time |
| Per-quarter event markers | index.html | `makeCompactPlugin` / `makeFullPlugin` | ▲ centre opened / ▼ centre closed in that quarter |
| Per-SA2 supply-demand chart | index.html | `chart-supply-demand` (line 1089) | places-per-100 under-5 over time |
| Per-SA2 catchment combined chart | index.html | `chart-catch-combined` (line 2760) | income + population + supply ratio overlaid |

### The supply-ratio direction note exists already

`index.html` line 2763:
> "A rising supply ratio indicates increasing competition pressure, not
> opportunity."

This is the same convention we discussed in chat. It's already shipped on
the industry page. Centre and operator pages need to match this language
when they render supply ratio.

---

## 3. The trajectory misalignment, explicitly

The bespoke SVG sparkline I wrote in centre.html v3:

- Different palette tokens (Palette A vs Palette B)
- Different stroke colour (`var(--accent)` = `#4a9eff` vs `index.html` uses
  multi-colour-per-series)
- Different background (`rgba(74,158,255,0.12)` fill vs `rgba(0,201,167,0.08)`
  for the under-5 chart on index.html)
- Different rendering tech (SVG path vs Chart.js canvas)
- No event-marker overlay (`makeCompactPlugin` ▲▼ ticks not present)
- Year labels rotated incorrectly (the "2 0 2 0 stack" you saw)

User's reaction was correct: they should look the same as
`chart-supply-demand` / `chart-catch-combined` on index.html.

---

## 4. Proposed alignment — three options

### Option 1: Centre page adopts System B for trends only (recommended)

**What changes:**
- centre.html v3 trajectory replaced with Chart.js.
- `<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>` added to centre.html.
- `_renderTrajectory()` becomes a Chart.js `<canvas>` element with
  `makeLine()` / `makeDataset()` matching index.html's style.
- Stroke colour per metric matches the industry page's convention
  (e.g. `#00c9a7` for under-5, `#3d7eff` for income, `#e05c3a` for
  supply ratio when Pass 4.2-A lands — same colours as `chart-catch-combined`).
- `makeCompactPlugin` (▲▼ event ticks) lifted as-is to surface centres
  added/removed in the SA2 over the same timeline.

**What stays:**
- All the System A decile-strip / fact-row / band-chip / km-badge primitives.
- Palette A everywhere else on centre.html.

**Effort:** ~0.5 sessions to swap `_renderTrajectory` for a Chart.js-based
implementation. Cohort histogram stays as bespoke SVG (Chart.js bar charts
are heavier than needed for a 30px shape-indicator).

**Why recommended:** The trend-rendering decision is genuinely better with
Chart.js. The decile-strip and chip primitives are genuinely better with
inline SVG. The boundary is clean — trend charts use Chart.js, position
indicators use SVG. Easy to maintain and easy to explain.

**Edge case:** Chart.js uses Palette B colours in System B. Importing it onto
a Palette A page means the chart strokes use #00c9a7 etc., but the surrounding
panel uses Palette A colours. This is fine — Chart.js charts read as
embedded "industry-style" mini-charts inside a System A page, which is how
the industry page also embeds them inside its own panels.

### Option 2: Whole-repo migration to one design system

Pick A or B, retire the other. Repaint 2-3 pages either way.

**Effort:** 1-2 sessions for whichever direction. Palette migration plus
chart-tech migration on the migrating side.

**Recommendation against:** doesn't pay back. The two systems serve different
purposes (drilldown detail vs trend intelligence) and the visual divergence
is justifiable when the page-purpose differs. Whole-repo migration would be
~10× the work of Option 1 for marginal congruence gain.

### Option 3: Keep bespoke SVG on centre.html, just visually-match Chart.js

Re-style the existing SVG sparklines to look like Chart.js output —
same palette, same stroke width, same event-marker convention.

**Effort:** ~0.3 sessions.

**Recommendation against:** lots of low-grade work to mimic something we
could just import. And we'd have to maintain "Chart.js-shaped SVG" code
forever as Chart.js evolves.

---

## 5. Separately — supply ratio direction convention

Lock as a working standard:

> **Supply ratio direction (credit lens).** From the perspective of a
> centre operator or operator-buyer, a high supply ratio is concerning
> (saturated catchment, lower fill, higher competition). A low ratio is
> positive (undersupplied, opportunity). This is the inverse of the
> family/policymaker perspective (high ratio = good access for children).
>
> **In the codebase:** `direction = "high_is_concerning"` on
> `LAYER3_METRIC_META.supply_ratio` (and any sibling ratio metrics).
> Band-copy text:
> - low band: "undersupplied catchment — opportunity"
> - mid band: "balanced supply"
> - high band: "saturated catchment — competition risk"
>
> **Already shipped** as a hover note on `index.html:2763`:
> *"A rising supply ratio indicates increasing competition pressure, not
> opportunity."* — extend this language convention to centre.html and
> operator.html when they render supply ratio.

This has implications for *every* metric where direction is non-obvious:
- `unemployment_rate` — already flagged `high_is_concerning` in
  centre_page.py LAYER3_METRIC_META.
- `competitor_density` — will be `high_is_concerning` (Pass 4.2-A).
- `new_competitor_12m` — will be `high_is_concerning`.
- `ccs_dependency_pct` — likely `high_is_concerning` from a fee-pricing view.

**Proposed working standard (new):** *"Every metric carries an explicit
direction marker (`high_is_positive` | `high_is_concerning`). The default
visual treatment is direction-agnostic (no red/green valence in cells —
single-hue gradient only). Direction lives in band-copy text only.
For metrics where the convention disagrees with a naive read of the
number (supply ratio, unemployment rate), the band-copy must explicitly
restate the direction."*

---

## 6. Recommended sequence

If we accept Option 1:

1. **Layer 4.2-B-fix (this session if you want):**
   1.1. Pull Chart.js into `centre.html`.
   1.2. Replace `_renderTrajectory` with a `makeLine`-backed Chart.js
        implementation matching the index.html visual style.
   1.3. Keep `_renderCohortHistogram` and `_renderDecileStrip` as
        bespoke SVG (correct call — they're position indicators, not trends).
   1.4. Visually QA against service 246; commit as Layer 4.2-B-fix.
2. **Pass 4.2-A** — catchment data on the centre page. The same
   Chart.js primitive then renders supply-ratio history / competitor-count
   history alongside the existing trend charts. Layer 4.2-A's Catchment
   Metrics card should **lift `chart-catch-combined`-style overlays
   wholesale** rather than build new ones — this is the chart you said
   "looks right" on the industry page.
3. **Cross-page hygiene** — out of session scope, but flag for backlog:
   - `catchment_html.py` "n/a" → "—" (carried from earlier).
   - operator.html SEIFA histogram could optionally migrate to Chart.js
     bar chart in a future pass; not urgent, the current SVG version
     looks right in System A.

---

## 7. Decisions requested

**E1 — Adopt Option 1 (Chart.js on centre.html for trends only)?** Recommended.

**E2 — Adopt the supply-ratio direction working standard from §5?**
Recommended.

**E3 — Land §6.1 in the current session, or stop here and resume next session?**
Roughly 0.5 session to swap the trajectory renderer; the decile strip
gradient + cohort histogram + the cohort-scope-in-title patches all
remain shipped and don't get re-touched.

After E1/E2/E3 close, implementation moves.
