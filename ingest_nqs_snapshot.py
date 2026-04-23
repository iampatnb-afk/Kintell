"""
ingest_nqs_snapshot.py  v1
────────────────────────────────────────────────────────────────
Tier 2 Phase D — ingest the NQS Data Q4 2025 current-state
snapshot into kintell.db.

What this does
--------------
For every Service Approval Number in the NQS file that matches a
row in services:
  UPDATE services SET
    lat, lng, aria_plus, seifa_decile, service_sub_type,
    provider_management_type, rating_issued_date, overall_nqs_rating,
    qa1..qa7
  WHERE service_approval_number = ?

Then for every group in the DB, derive ownership_type from the
plurality of PMT values across its services (using the mapping
confirmed in Phase B diagnostic):

  Private for profit                              → private
  Private not for profit community managed        → nfp
  Private not for profit other organisations      → nfp
  State/Territory and Local Government managed    → government
  State/Territory government schools              → government
  Independent schools                             → independent_school
  Catholic schools                                → catholic_school
  Other                                           → (unknown / unchanged)

  UPDATE groups SET ownership_type = ? WHERE group_id = ?

What this does NOT touch
------------------------
- entities (all 7,143 rows untouched)
- link_candidates (all merge decisions untouched)
- audit_log rows tagged accept_merge / reject_merge / reverse_merge
  (untouched; this script adds one new 'nqs_ingest' row and that's all)
- brands, portfolios, service_history, snapshots
- Any groups column other than ownership_type
- Services not matched in the NQS file (341 expected unmatched;
  they retain existing values)

Safety
------
- --dry-run prints the full write plan and field-by-field count
  deltas without touching the DB.
- Real run wraps all writes in a single transaction.
- Pre/post invariant check on counts of:
    audit_log rows with action='accept_merge'
    entities total
    groups total
    groups with is_active = 1
  If any changes, ABORT and roll back.
- One audit_log row written (action='nqs_ingest_q4_2025').

CLI
---
  python ingest_nqs_snapshot.py --dry-run   # plan only, no writes
  python ingest_nqs_snapshot.py             # real run

Date format handling
--------------------
The NQS file 'Final Report Sent Date' comes through openpyxl as
datetime.datetime objects (xlsx native dates). We store them in
kintell.db as ISO 'YYYY-MM-DD' strings. operator_page.py v5
_parse_date() already handles ISO, so the downstream computation
just works.
"""

import argparse
import datetime as dt
import json
import sqlite3
import sys
from collections import Counter
from pathlib import Path

import openpyxl

ROOT    = Path(__file__).resolve().parent
DB_PATH = ROOT / "data" / "kintell.db"
XLSX    = ROOT / "abs_data" / "NQS Data Q4 2025.XLSX"

# PMT label → ownership_type mapping, per Phase B decisions.
# Any PMT not in this dict falls through to "unknown" and leaves
# the existing groups.ownership_type value unchanged.
PMT_TO_OWNERSHIP = {
    "Private for profit":                            "private",
    "Private not for profit community managed":      "nfp",
    "Private not for profit other organisations":    "nfp",
    "State/Territory and Local Government managed":  "government",
    "State/Territory government schools":            "government",
    "Independent schools":                           "independent_school",
    "Catholic schools":                              "catholic_school",
    # "Other" intentionally absent → falls through to unknown
}

# Columns we pull from the NQS file. Exact header strings.
NQS_FIELDS = [
    "Service Approval Number",
    "Provider Management Type",
    "Service Sub Type",
    "Final Report Sent Date",
    "Overall Rating",
    "SEIFA",
    "ARIA+",
    "Latitude",
    "Longitude",
    "Quality Area 1",
    "Quality Area 2",
    "Quality Area 3",
    "Quality Area 4",
    "Quality Area 5",
    "Quality Area 6",
    "Quality Area 7",
]


# ─── Readers / parsers ─────────────────────────────────────────

def _to_iso_date(v):
    """
    Final Report Sent Date comes through openpyxl as datetime,
    or sometimes as string. Return ISO 'YYYY-MM-DD', or None.
    """
    if v is None or v == "":
        return None
    if isinstance(v, dt.datetime):
        return v.date().isoformat()
    if isinstance(v, dt.date):
        return v.isoformat()
    s = str(v).strip()
    # Accept 'YYYY-MM-DD 00:00:00' and 'YYYY-MM-DD'
    if len(s) >= 10:
        try:
            return dt.datetime.strptime(s[:10], "%Y-%m-%d").date().isoformat()
        except ValueError:
            pass
    return None


def _to_seifa(v):
    """SEIFA: integer 1..10, or None. '-', 0, '', NULL all → None."""
    if v is None or v == "":
        return None
    try:
        iv = int(v)
        if 1 <= iv <= 10:
            return iv
        return None   # 0 or out-of-range → NULL
    except (TypeError, ValueError):
        return None


def _to_float(v):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _to_text(v):
    if v is None:
        return None
    s = str(v).strip()
    return s if s else None


def read_nqs_records():
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    ws = wb["Approved Services"]
    rows_iter = ws.iter_rows(values_only=True)
    headers = list(next(rows_iter))

    col_ix = {f: (headers.index(f) if f in headers else None)
              for f in NQS_FIELDS}
    missing = [f for f, ix in col_ix.items() if ix is None]
    if missing:
        wb.close()
        raise RuntimeError(f"Missing expected columns: {missing}")

    records = []
    for row in rows_iter:
        sap = row[col_ix["Service Approval Number"]]
        if not sap:
            continue
        rec = {
            "sap":           _to_text(sap),
            "pmt":           _to_text(row[col_ix["Provider Management Type"]]),
            "sub_type":      _to_text(row[col_ix["Service Sub Type"]]),
            "rating_date":   _to_iso_date(row[col_ix["Final Report Sent Date"]]),
            "overall":       _to_text(row[col_ix["Overall Rating"]]),
            "seifa":         _to_seifa(row[col_ix["SEIFA"]]),
            "aria":          _to_text(row[col_ix["ARIA+"]]),
            "lat":           _to_float(row[col_ix["Latitude"]]),
            "lng":           _to_float(row[col_ix["Longitude"]]),
            "qa1":           _to_text(row[col_ix["Quality Area 1"]]),
            "qa2":           _to_text(row[col_ix["Quality Area 2"]]),
            "qa3":           _to_text(row[col_ix["Quality Area 3"]]),
            "qa4":           _to_text(row[col_ix["Quality Area 4"]]),
            "qa5":           _to_text(row[col_ix["Quality Area 5"]]),
            "qa6":           _to_text(row[col_ix["Quality Area 6"]]),
            "qa7":           _to_text(row[col_ix["Quality Area 7"]]),
        }
        records.append(rec)
    wb.close()
    return records


# ─── DB helpers ────────────────────────────────────────────────

def snapshot_invariants(conn):
    """Capture counts we expect to stay exactly the same."""
    return {
        "accept_merge_rows": conn.execute(
            "SELECT COUNT(*) FROM audit_log WHERE action = 'accept_merge'"
        ).fetchone()[0],
        "entities_total":    conn.execute(
            "SELECT COUNT(*) FROM entities"
        ).fetchone()[0],
        "groups_total":      conn.execute(
            "SELECT COUNT(*) FROM groups"
        ).fetchone()[0],
        "groups_active":     conn.execute(
            "SELECT COUNT(*) FROM groups WHERE is_active = 1"
        ).fetchone()[0],
    }


def fetch_db_index(conn):
    """Map service_approval_number → (service_id, entity_id)."""
    rows = conn.execute(
        "SELECT service_approval_number, service_id, entity_id "
        "  FROM services "
        " WHERE service_approval_number IS NOT NULL"
    ).fetchall()
    return {r[0]: (r[1], r[2]) for r in rows}


def fetch_entity_to_group(conn):
    return dict(conn.execute(
        "SELECT entity_id, group_id FROM entities"
    ).fetchall())


def log_audit(conn, summary):
    conn.execute(
        "INSERT INTO audit_log "
        "(actor, action, subject_type, subject_id, "
        " before_json, after_json, reason) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            "system",
            "nqs_ingest_q4_2025",
            "table",
            0,
            None,
            json.dumps(summary, default=str),
            f"Updated {summary['services_updated']} services and "
            f"{summary['groups_ownership_updated']} group ownership_types "
            f"from NQS Data Q4 2025.XLSX",
        ),
    )


# ─── Core ingest ───────────────────────────────────────────────

def ingest(dry_run):
    conn = sqlite3.connect(str(DB_PATH))
    try:
        # Confirm the migration ran
        cols = {r[1] for r in conn.execute("PRAGMA table_info(services)").fetchall()}
        required = {"aria_plus", "seifa_decile", "service_sub_type",
                    "provider_management_type", "qa1", "qa7"}
        missing = required - cols
        if missing:
            print(f"ERROR — services table is missing columns: {sorted(missing)}")
            print("Run migrate_schema_v0_4.py first.")
            return 1

        print("\n── ingest_nqs_snapshot ──")
        print(f"DB:    {DB_PATH}")
        print(f"XLSX:  {XLSX}")

        # Snapshot invariants before we do anything
        inv_before = snapshot_invariants(conn)
        print(f"Pre-flight invariants: {inv_before}")

        # Load file + index DB
        print("\nReading NQS file ...")
        records = read_nqs_records()
        print(f"  Rows with SAP#: {len(records)}")

        db_idx = fetch_db_index(conn)
        ent_to_group = fetch_entity_to_group(conn)
        print(f"  kintell.db services with SAP#: {len(db_idx)}")

        # ── Phase 1: service-level updates ─────────────────────
        matched = []
        unmatched_nqs = []
        for rec in records:
            sap = rec["sap"]
            if sap in db_idx:
                matched.append(rec)
            else:
                unmatched_nqs.append(sap)

        print(f"\nService match summary:")
        print(f"  matched     : {len(matched):>6}")
        print(f"  NQS only    : {len(unmatched_nqs):>6}")
        print(f"  DB only     : {len(db_idx) - len(matched):>6}")

        # Fields we will SET per row: tuple (col, fetcher)
        field_map = [
            ("lat",                       lambda r: r["lat"]),
            ("lng",                       lambda r: r["lng"]),
            ("aria_plus",                 lambda r: r["aria"]),
            ("seifa_decile",              lambda r: r["seifa"]),
            ("service_sub_type",          lambda r: r["sub_type"]),
            ("provider_management_type",  lambda r: r["pmt"]),
            ("rating_issued_date",        lambda r: r["rating_date"]),
            ("overall_nqs_rating",        lambda r: r["overall"]),
            ("qa1",                       lambda r: r["qa1"]),
            ("qa2",                       lambda r: r["qa2"]),
            ("qa3",                       lambda r: r["qa3"]),
            ("qa4",                       lambda r: r["qa4"]),
            ("qa5",                       lambda r: r["qa5"]),
            ("qa6",                       lambda r: r["qa6"]),
            ("qa7",                       lambda r: r["qa7"]),
        ]

        # Count how many non-null values we'll write per column
        per_col_nonnull = Counter()
        for rec in matched:
            for col, fetch in field_map:
                if fetch(rec) is not None:
                    per_col_nonnull[col] += 1

        print(f"\nPer-column non-null values to write (across {len(matched)} matched services):")
        for col, _ in field_map:
            n = per_col_nonnull[col]
            pct = 100.0 * n / len(matched) if matched else 0
            print(f"  {col:28} {n:>6}   ({pct:5.1f}%)")

        # ── Phase 2: group ownership_type derivation ──────────
        # Build: group_id → Counter of PMT values
        group_pmts = {}
        for rec in matched:
            sap = rec["sap"]
            _sid, eid = db_idx[sap]
            gid = ent_to_group.get(eid)
            if gid is None:
                continue
            pmt = rec["pmt"] or "(null)"
            group_pmts.setdefault(gid, Counter())[pmt] += 1

        # Fetch current ownership_type for all affected groups so we can
        # compute deltas, not rewrite everything.
        gids = list(group_pmts.keys())
        current_ownership = {}
        if gids:
            placeholders = ",".join(["?"] * len(gids))
            rows = conn.execute(
                f"SELECT group_id, ownership_type "
                f"  FROM groups WHERE group_id IN ({placeholders})",
                gids,
            ).fetchall()
            current_ownership = dict(rows)

        # Plan per-group updates
        group_updates = []        # [(gid, old_value, new_value)]
        derived_dist = Counter()  # what we'd set
        unchanged = 0
        for gid, cnt in group_pmts.items():
            top_label, _ = cnt.most_common(1)[0]
            new_val = PMT_TO_OWNERSHIP.get(top_label)  # may be None
            cur = current_ownership.get(gid)
            if new_val is None:
                # fall-through: don't overwrite with "unknown"
                derived_dist["(leave as unknown/existing)"] += 1
                continue
            derived_dist[new_val] += 1
            if cur == new_val:
                unchanged += 1
                continue
            group_updates.append((gid, cur, new_val))

        print(f"\nOwnership-type derivation across {len(group_pmts)} groups:")
        for label, n in derived_dist.most_common():
            print(f"  {label:35} {n:>6}")
        print(f"  Already matching target  : {unchanged:>6}")
        print(f"  To change                : {len(group_updates):>6}")

        # Sparrow + Harmony visibility
        for name, gid in [("Sparrow", 1887), ("Harmony", 236)]:
            c = group_pmts.get(gid)
            cur = current_ownership.get(gid)
            top = c.most_common(1)[0] if c else ("(no data)", 0)
            new_val = PMT_TO_OWNERSHIP.get(top[0]) if c else None
            print(f"  {name} (gid {gid}): cur={cur!r} top_pmt={top[0]!r} → new={new_val!r}")

        # ── Dry-run exit point ───────────────────────────────
        if dry_run:
            print("\n--dry-run: no writes. Exiting.")
            print("If these numbers look right, re-run without --dry-run.")
            return 0

        # ── Real run — write in a single transaction ─────────
        print("\nWriting ...")
        conn.execute("BEGIN")
        try:
            # Services update — only overwrite NULLs' targets with non-null
            # source values, AND always overwrite rating_issued_date /
            # overall_nqs_rating (refreshed from authoritative source).
            set_sql = (
                "UPDATE services SET "
                "  lat                      = COALESCE(?, lat), "
                "  lng                      = COALESCE(?, lng), "
                "  aria_plus                = COALESCE(?, aria_plus), "
                "  seifa_decile             = COALESCE(?, seifa_decile), "
                "  service_sub_type         = COALESCE(?, service_sub_type), "
                "  provider_management_type = COALESCE(?, provider_management_type), "
                "  rating_issued_date       = ?, "
                "  overall_nqs_rating       = COALESCE(?, overall_nqs_rating), "
                "  qa1                      = COALESCE(?, qa1), "
                "  qa2                      = COALESCE(?, qa2), "
                "  qa3                      = COALESCE(?, qa3), "
                "  qa4                      = COALESCE(?, qa4), "
                "  qa5                      = COALESCE(?, qa5), "
                "  qa6                      = COALESCE(?, qa6), "
                "  qa7                      = COALESCE(?, qa7), "
                "  updated_at               = datetime('now') "
                "WHERE service_approval_number = ?"
            )
            services_updated = 0
            for rec in matched:
                conn.execute(set_sql, (
                    rec["lat"], rec["lng"], rec["aria"], rec["seifa"],
                    rec["sub_type"], rec["pmt"],
                    rec["rating_date"],          # ALWAYS overwrite
                    rec["overall"],
                    rec["qa1"], rec["qa2"], rec["qa3"], rec["qa4"],
                    rec["qa5"], rec["qa6"], rec["qa7"],
                    rec["sap"],
                ))
                services_updated += 1
            print(f"  services updated: {services_updated}")

            # Groups.ownership_type update
            for gid, _old, new_val in group_updates:
                conn.execute(
                    "UPDATE groups SET ownership_type = ?, "
                    "                  updated_at = datetime('now') "
                    "WHERE group_id = ?",
                    (new_val, gid),
                )
            print(f"  groups ownership_type updated: {len(group_updates)}")

            # Invariant check — must be unchanged
            inv_after = snapshot_invariants(conn)
            if inv_after != inv_before:
                raise RuntimeError(
                    f"Invariant violation — ABORT.\n"
                    f"  Before: {inv_before}\n"
                    f"  After:  {inv_after}"
                )
            print(f"  invariants preserved: {inv_after}")

            # Audit row
            summary = {
                "services_matched":           len(matched),
                "services_updated":           services_updated,
                "services_nqs_only":          len(unmatched_nqs),
                "services_db_only":           len(db_idx) - len(matched),
                "groups_ownership_updated":   len(group_updates),
                "per_col_nonnull":            dict(per_col_nonnull),
                "derived_distribution":       dict(derived_dist),
                "invariants_pre":             inv_before,
                "invariants_post":            inv_after,
                "source_file":                str(XLSX.name),
            }
            log_audit(conn, summary)

            conn.commit()
            print("\n✓ Committed. audit_log row action='nqs_ingest_q4_2025' written.")
            return 0

        except Exception as e:
            conn.rollback()
            print(f"ERROR — rolled back: {e}", file=sys.stderr)
            return 1
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="Ingest NQS Data Q4 2025 into kintell.db.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show plan; write nothing.")
    args = parser.parse_args()
    return ingest(dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
