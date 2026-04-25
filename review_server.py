"""
review_server.py  (v5)
────────────────────────────────────────────────────────────────
Local-only web server for Kintell ownership review.

v5 changes:
  - /api/operator/<gid>            GET: consolidated payload for the
                                        operator summary page (group
                                        meta, entities, services, scale,
                                        NQS profile, growth, catchment
                                        stub, reg events, notes)

v4 changes:
  - /api/group/<gid>               GET: basic group info incl. display_name
                                        + effective_name (display_name or
                                        canonical_name)
  - /api/group/<gid>/rename        POST: set / clear groups.display_name
                                         via group_labels.py
                                         body: {"display_name": str|null}

v3 changes:
  - free-text search via ?q= on /api/queue (matches anywhere in
    either group name or the brand name)

v2 changes:
  - /api/clusters                  cluster view of pending proposals
  - /api/cluster/<brand>           full detail incl. centre lists
  - /api/centres/<group_id>        centre list for a group
  - /api/history                   recent decisions with undo metadata
  - POST /api/bulk-accept-cluster  accept all of a brand at once,
                                   optionally excluding given cids

All v1 endpoints retained.

Serves docs/ at port 8001. Localhost only.
Run: python review_server.py
"""

import argparse
import json
import mimetypes
import re
import sqlite3
import sys
import threading
import webbrowser
from collections import defaultdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
import apply_decisions  # noqa: E402
import group_labels      # noqa: E402
import operator_page     # noqa: E402

ROOT     = Path(__file__).resolve().parent
DOCS_DIR = ROOT / "docs"
DB_PATH  = ROOT / "data" / "kintell.db"


# ─── Read helpers ───────────────────────────────────────────────────

def _conn():
    return sqlite3.connect(str(DB_PATH))


def fetch_queue(status_filter=None, limit=None, brand=None,
                min_conf=None, max_conf=None, q=None):
    if not DB_PATH.exists():
        return []
    conn = _conn()
    try:
        where = ["c.link_type = 'group_merge'"]
        params = []
        if status_filter:
            where.append("c.status = ?")
            params.append(status_filter)
        else:
            where.append("c.status IN ('pending','parked')")
        if brand:
            where.append(
                "LOWER(json_extract(c.evidence_json,'$.brand')) = LOWER(?)"
            )
            params.append(brand)
        if min_conf is not None:
            where.append("c.composite_confidence >= ?")
            params.append(min_conf)
        if max_conf is not None:
            where.append("c.composite_confidence <= ?")
            params.append(max_conf)
        if q:
            # Free-text: match anywhere in either group name or the brand
            like = f"%{q.strip().lower()}%"
            where.append(
                "(LOWER(gA.canonical_name) LIKE ?"
                " OR LOWER(gB.canonical_name) LIKE ?"
                " OR LOWER(json_extract(c.evidence_json,'$.brand')) LIKE ?)"
            )
            params.extend([like, like, like])

        sql = f"""
            SELECT c.candidate_id, c.composite_confidence, c.status,
                   c.priority, c.proposed_at,
                   c.from_id, gA.canonical_name AS from_name,
                   c.to_id,   gB.canonical_name AS to_name,
                   c.evidence_json, c.review_note
              FROM link_candidates c
              JOIN groups gA ON gA.group_id = c.from_id
              JOIN groups gB ON gB.group_id = c.to_id
             WHERE {' AND '.join(where)}
             ORDER BY c.composite_confidence DESC, c.candidate_id
        """
        if limit:
            sql += f" LIMIT {int(limit)}"
        rows = conn.execute(sql, params).fetchall()
        out = []
        for r in rows:
            out.append({
                "candidate_id": r[0], "confidence": r[1], "status": r[2],
                "priority": r[3], "proposed_at": r[4],
                "from_id": r[5], "from_name": r[6],
                "to_id": r[7],   "to_name":   r[8],
                "evidence": json.loads(r[9] or "{}"),
                "review_note": r[10],
            })
        return out
    finally:
        conn.close()


def fetch_clusters(min_conf=0.85):
    """
    Returns one row per brand with a pending cluster:
      brand, canonical_group_id, canonical_name, canonical_centres,
      pending_count, total_other_centres, candidate_ids[],
      min_conf, max_conf, has_med_conf
    """
    if not DB_PATH.exists():
        return []
    conn = _conn()
    try:
        rows = conn.execute("""
            SELECT
              json_extract(c.evidence_json,'$.brand')       AS brand,
              json_extract(c.evidence_json,'$.canonical_group_id') AS canon_gid,
              json_extract(c.evidence_json,'$.canonical_group')    AS canon_name,
              json_extract(c.evidence_json,'$.canonical_brand_svc') AS canon_svc,
              c.candidate_id, c.composite_confidence,
              c.from_id, gA.canonical_name AS from_name,
              json_extract(c.evidence_json,'$.other_brand_svc') AS other_svc,
              json_extract(c.evidence_json,'$.other_total_svc') AS other_total,
              json_extract(c.evidence_json,'$.other_concentration') AS other_conc
            FROM link_candidates c
            JOIN groups gA ON gA.group_id = c.from_id
            WHERE c.link_type = 'group_merge'
              AND c.status = 'pending'
            ORDER BY brand, c.composite_confidence DESC
        """).fetchall()
    finally:
        conn.close()

    by_brand = defaultdict(lambda: {
        "brand": None, "canonical_gid": None, "canonical_name": None,
        "canonical_svc": 0,
        "absorbing": [],
        "min_conf": 1.0, "max_conf": 0.0,
        "high_conf_cids": [], "all_cids": [],
    })

    for (brand, canon_gid, canon_name, canon_svc, cid, conf,
         from_id, from_name, other_svc, other_total, other_conc) in rows:
        if not brand:
            continue
        b = by_brand[brand]
        b["brand"]          = brand
        b["canonical_gid"]  = canon_gid
        b["canonical_name"] = canon_name
        b["canonical_svc"]  = canon_svc or 0
        b["absorbing"].append({
            "candidate_id": cid,
            "confidence":   conf,
            "from_id":      from_id,
            "from_name":    from_name,
            "brand_svc":    other_svc or 0,
            "total_svc":    other_total or 0,
            "concentration": other_conc or 0,
        })
        b["min_conf"] = min(b["min_conf"], conf)
        b["max_conf"] = max(b["max_conf"], conf)
        b["all_cids"].append(cid)
        if conf >= min_conf:
            b["high_conf_cids"].append(cid)

    out = []
    for k, v in by_brand.items():
        out.append({
            "brand":           v["brand"],
            "canonical_gid":   v["canonical_gid"],
            "canonical_name":  v["canonical_name"],
            "canonical_svc":   v["canonical_svc"],
            "pending_count":   len(v["absorbing"]),
            "high_conf_count": len(v["high_conf_cids"]),
            "min_conf":        round(v["min_conf"], 3),
            "max_conf":        round(v["max_conf"], 3),
            "absorbing":       v["absorbing"],
        })
    out.sort(key=lambda x: (-x["pending_count"], -x["max_conf"]))
    return out


def fetch_centres_for_group(group_id, limit=None):
    if not DB_PATH.exists():
        return []
    conn = _conn()
    try:
        sql = """
            SELECT s.service_id, s.service_name, s.suburb, s.state,
                   s.approved_places, s.overall_nqs_rating,
                   s.provider_approval_number,
                   e.entity_id, e.legal_name
              FROM services s
              JOIN entities e ON e.entity_id = s.entity_id
             WHERE e.group_id = ?
             ORDER BY s.service_name
        """
        if limit:
            sql += f" LIMIT {int(limit)}"
        rows = conn.execute(sql, (group_id,)).fetchall()
        return [
            {
                "service_id": r[0], "service_name": r[1],
                "suburb": r[2], "state": r[3],
                "approved_places": r[4], "nqs": r[5],
                "provider_approval_number": r[6],
                "entity_id": r[7], "entity_legal_name": r[8],
            } for r in rows
        ]
    finally:
        conn.close()


def fetch_cluster_detail(brand):
    """Cluster view + centre lists on each side."""
    if not DB_PATH.exists():
        return None
    conn = _conn()
    try:
        rows = conn.execute("""
            SELECT
              json_extract(c.evidence_json,'$.brand')              AS brand,
              json_extract(c.evidence_json,'$.canonical_group_id') AS canon_gid,
              json_extract(c.evidence_json,'$.canonical_group')    AS canon_name,
              c.candidate_id, c.composite_confidence,
              c.from_id, gA.canonical_name AS from_name,
              c.evidence_json
              FROM link_candidates c
              JOIN groups gA ON gA.group_id = c.from_id
             WHERE c.link_type = 'group_merge'
               AND c.status = 'pending'
               AND LOWER(json_extract(c.evidence_json,'$.brand')) = LOWER(?)
             ORDER BY c.composite_confidence DESC
        """, (brand,)).fetchall()
    finally:
        conn.close()

    if not rows:
        return None

    canon_gid  = rows[0][1]
    canon_name = rows[0][2]

    absorbing = []
    for (_, _, _, cid, conf, from_id, from_name, ev_json) in rows:
        ev = json.loads(ev_json or "{}")
        absorbing.append({
            "candidate_id": cid,
            "confidence":   conf,
            "from_id":      from_id,
            "from_name":    from_name,
            "brand_svc":    ev.get("other_brand_svc", 0),
            "total_svc":    ev.get("other_total_svc", 0),
            "concentration": ev.get("other_concentration", 0),
            "adjustments":  ev.get("adjustments", []),
            "centres":      fetch_centres_for_group(from_id),
        })

    return {
        "brand":           rows[0][0],
        "canonical_gid":   canon_gid,
        "canonical_name":  canon_name,
        "canonical_centres": fetch_centres_for_group(canon_gid),
        "absorbing":       absorbing,
    }


def fetch_history(limit=200):
    if not DB_PATH.exists():
        return []
    conn = _conn()
    try:
        rows = conn.execute("""
            SELECT a.audit_id, a.actor, a.action, a.subject_type,
                   a.subject_id, a.before_json, a.after_json,
                   a.reason, a.occurred_at
              FROM audit_log a
             ORDER BY a.audit_id DESC
             LIMIT ?
        """, (limit,)).fetchall()

        out = []
        for r in rows:
            (aid, actor, action, st, sid, before, after, reason, at) = r
            entry = {
                "audit_id":     aid,
                "actor":        actor,
                "action":       action,
                "subject_type": st,
                "subject_id":   sid,
                "occurred_at":  at,
                "reason":       reason,
                "reversible":   action == "accept_merge",
            }
            if before:
                try:
                    bdata = json.loads(before)
                    if action == "accept_merge":
                        src  = bdata.get("source_group", {}) or {}
                        dest = bdata.get("dest_group",   {}) or {}
                        cand = bdata.get("candidate",    {}) or {}
                        entry["summary"] = {
                            "kind":         "merge",
                            "source_name":  src.get("canonical_name"),
                            "source_id":    src.get("group_id"),
                            "dest_name":    dest.get("canonical_name"),
                            "dest_id":      dest.get("group_id"),
                            "entities":     len(src.get("entity_ids", [])),
                            "brands":       len(src.get("brand_ids", [])),
                            "candidate_id": cand.get("candidate_id"),
                            "confidence":   cand.get("composite_confidence"),
                        }
                    elif action in ("reject_merge", "park_merge"):
                        cand = bdata.get("candidate", {}) or {}
                        entry["summary"] = {
                            "kind":         action.replace("_merge",""),
                            "candidate_id": cand.get("candidate_id"),
                            "confidence":   cand.get("composite_confidence"),
                            "from_id":      cand.get("from_id"),
                            "to_id":        cand.get("to_id"),
                        }
                    elif action == "reverse_accept":
                        rev = bdata.get("reversing", {}) or {}
                        src = rev.get("source_group", {}) or {}
                        entry["summary"] = {
                            "kind":          "reverse",
                            "restored_name": src.get("canonical_name"),
                            "restored_id":   src.get("group_id"),
                        }
                except Exception:
                    pass
            out.append(entry)
        return out
    finally:
        conn.close()


def fetch_status():
    if not DB_PATH.exists():
        return {"ok": False, "msg": "no db"}
    status = apply_decisions.get_status()
    conn = _conn()
    try:
        by_brand_rows = conn.execute("""
            SELECT LOWER(json_extract(c.evidence_json,'$.brand')) AS b,
                   c.status, COUNT(*)
              FROM link_candidates c
             WHERE c.link_type = 'group_merge'
             GROUP BY b, c.status
        """).fetchall()
        bb = {}
        for brand, st, n in by_brand_rows:
            bb.setdefault(brand or "(unknown)", {})[st] = n
        status["by_brand"] = bb

        recent = conn.execute("""
            SELECT audit_id, actor, action, subject_id,
                   occurred_at, reason
              FROM audit_log
             ORDER BY audit_id DESC LIMIT 20
        """).fetchall()
        status["recent_actions"] = [
            {"audit_id": a, "actor": b, "action": c,
             "subject_id": d, "at": e, "reason": f}
            for a, b, c, d, e, f in recent
        ]
    finally:
        conn.close()
    return status


def bulk_accept_cluster(brand, exclude_cids=None, actor="patrick"):
    """Accept every pending candidate for a given brand, except excluded."""
    if not brand:
        return {"ok": False, "msg": "brand required"}
    exclude_cids = set(int(x) for x in (exclude_cids or []))

    conn = _conn()
    try:
        cands = [r[0] for r in conn.execute("""
            SELECT c.candidate_id
              FROM link_candidates c
             WHERE c.link_type = 'group_merge'
               AND c.status = 'pending'
               AND LOWER(json_extract(c.evidence_json,'$.brand')) = LOWER(?)
        """, (brand,)).fetchall()]
    finally:
        conn.close()

    cands = [c for c in cands if c not in exclude_cids]
    accepted = 0
    failed   = 0
    errors   = []
    for cid in cands:
        res = apply_decisions.accept(cid, actor=actor)
        if res.get("ok"):
            accepted += 1
        else:
            failed += 1
            errors.append({"candidate_id": cid, "msg": res.get("msg")})

    return {
        "ok":       True,
        "brand":    brand,
        "accepted": accepted,
        "failed":   failed,
        "excluded": len(exclude_cids),
        "errors":   errors,
    }


# ─── HTTP ───────────────────────────────────────────────────────────

API_ACCEPT  = re.compile(r"^/api/accept/(\d+)/?$")
API_REJECT  = re.compile(r"^/api/reject/(\d+)/?$")
API_PARK    = re.compile(r"^/api/park/(\d+)/?$")
API_REVERSE = re.compile(r"^/api/reverse/(\d+)/?$")
API_CENTRES = re.compile(r"^/api/centres/(\d+)/?$")
API_CLUSTER = re.compile(r"^/api/cluster/(.+?)/?$")
# v4:
API_GROUP_RENAME = re.compile(r"^/api/group/(\d+)/rename/?$")
API_GROUP_GET    = re.compile(r"^/api/group/(\d+)/?$")
# v5:
API_OPERATOR     = re.compile(r"^/api/operator/(\d+)/?$")


class ReviewHandler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        sys.stdout.write("  %s - %s\n" % (
            self.log_date_time_string(), fmt % args))

    # ── helpers ──
    def _send_json(self, obj, status=200):
        body = json.dumps(obj, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path):
        if not path.exists() or not path.is_file():
            self._send_text("Not found", 404); return
        ctype, _ = mimetypes.guess_type(str(path))
        ctype = ctype or "application/octet-stream"
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _send_text(self, txt, status=200):
        body = txt.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self):
        ln = int(self.headers.get("Content-Length") or 0)
        if not ln:
            return {}
        try:
            return json.loads(self.rfile.read(ln).decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return {}

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs   = parse_qs(parsed.query)

        # GET endpoints
        if path == "/api/queue":
            try:
                self._send_json({"ok": True,
                                 "rows": fetch_queue(
                                    status_filter=(qs.get("status") or [None])[0],
                                    limit=(qs.get("limit") or [None])[0],
                                    brand=(qs.get("brand") or [None])[0],
                                    min_conf=float(qs["min_conf"][0])
                                        if "min_conf" in qs else None,
                                    max_conf=float(qs["max_conf"][0])
                                        if "max_conf" in qs else None,
                                    q=(qs.get("q") or [None])[0],
                                 )})
            except Exception as e:
                self._send_json({"ok": False, "msg": str(e)}, 500)
            return

        if path == "/api/clusters":
            try:
                mc = float(qs.get("min_conf", ["0.85"])[0])
                self._send_json({"ok": True,
                                 "clusters": fetch_clusters(min_conf=mc)})
            except Exception as e:
                self._send_json({"ok": False, "msg": str(e)}, 500)
            return

        if path == "/api/status":
            try:
                self._send_json(fetch_status())
            except Exception as e:
                self._send_json({"ok": False, "msg": str(e)}, 500)
            return

        if path == "/api/history":
            try:
                lim = int((qs.get("limit") or ["200"])[0])
                self._send_json({"ok": True,
                                 "entries": fetch_history(limit=lim)})
            except Exception as e:
                self._send_json({"ok": False, "msg": str(e)}, 500)
            return

        m = API_CENTRES.match(path)
        if m:
            try:
                self._send_json({"ok": True,
                                 "centres": fetch_centres_for_group(int(m.group(1)))})
            except Exception as e:
                self._send_json({"ok": False, "msg": str(e)}, 500)
            return

        m = API_CLUSTER.match(path)
        if m:
            try:
                brand = unquote(m.group(1))
                detail = fetch_cluster_detail(brand)
                if detail is None:
                    self._send_json({"ok": False, "msg": "not found"}, 404)
                else:
                    self._send_json({"ok": True, "cluster": detail})
            except Exception as e:
                self._send_json({"ok": False, "msg": str(e)}, 500)
            return

        # v4: single-group read (basic fields only; richer operator
        # payload comes in /api/operator/<gid> next)
        m = API_GROUP_GET.match(path)
        if m:
            try:
                self._send_json(group_labels.get_group(int(m.group(1))))
            except Exception as e:
                self._send_json({"ok": False, "msg": str(e)}, 500)
            return

        # v5: consolidated payload for the operator summary page
        m = API_OPERATOR.match(path)
        if m:
            try:
                self._send_json(
                    operator_page.get_operator_payload(int(m.group(1)))
                )
            except Exception as e:
                self._send_json({"ok": False, "msg": str(e)}, 500)
            return

        # static
        if path == "/" or path == "":
            target = DOCS_DIR / "index.html"
        else:
            rel = path.lstrip("/")
            if ".." in Path(rel).parts:
                self._send_text("Forbidden", 403); return
            target = DOCS_DIR / rel
        self._send_file(target)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        body = self._read_json_body()
        actor = body.get("actor") or "patrick"

        m = API_ACCEPT.match(path)
        if m:
            self._send_json(apply_decisions.accept(int(m.group(1)), actor=actor)); return

        m = API_REJECT.match(path)
        if m:
            self._send_json(apply_decisions.reject(int(m.group(1)),
                actor=actor, reason=body.get("reason"))); return

        m = API_PARK.match(path)
        if m:
            self._send_json(apply_decisions.park(int(m.group(1)),
                actor=actor, reason=body.get("reason"))); return

        m = API_REVERSE.match(path)
        if m:
            self._send_json(apply_decisions.reverse(int(m.group(1)), actor=actor)); return

        if path == "/api/bulk-accept":
            try:
                self._send_json(apply_decisions.bulk_accept(
                    min_confidence=float(body.get("min_confidence", 0.9)),
                    brand=body.get("brand"),
                    actor=actor,
                    dry_run=bool(body.get("dry_run", False)),
                ))
            except Exception as e:
                self._send_json({"ok": False, "msg": str(e)}, 500)
            return

        if path == "/api/bulk-accept-cluster":
            try:
                self._send_json(bulk_accept_cluster(
                    brand=body.get("brand"),
                    exclude_cids=body.get("exclude_cids", []),
                    actor=actor,
                ))
            except Exception as e:
                self._send_json({"ok": False, "msg": str(e)}, 500)
            return

        # v4: rename a group (sets groups.display_name; null clears)
        m = API_GROUP_RENAME.match(path)
        if m:
            try:
                self._send_json(group_labels.rename(
                    int(m.group(1)),
                    body.get("display_name"),
                    actor=actor,
                ))
            except Exception as e:
                self._send_json({"ok": False, "msg": str(e)}, 500)
            return

        self._send_text("Not found", 404)


# ─── Entry point ────────────────────────────────────────────────────

def run(port=8001, open_browser=True):
    if not DOCS_DIR.exists():
        print(f"[X] docs folder not found: {DOCS_DIR}"); sys.exit(1)
    if not DB_PATH.exists():
        print(f"[X] Database not found: {DB_PATH}");      sys.exit(1)

    addr = ("127.0.0.1", port)
    httpd = ThreadingHTTPServer(addr, ReviewHandler)
    url = f"http://localhost:{port}/"

    print(f"\n  Kintell review server (v5)")
    print(f"  ───────────────────────────")
    print(f"  Serving : {DOCS_DIR}")
    print(f"  Database: {DB_PATH}")
    print(f"  Dashboard : {url}")
    print(f"  Review    : {url}review.html")
    print(f"  Status API: {url}api/status\n")
    print(f"  Ctrl+C to stop.\n")

    if open_browser:
        threading.Timer(0.5,
            lambda: webbrowser.open(url + "review.html")).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  Shutting down.")
        httpd.shutdown()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=8001)
    p.add_argument("--no-browser", action="store_true")
    args = p.parse_args()
    run(port=args.port, open_browser=not args.no_browser)
