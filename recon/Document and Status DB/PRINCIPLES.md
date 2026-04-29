# Principles

Stable design and working principles for the Kintell project. Principles change rarely. They sit above standards and decisions: standards say *how* to do something, decisions record *what* was chosen, principles state *why* the project operates the way it does.

When a principle is restated or refined, the change is recorded with a date. Outright withdrawal of a principle is a serious event and is also recorded.

---

## P-1 — Probe before code (the Decision-65 pattern)
*Stated: 2026-04-27c (DEC-65) | Confirmed: 2026-04-28b*

Non-trivial work starts with a read-only probe of the affected surface, followed by a written design document, followed by explicitly closed decisions, followed by code. The order is non-negotiable for any work that touches schema, banding, page surface, or shared conventions.

**Why.** Banding choices, schema decisions, and visual conventions made in isolation conflict with what's already shipped. The cost of probe + design is reliably less than the cost of rework caught after code lands. Layer 3 was the canonical case: a precedent survey of shipped Operator/Catchment/Industry surfaces revealed conventions that Layer 3 had to honour, not redesign (DEC-65, DEC-67).

**The pattern in practice.**
1. Probe — write a read-only inspection script. Output goes to `recon/<step>_probe.md` or similar.
2. Design — write a design document closing the open questions. Output goes to `recon/<step>_design.md`.
3. Decide — every decision in the design doc gets either an explicit ID and ADR entry in `DECISIONS.md`, or is deferred with a tracked open item in `OPEN_ITEMS.md`.
4. Code — apply scripts, render code, schema migrations. Each is paired with a dry-run mode and a `_spotcheck.py` or invariant-check companion.

**When the pattern can be relaxed.** Pure renderer changes that consume an already-stable payload schema. Pure prose updates. Backup, audit, or housekeeping work. Probe-only sessions (the probe IS the work).

---

## P-2 — Honest absence over imputed presence
*Stated: 2026-04-25 (DEC-15 pricing placeholder); 2026-04-27 (DEC-53 SALM coverage); 2026-04-27c (DEC-63 SA2 residuals)*

Where data is genuinely absent, the page surface and the data layer reflect that absence honestly. Imputation is reserved for narrow, documented cases (e.g. point-in-polygon fallback for centroid-on-boundary SA2s in DEC-66). Synthetic numbers are never shown as if they were observed values.

**Examples.** Pricing placeholder is rendered as a placeholder, not a fabricated number (DEC-15). SA2-without-SALM-coverage centres render an explicit empty state, not a zero (DEC-53). Census-only LFP surfaces 3 points across 2011/2016/2021 as a dot trajectory, not a smoothed line (Layer 4.2 design).

---

## P-3 — Single source of truth for assumptions
*Stated: 2026-04-25 (DEC-13)*

Project assumptions (educator ratios, target margins, calibration constants, banding cutoffs) live in one canonical location per assumption type. Magic numbers in code are prohibited.

- Assumption *values* live in the `model_assumptions` table (DB-resident, audit-tracked).
- Calibration *functions* live in named modules (e.g. `catchment_calibration.py`) — see STD-34 staged.
- Banding *cutoffs* live in `STANDARDS.md` (STD-32) and `DECISIONS.md` (DEC-67), referenced by ID from code.

**Why.** Drift between a value declared in code and a value declared in docs is the single most common cause of cross-session inconsistency on this project. Keeping the value in one place — with audit trail — closes the drift.

---

## P-4 — Position indicators are not trends; trends are not position indicators
*Stated: 2026-04-28b (DEC-71)*

Two visual systems coexist in the codebase by design. The boundary between them is functional, not aesthetic.

- **Position indicators** — decile strips, cohort histograms, chip strips, decision strips. These show *where this thing sits within a peer group*. Implemented as bespoke inline SVG using Palette A.
- **Trends** — line charts showing how a value moves over time. Implemented in Chart.js 4.4.0 using Palette B's stroke conventions.

The centre page bridges the two: trend regions use Chart.js, position regions use bespoke SVG. Stroke colour on trends never carries valence — direction of "good vs concerning" lives only in band-copy text (DEC-72, STD-34).

**Why.** Position is a categorical/ordinal statement; a chart library's continuous-value affordances mislead the reader. Trend is a continuous-value statement; bespoke SVG is fine for one-off but incurs maintenance cost across pages and tooltips. Different tools for different statements.

---

## P-5 — Provenance is queryable, not narrated
*Stated: 2026-04-25 (DEC-12, OBS/DER/COM); 2026-04-25c (DEC-21, provenance row pattern)*

Every observed, derived, and commentary value on a page surface carries a tag (OBS / DER / COM) that exposes its provenance via tooltip. Every ingest produces a row in an `*_ingest_run` table capturing source, date, row counts, and run-specific caveats.

**Why.** Reviewers underwrite credit decisions on this data. The difference between an observed ABS value, a derived calibration, and a rule-based commentary line must be one click away — not buried in chat history or documentation. Provenance is part of the page, not an appendix.

---

## P-6 — Idempotency, dry-run, and audit on every mutation
*Stated: 2026-04-23 (DEC-10, Tier 2 ingest pattern); reinforced throughout*

Every DB-mutating script is idempotent (re-runnable), supports dry-run mode (default), and writes to `audit_log` (STD-11, DEC-62). A timestamped DB backup is taken before any mutation (STD-08), independent of session-level backups. Apply scripts pair with a `_diag.py` for read-only investigation and a `_spotcheck.py` for post-mutation validation.

**Why.** Recovery from a bad mutation must be a single-command operation. Without backups, dry-run, and audit, a regrettable run is a regrettable session. With them, it's a one-line revert.

---

## P-7 — Operator agency determines surface placement
*Stated: 2026-04-25d (DEC-23); reaffirmed 2026-04-26 (DEC-36)*

Metrics where the operator has agency or competitive position belong on operator surfaces. Metrics that describe the wider sector belong on the Industry view. State-level training-completions, regional childcare deserts, macro fee trends, and policy-effect signals are sector-level and live in the Industry view, even when they're operationally relevant to a specific operator.

**Why.** The credit lens needs to distinguish what an operator can change from what they cannot. Mixing them on the same card invites the wrong question — "what should this operator do about something they can't influence?". The right framing for sector context affecting an operator is "your share of state supply" or "your catchment's position within a peer cohort" — derived metrics that layer agency over a sector base.

---

## P-8 — Additive overlay before invasive change
*Stated: 2026-04-25 (DEC-11)*

New modules and metrics layer over existing data and surfaces. Existing surfaces are not modified to accommodate them where the addition can be made non-invasively. New tables, new helpers, new render slots — these are preferred over restructuring shipped tables and surfaces.

**Why.** Regression risk on shipped surfaces is high. Additive change is reviewable as a single commit. Invasive change requires synchronised front-end + back-end + data work, which is harder to verify and harder to revert. The cost of additive accumulation is real (occasional consolidation passes are needed) but is borne in a controlled way.

---

## P-9 — Visual consistency is downward, not just sideways
*Stated: 2026-04-27c (DEC-65); reinforced 2026-04-28b (DEC-71)*

Visual consistency between page surfaces is not a UI-only concern. The same principle extends downward into data-layer schema: shared metrics use the same percentile semantics, the same banding cutoffs, and the same cohort definitions across pages. Layer 3 doesn't redesign banding — it adopts the conventions already shipped on the Industry, Catchment, Operator, and Centre v1 surfaces (DEC-67 as the concrete instance).

**Why.** Surface consistency without data-layer consistency is theatre. If the operator card and the centre card both show a "low/mid/high" band but compute the bands from different cutoffs, the consistency is illusory and reviewers eventually notice. Shipped UI conventions are a contract; the data layer honours them.

---

## P-10 — Documentation is part of the system, not a side effect
*Stated: 2026-04-28 (this restructure)*

The doc set in this repository is operational, not informational. `PROJECT_STATUS.md` is the persistent memory between sessions. `DECISIONS.md` is the contract that prevents re-litigation. `STANDARDS.md` is the rule book that prevents the same pothole being hit twice. `recon/PHASE_LOG.md` is the change history.

Every session ends with a doc update. Sessions that ship work without updating the docs leave the project worse than they found it, regardless of what shipped.

**Why.** Cross-session drift is the failure mode this project has felt most acutely. The monolith chain that preceded this doc set accumulated 73 decisions, 34 standards, and 10+ session entries — and lost coherence twice on the way. Treating docs as part of the system, not commentary on it, is the structural fix.
