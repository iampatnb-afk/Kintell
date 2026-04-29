# Working Standards

Operational rules learned by doing. Each standard has a stable global ID (STD-N) and lives in one of five categories: Process, Coding, Data, Audit, Naming. IDs are global across categories, not per-category.

When a standard is consolidated with another or with a decision, the canonical ID survives and the merged entry is marked as `Consolidated → STD-X` or `Consolidated → DEC-X`. The `CONSOLIDATION_LOG.md` records every merge performed during the 2026-04-28 restructure.

---

## Category index

- **Process** — workflow discipline, session hygiene, communication conventions
- **Coding** — script structure, language idioms, file organisation
- **Data** — ingest patterns, data-quality validation, ABS workbook handling
- **Audit** — backup discipline, audit_log schema, mutation safety
- **Naming** — file, table, column, version conventions

---

## Process

### STD-01 — Step-by-step PowerShell with explicit "expected result"
*Origin: 2026-04-22 (canonical from session 1)*

Always provide step-by-step PowerShell commands, one per code block, with an explicit "expected result" so the operator can confirm progress before moving on. The expected result is the operative confirmation; assumed success is not enough.

### STD-02 — Never ask the operator to hand-edit code
*Origin: 2026-04-22*

Never ask the operator to hand-edit code. Regenerate the full file in `/mnt/user-data/outputs/`, present it via `present_files`, and provide overwrite instructions. Hand edits introduce silent drift between intention and what's on disk.

### STD-03 — Bump version markers in file headers
*Origin: 2026-04-22; amended 2026-04-26 (DEC-30)*

Bump version markers in file headers (v2, v3, …) so a quick `Select-String` confirms the right version landed on disk. The version comment embedded in the patched file is the canonical audit trail (DEC-30 amendment). Patcher scripts (`patch_*.py`) themselves are gitignored — they are mechanism, not artefact.

### STD-04 — End every session with a project doc update
*Origin: 2026-04-22*

End every session with a project doc update if there are unfinished threads, decisions worth carrying forward, or material state changes. The new doc set (this `STANDARDS.md` is one of the docs) reduces the session-end burden — only the docs whose content changed need to be touched, plus `recon/PHASE_LOG.md` (always append) and `PROJECT_STATUS.md` (always refresh).

### STD-13 — Kill orphan python.exe before starting review_server.py
*Origin: 2026-04-26*

Before starting `review_server.py`, kill any pre-existing `python.exe` processes — orphans from prior sessions silently bind port 8001 and the new server appears to start (banner prints) but never answers requests. ThreadingHTTPServer on Windows does not always raise on port-already-in-use.

```powershell
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Get-NetTCPConnection -LocalPort 8001 -State Listen -ErrorAction SilentlyContinue
# expected: no rows
```

Cost a full diagnostic round in the 2026-04-26 session: 6 orphan python processes accumulated across multi-day work; the v5 server from 25/04 was answering `/api/centre/<sid>` with "Not found" while the v6 server's banner suggested it was the live process.

### STD-14 — Verify server banner version matches file on disk
*Origin: 2026-04-26*

When restarting any server, verify the banner version output matches the file on disk:

```powershell
Get-Content .\review_server.py -TotalCount 5  # disk
<banner from server window>                    # in-memory
```

The banner is the only ground truth that the running process matches the expected source. File on disk + restarted-window assumption is insufficient (see STD-13).

### STD-21 — No Notepad-based verification gates in workflow
*Origin: 2026-04-27*

No Notepad-based verification gates in workflow. Use programmatic verification (Python prints, console output). If a config file needs editing, regenerate it as a download. Notepad introduces silent encoding drift and operator-eye errors.

### STD-35 — Cross-session continuity via end-of-session monolith
*Origin: 2026-04-29*

Project knowledge in claude.ai and the git repo are independent stores. Files committed to git do not appear in project knowledge; files uploaded to project knowledge do not appear in git. Without explicit synchronisation, every session starts blind to prior session work — the doc library on disk does not, by itself, ground a fresh chat.

The synchronisation discipline is three-tiered:

- **Tier 1 — permanent project knowledge.** Slow-changing canonical docs (`ARCHITECTURE.md`, `PRINCIPLES.md`, `GLOSSARY.md`, `README.md`, `DATA_INVENTORY.md`, `CONSOLIDATION_LOG.md`) plus external reference material (PC reports, credit policy, strategic insights). Uploaded once, replaced only when content materially changes.

- **Tier 2 — end-of-session monolith.** A single text file regenerated at the close of every session. Inlines the current state of every changed Tier-2 structured doc (`PROJECT_STATUS.md`, `ROADMAP.md`, `STANDARDS.md`, `DECISIONS.md`, `OPEN_ITEMS.md`); compresses unchanged content to ID ranges; cites canonical library file paths. Includes a "consolidation log" section naming any retired recon artefacts and where their decisions landed (so a future session reading the monolith does not ask for files that have been absorbed). The operator deletes the prior monolith from project knowledge and uploads the new one before closing the session — one in, one out.

- **Tier 3 — in-chat drop-in.** Files actively under edit during the session — code files (`centre.html`, `centre_page.py`, etc.) and the active recon design doc if there is one. Dropped into the chat at session start or at the moment of edit. Not added to project knowledge.

Mid-session regens of Tier-2 docs (per the regenerate-as-we-go discipline) require the operator to attach the current version of the relevant doc at the moment of regen — Claude does a faithful full-file regen per STD-02, which requires the source.

The end-of-session monolith is the cross-session ground-truth. The structured doc library on disk is the canonical source of truth; the monolith is a serialisation of its current state into a form project knowledge can index.

This standard supersedes the implicit "produce a monolith only when restructuring" assumption from the 2026-04-28 doc restructure. Monoliths now ship every session that materially changes Tier-2 state.

---

## Coding

### STD-05 — PowerShell escaping: never inline complex SQL
*Origin: 2026-04-22*

PowerShell escaping is unforgiving — never inline complex SQL with `$`-references in a `python -c`. Write a small helper `.py` file via a here-string instead. Extends to any one-liner with embedded quotes.

### STD-09 — PYTHONIOENCODING = utf-8 before any Unicode-printing script
*Origin: 2026-04-23*

`$env:PYTHONIOENCODING = "utf-8"` must be set before any script that prints Unicode box-drawing characters or other non-ASCII output. Windows cp1252 codepage crashes otherwise.

### STD-12 — Detect line endings at runtime in patchers
*Origin: 2026-04-25d (DEC-27 promoted)*
*Consolidates: DEC-27*

When patching files in the repo, detect line endings (CRLF vs LF) at runtime and rebuild every anchor with the detected ending. Hardcoding `\r\n` fails silently on LF-only copies (Unix tooling, VS Code with LF default, git autocrlf misconfigured).

Pattern: count file's `\r\n` vs orphan `\n`; pick predominant; substitute throughout. Source-of-truth anchors stored as LF-only in the script; runtime helper `with_le(s_lf, le)` converts.

Established in `patch_operator_html_to_v7.py v3` after v1+v2 failed mid-run on the operator's LF-only `operator.html`.

### STD-20 — When invoking Python with -c, use a helper file for any SQL
*Origin: 2026-04-27*

When invoking Python with `-c` on PowerShell, any SQL containing single quotes will be mangled by PS escaping. Always write a small helper `.py` file. Extends STD-05 to one-liner cases.

### STD-22 — Move-from-Downloads pattern (consolidated)
*Origin: 2026-04-23 (STD-07 origin) + 2026-04-25d (STD-12 origin) + 2026-04-27 (STD-22 origin)*
*Consolidates: STD-07 (original), STD-12 (original — Browser duplicate downloads), original STD-22 (Move-from-Downloads)*

When moving files from Downloads → repo, always pick the newest matching file by `LastWriteTime` and force overwrite. Versioned scripts (e.g. `apply v3`) replace prior files at the canonical name.

```powershell
Get-ChildItem "$env:USERPROFILE\Downloads\<file>*.<ext>" |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1 |
  Move-Item -Destination ".\<dest>" -Force
```

Known gotcha: if a versioned download (e.g. `_v2`) doesn't reach Downloads but the prior `_v1` still does, the move silently picks up the wrong file. Mitigation: give each new version a unique suffix in the source filename and use a matching glob in the move command.

Browser duplicate-download case: browsers may save duplicates as `filename (N).py`. `Move-Item` with the bare filename glob then silently no-op's. The pattern above resolves this — never move with a bare filename.

---

## Data

### STD-15 — ABS Data by Region: missing externalLinks .rels
*Origin: 2026-04-26b*

ABS "Data by Region" workbooks may publish with missing `externalLinks` `.rels` stubs. Repair via zip-surgery before any pandas/openpyxl read. Fail mode is silent — pandas reads the file but reports missing cells rather than the structural issue.

### STD-16 — PowerShell cannot accept raw multi-line SQL pasted directly
*Origin: 2026-04-26b*

PowerShell cannot accept raw multi-line SQL pasted directly. Backtick line continuations and here-strings are the workarounds; the cleanest approach is the helper `.py` pattern (STD-05, STD-20).

### STD-17 — Project doc version drift watch
*Origin: 2026-04-26b; superseded by this restructure*
*Consolidated: with the new doc set, version drift is detected by single-source-of-truth `PROJECT_STATUS.md` plus categorised standards/decisions docs. The original watch standard is preserved here for historical context.*

The original standard: project doc references to file versions (e.g. `operator_page.py v5`) drift from reality between sessions. Mitigation in the original: re-verify file version on session start. New mitigation: `PROJECT_STATUS.md` is refreshed each session and is the single source of truth for current state.

### STD-18 — ABS postcode→SA2 concordances may carry blank-SA2 rows
*Origin: 2026-04-26b*

ABS postcode→SA2 concordances may carry blank-SA2 rows. Filter on session ingest. Note that postcode→SA2 is itself superseded as the primary mapping for services with lat/lng (DEC-70); the concordance is fallback-only.

### STD-22 — ABS Data by Region WIDE-format header structure
*Origin: 2026-04-27 (originally STD-19)*

ABS "Data by Region" WIDE-format workbooks follow this header structure: row 6 = spanning headers (sex/persons groupings), row 7 = sub-headers (year + age band OR metric), row 8+ = data rows. Verified on Population and People Database, Income Database. Header rows still follow this pattern in LONG-format workbooks even when data shape differs (STD-23).

### STD-23 — ABS Data by Region LONG vs WIDE format
*Origin: 2026-04-27b (originally STD-26)*

Some ABS "Data by Region" workbooks are LONG-format (one row per geography × year), not WIDE. Specifically the Education and Employment Database has `Code|Label|Year|metric_cols` structure. STD-22 (header structure) still holds for the HEADER rows but the data shape differs:

- WIDE (Income, Population): metric values across columns; one row per geography
- LONG (Education+Employment): metric values down rows; one row per (geography × year)

Diagnostic must detect format BEFORE pivoting. For LONG, no wide-to-long pivot is needed in apply — year is already a column. Detection heuristic: if columns 1–3 are "Code", "Label", "Year" then LONG format. DEC-58 codifies this.

### STD-24 — Diagnostics on Census-mixed-cadence workbooks
*Origin: 2026-04-27b (originally STD-27)*

Diagnostics on Census-mixed-cadence workbooks (Census-only metrics + annual metrics in same file) must sample multiple years per candidate column, not just the latest. Single-year sampling will misclassify Census-only metrics as 'no_data' if the chosen sample year falls between Census releases.

Recommended: sample latest Census year (2021) AND a recent annual year (e.g. 2023) AND classify per-(column, year) so cadence is visible in output.

### STD-25 — Auto-detect column sanity check from SA2-level rows
*Origin: 2026-04-27 (originally STD-25)*
*Consolidates STD-25 (Auto-detect from SA2 rows) and DEC-50 (sample-value validation pattern)*

Diagnostics that auto-detect columns by header text MUST sample values from SA2-level rows (typically rows 75+ in WIDE-format ABS Data by Region workbooks), not the first 10 rows which are AUST/State aggregates. ABS publishes DIFFERENT metric types under the same column header depending on row geography (DEC-57).

Reusable pattern: any auto-detected column has a sample-value sanity check appropriate to the expected data type (range, scale, internal consistency). Header-text matching alone is not sufficient.

### STD-26 — Verify a public dataset's geographic level on the publisher's page
*Origin: 2026-04-27 (originally STD-24)*

Before assuming a public dataset is published at a given geographic level, verify on the publisher's page. Example failure: assumed JSA SALM publishes at SA4 alongside SA2; in reality JSA SALM is SA2 + LGA only (DEC-52).

### STD-27 — Check ABS_DATA inventory before suggesting a download
*Origin: 2026-04-27 (originally STD-23)*

Before suggesting a file download, CHECK the ABS_DATA inventory in `DATA_INVENTORY.md`. Do not pattern-match to "you need file X" without verifying X is not already on disk. The inventory exists for exactly this reason — read it first.

### STD-29 — ABS publication formats: three patterns
*Origin: 2026-04-27c (originally STD-29)*

ABS publication formats are not uniform. Three distinct patterns now encountered in Layer 2:
- **WIDE per-SA2-row, columns-per-metric** (STD-22) — e.g. Income Database, Population and People Database
- **LONG per-(SA2 × year)-row** (STD-23) — e.g. Education and Employment Database
- **TRI-METRIC-PER-YEAR + per-state-split sheets** — e.g. `Births_SA2_2011_2024.xlsx`, 8 sheets (NSW/VIC/QLD/SA/WA/TAS/NT/ACT), each with row 5 year header spanning 3 columns, row 6 sub-header (ERP | Births | TFR repeated), row 7 unit, row 8+ data

Apply scripts that consume any ABS workbook MUST detect target metric column from row-6 sub-header text match (case-insensitive "Birth", "ERP", "TFR", etc.) — never assume year-column offset. Year column alone identifies year-block, not within-block metric. For per-state-split workbooks, apply must iterate ALL state sheets and aggregate; per-state national-sum sanity check is incorrect (DEC-64).

### STD-31 — Banding tables record cohort_n
*Origin: 2026-04-28 (originally STD-31)*

Banding tables MUST record `cohort_n` alongside percentile/decile/band. `cohort_n` is the size of the cohort the rank was computed against. Layer 4 reads `cohort_n` to gate display (e.g. suppress band rendering when `cohort_n` is below a confidence floor).

### STD-32 — Long-format banding output schema
*Origin: 2026-04-28 (originally STD-32)*

Layer 3 canonical schema for `layer3_sa2_metric_banding`:
```
sa2_code TEXT, metric TEXT, year INT, period_label TEXT,
cohort_def TEXT, cohort_key TEXT, cohort_n INT,
raw_value REAL, percentile REAL, decile INT, band TEXT
```

One row per (sa2_code, metric) for the latest year with adequate coverage (DEC-68). Layer 4 trajectory queries do NOT use this table — they read source `abs_sa2_*` tables directly.

### STD-33 — Read ABS XLSX Metadata sheet before assuming national scope
*Origin: 2026-04-28 (originally STD-33)*

ABS-style XLSX filenames don't always indicate national vs state-only scope. Read the file's Metadata sheet (or first 8 rows of any "Contents"-flavoured sheet) BEFORE assuming national coverage. Example failure: `meshblock-correspondence-file-asgs-edn3.xlsx` is QLD-only despite the generic filename (caught during DEC-66 source hunt).

### STD-34 — Calibration discipline for non-SA2-measured metrics
*Origin: 2026-04-28b — locked 2026-04-29 with closure of Layer 4.3 design (DEC-74 through DEC-76)*

Where a catchment metric depends on data not directly measured at SA2 (`participation_rate`, `attendance_factor`, occupancy assumption), a documented calibration function returns a defensible per-SA2 value. The function's inputs and rule text must surface in the DER tooltip alongside the value, so the reader sees how the assumption was constructed for THEIR SA2.

Constants (`attendance_factor=0.6` = 3 days/week per PC universal-access target; `occupancy=0.85` industry baseline) are working-standard constants referenced from a single named module (`catchment_calibration.py`) — never magic numbers in code.

The calibration function `calibrate_participation_rate()` takes `(income_decile, female_lfp_pct, nes_share_pct, aria_band)` and returns `(rate, rule_text)`. Default 0.50, range [0.43, 0.55], nudges ±0.02 per documented input. Rule text format describes the inputs that pushed the rate above or below baseline so the DER tooltip is self-explanatory.

This standard applies to any future catchment metric whose underlying data is published at a coarser geography than SA2 — not just the Layer 4.3 four-ratio scope.

---

## Audit

### STD-08 — Timestamped backup before any DB mutation
*Origin: 2026-04-23*

DB-mutating scripts take their own timestamped backup before the mutation, even if a session-level backup already exists. Two backups = two recovery points at different granularities and zero downside.

Filename pattern: `kintell.db.backup_pre_<step>_<ts>` where `<step>` is the layer step name and `<ts>` is `YYYYMMDD_HHMMSS`. All backups gitignored under `data/` (DEC-31 covers the gitignore pattern).

### STD-11 — audit_log canonical schema and INSERT pattern
*Origin: 2026-04-25d (DEC-26 promoted) + 2026-04-27c (DEC-62 superseded DEC-26)*
*Consolidates: original STD-11 (DEC-26-derived NOT NULL contract), DEC-26 (NOT NULL contract), DEC-62 (full canonical schema)*

The complete canonical schema lives in DEC-62. The operative INSERT pattern is hardcoded 7-column:

```sql
INSERT INTO audit_log
  (actor, action, subject_type, subject_id,
   before_json, after_json, reason)
VALUES (?, ?, ?, ?, ?, ?, ?);
```

`occurred_at` is omitted — defaults to `datetime('now')`. NOT NULL columns: `actor`, `action`, `subject_type`, `subject_id`. `subject_id` is declared INTEGER but stores TEXT via SQLite affinity for table-level events (e.g. `subject_id='training_completions'`).

Generic schema discovery at runtime is prohibited (STD-30). The schema is stable and well-known; runtime discovery added a failure surface in Step 1b v1.

Use `'<source>_<verb>_v1'` naming for `action`. Use `subject_type='table'` and `subject_id='<table_name>'` for whole-table events; use the actual PK for row-level events.

### STD-28 — After any DB-mutating script, validate by querying the DB
*Origin: 2026-04-22 (originally STD-05)*

After any DB-mutating script: validate by querying the DB before moving on. Never assume idempotency until proven. Apply scripts include their own validate sub-step or pair with a `_spotcheck.py` companion.

### STD-30 — Pre-mutation read-only DB inventory
*Origin: 2026-04-27c (originally STD-28)*

Before starting any Layer 2 apply that mutates the DB, take a read-only snapshot covering: tables list with row counts, per-table schema, indexes, year/timestamp columns, SA2 coverage stats per table, year coverage stats per table, foreign-key / orphan health, backup file listing in `data/`, audit_log dump.

Output: `recon/db_inventory.md`. Helper: `db_inventory.py` (read-only, no DB writes).

Provides a clean rollback anchor and a reviewable surface so schema/coverage drift between sessions is visible.

### STD-19 — audit_log INSERT must be hardcoded 7-column
*Origin: 2026-04-28 (originally STD-30)*
*Consolidated → STD-11*

Originally a separate standard requiring hardcoded INSERTs and prohibiting generic discovery. Now consolidated into STD-11, which is the canonical standard for audit_log handling.

---

## Naming

### STD-06 — File version conventions
*Origin: 2026-04-22 (originally STD-03 part)*

Versions in file headers use the form `v2`, `v3`, etc. Versioned backups follow `<file>.v<N>_backup_<ts>`. Versioned downloads of canonical files follow `<filename>_v<N>.<ext>` to defeat the Move-from-Downloads gotcha (STD-22).

### STD-07 — Action naming convention for audit_log
*Origin: 2026-04-26b (referenced in DEC-62)*

`audit_log.action` follows `<source>_<verb>_v1` format (e.g. `sa2_polygon_backfill_v1`, `nqaits_ingest_v1`). The `_v1` suffix anticipates that re-runs with materially different logic will increment to `_v2`.

### STD-10 — Patcher pattern: file-naming and gitignore
*Origin: 2026-04-25d (originally STD-10 line-ending) + 2026-04-26 (DEC-30 amendment on patcher gitignore)*

Patcher scripts follow `patch_<target_file>_to_v<N>.py` naming. They are gitignored as `patch_*.py` (DEC-31 generic backup pattern doesn't conflict; patcher and backup ignores are separate). The version comment in the patched file is the canonical audit trail (DEC-30; STD-03 amended).

The line-ending detection content originally under STD-10 has been moved to STD-12 (Coding category) where it sits with related patcher discipline.

---

## Numbering note

The original chain ran 1–34 with overlaps and category-less ordering. This document preserves the global numbering for historical traceability while organising by category. Where the same standard was expressed twice in the chain (e.g. browser duplicate downloads + Move-from-Downloads), the entries are consolidated under one canonical ID with the merge recorded in `CONSOLIDATION_LOG.md`.

The skipped IDs in the displayed sequence (no STD-32 visible immediately under Coding, etc.) reflect cross-category placement rather than missing content. To check coverage, the full ID range is 1–35. Every ID resolves either to a live entry or to a `Consolidated → STD-X` pointer.
