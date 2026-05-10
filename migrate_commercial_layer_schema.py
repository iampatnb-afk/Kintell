"""
migrate_commercial_layer_schema.py — DEC-83 schema migration.

Adds the Commercial Layer V1 (Starting Blocks daily-rate + regulatory + operator-group)
schema to data/kintell.db.

DEC-83: Commercial Layer V1: daily-rate integration from Starting Blocks
       (pricing + regulatory snapshot + operator-group identity).

Tables created (6 new):
    1. service_fee                       — long format, per (service, age_band, session_type, as_of_date, source)
    2. service_regulatory_snapshot       — append-only Starting-Blocks-unique state snapshots
    3. service_condition                 — persistent state (regulatory conditions)
    4. service_vacancy                   — vacancy snapshots, longitudinal demand-side signal
    5. large_provider                    — operator-group dimension (Guardian/Goodstart/G8/etc. type chains)
    6. large_provider_provider_link      — many-to-many: large_provider <-> provider_approval_number
    7. service_external_capture          — provenance / raw __NEXT_DATA__ payload

Pre-existing scaffold reused (DEC-65 amendment, no new table created):
    - regulatory_events (existing, 0 rows) — populated at extract time for service-level
      enforcement actions; provider-level deferred to V2 (pending provider->entity mapping).

ALTER on existing services table:
    - services.large_provider_id TEXT NULL — FK to large_provider.

Discipline:
    - STD-08 pre-mutation backup: data/pre_commercial_layer_schema_YYYYMMDD_HHMMSS.db
    - STD-30 read-only inventory: row counts BEFORE/AFTER for sanity
    - STD-11 / DEC-62 audit_log canonical 7-column INSERT
    - Dry-run by default; --apply required to mutate
    - Idempotent: CREATE TABLE IF NOT EXISTS; ALTER guarded by column-existence check

Usage:
    $env:PYTHONIOENCODING = "utf-8"
    python migrate_commercial_layer_schema.py            # dry run (shows DDL, no DB writes)
    python migrate_commercial_layer_schema.py --apply    # take backup, run DDL, write audit_log row

Action: commercial_layer_schema_v1
"""

import argparse
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent
DB_PATH = ROOT / "data" / "kintell.db"

ACTOR = "migrate_commercial_layer_schema"
ACTION = "commercial_layer_schema_v1"
SUBJECT_TYPE = "kintell.db"
SUBJECT_ID = 0

# ---------------------------------------------------------------------------
# DDL — DEC-83 schema (6 new tables + 1 ALTER on services)
# ---------------------------------------------------------------------------

NEW_TABLES = {
    "service_fee": """
        CREATE TABLE IF NOT EXISTS service_fee (
            service_id      INTEGER NOT NULL,
            age_band        TEXT    NOT NULL,
            session_type    TEXT    NOT NULL,
            as_of_date      TEXT    NOT NULL,
            source          TEXT    NOT NULL,
            fee_aud         REAL    NOT NULL,
            fee_type        TEXT,
            inclusions      TEXT,
            fetch_id        INTEGER,
            fetched_at      TEXT    NOT NULL,
            created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
            PRIMARY KEY (service_id, age_band, session_type, as_of_date, source),
            FOREIGN KEY (service_id) REFERENCES services(service_id),
            FOREIGN KEY (fetch_id) REFERENCES service_external_capture(fetch_id)
        )
    """,

    "service_regulatory_snapshot": """
        CREATE TABLE IF NOT EXISTS service_regulatory_snapshot (
            snapshot_id                          INTEGER PRIMARY KEY AUTOINCREMENT,
            service_id                           INTEGER NOT NULL,
            snapshot_date                        TEXT    NOT NULL,
            source                               TEXT    NOT NULL,
            ccs_data_received                    INTEGER,
            ccs_revoked_by_ea                    INTEGER,
            is_closed                            INTEGER,
            temporarily_closed                   INTEGER,
            last_regulatory_visit                TEXT,
            last_transfer_date_starting_blocks   TEXT,
            enforcement_count                    INTEGER,
            nqs_starting_blocks_prev_overall     TEXT,
            nqs_starting_blocks_prev_issued      TEXT,
            provider_status                      TEXT,
            provider_approval_date               TEXT,
            provider_ccs_revoked_by_ea           INTEGER,
            provider_trade_name                  TEXT,
            hours_monday_open                    TEXT,
            hours_monday_close                   TEXT,
            hours_tuesday_open                   TEXT,
            hours_tuesday_close                  TEXT,
            hours_wednesday_open                 TEXT,
            hours_wednesday_close                TEXT,
            hours_thursday_open                  TEXT,
            hours_thursday_close                 TEXT,
            hours_friday_open                    TEXT,
            hours_friday_close                   TEXT,
            hours_saturday_open                  TEXT,
            hours_saturday_close                 TEXT,
            hours_sunday_open                    TEXT,
            hours_sunday_close                   TEXT,
            website_url                          TEXT,
            phone                                TEXT,
            email                                TEXT,
            fetch_id                             INTEGER,
            created_at                           TEXT    NOT NULL DEFAULT (datetime('now')),
            UNIQUE (service_id, snapshot_date, source),
            FOREIGN KEY (service_id) REFERENCES services(service_id),
            FOREIGN KEY (fetch_id) REFERENCES service_external_capture(fetch_id)
        )
    """,

    "service_condition": """
        CREATE TABLE IF NOT EXISTS service_condition (
            condition_id        TEXT    NOT NULL,
            level               TEXT    NOT NULL,
            source              TEXT    NOT NULL,
            service_id          INTEGER NOT NULL,
            condition_text      TEXT    NOT NULL,
            first_observed_at   TEXT    NOT NULL,
            last_observed_at    TEXT    NOT NULL,
            still_active        INTEGER NOT NULL DEFAULT 1,
            created_at          TEXT    NOT NULL DEFAULT (datetime('now')),
            PRIMARY KEY (condition_id, level, source),
            FOREIGN KEY (service_id) REFERENCES services(service_id),
            CHECK (level IN ('service', 'provider'))
        )
    """,

    "service_vacancy": """
        CREATE TABLE IF NOT EXISTS service_vacancy (
            vacancy_id          INTEGER PRIMARY KEY AUTOINCREMENT,
            service_id          INTEGER NOT NULL,
            age_band            TEXT,
            observed_at         TEXT    NOT NULL,
            source              TEXT    NOT NULL,
            vacancy_status      TEXT    NOT NULL,
            vacancy_detail_json TEXT,
            fetch_id            INTEGER,
            created_at          TEXT    NOT NULL DEFAULT (datetime('now')),
            UNIQUE (service_id, age_band, observed_at, source),
            FOREIGN KEY (service_id) REFERENCES services(service_id),
            FOREIGN KEY (fetch_id) REFERENCES service_external_capture(fetch_id)
        )
    """,

    "large_provider": """
        CREATE TABLE IF NOT EXISTS large_provider (
            large_provider_id   TEXT PRIMARY KEY,
            name                TEXT NOT NULL,
            slug                TEXT,
            source              TEXT NOT NULL,
            first_observed_at   TEXT NOT NULL,
            last_observed_at    TEXT NOT NULL,
            created_at          TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """,

    "large_provider_provider_link": """
        CREATE TABLE IF NOT EXISTS large_provider_provider_link (
            large_provider_id              TEXT NOT NULL,
            provider_approval_number       TEXT NOT NULL,
            source                         TEXT NOT NULL,
            provider_name_at_observation   TEXT,
            first_observed_at              TEXT NOT NULL,
            last_observed_at               TEXT NOT NULL,
            created_at                     TEXT NOT NULL DEFAULT (datetime('now')),
            PRIMARY KEY (large_provider_id, provider_approval_number, source),
            FOREIGN KEY (large_provider_id) REFERENCES large_provider(large_provider_id)
        )
    """,

    "service_external_capture": """
        CREATE TABLE IF NOT EXISTS service_external_capture (
            fetch_id            INTEGER PRIMARY KEY AUTOINCREMENT,
            service_id          INTEGER,
            external_id         TEXT NOT NULL,
            source              TEXT NOT NULL,
            source_url          TEXT NOT NULL,
            fetched_at          TEXT NOT NULL,
            http_status         INTEGER NOT NULL,
            payload_json        TEXT NOT NULL,
            payload_sha256      TEXT NOT NULL,
            extractor_version   TEXT NOT NULL,
            created_at          TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE (service_id, source, payload_sha256),
            FOREIGN KEY (service_id) REFERENCES services(service_id)
        )
    """,
}

# Order matters: service_external_capture must exist before tables that FK to its fetch_id.
TABLE_CREATE_ORDER = [
    "service_external_capture",      # provenance, FK target for service_fee/snapshot/vacancy
    "large_provider",                # FK target for large_provider_provider_link
    "large_provider_provider_link",
    "service_fee",
    "service_regulatory_snapshot",
    "service_condition",
    "service_vacancy",
]

INDEXES = [
    # service_fee
    "CREATE INDEX IF NOT EXISTS ix_service_fee_service_asof ON service_fee(service_id, as_of_date)",
    "CREATE INDEX IF NOT EXISTS ix_service_fee_source ON service_fee(source)",
    # service_regulatory_snapshot
    "CREATE INDEX IF NOT EXISTS ix_service_reg_snapshot_service_date ON service_regulatory_snapshot(service_id, snapshot_date)",
    "CREATE INDEX IF NOT EXISTS ix_service_reg_snapshot_ccs_revoked ON service_regulatory_snapshot(ccs_revoked_by_ea) WHERE ccs_revoked_by_ea = 1",
    # service_condition
    "CREATE INDEX IF NOT EXISTS ix_service_condition_service ON service_condition(service_id)",
    "CREATE INDEX IF NOT EXISTS ix_service_condition_active ON service_condition(still_active) WHERE still_active = 1",
    # service_vacancy
    "CREATE INDEX IF NOT EXISTS ix_service_vacancy_service_observed ON service_vacancy(service_id, observed_at)",
    # large_provider_provider_link
    "CREATE INDEX IF NOT EXISTS ix_lp_link_provider ON large_provider_provider_link(provider_approval_number)",
    # service_external_capture
    "CREATE INDEX IF NOT EXISTS ix_external_capture_service_fetched ON service_external_capture(service_id, fetched_at)",
    "CREATE INDEX IF NOT EXISTS ix_external_capture_external_fetched ON service_external_capture(external_id, fetched_at)",
    "CREATE INDEX IF NOT EXISTS ix_external_capture_source ON service_external_capture(source)",
    # services.large_provider_id (added in ALTER below, index here)
    "CREATE INDEX IF NOT EXISTS ix_services_large_provider ON services(large_provider_id)",
]

ALTER_SERVICES = (
    "ALTER TABLE services ADD COLUMN large_provider_id TEXT REFERENCES large_provider(large_provider_id)"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def take_backup() -> Path:
    """STD-08: timestamped pre-mutation backup. Returns the backup path."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = ROOT / "data" / f"pre_commercial_layer_schema_{ts}.db"
    shutil.copy2(DB_PATH, backup_path)
    return backup_path


def existing_tables(conn) -> set:
    return {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}


def services_has_column(conn, col: str) -> bool:
    return any(r[1] == col for r in conn.execute("PRAGMA table_info(services)"))


def row_counts(conn, tables) -> dict:
    out = {}
    existing = existing_tables(conn)
    for t in tables:
        if t in existing:
            out[t] = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        else:
            out[t] = None  # not yet created
    return out


def write_audit(conn, before: dict, after: dict, backup_path: Path | None) -> int:
    """STD-11 / DEC-62 — canonical 7-column audit_log INSERT (audit_id auto, occurred_at default)."""
    import json

    before_json = json.dumps(before, sort_keys=True)
    after_json = json.dumps(after, sort_keys=True)
    reason = (
        "DEC-83 schema migration: Commercial Layer V1 (Starting Blocks daily-rate + regulatory + "
        "operator-group). 7 new tables created (service_external_capture, large_provider, "
        "large_provider_provider_link, service_fee, service_regulatory_snapshot, service_condition, "
        "service_vacancy). 1 column added to services (large_provider_id). 13 indexes created. "
        "Pre-existing regulatory_events scaffold reused at extract time (no schema change). "
        f"Pre-mutation backup: {backup_path.name if backup_path else '<dry-run>'}. "
        "DDL idempotent (CREATE IF NOT EXISTS, ALTER guarded). "
        "audit_log row written per STD-11 / DEC-62 canonical 7-column format."
    )
    cur = conn.execute(
        """
        INSERT INTO audit_log (actor, action, subject_type, subject_id, before_json, after_json, reason)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (ACTOR, ACTION, SUBJECT_TYPE, SUBJECT_ID, before_json, after_json, reason),
    )
    return cur.lastrowid


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="DEC-83 schema migration: Commercial Layer V1.")
    parser.add_argument(
        "--apply", action="store_true",
        help="Take STD-08 backup, run DDL, write audit_log row. Without this flag, dry-run only.",
    )
    args = parser.parse_args()

    if not DB_PATH.exists():
        print(f"ERROR: {DB_PATH} not found.", file=sys.stderr)
        return 1

    target_tables = list(NEW_TABLES.keys())

    # -- Pre-flight inventory (STD-30 spirit) --------------------------------
    conn = sqlite3.connect(DB_PATH)
    try:
        before = {
            "audit_log_max_id":      conn.execute("SELECT MAX(audit_id) FROM audit_log").fetchone()[0],
            "row_counts":            row_counts(conn, target_tables + ["regulatory_events", "services"]),
            "services_has_large_provider_id": services_has_column(conn, "large_provider_id"),
            "tables_already_exist":  sorted(set(target_tables) & existing_tables(conn)),
        }
    finally:
        conn.close()

    print("=" * 70)
    print("  DEC-83 SCHEMA MIGRATION — Commercial Layer V1")
    print("=" * 70)
    print(f"  DB path: {DB_PATH}")
    print(f"  Mode:    {'APPLY (will mutate)' if args.apply else 'DRY-RUN (read-only)'}")
    print()
    print("PRE-FLIGHT INVENTORY")
    print(f"  audit_log max id:                {before['audit_log_max_id']}")
    print(f"  services.large_provider_id col:  {before['services_has_large_provider_id']}")
    print(f"  tables that already exist:       {before['tables_already_exist'] or '(none)'}")
    print()
    print("TARGET STATE")
    print(f"  + 7 new tables:")
    for t in TABLE_CREATE_ORDER:
        flag = " (already exists)" if t in before["tables_already_exist"] else ""
        print(f"      {t}{flag}")
    print(f"  + ALTER services ADD COLUMN large_provider_id"
          + (" (already exists)" if before['services_has_large_provider_id'] else ""))
    print(f"  + {len(INDEXES)} indexes (CREATE INDEX IF NOT EXISTS)")
    print(f"  + reuse pre-existing scaffold: regulatory_events (no schema change; populated at extract time)")
    print()

    if not args.apply:
        print("DRY-RUN — DDL preview (top of each):")
        for t in TABLE_CREATE_ORDER:
            print(f"  -- {t} --")
            preview = NEW_TABLES[t].strip().splitlines()[:3]
            for line in preview:
                print(f"    {line}")
            print(f"    ...")
        print(f"  -- ALTER services --")
        print(f"    {ALTER_SERVICES}")
        print()
        print("To apply: re-run with --apply")
        return 0

    # -- Apply path: STD-08 backup -------------------------------------------
    print("STD-08 backup ...")
    backup_path = take_backup()
    print(f"  -> {backup_path}")
    print(f"  size: {backup_path.stat().st_size / 1024 / 1024:.1f} MB")
    print()

    # -- Apply path: DDL ------------------------------------------------------
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()

        # Tables
        print("Creating tables...")
        for t in TABLE_CREATE_ORDER:
            cur.execute(NEW_TABLES[t])
            print(f"  {t}: created (or already existed)")

        # ALTER services (guarded by column-existence check)
        if not services_has_column(conn, "large_provider_id"):
            print(f"\nAltering services...")
            cur.execute(ALTER_SERVICES)
            print(f"  services.large_provider_id: added")
        else:
            print(f"\nservices.large_provider_id already exists; skipping ALTER")

        # Indexes
        print(f"\nCreating indexes...")
        for ix_sql in INDEXES:
            cur.execute(ix_sql)
        print(f"  {len(INDEXES)} indexes (CREATE IF NOT EXISTS)")

        conn.commit()

        # -- Post-flight inventory + audit_log row ---------------------------
        after = {
            "row_counts":            row_counts(conn, target_tables + ["regulatory_events", "services"]),
            "services_has_large_provider_id": services_has_column(conn, "large_provider_id"),
            "tables_now_exist":      sorted(set(target_tables) & existing_tables(conn)),
            "indexes_attempted":     len(INDEXES),
        }

        new_audit_id = write_audit(conn, before, after, backup_path)
        conn.commit()
        after["audit_log_new_id"] = new_audit_id

        print()
        print("POST-FLIGHT")
        print(f"  audit_log new id:          {new_audit_id}")
        print(f"  tables present:            {len(after['tables_now_exist'])}/{len(target_tables)}")
        print(f"  services.large_provider_id: {after['services_has_large_provider_id']}")
        print(f"  rows in new tables:        {sum(v or 0 for k, v in after['row_counts'].items() if k in target_tables)} (expected 0)")
        print()
        print("DONE.")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
