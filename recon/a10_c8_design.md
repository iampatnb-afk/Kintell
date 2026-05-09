# A10 + C8 — Demographic Mix bundle: design doc

*Created 2026-05-09. Probe-first per DEC-65. NO CODE until Patrick ratifies decisions D-A1 through D-A4 below.*

## 1. Headline finding (correction to roadmap)

The roadmap (CENTRE_PAGE_V1_5_ROADMAP §A10, PROJECT_STATUS §What's next) names the three TSP tables as:

- T07 — Indigenous status (ATSI)
- T08 — Country of birth
- T19 — Family composition (single-parent households)

**Probe of `2021_TSP_SA2_for_AUS_short-header.zip` shows the mapping is wrong for two of three.** The actual TSP-table-number → subject mapping (extracted from column headers):

| TSP # | Actual subject | Confirms via columns |
|---|---|---|
| **T05** | Marital status | `C11_15_19_Mar_RegM_*` (Married Registered, age × sex × census year) |
| **T06** ✅ | **Indigenous status (ATSI)** | `C{yr}_{age}_Indig_{sex}` / `_NonInd_{sex}` / `_Indig_st_ns_{sex}` / `_Tot_{sex}` |
| **T07** ❌ | **Children-ever-born × age (fertility)** — *not ATSI* | `C{yr}_AP_{age}_NCB_{count}` (NCB = Number of Children Born) |
| **T08** ✅ | **Country of birth** | `{Country}_C{yr}_{sex}` for ~50 countries |
| **T14** ✅ | **Family composition (single-parent share)** | `C{yr}_SH_FH_CF_no_ch / _w_ch / _One_PFam / _oth_fa / _Tot` |
| **T19** ❌ | **Tenure type / landlord** — *not family composition* | `C{yr}_*_REA / _ST_HA / _Co_ho_pr / _Per_no_sa_ho / _Oth_land_typ / _LLT_NS` |

**Effective correction:** A10 reads **T06 (ATSI), T08 (country of birth), T14 (family composition)**. All three are in the same TSP zip already on disk. Same processing pattern as A2. Same per-SA2 SA2_CODE_2021 + C11/C16/C21 census-year suffixes. **No scope change.**

**Bonus:** T05 (marital status) and T07 (children-ever-born) are also in this zip — banked as Stream C (childbearing-age + marital depth) future inputs.

**Recommendation:** ratify the corrected mapping, update CENTRE_PAGE_V1_5_ROADMAP §A10 in the same commit as the design doc closure.

---

## 2. Scope summary

**A10 ingest** — 3 metrics into `abs_sa2_education_employment_annual` (long-format) plus 1 new top-N table for country of birth.

**B-pass banding** — 3 banding registry entries (or 2; see D-A2). Pattern matches `patch_b2_layer3_add_nes.py`.

**C8 render** — extend Catchment Position card with a "Demographic mix" sub-panel header above the existing NES row, plus 3 new Lite rows.

Total: ~1.0 sess as scoped in CENTRE_PAGE_V1_5_ROADMAP.

---

## 3. Precedents we are cloning (probe outputs)

### 3.1 Ingest: `layer4_4_step_a2_apply.py` (A2 v3, 2026-05-04)

Pattern:
1. `preflight()` — DB + zip + table presence checks.
2. `read_source()` — pandas reads two CSVs from zip; filter SA2_CODE_2021 = `^\d{9}$`; index per SA2.
3. `derive_*()` — compute percentage; clamp to [0, 100]; per DEC-59 clamp negatives to 0.
4. `sanity_checks()` — value range, national weighted total, year breakdown, 3 verification SA2s.
5. `pre_state(con)` — count existing rows for metric; max audit_id; full table rowcount.
6. Idempotency gate — if metric already has rows and `--replace` not set, exit 4.
7. `backup_db()` — `data/pre_layer4_4_step_a2_v3_<ts>.db` (STD-08).
8. `write_rows()` — INSERT into target table.
9. `write_audit_log()` — STD-11 / DEC-62 8-column INSERT (7 placeholders + `datetime('now')` for `occurred_at`).
10. `post_state()` — count, range, mean, verification SA2 spot-check.

The 3 verification SA2s (Bayswater Vic 211011251, Bondi Junction-Waverly NSW 118011341, Bentley-Wilson WA 506031124) carry through every metric.

### 3.2 Banding: `patch_b2_layer3_add_nes.py` (B2, 2026-05-04)

Patcher appends one entry to `METRICS = [...]` in `layer3_apply.py`:

```python
{
    "canonical": "sa2_nes_share",
    "source_table": "abs_sa2_education_employment_annual",
    "value_column": "value",
    "filter_clause": "metric_name = 'census_nes_share_pct'",
    "year_column": "year",
    "cohort_def": "state_x_remoteness",
},
```

Then `layer3_apply.py --apply` populates `layer3_sa2_metric_banding` (and the OI-35 workaround `layer3_x_catchment_metric_banding.py --apply` follows).

### 3.3 Render: `patch_c2_nes_centre_page.py` (C2, 2026-05-04)

Patcher extends three constants in `centre_page.py`:
- `LAYER3_METRIC_META` — `display`, `card`, `value_format`, `direction`, `row_weight`, `source`, `band_copy{low/mid/high}`.
- `LAYER3_METRIC_INTENT_COPY` — italic explainer.
- `LAYER3_METRIC_TRAJECTORY_SOURCE` — `table`, `value_col`, `period_col`, `filter_clause`, `kind`.

The existing C2 patcher already left a comment: *"Phase 2 (country-of-birth) will add a Demographic Mix sub-panel header above NES."* — confirming the C8 panel placement intent.

Plus `POSITION_CARD_ORDER["catchment_position"]` in `centre_page.py` and the matching `order` array inside `renderCatchmentPositionCard()` in `centre.html` both need extending (per OI-36 close).

### 3.4 Schema (target table, audit_log)

```sql
CREATE TABLE abs_sa2_education_employment_annual (
    sa2_code    TEXT    NOT NULL,
    year        INTEGER NOT NULL,
    metric_name TEXT    NOT NULL,
    value       REAL,
    PRIMARY KEY (sa2_code, year, metric_name)
);
```

Currently 23 distinct `metric_name` values, including `census_nes_share_pct` (7,272 rows across 3 census years × ~2,424 SA2s). NES verification SA2 `211011251` shows: 21.59 / 27.05 / 31.07 across 2011 / 2016 / 2021.

`audit_log`: 9 columns (audit_id PK + 8 user). A2 INSERT uses 7 placeholders + `datetime('now')` for occurred_at.

---

## 4. Decisions to ratify

### D-A1 — Metrics shipped, naming, and what enters Layer 3 banding

**Decision (proposed):** ship 3 single-percentage metrics into the existing long-format table, all banded:

| Metric | Source | Formula | Storage | Band cohort | Direction (calibration) |
|---|---|---|---|---|---|
| `sa2_atsi_share` (`census_atsi_share_pct`) | T06 | `Tot_Indig_P / Tot_Tot_P × 100` | percentage 0–100 | state_x_remoteness | neutral (context); calibration deferred |
| `sa2_overseas_born_share` (`census_overseas_born_share_pct`) | T08 | `(Tot_C{yr}_P − Australia_C{yr}_P) / Tot_C{yr}_P × 100` | percentage 0–100 | state_x_remoteness | neutral (context); calibration deferred |
| `sa2_single_parent_family_share` (`census_single_parent_family_share_pct`) | T14 | `Tot_FH_One_PFam / Tot_FH_Tot × 100` | percentage 0–100 | state_x_remoteness | neutral (context); calibration deferred |

**Why:** mirrors NES exactly (state×remoteness cohort, percentage 0–100, neutral framing per P-2 + DEC-12).

**Calibration deferral rationale:** STD-34 nudges should be tuned against banding distributions we haven't seen yet. Ship as context-only Lite rows; revisit calibration scoping after spotchecks land. Avoids prematurely tuning the calibration coefficients without seeing the band shape.

**Open sub-question (low cost):** is `Tot_Tot_P` (Indig + NonInd + NS) or `(Indig_P + NonInd_P)` (NS-excluded) the right ATSI denominator? **Lean Tot_Tot_P** — matches ABS published convention, treats NS as "not Indigenous" for share purposes, matches the household-share pattern of the other two metrics.

**T08 numerator caveat:** "Australia" column in T08 may be `Australia_C{yr}_P`. Need to confirm column header at ingest time. Fallback: derive overseas as `Tot − sum(Aus + Oth_Aus_terr if present + Lang_used_home_NS_at_birth?)`. Will harden in code.

### D-A2 — T08 country-of-birth top-N: separate table, context-only

**Decision (proposed):** in addition to `sa2_overseas_born_share`, ship a new table `abs_sa2_country_of_birth_top_n` with the per-SA2 top-3 countries (excluding Australia) for the **2021 census year only**. Display-only; no banding; no calibration influence.

```sql
CREATE TABLE abs_sa2_country_of_birth_top_n (
    sa2_code     TEXT    NOT NULL,
    census_year  INTEGER NOT NULL,
    rank         INTEGER NOT NULL,            -- 1, 2, 3
    country_name TEXT    NOT NULL,
    count        INTEGER,
    share_pct    REAL,
    PRIMARY KEY (sa2_code, census_year, rank)
);
```

**Why:** the existing long-format `(sa2_code, year, metric_name, value)` table can't hold a country label. Top-N is structurally a list, not a scalar. Trying to encode in the value column or fan out as `census_cob_top1_pct`, `census_cob_top1_country` (which can't be REAL) breaks the table contract. A small dedicated table is the cleanest fit and adds zero ambiguity for downstream readers.

**Render:** in C8 panel, top-3 renders as a one-line "Top countries of birth: India 12.4%, China 8.1%, UK 4.2%" beneath the `sa2_overseas_born_share` Lite row. No trajectory; latest census only. Updates next census.

**Top-N count:** default 3, configurable. 5 was in roadmap; 3 reads tighter. Prefer 3 unless Patrick wants 5.

### D-A3 — C8 panel placement

**Decision (proposed):** **sub-panel header inside Catchment Position card**, not a new card.

```
Catchment position
├── sa2_supply_ratio          (Full)
├── sa2_demand_supply         (Full)
├── sa2_child_to_place        (Full)
├── sa2_adjusted_demand       (Full)
├── sa2_demand_share_state    (Context)
│
│ ── Demographic mix ──
├── sa2_nes_share                   (Lite, already shipping)
├── sa2_atsi_share                  (Lite, NEW)
├── sa2_overseas_born_share         (Lite, NEW; + top-3 CoB context line)
└── sa2_single_parent_family_share  (Lite, NEW)
```

**Why:**
- C2 patcher author explicitly anticipated this ("Phase 2 will add a Demographic Mix sub-panel header above NES").
- DEC-11 — additive overlay default, prefer extending existing surfaces.
- A new card adds UI sprawl; demographic signals are not credit-direct (calibration-only) — they sit naturally beneath the credit signals as additional peer context.
- Render mechanism: a `<div>` divider with a small header label inside `renderCatchmentPositionCard()`, breaking the rows array into two segments.

**Tradeoff:** Catchment Position card grows to ~10 rows vs the current 6. Acceptable; DEC-75 visual weight (Lite rows ~⅓ height of Full rows) keeps total card height modest. Revisit only if user testing flags it.

**Reject:** new `renderCommunityProfileCard()`. It would force NES to move card mid-flight (a small but real regression), proliferates renderer functions, and contradicts DEC-11.

### D-A4 — Verification SA2s + sanity expectations

**Decision (proposed):** keep the existing 3 verification SA2s (Bayswater Vic, Bondi Junction-Waverly NSW, Bentley-Wilson WA) for continuity with A2 + B2 + C2 spotchecks. Add a fourth — a high-ATSI-share SA2 — to give ATSI a non-trivial test value.

**Suggested fourth:** any SA2 in `Western Australia → Outback (North)` or `Northern Territory → Outback`. Example candidate: `702011053` (Tiwi Islands NT) or `508051176` (Halls Creek WA). Pick at probe time once column names are confirmed.

**Sanity bounds (national, 2021):**
- ATSI share ~3.2% (ABS published)
- Overseas-born share ~27% (ABS published)
- Single-parent-family share of family households ~15% (ABS published)

If the national-weighted total computed during sanity_checks() falls outside ±2pp of these, halt and re-probe column selection.

---

## 5. Implementation sequence (post-ratification)

Three commits per DEC-22 collapsed pattern (data + UI verified together):

### Commit 1 — A10 ingest + B-pass banding
1. New script `layer4_4_step_a10_apply.py` (clone of `layer4_4_step_a2_apply.py`, parameterised over the 3 metrics + the new top-N table).
2. `python layer4_4_step_a10_apply.py` (dry-run) — verify SA2 counts, national totals.
3. STD-30 pre-mutation `db_inventory.md` snapshot.
4. `python layer4_4_step_a10_apply.py --apply` — backup + INSERT + audit_log row.
5. Patcher `patch_b2_layer3_add_demographic_mix.py` (3 entries appended to `METRICS = [...]`).
6. `python patch_b2_layer3_add_demographic_mix.py --apply`.
7. `python layer3_apply.py --apply` (lands banding).
8. **OI-35 workaround:** `python layer3_x_catchment_metric_banding.py --apply` (restores catchment metrics).
9. Spotcheck: `recon/probes/probe_a10_state.py` over the 4 verification SA2s.

### Commit 2 — C8 render (centre_page.py + centre.html)
1. Patcher `patch_c8_demographic_mix_centre_page.py` extending `LAYER3_METRIC_META`, `LAYER3_METRIC_INTENT_COPY`, `LAYER3_METRIC_TRAJECTORY_SOURCE`, and `POSITION_CARD_ORDER["catchment_position"]` with the 3 new metrics.
2. Patcher `patch_c8_demographic_mix_centre_html.py` extending the `order` array in `renderCatchmentPositionCard()`, inserting the "Demographic mix" sub-panel divider, and adding a `_renderTopNCountriesOfBirth()` helper for the contextual top-3 line below `sa2_overseas_born_share`.
3. Restart `review_server.py` (Python module cache).
4. Hard-refresh centre page (Ctrl+F5) for each verification SA2.
5. Visual spotcheck — Patrick.

### Commit 3 — End-of-session doc refresh
1. Update `PROJECT_STATUS.md`, `CENTRE_PAGE_V1_5_ROADMAP.md` (A10 + C8 closed), `OPEN_ITEMS.md` (OI-19 sub-bundle close), `PHASE_LOG.md`.
2. Mint DEC-78 to lock the corrected TSP table mapping (T06=ATSI, T14=family-comp) and the top-N storage convention.
3. Regenerate end-of-session monolith per STD-35.

---

## 6. Risks / unknowns banked for ingest time

- **T08 column "Australia" exact header.** Probe it at ingest top of `read_source()`; halt if missing.
- **T06 NS handling.** Indig_st_ns_P is small (~1.5% nationally). Decision in D-A1 above (Tot_Tot_P denominator).
- **T14 nested column tree.** T14A/B/C have `F_a_3 / F_a_4_8 / OD_* / H_f_so_*` slices; the ingest reads only the simple `Tot_FH_One_PFam` and `Tot_FH_Tot` totals at the end of T14C. Confirm exact column names at ingest time.
- **Census-year availability.** All three tables carry C11 / C16 / C21. No backfill issue.
- **Sparse SA2s.** Same OI-33 25-SA2 outlier set will silently render `None` per P-2.
- **Country-of-birth COB column ordering.** T08A holds A–N countries, T08B holds N–Z + totals. Need to merge before extracting top-N.

---

## 7. Verification plan (Patrick-facing)

After Commit 1:
- DB `audit_log` row written with `action = 'census_atsi_share_ingest_v1'` (+ overseas_born + single_parent variants, or one combined `demographic_mix_ingest_v1`).
- 4 verification SA2s ATSI / overseas-born / single-parent values within sanity bounds.
- Top-N table: 3 rows × 4 verification SA2s = 12 rows.

After Commit 2:
- Hard-refresh centre page → Catchment Position card shows sub-panel "Demographic mix" header followed by 4 Lite rows.
- Each row carries a delta badge ("+Xpp from 2011 to 2021") via existing `_renderLiteDelta` helper.
- Top-3 country-of-birth context line renders below the overseas-born row.
- Bayswater Vic + Bondi Junction-Waverly + Bentley-Wilson WA + the new high-ATSI SA2 all render cleanly.

---

## 8. Decision request (Patrick)

Ratify (or amend):
- **D-A1** — 3 bandable metrics, percentage 0–100, state_x_remoteness cohort, calibration deferred.
- **D-A2** — T08 top-N as a separate small table; default top-3; latest census only.
- **D-A3** — sub-panel inside Catchment Position card, not a new card.
- **D-A4** — keep 3 existing verification SA2s, add a fourth high-ATSI SA2 (specific code TBD at ingest time).

Once ratified, sequence in §5 starts. No code until then.
