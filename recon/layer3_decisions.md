# Layer 3 Decisions (Decision 65 D1–D4)

_Captured: 2026-04-28_
_References: `recon/layer3_precedent_survey.md` (auto-generated evidence)_

This document closes Decision 65. The companion file
`recon/layer3_precedent_survey.md` is the raw evidence (DB scan + repo
keyword scan); this file records the decisions Patrick made on
D1–D4 after reviewing that evidence.

---

## Headline conclusions from the survey

1. **DB-level greenfield.** Zero views, zero `*_band` / `*_percentile`
   tables, zero `NTILE` / `PERCENT_RANK` / `RANK OVER` anywhere in the
   schema. The 9 matched columns are raw ABS classifications
   (`seifa_decile`, `aria_plus`, `remoteness_band`) or placeholders
   with 0 rows (`pricing_tier`, `supply_band`, `seifa_irsd`). No DB
   constraint on Layer 3 schema choice.

2. **Single shipped UI convention to match.** Operator + Catchment
   pages render SEIFA as: *"weighted decile + 1–10 histogram +
   low/mid/high band split."* Verbatim across `docs/operator.html`,
   `docs/_op_chunks/part2.txt`, `docs/_op_chunks/part3.txt`. **Layer 3
   outputs must support this triple (decile, histogram, low/mid/high
   band) for any SEIFA-pattern metric.**

3. **Cohort default already locked.** Decision 54 establishes
   state-x-remoteness as the default. Referenced in
   `layer2_step5b_prime_apply.py`. Status doc Layer 4 design block
   already specifies per-metric overrides (e.g. JSA vacancy =
   "vs national").

4. **Other "score" / "tier" hits are out of scope.**
   - `composite_confidence` (0.0–1.0, thresholds 0.85 / 0.50) →
     entity-resolution domain (`propose_merges.py`).
   - Operator targeting "100-point score, hot/warm tiers" →
     qualitative prioritisation, not peer-cohort percentile.
   - Centre v1 just displays raw SEIFA decile / ARIA label as-is.

5. **No within-cohort percentile or composite has ever been
   computed.** RWCI would be the first.

---

## D1 — Table shape

**DECISION: Option B — long format.**

Schema target:
```
layer3_sa2_metric_banding (
    sa2_code     TEXT NOT NULL,
    metric       TEXT NOT NULL,        -- canonical metric name
    year         INTEGER NOT NULL,     -- vintage year
    cohort_def   TEXT NOT NULL,        -- 'national' | 'state' | 'remoteness' | 'state_x_remoteness'
    raw_value    REAL,                 -- the underlying number
    percentile   REAL,                 -- 0..100, within cohort
    decile       INTEGER,              -- 1..10, within cohort
    band         TEXT,                 -- 'low' | 'mid' | 'high' (or metric-specific)
    PRIMARY KEY (sa2_code, metric, year, cohort_def)
)
```

**Why long over wide:**
- Greenfield — no existing convention to violate.
- Layer 4 design block specifies ~12 distinct percentile/band views
  across Population + Labour cards. Long format absorbs new metrics
  without schema migration.
- Per-metric cohort overrides require `cohort_def` as a row-level
  attribute, not a column suffix.
- Wide mart view can be added at Layer 4 read-time if perf needs it
  (deferred to Layer 4 — no premature optimisation).

**Why include both `percentile` AND `decile`:**
- `decile` directly satisfies the shipped operator/catchment 1–10
  histogram convention.
- `percentile` enables finer-grained displays without a second
  computation pass.
- Both derive from the same underlying rank within cohort.

---

## D2 — RWCI weighting

**DECISION: Option D — defer RWCI to Layer 3b.**

**Why:**
- Status doc principle (line 330): *"No composite scores — every
  number traceable to a labelled source."* RWCI is the first
  composite that violates this, so deserves its own deliberate
  treatment.
- Patrick's iteration posture (recorded below): hard to weight
  inputs sensibly until banding behaviour on individual inputs is
  visible on the UI.
- Layer 3b can be a one-session scope once Layer 3 outputs are
  rendered on Layer 4 and we observe distribution shape.

**Implication for Layer 3 scope:**
- RWCI inputs (occupation knowledge mix, industry knowledge share,
  median employee income) ARE banded by Layer 3 as individual
  metrics — same long-format treatment as everything else.
- Composite RWCI score column / table not built this layer.

---

## D3 — Cohort definitions per metric

**DECISION: state-x-remoteness as default, with explicit per-metric
overrides documented in a config map.**

Per-metric overrides (initial set, from status doc Layer 4 design):

| Metric                         | Cohort                | Source                     |
|--------------------------------|-----------------------|----------------------------|
| SA2 under-5 percentile         | state                 | Status doc line 343        |
| SA2 under-5 growth percentile  | remoteness            | Status doc line 344        |
| SA2 births percentile          | state-x-remoteness    | Default (Decision 54)      |
| SA2 unemployment percentile    | state                 | Status doc line 366        |
| SA2 median income percentile   | remoteness            | Status doc line 367        |
| SA2 LFP-females percentile     | state-x-remoteness    | Status doc line 368        |
| JSA vacancy rate percentile    | national              | Status doc line 370        |

Implementation: a `metric_cohort_map` dict in the Layer 3 apply
script, keyed on canonical metric name, defaulting to
`state_x_remoteness` if absent. The `cohort_def` column stores the
actual cohort used per row, so the choice is auditable from data
alone.

**Why not pure state-x-remoteness for everything:**
- JSA vacancy is genuinely state-bounded (vacancy posted to a state
  market) — national comparison is the meaningful frame.
- Income / unemployment have meaningful state-only or remoteness-only
  cohorts already specified in the shipped Layer 4 design.

---

## D4 — Session scope

**DECISION: Layer 3 minus RWCI.**

In scope for the next 1–1.5 sessions:
- Build `layer3_sa2_metric_banding` table (long format).
- Compute percentile / decile / band for the SEIFA-pattern shipped
  metrics first, to validate against existing operator/catchment UI.
- Then extend to Population (under-5 count, growth, births) and
  Labour (unemployment, income, LFP) metrics per the cohort map
  above.
- Standard 28 pre-mutation inventory beforehand.
- Apply pattern: diag → apply_dryrun → apply → spotcheck (project
  convention).

Out of scope this layer:
- RWCI composite score (Layer 3b).
- Wide mart view for Layer 4 (deferred to Layer 4 read-time work
  if perf needs it).

---

## Iteration posture (Patrick's caveat)

Patrick noted that several of these choices — particularly D2 (RWCI
weighting) and D3 (per-metric cohort definitions) — are difficult to
fully evaluate until banding outputs are visible on the UI in Layer 4.

The decisions above are **deliberately structured to absorb iteration
without schema change**:

- **D1 long format** lets us add or revise metrics, bands, cohorts
  by row insert/update, never by `ALTER TABLE`.
- **D2 deferred RWCI** is a recognition that composite-score weighting
  is best informed by visible behaviour of the inputs.
- **D3 cohort overrides as a config map** means changing a metric's
  cohort is a one-line edit + re-run, not a migration.

Re-runs after Layer 4 reveals banding behaviour are EXPECTED and
designed for — not a sign decisions were wrong.

---

## Next step

1. **Standard 28 — Pre-mutation DB inventory.**
   Refresh `recon/db_inventory.md` to capture the current state
   (post-Step-1b, post-Step-8) before any Layer 3 mutation. Helper:
   re-run `db_inventory.py`.

2. **Layer 3 design / diag artefact.**
   Build `layer3_diag.py` + `recon/layer3_diag.md` documenting:
   - Initial metric set and their source columns/tables
   - Cohort assignment per metric (matching the table in D3 above)
   - Banding cutoff conventions (decile = NTILE 10 within cohort;
     band low = decile ≤ 3, mid = 4–7, high = 8–10 — to be confirmed
     against shipped operator/catchment cutoffs in code review)
   - Expected row counts (~2,450 SA2s × ~10–12 metrics × 1–14 years
     × 1 cohort_def each = upper bound ~400K rows; long-format target)

3. **Layer 3 apply** — `layer3_apply.py` with `--dry-run` and
   `--apply` modes per project convention. Backup + audit_log per
   Standards 8 + 30.

4. **Layer 3 spotcheck** — `layer3_spotcheck.py` validating
   distributions match expected shape (each cohort sums to 100 by
   percentile, each decile bucket has ~10% of rows, no SA2 outside
   any cohort).

---

_End of decisions._
