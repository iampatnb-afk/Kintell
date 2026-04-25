"""
test_rename.py  v1
──────────────────
End-to-end test of the group rename flow. Hits the live
review_server.py on :8001 via HTTP so we exercise the endpoint
contract, not just the underlying Python function.

Uses Sparrow gid 1887 (confirmed by the migration snapshot).

Steps:
  1. GET  /api/group/1887               → current state
  2. POST /api/group/1887/rename with display_name='Sparrow'
  3. GET again                          → effective_name should flip
  4. POST /api/group/1887/rename with display_name=null (clear)
  5. GET again                          → effective_name back to canonical
  6. Read audit_log directly for rename_group entries on this group

Run from project root with review_server.py running on :8001.
"""

import json
import sqlite3
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE_URL = "http://localhost:8001"
DB_PATH = Path("data/kintell.db")
SPARROW_GID = 1887


def section(title):
    print()
    print("=" * 72)
    print(f"  {title}")
    print("=" * 72)


def http_request(method, path, body=None):
    url = BASE_URL + path
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else str(e)
        return e.code, raw
    except urllib.error.URLError as e:
        return None, f"<connection failed: {e.reason}>"


def show_group(label):
    status, raw = http_request("GET", f"/api/group/{SPARROW_GID}")
    print(f"[{label}]  HTTP {status}")
    try:
        parsed = json.loads(raw)
    except Exception as e:
        print(f"  PARSE FAILED: {e}")
        print(f"  raw body: {raw[:400]}")
        return
    if not parsed.get("ok"):
        print(f"  NOT OK: {parsed.get('msg')}")
        return
    g = parsed.get("group", {}) or {}
    print(f"  group_id       : {g.get('group_id')}")
    print(f"  canonical_name : {g.get('canonical_name')}")
    print(f"  display_name   : {g.get('display_name')!r}")
    print(f"  effective_name : {g.get('effective_name')!r}")


def post_rename(display_name, label):
    status, raw = http_request(
        "POST", f"/api/group/{SPARROW_GID}/rename",
        body={"display_name": display_name, "actor": "patrick"},
    )
    print(f"[{label}]  HTTP {status}")
    try:
        print(json.dumps(json.loads(raw), indent=2, default=str))
    except Exception:
        print(f"  raw body: {raw[:400]}")


def main():
    if not DB_PATH.exists():
        print(f"DB not found at {DB_PATH.resolve()}. Run from project root.")
        sys.exit(1)

    section("1. Current state (before any rename)")
    show_group("start")

    section("2. POST rename → 'Sparrow'")
    post_rename("Sparrow", "rename")

    section("3. After rename")
    show_group("renamed")

    section("4. POST rename → null (clear)")
    post_rename(None, "clear")

    section("5. After clear")
    show_group("cleared")

    section("6. rename_group audit trail for this group")
    con = sqlite3.connect(DB_PATH)
    try:
        rows = con.execute(
            "SELECT audit_id, actor, occurred_at, before_json, after_json "
            "FROM audit_log "
            "WHERE action='rename_group' AND subject_id=? "
            "ORDER BY audit_id DESC LIMIT 10",
            (SPARROW_GID,),
        ).fetchall()
        if not rows:
            print("  (none)")
        for aid, actor, at, bjson, ajson in rows:
            try:
                b = json.loads(bjson or "{}")
            except Exception:
                b = {}
            try:
                a = json.loads(ajson or "{}")
            except Exception:
                a = {}
            print(f"  audit_id={aid}  actor={actor}  at={at}")
            print(f"    before: display_name={b.get('display_name')!r}")
            print(f"    after : display_name={a.get('display_name')!r}")
    finally:
        con.close()

    section("RESULT")
    print("If you saw:")
    print("  - start  : display_name=None, effective=canonical legal name")
    print("  - renamed: display_name='Sparrow', effective='Sparrow'")
    print("  - cleared: display_name=None, effective=canonical again")
    print("  - audit  : two rename_group rows (set, then clear)")
    print("...then the rename flow is working end-to-end.")


if __name__ == "__main__":
    main()
