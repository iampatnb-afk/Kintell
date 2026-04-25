"""
module2c_targeting.py — Operator Group Scoring & Target List
Remara Agent | Run after module1_acecqa.py

Reads ACECQA services_snapshot.csv, infers operator groups using
tiered matching, scores each group against Remara target criteria,
and outputs a ranked target list.

Group inference tiers:
  confirmed     — same provider_approval_number
  high          — exact legal/trading name match across provider numbers
  medium        — fuzzy name match >85% OR same HO address
  review        — fuzzy name 70-85% OR same phone OR partial name

Scoring (100 pts):
  Centre count band      25 pts  (5-10 = 25, 3-4 or 11-12 = 15, 13-15 = 5)
  For-profit             20 pts
  NQS quality            20 pts  (all Meeting+ = 20, majority = 12, mixed = 5)
  Geographic focus       15 pts  (1 state = 15, 2 = 10, 3+ = 3)
  Growth signal          15 pts  (new centre <2 yrs = 15, <4 yrs = 8, stable = 3)
  Not existing client     5 pts

Outputs:
  operators_target_list.json   — all for-profit groups with 2+ centres, scored
  operators_hot_targets.json   — score >= 60, ready for outreach

Run:
  python module2c_targeting.py
"""

import json
import re
import logging
from pathlib import Path
from datetime import datetime, date
from collections import defaultdict

import pandas as pd
from rapidfuzz import fuzz, process

BASE_DIR   = Path(__file__).parent
DATA_DIR   = BASE_DIR / "data"
OUTPUT_ALL = BASE_DIR / "operators_target_list.json"
OUTPUT_HOT = BASE_DIR / "operators_hot_targets.json"
CRM_FILE   = BASE_DIR / "crm_clients.csv"
SNAP_FILE  = DATA_DIR / "services_snapshot.csv"

HOT_THRESHOLD    = 60
FUZZY_HIGH       = 88   # high confidence fuzzy match
FUZZY_MEDIUM     = 75   # medium confidence fuzzy match

NFP_KEYWORDS = [
    # Legal structure indicators
    "incorporated", " inc ", "association", "cooperative", "co-operative",
    "limited by guarantee", "society", "foundation", "charity",
    # Religious operators
    "church", "diocese", "parish", "cathedral", "adventist", "salvation",
    "catholic", "anglican", "uniting", "baptist", "lutheran", "presbyterian",
    "methodist", "quaker", "jewish", "islamic", "muslim", "buddhist",
    "christian", "scripture", "gospel", "mission",
    # Government / council
    "government", "department", "shire", "city of", "town of", "council",
    "municipal", "state government", "tafe",
    # Known NFP brands / structures
    "ymca", "ywca", "gowrie", "uplyft", "goodstart", "snowy",
    "neighbourhood", "aboriginal", "indigenous", " trust",
    "community", "welfare", "family services", "family support",
    # School operators (usually NFP)
    " school", "schools", "college", "academy", "montessori school",
    "steiner school", "waldorf",
]

# Known NFP operators that slip through keyword matching
# Add names here as you discover them — lowercase, partial match ok
NFP_MANUAL_EXCLUSIONS = [
    "lady gowrie",
    "goodstart",
    "g8 education",   # actually for-profit but add if needed
    "only about children",  # for-profit — remove if misclassified
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def is_nfp(name: str) -> bool:
    n = str(name).lower()
    # Check manual exclusions first
    if any(excl in n for excl in NFP_MANUAL_EXCLUSIONS):
        return True
    # Check keyword list
    if any(kw in n for kw in NFP_KEYWORDS):
        return True
    # "Limited" without "Pty" is often a company limited by guarantee (NFP)
    # BUT "Pty Limited" and "Pty. Limited" are valid for-profit structures
    if " limited" in n:
        if any(fp in n for fp in ["pty limited", "pty. limited", "pty ltd", "proprietary limited"]):
            pass  # for-profit structure, not NFP
        else:
            return True
    return False


def normalise_name(name: str) -> str:
    """Normalise operator name for matching."""
    n = str(name).lower().strip()
    # Remove common suffixes that vary between entities
    for suffix in [
        " pty ltd", " pty. ltd.", " pty limited", " ltd",
        " limited", " pty", " p/l", " p/l.", " proprietary",
        " atf", " as trustee", " trustee", " unit trust",
        " childcare", " child care", " early learning",
        " early education", " early childhood",
    ]:
        n = n.replace(suffix, "")
    # Remove punctuation and extra spaces
    n = re.sub(r"[^a-z0-9 ]", " ", n)
    n = re.sub(r"\s+", " ", n).strip()
    return n


def extract_ho_address(address: str) -> str:
    """Extract a normalised HO address key (street + suburb)."""
    if not address or str(address).lower() in ("nan", "none", ""):
        return ""
    a = str(address).lower().strip()
    a = re.sub(r"\s+", " ", a)
    return a


def days_since(date_str: str) -> int:
    """Days since a date string (dd/mm/yyyy or similar)."""
    if not date_str or str(date_str).lower() in ("nan", "none", ""):
        return 99999
    for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y"]:
        try:
            d = datetime.strptime(str(date_str).strip(), fmt).date()
            return (date.today() - d).days
        except ValueError:
            continue
    return 99999


# ─────────────────────────────────────────────
# GROUP INFERENCE
# ─────────────────────────────────────────────

def infer_groups(df: pd.DataFrame) -> list:
    """
    Infer operator groups from ACECQA data using tiered matching.
    Returns list of group dicts.
    """
    groups = {}   # group_key -> {centres, confidence, match_basis}

    # ── TIER 1: Same provider_approval_number (confirmed) ────────────
    for pa_num, grp in df.groupby("provider_approval_number"):
        key = f"PA:{pa_num}"
        groups[key] = {
            "group_key":       key,
            "provider_numbers": [pa_num],
            "legal_name":      grp["providerlegalname"].iloc[0],
            "norm_name":       normalise_name(grp["providerlegalname"].iloc[0]),
            "centres":         grp.to_dict("records"),
            "confidence":      "confirmed",
            "match_basis":     "same_provider_approval",
        }

    # ── TIER 2: Exact normalised name match across provider numbers ───
    # Group by normalised name, merge confirmed groups with same name
    name_to_keys = defaultdict(list)
    for key, g in groups.items():
        name_to_keys[g["norm_name"]].append(key)

    merged_keys = set()
    for norm_name, keys in name_to_keys.items():
        if len(keys) > 1 and norm_name:
            # Merge all into first key
            primary = keys[0]
            for secondary in keys[1:]:
                if secondary in merged_keys:
                    continue
                groups[primary]["centres"].extend(groups[secondary]["centres"])
                groups[primary]["provider_numbers"].extend(
                    groups[secondary]["provider_numbers"]
                )
                groups[primary]["confidence"] = "high"
                groups[primary]["match_basis"] = "exact_name_match"
                merged_keys.add(secondary)

    # Remove merged groups
    for key in merged_keys:
        del groups[key]

    # ── TIER 3: Fuzzy name match ──────────────────────────────────────
    remaining_keys = list(groups.keys())
    norm_names     = [groups[k]["norm_name"] for k in remaining_keys]
    fuzzy_merged   = set()

    for i, key_a in enumerate(remaining_keys):
        if key_a in fuzzy_merged:
            continue
        name_a = groups[key_a]["norm_name"]
        if not name_a or len(name_a) < 4:
            continue

        for j, key_b in enumerate(remaining_keys[i+1:], i+1):
            if key_b in fuzzy_merged:
                continue
            name_b = groups[key_b]["norm_name"]
            if not name_b or len(name_b) < 4:
                continue

            score = fuzz.token_set_ratio(name_a, name_b)

            # Skip if match is driven by generic business words only
            # Strip generic words and recheck — if score drops significantly, it's noise
            GENERIC_WORDS = [
                "investments", "investment", "enterprises", "enterprise",
                "services", "service", "holdings", "holding", "group",
                "management", "operations", "properties", "property",
                "solutions", "ventures", "capital", "assets",
            ]
            name_a_stripped = name_a
            name_b_stripped = name_b
            for gw in GENERIC_WORDS:
                name_a_stripped = name_a_stripped.replace(gw, "").strip()
                name_b_stripped = name_b_stripped.replace(gw, "").strip()
            
            # If stripped names are too short or score drops a lot, skip
            stripped_score = fuzz.token_set_ratio(name_a_stripped, name_b_stripped)
            if len(name_a_stripped) < 4 or len(name_b_stripped) < 4:
                continue  # nothing left after stripping — pure generic match
            if score - stripped_score > 25:
                continue  # score driven by generic words — skip

            if score >= FUZZY_HIGH:
                # High confidence merge
                groups[key_a]["centres"].extend(groups[key_b]["centres"])
                groups[key_a]["provider_numbers"].extend(
                    groups[key_b]["provider_numbers"]
                )
                if groups[key_a]["confidence"] == "confirmed":
                    groups[key_a]["confidence"] = "high"
                    groups[key_a]["match_basis"] = f"fuzzy_name_{score:.0f}pct"
                fuzzy_merged.add(key_b)

            elif score >= FUZZY_MEDIUM:
                # Medium confidence — flag for review, don't merge automatically
                if "fuzzy_related" not in groups[key_a]:
                    groups[key_a]["fuzzy_related"] = []
                groups[key_a]["fuzzy_related"].append({
                    "key":        key_b,
                    "name":       groups[key_b]["legal_name"],
                    "score":      score,
                    "confidence": "review_required",
                })

    for key in fuzzy_merged:
        if key in groups:
            del groups[key]

    # ── TIER 4: Same phone number across different groups ─────────────
    phone_to_keys = defaultdict(list)
    for key, g in groups.items():
        phones = set()
        for c in g["centres"]:
            ph = str(c.get("phone", "")).strip()
            if ph and ph not in ("nan", "None", "") and len(ph) >= 8:
                phones.add(ph)
        for ph in phones:
            phone_to_keys[ph].append(key)

    for ph, keys in phone_to_keys.items():
        if len(keys) > 1:
            primary = keys[0]
            for secondary in keys[1:]:
                if secondary not in groups:
                    continue
                if "phone_related" not in groups[primary]:
                    groups[primary]["phone_related"] = []
                groups[primary]["phone_related"].append({
                    "key":        secondary,
                    "name":       groups[secondary]["legal_name"],
                    "phone":      ph,
                    "confidence": "review_required",
                })

    return list(groups.values())


# ─────────────────────────────────────────────
# SCORING
# ─────────────────────────────────────────────

def score_group(g: dict, existing_clients: set) -> dict:
    """Score an operator group against Remara target criteria."""
    centres    = g["centres"]
    n_centres  = len(centres)
    legal_name = g.get("legal_name", "")

    # Basic filters
    nfp_flag   = is_nfp(legal_name)
    states     = list(set(str(c.get("state", "")).strip().upper()
                         for c in centres if c.get("state")))
    n_states   = len([s for s in states if s and s not in ("NAN", "")])

    # NQS ratings
    ratings = [str(c.get("overallrating", "")).lower() for c in centres]
    exceeding = sum(1 for r in ratings if "exceeding" in r)
    meeting   = sum(1 for r in ratings if "meeting" in r)
    working   = sum(1 for r in ratings if "working" in r)
    sig_imp   = sum(1 for r in ratings if "significant" in r)
    rated     = exceeding + meeting + working + sig_imp
    meeting_plus = exceeding + meeting

    # Kinder approval bonus — centres approved for kindergarten/preschool
    kinder_approved = sum(
        1 for c in centres
        if str(c.get("preschool/kindergarten_-_stand_alone", "")).upper() == "YES"
        or str(c.get("preschool/kindergarten_-_part_of_a_school", "")).upper() == "YES"
    )
    has_kinder = kinder_approved > 0

    # Growth signal — most recent service approval date
    approval_dates = [c.get("serviceapprovalgranteddate", "") for c in centres]
    min_days = min((days_since(d) for d in approval_dates), default=99999)
    recent_centre = min_days < 730    # centre approved in last 2 years
    growing_centre = min_days < 1460  # centre approved in last 4 years

    # Existing client check
    is_client = any(
        client.lower() in legal_name.lower() or
        legal_name.lower() in client.lower()
        for client in existing_clients
    )

    # ── SCORING ──────────────────────────────────────────────────────
    score = 0
    score_breakdown = {}

    # Centre count (25 pts)
    if 5 <= n_centres <= 10:
        pts = 25
    elif n_centres in (3, 4) or n_centres in (11, 12):
        pts = 15
    elif n_centres in (13, 14, 15):
        pts = 8
    elif n_centres == 2:
        pts = 5
    else:
        pts = 0
    score += pts
    score_breakdown["centre_count"] = pts

    # For-profit (20 pts)
    pts = 0 if nfp_flag else 20
    score += pts
    score_breakdown["for_profit"] = pts

    # NQS quality (20 pts)
    if rated == 0:
        pts = 8  # unrated — unknown, slight positive (new centres)
    elif sig_imp > 0:
        pts = 0  # significant improvement required — red flag
    elif working > meeting_plus:
        pts = 5
    elif meeting_plus >= rated * 0.75:
        pts = 20
    else:
        pts = 12
    score += pts
    score_breakdown["nqs_quality"] = pts

    # Geographic focus (15 pts)
    if n_states <= 1:
        pts = 15
    elif n_states == 2:
        pts = 10
    else:
        pts = 3
    score += pts
    score_breakdown["geo_focus"] = pts

    # Growth signal (15 pts)
    if recent_centre:
        pts = 15
    elif growing_centre:
        pts = 8
    else:
        pts = 3
    score += pts
    score_breakdown["growth_signal"] = pts

    # Not existing client (5 pts)
    pts = 0 if is_client else 5
    score += pts
    score_breakdown["not_client"] = pts

    # Kinder approval bonus (5 pts — added to score, max stays 100 effectively)
    # Not in base 100 but tracked separately as a quality signal
    kinder_bonus = 5 if has_kinder else 0
    score_breakdown["kinder_bonus"] = kinder_bonus

    # ── PRODUCT FIT ──────────────────────────────────────────────────
    if n_centres <= 4:
        product_fit = "Watch — too small, monitor for growth"
    elif n_centres <= 7:
        product_fit = "Established / Formative"
    elif n_centres <= 12:
        product_fit = "Formative / Construction — HO threshold zone"
    else:
        product_fit = "Portfolio — large group, complex underwrite"

    # ── PRIORITY TIER ─────────────────────────────────────────────────
    if is_client:
        tier = "existing_client"
    elif nfp_flag:
        tier = "nfp_excluded"
    elif score >= HOT_THRESHOLD and n_centres >= 3:
        tier = "hot"
    elif score >= 40 and n_centres >= 2:
        tier = "warm"
    else:
        tier = "watch"

    # ── TOTAL PLACES ─────────────────────────────────────────────────
    total_places = sum(
        int(str(c.get("numberofapprovedplaces", 0) or 0).split(".")[0] or 0)
        for c in centres
    )

    # ── CENTRE LIST (summary) ─────────────────────────────────────────
    centre_summary = []
    for c in sorted(centres, key=lambda x: str(x.get("serviceapprovalgranteddate", "")), reverse=True):
        centre_summary.append({
            "service_name":    str(c.get("servicename", "")).strip(),
            "suburb":          str(c.get("suburb", "")).strip(),
            "state":           str(c.get("state", "")).strip(),
            "postcode":        str(c.get("postcode", "")).strip(),
            "places":          int(str(c.get("numberofapprovedplaces", 0) or 0).split(".")[0] or 0),
            "nqs_rating":      str(c.get("overallrating", "")).strip(),
            "approval_number": str(c.get("serviceapprovalnumber", "")).strip(),
            "provider_number": str(c.get("provider_approval_number", "")).strip(),
            "approval_date":   str(c.get("serviceapprovalgranteddate", "")).strip(),
            "phone":           str(c.get("phone", "")).strip().replace(".0",""),
        })

    return {
        "legal_name":          legal_name,
        "norm_name":           g.get("norm_name", ""),
        "provider_numbers":    g.get("provider_numbers", []),
        "group_confidence":    g.get("confidence", "confirmed"),
        "match_basis":         g.get("match_basis", ""),
        "fuzzy_related":       g.get("fuzzy_related", []),
        "phone_related":       g.get("phone_related", []),
        "n_centres":           n_centres,
        "total_places":        total_places,
        "states":              sorted(states),
        "is_nfp":              nfp_flag,
        "is_existing_client":  is_client,
        "nqs_summary": {
            "exceeding": exceeding,
            "meeting":   meeting,
            "working_towards": working,
            "sig_improvement": sig_imp,
            "unrated":   n_centres - rated,
        },
        "recent_centre_added": recent_centre,
        "growing":             growing_centre,
        "score":               score,
        "score_breakdown":     score_breakdown,
        "kinder_approved_count": kinder_approved,
        "has_kinder":          has_kinder,
        "product_fit":         product_fit,
        "priority_tier":       tier,
        "centres":             centre_summary,
    }


# ─────────────────────────────────────────────
# MAIN RUNNER
# ─────────────────────────────────────────────

def run():
    log.info("=" * 55)
    log.info("module2c_targeting — operator group scoring")
    log.info("=" * 55)

    if not SNAP_FILE.exists():
        log.error(f"services_snapshot.csv not found: {SNAP_FILE}")
        return

    # Load ACECQA snapshot
    df = pd.read_csv(SNAP_FILE, dtype=str, low_memory=False)
    df.columns = [c.strip().lower() for c in df.columns]

    # Long Day Care only
    if "long_day_care" in df.columns:
        df = df[df["long_day_care"].str.upper() == "YES"]
        log.info(f"LDC services: {len(df):,}")

    # Skip temporarily closed
    if "temporarily_closed" in df.columns:
        df = df[df["temporarily_closed"].str.upper() != "YES"]
        log.info(f"Active LDC services: {len(df):,}")

    # Load existing clients
    existing_clients = set()
    if CRM_FILE.exists():
        try:
            crm = pd.read_csv(CRM_FILE, dtype=str)
            crm.columns = [c.strip().lower() for c in crm.columns]
            name_col = next((c for c in crm.columns if "name" in c), None)
            if name_col:
                existing_clients = set(crm[name_col].dropna().str.strip().tolist())
                log.info(f"CRM clients loaded: {len(existing_clients)}")
        except Exception as e:
            log.warning(f"Could not load CRM: {e}")

    # Infer operator groups
    log.info("Inferring operator groups...")
    groups = infer_groups(df)
    log.info(f"Groups identified: {len(groups):,}")

    # Confidence breakdown
    for conf in ["confirmed", "high", "medium", "review_required"]:
        n = sum(1 for g in groups if g.get("confidence") == conf)
        if n:
            log.info(f"  {conf}: {n:,}")

    # Score all groups
    log.info("Scoring groups...")
    scored = []
    for g in groups:
        try:
            result = score_group(g, existing_clients)
            scored.append(result)
        except Exception as e:
            log.warning(f"Error scoring {g.get('legal_name','?')}: {e}")

    # Sort by score descending
    scored.sort(key=lambda x: x["score"], reverse=True)

    # Summary stats
    total      = len(scored)
    hot        = sum(1 for s in scored if s["priority_tier"] == "hot")
    warm       = sum(1 for s in scored if s["priority_tier"] == "warm")
    watch      = sum(1 for s in scored if s["priority_tier"] == "watch")
    nfp_excl   = sum(1 for s in scored if s["priority_tier"] == "nfp_excluded")
    clients    = sum(1 for s in scored if s["priority_tier"] == "existing_client")
    review_req = sum(1 for s in scored if s.get("fuzzy_related") or s.get("phone_related"))

    log.info("=" * 55)
    log.info(f"Operator groups scored: {total:,}")
    log.info(f"  Hot targets:          {hot:,}")
    log.info(f"  Warm targets:         {warm:,}")
    log.info(f"  Watch:                {watch:,}")
    log.info(f"  NFP excluded:         {nfp_excl:,}")
    log.info(f"  Existing clients:     {clients:,}")
    log.info(f"  Review required:      {review_req:,} (possible related groups)")

    # Write outputs
    with open(OUTPUT_ALL, "w", encoding="utf-8") as f:
        json.dump(scored, f, indent=2, default=str)
    log.info(f"Full list: {OUTPUT_ALL.name}")

    hot_targets = [s for s in scored if s["priority_tier"] in ("hot", "warm")]
    with open(OUTPUT_HOT, "w", encoding="utf-8") as f:
        json.dump(hot_targets, f, indent=2, default=str)
    log.info(f"Hot+warm targets: {OUTPUT_HOT.name} ({len(hot_targets)} operators)")

    # Print top 10
    log.info("\nTOP 10 TARGETS:")
    for i, s in enumerate(scored[:10], 1):
        review = " [REVIEW GROUP LINKS]" if (s.get("fuzzy_related") or s.get("phone_related")) else ""
        log.info(
            f"  {i:2}. {s['legal_name'][:45]:<45} "
            f"score={s['score']:3d}  "
            f"centres={s['n_centres']:2d}  "
            f"states={','.join(s['states'])}  "
            f"[{s['priority_tier'].upper()}]{review}"
        )

    return scored


if __name__ == "__main__":
    run()
