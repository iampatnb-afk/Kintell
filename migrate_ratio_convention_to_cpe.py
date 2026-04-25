#!/usr/bin/env python3
# ─────────────────────────────────────────────────────────────────────
# migrate_ratio_convention_to_cpe.py  v1
#
# Phase 1 hot-fix: converts the three Phase 0a-seeded educator_ratio
# rows from "educators-per-child" (the implicit NQF representation) to
# "children-per-educator" (the convention used by every downstream
# consumer in v8+).
#
# Background:
#   model_assumptions had two conventions co-existing for the same
#   concept:
#     educator_ratio_0_24m       value_numeric=0.25,   units='ratio'
#     educator_ratio_24_36m      value_numeric=0.20,   units='ratio'
#     educator_ratio_36m_plus    value_numeric=0.0909, units='ratio'
#     educator_ratio_ldc_blended value_numeric=6.5,    units='children_per_educator'
#     educator_ratio_oshc        value_numeric=15.0,   units='children_per_educator'
#   operator_page.py v8 _compute_workforce() divides approved_places
#   by value_numeric, which is correct for children-per-educator but
#   gives wildly inflated numbers for educators-per-child. PSK
#   centres would have read 0.0909 and produced ~50,000 required
#   educators per centre.
#
# Action:
#   For the three "ratio"-units rows, rewrite value_numeric to the
#   canonical NQF children-per-educator integer (4 / 5 / 11) and set
#   units = 'children_per_educator'. value_text is already in "1:N"
#   form and is left untouched. description is left untouched.
#
#   Detection rules per row:
#     - If value_numeric is close to the old fraction AND units='ratio',
#       convert.
#     - If value_numeric is already the new integer AND units is
#       'children_per_educator', skip (idempotent re-run).
#     - Anything else: abort with a clear error so a stale or
#       partially-edited row doesn't get silently overwritten.
#
# Working standards honoured:
#   - Pre-mutation backup with timestamp.
#   - audit_log row capturing before- and after-state.
#   - Validation query at the end.
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations
import sqlite3, shutil, sys, json
from datetime import datetime
from pathlib import Path
from math import isclose

DB = Path("data/kintell.db")
NOW = datetime.now()
TS = NOW.strftime("%Y%m%d_%H%M%S")
BACKUP_PATH = Path("data") / f"kintell.db.backup_pre_ratio_convention_migration_{TS}"

TARGETS = [
    {"key": "educator_ratio_0_24m",    "old_num": 0.25,   "new_num": 4.0,  "text": "1:4"},
    {"key": "educator_ratio_24_36m",   "old_num": 0.20,   "new_num": 5.0,  "text": "1:5"},
    {"key": "educator_ratio_36m_plus", "old_num": 0.0909, "new_num": 11.0, "text": "1:11"},
]

# Tolerance for matching the old fractional values. 0.0909 was
# stored at 4 decimal places, so 0.001 is comfortably tight.
TOL = 0.001


def main() -> int:
    if not DB.exists():
        print(f"ERROR: {DB} not found. Run from repo root.", file=sys.stderr)
        return 2

    print(f"[1/6] Backing up DB -> {BACKUP_PATH}")
    shutil.copy2(DB, BACKUP_PATH)

    con = sqlite3.connect(DB)
    cur = con.cursor()

    # 2) Read current state
    print("[2/6] Reading current rows...")
    keys = tuple(t["key"] for t in TARGETS)
    placeholders = ",".join(["?"] * len(keys))
    rows = cur.execute(
        f"SELECT assumption_key, value_numeric, value_text, units "
        f"  FROM model_assumptions "
        f" WHERE assumption_key IN ({placeholders})",
        keys,
    ).fetchall()
    current = {r[0]: {"value_numeric": r[1], "value_text": r[2], "units": r[3]} for r in rows}

    missing = [k for k in keys if k not in current]
    if missing:
        print(f"ERROR: expected rows missing from model_assumptions: {missing}", file=sys.stderr)
        con.close()
        return 3

    # 3) Decide action per row
    plan = []
    for t in TARGETS:
        cur_row = current[t["key"]]
        cur_num   = cur_row["value_numeric"]
        cur_units = cur_row["units"]
        cur_text  = cur_row["value_text"]

        if cur_num is not None and isclose(cur_num, t["old_num"], abs_tol=TOL) and cur_units == "ratio":
            plan.append({"key": t["key"], "action": "convert",
                         "from_num": cur_num, "to_num": t["new_num"],
                         "from_units": cur_units, "to_units": "children_per_educator"})
        elif cur_num is not None and isclose(cur_num, t["new_num"], abs_tol=TOL) and cur_units == "children_per_educator":
            plan.append({"key": t["key"], "action": "skip_already_done",
                         "value_numeric": cur_num, "units": cur_units})
        else:
            plan.append({"key": t["key"], "action": "abort_unexpected",
                         "value_numeric": cur_num, "units": cur_units, "value_text": cur_text})

    print("[3/6] Plan:")
    for p in plan:
        print(f"      {p}")

    aborts = [p for p in plan if p["action"] == "abort_unexpected"]
    if aborts:
        print(f"ERROR: {len(aborts)} row(s) in unexpected state. Aborting WITHOUT mutation.", file=sys.stderr)
        con.close()
        return 4

    # 4) Apply conversions
    nowiso = NOW.isoformat(timespec="seconds")
    converted = []
    skipped = []
    for p in plan:
        if p["action"] == "convert":
            cur.execute(
                "UPDATE model_assumptions "
                "   SET value_numeric    = ?, "
                "       units            = 'children_per_educator', "
                "       last_changed_by  = 'migrate_ratio_convention_to_cpe.py v1', "
                "       last_changed_at  = ? "
                " WHERE assumption_key   = ?",
                (p["to_num"], nowiso, p["key"]),
            )
            if cur.rowcount != 1:
                con.rollback()
                print(f"ERROR: UPDATE affected {cur.rowcount} rows for {p['key']}; rolled back.", file=sys.stderr)
                con.close()
                return 5
            converted.append(p["key"])
        else:
            skipped.append(p["key"])

    con.commit()
    print(f"[4/6] Converted: {converted}")
    if skipped:
        print(f"      Skipped (already converted): {skipped}")

    # 5) audit_log row
    try:
        cur.execute(
            "INSERT INTO audit_log "
            "(actor, action, subject_type, subject_id, before_json, after_json, reason, occurred_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "migrate_ratio_convention_to_cpe.py v1",
                "data_migration",
                "table",
                "model_assumptions",
                json.dumps({k: current[k] for k in keys}, default=str),
                json.dumps({"converted": converted, "skipped": skipped,
                            "new_values": {t["key"]: t["new_num"] for t in TARGETS}}),
                "Convert Phase 0a-seeded educator_ratio rows from "
                "educators-per-child (units='ratio') to "
                "children-per-educator (units='children_per_educator') "
                "to match the convention used by operator_page.py v8 "
                "_compute_workforce() and the v2-seeded LDC/OSHC rows. "
                "Single convention prevents the 1/x bug from biasing "
                "any future Workforce-card consumer.",
                nowiso,
            ),
        )
        con.commit()
        print(f"[5/6] audit_log row inserted (audit_id={cur.lastrowid})")
    except (sqlite3.IntegrityError, sqlite3.OperationalError) as e:
        con.rollback()
        print(f"[5/6] audit_log insert failed ({e}). Data write is safe; audit row skipped.")

    # 6) Validate by reading all five educator_ratio_* rows
    rows = cur.execute(
        "SELECT assumption_key, value_numeric, value_text, units "
        "  FROM model_assumptions "
        " WHERE assumption_key LIKE 'educator_ratio_%' "
        " ORDER BY assumption_key"
    ).fetchall()
    print(f"[6/6] Validation ({len(rows)} rows):")
    all_cpe = True
    for r in rows:
        flag = "OK " if r[3] == "children_per_educator" else "!! "
        if r[3] != "children_per_educator":
            all_cpe = False
        print(f"      {flag}{r[0]:32s}  num={r[1]!s:7s}  text={r[2]!s:7s}  units={r[3]}")
    con.close()

    if not all_cpe:
        print("WARNING: not all educator_ratio_* rows are children_per_educator after migration.")
        return 1

    print("\nDone. All educator_ratio_* rows now use children-per-educator convention.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
