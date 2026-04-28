# Layer 3 Precedent Survey

_Generated: 2026-04-28T10:28:01_

Read-only catalogue of existing percentile / banding / cohort / composite-score conventions across the repo and DB. Per Decision 65: Layer 3 must adopt these where they exist rather than redesign.

**Sections:**
- A. DB evidence (column names, sample values, views with window funcs)
- B. Code evidence (per-keyword hits across the repo)
- C. Page-by-page heuristic grouping
- D. Open questions for Patrick (Decision 65 D1-D4)

---

## A. DB evidence

### A.1 Columns matching banding/percentile/score patterns

| Table | Column | Type | Non-null rows | Sample values |
|---|---|---|---:|---|
| `brands` | `pricing_tier` | TEXT | 0 | _(none)_ |
| `group_snapshots` | `weighted_avg_seifa_irsd` | REAL | 0 | _(none)_ |
| `nqs_history` | `aria` | TEXT | 785,857 | Major Cities of Australia, Inner Regional Australia, Outer Regional Australia, ... |
| `nqs_history` | `seifa` | TEXT | 767,088 | 10, 7, 4, 8, 9 |
| `service_catchment_cache` | `seifa_irsd` | INTEGER | 0 | _(none)_ |
| `service_catchment_cache` | `supply_band` | TEXT | 0 | _(none)_ |
| `services` | `aria_plus` | TEXT | 17,824 | Major Cities of Australia, Inner Regional Australia, Outer Regional Australia, ... |
| `services` | `seifa_decile` | INTEGER | 17,395 | 4, 8, 6, 3, 9 |
| `training_completions` | `remoteness_band` | TEXT | 768 | Major cities, Inner regional, Outer regional, Remote, Very remote |

### A.2 Tables/views with banding-flavoured names

_None found._

### A.3 Views with window functions (PERCENT_RANK / NTILE / RANK OVER)

_None found._

---

## B. Code evidence

### B.1 Hit counts by keyword (top files)

| Keyword | Hits | Files | Top files |
|---|---:|---:|---|
| aria | 85 | 25 | `build_historical_data.py` (5); `generate_dashboard.py` (5); `leads_catchment.json` (5) |
| band | 70 | 25 | `operator_page.py` (5); `remara_project_status_2026-04-26.txt` (5); `remara_project_status_2026-04-... |
| cohort | 21 | 9 | `layer2_step6_preflight.py` (5); `remara_project_status_2026-04-27c.txt` (5); `recon/layer2_step6_p... |
| composite | 32 | 12 | `propose_merges.py` (5); `remara_project_status_2026-04-27c.txt` (5); `review_server.py` (5) |
| decile | 77 | 24 | `index.html` (5); `leads_catchment.json` (5); `module2b_catchment.py` (5) |
| low_med_high | 2 | 1 | `remara_project_status_2026-04-27c.txt` (2) |
| ntile_sql | 6 | 2 | `remara_project_status_2026-04-27c.txt` (5); `layer2_step5b_prime_apply.py` (1) |
| percentile | 6 | 2 | `remara_project_status_2026-04-27c.txt` (5); `layer2_step5b_prime_apply.py` (1) |
| quintile | 1 | 1 | `remara_project_status_2026-04-27c.txt` (1) |
| rank | 17 | 6 | `docs/dashboard.html` (5); `docs/index.html` (5); `generate_dashboard.py` (2) |
| score | 79 | 27 | `generate_dashboard.py` (5); `generate_prospecting_page.py` (5); `leads_catchment.json` (5) |
| seifa | 93 | 27 | `ingest_nqs_snapshot.py` (5); `module2b_catchment.py` (5); `nqaits_xlsx_inspect.json` (5) |
| tier | 87 | 27 | `generate_dashboard.py` (5); `generate_prospecting_page.py` (5); `index.html` (5) |
| vs_peers | 3 | 1 | `remara_project_status_2026-04-27c.txt` (3) |
| z-score | 2 | 1 | `remara_project_status_2026-04-27c.txt` (2) |

### B.2 Per-keyword hits (capped at 5 per file)

#### `aria` - 85 hit(s)

| File | Line | Snippet |
|---|---:|---|
| `build_historical_data.py` | 14 | `  - ARIA zero-gap fix: Q2 2018–Q3 2021 set to null (not 0)` |
| `build_historical_data.py` | 50 | `# Quarters where ARIA source data is missing — set by_aria to None so charts` |
| `build_historical_data.py` | 221 | `        elif col.strip() == "ARIA+":` |
| `build_historical_data.py` | 222 | `            col_map["aria"] = col` |
| `build_historical_data.py` | 226 | `    # Also check explicit ARIA+ column` |
| `centre_page.py` | 45 | `# ARIA+ remoteness band labels. The aria_plus column stores label strings` |
| `centre_page.py` | 145 | `    """OBS. ARIA+ band lookup. v2: handles both label-form and code-form."""` |
| `centre_page.py` | 153 | `    # avoids the misleading 'Unknown ARIA+ code' wording for non-code data).` |
| `centre_page.py` | 363 | `        # --- CATCHMENT block (SEIFA + ARIA) ---` |
| `docs/_op_chunks/part2.txt` | 282 | `       Remoteness distribution renders real ARIA+ counts as a` |
| `docs/_op_chunks/part2.txt` | 460 | `  return `<span class="km-badge ${cls}${anchorCls}" tabindex="0" aria-label="${cls.toUpperCase()} metric â€” hover for methodology">${cls.t...` |
| `docs/_op_chunks/part2.txt` | 468 | `    <div class="methodology-legend" role="region" aria-label="Metric classification legend">` |
| `docs/_op_chunks/part4.txt` | 223 | `// â”€â”€ v5: Remoteness distribution (real ARIA+ data from Tier 2) â”€â”€â”€â”€` |
| `docs/_op_chunks/part4.txt` | 230 | `      <div class="placeholder">${htmlEscape(r.note \\|\\| "ARIA+ not present on services.")}` |
| `docs/_op_chunks/part4.txt` | 300 | `    ${unknown ? `<div style="margin-top:8px;font-size:11px;color:var(--text-mute);">${unknown} service${unknown===1?'':'s'} without ARIA+ v...` |
| `docs/centre.html` | 533 | `  return `<span class="km-badge ${cls}${anchorCls}" tabindex="0" aria-label="${cls.toUpperCase()} metric">${cls.toUpperCase()}${tipHtml}</s...` |
| `docs/centre.html` | 733 | `          ${renderBadge("OBS", { source: "ABS ARIA+ remoteness classification" }, true)}` |
| `docs/dashboard.html` | 684 | `            <div style="display:flex;gap:6px;flex-wrap:wrap" id="aria-filter-btns">` |
| `docs/dashboard.html` | 820 | `        <div id="aria-breakdown-cards" style="display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:16px">` |
| `docs/dashboard.html` | 823 | `            <strong style="color:var(--text)">ARIA+ Remoteness definitions:</strong>&nbsp;&nbsp;` |
| `docs/dashboard.html` | 1413 | `    const aria  = currentAriaFilter;` |
| `docs/dashboard.html` | 1434 | `        if (aria && ARIA_KEYS[aria]) parts.push(ARIA_KEYS[aria]);` |
| `docs/index.html` | 991 | `            <div style="display:flex;gap:6px;flex-wrap:wrap" id="aria-filter-btns">` |
| `docs/index.html` | 1144 | `        <div id="aria-breakdown-cards" style="display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:16px">` |
| `docs/index.html` | 1147 | `            <strong style="color:var(--text)">ARIA+ Remoteness definitions:</strong>&nbsp;&nbsp;` |
| `docs/index.html` | 1758 | `// Maps ARIA key → histData series key` |
| `docs/index.html` | 1773 | `function setAriaFilter(aria, el) {` |
| `docs/operator.html` | 1104 | `       Remoteness distribution renders real ARIA+ counts as a` |
| `docs/operator.html` | 1282 | `  return `<span class="km-badge ${cls}${anchorCls}" tabindex="0" aria-label="${cls.toUpperCase()} metric — hover for methodology">${cls.toU...` |
| `docs/operator.html` | 1290 | `    <div class="methodology-legend" role="region" aria-label="Metric classification legend">` |
| `docs/operator.html` | 2586 | `// ── v5: Remoteness distribution (real ARIA+ data from Tier 2) ────` |
| `docs/operator.html` | 2593 | `      <div class="placeholder">${htmlEscape(r.note \\|\\| "ARIA+ not present on services.")}` |
| `generate_dashboard.py` | 1725 | `            <div style="display:flex;gap:6px;flex-wrap:wrap" id="aria-filter-btns">` |
| `generate_dashboard.py` | 1878 | `        <div id="aria-breakdown-cards" style="display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:16px">` |
| `generate_dashboard.py` | 1881 | `            <strong style="color:var(--text)">ARIA+ Remoteness definitions:</strong>&nbsp;&nbsp;` |
| `generate_dashboard.py` | 2080 | `// Maps ARIA key → histData series key` |
| `generate_dashboard.py` | 2095 | `function setAriaFilter(aria, el) {{` |
| `index.html` | 559 | `                <p>• NQS rating distributions by state and ARIA</p>` |
| `ingest_nqs_snapshot.py` | 106 | `    "ARIA+",` |
| `ingest_nqs_snapshot.py` | 196 | `            "aria":          _to_text(row[col_ix["ARIA+"]]),` |
| `ingest_nqs_snapshot.py` | 319 | `            ("aria_plus",                 lambda r: r["aria"]),` |
| `ingest_nqs_snapshot.py` | 440 | `                    rec["lat"], rec["lng"], rec["aria"], rec["seifa"],` |
| `layer2_step4_nqaits_ingest.py` | 54 | `    "aria":                     ["ARIA", "ARIA+"],` |
| `layer2_step4_nqaits_ingest.py` | 91 | `    "aria", "seifa",` |
| `layer2_step4_nqaits_ingest.py` | 119 | `    aria                      TEXT,` |
| `layer2_step4_nqaits_ingest.py` | 336 | `                    cell_to_text(row[cols["aria"]]) if "aria" in cols and cols["aria"] < len(row) else None,` |
| `layer2_step4_nqaits_preflight_v2.py` | 22 | `    "aria":                     ["ARIA", "ARIA+"],` |
| `leads_catchment.json` | 325516 | `          "service_address": "1 ARIA BVD",` |
| `leads_catchment.json` | 364119 | `          "service_address": "1 ARIA BVD",` |
| `leads_catchment.json` | 366097 | `          "service_address": "1 ARIA BVD",` |
| `leads_catchment.json` | 889896 | `          "service_address": "1 ARIA BVD",` |
| `leads_catchment.json` | 902628 | `          "service_address": "1 ARIA BVD",` |
| `nqaits_xlsx_inspect.json` | 128 | `      "ARIA+",` |
| `nqaits_xlsx_inspect.json` | 233 | `      "ARIA+",` |
| `nqaits_xlsx_inspect.json` | 338 | `      "ARIA+",` |
| `nqaits_xlsx_inspect.json` | 443 | `      "ARIA+",` |
| `nqaits_xlsx_inspect.json` | 548 | `      "ARIA+",` |
| `nqs_xlsx_inspect.json` | 75 | `      "ARIA+",` |
| `operator_page.py` | 650 | `            "note": ("ARIA+ not populated on these services. "` |
| `operator_page.py` | 664 | `        "source":         "ACECQA ARIA+ via NQS Data Q4 2025",` |
| `operator_payload_snapshot.json` | 3450 | `      "source": "ACECQA ARIA+ via NQS Data Q4 2025"` |
| `operator_payload_snapshot.json` | 5590 | `      "source": "ACECQA ARIA+ via NQS Data Q4 2025"` |
| `property_owners.json` | 28624 | `          "address": "1 ARIA BVD",` |
| `recon/layer1_files_findings.md` | 108 | `    9. ARIA` |
| `recon/layer1_files_findings.md` | 143 | `    9. ARIA+` |
| `recon/layer1_files_findings.md` | 174 | `  - ARIA` |
| `recon/layer1_files_findings.md` | 207 | `  - ARIA+` |
| `recon/layer1_recon_findings.md` | 129 | `\\| ARIA / ARIA+ \\| Label string. Spelling drift — Q3 2013 uses `ARIA+`, Q1 2020 uses `ARIA`. Tier 2 already saw both code and label forms...` |
| `recon/layer1_recon_findings.md` | 143 | `'ARIA' -> aria` |
| `recon/layer1_recon_findings.md` | 144 | `'ARIA+' -> aria` |
| `recon/layer2_step4_nqaits_preflight.md` | 38 | `     39/50  'ARIA+' <-- DRIFT` |
| `recon/layer2_step4_nqaits_preflight.md` | 48 | `     11/50  'ARIA' <-- DRIFT` |
| `remara_project_status_2026-04-26.txt` | 17 | `an ARIA+ format mismatch that produced "Unknown ARIA+ code" labels.` |
| `remara_project_status_2026-04-26.txt` | 107 | `    cadence), places (approved + subtype), catchment (SEIFA + ARIA +` |
| `remara_project_status_2026-04-26.txt` | 145 | `      - Catchment: SEIFA decile + ARIA band + SA2 + Tier 3 cache` |
| `remara_project_status_2026-04-26.txt` | 256 | `2. ARIA+ format mismatch — services.aria_plus stores label strings,` |
| `remara_project_status_2026-04-26.txt` | 258 | `   "Unknown ARIA+ code (Major Cities of Australia)" labels. Fixed` |
| `tier2_diagnose.py` | 12 | `     (ARIA+, SEIFA, Lat/Lng, Service Sub Type, Final Report Sent Date)` |
| `tier2_diagnose.py` | 16 | `  5. Distribution of Service Sub Type and ARIA+ values (so we know` |
| `tier2_diagnose.py` | 46 | `    "ARIA+",` |
| `tier2_diagnose.py` | 175 | `    # ── ARIA+ distribution ──────────────────────────────────────` |
| `tier2_diagnose.py` | 176 | `    print("\n── ARIA+ distribution (full NQS file) ──")` |
| `validate_tier2.py` | 35 | `    # ARIA+ band distribution` |
| `validate_tier2.py` | 43 | `    print("  ARIA+ distribution:")` |
| `validate_tier2.py` | 82 | `        print(f"      ARIA={r[3]!r} SEIFA={r[4]} sub={r[5]!r}")` |

#### `band` - 70 hit(s)

| File | Line | Snippet |
|---|---:|---|
| `add_workforce_assumptions.py` | 42 | `            "age-band ratios:\n"` |
| `add_workforce_assumptions.py` | 47 | `            "revise this row if a specific operator's age-band data is loaded."` |
| `add_workforce_assumptions.py` | 51 | `            "(NQF age-band ratios: 1:4 / 1:5 / 1:11). Age-mix weighting from "` |
| `centre_page.py` | 45 | `# ARIA+ remoteness band labels. The aria_plus column stores label strings` |
| `centre_page.py` | 145 | `    """OBS. ARIA+ band lookup. v2: handles both label-form and code-form."""` |
| `docs/_op_chunks/part1.txt` | 509 | `  /* Histograms â€” places-band, generic horizontal */` |
| `docs/_op_chunks/part2.txt` | 281 | `       histogram + weighted decile + low/mid/high band split.` |
| `docs/_op_chunks/part2.txt` | 283 | `       5-band stacked bar with per-band chips. Both cards stop` |
| `docs/_op_chunks/part2.txt` | 299 | `       new Remoteness distribution placeholder (5-band ABS).` |
| `docs/_op_chunks/part3.txt` | 362 | `//      for supply bands / u5 / income until Tier 3 cache populates)` |
| `docs/_op_chunks/part3.txt` | 375 | `        a <b>1â€“10 decile histogram</b>, a <b>low/mid/high band split</b>,` |
| `docs/_op_chunks/part3.txt` | 377 | `        supply-band exposure once the SA2 catchment cache is populated (Tier 3).</span>` |
| `docs/_op_chunks/part3.txt` | 480 | `      Supply bands, weighted under-5 population and median income arrive when the` |
| `docs/_op_chunks/part4.txt` | 231 | `        <span class="will-show">Bands: Major Cities / Inner Regional / Outer` |
| `docs/_op_chunks/part4.txt` | 233 | `        Matches the ABS 5-band classification used on the Kintell industry panel.</span>` |
| `docs/_op_chunks/part4.txt` | 238 | `  // v5: canonical 5-band ordering + short display labels` |
| `docs/_op_chunks/part4.txt` | 261 | `  const bands  = r.bands \\|\\| {};` |
| `docs/_op_chunks/part4.txt` | 263 | `  const totalCentres = CANON.reduce((n, b) => n + (bands[b] \\|\\| 0), 0);` |
| `docs/operator.html` | 509 | `  /* Histograms — places-band, generic horizontal */` |
| `docs/operator.html` | 1103 | `       histogram + weighted decile + low/mid/high band split.` |
| `docs/operator.html` | 1105 | `       5-band stacked bar with per-band chips. Both cards stop` |
| `docs/operator.html` | 1121 | `       new Remoteness distribution placeholder (5-band ABS).` |
| `docs/operator.html` | 2057 | `//      for supply bands / u5 / income until Tier 3 cache populates)` |
| `docs/review.html` | 466 | `      <select id="f-band">` |
| `docs/review.html` | 467 | `        <option value="all" selected>all bands</option>` |
| `docs/review.html` | 553 | `function band(c) {` |
| `docs/review.html` | 723 | `  const bandVal  = document.getElementById("f-band").value;` |
| `docs/review.html` | 736 | `  // Show clusters when band filter allows hi (i.e. all or hi).` |
| `ingest_ncver_completions.py` | 105 | `# cells per state/year (4 programs × 5 remoteness bands), maximum` |
| `ingest_ncver_completions.py` | 263 | `        # Remoteness in this column → it's a real remoteness band, update context` |
| `layer2_step5b_prime_apply.py` | 421 | `                    "admin_support / total_jobs). Banded within state x "` |
| `layer2_step6_diag.py` | 193 | `        findings.append("- Will need to derive total by summing age bands "` |
| `migrate_schema_v0_4.py` | 7 | `  aria_plus                TEXT      -- ABS Remoteness 5-band string` |
| `migrate_schema_v0_4.py` | 50 | `    ("aria_plus",                "TEXT",    "ABS Remoteness 5-band string"),` |
| `migrate_schema_v0_5.py` | 24 | `                          occupancy bands, operating days, due-soon` |
| `module2c_targeting.py` | 16 | `  Centre count band      25 pts  (5-10 = 25, 3-4 or 11-12 = 15, 13-15 = 5)` |
| `operator_page.py` | 629 | `    bands = {label: 0 for label in ARIA_CANONICAL_BANDS}` |
| `operator_page.py` | 637 | `        if a in bands:` |
| `operator_page.py` | 638 | `            bands[a] += 1` |
| `operator_page.py` | 644 | `    populated_n = sum(bands.values())` |
| `operator_page.py` | 648 | `            "scheme":    "ABS Remoteness Structure (5-band)",` |
| `operator_payload_snapshot.json` | 3431 | `      "scheme": "ABS Remoteness Structure (5-band)",` |
| `operator_payload_snapshot.json` | 3432 | `      "bands": {` |
| `operator_payload_snapshot.json` | 5571 | `      "scheme": "ABS Remoteness Structure (5-band)",` |
| `operator_payload_snapshot.json` | 5572 | `      "bands": {` |
| `ownership_graph_schema_v0_2.sql` | 7 | `--      demographic averages, supply-band exposure using Panel 3` |
| `ownership_graph_schema_v0_2.sql` | 265 | `    -- supply exposure bands (Panel 3 thresholds)` |
| `property_owners.json` | 29752 | `          "entity_name": "FEDERATION UNIVERSITY AUSTRALIA PIPE BAND INC.",` |
| `recon/layer1_recon_findings.md` | 25 | `  0 / 18,223 active services. Every banding/catchment helper in` |
| `recon/layer1_recon_findings.md` | 107 | `\\| `module2b_catchment.py` \\| 30 KB \\| **MISPLACED** \\| Production script — postcode→SA2, SEIFA, supply ratio enrichment for `run_daily...` |
| `remara_project_status_2026-04-26.txt` | 12 | `PA chain, demographic trend, places/ADR banding, direct-competitor` |
| `remara_project_status_2026-04-26.txt` | 145 | `      - Catchment: SEIFA decile + ARIA band + SA2 + Tier 3 cache` |
| `remara_project_status_2026-04-26.txt` | 194 | `      - RELATIVE (banding within catchment / industry slice)` |
| `remara_project_status_2026-04-26.txt` | 332 | `              data-dependency: ingest first, banding helpers` |
| `remara_project_status_2026-04-26.txt` | 353 | `            Unblocks ADR data; until then ADR banding renders` |
| `remara_project_status_2026-04-27c.txt` | 16 | `now 99.89%). This was the hard prerequisite for Layer 3 banding —` |
| `remara_project_status_2026-04-27c.txt` | 17 | `banding within state-x-remoteness cohorts requires every centre to` |
| `remara_project_status_2026-04-27c.txt` | 60 | `    pages — banding conventions may already exist that Layer 3` |
| `remara_project_status_2026-04-27c.txt` | 81 | `    - Banding infrastructure — Layer 3 (NEXT)` |
| `remara_project_status_2026-04-27c.txt` | 86 | `      signal at SA2; required for Layer 3 banding completeness.` |
| `schema_dump.txt` | 143 | `    -- supply exposure bands (Panel 3 thresholds)` |
| `seed_model_assumptions.py` | 85 | `        "Maximum children per educator for the 0–24 months age band. "` |
| `seed_model_assumptions.py` | 95 | `        "Maximum children per educator for the 24–36 months age band. "` |
| `seed_model_assumptions.py` | 105 | `        "Maximum children per educator for the 36+ months age band. "` |
| `seed_model_assumptions.py` | 116 | `        "(low end of three-band display).",` |
| `seed_model_assumptions.py` | 126 | `        "(centre of three-band display).",` |
| `seed_workforce_metrics.py` | 54 | `            "NQF age-band ratios weighted to a typical LDC enrolment mix (or 1:15 "` |
| `validate_tier2.py` | 35 | `    # ARIA+ band distribution` |
| `validate_tier2.py` | 44 | `    for band, ct in aria_dist:` |
| `validate_tier2.py` | 45 | `        print(f"    {band:35} {ct}")` |

#### `cohort` - 21 hit(s)

| File | Line | Snippet |
|---|---:|---|
| `add_workforce_assumptions.py` | 39 | `            "Blended educator-to-child ratio across the 0-5 LDC cohort. Used to "` |
| `add_workforce_assumptions.py` | 69 | `            "OSHC cohorts. Revise per service_sub_type if a state-specific "` |
| `layer1_recheck.py` | 45 | `            print(f"\n  [searching for under-5 cohort columns]")` |
| `layer2_step5b_prime_apply.py` | 413 | `                    "should use stratified percentile cohorts (Decision 54) "` |
| `layer2_step5b_prime_apply.py` | 422 | `                    "remoteness cohort per Decision 54."` |
| `layer2_step6_preflight.py` | 37 | `# Under-5 cohort column indices documented in the status doc` |
| `layer2_step6_preflight.py` | 119 | `    findings.append("## C. Header row & under-5 cohort columns\n")` |
| `layer2_step6_preflight.py` | 144 | `    # Show first 6 columns (key cols) + the 3 under-5 cohort columns` |
| `layer2_step6_preflight.py` | 152 | `    findings.append("### Under-5 cohort columns "` |
| `layer2_step6_preflight.py` | 156 | `    print("Under-5 cohort columns:")` |
| `layer2_step6_spotcheck.py` | 44 | `print("Join sanity: first 5 services + 2024 SA2 under-5 cohort:")` |
| `recon/layer1_recon_findings.md` | 172 | `\\| 6 \\| ABS ERP at SA2 ingest → `abs_sa2_erp_annual`. Requires identifying which sheet inside `Population and People Database.xlsx` carri...` |
| `recon/layer2_step6_preflight.md` | 15 | `## C. Header row & under-5 cohort columns` |
| `recon/layer2_step6_preflight.md` | 30 | `### Under-5 cohort columns (per status doc: indices 12, 48, 84)` |
| `recon/layer2_step6_preflight.md` | 40 | `Showing column 0 (likely region code), column 1 (likely region name), and the 3 under-5 cohort columns.` |
| `remara_project_status_2026-04-26.txt` | 423 | `    - Filtered to under-5 cohort for ECEC demand modelling` |
| `remara_project_status_2026-04-27c.txt` | 17 | `banding within state-x-remoteness cohorts requires every centre to` |
| `remara_project_status_2026-04-27c.txt` | 368 | `    - SA2 LFP-females percentile vs same state-x-remoteness cohort` |
| `remara_project_status_2026-04-27c.txt` | 379 | `        state-x-remoteness cohort (Decision 54)` |
| `remara_project_status_2026-04-27c.txt` | 644 | `    cohort calculations.` |
| `remara_project_status_2026-04-27c.txt` | 658 | `    semantics, banding cutoffs, cohort definitions, or composite-` |

#### `composite` - 32 hit(s)

| File | Line | Snippet |
|---|---:|---|
| `apply_decisions.py` | 81 | `        "       to_type, to_id, composite_confidence, "` |
| `apply_decisions.py` | 92 | `        "composite_confidence": row[6],` |
| `apply_decisions.py` | 443 | `                 "composite_confidence >= ?"]` |
| `apply_decisions.py` | 453 | `               " ORDER BY composite_confidence DESC")` |
| `diag_harmony.py` | 4 | `    SELECT c.candidate_id, c.composite_confidence, c.status,` |
| `diag_harmony.py` | 12 | `     ORDER BY c.composite_confidence DESC` |
| `diagnose_centres_endpoint.py` | 8 | `    group, confidence in `composite_confidence`, brand inside` |
| `diagnose_centres_endpoint.py` | 45 | `               composite_confidence,` |
| `diagnose_centres_endpoint.py` | 50 | `        ORDER BY composite_confidence DESC, candidate_id ASC` |
| `diagnose_centres_endpoint.py` | 151 | `    print(f"composite_confidence : {conf}")` |
| `docs/_op_chunks/part3.txt` | 620 | `    <div class="placeholder">Bottom 5 centres by composite quality score.` |
| `docs/operator.html` | 2315 | `    <div class="placeholder">Bottom 5 centres by composite quality score.` |
| `docs/review.html` | 625 | `// v8: decompose the composite confidence into per-test rows so the` |
| `list_sparrow_candidates.py` | 4 | `    SELECT c.candidate_id, c.composite_confidence,` |
| `list_sparrow_candidates.py` | 11 | `     ORDER BY c.composite_confidence DESC` |
| `ownership_graph_schema_v0_2.sql` | 197 | `    composite_confidence  REAL    NOT NULL,        -- 0.0–1.0` |
| `propose_merges.py` | 10 | `Composite confidence (0.0–1.0):` |
| `propose_merges.py` | 242 | `                " composite_confidence, evidence_json, priority, status) "` |
| `propose_merges.py` | 258 | `          SUM(CASE WHEN composite_confidence >= 0.85 THEN 1 ELSE 0 END) AS hi,` |
| `propose_merges.py` | 259 | `          SUM(CASE WHEN composite_confidence >= 0.50` |
| `propose_merges.py` | 260 | `                   AND composite_confidence <  0.85 THEN 1 ELSE 0 END) AS md,` |
| `remara_project_status_2026-04-27c.txt` | 330 | `  - No composite scores — every number traceable to a labelled source.` |
| `remara_project_status_2026-04-27c.txt` | 378 | `      - Composite RWCI score, banded Low/Medium/High within` |
| `remara_project_status_2026-04-27c.txt` | 658 | `    semantics, banding cutoffs, cohort definitions, or composite-` |
| `remara_project_status_2026-04-27c.txt` | 782 | `   any shipped percentile, banding, cohort, or composite-score` |
| `remara_project_status_2026-04-27c.txt` | 803 | `    - Are there composite scores already in production? If so,` |
| `review_server.py` | 93 | `            where.append("c.composite_confidence >= ?")` |
| `review_server.py` | 96 | `            where.append("c.composite_confidence <= ?")` |
| `review_server.py` | 109 | `            SELECT c.candidate_id, c.composite_confidence, c.status,` |
| `review_server.py` | 118 | `             ORDER BY c.composite_confidence DESC, c.candidate_id` |
| `review_server.py` | 155 | `              c.candidate_id, c.composite_confidence,` |
| `schema_dump.txt` | 196 | `    composite_confidence  REAL    NOT NULL,        -- 0.0–1.0` |

#### `decile` - 77 hit(s)

| File | Line | Snippet |
|---|---:|---|
| `catchment_html.py` | 154 | `    irsd      = c.get("irsd_decile")` |
| `catchment_html.py` | 155 | `    irsad     = c.get("irsad_decile")` |
| `centre_page.py` | 365 | `            "seifa_decile": {` |
| `centre_page.py` | 367 | `                "value": r.get("seifa_decile"),` |
| `docs/_op_chunks/part2.txt` | 280 | `       Catchment section renders a SEIFA decile` |
| `docs/_op_chunks/part2.txt` | 281 | `       histogram + weighted decile + low/mid/high band split.` |
| `docs/_op_chunks/part3.txt` | 374 | `        <span class="will-show">Will show: <b>weighted SEIFA decile headline</b>,` |
| `docs/_op_chunks/part3.txt` | 375 | `        a <b>1â€“10 decile histogram</b>, a <b>low/mid/high band split</b>,` |
| `docs/_op_chunks/part3.txt` | 387 | `  const wd     = seifa.weighted_decile;` |
| `docs/_op_chunks/part3.txt` | 403 | `          <div title="Decile ${d}: ${n} centre${n===1?'':'s'}"` |
| `docs/_op_chunks/part3.txt` | 412 | `  // Weighted-decile interpretation` |
| `docs/catchments.json` | 1 | `[{"sa2_code": "212031555", "sa2_name": "CLYDE NORTH - NORTH", "pop_0_4": 1069, "pop_0_4_cagr": 4.31, "pop_growth_label": "strong_growth", "...` |
| `docs/centre.html` | 578 | `    { l: "SEIFA decile",    n: centre.catchment.seifa_decile.value ?? "—" },` |
| `docs/centre.html` | 722 | `        <span class="k">SEIFA decile</span>` |
| `docs/centre.html` | 724 | `          <b>${c.seifa_decile.value ?? "—"}</b>` |
| `docs/centre.html` | 725 | `          ${c.seifa_decile.value != null ? '<span style="color:var(--text-mute);font-size:11px;">/10</span>' : ""}` |
| `docs/index.html` | 2723 | `                <div class="stat-value" style="font-size:20px">${sa2.irsd_decile ? sa2.irsd_decile + '/10' : 'n/a'}</div>` |
| `docs/operator.html` | 1102 | `       Catchment section renders a SEIFA decile` |
| `docs/operator.html` | 1103 | `       histogram + weighted decile + low/mid/high band split.` |
| `docs/operator.html` | 2069 | `        <span class="will-show">Will show: <b>weighted SEIFA decile headline</b>,` |
| `docs/operator.html` | 2070 | `        a <b>1–10 decile histogram</b>, a <b>low/mid/high band split</b>,` |
| `docs/operator.html` | 2082 | `  const wd     = seifa.weighted_decile;` |
| `generate_dashboard.py` | 195 | `    def _ccs_insight(ccs_rate, irsd_decile):` |
| `generate_dashboard.py` | 294 | `                'irsd_decile':          c.get('irsd_decile'),` |
| `generate_dashboard.py` | 308 | `                'ccs_insight':          _ccs_insight(c.get('est_ccs_rate'), c.get('irsd_decile')),` |
| `generate_dashboard.py` | 3045 | `                <div class="stat-value" style="font-size:20px">${{sa2.irsd_decile ? sa2.irsd_decile + '/10' : 'n/a'}}</div>` |
| `index.html` | 715 | `    "irsd_decile": 10,` |
| `index.html` | 996 | `    "irsd_decile": 10,` |
| `index.html` | 1290 | `    "irsd_decile": 7,` |
| `index.html` | 1649 | `    "irsd_decile": 8,` |
| `index.html` | 1839 | `    "irsd_decile": 4,` |
| `ingest_nqs_snapshot.py` | 12 | `    lat, lng, aria_plus, seifa_decile, service_sub_type,` |
| `ingest_nqs_snapshot.py` | 275 | `        required = {"aria_plus", "seifa_decile", "service_sub_type",` |
| `ingest_nqs_snapshot.py` | 320 | `            ("seifa_decile",              lambda r: r["seifa"]),` |
| `ingest_nqs_snapshot.py` | 422 | `                "  seifa_decile             = COALESCE(?, seifa_decile), "` |
| `layer1_recon.py` | 90 | `    ("seifa_decile / sa2_code coverage on active services",` |
| `layer1_recon.py` | 92 | `               COUNT(seifa_decile) AS with_seifa,` |
| `leads_catchment.json` | 36 | `      "irsd_decile": 9,` |
| `leads_catchment.json` | 37 | `      "irsad_decile": 8,` |
| `leads_catchment.json` | 386 | `    "qikreport": "-- CATCHMENT REPORT: Cranbourne Daycare & Kindergarten Centre --\n  Suburb:          CLYDE, VIC\n  SA2:             CLYDE...` |
| `leads_catchment.json` | 422 | `      "irsd_decile": 9,` |
| `leads_catchment.json` | 423 | `      "irsad_decile": 8,` |
| `migrate_schema_v0_4.py` | 8 | `  seifa_decile             INTEGER   -- 1..10, nullable` |
| `migrate_schema_v0_4.py` | 51 | `    ("seifa_decile",             "INTEGER", "SEIFA decile 1..10"),` |
| `module2b_catchment.py` | 13 | `  - SEIFA IRSD + IRSAD deciles (socio-economic indicators)` |
| `module2b_catchment.py` | 63 | `IRSD_COL     = "SEIFA Index of relative socio-economic disadvantage (IRSD) - rank within Australia (decile)"` |
| `module2b_catchment.py` | 64 | `IRSAD_COL    = "SEIFA Index of relative socio-economic advantage and disadvantage (IRSAD) - rank within Australia (decile)"` |
| `module2b_catchment.py` | 140 | `def fee_sensitivity_label(irsd_decile: Optional[int], ccs_rate: float) -> str:` |
| `module2b_catchment.py` | 142 | `    Classify fee sensitivity based on IRSD decile and CCS rate.` |
| `operator_page.py` | 40 | `  - Tier 2 columns on services (aria_plus, seifa_decile,` |
| `operator_page.py` | 43 | `  - _compute_catchment uses services.seifa_decile directly;` |
| `operator_page.py` | 339 | `               s.aria_plus, s.seifa_decile, s.service_sub_type,` |
| `operator_page.py` | 382 | `         aria_plus, seifa_decile, sub_type,` |
| `operator_page.py` | 412 | `            "seifa_decile":             seifa_decile,` |
| `operator_payload_snapshot.json` | 578 | `        "seifa_decile": 7,` |
| `operator_payload_snapshot.json` | 616 | `        "seifa_decile": 3,` |
| `operator_payload_snapshot.json` | 654 | `        "seifa_decile": 7,` |
| `operator_payload_snapshot.json` | 692 | `        "seifa_decile": 5,` |
| `operator_payload_snapshot.json` | 730 | `        "seifa_decile": 8,` |
| `recon/layer1_db_findings.md` | 187 | `### seifa_decile / sa2_code coverage on active services` |
| `recon/layer1_db_findings.md` | 190 | `               COUNT(seifa_decile) AS with_seifa,` |
| `recon/layer1_files_findings.md` | 467 | `  \\|   - SEIFA IRSD + IRSAD deciles (socio-economic indicators)` |
| `recon/layer1_recon_findings.md` | 83 | `\\| `seifa_decile` NULL on active services \\| **828 / 18,223** \\| 4.5% — modest gap. Likely services in SA2s missing from the SEIFA-decil...` |
| `recon/layer1_recon_findings.md` | 128 | `\\| SEIFA \\| Decile (numeric or string) \\|` |
| `remara_project_status_2026-04-26.txt` | 138 | `      - Quick-fact strip: places, subtype, SEIFA decile, remoteness` |
| `remara_project_status_2026-04-26.txt` | 145 | `      - Catchment: SEIFA decile + ARIA band + SA2 + Tier 3 cache` |
| `remara_project_status_2026-04-26.txt` | 271 | `   NULL seifa_decile despite being in suburban Brisbane. Likely` |
| `remara_project_status_2026-04-26.txt` | 377 | `    - SQL: COUNT seifa_decile NULL vs total active services` |
| `remara_project_status_2026-04-26.txt` | 447 | `          "decile": 1..10,` |
| `remara_project_status_2026-04-27c.txt` | 802 | `      quintile? decile? specific thresholds?)` |
| `remara_project_status_2026-04-27c.txt` | 810 | `      "percentile", "rank", "cohort", "band", "decile", etc.` |
| `tier2_diagnose.py` | 204 | `                print(f"    decile {k:>2}      {sdist[k]:>6}")` |
| `validate_tier2.py` | 16 | `               SUM(CASE WHEN seifa_decile IS NOT NULL THEN 1 ELSE 0 END) AS seifa_n,` |
| `validate_tier2.py` | 47 | `    # SEIFA decile distribution` |
| `validate_tier2.py` | 49 | `        SELECT seifa_decile, COUNT(*)` |
| `validate_tier2.py` | 53 | `         GROUP BY seifa_decile ORDER BY seifa_decile` |
| `validate_tier2.py` | 55 | `    print("  SEIFA decile distribution:")` |

#### `low_med_high` - 2 hit(s)

| File | Line | Snippet |
|---|---:|---|
| `remara_project_status_2026-04-27c.txt` | 378 | `      - Composite RWCI score, banded Low/Medium/High within` |
| `remara_project_status_2026-04-27c.txt` | 801 | `    - What banding cutoffs / labels are used (Low/Medium/High?` |

#### `ntile_sql` - 6 hit(s)

| File | Line | Snippet |
|---|---:|---|
| `layer2_step5b_prime_apply.py` | 413 | `                    "should use stratified percentile cohorts (Decision 54) "` |
| `remara_project_status_2026-04-27c.txt` | 23 | `percentile" position are both now data-feasible.` |
| `remara_project_status_2026-04-27c.txt` | 326 | `  Operator / Centre v1 already define percentile or band semantics` |
| `remara_project_status_2026-04-27c.txt` | 343 | `    - SA2 under-5 percentile vs all SA2s in same state` |
| `remara_project_status_2026-04-27c.txt` | 344 | `    - SA2 under-5 growth percentile vs same remoteness band` |
| `remara_project_status_2026-04-27c.txt` | 345 | `    - SA2 births percentile (Step 8 - DONE; banding pending Layer 3)` |

#### `percentile` - 6 hit(s)

| File | Line | Snippet |
|---|---:|---|
| `layer2_step5b_prime_apply.py` | 413 | `                    "should use stratified percentile cohorts (Decision 54) "` |
| `remara_project_status_2026-04-27c.txt` | 23 | `percentile" position are both now data-feasible.` |
| `remara_project_status_2026-04-27c.txt` | 326 | `  Operator / Centre v1 already define percentile or band semantics` |
| `remara_project_status_2026-04-27c.txt` | 343 | `    - SA2 under-5 percentile vs all SA2s in same state` |
| `remara_project_status_2026-04-27c.txt` | 344 | `    - SA2 under-5 growth percentile vs same remoteness band` |
| `remara_project_status_2026-04-27c.txt` | 345 | `    - SA2 births percentile (Step 8 - DONE; banding pending Layer 3)` |

#### `quintile` - 1 hit(s)

| File | Line | Snippet |
|---|---:|---|
| `remara_project_status_2026-04-27c.txt` | 802 | `      quintile? decile? specific thresholds?)` |

#### `rank` - 17 hit(s)

| File | Line | Snippet |
|---|---:|---|
| `docs/dashboard.html` | 282 | `.rank {` |
| `docs/dashboard.html` | 848 | `            <td class='rank'>1</td>` |
| `docs/dashboard.html` | 856 | `            <td class='rank'>2</td>` |
| `docs/dashboard.html` | 864 | `            <td class='rank'>3</td>` |
| `docs/dashboard.html` | 872 | `            <td class='rank'>4</td>` |
| `docs/index.html` | 280 | `.rank {` |
| `docs/index.html` | 1172 | `            <td class='rank'>1</td>` |
| `docs/index.html` | 1180 | `            <td class='rank'>2</td>` |
| `docs/index.html` | 1188 | `            <td class='rank'>3</td>` |
| `docs/index.html` | 1196 | `            <td class='rank'>4</td>` |
| `generate_dashboard.py` | 714 | `            <td class='rank'>{i}</td>` |
| `generate_dashboard.py` | 1014 | `.rank {{` |
| `module2b_catchment.py` | 63 | `IRSD_COL     = "SEIFA Index of relative socio-economic disadvantage (IRSD) - rank within Australia (decile)"` |
| `module2b_catchment.py` | 64 | `IRSAD_COL    = "SEIFA Index of relative socio-economic advantage and disadvantage (IRSAD) - rank within Australia (decile)"` |
| `module2c_targeting.py` | 7 | `and outputs a ranked target list.` |
| `remara_project_status_2026-04-27c.txt` | 798 | `    - Which metrics carry a percentile, band, or rank?` |
| `remara_project_status_2026-04-27c.txt` | 810 | `      "percentile", "rank", "cohort", "band", "decile", etc.` |

#### `score` - 79 hit(s)

| File | Line | Snippet |
|---|---:|---|
| `centre_page.py` | 224 | `    """OBS. Quality assessment area scores qa1..qa7, only those populated."""` |
| `centre_page.py` | 381 | `        # --- QA SCORES block ---` |
| `check_module4.py` | 13 | `    print(f'  {p["entity_name"]} ABN:{p["abn"]} score:{p["score"]}')` |
| `cleanup.py` | 34 | `    "Hot &amp; warm targets, filterable by state / score / centre count"` |
| `docs/_op_chunks/part3.txt` | 620 | `    <div class="placeholder">Bottom 5 centres by composite quality score.` |
| `docs/catchments.json` | 1 | `[{"sa2_code": "212031555", "sa2_name": "CLYDE NORTH - NORTH", "pop_0_4": 1069, "pop_0_4_cagr": 4.31, "pop_growth_label": "strong_growth", "...` |
| `docs/centre.html` | 251 | `  /* QA scores grid */` |
| `docs/centre.html` | 759 | `        <div class="qa-empty">No quality assessment scores on record.</div>` |
| `docs/dashboard.html` | 843 | `                        <th class="text-center">Score</th>` |
| `docs/dashboard.html` | 1652 | `                <span style="font-family:var(--mono);font-size:11px">Score: ${op.score}</span>` |
| `docs/index.html` | 906 | `.score {` |
| `docs/index.html` | 1167 | `                        <th class="text-center">Score</th>` |
| `docs/index.html` | 2031 | `                <span style="font-family:var(--mono);font-size:11px">Score: ${op.score}</span>` |
| `docs/index.html` | 2613 | `                <span style="font-size:11px;font-weight:600">Quality score: ${nqs.quality_score != null ? nqs.quality_score + '/100' : 'n/a...` |
| `docs/operator.html` | 2315 | `    <div class="placeholder">Bottom 5 centres by composite quality score.` |
| `docs/operators.json` | 1 | `[{"legal_name": "Cranbourne Day Care and Kindergarten Centre Pty Ltd", "tier": "hot", "score": 100, "n_centres": 7, "states": ["VIC"], "is_...` |
| `docs/review.html` | 627 | `// Matches the scoring logic in propose_merges.py — if that changes,` |
| `generate_dashboard.py` | 224 | `        score = round((exc*100 + mtg*75 + wtn*50) / rated, 1) if rated > 0 else None` |
| `generate_dashboard.py` | 229 | `            "quality_score": score,` |
| `generate_dashboard.py` | 326 | `            'score':             record.get('score'),` |
| `generate_dashboard.py` | 580 | `            "score":       op.get("score", 0),` |
| `generate_dashboard.py` | 709 | `        score    = op.get("score", 0)` |
| `generate_prospecting_page.py` | 29 | `def score_bar(score: int) -> str:` |
| `generate_prospecting_page.py` | 30 | `    pct = min(score, 100)` |
| `generate_prospecting_page.py` | 34 | `    </div> <span style="font-size:11px;color:#555">{score}</span>"""` |
| `generate_prospecting_page.py` | 44 | `        score      = op.get("score", 0)` |
| `generate_prospecting_page.py` | 95 | `                parts = [f"{f['name'][:30]} ({f['score']:.0f}%)" for f in fuzzy[:2]]` |
| `leads_catchment.json` | 12 | `    "score": 100,` |
| `leads_catchment.json` | 398 | `    "score": 100,` |
| `leads_catchment.json` | 784 | `    "score": 100,` |
| `leads_catchment.json` | 1605 | `    "score": 100,` |
| `leads_catchment.json` | 2426 | `    "score": 100,` |
| `lookup_operator.py` | 130 | `        score  = fuzz.token_set_ratio(core, entity.lower())` |
| `lookup_operator.py` | 131 | `        if score < 60 or abn == base_abn:` |
| `lookup_operator.py` | 136 | `            "score":                score,` |
| `lookup_operator.py` | 143 | `    related.sort(key=lambda x: x["score"], reverse=True)` |
| `lookup_operator.py` | 202 | `        "score":               op.get("score", 0),` |
| `module2b_catchment.py` | 467 | `    for _, score, idx in matches:` |
| `module2b_catchment.py` | 468 | `        if score < FUZZY_THRESHOLD:` |
| `module2b_catchment.py` | 471 | `        row["match_score"] = score` |
| `module2c_targeting.py` | 2 | `module2c_targeting.py — Operator Group Scoring & Target List` |
| `module2c_targeting.py` | 6 | `tiered matching, scores each group against Remara target criteria,` |
| `module2c_targeting.py` | 15 | `Scoring (100 pts):` |
| `module2c_targeting.py` | 24 | `  operators_target_list.json   — all for-profit groups with 2+ centres, scored` |
| `module2c_targeting.py` | 25 | `  operators_hot_targets.json   — score >= 60, ready for outreach` |
| `module3_da_portals.py` | 369 | `    # Cross-reference and score` |
| `module4_property.py` | 172 | `        score       = fuzz.token_set_ratio(core, entity_name.lower())` |
| `module4_property.py` | 174 | `        if score < 60 or abn == base_abn:` |
| `module4_property.py` | 182 | `            "score":        score,` |
| `module4_property.py` | 188 | `    # Sort by score descending` |
| `module4_property.py` | 189 | `    related.sort(key=lambda x: x["score"], reverse=True)` |
| `module5_digest.py` | 158 | `        "Hot &amp; warm targets, filterable by state / score / centre count"` |
| `module5_export.txt` | 165 | `        "<div style='margin-top:20px;padding:12px 16px;background:#2c3e50;border-radius:6px;text-align:center'><a href='data/operators_pros...` |
| `operators_hot_targets.json` | 14 | `        "score": 75.40983606557377,` |
| `operators_hot_targets.json` | 20 | `        "score": 80.85106382978724,` |
| `operators_hot_targets.json` | 26 | `        "score": 75.0,` |
| `operators_hot_targets.json` | 32 | `        "score": 75.0,` |
| `operators_hot_targets.json` | 38 | `        "score": 79.16666666666667,` |
| `operators_target_list.json` | 14 | `        "score": 75.40983606557377,` |
| `operators_target_list.json` | 20 | `        "score": 80.85106382978724,` |
| `operators_target_list.json` | 26 | `        "score": 75.0,` |
| `operators_target_list.json` | 32 | `        "score": 75.0,` |
| `operators_target_list.json` | 38 | `        "score": 79.16666666666667,` |
| `operators_target_list_test.json` | 14 | `        "score": 75.40983606557377,` |
| `operators_target_list_test.json` | 20 | `        "score": 80.85106382978724,` |
| `operators_target_list_test.json` | 26 | `        "score": 75.0,` |
| `operators_target_list_test.json` | 32 | `        "score": 75.0,` |
| `operators_target_list_test.json` | 38 | `        "score": 79.16666666666667,` |
| `property_owners.json` | 28 | `      "score": 100,` |
| `property_owners.json` | 43 | `          "score": 100.0,` |
| `property_owners.json` | 51 | `          "score": 97.5,` |
| `property_owners.json` | 59 | `          "score": 95.1219512195122,` |
| `property_owners.json` | 67 | `          "score": 91.42857142857143,` |
| `remara_project_status_2026-04-27c.txt` | 330 | `  - No composite scores — every number traceable to a labelled source.` |
| `remara_project_status_2026-04-27c.txt` | 378 | `      - Composite RWCI score, banded Low/Medium/High within` |
| `remara_project_status_2026-04-27c.txt` | 659 | `    score conventions for shared metrics. Layer 3 must adopt those` |
| `remara_project_status_2026-04-27c.txt` | 670 | `          b. RWCI weighting: equal-weight z-scored inputs,` |
| `remara_project_status_2026-04-27c.txt` | 782 | `   any shipped percentile, banding, cohort, or composite-score` |
| `run_daily.py` | 9 | `  4. module2c_targeting.py      — Operator group scoring` |

#### `seifa` - 93 hit(s)

| File | Line | Snippet |
|---|---:|---|
| `centre_page.py` | 363 | `        # --- CATCHMENT block (SEIFA + ARIA) ---` |
| `centre_page.py` | 365 | `            "seifa_decile": {` |
| `centre_page.py` | 367 | `                "value": r.get("seifa_decile"),` |
| `docs/_op_chunks/part2.txt` | 263 | `       "SEIFA Â· places-weighted". Histogram gets 22px of top margin` |
| `docs/_op_chunks/part2.txt` | 280 | `       Catchment section renders a SEIFA decile` |
| `docs/_op_chunks/part3.txt` | 361 | `// â”€â”€ Catchment section (v5: renders real SEIFA, keeps placeholders` |
| `docs/_op_chunks/part3.txt` | 365 | `  const seifa = c.seifa \\|\\| {};` |
| `docs/_op_chunks/part3.txt` | 368 | `  // If neither SEIFA nor the old cache has anything, show placeholder` |
| `docs/_op_chunks/part3.txt` | 369 | `  if (!seifa.populated && !c.cache_populated) {` |
| `docs/_op_chunks/part3.txt` | 374 | `        <span class="will-show">Will show: <b>weighted SEIFA decile headline</b>,` |
| `docs/centre.html` | 578 | `    { l: "SEIFA decile",    n: centre.catchment.seifa_decile.value ?? "—" },` |
| `docs/centre.html` | 722 | `        <span class="k">SEIFA decile</span>` |
| `docs/centre.html` | 724 | `          <b>${c.seifa_decile.value ?? "—"}</b>` |
| `docs/centre.html` | 725 | `          ${c.seifa_decile.value != null ? '<span style="color:var(--text-mute);font-size:11px;">/10</span>' : ""}` |
| `docs/centre.html` | 726 | `          ${renderBadge("OBS", { source: "ABS SEIFA, joined via SA2" }, true)}` |
| `docs/index.html` | 2722 | `                <div class="stat-label">SEIFA (IRSD)</div>` |
| `docs/operator.html` | 1085 | `       "SEIFA · places-weighted". Histogram gets 22px of top margin` |
| `docs/operator.html` | 1102 | `       Catchment section renders a SEIFA decile` |
| `docs/operator.html` | 2056 | `// ── Catchment section (v5: renders real SEIFA, keeps placeholders` |
| `docs/operator.html` | 2060 | `  const seifa = c.seifa \\|\\| {};` |
| `docs/operator.html` | 2063 | `  // If neither SEIFA nor the old cache has anything, show placeholder` |
| `generate_dashboard.py` | 79 | `    seifa_desc = irsd_label.capitalize() if irsd_label else ""` |
| `generate_dashboard.py` | 82 | `    parts = [p for p in [seifa_desc, demand_desc, supply_desc] if p]` |
| `generate_dashboard.py` | 3044 | `                <div class="stat-label">SEIFA (IRSD)</div>` |
| `ingest_nqs_snapshot.py` | 12 | `    lat, lng, aria_plus, seifa_decile, service_sub_type,` |
| `ingest_nqs_snapshot.py` | 105 | `    "SEIFA",` |
| `ingest_nqs_snapshot.py` | 142 | `def _to_seifa(v):` |
| `ingest_nqs_snapshot.py` | 143 | `    """SEIFA: integer 1..10, or None. '-', 0, '', NULL all → None."""` |
| `ingest_nqs_snapshot.py` | 195 | `            "seifa":         _to_seifa(row[col_ix["SEIFA"]]),` |
| `layer1_recon.py` | 90 | `    ("seifa_decile / sa2_code coverage on active services",` |
| `layer1_recon.py` | 92 | `               COUNT(seifa_decile) AS with_seifa,` |
| `layer2_step4_nqaits_ingest.py` | 53 | `    "seifa":                    ["SEIFA"],` |
| `layer2_step4_nqaits_ingest.py` | 91 | `    "aria", "seifa",` |
| `layer2_step4_nqaits_ingest.py` | 120 | `    seifa                     TEXT,` |
| `layer2_step4_nqaits_ingest.py` | 337 | `                    cell_to_text(row[cols["seifa"]]) if "seifa" in cols and cols["seifa"] < len(row) else None,` |
| `layer2_step4_nqaits_preflight_v2.py` | 21 | `    "seifa":                    ["SEIFA"],` |
| `migrate_schema_v0_4.py` | 8 | `  seifa_decile             INTEGER   -- 1..10, nullable` |
| `migrate_schema_v0_4.py` | 51 | `    ("seifa_decile",             "INTEGER", "SEIFA decile 1..10"),` |
| `module2b_catchment.py` | 13 | `  - SEIFA IRSD + IRSAD deciles (socio-economic indicators)` |
| `module2b_catchment.py` | 55 | `SEIFA_FILE   = ABS_DIR / "Family and Community Database.xlsx"` |
| `module2b_catchment.py` | 63 | `IRSD_COL     = "SEIFA Index of relative socio-economic disadvantage (IRSD) - rank within Australia (decile)"` |
| `module2b_catchment.py` | 64 | `IRSAD_COL    = "SEIFA Index of relative socio-economic advantage and disadvantage (IRSAD) - rank within Australia (decile)"` |
| `module2b_catchment.py` | 497 | `def seifa_label(decile: Optional[int]) -> str:` |
| `nqaits_xlsx_inspect.json` | 127 | `      "SEIFA",` |
| `nqaits_xlsx_inspect.json` | 232 | `      "SEIFA",` |
| `nqaits_xlsx_inspect.json` | 337 | `      "SEIFA",` |
| `nqaits_xlsx_inspect.json` | 442 | `      "SEIFA",` |
| `nqaits_xlsx_inspect.json` | 547 | `      "SEIFA",` |
| `nqs_xlsx_inspect.json` | 74 | `      "SEIFA",` |
| `operator_page.py` | 40 | `  - Tier 2 columns on services (aria_plus, seifa_decile,` |
| `operator_page.py` | 43 | `  - _compute_catchment uses services.seifa_decile directly;` |
| `operator_page.py` | 339 | `               s.aria_plus, s.seifa_decile, s.service_sub_type,` |
| `operator_page.py` | 382 | `         aria_plus, seifa_decile, sub_type,` |
| `operator_page.py` | 412 | `            "seifa_decile":             seifa_decile,` |
| `operator_payload_snapshot.json` | 578 | `        "seifa_decile": 7,` |
| `operator_payload_snapshot.json` | 616 | `        "seifa_decile": 3,` |
| `operator_payload_snapshot.json` | 654 | `        "seifa_decile": 7,` |
| `operator_payload_snapshot.json` | 692 | `        "seifa_decile": 5,` |
| `operator_payload_snapshot.json` | 730 | `        "seifa_decile": 8,` |
| `ownership_graph_schema_v0_2.sql` | 263 | `    weighted_avg_seifa_irsd         REAL,` |
| `ownership_graph_schema_v0_2.sql` | 319 | `    seifa_irsd                INTEGER,` |
| `recon/layer1_db_findings.md` | 81 | `    - weighted_avg_seifa_irsd             REAL            pk=0 notnull=0` |
| `recon/layer1_db_findings.md` | 117 | `    - seifa_irsd                          INTEGER         pk=0 notnull=0` |
| `recon/layer1_db_findings.md` | 187 | `### seifa_decile / sa2_code coverage on active services` |
| `recon/layer1_db_findings.md` | 190 | `               COUNT(seifa_decile) AS with_seifa,` |
| `recon/layer1_db_findings.md` | 195 | `  total \\| with_seifa \\| with_sa2` |
| `recon/layer1_files_findings.md` | 107 | `    8. SEIFA` |
| `recon/layer1_files_findings.md` | 142 | `    8. SEIFA` |
| `recon/layer1_files_findings.md` | 201 | `  - SEIFA` |
| `recon/layer1_files_findings.md` | 234 | `  - SEIFA` |
| `recon/layer1_files_findings.md` | 467 | `  \\|   - SEIFA IRSD + IRSAD deciles (socio-economic indicators)` |
| `recon/layer1_recon_findings.md` | 83 | `\\| `seifa_decile` NULL on active services \\| **828 / 18,223** \\| 4.5% — modest gap. Likely services in SA2s missing from the SEIFA-decil...` |
| `recon/layer1_recon_findings.md` | 107 | `\\| `module2b_catchment.py` \\| 30 KB \\| **MISPLACED** \\| Production script — postcode→SA2, SEIFA, supply ratio enrichment for `run_daily...` |
| `recon/layer1_recon_findings.md` | 128 | `\\| SEIFA \\| Decile (numeric or string) \\|` |
| `recon/layer2_step4_nqaits_preflight.md` | 26 | `     50/50  'SEIFA'` |
| `remara_project_status_2026-04-26.txt` | 107 | `    cadence), places (approved + subtype), catchment (SEIFA + ARIA +` |
| `remara_project_status_2026-04-26.txt` | 138 | `      - Quick-fact strip: places, subtype, SEIFA decile, remoteness` |
| `remara_project_status_2026-04-26.txt` | 145 | `      - Catchment: SEIFA decile + ARIA band + SA2 + Tier 3 cache` |
| `remara_project_status_2026-04-26.txt` | 271 | `   NULL seifa_decile despite being in suburban Brisbane. Likely` |
| `remara_project_status_2026-04-26.txt` | 272 | `   sa2_code missing or SEIFA-table coverage gap. One example;` |
| `schema_dump.txt` | 141 | `    weighted_avg_seifa_irsd         REAL,` |
| `schema_dump.txt` | 266 | `    seifa_irsd                INTEGER,` |
| `test_operator.py` | 95 | `    print(f"    weighted_seifa      : {c.get('weighted_seifa')}")` |
| `tier2_diagnose.py` | 12 | `     (ARIA+, SEIFA, Lat/Lng, Service Sub Type, Final Report Sent Date)` |
| `tier2_diagnose.py` | 45 | `    "SEIFA",` |
| `tier2_diagnose.py` | 187 | `    # ── SEIFA value range ───────────────────────────────────────` |
| `tier2_diagnose.py` | 188 | `    print("\n── SEIFA value inspection ──")` |
| `tier2_diagnose.py` | 189 | `    seifa_vals = [r.get("SEIFA") for r in records if r.get("SEIFA") is not None]` |
| `validate_tier2.py` | 16 | `               SUM(CASE WHEN seifa_decile IS NOT NULL THEN 1 ELSE 0 END) AS seifa_n,` |
| `validate_tier2.py` | 29 | `    print(f"    seifa populated      : {stats[3]}/{n}")` |
| `validate_tier2.py` | 47 | `    # SEIFA decile distribution` |
| `validate_tier2.py` | 48 | `    seifa_dist = conn.execute("""` |
| `validate_tier2.py` | 49 | `        SELECT seifa_decile, COUNT(*)` |

#### `tier` - 87 hit(s)

| File | Line | Snippet |
|---|---:|---|
| `catchment_html.py` | 160 | `    tier         = _clean(c.get("supply_tier", "unknown"))` |
| `catchment_html.py` | 184 | `    }.get(tier, "#95a5a6")` |
| `catchment_html.py` | 269 | `            {tier.upper()}` |
| `centre_page.py` | 377 | `                "note": "Catchment cache not yet populated (Tier 3 ingest).",` |
| `docs/_op_chunks/part2.txt` | 278 | `   v5: Tier 2 NQS ingest wire-up. Header shows prettified` |
| `docs/_op_chunks/part3.txt` | 362 | `//      for supply bands / u5 / income until Tier 3 cache populates)` |
| `docs/_op_chunks/part3.txt` | 377 | `        supply-band exposure once the SA2 catchment cache is populated (Tier 3).</span>` |
| `docs/_op_chunks/part3.txt` | 383 | `  // SEIFA sub-block is what Tier 2 gives us. Render it.` |
| `docs/_op_chunks/part3.txt` | 481 | `      SA2 catchment cache is populated (Tier 3). SEIFA above is live from the NQS snapshot.` |
| `docs/_op_chunks/part4.txt` | 223 | `// â”€â”€ v5: Remoteness distribution (real ARIA+ data from Tier 2) â”€â”€â”€â”€` |
| `docs/centre.html` | 747 | `        <span class="will-show">awaiting Tier 3 service_catchment_cache build.</span>` |
| `docs/dashboard.html` | 291 | `/* ── TIER BADGES ── */` |
| `docs/dashboard.html` | 292 | `.tier-badge {` |
| `docs/dashboard.html` | 301 | `.tier-hot   { background: rgba(224,92,58,0.15); color: var(--hot); }` |
| `docs/dashboard.html` | 302 | `.tier-warm  { background: rgba(212,137,10,0.15); color: var(--warm); }` |
| `docs/dashboard.html` | 303 | `.tier-watch { background: rgba(90,100,128,0.15); color: var(--watch); }` |
| `docs/index.html` | 289 | `/* ── TIER BADGES ── */` |
| `docs/index.html` | 290 | `.tier-badge {` |
| `docs/index.html` | 299 | `.tier-hot   { background: rgba(224,92,58,0.15); color: var(--hot); }` |
| `docs/index.html` | 300 | `.tier-warm  { background: rgba(212,137,10,0.15); color: var(--warm); }` |
| `docs/index.html` | 301 | `.tier-watch { background: rgba(90,100,128,0.15); color: var(--watch); }` |
| `docs/operator.html` | 1100 | `   v5: Tier 2 NQS ingest wire-up. Header shows prettified` |
| `docs/operator.html` | 2057 | `//      for supply bands / u5 / income until Tier 3 cache populates)` |
| `docs/operator.html` | 2072 | `        supply-band exposure once the SA2 catchment cache is populated (Tier 3).</span>` |
| `docs/operator.html` | 2078 | `  // SEIFA sub-block is what Tier 2 gives us. Render it.` |
| `docs/operator.html` | 2176 | `      SA2 catchment cache is populated (Tier 3). SEIFA above is live from the NQS snapshot.` |
| `docs/operators.json` | 1 | `[{"legal_name": "Cranbourne Day Care and Kindergarten Centre Pty Ltd", "tier": "hot", "score": 100, "n_centres": 7, "states": ["VIC"], "is_...` |
| `generate_dashboard.py` | 508 | `                tier = match.get("priority_tier", "")` |
| `generate_dashboard.py` | 509 | `                tier_badge = f"<span class='tier-badge tier-{tier}'>{tier.upper()}</span>"` |
| `generate_dashboard.py` | 579 | `            "tier":        op.get("priority_tier", "watch"),` |
| `generate_dashboard.py` | 710 | `        tier     = op.get("priority_tier", "watch")` |
| `generate_dashboard.py` | 718 | `            <td class='text-center'><span class='tier-badge tier-{tier}'>{tier.upper()}</span></td>` |
| `generate_prospecting_page.py` | 43 | `        tier       = op.get("priority_tier", "")` |
| `generate_prospecting_page.py` | 58 | `        tier_color = {"hot": "#D85A30", "warm": "#E8A020"}.get(tier, "#888")` |
| `generate_prospecting_page.py` | 59 | `        tier_label = tier.upper()` |
| `generate_prospecting_page.py` | 106 | `            data-tier="{tier}"` |
| `generate_prospecting_page.py` | 188 | `        <option value="">All tiers</option>` |
| `index.html` | 155 | `    .tier {` |
| `index.html` | 163 | `    .tier-hot {` |
| `index.html` | 168 | `    .tier-warm {` |
| `index.html` | 173 | `    .tier-watch {` |
| `index.html` | 2264 | `                            <span class="tier tier-${op.tier}">${op.tier}</span>` |
| `ingest_nqs_snapshot.py` | 4 | `Tier 2 Phase D — ingest the NQS Data Q4 2025 current-state` |
| `layer2_step5b_apply.py` | 11 | `  - LFP discovery deferred to Tier 2 (Education and Employment` |
| `lookup_operator.py` | 286 | `    print(f"Tier: {result['priority_tier'].upper()}  "` |
| `migrate_schema_v0_4.py` | 4 | `Tier 2 Phase C — additive schema migration for the NQS ingest.` |
| `migrate_schema_v0_4.py` | 102 | `    parser = argparse.ArgumentParser(description="Schema migration v0.4 for Tier 2 NQS ingest.")` |
| `module1_acecqa.py` | 264 | `        tier, tier_note = classify_entity_size(group_info["group_centre_count"])` |
| `module1_acecqa.py` | 291 | `            "priority_tier":      "existing_client" if existing else tier,` |
| `module1_acecqa.py` | 340 | `        tier, tier_note = classify_entity_size(group_info["group_centre_count"])` |
| `module1_acecqa.py` | 371 | `            "priority_tier":      "existing_client" if existing else tier,` |
| `module2c_targeting.py` | 6 | `tiered matching, scores each group against Remara target criteria,` |
| `module2c_targeting.py` | 9 | `Group inference tiers:` |
| `module2c_targeting.py` | 158 | `    Infer operator groups from ACECQA data using tiered matching.` |
| `module2c_targeting.py` | 163 | `    # ── TIER 1: Same provider_approval_number (confirmed) ────────────` |
| `module2c_targeting.py` | 176 | `    # ── TIER 2: Exact normalised name match across provider numbers ───` |
| `module5_digest.py` | 25 | `def tier_color(tier):` |
| `module5_digest.py` | 32 | `    return colors.get(tier, "#5F5E5A")` |
| `module5_digest.py` | 35 | `def tier_label(tier):` |
| `module5_digest.py` | 42 | `    return labels.get(tier, tier.upper())` |
| `module5_digest.py` | 46 | `    tier = lead.get("priority_tier", "watch")` |
| `module5_digest_backup.py` | 25 | `def tier_color(tier):` |
| `module5_digest_backup.py` | 32 | `    return colors.get(tier, "#5F5E5A")` |
| `module5_digest_backup.py` | 35 | `def tier_label(tier):` |
| `module5_digest_backup.py` | 42 | `    return labels.get(tier, tier.upper())` |
| `module5_digest_backup.py` | 46 | `    tier = lead.get("priority_tier", "watch")` |
| `module5_export.txt` | 25 | `def tier_color(tier):` |
| `module5_export.txt` | 32 | `    return colors.get(tier, "#5F5E5A")` |
| `module5_export.txt` | 35 | `def tier_label(tier):` |
| `module5_export.txt` | 42 | `    return labels.get(tier, tier.upper())` |
| `module5_export.txt` | 46 | `    tier = lead.get("priority_tier", "watch")` |
| `operator_page.py` | 40 | `  - Tier 2 columns on services (aria_plus, seifa_decile,` |
| `operator_page.py` | 44 | `    service_catchment_cache path retained for Tier 3.` |
| `recon/layer1_recon_findings.md` | 52 | `\\| `service_catchment_cache` \\| 0 \\| empty \\| 17 cols; populated by Tier 3 build \\|` |
| `recon/layer1_recon_findings.md` | 53 | `\\| `service_tenures` \\| 0 \\| empty \\| 10 cols; carries property/lease (Tier 5) \\|` |
| `recon/layer1_recon_findings.md` | 63 | `\\| `services` \\| 18,223 \\| Live snapshot (Tier 2 NQS Q4 2025) \\|` |
| `recon/layer1_recon_findings.md` | 104 | `\\| `NQS Data Q4 2025.XLSX` \\| 10.7 MB \\| INGESTED \\| Tier 2 source — already in DB \\|` |
| `recon/layer1_recon_findings.md` | 129 | `\\| ARIA / ARIA+ \\| Label string. Spelling drift — Q3 2013 uses `ARIA+`, Q1 2020 uses `ARIA`. Tier 2 already saw both code and label forms...` |
| `remara_project_status_2026-04-26.txt` | 145 | `      - Catchment: SEIFA decile + ARIA band + SA2 + Tier 3 cache` |
| `remara_project_status_2026-04-26.txt` | 229 | `    table is built (Tier 3, currently pending).` |
| `remara_project_status_2026-04-26.txt` | 352 | `Phase 8 — Starting Blocks scraper (Tier 4 ingest)  [2 sessions, low risk]` |
| `remara_project_status_2026-04-26.txt` | 410 | `    - Pattern: same as Tier 2 ingest (dry-run, transaction,` |
| `remara_project_status_2026-04-26.txt` | 434 | `      service_catchment_cache when that's built (Tier 3 dep)` |
| `remara_project_status_2026-04-27c.txt` | 101 | `      ingest. Originally Tier 2 deferred. CONFIRMED V1, COMPLETE.` |
| `remara_project_status_2026-04-27c.txt` | 163 | `    Source for Tier 2 NQS ingest (COMPLETE).` |
| `remara_project_status_2026-04-27c.txt` | 251 | `  NQS Data (Tier 2)` |
| `tier2_diagnose.py` | 4 | `Phase B read-only diagnostic for the Tier 2 NQS ingest.` |

#### `vs_peers` - 3 hit(s)

| File | Line | Snippet |
|---|---:|---|
| `remara_project_status_2026-04-27c.txt` | 342 | `  POSITION (peer comparison):` |
| `remara_project_status_2026-04-27c.txt` | 370 | `    - JSA vacancy rate percentile vs national` |
| `remara_project_status_2026-04-27c.txt` | 799 | `    - What cohort defines "vs peers" (state? remoteness band?` |

#### `z-score` - 2 hit(s)

| File | Line | Snippet |
|---|---:|---|
| `remara_project_status_2026-04-27c.txt` | 670 | `          b. RWCI weighting: equal-weight z-scored inputs,` |
| `remara_project_status_2026-04-27c.txt` | 824 | `      Option A — equal-weight z-scored inputs` |

---

## C. Page-by-page heuristic grouping

_Grouped by path-name match: 'industry' / 'catchment' / 'operator' / 'centre' substring in file path. Files matching no page or multiple pages are listed separately. **This is heuristic - Patrick to verify.**_

### C.1 Industry tab

_No keyword hits in files path-matching this page._

### C.2 Catchment tab

| Keyword | Files |
|---|---|
| aria | `leads_catchment.json` |
| decile | `catchment_html.py`; `docs/catchments.json`; `leads_catchment.json`; `module2b_catchment.py` |
| rank | `module2b_catchment.py` |
| score | `docs/catchments.json`; `leads_catchment.json`; `module2b_catchment.py` |
| seifa | `module2b_catchment.py` |
| tier | `catchment_html.py` |

### C.3 Operator tab

| Keyword | Files |
|---|---|
| aria | `docs/operator.html`; `operator_page.py`; `operator_payload_snapshot.json` |
| band | `docs/operator.html`; `operator_page.py`; `operator_payload_snapshot.json` |
| composite | `docs/operator.html` |
| decile | `docs/operator.html`; `operator_page.py`; `operator_payload_snapshot.json` |
| score | `docs/operator.html`; `docs/operators.json`; `lookup_operator.py`; `operators_hot_targets.json`; `operators_target_list.json`; ...+1 more |
| seifa | `docs/operator.html`; `operator_page.py`; `operator_payload_snapshot.json`; `test_operator.py` |
| tier | `docs/operator.html`; `docs/operators.json`; `lookup_operator.py`; `operator_page.py` |

### C.4 Centre tab

| Keyword | Files |
|---|---|
| aria | `docs/centre.html` |
| decile | `docs/centre.html` |
| score | `docs/centre.html` |
| seifa | `docs/centre.html` |
| tier | `docs/centre.html` |

### C.5 Multi-page files (path matched >1 page)

_None._

### C.6 Unclassified (no page in path)

| Keyword | Files |
|---|---|
| aria | `build_historical_data.py`; `centre_page.py`; `docs/_op_chunks/part2.txt`; `docs/_op_chunks/part4.txt`; `docs/dashboard.html`; ...+15 more |
| band | `add_workforce_assumptions.py`; `centre_page.py`; `docs/_op_chunks/part1.txt`; `docs/_op_chunks/part2.txt`; `docs/_op_chunks/part3.txt`; ...+17 more |
| cohort | `add_workforce_assumptions.py`; `layer1_recheck.py`; `layer2_step5b_prime_apply.py`; `layer2_step6_preflight.py`; `layer2_step6_spotcheck.py`; ...+4 more |
| composite | `apply_decisions.py`; `diag_harmony.py`; `diagnose_centres_endpoint.py`; `docs/_op_chunks/part3.txt`; `docs/review.html`; ...+6 more |
| decile | `centre_page.py`; `docs/_op_chunks/part2.txt`; `docs/_op_chunks/part3.txt`; `docs/index.html`; `generate_dashboard.py`; ...+11 more |
| low_med_high | `remara_project_status_2026-04-27c.txt` |
| ntile_sql | `layer2_step5b_prime_apply.py`; `remara_project_status_2026-04-27c.txt` |
| percentile | `layer2_step5b_prime_apply.py`; `remara_project_status_2026-04-27c.txt` |
| quintile | `remara_project_status_2026-04-27c.txt` |
| rank | `docs/dashboard.html`; `docs/index.html`; `generate_dashboard.py`; `module2c_targeting.py`; `remara_project_status_2026-04-27c.txt` |
| score | `centre_page.py`; `check_module4.py`; `cleanup.py`; `docs/_op_chunks/part3.txt`; `docs/dashboard.html`; ...+12 more |
| seifa | `centre_page.py`; `docs/_op_chunks/part2.txt`; `docs/_op_chunks/part3.txt`; `docs/index.html`; `generate_dashboard.py`; ...+16 more |
| tier | `centre_page.py`; `docs/_op_chunks/part2.txt`; `docs/_op_chunks/part3.txt`; `docs/_op_chunks/part4.txt`; `docs/dashboard.html`; ...+16 more |
| vs_peers | `remara_project_status_2026-04-27c.txt` |
| z-score | `remara_project_status_2026-04-27c.txt` |

---

## D. Open questions for Patrick (Decision 65 D1-D4)

**D1. Layer 3 table shape:**
- Option A - wide table per SA2 (one row per SA2, many percentile/band cols)
- Option B - long format (sa2_code, metric, year, cohort_def, percentile, band)
- Option C - hybrid (long for stable Layer 3 metrics, wide mart view for Layer 4 reads)

Survey evidence: _[fill in after review of Sections A-C]_

**D2. RWCI weighting (only if RWCI in Layer 3 scope):**
- Option A - equal-weight z-scored inputs
- Option B - hand-calibrated weights (Patrick supplies)
- Option C - principal-component on inputs across all SA2s
- Option D - defer RWCI to Layer 3b

Survey evidence: _[fill in]_

**D3. Cohort definitions per metric:**
- Default cohort: state-x-remoteness?
- Per-metric override?

Survey evidence: _[fill in - note any precedent like SEIFA decile = national, ARIA = remoteness band, etc.]_

**D4. Session scope:**
- Full Layer 3 + RWCI / Layer 3 minus RWCI / pre-work + scope only
