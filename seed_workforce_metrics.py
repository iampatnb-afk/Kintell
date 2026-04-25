#!/usr/bin/env python3
# ─────────────────────────────────────────────────────────────────────
# seed_workforce_metrics.py  v1
# Phase 1 Step A. Seeds the six Workforce metric_definitions rows.
#
# Schema (PRAGMA table_info(metric_definitions)):
#   metric_key      TEXT  PK
#   display_name    TEXT  NOT NULL
#   classification  TEXT  NOT NULL    (OBS / DER / COM)
#   formula         TEXT  nullable
#   source          TEXT  nullable
#   units           TEXT  nullable
#   description     TEXT  nullable
#   version         TEXT  NOT NULL    default 'v1'
#   created_at      TEXT  NOT NULL    default datetime('now')
#   updated_at      TEXT  nullable
#
# audit_log mapping (now known — schema captured this session):
#   actor / action / subject_type / subject_id NOT NULL.
# Pattern: subject_type='table', subject_id='metric_definitions'.
#
# Idempotent: INSERT OR IGNORE keyed on metric_key. Re-runs safe.
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations
import sqlite3, shutil, sys, json
from datetime import datetime
from pathlib import Path

DB = Path("data/kintell.db")
NOW = datetime.now()
TS = NOW.strftime("%Y%m%d_%H%M%S")
BACKUP_PATH = Path("data") / f"kintell.db.backup_pre_workforce_metrics_{TS}"

ROWS = [
    {
        "metric_key":     "required_educators_centre",
        "display_name":   "Required educators (centre)",
        "classification": "DER",
        "formula": (
            "required_educators_centre = services.approved_places / blended_ratio_for_subtype, "
            "where blended_ratio_for_subtype is selected from model_assumptions:\n"
            "  service_sub_type IN ('LDC','CBDC') -> educator_ratio_ldc_blended (1:6.5)\n"
            "  service_sub_type = 'OSHC'          -> educator_ratio_oshc        (1:15)\n"
            "  service_sub_type = 'FDC' or NULL   -> NULL (FDC has a different regulatory model)."
        ),
        "source": (
            "services.approved_places (ACECQA NQAITS, Q4 2025 snapshot). "
            "Blended ratio from model_assumptions rows seeded by "
            "add_workforce_assumptions.py v2."
        ),
        "units": "educators (regulatory minimum on-floor)",
        "description": (
            "Per-centre regulatory educator-on-floor minimum, derived from the "
            "NQF age-band ratios weighted to a typical LDC enrolment mix (or 1:15 "
            "for OSHC). This is not an FTE figure: it does not account for shift "
            "coverage, breaks, supervisor density, or non-contact time. Use as "
            "a lower-bound demand signal for workforce planning."
        ),
    },
    {
        "metric_key":     "required_educators_group",
        "display_name":   "Required educators (group total)",
        "classification": "DER",
        "formula": (
            "required_educators_group = SUM(required_educators_centre) over all "
            "services where services.group_id = :group_id AND services.is_active = 1."
        ),
        "source": (
            "Aggregated over the operator's active centre roster. Inputs as per "
            "required_educators_centre."
        ),
        "units": "educators (regulatory minimum on-floor)",
        "description": (
            "Group-level rollup of per-centre minimums. Used as the headline "
            "Workforce-card statistic on the operator page."
        ),
    },
    {
        "metric_key":     "workforce_growth_12m",
        "display_name":   "Required educators 12-month change",
        "classification": "DER",
        "formula": (
            "workforce_growth_12m = required_educators_group(today) "
            "- required_educators_group(t-12m), where t-12m is the most recent "
            "group_snapshots row with occurred_at <= datetime('now', '-12 months'). "
            "NULL when no historical snapshot exists in that window."
        ),
        "source": (
            "Derived from the group_snapshots time series (Phase 0a infrastructure)."
        ),
        "units": "educators (delta)",
        "description": (
            "Change in required-educator demand over the trailing 12 months at "
            "the consolidated group level. Indicates whether the operator's "
            "workforce demand is growing, flat, or shrinking."
        ),
    },
    {
        "metric_key":     "workforce_growth_24m",
        "display_name":   "Required educators 24-month change",
        "classification": "DER",
        "formula": (
            "workforce_growth_24m = required_educators_group(today) "
            "- required_educators_group(t-24m), where t-24m is the most recent "
            "group_snapshots row with occurred_at <= datetime('now', '-24 months'). "
            "NULL when no historical snapshot exists in that window."
        ),
        "source": (
            "Derived from the group_snapshots time series (Phase 0a infrastructure)."
        ),
        "units": "educators (delta)",
        "description": (
            "Change in required-educator demand over the trailing 24 months. "
            "Provides a longer-horizon view than workforce_growth_12m and "
            "smooths through quarter-on-quarter snapshot noise."
        ),
    },
    {
        "metric_key":     "supply_completions_state",
        "display_name":   "Training completions (state, year)",
        "classification": "OBS",
        "formula": (
            "supply_completions_state(state, year) = "
            "SUM(training_completions.completions) "
            "WHERE training_completions.state = :state "
            "  AND training_completions.year  = :year "
            "  AND training_completions.qualification_code IN "
            "      (the four ECEC qualification codes captured by the Phase 1.5 ingest: "
            "       Cert III and Diploma of Early Childhood Education and Care, "
            "       current and superseded versions)."
        ),
        "source": (
            "NCVER VOCSTATS DataBuilder — Total Program Completions by State, "
            "Year, and Qualification Code. Each cell rounded to nearest 5; "
            "aggregate sums may drift by up to +/- 25 per state-year. NSW 2024 "
            "specifically flagged by NCVER as overstated. See "
            "training_completions_ingest_run for the per-run caveat capture."
        ),
        "units": "completions (people)",
        "description": (
            "Annual count of newly qualified ECEC educators graduating in a "
            "given state. The state-level supply pipeline available to operators "
            "with centres in that state."
        ),
    },
    {
        "metric_key":     "supply_growth_state",
        "display_name":   "Training completions YoY change",
        "classification": "DER",
        "formula": (
            "supply_growth_state(state, year) = "
            "supply_completions_state(state, year) "
            "- supply_completions_state(state, year - 1)."
        ),
        "source": (
            "Derived from training_completions. Inherits the +/- 25 "
            "rounding drift from each side of the subtraction (worst-case +/- 50 "
            "on the delta)."
        ),
        "units": "completions (delta)",
        "description": (
            "Year-on-year change in graduate supply at the state level. "
            "Compared against workforce_growth_12m at the operator level to "
            "trigger the COM commentary line when demand growth outpaces "
            "supply growth in the operator's primary state(s) of operation."
        ),
    },
]

def main() -> int:
    if not DB.exists():
        print(f"ERROR: {DB} not found. Run from repo root.", file=sys.stderr)
        return 2

    print(f"[1/5] Backing up DB -> {BACKUP_PATH}")
    shutil.copy2(DB, BACKUP_PATH)

    con = sqlite3.connect(DB)
    con.execute("PRAGMA foreign_keys = ON")
    cur = con.cursor()

    cur.execute("PRAGMA table_info(metric_definitions)")
    cols = [r[1] for r in cur.fetchall()]
    if not cols:
        print("ERROR: metric_definitions table not found.", file=sys.stderr)
        return 3
    print(f"[2/5] metric_definitions columns: {cols}")

    nowiso = NOW.isoformat(timespec="seconds")
    inserted_keys, skipped_keys = [], []
    for row in ROWS:
        full = dict(row)
        if "version" in cols:     full.setdefault("version", "v1")
        if "updated_at" in cols:  full.setdefault("updated_at", nowiso)
        # created_at intentionally left to the schema default (datetime('now'))

        payload = {k: v for k, v in full.items() if k in cols}
        col_list = ", ".join(payload.keys())
        ph_list  = ", ".join(["?"] * len(payload))
        cur.execute(
            f"INSERT OR IGNORE INTO metric_definitions ({col_list}) VALUES ({ph_list})",
            list(payload.values()),
        )
        (inserted_keys if cur.rowcount == 1 else skipped_keys).append(row["metric_key"])

    con.commit()
    print(f"[3/5] Inserted ({len(inserted_keys)}): {inserted_keys}")
    if skipped_keys:
        print(f"      Skipped ({len(skipped_keys)} already present): {skipped_keys}")

    # audit_log — schema now known. Single row capturing the seed event.
    try:
        cur.execute(
            "INSERT INTO audit_log "
            "(actor, action, subject_type, subject_id, before_json, after_json, reason, occurred_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "seed_workforce_metrics.py v1",
                "data_seed",
                "table",
                "metric_definitions",
                json.dumps({"existing_keys": skipped_keys}),
                json.dumps({"inserted": inserted_keys, "skipped": skipped_keys}),
                "Phase 1 Step A: seed six Workforce metric_definitions rows "
                "(required_educators_centre, required_educators_group, "
                "workforce_growth_12m, workforce_growth_24m, "
                "supply_completions_state, supply_growth_state).",
                nowiso,
            ),
        )
        con.commit()
        print(f"[4/5] audit_log row inserted (audit_id={cur.lastrowid})")
    except sqlite3.IntegrityError as e:
        con.rollback()
        print(f"[4/5] audit_log insert failed (IntegrityError: {e}). Data write is safe; audit row skipped.")
    except sqlite3.OperationalError as e:
        con.rollback()
        print(f"[4/5] audit_log insert failed (OperationalError: {e}). Data write is safe; audit row skipped.")

    cur.execute(
        "SELECT metric_key, classification, units "
        "FROM metric_definitions "
        "WHERE metric_key IN (?,?,?,?,?,?) "
        "ORDER BY classification, metric_key",
        tuple(r["metric_key"] for r in ROWS),
    )
    rows = cur.fetchall()
    print(f"[5/5] Validation ({len(rows)} rows):")
    for r in rows:
        print(f"      {r[1]}  {r[0]:32s}  units={r[2]}")
    con.close()

    if len(rows) != 6:
        print(f"WARNING: expected 6 rows back, got {len(rows)}")
        return 1

    print("\nDone.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
