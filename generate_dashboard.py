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
import shutil
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
SA2_HISTORY = DATA_DIR / "sa2_history.json"

DOCS_DIR.mkdir(exist_ok=True)

# ─────────────────────────────────────────────
# DATA LOADERS
# ─────────────────────────────────────────────

def load_json(path, default=None):
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception:
        return default or []


def _make_location_desc(record, catchment):
    """Generate a 1-2 sentence location description from SA2 data fields."""
    state_names = {
        "NSW": "New South Wales", "VIC": "Victoria", "QLD": "Queensland",
        "WA": "Western Australia", "SA": "South Australia", "TAS": "Tasmania",
        "ACT": "the Australian Capital Territory", "NT": "the Northern Territory",
    }
    state = str(record.get("state", "") or "").strip().upper()
    state_full = state_names.get(state, state)
    irsd_label = str(catchment.get("irsd_label", "") or "").replace("_", " ")
    pop_cagr = catchment.get("pop_0_4_cagr")
    pop_label = catchment.get("pop_growth_label", "")
    supply_tier = str(catchment.get("supply_tier", "") or "").replace("_", " ")
    sa2_name = str(catchment.get("sa2_name", "") or "").title()

    # Sentence 1: location context
    s1 = f"SA2 area in {state_full}."

    # Sentence 2: demand and supply characterisation
    demand_desc = ""
    if pop_cagr is not None:
        if pop_cagr >= 3.0:
            demand_desc = f"rapidly growing under-5 population (+{pop_cagr:.1f}% p.a.)"
        elif pop_cagr >= 1.0:
            demand_desc = f"growing under-5 population (+{pop_cagr:.1f}% p.a.)"
        elif pop_cagr >= -1.0:
            demand_desc = f"stable under-5 population ({pop_cagr:+.1f}% p.a.)"
        else:
            demand_desc = f"declining under-5 population ({pop_cagr:.1f}% p.a.)"

    seifa_desc = irsd_label.capitalize() if irsd_label else ""
    supply_desc = f"{supply_tier} childcare market" if supply_tier else ""

    parts = [p for p in [seifa_desc, demand_desc, supply_desc] if p]
    s2 = (". ".join(parts[:2]) + ".") if parts else ""

    return (s1 + " " + s2).strip()


def build_catchments_json(catchments, docs_dir, snap=None):
    """
    Group catchments by SA2 and write docs/catchments.json.

    ALL catchment-level metrics are computed from the FULL SA2 universe
    using services_snapshot.csv — not just our target operators.
    Target operators are stored separately in 'services[]'.

    snap = services_snapshot rows (all 18,223 LDC services).
    """
    import math
    import pandas as pd

    KINDER_TERMS = ["kindergarten", "kinder", "kindy"]
    NFP_KW = [
        "incorporated", " inc ", "association", "community", "council", "church",
        "diocese", "parish", "ymca", "salvation", "catholic", "anglican", "uniting",
        "baptist", "lutheran", "presbyterian", "limited by guarantee", "cooperative",
        "co-operative", "neighbourhood", "aboriginal", "indigenous",
    ]

    # ── Postcode → SA2 concordance ──
    pc_to_sa2 = {}
    conc_path = BASE_DIR / "abs_data" / "postcode_to_sa2_concordance.csv"
    if conc_path.exists():
        try:
            conc = pd.read_csv(conc_path, dtype=str)
            for _, row in conc.iterrows():
                pc   = str(row.get("POSTCODE", "") or "").strip().zfill(4)
                code = str(row.get("SA2_CODE",  "") or "").strip()
                if pc and code and code != "nan":
                    pc_to_sa2[pc] = code
            print(f"  Concordance: {len(pc_to_sa2):,} postcodes")
        except Exception as e:
            print(f"  WARNING concordance: {e}")

    # ── Group ALL LDC services by SA2 from snapshot ──
    sa2_all_centres = {}
    if snap and pc_to_sa2:
        for row in snap:
            if str(row.get("long_day_care","")).strip().upper() != "YES":
                continue
            pc_raw = str(row.get("postcode","") or "")
            try:
                pc = str(int(float(pc_raw))).zfill(4)
            except Exception:
                pc = pc_raw.strip().zfill(4)
            sa2 = pc_to_sa2.get(pc)
            if not sa2:
                continue

            places = 0
            try:
                places = int(float(str(row.get("numberofapprovedplaces","0") or "0")))
            except Exception:
                pass

            svc_name    = str(row.get("servicename","") or "").strip()
            provider    = str(row.get("providerlegalname","") or "")
            provider_lo = provider.lower()
            nqs         = str(row.get("overallrating","") or "").strip()

            # NFP detection — keyword on legal name
            is_nfp = any(kw in provider_lo for kw in NFP_KW)

            # Kinder detection — name-based (primary) + ACECQA flags (supplement)
            name_lo = svc_name.lower()
            name_has_kinder = any(t in name_lo for t in KINDER_TERMS)
            acecqa_kinder = (
                str(row.get("preschool/kindergarten_-_stand_alone","")).upper() == "YES" or
                str(row.get("preschool/kindergarten_-_part_of_a_school","")).upper() == "YES"
            )
            has_kinder = name_has_kinder or acecqa_kinder
            # Source label for display
            if has_kinder:
                if name_has_kinder and acecqa_kinder:
                    kinder_source = "ACECQA verified"
                elif name_has_kinder:
                    kinder_source = "name-based — ACECQA unverified"
                else:
                    kinder_source = "ACECQA"
            else:
                kinder_source = None

            # Approval date from snapshot
            appr_date = ""
            for dc in ["serviceapprovalgranteddate", "approval date", "approvaldate"]:
                val = str(row.get(dc, "") or "").strip()
                if val and val.lower() != "nan":
                    appr_date = val
                    break

            if sa2 not in sa2_all_centres:
                sa2_all_centres[sa2] = []
            sa2_all_centres[sa2].append({
                "service_name":    svc_name,
                "approved_places": places,
                "nqs_rating":      nqs,
                "is_nfp":          is_nfp,
                "has_kinder":      has_kinder,
                "kinder_source":   kinder_source,
                "approval_date":   appr_date,
            })

        print(f"  SA2 centre groups: {len(sa2_all_centres):,} SA2s from snapshot")

    # ── Helper: CCS pricing insight ──
    def _ccs_insight(ccs_rate, irsd_decile):
        if ccs_rate is None:
            return None
        pct = round(ccs_rate * 100)
        if ccs_rate >= 0.80:
            level = "High CCS dependency"
            msg = (f"~{pct}% of families at median income receive high subsidy. "
                   "Pricing above the CCS hourly cap sharply increases out-of-pocket "
                   "costs — enrolment risk is acute. New entrants must price carefully.")
        elif ccs_rate >= 0.60:
            level = "Moderate CCS dependency"
            msg = (f"~{pct}% subsidy rate at median income. Fee positioning relative "
                   "to the CCS hourly cap matters but catchment has some income buffer.")
        else:
            level = "Low CCS dependency"
            msg = (f"Affluent catchment (~{pct}% subsidy at median income). "
                   "Families can absorb above-cap pricing but expect premium quality.")
        return {"level": level, "message": msg}

    # ── Helper: NQS quality distribution ──
    def _nqs_quality(centres):
        if not centres:
            return None
        exc = sum(1 for c in centres if "Exceeding" in (c.get("nqs_rating") or ""))
        mtg = sum(1 for c in centres if c.get("nqs_rating","") == "Meeting NQS")
        wtn = sum(1 for c in centres if "Working Towards" in (c.get("nqs_rating") or ""))
        sir = sum(1 for c in centres if "Significant" in (c.get("nqs_rating") or ""))
        unr = len(centres) - exc - mtg - wtn - sir
        rated = exc + mtg + wtn + sir
        score = round((exc*100 + mtg*75 + wtn*50) / rated, 1) if rated > 0 else None
        return {
            "exceeding": exc, "meeting": mtg,
            "working_towards": wtn, "sir": sir, "unrated": unr,
            "total": len(centres),
            "quality_score": score,
            "stress_count": wtn + sir,
            "stress_pct": round((wtn + sir) / len(centres) * 100, 1),
        }

    # ── Helper: centre size profile ──
    def _size_profile(centres):
        pl = [c["approved_places"] for c in centres if (c.get("approved_places") or 0) > 0]
        if not pl:
            return None
        return {
            "largest":      max(pl),
            "smallest":     min(pl),
            "average":      round(sum(pl) / len(pl)),
            "band_u50":     sum(1 for p in pl if p < 50),
            "band_50_99":   sum(1 for p in pl if 50 <= p < 100),
            "band_100_149": sum(1 for p in pl if 100 <= p < 150),
            "band_150plus": sum(1 for p in pl if p >= 150),
        }

    # ── Build SA2 map ──
    sa2_map = {}
    for record in catchments:
        c = record.get('catchment', {})
        sa2_code = c.get('sa2_code')
        if not sa2_code:
            continue

        # Use ALL centres in SA2 (from snapshot) for catchment-level stats
        # Sort by approval_date descending (most recent first)
        def _parse_date(d):
            for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"]:
                try:
                    from datetime import datetime
                    return datetime.strptime(str(d), fmt)
                except Exception:
                    pass
            from datetime import datetime
            return datetime.min
        all_centres = sorted(
            sa2_all_centres.get(sa2_code, []),
            key=lambda c: _parse_date(c.get("approval_date", "")),
            reverse=True
        )
        kinder_centres  = [x for x in all_centres if x.get("has_kinder")]
        kinder_places   = sum(x.get("approved_places",0) for x in kinder_centres)
        nfp_centres     = [x for x in all_centres if x.get("is_nfp")]
        total_c         = len(all_centres)
        total_pl        = sum(x.get("approved_places",0) for x in all_centres)
        nfp_ratio       = round(len(nfp_centres)/total_c, 3) if total_c > 0 else None
        kinder_ratio    = round(len(kinder_centres)/total_c, 3) if total_c > 0 else None
        supply_ratio    = round(total_pl / c["pop_0_4"], 3) if c.get("pop_0_4") else c.get("supply_ratio")

        if sa2_code not in sa2_map:
            sa2_map[sa2_code] = {
                'sa2_code':             sa2_code,
                'sa2_name':             c.get('sa2_name'),
                'pop_0_4':              c.get('pop_0_4'),
                'pop_0_4_cagr':         c.get('pop_0_4_cagr'),
                'pop_growth_label':     c.get('pop_growth_label'),
                'median_income_annual': c.get('median_income_weekly_annual'),
                'income_cagr':          c.get('income_cagr'),
                'est_ccs_rate':         c.get('est_ccs_rate'),
                'est_gap_fee_per_day':  c.get('est_gap_fee_per_day'),
                'fee_sensitivity':      c.get('fee_sensitivity'),
                'irsd_decile':          c.get('irsd_decile'),
                'irsd_label':           c.get('irsd_label'),
                # Supply — from full SA2 snapshot universe
                'total_centres':        total_c or c.get('total_centres'),
                'total_licensed_places': total_pl or c.get('total_licensed_places'),
                'nfp_ratio':            nfp_ratio if nfp_ratio is not None else c.get('nfp_ratio'),
                'kinder_ratio':         kinder_ratio if kinder_ratio is not None else c.get('kinder_ratio'),
                'kinder_count':         len(kinder_centres),
                'kinder_places':        kinder_places,
                'supply_ratio':         supply_ratio,
                'supply_tier':          c.get('supply_tier'),
                # Enriched analytics — all from full SA2 universe
                'nqs_quality':          _nqs_quality(all_centres),
                'size_profile':         _size_profile(all_centres),
                'ccs_insight':          _ccs_insight(c.get('est_ccs_rate'), c.get('irsd_decile')),
                # Slim competing centres list for display
                'competing_centres':    all_centres,
                # Generated fields
                'location_description': _make_location_desc(record, c),
                'unemployment_rate':    None,
                'services': [],
            }

        sa2_map[sa2_code]['services'].append({
            'service_name':      record.get('service_name', ''),
            'operator_name':     record.get('operator_name', ''),
            'suburb':            record.get('suburb', ''),
            'postcode':          str(record.get('postcode', '') or ''),
            'state':             record.get('state', ''),
            'approved_places':   record.get('approved_places'),
            'overall_rating':    record.get('overall_rating', ''),
            'priority_tier':     record.get('priority_tier', ''),
            'score':             record.get('score'),
            'is_nfp':            record.get('is_nfp', False),
            'has_kinder':        record.get('has_kinder', False),
            'service_appr_num':  record.get('service_approval_number', ''),
        })

    def _sanitise(obj):
        if isinstance(obj, dict):
            return {k: _sanitise(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_sanitise(v) for v in obj]
        if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
            return None
        return obj

    grouped = [_sanitise(g) for g in sa2_map.values()]
    out_path = docs_dir / 'catchments.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(grouped, f, ensure_ascii=False)
    print(f"  Catchments JSON: {out_path.name} ({len(grouped):,} SA2 areas, "
          f"{sum(len(g['services']) for g in grouped):,} services)")
    return grouped
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

    # Auto-copy sa2_history.json from data/ to docs/ for browser fetch()
    if SA2_HISTORY.exists():
        dest = DOCS_DIR / "sa2_history.json"
        shutil.copy(SA2_HISTORY, dest)
        print(f"  Copied sa2_history.json → docs/ ({SA2_HISTORY.stat().st_size:,} bytes)")
    else:
        print(f"  WARNING: {SA2_HISTORY} not found — run build_sa2_history.py first")

    # Load data
    print("Loading data...")
    snap       = load_snapshot()
    operators  = load_json(TARGETS, [])
    hot        = load_json(HOT, [])
    property_d = load_json(PROPERTY, {})
    brief      = load_json(BRIEF, {})
    catchments = load_json(CATCHMENT, [])
    
    print(f"  Snapshot: {len(snap):,} services")
    history    = load_json(HISTORY, {})
    hist_data  = history.get("history", [])
    print(f"  History: {len(hist_data)} quarters ({hist_data[0]['quarter'] if hist_data else 'none'} → {hist_data[-1]['quarter'] if hist_data else 'none'})")
    print(f"  Operators: {len(operators):,}")
    print(f"  Property data: {len(property_d.get('operators',[]))} enriched")

    # Build catchments.json — SA2-grouped, written to docs/ for fetch() load
    build_catchments_json(catchments, DOCS_DIR, snap=snap)

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

/* ── ABR SEARCH LINK ── */
.abr-search-link {{
    color: var(--accent);
    text-decoration: none;
    font-size: 12px;
    font-weight: 500;
    padding: 4px 8px;
    border: 1px solid var(--border);
    border-radius: 4px;
    background: linear-gradient(135deg, var(--surface), var(--surface2));
    transition: all 0.2s ease;
    display: inline-block;
}}

.abr-search-link:hover {{
    color: var(--accent-bright);
    border-color: var(--accent);
    background: linear-gradient(135deg, var(--surface2), var(--surface));
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}}

/* ── CATCHMENT CARDS ── */
.catchment-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 16px;
}}

.catchment-header h3 {{
    margin: 0 0 4px 0;
    color: var(--text);
    font-size: 18px;
    font-weight: 600;
}}

.sa2-code {{
    color: var(--muted);
    font-size: 14px;
    font-weight: 400;
    font-family: var(--mono);
}}

.catchment-summary {{
    color: var(--muted);
    font-size: 14px;
    margin-bottom: 16px;
}}

.catchment-metrics {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 20px;
    padding: 16px;
    background: var(--surface2);
    border-radius: 6px;
}}

.metric {{
    text-align: center;
}}

.metric-label {{
    color: var(--muted);
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}}

.metric-value {{
    color: var(--text);
    font-size: 20px;
    font-weight: 600;
    font-family: var(--mono);
    margin-bottom: 4px;
}}

.metric-trend {{
    color: var(--muted);
    font-size: 11px;
}}

.metric-trend.declining {{ color: #ff6b6b; }}
.metric-trend.growing {{ color: #51cf66; }}
.metric-trend.stable {{ color: var(--muted); }}

.section-header {{
    color: var(--text);
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}}

.market-metrics {{
    color: var(--muted);
    font-size: 11px;
    font-weight: 400;
    text-transform: none;
}}

/* ── TREND SECTION ── */
.trend-section {{
    background: var(--surface2);
    border-radius: 6px;
    padding: 16px;
    margin-bottom: 20px;
}}

.mini-chart {{
    margin: 12px 0;
}}

.trend-chart {{
    width: 100%;
    height: 60px;
    background: var(--bg);
    border-radius: 4px;
    margin-bottom: 8px;
}}

.chart-legend {{
    display: flex;
    gap: 16px;
    font-size: 11px;
    color: var(--muted);
    justify-content: center;
}}

.legend-line {{
    display: inline-block;
    width: 20px;
    height: 2px;
    margin-right: 4px;
    vertical-align: middle;
}}

.legend-line.solid {{ background: var(--accent); }}
.legend-line.dashed {{ 
    background: linear-gradient(to right, var(--accent2) 50%, transparent 50%);
    background-size: 4px 2px;
}}

.trend-summary {{
    display: flex;
    gap: 20px;
    font-size: 12px;
    color: var(--muted);
    justify-content: center;
}}

/* ── OPERATORS SECTION ── */
.operators-section {{
    background: var(--surface2);
    border-radius: 6px;
    padding: 16px;
}}

.operators-list {{
    display: grid;
    gap: 8px;
}}

.operator-row {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    transition: all 0.2s ease;
    cursor: pointer;
}}

.operator-row:hover {{
    border-color: var(--accent);
    transform: translateY(-1px);
}}

.operator-summary {{
    padding: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}}

.operator-name {{
    color: var(--text);
    font-weight: 500;
    font-size: 14px;
}}

.operator-stats {{
    display: flex;
    gap: 12px;
    align-items: center;
    font-size: 12px;
    color: var(--muted);
}}

.market-share {{
    font-weight: 500;
    color: var(--accent);
}}

.nqs-indicator {{
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 10px;
    font-weight: 500;
    text-transform: uppercase;
}}

.nqs-indicator.nqs-exceeding-nqs {{ background: #51cf66; color: #000; }}
.nqs-indicator.nqs-meeting-nqs {{ background: #339af0; color: #fff; }}
.nqs-indicator.nqs-working-towards-nqs {{ background: #ffd43b; color: #000; }}
.nqs-indicator.nqs-not-rated {{ background: var(--border); color: var(--muted); }}

.operator-details {{
    padding: 0 12px;
    max-height: 0;
    overflow: hidden;
    transition: all 0.3s ease;
}}

.operator-row[data-expanded="true"] .operator-details {{
    max-height: 500px;
    padding: 0 12px 12px 12px;
}}

.performance-metrics {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 12px;
    padding: 12px;
    background: var(--surface2);
    border-radius: 4px;
    margin-bottom: 12px;
}}

.metric-small {{
    text-align: center;
}}

.metric-small span:first-child {{
    display: block;
    color: var(--muted);
    font-size: 10px;
    text-transform: uppercase;
    margin-bottom: 4px;
}}

.metric-small span:last-child {{
    display: block;
    color: var(--text);
    font-weight: 600;
    font-size: 14px;
}}

.score {{
    color: var(--accent) !important;
}}

.centres-list {{
    display: grid;
    gap: 6px;
}}

.centre-item {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px;
    background: var(--bg);
    border-radius: 4px;
    font-size: 12px;
}}

.centre-name {{
    flex: 1;
    color: var(--text);
    margin-right: 8px;
}}

.centre-places {{
    color: var(--muted);
    font-family: var(--mono);
    margin-right: 8px;
}}

.centre-rating {{
    padding: 2px 4px;
    border-radius: 2px;
    font-size: 9px;
    font-weight: 500;
    text-transform: uppercase;
}}

.no-data {{
    color: var(--muted);
    text-align: center;
    padding: 20px;
    font-size: 12px;
}}
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

// ── CATCHMENT DATA — loaded via fetch same as operators.json ──
let allCatchments = [];
let catchmentsReady = false;
let sa2HistoryData = {{}};  // keyed by sa2_code for O(1) lookup

fetch('sa2_history.json')
    .then(r => r.ok ? r.json() : Promise.reject('not found'))
    .then(data => {{
        // Build lookup: sa2_code → {{quarters, dates, places, services, supply_ratio}}
        (data.sa2s || []).forEach(sa2 => {{
            sa2HistoryData[sa2.sa2_code] = sa2;
        }});
        console.log('SA2 history loaded: ' + Object.keys(sa2HistoryData).length + ' SA2s');
    }})
    .catch(e => console.warn('sa2_history.json not available — Panel 3 will show current data only'));

// Show a loading indicator in Panel 3 immediately while data fetches
document.addEventListener('DOMContentLoaded', function() {{
    const results = document.getElementById('catchment-results');
    if (results) results.innerHTML = '<p style="color:var(--muted);padding:20px 0;">⏳ Loading catchment data…</p>';
}});

fetch('catchments.json')
    .then(r => {{
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json();
    }})
    .then(data => {{
        allCatchments = data;
        catchmentsReady = true;
        console.log('Catchments loaded: ' + data.length + ' SA2 areas');
        // Clear the loading message
        const results = document.getElementById('catchment-results');
        const q = document.getElementById('catch-search');
        if (q && q.value.trim().length >= 2) {{
            // User already has a search typed — run it immediately
            filterCatchments();
        }} else if (results) {{
            results.innerHTML = '<p style="color:var(--muted);padding:20px 0;">Enter a suburb or postcode to explore catchment intelligence.</p>';
        }}
    }})
    .catch(e => {{
        catchmentsReady = false;
        console.warn('catchments.json load failed:', e);
        const results = document.getElementById('catchment-results');
        if (results) results.innerHTML = '<p style="color:var(--hot);padding:20px 0;">Could not load catchment data. Check that catchments.json exists in docs/.</p>';
    }});
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
                    <a onclick="jumpToCatchment('${{c.suburb}}','${{c.postcode}}')" class="centre-link" style="cursor:pointer;color:var(--accent2)">Catchment →</a>
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
                    <div class="detail-block-value" style="font-family:var(--mono)">
                        ${{op.abn ? op.abn : `<a href="https://abr.business.gov.au/Search/Index?SearchText=${{encodeURIComponent(op.legal_name.replace(/\\s+(pty|ltd|limited|proprietary|group|holdings)$/gi, '').replace(/[^\\w\\s]/g, '').trim())}}" target="_blank" class="abr-search-link" title="Search ABR for ${{op.legal_name}}">🔍 Search ABR →</a>`}}
                    </div>
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
        {{ quarter: 'Q3 2013', label: 'NQF Launch',    color: 'rgba(61,126,255,0.35)' }},
        {{ quarter: 'Q1 2018', label: 'NQS Reform',    color: 'rgba(61,126,255,0.35)' }},
        {{ quarter: 'Q2 2020', label: 'COVID',         color: 'rgba(224,92,58,0.45)' }},
        {{ quarter: 'Q3 2022', label: 'CCS Reform',    color: 'rgba(0,201,167,0.35)' }},
        {{ quarter: 'Q3 2023', label: 'Wage +15%',     color: 'rgba(155,89,182,0.45)' }},
        {{ quarter: 'Q1 2026', label: '3-Day Guar.',   color: 'rgba(0,201,167,0.35)' }},
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

// ── PANEL 3 — CATCHMENT EXPLORER ──
// Search by suburb, postcode, or SA2 name → renders SA2-level charts

var _lastCatchmentMatches = [];

function filterCatchments() {{
    const q = document.getElementById('catch-search').value.trim().toLowerCase();
    const results = document.getElementById('catchment-results');

    if (q.length < 2) {{
        results.innerHTML = '<p style="color:var(--muted);padding:20px 0;">Enter a suburb or postcode to explore catchment intelligence.</p>';
        return;
    }}

    if (!allCatchments || allCatchments.length === 0) {{
        results.innerHTML = '<p style="color:var(--muted);padding:20px 0;">⏳ Catchment data still loading — results will appear automatically once ready.</p>';
        return;
    }}

    // Match on suburb, postcode, SA2 name or SA2 code from the services list
    const matches = allCatchments.filter(sa2 => {{
        if ((sa2.sa2_name || '').toLowerCase().includes(q)) return true;
        if ((sa2.sa2_code || '').includes(q)) return true;
        return (sa2.services || []).some(s =>
            (s.suburb || '').toLowerCase().includes(q) ||
            (s.postcode || '').includes(q) ||
            (s.service_name || '').toLowerCase().includes(q)
        );
    }});

    _lastCatchmentMatches = matches;

    if (matches.length === 0) {{
        results.innerHTML = '<p style="color:var(--muted);padding:20px 0;">No catchments found for <strong>' + q + '</strong>. Try a suburb name or postcode.</p>';
        return;
    }}

    // 1 match → show full detail immediately; 2-5 → show summary list
    const limited = matches.slice(0, 5);
    if (limited.length === 1) {{
        results.innerHTML = renderCatchmentDetail(limited[0]);
        buildCatchmentCharts(limited[0]);
    }} else {{
        results.innerHTML = limited.map((sa2, i) => renderCatchmentSummaryRow(sa2, i)).join('');
    }}
}}

function selectCatchment(idx) {{
    const sa2 = _lastCatchmentMatches[idx];
    if (!sa2) return;
    document.getElementById('catchment-results').innerHTML = renderCatchmentDetail(sa2);
    buildCatchmentCharts(sa2);
}}

function renderCatchmentSummaryRow(sa2, idx) {{
    const tier = sa2.supply_tier || 'unknown';
    const tierColor = {{ oversupplied: 'var(--hot)', supplied: 'var(--warm)', balanced: 'var(--accent2)', undersupplied: 'var(--accent)' }}[tier] || 'var(--muted)';
    const pop = sa2.pop_0_4 ? sa2.pop_0_4.toLocaleString() : 'n/a';
    const ratio = sa2.supply_ratio ? sa2.supply_ratio.toFixed(2) + 'x' : 'n/a';
    const suburbs = [...new Set((sa2.services || []).map(s => s.suburb).filter(Boolean))].slice(0, 3).join(', ');
    return `
    <div onclick="selectCatchment(${{idx}})" style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:16px;margin-bottom:10px;cursor:pointer;transition:border-color 0.2s"
         onmouseover="this.style.borderColor='var(--accent)'" onmouseout="this.style.borderColor='var(--border)'">
        <div style="display:flex;justify-content:space-between;align-items:center">
            <div>
                <div style="font-weight:600;font-size:14px">${{sa2.sa2_name || 'Unknown SA2'}}</div>
                <div style="color:var(--muted);font-size:12px;margin-top:2px">${{suburbs}} &bull; ${{(sa2.services||[]).length}} target services</div>
            </div>
            <div style="display:flex;gap:16px;align-items:center">
                <div style="text-align:right">
                    <div style="font-size:11px;color:var(--muted)">Under-5 pop</div>
                    <div style="font-weight:600">${{pop}}</div>
                </div>
                <div style="text-align:right">
                    <div style="font-size:11px;color:var(--muted)">Supply ratio</div>
                    <div style="font-weight:600">${{ratio}}</div>
                </div>
                <div style="padding:4px 10px;border-radius:4px;font-size:11px;font-weight:600;background:${{tierColor}}22;color:${{tierColor}};text-transform:uppercase">${{tier}}</div>
            </div>
        </div>
    </div>`;
}}

function renderCatchmentDetail(sa2) {{
    const tier = sa2.supply_tier || 'unknown';
    const tierColor = {{ oversupplied: 'var(--hot)', supplied: 'var(--warm)', balanced: 'var(--accent2)', undersupplied: 'var(--accent)' }}[tier] || 'var(--muted)';
    const popCagr = sa2.pop_0_4_cagr;
    const popTrend = popCagr == null ? '' : (popCagr >= 1 ? '▲' : popCagr <= -1 ? '▼' : '→') + ' ' + (popCagr > 0 ? '+' : '') + popCagr.toFixed(1) + '% p.a.';
    const popColor = popCagr == null ? 'var(--muted)' : popCagr >= 1 ? 'var(--accent2)' : popCagr <= -1 ? 'var(--hot)' : 'var(--muted)';

    // Kinder — from full SA2 universe (name-based + ACECQA)
    const kinderCount  = sa2.kinder_count || 0;
    const kinderPlaces = sa2.kinder_places || 0;
    const kinderStr    = sa2.total_centres ? kinderCount + ' of ' + sa2.total_centres : 'n/a';

    // NFP
    const nfpCount = sa2.nfp_ratio && sa2.total_centres ? Math.round(sa2.nfp_ratio * sa2.total_centres) : null;
    const nfpStr   = nfpCount != null
        ? nfpCount + ' of ' + sa2.total_centres + ' (' + Math.round(sa2.nfp_ratio*100) + '%)'
        : 'n/a';

    // NQS quality block
    const nqs = sa2.nqs_quality || {{}};
    const nqsTotal = nqs.total || 1;
    function nqsBar(count, color) {{
        const pct = Math.round(count/nqsTotal*100);
        return `<div style="display:flex;align-items:center;gap:8px;margin-bottom:5px">
            <div style="width:110px;font-size:11px;color:var(--muted)">${{count}} centres (${{pct}}%)</div>
            <div style="flex:1;height:7px;background:var(--surface);border-radius:3px;overflow:hidden">
                <div style="width:${{pct}}%;height:100%;background:${{color}};border-radius:3px"></div>
            </div></div>`;
    }}
    const nqsHtml = nqs.total ? `
        <div style="margin-bottom:6px">
            <div style="display:flex;justify-content:space-between;margin-bottom:8px">
                <span style="font-size:11px;font-weight:600">Quality score: ${{nqs.quality_score != null ? nqs.quality_score + '/100' : 'n/a'}}</span>
                <span style="font-size:11px;color:${{nqs.stress_pct > 20 ? 'var(--hot)' : nqs.stress_pct > 10 ? 'var(--warm)' : 'var(--accent2)'}}">
                    Regulatory stress: ${{nqs.stress_pct}}% (${{nqs.stress_count}} centres)
                </span>
            </div>
            <div style="font-size:10px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin-bottom:4px">Exceeding NQS</div>
            ${{nqsBar(nqs.exceeding, '#00c9a7')}}
            <div style="font-size:10px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin-bottom:4px">Meeting NQS</div>
            ${{nqsBar(nqs.meeting, '#3d7eff')}}
            <div style="font-size:10px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin-bottom:4px">Working Towards</div>
            ${{nqsBar(nqs.working_towards, '#d4890a')}}
            ${{nqs.sir > 0 ? '<div style="font-size:10px;text-transform:uppercase;letter-spacing:.06em;color:var(--hot);margin-bottom:4px">Sig. Improvement Required</div>' + nqsBar(nqs.sir, '#e05c3a') : ''}}
            ${{nqs.unrated > 0 ? '<div style="font-size:11px;color:var(--muted);margin-top:4px">' + nqs.unrated + ' not yet rated</div>' : ''}}
        </div>` : '<div style="color:var(--muted);font-size:11px">NQS data unavailable</div>';

    // Size profile block
    const sp = sa2.size_profile || null;
    const spHtml = sp ? `
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:8px">
            <div><div style="font-size:10px;color:var(--muted)">Largest</div><div style="font-size:16px;font-weight:600">${{sp.largest}} pl</div></div>
            <div><div style="font-size:10px;color:var(--muted)">Average</div><div style="font-size:16px;font-weight:600">${{sp.average}} pl</div></div>
            <div><div style="font-size:10px;color:var(--muted)">Smallest</div><div style="font-size:16px;font-weight:600">${{sp.smallest}} pl</div></div>
        </div>
        <div style="font-size:11px;color:var(--muted)">
            &lt;50pl: ${{sp.band_u50}} &nbsp;·&nbsp; 50–99: ${{sp.band_50_99}} &nbsp;·&nbsp; 100–149: ${{sp.band_100_149}} &nbsp;·&nbsp; 150+: ${{sp.band_150plus}}
        </div>` : '<div style="color:var(--muted);font-size:11px">Size data unavailable</div>';

    // CCS insight
    const ccs = sa2.ccs_insight || null;
    const ccsColor = ccs ? (ccs.level.includes('High') ? 'var(--hot)' : ccs.level.includes('Low') ? 'var(--accent2)' : 'var(--warm)') : 'var(--muted)';
    const ccsHtml = ccs ? `
        <div style="border-left:3px solid ${{ccsColor}};padding-left:12px">
            <div style="font-size:12px;font-weight:600;color:${{ccsColor}};margin-bottom:4px">${{ccs.level}}</div>
            <div style="font-size:12px;color:var(--muted);line-height:1.5">${{ccs.message}}</div>
            ${{sa2.est_gap_fee_per_day ? `<div style="font-size:11px;color:var(--muted);margin-top:6px">Est. gap fee at median income: <strong style="color:var(--text)">$` + sa2.est_gap_fee_per_day.toFixed(0) + `/day</strong></div>` : ''}}
        </div>` : '';

    // Target services
    const targetServices = (sa2.services || []);
    const nqsBadgeColor = {{ 'Exceeding NQS': '#00c9a7', 'Meeting NQS': '#3d7eff', 'Working Towards NQS': '#d4890a', 'Significant Improvement Required': '#e05c3a' }};
    const targetRows = targetServices.map((s, idx) => {{
        const tier2     = s.priority_tier || '';
        const typeLabel = s.is_nfp ? 'NFP' : 'For-Profit';
        const typeColor = s.is_nfp ? 'var(--accent2)' : 'var(--warm)';
        const kinderTag = s.has_kinder ? '<span style="background:rgba(0,201,167,0.1);color:var(--accent2);padding:1px 6px;border-radius:3px;font-size:10px;margin-left:4px">KINDER</span>' : '';
        const nqsRating = s.overall_rating || '';
        const nqsColor  = nqsBadgeColor[nqsRating] || 'var(--muted)';
        const nqsBg     = nqsRating.includes('Working') ? 'rgba(212,137,10,0.15)' :
                          nqsRating.includes('Significant') ? 'rgba(224,92,58,0.15)' :
                          nqsRating.includes('Exceeding') ? 'rgba(0,201,167,0.12)' :
                          nqsRating.includes('Meeting') ? 'rgba(61,126,255,0.12)' : 'var(--surface2)';
        const nqsTag    = nqsRating ? `<span style="background:${{nqsBg}};color:${{nqsColor}};padding:2px 8px;border-radius:4px;font-size:10px;font-weight:600">${{nqsRating.replace(' NQS','').replace('Significant Improvement Required','⚠ SIR')}}</span>` : '';
        const warnTag   = (nqsRating.includes('Working') || nqsRating.includes('Significant'))
            ? '<div style="font-size:10px;color:var(--hot);margin-top:3px">⚠ Poor quality rating — elevated enrolment and compliance risk</div>' : '';
        return `
        <div id="svc-card-${{idx}}" data-svcname="${{(s.service_name||'').replace(/"/g,'&quot;')}}"
             style="padding:10px 12px;background:var(--bg);border-radius:6px;margin-bottom:6px;border:1px solid transparent;transition:border-color 0.2s"
             onmouseenter="highlightEventByIdx(${{idx}}, true)"
             onmouseleave="highlightEventByIdx(${{idx}}, false)">
            <div style="display:flex;justify-content:space-between;align-items:flex-start">
                <div style="flex:1">
                    <div style="font-size:13px;font-weight:500;color:var(--text)">${{s.service_name || ''}}</div>
                    <div style="font-size:11px;color:var(--muted);margin-top:2px">
                        ${{s.operator_name || ''}} &bull; ${{s.suburb || ''}}, ${{s.state || ''}}
                        &bull; <span style="color:${{typeColor}}">${{typeLabel}}</span>
                        ${{kinderTag}}
                        ${{s.service_appr_num ? '&bull; <span style="font-family:var(--mono);font-size:10px">' + s.service_appr_num + '</span>' : ''}}
                    </div>
                    ${{warnTag}}
                </div>
                <div style="display:flex;gap:6px;align-items:center;flex-shrink:0;margin-left:12px">
                    <span style="font-family:var(--mono);font-size:11px;color:var(--muted)">${{s.approved_places || ''}} pl</span>
                    ${{nqsTag}}
                    ${{tier2 ? '<span class="tier-badge tier-' + tier2 + '">' + tier2.toUpperCase() + '</span>' : ''}}
                </div>
            </div>
        </div>`;
    }}).join('');

    return `
    <div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:24px;margin-bottom:24px">
        <!-- Header -->
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px">
            <div>
                <div style="font-size:18px;font-weight:600">${{sa2.sa2_name || 'Unknown SA2'}}</div>
                <div style="font-size:12px;color:var(--muted);margin-top:2px;font-family:var(--mono)">SA2 ${{sa2.sa2_code || ''}}</div>
            </div>
            <div style="padding:6px 14px;border-radius:6px;font-size:12px;font-weight:600;background:${{tierColor}}22;color:${{tierColor}};text-transform:uppercase;letter-spacing:.05em">${{tier}}</div>
        </div>
        ${{sa2.location_description ? `<div style="font-size:12px;color:var(--muted);margin-bottom:20px;line-height:1.5">${{sa2.location_description}}</div>` : ''}}

        <!-- 6 stat cards -->
        <div style="display:grid;grid-template-columns:repeat(6,1fr);gap:10px;margin-bottom:24px">
            <div style="background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius);padding:12px">
                <div class="stat-label">Under-5 Pop</div>
                <div class="stat-value" style="font-size:20px">${{sa2.pop_0_4 ? sa2.pop_0_4.toLocaleString() : 'n/a'}}</div>
                <div style="font-size:10px;color:${{popColor}};margin-top:3px">${{popTrend}}</div>
            </div>
            <div style="background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius);padding:12px">
                <div class="stat-label">Supply Ratio</div>
                <div class="stat-value" style="font-size:20px">${{sa2.supply_ratio ? sa2.supply_ratio.toFixed(2) + 'x' : 'n/a'}}</div>
                <div style="font-size:10px;color:var(--muted);margin-top:3px">places per child &lt;5</div>
            </div>
            <div style="background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius);padding:12px">
                <div class="stat-label">Median Income</div>
                <div class="stat-value" style="font-size:20px">${{sa2.median_income_annual ? '$' + Math.round(sa2.median_income_annual/1000) + 'k' : 'n/a'}}</div>
                <div style="font-size:10px;color:var(--muted);margin-top:3px">CCS ~${{sa2.est_ccs_rate ? Math.round(sa2.est_ccs_rate*100) + '%' : 'n/a'}}</div>
            </div>
            <div style="background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius);padding:12px">
                <div class="stat-label">SEIFA (IRSD)</div>
                <div class="stat-value" style="font-size:20px">${{sa2.irsd_decile ? sa2.irsd_decile + '/10' : 'n/a'}}</div>
                <div style="font-size:10px;color:var(--muted);margin-top:3px">${{(sa2.irsd_label || '').replace('_',' ')}}</div>
            </div>
            <div style="background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius);padding:12px">
                <div class="stat-label">Kinder-Approved</div>
                <div class="stat-value" style="font-size:20px">${{kinderStr}}</div>
                <div style="font-size:10px;color:var(--muted);margin-top:3px">${{kinderPlaces ? kinderPlaces.toLocaleString() + ' places' : ''}}</div>
            </div>
            <div style="background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius);padding:12px">
                <div class="stat-label">Unemployment</div>
                <div class="stat-value" style="font-size:20px;color:var(--muted)">—</div>
                <div style="font-size:10px;color:var(--muted);margin-top:3px">data pending</div>
            </div>
        </div>

        <!-- Top row: 3 small charts -->
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-bottom:20px">
            <div>
                <div style="font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-bottom:6px">Median Income (Annual)</div>
                <canvas id="chart-catch-income" height="100"></canvas>
            </div>
            <div>
                <div style="font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-bottom:6px">Under-5 Population</div>
                <canvas id="chart-catch-pop" height="100"></canvas>
            </div>
            <div>
                <div style="font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-bottom:6px">Centre Count</div>
                <canvas id="chart-catch-centres" height="100"></canvas>
            </div>
        </div>

        <!-- Large combined chart: Licensed Places + Supply Ratio -->
        <div id="combined-chart-wrapper" style="margin-bottom:24px">
            <div style="font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-bottom:6px">
                Licensed Places (left) &amp; Supply Ratio (right) &nbsp;—&nbsp;
                ▲ centre entry &nbsp; ▼ exit &nbsp; hover annotation for centre names
            </div>
            <canvas id="chart-catch-combined" height="160"></canvas>
            <div id="catch-event-tooltip" style="display:none;position:fixed;background:var(--surface);border:1px solid var(--accent2);border-radius:6px;padding:10px 14px;font-size:11px;color:var(--text);pointer-events:none;z-index:200;max-width:300px;box-shadow:0 4px 20px rgba(0,0,0,0.5)"></div>
            <div style="margin-top:8px;padding:8px 12px;background:var(--surface2);border-radius:6px;font-size:11px;color:var(--muted);line-height:1.5">
                <strong style="color:var(--text)">Note:</strong> A rising supply ratio indicates <em>increasing competition pressure</em>, not opportunity.
                Thresholds: &lt;0.55x balanced · 0.55–1.0x supplied · &gt;1.0x oversupplied
            </div>
        </div>

        <!-- Analytics: 3-column grid -->
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-bottom:24px">
            <!-- NQS Quality -->
            <div style="background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius);padding:16px">
                <div style="font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-bottom:12px">NQS Quality — All ${{sa2.total_centres || ''}} Centres</div>
                ${{nqsHtml}}
            </div>
            <!-- Centre Size Profile -->
            <div style="background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius);padding:16px">
                <div style="font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-bottom:12px">Centre Size Profile</div>
                ${{spHtml}}
                ${{sp && sa2.total_licensed_places ? '<div style="font-size:11px;color:var(--muted);margin-top:10px">Total: ' + sa2.total_licensed_places.toLocaleString() + ' licensed places across ' + sa2.total_centres + ' centres</div>' : ''}}
            </div>
            <!-- CCS Pricing Insight -->
            <div style="background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius);padding:16px">
                <div style="font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-bottom:12px">Fee &amp; Subsidy Dynamics</div>
                ${{ccsHtml}}
                <div style="font-size:10px;color:var(--muted);margin-top:10px;font-style:italic">Actual daily fees: Phase 2 (CareforKids data)</div>
            </div>
        </div>

        <!-- Supply Landscape -->
        <div style="margin-bottom:24px;background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius);padding:16px">
            <div style="font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-bottom:10px">Supply Landscape</div>
            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px">
                <div><div style="font-size:11px;color:var(--muted)">Total centres</div><div style="font-size:18px;font-weight:600;margin-top:2px">${{sa2.total_centres || 'n/a'}}</div></div>
                <div><div style="font-size:11px;color:var(--muted)">Licensed places</div><div style="font-size:18px;font-weight:600;margin-top:2px">${{sa2.total_licensed_places ? sa2.total_licensed_places.toLocaleString() : 'n/a'}}</div></div>
                <div><div style="font-size:11px;color:var(--muted)">NFP</div><div style="font-size:15px;font-weight:600;margin-top:2px">${{nfpStr}}</div></div>
                <div>
                    <div style="font-size:11px;color:var(--muted)">Kinder</div>
                    <div style="font-size:15px;font-weight:600;margin-top:2px">${{kinderCount}} centres · ${{kinderPlaces}} places</div>
                    <div style="font-size:10px;color:var(--muted);margin-top:2px;font-style:italic">Name-based detection — ACECQA flags may undercount</div>
                </div>
            </div>
        </div>

        <!-- Target Services -->
        ${{targetServices.length > 0 ? `
        <div>
            <div style="font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-bottom:10px">
                Target Services in this SA2 (${{targetServices.length}}) — hover to highlight on chart
            </div>
            ${{targetRows}}
        </div>` : ''}}
    </div>`;
}}

// Highlight chart event lines when hovering service cards
var _highlightedService = null;

function highlightEvent(svcName, on, cardIdx) {{
    _highlightedService = on ? svcName : null;
    const card = document.getElementById('svc-card-' + cardIdx);
    if (card) card.style.borderColor = on ? 'var(--accent2)' : 'transparent';
    Object.values(catchmentChartInstances).forEach(c => {{ try {{ c.update('none'); }} catch(e) {{}} }});
}}
function highlightEventByIdx(cardIdx, on) {{
    const card = document.getElementById('svc-card-' + cardIdx);
    const svcName = card ? card.dataset.svcname : '';
    highlightEvent(svcName, on, cardIdx);
}}

// ── Sticky chart: fixes combined chart to top of viewport when scrolled past ──
(function() {{
    var _stickyActive = false;
    var _chartPlaceholder = null;

    function updateStickyChart() {{
        const wrapper = document.getElementById('combined-chart-wrapper');
        if (!wrapper) return;
        const panel = document.getElementById('panel-catchment');
        if (!panel || !panel.classList.contains('active')) return;

        const wrapperTop = wrapper.getBoundingClientRect().top;

        if (!_stickyActive && wrapperTop < -10) {{
            // Chart has scrolled above viewport — make it sticky
            const h = wrapper.offsetHeight;
            // Insert placeholder to preserve layout space
            if (!_chartPlaceholder) {{
                _chartPlaceholder = document.createElement('div');
                _chartPlaceholder.id = 'chart-sticky-placeholder';
                wrapper.parentNode.insertBefore(_chartPlaceholder, wrapper);
            }}
            _chartPlaceholder.style.height = h + 'px';
            _chartPlaceholder.style.display = 'block';

            wrapper.style.position = 'fixed';
            wrapper.style.top = '60px';
            wrapper.style.left = '50%';
            wrapper.style.transform = 'translateX(-50%)';
            wrapper.style.width = '90%';
            wrapper.style.maxWidth = '1400px';
            wrapper.style.zIndex = '50';
            wrapper.style.background = 'var(--surface)';
            wrapper.style.border = '1px solid var(--accent2)';
            wrapper.style.borderRadius = '0 0 var(--radius) var(--radius)';
            wrapper.style.padding = '12px 24px';
            wrapper.style.maxHeight = '300px';
            wrapper.style.boxShadow = '0 8px 32px rgba(0,0,0,0.6)';
            _stickyActive = true;

            // Resize charts to fit sticky height
            Object.values(catchmentChartInstances).forEach(c => {{
                try {{ c.resize(); }} catch(e) {{}}
            }});

        }} else if (_stickyActive) {{
            // Use placeholder position to decide when to release
            const ph = document.getElementById('chart-sticky-placeholder');
            const phTop = ph ? ph.getBoundingClientRect().top : wrapperTop;
            if (phTop >= -10) {{
                // Scrolled back up — restore normal position
                wrapper.style.position = '';
                wrapper.style.top = '';
                wrapper.style.left = '';
                wrapper.style.right = '';
                wrapper.style.transform = '';
                wrapper.style.width = '';
                wrapper.style.maxWidth = '';
                wrapper.style.zIndex = '';
                wrapper.style.background = '';
                wrapper.style.border = '';
                wrapper.style.borderRadius = '';
                wrapper.style.padding = '';
                wrapper.style.maxHeight = '';
                wrapper.style.boxShadow = '';
                if (_chartPlaceholder) {{
                    _chartPlaceholder.style.display = 'none';
                }}
                _stickyActive = false;

                Object.values(catchmentChartInstances).forEach(c => {{ try {{ c.resize(); }} catch(e) {{}} }});
            }}
        }}
    }}

    window.addEventListener('scroll', updateStickyChart, {{ passive: true }});
}})();

// Destroy previous catchment charts before rebuilding
var catchmentChartInstances = {{}};

function buildCatchmentCharts(sa2) {{
    Object.values(catchmentChartInstances).forEach(c => {{ try {{ c.destroy(); }} catch(e) {{}} }});
    catchmentChartInstances = {{}};

    const hist = sa2HistoryData[sa2.sa2_code] || null;
    const hasHist = hist && hist.quarters && hist.quarters.length > 0;

    if (!hasHist) {{
        ['chart-catch-income','chart-catch-pop','chart-catch-centres','chart-catch-combined'].forEach(id => {{
            const el = document.getElementById(id);
            if (el) el.parentElement.innerHTML = '<div style="color:var(--muted);font-size:11px;padding:16px 0">Run build_sa2_history.py to enable trend charts</div>';
        }});
        return;
    }}

    const qs = hist.quarters;

    // ── Shared opts ──
    function makeOpts(yLabel, extra) {{
        return {{
            responsive: true, maintainAspectRatio: true, spanGaps: true,
            interaction: {{ mode: 'index', intersect: false }},
            plugins: {{
                legend: {{ display: true, labels: {{ color: '#8890a8', font: {{ size: 10 }}, boxWidth: 12 }} }},
                tooltip: {{ backgroundColor: 'rgba(24,28,38,0.95)', titleColor: '#e8eaf0', bodyColor: '#8890a8', borderColor: '#2a2f3f', borderWidth: 1 }}
            }},
            scales: {{
                x: {{ ticks: {{ color: '#8890a8', font: {{ size: 9 }}, maxTicksLimit: 8 }}, grid: {{ color: 'rgba(255,255,255,0.04)' }} }},
                y: {{ ticks: {{ color: '#8890a8', font: {{ size: 9 }} }}, grid: {{ color: 'rgba(255,255,255,0.04)' }},
                      title: {{ display: !!yLabel, text: yLabel||'', color: '#8890a8', font: {{ size: 9 }} }} }},
                ...(extra || {{}})
            }}
        }};
    }}

    function makeLine(label, data, color, fill, yAxisID) {{
        const ds = {{ label, data, borderColor: color,
                      backgroundColor: fill || 'transparent',
                      fill: !!fill, tension: 0, pointRadius: 0,
                      borderWidth: 2, spanGaps: true }};
        if (yAxisID) ds.yAxisID = yAxisID;
        return ds;
    }}

    function trimNulls(labels, data) {{
        let start = 0;
        while (start < data.length && data[start] == null) start++;
        return {{ labels: labels.slice(start), data: data.slice(start) }};
    }}

    // ── Per-quarter event map (combine multiple events) ──
    const eventMap = {{}};
    (hist.centre_events || []).forEach(e => {{
        if (!eventMap[e.quarter]) eventMap[e.quarter] = {{ new_centres:0, removed_centres:0, places_change:0, new_names:[], removed_names:[] }};
        eventMap[e.quarter].new_centres     += e.new_centres || 0;
        eventMap[e.quarter].removed_centres += e.removed_centres || 0;
        eventMap[e.quarter].places_change   += e.places_change || 0;
        eventMap[e.quarter].new_names        = eventMap[e.quarter].new_names.concat(e.new_names || []);
        eventMap[e.quarter].removed_names    = eventMap[e.quarter].removed_names.concat(e.removed_names || []);
    }});

    // ── Compact event plugin for small charts (tiny ▲▼ tick at bottom) ──
    function makeCompactPlugin(labels) {{
        return {{
            id: 'compactEv_' + Math.random(),
            afterDraw(chart) {{
                const ctx = chart.ctx;
                labels.forEach((q, i) => {{
                    const ev = eventMap[q];
                    if (!ev || (ev.new_centres === 0 && ev.removed_centres === 0)) return;
                    const meta = chart.getDatasetMeta(0);
                    if (!meta?.data[i]) return;
                    const x = meta.data[i].x;
                    const isEntry = ev.new_centres > 0;
                    ctx.save();
                    ctx.strokeStyle = isEntry ? 'rgba(0,201,167,0.35)' : 'rgba(224,92,58,0.35)';
                    ctx.lineWidth = 1; ctx.setLineDash([2,3]);
                    ctx.beginPath();
                    ctx.moveTo(x, chart.chartArea.top);
                    ctx.lineTo(x, chart.chartArea.bottom - 8);
                    ctx.stroke();
                    ctx.fillStyle = isEntry ? 'rgba(0,201,167,0.7)' : 'rgba(224,92,58,0.7)';
                    ctx.font = '9px sans-serif'; ctx.textAlign = 'center';
                    ctx.fillText(isEntry ? '▲' : '▼', x, chart.chartArea.bottom - 2);
                    ctx.restore();
                }});
            }}
        }};
    }}

    // ── Full annotation plugin for combined chart with hover tooltip ──
    function makeFullPlugin(labels) {{
        return {{
            id: 'fullEv',
            afterDraw(chart) {{
                const ctx = chart.ctx;
                labels.forEach((q, i) => {{
                    const ev = eventMap[q];
                    if (!ev || (ev.new_centres === 0 && ev.removed_centres === 0)) return;
                    const meta = chart.getDatasetMeta(0);
                    if (!meta?.data[i]) return;
                    const x = meta.data[i].x;
                    const top = chart.chartArea.top;
                    const bot = chart.chartArea.bottom;
                    const isEntry = ev.new_centres > 0;
                    const isHigh = _highlightedService &&
                        (ev.new_names || []).concat(ev.removed_names || [])
                        .some(n => n === _highlightedService);
                    const baseAlpha = isHigh ? 0.95 : 0.55;
                    const lineColor = isEntry
                        ? `rgba(0,201,167,${{baseAlpha}})`
                        : `rgba(224,92,58,${{baseAlpha}})`;
                    const textColor = isEntry
                        ? `rgba(0,201,167,${{Math.min(1, baseAlpha + 0.2)}})`
                        : `rgba(224,92,58,${{Math.min(1, baseAlpha + 0.2)}})`;
                    ctx.save();
                    ctx.strokeStyle = lineColor;
                    ctx.lineWidth = isHigh ? 2 : 1;
                    ctx.setLineDash(isHigh ? [] : [3,2]);
                    ctx.beginPath(); ctx.moveTo(x, top); ctx.lineTo(x, bot); ctx.stroke();
                    // Arrow + count + places
                    const arrow = isEntry ? '▲' : '▼';
                    const count = isEntry ? ev.new_centres : ev.removed_centres;
                    const plSign = ev.places_change >= 0 ? '+' : '';
                    ctx.fillStyle = textColor;
                    ctx.font = 'bold 11px monospace'; ctx.textAlign = 'center';
                    ctx.fillText(arrow + count, x, top + 13);
                    ctx.font = '9px monospace';
                    ctx.fillText(plSign + ev.places_change + 'pl', x, top + 24);
                    ctx.restore();
                }});
            }},
            // Show tooltip on mousemove
            afterEvent(chart, args) {{
                const e = args.event;
                if (e.type !== 'mousemove' && e.type !== 'mouseout') return;
                const tooltip = document.getElementById('catch-event-tooltip');
                if (!tooltip) return;
                if (e.type === 'mouseout') {{ tooltip.style.display = 'none'; return; }}
                const ca = chart.chartArea;
                if (e.x < ca.left || e.x > ca.right) {{ tooltip.style.display = 'none'; return; }}
                // Find nearest event quarter
                let best = null, bestDist = 20;
                labels.forEach((q, i) => {{
                    const ev = eventMap[q];
                    if (!ev || (ev.new_centres === 0 && ev.removed_centres === 0)) return;
                    const meta = chart.getDatasetMeta(0);
                    if (!meta?.data[i]) return;
                    const dist = Math.abs(meta.data[i].x - e.x);
                    if (dist < bestDist) {{ bestDist = dist; best = {{ q, ev }}; }}
                }});
                if (!best) {{ tooltip.style.display = 'none'; return; }}
                const ev = best.ev;
                let html = `<div style="font-weight:600;color:var(--accent2);margin-bottom:6px">${{best.q}}</div>`;
                if (ev.new_names && ev.new_names.length > 0) {{
                    html += `<div style="color:var(--accent2);font-size:10px;margin-bottom:3px">▲ Entered (${{ev.new_centres}})</div>`;
                    ev.new_names.forEach(n => {{ html += `<div style="color:var(--text);padding-left:8px">${{n}}</div>`; }});
                }}
                if (ev.removed_names && ev.removed_names.length > 0) {{
                    html += `<div style="color:var(--hot);font-size:10px;margin-top:4px;margin-bottom:3px">▼ Exited (${{ev.removed_centres}})</div>`;
                    ev.removed_names.forEach(n => {{ html += `<div style="color:var(--muted);padding-left:8px">${{n}}</div>`; }});
                }}
                tooltip.innerHTML = html;
                tooltip.style.display = 'block';
                // Position tooltip away from data
                const canvasRect = chart.canvas.getBoundingClientRect();
                const tipX = e.x + ca.left + 10;
                tooltip.style.left = (canvasRect.left + window.scrollX + tipX) + 'px';
                tooltip.style.top  = (canvasRect.top  + window.scrollY + ca.top + 10) + 'px';
            }}
        }};
    }}

    // ── Chart 1 (small): Median Income ──
    const incEl = document.getElementById('chart-catch-income');
    if (incEl) {{
        const incData = qs.map((q, i) => hist.income?.[i] ?? null);
        if (incData.some(v => v != null)) {{
            catchmentChartInstances['income'] = new Chart(incEl, {{
                type: 'line', options: makeOpts('$ Annual'),
                plugins: [makeCompactPlugin(qs)],
                data: {{ labels: qs, datasets: [{{
                    label: 'Median Income', data: incData,
                    borderColor: '#d4890a', backgroundColor: 'transparent',
                    fill: false, tension: 0, pointRadius: 3,
                    pointBackgroundColor: '#d4890a', borderWidth: 2, spanGaps: true
                }}] }}
            }});
        }} else {{
            incEl.parentElement.innerHTML = '<div style="color:var(--muted);font-size:11px;padding:16px 0">Income data unavailable</div>';
        }}
    }}

    // ── Chart 2 (small): Under-5 Population ──
    const popEl = document.getElementById('chart-catch-pop');
    if (popEl) {{
        const t = trimNulls(qs, hist.pop_0_4);
        catchmentChartInstances['pop'] = new Chart(popEl, {{
            type: 'line', options: makeOpts('Children'),
            plugins: [makeCompactPlugin(t.labels)],
            data: {{ labels: t.labels, datasets: [makeLine('Under-5 Pop', t.data, '#00c9a7', 'rgba(0,201,167,0.08)')] }}
        }});
    }}

    // ── Chart 3 (small): Centre Count ──
    const centresEl = document.getElementById('chart-catch-centres');
    if (centresEl) {{
        const t = trimNulls(qs, hist.services);
        catchmentChartInstances['centres'] = new Chart(centresEl, {{
            type: 'line', options: makeOpts('Centres'),
            plugins: [makeCompactPlugin(t.labels)],
            data: {{ labels: t.labels, datasets: [makeLine('Centres', t.data, '#e05c3a', 'rgba(224,92,58,0.08)')] }}
        }});
    }}

    // ── Large combined chart: Licensed Places + Supply Ratio (dual Y) ──
    // Supply ratio recalculated using sa2.pop_0_4 (same source as stat card)
    // Back-calculates historical SA2 pop using CAGR for each quarter
    const combEl = document.getElementById('chart-catch-combined');
    if (combEl) {{
        const tPlaces = trimNulls(qs, hist.places);
        // Recalculate supply ratio using correct SA2 population
        const currentPop  = sa2.pop_0_4 || 0;
        const cagr        = sa2.pop_0_4_cagr != null ? sa2.pop_0_4_cagr / 100 : 0;
        const currentYear = new Date().getFullYear() + (new Date().getMonth() >= 9 ? 0.75 : 0.25);
        const correctedRatio = tPlaces.labels.map((q, i) => {{
            const places = tPlaces.data[i];
            if (places == null) return null;
            // Parse quarter year fraction
            const parts = q.split(' ');
            const qn = parseInt(parts[0].replace('Q',''));
            const yr = parseInt(parts[1]);
            const fracYr = yr + [0,0.25,0.5,0.75][qn-1];
            const yearsBack = currentYear - fracYr;
            const histPop = currentPop > 0 && cagr !== 0
                ? currentPop / Math.pow(1 + cagr, yearsBack)
                : currentPop;
            return histPop > 0 ? +(places / histPop).toFixed(3) : null;
        }});

        // Align labels
        const tRatio    = trimNulls(tPlaces.labels, correctedRatio);
        const allLabels = tPlaces.labels;
        const ratioAl   = allLabels.map((q, i) => correctedRatio[i] != null ? correctedRatio[i] : null);

        const combOpts = makeOpts('');
        combOpts.scales.y  = {{ position: 'left',  ticks: {{ color: '#3d7eff', font: {{ size: 9 }} }}, grid: {{ color: 'rgba(255,255,255,0.04)' }}, title: {{ display: true, text: 'Licensed Places', color: '#3d7eff', font: {{ size: 9 }} }} }};
        combOpts.scales.y2 = {{ position: 'right', ticks: {{ color: ctx => {{ const v = ctx.tick.value; return v > 1.0 ? '#e05c3a' : v > 0.55 ? '#d4890a' : '#00c9a7'; }}, font: {{ size: 9 }}, callback: v => v.toFixed(2) + 'x' }}, grid: {{ drawOnChartArea: false }}, title: {{ display: true, text: 'Supply Ratio', color: '#d4890a', font: {{ size: 9 }} }} }};

        catchmentChartInstances['combined'] = new Chart(combEl, {{
            type: 'line',
            options: combOpts,
            plugins: [makeFullPlugin(allLabels)],
            data: {{ labels: allLabels, datasets: [
                {{ label: 'Licensed Places', data: tPlaces.data,
                   borderColor: '#3d7eff', backgroundColor: 'rgba(61,126,255,0.06)',
                   fill: true, tension: 0, pointRadius: 0, borderWidth: 2,
                   spanGaps: true, yAxisID: 'y' }},
                {{ label: 'Supply Ratio', data: ratioAl,
                   borderColor: '#d4890a', backgroundColor: 'transparent',
                   fill: false, tension: 0, pointRadius: 0, borderWidth: 2,
                   spanGaps: true, yAxisID: 'y2',
                   segment: {{
                       borderColor: ctx => {{
                           const v = ctx.p1.parsed.y;
                           if (v == null) return '#d4890a';
                           return v > 1.0 ? '#e05c3a' : v > 0.55 ? '#d4890a' : '#00c9a7';
                       }}
                   }} }},
            ] }}
        }});
    }}
}}

// Toggle operator details
function toggleOperatorDetails(event, index) {{
    event.stopPropagation();
    const details = document.getElementById('op-details-' + index);
    const row = document.getElementById('op-row-' + index);
    
    if (details && row) {{
        const isExpanded = row.getAttribute('data-expanded') === 'true';
        row.setAttribute('data-expanded', (!isExpanded).toString());
    }}
}}

function searchOperator(operatorName) {{
    // Jump to Panel 2 and search for operator
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.getElementById('panel-operators').classList.add('active');
    document.querySelectorAll('.tab')[1].classList.add('active');
    document.getElementById('op-search').value = operatorName;
    filterOperators();
    window.scrollTo(0, 0);
}}

function jumpToCatchment(suburb, postcode) {{
    // Jump to Panel 3 and search for catchment by suburb or postcode
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.getElementById('panel-catchment').classList.add('active');
    document.querySelectorAll('.tab')[2].classList.add('active');
    const searchTerm = suburb || postcode || '';
    document.getElementById('catch-search').value = searchTerm;
    filterCatchments();
    window.scrollTo(0, 0);
}}

// Enhanced operator row interaction
document.addEventListener('click', function(e) {{
    // Handle operator row clicks for expansion
    if (e.target.closest('.operator-summary')) {{
        const row = e.target.closest('.operator-row');
        if (row) {{
            const isExpanded = row.getAttribute('data-expanded') === 'true';
            
            // Collapse all other rows first
            document.querySelectorAll('.operator-row[data-expanded="true"]').forEach(r => {{
                if (r !== row) r.setAttribute('data-expanded', 'false');
            }});
            
            // Toggle current row
            row.setAttribute('data-expanded', (!isExpanded).toString());
        }}
    }}
}});
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
