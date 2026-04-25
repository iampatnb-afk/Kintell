"""
lookup_operator.py — On-demand operator property research
Remara Agent

Usage:
  python lookup_operator.py "Wallaby Childcare"
  python lookup_operator.py "Malek Group"
  python lookup_operator.py --list          (show all cached lookups)
  python lookup_operator.py --clear         (clear cache)

Results are cached in data/lookup_cache/ so repeat lookups are instant.
Cached operators show a checkmark in the prospecting page.
"""

import json
import sys
import re
import time
import argparse
import logging
from pathlib import Path
from datetime import date
from urllib.parse import quote, urlencode

import requests
from rapidfuzz import fuzz
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR     = Path(__file__).parent
DATA_DIR     = BASE_DIR / "data"
CACHE_DIR    = DATA_DIR / "lookup_cache"
SNAP_FILE    = DATA_DIR / "services_snapshot.csv"
TARGETS_FILE = BASE_DIR / "operators_target_list.json"

ABR_GUID = os.getenv("ABR_GUID", "")
ABR_BASE = "https://abr.business.gov.au/json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# HELPERS (same as module4)
# ─────────────────────────────────────────────

def title_search_url(state: str, address: str, suburb: str) -> str:
    q = quote(f"{address} {suburb}".strip())
    s = str(state).strip().upper()
    urls = {
        "NSW": f"https://www.nswlrs.com.au/land_titles/property_search?q={q}",
        "VIC": f"https://www.landata.vic.gov.au/property-information?address={q}",
        "QLD": f"https://www.titlesqld.com.au/title-search?address={q}",
        "SA":  f"https://www.sailis.sa.gov.au/home/query?address={q}",
        "WA":  f"https://www0.landgate.wa.gov.au/property-search?address={q}",
        "TAS": f"https://www.thelist.tas.gov.au/app/content/property?address={q}",
        "ACT": f"https://actmapi.act.gov.au/actmapi/index.html?viewer=actmapi&address={q}",
    }
    return urls.get(s, f"https://www.google.com/search?q={quote(address+' '+suburb+' '+s+' land title owner')}")


def abr_lookup_abn(abn: str) -> dict:
    if not ABR_GUID:
        return {}
    try:
        clean = re.sub(r'\D', '', str(abn))
        r = requests.get(
            f"{ABR_BASE}/AbnDetails.aspx?abn={clean}&callback=callback&guid={ABR_GUID}",
            timeout=10
        )
        m = re.search(r'callback\((.*)\)', r.text, re.DOTALL)
        if m:
            data = json.loads(m.group(1))
            if not data.get("Message"):
                return data
    except Exception:
        pass
    return {}


def abr_search_name(name: str, max_results: int = 20) -> list:
    if not ABR_GUID or not name:
        return []
    try:
        clean = re.sub(r'[^\w\s]', ' ', name).strip()
        for suffix in [" pty ltd", " pty limited", " limited", " ltd",
                       " atf", " as trustee", " trust"]:
            clean = clean.lower().replace(suffix, "").strip()
        clean = clean[:50]
        params = urlencode({
            "name": clean, "maxResults": max_results,
            "callback": "callback", "guid": ABR_GUID
        })
        r = requests.get(f"{ABR_BASE}/MatchingNames.aspx?{params}", timeout=10)
        m = re.search(r'callback\((.*)\)', r.text, re.DOTALL)
        if m:
            return json.loads(m.group(1)).get("Names", [])
    except Exception:
        pass
    return []


def find_related_entities(name: str, base_abn: str = "") -> list:
    core = re.sub(
        r'\b(pty|ltd|limited|atf|as trustee|trust|unit trust|family trust|'
        r'holdings|investments|enterprises|services|group|management)\b',
        '', name.lower()
    )
    core = re.sub(r'\s+', ' ', core).strip()
    if len(core) < 3:
        return []

    results = abr_search_name(core)
    propco_kw = ["propert", "holding", "realt", "land", "asset",
                 "invest", "capital", "fund", "trust", "reit", "super"]
    fgc_kw    = ["super fund", "smsf", "unit trust", "property trust",
                 "projects trust", "property maintenance", "holdings trust",
                 "property pty", "realty", "land holdings"]

    related = []
    for r in results:
        entity = str(r.get("Name", "")).strip()
        abn    = str(r.get("Abn", "")).strip()
        score  = fuzz.token_set_ratio(core, entity.lower())
        if score < 60 or abn == base_abn:
            continue
        related.append({
            "entity_name":          entity,
            "abn":                  abn,
            "score":                score,
            "state":                r.get("State", ""),
            "postcode":             r.get("Postcode", ""),
            "is_propco_candidate":  any(kw in entity.lower() for kw in propco_kw),
            "is_fgc_candidate":     any(kw in entity.lower() for kw in fgc_kw),
        })

    related.sort(key=lambda x: x["score"], reverse=True)
    return related[:10]


def load_address_lookup() -> dict:
    if not SNAP_FILE.exists():
        return {}
    try:
        import pandas as pd
        snap = pd.read_csv(SNAP_FILE, dtype=str, low_memory=False)
        snap.columns = [c.strip().lower() for c in snap.columns]
        lookup = {}
        for _, row in snap.iterrows():
            val = {
                "address":  str(row.get("serviceaddress", "") or "").strip(),
                "suburb":   str(row.get("suburb", "") or "").strip(),
                "state":    str(row.get("state", "") or "").strip(),
                "postcode": str(row.get("postcode", "") or "").strip(),
            }
            lookup[str(row.get("servicename", "")).strip().lower()] = val
            appr = str(row.get("serviceapprovalnumber", "") or "").strip()
            if appr:
                lookup[appr] = val
        return lookup
    except Exception as e:
        log.warning(f"Address lookup failed: {e}")
        return {}


# ─────────────────────────────────────────────
# CORE LOOKUP
# ─────────────────────────────────────────────

def lookup_operator(name: str, address_lookup: dict, operators: list) -> dict:
    """Full property research for a single operator."""

    # Find operator in target list
    matches = [
        o for o in operators
        if fuzz.token_set_ratio(name.lower(), str(o.get("legal_name") or "").lower()) > 70
    ]
    if not matches:
        log.warning(f"No operator found matching '{name}'")
        return {}

    # Take best match
    op = max(matches, key=lambda o: fuzz.token_set_ratio(
        name.lower(), str(o.get("legal_name") or "").lower()
    ))

    legal_name = str(op.get("legal_name", "")).strip()
    log.info(f"Found: {legal_name} ({op.get('n_centres',0)} centres, "
             f"{', '.join(op.get('states',[]))})")

    result = {
        "legal_name":          legal_name,
        "n_centres":           op.get("n_centres", 0),
        "states":              op.get("states", []),
        "priority_tier":       op.get("priority_tier", ""),
        "score":               op.get("score", 0),
        "is_nfp":              op.get("is_nfp", False),
        "abr_data":            {},
        "related_entities":    [],
        "propco_candidates":   [],
        "fgc_candidates":      [],
        "freehold_going_concern": False,
        "centres":             [],
        "lookup_date":         str(date.today()),
    }

    # ABR lookup
    if ABR_GUID:
        log.info("Searching ABR...")
        abr_matches = abr_search_name(legal_name, max_results=5)
        for match in abr_matches:
            score = fuzz.token_set_ratio(
                legal_name.lower(),
                str(match.get("Name", "")).lower()
            )
            if score > 80:
                abn = str(match.get("Abn", "")).strip()
                if abn:
                    details = abr_lookup_abn(abn)
                    if details.get("Abn"):
                        result["abr_data"] = {
                            "abn":              details.get("Abn"),
                            "acn":              details.get("Acn"),
                            "entity_name":      details.get("EntityName"),
                            "entity_type":      details.get("EntityTypeName"),
                            "abn_status":       details.get("AbnStatus"),
                            "address_state":    details.get("AddressState"),
                            "address_postcode": details.get("AddressPostcode"),
                            "gst_from":         details.get("Gst"),
                        }
                        base_abn = abn
                        break

        log.info("Searching for related entities...")
        related = find_related_entities(legal_name, result["abr_data"].get("abn",""))
        result["related_entities"]  = related
        result["propco_candidates"] = [r for r in related if r["is_propco_candidate"]]
        result["fgc_candidates"]    = [r for r in related if r["is_fgc_candidate"]]
        result["freehold_going_concern"] = len(result["fgc_candidates"]) > 0

    # Build centre list with title search links
    for c in op.get("centres", []):
        svc_name = str(c.get("service_name", "")).strip()
        suburb   = str(c.get("suburb", "")).strip()
        state    = str(c.get("state", "")).strip()
        postcode = str(c.get("postcode", "")).strip()
        address  = ""
        appr     = str(c.get("approval_number", "")).strip()

        snap = address_lookup.get(svc_name.lower()) or address_lookup.get(appr) or {}
        if snap:
            address  = snap.get("address", "")
            suburb   = snap.get("suburb", "") or suburb
            state    = snap.get("state", "") or state
            postcode = snap.get("postcode", "") or postcode

        result["centres"].append({
            "service_name":      svc_name,
            "address":           address,
            "suburb":            suburb,
            "state":             state,
            "postcode":          postcode,
            "places":            c.get("places", 0),
            "nqs_rating":        str(c.get("nqs_rating", "")).strip(),
            "approval_number":   appr,
            "title_search_url":  title_search_url(state, address, suburb),
            "google_maps_url":   f"https://www.google.com/maps/search/{quote(address+' '+suburb+' '+state)}",
        })

    return result


def print_result(result: dict):
    """Pretty print lookup result to terminal."""
    if not result:
        return

    print("\n" + "="*60)
    print(f"OPERATOR: {result['legal_name']}")
    print(f"Tier: {result['priority_tier'].upper()}  "
          f"Score: {result['score']}  "
          f"Centres: {result['n_centres']}  "
          f"States: {', '.join(result['states'])}")
    print("="*60)

    if result.get("abr_data"):
        d = result["abr_data"]
        print(f"\nABR RECORD:")
        print(f"  ABN:         {d.get('abn')}")
        print(f"  ACN:         {d.get('acn')}")
        print(f"  Entity type: {d.get('entity_type')}")
        print(f"  Status:      {d.get('abn_status')}")
        print(f"  Address:     {d.get('address_state')} {d.get('address_postcode')}")
        print(f"  GST from:    {d.get('gst_from')}")

    if result.get("freehold_going_concern"):
        print(f"\n*** FREEHOLD GOING CONCERN CANDIDATES DETECTED ***")

    if result.get("propco_candidates"):
        print(f"\nRELATED ENTITIES (PropCo candidates):")
        for e in result["propco_candidates"]:
            fgc = " *** FGC ***" if e.get("is_fgc_candidate") else ""
            print(f"  {e['entity_name']}")
            print(f"    ABN: {e['abn']}  Score: {e['score']:.0f}%  "
                  f"{e.get('state','')} {e.get('postcode','')}{fgc}")

    if result.get("related_entities"):
        non_propco = [e for e in result["related_entities"]
                      if not e.get("is_propco_candidate")]
        if non_propco:
            print(f"\nOTHER RELATED ENTITIES:")
            for e in non_propco[:5]:
                print(f"  {e['entity_name']} (ABN: {e['abn']})")

    print(f"\nCENTRES ({len(result.get('centres',[]))}) — with title search links:")
    for c in result.get("centres", []):
        print(f"\n  {c['service_name']}")
        if c.get("address"):
            print(f"  {c['address']}, {c['suburb']} {c['state']} {c['postcode']}")
        else:
            print(f"  {c['suburb']}, {c['state']} {c['postcode']}")
        print(f"  Places: {c['places']}  NQS: {c.get('nqs_rating','-')}")
        print(f"  Title search: {c['title_search_url']}")
        print(f"  Google Maps:  {c['google_maps_url']}")

    print()


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def run():
    parser = argparse.ArgumentParser(
        description="On-demand operator property research"
    )
    parser.add_argument("operator", nargs="?", default="",
                        help="Operator name to look up")
    parser.add_argument("--list",  action="store_true",
                        help="List all cached lookups")
    parser.add_argument("--clear", action="store_true",
                        help="Clear lookup cache")
    args = parser.parse_args()

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    if args.list:
        cached = list(CACHE_DIR.glob("*.json"))
        if not cached:
            print("No cached lookups yet.")
        else:
            print(f"\n{len(cached)} cached operator lookups:")
            for f in sorted(cached):
                data = json.loads(f.read_text(encoding="utf-8"))
                fgc = " *** FGC ***" if data.get("freehold_going_concern") else ""
                print(f"  {data.get('legal_name','?')} "
                      f"({data.get('n_centres',0)} centres, "
                      f"{data.get('lookup_date','')}){fgc}")
        return

    if args.clear:
        for f in CACHE_DIR.glob("*.json"):
            f.unlink()
        print("Cache cleared.")
        return

    if not args.operator:
        parser.print_help()
        return

    if not ABR_GUID:
        print("WARNING: ABR_GUID not set in .env — ABR lookups disabled")
        print("Add ABR_GUID=your-guid to .env")

    # Check cache first
    cache_key = re.sub(r'[^\w]', '_', args.operator.lower())[:50]
    cache_file = CACHE_DIR / f"{cache_key}.json"

    if cache_file.exists():
        print(f"[Cache hit — loaded from {cache_file.name}]")
        result = json.loads(cache_file.read_text(encoding="utf-8"))
        print_result(result)
        return

    # Load reference data
    log.info("Loading reference data...")
    address_lookup = load_address_lookup()
    log.info(f"Address lookup: {len(address_lookup):,} entries")

    if not TARGETS_FILE.exists():
        log.error("operators_target_list.json not found — run module2c first")
        return

    operators = json.load(open(TARGETS_FILE, encoding="utf-8"))
    log.info(f"Operators: {len(operators):,}")

    # Run lookup
    result = lookup_operator(args.operator, address_lookup, operators)

    if result:
        # Cache result
        cache_file.write_text(
            json.dumps(result, indent=2, default=str),
            encoding="utf-8"
        )
        print_result(result)
        print(f"[Saved to cache: {cache_file}]")
    else:
        print(f"No results found for '{args.operator}'")
        print("Try a partial name, e.g.: python lookup_operator.py Wallaby")


if __name__ == "__main__":
    run()
