"""
build_graph.py  (v2)
────────────────────────────────────────────────────────────────
Populates the Kintell ownership graph from the existing pipeline
data sources.

v2 fix: defensive as_str() coercion — some rows in
operators_target_list.json had NaN / non-string values in
string fields (legal_name). v1 crashed on these; v2 coerces.

Inputs:
  - operators_target_list.json       (pre-existing group structure)
  - data/services_snapshot.csv       (all 18k+ services, ACECQA)

Outputs (into data/kintell.db, created by init_db.py):
  - groups, portfolios, entities, services, evidence

Not populated yet (future cycles):
  - brands, service_catchment_cache, *_snapshots, *_financials,
    link_candidates, audit_log, intelligence_notes, people,
    regulatory_events, properties

Idempotent: clears + rebuilds on every run.
Run from: C:\\Users\\Patrick Bell\\remara-agent
"""

import csv
import json
import math
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_PATH        = ROOT / "data" / "kintell.db"
OPERATORS_FILE = ROOT / "operators_target_list.json"
SNAPSHOT_FILE  = ROOT / "data" / "services_snapshot.csv"


def as_str(v):
    """
    Coerce any value to a safe string.
    Returns '' for None, NaN, empty string, or non-coercible values.
    """
    if v is None:
        return ""
    if isinstance(v, float):
        if math.isnan(v):
            return ""
        return str(v)
    try:
        return str(v).strip()
    except Exception:
        return ""


def norm(s):
    return as_str(s).lower()


def slugify(s, suffix):
    base = re.sub(r"[^a-zA-Z0-9]+", "-", norm(s)).strip("-")
    return (base[:100] + f"-{suffix}")[:120]


def safe_int(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def main():
    # Prechecks
    if not DB_PATH.exists():
        print(f"[X] Database not found: {DB_PATH}")
        print("    Run init_db.py first.")
        sys.exit(1)
    for f in [OPERATORS_FILE, SNAPSHOT_FILE]:
        if not f.exists():
            print(f"[X] Input file missing: {f}")
            sys.exit(1)

    # Load sources
    print("Loading operators_target_list.json...")
    with OPERATORS_FILE.open(encoding="utf-8") as f:
        operators = json.load(f)
    if isinstance(operators, dict):
        operators = list(operators.values())
    print(f"  {len(operators)} group records")

    print("Loading services_snapshot.csv...")
    with SNAPSHOT_FILE.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        services_rows = list(reader)
    print(f"  {len(services_rows)} services total in snapshot")

    # Connect
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON")

    # ── Clear graph tables (idempotent full rebuild) ──
    print("\nClearing existing graph data...")
    for tbl in ("evidence", "link_candidates",
                "services", "brands",
                "portfolios", "entities", "groups"):
        conn.execute(f"DELETE FROM {tbl}")
    conn.execute(
        "DELETE FROM sqlite_sequence WHERE name IN "
        "('evidence','link_candidates','services','brands',"
        " 'portfolios','entities','groups')"
    )
    conn.commit()

    # ── 1. Groups ──
    print("\n[1/5] Inserting groups from target list...")
    group_id_by_ix = {}
    skipped_rows = 0
    coerced_names = 0

    for i, rec in enumerate(operators):
        if not isinstance(rec, dict):
            skipped_rows += 1
            continue
        raw_name = rec.get("legal_name")
        name = as_str(raw_name)
        if not name:
            name = f"(unknown #{i})"
            coerced_names += 1
        elif not isinstance(raw_name, str):
            coerced_names += 1

        is_nfp = bool(rec.get("is_nfp"))
        ownership = "nfp" if is_nfp else "unknown"
        cur = conn.execute(
            "INSERT INTO groups "
            "(canonical_name, slug, is_for_profit, ownership_type) "
            "VALUES (?, ?, ?, ?)",
            (name, slugify(name, i), 0 if is_nfp else 1, ownership)
        )
        group_id_by_ix[i] = cur.lastrowid
    conn.commit()
    print(f"  {len(group_id_by_ix)} groups inserted")
    if skipped_rows:
        print(f"  [!] {skipped_rows} non-dict rows in source skipped")
    if coerced_names:
        print(f"  [!] {coerced_names} rows had missing / non-string "
              f"legal_name (coerced)")

    # ── 2. Default portfolios ──
    print("\n[2/5] Inserting default portfolios...")
    for i, gid in group_id_by_ix.items():
        conn.execute(
            "INSERT INTO portfolios (group_id, name, is_default) "
            "VALUES (?, 'default', 1)",
            (gid,)
        )
    conn.commit()
    print(f"  {len(group_id_by_ix)} portfolios inserted")

    # ── 3. Entities (one per Provider Approval number) ──
    print("\n[3/5] Deriving entities from snapshot...")
    pa_to_entity_id  = {}
    pa_to_legal_name = {}
    inconsistent = 0

    for row in services_rows:
        pa    = as_str(row.get("provider_approval_number"))
        legal = as_str(row.get("providerlegalname"))
        if not pa or not legal:
            continue
        if pa in pa_to_entity_id:
            if legal != pa_to_legal_name[pa]:
                inconsistent += 1
            continue
        cur = conn.execute(
            "INSERT INTO entities (legal_name, normalised_name) "
            "VALUES (?, ?)",
            (legal, norm(legal))
        )
        pa_to_entity_id[pa]  = cur.lastrowid
        pa_to_legal_name[pa] = legal
    conn.commit()
    print(f"  {len(pa_to_entity_id)} unique entities (by PA#)")
    if inconsistent:
        print(f"  [!] {inconsistent} rows had PA# with inconsistent legal_name")

    # ── 4. Link entities to groups via PA# (with evidence) ──
    print("\n[4/5] Linking entities to groups via PA#...")
    pa_to_gid = {}
    for i, rec in enumerate(operators):
        if not isinstance(rec, dict):
            continue
        gid = group_id_by_ix.get(i)
        if gid is None:
            continue
        for pa in (rec.get("provider_numbers") or []):
            pa_clean = as_str(pa)
            if pa_clean:
                pa_to_gid[pa_clean] = gid

    linked = 0
    orphan = 0
    for pa, entity_id in pa_to_entity_id.items():
        gid = pa_to_gid.get(pa)
        if gid:
            conn.execute(
                "UPDATE entities SET group_id=? WHERE entity_id=?",
                (gid, entity_id)
            )
            conn.execute(
                "INSERT INTO evidence "
                "(subject_type, subject_id, field_name, asserted_value, "
                " source_type, confidence, asserted_by) "
                "VALUES ('entity', ?, 'group_id', ?, "
                "        'acecqa_pa_match', 1.0, 'system')",
                (entity_id, str(gid))
            )
            linked += 1
        else:
            orphan += 1
    conn.commit()
    print(f"  Entity→group links: {linked}")
    print(f"  Orphan entities (no group link): {orphan}")

    # ── 5. Services ──
    print("\n[5/5] Inserting services...")
    inserted = 0
    skipped  = 0

    for row in services_rows:
        svc_name = as_str(row.get("servicename"))
        if not svc_name:
            skipped += 1
            continue

        pa = as_str(row.get("provider_approval_number"))
        entity_id = pa_to_entity_id.get(pa)

        sap = as_str(row.get("serviceapprovalnumber")) or None
        ldc_flag = as_str(row.get("long_day_care")).upper()
        ldc = 1 if ldc_flag in ("Y", "YES", "1", "TRUE") else 0

        try:
            conn.execute(
                "INSERT OR IGNORE INTO services ("
                "  service_approval_number, provider_approval_number,"
                "  service_name, address_line, suburb, state, postcode,"
                "  approved_places, approval_granted_date, "
                "  last_transfer_date, overall_nqs_rating, "
                "  rating_issued_date, long_day_care, entity_id) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    sap, pa or None, svc_name,
                    as_str(row.get("serviceaddress")) or None,
                    as_str(row.get("suburb")) or None,
                    as_str(row.get("state")) or None,
                    as_str(row.get("postcode")) or None,
                    safe_int(row.get("numberofapprovedplaces")),
                    as_str(row.get("serviceapprovalgranteddate")) or None,
                    as_str(row.get("last_service_approval_transfer_date"))
                        or None,
                    as_str(row.get("overallrating")) or None,
                    as_str(row.get("ratingsissued")) or None,
                    ldc,
                    entity_id,
                )
            )
            inserted += 1
        except sqlite3.Error:
            skipped += 1

    conn.commit()
    n_services_actual = conn.execute(
        "SELECT COUNT(*) FROM services"
    ).fetchone()[0]
    print(f"  Attempted : {inserted}")
    print(f"  Skipped   : {skipped} (blank service_name or error)")
    print(f"  In table  : {n_services_actual}")

    # ── Summary ──
    print("\n" + "=" * 60)
    print("  BUILD COMPLETE")
    print("=" * 60)

    for tbl in ("groups", "portfolios", "entities",
                "services", "evidence"):
        n = conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
        print(f"  {tbl:14s}: {n:,}")

    print("\n  Top 10 groups by service count:")
    rows = conn.execute("""
        SELECT g.canonical_name,
               COUNT(s.service_id) AS svc,
               COALESCE(SUM(s.approved_places), 0) AS places
          FROM groups g
          LEFT JOIN entities e ON e.group_id  = g.group_id
          LEFT JOIN services s ON s.entity_id = e.entity_id
         GROUP BY g.group_id
         ORDER BY svc DESC
         LIMIT 10
    """).fetchall()
    for name, svc, places in rows:
        print(f"    {svc:4d} centres  {places:6d} places   {name}")

    # ── Sparrow sanity check ──
    print("\n  Sparrow sanity check (should match diagnostic):")
    n_svc = conn.execute("""
        SELECT COUNT(*) FROM services
         WHERE LOWER(service_name) LIKE 'sparrow early learning%'
            OR LOWER(service_name) LIKE 'sparrow nest%'
    """).fetchone()[0]
    n_ent = conn.execute("""
        SELECT COUNT(DISTINCT e.entity_id)
          FROM entities e
          JOIN services s ON s.entity_id = e.entity_id
         WHERE LOWER(s.service_name) LIKE 'sparrow early learning%'
            OR LOWER(s.service_name) LIKE 'sparrow nest%'
    """).fetchone()[0]
    n_grp = conn.execute("""
        SELECT COUNT(DISTINCT g.group_id)
          FROM groups g
          JOIN entities e ON e.group_id  = g.group_id
          JOIN services s ON s.entity_id = e.entity_id
         WHERE LOWER(s.service_name) LIKE 'sparrow early learning%'
            OR LOWER(s.service_name) LIKE 'sparrow nest%'
    """).fetchone()[0]

    print(f"    Sparrow-branded services : {n_svc}   (expected 59)")
    print(f"    Distinct entities holding: {n_ent}   (expected 22)")
    print(f"    Distinct groups spanning : {n_grp}   (expected 8 — "
          f"the fragmentation the linker will collapse)")

    conn.close()
    print(f"\nDone.  {DB_PATH}")


if __name__ == "__main__":
    main()
