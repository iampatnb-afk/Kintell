# Layer 4.3 Design — Amendment v1.1

**Status:** Supersedes specific sections of `recon/layer4_3_design.md` v1.0 (committed 2026-04-28b).
**Date:** 2026-04-29
**Driver:** Session conversation closing G1–G4, opening G5 (visual weight by data depth), and adding Thread D (workforce supply context block). Per P-1, captures decisions before code.

---

## Why this amendment

The original design doc surfaced four decisions (G1–G4) and scoped three implementation threads (A, B, C). This amendment:

- Closes G1+G2 (merged), G3, and G4
- Opens G5 (visual weight by data depth) and Thread D (workforce supply context block)
- Logs four new open items: OI-19, OI-20, OI-21, OI-22

§1–§3, §4.1–§4.8 (intent copy mechanics, four-ratio scope, calibration function, open data limitations, general implementation sequence shape), §5, §8 list base, and §9 of the original are unchanged. §4.9 is added. §6, §7, and the effort summary are amended below.

---

## §6 amended — decision closures and additions

### G1 + G2 merged — perspective toggle on reversible ratio pairs

**Closed jointly.** G1 (supply_ratio vs child_to_place rendering) and G2 (demand_supply direction) collapse into a single design pattern: ratio reversibility surfaced through a per-row "perspective" toggle.

**Scope.** Reversibility is a property of the metric, not a project-wide setting. Two of the four catchment ratios are reversible:

| Pair | Forward | Reverse | Lens framing |
|---|---|---|---|
| Supply intensity | `supply_ratio` (places/child) | `child_to_place` (children/place) | Forward = competition. Reverse = demand-headroom. |
| Demand absorption | `demand_supply` (adjusted_demand/places) | `demand_supply_inv` (1 / demand_supply) | Forward = fill expectation. Reverse = spare-capacity. |

`adjusted_demand` and `capture_rate` are not pairs (absolute estimates, not ratios over capacity). They do not carry a toggle.

**Metric registry additions.** Four new fields on each Layer 4 catchment metric in `centre_page.py`:

```python
LAYER4_CATCHMENT_METRICS = {
    "supply_ratio": {
        ...,
        "reversible": True,
        "pair_with": "child_to_place",
        "default_perspective": "forward",  # credit lens
        "perspective_labels": ("competition", "demand"),
    },
    "child_to_place": {..., "reversible": True, "pair_with": "supply_ratio", ...},
    "demand_supply": {..., "reversible": True, "pair_with": "demand_supply_inv", ...},
    "adjusted_demand": {..., "reversible": False},
    "capture_rate": {..., "reversible": False},
}
```

**Render contract.** When `reversible: True`, the row renders a small inline pill near the title (two states, named in `perspective_labels`). Toggling:

- swaps which ratio is rendered as primary
- swaps the band-copy template (high_is_concerning vs high_is_positive)
- swaps the inline intent-copy line below the title
- **preserves** the underlying decile — the SA2's position does not change; only the framing changes

**Default.** Credit lens: `supply_ratio` forward (competition), `demand_supply` forward (fill expectation).

**Band copy locked:**

| Metric | Direction | Low | Mid | High |
|---|---|---|---|---|
| `supply_ratio` | high_is_concerning | undersupplied — opportunity | balanced supply | saturated — competition risk |
| `child_to_place` | high_is_positive | thin demand per place | balanced demand per place | strong demand per place |
| `demand_supply` | high_is_positive | soft catchment — fill risk | in balance | demand pull — strong fill expected |
| `demand_supply_inv` | high_is_concerning | tight capacity vs demand | balance | abundant spare capacity |

### G3 closed — STD-34 locked

Working Standard 34 (calibration discipline) is locked. Original staged wording stands. `catchment_calibration.py` becomes the single named module for calibration constants and functions. Never magic numbers in code.

### G4 closed with explicit OI tracking

Layer 4.4 (NES, parent-cohort 25–44, schools) is deferred from V1. The deferral is logged as **OI-19** (see §8) so the gap stays visible rather than buried in a deferred-list.

### G5 — Visual weight by data depth (NEW)

**Question.** Should every centre-page Position metric render the full visual treatment (trajectory + cohort histogram + decile strip + band chips), or should treatment vary with data depth and resolution?

**Recommendation: three weights.** Force visual treatment to match analytical depth, per P-2 (honest absence over imputed presence).

| Weight | Components | When to use |
|---|---|---|
| **Full** | Trajectory chart + cohort histogram + gradient decile strip + band chips + inline intent copy | SA2 peer cohort + ≥5 dense time-series points |
| **Lite** | Gradient decile strip + band chips + inline intent copy + "as at YYYY" stamp | SA2 peer cohort but <5 series points |
| **Context-only** | Single-fact line + inline intent copy (optional state-level sparkline) | No SA2 peer cohort (state/national data) |

**Reclassification of currently-rendered Position metrics:**

| Metric | Current | New | Reason |
|---|---|---|---|
| sa2_under5_count | Full | Full | unchanged |
| sa2_total_population | Full | Full | unchanged |
| sa2_births_count | Full | Full | unchanged |
| sa2_unemployment_rate | Full | Full | unchanged |
| sa2_median_employee_income | Full | Full | unchanged |
| sa2_median_household_income | Full | Full | unchanged |
| sa2_median_total_income | Full | Full | unchanged |
| sa2_lfp_persons | Full | **Lite** | 3 Census points is not a trajectory |
| sa2_lfp_females | Full | **Lite** | 3 Census points is not a trajectory |
| sa2_lfp_males | Full | **Lite** | 3 Census points is not a trajectory |

`jsa_vacancy_rate` (currently deferred from Position) moves to Context-only and lives in the new Thread D Workforce supply context block.

**Implementation.** New `row_weight: "full" | "lite" | "context"` field on each metric in the Layer 4 metric registry. `centre.html` `renderPositionRow` switches on the field. ~0.2 session, additive to Thread C since intent copy already touches every row.

---

## §4.9 added — Thread D: Workforce supply context block

A new Position-level block alongside Population and Labour Market on the centre page. **Default open** per session decision (the credit-lens user should see workforce constraint at first read; collapsing it would soft-pedal a top-tier credit signal). Holds Context-only metrics where the data is state-level and there is no SA2 peer cohort.

**V1 rows from already-shipped data:**

| Row | Source | Resolution | Render |
|---|---|---|---|
| Child Carer vacancy index (ANZSCO 4211) | JSA IVI Step 5c | State, monthly | Latest + state-level sparkline |
| Early Childhood Teacher vacancy index (ANZSCO 2411) | JSA IVI Step 5c | State, monthly | Latest + state-level sparkline |

State-level sparklines render here because the trend in vacancy intensity is meaningful even where SA2 peer comparison is missing. What's absent is the peer band, not the trend.

**Honest framing per row.** Each row carries an explicit "state-level — no SA2 peer cohort" stamp. Inline intent copy is one sentence per row, e.g.:

> *"Vacancy index for child carers in your state. Higher = tighter educator supply, harder to staff up. State-level data — your specific catchment may be tighter or looser."*

No band, no decile strip, no cohort histogram.

**V1 add — recommended fold-in:**

| Row | Source | Why V1 |
|---|---|---|
| ECEC Award minimum rates (Cert III, Diploma, ECT) | Fair Work Award data | Anchors wage floor; cheap to add; one-time fact + annual update |
| Three-Day Guarantee effective Jan 2026 | Policy fact | Demand-side shock relevant to every centre's intake projection from 2026 |

Cheap additions that round out the supply story without reaching for new ingest scaffolding.

**V1.5 enrichment — logged as OI-20:**

| Source | Signal | Resolution |
|---|---|---|
| Direct SEEK scrape | Per-SA2 vacancy density and salary | SA2 |
| NCVER VET enrolments — CHC30121 (Cert III) + CHC50121 (Diploma) | Pipeline of new educators | State / remoteness (possibly already ingested — needs probe) |
| ANZSCO 4211 / 2411 advertised wages | Wage pressure leading indicator | State |

The NCVER data may already be in the DB from earlier panel3 work; **a probe is required** as the first step of Thread D implementation to confirm. If present, NCVER becomes a V1 row, not V1.5.

---

## §7 amended — implementation sequence

After G1+G2, G3, G4, G5 close, in order:

1. **Thread A** — per-chart range buttons on unemployment + improved empty-state. ~0.3 session.
2. **Thread B** — SALM probe for LFP. ~0.2 session probe; if positive, ~0.5 session ingest.
3. **Thread D probe** — confirm NCVER VET enrolments DB state. ~0.1 session.
4. **G3 lock + calibration function** — `catchment_calibration.py` with `calibrate_participation_rate()`. STD-34 locked. ~0.3 session.
5. **Schema migration** — 7 new columns on `service_catchment_cache` (including `row_weight`-relevant metadata). ~0.1 session.
6. **G5 row_weight field** — add to metric registry; reclassify LFP triplet to Lite; render switch in `centre.html`. ~0.2 session.
7. **G1+G2 perspective toggle** — `reversible` and `pair_with` fields; render-time swap; band-copy templates. ~0.3 session.
8. **`LAYER3_METRIC_INTENT_COPY` constant** — inline intent prose for all 10 existing + 4 catchment metrics, plus 2-4 Thread D rows. ~0.3 session.
9. **Thread D — Workforce supply context block** — rendering JSA IVI 4211 + 2411 + (NCVER if probe positive) + ECEC Award + Three-Day Guarantee. ~0.3 session.

---

## Effort summary amended

| Layer | v1.0 estimate | v1.1 estimate | Delta |
|---|---|---|---|
| 4.3 | ~1.7 sessions | ~2.5 sessions | +0.8 (G5, perspective toggle, Thread D, NCVER probe) |
| 4.2-A | ~2.2 sessions | ~2.2 sessions | unchanged |
| 4.4 | ~1.5 sessions | ~1.5 sessions | unchanged (deferred per OI-19) |

**V1 path remaining:** ~4.7 sessions (was 3.9), plus Layer 4.4 if promoted post-V1.

---

## §8 amended — open items added

| ID | Item |
|---|---|
| **OI-19** | Layer 4.4 ingests (NES, parent-cohort 25–44, schools). NES is required for the participation-rate calibration's NES nudge — currently the calibration function has a documented gap (`nes_share_pct` input is None at all SA2s). Parent-cohort 25–44 deepens demand picture beyond raw under-5 count. Schools data informs kinder-penetration analysis affecting addressable market scoping. **V1.5 — promote immediately after V1 ships.** |
| **OI-20** | Workforce supply context enrichments. (a) Direct SEEK-by-SA2 vacancy density + salary scrape (originally Catchment Explorer Phase 2). (b) NCVER VET enrolments at SA2/remoteness if Thread D probe shows it isn't already ingested. (c) Advertised-wage data for ANZSCO 4211 / 2411. **V1.5.** |
| **OI-21** | Future centre-page tab — quality elements (NQS detail, regulatory history). Currently surfaced inline in NOW. User has flagged eventual move to a dedicated tab. **Not V1 or V1.5 — out of scope until tabbing model is reviewed.** |
| **OI-22** | Future centre-page tab — ownership and corporate detail. Cross-reference into operator graph. Currently accessed via the operator-page link in the centre header. **Not V1 or V1.5 — out of scope until tabbing model is reviewed.** |

---

## §9.4 — resolved

Project doc restructuring landed in the 2026-04-29 chat. The 12-document structure is in place. STD-34 lands cleanly into the categorised STANDARDS.md. No further action under §9.4.

---

*End of amendment v1.1.*
