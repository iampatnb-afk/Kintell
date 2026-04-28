# Layer 4 Design Probe — 2026-04-28T13:12:52

Repo root: `C:\Users\Patrick Bell\remara-agent`  
DB: `C:\Users\Patrick Bell\remara-agent\data\kintell.db` (read-only)

## 1. centre_page.py
Path: `centre_page.py`  (16738 bytes)

### Functions

| name | lines | args | first-line doc |
|---|---|---|---|
| `_connect` | 64–67 | - |  |
| `_row_to_dict` | 70–73 | row |  |
| `_parse_date` | 76–97 | s | Parse YYYY-MM-DD, ISO8601, 'Mon-YYYY', or DD/MM/YYYY. |
| `_months_since` | 100–105 | s |  |
| `_compute_inspection_cadence` | 108–141 | rating_issued_date, overall_rating | DER. Inspection cadence flag derived from rating_issued_date. |
| `_compute_remoteness` | 144–154 | aria_plus | OBS. ARIA+ band lookup. v2: handles both label-form and code-form. |
| `_compute_brownfield` | 157–188 | approval_granted_date, last_transfer_date | DER. Brownfield = a transfer date exists and post-dates the original |
| `_compute_subtype` | 191–220 | service_sub_type | OBS. service_sub_type with the Harmony-exclusion handling. |
| `_qa_scores` | 223–239 | service_row | OBS. Quality assessment area scores qa1..qa7, only those populated. |
| `get_centre_payload` | 242–405 | service_id | Top-level entry point. Returns a fully-hydrated centre payload, or |
| `_commentary_lines` | 408–454 | header, nqs, places, tenure, subtype | COM. Rule-based commentary lines. Conservative: skip if data missing. |

### Keyword hits — decile / seifa / band / percentile / wd / irsd / cohort

```
   45: # ARIA+ remoteness band labels. The aria_plus column stores label strings
  145:     """OBS. ARIA+ band lookup. v2: handles both label-form and code-form."""
  363:         # --- CATCHMENT block (SEIFA + ARIA) ---
```

## 2. docs/centre.html
Path: `docs\centre.html`  (28057 bytes, 888 lines)

Card-class element count: **0**

### Headings (in document order)

```
<h1> Kintell
<h2> ${htmlEscape(h.service_name || "Unnamed centre")}
<h3> NQS Rating
<h3> Places &amp; Service Type
<h3> Catchment
<h3> Quality Assessment Areas
<h3> Quality Assessment Areas <span class="note">${qa.length} populated</span>
<h3> Tenure
```

### Jinja constructs

```
```

### Section / card markers (now / trajectory / position / seifa / decile / band / peer / cohort)

```
(no markers found — Layer 4 will introduce these)
```

## 3. Operator / catchment SEIFA primitive — reuse target

### `module2b_catchment.py`  (29674 bytes)

```
   13:   - SEIFA IRSD + IRSAD deciles (socio-economic indicators)
   63: IRSD_COL     = "SEIFA Index of relative socio-economic disadvantage (IRSD) - rank within Australia (decile)"
   64: IRSAD_COL    = "SEIFA Index of relative socio-economic advantage and disadvantage (IRSAD) - rank within Australia (decile)"
  142:     Classify fee sensitivity based on IRSD decile and CCS rate.
  143:     IRSD decile 1 = most disadvantaged, 10 = least disadvantaged.
  497: def seifa_label(decile: Optional[int]) -> str:
  498:     if decile is None: return "unknown"
  499:     if decile <= 2:  return "highly_disadvantaged"
  500:     if decile <= 4:  return "disadvantaged"
  501:     if decile <= 6:  return "average"
  502:     if decile <= 8:  return "advantaged"
  511:     irsd     = c.get("irsd_decile")
  532:         f"  IRSD decile:     {irsd or 'n/a'}/10  [{seifa_label(irsd).upper()}]",
  533:         f"  IRSAD decile:    {irsad or 'n/a'}/10",
  593:     # SEIFA
  651:         # SEIFA
  704:     log.info(f"  SEIFA:        {len(seifa_df):,} SA2s")
  745:     log.info(f"  SEIFA loaded:       {sum(1 for l in enriched if l.get('catchment',{}).get('irsd_decile') is not None)}/{n}")
```

### `module2c_targeting.py`  (23634 bytes)

```
   16:   Centre count band      25 pts  (5-10 = 25, 3-4 or 11-12 = 15, 13-15 = 5)
```

### `operator_page.py`  (47003 bytes)

```
  648:             "scheme":    "ABS Remoteness Structure (5-band)",
  657:         "scheme":         "ABS Remoteness Structure (5-band)",
  720: def _seifa_band(decile):
  721:     if decile is None:
  724:         d = int(decile)
  747:         band = _seifa_band(d)
  748:         if band is None:
  754:         band_counts[band] += 1
  755:         band_places[band] += p
  763:         "weighted_decile":  round(w_sum / total_w, 2) if total_w else None,
  767:         "source":           "ACECQA SEIFA via NQS Data Q4 2025",
  774:         "seifa":           seifa_block,
  775:         "weighted_seifa":  seifa_block["weighted_decile"],
  844:     for sid, seifa, u5, inc, supply in rows:
  846:         if seifa is not None:
  847:             w_seifa += float(seifa) * w
```

### `docs\operator.html`  (113639 bytes)

```
  509:   /* Histograms — places-band, generic horizontal */
 1085:        "SEIFA · places-weighted". Histogram gets 22px of top margin
 1102:        Catchment section renders a SEIFA decile
 1103:        histogram + weighted decile + low/mid/high band split.
 1105:        5-band stacked bar with per-band chips. Both cards stop
 1121:        new Remoteness distribution placeholder (5-band ABS).
 2056: // ── Catchment section (v5: renders real SEIFA, keeps placeholders
 2060:   const seifa = c.seifa || {};
 2063:   // If neither SEIFA nor the old cache has anything, show placeholder
 2064:   if (!seifa.populated && !c.cache_populated) {
 2069:         <span class="will-show">Will show: <b>weighted SEIFA decile headline</b>,
 2070:         a <b>1–10 decile histogram</b>, a <b>low/mid/high band split</b>,
 2072:         supply-band exposure once the SA2 catchment cache is populated (Tier 3).</span>
 2078:   // SEIFA sub-block is what Tier 2 gives us. Render it.
 2079:   const hist   = seifa.histogram || {};
 2080:   const bc     = seifa.band_counts || {low:0, mid:0, high:0, unknown:0};
 2081:   const bp     = seifa.band_places || {low:0, mid:0, high:0, unknown:0};
 2082:   const wd     = seifa.weighted_decile;
 2083:   const popN   = seifa.populated_count || 0;
 2084:   const totalN = seifa.total_services || totalServices;
 2098:           <div title="Decile ${d}: ${n} centre${n===1?'':'s'}"
 2107:   // Weighted-decile interpretation
 2123:     <h3>Portfolio catchment profile <span class="note">SEIFA · places-weighted</span></h3>
 2125:     <div class="fact"><span class="k">Weighted SEIFA decile</span>
 2130:         <span>SEIFA decile distribution</span>
 2176:       SA2 catchment cache is populated (Tier 3). SEIFA above is live from the NQS snapshot.
 2596:         Matches the ABS 5-band classification used on the Kintell industry panel.</span>
 2601:   // v5: canonical 5-band ordering + short display labels
 2630:   const segs = CANON.map(band => {
 2631:     const n = bands[band] || 0;
 2633:     const p = places[band] || 0;
 2635:       <div style="flex:${n} 0 auto;background:${COLORS[band]};min-width:30px;padding:4px 6px;font-size:11px;color:#0b1020;"
 2636:            title="${htmlEscape(SHORT[band])}: ${n} centres, ${fmtN(p)} places (${pct(n, totalCentres)})">
 2637:         ${htmlEscape(SHORT[band])} ${n}
 2641:   // Per-band chip facts — only show bands with non-zero counts
 2642:   const chips = CANON.map(band => {
 2643:     const n = bands[band] || 0;
 2645:     const p = places[band] || 0;
 2647:       <div style="display:inline-flex;gap:8px;align-items:center;padding:4px 10px;border-radius:999px;background:rgba(255,255,255,.05);border:1px solid ${COLORS[band]}44;margin:2px 4px 2px 0;">
 2648:         <span style="width:8px;height:8px;border-radius:50%;background:${COLORS[band]};"></span>
```

## 4. layer3_sa2_metric_banding — schema + sample
Total rows: **23946**

### Schema — layer3_sa2_metric_banding

```
  sa2_code       TEXT     pk=1 notnull=1
  metric         TEXT     pk=2 notnull=1
  year           INTEGER  pk=3 notnull=1
  period_label   TEXT     pk=0 notnull=0
  cohort_def     TEXT     pk=4 notnull=1
  cohort_key     TEXT     pk=0 notnull=0
  cohort_n       INTEGER  pk=0 notnull=0
  raw_value      REAL     pk=0 notnull=0
  percentile     REAL     pk=0 notnull=0
  decile         INTEGER  pk=0 notnull=0
  band           TEXT     pk=0 notnull=0
```

### Schema — sa2_cohort

```
  sa2_code       TEXT     pk=1 notnull=1
  sa2_name       TEXT     pk=0 notnull=0
  state_code     TEXT     pk=0 notnull=0
  state_name     TEXT     pk=0 notnull=0
  ra_code        TEXT     pk=0 notnull=0
  ra_name        TEXT     pk=0 notnull=0
  ra_band        INTEGER  pk=0 notnull=0
```

### Indexes on layer3_sa2_metric_banding

```
  sqlite_autoindex_layer3_sa2_metric_banding_1: None
  idx_l3_sa2: CREATE INDEX idx_l3_sa2 ON layer3_sa2_metric_banding(sa2_code)
  idx_l3_metric: CREATE INDEX idx_l3_metric ON layer3_sa2_metric_banding(metric)
  idx_l3_band: CREATE INDEX idx_l3_band ON layer3_sa2_metric_banding(band)
```

### Per-metric stats (drives cohort_n display rule)

| metric | cohort_def | rows | min cn | max cn | rows cn<10 | rows cn 10-19 |
|---|---|---:|---:|---:|---:|---:|
| sa2_births_count | state_x_remoteness | 2450 | 2 | 417 | 46 | 62 |
| sa2_lfp_females | state_x_remoteness | 2386 | 1 | 411 | 49 | 62 |
| sa2_lfp_males | state_x_remoteness | 2397 | 1 | 414 | 48 | 62 |
| sa2_lfp_persons | state_x_remoteness | 2401 | 1 | 416 | 49 | 62 |
| sa2_median_employee_income | remoteness | 2398 | 60 | 1447 | 0 | 0 |
| sa2_median_household_income | remoteness | 2411 | 63 | 1447 | 0 | 0 |
| sa2_median_total_income | remoteness | 2402 | 60 | 1450 | 0 | 0 |
| sa2_total_population | state_x_remoteness | 2418 | 1 | 416 | 49 | 62 |
| sa2_under5_count | state | 2347 | 4 | 625 | 4 | 0 |
| sa2_unemployment_rate | state | 2336 | 62 | 623 | 0 | 0 |

### Sample SA2 — all metric rows for sa2_code `101021007`

```
{'sa2_code': '101021007', 'metric': 'sa2_births_count', 'year': 2024, 'period_label': None, 'cohort_def': 'state_x_remoteness', 'cohort_key': '1_2', 'cohort_n': 155, 'raw_value': 35.0, 'percentile': 13.2258, 'decile': 2, 'band': 'low'}
{'sa2_code': '101021007', 'metric': 'sa2_lfp_females', 'year': 2021, 'period_label': None, 'cohort_def': 'state_x_remoteness', 'cohort_key': '1_2', 'cohort_n': 151, 'raw_value': 58.59, 'percentile': 54.6358, 'decile': 6, 'band': 'mid'}
{'sa2_code': '101021007', 'metric': 'sa2_lfp_males', 'year': 2021, 'period_label': None, 'cohort_def': 'state_x_remoteness', 'cohort_key': '1_2', 'cohort_n': 153, 'raw_value': 65.92, 'percentile': 59.8039, 'decile': 6, 'band': 'mid'}
{'sa2_code': '101021007', 'metric': 'sa2_lfp_persons', 'year': 2021, 'period_label': None, 'cohort_def': 'state_x_remoteness', 'cohort_key': '1_2', 'cohort_n': 153, 'raw_value': 57.3, 'percentile': 52.6144, 'decile': 6, 'band': 'mid'}
{'sa2_code': '101021007', 'metric': 'sa2_median_employee_income', 'year': 2022, 'period_label': None, 'cohort_def': 'remoteness', 'cohort_key': '2', 'cohort_n': 505, 'raw_value': 55072.0, 'percentile': 56.3366, 'decile': 6, 'band': 'mid'}
{'sa2_code': '101021007', 'metric': 'sa2_median_household_income', 'year': 2021, 'period_label': None, 'cohort_def': 'remoteness', 'cohort_key': '2', 'cohort_n': 511, 'raw_value': 952.0, 'percentile': 54.501, 'decile': 6, 'band': 'mid'}
{'sa2_code': '101021007', 'metric': 'sa2_median_total_income', 'year': 2022, 'period_label': None, 'cohort_def': 'remoteness', 'cohort_key': '2', 'cohort_n': 505, 'raw_value': 48324.0, 'percentile': 36.1386, 'decile': 4, 'band': 'mid'}
{'sa2_code': '101021007', 'metric': 'sa2_total_population', 'year': 2024, 'period_label': None, 'cohort_def': 'state_x_remoteness', 'cohort_key': '1_2', 'cohort_n': 155, 'raw_value': 4484.0, 'percentile': 10.0, 'decile': 1, 'band': 'low'}
{'sa2_code': '101021007', 'metric': 'sa2_under5_count', 'year': 2024, 'period_label': None, 'cohort_def': 'state', 'cohort_key': '1', 'cohort_n': 625, 'raw_value': 208.0, 'percentile': 7.12, 'decile': 1, 'band': 'low'}
{'sa2_code': '101021007', 'metric': 'sa2_unemployment_rate', 'year': 2025, 'period_label': '2025-Q4', 'cohort_def': 'state', 'cohort_key': '1', 'cohort_n': 623, 'raw_value': 2.5, 'percentile': 25.4414, 'decile': 3, 'band': 'low'}
```
