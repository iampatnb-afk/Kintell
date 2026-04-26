"""
centre_page.py — Phase 2 backend helper for centre.html
Version: v2 (2026-04-26)

Provides get_centre_payload(service_id) -> dict
Returns full single-centre detail: service + entity + group + brand,
with OBS/DER/COM treatment matching operator_page.py conventions.

v2 fixes (2026-04-26):
  - aria_plus column stores label strings (e.g. "Major Cities of Australia"),
    not codes. ARIA_LABELS now maps both label-form and code-form to a
    canonical short label, with passthrough for any unmapped value.
  - _parse_date() now recognises DD/MM/YYYY (the format
    services.approval_granted_date actually uses).

Read-only. No DB mutations.
"""

import sqlite3
from datetime import datetime, timezone
from typing import Optional

DB_PATH = "data/kintell.db"

# OBS = observed (raw from source), DER = derived (computed),
# COM = commentary (rule-based text). Same convention as operator_page.py.
TAG_OBS = "OBS"
TAG_DER = "DER"
TAG_COM = "COM"

# Stale-rating threshold (years). Aligned with operator_page.py v5+.
STALE_RATING_YEARS = 2
DUE_SOON_MONTHS = 18

# Ownership-type label map (Decision 9). Same as operator_page.py.
OWNERSHIP_LABELS = {
    "private": "Private (for profit)",
    "nfp": "Not-for-profit",
    "government": "Government",
    "independent_school": "Independent school",
    "catholic_school": "Catholic school",
    "unknown": "Not classified",
}

# ARIA+ remoteness band labels. The aria_plus column stores label strings
# in this DB (e.g. "Major Cities of Australia"), not numeric codes. We
# accept both forms and normalise to a short canonical label.
ARIA_LABELS = {
    # Label-form keys (case-insensitive match below)
    "major cities of australia": "Major city",
    "inner regional australia": "Inner regional",
    "outer regional australia": "Outer regional",
    "remote australia": "Remote",
    "very remote australia": "Very remote",
    # Code-form keys (kept for backward compatibility)
    "0": "Major city",
    "1": "Inner regional",
    "2": "Outer regional",
    "3": "Remote",
    "4": "Very remote",
}


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _row_to_dict(row) -> Optional[dict]:
    if row is None:
        return None
    return {k: row[k] for k in row.keys()}


def _parse_date(s: Optional[str]) -> Optional[datetime]:
    """Parse YYYY-MM-DD, ISO8601, 'Mon-YYYY', or DD/MM/YYYY.

    services.approval_granted_date uses DD/MM/YYYY (e.g. '29/09/2010');
    operator_page.py v5 pattern handled the others.
    """
    if not s:
        return None
    s = str(s).strip()
    for fmt in (
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y",
        "%b-%Y",
        "%B-%Y",
    ):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def _months_since(s: Optional[str]) -> Optional[int]:
    d = _parse_date(s)
    if not d:
        return None
    now = datetime.now()
    return (now.year - d.year) * 12 + (now.month - d.month)


def _compute_inspection_cadence(rating_issued_date: Optional[str],
                                overall_rating: Optional[str]) -> dict:
    """
    DER. Inspection cadence flag derived from rating_issued_date.
    Matches operator_page.py v5: stale at 24 months, due_soon at 18 months.
    """
    months = _months_since(rating_issued_date)
    if months is None:
        return {
            "tag": TAG_DER,
            "status": "no_rating",
            "label": "No rating on record",
            "months_since": None,
        }
    if months >= STALE_RATING_YEARS * 12:
        return {
            "tag": TAG_DER,
            "status": "stale",
            "label": f"Stale ({months} months since last rating)",
            "months_since": months,
        }
    if months >= DUE_SOON_MONTHS:
        return {
            "tag": TAG_DER,
            "status": "due_soon",
            "label": f"Due soon ({months} months since last rating)",
            "months_since": months,
        }
    return {
        "tag": TAG_DER,
        "status": "current",
        "label": f"Current ({months} months since last rating)",
        "months_since": months,
    }


def _compute_remoteness(aria_plus: Optional[str]) -> dict:
    """OBS. ARIA+ band lookup. v2: handles both label-form and code-form."""
    if aria_plus is None or aria_plus == "":
        return {"tag": TAG_OBS, "code": None, "label": "Not classified"}
    raw = str(aria_plus).strip()
    key = raw.lower()
    if key in ARIA_LABELS:
        return {"tag": TAG_OBS, "code": raw, "label": ARIA_LABELS[key]}
    # Unknown form: pass through the raw value as label (preserves info,
    # avoids the misleading 'Unknown ARIA+ code' wording for non-code data).
    return {"tag": TAG_OBS, "code": raw, "label": raw}


def _compute_brownfield(approval_granted_date: Optional[str],
                        last_transfer_date: Optional[str]) -> dict:
    """
    DER. Brownfield = a transfer date exists and post-dates the original
    approval date. Greenfield = no transfer, or transfer == approval.
    """
    approval = _parse_date(approval_granted_date)
    transfer = _parse_date(last_transfer_date)
    if transfer and approval and transfer > approval:
        months = _months_since(last_transfer_date)
        return {
            "tag": TAG_DER,
            "status": "brownfield",
            "label": "Brownfield acquisition",
            "transfer_date": last_transfer_date,
            "months_since_transfer": months,
        }
    if transfer and not approval:
        return {
            "tag": TAG_DER,
            "status": "brownfield",
            "label": "Brownfield acquisition (no original approval date)",
            "transfer_date": last_transfer_date,
            "months_since_transfer": _months_since(last_transfer_date),
        }
    return {
        "tag": TAG_DER,
        "status": "greenfield",
        "label": "Greenfield (original operator)",
        "transfer_date": None,
        "months_since_transfer": None,
    }


def _compute_subtype(service_sub_type: Optional[str]) -> dict:
    """OBS. service_sub_type with the Harmony-exclusion handling."""
    if not service_sub_type:
        return {
            "tag": TAG_OBS,
            "code": None,
            "label": "Not classified",
            "excluded_from_workforce": True,
            "exclusion_reason": "service_sub_type is NULL (Harmony exclusion)",
        }
    code = str(service_sub_type).strip().upper()
    label_map = {
        "LDC": "Long Day Care",
        "OSHC": "Outside School Hours Care",
        "PSK": "Preschool / Kindergarten",
        "FDC": "Family Day Care",
    }
    excluded = code in ("FDC",) or code not in label_map
    reason = None
    if code == "FDC":
        reason = "FDC excluded from workforce computation"
    elif code not in label_map:
        reason = f"Unknown subtype: {code}"
    return {
        "tag": TAG_OBS,
        "code": code,
        "label": label_map.get(code, code),
        "excluded_from_workforce": excluded,
        "exclusion_reason": reason,
    }


def _qa_scores(service_row: dict) -> list:
    """OBS. Quality assessment area scores qa1..qa7, only those populated."""
    qa_labels = {
        "qa1": "Educational program and practice",
        "qa2": "Children's health and safety",
        "qa3": "Physical environment",
        "qa4": "Staffing arrangements",
        "qa5": "Relationships with children",
        "qa6": "Collaborative partnerships with families and communities",
        "qa7": "Governance and leadership",
    }
    out = []
    for k, label in qa_labels.items():
        v = service_row.get(k)
        if v is not None and str(v).strip() != "":
            out.append({"key": k, "label": label, "rating": str(v).strip(), "tag": TAG_OBS})
    return out


def get_centre_payload(service_id: int) -> Optional[dict]:
    """
    Top-level entry point. Returns a fully-hydrated centre payload, or
    None if service_id not found.
    """
    conn = _connect()
    try:
        # Single-row fetch for the service joined to entity, group, brand.
        row = conn.execute("""
            SELECT
                s.*,
                e.legal_name             AS entity_legal_name,
                e.abn                    AS entity_abn,
                e.acn                    AS entity_acn,
                e.entity_type            AS entity_type,
                e.is_propco              AS entity_is_propco,
                e.is_opco                AS entity_is_opco,
                e.is_fgc                 AS entity_is_fgc,
                e.is_notional            AS entity_is_notional,
                g.group_id               AS group_id,
                g.canonical_name         AS group_canonical_name,
                g.display_name           AS group_display_name,
                g.ownership_type         AS group_ownership_type,
                g.head_office_state      AS group_head_office_state,
                g.is_listed              AS group_is_listed,
                g.asx_code               AS group_asx_code,
                b.brand_id               AS brand_id,
                b.name                   AS brand_name,
                b.service_name_prefix    AS brand_prefix
            FROM services s
            LEFT JOIN entities e ON s.entity_id = e.entity_id
            LEFT JOIN groups   g ON e.group_id  = g.group_id
            LEFT JOIN brands   b ON s.brand_id  = b.brand_id
            WHERE s.service_id = ?
              AND s.is_active = 1
        """, (service_id,)).fetchone()

        if row is None:
            return None

        r = _row_to_dict(row)

        # --- HEADER block ---
        ownership_raw = r.get("group_ownership_type") or "unknown"
        header = {
            "service_id": r["service_id"],
            "service_name": r.get("service_name"),
            "service_approval_number": r.get("service_approval_number"),
            "provider_approval_number": r.get("provider_approval_number"),
            "address": {
                "address_line": r.get("address_line"),
                "suburb": r.get("suburb"),
                "state": r.get("state"),
                "postcode": r.get("postcode"),
            },
            "lat": r.get("lat"),
            "lng": r.get("lng"),
            "parent_group": {
                "group_id": r.get("group_id"),
                "name": r.get("group_canonical_name") or r.get("group_display_name"),
                "ownership_type_code": ownership_raw,
                "ownership_type_label": OWNERSHIP_LABELS.get(ownership_raw, ownership_raw),
                "head_office_state": r.get("group_head_office_state"),
                "is_listed": bool(r.get("group_is_listed")) if r.get("group_is_listed") is not None else None,
                "asx_code": r.get("group_asx_code"),
            },
            "entity": {
                "entity_id": r.get("entity_id"),
                "legal_name": r.get("entity_legal_name"),
                "abn": r.get("entity_abn"),
                "acn": r.get("entity_acn"),
                "entity_type": r.get("entity_type"),
                "is_propco": bool(r.get("entity_is_propco")) if r.get("entity_is_propco") is not None else False,
                "is_opco": bool(r.get("entity_is_opco")) if r.get("entity_is_opco") is not None else False,
                "is_fgc": bool(r.get("entity_is_fgc")) if r.get("entity_is_fgc") is not None else False,
                "is_notional": bool(r.get("entity_is_notional")) if r.get("entity_is_notional") is not None else False,
            },
            "brand": {
                "brand_id": r.get("brand_id"),
                "name": r.get("brand_name"),
                "prefix": r.get("brand_prefix"),
            } if r.get("brand_id") else None,
        }

        # --- NQS RATING block ---
        cadence = _compute_inspection_cadence(
            r.get("rating_issued_date"),
            r.get("overall_nqs_rating"),
        )
        nqs = {
            "overall_rating": {
                "tag": TAG_OBS,
                "value": r.get("overall_nqs_rating"),
            },
            "rating_issued_date": {
                "tag": TAG_OBS,
                "value": r.get("rating_issued_date"),
            },
            "inspection_cadence": cadence,
        }

        # --- PLACES & SUBTYPE block ---
        subtype = _compute_subtype(r.get("service_sub_type"))
        places = {
            "approved_places": {
                "tag": TAG_OBS,
                "value": r.get("approved_places"),
            },
            "service_sub_type": subtype,
            "long_day_care_flag": bool(r.get("long_day_care")) if r.get("long_day_care") is not None else None,
            "kinder_approved": {
                "tag": TAG_OBS,
                "value": bool(r.get("kinder_approved")) if r.get("kinder_approved") is not None else None,
                "source": r.get("kinder_source"),
            },
            "provider_management_type": {
                "tag": TAG_OBS,
                "value": r.get("provider_management_type"),
            },
        }

        # --- CATCHMENT block (SEIFA + ARIA) ---
        catchment = {
            "seifa_decile": {
                "tag": TAG_OBS,
                "value": r.get("seifa_decile"),
            },
            "remoteness": _compute_remoteness(r.get("aria_plus")),
            "sa2": {
                "code": r.get("sa2_code"),
                "name": r.get("sa2_name"),
            },
            "service_catchment_cache": {
                "tag": TAG_DER,
                "status": "pending",
                "note": "Catchment cache not yet populated (Tier 3 ingest).",
            },
        }

        # --- QA SCORES block ---
        qa_scores = _qa_scores(r)

        # --- BROWNFIELD / TENURE block ---
        tenure = _compute_brownfield(
            r.get("approval_granted_date"),
            r.get("last_transfer_date"),
        )
        tenure["approval_granted_date"] = r.get("approval_granted_date")

        # --- ASSEMBLE ---
        payload = {
            "schema_version": "centre_payload_v1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "header": header,
            "nqs": nqs,
            "places": places,
            "catchment": catchment,
            "qa_scores": qa_scores,
            "tenure": tenure,
            "commentary": _commentary_lines(header, nqs, places, tenure, subtype),
        }
        return payload
    finally:
        conn.close()


def _commentary_lines(header, nqs, places, tenure, subtype) -> list:
    """COM. Rule-based commentary lines. Conservative: skip if data missing."""
    lines = []
    rating = (nqs["overall_rating"]["value"] or "").strip()
    if rating in ("Working Towards NQS", "Significant Improvement Required"):
        lines.append({
            "tag": TAG_COM,
            "severity": "amber" if rating == "Working Towards NQS" else "red",
            "text": f"Centre is currently rated '{rating}'.",
        })
    elif rating in ("Excellent", "Exceeding NQS"):
        lines.append({
            "tag": TAG_COM,
            "severity": "green",
            "text": f"Centre holds a strong NQS rating ('{rating}').",
        })

    cadence = nqs["inspection_cadence"]
    if cadence["status"] == "stale":
        lines.append({
            "tag": TAG_COM,
            "severity": "amber",
            "text": "Rating is stale — re-inspection overdue.",
        })
    elif cadence["status"] == "due_soon":
        lines.append({
            "tag": TAG_COM,
            "severity": "info",
            "text": "Rating approaches its 2-year refresh window.",
        })

    if subtype["excluded_from_workforce"]:
        lines.append({
            "tag": TAG_COM,
            "severity": "info",
            "text": f"Excluded from workforce model: {subtype['exclusion_reason']}",
        })

    if tenure["status"] == "brownfield" and tenure.get("months_since_transfer") is not None:
        if tenure["months_since_transfer"] <= 18:
            lines.append({
                "tag": TAG_COM,
                "severity": "info",
                "text": f"Recent acquisition — {tenure['months_since_transfer']} months under current ownership.",
            })

    return lines


# CLI smoke test
if __name__ == "__main__":
    import json
    import sys
    sid = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    payload = get_centre_payload(sid)
    if payload is None:
        print(f"No active service with service_id={sid}")
        sys.exit(1)
    print(json.dumps(payload, indent=2, default=str))
