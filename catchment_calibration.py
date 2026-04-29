"""
catchment_calibration.py — Layer 4.3 sub-pass 4.3.4
Version: v1 (2026-04-29)

Calibration function for SA2-level participation rate.

Per DEC-65 / OI-07: participation_rate isn't directly measured at SA2
by ABS. The four catchment ratios in Layer 4.2-A scope
(adjusted_demand, capture_rate, demand_supply, child_to_place) all
depend on it. This module ships the documented calibration function
that derives a defensible per-SA2 value from observable inputs, with
a transparent rule_text suitable for surfacing in a DER tooltip
alongside the resulting value.

Locked spec (STD-34, 2026-04-28b → 2026-04-29):
  - Default rate: 0.50
  - Range: [0.43, 0.55]
  - Nudges: ±0.02 per documented input
  - Inputs: income_decile, female_lfp_pct, nes_share_pct, aria_band

Implementation choices (sub-pass 4.3.4 probe, 2026-04-29):
  D1: Additive nudge composition. All nudges sum, then clamp.
  D2: Income decile thresholds symmetric — 8–10 → +0.02; 1–3 → −0.02.
  D3: Female LFP thresholds symmetric quartiles, computed from
      layer3_sa2_metric_banding (metric='sa2_lfp_females') at first
      call; falls back to fixed 65% / 80% if data unavailable.
  D4: ARIA two-step — Major City → +0.02; Remote/Very Remote → −0.02;
      others → 0.

NES nudge direction (not in surfaced decisions; default chosen):
  high NES share → downward nudge (cultural/language barriers
  correlate with lower formal-childcare participation). In V1 the
  input is always None per OI-19 (NES ingest deferred to Layer 4.4)
  so the nudge never fires. Direction can be revised when NES data
  lands and the calibration is back-tested against any available
  ground truth.

Usage:
    from catchment_calibration import calibrate_participation_rate
    rate, rule = calibrate_participation_rate(
        income_decile=8,
        female_lfp_pct=78.0,
        nes_share_pct=None,
        aria_band="Major Cities of Australia",
    )
    # rate -> 0.55 (clamped at ceiling)
    # rule -> "default 0.50; +0.02 income decile 8; ..."

Companion working-standard constants (STD-34) for Layer 4.2-A:
  ATTENDANCE_FACTOR = 0.6   — 3 days/week per PC universal-access target
  OCCUPANCY        = 0.85   — industry baseline

Module is read-only on the DB. No DB writes. No call sites in V1 —
sits ready for Layer 4.2-A.3 to consume.
"""

import sqlite3
from pathlib import Path
from typing import Optional, Tuple


# ─────────────────────────────────────────────────────────────────────
# STD-34 locked constants
# ─────────────────────────────────────────────────────────────────────

DEFAULT_RATE = 0.50
MIN_RATE = 0.43
MAX_RATE = 0.55
NUDGE = 0.02

# Companion constants for Layer 4.2-A consumers (STD-34)
ATTENDANCE_FACTOR = 0.6
OCCUPANCY = 0.85


# ─────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────

# Default DB path — assumes module sits at repo root alongside
# centre_page.py / operator_page.py. Caller can override via
# set_db_path() before first calibrate call if needed.
_DEFAULT_DB_PATH = Path(__file__).resolve().parent / "data" / "kintell.db"
_DB_PATH_OVERRIDE: Optional[Path] = None


def set_db_path(path: Path) -> None:
    """Override the default DB path. Must be called before the first
    calibrate_participation_rate() call to take effect (quartiles are
    cached after first computation)."""
    global _DB_PATH_OVERRIDE, _FEMALE_LFP_QUARTILES
    _DB_PATH_OVERRIDE = path
    _FEMALE_LFP_QUARTILES = None  # invalidate cache


def _db_path() -> Path:
    return _DB_PATH_OVERRIDE if _DB_PATH_OVERRIDE is not None else _DEFAULT_DB_PATH


# ─────────────────────────────────────────────────────────────────────
# Income decile thresholds (D2 — symmetric)
# ─────────────────────────────────────────────────────────────────────

_INCOME_HIGH = 8   # deciles 8–10 → +NUDGE
_INCOME_LOW = 3    # deciles 1–3 → −NUDGE


# ─────────────────────────────────────────────────────────────────────
# ARIA band → nudge map (D4 — two-step)
# ─────────────────────────────────────────────────────────────────────
# Keys are lowercased ARIA band labels. Both the long ABS form
# ("Major Cities of Australia") and the short form ("Major City") are
# supported, since Layer 4 reads receive both depending on the source.

_ARIA_NUDGE_MAP = {
    "major cities of australia":  +NUDGE,
    "major city":                 +NUDGE,
    "major cities":               +NUDGE,
    "inner regional australia":   0.0,
    "inner regional":             0.0,
    "outer regional australia":   0.0,
    "outer regional":             0.0,
    "remote australia":           -NUDGE,
    "remote":                     -NUDGE,
    "very remote australia":      -NUDGE,
    "very remote":                -NUDGE,
}


# ─────────────────────────────────────────────────────────────────────
# Female LFP quartile computation (D3 — symmetric quartiles from data)
# ─────────────────────────────────────────────────────────────────────

# Fallback if Layer 3 banding data isn't available at module use.
# Anchors: ABS publishes female LFP for women 25-44 around 75-82%
# nationally; SA2 distribution centres there. These are conservative
# best-guess thresholds for the rare case where the canonical lookup
# fails. See lessons-learned: relative thresholds preferred when data
# present (D3); fixed are fallback only.
_FALLBACK_FEMALE_LFP_Q1 = 65.0
_FALLBACK_FEMALE_LFP_Q3 = 80.0

# Cache: (q1, q3) tuple, populated on first call
_FEMALE_LFP_QUARTILES: Optional[Tuple[float, float]] = None


def _compute_female_lfp_quartiles() -> Tuple[float, float]:
    """Compute Q1 and Q3 of female LFP percent across all SA2s.

    Reads from layer3_sa2_metric_banding where metric='sa2_lfp_females'.
    Returns (q1, q3) percentage points.

    Defensive: if the table doesn't exist, lacks the metric, or has
    fewer than 4 non-null rows, falls back to
    (_FALLBACK_FEMALE_LFP_Q1, _FALLBACK_FEMALE_LFP_Q3).
    """
    db_path = _db_path()
    if not db_path.exists():
        return (_FALLBACK_FEMALE_LFP_Q1, _FALLBACK_FEMALE_LFP_Q3)

    try:
        conn = sqlite3.connect(str(db_path))
        try:
            rows = conn.execute("""
                SELECT raw_value FROM layer3_sa2_metric_banding
                WHERE metric = 'sa2_lfp_females'
                  AND raw_value IS NOT NULL
                ORDER BY raw_value ASC
            """).fetchall()
            if len(rows) < 4:
                return (_FALLBACK_FEMALE_LFP_Q1, _FALLBACK_FEMALE_LFP_Q3)
            values = [float(r[0]) for r in rows]
            n = len(values)
            q1_idx = n // 4
            q3_idx = (3 * n) // 4
            return (values[q1_idx], values[q3_idx])
        finally:
            conn.close()
    except sqlite3.OperationalError:
        return (_FALLBACK_FEMALE_LFP_Q1, _FALLBACK_FEMALE_LFP_Q3)


def _female_lfp_quartiles() -> Tuple[float, float]:
    """Lazy accessor — computes once, caches."""
    global _FEMALE_LFP_QUARTILES
    if _FEMALE_LFP_QUARTILES is None:
        _FEMALE_LFP_QUARTILES = _compute_female_lfp_quartiles()
    return _FEMALE_LFP_QUARTILES


# ─────────────────────────────────────────────────────────────────────
# Main calibration function
# ─────────────────────────────────────────────────────────────────────

def calibrate_participation_rate(
    income_decile: Optional[int],
    female_lfp_pct: Optional[float],
    nes_share_pct: Optional[float],
    aria_band: Optional[str],
) -> Tuple[float, str]:
    """Calibrate a per-SA2 participation rate from observable inputs.

    Returns (rate, rule_text).
    - rate: float in [MIN_RATE, MAX_RATE] (clamped after additive
      nudge composition).
    - rule_text: human-readable explanation of the calibration. Each
      input contributes one segment to the text, separated by '; '.
      Suitable for surfacing in a DER tooltip alongside the value.

    Per STD-34: any input None means that nudge does not fire (no
    contribution to rate; rule_text records "no data" or equivalent
    for that input).

    Nudge composition: additive (D1). All nudges sum, then clamp.
    """
    rule_parts = [f"default {DEFAULT_RATE:.2f}"]
    nudge_total = 0.0

    # ── Income decile (D2: symmetric 8–10 / 1–3) ─────────────────────
    if income_decile is None:
        rule_parts.append("no income decile data")
    elif not isinstance(income_decile, int) or income_decile < 1 or income_decile > 10:
        rule_parts.append(f"income decile {income_decile!r} out of range (no nudge)")
    elif income_decile >= _INCOME_HIGH:
        nudge_total += NUDGE
        rule_parts.append(f"+{NUDGE:.2f} income decile {income_decile} (high)")
    elif income_decile <= _INCOME_LOW:
        nudge_total -= NUDGE
        rule_parts.append(f"−{NUDGE:.2f} income decile {income_decile} (low)")
    else:
        rule_parts.append(f"income decile {income_decile} (mid, no nudge)")

    # ── Female LFP (D3: symmetric quartiles from data) ───────────────
    if female_lfp_pct is None:
        rule_parts.append("no female LFP data")
    else:
        q1, q3 = _female_lfp_quartiles()
        if female_lfp_pct >= q3:
            nudge_total += NUDGE
            rule_parts.append(
                f"+{NUDGE:.2f} female LFP top quartile "
                f"({female_lfp_pct:.1f}% ≥ {q3:.1f}%)"
            )
        elif female_lfp_pct <= q1:
            nudge_total -= NUDGE
            rule_parts.append(
                f"−{NUDGE:.2f} female LFP bottom quartile "
                f"({female_lfp_pct:.1f}% ≤ {q1:.1f}%)"
            )
        else:
            rule_parts.append(f"female LFP {female_lfp_pct:.1f}% (mid, no nudge)")

    # ── NES share (V1: always None per OI-19; nudge dormant) ────────
    if nes_share_pct is None:
        rule_parts.append("NES share not yet ingested (OI-19; nudge dormant)")
    elif nes_share_pct >= 0.30:
        # High NES → cultural/language barriers correlate with lower
        # formal-childcare participation → downward nudge.
        nudge_total -= NUDGE
        rule_parts.append(f"−{NUDGE:.2f} high NES share ({nes_share_pct:.2f})")
    elif nes_share_pct <= 0.05:
        nudge_total += NUDGE
        rule_parts.append(f"+{NUDGE:.2f} low NES share ({nes_share_pct:.2f})")
    else:
        rule_parts.append(f"NES share {nes_share_pct:.2f} (mid, no nudge)")

    # ── ARIA band (D4: two-step) ────────────────────────────────────
    if aria_band is None:
        rule_parts.append("no ARIA band")
    else:
        aria_key = str(aria_band).strip().lower()
        if aria_key in _ARIA_NUDGE_MAP:
            aria_nudge = _ARIA_NUDGE_MAP[aria_key]
            if aria_nudge > 0:
                nudge_total += aria_nudge
                rule_parts.append(f"+{aria_nudge:.2f} ARIA Major City")
            elif aria_nudge < 0:
                nudge_total += aria_nudge
                rule_parts.append(f"−{abs(aria_nudge):.2f} ARIA {aria_band}")
            else:
                rule_parts.append(f"ARIA {aria_band} (mid, no nudge)")
        else:
            rule_parts.append(f"ARIA band {aria_band!r} unrecognised (no nudge)")

    # ── Compose + clamp ─────────────────────────────────────────────
    raw_rate = DEFAULT_RATE + nudge_total
    rate = max(MIN_RATE, min(MAX_RATE, raw_rate))
    if abs(rate - raw_rate) > 1e-9:
        rule_parts.append(
            f"clamped to [{MIN_RATE:.2f}, {MAX_RATE:.2f}] (raw {raw_rate:.2f})"
        )

    rule_text = "; ".join(rule_parts)
    return (rate, rule_text)


# ─────────────────────────────────────────────────────────────────────
# Inline unit tests
# ─────────────────────────────────────────────────────────────────────
# Run with: python catchment_calibration.py
# These tests don't require a DB — they pin the female LFP quartiles
# to a known value via direct cache assignment so they're hermetic.

def _selftest():
    """Hermetic unit tests. Pins female LFP quartiles to (65.0, 80.0)
    for predictable behaviour without DB dependency."""
    global _FEMALE_LFP_QUARTILES
    _FEMALE_LFP_QUARTILES = (65.0, 80.0)

    failures = []

    def case(label, got, expected_rate, expected_substrings=()):
        rate, rule = got
        if abs(rate - expected_rate) > 1e-9:
            failures.append(f"{label}: rate {rate} != expected {expected_rate}")
        for sub in expected_substrings:
            if sub not in rule:
                failures.append(f"{label}: rule missing substring {sub!r}\n   rule: {rule}")

    # All-default — no nudges fire
    case(
        "all None",
        calibrate_participation_rate(None, None, None, None),
        DEFAULT_RATE,
        ("default 0.50", "no income decile", "no female LFP", "OI-19", "no ARIA"),
    )

    # All-positive nudges → ceiling clamp
    # income 9 → +0.02; female LFP 85% (≥80) → +0.02; NES 0.03 (≤0.05) → +0.02; ARIA Major City → +0.02
    # Total nudge = +0.08; raw 0.58; clamped to 0.55
    case(
        "all positive → ceiling",
        calibrate_participation_rate(9, 85.0, 0.03, "Major Cities of Australia"),
        0.55,
        ("clamped", "raw 0.58"),
    )

    # All-negative nudges → floor clamp
    # income 2 → −0.02; female LFP 60% (≤65) → −0.02; NES 0.40 (≥0.30) → −0.02; ARIA Very Remote → −0.02
    # Total nudge = −0.08; raw 0.42; clamped to 0.43
    case(
        "all negative → floor",
        calibrate_participation_rate(2, 60.0, 0.40, "Very Remote Australia"),
        0.43,
        ("clamped", "raw 0.42"),
    )

    # All-mid → exact default
    case(
        "all mid",
        calibrate_participation_rate(5, 72.0, 0.15, "Inner Regional Australia"),
        DEFAULT_RATE,
        ("default 0.50", "(mid, no nudge)"),
    )

    # Mixed: income high (+) cancels ARIA Very Remote (−)
    case(
        "mixed cancel",
        calibrate_participation_rate(9, None, None, "Very Remote"),
        DEFAULT_RATE,  # 0.50 + 0.02 - 0.02 = 0.50
        ("+0.02", "−0.02"),
    )

    # Single positive nudge — uncapped
    case(
        "single positive",
        calibrate_participation_rate(8, None, None, None),
        DEFAULT_RATE + NUDGE,  # 0.52
    )

    # Single negative nudge — uncapped
    case(
        "single negative",
        calibrate_participation_rate(1, None, None, None),
        DEFAULT_RATE - NUDGE,  # 0.48
    )

    # Edge: income out of range → no nudge
    case(
        "income out of range",
        calibrate_participation_rate(99, None, None, None),
        DEFAULT_RATE,
        ("out of range",),
    )

    # Edge: unrecognised ARIA → no nudge
    case(
        "unrecognised ARIA",
        calibrate_participation_rate(None, None, None, "Mars Colony"),
        DEFAULT_RATE,
        ("unrecognised",),
    )

    # Edge: female LFP exactly at quartile boundary
    case(
        "female LFP exact Q3",
        calibrate_participation_rate(None, 80.0, None, None),
        DEFAULT_RATE + NUDGE,  # ≥ Q3 fires
    )
    case(
        "female LFP exact Q1",
        calibrate_participation_rate(None, 65.0, None, None),
        DEFAULT_RATE - NUDGE,  # ≤ Q1 fires
    )

    # NES dormancy in V1 — None never nudges
    case(
        "NES None",
        calibrate_participation_rate(None, None, None, None),
        DEFAULT_RATE,
        ("OI-19",),
    )

    # ARIA short forms work
    case(
        "ARIA short form Major City",
        calibrate_participation_rate(None, None, None, "Major City"),
        DEFAULT_RATE + NUDGE,
    )
    case(
        "ARIA short form Remote",
        calibrate_participation_rate(None, None, None, "Remote"),
        DEFAULT_RATE - NUDGE,
    )

    # Reset cache after tests so a real run after import doesn't get pinned values
    _FEMALE_LFP_QUARTILES = None

    if failures:
        print(f"FAILED: {len(failures)} test case(s)")
        for f in failures:
            print(f"  - {f}")
        return 1
    else:
        print("OK: all calibration test cases passed")
        return 0


if __name__ == "__main__":
    import sys
    sys.exit(_selftest())
