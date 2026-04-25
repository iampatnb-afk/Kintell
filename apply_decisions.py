"""
apply_decisions.py
────────────────────────────────────────────────────────────────
Performs actual group merges based on accepted link_candidate rows.

Core operations (all logged to audit_log):
  accept(candidate_id, actor)
    - moves every entity in the source group to the canonical group
    - re-points any brand whose group_id = source → canonical
    - sets source group is_active = 0 (soft-delete, audit-preserving)
    - marks candidate status = 'accepted'
    - writes evidence rows for each affected entity's group_id change

  reject(candidate_id, actor, reason)
    - marks candidate status = 'rejected'
    - records reason; no graph mutation

  park(candidate_id, actor, reason)
    - marks candidate status = 'parked' (show in filter, skip auto-processing)

  reverse(audit_id, actor)
    - reads the before_json of a previous accept action
    - restores the source group and moves entities back
    - records a reverse entry in audit_log

All operations are atomic — wrapped in BEGIN/COMMIT, rolled back on error.
All operations are idempotent — double-accepting a candidate no-ops safely.

CLI usage:
  python apply_decisions.py accept <candidate_id> [--actor NAME]
  python apply_decisions.py reject <candidate_id> [--reason TEXT]
  python apply_decisions.py park   <candidate_id> [--reason TEXT]
  python apply_decisions.py bulk-accept --min-confidence 0.9 [--brand NAME]
  python apply_decisions.py status
  python apply_decisions.py reverse <audit_id>

Importable for use by review_server.py:
  from apply_decisions import accept, reject, park, reverse, get_status
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "data" / "kintell.db"


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


def _get_candidate(conn, candidate_id):
    row = conn.execute(
        "SELECT candidate_id, link_type, from_type, from_id, "
        "       to_type, to_id, composite_confidence, "
        "       evidence_json, status "
        "  FROM link_candidates WHERE candidate_id = ?",
        (candidate_id,),
    ).fetchone()
    if not row:
        return None
    return {
        "candidate_id": row[0], "link_type": row[1],
        "from_type": row[2], "from_id": row[3],
        "to_type":   row[4], "to_id":   row[5],
        "composite_confidence": row[6],
        "evidence": json.loads(row[7] or "{}"),
        "status": row[8],
    }


def _group_snapshot(conn, group_id):
    g = conn.execute(
        "SELECT group_id, canonical_name, is_active "
        "  FROM groups WHERE group_id = ?", (group_id,)
    ).fetchone()
    if not g:
        return None
    entities = [r[0] for r in conn.execute(
        "SELECT entity_id FROM entities WHERE group_id = ?",
        (group_id,)
    ).fetchall()]
    brands = [r[0] for r in conn.execute(
        "SELECT brand_id FROM brands WHERE group_id = ?",
        (group_id,)
    ).fetchall()]
    return {
        "group_id":       g[0],
        "canonical_name": g[1],
        "is_active":      g[2],
        "entity_ids":     entities,
        "brand_ids":      brands,
    }


# ─── Primary operations ────────────────────────────────────────────

def accept(candidate_id, actor="patrick"):
    """
    Merge the source group into the canonical group.
    Returns dict: {ok, msg, candidate_id, entities_moved, brands_moved}
    """
    conn = _connect()
    try:
        cand = _get_candidate(conn, candidate_id)
        if not cand:
            return {"ok": False, "msg": f"Candidate {candidate_id} not found"}
        if cand["status"] == "accepted":
            return {"ok": True, "msg": "Already accepted (no-op)",
                    "candidate_id": candidate_id, "entities_moved": 0,
                    "brands_moved": 0}
        if cand["status"] == "rejected":
            return {"ok": False,
                    "msg": "Candidate was rejected; reverse the rejection first"}
        if cand["link_type"] != "group_merge":
            return {"ok": False,
                    "msg": f"Only group_merge supported, got {cand['link_type']}"}

        src_gid  = cand["from_id"]
        dest_gid = cand["to_id"]

        if src_gid == dest_gid:
            return {"ok": False, "msg": "Source equals destination"}

        src_before  = _group_snapshot(conn, src_gid)
        dest_before = _group_snapshot(conn, dest_gid)

        if src_before is None:
            return {"ok": False, "msg": f"Source group {src_gid} not found"}
        if dest_before is None:
            return {"ok": False, "msg": f"Destination group {dest_gid} not found"}

        conn.execute("BEGIN")

        # Move entities
        conn.execute(
            "UPDATE entities SET group_id = ?, updated_at = datetime('now') "
            "WHERE group_id = ?",
            (dest_gid, src_gid),
        )
        entities_moved = len(src_before["entity_ids"])

        # Evidence for each moved entity
        for eid in src_before["entity_ids"]:
            conn.execute(
                "INSERT INTO evidence "
                "(subject_type, subject_id, field_name, asserted_value, "
                " source_type, confidence, asserted_by, notes) "
                "VALUES ('entity', ?, 'group_id', ?, 'manual_link', 1.0, ?, ?)",
                (eid, str(dest_gid), actor,
                 f"Merged from group {src_gid} via candidate {candidate_id}")
            )

        # Re-point brands
        conn.execute(
            "UPDATE brands SET group_id = ?, updated_at = datetime('now') "
            "WHERE group_id = ?",
            (dest_gid, src_gid),
        )
        brands_moved = len(src_before["brand_ids"])

        # Soft-delete source group
        conn.execute(
            "UPDATE groups SET is_active = 0, "
            "                  deactivated_at = datetime('now'), "
            "                  updated_at = datetime('now') "
            "WHERE group_id = ?",
            (src_gid,),
        )

        # Mark candidate accepted
        conn.execute(
            "UPDATE link_candidates "
            "   SET status = 'accepted', "
            "       reviewed_at = datetime('now'), reviewed_by = ? "
            " WHERE candidate_id = ?",
            (actor, candidate_id),
        )

        # Audit
        _log_audit(conn, actor, "accept_merge",
                   "link_candidate", candidate_id,
                   before={"source_group": src_before,
                           "dest_group":   dest_before,
                           "candidate":    cand},
                   after={"dest_group_id": dest_gid,
                          "entities_moved": entities_moved,
                          "brands_moved":   brands_moved})

        conn.commit()
        return {
            "ok": True,
            "msg": f"Merged group {src_gid} → {dest_gid}",
            "candidate_id": candidate_id,
            "entities_moved": entities_moved,
            "brands_moved":   brands_moved,
            "source_group":   src_before["canonical_name"],
            "dest_group":     dest_before["canonical_name"],
        }
    except Exception as e:
        conn.rollback()
        return {"ok": False, "msg": f"Error: {e}"}
    finally:
        conn.close()


def reject(candidate_id, actor="patrick", reason=None):
    conn = _connect()
    try:
        cand = _get_candidate(conn, candidate_id)
        if not cand:
            return {"ok": False, "msg": f"Candidate {candidate_id} not found"}
        if cand["status"] == "rejected":
            return {"ok": True, "msg": "Already rejected (no-op)"}
        if cand["status"] == "accepted":
            return {"ok": False,
                    "msg": "Cannot reject an accepted candidate; reverse first"}

        conn.execute("BEGIN")
        conn.execute(
            "UPDATE link_candidates "
            "   SET status = 'rejected', "
            "       reviewed_at = datetime('now'), reviewed_by = ?, "
            "       review_note = ? "
            " WHERE candidate_id = ?",
            (actor, reason, candidate_id),
        )
        _log_audit(conn, actor, "reject_merge",
                   "link_candidate", candidate_id,
                   before={"candidate": cand},
                   after={"status": "rejected"},
                   reason=reason)
        conn.commit()
        return {"ok": True,
                "msg": f"Candidate {candidate_id} rejected",
                "candidate_id": candidate_id}
    except Exception as e:
        conn.rollback()
        return {"ok": False, "msg": f"Error: {e}"}
    finally:
        conn.close()


def park(candidate_id, actor="patrick", reason=None):
    conn = _connect()
    try:
        cand = _get_candidate(conn, candidate_id)
        if not cand:
            return {"ok": False, "msg": f"Candidate {candidate_id} not found"}
        if cand["status"] in ("accepted", "rejected"):
            return {"ok": False,
                    "msg": f"Cannot park a {cand['status']} candidate"}

        conn.execute("BEGIN")
        conn.execute(
            "UPDATE link_candidates "
            "   SET status = 'parked', "
            "       reviewed_at = datetime('now'), reviewed_by = ?, "
            "       review_note = ? "
            " WHERE candidate_id = ?",
            (actor, reason, candidate_id),
        )
        _log_audit(conn, actor, "park_merge",
                   "link_candidate", candidate_id,
                   before={"candidate": cand},
                   after={"status": "parked"},
                   reason=reason)
        conn.commit()
        return {"ok": True,
                "msg": f"Candidate {candidate_id} parked",
                "candidate_id": candidate_id}
    except Exception as e:
        conn.rollback()
        return {"ok": False, "msg": f"Error: {e}"}
    finally:
        conn.close()


def reverse(audit_id, actor="patrick"):
    """Reverse a previous accept_merge action by its audit_id."""
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT audit_id, action, subject_type, subject_id, "
            "       before_json, after_json "
            "  FROM audit_log WHERE audit_id = ?",
            (audit_id,),
        ).fetchone()
        if not row:
            return {"ok": False, "msg": f"Audit entry {audit_id} not found"}
        if row[1] != "accept_merge":
            return {"ok": False,
                    "msg": f"Can only reverse accept_merge, got {row[1]}"}

        before = json.loads(row[4] or "{}")
        src    = before.get("source_group", {})
        dest   = before.get("dest_group", {})
        cand   = before.get("candidate", {})

        if not src or not dest:
            return {"ok": False, "msg": "Audit entry missing source/dest"}

        src_gid    = src["group_id"]
        dest_gid   = dest["group_id"]
        entity_ids = src.get("entity_ids", [])
        brand_ids  = src.get("brand_ids", [])
        cand_id    = cand.get("candidate_id")

        conn.execute("BEGIN")

        # Restore source group
        conn.execute(
            "UPDATE groups SET is_active = 1, deactivated_at = NULL, "
            "                  updated_at = datetime('now') "
            "WHERE group_id = ?",
            (src_gid,),
        )

        # Move entities back
        for eid in entity_ids:
            conn.execute(
                "UPDATE entities SET group_id = ?, "
                "                    updated_at = datetime('now') "
                "WHERE entity_id = ?",
                (src_gid, eid),
            )
            conn.execute(
                "INSERT INTO evidence "
                "(subject_type, subject_id, field_name, asserted_value, "
                " source_type, confidence, asserted_by, notes) "
                "VALUES ('entity', ?, 'group_id', ?, 'manual_link', 1.0, ?, ?)",
                (eid, str(src_gid), actor,
                 f"Restored from reversal of audit {audit_id}")
            )

        # Move brands back
        for bid in brand_ids:
            conn.execute(
                "UPDATE brands SET group_id = ?, "
                "                  updated_at = datetime('now') "
                "WHERE brand_id = ?",
                (bid, src_gid),
            )

        # Reset candidate status
        if cand_id:
            conn.execute(
                "UPDATE link_candidates "
                "   SET status = 'pending', reviewed_at = NULL, "
                "       reviewed_by = NULL, review_note = NULL "
                " WHERE candidate_id = ?",
                (cand_id,),
            )

        _log_audit(conn, actor, "reverse_accept",
                   "audit_log", audit_id,
                   before={"reversing": before},
                   after={"source_group_restored": src_gid,
                          "entities_restored": len(entity_ids),
                          "brands_restored":   len(brand_ids)})

        conn.commit()
        return {
            "ok": True,
            "msg": f"Reversed audit {audit_id}: group {src_gid} restored",
            "audit_id": audit_id,
            "entities_restored": len(entity_ids),
            "brands_restored":   len(brand_ids),
        }
    except Exception as e:
        conn.rollback()
        return {"ok": False, "msg": f"Error: {e}"}
    finally:
        conn.close()


def get_status():
    """Summary of review queue state."""
    conn = _connect()
    try:
        by_status = dict(conn.execute(
            "SELECT status, COUNT(*) "
            "  FROM link_candidates WHERE link_type = 'group_merge' "
            " GROUP BY status"
        ).fetchall())

        active_groups = conn.execute(
            "SELECT COUNT(*) FROM groups WHERE is_active = 1"
        ).fetchone()[0]
        total_groups = conn.execute(
            "SELECT COUNT(*) FROM groups"
        ).fetchone()[0]

        audit_count = conn.execute(
            "SELECT COUNT(*) FROM audit_log WHERE action = 'accept_merge'"
        ).fetchone()[0]

        return {
            "ok": True,
            "by_status": by_status,
            "active_groups": active_groups,
            "total_groups":  total_groups,
            "merges_applied": audit_count,
        }
    finally:
        conn.close()


# ─── Bulk ───────────────────────────────────────────────────────────

def bulk_accept(min_confidence=0.9, brand=None, actor="patrick",
                dry_run=False):
    conn = _connect()
    try:
        where = ["link_type = 'group_merge'",
                 "status = 'pending'",
                 "composite_confidence >= ?"]
        params = [min_confidence]
        if brand:
            where.append(
                "LOWER(json_extract(evidence_json,'$.brand')) "
                "= LOWER(?)"
            )
            params.append(brand)
        sql = ("SELECT candidate_id FROM link_candidates "
               "WHERE " + " AND ".join(where) +
               " ORDER BY composite_confidence DESC")
        cand_ids = [r[0] for r in conn.execute(sql, params).fetchall()]
    finally:
        conn.close()

    print(f"Matched {len(cand_ids)} candidates "
          f"(min_conf={min_confidence}, brand={brand or '*'})")
    if dry_run:
        return {"ok": True, "matched": len(cand_ids), "dry_run": True}

    ok = 0
    fail = 0
    for cid in cand_ids:
        res = accept(cid, actor=actor)
        if res.get("ok"):
            ok += 1
        else:
            fail += 1
            print(f"  [!] {cid}: {res.get('msg')}")
    print(f"\nAccepted: {ok}   Failed: {fail}")
    return {"ok": True, "accepted": ok, "failed": fail}


# ─── CLI ────────────────────────────────────────────────────────────

def _cli():
    p = argparse.ArgumentParser(description="Apply review decisions.")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("accept")
    sp.add_argument("candidate_id", type=int)
    sp.add_argument("--actor", default="patrick")

    sp = sub.add_parser("reject")
    sp.add_argument("candidate_id", type=int)
    sp.add_argument("--reason")
    sp.add_argument("--actor", default="patrick")

    sp = sub.add_parser("park")
    sp.add_argument("candidate_id", type=int)
    sp.add_argument("--reason")
    sp.add_argument("--actor", default="patrick")

    sp = sub.add_parser("reverse")
    sp.add_argument("audit_id", type=int)
    sp.add_argument("--actor", default="patrick")

    sp = sub.add_parser("bulk-accept")
    sp.add_argument("--min-confidence", type=float, default=0.9)
    sp.add_argument("--brand")
    sp.add_argument("--actor", default="patrick")
    sp.add_argument("--dry-run", action="store_true")

    sub.add_parser("status")

    args = p.parse_args()

    if args.cmd == "accept":
        r = accept(args.candidate_id, args.actor)
    elif args.cmd == "reject":
        r = reject(args.candidate_id, args.actor, args.reason)
    elif args.cmd == "park":
        r = park(args.candidate_id, args.actor, args.reason)
    elif args.cmd == "reverse":
        r = reverse(args.audit_id, args.actor)
    elif args.cmd == "bulk-accept":
        r = bulk_accept(args.min_confidence, args.brand, args.actor,
                        args.dry_run)
    elif args.cmd == "status":
        r = get_status()
    else:
        p.print_help()
        sys.exit(1)

    print(json.dumps(r, indent=2, default=str))
    sys.exit(0 if r.get("ok") else 1)


if __name__ == "__main__":
    _cli()
