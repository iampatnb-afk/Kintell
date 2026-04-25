import os
import json
import smtplib
import ssl
from pathlib import Path
try:
    from catchment_html import render_catchment_block
    CATCHMENT_HTML = True
except ImportError:
    CATCHMENT_HTML = False
    def render_catchment_block(lead): return ""

from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

LEADS_FILE = Path("leads_catchment.json")  # updated by module2b
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")


def tier_color(tier):
    colors = {
        "hot": "#D85A30",
        "warm": "#BA7517",
        "watch": "#5F5E5A",
        "existing_client": "#185FA5"
    }
    return colors.get(tier, "#5F5E5A")


def tier_label(tier):
    labels = {
        "hot": "HOT",
        "warm": "WARM",
        "watch": "WATCH",
        "existing_client": "CLIENT"
    }
    return labels.get(tier, tier.upper())


def format_lead_card(lead):
    tier = lead.get("priority_tier", "watch")
    color = tier_color(tier)
    label = tier_label(tier)
    legal_name = lead.get("legal_name", "")
    trading_name = lead.get("trading_name", "")
    display_name = trading_name if trading_name else legal_name
    suburb = lead.get("suburb", "")
    state = lead.get("state", "")
    signal = lead.get("signal_type", "").replace("_", " ").title()
    places = str(lead.get("approved_places", "") or "")
    centre_count = lead.get("group_centre_count", 1)
    confidence = lead.get("group_confidence", "")
    product = lead.get("product_fit", "")
    nfp = lead.get("is_nfp_flag", False)
    contact_name = lead.get("contact_name", "")
    contact_role = lead.get("contact_role", "")
    contact_phone = lead.get("contact_phone", "")
    contact_email = lead.get("contact_email", "")
    contact_linkedin = lead.get("contact_linkedin", "")
    contact_confidence = lead.get("contact_confidence", "")
    acecqa_link = lead.get("acecqa_link", "https://www.acecqa.gov.au/resources/national-registers")

    nfp_badge = ""
    if nfp:
        nfp_badge = "<span style='background:#FAEEDA;color:#633806;padding:2px 8px;border-radius:4px;font-size:11px;margin-left:8px;'>NFP FLAG</span>"

    if contact_name:
        contact_html = (
            "<div style='margin-top:12px;padding:10px;background:#f8f8f6;border-radius:6px;'>"
            "<div style='font-size:12px;color:#5F5E5A;margin-bottom:4px;'>CONTACT</div>"
            "<div style='font-weight:500;'>" + contact_name + "</div>"
            "<div style='color:#5F5E5A;font-size:13px;'>" + contact_role + "</div>"
        )
        if contact_phone:
            contact_html += "<div style='margin-top:4px;'><a href='tel:" + contact_phone + "' style='color:#185FA5;'>" + contact_phone + "</a></div>"
        if contact_email:
            contact_html += "<div><a href='mailto:" + contact_email + "' style='color:#185FA5;'>" + contact_email + "</a></div>"
        if contact_linkedin:
            contact_html += "<div><a href='" + contact_linkedin + "' style='color:#185FA5;'>LinkedIn profile</a></div>"
        contact_html += "<div style='font-size:11px;color:#888;margin-top:4px;'>Confidence: " + contact_confidence + "</div></div>"
    else:
        contact_html = (
            "<div style='margin-top:12px;padding:10px;background:#f8f8f6;border-radius:6px;'>"
            "<div style='font-size:12px;color:#5F5E5A;margin-bottom:4px;'>CONTACT</div>"
            "<div style='color:#888;font-size:13px;'>Not found - manual search required</div>"
            "</div>"
        )

    places_text = (" &bull; " + places + " places") if places and places != "nan" else ""
    group_text = str(centre_count) + " centre" + ("s" if centre_count != 1 else "") + " (" + confidence + ")"

    card = (
        "<div style='border:1px solid #e0e0dc;border-radius:8px;padding:16px;margin-bottom:16px;background:#ffffff;'>"
        "<div style='display:flex;align-items:center;margin-bottom:8px;'>"
        "<span style='background:" + color + ";color:white;padding:3px 10px;border-radius:4px;font-size:12px;font-weight:600;'>" + label + "</span>"
        "<span style='font-size:16px;font-weight:500;margin-left:10px;'>" + display_name + "</span>"
        + nfp_badge +
        "</div>"
        "<div style='color:#5F5E5A;font-size:13px;margin-bottom:2px;'>" + legal_name + "</div>"
        "<div style='font-size:13px;margin-bottom:8px;'>"
        + suburb + ", " + state +
        " &bull; " + signal +
        places_text +
        "</div>"
        "<div style='font-size:13px;color:#3B6D11;margin-bottom:4px;'>Group size: " + group_text + "</div>"
        "<div style='font-size:13px;color:#185FA5;margin-bottom:4px;'>Product fit: " + product + "</div>"
        + contact_html
        + render_catchment_block(lead)
        + "<div style='margin-top:10px;font-size:12px;'>"
        "<a href='" + acecqa_link + "' style='color:#888;'>View on ACECQA</a>"
        "</div>"
        "</div>"
    )
    return card


def build_email_html(leads):
    today = str(date.today())

    # Load weekly news brief if available
    brief_html = ""
    try:
        brief = json.load(open("data/weekly_brief.json", encoding="utf-8"))
        brief_html = brief.get("html", "")
    except Exception:
        pass

    hot_leads    = [l for l in leads if l.get("priority_tier") == "hot"]
    warm_leads   = [l for l in leads if l.get("priority_tier") == "warm"]
    watch_leads  = [l for l in leads if l.get("priority_tier") == "watch"]
    client_leads = [l for l in leads if l.get("priority_tier") == "existing_client"]
    nfp_leads    = [l for l in leads if l.get("is_nfp_flag")]

    def section(title, color, items):
        if not items:
            return ""
        cards = "".join(format_lead_card(l) for l in items)
        return (
            "<div style='margin-bottom:32px;'>"
            "<h2 style='font-size:16px;font-weight:600;color:" + color + ";border-bottom:2px solid " + color + ";padding-bottom:6px;margin-bottom:16px;'>"
            + title + " (" + str(len(items)) + ")</h2>"
            + cards +
            "</div>"
        )

    prospecting_banner = (
        "<div style='margin-top:20px;padding:12px 16px;background:#2c3e50;"
        "border-radius:6px;text-align:center'>"
        "<a href='data/operators_prospecting.html' style='color:#3498db;"
        "font-size:13px;font-weight:bold;text-decoration:none'>"
        "View Full Prospecting List &#8594;</a>"
        "<span style='color:#aaa;font-size:12px;margin-left:16px'>"
        "Hot &amp; warm targets, filterable by state / score / centre count"
        "</span></div><br>"
    )

    footer = (
        "<div style='margin-top:32px;padding:16px;background:#f0f0ec;"
        "border-radius:8px;font-size:12px;color:#888;'>"
        + prospecting_banner +
        "Generated by Remara Market Intelligence Agent &bull; "
        "Data sources: ACECQA National Register &bull; "
        "Remara Weekly Intelligence Pipeline - runs every Tuesday 10:00 AM."
        "</div>"
    )

    body = (
        "<html><body style='font-family:Arial,sans-serif;max-width:680px;"
        "margin:0 auto;padding:20px;color:#2C2C2A;'>"
        "<div style='background:#0F6E56;color:white;padding:20px;"
        "border-radius:8px;margin-bottom:24px;'>"
        "<h1 style='margin:0;font-size:22px;'>Remara Weekly Lead Digest</h1>"
        "<div style='margin-top:4px;opacity:0.85;'>" + today + " &bull; "
        + str(len(hot_leads)) + " hot &bull; "
        + str(len(warm_leads)) + " warm &bull; "
        + str(len(watch_leads)) + " watch"
        + (" &bull; " + str(len(nfp_leads)) + " NFP flagged" if nfp_leads else "")
        + "</div></div>"
        + section("Section A - Hot leads", "#D85A30", hot_leads)
        + section("Section B - Warm leads", "#BA7517", warm_leads)
        + section("Section C - Watch list", "#5F5E5A", watch_leads)
        + section("Section D - Existing clients (activity detected)", "#185FA5", client_leads)
        + brief_html
        + footer
        + "</body></html>"
    )
    return body


def send_email(subject, html_body, to_address):
    from_address = GMAIL_ADDRESS
    app_password = GMAIL_APP_PASSWORD

    if not app_password:
        print("ERROR: GMAIL_APP_PASSWORD not set in .env file")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_address
    msg["To"] = to_address
    msg.attach(MIMEText(html_body, "html"))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(from_address, app_password)
            server.sendmail(from_address, to_address, msg.as_string())
        print("Email sent successfully to", to_address)
        return True
    except Exception as e:
        print("Email error:", e)
        return False


def save_html_preview(html_body):
    preview_path = Path("data/digest_preview.html")
    with open(preview_path, "w", encoding="utf-8") as f:
        f.write(html_body)
    print("HTML preview saved to:", str(preview_path))
    return preview_path


def run_digest():
    print("\n=== Module 5: Email Digest ===")
    print("Run date:", str(date.today()))

    if not LEADS_FILE.exists():
        leads_path = Path("data/leads_today.json")
        if leads_path.exists():
            with open(leads_path) as f:
                leads = json.load(f)
        else:
            print("No leads file found.")
            return
    else:
        with open(LEADS_FILE) as f:
            leads = json.load(f)

    if not leads:
        print("No leads today.")
        leads = []

    print("Building digest for", len(leads), "leads...")

    hot   = len([l for l in leads if l.get("priority_tier") == "hot"])
    warm  = len([l for l in leads if l.get("priority_tier") == "warm"])
    watch = len([l for l in leads if l.get("priority_tier") == "watch"])

    subject = ("Remara Leads " + str(date.today()) +
               " - " + str(hot) + " hot, " + str(warm) + " warm, " + str(watch) + " watch")

    html_body = build_email_html(leads)
    save_html_preview(html_body)
    print("Open this file in your browser to preview: data/digest_preview.html")

    send_email(subject, html_body, GMAIL_ADDRESS)
    print("Digest delivered to", GMAIL_ADDRESS)


if __name__ == "__main__":
    run_digest()
