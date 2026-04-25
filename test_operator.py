"""
test_operator.py  v3
────────────────────
Exercises /api/operator/<gid> against the live review_server and
reports on both the v2 blocks (scale/nqs/growth/catchment/...) and
the v3 blocks (quality/acquisition/valuation/places_timeline).

v3 of this test: acquisition block now uses brownfield terminology
(matches operator_page.py v4).

Fails loudly when any v3 block is missing — that's almost always
a sign the server hasn't been restarted since operator_page.py
was updated.

Run from project root with review_server.py (v5) on :8001.
"""

import json
import sys
import urllib.error
import urllib.request

BASE_URL = "http://localhost:8001"

GROUPS_TO_TEST = [
    # (group_id, label, expected_entities)
    (1887, "Sparrow Group Vic",      23),
    (236,  "Harmony West Burleigh",  23),
]


def section(title: str) -> None:
    print()
    print("=" * 72)
    print(f"  {title}")
    print("=" * 72)


def http_get(path: str):
    url = BASE_URL + path
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as e:
        return None, f"<connection failed: {e.reason}>"


def print_group_block(g):
    print("  [group]")
    print(f"    group_id          : {g.get('group_id')}")
    print(f"    canonical_name    : {g.get('canonical_name')}")
    print(f"    display_name      : {g.get('display_name')!r}")
    print(f"    effective_name    : {g.get('effective_name')!r}")
    print(f"    ownership_type    : {g.get('ownership_type')}")
    print(f"    parent_entity_id  : {g.get('parent_entity_id')}")
    pe = g.get("parent_entity")
    if pe:
        print(f"    parent_entity     : {pe.get('legal_name')} "
              f"(eid {pe.get('entity_id')}, is_notional={pe.get('is_notional')})")
    else:
        print(f"    parent_entity     : not nominated")


def print_scale(s):
    print("  [scale]")
    for k in ("entities", "entities_notional", "services", "approved_places",
              "state_count", "brand_count", "kinder_services",
              "long_day_care_services", "propco_entities", "opco_entities"):
        print(f"    {k:<22}: {s.get(k)}")
    print(f"    states                : {s.get('states')}")
    print(f"    brands                : {s.get('brands')}")


def print_nqs(n):
    print("  [nqs_profile]")
    print(f"    total                 : {n.get('total')}")
    for r in n.get("by_rating", []):
        print(f"      {r['rating']:<40}  {r['count']}")


def print_growth(g):
    print("  [growth]")
    for k in ("window_12m", "window_24m", "window_36m"):
        w = g.get(k, {})
        print(f"    {k}: since {w.get('cutoff_date')} -> "
              f"{w.get('new_services')} services, {w.get('new_places')} places")


def print_catchment(c):
    print("  [catchment]")
    print(f"    populated           : {c.get('populated')}")
    print(f"    weighted_seifa      : {c.get('weighted_seifa')}")
    print(f"    weighted_under5     : {c.get('weighted_under5')}")
    print(f"    weighted_income     : {c.get('weighted_income')}")
    print(f"    supply_bands        : {c.get('supply_bands')}")


def print_misc(payload):
    reg = payload.get("regulatory_events") or []
    notes = payload.get("intelligence_notes") or {}
    gn = notes.get("group") or []
    ee = notes.get("by_entity") or {}
    print("  [regulatory_events]")
    print(f"    count               : {len(reg)}")
    print("  [intelligence_notes]")
    print(f"    group-level count   : {len(gn)}")
    print(f"    entities with notes : {len(ee)}")
    print("  [competitive_exposure]")
    ce = payload.get("competitive_exposure") or {}
    print(f"    populated           : {ce.get('populated')}")


# v2 OF THIS TEST: probe the v3 server blocks and report missing ones.

def print_quality(payload, missing):
    q = payload.get("quality")
    print("  [quality]  (v3 block)")
    if q is None:
        print("    !! BLOCK MISSING — operator_page.py v3 not loaded by server")
        missing.append("quality")
        return
    for k in ("total_services", "kinder_by_flag", "kinder_by_name",
              "long_day_care", "most_recent_rating_date",
              "oldest_rating_date", "stale_rating_count",
              "never_rated_count"):
        print(f"    {k:<22}: {q.get(k)}")


def print_acquisition(payload, missing):
    a = payload.get("acquisition")
    print("  [acquisition]  (v4 — brownfield)")
    if a is None:
        print("    !! BLOCK MISSING — operator_page.py v4 not loaded by server")
        missing.append("acquisition")
        return
    for k in ("greenfield_count", "brownfield_count",
              "brownfield_12m", "brownfield_24m", "brownfield_36m"):
        print(f"    {k:<22}: {a.get(k)}")
    bl = a.get("brownfield_list") or []
    print(f"    brownfield_list count : {len(bl)}")
    if bl:
        first = bl[0]
        print(f"    newest transfer       : {first.get('last_transfer_date')}  "
              f"{first.get('service_name')}  "
              f"({first.get('suburb')} {first.get('state')})")


def print_valuation(payload, missing):
    v = payload.get("valuation")
    print("  [valuation]  (v3 block)")
    if v is None:
        print("    !! BLOCK MISSING — operator_page.py v3 not loaded by server")
        missing.append("valuation")
        return
    for k in ("total_places", "per_place_low", "per_place_high",
              "group_low", "group_high"):
        print(f"    {k:<22}: {v.get(k)}")
    print(f"    source              : {v.get('source')}")


def print_timeline(payload, missing):
    t = payload.get("places_timeline")
    print("  [places_timeline]  (v3 block)")
    if t is None:
        print("    !! BLOCK MISSING — operator_page.py v3 not loaded by server")
        missing.append("places_timeline")
        return
    print(f"    event count         : {len(t)}")
    if t:
        first = t[0]; last = t[-1]
        print(f"    first event         : {first.get('date')}  "
              f"+{first.get('places')}  {first.get('type')}  "
              f"{first.get('service_name')}")
        print(f"    last event          : {last.get('date')}  "
              f"+{last.get('places')}  {last.get('type')}  "
              f"{last.get('service_name')}")


def print_first_entity(entities):
    print("  [first entity row]")
    if not entities:
        print("    (none)")
        return
    e = entities[0]
    for k in ("entity_id", "legal_name", "abn", "entity_type",
              "registered_state", "is_trustee", "is_propco", "is_opco",
              "is_fgc", "is_notional", "is_parent", "is_largest",
              "services_count", "places_count"):
        print(f"    {k:<22}: {e.get(k)}")


def print_first_service(services):
    print("  [first service row]")
    if not services:
        print("    (none)")
        return
    s = services[0]
    for k in ("service_id", "service_name", "suburb", "state", "postcode",
              "approved_places", "nqs", "brand_name", "entity_legal_name",
              "approval_granted_date", "last_transfer_date", "sa2_name",
              "kinder_approved", "long_day_care"):
        print(f"    {k:<22}: {s.get(k)}")


def test_group(group_id, label, expected_entities, missing):
    section(f"{label}  (group_id={group_id})")
    status, raw = http_get(f"/api/operator/{group_id}")
    if status != 200:
        print(f"HTTP {status}")
        print(raw[:800])
        return False
    try:
        payload = json.loads(raw)
    except Exception as e:
        print(f"JSON parse FAILED: {e}")
        return False
    if not payload.get("ok"):
        print(f"ok=false: {payload.get('msg')}")
        return False

    print_group_block(payload.get("group", {}))
    print_scale(payload.get("scale", {}))
    print_nqs(payload.get("nqs_profile", {}))
    print_quality(payload, missing)         # v3
    print_growth(payload.get("growth", {}))
    print_acquisition(payload, missing)     # v3
    print_timeline(payload, missing)        # v3
    print_valuation(payload, missing)       # v3
    print_catchment(payload.get("catchment", {}))
    print_misc(payload)
    print_first_entity(payload.get("entities", []))
    print_first_service(payload.get("services", []))

    actual_entities = payload.get("scale", {}).get("entities")
    ok = (actual_entities == expected_entities)
    print()
    print(f"  Entity count check   : expected {expected_entities}, got {actual_entities}"
          f"   {'OK' if ok else 'MISMATCH'}")
    return ok


def main():
    section("Testing /api/operator/<gid>")
    all_ok = True
    missing_blocks = []
    for gid, label, n in GROUPS_TO_TEST:
        ok = test_group(gid, label, n, missing_blocks)
        if not ok:
            all_ok = False

    section("RESULT")
    # De-dupe and drop blank entries
    missing_unique = sorted(set(x for x in missing_blocks if x))
    if missing_unique:
        print("FAILED — one or more v3 server blocks are missing from the payload:")
        for b in missing_unique:
            print(f"  - {b}")
        print()
        print("Diagnosis: operator_page.py v3 is not loaded by the running server.")
        print("Fix: stop the server (Ctrl+C), confirm v3 is on disk with")
        print("     Select-String -Path .\\operator_page.py -Pattern 'operator_page.py  v3'")
        print("     then start it again:  python review_server.py")
        sys.exit(2)
    if all_ok:
        print("OK — all v2 and v3 blocks present with expected counts.")
    else:
        print("FAILED — review sections above.")
    sys.exit(0 if all_ok else 2)


if __name__ == "__main__":
    main()
