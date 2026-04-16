"""
generate_dashboard.py — Kintell ECEC Market Intelligence Dashboard
Generates docs/index.html — pushed to GitHub Pages after each weekly run.

Three panels:
  Panel 1 — Industry Snapshot (sector-level metrics from ACECQA + news)
  Panel 2 — Operator Intelligence (all 4,188 operators, searchable by name/director/ABN)
  Panel 3 — Catchment Explorer (search by suburb/SA2)

Plus: AI-generated weekly hot buttons (3-5 left-field observations)

Output: docs/index.html
Run: python generate_dashboard.py
"""

import json
import os
import re
from pathlib import Path
from datetime import date, datetime, timedelta
from collections import Counter, defaultdict

BASE_DIR   = Path(__file__).parent
DATA_DIR   = BASE_DIR / "data"
DOCS_DIR   = BASE_DIR / "docs"
SNAP_FILE  = DATA_DIR / "services_snapshot.csv"
TARGETS    = BASE_DIR / "operators_target_list.json"
HOT        = BASE_DIR / "operators_hot_targets.json"
PROPERTY   = BASE_DIR / "property_owners.json"
BRIEF      = DATA_DIR / "weekly_brief.json"
CATCHMENT  = BASE_DIR / "leads_catchment.json"
HISTORY    = DATA_DIR / "sector_history.json"

DOCS_DIR.mkdir(exist_ok=True)

# ─────────────────────────────────────────────
# DATA LOADERS
# ─────────────────────────────────────────────

def load_json(path, default=None):
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception:
        return default or []


def load_snapshot():
    if not SNAP_FILE.exists():
        return []
    try:
        import pandas as pd
        df = pd.read_csv(SNAP_FILE, dtype=str, low_memory=False)
        df.columns = [c.strip().lower() for c in df.columns]
        return df.to_dict("records")
    except Exception:
        return []


def compute_sector_stats(snap):
    """Compute sector-level statistics from ACECQA snapshot."""
    stats = {
        "total_services": 0,
        "total_places": 0,
        "by_state": {},
        "nqs_dist": {"Exceeding NQS": 0, "Meeting NQS": 0, "Working Towards NQS": 0, "Significant Improvement Required": 0, "Unknown": 0},
        "nfp_count": 0,
        "forprofit_count": 0,
        "kinder_count": 0,
        "service_types": {},
    }

    for row in snap:
        stype = str(row.get("servicetype", "") or "").strip()
        if str(row.get("long_day_care","")).strip().upper() != "YES":
            continue

        stats["total_services"] += 1

        try:
            places = int(str(row.get("numberofapprovedplaces", 0) or 0))
            stats["total_places"] += places
        except Exception:
            pass

        state = str(row.get("state", "") or "").strip().upper()
        if state:
            stats["by_state"][state] = stats["by_state"].get(state, {"services": 0, "places": 0})
            stats["by_state"][state]["services"] += 1
            try:
                stats["by_state"][state]["places"] += int(str(row.get("numberofapprovedplaces", 0) or 0))
            except Exception:
                pass

        nqs = str(row.get("overallrating", "") or "").strip()
        if nqs in stats["nqs_dist"]:
            stats["nqs_dist"][nqs] += 1
        else:
            stats["nqs_dist"]["Unknown"] += 1

    return stats


def get_top_operators(operators, n=20):
    """Top N for-profit non-listed operators by places."""
    listed = {"g8 education", "goodstart", "guardian", "only about children",
              "affinity", "nido", "think childcare", "story house"}
    eligible = [
        o for o in operators
        if not o.get("is_nfp")
        and o.get("legal_name")
        and not any(l in str(o.get("legal_name", "")).lower() for l in listed)
    ]
    eligible.sort(key=lambda x: x.get("total_places", 0) or x.get("n_centres", 0) * 80, reverse=True)
    return eligible[:n]


def parse_date(d):
    """Parse a date string in common formats. Returns datetime or datetime.min."""
    for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"]:
        try:
            return datetime.strptime(str(d), fmt)
        except Exception:
            pass
    return datetime.min


def get_recent_approvals(snap, n=30):
    """Get last N service approvals by date."""
    approvals = []
    for row in snap:
        if str(row.get("long_day_care","")).strip().upper() != "YES":
            continue
        appr_date = str(row.get("serviceapprovalgranteddate", "") or "").strip()
        if not appr_date or appr_date == "nan":
            continue
        approvals.append({
            "service_name":    str(row.get("servicename", "") or "").strip(),
            "legal_name":      str(row.get("providerlegalname", "") or "").strip()[:35],
            "suburb":          str(row.get("suburb", "") or "").strip(),
            "state":           str(row.get("state", "") or "").strip(),
            "places":          str(row.get("approvedplaces", "") or "").strip(),
            "approval_date":   appr_date,
        })

    approvals.sort(key=lambda x: parse_date(x["approval_date"]), reverse=True)
    return approvals[:n]


# ─────────────────────────────────────────────
# HTML BUILDERS
# ─────────────────────────────────────────────

def build_news_html(brief):
    """Build news section HTML from weekly brief."""
    if not brief:
        return "<p style='color:#888;'>News brief not yet available.</p>"

    sections = brief.get("sections", [])
    if not sections:
        return "<p style='color:#888;'>No news items this week.</p>"

    html = ""
    for section in sections:
        items = section.get("items", [])
        if not items:
            continue
        html += f"<div class='news-section'>"
        html += f"<h3 class='news-section-title'>{section.get('title','')}</h3>"
        for item in items:
            title   = item.get("title", "")
            summary = item.get("summary", "")
            source  = item.get("source", "")
            date_s  = item.get("date", "")
            tag     = item.get("tag", "")
            url     = item.get("url", "#")
            tag_html = f"<span class='news-tag'>{tag}</span>" if tag else ""
            html += f"""
            <div class='news-item'>
                <a href='{url}' target='_blank' class='news-title'>{title}</a>
                <p class='news-summary'>{summary}</p>
                <div class='news-meta'>{source} &bull; {date_s} {tag_html}</div>
            </div>"""
        html += "</div>"
    return html


def build_approvals_table(approvals, operators_by_name=None):
    """Build clickable service approvals table."""
    if not approvals:
        return "<p style='color:#888;'>No recent approvals.</p>"

    rows = ""
    for a in approvals:
        name     = a["service_name"]
        operator = a["legal_name"]
        loc      = f"{a['suburb']}, {a['state']}"
        places   = a["places"]
        appr     = a["approval_date"]

        # Check if operator is in our target list
        op_link = ""
        if operators_by_name:
            key = operator.lower()[:20]
            match = next((o for o in operators_by_name
                         if str(o.get("legal_name","")).lower().startswith(key)), None)
            if match:
                tier = match.get("priority_tier", "")
                tier_badge = f"<span class='tier-badge tier-{tier}'>{tier.upper()}</span>"
                op_link = f" {tier_badge}"

        rows += f"""
        <tr class='approval-row' data-operator='{operator}' data-state='{a["state"]}'
            onclick='jumpToOperator("{operator[:30]}")' style='cursor:pointer'>
            <td class='approval-centre' style='color:var(--accent);text-decoration:underline;text-decoration-style:dotted'>{name}</td>
            <td>{operator}{op_link}</td>
            <td>{loc}</td>
            <td class='text-center'>{places}</td>
            <td class='text-center'>{appr}</td>
        </tr>"""

    return f"""
    <table class='approvals-table'>
        <thead>
            <tr>
                <th>Centre</th>
                <th>Operator</th>
                <th>Location</th>
                <th class='text-center'>Places</th>
                <th class='text-center'>Approved</th>
            </tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>"""


def build_operator_cards(operators, property_data=None):
    """Build operator data for Panel 2 as JSON for JS rendering."""
    prop_map = {}
    if property_data:
        for op in property_data.get("operators", []):
            key = str(op.get("legal_name", "")).strip().lower()
            prop_map[key] = op

    cards = []
    for op in operators:
        name    = str(op.get("legal_name") or "").strip()
        if not name or name == "nan":
            continue

        prop = prop_map.get(name.lower(), {})
        fgc  = prop.get("freehold_going_concern", False)

        centres = []
        for c in op.get("centres", []):
            centres.append({
                "name":     str(c.get("service_name", "") or "").strip(),
                "suburb":   str(c.get("suburb", "") or "").strip(),
                "state":    str(c.get("state", "") or "").strip(),
                "postcode": str(c.get("postcode", "") or "").strip(),
                "places":   c.get("places", 0),
                "nqs":      str(c.get("nqs_rating", "") or "").strip(),
                "kinder":   bool(c.get("kinder_approved", False)),
                "appr_num": str(c.get("approval_number", "") or "").strip(),
            })

        related = []
        for r in prop.get("propco_candidates", []):
            related.append({
                "name":   r.get("entity_name", ""),
                "abn":    r.get("abn", ""),
                "is_fgc": r.get("is_fgc_candidate", False),
            })

        abr = prop.get("abr_data", {})

        cards.append({
            "legal_name":  name,
            "tier":        op.get("priority_tier", "watch"),
            "score":       op.get("score", 0),
            "n_centres":   op.get("n_centres", 0),
            "states":      op.get("states", []),
            "is_nfp":      op.get("is_nfp", False),
            "kinder":      op.get("kinder_approved", False),
            "review":      op.get("review_required", False),
            "fgc":         fgc,
            "abn":         abr.get("abn", ""),
            "acn":         abr.get("acn", ""),
            "entity_type": abr.get("entity_type", ""),
            "reg_state":   abr.get("address_state", ""),
            "centres":     centres,
            "propco":      related,
        })

    return cards


def build_state_stats_js(stats):
    """Build state statistics as JS object."""
    state_order = ["NSW", "VIC", "QLD", "WA", "SA", "TAS", "ACT", "NT"]
    labels = []
    services = []
    places = []
    for s in state_order:
        if s in stats["by_state"]:
            labels.append(s)
            services.append(stats["by_state"][s]["services"])
            places.append(stats["by_state"][s]["places"])
    return {
        "labels": labels,
        "services": services,
        "places": places,
    }


# ─────────────────────────────────────────────
# MAIN HTML GENERATOR
# ─────────────────────────────────────────────

def generate():
    print("=== Kintell Dashboard Generator ===")
    today = str(date.today())

    # Load data
    print("Loading data...")
    snap       = load_snapshot()
    operators  = load_json(TARGETS, [])
    hot        = load_json(HOT, [])
    property_d = load_json(PROPERTY, {})
    brief      = load_json(BRIEF, {})

    print(f"  Snapshot: {len(snap):,} services")
    history    = load_json(HISTORY, {})
    hist_data  = history.get("history", [])
    print(f"  History: {len(hist_data)} quarters ({hist_data[0]['quarter'] if hist_data else 'none'} → {hist_data[-1]['quarter'] if hist_data else 'none'})")
    print(f"  Operators: {len(operators):,}")
    print(f"  Property data: {len(property_d.get('operators',[]))} enriched")

    # Compute stats
    stats       = compute_sector_stats(snap)
    top_ops     = get_top_operators(operators)
    approvals   = get_recent_approvals(snap, 30)
    state_stats = build_state_stats_js(stats)

    # Compute formative centres — approved within last 18 months
    cutoff_24m = datetime.now() - timedelta(days=548)
    cutoff_30d = datetime.now() - timedelta(days=30)
    formative_count = sum(
        1 for row in snap
        if str(row.get("long_day_care","")).strip().upper() == "YES"
        and parse_date(str(row.get("serviceapprovalgranteddate","") or "")) > cutoff_24m
    )
    formative_pct = round(formative_count / stats['total_services'] * 100, 1) if stats['total_services'] else 0
    approvals_30d = sum(
        1 for row in snap
        if str(row.get("long_day_care","")).strip().upper() == "YES"
        and parse_date(str(row.get("serviceapprovalgranteddate","") or "")) > cutoff_30d
    )

    # Build history JS data for trend charts
    hist_js = {
        "labels":     [h["quarter"] for h in hist_data],
        "dates":      [h["date"] for h in hist_data],
        "services":   [h["total_ldc"] for h in hist_data],
        "places":     [h["total_places"] for h in hist_data],
        "exceeding":  [h["exceeding"] for h in hist_data],
        "meeting":    [h["meeting"] for h in hist_data],
        "working":    [h["working"] for h in hist_data],
        "nfp":        [h.get("nfp", 0) for h in hist_data],
        "forprofit":  [h.get("forprofit", 0) for h in hist_data],
        "nsw":        [h.get("by_state", {}).get("NSW", 0) for h in hist_data],
        "vic":        [h.get("by_state", {}).get("VIC", 0) for h in hist_data],
        "qld":        [h.get("by_state", {}).get("QLD", 0) for h in hist_data],
        "wa":         [h.get("by_state", {}).get("WA", 0) for h in hist_data],
        "sa":         [h.get("by_state", {}).get("SA", 0) for h in hist_data],
        "major_cities":   [(h.get("by_aria") or {}).get("Major Cities of Australia") for h in hist_data],
        "inner_regional": [(h.get("by_aria") or {}).get("Inner Regional Australia") for h in hist_data],
        "outer_regional": [(h.get("by_aria") or {}).get("Outer Regional Australia") for h in hist_data],
        "remote":         [(h.get("by_aria") or {}).get("Remote Australia") for h in hist_data],
        "very_remote":    [(h.get("by_aria") or {}).get("Very Remote Australia") for h in hist_data],
        "supply_demand":  [h.get("supply_demand_ratio") for h in hist_data],
        "new_approvals":  [h.get("new_approvals") for h in hist_data],
    }
    op_cards    = build_operator_cards(operators, property_d)
    news_html   = build_news_html(brief)
    approvals_html = build_approvals_table(approvals, operators)

    nqs = stats["nqs_dist"]
    total_nqs = sum(nqs.values()) or 1

    # Build top operators table
    top_ops_rows = ""
    for i, op in enumerate(top_ops, 1):
        name     = str(op.get("legal_name") or "")[:45]
        centres  = op.get("n_centres", 0)
        states   = ", ".join(op.get("states", []))
        score    = op.get("score", 0)
        tier     = op.get("priority_tier", "watch")
        op_js_name = name.replace("'", "").replace('"', '')
        top_ops_rows += f"""
        <tr onclick="jumpToOperator('{op_js_name}')" data-states="{','.join(op.get('states',[]))}" style='cursor:pointer'>
            <td class='rank'>{i}</td>
            <td class='op-name'>{name}</td>
            <td class='text-center'>{centres}</td>
            <td>{states}</td>
            <td class='text-center'><span class='tier-badge tier-{tier}'>{tier.upper()}</span></td>
            <td class='text-center'>{score}</td>
        </tr>"""

    # Serialize operator cards for JS
    # Save operators as separate JSON file for performance
    ops_json_path = DOCS_DIR / "operators.json"
    with open(ops_json_path, "w", encoding="utf-8") as f:
        json.dump(op_cards, f, ensure_ascii=False)
    print(f"  Operators JSON: {ops_json_path.name} ({len(op_cards):,} operators)")
    op_cards_json = "[]"  # placeholder — loaded via fetch

    # Build week date range
    week_start = brief.get("week_start", "")
    week_end   = brief.get("week_end", today)
    week_range = f"{week_start} — {week_end}" if week_start else today

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Kintell — ECEC Market Intelligence</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&family=Playfair+Display:wght@600&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
:root {{
    --bg:        #0f1117;
    --surface:   #181c26;
    --surface2:  #1e2333;
    --border:    #2a2f3f;
    --text:      #e8eaf0;
    --muted:     #8890a8;
    --accent:    #3d7eff;
    --accent2:   #00c9a7;
    --hot:       #e05c3a;
    --warm:      #d4890a;
    --watch:     #5a6480;
    --fgc:       #9b59b6;
    --radius:    10px;
    --font:      'DM Sans', sans-serif;
    --mono:      'DM Mono', monospace;
    --display:   'Playfair Display', serif;
}}

* {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
    font-family: var(--font);
    background: var(--bg);
    color: var(--text);
    font-size: 14px;
    line-height: 1.6;
}}

/* ── HEADER ── */
.header {{
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 0 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 60px;
    position: sticky;
    top: 0;
    z-index: 100;
}}

.logo {{
    font-family: var(--display);
    font-size: 22px;
    color: var(--text);
    letter-spacing: -0.5px;
}}

.logo span {{ color: var(--accent); }}

.header-meta {{
    font-family: var(--mono);
    font-size: 11px;
    color: var(--muted);
}}

/* ── TABS ── */
.tabs {{
    display: flex;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 0 32px;
    gap: 0;
}}

.tab {{
    padding: 14px 24px;
    cursor: pointer;
    color: var(--muted);
    font-size: 13px;
    font-weight: 500;
    border-bottom: 2px solid transparent;
    transition: all 0.2s;
    user-select: none;
}}

.tab:hover {{ color: var(--text); }}
.tab.active {{
    color: var(--accent);
    border-bottom-color: var(--accent);
}}

/* ── PANELS ── */
.panel {{ display: none; padding: 32px; max-width: 1400px; margin: 0 auto; }}
.panel.active {{ display: block; }}

/* ── STAT CARDS ── */
.stat-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px;
    margin-bottom: 32px;
}}

.stat-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px;
}}

.stat-label {{
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted);
    margin-bottom: 8px;
}}

.stat-value {{
    font-size: 28px;
    font-weight: 600;
    color: var(--text);
    line-height: 1;
}}

.stat-sub {{
    font-size: 12px;
    color: var(--muted);
    margin-top: 4px;
}}

/* ── SECTION HEADERS ── */
.section {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px;
    margin-bottom: 24px;
}}

.section-title {{
    font-size: 13px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted);
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border);
}}

/* ── TWO COLUMN ── */
.two-col {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    margin-bottom: 24px;
}}

@media (max-width: 900px) {{
    .two-col {{ grid-template-columns: 1fr; }}
}}

/* ── NQS BARS ── */
.nqs-bar-wrap {{
    display: flex;
    flex-direction: column;
    gap: 10px;
}}

.nqs-row {{
    display: flex;
    align-items: center;
    gap: 12px;
}}

.nqs-label {{
    width: 180px;
    font-size: 12px;
    color: var(--muted);
    flex-shrink: 0;
}}

.nqs-bar-bg {{
    flex: 1;
    height: 8px;
    background: var(--surface2);
    border-radius: 4px;
    overflow: hidden;
}}

.nqs-bar-fill {{
    height: 100%;
    border-radius: 4px;
    transition: width 0.8s ease;
}}

.nqs-count {{
    font-family: var(--mono);
    font-size: 11px;
    color: var(--muted);
    width: 50px;
    text-align: right;
}}

/* ── STATE CHART ── */
.state-chart {{
    display: flex;
    flex-direction: column;
    gap: 10px;
}}

.state-row {{
    display: flex;
    align-items: center;
    gap: 12px;
}}

.state-label {{
    width: 40px;
    font-family: var(--mono);
    font-size: 12px;
    font-weight: 500;
    color: var(--text);
}}

.state-bar-bg {{
    flex: 1;
    height: 10px;
    background: var(--surface2);
    border-radius: 5px;
    overflow: hidden;
}}

.state-bar-fill {{
    height: 100%;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    border-radius: 5px;
}}

.state-count {{
    font-family: var(--mono);
    font-size: 11px;
    color: var(--muted);
    width: 60px;
    text-align: right;
}}

/* ── TOP OPERATORS TABLE ── */
.data-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}}

.data-table th {{
    text-align: left;
    padding: 8px 12px;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--muted);
    border-bottom: 1px solid var(--border);
    font-weight: 500;
}}

.data-table td {{
    padding: 10px 12px;
    border-bottom: 1px solid var(--border);
    color: var(--text);
}}

.data-table tr:last-child td {{ border-bottom: none; }}
.data-table tr:hover td {{ background: var(--surface2); cursor: pointer; }}

.rank {{
    font-family: var(--mono);
    color: var(--muted);
    width: 30px;
}}

.op-name {{ font-weight: 500; }}
.text-center {{ text-align: center; }}

/* ── TIER BADGES ── */
.tier-badge {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.05em;
}}

.tier-hot   {{ background: rgba(224,92,58,0.15); color: var(--hot); }}
.tier-warm  {{ background: rgba(212,137,10,0.15); color: var(--warm); }}
.tier-watch {{ background: rgba(90,100,128,0.15); color: var(--watch); }}
.tier-nfp   {{ background: rgba(155,89,182,0.1);  color: #c39bd3; }}

.fgc-badge {{
    display: inline-block;
    padding: 2px 7px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: 600;
    background: rgba(155,89,182,0.15);
    color: var(--fgc);
    margin-left: 6px;
}}

/* ── APPROVALS TABLE ── */
.approvals-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
}}

.approvals-table th {{
    text-align: left;
    padding: 8px 10px;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--muted);
    border-bottom: 1px solid var(--border);
}}

.approvals-table td {{
    padding: 9px 10px;
    border-bottom: 1px solid var(--border);
}}

.approval-row:hover td {{
    background: var(--surface2);
    cursor: pointer;
}}

.approval-centre {{ font-weight: 500; color: var(--text); }}

/* ── NEWS ── */
.news-section {{ margin-bottom: 24px; }}

.news-section-title {{
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--accent);
    margin-bottom: 14px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
}}

.news-item {{
    padding: 14px 0;
    border-bottom: 1px solid var(--border);
}}

.news-item:last-child {{ border-bottom: none; }}

.news-title {{
    display: block;
    font-size: 14px;
    font-weight: 500;
    color: var(--text);
    text-decoration: none;
    margin-bottom: 6px;
    line-height: 1.4;
}}

.news-title:hover {{ color: var(--accent); }}

.news-summary {{
    font-size: 13px;
    color: var(--muted);
    margin-bottom: 8px;
    line-height: 1.5;
}}

.news-meta {{
    font-size: 11px;
    color: var(--watch);
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}}

.news-tag {{
    background: var(--surface2);
    padding: 1px 8px;
    border-radius: 10px;
    font-size: 10px;
    color: var(--accent2);
}}

/* ── PANEL 2 — OPERATOR SEARCH ── */
.search-bar {{
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
    flex-wrap: wrap;
}}

.search-input {{
    flex: 1;
    min-width: 200px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 16px;
    color: var(--text);
    font-family: var(--font);
    font-size: 13px;
    outline: none;
    transition: border-color 0.2s;
}}

.search-input:focus {{ border-color: var(--accent); }}
.search-input::placeholder {{ color: var(--muted); }}

.filter-select {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 14px;
    color: var(--text);
    font-family: var(--font);
    font-size: 13px;
    outline: none;
    cursor: pointer;
}}

.filter-select:focus {{ border-color: var(--accent); }}

/* ── OPERATOR LIST ── */
.op-list {{
    display: flex;
    flex-direction: column;
    gap: 2px;
}}

.op-row {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px 16px;
    cursor: pointer;
    transition: all 0.15s;
    display: flex;
    align-items: center;
    gap: 12px;
}}

.op-row:hover {{ border-color: var(--accent); background: var(--surface2); }}
.op-row.expanded {{ border-color: var(--accent); background: var(--surface2); border-bottom-left-radius: 0; border-bottom-right-radius: 0; }}

.op-row-name {{
    flex: 1;
    font-weight: 500;
    font-size: 13px;
}}

.op-row-meta {{
    font-size: 12px;
    color: var(--muted);
    display: flex;
    gap: 12px;
    align-items: center;
}}

.op-detail {{
    display: none;
    background: var(--surface2);
    border: 1px solid var(--accent);
    border-top: none;
    border-bottom-left-radius: 8px;
    border-bottom-right-radius: 8px;
    padding: 20px;
    margin-bottom: 2px;
}}

.op-detail.visible {{ display: block; }}

.detail-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 16px;
}}

.detail-block {{
    background: var(--surface);
    border-radius: 6px;
    padding: 12px;
}}

.detail-block-label {{
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted);
    margin-bottom: 6px;
}}

.detail-block-value {{
    font-size: 13px;
    font-weight: 500;
}}

.propco-list {{
    margin-top: 12px;
}}

.propco-item {{
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 0;
    border-bottom: 1px solid var(--border);
    font-size: 12px;
}}

.propco-item:last-child {{ border-bottom: none; }}

.centres-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 10px;
    margin-top: 16px;
}}

.centre-card {{
    background: var(--surface);
    border-radius: 6px;
    padding: 12px;
    font-size: 12px;
}}

.centre-name {{
    font-weight: 500;
    margin-bottom: 4px;
    font-size: 13px;
}}

.centre-meta {{
    color: var(--muted);
    margin-bottom: 8px;
}}

.centre-links {{
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}}

.centre-link {{
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 4px;
    background: var(--surface2);
    color: var(--accent);
    text-decoration: none;
    border: 1px solid var(--border);
}}

.centre-link:hover {{ border-color: var(--accent); }}

.result-count {{
    font-size: 12px;
    color: var(--muted);
    margin-bottom: 12px;
    font-family: var(--mono);
}}

/* ── LOADING STATE ── */
.loading {{
    text-align: center;
    padding: 60px;
    color: var(--muted);
}}

/* ── HOT BUTTONS ── */
.hot-buttons {{
    display: flex;
    flex-direction: column;
    gap: 12px;
}}

.hot-button {{
    background: linear-gradient(135deg, var(--surface) 0%, rgba(61,126,255,0.05) 100%);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent2);
    border-radius: var(--radius);
    padding: 16px 20px;
}}

.hot-button-label {{
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--accent2);
    margin-bottom: 6px;
}}

.hot-button-text {{
    font-size: 13px;
    color: var(--text);
    line-height: 1.5;
}}

.hot-button-conf {{
    font-size: 11px;
    color: var(--muted);
    margin-top: 6px;
    font-family: var(--mono);
}}

/* ── TIME RANGE BUTTONS ── */
.range-btn {{
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 5px;
    padding: 4px 12px;
    color: var(--muted);
    font-family: var(--mono);
    font-size: 11px;
    cursor: pointer;
    transition: all 0.15s;
}}
.range-btn:hover {{ color: var(--text); border-color: var(--accent); }}
.range-btn.active {{ background: var(--accent); color: white; border-color: var(--accent); }}

/* ── SCROLLBAR ── */
::-webkit-scrollbar {{ width: 6px; }}
::-webkit-scrollbar-track {{ background: var(--bg); }}
::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 3px; }}
</style>
</head>
<body>

<header class="header">
    <div class="logo">Kint<span>ell</span></div>
    <div class="header-meta">ECEC Market Intelligence &bull; Updated {today} &bull; {len(snap):,} services tracked</div>
</header>

<nav class="tabs">
    <div class="tab active" onclick="showPanel('industry')">Industry Snapshot</div>
    <div class="tab" onclick="showPanel('operators')">Operator Intelligence</div>
    <div class="tab" onclick="showPanel('catchment')">Catchment Explorer</div>
</nav>

<!-- ═══════════════════════════════════════════ -->
<!-- PANEL 1 — INDUSTRY SNAPSHOT                -->
<!-- ═══════════════════════════════════════════ -->
<div class="panel active" id="panel-industry">

    <!-- UNIFIED FILTER BAR -->
    <div style="background:var(--surface2);border:1px solid var(--border);border-radius:8px;padding:14px 16px;margin-bottom:20px">
        <div style="display:flex;align-items:center;gap:16px;margin-bottom:10px">
            <div style="font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);width:64px;flex-shrink:0">State</div>
            <div style="display:flex;gap:6px;flex-wrap:wrap" id="state-filter-btns">
                <button class="range-btn active" onclick="setStateFilter('',this)">National</button>
                <button class="range-btn" onclick="setStateFilter('NSW',this)">NSW</button>
                <button class="range-btn" onclick="setStateFilter('VIC',this)">VIC</button>
                <button class="range-btn" onclick="setStateFilter('QLD',this)">QLD</button>
                <button class="range-btn" onclick="setStateFilter('WA',this)">WA</button>
                <button class="range-btn" onclick="setStateFilter('SA',this)">SA</button>
                <button class="range-btn" onclick="setStateFilter('TAS',this)">TAS</button>
                <button class="range-btn" onclick="setStateFilter('ACT',this)">ACT</button>
                <button class="range-btn" onclick="setStateFilter('NT',this)">NT</button>
            </div>
            <div id="state-filter-label" style="font-size:12px;color:var(--accent2);margin-left:4px;white-space:nowrap"></div>
        </div>
        <div style="height:1px;background:var(--border);margin-bottom:10px"></div>
        <div style="display:flex;align-items:center;gap:16px">
            <div style="font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);width:64px;flex-shrink:0">Location</div>
            <div style="display:flex;gap:6px;flex-wrap:wrap" id="aria-filter-btns">
                <button class="range-btn active" onclick="setAriaFilter('',this)">All</button>
                <button class="range-btn" onclick="setAriaFilter('major',this)">Major Cities</button>
                <button class="range-btn" onclick="setAriaFilter('inner',this)">Inner Regional</button>
                <button class="range-btn" onclick="setAriaFilter('outer',this)">Outer Regional</button>
                <button class="range-btn" onclick="setAriaFilter('remote',this)">Remote</button>
                <button class="range-btn" onclick="setAriaFilter('very_remote',this)">Very Remote</button>
            </div>
        </div>
    </div>

    <div class="stat-grid">
        <div class="stat-card">
            <div class="stat-label">LDC Services</div>
            <div class="stat-value">{stats['total_services']:,}</div>
            <div class="stat-sub">Active nationally</div>
            <div id="growth-services" style="margin-top:8px;font-size:11px;color:var(--muted)">Loading...</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Licensed Places</div>
            <div class="stat-value">{stats['total_places']:,}</div>
            <div class="stat-sub">Total capacity</div>
            <div id="growth-places" style="margin-top:8px;font-size:11px;color:var(--muted)">Loading...</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Exceeding NQS</div>
            <div class="stat-value">{round(nqs['Exceeding NQS']/total_nqs*100)}%</div>
            <div class="stat-sub">{nqs['Exceeding NQS']:,} services</div>
            <div id="growth-nqs" style="margin-top:8px;font-size:11px;color:var(--muted)">Loading...</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">New Approvals (30d)</div>
            <div class="stat-value">{approvals_30d}</div>
            <div class="stat-sub">New LDC services approved</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Regulatory Stress</div>
            <div class="stat-value">{round(nqs['Working Towards NQS']/total_nqs*100)}%</div>
            <div class="stat-sub">{nqs['Working Towards NQS']:,} working towards NQS</div>
            <div id="growth-wtn" style="margin-top:8px;font-size:11px;color:var(--muted)">Loading...</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Formative Centres</div>
            <div class="stat-value">{formative_pct}%</div>
            <div class="stat-sub">{formative_count:,} approved in last 18 months</div>
        </div>
    </div>

    <!-- TREND CHARTS -->
    <div class="section" style="margin-bottom:24px">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px">
            <div class="section-title" style="margin-bottom:0">Sector Growth — Q3 2013 to Q4 2025</div>
            <div style="display:flex;gap:12px;align-items:center">
                <div style="display:flex;gap:6px" id="time-range-btns">
                    <button class="range-btn" onclick="setRange(4,this)">1Y</button>
                    <button class="range-btn" onclick="setRange(8,this)">2Y</button>
                    <button class="range-btn" onclick="setRange(20,this)">5Y</button>
                    <button class="range-btn active" onclick="setRange(0,this)">All</button>
                </div>
                <div style="width:1px;height:20px;background:var(--border)"></div>
                <div style="display:flex;gap:6px" id="compare-btns">
                    <button class="range-btn active" onclick="setCompare(1,'QoQ',this)">QoQ</button>
                    <button class="range-btn" onclick="setCompare(2,'HoH',this)">HoH</button>
                    <button class="range-btn" onclick="setCompare(4,'YoY',this)">YoY</button>
                </div>
            </div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:24px">
            <div>
                <div style="font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-bottom:8px">Total LDC Services</div>
                <div id="stat-services-growth" style="font-size:11px;color:var(--accent2);margin-bottom:8px"></div>
                <canvas id="chart-services" height="120"></canvas>
            </div>
            <div>
                <div style="font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-bottom:8px">Licensed Places</div>
                <div id="stat-places-growth" style="font-size:11px;color:var(--accent2);margin-bottom:8px"></div>
                <canvas id="chart-places" height="120"></canvas>
            </div>
            <div>
                <div style="font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-bottom:8px">NQS Quality & Stress (%)</div>
                <canvas id="chart-nqs" height="120"></canvas>
            </div>
            <div>
                <div style="font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-bottom:8px">State Growth (LDC Services)</div>
                <canvas id="chart-states" height="120"></canvas>
            </div>
            <div>
                <div style="font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-bottom:8px">Top 10 Operators — Licensed Places</div>
                <div id="chart-concentration" style="padding-top:4px"></div>
            </div>
            <div>
                <div style="font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-bottom:8px">For-Profit % Share</div>
                <div id="stat-fp-growth" style="font-size:11px;color:var(--accent2);margin-bottom:8px"></div>
                <canvas id="chart-fp-pct" height="120"></canvas>
            </div>
            <div>
                <div style="font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-bottom:8px">Supply/Demand Ratio — Licensed Places per 100 Children Under 5</div>
                <div id="stat-supply-demand" style="font-size:11px;color:var(--accent2);margin-bottom:8px"></div>
                <canvas id="chart-supply-demand" height="120"></canvas>
            </div>
            <div>
                <div style="font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-bottom:8px">New Service Approvals per Quarter <span style="color:var(--muted);font-size:10px">(4-quarter rolling sum)</span></div>
                <div id="stat-new-approvals" style="font-size:11px;color:var(--accent2);margin-bottom:8px"></div>
                <canvas id="chart-new-approvals" height="120"></canvas>
                <div style="margin-top:10px;padding:10px 12px;background:var(--surface2);border-left:3px solid var(--warm);border-radius:0 6px 6px 0;font-size:11px;color:var(--muted);line-height:1.6">
                    <span style="color:var(--warm);font-weight:600">Seasonal pattern:</span> Q1 (Jan–Mar) approvals average 101/quarter vs 77 for Q2–Q4 — a structural 30% premium. Operators target Q1 openings to capture the new-year enrolment wave, making Q1 the lowest-risk quarter to begin ramp-up. A Q1 undershoot is an early pipeline slowdown signal; a Q2–Q4 spike (as seen post-CCS Reform 2023–24) indicates operators accelerating despite the seasonal headwind.
                </div>
            </div>
        </div>
    </div>

    <div class="two-col">
        <div class="section">
            <div class="section-title">Services by State</div>
            <div class="state-chart" id="state-chart"></div>
        </div>
        <div class="section">
            <div class="section-title">NQS Rating Distribution</div>
            <div class="nqs-bar-wrap">
                <div class="nqs-row">
                    <div class="nqs-label">Exceeding NQS</div>
                    <div class="nqs-bar-bg"><div class="nqs-bar-fill" style="width:{round(nqs['Exceeding NQS']/total_nqs*100)}%;background:#00c9a7;"></div></div>
                    <div class="nqs-count">{nqs['Exceeding NQS']:,}</div>
                </div>
                <div class="nqs-row">
                    <div class="nqs-label">Meeting NQS</div>
                    <div class="nqs-bar-bg"><div class="nqs-bar-fill" style="width:{round(nqs['Meeting NQS']/total_nqs*100)}%;background:#3d7eff;"></div></div>
                    <div class="nqs-count">{nqs['Meeting NQS']:,}</div>
                </div>
                <div class="nqs-row">
                    <div class="nqs-label">Working Towards</div>
                    <div class="nqs-bar-bg"><div class="nqs-bar-fill" style="width:{round(nqs['Working Towards NQS']/total_nqs*100)}%;background:#d4890a;"></div></div>
                    <div class="nqs-count">{nqs['Working Towards NQS']:,}</div>
                </div>
                <div class="nqs-row">
                    <div class="nqs-label">Sig. Improvement Req.</div>
                    <div class="nqs-bar-bg"><div class="nqs-bar-fill" style="width:{round(nqs['Significant Improvement Required']/total_nqs*100)}%;background:#e05c3a;"></div></div>
                    <div class="nqs-count">{nqs['Significant Improvement Required']:,}</div>
                </div>
                <div class="nqs-row">
                    <div class="nqs-label">Not Yet Rated</div>
                    <div class="nqs-bar-bg"><div class="nqs-bar-fill" style="width:{round(nqs['Unknown']/total_nqs*100)}%;background:#5a6480;"></div></div>
                    <div class="nqs-count">{nqs['Unknown']:,}</div>
                </div>
            </div>
        </div>
    </div>

    <!-- METRO / REGIONAL BREAKDOWN -->
    <div class="section" style="margin-bottom:24px">
        <div style="margin-bottom:16px">
            <div class="section-title" style="margin-bottom:0">Metro vs Regional Breakdown</div>
        </div>
        <div id="aria-breakdown-cards" style="display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:16px">
        </div>
        <div style="font-size:11px;color:var(--muted);line-height:1.8;padding:12px;background:var(--surface2);border-radius:6px">
            <strong style="color:var(--text)">ARIA+ Remoteness definitions:</strong>&nbsp;&nbsp;
            <strong style="color:#3d7eff">Major Cities</strong> — pop. centres &ge;100,000 &bull;
            <strong style="color:#00c9a7">Inner Regional</strong> — reasonably accessible, pop. 1,000&ndash;99,999 &bull;
            <strong style="color:#d4890a">Outer Regional</strong> — limited accessibility &bull;
            <strong style="color:#e05c3a">Remote</strong> — very limited service access &bull;
            <strong style="color:#9b59b6">Very Remote</strong> — extremely isolated communities
        </div>
    </div>

    <div class="two-col">
        <div class="section">
            <div class="section-title">Top 20 For-Profit Operators (non-listed)</div>
            <table class="data-table" id="top20-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Operator</th>
                        <th class="text-center">Centres</th>
                        <th>States</th>
                        <th class="text-center">Tier</th>
                        <th class="text-center">Score</th>
                    </tr>
                </thead>
                <tbody>{top_ops_rows}</tbody>
            </table>
        </div>
        <div class="section">
            <div class="section-title">Weekly Intelligence Signals</div>
            <div class="hot-buttons" id="hot-buttons">
                <div class="hot-button">
                    <div class="hot-button-label">Signal</div>
                    <div class="hot-button-text">Loading weekly signals...</div>
                </div>
            </div>
        </div>
    </div>

    <div class="section">
        <div class="section-title">Weekly News &bull; {week_range}</div>
        {news_html}
    </div>

    <div class="section">
        <div class="section-title">Last 30 Service Approvals</div>
        {approvals_html}
    </div>

</div>

<!-- ═══════════════════════════════════════════ -->
<!-- PANEL 2 — OPERATOR INTELLIGENCE            -->
<!-- ═══════════════════════════════════════════ -->
<div class="panel" id="panel-operators">

    <div class="search-bar">
        <input type="text" class="search-input" id="op-search"
               placeholder="Search by operator name, director, ABN, suburb..."
               oninput="filterOperators()">
        <select class="filter-select" id="op-tier" onchange="filterOperators()">
            <option value="">All tiers</option>
            <option value="hot">Hot</option>
            <option value="warm">Warm</option>
            <option value="watch">Watch</option>
        </select>
        <select class="filter-select" id="op-state" onchange="filterOperators()">
            <option value="">All states</option>
            <option value="NSW">NSW</option>
            <option value="VIC">VIC</option>
            <option value="QLD">QLD</option>
            <option value="WA">WA</option>
            <option value="SA">SA</option>
            <option value="TAS">TAS</option>
            <option value="ACT">ACT</option>
            <option value="NT">NT</option>
        </select>
        <select class="filter-select" id="op-fgc" onchange="filterOperators()">
            <option value="">All structures</option>
            <option value="fgc">Freehold Going Concern</option>
        </select>
    </div>

    <div class="result-count" id="op-count">Loading operators...</div>
    <div class="op-list" id="op-list"></div>

</div>

<!-- ═══════════════════════════════════════════ -->
<!-- PANEL 3 — CATCHMENT EXPLORER               -->
<!-- ═══════════════════════════════════════════ -->
<div class="panel" id="panel-catchment">
    <div class="section">
        <div class="section-title">Catchment Explorer</div>
        <div class="search-bar">
            <input type="text" class="search-input" id="catch-search"
                   placeholder="Search by suburb, postcode, or SA2..."
                   oninput="filterCatchments()">
        </div>
        <div id="catchment-results">
            <p style="color:var(--muted);padding:20px 0;">
                Enter a suburb or postcode to explore catchment intelligence.
            </p>
        </div>
    </div>
</div>

<script>
// ── STATE FILTER ──
var currentStateFilter = '';

function setStateFilter(state, el) {{
    currentStateFilter = state;
    document.querySelectorAll('#state-filter-btns .range-btn').forEach(b => b.classList.remove('active'));
    if (el) el.classList.add('active');
    applyFilters();
    rebuildChartsForFilter();
}}

function updateStatCardsForState(state) {{
    // Kept for compatibility
}}


// ── TAB NAVIGATION ──
function showPanel(name) {{
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.getElementById('panel-' + name).classList.add('active');
    event.target.classList.add('active');
}}

// ── STATE CHART ──
const stateData = {json.dumps(state_stats)};
const histData = {json.dumps(hist_js)};
function buildStateChart() {{
    const el = document.getElementById('state-chart');
    const max = Math.max(...stateData.services);
    el.innerHTML = stateData.labels.map((s, i) => `
        <div class="state-row">
            <div class="state-label">${{s}}</div>
            <div class="state-bar-bg">
                <div class="state-bar-fill" style="width:${{Math.round(stateData.services[i]/max*100)}}%"></div>
            </div>
            <div class="state-count">${{stateData.services[i].toLocaleString()}}</div>
        </div>
    `).join('');
}}
buildStateChart();

// Populate stat card growth rates from history
var currentAriaFilter = '';

// Maps ARIA key → histData series key
var ARIA_SERIES = {{
    'major':       'major_cities',
    'inner':       'inner_regional',
    'outer':       'outer_regional',
    'remote':      'remote',
    'very_remote': 'very_remote',
}};

function rebuildChartsForFilter() {{
    Object.values(chartInstances).forEach(c => c.destroy());
    chartInstances = {{}};
    buildTrendCharts();
}}

function setAriaFilter(aria, el) {{
    currentAriaFilter = aria;
    document.querySelectorAll('#aria-filter-btns .range-btn').forEach(b => b.classList.remove('active'));
    if (el) el.classList.add('active');
    document.querySelectorAll('.aria-card').forEach(c => {{
        c.style.opacity = (!aria || c.dataset.aria === aria) ? '1' : '0.3';
    }});
    applyFilters();
    rebuildChartsForFilter();
}}

// ARIA label → key mapping for row data attributes
const ARIA_KEYS = {{
    'major':      'Major Cities of Australia',
    'inner':      'Inner Regional Australia',
    'outer':      'Outer Regional Australia',
    'remote':     'Remote Australia',
    'very_remote':'Very Remote Australia',
}};

function applyFilters() {{
    const state = currentStateFilter;
    const aria  = currentAriaFilter;
    const ariaLabel = aria ? ARIA_KEYS[aria] : '';

    // Filter Top 20 table
    document.querySelectorAll('#top20-table tr[data-states]').forEach(row => {{
        const rowStates = (row.dataset.states || '').split(',');
        const stateOk = !state || rowStates.includes(state);
        row.style.display = stateOk ? '' : 'none';
    }});

    // Filter approvals table
    document.querySelectorAll('.approval-row').forEach(row => {{
        const rowState = row.dataset.state || '';
        const stateOk  = !state || rowState === state;
        row.style.display = stateOk ? '' : 'none';
    }});

    // Update state label
    const label = document.getElementById('state-filter-label');
    if (label) {{
        let parts = [];
        if (state) parts.push(state);
        if (ariaLabel) parts.push(ariaLabel);
        if (parts.length > 0) {{
            const stateData = state ? histData[state.toLowerCase()] : histData.services;
            const latest = stateData ? stateData[stateData.length-1] : 0;
            const prev4  = stateData ? stateData[stateData.length-5] : 0;
            const yoy    = prev4 ? (((latest-prev4)/prev4)*100).toFixed(1) : '';
            const sign   = yoy > 0 ? '+' : '';
            label.textContent = parts.join(' · ') + (latest ? ': ' + latest.toLocaleString() + ' services' : '') + (yoy ? '  (1Y: ' + sign + yoy + '%)' : '');
        }} else {{
            label.textContent = '';
        }}
    }}
}}

function buildAriaCards() {{
    if (!histData || !histData.major_cities) return;
    const el = document.getElementById('aria-breakdown-cards');
    if (!el) return;
    const n = histData.major_cities.length;
    if (n === 0) return;

    const categories = [
        {{ key: 'major', label: 'Major Cities', data: histData.major_cities, color: '#3d7eff' }},
        {{ key: 'inner', label: 'Inner Regional', data: histData.inner_regional, color: '#00c9a7' }},
        {{ key: 'outer', label: 'Outer Regional', data: histData.outer_regional, color: '#d4890a' }},
        {{ key: 'remote', label: 'Remote', data: histData.remote, color: '#e05c3a' }},
        {{ key: 'very_remote', label: 'Very Remote', data: histData.very_remote, color: '#9b59b6' }},
    ];

    el.innerHTML = categories.map(cat => {{
        const latest = cat.data[n-1] || 0;
        const prev4  = cat.data[n-5] || 0;
        const yoy    = prev4 ? (((latest - prev4) / prev4) * 100).toFixed(1) : '—';
        const sign   = yoy > 0 ? '+' : '';
        const yoyColor = yoy > 0 ? 'var(--accent2)' : yoy < 0 ? 'var(--hot)' : 'var(--muted)';
        return `
        <div class="aria-card stat-card" data-aria="${{cat.key}}" style="border-top:2px solid ${{cat.color}}">
            <div class="stat-label">${{cat.label}}</div>
            <div class="stat-value" style="font-size:22px">${{latest.toLocaleString()}}</div>
            <div class="stat-sub">LDC services</div>
            <div style="margin-top:6px;font-size:11px;color:${{yoyColor}}">
                1Y: ${{yoy === '—' ? '—' : sign + yoy + '%'}}
            </div>
        </div>`;
    }}).join('');
}}

function buildStatGrowths() {{
    if (!histData || !histData.services || histData.services.length < 5) return;
    const n = histData.services.length;

    function growth(arr, periods) {{
        if (arr.length < periods + 1) return null;
        const curr = arr[arr.length - 1];
        const prev = arr[arr.length - 1 - periods];
        if (!prev) return null;
        const pct = ((curr - prev) / prev * 100).toFixed(1);
        const sign = pct > 0 ? '+' : '';
        const color = pct > 0 ? 'var(--accent2)' : 'var(--hot)';
        return `<span style="color:${{color}}">${{sign}}${{pct}}%</span>`;
    }}

    function growthLine(arr) {{
        const h = growth(arr, 2);
        const y = growth(arr, 4);
        const t = growth(arr, 8);
        const all = arr.length > 1 ? (() => {{
            const pct = ((arr[arr.length-1] - arr[0]) / arr[0] * 100).toFixed(0);
            const sign = pct > 0 ? '+' : '';
            const color = pct > 0 ? 'var(--accent2)' : 'var(--hot)';
            return `<span style="color:${{color}}">${{sign}}${{pct}}%</span>`;
        }})() : null;
        let parts = [];
        if (h) parts.push('6M: ' + h);
        if (y) parts.push('1Y: ' + y);
        if (t) parts.push('2Y: ' + t);
        if (all) parts.push('All: ' + all);
        return parts.join('&nbsp;&nbsp;');
    }}

    const sEl = document.getElementById('growth-services');
    const pEl = document.getElementById('growth-places');
    const nEl = document.getElementById('growth-nqs');
    const wEl = document.getElementById('growth-wtn');
    const hEl = document.getElementById('growth-hist');

    if (sEl) sEl.innerHTML = growthLine(histData.services);
    if (pEl) pEl.innerHTML = growthLine(histData.places);
    if (nEl) {{
        // For NQS % exceeding
        const excPct = histData.exceeding.map((e, i) => {{
            const total = e + (histData.meeting[i]||0) + (histData.working[i]||0);
            return total ? +(e/total*100).toFixed(1) : 0;
        }});
        nEl.innerHTML = growthLine(excPct);
    }}
    if (wEl) {{
        // Working Towards NQS % trend
        const wtnPct = histData.working.map((w, i) => {{
            const total = w + (histData.meeting[i]||0) + (histData.exceeding[i]||0);
            return total ? +(w/total*100).toFixed(1) : 0;
        }});
        wEl.innerHTML = growthLine(wtnPct);
    }}
    if (hEl) hEl.innerHTML = histData.labels[0] + ' → ' + histData.labels[histData.labels.length-1] + '&nbsp;&nbsp;' + histData.labels.length + ' quarters';
}}

// Chart.js loaded statically in <head> — call initialisers directly
// buildConcentrationChart called after operators.json fetch completes

// ── HOT BUTTONS (from brief) ──
const hotButtons = {json.dumps(brief.get('hot_buttons', []))};
function buildHotButtons() {{
    const el = document.getElementById('hot-buttons');
    if (!hotButtons || hotButtons.length === 0) {{
        el.innerHTML = '<p style="color:var(--muted);font-size:13px;">Weekly signals will appear after the next pipeline run.</p>';
        return;
    }}
    el.innerHTML = hotButtons.map(b => `
        <div class="hot-button">
            <div class="hot-button-label">${{b.type || 'Signal'}}</div>
            <div class="hot-button-text">${{b.text}}</div>
            <div class="hot-button-conf">Confidence: ${{b.confidence || 'observation'}}</div>
        </div>
    `).join('');
}}
buildHotButtons();

// Chart state variables — must be declared before buildTrendCharts() is called
var chartInstances = {{}};
var currentRange = 0;
var compareWindow = 1;
var compareLabel = 'QoQ';

// Initialise charts
buildTrendCharts();
buildStatGrowths();
buildAriaCards();

// ── OPERATOR DATA ──
let allOperators = [];
fetch('operators.json')
    .then(r => r.json())
    .then(data => {{
        allOperators = data;
        renderOpList();
        document.getElementById('op-count').textContent = data.length.toLocaleString() + ' operators';
        buildConcentrationChart();
    }})
    .catch(e => {{
        document.getElementById('op-count').textContent = 'Error loading operators — open locally or check network';
    }});

function titleSearch(state, address, suburb) {{
    const q = encodeURIComponent((address + ' ' + suburb).trim());
    const urls = {{
        NSW: `https://www.nswlrs.com.au/land_titles/property_search?q=${{q}}`,
        VIC: `https://www.landata.vic.gov.au/property-information?address=${{q}}`,
        QLD: `https://www.titlesqld.com.au/title-search?address=${{q}}`,
        SA:  `https://www.sailis.sa.gov.au/home/query?address=${{q}}`,
        WA:  `https://www0.landgate.wa.gov.au/property-search?address=${{q}}`,
        TAS: `https://www.thelist.tas.gov.au/app/content/property?address=${{q}}`,
        ACT: `https://actmapi.act.gov.au/actmapi/index.html?viewer=actmapi&address=${{q}}`,
    }};
    return urls[state] || `https://www.google.com/search?q=${{q}}+title+owner`;
}}

function renderOperator(op, idx) {{
    const tierBadge = `<span class="tier-badge tier-${{op.tier}}">${{op.tier.toUpperCase()}}</span>`;
    const fgcBadge  = op.fgc ? `<span class="fgc-badge">FGC</span>` : '';
    const states    = op.states.join(', ');

    const propcoHtml = op.propco.length > 0 ? `
        <div class="detail-block" style="grid-column:1/-1">
            <div class="detail-block-label">Related Entities (PropCo candidates)</div>
            <div class="propco-list">
                ${{op.propco.map(p => `
                    <div class="propco-item">
                        <span style="flex:1;font-weight:500">${{p.name}}</span>
                        <span style="color:var(--muted);font-family:var(--mono);font-size:11px">ABN: ${{p.abn}}</span>
                        ${{p.is_fgc ? '<span class="fgc-badge">FGC</span>' : ''}}
                    </div>
                `).join('')}}
            </div>
        </div>
    ` : '';

    const centresHtml = op.centres.map(c => {{
        const ts = titleSearch(c.state, '', c.suburb);
        const maps = `https://www.google.com/maps/search/${{encodeURIComponent(c.suburb + ' ' + c.state)}}`;
        const sb = `https://www.google.com/search?q=site:startingblocks.gov.au+${{encodeURIComponent(c.name)}}`;
        const nqsBadge = c.nqs ? `<span style="font-size:10px;color:var(--muted)">${{c.nqs.replace(' NQS','').replace('Working Towards','WTN').replace('Exceeding','EXC').replace('Meeting','MNS')}}</span>` : '';
        const kinderBadge = c.kinder ? `<span style="background:rgba(0,201,167,0.1);color:var(--accent2);padding:1px 6px;border-radius:3px;font-size:10px">KINDER</span>` : '';
        return `
            <div class="centre-card">
                <div class="centre-name">${{c.name}}</div>
                <div class="centre-meta">${{c.suburb}}, ${{c.state}} ${{c.postcode}} &bull; ${{c.places}} places ${{nqsBadge}} ${{kinderBadge}}</div>
                <div class="centre-links">
                    <a href="${{ts}}" target="_blank" class="centre-link">Title Search</a>
                    <a href="${{maps}}" target="_blank" class="centre-link">Maps</a>
                    <a href="${{sb}}" target="_blank" class="centre-link">StartingBlocks</a>
                </div>
            </div>
        `;
    }}).join('');

    return `
        <div class="op-row" id="op-row-${{idx}}" onclick="toggleOperator(${{idx}})">
            <div class="op-row-name">${{op.legal_name}} ${{fgcBadge}}</div>
            <div class="op-row-meta">
                ${{tierBadge}}
                <span>${{op.n_centres}} centres</span>
                <span>${{states}}</span>
                <span style="font-family:var(--mono);font-size:11px">Score: ${{op.score}}</span>
            </div>
        </div>
        <div class="op-detail" id="op-detail-${{idx}}">
            <div class="detail-grid">
                <div class="detail-block">
                    <div class="detail-block-label">ABN</div>
                    <div class="detail-block-value" style="font-family:var(--mono)">${{op.abn || '—'}}</div>
                </div>
                <div class="detail-block">
                    <div class="detail-block-label">ACN</div>
                    <div class="detail-block-value" style="font-family:var(--mono)">${{op.acn || '—'}}</div>
                </div>
                <div class="detail-block">
                    <div class="detail-block-label">Entity Type</div>
                    <div class="detail-block-value">${{op.entity_type || '—'}}</div>
                </div>
                <div class="detail-block">
                    <div class="detail-block-label">Reg. State</div>
                    <div class="detail-block-value">${{op.reg_state || '—'}}</div>
                </div>
                ${{propcoHtml}}
            </div>
            <div class="section-title" style="margin-top:8px">Centres (${{op.centres.length}})</div>
            <div class="centres-grid">${{centresHtml}}</div>
        </div>
    `;
}}

let expandedIdx = null;
function toggleOperator(idx) {{
    const detail = document.getElementById('op-detail-' + idx);
    const row    = document.getElementById('op-row-' + idx);
    if (expandedIdx !== null && expandedIdx !== idx) {{
        document.getElementById('op-detail-' + expandedIdx).classList.remove('visible');
        document.getElementById('op-row-' + expandedIdx).classList.remove('expanded');
    }}
    detail.classList.toggle('visible');
    row.classList.toggle('expanded');
    expandedIdx = detail.classList.contains('visible') ? idx : null;
}}

let filteredOps = [...allOperators];

function filterOperators() {{
    const q     = document.getElementById('op-search').value.toLowerCase();
    const tier  = document.getElementById('op-tier').value;
    const state = document.getElementById('op-state').value;
    const fgc   = document.getElementById('op-fgc').value;

    filteredOps = allOperators.filter(op => {{
        if (tier  && op.tier !== tier) return false;
        if (state && !op.states.includes(state)) return false;
        if (fgc   && !op.fgc) return false;
        if (q) {{
            const searchStr = [
                op.legal_name,
                op.abn,
                op.acn,
                ...op.states,
                ...op.propco.map(p => p.name),
                ...op.centres.map(c => c.suburb),
            ].join(' ').toLowerCase();
            if (!searchStr.includes(q)) return false;
        }}
        return true;
    }});

    renderOpList();
}}

function renderOpList() {{
    const list = document.getElementById('op-list');
    const count = document.getElementById('op-count');
    count.textContent = filteredOps.length.toLocaleString() + ' operators';
    expandedIdx = null;

    if (filteredOps.length === 0) {{
        list.innerHTML = '<p style="color:var(--muted);padding:20px">No operators match your search.</p>';
        return;
    }}

    // Render first 100 for performance
    const toRender = filteredOps.slice(0, 100);
    list.innerHTML = toRender.map((op, i) => renderOperator(op, i)).join('');

    if (filteredOps.length > 100) {{
        list.innerHTML += `<div style="text-align:center;padding:20px;color:var(--muted);font-size:12px">
            Showing 100 of ${{filteredOps.length}} — refine your search to see more
        </div>`;
    }}
}}

// Initial render
renderOpList();

// Top 20 click-through to Operator Intelligence
function jumpToOperator(name) {{
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.getElementById('panel-operators').classList.add('active');
    document.querySelectorAll('.tab')[1].classList.add('active');
    document.getElementById('op-search').value = name;
    filterOperators();
    window.scrollTo(0, 0);
}}

// CHART.JS TREND CHARTS

function getSlicedData(arr, n) {{
    if (!n || n === 0) return arr;
    return arr.slice(-n);
}}

function setCompare(n, label, el) {{
    compareWindow = n;
    compareLabel = label;
    document.querySelectorAll('#compare-btns .range-btn').forEach(b => b.classList.remove('active'));
    if (el) el.classList.add('active');
    Object.values(chartInstances).forEach(c => c.destroy());
    chartInstances = {{}};
    buildTrendCharts();
}}

function setRange(n, el) {{
    currentRange = n;
    document.querySelectorAll('#time-range-btns .range-btn').forEach(b => b.classList.remove('active'));
    if (el) el.classList.add('active');
    Object.values(chartInstances).forEach(c => c.destroy());
    chartInstances = {{}};
    buildTrendCharts();
}}

function buildGrowthStat(elId, data, suffix) {{
    if (!data || data.length < 2) return;
    const first = data[0], last = data[data.length-1];
    const pct = ((last - first) / first * 100).toFixed(1);
    const sign = pct > 0 ? '+' : '';
    const el = document.getElementById(elId);
    if (el) el.textContent = last.toLocaleString() + suffix + '  (' + sign + pct + '% over period)';
}}

function buildTrendCharts() {{
    if (!histData || !histData.labels || histData.labels.length === 0) return;

    const n = currentRange;
    const rawLabels = getSlicedData(histData.labels, n);
    const labels = rawLabels.map((l, i) => i % 4 === 0 ? l : '');

    // Key sector events for annotation
    const sectorEvents = [
        {{ quarter: 'Q3 2013', label: 'NQF Launch', color: 'rgba(61,126,255,0.6)' }},
        {{ quarter: 'Q1 2018', label: 'NQS Reform', color: 'rgba(61,126,255,0.6)' }},
        {{ quarter: 'Q2 2020', label: 'COVID', color: 'rgba(224,92,58,0.7)' }},
        {{ quarter: 'Q3 2022', label: 'CCS Reform', color: 'rgba(0,201,167,0.6)' }},
        {{ quarter: 'Q3 2023', label: 'Wage +15%', color: 'rgba(155,89,182,0.7)' }},
        {{ quarter: 'Q1 2026', label: '3-Day Guar.', color: 'rgba(0,201,167,0.6)' }},
    ];

    function getEventIndices(labels) {{
        return sectorEvents.map(ev => {{
            const idx = labels.indexOf(ev.quarter);
            return idx >= 0 ? {{ idx, label: ev.label, color: ev.color }} : null;
        }}).filter(Boolean);
    }}

    const chartOpts = {{
        responsive: true,
        maintainAspectRatio: true,
        interaction: {{ mode: 'index', intersect: false }},
        hover: {{ mode: 'index', intersect: false }},
        plugins: {{
            legend: {{ labels: {{ color: '#8890a8', font: {{ size: 10 }}, boxWidth: 12 }} }},
            tooltip: {{
                backgroundColor: 'rgba(24,28,38,0.95)',
                borderColor: '#2a2f3f',
                borderWidth: 1,
                titleColor: '#e8eaf0',
                bodyColor: '#8890a8',
                padding: 10,
                callbacks: {{
                    title: function(items) {{
                        return items[0].label || '';
                    }},
                    label: function(ctx) {{
                        const v = ctx.raw;
                        const arr = ctx.dataset.data;
                        const i = ctx.dataIndex;
                        let s = '  ' + ctx.dataset.label + ': ' + v.toLocaleString();
                        if (i >= compareWindow && arr[i - compareWindow] != null) {{
                            const prev = arr[i - compareWindow];
                            const chg = ((v - prev) / prev * 100).toFixed(1);
                            s += '  (' + (chg > 0 ? '+' : '') + chg + '% ' + compareLabel + ')';
                        }}
                        return s;
                    }},
                    afterBody: function(items) {{
                        const label = items[0].label;
                        const ev = sectorEvents.find(e => e.quarter === label);
                        return ev ? ['', '  ★ ' + ev.label] : [];
                    }}
                }}
            }}
        }},
        scales: {{
            x: {{ ticks: {{ color: '#8890a8', font: {{ size: 9 }}, maxRotation: 45 }}, grid: {{ color: '#2a2f3f' }} }},
            y: {{ ticks: {{ color: '#8890a8', font: {{ size: 9 }} }}, grid: {{ color: '#2a2f3f' }} }}
        }}
    }};

    // Event annotation plugin (vertical lines + visible labels)
    const eventAnnotationPlugin = {{
        id: 'eventLines',
        afterDraw(chart) {{
            const ctx2 = chart.ctx;
            const xAxis = chart.scales.x;
            const yAxis = chart.scales.y;
            if (!xAxis || !yAxis) return;

            const slicedLabels = getSlicedData(histData.labels, currentRange);

            sectorEvents.forEach((ev, evIdx) => {{
                const idx = slicedLabels.indexOf(ev.quarter);
                if (idx < 0) return;

                const xPixel = xAxis.getPixelForValue(idx);
                if (!xPixel || xPixel < xAxis.left || xPixel > xAxis.right) return;

                ctx2.save();

                // Dashed vertical line - more visible
                ctx2.strokeStyle = ev.color;
                ctx2.lineWidth = 2;
                ctx2.setLineDash([5, 4]);
                ctx2.globalAlpha = 0.8;
                ctx2.beginPath();
                ctx2.moveTo(xPixel, yAxis.top + 28);
                ctx2.lineTo(xPixel, yAxis.bottom);
                ctx2.stroke();
                ctx2.setLineDash([]);
                ctx2.globalAlpha = 1;

                // Label box - stagger vertically to avoid overlap
                const label = ev.label;
                ctx2.font = 'bold 10px sans-serif';
                const tw = ctx2.measureText(label).width;
                const pad = 5;
                const bw = tw + pad * 2;
                const bh = 18;
                const bx = xPixel - bw / 2;
                // Stagger: alternate between top positions
                const by = yAxis.top + (evIdx % 2 === 0 ? 2 : 22);

                // Shadow for readability
                ctx2.shadowColor = 'rgba(0,0,0,0.8)';
                ctx2.shadowBlur = 4;

                // Solid background
                ctx2.fillStyle = 'rgba(15,17,23,0.95)';
                ctx2.fillRect(bx, by, bw, bh);

                ctx2.shadowBlur = 0;

                // Colored border
                ctx2.strokeStyle = ev.color;
                ctx2.lineWidth = 1.5;
                ctx2.strokeRect(bx, by, bw, bh);

                // Text
                ctx2.fillStyle = '#ffffff';
                ctx2.textAlign = 'center';
                ctx2.textBaseline = 'middle';
                ctx2.fillText(label, xPixel, by + bh / 2);

                ctx2.restore();
            }});
        }}
    }};

    // COVID + event annotations
    const events = [
        {{ quarter: 'Q1 2020', label: 'COVID', color: 'rgba(224,92,58,0.3)' }},
        {{ quarter: 'Q1 2018', label: 'NQS reform', color: 'rgba(61,126,255,0.2)' }},
        {{ quarter: 'Q1 2026', label: '3-Day Guarantee', color: 'rgba(0,201,167,0.2)' }},
    ];

    function makeDataset(label, data, color, fill) {{
        return {{ label, data: getSlicedData(data, n), borderColor: color,
                  backgroundColor: fill || 'transparent',
                  fill: !!fill, tension: 0.3, pointRadius: 0, borderWidth: 2 }};
    }}

    // Resolve active data series based on state/ARIA filter
    const activeState = currentStateFilter ? currentStateFilter.toLowerCase() : '';
    const activeAria  = currentAriaFilter;
    const ariaSeriesKey = activeAria ? ARIA_SERIES[activeAria] : null;

    // Primary services series — state → state series, ARIA → ARIA series, else national
    let primaryServices = histData.services;
    let primaryLabel    = 'LDC Services (National)';
    let primaryColor    = '#3d7eff';
    if (activeState && histData[activeState]) {{
        primaryServices = histData[activeState];
        primaryLabel    = 'LDC Services (' + currentStateFilter + ')';
    }} else if (ariaSeriesKey && histData[ariaSeriesKey]) {{
        primaryServices = histData[ariaSeriesKey];
        primaryLabel    = 'LDC Services (' + (ARIA_KEYS[activeAria] || activeAria) + ')';
        primaryColor    = '#00c9a7';
    }}

    // 1. Services — uses filtered primary series
    buildGrowthStat('stat-services-growth', getSlicedData(primaryServices, n), ' services');
    chartInstances['services'] = new Chart(document.getElementById('chart-services'), {{
        type: 'line', options: chartOpts,
        plugins: [eventAnnotationPlugin],
        data: {{ labels, datasets: [makeDataset(primaryLabel, primaryServices, primaryColor, 'rgba(61,126,255,0.1)')] }}
    }});

    // 2. Places — national only (no per-state places history available)
    buildGrowthStat('stat-places-growth', getSlicedData(histData.places, n), ' places');
    chartInstances['places'] = new Chart(document.getElementById('chart-places'), {{
        type: 'line', options: chartOpts,
        plugins: [eventAnnotationPlugin],
        data: {{ labels, datasets: [makeDataset('Licensed Places', histData.places, '#00c9a7', 'rgba(0,201,167,0.08)')] }}
    }});

    // 3. NQS quality & stress as % of total rated
    const nqsPctOpts = JSON.parse(JSON.stringify(chartOpts));
    nqsPctOpts.scales.y.ticks = {{ ...nqsPctOpts.scales.y.ticks, callback: v => v + '%' }};
    const excPctData = histData.exceeding.map((e, i) => {{
        const total = e + (histData.meeting[i]||0) + (histData.working[i]||0);
        return total ? +(e/total*100).toFixed(1) : null;
    }});
    const wtnPctData = histData.working.map((w, i) => {{
        const total = (histData.exceeding[i]||0) + (histData.meeting[i]||0) + w;
        return total ? +(w/total*100).toFixed(1) : null;
    }});
    chartInstances['nqs'] = new Chart(document.getElementById('chart-nqs'), {{
        type: 'line', options: nqsPctOpts,
        plugins: [eventAnnotationPlugin],
        data: {{ labels, datasets: [
            makeDataset('Exceeding NQS %', excPctData, '#00c9a7'),
            makeDataset('Working Towards %', wtnPctData, '#d4890a'),
        ] }}
    }});

    // 4. State growth — highlight selected state if filtered
    const stateColors = {{ nsw:'#3d7eff', vic:'#00c9a7', qld:'#d4890a', wa:'#e05c3a', sa:'#9b59b6' }};
    function stateDataset(label, key, color) {{
        const dimmed = activeState && activeState !== key;
        return {{ label, data: getSlicedData(histData[key], n), borderColor: dimmed ? color + '33' : color,
                  backgroundColor: 'transparent', fill: false, tension: 0.3,
                  pointRadius: 0, borderWidth: dimmed ? 1 : (activeState === key ? 3 : 2) }};
    }}
    chartInstances['states'] = new Chart(document.getElementById('chart-states'), {{
        type: 'line', options: chartOpts,
        plugins: [eventAnnotationPlugin],
        data: {{ labels, datasets: [
            stateDataset('NSW', 'nsw', '#3d7eff'),
            stateDataset('VIC', 'vic', '#00c9a7'),
            stateDataset('QLD', 'qld', '#d4890a'),
            stateDataset('WA',  'wa',  '#e05c3a'),
            stateDataset('SA',  'sa',  '#9b59b6'),
        ] }}
    }});

    // 5. For-profit % share
    const fpPct = histData.forprofit.map((fp, i) => {{
        const total = fp + (histData.nfp[i] || 0);
        return total ? +(fp / total * 100).toFixed(1) : 0;
    }});
    const fpPctSliced = getSlicedData(fpPct, n);
    const fpLast = fpPctSliced[fpPctSliced.length-1];
    const fpFirst = fpPctSliced[0];
    const fpEl = document.getElementById('stat-fp-growth');
    if (fpEl && fpLast) fpEl.textContent = fpLast + '% for-profit  (' + (fpLast - fpFirst).toFixed(1) + 'pp change over period)';

    const fpOpts = JSON.parse(JSON.stringify(chartOpts));
    fpOpts.scales.y.ticks.callback = v => v + '%';
    chartInstances['fp-pct'] = new Chart(document.getElementById('chart-fp-pct'), {{
        type: 'line', options: fpOpts,
        data: {{ labels, datasets: [makeDataset('For-Profit %', fpPct, '#3d7eff', 'rgba(61,126,255,0.08)')] }}
    }});

    // 6. Supply/Demand ratio — licensed places per 100 children under 5
    // Trim to first non-null index so empty pre-2019 period doesn't dominate the x-axis
    const sdAllData = histData.supply_demand;
    const sdStartIdx = sdAllData.findIndex(v => v !== null);
    const sdLabels = sdStartIdx >= 0 ? labels.slice(sdStartIdx) : labels;
    const sdSliced = sdStartIdx >= 0 ? sdAllData.slice(sdStartIdx) : sdAllData;
    const sdLast = sdSliced.filter(v => v !== null).slice(-1)[0];
    const sdFirst = sdSliced.filter(v => v !== null)[0];
    const sdEl = document.getElementById('stat-supply-demand');
    if (sdEl && sdLast != null) {{
        const sdChange = sdFirst != null ? ' (+' + (sdLast - sdFirst).toFixed(1) + ' over period)' : '';
        sdEl.textContent = sdLast.toFixed(1) + ' places per 100 children under 5' + sdChange;
    }}
    const sdOpts = JSON.parse(JSON.stringify(chartOpts));
    chartInstances['supply-demand'] = new Chart(document.getElementById('chart-supply-demand'), {{
        type: 'line', options: sdOpts,
        plugins: [eventAnnotationPlugin],
        data: {{ labels: sdLabels, datasets: [makeDataset('Places per 100 Under-5', sdSliced, '#9b59b6', 'rgba(155,89,182,0.08)')] }}
    }});

    // 7. New approvals per quarter — shown as 4-quarter rolling sum to smooth lumpiness
    // Trim to first non-null index so empty gap period doesn't dominate the x-axis
    const apprAllRaw = histData.new_approvals;
    const apprStartIdx = apprAllRaw.findIndex(v => v !== null);
    const apprLabels = apprStartIdx >= 0 ? labels.slice(apprStartIdx) : labels;
    const apprRawSliced = apprStartIdx >= 0 ? apprAllRaw.slice(apprStartIdx) : apprAllRaw;
    const rolling4 = apprRawSliced.map((v, i, arr) => {{
        const win = arr.slice(Math.max(0, i - 3), i + 1).filter(x => x !== null);
        return win.length === 4 ? win.reduce((a, b) => a + b, 0) : null;
    }});
    const apprLast = rolling4.filter(v => v !== null).slice(-1)[0];
    const apprEl = document.getElementById('stat-new-approvals');
    if (apprEl && apprLast != null) {{
        apprEl.textContent = apprLast + ' new approvals (trailing 4-quarter sum)';
    }}
    const apprOpts = JSON.parse(JSON.stringify(chartOpts));
    chartInstances['new-approvals'] = new Chart(document.getElementById('chart-new-approvals'), {{
        type: 'line', options: apprOpts,
        plugins: [eventAnnotationPlugin],
        data: {{ labels: apprLabels, datasets: [
            makeDataset('Rolling 4-Qtr Approvals', rolling4, '#e05c3a', 'rgba(224,92,58,0.08)'),
            {{ label: 'Quarterly Approvals', data: apprRawSliced, borderColor: 'rgba(224,92,58,0.3)',
               backgroundColor: 'transparent', fill: false, tension: 0.3, pointRadius: 0,
               borderWidth: 1, borderDash: [4, 3] }},
        ] }}
    }});
}}

function buildConcentrationChart() {{
    if (!allOperators || allOperators.length === 0) return;
    const el = document.getElementById('chart-concentration');
    if (!el) return;

    // Get top 10 by total_places (or n_centres * 80 as proxy)
    const sorted = [...allOperators]
        .filter(o => o.n_centres > 0)
        .sort((a, b) => (b.total_places || b.n_centres * 80) - (a.total_places || a.n_centres * 80))
        .slice(0, 10);

    const totalPlaces = {stats['total_places']};
    const maxVal = sorted[0] ? (sorted[0].total_places || sorted[0].n_centres * 80) : 1;

    el.innerHTML = sorted.map(op => {{
        const places = op.total_places || op.n_centres * 80;
        const pct = totalPlaces ? (places / totalPlaces * 100).toFixed(1) : 0;
        const barPct = Math.round(places / maxVal * 100);
        const name = op.legal_name.length > 30 ? op.legal_name.slice(0,28) + '…' : op.legal_name;
        return `
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:7px">
            <div style="width:160px;font-size:11px;color:var(--muted);flex-shrink:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${{name}}</div>
            <div style="flex:1;height:8px;background:var(--surface2);border-radius:4px;overflow:hidden">
                <div style="width:${{barPct}}%;height:100%;background:linear-gradient(90deg,var(--accent),var(--accent2));border-radius:4px"></div>
            </div>
            <div style="font-family:var(--mono);font-size:10px;color:var(--muted);width:44px;text-align:right">${{pct}}%</div>
        </div>`;
    }}).join('');
}}

// Catchment placeholder
function filterCatchments() {{
    const q = document.getElementById('catch-search').value;
    document.getElementById('catchment-results').innerHTML =
        q.length > 1
        ? '<p style="color:var(--muted);padding:20px 0">Catchment Explorer will be fully interactive in the next release. Use the Operator Intelligence panel to find centres in a specific suburb.</p>'
        : '<p style="color:var(--muted);padding:20px 0">Enter a suburb or postcode to explore catchment intelligence.</p>';
}}
</script>
</body>
</html>"""

    # Write to docs/index.html
    output = DOCS_DIR / "index.html"
    output.write_text(html, encoding="utf-8")
    print(f"Dashboard written: {output}")
    print(f"  Services: {stats['total_services']:,}")
    print(f"  Operators in Panel 2: {len(op_cards):,}")
    print(f"  Approvals shown: {len(approvals)}")
    print(f"\nPush to GitHub Pages:")
    print(f"  git add docs/ && git commit -m 'Dashboard {today}' && git push origin master:main")


if __name__ == "__main__":
    generate()
