# OI-NEW-21 — Catchment trajectory coverage gap (probe)

*Origin: 2026-05-10 PM session 2 — Patrick noticed `docs/sa2_history.json` covers only 1,267 of ~2,400 Australian SA2s; centres in absent SA2s render no catchment-position trajectory. V1 priority HIGH per Patrick. This probe is read-only per DEC-65 — no DB or file mutations.*

---

## 1. Question

Why does `docs/sa2_history.json` cover only 1,267 SA2s when `services.sa2_code` (polygon-backfilled per DEC-70) anchors services in 2,294 distinct SA2s? Which fix shape is correct?

---

## 2. Method

Read-only inspection of:

- `build_sa2_history.py` (the script that produces `sa2_history.json`)
- `docs/sa2_history.json` (the output consumed by `centre.html` / `index.html`)
- `services` table — distinct `sa2_code` count and per-SA2 service samples
- `abs_data/postcode_to_sa2_concordance.csv` — the SA2 attribution mechanism the build script uses
- Concordance lookups for postcodes attached to the two known-missing SA2s (Bentley-Wilson WA `506031124` and Outback NT `702041063`)

---

## 3. Findings

### 3.1 The gating mechanism

`build_sa2_history.py:274-276`:

```python
sa2_info = concordance.get(pc)
if not sa2_info:
    continue
```

Each NQAITS service row's **postcode** is looked up in `postcode_to_sa2_concordance.csv` to derive an SA2. An SA2 only ends up in `sa2_history.json` if at least one service's postcode resolves to it via the concordance. **Attribution is postcode-based.**

### 3.2 Quantified gap

| Source | Distinct SA2s | Notes |
|---|---|---|
| `services.sa2_code` (polygon-derived per DEC-70) | **2,294** | Authoritative — what the centre page uses |
| `sa2_history.json` (postcode-derived via concordance) | **1,267** | What the trajectory renderer uses |
| **Gap (services-anchored SA2s missing from history)** | **1,043** | The user-visible coverage gap |
| Phantom history SA2s (in history, no service polygon-anchored) | 16 | Misattributed inflow from gap SA2s |
| Concordance postcodes total | 1,983 | One-postcode→one-SA2 |
| Services in gap SA2s | **7,143 of 18,203 (39.2%)** | Worse than SA2-count ratio because gap SA2s anchor more services on average |

### 3.3 Failure modes (verified empirically)

For Bentley-Wilson WA (`506031124`, 11 polygon-anchored services):

| Postcode | Concordance maps to | Failure mode |
|---|---|---|
| 6102 | `306021144 BENTLEY PARK` (QLD) | **Cross-state name collision** — concordance picked QLD's "Bentley Park" not WA's "Bentley" |
| 6107 | `506041132 BECKENHAM-KENWICK-LANGFORD` (WA) | **Neighbour SA2 within same state** — postcode covers multiple SA2s, concordance picked one |

For Outback NT (`702041063`, 5 polygon-anchored services):

| Postcode | Concordance maps to | Failure mode |
|---|---|---|
| 0822 | `('', '')` empty | **Postcode missing from concordance** |
| 0880 | `702041064 NHULUNBUY` (NT) | **Neighbour SA2** |

### 3.4 Root cause

The concordance is structurally **one-postcode → one-SA2**, while reality is many-to-many (postcodes routinely span SA2s, and SA2s like Outback NT cover multiple postcodes). Plus there are cross-state postcode-name collisions where the concordance happens to pick the wrong state. Plus some postcodes are simply absent from the concordance.

The build was correct for V1.0 (where polygon-derived `services.sa2_code` didn't yet exist consistently), but is now superseded by DEC-70 polygon attribution. The two systems are **mutually inconsistent on 1,043 SA2s** — a centre page anchors at one SA2 (polygon truth) and the trajectory build attributes its history to a different SA2 (concordance assumption). This is silent and the renderer correctly suppresses absent canvases per P-2.

---

## 4. Fix options (ranked)

### Option A (recommended) — Polygon-first attribution in the build

Switch `build_sa2_history.py` from postcode-concordance lookup to a polygon-derived service→SA2 lookup, with postcode-concordance as fallback for pre-Q12022 quarters where Service Approval Number doesn't yet appear.

**Mechanism:**

1. At build start, read `services` table and build two lookup dicts:
 - `appr_to_sa2`: `Service Approval Number → sa2_code` (covers Q12022+)
 - `name_pc_to_sa2`: `(normalised_service_name, postcode) → sa2_code` (covers pre-Q12022)
2. In `process_sheet_sa2()`, replace the concordance lookup:
 - Q12022+: try `appr_to_sa2[appr_num]` first; if absent, fall back to `name_pc_to_sa2[(name, pc)]`; if still absent, fall back to postcode concordance
 - Pre-Q12022: try `name_pc_to_sa2[(name, pc)]` first; if absent, fall back to postcode concordance
3. Rebuild `sa2_history.json` (~15–25 min runtime).

**Effort:** ~0.4–0.6 sess. Single function refactor + run + spotcheck.

**Expected outcome:** SA2 coverage expands from 1,267 → ~2,294 (or close to it; some fallback misses will remain). The 4 verifying SA2s all render trajectories, including Bentley-Wilson WA and Outback NT.

**Verification plan:** spotcheck that all 4 verifying SA2s render trajectories; spot-confirm a sample of new-coverage SA2s render the expected centre count and supply ratio against `services` table values; compare pre/post unique-SA2 count and total event count.

### Option B — Concordance hygiene only

Patch the concordance to add missing postcodes (e.g., 0822) and resolve cross-state name collisions. Leave the build mechanism unchanged.

**Effort:** ~0.5–1.0 sess. Concordance is 1,983 entries; auditing 8,000+ postcodes-in-services for misattribution and resolving each is substantial.

**Why not preferred:** treats the symptom (concordance entries) not the cause (postcode is the wrong key). Polygon attribution already exists and is authoritative; we'd be duplicating its accuracy in a less-authoritative file.

### Option C — Renderer fallback path

Change `centre.html` to render a different proxy trajectory (e.g., neighbour SA2 average, or state-level series) when the centre's SA2 is absent from `sa2_history.json`.

**Effort:** ~0.3 sess. UI-only, no rebuild needed.

**Why not preferred:** masks data correctness with an inferred/blended series. Violates "honest absence over imputed presence" (P-2). Excel exports and group-page rollups would inherit blended data without provenance.

---

## 5. Recommendation

**Option A.** Polygon-first attribution in `build_sa2_history.py`, with postcode concordance as fallback only for old quarters or unmatched rows. This is the only fix that resolves the underlying inconsistency between the centre-page SA2 (polygon) and the trajectory SA2 (postcode).

---

## 6. Open questions / risks

- **Pre-Q12022 fuzzy match accuracy.** `name_pc_to_sa2` lookup against `services.service_name` may miss services that have been renamed or de-registered since 2022. We should measure miss-rate during implementation; if material, consider keeping postcode-concordance as final fallback.
- **Phantom history SA2s.** 16 SA2s currently have history rows but no polygon-anchored service. After the fix, those rows disappear (correctness improves). `index.html` and `centre.html` should be re-checked for any code that lists "all SA2s with history" assuming current set.
- **Concordance hygiene as separate item.** The concordance is still used as a fallback. Items like missing PC 0822 are worth a separate light hygiene pass — could fold into a future OI for completeness, but not a blocker for OI-NEW-21.
- **`docs/sa2_history.json` size.** Currently 13.2 MB at 1,267 SA2s. Expanding to ~2,294 SA2s could push it to ~24 MB. May affect `centre.html` cold-load on slower connections; worth monitoring but no V1 mitigation needed.
- **Re-banding implications.** `layer3_sa2_metric_banding` and the catchment cache use `services.sa2_code` directly — neither depends on `sa2_history.json`. So no re-banding work cascaded by this fix. The fix is contained to the trajectory build + JSON output.

---

## 7. Next step

If Option A is approved, implementation is a single-script edit in `build_sa2_history.py` plus rebuild + spotcheck. STD-08 backup of `data/sa2_history.json` and `docs/sa2_history.json`, STD-11 audit_log INSERT (`sa2_history_rebuild_v3` action), then run.

The fix should land **before** the Centre v2 redesign design pass per Patrick's sequencing.
