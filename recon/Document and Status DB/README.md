# Kintell — Project Documentation

This is the documentation set for the Kintell childcare-industry data platform. It replaces the earlier monolith status documents (`remara_project_status_*.txt`) with a structured set of files, each with a defined purpose, scope, and refresh cadence.

The monolith files remain in place for historical reference. They are not deleted, not updated, and not authoritative. This set is.

---

## The doc set

| File | Purpose | Refresh cadence |
|---|---|---|
| `README.md` | This file. Index and navigation. | When the doc set itself changes. |
| `PROJECT_STATUS.md` | Current state of work. What has shipped, what is in flight, what is next. | Every session that ships work. Hard ceiling 7 KB. |
| `PRINCIPLES.md` | Stable design and working principles. The "why" behind how the project operates. | Rare. Only when a principle is added, removed, or materially restated. |
| `STANDARDS.md` | Categorised working standards — process, coding, data, audit, naming. Operational rules that have been learned the hard way. | When a new standard is added or an existing one is amended. Numbered globally; categories are sections, not separate files. |
| `DECISIONS.md` | ADR-style record of all material decisions made on the project, with status (Active, Superseded, Withdrawn). | When a decision is made, superseded, or withdrawn. Numbered globally. |
| `ARCHITECTURE.md` | Visual systems, palette tokens, chart technology, page topology, data-layer architecture. | When architecture changes. Stable between phases. |
| `DATA_INVENTORY.md` | Source files in `abs_data/`, database tables in `kintell.db`, refresh policy, and provenance per dataset. | When a data file is added, when a DB table is added or schema-bumped, or when a backup is taken. |
| `ROADMAP.md` | V1 launch scope, V1 path remaining, deferred (P2) scope, parallel work streams. | When V1 scope changes or a phase moves. Distinct from `PROJECT_STATUS.md`: roadmap is forward-looking; status is present-tense. |
| `OPEN_ITEMS.md` | Known bugs, open data quality issues, deferred fixes, residuals. | When an open item is added, resolved, or re-scoped. |
| `GLOSSARY.md` | Terms, acronyms, and project-specific jargon. | When a new term enters routine use. |
| `recon/PHASE_LOG.md` | Append-only historical log of "what was built this session". One entry per session. | Append at session end. Never edit prior entries except to mark superseded content. |

---

## How to use this set

**Starting a new session.** Read `PROJECT_STATUS.md` first. It tells you what is current. If you need historical context for a specific decision, look in `DECISIONS.md`. If you need historical context for what was built when, look in `recon/PHASE_LOG.md`.

**Making a decision.** Add an ADR entry to `DECISIONS.md` with the next sequential ID. If the decision changes a principle, update `PRINCIPLES.md` in the same commit. If it changes architecture, update `ARCHITECTURE.md`.

**Adopting a working standard.** Add to the appropriate category in `STANDARDS.md` with the next sequential ID. Standards and decisions can cross-reference; they do not duplicate.

**Ending a session.** Update `PROJECT_STATUS.md` (always). Append to `recon/PHASE_LOG.md` (when the session shipped work). Update `OPEN_ITEMS.md` (when items were added or resolved). Update `DATA_INVENTORY.md` (when data state changed). Update other docs only if their content changed.

**Numbering discipline.** Decision IDs and Standard IDs are global and stable. Never re-number, even when content is consolidated. When two entries are merged, the canonical ID survives and the merged one is marked `[SUPERSEDED → DEC-N]` with a pointer. The `CONSOLIDATION_LOG.md` (a one-time artefact from the 2026-04-28 restructure) records the merges that produced the initial doc set.

---

## What this set is not

It is not a wiki. It is not exhaustive product documentation. It is not user-facing. It is the working substrate the project is built on — the persistent memory that survives between sessions and prevents drift.

If a fact lives only in a chat transcript, it is at risk. If it lives here, it is durable.
