"""
module3_da_portals.py — Childcare DA Pipeline Monitor
Remara Agent | Run after module2b_catchment.py

Monitors childcare development applications across NSW, VIC and QLD.

Current implementation (Track A):
  - Claude web search daily scan per state
  - Structured JSON extraction from search results
  - Cross-reference against ACECQA operators + hot targets

Track B (to add):
  - NSW: Data Broker API (email request to NSW Planning Portal pending)
  - NSW: ACA NSW Development Watch feed (Remara is ACA member)
  - VIC: Council scrapers — Casey, Wyndham, Melton, Hume, Whittlesea
  - QLD: Council scrapers — Brisbane, Gold Coast, Sunshine Coast,
          Moreton Bay, Logan

Output: da_leads.json
  Fields per lead: state, council, address, suburb, postcode,
  applicant_name, development_type, description, places, da_number,
  da_status, lodgement_date, decision_date, title_search_url,
  acecqa_match, target_match, matched_name, remara_signal

Run:
  python module3_da_portals.py
"""

import json
import re
import time
import logging
from pathlib import Path
from datetime import datetime, date, timedelta

import requests
from rapidfuzz import fuzz

BASE_DIR     = Path(__file__).parent
DATA_DIR     = BASE_DIR / "data"
OUTPUT_FILE  = BASE_DIR / "da_leads.json"
CACHE_FILE   = DATA_DIR / "da_cache.json"
SNAP_FILE    = DATA_DIR / "services_snapshot.csv"
TARGETS_FILE = BASE_DIR / "operators_hot_targets.json"

LOOKBACK_DAYS = 30

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def clean(v) -> str:
    s = str(v or "").strip()
    return "" if s.lower() in ("nan", "none") else s


def extract_places(text: str) -> int | None:
    for pat in [
        r"(\d+)\s*(?:licensed\s+)?places",
        r"(\d+)\s*(?:child\s+)?(?:care\s+)?(?:spaces|positions)",
        r"capacity\s+(?:of\s+)?(\d+)",
        r"(\d+)\s*children",
        r"(\d+)[- ]place",
    ]:
        m = re.search(pat, str(text).lower())
        if m:
            n = int(m.group(1))
            if 10 <= n <= 500:
                return n
    return None


def title_search_url(state: str, address: str, suburb: str) -> str:
    q = requests.utils.quote(f"{address} {suburb}".strip())
    if state == "NSW":
        return f"https://www.nswlrs.com.au/land_titles/property_search?q={q}"
    elif state == "VIC":
        return f"https://www.landata.vic.gov.au/property-information?address={q}"
    elif state == "QLD":
        return f"https://www.titlesqld.com.au/title-search?address={q}"
    return ""


def load_known_operators() -> list:
    if not SNAP_FILE.exists():
        return []
    try:
        import pandas as pd
        df = pd.read_csv(SNAP_FILE, dtype=str, low_memory=False)
        df.columns = [c.strip().lower() for c in df.columns]
        names = []
        for col in ["servicename", "providerlegalname"]:
            if col in df.columns:
                names += df[col].dropna().str.strip().str.lower().tolist()
        return list(set(names))
    except Exception as e:
        log.warning(f"Could not load operators: {e}")
        return []


def load_hot_targets() -> list:
    if not TARGETS_FILE.exists():
        return []
    try:
        return json.load(open(TARGETS_FILE, encoding="utf-8"))
    except Exception:
        return []


def match_to_known(applicant: str, known: list, targets: list) -> dict:
    if not applicant:
        return {"acecqa_match": False, "target_match": False, "matched_name": None}
    app = applicant.lower().strip()

    # Sample known operators for speed (fuzzy match is slow on 18k names)
    acecqa_match = any(
        fuzz.token_set_ratio(app, op) > 82
        for op in known[:3000]
    )

    target_match = False
    matched_name = None
    for t in targets:
        if fuzz.token_set_ratio(app, t.get("legal_name", "").lower()) > 82:
            target_match = True
            matched_name = t.get("legal_name")
            break

    return {
        "acecqa_match":  acecqa_match,
        "target_match":  target_match,
        "matched_name":  matched_name,
    }


def load_cache() -> dict:
    if CACHE_FILE.exists():
        try:
            return json.load(open(CACHE_FILE, encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_cache(cache: dict):
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    json.dump(cache, open(CACHE_FILE, "w", encoding="utf-8"), indent=2, default=str)


# ─────────────────────────────────────────────
# TRACK A — Claude web search
# ─────────────────────────────────────────────

STATE_PROMPTS = {
    "NSW": (
        "Search for new childcare centre or long day care development applications "
        "in NSW Australia lodged in the last 30 days. Search NSW Planning Portal "
        "application tracker, council DA search pages, and planning news. "
        "You MUST return results as a raw JSON array only — no prose, no markdown, "
        "no explanation. Start your response with [ and end with ]. "
        "Each item must have: applicant_name, address, suburb, state, council, "
        "places (integer or null), da_number, da_status, lodgement_date, "
        "description, source_url."
    ),
    "VIC": (
        "Search for new childcare centre or long day care planning permit applications "
        "in Victoria Australia lodged in the last 30 days. Search VicPlan, Casey, "
        "Wyndham, Melton, Hume council planning pages, and planning news. "
        "You MUST return results as a raw JSON array only — no prose, no markdown, "
        "no explanation. Start your response with [ and end with ]. "
        "Each item must have: applicant_name, address, suburb, state, council, "
        "places (integer or null), da_number, da_status, lodgement_date, "
        "description, source_url."
    ),
    "QLD": (
        "Search for new childcare centre or long day care development applications "
        "in Queensland Australia lodged in the last 30 days. Search Brisbane, "
        "Gold Coast, Sunshine Coast, Moreton Bay, Logan council DA search pages "
        "and planning news. "
        "You MUST return results as a raw JSON array only — no prose, no markdown, "
        "no explanation. Start your response with [ and end with ]. "
        "Each item must have: applicant_name, address, suburb, state, council, "
        "places (integer or null), da_number, da_status, lodgement_date, "
        "description, source_url."
    ),
}


def search_state_das(state: str, cache: dict) -> list:
    """Use Claude web search to find recent childcare DAs in a state."""
    import anthropic
    from dotenv import load_dotenv
    load_dotenv()

    # Check cache — don't re-search same state on same day
    today = str(date.today())
    cache_key = f"{state}_{today}"
    if cache_key in cache:
        log.info(f"{state}: using cached results ({len(cache[cache_key])} leads)")
        return cache[cache_key]

    log.info(f"{state}: searching via Claude web search...")
    client = anthropic.Anthropic()

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[{"role": "user", "content": STATE_PROMPTS[state]}],
        )

        # Extract text blocks from response
        full_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                full_text += block.text

        # Parse JSON from response — try multiple extraction strategies
        leads = []
        # Log raw response for debugging
        log.debug(f"{state} raw response: {full_text[:300]}")
        
        # Strategy 1: find JSON array in response
        json_match = re.search(r'\[.*\]', full_text, re.DOTALL)
        if not json_match:
            # Strategy 2: response might BE the JSON
            stripped = full_text.strip()
            if stripped.startswith('['):
                json_match = type('Match', (), {'group': lambda self: stripped})()
        if json_match:
            try:
                items = json.loads(json_match.group())
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    address = clean(item.get("address", ""))
                    suburb  = clean(item.get("suburb", ""))
                    desc    = clean(item.get("description", ""))
                    leads.append({
                        "state":            state,
                        "council":          clean(item.get("council", "")),
                        "address":          address,
                        "suburb":           suburb,
                        "postcode":         clean(item.get("postcode", "")),
                        "applicant_name":   clean(item.get("applicant_name", "")),
                        "development_type": "Child Care Centre",
                        "description":      desc,
                        "places":           item.get("places") or extract_places(desc),
                        "da_number":        clean(item.get("da_number", "")),
                        "da_status":        clean(item.get("da_status", "")),
                        "lodgement_date":   clean(item.get("lodgement_date", "")),
                        "decision_date":    "",
                        "title_search_url": title_search_url(state, address, suburb),
                        "source_url":       clean(item.get("source_url", "")),
                        "source":           f"{state} web search",
                    })
                log.info(f"{state}: {len(leads)} DAs found")
            except json.JSONDecodeError as e:
                log.warning(f"{state}: JSON parse error: {e}")
                log.debug(f"Raw response: {full_text[:500]}")
        else:
            log.warning(f"{state}: no JSON array found in response")
            log.debug(f"Response text: {full_text[:300]}")

        # Cache results
        cache[cache_key] = leads
        save_cache(cache)

        time.sleep(15)  # delay between states to avoid rate limits
        return leads

    except Exception as e:
        log.warning(f"{state}: web search failed: {e}")
        return []


# ─────────────────────────────────────────────
# TRACK B STUBS — to implement
# ─────────────────────────────────────────────

def fetch_nsw_data_broker() -> list:
    """
    TRACK B: NSW Planning Portal Data Broker API.
    Requires email registration: datansw@planning.nsw.gov.au
    Free access, provides full DA feed since 2019.
    TODO: implement once API access approved.
    """
    log.info("NSW Data Broker API: not yet configured (pending registration)")
    return []


def fetch_aca_nsw_development_watch() -> list:
    """
    TRACK B: ACA NSW Development Watch daily feed.
    Remara is an ACA NSW member — credentials needed.
    URL: https://nsw.childcarealliance.org.au/services/childcare-development-watch
    TODO: implement with ACA member login credentials.
    """
    log.info("ACA NSW Development Watch: not yet configured (add member credentials)")
    return []


def fetch_council_scraper(council: str, state: str) -> list:
    """
    TRACK B: Individual council planning portal scraper.
    TODO: implement for high-volume councils:
      VIC: Casey, Wyndham, Melton, Hume, Whittlesea
      QLD: Brisbane, Gold Coast, Sunshine Coast, Moreton Bay, Logan
    """
    log.info(f"{council} ({state}) scraper: not yet implemented")
    return []


# ─────────────────────────────────────────────
# DEDUPLICATION
# ─────────────────────────────────────────────

def deduplicate(leads: list) -> list:
    """Remove duplicate DAs by address + state."""
    seen = set()
    unique = []
    for lead in leads:
        key = f"{lead['state']}:{lead['address'].lower()}:{lead['suburb'].lower()}"
        if key not in seen and lead['address']:
            seen.add(key)
            unique.append(lead)
    return unique


# ─────────────────────────────────────────────
# MAIN RUNNER
# ─────────────────────────────────────────────

def run():
    log.info("=" * 55)
    log.info("module3_da_portals — childcare DA monitor")
    log.info("=" * 55)

    # Load reference data
    log.info("Loading reference data...")
    known    = load_known_operators()
    targets  = load_hot_targets()
    cache    = load_cache()
    log.info(f"Known operators: {len(known):,}  Hot targets: {len(targets):,}")

    all_leads = []

    # Track A: web search per state
    for state in ["NSW", "VIC", "QLD"]:
        all_leads.extend(search_state_das(state, cache))

    # Track B stubs (currently return empty)
    all_leads.extend(fetch_nsw_data_broker())
    all_leads.extend(fetch_aca_nsw_development_watch())

    # Deduplicate
    all_leads = deduplicate(all_leads)
    log.info(f"Total unique DA leads: {len(all_leads)}")

    # Cross-reference and score
    priority = {"HOT": 0, "WARM": 1, "WATCH": 2, "monitor": 3}
    for lead in all_leads:
        match = match_to_known(lead.get("applicant_name", ""), known, targets)
        lead.update(match)

        places = lead.get("places") or 0
        if lead.get("target_match"):
            lead["remara_signal"] = "HOT — known target operator"
        elif lead.get("acecqa_match"):
            lead["remara_signal"] = "WARM — existing operator expanding"
        elif places >= 80:
            lead["remara_signal"] = "WATCH — large new centre"
        elif places >= 50:
            lead["remara_signal"] = "WATCH — medium new centre"
        else:
            lead["remara_signal"] = "monitor"

        lead["enriched_date"] = datetime.now().isoformat()

    # Sort by priority
    all_leads.sort(
        key=lambda x: priority.get(
            x.get("remara_signal", "monitor").split(" ")[0], 3
        )
    )

    # Save
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_leads, f, indent=2, default=str)

    # Summary
    log.info("=" * 55)
    log.info(f"Output: {OUTPUT_FILE.name} ({len(all_leads)} leads)")
    for sig in ["HOT", "WARM", "WATCH", "monitor"]:
        n = sum(1 for l in all_leads if l.get("remara_signal","").startswith(sig))
        if n:
            log.info(f"  {sig}: {n}")

    top = [l for l in all_leads
           if l.get("remara_signal","").startswith(("HOT","WARM","WATCH"))][:10]
    if top:
        log.info("\nTOP DA LEADS:")
        for l in top:
            places_str = f"{l['places']}pl" if l.get("places") else "?pl"
            log.info(
                f"  [{l['state']}] {l.get('applicant_name','Unknown')[:35]:<35} "
                f"{l.get('suburb',''):<18} {places_str:<6} "
                f"[{l.get('remara_signal','').split(' ')[0]}]"
            )
    else:
        log.info("No significant DA leads found today")

    log.info(f"\nTrack B to add:")
    log.info(f"  NSW Data Broker API: email datansw@planning.nsw.gov.au")
    log.info(f"  ACA NSW Dev Watch: add member credentials to .env")


if __name__ == "__main__":
    run()
