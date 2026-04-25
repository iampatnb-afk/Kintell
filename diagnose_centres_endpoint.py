"""
diagnose_centres_endpoint.py  v2
--------------------------------
Triage helper for the "view centres on each side" bug in review.html.

v2: corrected to the real link_candidates schema.
    link_type='group_merge', from_id = source group, to_id = canonical
    group, confidence in `composite_confidence`, brand inside
    evidence_json (not a column).

Does three things:
  1. Pulls a pending group_merge candidate from link_candidates.
  2. Queries the DB directly for service counts per group.
  3. Calls /api/centres/<group_id> for canonical, source, and a bogus
     id (control) and reports status / content-type / body / JSON shape.

Run from project root with review_server.py listening on :8001.
Read-only.
"""

import json
import sqlite3
import sys
import urllib.error
import urllib.request
from pathlib import Path

DB_PATH = Path("data/kintell.db")
BASE_URL = "http://localhost:8001"


def section(title: str) -> None:
    print()
    print("=" * 72)
    print(f"  {title}")
    print("=" * 72)


def pick_pending_proposal(con: sqlite3.Connection):
    row = con.execute(
        """
        SELECT candidate_id,
               from_id,
               to_id,
               composite_confidence,
               evidence_json
        FROM link_candidates
        WHERE status = 'pending'
          AND link_type = 'group_merge'
        ORDER BY composite_confidence DESC, candidate_id ASC
        LIMIT 1
        """
    ).fetchone()
    if row is None:
        print("No pending group_merge proposals found. Abort.")
        sys.exit(1)
    return row


def count_services_for_group(con: sqlite3.Connection, group_id: int) -> int:
    row = con.execute(
        """
        SELECT COUNT(*)
        FROM services s
        JOIN entities e ON e.entity_id = s.entity_id
        WHERE e.group_id = ?
        """,
        (group_id,),
    ).fetchone()
    return int(row[0])


def group_name(con: sqlite3.Connection, group_id: int) -> str:
    row = con.execute(
        "SELECT canonical_name FROM groups WHERE group_id = ?", (group_id,)
    ).fetchone()
    return row[0] if row else "<not found>"


def hit_endpoint(group_id: int) -> None:
    url = f"{BASE_URL}/api/centres/{group_id}"
    print(f"GET  {url}")
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            status = resp.status
            ctype = resp.headers.get("Content-Type", "<missing>")
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        status = e.code
        ctype = e.headers.get("Content-Type", "<missing>") if e.headers else "<no-headers>"
        raw = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else str(e)
    except urllib.error.URLError as e:
        print(f"  CONNECTION FAILED: {e.reason}")
        print("  -> Is review_server.py running on port 8001?")
        return
    except Exception as e:
        print(f"  UNEXPECTED ERROR: {type(e).__name__}: {e}")
        return

    print(f"  Status       : {status}")
    print(f"  Content-Type : {ctype}")
    print(f"  Body length  : {len(raw)} chars")
    body_preview = raw if len(raw) <= 800 else raw[:800] + f"\n... [{len(raw) - 800} more chars truncated]"
    print("  Body preview :")
    for line in body_preview.splitlines():
        print(f"    {line}")

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"  JSON parse   : FAILED ({e.msg} at char {e.pos})")
        return
    print(f"  JSON parse   : OK  (top-level type = {type(parsed).__name__})")
    if isinstance(parsed, dict):
        print(f"  Top-level keys: {list(parsed.keys())}")
        for k, v in parsed.items():
            if isinstance(v, list):
                first_keys = list(v[0].keys()) if v and isinstance(v[0], dict) else None
                print(f"    - {k}: list of {len(v)} items"
                      + (f"  (first item keys: {first_keys})" if first_keys else ""))
            else:
                print(f"    - {k}: {type(v).__name__}")
    elif isinstance(parsed, list):
        print(f"  List length  : {len(parsed)}")
        if parsed and isinstance(parsed[0], dict):
            print(f"  First item   : keys = {list(parsed[0].keys())}")


def main() -> None:
    if not DB_PATH.exists():
        print(f"DB not found at {DB_PATH.resolve()}. Run from project root.")
        sys.exit(1)

    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row

    section("1. Pick a pending proposal to test against")
    cid, from_id, to_id, conf, ev_raw = pick_pending_proposal(con)
    canonical_gid, source_gid = to_id, from_id  # to_id is canonical per evidence_json schema

    try:
        ev = json.loads(ev_raw) if ev_raw else {}
    except Exception:
        ev = {}
    brand = ev.get("brand", "<no brand in evidence>")

    print(f"candidate_id         : {cid}")
    print(f"source_group_id      : {source_gid}   ({group_name(con, source_gid)})")
    print(f"canonical_group_id   : {canonical_gid}   ({group_name(con, canonical_gid)})")
    print(f"composite_confidence : {conf}")
    print(f"brand (from evidence): {brand}")

    section("2. What the DB says each group has")
    src_count = count_services_for_group(con, source_gid)
    can_count = count_services_for_group(con, canonical_gid)
    print(f"group {source_gid} (source)    : {src_count} services")
    print(f"group {canonical_gid} (canonical): {can_count} services")

    section("3. Live endpoint: canonical group")
    hit_endpoint(canonical_gid)

    section("4. Live endpoint: source group")
    hit_endpoint(source_gid)

    section("5. Live endpoint: deliberately bogus id (control)")
    hit_endpoint(999999999)

    con.close()


if __name__ == "__main__":
    main()
