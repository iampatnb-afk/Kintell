"""
generate_prospecting_page.py — Build HTML prospecting page from target list.
Reads operators_hot_targets.json and generates operators_prospecting.html.

Run after module2c_targeting.py:
  python generate_prospecting_page.py

The daily email digest links to this file.
"""

import json
from pathlib import Path
from datetime import date

INPUT  = Path("operators_hot_targets.json")
OUTPUT = Path("data/operators_prospecting.html")


def nqs_color(summary: dict) -> str:
    if summary.get("sig_improvement", 0) > 0:
        return "#c0392b"
    if summary.get("working_towards", 0) > summary.get("meeting", 0):
        return "#e67e22"
    if summary.get("exceeding", 0) > 0:
        return "#27ae60"
    return "#2980b9"


def score_bar(score: int) -> str:
    pct = min(score, 100)
    color = "#27ae60" if pct >= 80 else ("#f39c12" if pct >= 60 else "#e67e22")
    return f"""<div style="background:#eee;border-radius:3px;height:8px;width:80px;display:inline-block;vertical-align:middle">
        <div style="background:{color};height:8px;border-radius:3px;width:{pct}%"></div>
    </div> <span style="font-size:11px;color:#555">{score}</span>"""


def build_page(operators: list) -> str:
    today = str(date.today())

    # Build operator rows
    rows = []
    for i, op in enumerate(operators):
        tier       = op.get("priority_tier", "")
        score      = op.get("score", 0)
        name       = op.get("legal_name", "")
        n_centres  = op.get("n_centres", 0)
        states     = ", ".join(op.get("states", []))
        total_pl   = op.get("total_places", 0)
        has_kinder = op.get("has_kinder", False)
        nfp        = op.get("is_nfp", False)
        review     = bool(op.get("fuzzy_related") or op.get("phone_related"))
        nqs        = op.get("nqs_summary", {})
        product    = op.get("product_fit", "")
        growing    = op.get("recent_centre_added", False)
        centres    = op.get("centres", [])
        conf       = op.get("group_confidence", "confirmed")

        tier_color = {"hot": "#D85A30", "warm": "#E8A020"}.get(tier, "#888")
        tier_label = tier.upper()

        # Build centre sub-rows (hidden by default)
        centre_rows = ""
        for c in centres:
            kinder_badge = "<span style='background:#1abc9c;color:white;padding:1px 4px;border-radius:2px;font-size:10px'>K</span>" if c.get("has_kinder") else ""
            nfp_badge    = "<span style='background:#8e44ad;color:white;padding:1px 4px;border-radius:2px;font-size:10px'>NFP</span>" if c.get("is_nfp") else ""
            phone        = str(c.get("phone","")).replace(".0","").strip()
            phone_html   = f"<a href='tel:{phone}' style='color:#2980b9'>{phone}</a>" if phone and phone not in ("nan","") else ""
            sb_q         = f"site:startingblocks.gov.au \"{c.get('service_name','')}\" {c.get('suburb','')}"
            import urllib.parse
            sb_link      = f"https://www.google.com/search?{urllib.parse.urlencode({'q': sb_q})}"
            g_q          = f"{c.get('service_name','')} {c.get('suburb','')} childcare"
            g_link       = f"https://www.google.com/search?{urllib.parse.urlencode({'q': g_q})}"

            centre_rows += f"""
            <tr style="background:#fafafa;font-size:11px">
                <td style="padding:4px 8px 4px 32px">
                    <a href="{sb_link}" target="_blank" style="color:#2c3e50;text-decoration:none">{c.get('service_name','')}</a>
                    <a href="{g_link}" target="_blank" style="color:#aaa;font-size:10px;margin-left:4px">&#127760;</a>
                    {kinder_badge} {nfp_badge}
                </td>
                <td style="padding:4px 8px;color:#666">{c.get('suburb','')}, {c.get('state','')}</td>
                <td style="padding:4px 8px;text-align:center">{c.get('places',0)}</td>
                <td style="padding:4px 8px">{c.get('nqs_rating','')}</td>
                <td style="padding:4px 8px">{phone_html}</td>
                <td style="padding:4px 8px;color:#999;font-size:10px">{c.get('approval_date','')}</td>
            </tr>"""

        # Review flags
        review_html = ""
        if review:
            fuzzy = op.get("fuzzy_related", [])
            phone_rel = op.get("phone_related", [])
            if fuzzy or phone_rel:
                review_html = "<div style='margin-top:4px;font-size:11px;color:#e67e22'>&#9888; Review: possible related groups — "
                parts = [f"{f['name'][:30]} ({f['score']:.0f}%)" for f in fuzzy[:2]]
                parts += [f"{p['name'][:30]} (phone)" for p in phone_rel[:1]]
                review_html += " | ".join(parts) + "</div>"

        kinder_html = "<span style='background:#1abc9c;color:white;padding:1px 5px;border-radius:3px;font-size:10px;margin-left:4px'>Kinder</span>" if has_kinder else ""
        growing_html = "<span style='background:#27ae60;color:white;padding:1px 5px;border-radius:3px;font-size:10px;margin-left:4px'>Growing</span>" if growing else ""
        conf_html = "" if conf == "confirmed" else f"<span style='background:#f39c12;color:white;padding:1px 4px;border-radius:3px;font-size:10px;margin-left:4px'>{conf}</span>"

        rows.append(f"""
        <tr class="op-row" 
            data-score="{score}" 
            data-tier="{tier}"
            data-states="{states.lower()}"
            data-centres="{n_centres}"
            data-kinder="{'1' if has_kinder else '0'}"
            data-review="{'1' if review else '0'}"
            onclick="toggleCentres({i})"
            style="cursor:pointer;border-bottom:1px solid #eee">
            <td style="padding:8px;font-size:12px">
                <span style="background:{tier_color};color:white;padding:2px 7px;border-radius:3px;font-size:11px;font-weight:bold">{tier_label}</span>
            </td>
            <td style="padding:8px;font-size:13px;font-weight:500">
                {name}
                {kinder_html}{growing_html}{conf_html}
                {review_html}
            </td>
            <td style="padding:8px;text-align:center;font-size:12px">{n_centres}</td>
            <td style="padding:8px;text-align:center;font-size:12px">{total_pl:,}</td>
            <td style="padding:8px;font-size:12px">{states}</td>
            <td style="padding:8px">{score_bar(score)}</td>
            <td style="padding:8px;font-size:11px;color:#666">{product[:35]}</td>
        </tr>
        <tr id="centres-{i}" style="display:none">
            <td colspan="7" style="padding:0 8px 8px 8px">
                <table style="width:100%;border-collapse:collapse;border:1px solid #e8e8e8;border-radius:4px">
                    <thead>
                        <tr style="background:#f5f5f5;font-size:11px">
                            <th style="padding:4px 8px;text-align:left">Centre</th>
                            <th style="padding:4px 8px;text-align:left">Location</th>
                            <th style="padding:4px 8px;text-align:center">Places</th>
                            <th style="padding:4px 8px;text-align:left">NQS</th>
                            <th style="padding:4px 8px;text-align:left">Phone</th>
                            <th style="padding:4px 8px;text-align:left">Approved</th>
                        </tr>
                    </thead>
                    <tbody>{centre_rows}</tbody>
                </table>
            </td>
        </tr>""")

    rows_html = "\n".join(rows)
    n_hot  = sum(1 for o in operators if o.get("priority_tier") == "hot")
    n_warm = sum(1 for o in operators if o.get("priority_tier") == "warm")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Remara Prospecting List — {today}</title>
<style>
    body {{ font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; color: #2c3e50; }}
    h1 {{ color: #2c3e50; margin-bottom: 4px; }}
    .summary {{ background: #2c3e50; color: white; padding: 12px 20px; border-radius: 8px; margin-bottom: 20px; display: flex; gap: 24px; align-items: center; }}
    .summary span {{ font-size: 14px; }}
    .summary b {{ font-size: 18px; }}
    .filters {{ background: #f8f9fa; padding: 12px 16px; border-radius: 6px; margin-bottom: 16px; display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }}
    .filters select, .filters input {{ padding: 6px 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 13px; }}
    .filters button {{ padding: 6px 14px; background: #2c3e50; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 13px; }}
    .filters button:hover {{ background: #34495e; }}
    table {{ width: 100%; border-collapse: collapse; }}
    thead tr {{ background: #ecf0f1; }}
    th {{ padding: 10px 8px; text-align: left; font-size: 12px; color: #555; font-weight: 600; cursor: pointer; user-select: none; }}
    th:hover {{ background: #dde; }}
    .op-row:hover {{ background: #f0f4ff !important; }}
    .op-row td:first-child {{ width: 60px; }}
    #count {{ font-size: 13px; color: #666; margin-bottom: 8px; }}
    .export-btn {{ float: right; padding: 6px 14px; background: #27ae60; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 13px; }}
</style>
</head>
<body>

<h1>Remara Prospecting List</h1>
<div class="summary">
    <span>Generated: <b>{today}</b></span>
    <span>Hot: <b style="color:#ff8c69">{n_hot}</b></span>
    <span>Warm: <b style="color:#ffd27f">{n_warm}</b></span>
    <span>Total: <b>{len(operators)}</b></span>
</div>

<div class="filters">
    <label style="font-size:13px;font-weight:bold">Filter:</label>
    <select id="filterTier" onchange="applyFilters()">
        <option value="">All tiers</option>
        <option value="hot">Hot only</option>
        <option value="warm">Warm only</option>
    </select>
    <select id="filterState" onchange="applyFilters()">
        <option value="">All states</option>
        <option value="nsw">NSW</option>
        <option value="vic">VIC</option>
        <option value="qld">QLD</option>
        <option value="wa">WA</option>
        <option value="sa">SA</option>
        <option value="act">ACT</option>
        <option value="tas">TAS</option>
        <option value="nt">NT</option>
    </select>
    <select id="filterScore" onchange="applyFilters()">
        <option value="0">Any score</option>
        <option value="90">90+ only</option>
        <option value="80">80+ only</option>
        <option value="70">70+ only</option>
        <option value="60">60+ only</option>
    </select>
    <select id="filterCentres" onchange="applyFilters()">
        <option value="0">Any centre count</option>
        <option value="5">5+ centres</option>
        <option value="7">7+ centres</option>
        <option value="10">10+ centres</option>
    </select>
    <label style="font-size:13px"><input type="checkbox" id="filterKinder" onchange="applyFilters()"> Kinder approved</label>
    <label style="font-size:13px"><input type="checkbox" id="filterReview" onchange="applyFilters()"> Review required only</label>
    <button onclick="resetFilters()">Reset</button>
    <button class="export-btn" onclick="exportCSV()">Export CSV</button>
</div>

<div id="count"></div>

<table id="mainTable">
    <thead>
        <tr>
            <th onclick="sortTable(0)">Tier</th>
            <th onclick="sortTable(1)">Operator</th>
            <th onclick="sortTable(2)">Centres</th>
            <th onclick="sortTable(3)">Places</th>
            <th onclick="sortTable(4)">States</th>
            <th onclick="sortTable(5)">Score</th>
            <th>Product Fit</th>
        </tr>
    </thead>
    <tbody id="tableBody">
        {rows_html}
    </tbody>
</table>

<script>
function toggleCentres(i) {{
    var el = document.getElementById('centres-' + i);
    el.style.display = el.style.display === 'none' ? 'table-row' : 'none';
}}

function applyFilters() {{
    var tier    = document.getElementById('filterTier').value;
    var state   = document.getElementById('filterState').value;
    var score   = parseInt(document.getElementById('filterScore').value) || 0;
    var centres = parseInt(document.getElementById('filterCentres').value) || 0;
    var kinder  = document.getElementById('filterKinder').checked;
    var review  = document.getElementById('filterReview').checked;
    
    var rows = document.querySelectorAll('.op-row');
    var visible = 0;
    rows.forEach(function(row) {{
        var rowTier    = row.dataset.tier;
        var rowStates  = row.dataset.states;
        var rowScore   = parseInt(row.dataset.score);
        var rowCentres = parseInt(row.dataset.centres);
        var rowKinder  = row.dataset.kinder === '1';
        var rowReview  = row.dataset.review === '1';
        
        var show = true;
        if (tier   && rowTier !== tier)           show = false;
        if (state  && !rowStates.includes(state)) show = false;
        if (score  && rowScore < score)           show = false;
        if (centres && rowCentres < centres)      show = false;
        if (kinder && !rowKinder)                 show = false;
        if (review && !rowReview)                 show = false;
        
        row.style.display = show ? '' : 'none';
        // Hide centre sub-row too
        var centreRow = row.nextElementSibling;
        if (centreRow) centreRow.style.display = 'none';
        if (show) visible++;
    }});
    document.getElementById('count').textContent = visible + ' operators shown';
}}

function resetFilters() {{
    document.getElementById('filterTier').value = '';
    document.getElementById('filterState').value = '';
    document.getElementById('filterScore').value = '0';
    document.getElementById('filterCentres').value = '0';
    document.getElementById('filterKinder').checked = false;
    document.getElementById('filterReview').checked = false;
    applyFilters();
}}

function sortTable(col) {{
    var tbody = document.getElementById('tableBody');
    var rows  = Array.from(tbody.querySelectorAll('.op-row'));
    var asc   = tbody.dataset.sortCol == col && tbody.dataset.sortDir == 'asc';
    tbody.dataset.sortCol = col;
    tbody.dataset.sortDir = asc ? 'desc' : 'asc';
    
    rows.sort(function(a, b) {{
        var va = a.cells[col].textContent.trim();
        var vb = b.cells[col].textContent.trim();
        var na = parseFloat(va), nb = parseFloat(vb);
        if (!isNaN(na) && !isNaN(nb)) return asc ? nb - na : na - nb;
        return asc ? vb.localeCompare(va) : va.localeCompare(vb);
    }});
    
    rows.forEach(function(row) {{
        tbody.appendChild(row);
        var next = row.nextElementSibling;
        if (next && !next.classList.contains('op-row')) tbody.appendChild(next);
    }});
}}

function exportCSV() {{
    var rows = document.querySelectorAll('.op-row:not([style*="display: none"])');
    var csv  = 'Tier,Operator,Centres,Places,States,Score,Product Fit\\n';
    rows.forEach(function(row) {{
        var cells = row.cells;
        csv += [
            cells[0].textContent.trim(),
            '"' + cells[1].textContent.trim().replace(/\\n/g,' ').replace(/"/g,"'") + '"',
            cells[2].textContent.trim(),
            cells[3].textContent.trim(),
            cells[4].textContent.trim(),
            cells[5].textContent.trim(),
            '"' + cells[6].textContent.trim() + '"'
        ].join(',') + '\\n';
    }});
    var blob = new Blob([csv], {{type: 'text/csv'}});
    var a    = document.createElement('a');
    a.href   = URL.createObjectURL(blob);
    a.download = 'remara_targets_{today}.csv';
    a.click();
}}

// Init count
applyFilters();
</script>
</body>
</html>"""


def run():
    if not INPUT.exists():
        print(f"ERROR: {INPUT} not found — run module2c_targeting.py first")
        return

    operators = json.load(open(INPUT, encoding="utf-8"))
    print(f"Building prospecting page for {len(operators)} operators...")

    html = build_page(operators)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Saved: {OUTPUT}")
    print(f"Open in browser: start {OUTPUT}")


if __name__ == "__main__":
    run()
