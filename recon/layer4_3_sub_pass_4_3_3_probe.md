# Layer 4.3 sub-pass 4.3.3 — NCVER VET enrolments DB-state probe (Thread D)

**Date:** 2026-04-29
**Operator:** Patrick Bell
**Sub-pass:** 4.3.3 (seventh of nine in re-sequenced Layer 4.3; Thread D probe from Layer 4.3 design closure)
**Effort:** Probe ~0.1 session (read-only); follow-up wire-up ~0.2 session if positive
**Decision drivers:** DEC-76 (Workforce supply context block) + OI-20 (workforce supply enrichments) + DEC-36 (NCVER stays at industry view) [conditionally superseded if probe positive]

---

## Question

Is NCVER VET enrolments data for childcare-relevant qualifications
(CHC30121 Cert III ECEC, CHC50121 Diploma ECEC) already present in
`kintell.db` from earlier panel3 / Industry-view work?

If yes:
- NCVER promotes immediately to a V1 row in the Workforce supply
  context block (DEC-76) — joins JSA IVI 4211 + 2411, ECEC Award
  rates, Three-Day Guarantee.
- DEC-36 (NCVER stays at Industry view) is partially superseded:
  the data was held at industry view because the *granularity*
  (state/remoteness) wasn't catchment-specific; if it's already
  ingested at SA4+remoteness, the centre-page rendering becomes a
  no-cost addition that clears OI-20's NCVER bullet.

If no:
- NCVER stays in OI-20 as a V1.5 enrichment.
- The probe-then-ingest path becomes a future sub-pass; not blocking
  V1 ship.

---

## Probe

Read-only Python script: `recon/probes/probe_ncver_vet_enrolments.py`.

Checks:
1. Tables matching keywords: ncver, vet, tva, training, qualification,
   enrolment, completion.
2. For each matching table: schema + sample of first 3 rows.
3. Any rows referencing CHC30121 / CHC30113 / CHC50121 / CHC50113
   across ALL tables (catches cases where the table name doesn't
   match keywords but the qualification codes are present).
4. Geographic resolution columns (sa4 / sa2 / remoteness / state)
   in candidate tables — determines whether centre-page rendering
   is feasible at the state-level (same as JSA IVI rows) or finer.
5. Provenance rows in `*_ingest_run` tables referencing NCVER / VET /
   TVA.

The qualification-transition caveat (DEC-24): single-year YoY against
2023 is misleading because the CHC30121/CHC50121 codes superseded the
113 codes during 2022–2024. Multi-year baselines or rolling averages
are the correct comparison. The probe reports raw counts only;
interpretation handles the transition.

---

## Findings

**Disposition: NEGATIVE WITH REASONING — DEC-36 stands; data exists but stays at Industry view.**

The probe confirmed NCVER VET enrolments data is already in `kintell.db` from earlier panel3 work. The data IS available; the disposition is editorial, not technical.

### Probe output (run 2026-04-29, on `data/kintell.db`)

```
======================================================================
NCVER VET enrolments probe (Thread D) — recon read-only
======================================================================
DB: C:\Users\Patrick Bell\remara-agent\data\kintell.db

──────────────────────────────────────────────────────────────────────
1. Tables with NCVER / VET / TVA / training / qualification keywords
──────────────────────────────────────────────────────────────────────
  training_completions: 768 rows
  training_completions_ingest_run: 1 rows

──────────────────────────────────────────────────────────────────────
2. Schema + sample for each candidate table
──────────────────────────────────────────────────────────────────────

  TABLE training_completions
    completion_id, state_code, state_name, remoteness_band,
    qualification_code, qualification_name, qualification_level,
    qualification_era, year, completions, ingest_run_id

  Sample row: NSW · Major cities · CHC30113 'old' era · 2019 ·
  completions=3735

  TABLE training_completions_ingest_run
    Source: NCVER VOCSTATS Total VET students and courses 2024 —
    Program Completions. Ingested 2026-04-25 by
    ingest_ncver_completions.py.
    Caveats: NCVER rounding to nearest 5 (per-cell independent, leaf
    sums may drift ±25 per state/year); 2024 NSW figures likely
    overstated.

──────────────────────────────────────────────────────────────────────
3. Rows referencing CHC30121 / CHC30113 / CHC50121 / CHC50113
──────────────────────────────────────────────────────────────────────
  training_completions.qualification_code = 'CHC30121': 192 rows
  training_completions.qualification_code = 'CHC30113': 198 rows
  training_completions.qualification_code = 'CHC50121': 180 rows
  training_completions.qualification_code = 'CHC50113': 198 rows
  Total: 768 rows (matches table count exactly).

──────────────────────────────────────────────────────────────────────
4. Geographic resolution columns
──────────────────────────────────────────────────────────────────────
  (Probe-script gap: reported "(no geographic columns)" because the
  candidate-name set contained "state" (exact-match) which doesn't
  hit "state_code". Lessons-learned. Actual resolution is
  state_code × remoteness_band, plainly visible in section 2.)

──────────────────────────────────────────────────────────────────────
5. NCVER / VET / TVA references in *_ingest_run tables
──────────────────────────────────────────────────────────────────────
  (Probe-script gap: filtered on `source` column; actual provenance
  column is `source_label`. The provenance row IS present, surfaced
  by section 2 above.)
```

### Operator interpretation

Data is rich: 768 rows across 4 CHC qualifications, state × remoteness × year for 2019–2024. All four codes covered (current + superseded across the DEC-24 transition).

But the relevant question for centre-page admission is **NOT data availability**, it's whether the data carries a meaningful credit-lens read at the centre level. After consideration: **it doesn't.**

State-wide pipeline numbers are two layers of indirection from "can THIS centre hire and retain staff":

```
NCVER state completions → state-wide employment market → catchment hiring → this centre's staffing
```

Compare JSA IVI (admitted under DEC-76):

```
JSA IVI state vacancies → state-wide employment market → catchment hiring → this centre's staffing
```

Same number of layers in the abstract, but JSA IVI carries a *current-tightness* read (vacancies posted right now answer "is the market tight today?"). NCVER carries a *future-pipeline* read (completions feed into employment 1–2 years out, lagged).

Lagged supply data is genuinely interesting for portfolio strategy or origination policy. At the deal level — pricing THIS centre, assessing THIS borrower — the marginal information is small once JSA IVI has covered the state-tightness question.

DEC-76's admission of state-level data wasn't a general overturning of DEC-23 — it was specifically about workforce **constraint** signals where trend-in-tightness translates to current staffing risk. NCVER doesn't carry that immediacy. The line between *current-tightness signal* (admitted) and *future-pipeline signal* (deferred) is a defensible place to draw editorial discipline. Once you start admitting lagged supply data, page bloat compounds — every "kind of relevant" indicator demands a row, and the credit-lens read dilutes.

DEC-36's existing wording ("NCVER specifically remains Industry-view per this decision unless the OI-20 probe confirms NCVER-by-SA2/remoteness is already ingested AND useful for centre-level rendering") covers this exactly. The probe found:

1. ✓ NCVER IS ingested
2. ✗ At state × remoteness — NOT SA2/remoteness (granularity test fails)
3. ✗ Assessed not useful for centre-level credit-lens read (usefulness test fails)

DEC-36 stands. No amendment needed.

---

## Disposition

**Negative for centre-page admission. Positive for Industry view.**

- **Centre page:** no row added to Workforce supply context block. Block stays at 4 V1 rows (JSA IVI 4211 + 2411 + ECEC Award + Three-Day Guarantee). DEC-36 stands as written.
- **Industry view:** the `training_completions` table is the canonical home for this data. When the Industry view ships, the multi-year sector pipeline analysis with the DEC-24 transition trough labelled is genuinely the right rendering home. Cert III + Diploma trajectories combined within era to smooth the transition; per-state per-remoteness slice drillable.
- **OI-20 NCVER bullet closes** as "kept at Industry view per DEC-36; data is in DB at `training_completions`, ready for Industry-view consumption when that work lands."
- **OI-20 SEEK and advertised-wage bullets stay open** as V1.5 enrichments — those carry catchment-level (SA2) granularity and a different credit-lens framing.
- **DEC-36 stands.** No amendment.

---

## Cross-references

- **DEC-23** — Operator-level vs industry-level metric separation (the foundational principle this disposition reaffirms)
- **DEC-24** — NCVER qualification-transition caveat (CHC30113 → 30121, 2023 trough; relevant for Industry-view rendering)
- **DEC-36** — NCVER training-completions stays at Industry view (stands, this session confirmed)
- **DEC-76** — Workforce supply context block on the centre page (admits state-level workforce *constraint* signals only)
- **OI-20** — Workforce supply context enrichments (NCVER bullet closes; SEEK and advertised-wage stay open as V1.5)
- `recon/layer4_3_design.md` v1.1 — Thread D framing

---

## Probe-script lessons learned

Same as the SALM probe — the script had two cosmetic gaps that didn't affect the disposition but are worth noting:

1. Section 4 candidate-name set used `"state"` for exact-match against column names; missed `state_code`. Should detect schema then test for substring matches against the geographic-name domain.
2. Section 5 filtered `*_ingest_run` rows on a column called `source`; actual provenance column is `source_label`. Same fix — schema-discover.

Probe-script convention going forward: schema-discover all column names before query construction. Both this script and `probe_salm_lfp_sa2.py` had the same root issue. Cosmetic fixes; not worth a separate sub-pass to retrofit the probes.
