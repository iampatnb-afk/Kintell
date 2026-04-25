"""
Remara Agent — Module 1: ACECQA Daily Diff
Detects new approved providers and service approvals daily.
Performs group inference (related entities) and NFP detection.
Outputs structured leads ready for Module 2 enrichment.
"""

import os
import csv
import json
import time
import hashlib
import requests
import pandas as pd
from io import StringIO
from datetime import datetime, date
from pathlib import Path
from fuzzywuzzy import fuzz
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

PROVIDERS_SNAPSHOT = DATA_DIR / "providers_snapshot.csv"
SERVICES_SNAPSHOT  = DATA_DIR / "services_snapshot.csv"
LEADS_OUTPUT       = DATA_DIR / "leads_today.json"
CRM_FILE           = Path("crm_clients.csv")

PROVIDERS_URL = "https://www.acecqa.gov.au/sites/default/files/national-registers/providers/Approved-providers-au-export.csv"
SERVICES_URL  = "https://www.acecqa.gov.au/sites/default/files/national-registers/services/Education-services-au-export.csv"

NFP_KEYWORDS = [
    "incorporated association", "inc association", " inc.", "incorporated",
    "company limited by guarantee", "limited by guarantee", "co ltd by guarantee",
    "cooperative", "co-operative", "community", "council", "church",
    "diocese", "uniting", "catholic", "anglican", "presbyterian",
    "school council", "parents club", "association inc",
    "charitable", "charity", "foundation", "not for profit", "not-for-profit",
    "government", "department of", "shire council", "city council",
    "municipal", "state government", "territory government",
]

FOR_PROFIT_KEYWORDS = [
    "pty ltd", "pty. ltd.", "proprietary limited",
    "unit trust", "family trust", " trust", "atf ",
]

ABR_NAME_URL = "https://abr.business.gov.au/json/MatchingNames.aspx"

def abr_lookup_by_name(name):
    try:
        params = {"name": name, "guid": ""}
        r = requests.get(ABR_NAME_URL, params=params, timeout=10)
        if r.status_code == 200:
            text = r.text.strip()
            if text.startswith("callback("):
                text = text[9:-1]
            data = json.loads(text)
            results = data.get("Names", [])
            if results:
                return results[0]
    except Exception as e:
        print(f"  ABR lookup failed for '{name}': {e}")
    return {}


def detect_nfp(legal_name, abr_type=""):
    name_lower = legal_name.lower()
    type_lower = abr_type.lower()
    for kw in FOR_PROFIT_KEYWORDS:
        if kw in name_lower:
            return False, "Pty Ltd / Trust — for-profit"
    for kw in NFP_KEYWORDS:
        if kw in name_lower or kw in type_lower:
            return True, "Possible NFP — " + kw + " in name/type"
    return False, "Unknown entity type — verify"


def classify_entity_size(centre_count):
    if centre_count == 1:
        return "watch", "Single centre — may have other entities"
    elif centre_count <= 4:
        return "warm", "Early track record — 2-4 centres"
    elif centre_count <= 12:
        return "hot", "Core target — 5-12 centres"
    else:
        return "hot", "Large group — " + str(centre_count) + " centres — note HO cost threshold"


def download_csv(url, label):
    print("  Downloading " + label + "...")
    try:
        r = requests.get(url, timeout=60, headers={"User-Agent": "Remara-Agent/1.0"})
        r.raise_for_status()
        content = r.content.decode("utf-8-sig")
        df = pd.read_csv(StringIO(content), dtype=str, low_memory=False)
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
        print("  " + label + ": " + str(len(df)) + " records downloaded")
        return df
    except Exception as e:
        print("  ERROR downloading " + label + ": " + str(e))
        return None


def load_snapshot(path):
    if path.exists():
        return pd.read_csv(path, dtype=str, low_memory=False)
    return pd.DataFrame()


def save_snapshot(df, path):
    df.to_csv(path, index=False)


def df_hash(df):
    if df.empty:
        return set()
    return set(
        hashlib.md5(row.encode()).hexdigest()
        for row in df.apply(lambda r: "|".join(r.fillna("").values), axis=1)
    )


def infer_group(provider_row, all_providers, all_services):
    legal_name   = str(provider_row.get("legal_name", "")).strip()
    address      = str(provider_row.get("address", "")).strip().lower()
    provider_num = str(provider_row.get("provider_approval_number", "")).strip()
    related = []
    for _, row in all_providers.iterrows():
        other_num = str(row.get("provider_approval_number", "")).strip()
        if other_num == provider_num:
            continue
        other_name = str(row.get("legal_name", "")).strip()
        other_addr = str(row.get("address", "")).strip().lower()
        addr_match = (address and other_addr and address != "nan" and other_addr != "nan" and address == other_addr)
        base_name  = legal_name.lower().replace("pty ltd", "").replace("pty. ltd.", "").strip()
        base_other = other_name.lower().replace("pty ltd", "").replace("pty. ltd.", "").strip()
        name_score = fuzz.token_set_ratio(base_name, base_other)
        name_match = name_score >= 82 and len(base_name) > 4
        if addr_match or name_match:
            related.append({
                "provider_number": other_num,
                "legal_name": other_name,
                "match_type": "address" if addr_match else "name_similarity_" + str(name_score),
            })
    all_related_nums = [provider_num] + [r["provider_number"] for r in related]
    if "provider_approval_number" in all_services.columns:
        services_for_group = all_services[all_services["provider_approval_number"].isin(all_related_nums)]
    else:
        services_for_group = pd.DataFrame()
    group_size = len(services_for_group)
    if len(related) == 0:
        confidence = "single_entity"
    elif any(r["match_type"] == "address" for r in related):
        confidence = "likely_group"
    else:
        confidence = "possible_group"
    return {
        "group_centre_count": max(group_size, 1),
        "related_entities":   related[:5],
        "group_confidence":   confidence,
    }


def load_crm_names():
    if not CRM_FILE.exists():
        return set()
    try:
        df = pd.read_csv(CRM_FILE, dtype=str)
        name_col = next((c for c in df.columns if "name" in c.lower()), None)
        if name_col:
            return set(df[name_col].str.lower().str.strip().dropna())
    except Exception as e:
        print("  CRM load warning: " + str(e))
    return set()


def is_existing_client(legal_name, crm_names):
    name_lower = legal_name.lower().strip()
    if name_lower in crm_names:
        return True
    for crm_name in crm_names:
        if fuzz.token_set_ratio(name_lower, crm_name) >= 90:
            return True
    return False


def run_acecqa_diff():
    print("\n=== Module 1: ACECQA Daily Diff ===")
    print("Run date: " + str(date.today()))

    providers_today = download_csv(PROVIDERS_URL, "Providers")
    services_today  = download_csv(SERVICES_URL,  "Services")

    if providers_today is None or services_today is None:
        print("ERROR: Could not download ACECQA data. Aborting.")
        return []

    providers_yesterday = load_snapshot(PROVIDERS_SNAPSHOT)
    services_yesterday  = load_snapshot(SERVICES_SNAPSHOT)

    # Skip if snapshot saved less than 6 hours ago (already ran today)
    import time as _time
    snapshot_age = (_time.time() - SERVICES_SNAPSHOT.stat().st_mtime) / 3600 if SERVICES_SNAPSHOT.exists() else 999
    if snapshot_age < 6:
        print("  Snapshot is less than 6 hours old - skipping diff.")
        return []

    if providers_yesterday.empty:
        print("\n  First run — saving baseline snapshot.")
        print("  No leads generated today. Run again tomorrow for live diff.")
        save_snapshot(providers_today, PROVIDERS_SNAPSHOT)
        save_snapshot(services_today,  SERVICES_SNAPSHOT)
        return []

    providers_old_hashes = df_hash(providers_yesterday)
    services_old_hashes  = df_hash(services_yesterday)

    new_providers = providers_today[
        ~providers_today.apply(
            lambda r: hashlib.md5("|".join(r.fillna("").values).encode()).hexdigest(),
            axis=1
        ).isin(providers_old_hashes)
    ]

    new_services = services_today[
        ~services_today.apply(
            lambda r: hashlib.md5("|".join(r.fillna("").values).encode()).hexdigest(),
            axis=1
        ).isin(services_old_hashes)
    ]

    print("\n  New providers detected: " + str(len(new_providers)))
    print("  New services detected:  " + str(len(new_services)))

    crm_names = load_crm_names()
    print("  CRM clients loaded: " + str(len(crm_names)))

    leads = []

    for _, row in new_providers.iterrows():
        legal_name    = str(row.get("legal_name", "Unknown")).strip()
        trading_name  = str(row.get("trading_name", "")).strip()
        address       = str(row.get("address", "")).strip()
        suburb        = str(row.get("suburb", "")).strip()
        state         = str(row.get("state", "")).strip()
        postcode      = str(row.get("postcode", "")).strip()
        approval_num  = str(row.get("provider_approval_number", "")).strip()
        approval_date = str(row.get("date_approval_granted", "")).strip()

        print("\n  Processing new provider: " + legal_name)

        is_nfp, nfp_reason = detect_nfp(legal_name)
        time.sleep(0.5)
        abr_data = abr_lookup_by_name(legal_name)
        abr_type = abr_data.get("EntityTypeCode", "")
        if abr_type:
            is_nfp, nfp_reason = detect_nfp(legal_name, abr_type)

        existing   = is_existing_client(legal_name, crm_names)
        group_info = infer_group(row, providers_today, services_today)
        tier, tier_note = classify_entity_size(group_info["group_centre_count"])

        if group_info["group_centre_count"] <= 4:
            product = "Formative (new centre opening)"
        elif group_info["group_centre_count"] <= 12:
            product = "Formative or Established (expansion)"
        else:
            product = "Established (large group — assess HO costs)"

        lead = {
            "stream":             "opco",
            "signal_type":        "new_approved_provider",
            "date_detected":      str(date.today()),
            "legal_name":         legal_name,
            "trading_name":       trading_name if trading_name != "nan" else "",
            "provider_number":    approval_num,
            "approval_date":      approval_date,
            "address":            address,
            "suburb":             suburb,
            "state":              state,
            "postcode":           postcode,
            "is_nfp_flag":        is_nfp,
            "nfp_reason":         nfp_reason,
            "existing_client":    existing,
            "group_centre_count": group_info["group_centre_count"],
            "group_confidence":   group_info["group_confidence"],
            "related_entities":   group_info["related_entities"],
            "priority_tier":      "existing_client" if existing else tier,
            "tier_note":          "Already a Remara client" if existing else tier_note,
            "product_fit":        product,
            "acecqa_link":        "https://www.acecqa.gov.au/resources/national-registers/providers",
            "contact_name":       "",
            "contact_role":       "",
            "contact_phone":      "",
            "contact_email":      "",
            "contact_linkedin":   "",
            "contact_confidence": "pending_enrichment",
        }
        leads.append(lead)

    for _, row in new_services.iterrows():
        service_name  = str(row.get("service_name", "Unknown")).strip()
        provider_num  = str(row.get("provider_approval_number", "")).strip()
        service_num   = str(row.get("service_approval_number", "")).strip()
        address       = str(row.get("address", "")).strip()
        suburb        = str(row.get("suburb", "")).strip()
        state         = str(row.get("state", "")).strip()
        postcode      = str(row.get("postcode", "")).strip()
        service_type  = str(row.get("service_type", "")).strip()
        approval_date = str(row.get("date_approval_granted", "")).strip()
        places        = str(row.get("approved_places", "")).strip()

        if service_type and "centre" not in service_type.lower() and "long day" not in service_type.lower() and "ldcc" not in service_type.lower():
            continue

        provider_row = providers_today[providers_today.get("provider_approval_number", pd.Series(dtype=str)) == provider_num]

        if provider_row.empty:
            legal_name   = "Provider " + provider_num
            trading_name = ""
            is_nfp, nfp_reason = False, "Provider not found in register"
            group_info = {"group_centre_count": 1, "related_entities": [], "group_confidence": "unknown"}
            existing = False
        else:
            prow         = provider_row.iloc[0]
            legal_name   = str(prow.get("legal_name", "Unknown")).strip()
            trading_name = str(prow.get("trading_name", "")).strip()
            is_nfp, nfp_reason = detect_nfp(legal_name)
            time.sleep(0.5)
            abr_data = abr_lookup_by_name(legal_name)
            abr_type = abr_data.get("EntityTypeCode", "")
            if abr_type:
                is_nfp, nfp_reason = detect_nfp(legal_name, abr_type)
            group_info = infer_group(prow, providers_today, services_today)
            existing   = is_existing_client(legal_name, crm_names)

        tier, tier_note = classify_entity_size(group_info["group_centre_count"])

        if group_info["group_centre_count"] <= 4:
            product = "Formative (new centre opening)"
        else:
            product = "Formative or Established (group expansion)"

        print("  Processing new service: " + service_name + " — " + legal_name)

        lead = {
            "stream":             "opco",
            "signal_type":        "new_service_approval",
            "date_detected":      str(date.today()),
            "service_name":       service_name,
            "service_number":     service_num,
            "service_type":       service_type,
            "approved_places":    places,
            "approval_date":      approval_date,
            "address":            address,
            "suburb":             suburb,
            "state":              state,
            "postcode":           postcode,
            "legal_name":         legal_name,
            "trading_name":       trading_name if trading_name != "nan" else "",
            "provider_number":    provider_num,
            "is_nfp_flag":        is_nfp,
            "nfp_reason":         nfp_reason,
            "existing_client":    existing,
            "group_centre_count": group_info["group_centre_count"],
            "group_confidence":   group_info["group_confidence"],
            "related_entities":   group_info["related_entities"],
            "priority_tier":      "existing_client" if existing else tier,
            "tier_note":          "Already a Remara client" if existing else tier_note,
            "product_fit":        product,
            "acecqa_link":        "https://www.acecqa.gov.au/resources/national-registers",
            "contact_name":       "",
            "contact_role":       "",
            "contact_phone":      "",
            "contact_email":      "",
            "contact_linkedin":   "",
            "contact_confidence": "pending_enrichment",
        }
        leads.append(lead)

    from datetime import date as _date
    dated = DATA_DIR / f"services_snapshot_{_date.today()}.csv"
    save_snapshot(services_today, dated)
    for old in DATA_DIR.glob("services_snapshot_2*.csv"):
        try:
            d = _date.fromisoformat(old.stem.split("_")[-1])
            if (_date.today() - d).days > 14:
                old.unlink()
        except Exception:
            pass
    save_snapshot(providers_today, PROVIDERS_SNAPSHOT)
    save_snapshot(services_today,  SERVICES_SNAPSHOT)

    with open(LEADS_OUTPUT, "w") as f:
        json.dump(leads, f, indent=2)

    print("\n" + "="*50)
    print("LEADS GENERATED TODAY: " + str(len(leads)))
    hot   = [l for l in leads if l["priority_tier"] == "hot"]
    warm  = [l for l in leads if l["priority_tier"] == "warm"]
    watch = [l for l in leads if l["priority_tier"] == "watch"]
    ec    = [l for l in leads if l["priority_tier"] == "existing_client"]
    nfp   = [l for l in leads if l["is_nfp_flag"]]
    print("  Hot leads:        " + str(len(hot)))
    print("  Warm leads:       " + str(len(warm)))
    print("  Watch list:       " + str(len(watch)))
    print("  Existing clients: " + str(len(ec)))
    print("  NFP flagged:      " + str(len(nfp)))
    print("  Output saved to:  " + str(LEADS_OUTPUT))
    print("="*50)

    return leads


if __name__ == "__main__":
    leads = run_acecqa_diff()
    if leads:
        print("\nSample lead preview:")
        for lead in leads[:3]:
            print("\n  [" + lead["priority_tier"].upper() + "] " + lead["legal_name"])
            print("  Signal:   " + lead["signal_type"])
            print("  Location: " + lead["suburb"] + ", " + lead["state"])
            print("  Centres:  " + str(lead["group_centre_count"]) + " (" + lead["group_confidence"] + ")")
            print("  NFP flag: " + str(lead["is_nfp_flag"]) + " — " + lead["nfp_reason"])
            print("  Product:  " + lead["product_fit"])
