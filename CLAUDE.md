# CLAUDE.md — Orientation for Claude Code sessions

*Last updated: 2026-05-09. Always-loaded by Claude Code at session start.*

This file is the lifeline for any Claude Code session on this project. Read it completely before doing anything else.

---

## What this project is

**Novara Intelligence** (working brand) — an Australian childcare asset & portfolio intelligence platform. Owner: Patrick Bell. Independent commercial product, not internal Remara tooling. Filesystem still uses legacy names (`remara-agent/` working dir, `kintell.db` database, various `kintell_*` and `remara_*` artefacts) — brand rename pass deferred to OI-NEW-6.

The platform takes a per-centre, per-catchment, per-operator view of the Australian childcare sector and turns it into structured intelligence for institutional decision-making — credit, investment, valuation, acquisition, NFP impact assessment.

**Reference docs to read in order at session start:**
1. `CLAUDE.md` (this file)
2. `PROJECT_STATUS.md` — current state, latest commits, what just shipped
3. `PRODUCT_VISION.md` — strategic frame, audience, V1/V2/V3 horizon, five new streams
4. `ROADMAP.md` — dependency-ordered queue
5. `CENTRE_PAGE_V1_5_ROADMAP.md` (underscore version is canonical) — V1.5 source of truth
6. `OPEN_ITEMS.md` — what's tracked as open
7. Tier-1 docs at `recon/Document and Status DB/` — ARCHITECTURE, PRINCIPLES, GLOSSARY, DATA_INVENTORY, CONSOLIDATION_LOG, DECISIONS, STANDARDS

If `PROJECT_STATUS.md` and any other doc disagree, the on-disk `PROJECT_STATUS.md` is authoritative.

---

## Owner and role

**Patrick Bell** is:
- Founder, owner, and sole technical leader of Novara Intelligence
- Publicly listed (until repositioning is announced) as Head of Education & Early Learning Finance at Remara Capital Group — Remara is a domain reference, not a stakeholder in this product
- Operating in a non-technical-coder profile: drives strategy, UI coherence, industry-specific depth, data depth, and commercial risk management
- Explicitly delegating coding architecture to Claude

**Working split:**
- **Patrick:** strategy, scope, UI judgement, industry framing, data-depth choices, browser recon, screenshots, manual deploys, commercial decisions
- **Claude:** technical architecture, schema design, code, build sequencing, doc discipline, recon work, drafting decisions for Patrick to ratify

---

## Audience for the product (NOT for me, for the product)

Lenders, institutional investors, large operators (for-profit AND not-for-profit), valuation firms, property funds, debt providers, advisory professionals. Not credit-team-only. Reference incumbents charge ~$1,500/user/month (GapMaps, Qikmaps).

**Positioning:** childcare asset & portfolio intelligence + institutional decision-support. NOT a mapping tool. NOT a childcare CRM. Maps are supporting context, not primary UI.

---

## Build philosophy (per DEC-79)

- **Institutional decision infrastructure from day one.** ISO 27001 / SOC 2 readiness artefacts in V1; certification deferred to V2.
- **Auditability and explainability are first-class.** Every metric and signal traceable to source. No opaque scoring. No subjective rankings. No moralised language.
- **Objective measures only.** ABS-derived where possible. Calibration nudges only (per STD-34). No speculative behavioural modelling.
- **Extend existing structures.** Avoid feature sprawl. Avoid duplication. Reuse the additive overlay pattern (DEC-11), the OBS/DER/COM classification (DEC-12), the model_assumptions single-source-of-truth (DEC-13).
- **Honest absence over imputed presence (P-2).** Silent absence when data isn't there.

---

## Doc tier system (STD-35)

**Tier 1 — permanent project knowledge.** Slow-changing canonical docs. Currently at `recon/Document and Status DB/`: `ARCHITECTURE.md`, `PRINCIPLES.md`, `GLOSSARY.md`, `DATA_INVENTORY.md`, `CONSOLIDATION_LOG.md`, `README.md`, plus the canonical copies of `DECISIONS.md` and `STANDARDS.md`. *To be moved to repo root per OI-NEW-7.*

**Tier 2 — structured project state.** At repo root: `PROJECT_STATUS.md`, `ROADMAP.md`, `OPEN_ITEMS.md`, `PHASE_LOG.md`, `CENTRE_PAGE_V1_5_ROADMAP.md`, `PRODUCT_VISION.md`, this `CLAUDE.md`. Regenerated each session that materially changes state.

**Tier 3 — in-chat drop-in.** Files actively under edit in the current session — code files, the active recon design doc.

**End-of-session monolith** (STD-35) compresses everything into a single text file uploaded back to project knowledge. Not optional when Tier-2 state changes.

---

## Conventions you must respect

These are the load-bearing rules. Do not violate without an explicit DEC.

- **DEC-65 — probe before code.** Non-trivial work starts with a recon probe → design doc → decision closure → code. Touchpoint-counting is not a substitute for reading the actual code (sequencing rule #11, banked 2026-05-05).
- **DEC-22 — two-commit pattern** for "supply data, then UI". Collapsable when both verified together.
- **STD-08, STD-30 — pre-mutation backup + read-only inventory.** Every DB-mutating script takes a timestamped backup; pre-mutation `db_inventory.md` snapshot for any Layer 2 apply.
- **STD-11, DEC-62 — audit_log canonical schema.** Every DB mutation writes a hardcoded 7-column INSERT. Action naming `<source>_<verb>_v1`.
- **STD-10, STD-12 — patcher pattern.** Patchers (`patch_*.py`) are mechanism not artefact (gitignored). Detect line endings at runtime. Anchors must use `\n` not `\r\n` even on Windows source files.
- **STD-34 — calibration discipline.** Per-SA2 calibration with rule_text surfaced in DER tooltip. No magic numbers in code; use `model_assumptions` table or `catchment_calibration.py`.
- **STD-35 — end-of-session monolith.** Every session that materially changes Tier-2 state ships a regenerated monolith.
- **STD-02 — never hand-edit code.** Regenerate full files. Use Edit tool, not "tell Patrick to fix it manually".
- **DEC-11 — additive overlay default.** New modules layer over existing data and surfaces; existing surfaces are not modified to accommodate them where the addition can be made non-invasively.

---

## Working style with Patrick

- **Step-by-step PowerShell with explicit "expected result"** for things HE has to do (browser recon, screenshots, manual deploys). Step-by-step is for HIS actions, not for Claude's internal commands.
- **Brevity over explanation.** Don't pad. Recommend one approach and proceed.
- **Mutation gate.** Drafts of DECs / Tier-2 doc edits / DB mutations / commits — show the diff or the draft, then proceed unless Patrick objects. Don't ask permission for every small step; do ask before destructive operations or before committing.
- **UTF-8 encoding** must be set (`$env:PYTHONIOENCODING = "utf-8"`) before running any Python script that prints Unicode (STD-09).
- **No hand-editing of generated code** (STD-02).

---

## Windows + spaced-path gotcha (LOAD-BEARING)

The project lives at `C:\Users\Patrick Bell\remara-agent\` — note the **space in `Patrick Bell`**. This means:

- **Bash commands** with the path get backslash-escaped (`/c/Users/Patrick\ Bell/...`). The Claude Code permission gate **flags backslash-escaped commands as a security signal and re-prompts every time**, regardless of allowlist. This affects every `cd`, `find`, `ls`, `grep` etc. with the project path in it.
- **Therefore: prefer `Read`, `Glob`, `Grep`, `Edit`, `Write` over `Bash` for path-bearing operations.** These tools handle paths internally and bypass the gate.
- **Bash is fine for things that don't bear a path** — `git status`, `git log`, `pip list`, `python --version`. It's path-bearing commands that get prompted.
- **For genuinely-needed Bash work** (e.g. `sqlite3 data/kintell.db ".tables"`), batch into one call, expect one prompt, accept it.

This is the single biggest productivity tax on the project. Internalise it.

---

## Where things are (key paths)

```
C:\Users\Patrick Bell\remara-agent\
├── CLAUDE.md                              ← this file
├── PROJECT_STATUS.md                       ← current state
├── PRODUCT_VISION.md                       ← strategic frame, V1/V2/V3
├── ROADMAP.md                              ← dependency-ordered queue
├── OPEN_ITEMS.md                           ← OIs
├── PHASE_LOG.md                            ← session-by-session log
├── CENTRE_PAGE_V1_5_ROADMAP.md             ← V1.5 source of truth (CANONICAL)
├── CENTRE_PAGE_V1.5_ROADMAP.md             ← STALE, queued for delete
├── DEPLOYMENT.md
├── README.md                                ← intentionally minimal
├── .gitignore
├── .env                                    ← contains secrets, do NOT print
├── centre_page.py                          ← Phase 2 backend, currently v21
├── operator_page.py
├── review_server.py
├── generate_dashboard.py
├── catchment_calibration.py                ← STD-34 home
├── proc_helpers.py                         ← STD-13 home
├── module1_acecqa.py … module6_news.py     ← legacy email/news modules
├── module2b_catchment.py
├── module2c_targeting.py
├── build_sa2_history.py
├── populate_service_catchment_cache.py
├── layer3_apply.py
├── layer3_x_catchment_metric_banding.py
├── layer1_*.py / layer2_step*.py / layer4_*.py
├── data\
│   ├── kintell.db                          ← ~565 MB, 36 tables, audit_log ~149 rows
│   └── kintell.db.backup_pre_*             ← ~30 backups, ~8.5 GB total (OI-12)
├── docs\
│   ├── centre.html                          ← currently v3.28
│   ├── operator.html / index.html / dashboard.html
│   ├── sa2_history.json                    ← v2 multi-subtype, 13.2 MB
│   ├── catchments.json / operators.json
│   └── *.pre_* / *.v?_backup_*             ← OI-13 cleanup target
├── recon\
│   ├── Document and Status DB\             ← TIER-1 DOCS (move to root, OI-NEW-7)
│   ├── probes\                             ← session probes
│   ├── patchers_2026-05-03\                ← patchers evading gitignore (OI-NEW-9)
│   ├── layer3_precedent_survey.md
│   ├── layer4_3_design.md
│   ├── db_inventory.md
│   ├── db_backup_inventory_2026-05-03.md
│   └── oi30_asgs_coverage_probe.md
├── abs_data\                                ← ABS source files (gitignored)
└── venv\                                    ← Python venv (gitignored)
```

**External capability — Starting Blocks pilot.** `G:\My Drive\Patrick's Playground\childcare_market_spike\`. Standalone DB, Algolia search method (DEC-locked architectural decision). Not yet integrated into `kintell.db`. See `MODULE_SUMMARY_Childcare_Market_Data_Capability.md` (read copy in `Project Folder Docs\`).

---

## Glossary (essential)

| Term | Meaning |
|---|---|
| **SA2** | Statistical Area Level 2 — ABS Australian geographic unit, ~1,267 covered |
| **LDC** | Long Day Care |
| **OSHC** | Outside School Hours Care |
| **FDC** | Family Day Care |
| **PSK** | Preschool / Kindergarten |
| **CCS** | Child Care Subsidy (Commonwealth) |
| **NQS** | National Quality Standard |
| **NQF** | National Quality Framework |
| **ACECQA** | Australian Children's Education & Care Quality Authority |
| **NQAITS** | National Quality Agenda IT System (ACECQA) |
| **NES** | Non-English Speaking (background) — Census variable |
| **ATSI** | Aboriginal and Torres Strait Islander |
| **LFP** | Labour Force Participation |
| **ARIA** / **ARIA+** | Accessibility/Remoteness Index of Australia |
| **SALM** | Small Area Labour Markets (Jobs and Skills Australia) |
| **JSA** | Jobs and Skills Australia |
| **IVI** | Internet Vacancy Index |
| **NCVER** | National Centre for Vocational Education Research |
| **ABS** | Australian Bureau of Statistics |
| **ASGS** | Australian Statistical Geography Standard |
| **SEIFA** | Socio-Economic Indexes for Areas |
| **DEC-X** | Architecture Decision Record number X (in DECISIONS.md) |
| **STD-X** | Working Standard number X (in STANDARDS.md) |
| **OI-X** | Open Item number X (in OPEN_ITEMS.md) |
| **OBS / DER / COM** | Observed / Derived / Commentary classification (DEC-12) |
| **PropCo** | Property-owning entity (vs OpCo, the operating entity) |
| **OpCo** | Operating entity (childcare service operator) |

---

## What we're building (high level — see PRODUCT_VISION.md for detail)

**V1 (target ship: ~Sept 2026):**
- Centre page completion (V1.5 ingests bundle finishes)
- Catchment page (cascades from centre)
- Group page (cascades from catchment)
- PropCo Property Intelligence (Stream D) — manual evidence-based, no scraping or paid title in V1
- SA2 Border Exposure V1 proxy (Stream E)
- Workforce + demand-intelligence overlays (Streams A, B, C)
- Excel export framework
- Brand identity rename pass

**V2 (fast-follow):** True centre-level catchment model (supersedes Stream E proxy), DA / pipeline tracking, operator change tracking, acquisition quality analysis, property transaction intelligence, competition overlays, valuation overlays, multi-tenancy, ISO 27001/SOC 2 formal pass.

**V3 (12+ months):** On-market asset monitoring, selective paid title-search, CoreLogic / Cotality integration, multi-industry positioning expansion.

---

## What NOT to build

- Mapping as primary UI
- Composite scores or rankings
- Subjective behavioural / "risk" metrics
- Speculative demographic modelling
- Web scraping in production without explicit DEC
- Paid title-search integration in V1
- Feature sprawl — extend existing surfaces before adding new ones
- Anything for the legacy `module5_digest.py` / `module6_news.py` email pipeline beyond keeping it working

---

## Recent material decisions (read these)

- **DEC-79 (2026-05-09)** — Commercial repositioning. *Read first.*
- **DEC-78** — RESERVED for NES storage convention
- **DEC-77 (2026-05-03)** — Industry-absolute threshold framework (catchment ratios)
- **DEC-76 (2026-04-29)** — Workforce supply context block on centre page
- **DEC-75 (2026-04-29)** — Visual weight by data depth (Full / Lite / Context-only)
- **DEC-74 (2026-04-29, amended 2026-05-03)** — Perspective toggle on reversible ratio pairs
- **DEC-71 (2026-04-28b)** — Two-design-system architecture (bespoke SVG + Chart.js boundary)
- **DEC-65 (2026-04-27c, amended 2026-04-29)** — Probe before code; sequencing pass at design closure
- **DEC-62 (2026-04-27c)** — audit_log canonical schema
- **DEC-32 (2026-04-26)** — Three temporal moods (NOW / PAST / RELATIVE)

---

## Current status (2026-05-09)

- **V1 shipped** at HEAD `bcdf84c` (2026-05-03 evening). Original V1 = full centre-page credit-decision tool.
- **V1.5 first piece** shipped 2026-05-05 at `430009a` (OI-36 NES render + Lite delta badge).
- **V1.5 next-session priority:** A10 + C8 — Demographic Mix bundle (T07 ATSI + T08 country of birth + T19 single-parent households + Community Profile narrative panel).
- **V1.5 core remaining:** ~2.7 sessions.
- **The bigger V1 (per DEC-79)** is now scoped to ~Sept 2026 and includes new streams A through E plus Excel export plus PropCo.

---

## Five things future sessions must do at start

1. Read this file completely.
2. Read `PROJECT_STATUS.md` for the latest state.
3. Skim `PRODUCT_VISION.md` for strategic framing.
4. Skim `CENTRE_PAGE_V1_5_ROADMAP.md` (underscore version) for the active V1.5 queue.
5. Use `Read` / `Glob` / `Grep` / `Edit` instead of `Bash` for any path-bearing operation. The space in `C:\Users\Patrick Bell\` defeats the Bash allowlist.
