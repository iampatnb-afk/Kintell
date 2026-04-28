# Layer 4.2 — Centre Page Design (trajectory + histograms + catchment)

**Status:** pre-work artefact. No code yet. Decisions in §6 must be closed before
implementation.
**Inputs:** `recon/layer4_2_probe.md`; the shipped Layer 4 v2 + 4.1 in
`centre_page.py` and `docs/centre.html`; `module2b_catchment.py`,
`catchment_html.py`, the empty `service_catchment_cache` schema.

---

## 1. Scope

Four elements, one design doc, **two implementation passes**:

| element | pass | data prerequisite |
|---|---|---|
| Trajectory band — historical sparklines / dot trajectories | 4.2-B | none (reads existing `abs_sa2_*` tables) |
| Cohort-distribution histogram per metric | 4.2-B | none (reads existing `layer3_sa2_metric_banding`) |
| Gradient strip (single-hue blue ramp) | 4.2-B | none (pure CSS) |
| Catchment data on centre page (supply ratio, competitor density) | 4.2-A | **`service_catchment_cache` must be populated first** (Layer 2.5 work) |

Pass 4.2-B ships first. The row primitive `renderPositionRow` absorbs three
elements at once because they all touch the same row, and shipping them
separately would mean three rounds of visual review on the same component.
Pass 4.2-A follows once the catchment cache is built.

---

## 2. Pass 4.2-B — trajectory + cohort histogram + gradient strip

### 2.1 What the row looks like

Each Position row currently renders (Layer 4 v2 + 4.1):

```
[title (vs cohort-short)]                              [value (period) OBS]
                              Decile X · band · n=N
                            [10-cell decile strip]
                            [low / mid / high chips]
                                              [DER] [COM]
```

After 4.2-B, each row renders:

```
[title (vs cohort-short)]                              [value (period) OBS]
[trajectory sparkline / dot trajectory]
                              Decile X · band · n=N
                       [cohort-distribution histogram]
                          [10-cell gradient strip]
                            [low / mid / high chips]
                                              [DER] [COM]
```

Three new visual elements stacked between the value line and the band chips.
Total row height ~1.5x current, but each element earns its space.

### 2.2 Trajectory — sparkline vs connected-dot

The probe (§C) confirmed actual data depth per metric:

| metric | source | points | period | render style |
|---|---|---:|---|---|
| sa2_under5_count           | abs_sa2_erp_annual              | 6  | 2019-2024 (3 NULLs in 2011/2016/2018) | dot trajectory |
| sa2_total_population       | abs_sa2_erp_annual              | 6  | 2019-2024 (3 NULLs)                   | dot trajectory |
| sa2_births_count           | abs_sa2_births_annual           | 14 | 2011-2024                             | sparkline      |
| sa2_unemployment_rate      | abs_sa2_unemployment_quarterly  | 61 | 2010Q4-2025Q4                         | sparkline      |
| sa2_median_employee_income | abs_sa2_socioeconomic_annual    | 5  | 2018-2022                             | dot trajectory |
| sa2_median_household_income| abs_sa2_socioeconomic_annual    | 3  | 2011, 2016, 2021                      | dot trajectory |
| sa2_median_total_income    | abs_sa2_socioeconomic_annual    | 5  | 2018-2022                             | dot trajectory |
| sa2_lfp_persons            | abs_sa2_education_employment_annual | 3 | 2011, 2016, 2021                  | dot trajectory |
| sa2_lfp_females            | abs_sa2_education_employment_annual | 3 | 2011, 2016, 2021                  | dot trajectory |
| sa2_lfp_males              | abs_sa2_education_employment_annual | 3 | 2011, 2016, 2021                  | dot trajectory |

**Sparkline** (≥10 points): smooth line, no point markers, area fill at low
opacity, end-point dot, value+period tooltip on hover. Births and unemployment
use this.

**Dot trajectory** (≤6 points): individual dots connected by thin line, year
labels under each dot, value tooltip on hover. The visual difference is
deliberate — it tells the reader "we have a few snapshots, not a continuous
series."

Both elements: ~24px high, full row width, x-axis implicit (no labels for
sparklines except hover; year labels for dot trajectories).

### 2.3 Cohort-distribution histogram

The mini-histogram shows the cohort's distribution shape on this metric, with
the SA2's position marked.

**Read pattern.** New helper `_cohort_distribution(con, metric, cohort_def, cohort_key)`:

```sql
SELECT raw_value, decile
  FROM layer3_sa2_metric_banding
 WHERE metric     = ?
   AND cohort_def = ?
   AND cohort_key = ?
 ORDER BY raw_value
```

Returns `~80-500` rows depending on cohort size. Computed at render time
(no payload precompute — Layer 5 territory if perf becomes an issue).

**Bin count.** 10 bins, decile-aligned. Each bin = one decile of the cohort.
Bin height = count of SA2s in that decile (always ~10% of cohort, by
definition of NTILE(10), so bars are ~equal height — and that's the point: a
flat histogram tells the reader "deciles are evenly populated, this is a
peer-position scale, not a value-distribution scale"). Marker shows the
SA2's bin.

**Wait — is the histogram even useful then?** Yes, but differently than I'd
first assumed. Because Layer 3 deciles are NTILE-based, the "cohort
distribution" by decile is always uniform. So a 10-bin histogram of the
**decile distribution** is uninformative. What's actually informative is the
**raw_value distribution** — i.e. how clumpy/skewed the underlying values are
in this cohort. For income, raw values cluster heavily at low-mid range and
trail to a long high tail. For LFP, raw values are roughly normal. That
shape varies by metric and is the genuinely new information.

So: **20-bin histogram of raw_value, equal-width bins from cohort min to
cohort max,** with the SA2's bin highlighted. This shows skew, modality, and
the SA2's position within the actual value distribution rather than the
artificially-uniform decile distribution.

**Visual.** ~30px high, full row width, faint blue (`--accent` at 15%
opacity) bars, the SA2's bin at full `--accent`. No axis labels (the cohort
size and min/max could go in the DER tooltip). Just shape.

**Placement.** Above the decile strip. Reads top-to-bottom as "where the
cohort sits in absolute value" → "where the cohort sits in decile bands."

### 2.4 Gradient strip — single-hue blue ramp

Currently every cell shares `--panel-2`; only the SA2's cell carries
`--accent` outline. The gradient ramp adds a duller version of the underlying
colour so the eye reads low→mid→high at a glance, without ever implying valence.

**Implementation.** Single-hue blue ramp, fade from cooler to warmer
**lightness**, not hue:

```
deciles 1-3 (low):   background: rgba(74,158,255,0.06)
deciles 4-6 (mid):   background: rgba(74,158,255,0.13)
deciles 7-10 (high): background: rgba(74,158,255,0.20)
```

(`74,158,255` = `--accent` decomposed.) Rule of thumb: bottom band ~6%, top
band ~20% — visible gradient at a glance, dull enough not to compete with the
SA2's full-saturation cell.

The SA2's cell stays as is: `border: 2px solid var(--accent)`,
`background: rgba(74,158,255,0.10)` overridden by the gradient, plus the
bright outline. Will need to test that the outline still pops against
the densest gradient tone — likely fine, but worth eyeballing on metrics
where the SA2 sits in deciles 7-10.

### 2.5 Payload changes (centre_page.py)

Each Position row entry gains two new fields:

```python
"trajectory": [
    {"period": 2019, "value": 1082},
    {"period": 2020, "value": 1087},
    {"period": 2021, "value": 1072},
    # ...
],
"trajectory_kind": "annual" | "quarterly",
"cohort_distribution": [
    {"bin_min": 12.5, "bin_max": 15.0, "count": 28, "is_self": false},
    {"bin_min": 15.0, "bin_max": 17.5, "count": 47, "is_self": true},
    # ... 20 bins
],
```

Both fields are populated only for `confidence in {normal, low}`. For
`insufficient` / `unavailable` / `deferred`, both are omitted (and the row
renders as it does today).

New helpers in `centre_page.py`:

- `_metric_trajectory(con, sa2_code, metric_name) -> list[dict]` — reads the
  metric's source table for the SA2, returns the historical series.
- `_cohort_distribution(con, metric, cohort_def, cohort_key, n_bins=20)` —
  reads the cohort's raw_values from `layer3_sa2_metric_banding`, bins them.

These slot into `_layer3_position`, which now does one extra read per metric
(for trajectory) and one cohort-level read (for histogram). Performance
budget: 10 metrics × 2 extra reads = ~20 extra indexed queries per centre
render. Still O(ms).

A new constant `LAYER3_METRIC_TRAJECTORY_SOURCE` maps each Layer 4 metric to
its (table, value_col, period_col, filter_clause, kind). Already inventoried
in the probe.

### 2.6 Render changes (centre.html)

Three new private helpers in the JS:

- `_renderTrajectory(p)` — branches on `p.trajectory_kind` and
  `p.trajectory.length` to pick sparkline vs dot trajectory. SVG, ~24px high.
- `_renderCohortHistogram(p)` — SVG, ~30px high, 20 bars.
- `_renderDecileStrip(decile)` — gets a one-line gradient ramp added inline.

`renderPositionRow` slots them in: trajectory above the decile strip, then
the histogram above the strip, then the strip with gradient. Roughly:

```js
${trajectoryHtml}                  // NEW
<div>${headlineHtml}</div>
${cohortHistogramHtml}             // NEW
${_renderDecileStrip(decile)}      // GRADIENT NOW
${_renderBandChips(p)}
```

No new CSS classes. All inline styles, consistent with the existing primitive.

---

## 3. Pass 4.2-A — catchment data on centre page

### 3.1 The blocker — `service_catchment_cache` is empty

Probe §B.1 confirms: the table exists with a clean schema (17 columns
including `supply_ratio`, `supply_band`, `competing_centres_count`,
`ccs_dependency_pct`), but row count = 0. The note on the placeholder
already says "awaiting Tier 3 ingest" — that's the work we have to do.

### 3.2 Pre-pass — catchment cache build (Layer 2.5)

Before any centre-page rendering work for catchment data, the cache must
be populated. This is its own apply pass with full Layer-2 ceremony.

**Inputs:**
- `services` table (18,223 active services with sa2_code now correct after
  Step 1c)
- `abs_sa2_erp_annual` (under-5 + total population at SA2)
- `abs_sa2_socioeconomic_annual` (median income at SA2)
- `abs_sa2_unemployment_quarterly` (latest quarter)
- `services.seifa_decile` (existing column)
- Existing computation logic in `module2b_catchment.py`:
  - `compute_supply_and_nfp` — per-SA2 supply ratio
  - `enrich_lead_catchment` — per-service catchment block

**Per-service computation:**

| target column | source / formula |
|---|---|
| sa2_code, sa2_name | from services |
| u5_pop | latest non-null `under_5_persons` from abs_sa2_erp_annual |
| median_income | latest non-null `median_employee_income_annual` from abs_sa2_socioeconomic_annual |
| seifa_irsd | services.seifa_decile (passthrough) |
| unemployment_pct | latest quarter's `rate` from abs_sa2_unemployment_quarterly |
| supply_ratio | (sum of approved_places of LDC services in same SA2) / u5_pop × 100 |
| supply_band | low (<15) / mid (15-25) / high (>25) — from `module2b_catchment.supply_tier` |
| supply_ratio_4q_change | difference vs 4 quarters ago (deferred — annual data only, can't compute quarterly delta yet — leave NULL) |
| is_deteriorating | derived — true iff supply_ratio_4q_change indicates new entrants > births trend (deferred until 4q_change is computable) |
| competing_centres_count | count of OTHER active LDC services in same SA2 (excluding this service) |
| new_competitor_12m | count of LDC services in same SA2 with `approval_granted_date` within 12 months (computed from `services.approval_granted_date`) |
| ccs_dependency_pct | derived from median_income + IRSD via `estimate_ccs_rate` in module2b_catchment.py |
| as_of_date | computation timestamp |

**Decision needed (D4 below):** "competing centres" defined as same-SA2.
Alternative would be within X km radius. Same-SA2 is the natural definition
given everything else here is SA2-keyed; leave radius-based for a future
enhancement if useful.

**New script:** `layer2_5_catchment_cache_apply.py`. Same Layer 2 ceremony
as Step 1c (preflight, dry-run/apply modes, backup, transaction, audit_log,
invariants). Probably 1.0 sessions to build + dry-run + review + apply.

### 3.3 Centre page — what catchment data renders

Once the cache is populated, the centre page extends the existing
`renderCatchmentCard` to render four new metrics, each with the same
treatment as Position rows (value + cohort histogram + decile strip + band
copy):

| metric | source | cohort_def | direction |
|---|---|---|---|
| Supply ratio (places per 100 under-5) | service_catchment_cache.supply_ratio | state_x_remoteness | high=competition-positive (low=undersupplied = opportunity) |
| Competitor density (centres in SA2) | service_catchment_cache.competing_centres_count | state_x_remoteness | high=concerning (more competition) |
| New competitor 12m | service_catchment_cache.new_competitor_12m | state_x_remoteness | high=concerning |
| CCS dependency | service_catchment_cache.ccs_dependency_pct | state_x_remoteness | high=concerning |

These are catchment-keyed (per-SA2), but the value is service-specific
(competing-centres count excludes self). They join Layer 3 banding through
a new `layer3_catchment_metric_banding` table — small, ~4 metrics ×
2,473 SA2s = ~10,000 rows, decile/band the same way as Layer 3.

That's a Layer 3.x extension before Pass 4.2-A can render. Sequence is
therefore:

1. **Layer 2.5 catchment-cache build** (~1.0 sessions)
2. **Layer 3.x catchment metric banding** (~0.4 sessions, mirrors Layer 3
   exactly, just different metrics)
3. **Pass 4.2-A render extension to centre page** (~0.6 sessions)

Total Pass 4.2-A: ~2.0 sessions. **Sequence will be re-confirmed after
Pass 4.2-B ships and is reviewed visually.**

### 3.4 Catchment placement on the centre page

Two options:
- (a) Extend the existing `renderCatchmentCard` (currently shows SEIFA +
  ARIA + SA2 only) to add the four catchment metrics
- (b) New `renderCatchmentMetricsCard` after `renderCatchmentCard`

**Decision needed (D5 below).**

### 3.5 What's deliberately NOT in scope for either pass

- **Layer 5** — pre-computed POSITION cache. Trajectory + histogram reads
  are O(ms); precompute only if QA shows perf drift.
- **Operator-page catchment summary** — the "operator's centres vs all
  centres in the same area" thing you mentioned. Out of scope for Layer 4.2;
  add to backlog as Layer 4.3 or Layer 5 work.
- **Quality + ownership history card** — separate backlog item.
- **Daily rate / vacancy slot reservation** — separate backlog item.

---

## 4. Open data quality — `service_catchment_cache` columns we can't fully populate

The probe-derived inventory shows two cache columns we'll **leave NULL** in the
first build:

- `supply_ratio_4q_change` — needs at least 4 quarters of supply-ratio
  history. Population is annual, so quarterly delta is computable only
  going forward (we'd populate this column starting 4 quarters after the
  cache is first built, or backfill from any historical
  `service_catchment_cache_history` we don't yet have).
- `is_deteriorating` — derived from the above.

UI behaviour for NULL: render as "—" with a small COM note explaining the
deferral. Same convention as the existing "(coming next)" placeholders.

---

## 5. Effort estimate

| pass | step | sessions |
|---|---|---:|
| 4.2-B | trajectory + histogram + gradient strip in centre_page.py + centre.html | 1.0 |
| 4.2-B | visual QA on the 5 sample SA2s + service 246 | 0.2 |
| 4.2-B | commit + push | 0.05 |
| 4.2-A | layer2_5_catchment_cache_apply.py (probe + diag + dry-run + apply) | 1.0 |
| 4.2-A | layer3_x_catchment_metric_banding (mirror Layer 3 pattern) | 0.4 |
| 4.2-A | centre.html catchment-metric rendering | 0.5 |
| 4.2-A | visual QA + commit | 0.2 |
| **Total** | | **3.4** |

Spread across multiple sessions. Pass 4.2-B is ~1.25 sessions; Pass 4.2-A is
~2.1 sessions and gated on cache build.

---

## 6. Decisions to close

### D1 — Sparkline vs dot-trajectory threshold

Where's the cutoff between sparkline (smooth line) and dot trajectory
(dots + connecting line)?

**Question:** ≥10 points = sparkline, <10 = dot trajectory? Or different cut?

**Recommendation: ≥7 points = sparkline, <7 = dot trajectory.** Reasoning:
under-5 + total population have 6 dense points; pushing them to dot
trajectory honestly signals "annual snapshots" rather than implying
continuous series. Births (14) and unemployment (61) are clearly
sparklines. Income (5) and LFP (3) are clearly dot trajectories. The
threshold of 7 puts the dense-but-short metrics in the dot bucket, which
is more honest.

### D2 — Cohort histogram bin count + alignment

**Question:** 10 bins (decile-aligned) or 20 bins (raw_value range,
equal-width)?

**Recommendation: 20 bins, raw-value range, equal-width.** Reasoning:
explained in §2.3 — decile-aligned is uniform by definition and
uninformative; raw-value bins surface skew/modality, which is the new
information.

### D3 — Cohort histogram placement

**Question:** Above or below the decile strip?

**Recommendation: above the decile strip.** Reads top-to-bottom: trajectory
(over time) → cohort distribution (in absolute value) → decile strip (in
relative bands) → band chip (interpretive).

### D4 — Competitor density definition

**Question:** "Competing centres" = same-SA2 / within X km / within ABS
catchment polygon?

**Recommendation: same-SA2 (excluding self).** Consistent with everything
else here being SA2-keyed. Radius-based is more accurate but adds
GeoPackage compute to every Layer 2.5 build. Future enhancement.

### D5 — Catchment metrics placement on centre page

**Question:** Extend existing `renderCatchmentCard` or new
`renderCatchmentMetricsCard`?

**Recommendation: new `renderCatchmentMetricsCard`** placed after the
existing Catchment card. Reasons: existing Catchment card is small (SEIFA +
ARIA + SA2, all single values, no peer-position structure). The new
metrics need the full Position-row treatment (trajectory + histogram +
strip + chips). Mixing them creates visual confusion. Two cards keeps each
one's purpose clear: "Catchment context" (where this centre sits) vs
"Catchment metrics" (how this catchment performs).

---

## 7. Implementation sequence (after decisions close)

1. Pass 4.2-B implementation:
   1.1. `centre_page.py` — `_metric_trajectory`, `_cohort_distribution`,
        `LAYER3_METRIC_TRAJECTORY_SOURCE` constant, payload extension.
   1.2. `docs/centre.html` — `_renderTrajectory`, `_renderCohortHistogram`,
        gradient on `_renderDecileStrip`, slot into `renderPositionRow`.
   1.3. Visual QA on service 246 (Bentley WA — should now show WA cohorts).
   1.4. Visual QA on Banksmeadow / Alderley / Hughesdale / Braidwood / Norfolk Island.
   1.5. Commit "Layer 4.2-B: trajectory + cohort histogram + gradient strip".
   1.6. Push.

2. Pass 4.2-A implementation (separate session, after Pass 4.2-B review):
   2.1. `layer2_5_catchment_cache_apply.py` — diag → dry-run → apply.
   2.2. `layer3_x_catchment_metric_banding.py` — apply.
   2.3. `centre_page.py` — extend payload with `catchment_metrics` block.
   2.4. `docs/centre.html` — `renderCatchmentMetricsCard`.
   2.5. Visual QA + commit.

---

## 8. Reply requested

For each of D1–D5, either confirm the recommendation or amend it.
After they close, Pass 4.2-B implementation starts.
