"""
commercial_layer_extract.py — DEC-83 extraction logic.

Pure extraction + persistence for one Starting Blocks `__NEXT_DATA__` payload
into main `data/kintell.db` Commercial Layer tables.

Used by:
- `commercial_layer_load_pilot.py` — one-shot V1 load of pilot's 130 centres into main DB
- (future) `commercial_layer_fetch_refresh.py` — weekly fee / monthly regulatory refreshes

Destination tables (DEC-83 schema, created by `migrate_commercial_layer_schema.py`):
- `service_external_capture` — raw payload provenance (always written)
- `service_fee` — long-format fee history
- `service_regulatory_snapshot` — Starting-Blocks-unique state snapshot
- `service_condition` — persistent regulatory conditions (service + provider levels)
- `service_vacancy` — vacancy snapshots
- `large_provider` + `large_provider_provider_link` — operator-group identity
- `regulatory_events` (pre-existing) — populated for service-level enforcement actions
- `services.large_provider_id` — populated when service is part of a chain

Identity resolution (DEC-83 #4):
- Primary: substr(payload.service.serviceId, 1, 11) = services.service_approval_number
- For V1 the 1 SAN-less pilot centre (Redfern Occasional CC) gets capture-only
  with service_id=NULL; structured rows skipped. V2 adds fuzzy fallback.

Provider-level enforcement actions and conditions: V1 deferred. Captured in
`service_external_capture.payload_json` (verbatim) but not extracted to
structured rows — pending provider->entity reconciliation work.

Idempotency:
- service_external_capture: UNIQUE (service_id, source, payload_sha256) — re-runs skip
- service_fee: PK includes (service_id, age_band, session_type, as_of_date, source) —
  re-runs INSERT OR REPLACE
- service_regulatory_snapshot: UNIQUE (service_id, snapshot_date, source) — re-runs skip
- service_condition: PK (condition_id, level, source) — re-runs UPDATE last_observed_at
- service_vacancy: UNIQUE (service_id, age_band, observed_at, source) — append-only
- large_provider: PK large_provider_id — re-runs UPDATE last_observed_at
- large_provider_provider_link: PK includes source — re-runs UPDATE last_observed_at
- regulatory_events: dedupe at extract time on (subject_type, subject_id, event_type, event_date, detail-prefix)
"""

import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from typing import Any

EXTRACTOR_VERSION = "v1.0"

# ---------------------------------------------------------------------------
# Code mappings (Starting Blocks → main DB)
# ---------------------------------------------------------------------------

AGE_GROUP_MAP = {
    "0012MN": "0-12m",
    "1324MN": "13-24m",
    "2535MN": "25-35m",
    "36MNPR": "36m-preschool",
    "OVPRAG": "school-age",
}

SESSION_TYPE_MAP = {
    "FULLDY": "full_day",
    "HALFDY": "half_day",
    "BEFSCH": "before_school",
    "AFTSCH": "after_school",
    "HOURLY": "hourly",
    "SESSON": "session",
    "WEEKLY": "weekly",
    "DAILY":  "daily",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def normalise_iso_date(s: Any) -> str | None:
    if s is None or s == "":
        return None
    s = str(s).strip()
    if "T" in s:
        return s.split("T")[0]
    return s[:10] if len(s) >= 10 else s


def normalise_mmyyyy_to_yyyy_mm(s: Any) -> str | None:
    """LastVisitDateCalc is 'MM/YYYY'. Return 'YYYY-MM' or None."""
    if s is None or s == "":
        return None
    s = str(s).strip()
    if "/" in s and len(s) == 7:
        mm, yyyy = s.split("/", 1)
        return f"{yyyy}-{mm.zfill(2)}"
    return s


def empty_to_none(v: Any) -> Any:
    if v is None or (isinstance(v, str) and v.strip() == ""):
        return None
    return v


def map_age_group(code):
    if code is None:
        return None
    return AGE_GROUP_MAP.get(code, f"unknown:{code}")


def map_session_type(code):
    if code is None:
        return None
    return SESSION_TYPE_MAP.get(code, f"unknown:{code}")


def starting_blocks_url(ulid: str, slug: str | None) -> str:
    slug = slug or ""
    return f"https://www.startingblocks.gov.au/find-child-care/{ulid}/{slug}"


def name_to_slug(name: str | None) -> str:
    if not name:
        return ""
    s = re.sub(r"\s+", "-", name.strip())
    s = re.sub(r"[^A-Za-z0-9-]", "", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ---------------------------------------------------------------------------
# Identity resolution (DEC-83 #4)
# ---------------------------------------------------------------------------

def resolve_service_id(conn, source_san: str | None, source_publicid: str | None = None) -> int | None:
    """
    Resolve Starting Blocks payload to main services.service_id.

    Primary: substr(serviceId, 1, 11) = services.service_approval_number
    e.g. 'SE-00012223MQA5ADAAMAAxADcANgAwADQAVAA=' → 'SE-00012223'

    Returns service_id or None. None means an unresolvable centre (V1: 1 known case).
    V2 will add name+suburb+postcode fuzzy fallback.
    """
    if not source_san:
        return None
    short = str(source_san).strip()[:11]
    if not short.startswith("SE-"):
        return None
    row = conn.execute(
        "SELECT service_id FROM services WHERE service_approval_number = ? LIMIT 1",
        (short,),
    ).fetchone()
    return row[0] if row else None


# ---------------------------------------------------------------------------
# Extract: external capture (raw payload provenance)
# ---------------------------------------------------------------------------

def upsert_external_capture(
    conn,
    *,
    service_id: int | None,
    external_id: str,
    source: str,
    source_url: str,
    fetched_at: str,
    http_status: int,
    payload_text: str,
) -> tuple[int, bool]:
    """
    Insert into service_external_capture if (service_id, source, payload_sha256)
    not already present. Returns (fetch_id, is_new_insert).
    """
    sha = hashlib.sha256(payload_text.encode("utf-8")).hexdigest()
    existing = conn.execute(
        "SELECT fetch_id FROM service_external_capture "
        "WHERE service_id IS ? AND source = ? AND payload_sha256 = ? LIMIT 1",
        (service_id, source, sha),
    ).fetchone()
    if existing:
        return existing[0], False
    cur = conn.execute(
        """
        INSERT INTO service_external_capture
            (service_id, external_id, source, source_url,
             fetched_at, http_status, payload_json, payload_sha256, extractor_version)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (service_id, external_id, source, source_url,
         fetched_at, http_status, payload_text, sha, EXTRACTOR_VERSION),
    )
    return cur.lastrowid, True


# ---------------------------------------------------------------------------
# Extract: fees
# ---------------------------------------------------------------------------

def extract_fee_rows(payload: dict, service_id: int, source: str, fetch_id: int, fetched_at: str) -> tuple[list[dict], int]:
    """
    Yields rows for service_fee. Pulls from three Starting Blocks fee arrays:
      1. props.pageProps.service.historicalFees       — older, has fee_type
      2. props.pageProps.historicalFees               — newer
      3. props.pageProps.currentFees                  — snapshot, has inclusions

    Returns (rows, skipped_count).
    """
    pp = payload["props"]["pageProps"]
    rows_by_pk = {}  # dedupe within payload — last write wins
    skipped = 0

    def push(age_code, session_code, rate, date_str, fee_type, inclusions):
        nonlocal skipped
        age_band = map_age_group(age_code)
        session_type = map_session_type(session_code)
        as_of_date = normalise_iso_date(date_str)
        if (age_band is None or session_type is None or
                as_of_date is None or rate is None):
            skipped += 1
            return
        try:
            fee_aud = float(rate)
        except (TypeError, ValueError):
            skipped += 1
            return
        if age_band.startswith("unknown:") or session_type.startswith("unknown:"):
            # Surface the unmapped code rather than silently dropping —
            # invariant check at validate time will flag.
            pass
        pk = (service_id, age_band, session_type, as_of_date, source)
        rows_by_pk[pk] = {
            "service_id":   service_id,
            "age_band":     age_band,
            "session_type": session_type,
            "as_of_date":   as_of_date,
            "source":       source,
            "fee_aud":      fee_aud,
            "fee_type":     empty_to_none(fee_type),
            "inclusions":   empty_to_none(inclusions),
            "fetch_id":     fetch_id,
            "fetched_at":   fetched_at,
        }

    svc = pp.get("service") or {}
    for h in (svc.get("historicalFees") or []):
        push(
            age_code=h.get("age_group"),
            session_code=h.get("session_type"),
            rate=h.get("rate"),
            date_str=h.get("date"),
            fee_type=h.get("type"),
            inclusions=None,
        )

    for h in (pp.get("historicalFees") or []):
        push(
            age_code=h.get("age_group"),
            session_code=h.get("session_type"),
            rate=h.get("rate"),
            date_str=h.get("date"),
            fee_type=None,
            inclusions=None,
        )

    for c in (pp.get("currentFees") or []):
        push(
            age_code=c.get("AgeGroup"),
            session_code=c.get("SessionType"),
            rate=c.get("UsualFeeAmount"),
            date_str=c.get("LastUpdatedFile"),
            fee_type=None,
            inclusions=c.get("InclusionCode"),
        )

    return list(rows_by_pk.values()), skipped


def upsert_fee_rows(conn, rows: list[dict]) -> int:
    if not rows:
        return 0
    conn.executemany(
        """
        INSERT INTO service_fee
            (service_id, age_band, session_type, as_of_date, source,
             fee_aud, fee_type, inclusions, fetch_id, fetched_at)
        VALUES (:service_id, :age_band, :session_type, :as_of_date, :source,
                :fee_aud, :fee_type, :inclusions, :fetch_id, :fetched_at)
        ON CONFLICT(service_id, age_band, session_type, as_of_date, source) DO UPDATE SET
            fee_aud     = excluded.fee_aud,
            fee_type    = COALESCE(excluded.fee_type, service_fee.fee_type),
            inclusions  = COALESCE(excluded.inclusions, service_fee.inclusions),
            fetch_id    = excluded.fetch_id,
            fetched_at  = excluded.fetched_at
        """,
        rows,
    )
    return len(rows)


# ---------------------------------------------------------------------------
# Extract: regulatory snapshot
# ---------------------------------------------------------------------------

def extract_regulatory_snapshot(payload: dict, service_id: int, source: str,
                                snapshot_date: str, fetch_id: int) -> dict:
    pp = payload["props"]["pageProps"]
    svc = pp.get("service") or {}
    prov = pp.get("provider") or {}
    rating = svc.get("rating") or {}
    hours_block = (svc.get("hours") or [])
    hours = (hours_block[0].get("days") if hours_block else None) or {}

    def hour_pair(day_key: str):
        v = hours.get(day_key) or []
        if isinstance(v, list) and len(v) >= 2:
            return empty_to_none(v[0]), empty_to_none(v[1])
        return None, None

    mon_o, mon_c = hour_pair("monday")
    tue_o, tue_c = hour_pair("tuesday")
    wed_o, wed_c = hour_pair("wednesday")
    thu_o, thu_c = hour_pair("thursday")
    fri_o, fri_c = hour_pair("friday")
    sat_o, sat_c = hour_pair("saturday")
    sun_o, sun_c = hour_pair("sunday")

    return {
        "service_id":                          service_id,
        "snapshot_date":                       snapshot_date,
        "source":                              source,
        "ccs_data_received":                   1 if svc.get("CCSDataReceived") else 0,
        "ccs_revoked_by_ea":                   1 if svc.get("ccsRevokedByEA") else 0,
        "is_closed":                           1 if svc.get("isClosed") else 0,
        "temporarily_closed":                  1 if svc.get("temporarilyClosed") else 0,
        "last_regulatory_visit":               normalise_mmyyyy_to_yyyy_mm(svc.get("LastVisitDateCalc")),
        "last_transfer_date_starting_blocks":  normalise_iso_date(svc.get("lastTransferDate")),
        "enforcement_count":                   len(svc.get("enforcementActions") or []),
        "nqs_starting_blocks_prev_overall":    empty_to_none(rating.get("prevOverall")),
        "nqs_starting_blocks_prev_issued":     normalise_iso_date(rating.get("prevIssued")),
        "provider_status":                     empty_to_none(prov.get("status")),
        "provider_approval_date":              normalise_iso_date(prov.get("approvalDate")),
        "provider_ccs_revoked_by_ea":          1 if prov.get("ccsRevokedByEA") else 0,
        "provider_trade_name":                 empty_to_none(prov.get("providerTradeName")),
        "hours_monday_open":    mon_o, "hours_monday_close":    mon_c,
        "hours_tuesday_open":   tue_o, "hours_tuesday_close":   tue_c,
        "hours_wednesday_open": wed_o, "hours_wednesday_close": wed_c,
        "hours_thursday_open":  thu_o, "hours_thursday_close":  thu_c,
        "hours_friday_open":    fri_o, "hours_friday_close":    fri_c,
        "hours_saturday_open":  sat_o, "hours_saturday_close":  sat_c,
        "hours_sunday_open":    sun_o, "hours_sunday_close":    sun_c,
        "website_url":                         empty_to_none(svc.get("website")),
        "phone":                               empty_to_none(svc.get("phone")),
        "email":                               empty_to_none(svc.get("email")),
        "fetch_id":                            fetch_id,
    }


def upsert_regulatory_snapshot(conn, row: dict) -> int:
    """Insert if (service_id, snapshot_date, source) absent; else skip."""
    existing = conn.execute(
        "SELECT snapshot_id FROM service_regulatory_snapshot "
        "WHERE service_id = ? AND snapshot_date = ? AND source = ? LIMIT 1",
        (row["service_id"], row["snapshot_date"], row["source"]),
    ).fetchone()
    if existing:
        return 0
    cols = list(row.keys())
    placeholders = ",".join(f":{k}" for k in cols)
    conn.execute(
        f"INSERT INTO service_regulatory_snapshot ({','.join(cols)}) VALUES ({placeholders})",
        row,
    )
    return 1


# ---------------------------------------------------------------------------
# Extract: conditions
# ---------------------------------------------------------------------------

def extract_condition_rows(payload: dict, service_id: int, source: str, observed_at: str) -> list[dict]:
    pp = payload["props"]["pageProps"]
    svc = pp.get("service") or {}
    prov = pp.get("provider") or {}
    out = []
    for c in (svc.get("conditions") or []):
        cid = c.get("ConditionID")
        text = c.get("ConditionText")
        if not cid or not text:
            continue
        out.append({
            "condition_id":      str(cid),
            "level":             "service",
            "source":            source,
            "service_id":        service_id,
            "condition_text":    str(text),
            "first_observed_at": observed_at,
            "last_observed_at":  observed_at,
            "still_active":      1,
        })
    for c in (prov.get("conditions") or []):
        cid = c.get("ConditionID")
        text = c.get("ConditionText")
        if not cid or not text:
            continue
        out.append({
            "condition_id":      str(cid),
            "level":             "provider",
            "source":            source,
            "service_id":        service_id,  # canonical "first observation" service
            "condition_text":    str(text),
            "first_observed_at": observed_at,
            "last_observed_at":  observed_at,
            "still_active":      1,
        })
    return out


def upsert_condition_rows(conn, rows: list[dict]) -> int:
    if not rows:
        return 0
    conn.executemany(
        """
        INSERT INTO service_condition
            (condition_id, level, source, service_id, condition_text,
             first_observed_at, last_observed_at, still_active)
        VALUES (:condition_id, :level, :source, :service_id, :condition_text,
                :first_observed_at, :last_observed_at, :still_active)
        ON CONFLICT(condition_id, level, source) DO UPDATE SET
            last_observed_at = excluded.last_observed_at,
            condition_text   = excluded.condition_text,
            still_active     = 1
        """,
        rows,
    )
    return len(rows)


# ---------------------------------------------------------------------------
# Extract: enforcement events → regulatory_events (existing scaffold)
# ---------------------------------------------------------------------------

def extract_enforcement_events(payload: dict, service_id: int, source_url: str) -> list[dict]:
    """
    Extract service-level enforcement actions only (V1 — provider-level deferred
    pending provider->entity reconciliation; preserved verbatim in
    service_external_capture.payload_json).

    Returns rows for regulatory_events table:
      - subject_type='service', subject_id=service_id
      - event_type='enforcement_action'
      - event_date=action.date
      - detail = JSON string with full action object {id, action_type, ...}
      - regulator='ACECQA' (national framework)
      - source_url=startingblocks-detail-page-url
    """
    pp = payload["props"]["pageProps"]
    svc = pp.get("service") or {}
    out = []
    for ea in (svc.get("enforcementActions") or []):
        action_id = ea.get("id")
        action_date = normalise_iso_date(ea.get("date"))
        action_type = ea.get("action_type") or ""
        if not action_id or not action_date:
            continue
        detail = json.dumps({
            "action_id":   action_id,
            "action_type": action_type,
            "raw":         ea,  # preserve full payload sub-object
        }, sort_keys=True)
        out.append({
            "subject_type": "service",
            "subject_id":   service_id,
            "event_type":   "enforcement_action",
            "event_date":   action_date,
            "detail":       detail,
            "severity":     None,  # not derivable from Starting Blocks; future work
            "regulator":    "ACECQA",
            "source_url":   source_url,
        })
    return out


def upsert_enforcement_events(conn, rows: list[dict]) -> int:
    """
    regulatory_events has no natural unique key beyond event_id auto-PK.
    Dedupe at extract time on (subject_type, subject_id, event_type, event_date)
    + action_id-in-detail. Idempotent for V1 single-shot load.
    """
    if not rows:
        return 0
    inserted = 0
    for r in rows:
        # Cheap dedupe on (subject_type, subject_id, event_type, event_date) +
        # action_id substring in detail. action_id is JSON-encoded, e.g.:
        #   '"action_id": 508104,'
        action_id_marker = ""
        try:
            d = json.loads(r["detail"])
            action_id_marker = f'"action_id": {d["action_id"]}'
        except Exception:
            pass
        existing = conn.execute(
            """
            SELECT 1 FROM regulatory_events
            WHERE subject_type = ? AND subject_id = ? AND event_type = ?
              AND event_date = ? AND detail LIKE ? LIMIT 1
            """,
            (r["subject_type"], r["subject_id"], r["event_type"], r["event_date"],
             f"%{action_id_marker}%" if action_id_marker else r["detail"]),
        ).fetchone()
        if existing:
            continue
        conn.execute(
            """
            INSERT INTO regulatory_events
                (subject_type, subject_id, event_type, event_date, detail,
                 severity, regulator, source_url, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """,
            (r["subject_type"], r["subject_id"], r["event_type"], r["event_date"],
             r["detail"], r["severity"], r["regulator"], r["source_url"]),
        )
        inserted += 1
    return inserted


# ---------------------------------------------------------------------------
# Extract: vacancies
# ---------------------------------------------------------------------------

def extract_vacancy_rows(payload: dict, service_id: int, source: str,
                        observed_at: str, fetch_id: int) -> list[dict]:
    """
    One row per ageGroup observed. vacancy_status values:
      - 'has_vacancies'           — vacancies[] populated
      - 'no_vacancies_published'  — vacancies[] empty (most common)
    The empty case is meaningful — 'we asked, source did not publish' provenance.
    """
    pp = payload["props"]["pageProps"]
    svc = pp.get("service") or {}
    out = []
    for entry in (svc.get("vacanciesAndFees") or []):
        age_code = entry.get("ageGroup")
        age_band = map_age_group(age_code)
        if age_band is None:
            continue
        vac_list = entry.get("vacancies") or []
        if vac_list:
            status = "has_vacancies"
            detail_json = json.dumps(vac_list, sort_keys=True)
        else:
            status = "no_vacancies_published"
            detail_json = None
        out.append({
            "service_id":         service_id,
            "age_band":           age_band,
            "observed_at":        observed_at,
            "source":             source,
            "vacancy_status":     status,
            "vacancy_detail_json": detail_json,
            "fetch_id":           fetch_id,
        })
    return out


def upsert_vacancy_rows(conn, rows: list[dict]) -> int:
    if not rows:
        return 0
    inserted = 0
    for r in rows:
        existing = conn.execute(
            "SELECT vacancy_id FROM service_vacancy "
            "WHERE service_id = ? AND age_band IS ? AND observed_at = ? AND source = ? LIMIT 1",
            (r["service_id"], r["age_band"], r["observed_at"], r["source"]),
        ).fetchone()
        if existing:
            continue
        conn.execute(
            """
            INSERT INTO service_vacancy
                (service_id, age_band, observed_at, source,
                 vacancy_status, vacancy_detail_json, fetch_id)
            VALUES (:service_id, :age_band, :observed_at, :source,
                    :vacancy_status, :vacancy_detail_json, :fetch_id)
            """,
            r,
        )
        inserted += 1
    return inserted


# ---------------------------------------------------------------------------
# Extract: large provider (operator-group identity)
# ---------------------------------------------------------------------------

def extract_large_provider(payload: dict, source: str, observed_at: str) -> tuple[dict | None, list[dict]]:
    pp = payload["props"]["pageProps"]
    lp = pp.get("largeProvider")
    if not lp:
        return None, []
    lp_id = lp.get("_id")
    name = lp.get("name")
    if not lp_id or not name:
        return None, []
    slug_obj = lp.get("slug") or {}
    slug = slug_obj.get("current") if isinstance(slug_obj, dict) else None

    lp_row = {
        "large_provider_id": str(lp_id),
        "name":              str(name),
        "slug":              slug,
        "source":            source,
        "first_observed_at": observed_at,
        "last_observed_at":  observed_at,
    }

    link_rows = []
    seen_pids = set()
    for prov in (lp.get("providers") or []):
        pid = prov.get("providerId")
        if not pid or pid in seen_pids:
            continue
        seen_pids.add(pid)
        link_rows.append({
            "large_provider_id":             str(lp_id),
            "provider_approval_number":      str(pid),
            "source":                        source,
            "provider_name_at_observation":  empty_to_none(prov.get("name")),
            "first_observed_at":             observed_at,
            "last_observed_at":              observed_at,
        })

    return lp_row, link_rows


def upsert_large_provider(conn, lp_row: dict | None, link_rows: list[dict]) -> tuple[int, int]:
    """
    Returns (lp_inserted_or_updated, link_inserted_or_updated).
    """
    lp_n = 0
    if lp_row is not None:
        conn.execute(
            """
            INSERT INTO large_provider
                (large_provider_id, name, slug, source, first_observed_at, last_observed_at)
            VALUES (:large_provider_id, :name, :slug, :source, :first_observed_at, :last_observed_at)
            ON CONFLICT(large_provider_id) DO UPDATE SET
                name             = excluded.name,
                slug             = COALESCE(excluded.slug, large_provider.slug),
                last_observed_at = excluded.last_observed_at
            """,
            lp_row,
        )
        lp_n = 1
    link_n = 0
    if link_rows:
        conn.executemany(
            """
            INSERT INTO large_provider_provider_link
                (large_provider_id, provider_approval_number, source,
                 provider_name_at_observation, first_observed_at, last_observed_at)
            VALUES (:large_provider_id, :provider_approval_number, :source,
                    :provider_name_at_observation, :first_observed_at, :last_observed_at)
            ON CONFLICT(large_provider_id, provider_approval_number, source) DO UPDATE SET
                provider_name_at_observation = COALESCE(
                    excluded.provider_name_at_observation,
                    large_provider_provider_link.provider_name_at_observation),
                last_observed_at = excluded.last_observed_at
            """,
            link_rows,
        )
        link_n = len(link_rows)
    return lp_n, link_n


def update_service_large_provider_id(conn, service_id: int, large_provider_id: str | None) -> int:
    """Set services.large_provider_id for the resolved service. Returns 1 if changed, 0 if same/unset."""
    if not service_id:
        return 0
    cur_row = conn.execute(
        "SELECT large_provider_id FROM services WHERE service_id = ?",
        (service_id,),
    ).fetchone()
    if cur_row is None:
        return 0
    if cur_row[0] == large_provider_id:
        return 0
    conn.execute(
        "UPDATE services SET large_provider_id = ? WHERE service_id = ?",
        (large_provider_id, service_id),
    )
    return 1


# ---------------------------------------------------------------------------
# Top-level extraction
# ---------------------------------------------------------------------------

def extract_payload(
    conn,
    *,
    payload_text: str,
    source: str,
    fetched_at: str,
    http_status: int = 200,
    source_url_override: str | None = None,
) -> dict:
    """
    Extract one __NEXT_DATA__ payload into all destination tables.

    Returns counts dict: keys are
      service_id, external_id, capture_inserted, fee_rows, fee_skipped,
      regulatory_snapshot_rows, condition_rows, enforcement_events,
      vacancy_rows, large_provider_set, large_provider_links,
      service_large_provider_updated, unresolved (1 if SAN doesn't resolve, else 0)
    """
    payload = json.loads(payload_text)
    pp = payload["props"]["pageProps"]
    svc = pp.get("service") or {}

    external_id = svc.get("publicId") or svc.get("objectID")
    source_san = svc.get("serviceId")
    name = svc.get("name") or ""
    slug = name_to_slug(name)
    if not external_id:
        # malformed payload — abort gracefully
        return {"error": "no external_id in payload", "skipped": True}

    source_url = source_url_override or starting_blocks_url(external_id, slug)
    service_id = resolve_service_id(conn, source_san)
    unresolved = 1 if service_id is None else 0

    # 1. service_external_capture (always written, even when unresolved)
    fetch_id, capture_inserted = upsert_external_capture(
        conn,
        service_id=service_id,
        external_id=external_id,
        source=source,
        source_url=source_url,
        fetched_at=fetched_at,
        http_status=http_status,
        payload_text=payload_text,
    )

    counts = {
        "service_id": service_id,
        "external_id": external_id,
        "capture_inserted": int(capture_inserted),
        "fee_rows": 0,
        "fee_skipped": 0,
        "regulatory_snapshot_rows": 0,
        "condition_rows": 0,
        "enforcement_events": 0,
        "vacancy_rows": 0,
        "large_provider_set": 0,
        "large_provider_links": 0,
        "service_large_provider_updated": 0,
        "unresolved": unresolved,
    }

    if service_id is None:
        # Capture-only: structured rows skipped. V2 reconciliation will resolve later.
        return counts

    # 2. service_fee
    fee_rows, fee_skipped = extract_fee_rows(payload, service_id, source, fetch_id, fetched_at)
    counts["fee_rows"] = upsert_fee_rows(conn, fee_rows)
    counts["fee_skipped"] = fee_skipped

    # 3. service_regulatory_snapshot
    snap_date = normalise_iso_date(fetched_at) or fetched_at[:10]
    snap_row = extract_regulatory_snapshot(payload, service_id, source, snap_date, fetch_id)
    counts["regulatory_snapshot_rows"] = upsert_regulatory_snapshot(conn, snap_row)

    # 4. service_condition
    cond_rows = extract_condition_rows(payload, service_id, source, fetched_at)
    counts["condition_rows"] = upsert_condition_rows(conn, cond_rows)

    # 5. regulatory_events (enforcement actions)
    enf_rows = extract_enforcement_events(payload, service_id, source_url)
    counts["enforcement_events"] = upsert_enforcement_events(conn, enf_rows)

    # 6. service_vacancy
    vac_rows = extract_vacancy_rows(payload, service_id, source, fetched_at, fetch_id)
    counts["vacancy_rows"] = upsert_vacancy_rows(conn, vac_rows)

    # 7. large_provider + link + services.large_provider_id
    lp_row, link_rows = extract_large_provider(payload, source, fetched_at)
    counts["large_provider_set"], counts["large_provider_links"] = upsert_large_provider(conn, lp_row, link_rows)
    if lp_row:
        counts["service_large_provider_updated"] = update_service_large_provider_id(
            conn, service_id, lp_row["large_provider_id"]
        )
    else:
        # No large provider attached — leave services.large_provider_id alone
        pass

    return counts
