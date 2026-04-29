# Layer 4.3 sub-pass 4.3.4 — Calibration function (`catchment_calibration.py`)

**Date:** 2026-04-29
**Operator:** Patrick Bell
**Sub-pass:** 4.3.4 (eighth of nine in Layer 4.3; STD-34 implementation)
**Effort:** ~0.3 session
**Decision drivers:** STD-34 (locked 2026-04-29 with closure of Layer 4.3 design) + DEC-65 (probe before code) + OI-07 (participation_rate not measured at SA2)

---

## Why this sub-pass exists

The four catchment ratios in Layer 4.2-A scope (`adjusted_demand`, `capture_rate`, `demand_supply`, `child_to_place`) all depend on `participation_rate`. ABS doesn't directly publish participation rate at SA2 — only at SA4. Without calibration, the four catchment ratios can't render at the SA2 level the centre page operates on.

STD-34 locked the calibration approach 2026-04-29 with the closure of the Layer 4.3 design (DEC-74 through DEC-76 + STD-34). This sub-pass implements the locked spec.

---

## Locked spec (STD-34)

- **Default rate:** 0.50
- **Range:** [0.43, 0.55]
- **Nudges:** ±0.02 per documented input
- **Function signature:** `calibrate_participation_rate(income_decile, female_lfp_pct, nes_share_pct, aria_band) → (rate, rule_text)`
- **Output:** the rate AND a human-readable explanation of which nudges fired, suitable for surfacing in a DER tooltip alongside the value

Companion working-standard constants for Layer 4.2-A consumers:
- `ATTENDANCE_FACTOR = 0.6` (3 days/week per PC universal-access target)
- `OCCUPANCY = 0.85` (industry baseline)

These are exposed as module-level constants in `catchment_calibration.py` so Layer 4.2-A code references them by canonical name rather than recreating magic numbers (DEC-13).

---

## Implementation choices (D1–D4 confirmed in chat)

| | Choice | Rationale |
|---|---|---|
| **D1** | Additive nudge composition: sum all, clamp at end | Simplest, transparent. Narrow [0.43, 0.55] band makes clamping informative ("at the ceiling = every signal positive"). |
| **D2** | Income decile thresholds symmetric: 8–10 → +0.02; 1–3 → −0.02 | Decile is a coarse signal anyway; symmetric thresholds reflect methodological humility. |
| **D3** | Female LFP thresholds symmetric quartiles, computed at first call from `layer3_sa2_metric_banding` (metric=`sa2_lfp_females`) | Relative thresholds adapt to the distribution; fixed thresholds risk being mis-tuned. Cached after first compute. Falls back to fixed (65%, 80%) if data unavailable. |
| **D4** | ARIA two-step: Major City → +0.02; Remote/Very Remote → −0.02; others → 0 | Fractional nudges feel false-precise given the methodology. Two-step matches the other dimensions. |

### NES nudge direction (not surfaced as a numbered decision)

Default chosen: high NES share (≥0.30) → downward nudge; low (≤0.05) → upward. Cultural/language barriers correlate with lower formal-childcare participation. **Never fires in V1** because `nes_share_pct` is `None` at all SA2s per OI-19 (NES ingest deferred to Layer 4.4). Direction can be revised when NES data lands and the calibration is back-tested against ground truth.

---

## File: `catchment_calibration.py` v1

Module structure:

1. **Module docstring** — full spec, decisions, usage example
2. **STD-34 constants** — `DEFAULT_RATE`, `MIN_RATE`, `MAX_RATE`, `NUDGE`, `ATTENDANCE_FACTOR`, `OCCUPANCY`
3. **Configuration** — DB path with `set_db_path()` override
4. **Income decile thresholds** — `_INCOME_HIGH = 8`, `_INCOME_LOW = 3`
5. **ARIA nudge map** — long ABS forms ("Major Cities of Australia") and short forms ("Major City") both supported, lowercased lookup
6. **Female LFP quartile computation** — `_compute_female_lfp_quartiles()` reads `layer3_sa2_metric_banding` filtered to `metric='sa2_lfp_females'`, computes Q1/Q3, caches; defensive on missing table or low-row-count
7. **`calibrate_participation_rate()`** — main function; additive composition with end clamp; rule_text composed segment by segment
8. **Inline `_selftest()`** — 13 hermetic test cases (DB-independent; pins quartiles to 65/80 for predictable behaviour)

The module is read-only on the DB. No DB writes. No import side-effects beyond the (lazy) quartile lookup. Sits ready for Layer 4.2-A.3 to consume; no V1 call sites yet.

---

## Validation

All 13 inline test cases pass:

```
python catchment_calibration.py
OK: all calibration test cases passed
```

Cases cover:
- All-None inputs → exact default
- All-positive nudges → ceiling clamp + "raw 0.58" in rule
- All-negative nudges → floor clamp + "raw 0.42" in rule
- All-mid → exact default
- Mixed positive/negative → cancel out
- Single positive / single negative → ±NUDGE off default
- Income decile out of range → no nudge + "out of range" in rule
- Unrecognised ARIA → no nudge + "unrecognised" in rule
- Female LFP exactly at Q1 / Q3 boundary → nudges fire (≤ / ≥ inclusive)
- NES None → never nudges + "OI-19" in rule
- ARIA short forms ("Major City", "Remote") work alongside long forms

The selftest pins `_FEMALE_LFP_QUARTILES = (65.0, 80.0)` directly so test results are predictable independent of DB state, then resets the cache after.

---

## Open dependencies

When Layer 4.2-A.3 ships (catchment ratios), it will:

1. Import `calibrate_participation_rate` from this module
2. For each centre's SA2, gather the four inputs (income_decile from `sa2_cohort.seifa_decile`; female_lfp_pct from `layer3_sa2_metric_banding[metric=sa2_lfp_females].raw_value`; nes_share_pct = None until Layer 4.4; aria_band from `sa2_cohort.ra_name`)
3. Call the function, apply the rate to the four catchment ratios, surface `rule_text` in each ratio's DER tooltip
4. Reference `ATTENDANCE_FACTOR` and `OCCUPANCY` from this module by canonical name (no magic numbers, per DEC-13)

When Layer 4.4 NES ingest ships, the `nes_share_pct` input becomes populated and the NES branch of the function fires for high-NES SA2s. No changes required to this module — the input was always part of the signature, just unpopulated in V1.

---

## Cross-references

- **STD-34** — Calibration discipline for non-SA2-measured metrics (locked spec)
- **DEC-13** — `model_assumptions` table as single source of truth (justifies module-constant exposure)
- **DEC-65** — Calibration function is the path through OI-07
- **OI-07** — `participation_rate` not measured at SA2 (this sub-pass closes the fix path; OI-07 effectively closes when 4.2-A.3 consumes the function)
- **OI-19** — Layer 4.4 V1.5 ingests deferred (NES; the NES nudge stays dormant until that lands)
- `recon/layer4_3_design.md` v1.1 — Layer 4.3 design closure
