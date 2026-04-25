"""
operator_page.py v8

v8 additions:
  - _compute_workforce(): Phase 1 Module 2 backend.
    Computes required_educators per centre by service_sub_type using
    model_assumptions ratios:
      LDC  -> educator_ratio_ldc_blended  (1:6.5)
      OSHC -> educator_ratio_oshc         (1:15)
      PSK  -> educator_ratio_36m_plus     (1:11)
      FDC, NULL, 'Other' -> excluded (different regulatory model or
                                       data-quality exclusion).
    Aggregates to group total. Pulls historical trend from
    group_snapshots when available (12m and 24m deltas; None when
    no historical snapshot exists in the window).
  - _supply_state_lookup(): training_completions read for the
    operator's states of operation. Returns latest year, prior year,
    YoY change, YoY %, and a caveat string for NSW 2024 (NCVER
    flagged as overstated).
  - _fetch_workforce_growth(): defensive group_snapshots reader.
    Auto-discovers required-educator column name; returns empty
    shape when table or column is missing.
  - get_operator_payload() now surfaces a top-level `workforce`
    block. Backwards-compatible: every v7 key is unchanged.
  - No COM trigger fires in v8 (rule deferred to Phase 7 commentary
    engine). Data is exposed; the commentary line is a frontend
    decision in v8 of operator.html.

v7 changes retained:
  - _fetch_assumptions / _assumption_value: model_assumptions reader.
  - _compute_quality reads inspection thresholds + commentary
    threshold from model_assumptions, with module constants as
    fallback defaults.
  - quality block carries due_soon_threshold_months,
    overdue_threshold_years, due_soon_share, commentary_threshold,
    elevated_inspection_exposure.
  - get_operator_payload surfaces a top-level `assumptions` block.

v6 changes retained:
  - Tier 2 columns on services (aria_plus, seifa_decile,
    service_sub_type, provider_management_type, qa1..qa7).
  - _compute_remoteness driven by services.aria_plus.
  - _compute_catchment uses services.seifa_decile directly;
    service_catchment_cache path retained for Tier 3.

v5 changes retained:
  - _parse_date() accepts Mon-YYYY ("Feb 2023") in addition to
    DD/MM/YYYY and YYYY-MM-DD. Maps Mon-YYYY to first of month.
  - STALE_RATING_YEARS = 2 (was 3).
  - quality.due_soon_count - rated >18 months ago.

v4 changes retained:
  - acquisition block uses "brownfield" terminology.
  - acquisition.brownfield_list with suburb/state.

v3 additions retained:
  - quality block, places_timeline, valuation.

v2 fixes retained:
  - DD/MM/YYYY date handling, brand-name column introspection.

Public:
  get_operator_payload(group_id) -> dict

CLI:
  python operator_page.py <group_id>
  python operator_page.py <group_id> --summary
"""

import argparse
import json
import re
import sqlite3
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "data" / "kintell.db"

# Illustrative valuation constants - stabilised-market range per
# Remara Credit Committee Briefing Paper (leasehold going concern).
VALUATION_LOW_PER_PLACE  = 25_000
VALUATION_HIGH_PER_PLACE = 40_000
VALUATION_SOURCE = (
    "Leasehold going concern, stabilised-market range "
    "(Remara Credit Committee Briefing Paper)"
)

# v7: STALE_RATING_YEARS, STALE_RATING_DAYS, and DUE_SOON_DAYS are
# fallback defaults. _compute_quality reads canonical values from
# model_assumptions; if the table is missing or empty, these
# constants keep the card rendering. Single source of truth is the
# DB; this is the safety net.
STALE_RATING_YEARS = 2
STALE_RATING_DAYS  = 365 * STALE_RATING_YEARS
DUE_SOON_DAYS      = int(365 * 1.5)

# Regex for "kindergarten" / "kinder" / "preschool" in service names.
KINDER_PAT = re.compile(r'\b(kinder(garten)?|pre-?school)\b', re.I)

# v8: service_sub_type to model_assumptions key mapping for the
# Workforce card. Subtypes not in the map are excluded from the
# required_educators computation:
#   FDC has a different regulatory model (1 carer per up to 7
#        children, including own); not directly comparable.
#   NULL and 'Other' are data-quality exclusions; revisit when
#        subtype is populated.
SUBTYPE_TO_RATIO_KEY = {
    "LDC":  "educator_ratio_ldc_blended",
    "OSHC": "educator_ratio_oshc",
    "PSK":  "educator_ratio_36m_plus",
}

# v8: if model_assumptions row for a key is missing, these defaults
# keep the card rendering. They mirror the seeded values.
SUBTYPE_RATIO_FALLBACKS = {
    "educator_ratio_ldc_blended": 6.5,
    "educator_ratio_oshc":        15.0,
    "educator_ratio_36m_plus":    11.0,
}


# --- Utilities -----------------------------------------------------

def _connect():
    if not DB_PATH.exists():
        raise RuntimeError(f"Database not found: {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _table_exists(conn, name):
    r = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name = ?", (name,)
    ).fetchone()
    return r is not None


def _columns(conn, table):
    return [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]


def _fetch_assumptions(conn):
    if not _table_exists(conn, "model_assumptions"):
        return {}
    out = {}
    for row in conn.execute(
        """SELECT assumption_key, display_name, value_numeric, value_text,
                  units, description, source, last_changed_at
             FROM model_assumptions
            WHERE is_active = 1"""
    ).fetchall():
        out[row[0]] = {
            "display_name":    row[1],
            "value_numeric":   row[2],
            "value_text":      row[3],
            "units":           row[4],
            "description":     row[5],
            "source":          row[6],
            "last_changed_at": row[7],
        }
    return out


def _assumption_value(assumptions, key, default):
    if not assumptions:
        return default
    entry = assumptions.get(key)
    if not entry:
        return default
    v = entry.get("value_numeric")
    return v if v is not None else default


def _parse_date(s):
    if s is None:
        return None
    s = str(s).strip()
    if not s:
        return None
    head = s[:10]
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(head, fmt).date()
        except ValueError:
            continue
    short = s[:8].strip().rstrip(",").title()
    try:
        return datetime.strptime(short, "%b %Y").date()
    except ValueError:
        pass
    return None


def _brand_name_column(conn):
    if not _table_exists(conn, "brands"):
        return None
    cols = set(_columns(conn, "brands"))
    for candidate in ("canonical_name", "brand_name", "display_name", "name", "label"):
        if candidate in cols:
            return candidate
    return None


# --- Group meta + parent -------------------------------------------

def _fetch_group(conn, group_id):
    row = conn.execute("""
        SELECT g.group_id, g.canonical_name, g.display_name, g.is_active,
               g.is_for_profit, g.is_listed, g.asx_code, g.primary_domain,
               g.head_office_state, g.ownership_type, g.parent_entity_id,
               g.created_at, g.updated_at, g.deactivated_at,
               e.legal_name, e.abn, e.acn, e.entity_type,
               e.registered_state, e.is_notional
          FROM groups g
          LEFT JOIN entities e ON e.entity_id = g.parent_entity_id
         WHERE g.group_id = ?
    """, (group_id,)).fetchone()
    if not row:
        return None
    (gid, canonical, display, is_active, is_fp, is_listed, asx,
     domain, ho_state, ownership, parent_eid, created, updated, deactivated,
     p_name, p_abn, p_acn, p_type, p_state, p_notional) = row
    parent_entity = None
    if parent_eid:
        parent_entity = {
            "entity_id":        parent_eid,
            "legal_name":       p_name,
            "abn":              p_abn,
            "acn":              p_acn,
            "entity_type":      p_type,
            "registered_state": p_state,
            "is_notional":      p_notional,
        }
    return {
        "group_id":          gid,
        "canonical_name":    canonical,
        "display_name":      display,
        "effective_name":    display or canonical,
        "is_active":         is_active,
        "is_for_profit":     is_fp,
        "is_listed":         is_listed,
        "asx_code":          asx,
        "primary_domain":    domain,
        "head_office_state": ho_state,
        "ownership_type":    ownership,
        "parent_entity_id":  parent_eid,
        "parent_entity":     parent_entity,
        "created_at":        created,
        "updated_at":        updated,
        "deactivated_at":    deactivated,
    }


# --- Entities ------------------------------------------------------

def _fetch_entities(conn, group_id, parent_entity_id):
    rows = conn.execute("""
        SELECT e.entity_id, e.legal_name, e.normalised_name,
               e.abn, e.acn, e.entity_type,
               e.registered_state, e.registered_postcode,
               e.incorporation_date,
               e.is_trustee, e.trust_name,
               e.is_propco, e.is_opco, e.is_fgc,
               e.is_notional, e.is_active,
               COUNT(s.service_id) AS services_count,
               COALESCE(SUM(s.approved_places), 0) AS places_count
          FROM entities e
          LEFT JOIN services s
            ON s.entity_id = e.entity_id AND s.is_active = 1
         WHERE e.group_id = ?
         GROUP BY e.entity_id
         ORDER BY services_count DESC, e.legal_name
    """, (group_id,)).fetchall()

    out = []
    for r in rows:
        (eid, legal, norm, abn, acn, etype, reg_state, reg_pc,
         inc_date, trustee, trust, propco, opco, fgc,
         notional, is_active, svc_count, places) = r
        out.append({
            "entity_id":           eid,
            "legal_name":          legal,
            "normalised_name":     norm,
            "abn":                 abn,
            "acn":                 acn,
            "entity_type":         etype,
            "registered_state":    reg_state,
            "registered_postcode": reg_pc,
            "incorporation_date":  inc_date,
            "is_trustee":          trustee,
            "trust_name":          trust,
            "is_propco":           propco,
            "is_opco":              opco,
            "is_fgc":              fgc,
            "is_notional":         notional,
            "is_active":           is_active,
            "is_parent":           (parent_entity_id is not None
                                    and eid == parent_entity_id),
            "services_count":      svc_count,
            "places_count":        places,
        })
    if out and parent_entity_id is None:
        out[0]["is_largest"] = True
        for e in out[1:]:
            e["is_largest"] = False
    else:
        for e in out:
            e["is_largest"] = False
    return out


# --- Services ------------------------------------------------------

def _fetch_services(conn, group_id):
    brand_col = _brand_name_column(conn)
    if brand_col:
        brand_select = f"b.{brand_col} AS brand_name"
        brand_join   = "LEFT JOIN brands b ON b.brand_id = s.brand_id"
    else:
        brand_select = "NULL AS brand_name"
        brand_join   = ""

    sql = f"""
        SELECT s.service_id, s.service_name,
               s.address_line, s.suburb, s.state, s.postcode,
               s.sa2_code, s.sa2_name, s.lat, s.lng,
               s.approved_places,
               s.approval_granted_date, s.last_transfer_date,
               s.overall_nqs_rating, s.rating_issued_date,
               s.kinder_approved, s.kinder_source, s.long_day_care,
               s.provider_approval_number, s.service_approval_number,
               s.is_active,
               s.brand_id, {brand_select},
               e.entity_id, e.legal_name AS entity_legal_name,
               s.aria_plus, s.seifa_decile, s.service_sub_type,
               s.provider_management_type,
               s.qa1, s.qa2, s.qa3, s.qa4, s.qa5, s.qa6, s.qa7
          FROM services s
          JOIN entities e ON e.entity_id = s.entity_id
          {brand_join}
         WHERE e.group_id = ?
         ORDER BY s.service_name
    """
    try:
        rows = conn.execute(sql, (group_id,)).fetchall()
    except sqlite3.OperationalError:
        rows = conn.execute("""
            SELECT s.service_id, s.service_name,
                   s.address_line, s.suburb, s.state, s.postcode,
                   s.sa2_code, s.sa2_name, s.lat, s.lng,
                   s.approved_places,
                   s.approval_granted_date, s.last_transfer_date,
                   s.overall_nqs_rating, s.rating_issued_date,
                   s.kinder_approved, s.kinder_source, s.long_day_care,
                   s.provider_approval_number, s.service_approval_number,
                   s.is_active,
                   s.brand_id, NULL AS brand_name,
                   e.entity_id, e.legal_name AS entity_legal_name,
                   NULL, NULL, NULL,
                   NULL,
                   NULL, NULL, NULL, NULL, NULL, NULL, NULL
              FROM services s
              JOIN entities e ON e.entity_id = s.entity_id
             WHERE e.group_id = ?
             ORDER BY s.service_name
        """, (group_id,)).fetchall()

    out = []
    for r in rows:
        (sid, name, addr, suburb, state, postcode,
         sa2c, sa2n, lat, lng,
         places, approved, transfer,
         nqs, rating_date,
         kinder, kinder_src, ldc,
         pan, san, is_active,
         bid, brand_name,
         eid, eln,
         aria_plus, seifa_decile, sub_type,
         pmt,
         qa1, qa2, qa3, qa4, qa5, qa6, qa7) = r
        out.append({
            "service_id":               sid,
            "service_name":             name,
            "address_line":             addr,
            "suburb":                   suburb,
            "state":                    state,
            "postcode":                 postcode,
            "sa2_code":                 sa2c,
            "sa2_name":                 sa2n,
            "lat":                      lat,
            "lng":                      lng,
            "approved_places":          places,
            "approval_granted_date":    approved,
            "last_transfer_date":       transfer,
            "nqs":                      nqs,
            "rating_issued_date":       rating_date,
            "kinder_approved":          kinder,
            "kinder_source":            kinder_src,
            "long_day_care":            ldc,
            "provider_approval_number": pan,
            "service_approval_number":  san,
            "is_active":                is_active,
            "brand_id":                 bid,
            "brand_name":               brand_name,
            "entity_id":                eid,
            "entity_legal_name":        eln,
            "aria_plus":                aria_plus,
            "seifa_decile":             seifa_decile,
            "service_sub_type":         sub_type,
            "provider_management_type": pmt,
            "qa1":                      qa1,
            "qa2":                      qa2,
            "qa3":                      qa3,
            "qa4":                      qa4,
            "qa5":                      qa5,
            "qa6":                      qa6,
            "qa7":                      qa7,
        })
    return out


# --- Aggregations --------------------------------------------------

def _compute_scale(entities, services):
    active_entities = [e for e in entities if e.get("is_active")]
    active_services = [s for s in services if s.get("is_active")]
    states = sorted({s["state"] for s in active_services if s.get("state")})
    brands = sorted({s["brand_name"] for s in active_services if s.get("brand_name")})
    return {
        "entities":               len(active_entities),
        "entities_notional":      sum(1 for e in active_entities if e.get("is_notional")),
        "services":               len(active_services),
        "approved_places":        sum((s.get("approved_places") or 0) for s in active_services),
        "states":                 states,
        "state_count":            len(states),
        "brands":                 brands,
        "brand_count":            len(brands),
        "kinder_services":        sum(1 for s in active_services if s.get("kinder_approved")),
        "long_day_care_services": sum(1 for s in active_services if s.get("long_day_care")),
        "propco_entities":        sum(1 for e in active_entities if e.get("is_propco")),
        "opco_entities":          sum(1 for e in active_entities if e.get("is_opco")),
    }


NQS_ORDER = [
    "Excellent",
    "Exceeding NQS",
    "Meeting NQS",
    "Working Towards NQS",
    "Significant Improvement Required",
    "Provisional - Not Yet Assessed",
    "(not rated)",
]


def _compute_nqs_profile(services):
    active = [s for s in services if s.get("is_active")]
    counts = Counter((s.get("nqs") or "(not rated)") for s in active)
    seen = set()
    ordered = []
    for key in NQS_ORDER:
        if key in counts:
            ordered.append({"rating": key, "count": counts[key]})
            seen.add(key)
    for key, n in counts.items():
        if key not in seen:
            ordered.append({"rating": key, "count": n})
    return {"total": len(active), "by_rating": ordered}


def _compute_growth(services):
    now = datetime.now().date()
    windows = [("window_12m", 365), ("window_24m", 730), ("window_36m", 1095)]

    dated = []
    unparseable = 0
    for s in services:
        if not s.get("is_active"):
            continue
        d = _parse_date(s.get("approval_granted_date"))
        if d is None:
            if s.get("approval_granted_date"):
                unparseable += 1
            continue
        dated.append((d, s))

    result = {}
    for label, days in windows:
        cutoff = now - timedelta(days=days)
        in_window = [(d, s) for d, s in dated if d >= cutoff]
        result[label] = {
            "cutoff_date":   cutoff.strftime("%Y-%m-%d"),
            "new_services":  len(in_window),
            "new_places":    sum((s.get("approved_places") or 0)
                                 for _, s in in_window),
        }
    if unparseable:
        result["unparseable_dates"] = unparseable
    return result


def _compute_quality(services, assumptions):
    active = [s for s in services if s.get("is_active")]
    kinder_by_flag = sum(1 for s in active if s.get("kinder_approved"))
    kinder_by_name = sum(
        1 for s in active
        if s.get("service_name") and KINDER_PAT.search(str(s["service_name"]))
    )
    ldc = sum(1 for s in active if s.get("long_day_care"))

    due_soon_months = _assumption_value(
        assumptions, "inspection_due_soon_months", default=18.0
    )
    overdue_years = _assumption_value(
        assumptions, "inspection_overdue_years", default=float(STALE_RATING_YEARS)
    )
    due_soon_days = int(round(due_soon_months * 365.0 / 12.0))
    stale_days    = int(round(overdue_years * 365.0))
    stale_years   = overdue_years

    now = datetime.now().date()
    due_soon_cutoff = now - timedelta(days=due_soon_days)
    stale_cutoff    = now - timedelta(days=stale_days)

    rating_dates = []
    never_rated = 0
    for s in active:
        d = _parse_date(s.get("rating_issued_date"))
        if d is None:
            never_rated += 1
        else:
            rating_dates.append(d)

    most_recent = max(rating_dates).isoformat() if rating_dates else None
    oldest      = min(rating_dates).isoformat() if rating_dates else None
    due_soon    = sum(1 for d in rating_dates if d < due_soon_cutoff)
    stale       = sum(1 for d in rating_dates if d < stale_cutoff)

    com_threshold = _assumption_value(
        assumptions, "commentary_inspection_threshold", default=0.30
    )
    total_active = len(active)
    due_soon_share = (due_soon / total_active) if total_active else 0.0
    elevated_inspection_exposure = due_soon_share > com_threshold

    return {
        "total_services":                    total_active,
        "kinder_by_flag":                    kinder_by_flag,
        "kinder_by_name":                    kinder_by_name,
        "long_day_care":                     ldc,
        "most_recent_rating_date":           most_recent,
        "oldest_rating_date":                oldest,
        "due_soon_count":                    due_soon,
        "stale_rating_count":                stale,
        "never_rated_count":                 never_rated,
        "due_soon_threshold_days":           due_soon_days,
        "stale_threshold_days":              stale_days,
        "stale_threshold_years":             stale_years,
        "due_soon_threshold_months":         due_soon_months,
        "overdue_threshold_years":           overdue_years,
        "due_soon_share":                    round(due_soon_share, 4),
        "commentary_threshold":              com_threshold,
        "elevated_inspection_exposure":      elevated_inspection_exposure,
    }


def _compute_acquisition(services):
    now = datetime.now().date()
    greenfield = 0
    brownfield = 0
    b_12 = b_24 = b_36 = 0
    brownfield_list = []

    for s in services:
        if not s.get("is_active"):
            continue
        ag = _parse_date(s.get("approval_granted_date"))
        lt = _parse_date(s.get("last_transfer_date"))
        if lt is None or ag is None:
            greenfield += 1
            continue
        gap_days = (lt - ag).days
        if gap_days > 30:
            brownfield += 1
            days_since = (now - lt).days
            if days_since <= 365:  b_12 += 1
            if days_since <= 730:  b_24 += 1
            if days_since <= 1095: b_36 += 1
            brownfield_list.append({
                "service_id":         s.get("service_id"),
                "service_name":       s.get("service_name"),
                "suburb":              s.get("suburb"),
                "state":              s.get("state"),
                "last_transfer_date": s.get("last_transfer_date"),
                "approved_places":    s.get("approved_places"),
                "transfer_iso":       lt.isoformat(),
                "brand_name":         s.get("brand_name"),
            })
        else:
            greenfield += 1

    brownfield_list.sort(key=lambda x: x["transfer_iso"], reverse=True)

    return {
        "greenfield_count": greenfield,
        "brownfield_count": brownfield,
        "brownfield_12m":   b_12,
        "brownfield_24m":   b_24,
        "brownfield_36m":   b_36,
        "brownfield_list":  brownfield_list,
    }


ARIA_CANONICAL_BANDS = [
    "Major Cities of Australia",
    "Inner Regional Australia",
    "Outer Regional Australia",
    "Remote Australia",
    "Very Remote Australia",
]


def _compute_remoteness(services):
    active = [s for s in services if s.get("is_active")]
    bands = {label: 0 for label in ARIA_CANONICAL_BANDS}
    unknown_count = 0
    places_by_band = {label: 0 for label in ARIA_CANONICAL_BANDS}
    places_unknown = 0

    for s in active:
        a = s.get("aria_plus")
        p = s.get("approved_places") or 0
        if a in bands:
            bands[a] += 1
            places_by_band[a] += p
        else:
            unknown_count += 1
            places_unknown += p

    populated_n = sum(bands.values())
    if populated_n == 0:
        return {
            "populated": False,
            "scheme":    "ABS Remoteness Structure (5-band)",
            "bands":     {k: 0 for k in ARIA_CANONICAL_BANDS},
            "note": ("ARIA+ not populated on these services. "
                     "Re-run ingest_nqs_snapshot.py to populate, or "
                     "confirm the services exist in the NQS snapshot."),
        }

    return {
        "populated":      True,
        "scheme":         "ABS Remoteness Structure (5-band)",
        "bands":          bands,
        "places_by_band": places_by_band,
        "unknown_count":  unknown_count,
        "places_unknown": places_unknown,
        "total_services": len(active),
        "total_places":   sum((s.get("approved_places") or 0) for s in active),
        "source":         "ACECQA ARIA+ via NQS Data Q4 2025",
    }


def _compute_places_timeline(services):
    events = []
    for s in services:
        if not s.get("is_active"):
            continue
        ag = _parse_date(s.get("approval_granted_date"))
        lt = _parse_date(s.get("last_transfer_date"))
        join_date = None
        kind = "greenfield"
        if lt and ag and (lt - ag).days > 30:
            join_date = lt
            kind = "acquired"
        elif ag:
            join_date = ag
            kind = "greenfield"
        elif lt:
            join_date = lt
            kind = "acquired"
        if join_date is None:
            continue
        events.append({
            "date":         join_date.isoformat(),
            "places":       s.get("approved_places") or 0,
            "type":         kind,
            "service_id":   s.get("service_id"),
            "service_name": s.get("service_name"),
            "state":        s.get("state"),
        })
    events.sort(key=lambda e: e["date"])
    return events


def _compute_valuation(services):
    active = [s for s in services if s.get("is_active")]
    total_places = sum((s.get("approved_places") or 0) for s in active)
    low  = total_places * VALUATION_LOW_PER_PLACE
    high = total_places * VALUATION_HIGH_PER_PLACE
    return {
        "total_places":    total_places,
        "per_place_low":   VALUATION_LOW_PER_PLACE,
        "per_place_high":  VALUATION_HIGH_PER_PLACE,
        "group_low":       low,
        "group_high":      high,
        "source":          VALUATION_SOURCE,
        "note":            ("Illustrative only. Does not account for "
                            "occupancy, lease terms, rent levels, or "
                            "freehold / leasehold mix."),
    }


# --- Catchment -----------------------------------------------------

def _seifa_band(decile):
    if decile is None:
        return None
    try:
        d = int(decile)
    except (TypeError, ValueError):
        return None
    if 1 <= d <= 3:  return "low"
    if 4 <= d <= 6:  return "mid"
    if 7 <= d <= 10: return "high"
    return None


def _compute_catchment(conn, services):
    active = [s for s in services if s.get("is_active")]
    active_sids = [s["service_id"] for s in active]

    decile_hist = {d: 0 for d in range(1, 11)}
    band_counts = {"low": 0, "mid": 0, "high": 0, "unknown": 0}
    band_places = {"low": 0, "mid": 0, "high": 0, "unknown": 0}
    total_w = 0
    w_sum   = 0.0
    seifa_populated_n = 0

    for s in active:
        d = s.get("seifa_decile")
        p = s.get("approved_places") or 0
        band = _seifa_band(d)
        if band is None:
            band_counts["unknown"] += 1
            band_places["unknown"] += p
            continue
        seifa_populated_n += 1
        decile_hist[int(d)] += 1
        band_counts[band] += 1
        band_places[band] += p
        w_sum += float(d) * p
        total_w += p

    seifa_block = {
        "populated":        seifa_populated_n > 0,
        "populated_count":  seifa_populated_n,
        "total_services":   len(active),
        "weighted_decile":  round(w_sum / total_w, 2) if total_w else None,
        "histogram":        decile_hist,
        "band_counts":      band_counts,
        "band_places":      band_places,
        "source":           "ACECQA SEIFA via NQS Data Q4 2025",
    }

    cache_block = _fetch_catchment_cache(conn, active_sids, active)

    return {
        "populated":       seifa_block["populated"] or cache_block.get("populated", False),
        "seifa":           seifa_block,
        "weighted_seifa":  seifa_block["weighted_decile"],
        "weighted_under5": cache_block.get("weighted_under5"),
        "weighted_income": cache_block.get("weighted_income"),
        "supply_bands":    cache_block.get("supply_bands", {
            "balanced": 0, "supplied": 0, "oversupplied": 0,
            "not_cached": len(active_sids),
        }),
        "cache_populated": cache_block.get("populated", False),
    }


def _fetch_catchment_cache(conn, active_sids, services):
    stub = {
        "populated":        False,
        "weighted_seifa":   None,
        "weighted_under5":  None,
        "weighted_income":  None,
        "supply_bands": {
            "balanced":    0,
            "supplied":    0,
            "oversupplied": 0,
            "not_cached":  len(active_sids),
        },
    }
    if not active_sids or not _table_exists(conn, "service_catchment_cache"):
        return stub

    placeholders = ",".join(["?"] * len(active_sids))
    try:
        count = conn.execute(
            f"SELECT COUNT(*) FROM service_catchment_cache "
            f" WHERE service_id IN ({placeholders})",
            active_sids,
        ).fetchone()[0]
    except sqlite3.OperationalError:
        return stub

    if count == 0:
        return stub

    cols = set(_columns(conn, "service_catchment_cache"))
    expected = {"service_id", "seifa_decile", "under5_pop",
                "median_income", "supply_ratio"}
    result = dict(stub)
    result["populated"] = True
    result["rows_found"] = count

    if not expected.issubset(cols):
        return result

    try:
        rows = conn.execute(
            f"SELECT service_id, seifa_decile, under5_pop, "
            f"       median_income, supply_ratio "
            f"  FROM service_catchment_cache "
            f" WHERE service_id IN ({placeholders})",
            active_sids,
        ).fetchall()
    except sqlite3.OperationalError:
        return result

    by_sid_places = {s["service_id"]: (s.get("approved_places") or 0)
                     for s in services if s.get("is_active")}
    total_w = 0
    w_seifa = 0.0
    w_u5    = 0.0
    w_inc   = 0.0
    bands = {"balanced": 0, "supplied": 0, "oversupplied": 0, "not_cached": 0}
    cached = set()
    for sid, seifa, u5, inc, supply in rows:
        w = by_sid_places.get(sid, 0)
        if seifa is not None:
            w_seifa += float(seifa) * w
        if u5 is not None:
            w_u5 += float(u5) * w
        if inc is not None:
            w_inc += float(inc) * w
        if w > 0:
            total_w += w
        cached.add(sid)
        if supply is None:
            pass
        elif supply < 0.55:
            bands["balanced"] += 1
        elif supply <= 1.0:
            bands["supplied"] += 1
        else:
            bands["oversupplied"] += 1
    bands["not_cached"] = len(active_sids) - len(cached)

    if total_w > 0:
        result["weighted_seifa"]  = round(w_seifa / total_w, 2)
        result["weighted_under5"] = round(w_u5    / total_w, 0)
        result["weighted_income"] = round(w_inc   / total_w, 0)
    result["supply_bands"] = bands
    return result


# --- Workforce (v8) ------------------------------------------------

def _supply_state_lookup(conn, state_codes):
    """For each state code in `state_codes`, summarise training_completions
    as latest year, prior year, YoY change, YoY%, and an attached
    caveat string for NSW 2024 (NCVER flagged as overstated).

    Defensive: returns {} if training_completions is missing or no
    state codes are supplied.
    """
    if not state_codes or not _table_exists(conn, "training_completions"):
        return {}
    placeholders = ",".join(["?"] * len(state_codes))
    try:
        rows = conn.execute(
            f"SELECT state_code, year, SUM(completions) AS total "
            f"  FROM training_completions "
            f" WHERE state_code IN ({placeholders}) "
            f" GROUP BY state_code, year",
            list(state_codes),
        ).fetchall()
    except sqlite3.OperationalError:
        return {}

    by_state = {}
    for sc, yr, total in rows:
        by_state.setdefault(sc, {})[int(yr)] = int(total or 0)

    nsw_2024_caveat = (
        "NCVER flagged NSW 2024 completions as overstated; treat as "
        "an upper-bound figure pending the next NCVER release."
    )

    out = {}
    for sc, year_map in by_state.items():
        years = sorted(year_map.keys())
        if not years:
            continue
        latest_year = years[-1]
        prior_year  = years[-2] if len(years) >= 2 else None
        latest = {"year": latest_year, "completions": year_map[latest_year]}
        prior  = ({"year": prior_year, "completions": year_map[prior_year]}
                  if prior_year is not None else None)
        yoy = None
        yoy_pct = None
        if prior:
            yoy = latest["completions"] - prior["completions"]
            if prior["completions"] > 0:
                yoy_pct = round(100.0 * yoy / prior["completions"], 1)
        block = {
            "available_years": years,
            "latest":          latest,
            "prior":           prior,
            "yoy_change":      yoy,
            "yoy_pct":         yoy_pct,
        }
        if sc == "NSW" and latest_year == 2024:
            block["caveat"] = nsw_2024_caveat
        out[sc] = block
    return out


def _fetch_workforce_growth(conn, group_id, current_required):
    """Read group_snapshots for 12m and 24m historical required-educator
    counts. Returns the empty shape if the table is missing, the
    required-educator column doesn't exist, or no historical row
    is found in either window. Auto-discovers the column name across
    common variants.
    """
    empty = {
        "growth_12m":         None,
        "growth_24m":         None,
        "snapshot_12m_date":  None,
        "snapshot_12m_value": None,
        "snapshot_24m_date":  None,
        "snapshot_24m_value": None,
        "table_available":    False,
        "column_used":        None,
    }
    if not _table_exists(conn, "group_snapshots"):
        return empty
    cols = set(_columns(conn, "group_snapshots"))
    candidate = None
    for c in ("required_educators", "required_educators_total",
              "required_educators_group", "workforce_required"):
        if c in cols:
            candidate = c
            break
    if candidate is None or "occurred_at" not in cols or "group_id" not in cols:
        out = dict(empty)
        out["table_available"] = True  # table exists but column is missing
        return out

    cutoff_12 = (datetime.now() - timedelta(days=365)).isoformat(timespec="seconds")
    cutoff_24 = (datetime.now() - timedelta(days=730)).isoformat(timespec="seconds")

    out = dict(empty)
    out["table_available"] = True
    out["column_used"]     = candidate
    try:
        r12 = conn.execute(
            f"SELECT occurred_at, {candidate} FROM group_snapshots "
            f" WHERE group_id = ? AND occurred_at <= ? "
            f"   AND {candidate} IS NOT NULL "
            f" ORDER BY occurred_at DESC LIMIT 1",
            (group_id, cutoff_12),
        ).fetchone()
        if r12:
            out["snapshot_12m_date"]  = r12[0]
            out["snapshot_12m_value"] = r12[1]
            if current_required is not None and r12[1] is not None:
                out["growth_12m"] = current_required - r12[1]
        r24 = conn.execute(
            f"SELECT occurred_at, {candidate} FROM group_snapshots "
            f" WHERE group_id = ? AND occurred_at <= ? "
            f"   AND {candidate} IS NOT NULL "
            f" ORDER BY occurred_at DESC LIMIT 1",
            (group_id, cutoff_24),
        ).fetchone()
        if r24:
            out["snapshot_24m_date"]  = r24[0]
            out["snapshot_24m_value"] = r24[1]
            if current_required is not None and r24[1] is not None:
                out["growth_24m"] = current_required - r24[1]
    except sqlite3.OperationalError:
        return empty
    return out


def _compute_workforce(conn, services, assumptions, group_id):
    """Phase 1 Module 2 main computation.
    Returns:
      required_total            - int (rounded headline)
      required_total_precise    - float (1dp, for tooltip)
      by_subtype                - per-subtype services / places / required
      excluded                  - FDC + Unknown buckets with reasons
      ratios_used               - the actual ratio numbers used per subtype
      growth_12m / growth_24m   - int or None (None when no snapshot)
      growth_snapshots          - the underlying snapshot dates / values
      supply.operator_states    - sorted list of state codes the operator
                                  has active centres in
      supply.primary_state      - state with the largest share of places
      supply.primary_state_place_share
      supply.by_state           - per-state training_completions block
                                  (latest year, prior year, YoY)
      supply.source             - methodology citation
    """
    # 1) Pull ratios (with hardcoded fallbacks)
    ratios_used = {}
    for subtype, key in SUBTYPE_TO_RATIO_KEY.items():
        ratios_used[subtype] = _assumption_value(
            assumptions, key,
            default=SUBTYPE_RATIO_FALLBACKS[key],
        )

    # 2) Per-centre required_educators by subtype, plus state place tally
    by_subtype = {st: {"services": 0, "places": 0,
                       "required_educators": 0.0,
                       "ratio_used": ratios_used.get(st)}
                  for st in SUBTYPE_TO_RATIO_KEY}
    excluded = {
        "FDC": {
            "services": 0, "places": 0,
            "reason": ("FDC operates under a different regulatory model "
                       "(1 educator per up to 7 children, including own). "
                       "Not directly comparable to the educator-on-floor "
                       "headcount derived for centre-based services."),
        },
        "Unknown": {
            "services": 0, "places": 0,
            "reason": ("service_sub_type is NULL or 'Other'. Excluded "
                       "for data quality; revisit when subtype is "
                       "populated upstream."),
        },
    }
    state_places = {}
    required_total = 0.0

    for s in services:
        if not s.get("is_active"):
            continue
        st = s.get("service_sub_type")
        places = s.get("approved_places") or 0
        sc = s.get("state")
        if sc:
            state_places[sc] = state_places.get(sc, 0) + places
        if st in SUBTYPE_TO_RATIO_KEY:
            ratio = ratios_used[st]
            req = (places / ratio) if ratio else 0.0
            by_subtype[st]["services"]            += 1
            by_subtype[st]["places"]              += places
            by_subtype[st]["required_educators"]  += req
            required_total                        += req
        elif st == "FDC":
            excluded["FDC"]["services"] += 1
            excluded["FDC"]["places"]   += places
        else:
            excluded["Unknown"]["services"] += 1
            excluded["Unknown"]["places"]   += places

    for st, blk in by_subtype.items():
        blk["required_educators"] = round(blk["required_educators"], 1)
    required_total_int = int(round(required_total))

    # 3) Historical growth (defensive)
    growth = _fetch_workforce_growth(conn, group_id, required_total_int)

    # 4) Supply lookup
    operator_states = sorted(state_places.keys())
    primary_state = None
    primary_share = None
    if state_places:
        total_places = sum(state_places.values())
        primary_state = max(state_places.items(), key=lambda kv: kv[1])[0]
        if total_places > 0:
            primary_share = round(state_places[primary_state] / total_places, 4)

    supply_by_state = _supply_state_lookup(conn, operator_states)

    return {
        "populated":              True,
        "required_total":         required_total_int,
        "required_total_precise": round(required_total, 1),
        "by_subtype":             by_subtype,
        "excluded":               excluded,
        "ratios_used":            ratios_used,
        "growth_12m":             growth["growth_12m"],
        "growth_24m":             growth["growth_24m"],
        "growth_snapshots": {
            "snapshot_12m_date":  growth["snapshot_12m_date"],
            "snapshot_12m_value": growth["snapshot_12m_value"],
            "snapshot_24m_date":  growth["snapshot_24m_date"],
            "snapshot_24m_value": growth["snapshot_24m_value"],
            "table_available":    growth["table_available"],
            "column_used":        growth["column_used"],
        },
        "supply": {
            "operator_states":           operator_states,
            "primary_state":             primary_state,
            "primary_state_place_share": primary_share,
            "by_state":                  supply_by_state,
            "source": (
                "NCVER VOCSTATS DataBuilder, Total Program Completions, "
                "filtered to ECEC qualification codes (Cert III and "
                "Diploma of Early Childhood Education and Care, current "
                "and superseded versions)."
            ),
        },
    }


# --- Regulatory events / Intelligence notes (defensive) ------------

def _fetch_regulatory_events(conn, group_id, entities, services):
    if not _table_exists(conn, "regulatory_events"):
        return []
    try:
        cols = _columns(conn, "regulatory_events")
        if "subject_type" not in cols or "subject_id" not in cols:
            return []

        entity_ids  = [e["entity_id"]  for e in entities]
        service_ids = [s["service_id"] for s in services]

        where_parts = ["(subject_type='group' AND subject_id = ?)"]
        params = [group_id]
        if entity_ids:
            ep = ",".join(["?"] * len(entity_ids))
            where_parts.append(f"(subject_type='entity' AND subject_id IN ({ep}))")
            params.extend(entity_ids)
        if service_ids:
            sp = ",".join(["?"] * len(service_ids))
            where_parts.append(f"(subject_type='service' AND subject_id IN ({sp}))")
            params.extend(service_ids)

        order_col = "occurred_at" if "occurred_at" in cols else "rowid"
        sql = ("SELECT * FROM regulatory_events WHERE "
               + " OR ".join(where_parts)
               + f" ORDER BY {order_col} DESC LIMIT 200")
        rows = conn.execute(sql, params).fetchall()
        return [dict(zip(cols, r)) for r in rows]
    except sqlite3.OperationalError:
        return []


def _fetch_intelligence_notes(conn, group_id, entities):
    empty = {"group": [], "by_entity": {}}
    if not _table_exists(conn, "intelligence_notes"):
        return empty
    try:
        cols = _columns(conn, "intelligence_notes")
        if "subject_type" not in cols or "subject_id" not in cols:
            return empty
        order_col = "created_at" if "created_at" in cols else "rowid"

        g_rows = conn.execute(
            f"SELECT * FROM intelligence_notes "
            f" WHERE subject_type='group' AND subject_id = ? "
            f" ORDER BY {order_col} DESC LIMIT 100",
            (group_id,),
        ).fetchall()
        group_notes = [dict(zip(cols, r)) for r in g_rows]

        by_entity = {}
        eids = [e["entity_id"] for e in entities]
        if eids:
            ep = ",".join(["?"] * len(eids))
            e_rows = conn.execute(
                f"SELECT * FROM intelligence_notes "
                f" WHERE subject_type='entity' AND subject_id IN ({ep}) "
                f" ORDER BY subject_id, {order_col} DESC",
                eids,
            ).fetchall()
            for r in e_rows:
                d = dict(zip(cols, r))
                sid = d.get("subject_id")
                by_entity.setdefault(sid, []).append(d)
        return {"group": group_notes, "by_entity": by_entity}
    except sqlite3.OperationalError:
        return empty


# --- Public --------------------------------------------------------

def get_operator_payload(group_id):
    conn = _connect()
    try:
        group = _fetch_group(conn, group_id)
        if not group:
            return {"ok": False, "msg": f"Group {group_id} not found"}

        assumptions = _fetch_assumptions(conn)

        entities = _fetch_entities(conn, group_id, group.get("parent_entity_id"))
        services = _fetch_services(conn, group_id)

        return {
            "ok":                   True,
            "group":                group,
            "scale":                _compute_scale(entities, services),
            "entities":             entities,
            "services":             services,
            "nqs_profile":          _compute_nqs_profile(services),
            "quality":              _compute_quality(services, assumptions),
            "growth":               _compute_growth(services),
            "acquisition":          _compute_acquisition(services),
            "remoteness":           _compute_remoteness(services),
            "places_timeline":      _compute_places_timeline(services),
            "valuation":            _compute_valuation(services),
            "catchment":            _compute_catchment(conn, services),
            # v8: Phase 1 Module 2 Workforce.
            "workforce":            _compute_workforce(
                                        conn, services, assumptions, group_id),
            "competitive_exposure": {
                "populated":                   False,
                "oversupplied_places_pct":     None,
                "deteriorating_catchments":    None,
                "recent_competitor_approvals": None,
            },
            "regulatory_events":    _fetch_regulatory_events(
                                        conn, group_id, entities, services),
            "intelligence_notes":   _fetch_intelligence_notes(
                                        conn, group_id, entities),
            "assumptions":          assumptions,
        }
    finally:
        conn.close()


# --- CLI -----------------------------------------------------------

def _cli():
    p = argparse.ArgumentParser(description="Dump operator payload for a group.")
    p.add_argument("group_id", type=int)
    p.add_argument("--summary", action="store_true",
                   help="Show counts/keys only, not full entities/services arrays")
    args = p.parse_args()

    r = get_operator_payload(args.group_id)
    if args.summary and r.get("ok"):
        payload = dict(r)
        payload["entities"] = f"<{len(r['entities'])} items>"
        payload["services"] = f"<{len(r['services'])} items>"
        print(json.dumps(payload, indent=2, default=str))
    else:
        print(json.dumps(r, indent=2, default=str))
    sys.exit(0 if r.get("ok") else 1)


if __name__ == "__main__":
    _cli()
