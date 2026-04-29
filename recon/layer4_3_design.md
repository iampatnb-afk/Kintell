# Layer 4.3 Design — Calibration, Intent Copy, Per-Chart Buttons, Perspective Toggle, Visual Weight, Workforce Supply Context

**Version:** v1.1
**Status:** All design decisions closed. Implementation ready.
**v1.0:** 2026-04-28 — initial design surfaced four decisions G1–G4 plus §9.4 + three threads A/B/C
**v1.1:** 2026-04-29 — G1+G2 merged into perspective toggle (DEC-74); G3 closed by locking STD-34; G4 closed with OI-19 tracking; G5 added (DEC-75 visual weight by depth); Thread D added (DEC-76 workforce supply context block); §9.4 implicitly resolved by 2026-04-28 doc restructure.

---

## §1. Scope

Layer 4.3 is the centre-page enhancement layer that completes the Position-block treatment. It adds:

- **Catchment ratios** as Position rows: four metrics (`supply_ratio`, `child_to_place`, `demand_supply`, `adjusted_demand` — `capture_rate` is also a derived metric in the same family). All depend on a `participation_rate` input that is not directly measured at SA2.
- **Per-chart range buttons** for short-data series (Thread A — primarily unemployment).
- **LFP source upgrade probe** (Thread B — does JSA SALM publish LFP at SA2?).
- **Inline intent copy** under each metric title — one-sentence "what this tells you" prose.
- **Perspective toggle** on reversible ratio pairs (DEC-74, added v1.1).
- **Visual weight reclassification** by data depth (DEC-75, added v1.1).
- **Workforce supply context block** (DEC-76, Thread D added v1.1).

What is **out of scope**: Layer 4.4 ingests (NES, parent-cohort, schools — deferred to V1.5 per OI-19); a new tab structure for the centre page (deferred per OI-21 / OI-22); SEEK-by-SA2 / NCVER-by-SA2 / advertised-wage data (V1.5 enrichments per OI-20).

---

## §2. Threads

| Thread | Focus | v1.1 status |
|---|---|---|
| A | Per-chart range buttons + improved empty-state on unemployment | Unchanged from v1.0 — implementation pending |
| B | SALM probe for LFP at SA2; if positive, ingest | Unchanged from v1.0 — probe pending |
| C | Catchment ratios + calibration function + intent copy | Calibration discipline locked as STD-34. Implementation pending. |
| **D** | **Workforce supply context block** — state-level supply data on the centre page in Context-only weight | **New in v1.1 (DEC-76).** Default-open block alongside Population and Labour Market cards. |

---

## §3. Catchment ratios — analytical scope

Four catchment ratios + one absolute estimate, derived per-SA2 from population, places, and a calibrated participation rate:

| Metric | Formula | Type |
|---|---|---|
| `supply_ratio` | `places / under_5_count` | Ratio (places per child) |
| `child_to_place` | `under_5_count / places` | Ratio (children per place) — inverse of supply_ratio |
| `adjusted_demand` | `under_5_count × participation_rate × attendance_factor` | Absolute (estimated demand in children) |
| `capture_rate` | `adjusted_demand / total_state_demand` | Ratio (share of state demand) |
| `demand_supply` | `adjusted_demand / places` | Ratio (demand absorption) |
| `demand_supply_inv` | `1 / demand_supply` | Ratio (spare capacity) — inverse of demand_supply |

Two interpretive pairs:

- **Supply intensity:** `supply_ratio` ↔ `child_to_place`. Forward = competition lens. Reverse = demand-headroom lens.
- **Demand absorption:** `demand_supply` ↔ `demand_supply_inv`. Forward = fill expectation. Reverse = spare-capacity lens.

`adjusted_demand` and `capture_rate` are absolute estimates, not ratios with meaningful inverses. They do not pair.

This pairing structure is the basis of DEC-74 (perspective toggle).

---

## §4. Sub-threads (implementation detail)

### §4.1 Thread A — Per-chart range buttons (unchanged from v1.0)

Unemployment series has 61 quarterly points. The global 3Y/5Y/10Y/All trend window (DEC-73) applies relative to the most recent point. Reviewers asked for per-chart 1Y / 2Y zoom on unemployment specifically — the metric most often inspected at short horizon (recent labour-market shock).

**Implementation:** small inline button strip on the unemployment row. Falls back to the global window when not pressed. ~0.3 session.

**Empty-state:** for SALM-missing SA2s (DEC-53), render an explicit "no SALM data published for this SA2" tile, not a missing chart.

### §4.2 Thread B — SALM LFP probe (unchanged from v1.0)

JSA SALM publishes unemployment at SA2 quarterly. If JSA SALM also publishes LFP (labour force participation) at SA2, the centre page can promote LFP from 3 Census points (DEC-60) to ~60 quarterly points.

**Probe steps (~0.2 session):**
1. Inspect the JSA SALM publication page for an LFP series alongside unemployment.
2. If present at SA2: download, schema-check, confirm coverage matches existing SALM ingest.
3. If absent or coarser: stay on Census-only LFP. Reclassify to **Lite** weight per DEC-75.

**If positive:** ~0.5 session ingest + Layer 3 banding update + Layer 4 render swap. LFP triplet stays at Full weight.

**If negative:** LFP triplet renders Lite per DEC-75. Per-decade Census points + decile strip + chips + intent copy. Honest about depth.

### §4.3 Thread C — Catchment ratios + calibration function

The four catchment ratios all depend on `participation_rate`, which is not directly measured at SA2. STD-34 (locked 2026-04-29) defines the calibration discipline.

**Calibration module:** `catchment_calibration.py`. Single named module; no magic numbers in code (DEC-13 + STD-34).

**Function signature:**

```python
def calibrate_participation_rate(
    income_decile: int | None,
    female_lfp_pct: float | None,
    nes_share_pct: float | None,
    aria_band: str | None,
) -> tuple[float, str]:
    """
    Returns (rate, rule_text).
    Default 0.50; range [0.43, 0.55]; nudges ±0.02 per documented input.
    """
```

**Nudge rules:**

| Input | Direction | Magnitude |
|---|---|---|
| `income_decile` 7–10 | Up | +0.02 |
| `income_decile` 1–3 | Down | −0.02 |
| `female_lfp_pct` ≥ 70 | Up | +0.02 |
| `female_lfp_pct` ≤ 50 | Down | −0.02 |
| `nes_share_pct` ≥ 30 | Down | −0.02 |
| `aria_band` Outer/Remote/Very Remote | Down | −0.02 |

**Documented gap:** `nes_share_pct` is None at all SA2s in V1 (NES ingest deferred to Layer 4.4 per OI-19). The NES nudge therefore never fires in V1. The function returns the rate computed without the NES branch and the rule text is explicit about which inputs were available.

**Constants:**
- `attendance_factor = 0.6` — 3 days per week per Productivity Commission universal-access target
- `occupancy_assumption = 0.85` — industry baseline

Both stored as module-level constants in `catchment_calibration.py`. STD-34 prohibits magic numbers anywhere else.

**DER tooltip surface (DEC-12 + STD-34):** every centre-page row that consumes a calibrated rate exposes the function's `rule_text` in the DER tooltip. The reader sees how the rate was constructed for their SA2.

### §4.4 Schema migration

`service_catchment_cache` gets 7 new columns (initial population is OI-05 — currently empty):

```
participation_rate REAL,           -- calibrated per-SA2
participation_rule_text TEXT,      -- DER tooltip surface
attendance_factor REAL,            -- always 0.6 (constant)
adjusted_demand REAL,              -- under_5_count * participation * attendance
capture_rate REAL,                 -- share of state demand
demand_supply REAL,                -- adjusted_demand / places
demand_supply_inv REAL             -- 1 / demand_supply
```

Migration pattern follows DEC-10 (Tier 2 ingest). Pre-mutation backup per STD-08; audit_log row per STD-11.

### §4.5 Inline intent copy

Each Position-row metric carries a one-sentence prose line under the title — "what this tells you in this row". Stored as `LAYER3_METRIC_INTENT_COPY` in `centre_page.py` (single source of truth, DEC-13 pattern).

**Coverage:** all 10 existing Position metrics + 4 catchment metrics + 2-4 Workforce supply context block rows = 16-18 prose lines.

**Tone:** neutral, single sentence, no jargon. Example: *"Under-5 population is the size of the demand pool. Higher = bigger market, lower = thinner market."*

For reversible-pair metrics (DEC-74), the intent copy has two variants — one per perspective state. Toggling the perspective swaps the prose.

### §4.6 Per-metric direction conventions (locked 2026-04-29)

Band copy templates for the four catchment ratios — locked per DEC-74, superseding DEC-72:

| Metric | Direction | Low | Mid | High |
|---|---|---|---|---|
| `supply_ratio` | high_is_concerning | undersupplied — opportunity | balanced supply | saturated — competition risk |
| `child_to_place` | high_is_positive | thin demand per place | balanced demand per place | strong demand per place |
| `demand_supply` | high_is_positive | soft catchment — fill risk | in balance | demand pull — strong fill expected |
| `demand_supply_inv` | high_is_concerning | tight capacity vs demand | balance | abundant spare capacity |

Stroke colour does NOT carry valence (DEC-71). Direction lives only in band-copy text.

### §4.7 Per-chart-row visual treatment (DEC-75, locked v1.1)

Three row weights for centre-page metrics:

| Weight | Components | When applied |
|---|---|---|
| **Full** | Trajectory chart + cohort histogram + gradient decile strip + band chips + inline intent copy | SA2 peer cohort + ≥5 dense series points |
| **Lite** | Gradient decile strip + band chips + inline intent copy + "as at YYYY" stamp | SA2 peer cohort but <5 series points |
| **Context-only** | Single-fact line + inline intent copy (optional state-level sparkline) | No SA2 peer cohort (state/national data) |

Reclassifications applied to currently-rendered Position metrics:

- `sa2_lfp_persons`, `sa2_lfp_females`, `sa2_lfp_males` → **Lite** (3 Census points is not a trajectory; promote to Full only if Thread B probe is positive)
- `jsa_vacancy_rate` → **Context-only** (state-level; moves out of Position into the Workforce supply context block per DEC-76)
- All 7 other Position metrics → **Full** (unchanged)

**Implementation:** `row_weight: "full" | "lite" | "context"` field on each metric in the Layer 4 metric registry. `centre.html renderPositionRow` switches on the field.

### §4.8 Perspective toggle on reversible ratio pairs (DEC-74, added v1.1)

The two reversible ratio pairs (§3) carry a per-row perspective toggle.

**Metric registry additions:**

```python
LAYER4_CATCHMENT_METRICS = {
    "supply_ratio": {
        ...,
        "reversible": True,
        "pair_with": "child_to_place",
        "default_perspective": "forward",   # credit lens
        "perspective_labels": ("competition", "demand"),
    },
    "child_to_place": {
        ...,
        "reversible": True,
        "pair_with": "supply_ratio",
        ...
    },
    "demand_supply": {
        ...,
        "reversible": True,
        "pair_with": "demand_supply_inv",
        "default_perspective": "forward",   # credit lens
        "perspective_labels": ("fill", "spare"),
    },
    "demand_supply_inv": { ... },
    "adjusted_demand": { ..., "reversible": False },
    "capture_rate": { ..., "reversible": False },
}
```

**Render contract.** When `reversible: True`, the row renders a small inline pill near the title (two states, named in `perspective_labels`). Toggling:

- swaps which ratio renders as primary
- swaps the band-copy template (high_is_concerning ↔ high_is_positive)
- swaps the inline intent-copy line
- *preserves* the underlying decile — the SA2's position does not change, only the framing changes

Default state per metric in registry. Credit-lens defaults: `supply_ratio` forward (competition); `demand_supply` forward (fill expectation).

### §4.9 Workforce supply context block (DEC-76, Thread D, added v1.1)

A new Position-level block on the centre page alongside Population and Labour Market cards.

**Default open.** Workforce constraint is a top-tier credit signal; collapsing it would soft-pedal the data.

**Content type.** Holds Context-only metrics per DEC-75 — state-level data with no SA2 peer cohort.

**V1 rows from already-shipped data:**

| Row | Source | Resolution | Render |
|---|---|---|---|
| Child Carer vacancy index (ANZSCO 4211) | JSA IVI Step 5c | State, monthly | Latest + state-level sparkline |
| ECT vacancy index (ANZSCO 2411) | JSA IVI Step 5c | State, monthly | Latest + state-level sparkline |
| ECEC Award minimum rates (Cert III, Diploma, ECT) | Fair Work Award data | National | Fact + annual update |
| Three-Day Guarantee policy effective Jan 2026 | Policy fact | National | Single-line |

State-level sparklines render here because the trend in vacancy intensity is meaningful even where SA2 peer comparison is missing. What's absent is the peer band, not the trend.

**Honest framing per row.** Each row carries an explicit "state-level — no SA2 peer cohort" stamp (or "national" for Award/policy rows). Inline intent copy is one sentence per row. No band, no decile strip, no cohort histogram.

**Example row content:**

> **Child Carer vacancy index (ANZSCO 4211, your state)**
> Latest: [value] · 12-month change: [delta] · State-level — no SA2 peer cohort
> [sparkline: state-level monthly index]
> *Vacancy index for child carers in your state. Higher = tighter educator supply, harder to staff up. State-level data; your specific catchment may be tighter or looser.*

**V1.5 enrichments (tracked as OI-20):**

- Direct SEEK-by-SA2 vacancy density and salary scrape (originally Catchment Explorer Phase 2)
- NCVER VET enrolments at SA2/remoteness for CHC30121 (Cert III) + CHC50121 (Diploma) — pipeline of new educators (probe needed: may already be in DB from earlier panel3 work; if so, promote to V1)
- ANZSCO 4211 / 2411 advertised-wage data — wage pressure leading indicator

---

## §5. Open data quality issues affecting Layer 4.3

| Issue | Impact | Mitigation |
|---|---|---|
| `participation_rate` not measured at SA2 (OI-07) | Four catchment ratios depend on calibration | STD-34 calibration discipline + DER tooltip surface |
| `nes_share_pct` not yet ingested (OI-19) | NES nudge in calibration function never fires in V1 | Function handles `None` input gracefully; rule text states which inputs were available |
| LFP source is Census-only, 3 points (OI-06) | Cannot render trajectory chart honestly | DEC-75 Lite weight; promote to Full on positive Thread B probe |
| `jsa_vacancy_rate` is state-level (OI-11) | Cannot band against SA2 peers | DEC-76 Context-only block — render as fact, not Position row |
| `service_catchment_cache` is empty (OI-05) | Catchment ratios unrenderable until populated | Layer 2.5 cache build is gated on Layer 4.3 calibration function landing |

---

## §6. Decisions — closure record

All five threads closed during the 2026-04-29 closure session.

### G1 + G2 — merged → DEC-74 (Perspective toggle on reversible ratio pairs)

**Context.** G1 surfaced the question of whether `supply_ratio` or `child_to_place` should render as primary. G2 surfaced the same question for `demand_supply` direction. Both collapse into the same design pattern.

**Decision.** Reversibility is a per-metric property surfaced via a per-row "perspective" toggle. Two reversible pairs (§3); two fixed metrics (`adjusted_demand`, `capture_rate`). Toggle preserves the underlying decile — only framing changes. Default = credit lens.

**Closure status.** **CLOSED 2026-04-29 → DEC-74.** Supersedes DEC-72 by promoting its conventions into the toggle pattern. Band copy locked per §4.6.

### G3 — STD-34 locked

**Context.** Calibration discipline was staged in v1.0 awaiting design closure.

**Decision.** Lock STD-34. `catchment_calibration.py` is the named module. `calibrate_participation_rate()` signature locked per §4.3. Constants (`attendance_factor=0.6`, `occupancy_assumption=0.85`) locked.

**Closure status.** **CLOSED 2026-04-29.** STD-34 status changed from STAGED to locked.

### G4 — Layer 4.4 deferral → OI-19

**Context.** Layer 4.4 covers three SA2-level ingests (NES, parent-cohort 25–44, schools) that deepen the demand picture. None is V1-critical, but NES is required to close the calibration function's documented `nes_share_pct` gap.

**Decision.** Defer Layer 4.4 to V1.5. Promote immediately after V1 ships. Track explicitly as OI-19 so the gap stays visible.

**Closure status.** **CLOSED 2026-04-29 → OI-19.**

### G5 — Visual weight by data depth → DEC-75 (NEW in v1.1)

**Context.** v1.0 implicitly assumed every Position row carried the full visual treatment. The 2026-04-29 session surfaced that several metrics (LFP triplet, `jsa_vacancy_rate`) don't have the data depth or geographic resolution to justify the full template. Forcing them into the full template breaks P-2.

**Decision.** Three row weights — Full / Lite / Context-only — assigned per-metric. Reclassify LFP triplet to Lite, `jsa_vacancy_rate` to Context-only.

**Closure status.** **CLOSED 2026-04-29 → DEC-75.**

### Thread D — Workforce supply context block → DEC-76 (NEW in v1.1)

**Context.** Educator and ECT workforce supply is a top-tier credit signal. Available data is state-level (JSA IVI 4211, 2411). Suppressing it from the centre page would soft-pedal the signal; rendering as a Position row would fake SA2 resolution it doesn't have.

**Decision.** New default-open block alongside Population and Labour Market, holding Context-only rows. V1 content per §4.9. V1.5 enrichments tracked as OI-20.

**Closure status.** **CLOSED 2026-04-29 → DEC-76.**

### §9.4 — Project doc restructuring

**Context.** v1.0 §9.4 raised a question about how Layer 4.3 outputs would land in the project doc set.

**Closure status.** **Implicitly resolved.** The 2026-04-28 doc restructure produced the 12-doc structure (`PROJECT_STATUS.md`, `DECISIONS.md`, `STANDARDS.md`, `OPEN_ITEMS.md`, `ROADMAP.md`, `recon/PHASE_LOG.md`, etc.). Layer 4.3's outputs land cleanly in those docs.

---

## §7. Implementation sequence

Total ~2.5 sessions (was 1.7 in v1.0; +0.8 for DEC-74 toggle, DEC-75 row-weight, DEC-76 block, NCVER probe).

| Step | Description | Effort |
|---|---|---|
| 1 | **Thread A** — per-chart range buttons on unemployment + improved empty-state | ~0.3 session |
| 2 | **Thread B** — SALM probe for LFP. Probe ~0.2; if positive, ingest ~0.5 | ~0.7 session |
| 3 | **Thread D probe** — confirm NCVER VET enrolments DB state (whether already ingested) | ~0.1 session |
| 4 | **G3 implementation** — `catchment_calibration.py` with `calibrate_participation_rate()`. STD-34 locked. | ~0.3 session |
| 5 | **Schema migration** — 7 new columns on `service_catchment_cache` per §4.4 | ~0.1 session |
| 6 | **G5 implementation** — `row_weight` field on metric registry; reclassify LFP triplet to Lite; render switch in `centre.html` | ~0.2 session |
| 7 | **G1+G2 implementation** — `reversible` / `pair_with` / `default_perspective` / `perspective_labels` fields; render-time swap; band-copy templates | ~0.3 session |
| 8 | **`LAYER3_METRIC_INTENT_COPY`** — inline prose for all 10 existing + 4 catchment metrics + 2–4 Workforce supply context rows | ~0.3 session |
| 9 | **Thread D implementation** — Workforce supply context block render. JSA IVI 4211 + 2411 + (NCVER if probe positive) + ECEC Award + Three-Day Guarantee. Default open. | ~0.3 session |

**Order rationale.** Threads A and B are independent of the new design and can land first. Thread D probe (step 3) gates whether NCVER promotes from V1.5 to V1. Steps 4–5 land the calibration scaffolding before any UI consumes it. Steps 6–9 are UI-side; can interleave with Layer 4.2-A's render work.

---

## §8. Open items raised by this design

| ID | Item |
|---|---|
| OI-07 | `participation_rate` not measured at SA2 — closed by STD-34 + calibration function landing |
| OI-19 | Layer 4.4 ingests deferred (NES, parent-cohort, schools) — V1.5 |
| OI-20 | Workforce supply context enrichments — SEEK-by-SA2, NCVER-by-SA2, advertised wages — V1.5 |
| OI-21 | Future centre-page tab for quality elements — out of scope until tabbing model reviewed |
| OI-22 | Future centre-page tab for ownership — out of scope until tabbing model reviewed |

---

## §9. Cross-document landings

When this design implements, the following structured docs are touched:

| Doc | Update |
|---|---|
| `DECISIONS.md` | DEC-74, DEC-75, DEC-76 added (this session) |
| `STANDARDS.md` | STD-34 locked (this session) |
| `OPEN_ITEMS.md` | OI-19, OI-20, OI-21, OI-22 added; OI-18 closed (this session) |
| `ROADMAP.md` | Layer 4.3 effort 1.7 → 2.5 sessions; Thread D added; closure status logged (this session) |
| `PROJECT_STATUS.md` | Layer 4.3 status: design v1.1 closed, implementation ready (this session) |
| `recon/PHASE_LOG.md` | Session entry appended (this session) |
| `ARCHITECTURE.md` | No update needed — DEC-71 boundary still holds; new block uses existing Palette A + Chart.js mix |

---

*End of v1.1.*
