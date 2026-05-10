"""
algolia_reconcile.py — DEC-83 Algolia reconciliation tool.

Surfaces deltas between Starting Blocks' Algolia index and main `services` table:
  (a) Algolia hits NOT in main DB — new registrations / Algolia-only services
  (b) main-DB services NOT in Algolia (within scanned area) — potential closures
      or Algolia-index gaps

V1 = read-only report. No DB mutations. V2 = automated tracking row writes.

Closes the Algolia portion of OI-NEW-4 (Starting Blocks Algolia smoke test).

Per DEC-83 #10: Algolia credentials are public values from Starting Blocks JS
bundle (not secrets). Hardcoded as constants. Smoke test on every run; if it
returns HTTP 403 or empty results, refresh procedure documented in pilot's
STAGE2_DESIGN.md (5-min DevTools sweep — open Find Child Care page in browser,
DevTools Network tab, find `queries?x-algolia-agent=...` request, read new
credentials from URL query string, update constants below).

Usage:
    $env:PYTHONIOENCODING = "utf-8"
    python algolia_reconcile.py                       # smoke test only
    python algolia_reconcile.py --pilot               # smoke test + reconcile 3 pilot SA2s
    python algolia_reconcile.py --centroid <lat> <lng> [--radius-m 2000]  # custom area
    python algolia_reconcile.py --csv <path>          # also write delta to CSV

Notes:
  - V1 deliberately does NOT do a national sweep — Algolia hits-per-query cap (~1000)
    means national reconciliation needs SA4-loop or postcode-loop driver, deferred to V2.
  - V1 area scopes (pilot or single centroid) prove the tool works; production
    refresh wiring (weekly cron) layers on top.
"""

import argparse
import csv
import json
import sqlite3
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent
DB_PATH = ROOT / "data" / "kintell.db"

# ---------------------------------------------------------------------------
# Algolia configuration — public values from Starting Blocks JS bundle.
# Refresh procedure: see module docstring (5 min DevTools).
# ---------------------------------------------------------------------------
ALGOLIA_APP_ID = "CGQW4YLCUR"
ALGOLIA_API_KEY = "59d33900544ce513400031e6bff95522"
ALGOLIA_INDEX = "production_services"
ALGOLIA_HOST = f"{ALGOLIA_APP_ID.lower()}-dsn.algolia.net"
ALGOLIA_AGENT = "Algolia for JavaScript (5.46.2); Search (5.46.2); Browser"
HITS_PER_PAGE = 25
POLITE_SLEEP_S = 0.5
REQUEST_TIMEOUT_S = 20
USER_AGENT = "NovaraIntelligence/1.0 (commercial-layer reconcile; respects robots.txt)"

# Pilot SA2 centroids — preserve from pilot's discover.py for V1 reconciliation
PILOT_SA2S = {
    "Haymarket":      {"lat": -33.8803, "lng": 151.2049, "radius_m": 2000, "state": "NSW"},
    "Carlton":        {"lat": -37.8001, "lng": 144.9670, "radius_m": 2000, "state": "VIC"},
    "Toowoomba East": {"lat": -27.5598, "lng": 151.9700, "radius_m": 2000, "state": "QLD"},
}


def query_algolia_page(lat: float, lng: float, radius_m: int, page: int) -> dict:
    """POST one page of search results from Algolia. Returns parsed response."""
    url = (
        f"https://{ALGOLIA_HOST}/1/indexes/*/queries"
        f"?x-algolia-agent={urllib.parse.quote(ALGOLIA_AGENT)}"
        f"&x-algolia-api-key={ALGOLIA_API_KEY}"
        f"&x-algolia-application-id={ALGOLIA_APP_ID}"
    )
    params_str = (
        f"page={page}&aroundLatLng={lat},{lng}&aroundRadius={radius_m}"
        f"&hitsPerPage={HITS_PER_PAGE}&getRankingInfo=true&facets=[*]&facetFilters=[]"
    )
    body = json.dumps({"requests": [{"indexName": ALGOLIA_INDEX, "params": params_str}]}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_S) as resp:
        return json.loads(resp.read().decode("utf-8"))


def smoke_test() -> bool:
    """One Algolia query against Haymarket centroid; expect HTTP 200 + nbHits > 0."""
    try:
        sa2 = PILOT_SA2S["Haymarket"]
        resp = query_algolia_page(sa2["lat"], sa2["lng"], sa2["radius_m"], page=0)
    except Exception as e:
        print(f"  [FAIL] Algolia smoke test: {e!r}", file=sys.stderr)
        return False
    results = resp.get("results") or []
    if not results:
        print(f"  [FAIL] Algolia returned no 'results' array.", file=sys.stderr)
        print(f"         Response keys: {list(resp.keys())}", file=sys.stderr)
        return False
    n_hits = results[0].get("nbHits", 0)
    if n_hits == 0:
        print(f"  [FAIL] Algolia returned 0 hits at Haymarket centroid (expected ~70).", file=sys.stderr)
        print(f"         Likely cause: Algolia key rotated. See refresh procedure in module docstring.")
        return False
    print(f"  [PASS] Algolia smoke test: {n_hits} hits at Haymarket (expected ~70).")
    return True


def collect_algolia_hits(lat: float, lng: float, radius_m: int) -> list[dict]:
    """Paginate through all Algolia hits in a radius. Returns list of hit dicts."""
    hits = []
    page = 0
    nb_pages = 1
    while page < nb_pages:
        resp = query_algolia_page(lat, lng, radius_m, page)
        result = (resp.get("results") or [{}])[0]
        page_hits = result.get("hits") or []
        nb_pages = result.get("nbPages", 1)
        for h in page_hits:
            hits.append(h)
        page += 1
        if page < nb_pages:
            time.sleep(POLITE_SLEEP_S)
    return hits


def reconcile_area(conn, label: str, lat: float, lng: float, radius_m: int) -> dict:
    """Reconcile one geographic area. Returns delta dict."""
    print(f"\n--- Reconciling area: {label} ({lat},{lng} r={radius_m}m) ---")
    hits = collect_algolia_hits(lat, lng, radius_m)
    print(f"  Algolia returned {len(hits)} hits")

    # Extract Algolia SAN -> short form (substring 1..11) for join
    algolia_short_sans = {}
    for h in hits:
        # Algolia hits have full long-form SAN at h.objectID's underlying serviceId is via fetch only;
        # for reconciliation we use the Algolia hit's name + suburb + postcode to match against services
        # Algolia hits don't include serviceId directly; need to use lat/lng + name proximity
        # Realistic reconcile: use suburb + state + postcode + name match
        addr = h.get("address") or {}
        algolia_short_sans[h.get("objectID")] = {
            "name":     h.get("name"),
            "suburb":   addr.get("suburbTown"),
            "state":    addr.get("stateTerritory"),
            "postcode": str(addr.get("postcode") or "").zfill(4) if addr.get("postcode") else None,
            "lat":      (h.get("_geoloc") or {}).get("lat"),
            "lng":      (h.get("_geoloc") or {}).get("lng"),
        }

    # Match Algolia hits against services via lat/lng proximity (within ~100m) OR name+suburb+postcode
    # For V1 simplicity: use suburb+state match within the same area, then name fuzzy match
    in_algolia_not_in_services = []
    matched_via_external_capture = 0
    for ulid, info in algolia_short_sans.items():
        # Most reliable: check if we already have this ulid in service_external_capture (130 pilot centres do)
        cap = conn.execute(
            "SELECT 1 FROM service_external_capture WHERE external_id = ? LIMIT 1",
            (ulid,),
        ).fetchone()
        if cap:
            matched_via_external_capture += 1
            continue
        # Fall back to suburb+state+name match against services
        if not info["suburb"] or not info["state"]:
            in_algolia_not_in_services.append((ulid, info))
            continue
        match = conn.execute(
            """
            SELECT service_id FROM services
            WHERE upper(suburb) = upper(?) AND upper(state) = upper(?)
              AND lower(service_name) LIKE lower(?)
            LIMIT 1
            """,
            (info["suburb"], info["state"], f"%{(info['name'] or '')[:30]}%"),
        ).fetchone()
        if not match:
            in_algolia_not_in_services.append((ulid, info))

    print(f"  Algolia hits matched to services (via external_capture): {matched_via_external_capture}")
    print(f"  Algolia hits matched to services (via suburb+name fallback): "
          f"{len(hits) - matched_via_external_capture - len(in_algolia_not_in_services)}")
    print(f"  Algolia hits with no match in main DB: {len(in_algolia_not_in_services)}")
    if in_algolia_not_in_services:
        print(f"    First 5 unmatched (potential new centres or fuzzy-match misses):")
        for ulid, info in in_algolia_not_in_services[:5]:
            print(f"      ulid={ulid}  {info['name']}  ({info['suburb']}, {info['state']} {info['postcode']})")

    # Now check: services in this geographic area that are NOT in Algolia hits
    # Use a simple bounding-box-ish radius via lat/lng of services in the same suburb cluster
    # This is approximate; a clean V2 spatial query would be better
    # For V1, use suburb+state from Algolia hits as the area definition
    suburbs_in_algolia = {(info["suburb"], info["state"]) for info in algolia_short_sans.values()
                          if info["suburb"] and info["state"]}
    if suburbs_in_algolia:
        suburbs_clause = " OR ".join(f"(upper(suburb) = upper(?) AND upper(state) = upper(?))"
                                      for _ in suburbs_in_algolia)
        params = []
        for sub, st in suburbs_in_algolia:
            params.extend([sub, st])
        services_in_area = conn.execute(
            f"SELECT service_id, service_name, suburb, state, service_approval_number, is_active "
            f"FROM services WHERE ({suburbs_clause}) AND is_active = 1",
            params,
        ).fetchall()
        # Match each service: do we have it in Algolia hits?
        services_in_algolia_via_capture = set()
        for ulid in algolia_short_sans.keys():
            cap = conn.execute(
                "SELECT service_id FROM service_external_capture WHERE external_id = ? LIMIT 1",
                (ulid,),
            ).fetchone()
            if cap and cap[0]:
                services_in_algolia_via_capture.add(cap[0])
        in_services_not_in_algolia = [s for s in services_in_area
                                       if s["service_id"] not in services_in_algolia_via_capture]
        print(f"  services in area (active, by suburb match): {len(services_in_area)}")
        print(f"  services in area NOT in Algolia hits: {len(in_services_not_in_algolia)} "
              f"(potential closures / Algolia-index gaps / fuzzy mismatches)")
        if in_services_not_in_algolia:
            print(f"    First 5:")
            for s in in_services_not_in_algolia[:5]:
                print(f"      {s['service_approval_number']:<14} {s['service_name'][:35]:<35} ({s['suburb']}, {s['state']})")
    else:
        in_services_not_in_algolia = []

    return {
        "area":                            label,
        "algolia_hits":                    len(hits),
        "matched_via_external_capture":    matched_via_external_capture,
        "in_algolia_not_in_services":      [(u, i) for u, i in in_algolia_not_in_services],
        "in_services_not_in_algolia":      [dict(s) for s in in_services_not_in_algolia],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="DEC-83 Algolia reconciliation.")
    parser.add_argument("--smoke-test-only", action="store_true",
                        help="Run only the Algolia API smoke test, then exit.")
    parser.add_argument("--pilot", action="store_true",
                        help="Reconcile against the 3 pilot SA2 centroids (Haymarket, Carlton, Toowoomba East).")
    parser.add_argument("--centroid", nargs=2, metavar=("LAT", "LNG"), type=float,
                        help="Reconcile a custom centroid (lat lng).")
    parser.add_argument("--radius-m", type=int, default=2000,
                        help="Radius in metres for --centroid (default 2000).")
    parser.add_argument("--csv", type=str, default=None,
                        help="Optional path to write delta CSV.")
    args = parser.parse_args()

    print("=" * 70)
    print("  DEC-83 Algolia Reconciliation")
    print("=" * 70)
    print(f"  ts: {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    print(f"  Algolia: app={ALGOLIA_APP_ID} index={ALGOLIA_INDEX}")
    print()

    print("Smoke test ...")
    if not smoke_test():
        print()
        print("ABORT: Algolia smoke test failed.")
        print("Refresh procedure: open https://www.startingblocks.gov.au/find-child-care, ")
        print("DevTools > Network > Fetch/XHR > 'queries?x-algolia-agent=...' request URL.")
        print("Read x-algolia-application-id and x-algolia-api-key from query string.")
        print("Update constants at top of this script.")
        return 2

    if args.smoke_test_only:
        print()
        print("Smoke-test-only mode — exit successful.")
        return 0

    if not args.pilot and not args.centroid:
        print()
        print("No reconciliation scope specified — use --pilot or --centroid lat lng.")
        print("Smoke test passed; tool is ready. Exiting.")
        return 0

    if not DB_PATH.exists():
        print(f"ERROR: {DB_PATH} not found.", file=sys.stderr)
        return 1
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    deltas = []
    if args.pilot:
        for label, sa2 in PILOT_SA2S.items():
            d = reconcile_area(conn, label, sa2["lat"], sa2["lng"], sa2["radius_m"])
            deltas.append(d)
            time.sleep(POLITE_SLEEP_S)
    if args.centroid:
        lat, lng = args.centroid
        d = reconcile_area(conn, f"custom_{lat:.4f}_{lng:.4f}", lat, lng, args.radius_m)
        deltas.append(d)

    # Aggregate report
    print()
    print("=" * 70)
    print("  RECONCILIATION SUMMARY")
    print("=" * 70)
    total_hits = sum(d["algolia_hits"] for d in deltas)
    total_unmatched_alg = sum(len(d["in_algolia_not_in_services"]) for d in deltas)
    total_unmatched_svc = sum(len(d["in_services_not_in_algolia"]) for d in deltas)
    print(f"  Areas reconciled:                          {len(deltas)}")
    print(f"  Total Algolia hits:                        {total_hits}")
    print(f"  Algolia hits not in services (new/gaps):   {total_unmatched_alg}")
    print(f"  Services not in Algolia hits (closures?):  {total_unmatched_svc}")

    if args.csv:
        path = Path(args.csv)
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["area", "side", "ulid_or_san", "name", "suburb", "state", "postcode"])
            for d in deltas:
                for ulid, info in d["in_algolia_not_in_services"]:
                    w.writerow([d["area"], "in_algolia_not_in_services", ulid,
                                info["name"], info["suburb"], info["state"], info["postcode"]])
                for s in d["in_services_not_in_algolia"]:
                    w.writerow([d["area"], "in_services_not_in_algolia",
                                s.get("service_approval_number"), s.get("service_name"),
                                s.get("suburb"), s.get("state"), ""])
        print(f"  CSV written: {path}")

    print()
    print("V1 reconciliation = report only. V2 will write tracking rows for unmatched cases.")
    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
