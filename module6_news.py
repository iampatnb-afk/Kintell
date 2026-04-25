"""
module6_news.py — Weekly Childcare Intelligence Brief
Remara Agent | Runs every Tuesday at 10:00 AM

Produces a weekly intelligence brief covering:
  1. Industry news — The Sector, COMMO, ACECQA, ACA, ECA
  2. Government & policy — Dept Education, Services Australia,
     Productivity Commission, state education departments
  3. M&A and investment — AFR, The Australian, ASX announcements,
     Arena REIT, commercial property
  4. Development pipeline — new centre announcements (feeds module3)
  5. People intelligence — named individuals at target operators
     (ASIC directors, LinkedIn, news mentions)
  6. Last 30 service approvals — from ACECQA data (no search needed)

Output: data/weekly_brief.json + section added to digest email

Schedule: Tuesday 10:00 AM via Task Scheduler
  Action: python module6_news.py

Run manually:
  python module6_news.py
  python module6_news.py --force   (ignore day-of-week check)
"""

import json
import re
import logging
import argparse
from pathlib import Path
from datetime import datetime, date, timedelta

import anthropic
from dotenv import load_dotenv

load_dotenv()

BASE_DIR     = Path(__file__).parent
DATA_DIR     = BASE_DIR / "data"
OUTPUT_FILE  = DATA_DIR / "weekly_brief.json"
TARGETS_FILE = BASE_DIR / "operators_hot_targets.json"
SNAP_FILE    = DATA_DIR / "services_snapshot.csv"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# SEARCH TOPICS
# ─────────────────────────────────────────────

WEEKLY_SEARCHES = [
    {
        "section":  "industry_news",
        "label":    "Industry News",
        "prompt":   (
            "Search thesector.com.au, commo.com.au, and ACECQA news for childcare "
            "industry news published in the last 7 days in Australia. "
            "Include: new centre openings, operator expansions, acquisitions, "
            "NQS outcomes, regulatory changes, workforce issues, funding news. "
            "Return a JSON array. Each item: headline, summary (2 sentences), "
            "source, url, date, category (one of: expansion/acquisition/regulatory/"
            "workforce/funding/property/other), "
            "operator_names (list of any operator names mentioned). "
            "Return ONLY the JSON array."
        ),
    },
    {
        "section":  "government_policy",
        "label":    "Government & Policy",
        "prompt":   (
            "Search for Australian childcare policy news from the last 7 days. "
            "Sources: education.gov.au, services australia, productivity commission, "
            "NSW/VIC/QLD education departments, federal parliament. "
            "Include: CCS changes, NQF updates, kinder funding, childcare "
            "affordability policy, regulatory announcements. "
            "Return a JSON array. Each item: headline, summary (2 sentences), "
            "source, url, date, category (policy/funding/regulatory/other), "
            "impact (one sentence on what this means for childcare operators). "
            "Return ONLY the JSON array."
        ),
    },
    {
        "section":  "investment_ma",
        "label":    "M&A and Investment",
        "prompt":   (
            "Search for Australian childcare sector mergers, acquisitions, "
            "property transactions and investment news from the last 7 days. "
            "Sources: AFR, The Australian, ASX announcements (G8 Education GEM, "
            "Arena REIT ARF, Think Childcare), commercialrealestate.com.au, "
            "developmentready.com.au. "
            "Include: centre sales, portfolio acquisitions, PE activity, "
            "childcare property transactions, REIT announcements. "
            "Return a JSON array. Each item: headline, summary (2 sentences), "
            "source, url, date, deal_value (if mentioned), "
            "buyer, seller, number_of_centres (if mentioned), "
            "operator_names (list of operators involved). "
            "Return ONLY the JSON array."
        ),
    },
    {
        "section":  "development_pipeline",
        "label":    "Development Pipeline",
        "prompt":   (
            "Search for new childcare centre development announcements in Australia "
            "from the last 7 days. Include DA approvals, construction starts, "
            "new centre openings, site acquisitions for childcare development. "
            "Sources: council planning portals, local news, industry publications. "
            "Return a JSON array. Each item: headline, summary (2 sentences), "
            "source, url, date, state, suburb, council, places (if mentioned), "
            "developer_name, operator_name, stage (DA/approved/construction/opened). "
            "Return ONLY the JSON array."
        ),
    },
    {
        "section":  "people_intelligence",
        "label":    "People & Operators",
        "prompt":   (
            "Search for news about Australian childcare operator executives, "
            "directors and key people from the last 7 days. "
            "Include: executive appointments, departures, LinkedIn announcements, "
            "operator interviews, conference speakers, ACA/ECA committee members, "
            "people named in childcare news or DA applications. "
            "Return a JSON array. Each item: person_name, role, operator_name, "
            "headline, summary (1-2 sentences), source, url, date, "
            "signal (one of: new_appointment/departure/expansion/interview/other). "
            "Return ONLY the JSON array."
        ),
    },
]


# ─────────────────────────────────────────────
# LAST 30 SERVICE APPROVALS (no search needed)
# ─────────────────────────────────────────────

def get_recent_approvals(n: int = 30) -> list:
    """
    Pull the last N service approvals from ACECQA services_snapshot.csv.
    Uses serviceapprovalgranteddate column, sorted newest first.
    No API call needed — pure ACECQA data.
    """
    if not SNAP_FILE.exists():
        log.warning("services_snapshot.csv not found")
        return []
    try:
        import pandas as pd
        df = pd.read_csv(SNAP_FILE, dtype=str, low_memory=False)
        df.columns = [c.strip().lower() for c in df.columns]

        if "serviceapprovalgranteddate" not in df.columns:
            log.warning("serviceapprovalgranteddate column not found")
            return []

        # LDC only
        if "long_day_care" in df.columns:
            df = df[df["long_day_care"].str.upper() == "YES"]

        df["approval_date_parsed"] = pd.to_datetime(
            df["serviceapprovalgranteddate"], dayfirst=True, errors="coerce"
        )
        df = df.dropna(subset=["approval_date_parsed"])
        df = df.sort_values("approval_date_parsed", ascending=False).head(n)

        results = []
        for _, row in df.iterrows():
            results.append({
                "service_name":     str(row.get("servicename", "") or "").strip(),
                "operator_name":    str(row.get("providerlegalname", "") or "").strip(),
                "address":          str(row.get("serviceaddress", "") or "").strip(),
                "suburb":           str(row.get("suburb", "") or "").strip(),
                "state":            str(row.get("state", "") or "").strip(),
                "postcode":         str(row.get("postcode", "") or "").strip(),
                "places":           str(row.get("numberofapprovedplaces", "") or "").strip(),
                "approval_date":    row["approval_date_parsed"].strftime("%d/%m/%Y"),
                "service_approval": str(row.get("serviceapprovalnumber", "") or "").strip(),
                "nqs_rating":       str(row.get("overallrating", "") or "").strip(),
            })

        log.info(f"Last {len(results)} service approvals loaded from ACECQA")
        return results

    except Exception as e:
        log.warning(f"Could not load recent approvals: {e}")
        return []


# ─────────────────────────────────────────────
# PEOPLE INTELLIGENCE — ASIC director search
# ─────────────────────────────────────────────

def search_operator_directors(operators: list, client: anthropic.Anthropic) -> list:
    """
    For top hot targets, search for named directors/key people.
    Uses Claude web search against ASIC, LinkedIn, news.
    Limited to top 10 operators to manage token usage.
    """
    if not operators:
        return []

    top = operators[:10]
    names_list = "\n".join(
        f"- {op['legal_name']} ({op['n_centres']} centres, {', '.join(op['states'])})"
        for op in top
    )

    prompt = (
        f"For each of these Australian childcare operators, search for the names "
        f"of their directors, owners, or key executives. Use ASIC company search, "
        f"LinkedIn, The Sector, COMMO, and company websites.\n\n"
        f"{names_list}\n\n"
        f"Return a JSON array. Each item: operator_name, person_name, role, "
        f"linkedin_url (if found), email (if publicly listed), phone (if public), "
        f"source, notes (1 sentence on their role/background). "
        f"Return ONLY the JSON array."
    )

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[{"role": "user", "content": prompt}],
        )

        full_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                full_text += block.text

        json_match = re.search(r'\[.*\]', full_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        log.warning("Director search: no JSON returned")
        return []

    except Exception as e:
        log.warning(f"Director search failed: {e}")
        return []


# ─────────────────────────────────────────────
# WEB SEARCH RUNNER
# ─────────────────────────────────────────────

def run_search(topic: dict, client: anthropic.Anthropic) -> list:
    """Run a single web search topic and return parsed results."""
    log.info(f"Searching: {topic['label']}...")
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[{"role": "user", "content": topic["prompt"]}],
        )

        full_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                full_text += block.text

        # Extract JSON
        stripped = full_text.strip()
        if stripped.startswith('['):
            json_str = stripped
        else:
            m = re.search(r'\[.*\]', full_text, re.DOTALL)
            json_str = m.group() if m else None

        if json_str:
            try:
                items = json.loads(json_str)
                log.info(f"  {topic['label']}: {len(items)} items found")
                return items if isinstance(items, list) else []
            except json.JSONDecodeError as e:
                log.warning(f"  {topic['label']}: JSON parse error: {e}")

        log.info(f"  {topic['label']}: no structured results returned")
        return []

    except Exception as e:
        log.warning(f"  {topic['label']} search failed: {e}")
        return []


# ─────────────────────────────────────────────
# HTML BRIEF RENDERER
# ─────────────────────────────────────────────

def render_html_brief(brief: dict) -> str:
    """Render the weekly brief as HTML for inclusion in email digest."""
    today = str(date.today())
    week_start = (date.today() - timedelta(days=7)).strftime("%d %b")
    week_end = date.today().strftime("%d %b %Y")

    sections_html = ""

    section_config = {
        "industry_news":       ("Industry News",        "#2980b9"),
        "government_policy":   ("Government & Policy",  "#8e44ad"),
        "investment_ma":       ("M&A and Investment",   "#27ae60"),
        "development_pipeline":("Development Pipeline", "#e67e22"),
        "people_intelligence": ("People & Operators",   "#c0392b"),
    }

    for key, (label, color) in section_config.items():
        items = brief.get(key, [])
        if not items:
            continue

        items_html = ""
        for item in items[:8]:  # cap at 8 per section
            headline = str(item.get("headline", "") or item.get("person_name", ""))
            summary  = str(item.get("summary", "") or item.get("notes", ""))
            source   = str(item.get("source", ""))
            url      = str(item.get("url", "") or item.get("linkedin_url", ""))
            dt       = str(item.get("date", ""))
            category = str(item.get("category", "") or item.get("signal", ""))

            # Operator name tags
            op_names = item.get("operator_names", []) or []
            if item.get("operator_name"):
                op_names.append(item["operator_name"])
            op_html = ""
            if op_names:
                tags = "".join(
                    f"<span style='background:#ecf0f1;padding:1px 6px;"
                    f"border-radius:3px;font-size:10px;margin-right:3px'>{n}</span>"
                    for n in op_names[:3]
                )
                op_html = f"<div style='margin-top:3px'>{tags}</div>"

            link_html = (
                f"<a href='{url}' style='color:#2980b9;font-size:11px' target='_blank'>"
                f"{source}</a>" if url else
                f"<span style='color:#aaa;font-size:11px'>{source}</span>"
            )

            items_html += f"""
            <div style='border-bottom:1px solid #f0f0f0;padding:8px 0'>
                <div style='font-size:13px;font-weight:500;color:#2c3e50'>
                    {headline}
                </div>
                <div style='font-size:12px;color:#555;margin-top:2px'>{summary}</div>
                {op_html}
                <div style='margin-top:3px'>
                    {link_html}
                    {f"<span style='color:#aaa;font-size:11px'> &bull; {dt}</span>" if dt else ""}
                    {f"<span style='background:#eaf4ff;color:#2980b9;padding:1px 5px;border-radius:3px;font-size:10px;margin-left:6px'>{category}</span>" if category else ""}
                </div>
            </div>"""

        sections_html += f"""
        <div style='margin-bottom:20px'>
            <div style='font-size:14px;font-weight:bold;color:{color};
                        border-bottom:2px solid {color};padding-bottom:4px;
                        margin-bottom:8px'>
                {label}
            </div>
            {items_html}
        </div>"""

    # Last 30 approvals table
    approvals = brief.get("recent_approvals", [])
    if approvals:
        rows = ""
        for a in approvals[:30]:
            sb_q = f"site:startingblocks.gov.au \"{a['service_name']}\" {a['suburb']}"
            import urllib.parse
            sb_link = f"https://www.google.com/search?{urllib.parse.urlencode({'q': sb_q})}"
            rows += f"""
            <tr style='border-bottom:1px solid #f5f5f5;font-size:11px'>
                <td style='padding:4px 8px'>
                    <a href='{sb_link}' target='_blank'
                       style='color:#2c3e50;text-decoration:none'>{a['service_name']}</a>
                </td>
                <td style='padding:4px 8px;color:#555'>{a['operator_name'][:35]}</td>
                <td style='padding:4px 8px'>{a['suburb']}, {a['state']}</td>
                <td style='padding:4px 8px;text-align:center'>{a['places']}</td>
                <td style='padding:4px 8px;color:#888'>{a['approval_date']}</td>
            </tr>"""

        sections_html += f"""
        <div style='margin-bottom:20px'>
            <div style='font-size:14px;font-weight:bold;color:#2c3e50;
                        border-bottom:2px solid #2c3e50;padding-bottom:4px;
                        margin-bottom:8px'>
                Last 30 Service Approvals
            </div>
            <table style='width:100%;border-collapse:collapse;font-size:12px'>
                <thead>
                    <tr style='background:#f5f5f5'>
                        <th style='padding:5px 8px;text-align:left'>Centre</th>
                        <th style='padding:5px 8px;text-align:left'>Operator</th>
                        <th style='padding:5px 8px;text-align:left'>Location</th>
                        <th style='padding:5px 8px;text-align:center'>Places</th>
                        <th style='padding:5px 8px;text-align:left'>Approved</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </div>"""

    return f"""
<div style='background:#fff;border:1px solid #e0e0dc;border-radius:8px;
            padding:16px;margin:16px 0'>
    <div style='font-size:18px;font-weight:bold;color:#2c3e50;margin-bottom:4px'>
        Weekly Intelligence Brief
    </div>
    <div style='font-size:12px;color:#888;margin-bottom:16px'>
        {week_start} — {week_end}
    </div>
    {sections_html}
</div>"""


# ─────────────────────────────────────────────
# MAIN RUNNER
# ─────────────────────────────────────────────

def run(force: bool = False):
    log.info("=" * 55)
    log.info("module6_news — weekly childcare intelligence brief")
    log.info("=" * 55)

    # Day check removed — scheduling handled by run_daily.py / Task Scheduler
    # Use --force flag only needed if running module6 standalone on a non-Tuesday

    client = anthropic.Anthropic()

    brief = {
        "generated_date": str(date.today()),
        "week_ending":    str(date.today()),
    }

    # Run each search topic with delay to avoid rate limits
    import time
    for i, topic in enumerate(WEEKLY_SEARCHES):
        if i > 0:
            log.info("  Waiting 60s between searches (rate limit)...")
            time.sleep(60)
        results = run_search(topic, client)
        brief[topic["section"]] = results

    # People intelligence for top hot targets
    log.info("  Waiting 60s before director search...")
    time.sleep(60)
    log.info("Searching for operator directors and key people...")
    try:
        targets = json.load(open(TARGETS_FILE, encoding="utf-8"))
        hot = [t for t in targets if t.get("priority_tier") == "hot"][:10]
        brief["operator_directors"] = search_operator_directors(hot, client)
        log.info(f"  Directors found: {len(brief['operator_directors'])}")
    except Exception as e:
        log.warning(f"Director search skipped: {e}")
        brief["operator_directors"] = []

    # Last 30 service approvals (no API call)
    brief["recent_approvals"] = get_recent_approvals(30)

    # Render HTML
    brief["html"] = render_html_brief(brief)

    # Save
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(brief, f, indent=2, default=str)

    # Summary
    log.info("=" * 55)
    total_items = sum(
        len(brief.get(t["section"], []))
        for t in WEEKLY_SEARCHES
    )
    log.info(f"Brief complete: {total_items} news items across {len(WEEKLY_SEARCHES)} sections")
    log.info(f"Service approvals: {len(brief['recent_approvals'])}")
    log.info(f"Director records: {len(brief['operator_directors'])}")
    log.info(f"Output: {OUTPUT_FILE}")

    for t in WEEKLY_SEARCHES:
        n = len(brief.get(t["section"], []))
        if n:
            log.info(f"  {t['label']}: {n} items")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true",
                        help="Run regardless of day of week")
    args = parser.parse_args()
    run(force=args.force)
