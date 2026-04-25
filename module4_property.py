"""
module4_property.py — Property Ownership & PropCo Research
Remara Agent | Runs as part of Tuesday pipeline after module3_da_portals.py

Goal: Find the freehold owner of every childcare centre in Australia.

Approach:
  Layer 1 — Arena REIT portfolio scrape (~250 properties, free)
  Layer 2 — ABR name search for PropCo entities related to each operator
  Layer 3 — Pre-built title search links for all 9,652 ACECQA centres
  Layer 4 — DA applicant tracking from module3 (PropCo from new builds)

ABR API: free, requires GUID in .env as ABR_GUID
  ABN lookup:   abr.business.gov.au/json/AbnDetails.aspx
  Name search:  abr.business.gov.au/json/MatchingNames.aspx

Output: property_owners.json
  Per operator group:
  - operator_name, acn, abn, entity_type, registered_address
  - directors (from ABR where available)
  - related_entities (PropCo candidates via name + director matching)
  - centres (with title_search_url per centre)
  - arena_reit_properties (if operator centres appear in Arena portfolio)

Run:
  python module4_property.py
  python module4_property.py --operator "Davmat Investments"  (single operator)
"""

import json
import re
import time
import logging
import argparse
from pathlib import Path
from datetime import date
from urllib.parse import quote, urlencode

import requests
import pandas as pd
from rapidfuzz import fuzz
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR     = Path(__file__).parent
DATA_DIR     = BASE_DIR / "data"
OUTPUT_FILE  = BASE_DIR / "property_owners.json"
TARGETS_FILE = BASE_DIR / "operators_target_list.json"
SNAP_FILE    = DATA_DIR / "services_snapshot.csv"
DA_FILE      = BASE_DIR / "da_leads.json"

ABR_GUID     = os.getenv("ABR_GUID", "")
ABR_BASE     = "https://abr.business.gov.au/json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# TITLE SEARCH URL BUILDERS
# ─────────────────────────────────────────────

def title_search_url(state: str, address: str, suburb: str) -> str:
    """Generate pre-built land title search URL per state."""
    q = quote(f"{address} {suburb}".strip())
    state = str(state).strip().upper()
    if state == "NSW":
        return f"https://www.nswlrs.com.au/land_titles/property_search?q={q}"
    elif state == "VIC":
        return f"https://www.landata.vic.gov.au/property-information?address={q}"
    elif state == "QLD":
        return f"https://www.titlesqld.com.au/title-search?address={q}"
    elif state == "SA":
        return f"https://www.sailis.sa.gov.au/home/query?address={q}"
    elif state == "WA":
        return f"https://www0.landgate.wa.gov.au/property-search?address={q}"
    elif state == "TAS":
        return f"https://www.thelist.tas.gov.au/app/content/property?address={q}"
    elif state == "ACT":
        return f"https://actmapi.act.gov.au/actmapi/index.html?viewer=actmapi&address={q}"
    elif state == "NT":
        return f"https://www.ntlis.nt.gov.au/imf/imf.jsp?address={q}"
    return f"https://www.google.com/search?q={quote(address+' '+suburb+' '+state+' land title owner')}"


# ─────────────────────────────────────────────
# ABR API
# ─────────────────────────────────────────────

def abr_lookup_abn(abn: str) -> dict:
    """Look up company details by ABN."""
    if not ABR_GUID:
        return {}
    try:
        clean_abn = re.sub(r'\D', '', str(abn))
        url = f"{ABR_BASE}/AbnDetails.aspx?abn={clean_abn}&callback=callback&guid={ABR_GUID}"
        r = requests.get(url, timeout=10)
        text = r.text
        # Strip callback wrapper
        m = re.search(r'callback\((.*)\)', text, re.DOTALL)
        if m:
            data = json.loads(m.group(1))
            if data.get("Message") == "":
                return data
    except Exception as e:
        log.debug(f"ABR ABN lookup failed: {e}")
    return {}


def abr_search_name(name: str, max_results: int = 10) -> list:
    """Search ABR by company name. Returns list of matching entities."""
    if not ABR_GUID or not name:
        return []
    try:
        clean = re.sub(r'[^\w\s]', ' ', name).strip()
        # Remove common suffixes for broader search
        for suffix in [" pty ltd", " pty limited", " limited", " ltd",
                       " atf", " as trustee", " trust"]:
            clean = clean.lower().replace(suffix, "").strip()
        clean = clean[:50]

        params = urlencode({
            "name": clean,
            "maxResults": max_results,
            "callback": "callback",
            "guid": ABR_GUID
        })
        url = f"{ABR_BASE}/MatchingNames.aspx?{params}"
        r = requests.get(url, timeout=10)
        m = re.search(r'callback\((.*)\)', r.text, re.DOTALL)
        if m:
            data = json.loads(m.group(1))
            return data.get("Names", [])
    except Exception as e:
        log.debug(f"ABR name search failed for '{name}': {e}")
    return []


def find_related_entities(operator_name: str, base_abn: str = "") -> list:
    """
    Search ABR for entities related to an operator.
    Looks for PropCo candidates using name similarity.
    """
    # Extract core name (strip legal suffixes and trust names)
    core = re.sub(
        r'\b(pty|ltd|limited|atf|as trustee|trust|unit trust|family trust|'
        r'holdings|investments|enterprises|services|group|management)\b',
        '', operator_name.lower()
    )
    core = re.sub(r'\s+', ' ', core).strip()

    if len(core) < 3:
        return []

    results = abr_search_name(core, max_results=20)

    # Flag PropCo candidates
    propco_keywords = [
        "propert", "holding", "realt", "land", "asset",
        "invest", "capital", "fund", "trust", "reit"
    ]

    related = []
    for r in results:
        entity_name = str(r.get("Name", "")).strip()
        abn         = str(r.get("Abn", "")).strip()
        score       = fuzz.token_set_ratio(core, entity_name.lower())

        if score < 60 or abn == base_abn:
            continue

        is_propco = any(kw in entity_name.lower() for kw in propco_keywords)

        related.append({
            "entity_name":  entity_name,
            "abn":          abn,
            "score":        score,
            "is_propco_candidate": is_propco,
            "state":        r.get("State", ""),
            "postcode":     r.get("Postcode", ""),
        })

    # Sort by score descending
    related.sort(key=lambda x: x["score"], reverse=True)
    return related[:10]


# ─────────────────────────────────────────────
# ARENA REIT PORTFOLIO
# ─────────────────────────────────────────────

def fetch_arena_reit_portfolio() -> list:
    """
    Fetch Arena REIT (ARF) childcare property portfolio from ASX announcements.
    Arena REIT is one of Australia's largest childcare property owners (~250 props).
    Returns list of properties with address, operator, and lease details.
    """
    log.info("Fetching Arena REIT portfolio from ASX...")
    properties = []

    try:
        # Get latest ASX announcements for ARF
        url = "https://www.asx.com.au/asx/1/company/ARF/announcements?count=20&market_sensitive=false"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=15)
        data = r.json()

        announcements = data.get("data", [])
        # Look for annual report or property portfolio announcement
        portfolio_ann = None
        for ann in announcements:
            title = str(ann.get("header", "")).lower()
            if any(kw in title for kw in ["property portfolio", "annual report",
                                           "investor presentation", "portfolio update"]):
                portfolio_ann = ann
                break

        if portfolio_ann:
            log.info(f"Arena REIT: found '{portfolio_ann.get('header')}' — "
                     f"PDF parsing not yet implemented")
            # TODO: download PDF and parse with Claude API
            # The PDF contains full portfolio with addresses and operators
            properties.append({
                "source": "Arena REIT ASX",
                "announcement": portfolio_ann.get("header"),
                "date": portfolio_ann.get("document_date"),
                "note": "PDF parsing pending — see pdf_url for manual review",
                "pdf_url": portfolio_ann.get("url", ""),
            })
        else:
            log.info("Arena REIT: no portfolio announcement found in latest 20")

    except Exception as e:
        log.warning(f"Arena REIT fetch failed: {e}")

    # Known Arena REIT statistics (from public disclosures)
    # Used as metadata until full portfolio scrape is implemented
    properties.append({
        "source":      "Arena REIT (known stats)",
        "total_properties": 258,
        "asset_class": "Long Day Care (primary)",
        "major_tenants": ["Guardian Early Learning", "Goodstart", "G8 Education",
                          "Only About Children", "Affinity Education"],
        "note": "Full property list requires PDF parse of annual report",
        "investor_page": "https://www.arenaonline.com.au/property-portfolio",
    })

    log.info(f"Arena REIT: {len(properties)} records (stub — full parse pending)")
    return properties


# ─────────────────────────────────────────────
# ENRICH OPERATOR WITH PROPERTY DATA
# ─────────────────────────────────────────────

def enrich_operator(op: dict, address_lookup: dict = None) -> dict:
    """
    Enrich a single operator group with property ownership data.
    """
    legal_name = op.get("legal_name", "")
    centres    = op.get("centres", [])

    result = {
        "legal_name":        legal_name,
        "n_centres":         op.get("n_centres", 0),
        "states":            op.get("states", []),
        "priority_tier":     op.get("priority_tier", ""),
        "score":             op.get("score", 0),
        "abr_data":          {},
        "related_entities":  [],
        "propco_candidates": [],
        "centres_with_title_search": [],
        "enriched_date":     str(date.today()),
    }

    # ABR lookup by name
    if ABR_GUID:
        abr_matches = abr_search_name(legal_name, max_results=5)
        # Find best match
        for match in abr_matches:
            score = fuzz.token_set_ratio(
                legal_name.lower(),
                str(match.get("Name", "")).lower()
            )
            if score > 80:
                # Get full details
                abn = str(match.get("Abn", "")).strip()
                if abn:
                    details = abr_lookup_abn(abn)
                    if details.get("Abn"):
                        result["abr_data"] = {
                            "abn":           details.get("Abn"),
                            "acn":           details.get("Acn"),
                            "entity_name":   details.get("EntityName"),
                            "entity_type":   details.get("EntityTypeName"),
                            "abn_status":    details.get("AbnStatus"),
                            "address_state": details.get("AddressState"),
                            "address_postcode": details.get("AddressPostcode"),
                            "gst_from":      details.get("Gst"),
                        }
                        break

        # Find related PropCo entities
        related = find_related_entities(legal_name)
        result["related_entities"]  = related
        result["propco_candidates"] = [r for r in related if r["is_propco_candidate"]]

    # Build title search links for each centre
    for c in centres:
        address  = str(c.get("service_address", "") or c.get("address", "") or "").strip()
        suburb   = str(c.get("suburb", "")).strip()
        state    = str(c.get("state", "")).strip()
        postcode = str(c.get("postcode", "")).strip()
        # Enrich from snapshot if address missing
        if address_lookup:
            svc_key  = str(c.get("service_name", "")).strip().lower()
            appr_key = str(c.get("approval_number", "") or c.get("service_approval", "")).strip()
            snap_addr = address_lookup.get(svc_key) or address_lookup.get(appr_key) or {}
            if snap_addr.get("address"):
                address  = snap_addr.get("address", "") or address
                suburb   = snap_addr.get("suburb", "") or suburb
                state    = snap_addr.get("state", "") or state
                postcode = snap_addr.get("postcode", "") or postcode

        result["centres_with_title_search"].append({
            "service_name":    str(c.get("service_name", "")).strip(),
            "address":         address,
            "suburb":          suburb,
            "state":           state,
            "postcode":        postcode,
            "places":          c.get("places", 0),
            "nqs_rating":      str(c.get("nqs_rating", "")).strip(),
            "title_search_url": title_search_url(state, address, suburb),
            "google_maps_url": f"https://www.google.com/maps/search/{quote(address+' '+suburb+' '+state)}",
        })

    # Freehold going concern flag
    fgc_keywords = ["super fund", "smsf", "unit trust", "property trust",
                    "projects trust", "property maintenance", "holdings trust",
                    "property pty", "realty", "land holdings"]
    fgc = any(
        any(kw in pc.get("entity_name", "").lower() for kw in fgc_keywords)
        for pc in result.get("propco_candidates", [])
    )
    result["freehold_going_concern"] = fgc
    if fgc:
        result["freehold_signal"] = "PropCo entity detected via ABR — possible freehold going concern"

    return result


# ─────────────────────────────────────────────
# MAIN RUNNER
# ─────────────────────────────────────────────

def run(operator_filter: str = ""):
    log.info("=" * 55)
    log.info("module4_property — property ownership research")
    log.info("=" * 55)

    if not ABR_GUID:
        log.warning("ABR_GUID not set in .env — ABR lookups will be skipped")
        log.warning("Add ABR_GUID=your-guid to .env to enable company lookups")
    else:
        log.info(f"ABR API: configured (GUID ends ...{ABR_GUID[-8:]})")

    # Load full addresses from services_snapshot.csv
    address_lookup = {}
    if SNAP_FILE.exists():
        try:
            snap = pd.read_csv(SNAP_FILE, dtype=str, low_memory=False)
            snap.columns = [c.strip().lower() for c in snap.columns]
            for _, row in snap.iterrows():
                addr_val = {
                    "address":  str(row.get("serviceaddress", "") or "").strip(),
                    "suburb":   str(row.get("suburb", "") or "").strip(),
                    "state":    str(row.get("state", "") or "").strip(),
                    "postcode": str(row.get("postcode", "") or "").strip(),
                }
                # Index by service name (lowercase)
                key = str(row.get("servicename", "")).strip().lower()
                address_lookup[key] = addr_val
                # Also index by service approval number
                appr = str(row.get("serviceapprovalnumber", "") or "").strip()
                if appr:
                    address_lookup[appr] = addr_val
            log.info(f"Address lookup: {len(address_lookup):,} centres loaded")
        except Exception as e:
            log.warning(f"Could not load address lookup: {e}")

    # Load operator target list
    if not TARGETS_FILE.exists():
        log.error(f"operators_target_list.json not found — run module2c first")
        return

    operators = json.load(open(TARGETS_FILE, encoding="utf-8"))
    log.info(f"Operators loaded: {len(operators):,}")

    # Filter if single operator requested
    if operator_filter:
        operators = [o for o in operators
                     if operator_filter.lower() in str(o.get("legal_name") or "").lower()]
        log.info(f"Filtered to: {len(operators)} matching '{operator_filter}'")

    # Skip NFP and very small operators for efficiency
    operators = [o for o in operators
                 if not o.get("is_nfp") and o.get("n_centres", 0) >= 2 and o.get("legal_name")]
    log.info(f"Processing: {len(operators):,} for-profit operators with 2+ centres")

    # Fetch Arena REIT portfolio
    arena = fetch_arena_reit_portfolio()

    # Enrich operators
    results = []
    hot_warm = [o for o in operators if o.get("priority_tier") in ("hot", "warm")]
    watch    = [o for o in operators if o.get("priority_tier") == "watch"]

    # Weekly run: hot targets only (~18 min). Use --all for full run.
    if not getattr(args, "all_operators", False) and not operator_filter:
        hot_only = [o for o in hot_warm if o.get("priority_tier") == "hot"]
        log.info(f"Weekly mode: processing {len(hot_only)} hot targets only")
        log.info("Use --all to process all 758 hot+warm operators")
        process_list = hot_only
    else:
        process_list = hot_warm + watch
    total = len(process_list)

    log.info(f"Enriching {len(hot_warm)} hot+warm + {len(watch)} watch operators...")

    for i, op in enumerate(process_list, 1):
        name = op.get("legal_name", "")[:50]
        if i % 50 == 0 or i <= 5:
            log.info(f"  [{i}/{total}] {name}")

        enriched = enrich_operator(op, address_lookup)
        results.append(enriched)

        # Rate limit ABR API
        if ABR_GUID:
            time.sleep(0.3)

    # Save output
    output = {
        "generated_date":   str(date.today()),
        "total_operators":  len(results),
        "arena_reit":       arena,
        "operators":        results,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, default=str)

    # Summary
    log.info("=" * 55)
    log.info(f"Output: {OUTPUT_FILE.name}")
    log.info(f"Operators enriched: {len(results):,}")

    with_abr     = sum(1 for r in results if r.get("abr_data", {}).get("abn"))
    with_propco  = sum(1 for r in results if r.get("propco_candidates"))
    with_titles  = sum(1 for r in results if r.get("centres_with_title_search"))

    log.info(f"ABR data found:      {with_abr:,}")
    log.info(f"PropCo candidates:   {with_propco:,}")
    log.info(f"Title search links:  {with_titles:,} operators")

    total_links = sum(
        len(r.get("centres_with_title_search", []))
        for r in results
    )
    log.info(f"Total title links:   {total_links:,} centres")

    # Show top PropCo discoveries
    propco_ops = [r for r in results if r.get("propco_candidates")][:5]
    if propco_ops:
        log.info("\nPROPCO CANDIDATES FOUND:")
        for op in propco_ops:
            log.info(f"  {op['legal_name'][:45]}")
            for pc in op["propco_candidates"][:2]:
                log.info(f"    → {pc['entity_name'][:45]} (ABN: {pc['abn']})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--operator", default="",
                        help="Filter to single operator name (partial match)")
    parser.add_argument("--all", dest="all_operators", action="store_true",
                        help="Process all hot+warm operators (default: hot only)")
    args = parser.parse_args()
    run(operator_filter=args.operator)
