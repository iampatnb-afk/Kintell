"""
inspect_queue_payload.py  v1
----------------------------
Read-only. Confirms whether /api/queue hands the review UI the field
names it expects (r.from_id, r.to_id, r.from_name, r.to_name,
r.candidate_id, r.review_note).

Also probes /api/centres/undefined to see how the server reacts when
passed the literal string 'undefined' — which would be the failure
path if r.from_id is missing from the queue payload.
"""

import json
import urllib.error
import urllib.request

BASE = "http://localhost:8001"
EXPECTED_ROW_FIELDS = [
    "candidate_id",
    "from_id",
    "to_id",
    "from_name",
    "to_name",
    "confidence",
    "review_note",
]


def section(title: str) -> None:
    print()
    print("=" * 72)
    print(f"  {title}")
    print("=" * 72)


def get(url: str):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, resp.headers.get("Content-Type", ""), resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace") if hasattr(e, "read") else str(e)
        return e.code, (e.headers.get("Content-Type", "") if e.headers else ""), raw
    except urllib.error.URLError as e:
        return None, "", f"<connection failed: {e.reason}>"


def main() -> None:
    section("1. GET /api/queue?status=pending  — field audit")
    status, ctype, raw = get(f"{BASE}/api/queue?status=pending")
    print(f"Status: {status}   Content-Type: {ctype}   Body length: {len(raw)}")
    try:
        parsed = json.loads(raw)
    except Exception as e:
        print(f"JSON parse FAILED: {e}")
        print("Body preview:")
        print(raw[:800])
        return

    print(f"Top-level keys: {list(parsed.keys()) if isinstance(parsed, dict) else '<not dict>'}")
    rows = parsed.get("rows") if isinstance(parsed, dict) else None
    if not isinstance(rows, list) or not rows:
        print("No rows in payload. Dumping top 800 chars:")
        print(raw[:800])
        return

    print(f"Row count: {len(rows)}")
    first = rows[0]
    print(f"First row keys: {list(first.keys())}")
    print()
    print("Field presence check (what the client expects vs what is delivered):")
    for k in EXPECTED_ROW_FIELDS:
        present = k in first
        val = first.get(k)
        vpreview = "" if not present else (f"= {val!r}" if not isinstance(val, str) or len(val) < 80 else f"= {val[:80]!r}...")
        print(f"  {'OK ' if present else 'MISSING':<8} {k:<16} {vpreview}")

    print()
    print("First row (full, pretty):")
    print(json.dumps(first, indent=2)[:1200])

    section("2. GET /api/clusters?min_conf=0.85  — just top-level shape")
    status, ctype, raw = get(f"{BASE}/api/clusters?min_conf=0.85")
    print(f"Status: {status}   Body length: {len(raw)}")
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            print(f"Top-level keys: {list(parsed.keys())}")
            cl = parsed.get("clusters") or []
            print(f"Clusters: {len(cl)}")
            if cl:
                print(f"First cluster keys: {list(cl[0].keys())}")
    except Exception as e:
        print(f"parse failed: {e}")

    section("3. GET /api/centres/undefined  — does the server throw?")
    status, ctype, raw = get(f"{BASE}/api/centres/undefined")
    print(f"Status: {status}   Content-Type: {ctype}   Body length: {len(raw)}")
    print("Body preview:")
    for line in raw[:800].splitlines():
        print(f"  {line}")


if __name__ == "__main__":
    main()
