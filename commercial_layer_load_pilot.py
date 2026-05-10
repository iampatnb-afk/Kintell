"""
commercial_layer_load_pilot.py — DEC-83 V1 proof load.

One-shot script that loads the Starting Blocks pilot's 130 centres into main
`data/kintell.db` Commercial Layer tables. Reads pilot's raw_payload directly
(no re-fetch from Starting Blocks needed — payloads preserved on G: drive).

Per DEC-83:
- Identity resolution via substr(serviceId, 1, 11) = services.service_approval_number
- 1 expected unresolvable centre (Redfern Occasional Child Care) gets capture-only
- All 7 commercial-layer tables populated
- Pre-existing regulatory_events scaffold populated for service-level enforcement
- services.large_provider_id updated where Starting Blocks provides largeProvider

Discipline:
- STD-08 pre-mutation backup
- STD-30 row-count inventory before/after
- STD-11 / DEC-62 audit_log canonical 7-column row
- Dry-run by default (--apply required to mutate)

Usage:
    $env:PYTHONIOENCODING = "utf-8"
    python commercial_layer_load_pilot.py            # dry run (extract logic, no DB writes)
    python commercial_layer_load_pilot.py --apply    # take backup, run, write audit_log row

Action: commercial_layer_load_v1
"""

import argparse
import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

import commercial_layer_extract as cle

ROOT = Path(__file__).parent
DB_PATH = ROOT / "data" / "kintell.db"
PILOT_DB_PATH = Path(r"G:\My Drive\Patrick's Playground\childcare_market_spike\startingblocks_pilot.sqlite")

ACTOR = "commercial_layer_load_pilot"
ACTION = "commercial_layer_load_v1"
SUBJECT_TYPE = "kintell.db"
SUBJECT_ID = 0
SOURCE = "startingblocks"

NEW_TABLES_FOR_INVENTORY = [
    "service_fee", "service_regulatory_snapshot", "service_condition",
    "service_vacancy", "large_provider", "large_provider_provider_link",
    "service_external_capture", "regulatory_events",
]


def take_backup() -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = ROOT / "data" / f"pre_commercial_layer_load_{ts}.db"
    shutil.copy2(DB_PATH, backup_path)
    return backup_path


def row_counts(conn) -> dict:
    out = {}
    for t in NEW_TABLES_FOR_INVENTORY:
        out[t] = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    out["services_with_large_provider_id"] = conn.execute(
        "SELECT COUNT(*) FROM services WHERE large_provider_id IS NOT NULL"
    ).fetchone()[0]
    return out


def write_audit(conn, before: dict, after: dict, summary: dict, backup_path: Path | None) -> int:
    reason = (
        "DEC-83 V1 proof load: 130 Starting Blocks pilot centres -> main kintell.db Commercial Layer. "
        "Reads pilot's raw_payload (preserved on G: drive) and runs commercial_layer_extract.extract_payload "
        "for each. Populates 7 new tables + regulatory_events (existing scaffold) + services.large_provider_id. "
        f"Identity resolution: substr(serviceId,1,11) -> services.service_approval_number ({summary['resolved']}/130 resolved; "
        f"{summary['unresolved']} captured with service_id=NULL for V2 reconciliation). "
        f"Pre-mutation backup: {backup_path.name if backup_path else '<dry-run>'}. "
        "audit_log row per STD-11 / DEC-62 canonical 7-column format."
    )
    cur = conn.execute(
        """
        INSERT INTO audit_log (actor, action, subject_type, subject_id, before_json, after_json, reason)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (ACTOR, ACTION, SUBJECT_TYPE, SUBJECT_ID,
         json.dumps(before, sort_keys=True), json.dumps(after, sort_keys=True), reason),
    )
    return cur.lastrowid


def main() -> int:
    parser = argparse.ArgumentParser(description="DEC-83 V1 proof load.")
    parser.add_argument("--apply", action="store_true",
                        help="Take backup, run, write audit_log. Without --apply, dry-run only.")
    parser.add_argument("--limit", type=int, default=0,
                        help="Limit pilot rows processed (0 = all 130). Useful for spot-checks.")
    args = parser.parse_args()

    if not DB_PATH.exists():
        print(f"ERROR: {DB_PATH} not found.", file=sys.stderr)
        return 1
    if not PILOT_DB_PATH.exists():
        print(f"ERROR: pilot DB not found at {PILOT_DB_PATH}", file=sys.stderr)
        return 1

    # Pre-flight inventory
    main_conn = sqlite3.connect(DB_PATH)
    main_conn.row_factory = sqlite3.Row
    before = row_counts(main_conn)
    pre_audit_max = main_conn.execute("SELECT MAX(audit_id) FROM audit_log").fetchone()[0]
    main_conn.close()

    print("=" * 70)
    print("  DEC-83 COMMERCIAL LAYER V1 PROOF LOAD")
    print("=" * 70)
    print(f"  main DB:  {DB_PATH}")
    print(f"  pilot DB: {PILOT_DB_PATH}")
    print(f"  Mode:     {'APPLY' if args.apply else 'DRY-RUN (transaction will be rolled back)'}")
    if args.limit:
        print(f"  Limit:    {args.limit} pilot rows")
    print()
    print(f"  Pre-flight (audit_log max id: {pre_audit_max}):")
    for k, v in before.items():
        print(f"    {k:<40} {v}")
    print()

    backup_path = None
    if args.apply:
        print("STD-08 backup ...")
        backup_path = take_backup()
        print(f"  -> {backup_path.name}")
        print(f"  size: {backup_path.stat().st_size / 1024 / 1024:.1f} MB")
        print()

    # Open both connections
    main_conn = sqlite3.connect(DB_PATH, isolation_level=None)  # manual txn control
    main_conn.row_factory = sqlite3.Row
    pilot_conn = sqlite3.connect(PILOT_DB_PATH)
    pilot_conn.row_factory = sqlite3.Row

    # Read pilot raw_payload — most-recent fetch per ULID (pilot only has 1 per ulid but be defensive)
    sql = """
        SELECT ulid, source_url, fetched_at, http_status, payload_json
        FROM raw_payload rp
        WHERE fetch_id = (
            SELECT fetch_id FROM raw_payload WHERE ulid = rp.ulid
            ORDER BY fetched_at DESC LIMIT 1
        )
        ORDER BY ulid
    """
    if args.limit:
        sql += f" LIMIT {args.limit}"
    pilot_rows = pilot_conn.execute(sql).fetchall()
    print(f"  pilot raw_payload rows to process: {len(pilot_rows)}")
    print()

    # Begin transaction (rolled back in dry-run)
    main_conn.execute("BEGIN")

    summary = {
        "processed": 0, "resolved": 0, "unresolved": 0,
        "capture_inserted": 0, "fee_rows": 0, "fee_skipped": 0,
        "regulatory_snapshot_rows": 0, "condition_rows": 0,
        "enforcement_events": 0, "vacancy_rows": 0,
        "large_provider_set_writes": 0, "large_provider_links": 0,
        "service_large_provider_updated": 0,
        "errors": [],
    }
    unresolved_examples = []
    large_providers_seen = {}

    for i, pr in enumerate(pilot_rows, 1):
        ulid = pr["ulid"]
        try:
            counts = cle.extract_payload(
                main_conn,
                payload_text=pr["payload_json"],
                source=SOURCE,
                fetched_at=pr["fetched_at"],
                http_status=pr["http_status"],
                source_url_override=pr["source_url"],
            )
            summary["processed"] += 1
            if counts.get("error"):
                summary["errors"].append((ulid, counts["error"]))
                continue
            if counts.get("unresolved"):
                summary["unresolved"] += 1
                if len(unresolved_examples) < 5:
                    unresolved_examples.append((ulid, counts.get("external_id")))
            else:
                summary["resolved"] += 1
            summary["capture_inserted"]               += counts["capture_inserted"]
            summary["fee_rows"]                       += counts["fee_rows"]
            summary["fee_skipped"]                    += counts["fee_skipped"]
            summary["regulatory_snapshot_rows"]       += counts["regulatory_snapshot_rows"]
            summary["condition_rows"]                 += counts["condition_rows"]
            summary["enforcement_events"]             += counts["enforcement_events"]
            summary["vacancy_rows"]                   += counts["vacancy_rows"]
            summary["large_provider_set_writes"]      += counts["large_provider_set"]
            summary["large_provider_links"]           += counts["large_provider_links"]
            summary["service_large_provider_updated"] += counts["service_large_provider_updated"]
        except Exception as e:
            summary["errors"].append((ulid, repr(e)))
            if len(summary["errors"]) <= 3:
                # surface early errors immediately so the run can be aborted
                print(f"  ERROR [{i}/{len(pilot_rows)}] {ulid}: {e!r}")
        if i % 25 == 0 or i == len(pilot_rows):
            print(f"  [{i:>3}/{len(pilot_rows)}] processed; "
                  f"resolved={summary['resolved']} unresolved={summary['unresolved']} "
                  f"errors={len(summary['errors'])}")

    print()
    print("EXTRACTION COUNTS")
    for k in ("processed", "resolved", "unresolved", "capture_inserted",
              "fee_rows", "fee_skipped", "regulatory_snapshot_rows",
              "condition_rows", "enforcement_events", "vacancy_rows",
              "large_provider_set_writes", "large_provider_links",
              "service_large_provider_updated"):
        print(f"  {k:<40} {summary[k]}")
    if summary["errors"]:
        print(f"  errors: {len(summary['errors'])}")
        for ulid, e in summary["errors"][:5]:
            print(f"    {ulid}: {e}")
    if unresolved_examples:
        print(f"  unresolved examples (capture-only):")
        for u, ext in unresolved_examples:
            print(f"    ulid={u}  external_id={ext}")

    # Post-flight inventory (BEFORE rollback so we see uncommitted state)
    after = row_counts(main_conn)
    print()
    print("POST-EXTRACTION INVENTORY (uncommitted)")
    for k, v in after.items():
        delta = (v - before[k]) if isinstance(v, int) and isinstance(before[k], int) else "?"
        print(f"  {k:<40} {v}  (delta: +{delta})")

    if not args.apply:
        print()
        print("DRY-RUN — rolling back transaction; no DB changes persisted.")
        main_conn.execute("ROLLBACK")
        main_conn.close()
        pilot_conn.close()
        return 0 if not summary["errors"] else 2

    # Apply path: write audit_log + commit
    new_audit_id = write_audit(main_conn, before, after, summary, backup_path)
    main_conn.execute("COMMIT")
    print()
    print(f"COMMITTED. audit_log new id: {new_audit_id}")
    main_conn.close()
    pilot_conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
