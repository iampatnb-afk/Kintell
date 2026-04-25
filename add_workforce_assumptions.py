#!/usr/bin/env python3
# ─────────────────────────────────────────────────────────────────────
# add_workforce_assumptions.py  v1
# Phase 1 (Module 2 Workforce) pre-step.
# Adds two rows to model_assumptions:
#   educator_ratio_ldc_blended = 6.5   (children per educator, blended LDC)
#   educator_ratio_oshc        = 15    (children per educator, OSHC)
# Same pattern as add_commentary_threshold.py:
#   - timestamped pre-mutation backup
#   - INSERT OR IGNORE (idempotent — safe to re-run)
#   - audit_log row capturing what landed
#   - post-write validation query
# Defensive: discovers model_assumptions columns at runtime via
# PRAGMA table_info, so unexpected schema additions won't break it.
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations
import sqlite3, shutil, sys, json
from datetime import datetime
from pathlib import Path

DB = Path("data/kintell.db")
BACKUP_DIR = Path("data")
NOW = datetime.now()
TS = NOW.strftime("%Y%m%d_%H%M%S")
BACKUP_PATH = BACKUP_DIR / f"kintell.db.backup_pre_workforce_assumptions_{TS}"

ROWS = [
    {
        "assumption_key": "educator_ratio_ldc_blended",
        "display_name":   "LDC blended educator-to-child ratio",
        "value_numeric":  6.5,
        "value_text":     "1:6.5",
        "units":          "children_per_educator",
        "description": (
            "Blended educator-to-child ratio across the 0-5 LDC cohort. Used to "
            "derive required_educators per centre as approved_places / "
            "value_numeric. Computed as the weighted reciprocal of the NQF "
            "age-band ratios:\n"
            "  (0.20 / 4) + (0.25 / 5) + (0.55 / 11) = 0.150 educators per child\n"
            "  => 1 educator per 6.67 children, rounded to 1:6.5 (conservative).\n"
            "Weighting reflects industry-typical LDC enrolment mix "
            "(~20% under-2, ~25% 2-3yo, ~55% 3-5yo). Mix is operator-dependent; "
            "revise this row if a specific operator's age-band data is loaded."
        ),
        "source": (
            "Education and Care Services National Regulations Reg 123 "
            "(NQF age-band ratios: 1:4 / 1:5 / 1:11). Age-mix weighting from "
            "industry-typical LDC enrolment distribution, cross-referenced "
            "with Productivity Commission (2024) 'A path to universal early "
            "childhood education and care' Volume 1 Figure 1 (CCS-approved "
            "ECEC engagement by single year of age)."
        ),
    },
    {
        "assumption_key": "educator_ratio_oshc",
        "display_name":   "OSHC educator-to-child ratio",
        "value_numeric":  15.0,
        "value_text":     "1:15",
        "units":          "children_per_educator",
        "description": (
            "Educator-to-child ratio for outside-school-hours care services. "
            "Used to derive required_educators for OSHC-classified centres as "
            "approved_places / value_numeric. National/dominant figure for "
            "school-age OSHC; some jurisdictions permit 1:11 for younger "
            "OSHC cohorts. Revise per service_sub_type if a state-specific "
            "ratio is required."
        ),
        "source": (
            "Education and Care Services National Regulations Reg 123, plus "
            "NSW Children (Education and Care Services) Supplementary "
            "Provisions Regulation 2019, and equivalent provisions in "
            "VIC/QLD/SA/WA/TAS/NT/ACT."
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

    cur.execute("PRAGMA table_info(model_assumptions)")
    cols = [r[1] for r in cur.fetchall()]
    if not cols:
        print("ERROR: model_assumptions table not found.", file=sys.stderr)
        return 3
    print(f"[2/5] model_assumptions columns: {cols}")

    nowiso = NOW.isoformat(timespec="seconds")
    inserted_keys, skipped_keys = [], []
    for row in ROWS:
        full = dict(row)
        if "is_active" in cols:        full.setdefault("is_active", 1)
        if "last_changed_at" in cols:  full.setdefault("last_changed_at", nowiso)
        if "created_at" in cols:       full.setdefault("created_at", nowiso)
        if "updated_at" in cols:       full.setdefault("updated_at", nowiso)

        payload = {k: v for k, v in full.items() if k in cols}
        col_list = ", ".join(payload.keys())
        ph_list  = ", ".join(["?"] * len(payload))
        cur.execute(
            f"INSERT OR IGNORE INTO model_assumptions ({col_list}) VALUES ({ph_list})",
            list(payload.values()),
        )
        (inserted_keys if cur.rowcount == 1 else skipped_keys).append(row["assumption_key"])

    print(f"[3/5] Inserted: {inserted_keys}")
    if skipped_keys:
        print(f"      Skipped (already present): {skipped_keys}")

    cur.execute("PRAGMA table_info(audit_log)")
    audit_cols = {r[1] for r in cur.fetchall()}
    if audit_cols:
        audit_payload = {
            "action_type": "data_seed",
            "entity_type": "model_assumptions",
            "entity_key":  "phase_1_workforce_assumptions",
            "actor":       "add_workforce_assumptions.py v1",
            "occurred_at": nowiso,
            "after_json":  json.dumps({"inserted": inserted_keys, "skipped": skipped_keys}),
            "notes":       "Phase 1 pre-step: educator_ratio_ldc_blended + educator_ratio_oshc",
        }
        audit_use = {k: v for k, v in audit_payload.items() if k in audit_cols}
        if audit_use:
            cl = ", ".join(audit_use.keys())
            pl = ", ".join(["?"] * len(audit_use))
            cur.execute(f"INSERT INTO audit_log ({cl}) VALUES ({pl})", list(audit_use.values()))
            print(f"[4/5] audit_log row inserted (audit_id={cur.lastrowid})")
        else:
            print("[4/5] audit_log columns mismatched; audit row skipped")
    else:
        print("[4/5] audit_log table missing; audit row skipped")

    con.commit()

    cur.execute(
        "SELECT assumption_key, value_numeric, value_text, units "
        "FROM model_assumptions "
        "WHERE assumption_key IN ('educator_ratio_ldc_blended','educator_ratio_oshc') "
        "ORDER BY assumption_key"
    )
    rows = cur.fetchall()
    print(f"[5/5] Validation ({len(rows)} rows):")
    for r in rows:
        print(f"      {r[0]:32s}  num={r[1]}  text={r[2]!s:8s}  units={r[3]}")
    con.close()

    if len(rows) != 2:
        print("WARNING: expected 2 rows back, got", len(rows))
        return 1

    print("\nDone.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
