# Layer 4.3 sub-pass 4.3.2 — SALM LFP at SA2 probe (Thread B)

**Date:** 2026-04-29
**Operator:** Patrick Bell
**Sub-pass:** 4.3.2 (sixth of nine in re-sequenced Layer 4.3; Thread B from Layer 4.3 design closure)
**Effort:** Probe ~0.1 session (read-only); follow-up ingest ~0.5 session if positive
**Decision drivers:** DEC-75 (visual weight) + OI-06 (LFP source is Census-only, 3 points)

---

## Question

Does ABS / JSA SALM publish labour force participation (LFP) at SA2
level, alongside the existing unemployment series in
`abs_sa2_unemployment_quarterly`?

If yes:
- LFP source upgrades from Census 2021 TSP T33A-H (3 points) to SALM
  quarterly (~60 points across 2010s–2020s).
- LFP triplet (`sa2_lfp_persons` / `_females` / `_males`) promotes
  from LITE → FULL row weight in centre.html.
- The "as at YYYY · static snapshot, no trajectory" stamp drops; the
  trajectory chart returns; cohort histogram returns.
- OI-06 closes.

If no:
- LFP triplet stays at LITE weight permanently. OI-06 stays open as
  tracking-only (no fix path until a different SA2-level LFP source
  is identified).

---

## Probe

Read-only Python script: `recon/probes/probe_salm_lfp_sa2.py`.

Checks:
1. Any table with `lfp` in the name.
2. Any table with `salm` in the name.
3. `abs_sa2_unemployment_quarterly` — schema + period coverage +
   sample row (the LFP data, if it exists, is most likely a sibling
   column in this same table).
4. Any column with `lfp` / `participation` / `labour_force` in its
   name across all tables (catches the sibling-column hypothesis).
5. Provenance rows in `*_ingest_run` tables referencing JSA / SALM.

---

## Findings

**Disposition: CONDITIONAL POSITIVE — defer to V1.5.**

The probe surfaced a more nuanced picture than the binary "SALM publishes LFP at SA2: yes/no" the script was designed to answer. SALM does NOT publish LFP-percent directly at SA2 in the existing ingest, but the SALM source publishes `participation_rate` alongside `unemployment_rate` in the same workbooks, and the existing `abs_sa2_unemployment_quarterly` table already captures `labour_force` (the LFP numerator). The remaining gap is publishing-source-to-DB ingest scope, not source data availability.

### Probe output (run 2026-04-29, on `data/kintell.db`)

```
======================================================================
SALM LFP probe (Thread B) — recon read-only
======================================================================
DB: C:\Users\Patrick Bell\remara-agent\data\kintell.db

──────────────────────────────────────────────────────────────────────
1. Tables with 'lfp' in name (case-insensitive)
──────────────────────────────────────────────────────────────────────
  (none)

──────────────────────────────────────────────────────────────────────
2. Tables with 'salm' in name (case-insensitive)
──────────────────────────────────────────────────────────────────────
  (none)

──────────────────────────────────────────────────────────────────────
3. abs_sa2_unemployment_quarterly — schema + coverage + sample
──────────────────────────────────────────────────────────────────────
  Columns:
    sa2_code: TEXT
    year_qtr: TEXT
    rate: REAL          ← unemployment rate
    count: INTEGER      ← unemployed count
    labour_force: INTEGER

  Total rows: 142,496
  Distinct SA2s: 2,336

  (Probe-script gap: the sample-row + period-coverage step errored
  looking for `period_label`. Actual period column is `year_qtr`. Does
  not affect disposition; lessons-learned for future probes.)

──────────────────────────────────────────────────────────────────────
4. Columns named like LFP/participation across all tables
──────────────────────────────────────────────────────────────────────
  abs_sa2_unemployment_quarterly.labour_force (INTEGER)

──────────────────────────────────────────────────────────────────────
5. JSA / SALM provenance rows in *_ingest_run tables (if any)
──────────────────────────────────────────────────────────────────────
  (Probe-script gap: filter ran on `source` column; actual provenance
  column is `source_label`. No SALM rows surfaced as a result. Does
  not affect disposition; lessons-learned for future probes.)
```

### Operator interpretation

The shape of the finding is "data is published by source, ingest scope didn't capture it" rather than "data not available." Three concrete signals:

1. **`labour_force` column already populated** at SA2 × quarter. That's the numerator of LFP. The denominator (working-age population) is published by SALM in the same workbook tab but wasn't captured in the original ingest.
2. **No table named `*_lfp_*` or `*_salm_*`** — confirms LFP-percent isn't already derived in a sibling table.
3. **SALM as a source publishes `participation_rate` directly** alongside `unemployment_rate` in the workbook. Re-ingesting with extended column scope is straightforward — Step 5b's existing apply pipeline covers it.

So the question reframes from "does SALM publish LFP at SA2?" (answer: yes, via participation_rate) to "is extending the SALM ingest worth a session of work for V1?"

---

## Disposition — defer to V1.5

LFP is a secondary credit signal for the centre page. The dominant demand metrics (under-5 count, births, income trio) all carry rich SA2-level data and Full-weight rendering. LFP's LITE treatment in V1 (3 Census points, decile strip + chips + intent copy + as-at stamp) conveys the SA2 peer position adequately for a credit-lens read.

Promoting LFP-persons from LITE to FULL via SALM-extension would add a trajectory chart + cohort histogram + trend-% label — a real visual upgrade, but on a metric that's not blocking V1 credibility. The ~0.5–0.6 session of work is better deferred and bundled with OI-19's three V1.5 ingests (NES, parent-cohort 25–44, schools), all of which share the "pure deepening" framing.

**SALM-extension follow-up sub-pass, queued for V1.5:**

1. Re-run SALM ingest pulling `participation_rate` column alongside `rate`/`count`/`labour_force` (~0.3 session). Adds an `lfp_persons_pct` column (or similar) to `abs_sa2_unemployment_quarterly`, or a sibling `abs_sa2_lfp_quarterly` table — naming to be decided when the apply lands.
2. Layer 3 banding apply for `sa2_lfp_persons` against state-x-remoteness cohort (~0.2 session). Same cohort definition as `sa2_unemployment_rate` per DEC-54.
3. centre.html: flip `LAYER3_METRIC_META["sa2_lfp_persons"].row_weight` from `lite` to `full`. ~5 lines.
4. centre_page.py: add SALM as the trajectory source for `sa2_lfp_persons` in `LAYER4_TRAJECTORY_SOURCES`. ~5 lines.

**LFP_F and LFP_M (sex-disaggregated) stay LITE permanently in V1.5.** SALM publishes persons-only at SA2; sex disaggregation is Census 2021 TSP T33A-H, structurally 3 points. DEC-61's "do not reconcile cross-product Census rates" framing applies — the persons series moves to SALM-quarterly while the sex split stays Census-3-point. LFP-persons FULL + LFP-F/M LITE on the same card is internally consistent: rich data on overall LFP at SA2, less rich on the sex breakdown.

---

## Cross-references

- **DEC-54** — State-and-remoteness-stratified cohort (would apply to LFP-persons banding)
- **DEC-60** — Female LFP rate at SA2: TSP-derived (LFP_F / LFP_M source unchanged)
- **DEC-61** — Cross-product Census rates: do not reconcile or sum (justifies LFP-persons SALM + LFP_F/M Census split)
- **DEC-75** — Visual weight by data depth (LITE classification origin)
- **OI-06** — LFP source is Census-only (3 points) — updated this session: SALM-extension path documented; deferred to V1.5
- **OI-19** — Layer 4.4 V1.5 ingests; SALM-extension is a natural companion ingest
- `recon/layer4_3_design.md` v1.1 §G5 — Thread B framing

---

## Probe-script lessons learned

The script had two cosmetic gaps that didn't affect the disposition but are worth noting for future probe scripts:

1. Section 3 hard-coded `period_label` as the period column name. The actual column is `year_qtr` — a probe should detect period column name dynamically from `PRAGMA table_info`, not assume a name.
2. Section 5 filtered `*_ingest_run` rows on a column called `source`; the actual provenance column is `source_label`. Same fix — detect from schema, not assume.

Both gaps were also present in the NCVER probe (different manifestation but same root cause). Probe-script convention going forward: schema-discover all column names before query construction.
