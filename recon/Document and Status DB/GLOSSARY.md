# Glossary

Terms, acronyms, and project-specific jargon used in this documentation set and the codebase.

---

## Geography and demographics

**SA2** — Statistical Area Level 2. Australian Bureau of Statistics geographic unit, ~10,000 people. Primary unit of analysis for catchment work in this project.

**SA4** — Statistical Area Level 4. Larger ABS unit; used for some labour-force series.

**LGA** — Local Government Area.

**ASGS** — Australian Statistical Geography Standard. Edition 3 (2021) is the current basis for SA2 and Remoteness Area definitions.

**ARIA / ARIA+** — Accessibility / Remoteness Index of Australia. The "+" version has more granularity. Stored on `services` as `aria_plus` (label string, not code).

**RA** — Remoteness Area. Five categories: Major Cities, Inner Regional, Outer Regional, Remote, Very Remote. SA2-level RA mapping comes from the ABS Remoteness Areas GeoPackage.

**SEIFA** — Socio-Economic Indexes for Areas. Decile per SA2 used as a catchment proxy. The IRSD (Index of Relative Socio-economic Disadvantage) is the primary index in use.

**ERP** — Estimated Resident Population. ABS annual population estimate at SA2.

**TFR** — Total Fertility Rate.

**Census TSP** — Census of Population and Housing — Time Series Profile. Multi-Census-cycle SA2-level data tables.

---

## Childcare regulatory and operational

**ACECQA** — Australian Children's Education and Care Quality Authority. Source for NQS ratings.

**NQS** — National Quality Standard. Seven quality areas (qa1-qa7).

**NQS rating values** — `MEET` (Meeting), `EXCD` (Exceeding), `WORK` (Working Towards), `SIGI` (Significant Improvement Required), `PROV` (Provisional), `NYR` (Not Yet Rated), `OOS` (Out of Scope), `NONE` (sentinel for service types not under NQS).

**NQAITS** — National Quality Agenda IT System. The ACECQA back-end.

**NQF** — National Quality Framework. The umbrella regulatory framework.

**LDC** — Long Day Care.

**OSHC** — Outside School Hours Care.

**FDC** — Family Day Care.

**PSK / Preschool** — Preschool / Kindergarten.

**CCS** — Child Care Subsidy. Australian Government subsidy paid to families.

**ACCS** — Additional Child Care Subsidy. Targeted top-ups (Grandparent, Child Wellbeing, etc.).

**HCCS** — High Child Care Subsidy.

**NES** — Non-English-Speaking. Used in the catchment-calibration framework as one input to the participation-rate function.

**Service approval** — A regulatory approval at the centre level. Identifier prefix `SE-`.

**Provider approval** — A regulatory approval at the legal-entity level. Identifier prefix `PR-`. The mapping from provider to centre is the basis for ownership-graph work.

**SALM** — Small Area Labour Markets. Jobs and Skills Australia (JSA) quarterly smoothed unemployment series at SA2.

**JSA** — Jobs and Skills Australia. Australian Government agency. Publishes SALM and the Internet Vacancy Index (IVI).

**IVI** — Internet Vacancy Index. JSA series of online job vacancies by ANZSCO code. Used for ECEC workforce demand signal.

**ANZSCO** — Australia and New Zealand Standard Classification of Occupations. Code 4211 = Child Carers; code 2411 = Early Childhood Teachers.

**NCVER** — National Centre for Vocational Education Research. Source for training-completions data.

**RWCI** — Regional Workforce Constraint Index. Composite indicator (deferred to P2).

---

## Data layer

**ULID** — Universally Unique Lexicographically Sortable Identifier. Used as primary key in the Starting Blocks pilot data.

**OBS / DER / COM** — Cross-cutting classification tags applied to fields and rows in the platform.
- **OBS** = Observed. Direct from source.
- **DER** = Derived. Computed from observed inputs with a documented rule.
- **COM** = Commentary. Rule-based narrative line.

**DER tooltip** — Hover tooltip on the centre/operator pages that exposes the rule and inputs behind a derived value.

**Cohort** — The peer group an SA2 is compared against in Layer 3 banding. Cohort definitions: `state`, `remoteness`, `state_x_remoteness`, `national`.

**Layer 1 / 2 / 3 / 4 / 5** — The Phase 2.5 pipeline tiers. See `ARCHITECTURE.md`. Layer 1 = recon, Layer 2 = data ingest, Layer 3 = banding, Layer 4 = page render, Layer 5 = doc restructuring.

---

## Visual / UI

**Palette A** — The colour token set used by the centre, operator, and review pages. Accent `#4a9eff`. 18 tokens.

**Palette B** — The colour token set used by the dashboard and industry pages. Accent `#3d7eff`, accent2 `#00c9a7`, hot `#e05c3a`. 16 tokens.

**System A** — The "operator family" visual system. Palette A, bespoke inline SVG.

**System B** — The "dashboard family" visual system. Palette B, Chart.js 4.4.0.

**Chip strip** — Horizontal row of low/mid/high band chips, with the active band highlighted.

**Decile strip** — Ten-cell gradient bar showing the SA2's position within the cohort. Single-hue blue ramp; saturation steps with band; SA2 cell at full accent.

**Trajectory** — Time-series chart on the centre page. Sparkline (≥7 points) or dot trajectory (<7 points).

**Trend window buttons** — Global 3Y / 5Y / 10Y / All button strip controlling the time scale of all trajectory charts on a page.

---

## Process

**Decision-65 pattern** — Probe → design doc → decisions closed → code. The project's standard pre-work pattern for non-trivial work, named for the decision that codified it. See `PRINCIPLES.md` for the full statement.

**ADR** — Architecture Decision Record. The structured format used in `DECISIONS.md`.

**Apply script** — A DB-mutating script that performs an ingest or migration step. Naming convention: `layer<N>_step<X>_apply.py`. Always paired with a dry-run mode and a diagnostic (`_diag`) script.

**Probe script** — A read-only script that inspects state without mutation. Naming: `*_probe.py` or `*_inspect.py`.

**Pre-state inventory** — The read-only DB snapshot taken before any mutating run. Helper: `db_inventory.py`. See Standard 28.

**audit_log** — The DB table that records every mutation. Schema is canonical (see `DECISIONS.md` DEC-62 and `STANDARDS.md` AUDIT-01).
