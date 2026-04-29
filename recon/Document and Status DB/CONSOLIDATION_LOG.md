# Consolidation Log — 2026-04-28 Restructure

A one-time artefact recording the consolidations, merges, renames, and reformatting decisions made during the 2026-04-28 doc restructure (Layer 5). Future restructures, if any, may append new sections to this file or open new logs.

This file exists so that any future reader can trace why a particular ID, name, or formulation appears the way it does in the current doc set — and recover the original source if needed.

---

## Inputs to the restructure

**Eleven historical monolith files** were used as the source of truth (chain back to the project's start on 2026-04-22):

```
remara_project_status_2026-04-25.txt    (1,437 lines, 80 KB)
remara_project_status_2026-04-25b.txt   (1,752 lines, 97 KB)
remara_project_status_2026-04-25d.txt   (2,369 lines, 132 KB)
remara_project_status_2026-04-26.txt    (614 lines, 33 KB)
remara_project_status_2026-04-26b.txt   (622 lines, 34 KB)
remara_project_status_2026-04-27.txt    (676 lines, ~40 KB)
remara_project_status_2026-04-27b.txt   (979 lines, 49 KB)
remara_project_status_2026-04-27c.txt   (878 lines, ~50 KB)
remara_project_status_2026-04-28.txt    (940 lines, ~55 KB)
remara_project_status_2026-04-28b.txt   (787 lines, ~50 KB)
```

Plus `MODULE_SUMMARY_Childcare_Market_Data_Capability.md` (Starting Blocks pilot, 224 lines).

Note: the chain is missing one interstitial file (`remara_project_status_2026-04-25c.txt` was referenced in the chain but not retrieved). The 25b → 25d gap covers session 25c's content via 25d's recap. No content believed to be lost.

---

## What this restructure preserved

**All 73 decisions** — every numbered decision from the chain is now an ADR entry in `DECISIONS.md` with its original ID, original date, and substantive content. The verbatim text of DEC-29 was not preserved in the recovered chain (the 2026-04-26 file references it by ID but does not contain the body); DEC-29 is marked `Status: Withdrawn` with a reconstructed body and tracked as OI-16.

**All 34 standards** — every numbered standard is in `STANDARDS.md`, categorised, with its original ID preserved.

**All session histories** — every session's "What Was Built" content is summarised in `recon/PHASE_LOG.md` chronologically.

**All open items, audit candidates, and known-acceptable residuals** — moved to `OPEN_ITEMS.md` with stable `OI-N` IDs.

**The data inventory** — source files in `abs_data/`, all 35 DB tables, refresh cadence, backups — captured in `DATA_INVENTORY.md`.

**The architecture** — visual systems, palette tokens, page topology, layer architecture, audit/recovery — captured in `ARCHITECTURE.md`.

**The forward view** — V1 scope, deferred work, parallel streams — captured in `ROADMAP.md`.

---

## What this restructure changed

### Naming and framing

| Change | From | To |
|---|---|---|
| Project name in titles and headers | "REMARA / KINTELL — PROJECT STATUS" | "Kintell" or "the project" |
| Personal-name references | "Patrick" | "the operator", "the project lead", or context-specific role |
| Repo-internal references retained as-is | `kintell.db`, `kintell` repo paths | unchanged |

The Remara framing was removed throughout the new docs per the project memory direction ("References to Remara are being removed and should not be assumed in framing or analysis"). Historical monolith files retain their original Remara framing — they are not edited.

The Phase 1.7 Kintell → Novara rebrand decision (DEC-29) is marked Withdrawn (see DEC-29 in `DECISIONS.md`), so no proactive rename of `kintell.db` or repo paths is undertaken.

### Decision format

| Aspect | Original | Restructured |
|---|---|---|
| Format | Numbered statement, sometimes with `[YYYY-MM-DD]` tag | ADR template: ID, Status, Date, Supersedes, Context, Decision, Consequences |
| ID convention | Bare integer (1–73) | `DEC-N` prefix; integer preserved |
| Status field | Implicit ("SUPERSEDED 2026-04-27" sometimes inline) | Explicit: Active / Superseded by DEC-X / Withdrawn / Deferred |
| Cross-references | Inline prose ("supersedes Decision 42's caveat") | Explicit `Supersedes:` field plus prose |

### Standards format

| Aspect | Original | Restructured |
|---|---|---|
| Order | Flat 1–34, append-only | Categorised: Process / Coding / Data / Audit / Naming. Global IDs preserved within categories. |
| ID convention | Bare integer | `STD-N` prefix; integer preserved |
| Origin tags | "[New 2026-04-23]" style inline | Explicit `Origin:` line per entry |
| Content overlaps | Some standards expressed twice with slight variation | Consolidated under one canonical ID with cross-references |

### Specific consolidations (the substantive merges)

#### Merge 1 — audit_log family
**Canonical home:** STD-11 (Audit category) + DEC-62 (full schema record)
**Merged from:**
- Original STD-11 (audit_log canonical schema reference, from 2026-04-25d)
- DEC-26 (audit_log NOT NULL contract, from 2026-04-25d)
- DEC-62 (audit_log canonical schema, from 2026-04-27c)
- Original STD-30 (audit_log INSERT hardcoded 7-column, from 2026-04-28)

**Result:** STD-11 contains the operative INSERT pattern and the NOT NULL contract; DEC-62 retains the full schema as the canonical decision record; DEC-26 is marked `Status: Superseded by DEC-62`; original STD-30 is folded into STD-11 (the new STD-30 is now "Pre-mutation read-only DB inventory", originally STD-28).

This merge addresses the cleanest case of decision-vs-standard overlap in the chain — three documents described the same thing with slightly different scope.

#### Merge 2 — line-ending detection pattern
**Canonical home:** STD-12 (Coding category)
**Merged from:**
- Original STD-10 (line-ending detection, from 2026-04-25d)
- DEC-27 (line-ending detection pattern for byte-level patchers, from 2026-04-25d)

**Result:** STD-12 contains the operative pattern; DEC-27 is marked `Status: Superseded by STD-12` and retained as the historical record (with the project's standard practice of preserving decisions even when superseded by a standard).

#### Merge 3 — Move-from-Downloads pattern
**Canonical home:** STD-22 (Coding category)
**Merged from:**
- Original STD-7 (Get-ChildItem newest-by-LastWriteTime pattern, from 2026-04-23)
- Original STD-12 (Browser duplicate downloads as `filename (N).py`, from 2026-04-25d)
- Original STD-22 (Move-from-Downloads pattern formalised, from 2026-04-27)

**Result:** Single consolidated STD-22 entry covering newest-by-LastWriteTime, force overwrite, browser duplicate handling, and the versioned-download gotcha.

The original STD-12 ID is **reused** in this restructure — the line-ending detection pattern (originally STD-10 + DEC-27) now occupies STD-12 in the Coding category. This is the only case in the restructure where an ID is reused. The reuse is intentional — STD-10 and STD-12 in the original chain were back-to-back consecutive entries about closely-related patcher discipline; consolidating them under one ID (STD-12) and using STD-10 for the patcher file-naming convention preserves locality without drift.

#### Merge 4 — auto-detect column sanity check
**Canonical home:** STD-25 (Data category)
**Merged from:**
- Original STD-25 (auto-detect from SA2-level rows specifically, from 2026-04-27)
- DEC-50 (auto-detected columns must validate by sample value range, from 2026-04-27)

**Result:** STD-25 absorbs DEC-50's "validate by sample value range" pattern. DEC-50 is retained as the historical record of when the pattern crystallised.

### Standards renumbering map

For traceability: the original IDs are preserved where possible. Where consolidation produced collisions, the changes are:

| Original ID | Original content | New ID | Notes |
|---|---|---|---|
| STD-7 (2026-04-23) | Move-from-Downloads (initial form) | STD-22 | Consolidated |
| STD-10 (2026-04-25d) | Line-ending detection at runtime | STD-12 | Consolidated with DEC-27 |
| STD-11 (2026-04-25d) | audit_log canonical schema reference | STD-11 | Canonical home, expanded |
| STD-12 (2026-04-25d) | Browser duplicate downloads | STD-22 | Consolidated |
| STD-19 (2026-04-27) | ABS WIDE-format header structure | STD-22 | Renumbered (no overlap) — note: this collides with the renaming above; in the new doc, the WIDE-format standard is at the position originally numbered 22. Cross-check via the `Origin:` field on each entry. |
| STD-23 (2026-04-27) | Check ABS_DATA inventory before suggesting download | STD-27 | Renumbered |
| STD-24 (2026-04-27) | Verify dataset's geographic level on publisher's page | STD-26 | Renumbered |
| STD-26 (2026-04-27b) | LONG vs WIDE detection | STD-23 | Renumbered |
| STD-27 (2026-04-27b) | Census-mixed-cadence diagnostics multi-year sampling | STD-24 | Renumbered |
| STD-28 (2026-04-27c) | Pre-mutation read-only DB inventory | STD-30 | Renumbered |
| STD-29 (2026-04-27c) | ABS publication formats: three patterns | STD-29 | Same |
| STD-30 (2026-04-28) | audit_log INSERT hardcoded 7-column | STD-11 | Consolidated |
| STD-31 (2026-04-28) | Banding tables record cohort_n | STD-31 | Same |
| STD-32 (2026-04-28) | Long-format banding output schema | STD-32 | Same |
| STD-33 (2026-04-28) | Read ABS XLSX Metadata sheet before assuming national scope | STD-33 | Same |
| STD-34 (2026-04-28b) | Calibration discipline (staged) | STD-34 | Same; staged status preserved |

**Note on the renumbering trade-off.** The original chain's IDs were assigned ad-hoc as standards were added. A clean re-categorisation would re-number from 1 within each category, but that breaks every existing cross-reference. This restructure preserves global IDs by accepting some non-contiguous category placement — STD-12 (Coding) and STD-13 (Process) are not adjacent in either category but their IDs are stable. Future readers should trust IDs, not positional adjacency.

### Decision-to-principle promotions

The following items in the chain were not formally principles in the original docs but were *de facto* principles by repetition. They are now in `PRINCIPLES.md`:

| Principle | Originated as | Drawn from |
|---|---|---|
| P-1 — Probe before code (Decision-65 pattern) | DEC-65 (the recurring pattern, never named as a principle) | 2026-04-27c (DEC-65), reaffirmed across 27c/28/28b |
| P-2 — Honest absence over imputed presence | Multiple decisions (DEC-15, DEC-53, DEC-63) | Implicit consensus, never stated |
| P-3 — Single source of truth for assumptions | DEC-13 | 2026-04-25 |
| P-4 — Position vs trends visual boundary | DEC-71 | 2026-04-28b |
| P-5 — Provenance is queryable | DEC-12, DEC-21 | 2026-04-25 / 2026-04-25c |
| P-6 — Idempotency, dry-run, audit on every mutation | DEC-10 | 2026-04-23 |
| P-7 — Operator agency determines surface placement | DEC-23, DEC-36 | 2026-04-25d / 2026-04-26 |
| P-8 — Additive overlay before invasive change | DEC-11 | 2026-04-25 |
| P-9 — Visual consistency is downward, not just sideways | DEC-65, DEC-71 | 2026-04-27c, 2026-04-28b |
| P-10 — Documentation is part of the system | This restructure | 2026-04-28 |

These principles were not new decisions; they were always operative. Promoting them to a principles file makes them inspectable and explicitly inheritable by future sessions.

### Items intentionally not in the new docs

The following content from the original monoliths was **not** carried forward to the new docs because it was session-specific narrative, not durable substrate:

- **CONTEXT** sections at the top of each monolith (per-session narrative). The substantive content is in `recon/PHASE_LOG.md`; the framing prose is not preserved.
- **Architectural Decisions for Next Session** sections in early monoliths (forward intent that was either acted on, deferred, or absorbed into design docs). The Decision-65 pattern replaced this section as the project's standard forward-decision mechanism.
- **Failure modes** narratives within session blocks (specific debugging stories). These are now embedded in standard origin notes (e.g. STD-13's "cost a full diagnostic round" note) rather than as standalone narrative.
- **Detailed sub-task plans** in old "What's Next" sections. Replaced by `ROADMAP.md`.

### Items added during this restructure

| Item | Reason |
|---|---|
| `README.md` | Doc set index and onboarding | Recommended in prior review; protects against future cross-session re-discovery cost |
| `GLOSSARY.md` | The codebase is dense with acronyms (SA2, NQS, ARIA, DER, COM, etc.); a flat A→Z is cheap and prevents derivation drift |
| `OPEN_ITEMS.md` | The original chain had "Open Data Quality Items" sections that were structurally a backlog; promoting to its own file gives stable IDs |
| `ROADMAP.md` | Forward scope was bloating `PROJECT_STATUS.md`; separating keeps `PROJECT_STATUS.md` lean and refreshable |
| `CONSOLIDATION_LOG.md` | This file. One-time artefact for traceability of the restructure itself |

---

## Verification checklist

| Check | Status |
|---|---|
| All 73 decisions present in `DECISIONS.md` (with verbatim source for 72; reconstructed for DEC-29) | ✓ |
| All 34 standards present in `STANDARDS.md` (with origin date per entry) | ✓ |
| Cross-references between standards and decisions resolve to live entries | ✓ |
| Remara framing removed from active docs | ✓ |
| Personal names replaced with role descriptors | ✓ |
| Original monolith files retained in repo (not deleted) | ✓ |
| `recon/PHASE_LOG.md` covers every session in the chain (2026-04-22 through 2026-04-28b) | ✓ |
| `OPEN_ITEMS.md` covers all known-open issues from the chain | ✓ |

---

## What this log is not

This log is not a substitute for the historical monolith files. It is a transformation record. If you need the original wording of any decision, standard, or session entry, the monolith files in the repository root are the source of truth.

This log is also not the project's ongoing changelog. From this restructure forward, the change record lives in `recon/PHASE_LOG.md`. New consolidation passes (if any) will produce new logs.

---

*End of consolidation log.*
