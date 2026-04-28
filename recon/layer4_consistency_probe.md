# Layer 4 Consistency Probe — 2026-04-28T13:33:45

Repo root: `C:\Users\Patrick Bell\remara-agent`

Excluded dirs: `['.git', '.venv', '__pycache__', 'abs_data', 'build', 'data', 'dist', 'node_modules', 'recon', 'venv']`

Scanned: **137 .py files**, **6 .html files**.

## 1. Where each Layer 4 metric already appears

### under5

**`build_historical_data.py`** (9 hits shown, capped at 15)
```
   96:     Load national under-5 population (Persons 0-4 years) from ABS Population
  138: def interpolate_under5_population(abs_data, quarter_key):
  140:     Return an estimated national under-5 population for the given quarter,
  357:                 under5_pop   = interpolate_under5_population(abs_pop, q)
  359:                 if under5_pop and under5_pop > 0 and metrics["total_places"] > 0:
  361:                         metrics["total_places"] / under5_pop * 100, 2
  367:                     "under5_pop":           under5_pop,           # national 0-4 ERP (interpolated)
  368:                     "supply_demand_ratio":  supply_demand_ratio,  # licensed places per 100 under-5
  411:         print(f"  Under-5 population:   {latest.get('under5_pop', 'N/A')}")
```

**`build_sa2_history.py`** (1 hits shown, capped at 15)
```
   11:   - pop_0_4:       SA2 under-5 population (ABS annual, interpolated quarterly)
```

**`catchment_html.py`** (1 hits shown, capped at 15)
```
  240:                 <div>Under-5 pop: <b>{f"{pop:,}" if pop else "n/a"}</b> ({pop_yr})
```

**`generate_dashboard.py`** (12 hits shown, capped at 15)
```
   71:             demand_desc = f"rapidly growing under-5 population (+{pop_cagr:.1f}% p.a.)"
   73:             demand_desc = f"growing under-5 population (+{pop_cagr:.1f}% p.a.)"
   75:             demand_desc = f"stable under-5 population ({pop_cagr:+.1f}% p.a.)"
   77:             demand_desc = f"declining under-5 population ({pop_cagr:.1f}% p.a.)"
  243:             "band_u50":     sum(1 for p in pl if p < 50),
 2759:         data: {{ labels: sdLabels, datasets: [makeDataset('Places per 100 Under-5', sdSliced, '#9b59b6', 'rgba(155,89,182,0.08)')] }}
 2890:                     <div style="font-size:11px;color:var(--muted)">Under-5 pop</div>
 2959:             &lt;50pl: ${{sp.band_u50}} &nbsp;·&nbsp; 50–99: ${{sp.band_50_99}} &nbsp;·&nbsp; 100–149: ${{sp.band_100_149}} &nbsp;·&nbsp; 150+: ${{sp.band_150plus}}
 3029:                 <div class="stat-label">Under-5 Pop</div>
 3067:                 <div style="font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-bottom:6px">Under-5 Population</div>
 3426:     // ── Chart 2 (small): Under-5 Population ──
 3433:             data: {{ labels: t.labels, datasets: [makeLine('Under-5 Pop', t.data, '#00c9a7', 'rgba(0,201,167,0.08)')] }}
```

**`layer1_recheck.py`** (3 hits shown, capped at 15)
```
    3: # Looks for SA2-level data in Table 1, under-5 age columns, and confirms openpyxl can read.
   43:         # For Population: scan all sheets for under-5 age columns
   45:             print(f"\n  [searching for under-5 cohort columns]")
```

**`layer2_step6_apply.py`** (14 hits shown, capped at 15)
```
   21:   age_group in {under_5_persons, under_5_males, under_5_females, total_persons}
   48:     ("under_5_persons", "under_5_persons"),
   49:     ("under_5_males", "under_5_males"),
   50:     ("under_5_females", "under_5_females"),
   89:               "under_5_persons", "under_5_males", "under_5_females",
  207:     # Sanity check: under_5_males + under_5_females should ~= under_5_persons
  208:     print(banner("SANITY CHECK: under-5 males + females ~= persons"))
  216:         m = grp.get("under_5_males")
  217:         f = grp.get("under_5_females")
  218:         p = grp.get("under_5_persons")
  233:         print("  All under-5 splits internally consistent.")
  235:     # Sanity check: total_persons should be substantially larger than under_5
  236:     print(banner("SANITY CHECK: total_persons >> under_5_persons"))
  239:         u5 = grp.get("under_5_persons")
```

**`layer2_step6_diag.py`** (5 hits shown, capped at 15)
```
   10:     - Confirms under-5 columns at indices 12/48/84
  204:     # ── 7. Sample 5 SA2 rows showing year col + under-5 cols ─────────
  306:             "under_5_males": 12,
  307:             "under_5_females": 48,
  308:             "under_5_persons": 84,
```

**`layer2_step6_preflight.py`** (14 hits shown, capped at 15)
```
   37: # Under-5 cohort column indices documented in the status doc
   38: UNDER_5_COL_INDICES = [12, 48, 84]
  119:     findings.append("## C. Header row & under-5 cohort columns\n")
  144:     # Show first 6 columns (key cols) + the 3 under-5 cohort columns
  152:     findings.append("### Under-5 cohort columns "
  156:     print("Under-5 cohort columns:")
  157:     for i in UNDER_5_COL_INDICES:
  170:                     "(likely region name), and the 3 under-5 cohort columns.\n")
  171:     findings.append("| code | name | u5_a | u5_b | u5_c |")
  178:         u5_vals = []
  179:         for i in UNDER_5_COL_INDICES:
  180:             u5_vals.append(r[i] if i < len(r) else "OOR")
  182:                 f"{u5_vals[0]} | {u5_vals[1]} | {u5_vals[2]}")
  185:                         f"{u5_vals[0]} | {u5_vals[1]} | {u5_vals[2]} |")
```

**`layer2_step6_spotcheck.py`** (8 hits shown, capped at 15)
```
   42: # 3. Join to services — first 5 services in 2024 with their under-5 count
   44: print("Join sanity: first 5 services + 2024 SA2 under-5 cohort:")
   51:       AND e.age_group = 'under_5_persons'
   57:           f"sa2={sa2} | u5_2024={persons}")
   68:                                   AND e.age_group = 'under_5_persons'
   73: print(f"Service coverage with 2024 under-5 data: "
   91:         WHERE sa2_code = ? AND age_group = 'under_5_persons'
   94:     print(f"  {'year':>6}  {'under-5':>8}")
```

**`layer3_apply.py`** (2 hits shown, capped at 15)
```
   68:         "canonical": "sa2_under5_count",
   71:         "filter_clause": "age_group = 'under_5_persons'",
```

**`layer3_diag.py`** (4 hits shown, capped at 15)
```
  372:     ("sa2_under5_count",
  376:      "Under-5 population, by year",
  384:     ("sa2_under5_growth_5y",
  388:      "5-year CAGR of under-5 population",
```

**`layer4_consistency_probe.py`** (2 hits shown, capped at 15)
```
    6:   1. Where each Layer 4 metric currently displays (under5, total_pop,
   35:     "under5":           ["under5", "under-5", "under_5", "u5_", "_u5"],
```

**`module2b_catchment.py`** (2 hits shown, capped at 15)
```
   14:   - Supply ratio: LDC licensed places / under-5 population
  523:         f"  Under-5 pop:     {_fmt_int(c.get('pop_0_4'))} ({c.get('pop_year','?')})  "
```

**`operator_page.py`** (7 hits shown, capped at 15)
```
  776:         "weighted_under5": cache_block.get("weighted_under5"),
  790:         "weighted_under5":  None,
  816:     expected = {"service_id", "seifa_decile", "under5_pop",
  827:             f"SELECT service_id, seifa_decile, under5_pop, "
  840:     w_u5    = 0.0
  849:             w_u5 += float(u5) * w
  867:         result["weighted_under5"] = round(w_u5    / total_w, 0)
```

**`test_operator.py`** (1 hits shown, capped at 15)
```
   96:     print(f"    weighted_under5     : {c.get('weighted_under5')}")
```

**`docs\centre.html`** (1 hits shown, capped at 15)
```
  746:         Service-level catchment metrics (under-5 population, supply ratio, competitor density)
```

**`docs\index.html`** (7 hits shown, capped at 15)
```
 2437:         data: { labels: sdLabels, datasets: [makeDataset('Places per 100 Under-5', sdSliced, '#9b59b6', 'rgba(155,89,182,0.08)')] }
 2568:                     <div style="font-size:11px;color:var(--muted)">Under-5 pop</div>
 2637:             &lt;50pl: ${sp.band_u50} &nbsp;·&nbsp; 50–99: ${sp.band_50_99} &nbsp;·&nbsp; 100–149: ${sp.band_100_149} &nbsp;·&nbsp; 150+: ${sp.band_150plus}
 2707:                 <div class="stat-label">Under-5 Pop</div>
 2745:                 <div style="font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-bottom:6px">Under-5 Population</div>
 3104:     // ── Chart 2 (small): Under-5 Population ──
 3111:             data: { labels: t.labels, datasets: [makeLine('Under-5 Pop', t.data, '#00c9a7', 'rgba(0,201,167,0.08)')] }
```

**`docs\operator.html`** (5 hits shown, capped at 15)
```
 2071:         plus weighted under-5 population, weighted median income, and
 2116:   const u5   = c.weighted_under5;
 2167:       <div class="fact"><span class="k">Weighted under-5 population</span><b>${fmtN(u5)}</b></div>
 2175:       Supply bands, weighted under-5 population and median income arrive when the
 2332:       <span class="will-show">Will show: SA2s with high under-5 population and
```

**`index.html`** (1 hits shown, capped at 15)
```
 2100:                         <div class="metric-label">Under-5 Population</div>
```

### total_population

**`build_historical_data.py`** (10 hits shown, capped at 15)
```
   15:     so dashboard charts interpolate cleanly across the gap
   51: # interpolate cleanly rather than showing a false zero-gap.
  138: def interpolate_under5_population(abs_data, quarter_key):
  141:     by linear interpolation between annual June-30 data points.
  180:     # Find bracketing data points for interpolation
  194:     # Linear interpolation
  283:     # For quarters in the known data gap, emit None so dashboard interpolates.
  286:         by_aria = None  # explicit null — chart will interpolate
  357:                 under5_pop   = interpolate_under5_population(abs_pop, q)
  367:                     "under5_pop":           under5_pop,           # national 0-4 ERP (interpolated)
```

**`build_sa2_history.py`** (4 hits shown, capped at 15)
```
   11:   - pop_0_4:       SA2 under-5 population (ABS annual, interpolated quarterly)
  108: def interpolate_sa2_value(ts, sa2_code, frac_yr):
  305:                 sa2_pop = interpolate_sa2_value(pop_ts, sa2_code, frac_yr)
  311:                 sa2_income_w = interpolate_sa2_value(income_ts, sa2_code, frac_yr)
```

**`db_inventory.py`** (1 hits shown, capped at 15)
```
  362:     ("services", "sa2_code", "abs_sa2_erp_annual", "sa2_code",
```

**`generate_dashboard.py`** (3 hits shown, capped at 15)
```
 2912:     const kinderPlaces = sa2.kinder_places || 0;
 3051:                 <div style="font-size:10px;color:var(--muted);margin-top:3px">${{kinderPlaces ? kinderPlaces.toLocaleString() + ' places' : ''}}</div>
 3120:                     <div style="font-size:15px;font-weight:600;margin-top:2px">${{kinderCount}} centres · ${{kinderPlaces}} places</div>
```

**`layer2_step1b_apply.py`** (5 hits shown, capped at 15)
```
   20:   every assigned sa2_code present in abs_sa2_erp_annual.sa2_code
  227:             "SELECT DISTINCT sa2_code FROM abs_sa2_erp_annual "
  242:             f"{len(orphans)} assigned sa2_codes not in abs_sa2_erp_annual"
  314:           f"(all assigned sa2_codes present in `abs_sa2_erp_annual`)")
  516:             f'(SELECT sa2_code FROM abs_sa2_erp_annual WHERE sa2_code IS NOT NULL)'
```

**`layer2_step1b_diag.py`** (1 hits shown, capped at 15)
```
  376: w("     - every assigned `sa2_code` present in `abs_sa2_erp_annual.sa2_code`")
```

**`layer2_step1b_spotcheck.py`** (1 hits shown, capped at 15)
```
  296:     ("abs_sa2_erp_annual", "ERP (Step 6)"),
```

**`layer2_step5b_prime_preflight.py`** (1 hits shown, capped at 15)
```
  123:         ("abs_sa2_erp_annual", "ERP table (Step 6)"),
```

**`layer2_step6_apply.py`** (15 hits shown, capped at 15)
```
    2: Layer 2 Step 6 APPLY v2 — ABS ERP at SA2 ingest (long format)
   20:   abs_sa2_erp_annual (sa2_code, year, age_group, persons)
   56: ACTION = "sa2_erp_ingest_v1"
   57: SUBJECT_TYPE = "abs_sa2_erp_annual"
  149:     print(banner(f"LAYER 2 STEP 6 v2 — ABS ERP INGEST ({mode})"))
  290:             CREATE TABLE IF NOT EXISTS abs_sa2_erp_annual (
  298:         cur.execute("CREATE INDEX IF NOT EXISTS ix_erp_year "
  299:                     "ON abs_sa2_erp_annual(year)")
  300:         cur.execute("CREATE INDEX IF NOT EXISTS ix_erp_age "
  301:                     "ON abs_sa2_erp_annual(age_group)")
  305:         cur.execute("SELECT COUNT(*) FROM abs_sa2_erp_annual")
  307:         print(f"Pre-state: abs_sa2_erp_annual has {pre_count:,} rows")
  320:                 "INSERT INTO abs_sa2_erp_annual "
  329:         cur.execute("SELECT COUNT(*) FROM abs_sa2_erp_annual")
  332:                     "FROM abs_sa2_erp_annual")
```

**`layer2_step6_diag.py`** (9 hits shown, capped at 15)
```
    2: Layer 2 Step 6 DIAGNOSTIC — ABS ERP at SA2 layout discovery
   12:     - Checks whether abs_sa2_erp_annual already exists
  268:     # Check for sa2_erp_annual
  271:         WHERE type='table' AND name='abs_sa2_erp_annual'
  275:         cur.execute("SELECT COUNT(*) FROM abs_sa2_erp_annual")
  277:         print(f"\nabs_sa2_erp_annual already exists: {n:,} rows")
  278:         findings.append(f"- ⚠️ `abs_sa2_erp_annual` already exists "
  282:         print("\nabs_sa2_erp_annual does not exist (apply will create).")
  283:         findings.append("- `abs_sa2_erp_annual` does not exist (apply "
```

**`layer2_step6_preflight.py`** (3 hits shown, capped at 15)
```
    2: Layer 2 Step 6 PREFLIGHT — ABS ERP at SA2 ingest
   50:     findings.append("Read-only inventory of ABS ERP workbook before ingest.")
  292:     findings.append("CREATE TABLE abs_sa2_erp_annual (")
```

**`layer2_step6_spotcheck.py`** (9 hits shown, capped at 15)
```
    3: Confirms abs_sa2_erp_annual is queryable end-to-end and joins cleanly
   15: print("ABS_SA2_ERP_ANNUAL SPOTCHECK")
   19: cur.execute("SELECT COUNT(*) FROM abs_sa2_erp_annual")
   22: cur.execute("SELECT COUNT(DISTINCT sa2_code) FROM abs_sa2_erp_annual")
   25: cur.execute("SELECT COUNT(DISTINCT year) FROM abs_sa2_erp_annual")
   32:     FROM abs_sa2_erp_annual
   48:     JOIN abs_sa2_erp_annual e ON s.sa2_code = e.sa2_code
   66:     LEFT JOIN abs_sa2_erp_annual e
   90:         SELECT year, persons FROM abs_sa2_erp_annual
```

**`layer2_step8_apply.py`** (6 hits shown, capped at 15)
```
   13:     row 6 — sub-header (ERP | Births | TFR repeated per year)
   36:   - 0 SA2 codes outside abs_sa2_erp_annual canonical universe
  259:             "SELECT DISTINCT sa2_code FROM abs_sa2_erp_annual "
  306:             f"{len(orphans)} SA2 codes outside abs_sa2_erp_annual"
  364:     w(f"- Canonical universe (abs_sa2_erp_annual): "
  676:             f'(SELECT sa2_code FROM abs_sa2_erp_annual WHERE sa2_code IS NOT NULL)'
```

**`layer2_step8_diag.py`** (1 hits shown, capped at 15)
```
  390: w("- no births_count < 0; no SA2 codes outside abs_sa2_erp_annual")
```

**`layer3_apply.py`** (4 hits shown, capped at 15)
```
   10:   - abs_sa2_erp_annual
   69:         "source_table": "abs_sa2_erp_annual",
   76:         "canonical": "sa2_total_population",
   77:         "source_table": "abs_sa2_erp_annual",
```

**`layer3_diag.py`** (15 hits shown, capped at 15)
```
  121:         cur.execute("SELECT COUNT(DISTINCT sa2_code) FROM abs_sa2_erp_annual")
  122:         findings["distinct_sa2_erp"] = cur.fetchone()[0]
  124:         findings["distinct_sa2_erp"] = None
  160:               FROM abs_sa2_erp_annual e
  207:     # 2a. abs_sa2_erp_annual — list age_groups + per-year SA2 counts
  214:               FROM abs_sa2_erp_annual
  218:         findings["erp_age_groups"] = cur.fetchall()
  220:         findings["erp_age_groups_err"] = str(e)
  373:      "abs_sa2_erp_annual",
  378:     ("sa2_total_population",
  379:      "abs_sa2_erp_annual",
  385:      "abs_sa2_erp_annual (derived)",
  453:     yrs_max = 14  # full history for births / ERP
  521:     w(f"| `abs_sa2_erp_annual` "
  522:       f"| {fmt_int(coh.get('distinct_sa2_erp'))} |")
```

**`layer4_consistency_probe.py`** (2 hits shown, capped at 15)
```
    6:   1. Where each Layer 4 metric currently displays (under5, total_pop,
   36:     "total_population": ["total_population", "total_pop", "erp"],
```

**`lookup_operator.py`** (1 hits shown, capped at 15)
```
  112:         r'holdings|investments|enterprises|services|group|management)\b',
```

**`migrate_schema_v0_5.py`** (2 hits shown, capped at 15)
```
   88:                      -- COM = Commentary (rule-based interpretation, no AI)
  100:                      -- bump when formula or interpretation changes
```

**`module2c_targeting.py`** (1 hits shown, capped at 15)
```
  226:                 "investments", "investment", "enterprises", "enterprise",
```

**`module4_property.py`** (1 hits shown, capped at 15)
```
  152:         r'holdings|investments|enterprises|services|group|management)\b',
```

**`patch_operator_html_to_v8.py`** (10 hits shown, capped at 15)
```
   27: #   - Replaces the ${supplyHtml} interpolation in renderWorkforce()
   50: # Anchor: the template-literal interpolation inside renderWorkforce
   52: SUPPLY_INTERP_ANCHOR = b"${supplyHtml}"
   60:           State-level training-supply data is best interpreted at the industry level
  109:     if SUPPLY_INTERP_ANCHOR not in original:
  110:         print(f"ERROR: anchor '{SUPPLY_INTERP_ANCHOR.decode()}' not found. "
  126:     # Replace the supply interpolation with the static placeholder.
  129:         buf, SUPPLY_INTERP_ANCHOR, placeholder,
  130:         "supply interpolation -> placeholder",
  150:         ("supply interp removed",     SUPPLY_INTERP_ANCHOR not in verify),
```

**`sa2_cohort_apply.py`** (15 hits shown, capped at 15)
```
  234:     cur.execute("SELECT DISTINCT sa2_code FROM abs_sa2_erp_annual")
  235:     erp_sa2 = {r[0] for r in cur.fetchall()}
  238:     findings["erp_distinct_sa2"] = len(erp_sa2)
  240:     findings["coverage_overlap"] = len(erp_sa2 & cohort_sa2)
  241:     findings["erp_not_in_cohort"] = sorted(erp_sa2 - cohort_sa2)
  242:     findings["cohort_not_in_erp"] = sorted(cohort_sa2 - erp_sa2)
  285:     print(f"  ERP distinct SA2:        {findings['erp_distinct_sa2']:,}")
  288:     print(f"  ERP-not-in-cohort:       {len(findings['erp_not_in_cohort']):,}")
  289:     print(f"  cohort-not-in-ERP:       {len(findings['cohort_not_in_erp']):,}")
  446:     w("## Coverage check vs `abs_sa2_erp_annual`")
  448:     w(f"- ERP distinct SA2:    {fmt_int(validation['erp_distinct_sa2'])}")
  451:     w(f"- ERP not in cohort:   "
  452:       f"{fmt_int(len(validation['erp_not_in_cohort']))}")
  453:     w(f"- Cohort not in ERP:   "
  454:       f"{fmt_int(len(validation['cohort_not_in_erp']))}")
```

**`docs\centre.html`** (3 hits shown, capped at 15)
```
  542:       <span class="ml-item">${renderBadge("COM")} <span>Commentary — rule-based interpretation</span></span>
  663: function renderPlacesCard(centre) {
  853:       ${renderPlacesCard(centre)}
```

**`docs\dashboard.html`** (1 hits shown, capped at 15)
```
 1073:             <td class='approval-centre' style='color:var(--accent);text-decoration:underline;text-decoration-style:dotted'>CATERPILLAR KIDZ EARLY LEARNING CENTRE AND KINDERGARTEN</td>
```

**`docs\index.html`** (4 hits shown, capped at 15)
```
 1397:             <td class='approval-centre' style='color:var(--accent);text-decoration:underline;text-decoration-style:dotted'>CATERPILLAR KIDZ EARLY LEARNING CENTRE AND KINDERGARTEN</td>
 2590:     const kinderPlaces = sa2.kinder_places || 0;
 2729:                 <div style="font-size:10px;color:var(--muted);margin-top:3px">${kinderPlaces ? kinderPlaces.toLocaleString() + ' places' : ''}</div>
 2798:                     <div style="font-size:15px;font-weight:600;margin-top:2px">${kinderCount} centres · ${kinderPlaces} places</div>
```

**`docs\operator.html`** (8 hits shown, capped at 15)
```
  861:      A single sentence summarising rule-based interpretation,
 1294:       <span class="ml-item">${renderBadge("COM")} <span>Commentary — rule-based interpretation</span></span>
 1353:     renderPlacesTimelineCard(),                                      // Mon-YYYY axis
 1357:     renderSectionRow(renderStateShare(), renderPlacesBandCard()),    // state share now count+%
 2016:           State-level training-supply data is best interpreted at the industry level
 2107:   // Weighted-decile interpretation
 2341: function renderPlacesTimelineCard() {
 2735: function renderPlacesBandCard() {
```

**`docs\review.html`** (5 hits shown, capped at 15)
```
  719:   renderPending();
  722: function renderPending() {
 1324:       renderPending();
 1356: document.getElementById("f-band").addEventListener("change", renderPending);
 1357: document.getElementById("f-brand").addEventListener("change", renderPending);
```

### births

**`layer1_files_inspect.py`** (3 hits shown, capped at 15)
```
  229: # --- Births file search (Layer 2 dependency) ---
  230: emit("## Births data — file search")
  256:     emit("NO MATCHES — births file not present in expected locations.")
```

**`layer2_step8_apply.py`** (15 hits shown, capped at 15)
```
    2: layer2_step8_apply.py — ABS Births SA2 ingest.
    9:   abs_data/Births_SA2_2011_2024.xlsx
   13:     row 6 — sub-header (ERP | Births | TFR repeated per year)
   16:   Births = year_col + 1 (verified from sub-header at runtime, not assumed).
   22:   audit_log row, action='abs_sa2_births_ingest_v1'   (apply only)
   25:   CREATE TABLE abs_sa2_births_annual (
   28:     births_count INTEGER,           -- NULL for 'np' or non-numeric
   37:   - all births_count values are NULL or non-negative integer
   52: XLSX_PATH = "abs_data/Births_SA2_2011_2024.xlsx"
   53: TARGET_TABLE = "abs_sa2_births_annual"
   54: AUDIT_ACTION = "abs_sa2_births_ingest_v1"
   66: ABS_NATIONAL_BIRTHS = {
  110: def coerce_births(v):
  133: # Detect (year -> births_col_idx) mapping for a sheet
  136:     """For one state sheet, return {year: 0-based-col-idx-of-births}.
```

**`layer2_step8_diag.py`** (15 hits shown, capped at 15)
```
    2: layer2_step8_diag.py — Read-only diagnostic for ABS Births SA2 ingest.
    5:   abs_data/Births_SA2_2011_2024.xlsx  (ABS Cat 3301.0 Table 2)
   18:   7. National aggregate sanity check vs ABS published births
   31: XLSX_PATH = "abs_data/Births_SA2_2011_2024.xlsx"
   38: # ABS published national births (Cat 3301.0 Table 1) — sanity baseline
   40: ABS_NATIONAL_BIRTHS = {
   97: w("# Layer 2 Step 8 — Births SA2 Diagnostic")
  204: # Run probe for every sheet (births workbook usually has Contents + Table sheets)
  336:                 exp = ABS_NATIONAL_BIRTHS.get(year)
  370: w("CREATE TABLE abs_sa2_births_annual (")
  373: w("  births_count INTEGER,")
  376: w("CREATE INDEX idx_abs_sa2_births_annual_sa2  ON abs_sa2_births_annual(sa2_code);")
  377: w("CREATE INDEX idx_abs_sa2_births_annual_year ON abs_sa2_births_annual(year);")
  380: w("**Audit log row** (action='abs_sa2_births_ingest_v1', subject_type="
  381:   "'abs_sa2_births_annual').")
```

**`layer3_apply.py`** (4 hits shown, capped at 15)
```
   11:   - abs_sa2_births_annual
   84:         "canonical": "sa2_births_count",
   85:         "source_table": "abs_sa2_births_annual",
   86:         "value_column": "births_count",
```

**`layer3_diag.py`** (15 hits shown, capped at 15)
```
  127:         cur.execute("SELECT COUNT(DISTINCT sa2_code) FROM abs_sa2_births_annual")
  128:         findings["distinct_sa2_births"] = cur.fetchone()[0]
  130:         findings["distinct_sa2_births"] = None
  254:     # 2d. abs_sa2_births_annual — yearly summary
  259:                    SUM(CASE WHEN births_count IS NULL THEN 1 ELSE 0 END) AS n_nulls,
  260:                    SUM(births_count) AS national_total
  261:               FROM abs_sa2_births_annual
  265:         findings["births_yearly"] = cur.fetchall()
  267:         findings["births_yearly_err"] = str(e)
  390:     ("sa2_births_count",
  391:      "abs_sa2_births_annual",
  392:      "births_count",
  394:      "SA2 births, by year",
  453:     yrs_max = 14  # full history for births / ERP
  523:     w(f"| `abs_sa2_births_annual` "
```

**`layer4_consistency_probe.py`** (2 hits shown, capped at 15)
```
    7:      births, unemployment, the income trio, the LFP triplet, plus
   37:     "births":           ["births", "birth_count", "tfr"],
```

### unemployment

**`generate_dashboard.py`** (2 hits shown, capped at 15)
```
  313:                 'unemployment_rate':    None,
 3054:                 <div class="stat-label">Unemployment</div>
```

**`layer2_step1b_spotcheck.py`** (2 hits shown, capped at 15)
```
   14:   5. SALM coverage uplift: services that now join to abs_sa2_unemployment_quarterly
  294:     ("abs_sa2_unemployment_quarterly", "SALM (Step 5)"),
```

**`layer2_step5_apply.py`** (15 hits shown, capped at 15)
```
    2: Layer 2 Step 5 APPLY — SALM SA2 unemployment ingest
   12:   abs_sa2_unemployment_quarterly (
   15:     rate          REAL,        -- smoothed_unemployment_rate (%)
   16:     count         INTEGER,     -- smoothed_unemployment_count
   26:   - 3 sheets: 'Smoothed SA2 unemployment rate',
   27:               'Smoothed SA2 unemployment',
   67:     "rate": "Smoothed SA2 unemployment rate",
   68:     "count": "Smoothed SA2 unemployment",
   74: SUBJECT_TYPE = "abs_sa2_unemployment_quarterly"
  353:             CREATE TABLE IF NOT EXISTS abs_sa2_unemployment_quarterly (
  363:                     "ON abs_sa2_unemployment_quarterly(year_qtr)")
  366:         cur.execute("SELECT COUNT(*) FROM abs_sa2_unemployment_quarterly")
  381:                 "INSERT INTO abs_sa2_unemployment_quarterly "
  390:         cur.execute("SELECT COUNT(*) FROM abs_sa2_unemployment_quarterly")
  393:                     "FROM abs_sa2_unemployment_quarterly")
```

**`layer2_step5_diag.py`** (9 hits shown, capped at 15)
```
    2: Layer 2 Step 5 DIAGNOSTIC — SALM SA2 unemployment layout discovery
   65:     if "count" in s or "unemploy" in s:
  330:         WHERE type='table' AND name='abs_sa2_unemployment_quarterly'
  333:         cur.execute("SELECT COUNT(*) FROM abs_sa2_unemployment_quarterly")
  335:         print(f"abs_sa2_unemployment_quarterly already exists ({n:,} rows)")
  336:         findings.append(f"- ⚠️ `abs_sa2_unemployment_quarterly` already "
  340:         print("abs_sa2_unemployment_quarterly: does not exist (apply "
  342:         findings.append("- `abs_sa2_unemployment_quarterly`: does not "
  362:         "target_table": "abs_sa2_unemployment_quarterly",
```

**`layer2_step5_spotcheck.py`** (12 hits shown, capped at 15)
```
    3: Confirms abs_sa2_unemployment_quarterly is queryable end-to-end and
   19: cur.execute("SELECT COUNT(*) FROM abs_sa2_unemployment_quarterly")
   23:             "FROM abs_sa2_unemployment_quarterly")
   27:             "FROM abs_sa2_unemployment_quarterly")
   35:     FROM abs_sa2_unemployment_quarterly
   54:     LEFT JOIN abs_sa2_unemployment_quarterly u
   63: # 4. Distribution of latest-quarter unemployment rates
   69:     FROM abs_sa2_unemployment_quarterly
   78: print("Sample 5 services + 2025-Q4 SALM unemployment:")
   82:     JOIN abs_sa2_unemployment_quarterly u
   94: print("Ellenbrook WA — SALM unemployment trajectory:")
  107:         FROM abs_sa2_unemployment_quarterly
```

**`layer2_step5b_prime_apply.py`** (4 hits shown, capped at 15)
```
   60:     (54, "ee_unemployment_rate_persons_pct",        "census", "pct"),
   95:     "ee_unemployment_rate_persons_pct":  (2, 12),
  430:                 "Bachelor %; persons unemployment rate + LFP %; jobs counts; "
  434:                 "unemployment, employment-to-pop for 2011/2016/2021). Recovers "
```

**`layer2_step5b_prime_diag.py`** (2 hits shown, capped at 15)
```
   48:     ("unemployment",        ["unemployment", "unemployed", "jobless"]),
  367:     L.append("   - Census labour: col 54 (Unemployment rate %),")
```

**`layer2_step5b_prime_spotcheck.py`** (1 hits shown, capped at 15)
```
  119:                        "ee_lfp_persons_pct", "ee_unemployment_rate_persons_pct",
```

**`layer2_step5b_prime_t33_extract.py`** (1 hits shown, capped at 15)
```
    6: per (year, sex), computes LFP rate + Unemployment rate +
```

**`layer2_step5b_spotcheck.py`** (3 hits shown, capped at 15)
```
  109: # also have lower unemployment? Quick correlation peek.
  117:     LEFT JOIN abs_sa2_unemployment_quarterly u
  135:     LEFT JOIN abs_sa2_unemployment_quarterly u
```

**`layer3_apply.py`** (3 hits shown, capped at 15)
```
   14:   - abs_sa2_unemployment_quarterly
   92:         "canonical": "sa2_unemployment_rate",
   93:         "source_table": "abs_sa2_unemployment_quarterly",
```

**`layer3_diag.py`** (6 hits shown, capped at 15)
```
  269:     # 2e. abs_sa2_unemployment_quarterly — latest 4 quarters
  276:               FROM abs_sa2_unemployment_quarterly
  396:     ("sa2_unemployment_rate",
  397:      "abs_sa2_unemployment_quarterly",
  400:      "Unemployment rate, latest quarter",
  678:     w("### 2.5 `abs_sa2_unemployment_quarterly` — recent quarters")
```

**`layer4_consistency_probe.py`** (2 hits shown, capped at 15)
```
    7:      births, unemployment, the income trio, the LFP triplet, plus
   38:     "unemployment":     ["unemployment", "unemploy"],
```

**`docs\index.html`** (1 hits shown, capped at 15)
```
 2732:                 <div class="stat-label">Unemployment</div>
```

### income

**`layer2_step5b_apply.py`** (9 hits shown, capped at 15)
```
   30:   median_equiv_household_income_weekly       col 11  Census-only ($, weekly)
   31:   median_employee_income_annual              col 26  Annual ($)
   35:   median_total_income_excl_pensions_annual   col 50  Annual ($)
   72:     (11, "median_equiv_household_income_weekly", "census"),
   73:     (26, "median_employee_income_annual", "annual"),
   77:     (50, "median_total_income_excl_pensions_annual", "annual"),
  209:     target = "median_equiv_household_income_weekly"
  225:     target = "median_employee_income_annual"
  245:     target = "median_equiv_household_income_weekly"
```

**`layer2_step5b_spotcheck.py`** (4 hits shown, capped at 15)
```
   65:      AND x.metric_name = 'median_equiv_household_income_weekly'
   82:      AND x.metric_name = 'median_equiv_household_income_weekly'
  120:       AND x.metric_name = 'median_equiv_household_income_weekly'
  138:       AND x.metric_name = 'median_equiv_household_income_weekly'
```

**`layer3_apply.py`** (6 hits shown, capped at 15)
```
  101:         "canonical": "sa2_median_employee_income",
  104:         "filter_clause": "metric_name = 'median_employee_income_annual'",
  109:         "canonical": "sa2_median_household_income",
  112:         "filter_clause": "metric_name = 'median_equiv_household_income_weekly'",
  117:         "canonical": "sa2_median_total_income",
  120:         "filter_clause": "metric_name = 'median_total_income_excl_pensions_annual'",
```

**`layer3_diag.py`** (4 hits shown, capped at 15)
```
  402:     ("sa2_median_employee_income",
  404:      "value where metric_name = 'median_employee_income' (verify)",
  408:     ("sa2_median_total_income_excl_govt",
  410:      "value where metric_name = 'median_total_income_excl_govt' (verify)",
```

**`layer4_consistency_probe.py`** (3 hits shown, capped at 15)
```
   39:     "income":           ["median_employee_income", "median_household_income",
   40:                          "median_total_income", "household_income",
   41:                          "employee_income", "total_income"],
```

**`module2b_catchment.py`** (2 hits shown, capped at 15)
```
  118: def estimate_ccs_rate(weekly_household_income: float) -> float:
  124:         if lo <= weekly_household_income < hi:
```

### lfp

**`layer2_step5b_apply.py`** (1 hits shown, capped at 15)
```
    5:   - Drop labour_force_participation_pct (col 54). Caught in v2 dry-run:
```

**`layer2_step5b_diag.py`** (2 hits shown, capped at 15)
```
  221:         "EDUCATION & EMPLOYMENT (target: female labour force participation)",
  223:             "labour force participation",
```

**`layer2_step5b_diag_v2.py`** (1 hits shown, capped at 15)
```
   52:     "labour force participation",
```

**`layer2_step5b_diag_v3.py`** (1 hits shown, capped at 15)
```
   53:     "labour force participation",
```

**`layer2_step5b_prime_apply.py`** (6 hits shown, capped at 15)
```
   61:     (55, "ee_lfp_persons_pct",                      "census", "pct"),
   77:     ("F", "lfp_rate_pct",   "census_lfp_females_pct"),
   80:     ("M", "lfp_rate_pct",   "census_lfp_males_pct"),
   96:     "ee_lfp_persons_pct":                (50, 75),
  100:     "census_lfp_females_pct":            (50, 70),
  101:     "census_lfp_males_pct":              (60, 80),
```

**`layer2_step5b_prime_diag.py`** (1 hits shown, capped at 15)
```
   37:     ("labour_force_partic", ["labour force participation", "participation rate",
```

**`layer2_step5b_prime_spotcheck.py`** (9 hits shown, capped at 15)
```
   10:   5. Cross-source validation: ee_lfp_persons_pct vs derived persons LFP
   97:         # Fallback: first 4 SA2s with rows in all three census years for ee_lfp_persons_pct
  100:             WHERE metric_name = 'ee_lfp_persons_pct'
  119:                        "ee_lfp_persons_pct", "ee_unemployment_rate_persons_pct",
  120:                        "census_lfp_females_pct", "census_lfp_males_pct",
  165:         WHERE metric_name = 'census_lfp_females_pct' AND year = 2021
  262:     # 6. Cross-source validation: ee_lfp_persons_pct (EE DB) vs T33-derived
  270:     t33_lookup = {}  # (sa2, year) -> lfp_persons_pct
  285:         WHERE metric_name = 'ee_lfp_persons_pct'
```

**`layer3_apply.py`** (6 hits shown, capped at 15)
```
  125:         "canonical": "sa2_lfp_persons",
  128:         "filter_clause": "metric_name = 'ee_lfp_persons_pct'",
  133:         "canonical": "sa2_lfp_females",
  136:         "filter_clause": "metric_name = 'census_lfp_females_pct'",
  141:         "canonical": "sa2_lfp_males",
  144:         "filter_clause": "metric_name = 'census_lfp_males_pct'",
```

**`layer3_diag.py`** (7 hits shown, capped at 15)
```
  414:     ("sa2_lfp_persons",
  416:      "value where metric_name = 'ee_lfp_persons_pct' (verify)",
  418:      "Labour force participation, persons",
  420:     ("sa2_lfp_females",
  422:      "value where metric_name = 'census_lfp_females_pct' (verify)",
  426:     ("sa2_lfp_males",
  428:      "value where metric_name = 'census_lfp_males_pct' (verify)",
```

**`layer4_consistency_probe.py`** (2 hits shown, capped at 15)
```
   42:     "lfp":              ["lfp_persons", "lfp_females", "lfp_males",
   43:                          "labour_force_participation", "labour force participation"],
```

### seifa_palette

**`catchment_html.py`** (3 hits shown, capped at 15)
```
  154:     irsd      = c.get("irsd_decile")
  155:     irsad     = c.get("irsad_decile")
  260:                     IRSD: <b>{irsd or "n/a"}/10</b> &nbsp;|&nbsp; IRSAD: <b>{irsad or "n/a"}/10</b>
```

**`centre_page.py`** (3 hits shown, capped at 15)
```
  363:         # --- CATCHMENT block (SEIFA + ARIA) ---
  365:             "seifa_decile": {
  367:                 "value": r.get("seifa_decile"),
```

**`generate_dashboard.py`** (10 hits shown, capped at 15)
```
   58:     irsd_label = str(catchment.get("irsd_label", "") or "").replace("_", " ")
   79:     seifa_desc = irsd_label.capitalize() if irsd_label else ""
   82:     parts = [p for p in [seifa_desc, demand_desc, supply_desc] if p]
  195:     def _ccs_insight(ccs_rate, irsd_decile):
  294:                 'irsd_decile':          c.get('irsd_decile'),
  295:                 'irsd_label':           c.get('irsd_label'),
  308:                 'ccs_insight':          _ccs_insight(c.get('est_ccs_rate'), c.get('irsd_decile')),
 3044:                 <div class="stat-label">SEIFA (IRSD)</div>
 3045:                 <div class="stat-value" style="font-size:20px">${{sa2.irsd_decile ? sa2.irsd_decile + '/10' : 'n/a'}}</div>
 3046:                 <div style="font-size:10px;color:var(--muted);margin-top:3px">${{(sa2.irsd_label || '').replace('_',' ')}}</div>
```

**`ingest_nqs_snapshot.py`** (9 hits shown, capped at 15)
```
   12:     lat, lng, aria_plus, seifa_decile, service_sub_type,
  105:     "SEIFA",
  142: def _to_seifa(v):
  143:     """SEIFA: integer 1..10, or None. '-', 0, '', NULL all → None."""
  195:             "seifa":         _to_seifa(row[col_ix["SEIFA"]]),
  275:         required = {"aria_plus", "seifa_decile", "service_sub_type",
  320:             ("seifa_decile",              lambda r: r["seifa"]),
  422:                 "  seifa_decile             = COALESCE(?, seifa_decile), "
  440:                     rec["lat"], rec["lng"], rec["aria"], rec["seifa"],
```

**`layer1_recon.py`** (2 hits shown, capped at 15)
```
   90:     ("seifa_decile / sa2_code coverage on active services",
   92:                COUNT(seifa_decile) AS with_seifa,
```

**`layer2_step4_nqaits_ingest.py`** (4 hits shown, capped at 15)
```
   53:     "seifa":                    ["SEIFA"],
   91:     "aria", "seifa",
  120:     seifa                     TEXT,
  337:                     cell_to_text(row[cols["seifa"]]) if "seifa" in cols and cols["seifa"] < len(row) else None,
```

**`layer2_step4_nqaits_preflight_v2.py`** (1 hits shown, capped at 15)
```
   21:     "seifa":                    ["SEIFA"],
```

**`layer3_diag.py`** (7 hits shown, capped at 15)
```
  432:     ("seifa_decile_sa2",
  434:      "seifa_decile aggregated to SA2 mode",
  435:      "(decision needed: derive from services or import ABS SEIFA)",
  436:      "SEIFA IRSD decile at SA2 level (national cohort, raw passthrough)",
  451:     yrs_min = 1   # static metrics like SEIFA: 1 year
  807:     w("**O5.** SEIFA: include in `layer3_sa2_metric_banding` as a "
  808:       "national-cohort passthrough, OR leave as raw `services.seifa_decile` "
```

**`layer3_precedent_survey.py`** (3 hits shown, capped at 15)
```
   68:     "seifa":        r"seifa",
   83:     "quartile", "score", "tier", "cohort", "seifa", "aria", "peer",
  471:     w("Survey evidence: _[fill in - note any precedent like SEIFA decile "
```

**`layer4_consistency_probe.py`** (4 hits shown, capped at 15)
```
    8:      seifa for palette comparison) — Python files build payloads,
   44:     "seifa_palette":    ["irsd", "irsad", "seifa"],
   58:     r"(?i)(histogram|sparkline|decile|band|chip|fact|render|draw|primitive|widget|seifa|cohort)"
  140:     buf.append("\n## 3. Visual-primitive CSS class names (filtered: histogram/sparkline/decile/band/chip/fact/render/draw/seifa/cohort)\n")
```

**`layer4_design_probe.py`** (12 hits shown, capped at 15)
```
   11:      decile / SEIFA / band / percentile / weighted_decile / irsd
   15:      Now / Trajectory / Position / SEIFA / decile / band / peer / cohort.
   16:   3. Operator + catchment SEIFA primitive: keyword hits in
   18:      HTML partials that look SEIFA / decile related. This is the
   42:     "decile", "seifa", "band", "percentile",
   43:     "weighted_decile", "weighted decile", "irsd", "cohort",
  111:         r'\b(id|class)="([^"]*\b(?:now|trajectory|position|seifa|decile|band|peer|cohort)\b[^"]*)"',
  191:         "**/_seifa*.html", "**/_decile*.html", "**/_band*.html",
  231:         buf.append("\n### Keyword hits — decile / seifa / band / percentile / wd / irsd / cohort\n\n```\n")
  259:         buf.append("```\n\n### Section / card markers (now / trajectory / position / seifa / decile / band / peer / cohort)\n\n```\n")
  267:     # 3. Operator/catchment SEIFA primitive (visual reuse target)
  268:     write_section(buf, "3. Operator / catchment SEIFA primitive — reuse target")
```

**`migrate_schema_v0_4.py`** (2 hits shown, capped at 15)
```
    8:   seifa_decile             INTEGER   -- 1..10, nullable
   51:     ("seifa_decile",             "INTEGER", "SEIFA decile 1..10"),
```

**`module2b_catchment.py`** (15 hits shown, capped at 15)
```
   13:   - SEIFA IRSD + IRSAD deciles (socio-economic indicators)
   55: SEIFA_FILE   = ABS_DIR / "Family and Community Database.xlsx"
   63: IRSD_COL     = "SEIFA Index of relative socio-economic disadvantage (IRSD) - rank within Australia (decile)"
   64: IRSAD_COL    = "SEIFA Index of relative socio-economic advantage and disadvantage (IRSAD) - rank within Australia (decile)"
  140: def fee_sensitivity_label(irsd_decile: Optional[int], ccs_rate: float) -> str:
  142:     Classify fee sensitivity based on IRSD decile and CCS rate.
  143:     IRSD decile 1 = most disadvantaged, 10 = least disadvantaged.
  145:     if irsd_decile is None:
  147:     if irsd_decile <= 3:
  149:     if irsd_decile <= 6:
  497: def seifa_label(decile: Optional[int]) -> str:
  511:     irsd     = c.get("irsd_decile")
  512:     irsad    = c.get("irsad_decile")
  532:         f"  IRSD decile:     {irsd or 'n/a'}/10  [{seifa_label(irsd).upper()}]",
  533:         f"  IRSAD decile:    {irsad or 'n/a'}/10",
```

**`operator_page.py`** (15 hits shown, capped at 15)
```
   40:   - Tier 2 columns on services (aria_plus, seifa_decile,
   43:   - _compute_catchment uses services.seifa_decile directly;
  339:                s.aria_plus, s.seifa_decile, s.service_sub_type,
  382:          aria_plus, seifa_decile, sub_type,
  412:             "seifa_decile":             seifa_decile,
  720: def _seifa_band(decile):
  742:     seifa_populated_n = 0
  745:         d = s.get("seifa_decile")
  747:         band = _seifa_band(d)
  752:         seifa_populated_n += 1
  759:     seifa_block = {
  760:         "populated":        seifa_populated_n > 0,
  761:         "populated_count":  seifa_populated_n,
  767:         "source":           "ACECQA SEIFA via NQS Data Q4 2025",
  773:         "populated":       seifa_block["populated"] or cache_block.get("populated", False),
```

**`test_operator.py`** (1 hits shown, capped at 15)
```
   95:     print(f"    weighted_seifa      : {c.get('weighted_seifa')}")
```

**`tier2_diagnose.py`** (8 hits shown, capped at 15)
```
   12:      (ARIA+, SEIFA, Lat/Lng, Service Sub Type, Final Report Sent Date)
   45:     "SEIFA",
  187:     # ── SEIFA value range ───────────────────────────────────────
  188:     print("\n── SEIFA value inspection ──")
  189:     seifa_vals = [r.get("SEIFA") for r in records if r.get("SEIFA") is not None]
  190:     if seifa_vals:
  194:         for v in seifa_vals:
  208:         print("  No SEIFA values present")
```

**`validate_tier2.py`** (10 hits shown, capped at 15)
```
   16:                SUM(CASE WHEN seifa_decile IS NOT NULL THEN 1 ELSE 0 END) AS seifa_n,
   29:     print(f"    seifa populated      : {stats[3]}/{n}")
   47:     # SEIFA decile distribution
   48:     seifa_dist = conn.execute("""
   49:         SELECT seifa_decile, COUNT(*)
   53:          GROUP BY seifa_decile ORDER BY seifa_decile
   55:     print("  SEIFA decile distribution:")
   56:     for dec, ct in seifa_dist:
   73:         SELECT service_name, lat, lng, aria_plus, seifa_decile,
   82:         print(f"      ARIA={r[3]!r} SEIFA={r[4]} sub={r[5]!r}")
```

**`docs\centre.html`** (5 hits shown, capped at 15)
```
  578:     { l: "SEIFA decile",    n: centre.catchment.seifa_decile.value ?? "—" },
  722:         <span class="k">SEIFA decile</span>
  724:           <b>${c.seifa_decile.value ?? "—"}</b>
  725:           ${c.seifa_decile.value != null ? '<span style="color:var(--text-mute);font-size:11px;">/10</span>' : ""}
  726:           ${renderBadge("OBS", { source: "ABS SEIFA, joined via SA2" }, true)}
```

**`docs\index.html`** (3 hits shown, capped at 15)
```
 2722:                 <div class="stat-label">SEIFA (IRSD)</div>
 2723:                 <div class="stat-value" style="font-size:20px">${sa2.irsd_decile ? sa2.irsd_decile + '/10' : 'n/a'}</div>
 2724:                 <div style="font-size:10px;color:var(--muted);margin-top:3px">${(sa2.irsd_label || '').replace('_',' ')}</div>
```

**`docs\operator.html`** (15 hits shown, capped at 15)
```
 1085:        "SEIFA · places-weighted". Histogram gets 22px of top margin
 1102:        Catchment section renders a SEIFA decile
 2056: // ── Catchment section (v5: renders real SEIFA, keeps placeholders
 2060:   const seifa = c.seifa || {};
 2063:   // If neither SEIFA nor the old cache has anything, show placeholder
 2064:   if (!seifa.populated && !c.cache_populated) {
 2069:         <span class="will-show">Will show: <b>weighted SEIFA decile headline</b>,
 2078:   // SEIFA sub-block is what Tier 2 gives us. Render it.
 2079:   const hist   = seifa.histogram || {};
 2080:   const bc     = seifa.band_counts || {low:0, mid:0, high:0, unknown:0};
 2081:   const bp     = seifa.band_places || {low:0, mid:0, high:0, unknown:0};
 2082:   const wd     = seifa.weighted_decile;
 2083:   const popN   = seifa.populated_count || 0;
 2084:   const totalN = seifa.total_services || totalServices;
 2123:     <h3>Portfolio catchment profile <span class="note">SEIFA · places-weighted</span></h3>
```

**`index.html`** (11 hits shown, capped at 15)
```
  715:     "irsd_decile": 10,
  716:     "irsd_label": "highly_advantaged",
  996:     "irsd_decile": 10,
  997:     "irsd_label": "highly_advantaged",
 1290:     "irsd_decile": 7,
 1291:     "irsd_label": "advantaged",
 1649:     "irsd_decile": 8,
 1650:     "irsd_label": "advantaged",
 1839:     "irsd_decile": 4,
 1840:     "irsd_label": "disadvantaged",
 2117:                         <div class="metric-trend">IRSD ${catchment.irsd_decile}/10 • ${catchment.irsd_label}</div>
```

## 2. CSS variables / palette tokens (docs/*.html)

### `docs\centre.html` (18 variables)
```
  --accent: #4a9eff
  --amber: #fbbf24
  --amber-bg: #2f2310
  --bg: #0f1419
  --border: #2d343f
  --green: #4ade80
  --green-bg: #14301e
  --grey: #94a3b8
  --panel: #1a1f26
  --panel-2: #232933
  --panel-3: #2a313c
  --purple: #a78bfa
  --purple-bg: #1f1a2e
  --red: #f87171
  --red-bg: #2e1414
  --text: #e6e8eb
  --text-dim: #9aa4b1
  --text-mute: #6b7684
```

### `docs\dashboard.html` (16 variables)
```
  --accent: #3d7eff
  --accent2: #00c9a7
  --bg: #0f1117
  --border: #2a2f3f
  --display: 'Playfair Display', serif
  --fgc: #9b59b6
  --font: 'DM Sans', sans-serif
  --hot: #e05c3a
  --mono: 'DM Mono', monospace
  --muted: #8890a8
  --radius: 10px
  --surface: #181c26
  --surface2: #1e2333
  --text: #e8eaf0
  --warm: #d4890a
  --watch: #5a6480
```

### `docs\index.html` (16 variables)
```
  --accent: #3d7eff
  --accent2: #00c9a7
  --bg: #0f1117
  --border: #2a2f3f
  --display: 'Playfair Display', serif
  --fgc: #9b59b6
  --font: 'DM Sans', sans-serif
  --hot: #e05c3a
  --mono: 'DM Mono', monospace
  --muted: #8890a8
  --radius: 10px
  --surface: #181c26
  --surface2: #1e2333
  --text: #e8eaf0
  --warm: #d4890a
  --watch: #5a6480
```

### `docs\operator.html` (18 variables)
```
  --accent: #4a9eff
  --amber: #fbbf24
  --amber-bg: #2f2310
  --bg: #0f1419
  --border: #2d343f
  --green: #4ade80
  --green-bg: #14301e
  --grey: #94a3b8
  --panel: #1a1f26
  --panel-2: #232933
  --panel-3: #2a313c
  --purple: #a78bfa
  --purple-bg: #1f1a2e
  --red: #f87171
  --red-bg: #2e1414
  --text: #e6e8eb
  --text-dim: #9aa4b1
  --text-mute: #6b7684
```

### `docs\review.html` (18 variables)
```
  --accent: #4a9eff
  --amber: #fbbf24
  --amber-bg: #2f2310
  --bg: #0f1419
  --border: #2d343f
  --green: #4ade80
  --green-bg: #14301e
  --grey: #94a3b8
  --panel: #1a1f26
  --panel-2: #232933
  --panel-3: #2a313c
  --purple: #a78bfa
  --purple-bg: #1f1a2e
  --red: #f87171
  --red-bg: #2e1414
  --text: #e6e8eb
  --text-dim: #9aa4b1
  --text-mute: #6b7684
```

### `index.html` (9 variables)
```
  --accent: #58a6ff
  --accent2: #f78166
  --bg: #0d1117
  --border: #30363d
  --card-bg: #161b22
  --hover: #21262d
  --mono: 'SF Mono', Consolas, 'Roboto Mono', monospace
  --muted: #7d8590
  --text: #f0f6fc
```

## 3. Visual-primitive CSS class names (filtered: histogram/sparkline/decile/band/chip/fact/render/draw/seifa/cohort)

### `docs\centre.html`
```
  .brand-chip
  .chip
  .fact
```

### `docs\operator.html`
```
  .brand-chip
  .chip
  .chip-inline
  .fact
```

### `docs\review.html`
```
  .brand-chip
```

## 4. JS visual primitive functions in docs/*.html (filtered for relevance)

### `docs\centre.html`
```
  render
  renderBadge
  renderCatchmentCard
  renderCommentary
  renderHeader
  renderMethodologyLegend
  renderNqsCard
  renderPlacesCard
  renderQaCard
  renderTenureCard
```

### `docs\dashboard.html`
```
  renderOpList
  renderOperator
```

### `docs\index.html`
```
  renderCatchmentDetail
  renderCatchmentSummaryRow
  renderOpList
  renderOperator
```

### `docs\operator.html`
```
  render
  renderAcquisition
  renderBadge
  renderBrownfieldGeography
  renderCatchment
  renderCentresTable
  renderCompetitive
  renderEntitiesTable
  renderGrowthSection
  renderHeader
  renderMethodologyLegend
  renderNotes
  renderNqsDonut
  renderOpportunities
  renderPlacesBandCard
  renderPlacesTimelineCard
  renderQuality
  renderRemoteness
  renderSectionRow
  renderSoftSpots
  renderStateShare
  renderStructural
  renderValuation
  renderWorkforce
```

### `docs\review.html`
```
  band
  renderBrandSummary
  renderClusterCard
  renderHistory
  renderIndividualCard
  renderPending
```
