"""
catchment_html.py — HTML renderer for catchment data in email digest.
Import from module5_digest.py:
    from catchment_html import render_catchment_block
"""
import urllib.parse


def _sb_url(service_name: str, suburb: str, state: str) -> str:
    """Google search scoped to startingblocks.gov.au for the exact centre."""
    query = f'site:startingblocks.gov.au "{service_name}" {suburb}'
    params = urllib.parse.urlencode({"q": query})
    return f"https://www.google.com/search?{params}"


def _google_url(operator_name: str, suburb: str) -> str:
    """Google search URL for operator website."""
    query = f"{operator_name} {suburb} childcare"
    params = urllib.parse.urlencode({"q": query})
    return f"https://www.google.com/search?{params}"


def _clean(val) -> str:
    """Return empty string for None/nan values."""
    s = str(val).strip()
    return "" if s.lower() in ("nan", "none", "") else s


def _fmt_phone(phone: str) -> str:
    """Format Australian phone number for display."""
    p = _clean(phone).replace(" ", "").replace("-", "")
    if not p:
        return ""
    if len(p) == 10 and p.startswith("0"):
        if p.startswith("04"):
            return f"{p[:4]} {p[4:7]} {p[7:]}"
        return f"{p[:2]} {p[2:6]} {p[6:]}"
    return p


def nqs_badge(rating: str) -> str:
    r = _clean(rating).lower()
    if not r:
        return "<span style='color:#aaa;font-size:11px'>-</span>"
    if "exceeding" in r:
        return "<span style='background:#27ae60;color:white;padding:2px 6px;border-radius:3px;font-size:11px'>Exceeding</span>"
    if "meeting" in r:
        return "<span style='background:#2980b9;color:white;padding:2px 6px;border-radius:3px;font-size:11px'>Meeting</span>"
    if "working" in r:
        return "<span style='background:#e67e22;color:white;padding:2px 6px;border-radius:3px;font-size:11px'>Working Towards</span>"
    if "significant" in r:
        return "<span style='background:#c0392b;color:white;padding:2px 6px;border-radius:3px;font-size:11px'>Sig. Improvement</span>"
    return f"<span style='color:#aaa;font-size:11px'>-</span>"


def kinder_badge(has_kinder: bool) -> str:
    if has_kinder:
        return "<span style='background:#1abc9c;color:white;padding:1px 5px;border-radius:3px;font-size:10px'>Kinder</span>"
    return ""


def nfp_badge(is_nfp: bool) -> str:
    if is_nfp:
        return "<span style='background:#8e44ad;color:white;padding:1px 5px;border-radius:3px;font-size:10px'>NFP</span>"
    return "<span style='background:#7f8c8d;color:white;padding:1px 5px;border-radius:3px;font-size:10px'>For-profit</span>"


def render_centre_row(c: dict, is_lead: bool = False) -> str:
    """Render a single centre as a table row."""
    bg         = "#fffde7" if is_lead else "white"
    name       = _clean(c.get("service_name", ""))
    operator   = _clean(c.get("operator_name", ""))
    suburb     = _clean(c.get("suburb", ""))
    state      = _clean(c.get("state", ""))
    phone_raw  = _clean(c.get("phone", ""))
    phone_fmt  = _fmt_phone(phone_raw)
    places     = c.get("approved_places", 0)
    address    = _clean(c.get("service_address", ""))

    # Search URLs
    sb_link     = _sb_url(name, suburb, state)
    google_link = _google_url(operator if operator else name, suburb)

    # Contact match
    contacts = c.get("matched_contacts", [])
    contact_html = ""
    if contacts:
        best  = contacts[0]
        cname = f"{_clean(best.get('first_name',''))} {_clean(best.get('last_name',''))}".strip()
        email = _clean(best.get("email", ""))
        title = _clean(best.get("title", ""))
        if email:
            contact_html = (
                f"<br><span style='color:#555;font-size:11px'>"
                f"{cname}{' — ' + title if title else ''} "
                f"&bull; <a href='mailto:{email}' style='color:#2980b9'>{email}</a>"
                f"</span>"
            )
        elif cname:
            contact_html = (
                f"<br><span style='color:#555;font-size:11px'>"
                f"{cname}{' — ' + title if title else ''}"
                f"</span>"
            )

    # Phone cell
    if phone_fmt and phone_raw:
        phone_cell = f"<a href='tel:{phone_raw}' style='color:#2c3e50;text-decoration:none'>{phone_fmt}</a>"
    else:
        phone_cell = "<span style='color:#ccc'>—</span>"

    # Address tooltip
    addr_tip = f" title='{address}'" if address else ""

    # Lead indicator
    lead_marker = " &#9733;" if is_lead else ""

    return f"""
    <tr style='background:{bg};border-bottom:1px solid #f0f0f0'>
        <td style='padding:6px 8px;font-size:12px'>
            <a href='{sb_link}' style='color:#2c3e50;font-weight:{"bold" if is_lead else "normal"};text-decoration:none'
               target='_blank'{addr_tip}>
                {name}{lead_marker}
            </a>
            <a href='{google_link}' target='_blank'
               style='margin-left:6px;font-size:10px;color:#aaa;text-decoration:none'
               title='Search {operator or name} on Google'>&#127760;</a>
            {contact_html}
        </td>
        <td style='padding:6px 8px;font-size:11px;color:#666;max-width:140px;overflow:hidden;white-space:nowrap;text-overflow:ellipsis'
            title='{operator}'>{operator[:35] + "..." if len(operator) > 35 else operator}</td>
        <td style='padding:6px 8px;font-size:12px;text-align:center;font-weight:bold'>{places}</td>
        <td style='padding:6px 8px;font-size:12px;text-align:center'>{nqs_badge(c.get("nqs_rating",""))}</td>
        <td style='padding:6px 8px;font-size:12px;text-align:center'>{nfp_badge(c.get("is_nfp", False))}</td>
        <td style='padding:6px 8px;font-size:12px;text-align:center'>{kinder_badge(c.get("has_kinder", False))}</td>
        <td style='padding:6px 8px;font-size:12px'>{phone_cell}</td>
    </tr>"""


def render_catchment_block(lead: dict) -> str:
    """Render full catchment section as HTML for email digest."""
    c = lead.get("catchment", {})
    if not c:
        return ""

    sa2       = _clean(c.get("sa2_name", "Unknown SA2"))
    sa2_code  = _clean(c.get("sa2_code", ""))
    pop       = c.get("pop_0_4")
    pop_yr    = _clean(c.get("pop_year", ""))
    pop_cagr  = c.get("pop_0_4_cagr")
    inc_ann   = c.get("median_income_weekly_annual")
    inc_yr    = _clean(c.get("income_year", ""))
    inc_cagr  = c.get("income_cagr")
    irsd      = c.get("irsd_decile")
    irsad     = c.get("irsad_decile")
    ccs       = c.get("est_ccs_rate")
    gap       = c.get("est_gap_fee_per_day")
    fee_sens  = _clean(c.get("fee_sensitivity", "unknown"))
    ratio        = c.get("supply_ratio")
    tier         = _clean(c.get("supply_tier", "unknown"))
    nfp_ratio    = c.get("nfp_ratio")
    kinder_ratio = c.get("kinder_ratio")
    lead_kinder  = c.get("lead_has_kinder", False)
    total_cen    = c.get("total_centres", 0) or 0
    total_pl     = c.get("total_licensed_places", 0) or 0
    centres      = c.get("competing_centres", [])
    pop_gr       = _clean(c.get("pop_growth_label", "unknown"))

    # Lead's own service name for highlighting in centre list
    lead_service = _clean(lead.get("service_name", ""))

    def fmt_cagr(cagr, positive_color="#27ae60", negative_color="#c0392b"):
        if cagr is None:
            return ""
        color = positive_color if cagr >= 0 else negative_color
        arrow = "^^" if cagr >= 3 else ("^" if cagr >= 1 else ("->" if cagr >= -1 else "v"))
        return f"<span style='color:{color};font-size:11px'> {arrow} {cagr:+.1f}% p.a.</span>"

    tier_color = {
        "undersupplied": "#27ae60",
        "balanced":      "#f39c12",
        "supplied":      "#e67e22",
        "oversupplied":  "#c0392b",
    }.get(tier, "#95a5a6")

    sens_color = {
        "high":     "#c0392b",
        "moderate": "#e67e22",
        "low":      "#27ae60",
    }.get(fee_sens, "#95a5a6")

    growth_color = {
        "strong_growth": "#27ae60",
        "growth":        "#2ecc71",
        "stable":        "#f39c12",
        "declining":     "#c0392b",
    }.get(pop_gr, "#95a5a6")

    # Build centre rows — highlight the lead's own centre
    centre_rows = ""
    for ctr in centres:
        is_lead_centre = _clean(ctr.get("service_name", "")) == lead_service
        centre_rows += render_centre_row(ctr, is_lead=is_lead_centre)

    centres_table = f"""
    <details style='margin-top:8px'>
        <summary style='cursor:pointer;color:#2980b9;font-size:12px;font-weight:bold;padding:4px 0;list-style:none'>
            &#9660; View all {total_cen} centres in {sa2} SA2 ({total_pl:,} licensed places)
        </summary>
        <table style='width:100%;border-collapse:collapse;margin-top:6px;font-size:12px'>
            <thead>
                <tr style='background:#ecf0f1'>
                    <th style='padding:6px 8px;text-align:left;font-size:11px'>Centre
                        <span style='font-weight:normal;color:#888'>&nbsp;[SB &#128269; | &#127760; web]</span>
                    </th>
                    <th style='padding:6px 8px;text-align:left;font-size:11px'>Operator</th>
                    <th style='padding:6px 8px;text-align:center;font-size:11px'>Places</th>
                    <th style='padding:6px 8px;text-align:center;font-size:11px'>NQS</th>
                    <th style='padding:6px 8px;text-align:center;font-size:11px'>Type</th>
                    <th style='padding:6px 8px;text-align:center;font-size:11px'>Kinder</th>
                    <th style='padding:6px 8px;text-align:left;font-size:11px'>Phone</th>
                </tr>
            </thead>
            <tbody>
                {centre_rows}
            </tbody>
        </table>
    </details>""" if centres else f"<p style='font-size:12px;color:#555'>{total_cen} centres in SA2</p>"

    html = f"""
<div style='background:#f8f9fa;border-left:4px solid #3498db;padding:12px 16px;margin:8px 0;border-radius:0 4px 4px 0'>
    <div style='font-size:13px;font-weight:bold;color:#2c3e50;margin-bottom:8px'>
        Catchment: {sa2} [{sa2_code}]
    </div>

    <table style='width:100%;border-collapse:collapse;font-size:12px'>
        <tr>
            <td style='width:50%;vertical-align:top;padding-right:12px'>
                <div style='font-weight:bold;color:#555;margin-bottom:4px;font-size:11px;letter-spacing:0.5px'>DEMAND</div>
                <div>Under-5 pop: <b>{f"{pop:,}" if pop else "n/a"}</b> ({pop_yr})
                    {fmt_cagr(pop_cagr)}
                    <span style='background:{growth_color};color:white;padding:1px 5px;border-radius:3px;font-size:10px;margin-left:4px'>
                        {pop_gr.upper().replace("_"," ")}
                    </span>
                </div>
                <div style='margin-top:2px'>
                    Median income: <b>${f"{int(inc_ann):,}" if inc_ann else "n/a"}</b> p.a. ({inc_yr})
                    {fmt_cagr(inc_cagr)}
                </div>
            </td>
            <td style='width:50%;vertical-align:top'>
                <div style='font-weight:bold;color:#555;margin-bottom:4px;font-size:11px;letter-spacing:0.5px'>CCS &amp; FEE SENSITIVITY</div>
                <div>Est. CCS rate: <b>{f"{ccs*100:.0f}%" if ccs is not None else "n/a"}</b> at median income</div>
                <div>Est. gap fee: <b>${f"{int(gap):,}" if gap else "n/a"}/day</b>
                    <span style='background:{sens_color};color:white;padding:1px 5px;border-radius:3px;font-size:10px;margin-left:4px'>
                        {fee_sens.upper()} SENSITIVITY
                    </span>
                </div>
                <div style='margin-top:2px'>
                    IRSD: <b>{irsd or "n/a"}/10</b> &nbsp;|&nbsp; IRSAD: <b>{irsad or "n/a"}/10</b>
                </div>
            </td>
        </tr>
    </table>

    <div style='margin-top:8px;font-size:12px'>
        <b>Supply:</b>
        <span style='background:{tier_color};color:white;padding:1px 6px;border-radius:3px;font-size:11px;margin:0 4px'>
            {tier.upper()}
        </span>
        {f"{ratio:.2f}x" if ratio else "n/a"} ratio &nbsp;|&nbsp;
        {f"{nfp_ratio*100:.0f}%" if nfp_ratio is not None else "?"} NFP &nbsp;|&nbsp;
        {f"{kinder_ratio*100:.0f}%" if kinder_ratio is not None else "?"} kinder
        {"&nbsp;|&nbsp; <b style='color:#1abc9c'>This centre: Kinder approved &#10003;</b>" if lead_kinder else ""}
    </div>

    {centres_table}
</div>"""

    return html
