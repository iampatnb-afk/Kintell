"""
group_labels.py  v1
────────────────────────────────────────────────────────────────
Group-level rename flow. Sets groups.display_name so the
operator-facing label is independent of the canonical legal entity
name. A NULL display_name means the UI falls back to canonical_name.

  rename(group_id, display_name, actor)
    - Updates groups.display_name (stripped)
    - Empty / None / whitespace-only clears the field
    - Logs rename_group audit entry with before/after values
    - Idempotent: no-op and success when display_name unchanged
    - No uniqueness enforcement (per decision: two legitimately
      separate groups can share a trading name)

  clear_name(group_id, actor)
    - Convenience wrapper around rename(group_id, None, actor)

  get_group(group_id)
    - Returns {group_id, canonical_name, display_name, effective_name,
      is_active, parent_entity_id, ownership_type}
    - effective_name = display_name or canonical_name (never null)

All write ops are atomic and audit-logged.

CLI:
  python group_labels.py show   <group_id>
  python group_labels.py rename <group_id> "New Name" [--actor NAME]
  python group_labels.py clear  <group_id> [--actor NAME]

Importable for review_server.py:
  from group_labels import rename, clear_name, get_group
"""

import argparse
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "data" / "kintell.db"

MAX_DISPLAY_NAME_LEN = 200


# ─── Utilities ─────────────────────────────────────────────────────

def _connect():
    if not DB_PATH.exists():
        raise RuntimeError(f"Database not found: {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _log_audit(conn, actor, action, subject_type, subject_id,
               before=None, after=None, reason=None):
    conn.execute(
        "INSERT INTO audit_log "
        "(actor, action, subject_type, subject_id, "
        " before_json, after_json, reason) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            actor, action, subject_type, subject_id,
            json.dumps(before) if before is not None else None,
            json.dumps(after)  if after  is not None else None,
            reason,
        ),
    )


def _group_row(conn, group_id):
    return conn.execute(
        "SELECT group_id, canonical_name, display_name, is_active, "
        "       parent_entity_id, ownership_type "
        "FROM groups WHERE group_id = ?",
        (group_id,),
    ).fetchone()


def _row_to_dict(row):
    if row is None:
        return None
    gid, canonical, display, is_active, parent_eid, ownership = row
    return {
        "group_id":         gid,
        "canonical_name":   canonical,
        "display_name":     display,
        "effective_name":   display or canonical,
        "is_active":        is_active,
        "parent_entity_id": parent_eid,
        "ownership_type":   ownership,
    }


# ─── Primary operations ────────────────────────────────────────────

def get_group(group_id):
    conn = _connect()
    try:
        row = _group_row(conn, group_id)
        if row is None:
            return {"ok": False, "msg": f"Group {group_id} not found"}
        return {"ok": True, "group": _row_to_dict(row)}
    finally:
        conn.close()


def rename(group_id, display_name, actor="patrick"):
    """
    Set groups.display_name.

    None, empty string, or whitespace-only clears the field (UI falls
    back to canonical_name).

    Returns {ok, msg, group}. Idempotent; audit-logged.
    """
    new_name = None
    if display_name is not None and str(display_name).strip():
        new_name = str(display_name).strip()
        if len(new_name) > MAX_DISPLAY_NAME_LEN:
            return {"ok": False,
                    "msg": f"display_name too long (max {MAX_DISPLAY_NAME_LEN})"}

    conn = _connect()
    try:
        row = _group_row(conn, group_id)
        if row is None:
            return {"ok": False, "msg": f"Group {group_id} not found"}

        before = _row_to_dict(row)
        old_name = before["display_name"]

        if old_name == new_name:
            return {"ok": True, "msg": "no change (idempotent)",
                    "group": before}

        conn.execute("BEGIN")
        conn.execute(
            "UPDATE groups SET display_name = ?, "
            "                  updated_at = datetime('now') "
            "WHERE group_id = ?",
            (new_name, group_id),
        )
        after = _row_to_dict(_group_row(conn, group_id))

        _log_audit(
            conn, actor,
            "rename_group",
            "group", group_id,
            before={"display_name":   old_name,
                    "canonical_name": before["canonical_name"]},
            after ={"display_name":   new_name,
                    "canonical_name": after["canonical_name"]},
        )

        conn.commit()

        if new_name:
            human = (f"{before['canonical_name']}: "
                     f"display name set to '{new_name}'")
        else:
            human = (f"{before['canonical_name']}: "
                     f"display name cleared (will show as canonical)")

        return {"ok": True, "msg": human, "group": after}
    except Exception as e:
        conn.rollback()
        return {"ok": False, "msg": f"Error: {e}"}
    finally:
        conn.close()


def clear_name(group_id, actor="patrick"):
    """Convenience — clear display_name so UI falls back to canonical_name."""
    return rename(group_id, None, actor=actor)


# ─── CLI ───────────────────────────────────────────────────────────

def _cli():
    p = argparse.ArgumentParser(description="Group rename / display-name tool.")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("show")
    sp.add_argument("group_id", type=int)

    sp = sub.add_parser("rename")
    sp.add_argument("group_id", type=int)
    sp.add_argument("display_name")
    sp.add_argument("--actor", default="patrick")

    sp = sub.add_parser("clear")
    sp.add_argument("group_id", type=int)
    sp.add_argument("--actor", default="patrick")

    args = p.parse_args()

    if args.cmd == "show":
        r = get_group(args.group_id)
    elif args.cmd == "rename":
        r = rename(args.group_id, args.display_name, args.actor)
    elif args.cmd == "clear":
        r = clear_name(args.group_id, args.actor)
    else:
        p.print_help(); sys.exit(1)

    print(json.dumps(r, indent=2, default=str))
    sys.exit(0 if r.get("ok") else 1)


if __name__ == "__main__":
    _cli()
