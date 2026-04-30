"""
migrate_4_3_5_service_catchment_cache.py v2
=============================================
Sub-pass 4.3.5 — schema migration on `service_catchment_cache`.

v2 change: STD-13 self-check in v1 used `tasklist`, which on Windows
spawns transient helper python.exe processes via subprocess
machinery, causing false positives. v2 uses WMIC to query the full
process tree with parent PIDs, then excludes (a) this process and
(b) any descendant of this process. Falls back to a "skip with
warning" if WMIC is unavailable rather than blocking the migration.

Adds 7 columns per layer4_3_design.md s4.4:
  Ratio columns (REAL):
    - adjusted_demand
    - capture_rate
    - demand_supply
    - child_to_place
  Calibration-metadata columns:
    - calibrated_rate     REAL
    - rule_text           TEXT
    - calibration_run_at  TEXT  (format 'YYYY-MM-DD HH:MM:SS' UTC,
                                 set by populator)

All 7 columns are nullable with no DEFAULT — per DEC-11, the
migration adds shape only; population is the 4.2-A populator's job.

STD-30 pre-mutation discipline:
  1. STD-13 self-check (refuse to run if true orphan python.exe).
  2. STD-08 backup of data/kintell.db.
  3. BEGIN IMMEDIATE; re-verify pre-conditions inside the txn.
  4. 7 x ALTER TABLE ADD COLUMN.
  5. INSERT into audit_log with before/after column lists.
  6. COMMIT.
  7. Post-mutation validation (read-only).

Idempotent-safe: step 3 will ROLLBACK if any of the 7 target columns
already exist.

Usage (from repo root):
    python migrate_4_3_5_service_catchment_cache.py
"""

import json
import os
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime

DB_PATH = os.path.join("data", "kintell.db")
TABLE = "service_catchment_cache"

NEW_COLUMNS = [
    ("adjusted_demand", "REAL"),
    ("capture_rate", "REAL"),
    ("demand_supply", "REAL"),
    ("child_to_place", "REAL"),
    ("calibrated_rate", "REAL"),
    ("rule_text", "TEXT"),
    ("calibration_run_at", "TEXT"),
]
EXPECTED_FINAL_COLUMN_COUNT = 17 + len(NEW_COLUMNS)  # 24

AUDIT_ACTOR = "layer4_3_5_apply"
AUDIT_ACTION = "service_catchment_cache_extend_v1"
AUDIT_SUBJECT_TYPE = "service_catchment_cache"
AUDIT_SUBJECT_ID = 0
AUDIT_REASON = (
    "Layer 4.3 sub-pass 4.3.5: schema extension on "
    "service_catchment_cache. Added 4 catchment ratio columns "
    "(adjusted_demand, capture_rate, demand_supply, child_to_place) "
    "and 3 calibration-metadata columns (calibrated_rate, rule_text, "
    "calibration_run_at) per layer4_3_design.md s4.4. Migration adds "
    "shape only; population is the 4.2-A populator's job (DEC-11). "
    "Table was empty pre-migration (OI-05) so no data preservation "
    "required. Backup taken pre-migration per STD-08."
)


def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def fail(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


# ------------------------------------------------------------------
# STD-13 self-check (v2)
# ------------------------------------------------------------------
def _query_python_processes_via_wmic() -> list:
    """Return list of (pid, parent_pid) for all python.exe processes.

    Uses WMIC to get parent PID, which lets us exclude descendants of
    this script. Returns None if WMIC fails or is unavailable.
    """
    try:
        out = subprocess.check_output(
            ["wmic", "process", "where",
             "name='python.exe'", "get",
             "ProcessId,ParentProcessId", "/FORMAT:CSV"],
            text=True, stderr=subprocess.DEVNULL,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None

    procs = []
    for line in out.splitlines():
        line = line.strip()
        if not line or line.lower().startswith("node"):
            continue
        # CSV: Node,ParentProcessId,ProcessId
        parts = line.split(",")
        if len(parts) < 3:
            continue
        try:
            ppid = int(parts[1])
            pid = int(parts[2])
        except ValueError:
            continue
        procs.append((pid, ppid))
    return procs


def std13_self_check() -> None:
    """Refuse to run if a non-descendant orphan python.exe is alive."""
    log("STD-13: scanning for orphan python.exe processes (WMIC)")
    my_pid = os.getpid()
    procs = _query_python_processes_via_wmic()

    if procs is None:
        log("STD-13: WMIC unavailable; SKIPPING check with warning")
        log("        (operator should have killed orphans manually)")
        return

    # Build set of PIDs to exclude: self + anything descended from self.
    excluded = {my_pid}
    # Iterate to a fixed point — child of child of self also excluded.
    changed = True
    while changed:
        changed = False
        for pid, ppid in procs:
            if ppid in excluded and pid not in excluded:
                excluded.add(pid)
                changed = True

    orphans = [pid for pid, _ in procs if pid not in excluded]
    if orphans:
        fail(f"STD-13 violation: orphan python.exe processes alive: "
             f"{orphans}. Kill them and re-run.")
    log(f"STD-13: clean ({len(procs)} python procs total, all are "
        f"this script or its descendants)")


# ------------------------------------------------------------------
def std08_backup() -> str:
    if not os.path.exists(DB_PATH):
        fail(f"DB not found at {DB_PATH}")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(
        "data", f"kintell.db.backup_pre_4_3_5_{ts}"
    )
    log(f"STD-08: copying {DB_PATH} -> {backup_path}")
    shutil.copy2(DB_PATH, backup_path)
    src_size = os.path.getsize(DB_PATH)
    dst_size = os.path.getsize(backup_path)
    if src_size != dst_size:
        fail(f"STD-08: backup size mismatch "
             f"(src={src_size}, dst={dst_size})")
    log(f"STD-08: backup OK ({src_size:,} bytes)")
    return backup_path


def get_column_names(cur: sqlite3.Cursor, table: str) -> list:
    cur.execute(f"PRAGMA table_info({table})")
    return [row[1] for row in cur.fetchall()]


def apply_migration(backup_path: str) -> dict:
    log(f"opening {DB_PATH} read-write")
    conn = sqlite3.connect(DB_PATH, isolation_level=None)
    cur = conn.cursor()

    try:
        log("BEGIN IMMEDIATE")
        cur.execute("BEGIN IMMEDIATE")

        log("re-verifying pre-conditions")
        cols_before = get_column_names(cur, TABLE)
        if not cols_before:
            raise RuntimeError(f"{TABLE} not found in DB")
        if len(cols_before) != 17:
            raise RuntimeError(
                f"unexpected pre-migration column count: "
                f"{len(cols_before)} (expected 17). "
                f"Cols: {cols_before}"
            )

        cur.execute(f"SELECT COUNT(*) FROM {TABLE}")
        (row_count,) = cur.fetchone()
        if row_count != 0:
            raise RuntimeError(
                f"{TABLE} is NOT empty (rows={row_count}). "
                f"OI-05 is stale; re-plan before mutating."
            )

        existing = set(cols_before)
        overlap = [c for c, _ in NEW_COLUMNS if c in existing]
        if overlap:
            raise RuntimeError(
                f"{len(overlap)} target columns already exist: "
                f"{overlap}. Migration not clean — re-plan."
            )
        log(f"  pre-check OK: 17 cols, 0 rows, no overlap")

        log("applying 7 ALTER TABLE ADD COLUMN statements")
        for col_name, col_type in NEW_COLUMNS:
            stmt = (f"ALTER TABLE {TABLE} "
                    f"ADD COLUMN {col_name} {col_type}")
            log(f"  {stmt}")
            cur.execute(stmt)

        cols_after = get_column_names(cur, TABLE)
        if len(cols_after) != EXPECTED_FINAL_COLUMN_COUNT:
            raise RuntimeError(
                f"post-ALTER column count "
                f"{len(cols_after)} != expected "
                f"{EXPECTED_FINAL_COLUMN_COUNT}"
            )
        for col_name, _ in NEW_COLUMNS:
            if col_name not in cols_after:
                raise RuntimeError(
                    f"post-ALTER: {col_name} missing"
                )
        log(f"  post-ALTER shape OK ({len(cols_after)} cols)")

        before_json = json.dumps({"columns": cols_before})
        after_json = json.dumps({
            "columns": cols_after,
            "added": [c for c, _ in NEW_COLUMNS],
            "backup": os.path.basename(backup_path),
        })
        log("inserting audit_log row")
        cur.execute(
            "INSERT INTO audit_log "
            "(actor, action, subject_type, subject_id, "
            " before_json, after_json, reason) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (AUDIT_ACTOR, AUDIT_ACTION, AUDIT_SUBJECT_TYPE,
             AUDIT_SUBJECT_ID, before_json, after_json, AUDIT_REASON),
        )
        audit_id = cur.lastrowid
        log(f"  audit_log.audit_id = {audit_id}")

        log("COMMIT")
        cur.execute("COMMIT")

        return {
            "cols_before": cols_before,
            "cols_after": cols_after,
            "audit_id": audit_id,
            "backup_path": backup_path,
        }

    except Exception as e:
        log(f"EXCEPTION: {e!r} -- ROLLBACK")
        try:
            cur.execute("ROLLBACK")
        except Exception:
            pass
        raise
    finally:
        conn.close()


def post_mutation_validation(result: dict) -> None:
    log("post-mutation validation (read-only)")
    uri = f"file:{DB_PATH}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    cur = conn.cursor()
    try:
        cols = get_column_names(cur, TABLE)
        if len(cols) != EXPECTED_FINAL_COLUMN_COUNT:
            fail(f"validation: column count "
                 f"{len(cols)} != {EXPECTED_FINAL_COLUMN_COUNT}")
        for col_name, _ in NEW_COLUMNS:
            if col_name not in cols:
                fail(f"validation: {col_name} missing")
        log(f"  shape OK ({len(cols)} cols, all 7 new present)")

        cur.execute(f"SELECT COUNT(*) FROM {TABLE}")
        (n,) = cur.fetchone()
        if n != 0:
            fail(f"validation: {TABLE} row count {n} != 0")
        log(f"  rows OK (still 0 — DEC-11)")

        cur.execute(
            "SELECT audit_id, actor, action, subject_type, "
            "subject_id, occurred_at FROM audit_log "
            "WHERE audit_id = ?",
            (result["audit_id"],),
        )
        row = cur.fetchone()
        if not row:
            fail(f"validation: audit_log row "
                 f"{result['audit_id']} not found")
        log(f"  audit_log OK: {row}")

        print()
        print("Final service_catchment_cache schema:")
        cur.execute(f"PRAGMA table_info({TABLE})")
        new_set = {c for c, _ in NEW_COLUMNS}
        for cid, name, ctype, notnull, dflt, pk in cur.fetchall():
            marker = "  <-- NEW" if name in new_set else ""
            print(f"  {cid:2}  {name:<28} {ctype:<8}{marker}")
    finally:
        conn.close()


def main() -> None:
    print("=" * 72)
    print("migrate_4_3_5_service_catchment_cache.py v2")
    print(f"started      : {datetime.now().isoformat()}")
    print(f"target db    : {os.path.abspath(DB_PATH)}")
    print(f"target table : {TABLE}")
    print(f"adding cols  : {[c for c, _ in NEW_COLUMNS]}")
    print("=" * 72)
    print()

    std13_self_check()
    backup_path = std08_backup()

    try:
        result = apply_migration(backup_path)
    except Exception as e:
        print()
        print("=" * 72)
        print(f"MIGRATION FAILED: {e!r}")
        print(f"DB rolled back. Backup preserved at: {backup_path}")
        print("=" * 72)
        sys.exit(2)

    post_mutation_validation(result)

    print()
    print("=" * 72)
    print("MIGRATION SUCCESS")
    print(f"audit_id     : {result['audit_id']}")
    print(f"backup       : {result['backup_path']}")
    print(f"cols before  : {len(result['cols_before'])}")
    print(f"cols after   : {len(result['cols_after'])}")
    print(f"finished     : {datetime.now().isoformat()}")
    print("=" * 72)


if __name__ == "__main__":
    main()
