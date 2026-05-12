# Centre v2 design pass: content map

*Created 2026-05-12 (next-session pickup after DEC-83 Commercial Layer V1 ship). Probe-first per DEC-65. **Status: RATIFIED 2026-05-12 — D-1 through D-12 batch-ratified by Patrick; DEC-84 minted in canonical DECISIONS.md. v1 stake + v2 build sequence cleared to proceed.***

*This doc takes the locked Centre v2 6-layer skeleton (per `project_centre_v2_redesign.md`) and proposes the content map: which existing piece + which DEC-83 new piece sits in which layer, in what tile, with what interaction. Joint design pass = content map + a small batch of layer-mechanics decisions, then v2 build follows.*

---

## RATIFIED SUMMARY (2026-05-12)

**DEC-84 minted in canonical DECISIONS.md.** Decision batch D-1 through D-12 ratified by Patrick as a single batch (no specific objections). The 6-layer page architecture, matrix-as-center-of-gravity framing, layer-by-layer content map, and 12 layer-mechanic locks all proceed as proposed in §3 + §4 of this doc.

**V1 ships:**
- 6-layer architecture: Layer 1 Header / Layer 2 Executive interpretation / Layer 3 Primary historical trends (~7 charts) / Layer 4 Secondary historical trends accordion / Layer 5 Institutional signal matrix (~52 rows, 9 categories) / Layer 6 Detail side-drawer
- v1's 5-card stack dissolves; every existing metric appears once in matrix; charted metrics also appear in Layer 3 (primary) or Layer 4 (secondary)
- DEC-83 Commercial Layer V1 substrate fully placed across Layers 1, 2, 5, 6 per §3
- Existing renderer inventory survives unchanged (`_renderFullRow`, `_renderLiteRow`, `_renderContextRow`, `_renderTrajectory`, `_renderIntentCopy`, `_renderIndustryBand`, `_renderDecileStrip`, `_renderBandChips`, `_renderCohortHistogram`, `_renderLiteDelta`, `_renderTrajectoryRangeBar`); two new render primitives needed (`MatrixRow`, `DrawerPanel`); one new helper (`_buildExecutiveHeadline`); `_renderAboutData` and `_renderTopNContext` migrate into drawer; `_renderWfsRangeBar` retires
- V1.5 pending-ingest rows render as Layer 5 matrix stubs with "Pending V1.5 A5/A6/B1/A7" status pill — keeps layer plan stable as ingests land
- Old `/centres/{id}` preserved via git tag `centre-v1-stake-2026-05-12` on commit `212b597` (pre-v2-build SHA) + `recon/v1_final_stake_2026-05-12/` bundle dir with v1 file copies + ROLLBACK.md recovery recipe (created BEFORE v2 build's first `centre_page.py` v24 edit)

**V2 banked from this design pass:**
- Measurement tools (two-point delta picker, decile-movement readout)
- Layer 5 matrix sort by signal strength (V1 = fixed display order)
- Layer 5 matrix filter chips beyond category quick-jump (search + filter-by-decile)
- Mobile/narrow-screen layout (<1024px breakpoint) — matrix row columns stack vertically
- Hover-preview drawer interaction (V1 is click-anywhere-on-row + `›` icon + ESC)

**Effort:** ~3.9 sess from this point.
- DEC-84 mint + design doc finalise: 0.1 sess (DONE)
- v1 stake (git tag + bundle dir + ROLLBACK.md): 0.1 sess
- `centre_page.py` v24 — payload schema `centre_payload_v7`: matrix structure assembly + flag computation + headline composition + drawer payload sub-tree: 1.0 sess
- `docs/centre_v2.html` parallel renderer at `/centre_v2/{id}`: 2.0 sess
- Verification capture (4 verifying SA2s × 2-3 service archetypes): 0.3 sess
- Smoke test + smoke-test docs in `docs/`: 0.2 sess
- Cut-over `/centres/{id}` → centre v2 renderer: 0.1 sess
- End-of-session monolith STD-35 + commit: 0.1 sess

Plus this design pass session itself (~1.0 sess including ratification + DEC-84 mint).

**Cross-effects unlocked:**
- **Group page (OI-NEW-17) deep-link entry point** seeded by Layer 6 operator-group drawer's chain detail
- **Child Safety satellite page deep-link** seeded by Layer 5 conditions/enforcement count rows linking to "coming soon" stubs
- **Competition satellite page deep-link** similarly seeded
- **Excel export framework (V1, separate DEC-candidate per ROADMAP §2.4)** — Layer 5 matrix structure confirmed as primary export source; one row per metric with all 8 columns flattened
- **V1.5 ingest queue render landing** now defaults to Layer 5 matrix rows; ingest scripts write to existing tables and the matrix renderer surfaces new metrics automatically per registry pattern. Reduces post-v2 ingest-render coupling work
- **Centre v2 build sequence** cleared to proceed: stake → `centre_page.py` v24 → `docs/centre_v2.html` → capture → smoke → cut-over → monolith

---

---

## 0. What's already locked (don't re-litigate)

Per `project_centre_v2_redesign.md`:

- **Six-layer structure:** Header / Executive interpretation / Primary historical trends / Secondary historical trends / Institutional signal matrix / Detail side-drawer
- **Detail = side drawer** (slide-in panel; not in-row expand, not modal, not tab)
- **Sparklines OK in matrix rows** (Lite-row rejection was contextual)
- **Histograms stay visible** (not collapsible) but redesigned less vertically dominant; peer 1-10 logic preserved
- **Measurement tools** (two-point delta picker, decile-movement readout) → V2 redesign-of-redesign, not this V1
- **Cut order:** Centre v2 → Child Safety → Competition. Child Safety + Competition are full surfaces with deep-link "coming soon" stubs in v2
- **Old `/centres/{id}` preservation:** git tag `centre-v1-stake-YYYY-MM-DD` + `recon/v1_final_stake_YYYY-MM-DD/` bundle directory before v2 build starts. v2 takes over `/centres/{id}` once verified
- **Sequencing:** ✅ OI-NEW-21 → ✅ DEC-83 daily-rate → **this design pass** → v2 parallel build → satellite pages

This doc decides content placement + layer mechanics, not the skeleton itself.

---

## 1. Probe findings — what we have to place

### 1.1 Current centre v3.31 surface (32 metrics, 5 cards, 6 helpers)

**5 cards in render order:**

| # | Card | Anchor | Rows | Sub-panels |
|---|---|---|---|---|
| 1 | Catchment Position | `renderCatchmentPositionCard` | 5 credit + 8 demographic = 13 | Demographic mix sub-panel |
| 2 | Population | `renderPopulationCard` | 4 | — |
| 3 | Education Infrastructure | `renderEducationInfrastructureCard` | 3 (5 banked) | — |
| 4 | Labour Market | `renderLabourMarketCard` | 8 | — |
| 5 | Workforce Supply Context | `renderWorkforceSupplyCard` | 4 (all deferred) | — |

**13 catchment rows in card #1:** sa2_supply_ratio (FULL/ratio_x/quarterly/7-band/about_data), sa2_demand_supply (FULL/ratio_x/quarterly/4-band/calibrated/about_data), sa2_child_to_place (FULL/ratio_x/quarterly/5-band/about_data), sa2_adjusted_demand (FULL/int/quarterly/decile-only/calibrated/about_data), sa2_demand_share_state (CONTEXT/percent_share/none/calibrated). Demographic mix sub-panel (8 LITE rows): sa2_nes_share (+ top-N languages context line), sa2_atsi_share, sa2_overseas_born_share (+ top-N COB context line), sa2_single_parent_family_share, sa2_parent_cohort_25_44_share, sa2_partnered_25_44_share, sa2_women_35_44_with_child_share, sa2_women_25_34_with_child_share.

**4 population rows:** sa2_under5_count (FULL/annual), sa2_total_population (FULL/annual), sa2_births_count (FULL/annual), sa2_under5_growth_5y (FULL/deferred).

**3 ACARA + 5 banked sector-mix rows in card #3:** sa2_school_count_total (LITE/18yr-annual), sa2_school_enrolment_total (LITE/18yr-annual), sa2_school_enrolment_govt_share (LITE/18yr-annual). Banked: govt/catholic/independent count + govt/catholic/independent enrolment shares.

**8 labour-market rows:** sa2_unemployment_rate (FULL/quarterly), sa2_median_employee_income (FULL/annual), sa2_median_household_income (LITE/3pt-Census), sa2_median_total_income (FULL/annual), sa2_lfp_persons (LITE/3pt), sa2_lfp_females (LITE/3pt), sa2_lfp_males (LITE/3pt), jsa_vacancy_rate (CONTEXT/deferred).

**4 workforce-supply context rows (all deferred wire-up):** jsa_ivi_4211_child_carer (state-month), jsa_ivi_2411_ect (state-month), ecec_award_rates (national fact), three_day_guarantee (national fact, Jan 2026).

**Render helpers:** `_renderFullRow`, `_renderLiteRow`, `_renderContextRow`, `_renderTrajectory`, `_renderAboutData` (4 entries: 4 catchment Full metrics), `_renderIntentCopy` (22 entries), `_renderIndustryBand` (3 metrics), `_renderTopNContext` (2 calls), `_renderDecileStrip`, `_renderBandChips`, `_renderCohortHistogram`, `_renderLiteDelta`, `_renderTrajectoryRangeBar`, `_renderWfsRangeBar`. Badges: OBS / DER / COM.

### 1.2 DEC-83 new substrate (in `kintell.db` from 2026-05-11)

| Source | What | Granularity | Pilot rows |
|---|---|---|---|
| `service_fee` | Daily rate per (service × age_band × session_type × as_of_date) | 5 age bands × 5 session types × 2018-2026 history | 8,220 fees / 109 of 130 services |
| `service_regulatory_snapshot` | NQS overall + prev (with issued dates), CCS-revoked-by-EA, last regulatory visit, hours mon-sun, provider sub-block (status / approval date / CCS-rev / trade name), website / phone / email | 1+ snapshots per service | 129 of 130 |
| `service_condition` | Conditions text on service or provider, level discriminator | 76 service + 9 provider = 85 conditions | 85 |
| `service_vacancy` | Vacancy posture per (service × age_band × observed_at), `has_vacancies` vs `no_vacancies_published` | 5 age bands × refresh history | 486 (352 has / 134 none) |
| `regulatory_events` (reused scaffold) | ACECQA enforcement actions per service, action_type / action_date / action_id | 1+ per service | 9 (all "Compliance notice issued") |
| `large_provider` + `large_provider_provider_link` | Operator-group dimension; `services.large_provider_id` flags membership | 13 chains in pilot | 13 chains, 92 provider links, 37 services flagged |

### 1.3 Out of scope for this design pass

- **V1.5 ingest queue not yet shipped:** A5 subtype-correct denominators, A6 SALM extension (LFP triplet → Full), B1 (`sa2_jsa_vacancy_rate`), C2-other render polish, C6. These are bundled into the v2 layer plan as **future-row slots** in Layer 4/5 with explicit "pending V1.5 ingest" stubs. The design must not block on them.
- **National commercial-layer scale-up** (130 → 18,223 services). Banked separately. Affects coverage of every DEC-83-derived row; v2 design assumes data flows through the existing layer pattern.
- **Excel export framework.** Layer 5 matrix structure is the natural export source; V1 export hooks land later as DEC-candidate.
- **PropCo Stream D, Stream A workforce visa, Stream E border exposure.** New streams plug into v2 layer plan additively; explicit slots reserved in §3, but their content is V1-broader work, not this design pass.

---

## 2. Strong opinion (review-and-react)

**v1 had five vertical cards, each 4-13 rows, all roughly equal weight.** Decision-critical metrics and demographic context shared the same visual treatment. Reading time was linear. Density grew with each ingest.

**v2 should reframe the page around four reading speeds:**

1. **30-second view (Layers 1-2):** identity + executive interpretation. Patrick's "30-sec" target.
2. **2-minute view (Layer 3):** primary trends — 6-8 most decision-critical charts, visually prominent.
3. **5-10 minute view (Layers 4-5):** secondary trends accordion + comprehensive matrix.
4. **Drill view (Layer 6):** side drawer for full methodology / source / commentary on any tile.

The matrix becomes the center of gravity. The cards-of-rows pattern from v1 dissolves into category groupings inside Layer 5. Existing helper inventory carries forward — no new render primitives needed for V1; only one new container (the matrix) and one new pattern (the side drawer).

**This is a redesign-by-reorganisation, not a redesign-by-rewrite.** Every existing renderer (full / lite / context / trajectory / industry-band / about-data / decile-strip / band-chips / cohort-histogram / lite-delta / top-N) survives. The matrix row is a new variant — basically a compressed Lite row with a 24px sparkline and a category column.

If you disagree with the "matrix as center of gravity" framing — that's the load-bearing structural call to make first. Everything below assumes it.

---

## 3. Layer-by-layer content map

### LAYER 1 — Header

**Purpose:** centre identity + at-a-glance status. Spacing and hierarchy refinement only (per locked decisions).

| Slot | Content | Source | New? |
|---|---|---|---|
| Title | Service name | `services.service_name` | existing |
| Subtitle | Provider name | `services.provider_name` (or `provider_trade_name` from regulatory snapshot if set, fallback to `services.provider_name`) | existing + DEC-83 enrich |
| Operator-group chip | "Goodstart Early Learning" / "Guardian Early Learning" / etc. — only when `services.large_provider_id` IS NOT NULL | `large_provider.name` | **NEW (DEC-83)** |
| Identity row | SAN, suburb, state, postcode, ARIA+ remoteness | `services.*` | existing |
| Subtype tag | LDC / OSHC / FDC / Preschool | `services.service_type` | existing |
| Hours summary | "Mon–Fri 7:00am–6:00pm" or "Closed Mon" — single line, derived from latest snapshot's 14 hour cols | `service_regulatory_snapshot.hours_*` | **NEW (DEC-83)** |
| Contact strip | website (link) / phone / email — small muted line below identity row | `service_regulatory_snapshot.website_url / phone / email` | **NEW (DEC-83)** |

**No metrics, no charts, no flags here.** All status communication moves to Layer 2.

### LAYER 2 — Executive interpretation

**Purpose:** one headline + 5 signals + 0-2 flags. Reads like the analyst's first view.

**Headline structure (1 line, generated):**
- Pattern: `[supply band] · [demand band] · [demographic flavour] · [quality posture]`
- Example: "Saturated supply / strong demand / late-fertility urban catchment / Meeting NQS"
- Generated rule-based from band keys; not free-form prose

**5 signal tiles (small cards in a row, 1-line summary each):**

| # | Signal | Content | Driver |
|---|---|---|---|
| 1 | Demand | Adjusted demand band + decile + delta short ("Decile 8, ↑ since 2019") | `sa2_adjusted_demand` |
| 2 | Supply | Supply ratio band + decile ("Saturated, decile 9") | `sa2_supply_ratio` |
| 3 | Workforce | JSA IVI childcare-worker direction + shortage level ("Shortage tightening, IVI ↑12%") OR pending wire-up note | `jsa_ivi_4211_child_carer` (deferred today) |
| 4 | Quality | NQS overall current + trajectory arrow ("Meeting NQS, prev Working Towards") | `service_regulatory_snapshot.nqs_overall_rating` + `nqs_history` |
| 5 | Community | Demographic flavour ("High NES + culturally diverse" / "Anglo middle-income family belt") — pre-computed rule-based | derived from NES + ATSI + COB top-N + median income |

**Flag bar (0-2 flags, only when triggered):**

| Flag | Trigger | Severity |
|---|---|---|
| 🔴 CCS revoked by EA | `service_regulatory_snapshot.ccs_revoked_by_ea = 1` | RED — credit-direct |
| 🔴 Closed | `is_closed = 1` OR `temporarily_closed = 1` | RED — operational |
| 🟠 Active condition | EXISTS `service_condition` row with `still_active = 1` | AMBER — quality |
| 🟠 Sub-Meeting NQS | `nqs_overall_rating IN ('Working Towards NQS', 'Significant Improvement Required', 'Provisional')` | AMBER — quality |
| 🟠 Recent enforcement | `regulatory_events.action_date` within last 24 months | AMBER — quality |
| ⓘ No vacancies published | latest `service_vacancy` rows all `no_vacancies_published` | INFORMATIONAL — demand-side |

If more than 2 flags trigger, surface the 2 highest severity; rest spill into Layer 5 matrix flags column. **This avoids flag soup.**

**Interaction:** Each signal tile + each flag is clickable → opens the relevant Layer 5 matrix section pre-scrolled. Each links to the underlying Layer 6 detail drawer entry for "what does this mean / how is it computed".

### LAYER 3 — Primary historical trends

**Purpose:** the 7 charts an institutional reader needs in 2 minutes. Visually prominent but more compact than v1 cards (target chart height ~180px vs v1's ~280px, with histogram below at ~80px vs v1's ~140px).

| # | Chart | Cadence | Source | Layout |
|---|---|---|---|---|
| 1 | Supply ratio | quarterly per subtype | sa2_history.json | full-width, perspective toggle ready |
| 2 | Demand vs supply (parallel framing) | quarterly | sa2_history.json | full-width |
| 3 | Adjusted demand | quarterly | sa2_history.json | half-width pair with #4 |
| 4 | Children-per-place | quarterly | sa2_history.json | half-width pair with #3 |
| 5 | Under-5 population + births overlay | annual ABS ERP + births | abs_sa2_erp_annual + abs_sa2_births_annual | full-width, dual-line |
| 6 | Female LFP + unemployment overlay | mixed (3pt Census LFP + quarterly SALM unemployment) | mixed | full-width, dual-axis |
| 7 | Daily-rate (full_day × 36m-preschool) with peer-cohort overlay | annual snapshots from monthly raw fees | service_fee aggregated to year-medians | **NEW (DEC-83)** full-width, peer-cohort band shading |

**Notes:**
- #7 is the v2 headline new chart. Headline pair is **full_day × 36m-preschool** because it's the most-asked institutional question (prep-year-equivalent fee comp). Other (age × session) pairs surface in Layer 5 matrix with mini-sparklines + Layer 6 detail drawer with full per-pair history. Patrick to ratify the "headline pair" choice (D-7).
- #6 dual-axis is novel; alternative is two separate charts. Recommend dual-axis (saves vertical space, both metrics share the "pressure on parents to work and earn" story).
- **Workforce supply context (v1's card #5, all-deferred today)** does not get a chart slot in Layer 3 V1 — when JSA IVI wires up, it absorbs into chart #6 as a third overlay (or earns its own slot if Patrick prefers). For now, JSA IVI ties become a Layer 5 matrix row stub.
- **NQS overall trajectory** does not get a Layer 3 chart slot — it's a short pill ladder (Provisional → Working Towards → Meeting → Exceeding) that lives in Layer 2 Quality signal + Layer 5 matrix. Trajectory chart would be 2-3 datapoints; not chart-worthy.

**Window control:** existing trajectory range bar (1Y / 2Y / 5Y / 10Y / All) stays at top of Layer 3. Same `_setTrajectoryRange` mechanic.

**Histogram redesign:** every primary chart still gets its peer histogram below, but reduced from ~140px to ~80px tall, with decile strip + band chips inline rather than stacked. Saves ~60px per chart × 7 charts = ~420px vertical reclaim.

### LAYER 4 — Secondary historical trends

**Purpose:** useful context, not immediate. Single accordion section, default-collapsed. Open-by-default if Patrick wants per-user-pref toggle (V2).

| Group | Charts | Cadence | Source |
|---|---|---|---|
| Population context | Total population, parent-cohort 25-44, partnered 25-44 | annual / 3pt | abs_sa2_erp_annual + Census TSP |
| Income context | Median employee income, median total income, median household income | annual / 3pt | abs_sa2_socioeconomic_annual + Census |
| Workforce context | Total LFP, male LFP, JSA vacancy rate (when wired) | 3pt / quarterly | Census + JSA |
| Demographic trend | NES historical, overseas-born trend, ATSI trend, single-parent trend, women-25-34 + women-35-44 with-child cohorts | 3pt Census | abs_sa2_education_employment_annual |
| Education infrastructure | School count + total enrolment + govt share (currently the 3 V1 ACARA Lite rows) | 18yr annual | abs_sa2_education_employment_annual |

5 banked ACARA sector breakdowns (govt / catholic / independent share by count and by enrolment) live in Layer 5 matrix as standard rows; no Layer 4 chart slot.

**Layout:** when Layer 4 is expanded, render charts at half-width pairs in a 2-column grid (smaller than Layer 3). Each chart 120-150px tall. Histogram per chart is a tiny inline 30px strip with decile dot.

### LAYER 5 — Institutional signal matrix

**Purpose:** every metric in tabular quick-scan form. The center of gravity.

**Row structure (each row a horizontal band):**

| Column | Width | Content |
|---|---|---|
| Category tag | 80px | Color-coded chip: Demand / Supply / Pricing / Quality / Workforce / Community / Education / Operator / Operations |
| Metric name | flex | Display name + small OBS/DER/COM badge cluster |
| Current value | 100px | Raw value + unit + period stamp |
| Sparkline | 120px | Tiny inline sparkline (24px tall, last N points, no axes); silent absence if <2 points |
| Peer cohort | 80px | Decile strip (1-10 mini bar) + cohort_n in superscript |
| Signal | 120px | Band label (low/mid/high/saturated/etc.) — same band-chip color logic as v1 |
| Commentary | flex | One-line analyst summary (intent_copy short form, current registry) |
| Drawer trigger | 32px | "›" icon — click opens Layer 6 detail drawer scrolled to this metric |

**Categories in display order (~52 rows total V1, ~9 of them V1.5-pending stubs):**

#### Demand (3)
- sa2_adjusted_demand · sa2_demand_supply · sa2_demand_share_state

#### Supply (4)
- sa2_supply_ratio · sa2_child_to_place · supply ratio per subtype (V1.5 pending A5) · service_vacancy posture (NEW DEC-83)

#### Pricing & Fees (NEW — 5 rows V1)
- Daily-rate full_day × 36m-preschool (median + decile vs catchment) — **NEW DEC-83**
- Daily-rate full_day × 0-12m (median + decile vs catchment) — **NEW DEC-83**
- Daily-rate full_day × 13-24m (median + decile vs catchment) — **NEW DEC-83**
- Daily-rate full_day × 25-35m (median + decile vs catchment) — **NEW DEC-83**
- Daily-rate full_day × school-age (where applicable; OSHC fee bands for OSHC services) — **NEW DEC-83**

(Half-day / hourly / before/after school rows live in Layer 6 drawer detail — too sparse for matrix without bloating to 25+ rows in this section. D-8 to ratify.)

#### Quality (6)
- NQS overall rating + prev (pill ladder, no decile) — **NEW DEC-83 enrich**
- Active conditions count + link to detail (where >0) — **NEW DEC-83**
- Recent enforcement events count (24mo window) + link to detail — **NEW DEC-83**
- CCS revoked by EA flag (boolean row, only renders if 1) — **NEW DEC-83**
- NQS area breakdown (7 areas — only if `nqs_history` populates these; `service_regulatory_snapshot` cols dropped per DEC-83 amendment) — **NEW DEC-83 partial**
- Last regulatory visit date — **NEW DEC-83**

#### Workforce (4)
- jsa_ivi_4211_child_carer (deferred wire-up; row stub) — pending V1.5 A7
- jsa_ivi_2411_ect (deferred wire-up; row stub) — pending V1.5 A7
- ecec_award_rates (national fact row) — pending V1.5 A7
- three_day_guarantee (national fact row, Jan 2026) — pending V1.5 A7

#### Community (10)
- sa2_nes_share + top-N languages context line
- sa2_atsi_share
- sa2_overseas_born_share + top-N COB context line
- sa2_single_parent_family_share
- sa2_parent_cohort_25_44_share
- sa2_partnered_25_44_share
- sa2_women_35_44_with_child_share
- sa2_women_25_34_with_child_share
- sa2_median_household_income (also appears under Pricing+Workforce affordability lens? recommend single placement here in Community to avoid duplicates)
- sa2_total_population

#### Education (8)
- sa2_school_count_total
- sa2_school_enrolment_total
- sa2_school_enrolment_govt_share
- sa2_school_count_govt (banked from A4)
- sa2_school_count_catholic (banked)
- sa2_school_count_independent (banked)
- sa2_school_enrolment_catholic_share (banked)
- sa2_school_enrolment_independent_share (banked)

#### Operator / Group identity (NEW — 2 rows)
- Large-provider chain affiliation (with provider count + service count rollup) — **NEW DEC-83**
- Provider state: status + approval date + provider-level CCS-revoked — **NEW DEC-83**

#### Operations (NEW — 4 rows)
- Operating hours summary (per-day open/close) — **NEW DEC-83**
- Service status: open / temporarily closed / closed — **NEW DEC-83**
- CCS data received flag — **NEW DEC-83**
- Vacancy posture by age band (collapsed; click expands inline) — **NEW DEC-83**

#### Population (4 — same charts as Layer 3 + secondary Layer 4 but matrix row presence for completeness)
- sa2_under5_count
- sa2_births_count
- sa2_under5_growth_5y (deferred)
- sa2_total_population (also in Community; recommend single placement here, remove from Community)

#### Labour Market (4)
- sa2_unemployment_rate
- sa2_median_employee_income
- sa2_median_total_income
- sa2_lfp_persons / sa2_lfp_females / sa2_lfp_males (3 rows — keep separate per DEC-76 framing)

**Sorting:** within category, by descending signal strength is V2 (measurement-tools class). V1 is fixed display order matching POSITION_CARD_ORDER + new entries appended per category.

**Filter bar (top of matrix):** chips for category quick-jump (no full filter logic V1; just scroll-to-section). V2 adds search + filter-by-decile.

### LAYER 6 — Detail side drawer

**Purpose:** all the methodological depth that v1 carried inline (about_data panels, DER/COM tooltip detail, COM band copy, calibration rule_text, top-N detail, full enforcement-event detail, full condition text). Slide-in from the right edge.

**Trigger:** click on any tile/row drawer icon `›` in Layers 2-5. URL fragment `#metric-{key}` for shareable deep links + browser-back closes drawer.

**Drawer content per metric (template):**

```
[Metric display name]
[Category chip]

▌Current value
   [raw value · period · OBS badge · cohort_n]

▌Why it matters
   [intent_copy — full text, current registry]

▌How it's computed
   [about_data — full text, current registry]
   Formula: [DER detail]
   Source: [DER source link]

▌Peer cohort
   [cohort_def + cohort histogram full-size]
   Decile strip + band chips
   [Industry band rule_text if present]
   [Calibration rule_text if uses_calibration]

▌Trajectory
   [full chart — same as Layer 3/4 if also charted; else inline if Layer 5 only]
   [event overlays for catchment metrics]

▌Commentary
   [COM band copy for current band]

▌V1.5 / V2 banked
   [if applicable: "Subtype-correct denominators arrive in V1.5 A5"]
```

**Special drawer types:**

- **Daily-rate drawer:** full per-(age × session) fee history table; peer-cohort comparison panel; fee_type classification breakdown; inclusions text where present.
- **Conditions drawer:** full text of every condition (service + provider levels); first/last observed dates; level discriminator; click-through to provider-level conditions list.
- **Enforcement events drawer:** full event log (action_id, action_date, action_type) with chronological view.
- **Operator-group drawer:** chain name + slug; full list of provider entities in chain with names and approval numbers; service count per provider.
- **NQS drawer:** overall rating ladder (Provisional → WT → Meeting → Exceeding) with current + prev positions; 7-area breakdown if available; NQS history full sequence from `nqs_history`; last regulatory visit context.
- **Top-N (COB / language) drawer:** full top-10 lists with shares; methodological note on derivation.
- **Vacancy drawer:** age-band breakdown of latest snapshot; longitudinal sparkline of has-vacancy weeks vs no-vacancy weeks; methodological note on what "no_vacancies_published" means (sentinel state, not a guaranteed full state).

---

## 4. Decision points (D-1 through D-12)

Per session-density preference: all decisions surfaced together with my recommendation; ratify as a batch.

### D-1 — Page architecture: cards-or-matrix

**Q:** Does v2 keep the v1 cards visible above the Layer 5 matrix, or is the matrix the page's primary scan surface with cards dissolved?

**Recommendation: cards dissolve.** Layer 3 primary trends + Layer 5 matrix replace the v1 card stack. Each metric appears once: in matrix Layer 5; if also charted, in Layer 3 primary or Layer 4 secondary. Layer 1 + Layer 2 are above this. Total page becomes 4 conceptual zones, not 5+ cards.

This is the load-bearing structural call. If Patrick wants cards retained, every layer below needs re-thinking.

### D-2 — Layer 2 signal count: 4 or 5

**Q:** Patrick's notes say "4-5 key signals." Lock to 5? Or compress to 4 (Demand / Supply / Quality + 1 of Workforce/Community)?

**Recommendation: 5.** Demand + Supply + Workforce + Quality + Community is the institutional decision frame. Four loses Community framing which is most of the V1.5 demographic ingest work. Workforce can default to "pending wire-up" stub today; tile reserves the slot.

### D-3 — Layer 2 flag triggers + max count

**Q:** Lock the flag trigger rules (table in §3 Layer 2) and max-2-display-others-spill-to-matrix?

**Recommendation: ratify table as-stated, max 2 visible flags, others go to a "+N more" pill that opens Layer 5 matrix Quality/Operations sections.** Severity hierarchy: RED CCS-revoked / closed > AMBER active condition / sub-Meeting NQS / recent enforcement > INFORMATIONAL no-vacancies. Operator-group affiliation is **not** a flag — it's a Layer 1 chip.

### D-4 — Layer 3 chart count and headline pair for daily-rate

**Q:** 7 primary charts is dense. Cut to 5? And for the daily-rate chart, the headline (age × session) pair is full_day × 36m-preschool — confirm or re-pick?

**Recommendation: keep 7 charts. Headline daily-rate pair = full_day × 36m-preschool.**

Reasoning for 7: v1 currently shows 4-5 catchment Full charts + Population charts + Labour Market charts above the fold; consolidating to 7 with redesigned-shorter histograms is a net density improvement. Cutting to 5 forces decisions like "drop unemployment overlay" which loses workforce context.

Reasoning for 36m-preschool full_day: prep-year-equivalent fee is the most-cited institutional comp; full_day is the dominant session type by volume (4,668/8,220 = 57% of pilot fees); 36m-preschool is the highest age band before school. If Patrick prefers 0-12m (the most expensive end), happy to swap — content map identical, just chart-1-of-1 metric key changes.

### D-5 — Workforce supply card placement in v2

**Q:** v1's Workforce Supply Context card has 4 deferred rows. In v2: keep as standalone card, dissolve into Layer 5 matrix Workforce category, or split (JSA IVI → Layer 3 chart 6 overlay; ECEC Award + 3-Day-Guarantee → Layer 5 fact rows)?

**Recommendation: dissolve.** JSA IVI rows become Layer 5 Workforce matrix rows + (when wired) Layer 3 chart 6 third overlay. ECEC Award + 3-Day-Guarantee become Layer 5 Workforce fact rows (matrix-format-tolerable as "n/a sparkline, value = current rate, period = 'as at Jan 2026'"). The standalone card pattern goes away; DEC-76's intent (workforce supply context block) survives via Layer 2 Workforce signal + Layer 5 category.

### D-6 — Top-N (COB + language) inline or drawer-only

**Q:** Currently top-3 country-of-birth and top-3 language-at-home render as inline context lines below the relevant Demographic Mix Lite rows. In v2: keep inline in Layer 5 matrix (would consume an extra column or stack vertically), or move to Layer 6 drawer only with a "Top 3: ..." preview in the matrix Commentary column?

**Recommendation: drawer-only with preview text in Commentary column.** Matrix is for quick-scan; top-N detail is drawer-tier. Preview text "Top: Australian, Indian, Chinese" in Commentary column gives 80% of inline value at 0% extra column width. Full top-3 (with shares) lives in drawer.

### D-7 — Provincial decision: layer-6 drawer interaction model

**Q:** Drawer activation: click anywhere on a tile/row, click only on `›` icon, or hover-preview-click-to-pin?

**Recommendation: click anywhere on row OR `›` icon.** Hover-preview adds touch-screen complications (Patrick uses tablet for review per DEC-32 visual-design heritage). ESC closes; URL fragment shareable. No persistent multi-drawer (only one drawer open at a time; opening a second replaces the first).

### D-8 — Daily-rate matrix row count: 5 or 25

**Q:** Layer 5 Pricing & Fees has 5 rows in the proposal (full_day per age band only). Alternative: render every (age × session) combination = up to 25 rows. Or every observed combination only.

**Recommendation: 5 rows in matrix (full_day per age band), full grid in drawer.** Half-day + hourly + before/after-school are sparse (2,176/8,220 fees = 26% across 4 session types) and the institutional headline question is full-day. Drawer's daily-rate template covers the full grid for users who need it. This keeps Pricing density consistent with other categories.

OSHC services get a different headline pair (before_school + after_school × school-age). Recommend a service_type discriminator at render time — LDC sees full_day rows; OSHC sees before/after_school rows; FDC follows LDC convention; Preschool follows LDC convention with `36m-preschool` only.

### D-9 — Operator-group chip placement

**Q:** Operator-group chip position: Layer 1 header (visible always when applicable), Layer 2 community signal, Layer 5 matrix only, or all three?

**Recommendation: Layer 1 chip + Layer 5 matrix row + Layer 6 drawer with full chain detail. NOT in Layer 2 signals.** Layer 1 chip keeps the chain identity always-visible on chained services; Layer 2 signals stay focused on 5 institutional signals (chain affiliation isn't a "signal" per se, it's metadata). Drawer covers full provider list.

### D-10 — V1.5 pending ingest stub treatment

**Q:** V1.5 ingests not yet shipped (A5 subtype-correct, A6 SALM, B1 JSA banding, etc.) — render row stubs in Layer 5 matrix with "pending V1.5" text or hide entirely?

**Recommendation: render row stubs with status pill "Pending V1.5 A5/A6/B1".** Keeps the layer plan stable as ingests land; users see what's coming; honest absence (P-2) without forcing card-redesign on each ingest. Same pattern v1 uses for deferred workforce rows.

### D-11 — Histogram + decile rendering in Layer 5 matrix vs Layer 3 charts

**Q:** Layer 5 matrix rows have a 24px sparkline + decile strip + band chip inline. Layer 3 charts have ~80px histogram below chart + decile strip + band chips inline (down from v1's 140px stacked). Confirm the size cuts?

**Recommendation: confirm.** 80px histogram still legible; decile strip + band chips inline saves vertical at no readability cost (v1's stacked layout was a relic of original Lite-row design). Matrix sparkline 24px is the visual minimum that still reads as a trend; smaller becomes ornamental.

### D-12 — Excel export hooks shape

**Q:** Defer Excel export framework decision (it's separate DEC-candidate per ROADMAP.md) but lock the assumption that Layer 5 matrix structure exports cleanly: one row per metric with all 8 columns flattened?

**Recommendation: confirm.** Excel export reads the matrix payload structure unchanged. Drawer detail becomes additional sheets per-metric or a single "methodology" sheet keyed by metric. Doesn't bind us; just confirms the matrix shape is export-ready. Excel framework DEC ratifies the actual sheet structure later.

---

## 5. What this DEC-84 does NOT decide

- **The Excel export framework itself** — separate DEC-candidate per ROADMAP §2.4
- **Catchment page or Group page layout** — they cascade from Centre v2 patterns but get their own design pass
- **Child Safety + Competition page content** — full surfaces, separate scoping passes after Centre v2 ships
- **Brand identity rename pass (OI-NEW-6)** — independent low-risk pass
- **PropCo / Stream D content beyond reserving Layer 5 + Layer 6 slots** — Stream D has its own DEC-candidate
- **Stream E SA2 border exposure render** — slot reserved (Layer 5 Demand/Supply CONTEXT row), content TBD with Stream E ingest
- **Stream A workforce visa render** — slot reserved (Layer 5 Workforce category), content TBD with Stream A ingest
- **Measurement tools** (delta picker, decile-movement readout) — locked V2 of v2
- **National commercial-layer scale-up** — substrate work, not surface
- **Refresh cadence of DEC-83 data** — operational concern; v2 surfaces whatever's in `kintell.db` at render time

---

## 6. Effort estimate (post-ratification)

Assuming D-1 = matrix-as-center, D-2 = 5 signals, D-3 = ratified flags, D-4 = 7 charts, D-5 = workforce dissolves, D-6 = drawer-only top-N, D-7 = click-anywhere drawer, D-8 = 5 pricing rows + drawer grid, D-9 = Layer 1 chip + matrix + drawer, D-10 = stub pending pills, D-11 = confirmed sizes, D-12 = matrix-as-export-source:

| Step | Effort | Notes |
|---|---|---|
| DEC-84 mint + this design doc finalise | 0.1 sess | Append to canonical DECISIONS.md; ratify this doc |
| v1 stake: git tag `centre-v1-stake-YYYY-MM-DD` + bundle dir + ROLLBACK.md | 0.1 sess | Locked decision per project_centre_v2_redesign.md |
| `centre_page.py` v24 — payload schema `centre_payload_v7`: matrix structure assembly + flag computation + headline composition + drawer payload sub-tree | 1.0 sess | Significant new payload section; reuses existing _build_* helpers; adds _build_matrix, _build_executive, _build_drawer |
| `docs/centre_v2.html` (parallel renderer at `/centre_v2/{id}`) — Layer 1-6 render with all helpers reused; matrix + drawer + executive interpretation new patterns | 2.0 sess | New CSS for matrix layout + drawer slide-in; existing Lite/Full/Context renderers reused; new MatrixRow renderer; new DrawerPanel renderer |
| Verification capture (4 verifying SA2s × 2-3 service archetypes — large-provider chain, independent operator, OSHC, sub-Meeting NQS, CCS-revoked if any in pilot) | 0.3 sess | Static-HTML capture pattern (precedent: docs/a10_c8_review.html) |
| Smoke test + smoke-test docs in `docs/` | 0.2 sess | Visual review of all 6 layers across archetypes |
| Cut-over: `/centres/{id}` → centre v2 renderer | 0.1 sess | Patrick ratifies cut-over after smoke test |
| End-of-session monolith STD-35 + commit | 0.1 sess | |
| **TOTAL** | **~3.9 sess** | (vs locked memo estimate ~3-5 sess for build; this lands at lower-middle of band) |

Plus this design pass session itself (~0.7 sess so far + ratification + DEC-84 mint = ~1.0-1.2 sess for design pass).

**Grand total Centre v2 from this point: ~5 sess.** Locked memo estimate was 6-10 sess to v2 ship; this design pass + build comes in below that band, suggesting headroom for the v1 stake + capture polish + buffer.

---

## 7. Risk register

| Risk | Likelihood | Mitigation |
|---|---|---|
| Matrix density blowback — institutional users find 52 rows overwhelming | Medium | Layer 4 accordion + Layer 2 signal tiles handle the 30-second/2-minute view; matrix is the 5-10-minute view by design. Default-collapse Layer 4 reduces above-the-fold load |
| Drawer interaction confuses tablet users | Low-Medium | Click-anywhere row + ESC + back-button close + URL-fragment-shareable. Standard slide-in pattern. Smoke test on tablet pre-cut-over |
| Daily-rate peer-cohort overlay misleads (cohort definition fuzzy) | Medium | Drawer detail explicitly defines cohort (e.g. "median full_day 36m-preschool fee across 130 pilot LDC services in same SA2 + remoteness band, n=N"). Until national scale-up lands, peer cohort is small-n; render low-confidence pill (10≤n<20) or suppress (n<10) per existing v1 conventions |
| Flag noise on services with multiple AMBER triggers | Medium | Max 2 displayed + "+N more" spillover pill. Severity hierarchy locked. If still noisy in practice, V2 adjusts thresholds — not a v2-blocking issue |
| Workforce signal tile shows "pending wire-up" indefinitely | Low | V1.5 A6 SALM extension + A7 SEEK ingest land workforce data. Acceptable to ship with deferred state; matches v1's current state |
| Layer 5 matrix renders poorly on narrow screens | Medium | Stack columns vertically below 1024px breakpoint; sparkline + decile strip become single mini-row below metric name. Mobile is V2 polish; V1 targets desktop institutional use |
| v1 stake recovery untested before v2 cut-over | Low | Stake-creation is just `git tag` + `cp` to bundle dir; recovery is `git checkout <tag> -- <files>`. Trivial; document in ROLLBACK.md but no need to test live |
| `service_regulatory_snapshot` 7-area NQS cols dropped per DEC-83 amendment, but `nqs_history` may not have area-level data populated | Medium | Layer 5 NQS area row renders silent absence (P-2) until area-level data lands. Check `nqs_history` schema before final layout; if empty, drop the row from V1 matrix and re-add when populated |

---

## 8. Open questions for Patrick (please ratify or object)

| ID | Question | My recommendation |
|---|---|---|
| D-1 | Page architecture: cards-or-matrix? | Cards dissolve; matrix is center of gravity |
| D-2 | Layer 2 signal count: 4 or 5? | 5 (Demand / Supply / Workforce / Quality / Community) |
| D-3 | Layer 2 flag triggers + max count? | Ratify §3 table; max 2 visible + spillover pill |
| D-4 | Layer 3 chart count + daily-rate headline pair? | 7 charts; full_day × 36m-preschool headline pair |
| D-5 | Workforce supply card placement? | Dissolve into Layer 5 matrix + Layer 3 chart 6 overlay |
| D-6 | Top-N COB/language inline or drawer? | Drawer-only with Commentary column preview |
| D-7 | Drawer interaction model? | Click anywhere on row + ESC close + URL fragment |
| D-8 | Daily-rate matrix row count? | 5 (full_day per age band, OSHC sees before/after_school instead) |
| D-9 | Operator-group chip placement? | Layer 1 chip + Layer 5 matrix row + Layer 6 drawer; NOT in Layer 2 |
| D-10 | V1.5 pending ingest stubs? | Render with "Pending V1.5" status pill |
| D-11 | Histogram + decile size cuts in Layers 3 + 5? | Confirm 80px chart histograms / 24px matrix sparklines |
| D-12 | Excel export shape lock-in? | Confirm matrix structure as primary export source |

Once D-1 through D-12 are closed, RATIFIED SUMMARY at top gets populated and DEC-84 mint follows the precedent of DEC-83 (canonical DECISIONS.md append + cross-references in PROJECT_STATUS.md / ROADMAP.md / OPEN_ITEMS.md / `project_centre_v2_redesign.md` memory entry).

---

## 9. Appendix — counting the placement of every existing piece

Validation table: every metric / panel / helper from v1 has a placement in v2.

| v1 piece | v2 layer + slot | Notes |
|---|---|---|
| Header (service name, provider, identity) | Layer 1 | + new operator-group chip + hours summary + contact strip |
| sa2_supply_ratio | L3 chart 1 + L5 Supply matrix row + L6 drawer | |
| sa2_demand_supply | L3 chart 2 + L5 Demand row + L6 drawer | |
| sa2_child_to_place | L3 chart 4 + L5 Supply row + L6 drawer | |
| sa2_adjusted_demand | L3 chart 3 + L5 Demand row + L6 drawer + L2 Demand signal | |
| sa2_demand_share_state | L5 Demand row + L6 drawer | CONTEXT-only; no chart |
| sa2_nes_share | L4 demographic-trend chart + L5 Community row + L6 drawer | top-N languages preview in Commentary |
| sa2_atsi_share | L4 demographic-trend chart + L5 Community row + L6 drawer | |
| sa2_overseas_born_share | L4 demographic-trend chart + L5 Community row + L6 drawer | top-N COB preview in Commentary |
| sa2_single_parent_family_share | L4 demographic-trend chart + L5 Community row + L6 drawer | |
| sa2_parent_cohort_25_44_share | L4 population-context chart + L5 Community row + L6 drawer | |
| sa2_partnered_25_44_share | L4 population-context chart + L5 Community row + L6 drawer | |
| sa2_women_35_44_with_child_share | L4 demographic-trend chart + L5 Community row + L6 drawer | |
| sa2_women_25_34_with_child_share | L4 demographic-trend chart + L5 Community row + L6 drawer | |
| sa2_under5_count | L3 chart 5 + L5 Population row + L6 drawer | |
| sa2_total_population | L4 population-context chart + L5 Population row + L6 drawer | (deduped from Community) |
| sa2_births_count | L3 chart 5 overlay + L5 Population row + L6 drawer | |
| sa2_under5_growth_5y | L5 Population row stub (deferred) + L6 drawer | |
| sa2_unemployment_rate | L3 chart 6 + L5 Labour Market row + L6 drawer | |
| sa2_median_employee_income | L4 income-context chart + L5 Labour Market row + L6 drawer | |
| sa2_median_household_income | L4 income-context chart + L5 Community row + L6 drawer | |
| sa2_median_total_income | L4 income-context chart + L5 Labour Market row + L6 drawer | |
| sa2_lfp_persons | L4 workforce-context chart + L5 Labour Market row + L6 drawer | |
| sa2_lfp_females | L3 chart 6 overlay + L5 Labour Market row + L6 drawer + L2 Workforce signal | |
| sa2_lfp_males | L4 workforce-context chart + L5 Labour Market row + L6 drawer | |
| jsa_vacancy_rate | L5 Labour Market row stub (pending V1.5 B1) + L6 drawer | |
| sa2_school_count_total | L4 education-infra chart + L5 Education row + L6 drawer | |
| sa2_school_enrolment_total | L4 education-infra chart + L5 Education row + L6 drawer | |
| sa2_school_enrolment_govt_share | L4 education-infra chart + L5 Education row + L6 drawer | |
| 5 banked ACARA sector mix | L5 Education rows (5 entries) + L6 drawer | |
| jsa_ivi_4211_child_carer | L5 Workforce row stub + L3 chart 6 overlay (when wired) + L6 drawer + L2 Workforce signal | |
| jsa_ivi_2411_ect | L5 Workforce row stub + L3 chart 6 overlay (when wired) + L6 drawer | |
| ecec_award_rates | L5 Workforce fact row + L6 drawer | |
| three_day_guarantee | L5 Workforce fact row + L6 drawer | |
| Renderers: Full / Lite / Context | reused in L3 / L4 / L5 unchanged | |
| `_renderTrajectory` | reused in L3 / L4 charts | |
| `_renderAboutData` | moves into L6 drawer | inline panel pattern dissolves |
| `_renderIntentCopy` | reused in L5 matrix Commentary col | full text in L6 drawer |
| `_renderIndustryBand` | reused in L5 Signal column | |
| `_renderTopNContext` | moves into L6 drawer | preview in L5 Commentary column |
| `_renderDecileStrip` | reused in L3 + L5 | |
| `_renderBandChips` | reused in L3 + L5 | |
| `_renderCohortHistogram` | reused in L3 (smaller) + L6 drawer (full size) | |
| `_renderLiteDelta` | reused in L5 matrix + L6 drawer | |
| `_renderTrajectoryRangeBar` | reused at top of L3 | |
| `_renderWfsRangeBar` | dissolves with workforce card | functionality absorbs into L3 chart 6 range |
| Catchment Position card | dissolves | rows distribute to L2/L3/L4/L5 by category |
| Population card | dissolves | rows distribute to L3/L4/L5 |
| Education Infrastructure card | dissolves | rows distribute to L4/L5 |
| Labour Market card | dissolves | rows distribute to L3/L4/L5 |
| Workforce Supply Context card | dissolves | rows distribute to L3 (when wired) + L5 |

**Every existing piece has a v2 placement.** No orphans. New DEC-83 pieces (operator-group / daily-rate / regulatory snapshot / conditions / vacancies / enforcement events / hours / contact / website) all land in Layer 1, Layer 2 flags/signals, Layer 5 categories, or Layer 6 drawer types per §3.

---

*End of design doc. Patrick: please ratify D-1 to D-12 (or object to specific items) so we can mint DEC-84 and proceed to v1-stake + v2 build sequence.*

---

## Post-v0.1 review queue (2026-05-12)

*Items surfaced during Patrick's first visual review of centre_v2.html v0.1 + v0.2 (carryover block landed). Banked here pending the complete sheet (Layer 3 + Layer 4 charts) which Patrick wants in BEFORE further structural changes — "put layer three and layer four in, and then assess from there." Order below is the queued sequence; items 1-2 are this turn's work, 3-9 land in subsequent turns.*

### Doing this turn (Layer 3 + Layer 4 charts)
1. **Layer 3 primary historical trends** — 7 charts per DEC-84 #4 with full v1 chart infrastructure ported (Chart.js, trajectory range bar, cohort histograms, centre-events overlay on catchment metrics). Chart list: supply ratio quarterly / demand vs supply quarterly / adjusted demand / children-per-place / under-5 + births overlay / female LFP + unemployment dual-axis / daily-rate full_day × 36m-preschool annual (NEW DEC-83 trajectory backend extension required).
2. **Layer 4 secondary historical trends accordion** — 5 chart groups (population context / income context / workforce context / demographic trend / education infrastructure), default-collapsed, half-width 2-column grid pairs when expanded.

### Banked for next turn (top-of-page restructure)
3. **Layer 1 = rich identity block** — restructure header to carry: service name (large) + parent-group deep link (subtle, top-right; centre→group→industry hierarchical navigation principle) + fact chip strip (approved_places, daily rate single-figure, SEIFA decile, remoteness, SA2 name, kinder summary, subtype) + hours + contact. Absorbs the v1 Catchment-meta card content currently sitting in carryover block.
4. **Layer 2 (executive) shrunk to compact right-side panel** inside the Layer 1 block — no longer a full-width prominent section. 2-column internal grid: identity left, intelligence right.
5. **Matrix category reorder per analytical priority** — demand → supply → pricing → population → community → labour market → education → workforce → quality → operator → operations. Replaces the current arbitrary order (population currently at bottom; per `feedback_analytical_panel_order.md` that's wrong because population is a load-bearing demand fundamental).
6. **Carryover card reorder** — analytical priority, not code-emission order.

### Banked for turn after that (interaction patterns + drawer enrichment)
7. **Pricing inline-collapse** — Layer 5 Pricing matrix row shows single average daily rate; click expands inline to per-(age × session) breakdowns. Hybrid with side drawer: drawer for methodology, inline collapse for "show me the breakdown that lives behind this number."
8. **Schools-in-catchment drawer enrichment** — when user clicks the Education matrix row, drawer should list the actual school names + sectors + enrolments (currently just shows methodology). Backend extension to `_build_drawer` for sa2_school_count_total drawer with school list query against the ACARA tables.

### Banked for V2 of v2 (peer-cohort context infrastructure)
9. **Daily rate + places peer-cohort range visualisation** — show where this centre sits on the SA2 distribution at a glance. Needs backend cohort SQL: aggregate medians + range bands across all services in the same SA2 + remoteness band. Currently small-n (130-pilot only); land in earnest when national commercial-layer scale-up runs.

### Added 2026-05-12 (post Layer 3 + Layer 4 review)
10. **Chart polish — restore v1's hover register** (this turn): external readout above each chart + crosshair vertical line at hovered point. v0.2 simplified to native Chart.js tooltips; Patrick: "should have nice arrows for exact measurements." Port `_kintellExternalReadout` + `_kintellCrosshair` plugins from v3.31.
11. **Centre events overlay** (this turn): vertical dashed lines on catchment trajectory charts (and daily-rate where applicable) marking quarters when new centres opened / closed. Payload `centre_events` already populated by `_layer3_position` for the 4 catchment metrics (`sa2_supply_ratio` / `sa2_child_to_place` / `sa2_demand_supply` / `sa2_adjusted_demand`). Port `_kintellEventAnnotation` plugin from v3.31.
12. **Sticky trend window selector** (this turn): trend window bar should remain accessible as user scrolls down through Layer 3 charts. CSS `position: sticky` + scroll padding.
13. **Per-chart decile explanation caption** (this turn): small text below each Layer 3 chart explaining what the decile / cohort means in plain language ("Decile 5: this SA2 sits in the middle of the cohort of [definition]"). Replaces the bare D5 · n=347 stamp with a one-line explainer.
14. **Layer 4 → inline-row-click chart pattern (NEXT TURN)** — Patrick's structural reframing: remove the Layer 4 accordion entirely; instead, clicking a matrix row inline-expands a panel below the row containing the chart for that metric (plus optionally the row's drawer-content). Side drawer remains for "deep methodology" but the chart goes inline. Pattern extends to Pricing inline-collapse too (queue item 7). This consolidates: Layer 4 accordion goes away; matrix becomes the canonical home for "click to drill into history"; primary trends (Layer 3) remain at top for the 7 highest-priority decision-critical charts.
15. **Customisable matrix view (banked, V2 of v2)** — operator can select/deselect individual measures to show/hide in the matrix. Persistence via sessionStorage initially; per-user preference state lands later when multi-tenancy ships. Patrick: "is this a complex build?" — moderate. State management + persistence pattern; not blocking V1.
16. **"More info available" right-column indicator** — Layer 5 matrix right column renders a richer drawer-trigger icon when underlying data opportunity exists (top countries of birth, languages at home, school name list, full per-(age × session) fee grid, conditions list, enforcement event log). Distinguish from "generic methodology drawer" with a different icon or chip. Pairs with the schools drawer enrichment (queue item 8).
17. **"Click for more info" caption at top of matrix** — explanatory text above Layer 5 explaining that clicking the right-hand button on any row reveals deeper information.

### Other items raised
- "Institutional signal matrix" terminology rename pending (alternative names TBD; raised before v0.2 review)
- Visual softness pass (rounded panels, prose interleaved) — partial via carryover block in v0.2; full pass after Layer 3 + 4 land and the page rhythm is judgable

*This queue is the working list for centre_v2.html iteration. Items move from "queued" → "doing" → "done"; Patrick can re-order or de-queue at any time.*

---

## Comprehensive outstanding queue (refreshed 2026-05-13 — post-Turns-1-3 doc-refresh)

*Patrick: "I want you to look back in our chat here and see where there are any ideas that I put forward that we agreed to do that we got sidetracked on, to make sure they're in the list. That list should be confirmed back to me at the start of the next session." Section reset every session start. The 2026-05-12 EOD list was the baseline; Turns 1-3 (the first three visual-iteration turns post-build-kick-off) closed five items and added a sixteen-sub-decision DEC-84 amendment block in canonical DECISIONS.md. This refreshed list carries the eleven remaining items forward verbatim so banked context survives the session boundary.*

### ✅ Done by end of Turn 3 (2026-05-13 doc refresh closing out)

**From 2026-05-12 (DEC-84 design pass + v0.1-v0.5 build):**
- DEC-84 minted; v1 stake bundle (`recon/v1_final_stake_2026-05-12/` + git tag `centre-v1-stake-2026-05-12 212b597`)
- `centre_page.py` v24 + payload schema v7 (4 new top-level keys: `dec83` / `executive` / `matrix` / `drawer`); 4 new builders + 9 helpers
- `docs/centre_v2.html` v0.1 → v0.5 with: Layer 1 header / Layer 2 executive / Layer 3 primary trends (7 charts) / Layer 4 secondary trends accordion (17 charts) / Layer 5 institutional matrix (54 rows × 11 categories) / Layer 6 side-drawer
- v1-style chart polish: external readout + crosshair + centre-events overlay + sticky trend window selector
- Carryover block: NQS / Places+Kinder / Catchment-meta / Tenure / QA / Commentary
- Methodology legend bar (OBS / DER / COM explainer at top)
- Identity tiles row in Layer 1 (places / subtype / SEIFA / remoteness)
- Tag chips strip (acecqa SAN / abr legal name / google search lookup)
- Operator deep-link + ownership badge (Government / Private (for profit) / NFP) + brand badge + entity attribution
- Layer 3 full register (cohort histogram + caption + decile strip + band chips with descriptive text + INDUSTRY badge with note + intent_copy + ABOUT THIS MEASURE + source line + DER+COM badges)
- Cohort histogram presentation matches v1 exactly (full-width proportional bars + italic centred caption + small cohort meta)
- ABOUT panel lighter (left-border accent only, no full background fill, 11.5px font)
- OBS/DER/COM hover with richer methodology content (cohort, source, calibration, formula)
- Under-5+births dual-line chart with full register + combined source attribution
- Female LFP+unemployment dual-axis chart with full register + combined source attribution
- Daily-rate chart with full register + intent + ABOUT + source ("Starting Blocks daily fee schedule (DEC-83 Commercial Layer V1; service_fee table; weekly refresh cadence)")
- Combined trend label "−X% since Y · +N places · +M centres" using centre_events overlay
- Layer 4 secondary charts: trend label + decile snapshot + source line per chart

**Closed during Turns 1-3 (sixteen sub-decisions ratified; captured in DECISIONS.md DEC-84 AMENDMENT 2026-05-13):**
- ✅ **#11 closed — Matrix terminology rename:** "Institutional signal matrix" → **Signal Matrix** (D-1 confirmed; user-facing copy only — internal `matrix` payload key unchanged)
- ✅ **#1 closed — Inline-row-click expand on Layer 5 matrix:** trajectory chart + per-metric local trend-window state via `_INLINE_RANGE_BY_METRIC`; drawer reserved for deep methodology + rich-content panels
- ✅ **#4 closed — Matrix category reorder per analytical priority:** Turn 1 rewrote display order to credit-analytical flow (demand → supply → pricing → population → community → labour market → education → workforce → quality → operator → operations)
- ✅ **#9 closed — Top-N inline context lines on demographic-mix rows:** preview text back inline in Commentary column (top-2 or top-3 with share %); full top-10 + methodology stays in drawer
- ✅ **#2 de-queued — Layer 4 accordion removal reversed:** accordion retained as an overview-by-chart-group surface, co-existing with #1 inline-row-click drill from matrix. Layer 4 also gains its own trend-window selector independent of Layer 3
- ✅ Sparkline column retired from Layer 5 matrix rows (D-11 partially reversed; chart-below 80px histograms preserved); reclaimed width reflowed into Commentary column (minmax 280px 5fr); `_truncate_sentence` widened 120 → 240 chars
- ✅ Value-in-commentary pattern (leading bold value+period in Commentary column)
- ✅ Centre-events overlay extended from 4 catchment metrics to under-5/births + population/cohort charts
- ✅ Edge-event visibility nudge (~6px inward) for first/last-quarter annotations
- ✅ Event-line annotation badge with type abbreviation (+1/−1) + quarter year above chart top axis
- ✅ DER badge colour-coding (OBS blue / DER purple / COM amber; was uniform grey)
- ✅ SEIFA descriptor word alongside decile in Layer 1 identity tile (D7-D8 "advantaged" etc.)
- ✅ Layer 2 Community signal enrichment via top-2 languages substrate (extends DEC-84 #2 composer)
- ✅ Quality category transitional note (italic caption — Starting Blocks pilot coverage only until national scale-up)
- ✅ Explicit SA2 fact chip in Layer 1 identity row
- ✅ Source-attribution hygiene sweep across all Layer 3 + Layer 4 + Layer 5 source lines

### 🔴 Outstanding queue (eleven items carried forward from 2026-05-12 EOD list)

*Five items closed by Turns 1-3 (#1, #2, #4, #9, #11). Item numbers preserved from the 2026-05-12 list so cross-references in DECISIONS / memory stay stable.*

**Bigger structural items (highest priority):**
- ~~#1 Inline-row-click expand on Layer 5 matrix~~ ✅ closed Turn 2-3
- ~~#2 Layer 4 accordion removal~~ ✅ de-queued via reversal Turn 2
3. **Layer 1 rich-identity restructure: Layer 2 executive shrunk to compact top-right sidebar inside Layer 1** — Patrick's earlier feedback: "the intelligence cell, which is the next one, you I think it should be smaller and more subtle. It should be up the top right next to the information about the Service Centre." Currently Layer 2 is full-width below Layer 1.
- ~~#4 Matrix category reorder per analytical priority~~ ✅ closed Turn 1
5. **Carryover card reorder** per analytical priority (similarly).

**Drawer / interaction enrichments:**
6. **Pricing inline-collapse** — Patrick: "the pricing and fees should just have the single average daily rate, and then you click on it and collapse those individual room rates open." Single avg daily rate row in matrix; click expands inline to per-(age × session) breakdown. Hybrid with side drawer for full grid. *Pattern overlaps with #1 inline-row-click expand now landed; revisit whether the Pricing single-row collapse rides the same handler or stays distinct.*
7. **Schools-in-catchment drawer enrichment** — Patrick: "Down in education, when you click Schools in catchment, it should say what the schools are, their names, when you click on the detail arrow." Backend: query ACARA tables for school list per SA2 + sector + enrolment.
8. **Right-column "rich-content" indicator** — Patrick: "in the signal matrix, in the furthest right-hand column, wherever there's an underlying data opportunity such as the country of birth or the language they speak, or if the schools can fit, or any other information, it can be gracefully dragged to the front. Then that layer should be available again at the top. It should explain that there may be further information and that it can be clicked by the furthest right-hand access button you've set up." Distinguish rich-content drawer trigger from generic methodology trigger via different icon / chip + add caption above matrix explaining the right-button.

**Layer 5 matrix detail:**
- ~~#9 Top-N inline context lines on matrix demographic rows~~ ✅ closed Turn 3
10. **Lite row "as at YYYY · static snapshot, no trajectory" stamps** — for matrix rows with non-trajectory data (Census 3-point series). v1 has this stamp; v2 currently doesn't.
- ~~#11 "Institutional signal matrix" terminology rename~~ ✅ closed Turn 1 ("Signal Matrix")

**Workforce specific:**
12. **Workforce separate window selector** (6M / 1Y / 2Y / 5Y / All) + scope stamps ("state-level (NSW) — no SA2 peer cohort" / "national — no SA2 peer cohort") — v1 has these per `renderWorkforceSupplyCard`. v2's matrix Workforce category currently uses page-level trend window only and doesn't carry scope stamps prominently. *Inline-row-click expand (#1 closed) now carries per-metric `_INLINE_RANGE_BY_METRIC` state; pattern likely reusable for the workforce sub-window.*

**Customisable view:**
13. **Customisable matrix view (operator selects/deselects measures)** — Patrick: "in the signal matrix, it would be excellent if the operator could select or deselect individual measures to disappear or show up in the matrix below, allowing them to customise their view. Is this a complex build?" Moderate complexity; sessionStorage persistence first, per-user state later. *Pairs with page-top show/hide selector (below) — same persistence pattern.*

**Banked V2 of v2 (longer-horizon):**
14. **Daily rate + places peer-cohort range visualisation** — Patrick: "that figure and the places... should be sitting on a range of its competitors. In other words, we can see where the daily rate sits on the scale or the range of daily rates within that SA2... Also, the size of the centre should do the same." Needs backend cohort SQL across SA2 + remoteness band; currently small-n (130-pilot only). Land in earnest after national commercial-layer scale-up runs.
15. **Centre → Group → Industry hierarchical navigation** — Patrick: "the link back to the group that it's a part of. Remember, it's going to be part of all architecture here of centres up to groups and groups up to industry." Group page (OI-NEW-17) when it ships uses the same v2 patterns; navigation already partial via Layer 1 operator deep-link to `operator.html?id=N`. Industry-level lens further out.
16. **Visual softness pass (full)** — partial via carryover block + Layer 3 register; further refinement after structural items #3-#5 settle and the page rhythm is judgable.

### Banked from previous session opener (newly captured 2026-05-13 — for confirmation)

These items were named in the next-session-opener handoff alongside the Turns 1-3 list; they are not yet on the numbered queue above. Patrick to ratify if they remain target or de-queue.

**Bundle B — top-of-page strategic (banked candidate):**
- Peer-cohort range viz on places + daily rate (overlaps with #14 longer-horizon item — Patrick to confirm whether Bundle B advances this earlier than originally banked)
- Tenure relocation (carryover block tenure card → ? — placement TBD; pairs with #5 carryover reorder)
- Layer 2 enrichments: ratings exposure / unemployment exposure / community detail
- Stream E shorter version: SA2 border exposure proxy

**Small polish bundle (banked candidate):**
- Hover-info / drawer enrichment for event lines (full centre names propagating from the centre_events badge readout)
- Cosmetic SA2 name cleanup (formatting / case)
- Ratio chart reference line
- Unemployment axis fix

**Closer-to-V1 timeline (queued behind):**
- N21 Room mix / age cohort (probe needed first)
- Schools-with-attached-OSHC (new ingest; pairs with OI-NEW-19 OSHC-school adjacency from DEC-82 consequences)
- User-customisable matrix view (queue #13 / Doc-#10 banked)
- Page-top show/hide selector (Doc-#10 banked; pairs with #13)

### How next session opens
Per Patrick's request: confirm the queue list above at session start, identify which 2-3 items to bundle, then proceed line-by-line in the same back-and-forth iteration mode that worked this session.

