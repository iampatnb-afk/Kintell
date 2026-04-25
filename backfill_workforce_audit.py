#!/usr/bin/env python3
# ─────────────────────────────────────────────────────────────────────
# backfill_workforce_audit.py  v1
# Backfills the audit_log row that should have been written by
# add_workforce_assumptions.py v2 but failed due to a previously
# undiscovered NOT NULL column (audit_log.subject_type).
#
# Schema confirmed (PRAGMA table_info(audit_log)):
#   audit_id      INTEGER PK auto
#   actor         TEXT  NOT NULL
#   action        TEXT  NOT NULL
#   subject_type  TEXT  NOT NULL
#   subject_id    INTEGER NOT NULL  (stored as TEXT in practice — affinity)
#   before_json   TEXT  nullable
#   after_json    TEXT  nullable
#   reason        TEXT  nullable
#   occurred_at   TEXT  nullable (default datetime('now'))
#
# Convention from existing rows: subject_type='table',
# subject_id='<table_name>' (TEXT in INTEGER-affinity column, matching
# row 121 written by ingest_ncver_completions.py).
#
# Idempotent: skips if a matching row already exists.
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations
import sqlite3, shutil, sys, json
from datetime import datetime
from pathlib import Path

DB = Path("data/kintell.db")
NOW = datetime.now()
TS = NOW.strftime("%Y%m%d_%H%M%S")
BACKUP_PATH = Path("data") / f"kintell.db.backup_pre_audit_backfill_{TS}"

ACTOR        = "add_workforce_assumptions.py v2"
ACTION       = "data_seed"
SUBJECT_TYPE = "table"
SUBJECT_ID   = "model_assumptions"
BEFORE_JSON  = json.dumps({"missing_keys": ["educator_ratio_ldc_blended", "educator_ratio_oshc"]})
AFTER_JSON   = json.dumps({"inserted": ["educator_ratio_ldc_blended", "educator_ratio_oshc"], "skipped": []})
REASON       = (
    "Phase 1 pre-step backfill. v2 of add_workforce_assumptions.py committed "
    "both rows to model_assumptions successfully but the audit_log insert "
    "hit a NOT NULL violation on subject_type (column not in the script's "
    "payload). This script writes the missing audit row to maintain audit-trail "
    "completeness."
)

def main() -> int:
    if not DB.exists():
        print(f"ERROR: {DB} not found. Run from repo root.", file=sys.stderr)
        return 2

    print(f"[1/4] Backing up DB -> {BACKUP_PATH}")
    shutil.copy2(DB, BACKUP_PATH)

    con = sqlite3.connect(DB)
    cur = con.cursor()

    existing = cur.execute(
        "SELECT audit_id FROM audit_log "
        "WHERE actor = ? AND action = ? AND subject_type = ? AND subject_id = ?",
        (ACTOR, ACTION, SUBJECT_TYPE, SUBJECT_ID),
    ).fetchone()
    if existing:
        print(f"[2/4] audit_log row already present (audit_id={existing[0]}). Nothing to do.")
        total = cur.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0]
        print(f"[3/4] audit_log total rows: {total}")
        print("[4/4] Skipped (idempotent).")
        con.close()
        return 0

    nowiso = NOW.isoformat(timespec="seconds")
    cur.execute(
        "INSERT INTO audit_log "
        "(actor, action, subject_type, subject_id, before_json, after_json, reason, occurred_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (ACTOR, ACTION, SUBJECT_TYPE, SUBJECT_ID, BEFORE_JSON, AFTER_JSON, REASON, nowiso),
    )
    new_id = cur.lastrowid
    con.commit()
    print(f"[2/4] Inserted audit_log row (audit_id={new_id})")

    row = cur.execute(
        "SELECT audit_id, actor, action, subject_type, subject_id, occurred_at "
        "FROM audit_log WHERE audit_id = ?",
        (new_id,),
    ).fetchone()
    print("[3/4] Validation:")
    print(f"      audit_id     = {row[0]}")
    print(f"      actor        = {row[1]}")
    print(f"      action       = {row[2]}")
    print(f"      subject_type = {row[3]}")
    print(f"      subject_id   = {row[4]}")
    print(f"      occurred_at  = {row[5]}")

    total = cur.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0]
    print(f"[4/4] audit_log total rows: {total}")
    con.close()

    print("\nDone.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
