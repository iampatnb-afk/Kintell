# Open Items

Known bugs, open data quality issues, deferred fixes, and tracked residuals. This is the project's backlog of issues that are not active work but are not forgotten either.

Items are organised by severity, then by date opened. Closed items are moved to the bottom of their section with a resolution note. Items are removed from this file only when their fix is committed AND verified — partial fixes stay visible.

Last updated: 2026-04-29 (Layer 4.3 sub-pass 4.3.6: OI-23 closed).

---

## Active — data quality

### OI-01 — 18 services without lat/lng need geocoding fix
**Severity:** Medium · **Opened:** 2026-04-27c · **Decision:** DEC-63

18 services in `kintell.db` have no lat/lng. They cannot be assigned an `sa2_code` via point-in-polygon spatial join (Step 1b methodology). Their current `sa2_code` (if any) is postcode-derived, which is the superseded fallback (DEC-70).

**Fix path:** per-service address geocoding or manual lookup. ~½ session if undertaken systematically. Deferred to post-V1 per DEC-63. These services use postcode-derived `sa2_code` as fallback per DEC-70.

### OI-02 — 2 services at lat=0, lng=0 (null-island)
**Severity:** Medium · **Opened:** 2026-04-27c · **Decision:** DEC-63

Two services have `lat=0, lng=0`, which point-in-polygon resolves to nothing (or to a meaningless ocean location). Bad source data, not a polygon error.

**Fix path:** manual review and correction. Triage in one sitting (small enough). Deferred per DEC-63.

### OI-03 — 9 cross-state SA2 mismatches remain post-Step-1c
**Severity:** Low · **Opened:** 2026-04-28b · **Decision:** DEC-70

After Step 1c overwrite, 9 services remain where `services.state` disagrees with the assigned SA2's state. Five are at the Jervis Bay / NSW / ACT / Other Territories enclave boundary — postcode 2540 (Jervis Bay) is "Other Territories" for ABS while `services.state` may say ACT or NSW. This is not a polygon error; it is a data-classification ambiguity.

**Status:** documented as known-acceptable. No action required. Reviewed at next polygon-data refresh (likely on Census 2026 release).

### OI-04 — 43 services unchanged by Step 1c due to lat/lng (0,0)
**Severity:** Medium · **Opened:** 2026-04-28b · **Decision:** DEC-70 (extends DEC-63)

43 services were unchanged by Step 1c because their lat/lng is (0,0). 25 of these overlap with OI-01 + OI-02 (the 18+2 originally tracked). The remaining ~20 are new candidates for geocoding fix.

**Fix path:** combine with OI-01 / OI-02 in any geocoding session. Currently use Step 1's postcode-derived `sa2_code` as fallback.

### OI-05 — `service_catchment_cache` is empty (0 rows)
**Severity:** Tracking · **Opened:** 2026-04-28b

The `service_catchment_cache` table schema is in place (well-designed, per Layer 4.2 probe) but contains zero rows. Population is Layer 2.5 work, gated on Layer 4.3 calibration function landing.

**Status:** intentional pending-state, not a bug. Tracked here so cross-references to "the catchment cache" don't surprise future sessions.

### OI-06 — LFP source is Census-only (3 points)
**Severity:** Low · **Opened:** 2026-04-28b · **Updated:** 2026-04-29 (Thread B probe complete)

LFP (labour force participation) is currently derived from Census 2021 TSP only — 3 data points across 2011/2016/2021 (DEC-60). Per DEC-75, the LFP triplet now renders in **Lite** weight on the centre page (decile strip + chips + intent copy + as-at stamp; no trajectory chart) — three Census points is not a trajectory.

**Probe outcome (2026-04-29 — sub-pass 4.3.2):** SALM source publishes `participation_rate` alongside the existing `unemployment_rate` series in the same workbooks. The existing `abs_sa2_unemployment_quarterly` ingest captured `labour_force` (LFP numerator) at SA2 × quarter for ~60 quarters back to ~2010 but did not capture participation rate itself. **Conditional positive** — the data is available from source; ingest scope just needs extending. See `recon/layer4_3_sub_pass_4_3_2_probe.md`.

**Fix path (deferred to V1.5):** SALM-extended ingest, ~0.5–0.6 session. (1) Re-run SALM ingest pulling `participation_rate` column alongside existing series. (2) Layer 3 banding apply for `sa2_lfp_persons` against state-x-remoteness cohort per DEC-54. (3) `LAYER3_METRIC_META["sa2_lfp_persons"].row_weight` flips `lite` → `full` (~5 lines). (4) `LAYER4_TRAJECTORY_SOURCES` updated to point at SALM not Census TSP (~5 lines). LFP-persons promotes from LITE to FULL — trajectory chart returns, cohort histogram returns, trend-% label appears.

**Sex-disaggregated LFP (LFP_F / LFP_M) stays LITE permanently.** SALM publishes persons-only at SA2; sex disaggregation is Census 2021 TSP T33A-H, structurally 3 points. DEC-61's "do not reconcile cross-product Census rates" justifies LFP-persons SALM + LFP-F/M Census split as internally consistent.

Bundled with OI-19 in V1.5 — both pure-deepening ingests with similar cost/benefit profile.

### OI-07 — `participation_rate` not measured at SA2
**Severity:** Tracking · **Opened:** 2026-04-28b

The four catchment ratios (adjusted_demand, capture_rate, demand_supply, child_to_place) all depend on `participation_rate`, which is not directly measured at SA2 by ABS. Calibration is required. STD-34 locked 2026-04-29.

**Fix path:** Layer 4.3 sub-pass 4.3.4 (per ROADMAP.md). Calibration function (`catchment_calibration.py`) takes `(income_decile, female_lfp_pct, nes_share_pct, aria_band)` and returns `(rate, rule_text)`. Default 0.50, range [0.43, 0.55], nudges ±0.02 per documented input. Note: `nes_share_pct` is a documented input gap per OI-19 (NES ingest deferred to Layer 4.4).

### OI-08 — 19 synthetic SA2s in `sa2_cohort` have NULL ra_band
**Severity:** None (acceptable) · **Opened:** 2026-04-28

19 synthetic SA2s in `sa2_cohort` (no usual address / migratory / 'ZZZZZZZZZ') have NULL `ra_band` because they have no spatial location. They are not present in any source metric table, so Layer 3 reads naturally exclude them.

**Status:** no cleanup required. Documented for completeness.

---

## Active — product surface

### OI-09 — `sa2_under5_growth_5y` derived metric not in initial Layer 3 set
**Severity:** Low · **Opened:** 2026-04-28

`sa2_under5_growth_5y` was descoped from Layer 3 initial banding for tightness. ~30 lines in `layer3_apply.py` to add when needed. The centre page shows a placeholder for this metric.

**Fix path:** Add to `layer3_apply.py` when growth-as-leading-indicator becomes the next analytical priority.

### OI-10 — `provider_management_type` enum normalisation pending
**Severity:** Low · **Opened:** 2026-04-26

`provider_management_type` displays raw ACECQA values without normalisation. "Independent schools" (plural, ambiguous) appears alongside cleaner values like "Private for profit". A six-value enum mapping (similar to `ownership_type`'s, DEC-9) is the canonical fix.

**Fix path:** Phase 2.5 housekeeping. Small.

### OI-11 — `jsa_vacancy_rate` admitted to centre page in Context-only weight
**Severity:** None (intentional) · **Opened:** 2026-04-28b · **Updated:** 2026-04-29 · **Decision:** DEC-76

Originally tracked as a deferred Position-row metric on the centre page Labour Market card (state-level data, no SA2 peer cohort, would have rendered as DEFERRED placeholder). DEC-75 + DEC-76 close this differently: `jsa_vacancy_rate` moves to the Workforce supply context block (per DEC-76) in Context-only weight (per DEC-75) — single-fact line + intent copy + state-level sparkline, no band, no peer cohort.

**Status:** no longer tracked as a deferred-from-Position item; it is V1-rendered in the new block per DEC-76. This entry kept for traceability of the framing change.

---

## Active — operational

### OI-12 — Backup pruning needed in `data/`
**Severity:** Medium · **Opened:** 2026-04-28b

Cumulative DB backups in `data/` total ~5.0 GB. Approaching the threshold where a single git operation (which scans the working tree) can time out.

**Fix path:** P1.5 housekeeping task. Recommended retention: most recent 3 backups + the pre-major-mutation anchors (`pre_sa2_cohort`, `pre_layer3`, `pre_step1c`). Deletion is a manual `Remove-Item` on the older files; gitignored so no commit needed.

### OI-13 — Frontend file backups accumulate in `docs/`
**Severity:** Low · **Opened:** 2026-04-25d (DEC-28)

Patcher runs accumulate `docs/<file>.v?_backup_<ts>` files. Gitignored under `*.v?_backup_*` (DEC-31) so no commit pressure, but the working tree gets noisy.

**Fix path:** periodic manual purge. Low priority.

### OI-14 — Backfill audit for DD/MM/YYYY date parsing fix
**Severity:** Low · **Opened:** 2026-04-26

`centre_page.py` v1 had a date-parsing gap that misclassified brownfield centres as greenfield (Sparrow Bentley case). Fixed in v2. Open question: did any other code path (`operator_page.py`, `generate_dashboard.py`, growth/transfer time-series code) consume the same fields with a strict YYYY-MM-DD parser and silently produce the same misclassification?

**Fix path:** code-search audit, then targeted re-render of any affected operator pages.

### OI-15 — Backfill audit for ARIA+ format mismatch
**Severity:** Low · **Opened:** 2026-04-26

`services.aria_plus` stores label strings, not codes. `centre_page.py` v1 mapped only codes and produced "Unknown ARIA+ code (Major Cities of Australia)" labels. Fixed in v2 with bidirectional mapping. Open question: any other code consuming `aria_plus`.

**Fix path:** code-search audit. Low priority.

---

## Active — restructuring residuals

### OI-16 — DEC-29 verbatim text not recovered
**Severity:** Tracking · **Opened:** 2026-04-28

The original verbatim text of DEC-29 (Phase 1.7 Kintell → Novara rebrand) was not preserved in the recovered monolith chain. The 2026-04-26 and 2026-04-27c monoliths reference Decision 29 by ID but neither contains the body. The decision is currently marked `Status: Withdrawn` with a reconstructed body.

**Fix path:** if a recoverable monolith surfaces (e.g. `2026-04-25c.txt` or another interstitial), update DEC-29's body. Otherwise the current state is acceptable — the decision is withdrawn, so the reconstructed body is sufficient for historical context.

### OI-17 — `recon/layer4_3_design.md` v1.0 source verification
**Severity:** Tracking · **Opened:** 2026-04-28 · **Updated:** 2026-04-29

The Layer 4.3 design doc v1.0 was referenced extensively in the 2026-04-28b monolith but was not retrievable for the 2026-04-28 doc restructure. The §9 specification (the 6-doc structure proposal that the new doc set implements) was reconstructed from cross-references.

The 2026-04-29 design closure session (this work) regenerated `recon/layer4_3_design.md` as v1.1, absorbing G1+G2 closure (DEC-74), G3 lock (STD-34), G4 closure (OI-19 tracking), G5 addition (DEC-75), and Thread D (DEC-76). v1.1's §1–§5 unchanged sections are reconstructed from past-chat fragments rather than read directly from the v1.0 file in the repo.

**Fix path:** when next opening the repo for code work, diff `recon/layer4_3_design.md` v1.1 against any v1.0 still in git history; reconcile any divergence in unchanged sections. Low priority — the closures landed in the structured docs (DECISIONS, STANDARDS, OPEN_ITEMS, ROADMAP) are the canonical truth, so even if v1.1's reconstructed sections differ in phrasing from v1.0, the operative project state is preserved.

---

## Active — Layer 4.3 / 4.4 forward work (added 2026-04-29)

### OI-19 — Layer 4.4 ingests deferred (NES, parent-cohort 25–44, schools)
**Severity:** Medium · **Opened:** 2026-04-29 · **Decision:** DEC-74 closure context (Thread C of Layer 4.3 design); G4 closure

Layer 4.4 covers three new SA2-level ingests deferred from V1:

- **NES (Non-English Speaking) household share at SA2.** Required for the participation-rate calibration function's NES nudge — currently a documented gap (`nes_share_pct` input is None at all SA2s, so the calibration's NES branch never fires). Source: Census 2021 TSP T13 or equivalent.
- **Parent-cohort 25–44 at SA2.** Deepens the demand picture beyond raw under-5 count. Source: ABS ERP by single-year-of-age or 5-year band at SA2.
- **Schools data at SA2.** Informs kinder-penetration analysis affecting addressable market scoping (school-based kinder absorbs a share of the 3–4 cohort). Source: state education department cuts where available; gap-fill from MySchool or ACARA.

**Fix path:** Promote to V1.5 immediately after V1 ships. Each is its own probe → ingest → Layer 3 banding → Layer 4 render. ~1.5 sessions total combined.

### OI-20 — Workforce supply context enrichments
**Severity:** Low · **Opened:** 2026-04-29 · **Updated:** 2026-04-29 (Thread D probe complete) · **Decision:** DEC-76

V1.5 enrichments to the Workforce supply context block (DEC-76):

- **Direct SEEK scrape for per-SA2 vacancy density and salary.** Originally scoped as Catchment Explorer Phase 2. Lifts the workforce supply read from state-level (current JSA IVI) to catchment-level. Composite signal: high `supply_ratio` + high SEEK vacancy density at SA2 = double credit risk. Pickup triggers: (a) when SA2-level workforce signals become a tier of credit framing alongside the four catchment ratios in Layer 4.2-A; (b) if a SEEK API or partnership emerges that removes the scraper-engineering cost.
- **ANZSCO 4211 / 2411 advertised-wage data.** Wage pressure as a leading indicator of vacancy stress. Source: SEEK or JobOutlook. V1.5.

**Closed (2026-04-29):** ~~NCVER VET enrolments at SA2/remoteness for CHC30121 / CHC50121.~~ Probe complete (sub-pass 4.3.3) — data is already ingested in `training_completions` (768 rows, state × remoteness × qualification × year, 2019–2024 across all four CHC codes). Editorial disposition: **kept at Industry view per DEC-36.** State-level pipeline data lacks the current-tightness immediacy that DEC-76 admission requires; admitting it would dilute the credit-lens read on the Workforce supply context block. The data is preserved in DB at `training_completions`, ready for Industry-view consumption with the DEC-24 transition trough labelled. See `recon/layer4_3_sub_pass_4_3_3_probe.md`.

**Fix path:** V1.5 — promote SEEK and advertised-wage when triggers above resolve. Both stay as deferred enrichments without active queue pressure.

### OI-21 — Future centre-page tab: quality elements
**Severity:** Tracking · **Opened:** 2026-04-29

NQS quality detail and regulatory history currently render inline in the centre page NOW block. The user has flagged eventual move to a dedicated tab once the centre-page tabbing model is reviewed. The current inline rendering remains workable for V1.

**Fix path:** Not V1 or V1.5 — out of scope until the centre-page tabbing model is reviewed. Tabbing-model review is itself a not-yet-scoped piece of work; will likely follow the V1 ship and post-launch usage feedback.

### OI-22 — Future centre-page tab: ownership and corporate detail
**Severity:** Tracking · **Opened:** 2026-04-29

Ownership and corporate detail (cross-references into the operator graph, brand cluster context, group-level financial framing) currently surface via the operator-page link in the centre header. The user has flagged eventual move to a dedicated tab once the centre-page tabbing model is reviewed.

**Fix path:** Not V1 or V1.5 — out of scope until the centre-page tabbing model is reviewed. See OI-21 for the prerequisite work.

### OI-24 — Sub-pass dependency-ordering pass missing from design-closure protocol
**Severity:** Tracking · **Opened:** 2026-04-29 (continued) · **Decision:** DEC-65 (amended)

The Layer 4.3 design-closure session (2026-04-29) closed nine sub-passes but did not check whether their default ordering was dependency-optimised. The 2026-04-29 (continued) session caught the gap on Patrick's prompting — a renderer-only run could have shipped before data-plumbing sub-passes, surfacing best-practice rendering ~2.3 sessions earlier and eliminating retrofit risk on Layer 4.2-A catchment ratios and the parallel daily-rate integration. See `recon/PHASE_LOG.md` 2026-04-29 (continued) for the diagnosis.

DEC-65 (the Decision-65 pattern: probe → design doc → decisions closed → code) has been amended to include a dependency-ordered sequencing pass at design closure. The amendment is retroactive: any open multi-sub-pass plan that has not had a sequencing pass should have one run before the next sub-pass starts.

**Status:** structural gap closed by the DEC-65 amendment. This OI exists for traceability of the missed-then-caught protocol gap. No further action; close at next consolidation.

**Fix path:** none required — the protocol-level fix is the DEC-65 amendment. OI-24 is a marker, not active work.

---

## Closed

### OI-23 — Global trend-window bar disappears when Population card has no live data
**Severity:** Low · **Opened:** 2026-04-29 · **CLOSED 2026-04-29** · **Decision:** DEC-73 (extends)

Resolution: closed in Layer 4.3 sub-pass 4.3.6 (`centre.html` v3.4). `_renderTrajectoryRangeBar()` removed from inside `renderPopulationCard` and promoted to page level above both Position cards. Visibility gated on `_pageHasFullTrajectory(centre)` — render the bar whenever any Full-weight row on the page carries trajectory data; hide otherwise. Lite and Context-only rows have no trajectory by design and do not vote toward the gate. The unemployment per-chart 1Y/2Y override buttons (sub-pass 4.3.1) now sit beneath a globally-reachable control regardless of which Position card has data.

### OI-18 — Layer 4.3 design decisions G1–G4 + §9.4 awaiting closure
**Severity:** Medium · **Opened:** 2026-04-28b · **CLOSED 2026-04-29**

Resolution: closure session 2026-04-29 worked through all five threads.
- G1+G2 merged into the perspective-toggle pattern → **DEC-74**.
- G3 closed by locking STD-34 (calibration discipline).
- G4 closed by deferring Layer 4.4 to V1.5 → **OI-19** for explicit tracking.
- G5 added during the same session (visual weight by data depth) → **DEC-75**.
- Thread D added during the same session (workforce supply context block) → **DEC-76**.
- §9.4 (project doc restructuring) implicitly resolved by the 2026-04-28 restructure landing.

The closure also surfaced OI-20 (workforce supply context enrichments), OI-21 (future quality tab), and OI-22 (future ownership tab).

`recon/layer4_3_design.md` regenerated as v1.1 absorbing all closures. Layer 4.3 implementation now unblocked.

---

## Closed (pre-restructure)

Closed items from the prior monolith chain were captured at the time and are not re-listed here. Examples include:
- Individual cards "view centres on each side" bug (resolved in v4→v9 review.html refactor, ~2026-04-23)
- External-tools row "site:" chip URL synthesis bug (resolved in operator.html v5a, 2026-04-23)
- `.gitignore` `+.env` literal-plus bug (resolved in operator_page.py v5 commit `0a81de2`, 2026-04-23)
- Phase 2 silent bug: DD/MM/YYYY parsing (fixed in centre_page.py v2; remaining audit work tracked as OI-14)
- Phase 2 silent bug: ARIA+ format mismatch (fixed in centre_page.py v2; remaining audit work tracked as OI-15)

---

## How to use this file

**Adding an item.** Use the next sequential `OI-N` ID. Severity options: None (acceptable), Tracking (intentional pending state), Low, Medium, High. Include an `Opened:` date and a `Decision:` reference if applicable. State the fix path with effort estimate where known.

**Closing an item.** Move it to the "Closed" section. Add a `CLOSED YYYY-MM-DD` marker and a resolution note explaining what shipped or what other ID picked up the work. Do not delete.

**Severity escalation.** If an item's impact grows, edit the severity field and add a note explaining the escalation. Don't open a new item for the same underlying issue.

**Cross-references.** Items that originated from a decision should reference that decision's ID. Items that depend on another item's resolution should note the dependency.
