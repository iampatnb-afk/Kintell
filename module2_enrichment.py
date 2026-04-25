import os
import json
import time
from pathlib import Path
from datetime import date
from dotenv import load_dotenv
import anthropic

load_dotenv()

LEADS_INPUT = Path("data/leads_today.json")
LEADS_OUTPUT = Path("data/leads_enriched.json")

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def search_web_for_contact(legal_name, trading_name, suburb, state):
    display_name = trading_name if trading_name else legal_name
    prompt = (
        "Find the owner or director of this Australian childcare business. "
        "Return ONLY a JSON object, no other text.\n\n"
        "Business: " + display_name + " (" + legal_name + ")\n"
        "Location: " + suburb + ", " + state + "\n\n"
        "Search for the business name plus suburb, then search for the director name, "
        "then search LinkedIn. Look for owner, director, founder or principal.\n\n"
        "Return exactly this JSON:\n"
        "{\"contact_name\":\"\","
        "\"contact_role\":\"\","
        "\"contact_phone\":\"\","
        "\"contact_email\":\"\","
        "\"contact_linkedin\":\"\","
        "\"contact_source\":\"\","
        "\"confidence\":\"low\","
        "\"notes\":\"\"}\n\n"
        "Only include details you actually find. Never invent anything."
    )
    try:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=800,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[{"role": "user", "content": prompt}]
        )
        result_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                result_text += block.text
        if result_text.strip():
            s = result_text.find("{")
            e = result_text.rfind("}") + 1
            if s >= 0 and e > s:
                return json.loads(result_text[s:e])
    except Exception as ex:
        print("    Search error:", ex)
    return {
        "contact_name": "",
        "contact_role": "",
        "contact_phone": "",
        "contact_email": "",
        "contact_linkedin": "",
        "contact_source": "Search failed",
        "confidence": "low",
        "notes": ""
    }


def enrich_lead(lead):
    legal_name = lead.get("legal_name", "")
    trading_name = lead.get("trading_name", "")
    suburb = lead.get("suburb", "")
    state = lead.get("state", "")
    print("\n  Enriching:", legal_name)
    print("  Location: ", suburb + ",", state)
    if lead.get("contact_confidence") not in ["", "pending_enrichment", None]:
        print("  Already enriched - skipping")
        return lead
    if lead.get("existing_client"):
        lead["contact_confidence"] = "existing_client"
        return lead
    c = search_web_for_contact(legal_name, trading_name, suburb, state)
    lead["contact_name"] = c.get("contact_name", "")
    lead["contact_role"] = c.get("contact_role", "")
    lead["contact_phone"] = c.get("contact_phone", "")
    lead["contact_email"] = c.get("contact_email", "")
    lead["contact_linkedin"] = c.get("contact_linkedin", "")
    lead["contact_source"] = c.get("contact_source", "")
    lead["contact_confidence"] = c.get("confidence", "low")
    lead["contact_notes"] = c.get("notes", "")
    if lead["contact_name"]:
        print("  FOUND:", lead["contact_name"], "-", lead["contact_role"])
        if lead["contact_phone"]:
            print("  Phone:", lead["contact_phone"])
        if lead["contact_email"]:
            print("  Email:", lead["contact_email"])
    else:
        print("  No contact found")
    time.sleep(1)
    return lead


def run_enrichment():
    print("\n=== Module 2: Contact Enrichment ===")
    print("Run date:", str(date.today()))
    if not LEADS_INPUT.exists():
        print("No leads file found. Run module1_acecqa.py first.")
        return []
    with open(LEADS_INPUT) as f:
        leads = json.load(f)
    if not leads:
        print("No leads to enrich today.")
        return []

    # Cap leads to prevent rate limit issues on large runs
    MAX_LEADS = 50
    if len(leads) > MAX_LEADS:
        print(f"  Capping enrichment to {MAX_LEADS} leads (found {len(leads)} — use --all to override)")
        # Prioritise hot leads first
        hot   = [l for l in leads if l.get("priority_tier") == "hot"]
        warm  = [l for l in leads if l.get("priority_tier") == "warm"]
        other = [l for l in leads if l.get("priority_tier") not in ("hot","warm")]
        leads = (hot + warm + other)[:MAX_LEADS]
    print("Leads to enrich:", len(leads))
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key == "your-new-key-here":
        print("ERROR: ANTHROPIC_API_KEY not set in .env file")
        return []
    enriched = []
    found_count = 0
    for i, lead in enumerate(leads):
        print("\n[" + str(i + 1) + "/" + str(len(leads)) + "]", end="")
        el = enrich_lead(lead)
        enriched.append(el)
        if el.get("contact_name"):
            found_count += 1
        with open(LEADS_OUTPUT, "w") as f:
            json.dump(enriched, f, indent=2)
    print("\n" + "=" * 50)
    print("ENRICHMENT COMPLETE")
    print("  Contacts found:", found_count, "of", len(enriched))
    print("  Output saved to:", str(LEADS_OUTPUT))
    print("=" * 50)
    return enriched


if __name__ == "__main__":
    leads = run_enrichment()
    if leads:
        print("\nEnriched lead preview:")
        for lead in leads[:3]:
            print("\n  [" + lead.get("priority_tier", "").upper() + "]", lead.get("legal_name", ""))
            print("  Contact:", lead.get("contact_name", "Not found"))
            if lead.get("contact_phone"):
                print("  Phone:", lead["contact_phone"])
            if lead.get("contact_email"):
                print("  Email:", lead["contact_email"])
            print("  Product:", lead.get("product_fit", ""))