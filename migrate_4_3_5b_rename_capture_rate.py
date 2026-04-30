"""
migrate_4_3_5b_rename_capture_rate.py v1
=========================================
Sub-pass 4.3.5b — naming correction follow-on to 4.3.5.

Renames `capture_rate` to `demand_share_state` on
`service_catchment_cache`. Resolves the design-doc-vs-formula-list
naming clash surfaced during Layer 2.5 framing:

  - "Participation Rate" is a behavioural input
    (Children_in_Childcare / Children_0_5) — calibrated per-SA2
    via catchment_calibration.py and stored as `calibrated_rate`.
  - "Demand share state" is a relative-positioning OUTPUT metric
    (this SA2's adjusted_demand / sum across all SA2s in same
    state). It is NOT a participation rate.

Calling the latter "capture_rate" invited circular-logic confusion
because the same English-language term is also widely used for the
former. Rename now, before Layer 2.5 populates and before the term
appears in any V1 UI surface.

STD-30 pre-mutation discipline:
  1. STD-13 self-check (orphan python.exe, WMIC-via-Get-CimInstance
     fallback to "skip with warning" — same pattern as 4.3.5 v2).
  2. STD-08 backup of data/kintell.db.
  3. BEGIN IMMEDIATE; re-verify pre-conditions inside the txn.
  4. ALTER TABLE ... RENAME COLUMN ...
  5. INSERT into audit_log per STD-11.
  6. COMMIT.
  7. Post-mutation validation (read-only).

Idempotent-safe: if `capture_rate` is already renamed (e.g. on
re-run), step 3 detects this and ROLLBACKs cleanly with exit 2.

Usage (from repo root):
    python migrate_4_3_5b_rename_capture_rate.py
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
OLD_COLUMN = "capture_rate"
NEW_COLUMN = "demand_share_state"

AUDIT_ACTOR = "layer4_3_5b_apply"
AUDIT_ACTION = "service_catchment_cache_rename_column_v1"
AUDIT_SUBJECT_TYPE = "service_catchment_cache"
AUDIT_SUBJECT_ID = 0
AUDIT_REASON = (
    "Layer 4.3 sub-pass 4.3.5b: rename column "
    "capture_rate -> demand_share_state on "
    "service_catchment_cache. Naming correction follow-on to "
    "4.3.5 (commit 8e944d9), before Layer 2.5 populator runs. "
    "Resolves a naming clash between the design doc's "
    "share-of-state-demand definition and the formula list's "
    "participation-rate definition. The column stores the former "
    "(an OUTPUT relative-positioning metric); the latter is a "
    "behavioural INPUT and lives in calibrated_rate. Table is "
    "still empty pre-rename so no data preservation required. "
    "Backup taken pre-migration per STD-08."
)


def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def fail(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


# ------------------------------------------------------------------
# STD-13 self-check
# ------------------------------------------------------------------
def _query_python_processes_via_wmic() -> list:
    """Return list of (pid, parent_pid). None if WMIC unavailable."""
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
    log("STD-13: scanning for orphan python.exe processes (WMIC)")
    my_pid = os.getpid()
    procs = _query_python_processes_via_wmic()

    if procs is None:
        log("STD-13: WMIC unavailable; SKIPPING check with warning")
        log("        (operator should have killed orphans manually)")
        return

    excluded = {my_pid}
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
        "data", f"kintell.db.backup_pre_4_3_5b_{ts}"
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
        if OLD_COLUMN not in cols_before:
            raise RuntimeError(
                f"pre-check: {OLD_COLUMN!r} not present in {TABLE}. "
                f"Either 4.3.5 was not applied or 4.3.5b already "
                f"ran. Cols: {cols_before}"
            )
        if NEW_COLUMN in cols_before:
            raise RuntimeError(
                f"pre-check: {NEW_COLUMN!r} already exists in "
                f"{TABLE}. Migration is not idempotent under this "
                f"state — re-plan."
            )

        cur.execute(f"SELECT COUNT(*) FROM {TABLE}")
        (row_count,) = cur.fetchone()
        if row_count != 0:
            # Rename works on populated tables too, but per OI-05 we
            # expect 0 here. Surface as a warning, not a hard fail.
            log(f"  WARNING: {TABLE} has {row_count} rows "
                f"(expected 0 per OI-05). Proceeding because "
                f"RENAME COLUMN preserves data.")
        log(f"  pre-check OK: {OLD_COLUMN!r} present, "
            f"{NEW_COLUMN!r} absent, rows={row_count}")

        stmt = (f"ALTER TABLE {TABLE} "
                f"RENAME COLUMN {OLD_COLUMN} TO {NEW_COLUMN}")
        log(f"applying: {stmt}")
        cur.execute(stmt)

        cols_after = get_column_names(cur, TABLE)
        if OLD_COLUMN in cols_after:
            raise RuntimeError(
                f"post-rename: {OLD_COLUMN!r} still present"
            )
        if NEW_COLUMN not in cols_after:
            raise RuntimeError(
                f"post-rename: {NEW_COLUMN!r} not present"
            )
        if len(cols_after) != len(cols_before):
            raise RuntimeError(
                f"post-rename: column count changed "
                f"({len(cols_before)} -> {len(cols_after)})"
            )
        log(f"  post-rename shape OK ({len(cols_after)} cols, "
            f"rename in place)")

        before_json = json.dumps({
            "columns": cols_before,
            "renamed_from": OLD_COLUMN,
        })
        after_json = json.dumps({
            "columns": cols_after,
            "renamed_to": NEW_COLUMN,
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
            "row_count_at_migration": row_count,
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
        if OLD_COLUMN in cols:
            fail(f"validation: {OLD_COLUMN!r} still present")
        if NEW_COLUMN not in cols:
            fail(f"validation: {NEW_COLUMN!r} missing")
        log(f"  shape OK ({len(cols)} cols, rename verified)")

        cur.execute(f"SELECT COUNT(*) FROM {TABLE}")
        (n,) = cur.fetchone()
        if n != result["row_count_at_migration"]:
            fail(f"validation: row count drift "
                 f"({result['row_count_at_migration']} -> {n})")
        log(f"  rows OK ({n}, unchanged from migration)")

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
        print(f"Final {TABLE} schema:")
        cur.execute(f"PRAGMA table_info({TABLE})")
        for cid, name, ctype, notnull, dflt, pk in cur.fetchall():
            marker = "  <-- RENAMED" if name == NEW_COLUMN else ""
            print(f"  {cid:2}  {name:<28} {ctype:<8}{marker}")
    finally:
        conn.close()


def main() -> None:
    print("=" * 72)
    print("migrate_4_3_5b_rename_capture_rate.py v1")
    print(f"started      : {datetime.now().isoformat()}")
    print(f"target db    : {os.path.abspath(DB_PATH)}")
    print(f"target table : {TABLE}")
    print(f"rename       : {OLD_COLUMN!r} -> {NEW_COLUMN!r}")
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
    print(f"renamed      : {OLD_COLUMN!r} -> {NEW_COLUMN!r}")
    print(f"finished     : {datetime.now().isoformat()}")
    print("=" * 72)


if __name__ == "__main__":
    main()
