"""
db_inventory.py — Read-only inventory of data/kintell.db.

Writes recon/db_inventory.md with:
  1. Tables list + row counts
  2. Per-table schema, indexes, last-update hints (year col + audit_log mention)
  3. Coverage stats per key dimension (sa2, year, services breakdown)
  4. Foreign-key + implicit-orphan health
  5. Backup file listing in data/
  6. Full audit_log dump

No DB writes. Opens DB in URI read-only mode.
"""

from __future__ import annotations

import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = "data/kintell.db"
OUT_PATH = "recon/db_inventory.md"
DATA_DIR = "data"

# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------
if not Path(DB_PATH).exists():
    print(f"ERROR: {DB_PATH} not found. Run from project root.", file=sys.stderr)
    sys.exit(1)

try:
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
except sqlite3.Error as e:
    print(f"WARN: URI ro-mode failed ({e}); falling back to read-only-by-discipline", file=sys.stderr)
    conn = sqlite3.connect(DB_PATH)

conn.row_factory = sqlite3.Row
cur = conn.cursor()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
lines: list[str] = []


def w(line: str = "") -> None:
    lines.append(line)


def cols_of(table: str) -> list[tuple]:
    return cur.execute(f'PRAGMA table_info("{table}")').fetchall()


def col_names(table: str) -> list[str]:
    return [c[1] for c in cols_of(table)]


def first_present(target_cols: list[str], candidates: list[str]) -> str | None:
    lower = {c.lower(): c for c in target_cols}
    for cand in candidates:
        if cand.lower() in lower:
            return lower[cand.lower()]
    return None


def safe_count(sql: str, params: tuple = ()) -> int | None:
    try:
        return cur.execute(sql, params).fetchone()[0]
    except sqlite3.Error:
        return None


# ---------------------------------------------------------------------------
# Discover tables
# ---------------------------------------------------------------------------
tables = [
    r[0] for r in cur.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type='table' AND name NOT LIKE 'sqlite_%' "
        "ORDER BY name"
    ).fetchall()
]

table_rows: dict[str, int] = {}
for t in tables:
    table_rows[t] = safe_count(f'SELECT COUNT(*) FROM "{t}"') or 0

total_rows = sum(table_rows.values())

# Audit log column discovery (used in multiple sections)
audit_present = "audit_log" in tables
audit_cols = col_names("audit_log") if audit_present else []
audit_id_col = first_present(audit_cols, ["audit_id", "id"])
audit_ts_col = first_present(audit_cols, ["timestamp", "ts", "created_at", "run_at", "at"])
audit_action_col = first_present(audit_cols, ["action", "action_name", "event", "operation"])
audit_text_cols = [
    c for c in audit_cols
    if c.lower() in ("action", "action_name", "target_table", "notes",
                     "description", "details", "summary")
]

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
db_size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)

w("# DB Inventory — `data/kintell.db`")
w("")
w(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
w(f"DB size: {db_size_mb:,.1f} MB")
w(f"Tables: {len(tables)} | Total rows: {total_rows:,}")
w("")
w("Read-only snapshot. Pre-Step-1b reference.")
w("")

# ---------------------------------------------------------------------------
# 1. Tables list
# ---------------------------------------------------------------------------
w("## 1. Tables — row counts")
w("")
w("| # | Table | Rows |")
w("|---:|---|---:|")
for i, t in enumerate(tables, 1):
    w(f"| {i} | `{t}` | {table_rows[t]:,} |")
w(f"| | **TOTAL** | **{total_rows:,}** |")
w("")

# ---------------------------------------------------------------------------
# 2. Per-table detail
# ---------------------------------------------------------------------------
w("## 2. Per-table schema, indexes, last-update")
w("")

for t in tables:
    w(f"### `{t}`")
    w("")
    w(f"Rows: **{table_rows[t]:,}**")
    w("")

    cols = cols_of(t)
    names = [c[1] for c in cols]

    # Schema table
    w("Columns:")
    w("")
    w("| # | Name | Type | NotNull | Default | PK |")
    w("|---:|---|---|:-:|---|:-:|")
    for c in cols:
        default = "" if c[4] is None else str(c[4])
        w(f"| {c[0]} | `{c[1]}` | {c[2] or ''} | {c[3]} | {default} | {c[5]} |")
    w("")

    # Indexes
    idx_list = cur.execute(f'PRAGMA index_list("{t}")').fetchall()
    if idx_list:
        w("Indexes:")
        w("")
        for ix in idx_list:
            ix_info = cur.execute(f'PRAGMA index_info("{ix[1]}")').fetchall()
            ix_cols = ", ".join((ic[2] or "<expr>") for ic in ix_info)
            unique_tag = " UNIQUE" if ix[2] else ""
            origin = f" ({ix[3]})" if len(ix) > 3 else ""
            w(f"- `{ix[1]}`{unique_tag}{origin} on ({ix_cols})")
        w("")

    # Year column quick range
    year_col = first_present(names, ["year", "reference_year", "ref_year", "data_year"])
    if year_col:
        yr = cur.execute(
            f'SELECT MIN("{year_col}"), MAX("{year_col}"), COUNT(DISTINCT "{year_col}") '
            f'FROM "{t}" WHERE "{year_col}" IS NOT NULL'
        ).fetchone()
        if yr and yr[2]:
            w(f"- `{year_col}` range: {yr[0]} → {yr[1]} ({yr[2]} distinct)")

    # Timestamp columns
    ts_candidates = [c for c in names if c.lower() in (
        "updated_at", "created_at", "ingested_at", "as_of",
        "timestamp", "last_updated", "ingest_ts"
    )]
    for tc in ts_candidates:
        try:
            r = cur.execute(f'SELECT MIN("{tc}"), MAX("{tc}") FROM "{t}"').fetchone()
            w(f"- `{tc}` range: {r[0]} → {r[1]}")
        except sqlite3.Error:
            pass

    # Audit log mention (best-effort heuristic)
    if audit_present and audit_text_cols and audit_ts_col and t != "audit_log":
        like_clauses = " OR ".join(f'"{c}" LIKE ?' for c in audit_text_cols)
        params = tuple(f"%{t}%" for _ in audit_text_cols)
        try:
            r = cur.execute(
                f'SELECT MAX("{audit_ts_col}"), COUNT(*) FROM audit_log '
                f"WHERE {like_clauses}",
                params,
            ).fetchone()
            if r and r[1]:
                w(f"- audit_log mentions: {r[1]} (most recent ts: {r[0]})")
        except sqlite3.Error:
            pass

    w("")

# ---------------------------------------------------------------------------
# 3. Coverage stats per key dimension
# ---------------------------------------------------------------------------
w("## 3. Coverage stats — key dimensions")
w("")

# 3a. SA2 coverage
w("### 3a. SA2 coverage by table")
w("")
w("Tables exposing an SA2 column. NULLs and distinct-SA2 cardinality both shown.")
w("")
w("| Table | SA2 column | Distinct SA2s | NULL rows | Total |")
w("|---|---|---:|---:|---:|")
sa2_candidates = [
    "sa2_code", "sa2_code_2021", "SA2_CODE_2021", "sa2_2021_code",
    "sa2_main", "sa2_maincode_2021", "sa2"
]
for t in tables:
    names = col_names(t)
    sc = first_present(names, sa2_candidates)
    if not sc:
        continue
    n_distinct = safe_count(
        f'SELECT COUNT(DISTINCT "{sc}") FROM "{t}" WHERE "{sc}" IS NOT NULL'
    )
    n_null = safe_count(f'SELECT COUNT(*) FROM "{t}" WHERE "{sc}" IS NULL')
    w(f"| `{t}` | `{sc}` | {n_distinct:,} | {n_null:,} | {table_rows[t]:,} |")
w("")

# 3b. Year coverage
w("### 3b. Year coverage by table")
w("")
w("| Table | Year col | Min | Max | Distinct |")
w("|---|---|---:|---:|---:|")
for t in tables:
    names = col_names(t)
    yc = first_present(names, ["year", "reference_year", "ref_year", "data_year"])
    if not yc:
        continue
    try:
        r = cur.execute(
            f'SELECT MIN("{yc}"), MAX("{yc}"), COUNT(DISTINCT "{yc}") '
            f'FROM "{t}" WHERE "{yc}" IS NOT NULL'
        ).fetchone()
        if r and r[2]:
            w(f"| `{t}` | `{yc}` | {r[0]} | {r[1]} | {r[2]} |")
    except sqlite3.Error:
        continue
w("")

# 3c. services-specific (Step 1b directly cares about this)
if "services" in tables:
    w("### 3c. `services` table — Step 1b focus")
    w("")
    s_cols = col_names("services")
    n_total = table_rows["services"]
    sa2_col = first_present(s_cols, sa2_candidates)
    lat_col = first_present(s_cols, ["lat", "latitude"])
    lng_col = first_present(s_cols, ["lng", "lon", "long", "longitude"])
    state_col = first_present(s_cols, ["state", "state_code", "state_abbr"])

    if sa2_col:
        n_with = safe_count(f'SELECT COUNT(*) FROM services WHERE "{sa2_col}" IS NOT NULL') or 0
        n_null = n_total - n_with
        pct_with = (100 * n_with / n_total) if n_total else 0.0
        w(f"- Total services: **{n_total:,}**")
        w(f"- With `{sa2_col}` populated: **{n_with:,}** ({pct_with:.2f}%)")
        w(f"- NULL `{sa2_col}`: **{n_null:,}** ({100 - pct_with:.2f}%)")
        if lat_col and lng_col:
            n_recoverable = safe_count(
                f'SELECT COUNT(*) FROM services '
                f'WHERE "{sa2_col}" IS NULL '
                f'AND "{lat_col}" IS NOT NULL AND "{lng_col}" IS NOT NULL'
            )
            n_unrecoverable = safe_count(
                f'SELECT COUNT(*) FROM services '
                f'WHERE "{sa2_col}" IS NULL '
                f'AND ("{lat_col}" IS NULL OR "{lng_col}" IS NULL)'
            )
            w(f"- NULL SA2 **with** `{lat_col}/{lng_col}` (Step 1b candidates): **{n_recoverable:,}**")
            w(f"- NULL SA2 **without** lat/lng (unrecoverable via polygon): **{n_unrecoverable:,}**")
    if state_col:
        w("")
        w(f"By `{state_col}` (all services):")
        w("")
        w(f"| {state_col} | Rows | NULL sa2 | NULL sa2 with lat/lng |")
        w("|---|---:|---:|---:|")
        rows = cur.execute(
            f'SELECT "{state_col}", COUNT(*) FROM services '
            f'GROUP BY "{state_col}" ORDER BY 2 DESC'
        ).fetchall()
        for r in rows:
            sval = r[0] if r[0] is not None else "(NULL)"
            n_state_null_sa2 = safe_count(
                f'SELECT COUNT(*) FROM services '
                f'WHERE "{state_col}" IS ? AND "{sa2_col}" IS NULL',
                (r[0],)
            ) if sa2_col else None
            n_state_recov = None
            if sa2_col and lat_col and lng_col:
                n_state_recov = safe_count(
                    f'SELECT COUNT(*) FROM services '
                    f'WHERE "{state_col}" IS ? AND "{sa2_col}" IS NULL '
                    f'AND "{lat_col}" IS NOT NULL AND "{lng_col}" IS NOT NULL',
                    (r[0],)
                )
            w(f"| {sval} | {r[1]:,} | "
              f"{(n_state_null_sa2 or 0):,} | "
              f"{(n_state_recov or 0):,} |")
    w("")

# ---------------------------------------------------------------------------
# 4. FK / orphan health
# ---------------------------------------------------------------------------
w("## 4. Foreign-key / orphan health")
w("")

declared_any = False
for t in tables:
    fks = cur.execute(f'PRAGMA foreign_key_list("{t}")').fetchall()
    if not fks:
        continue
    if not declared_any:
        w("### 4a. Declared foreign keys")
        w("")
        declared_any = True
    w(f"**`{t}`**")
    w("")
    for fk in fks:
        ref_t = fk[2]
        from_c = fk[3]
        to_c = fk[4]
        try:
            orphan = cur.execute(
                f'SELECT COUNT(*) FROM "{t}" c '
                f'LEFT JOIN "{ref_t}" p ON c."{from_c}" = p."{to_c}" '
                f'WHERE c."{from_c}" IS NOT NULL AND p."{to_c}" IS NULL'
            ).fetchone()[0]
            verdict = "✓" if orphan == 0 else "⚠"
            w(f"- {verdict} `{from_c}` → `{ref_t}.{to_c}` — orphans: {orphan:,}")
        except sqlite3.Error as e:
            w(f"- `{from_c}` → `{ref_t}.{to_c}` — check error: {e}")
    w("")

if not declared_any:
    w("### 4a. Declared foreign keys")
    w("")
    w("(No declared FKs in schema.)")
    w("")

# 4b. Implicit reference checks — known logical FKs from project doc
w("### 4b. Implicit reference checks")
w("")
implicit = [
    ("services", "sa2_code", "abs_sa2_erp_annual", "sa2_code",
     "Service SA2s present in canonical SA2 universe"),
]
implicit_run = 0
for child, c_col, parent, p_col, label in implicit:
    if child not in tables or parent not in tables:
        continue
    if c_col not in col_names(child) or p_col not in col_names(parent):
        continue
    implicit_run += 1
    try:
        n_orphan_sa2s = cur.execute(
            f'SELECT COUNT(DISTINCT c."{c_col}") FROM "{child}" c '
            f'WHERE c."{c_col}" IS NOT NULL '
            f'AND c."{c_col}" NOT IN '
            f'(SELECT "{p_col}" FROM "{parent}" WHERE "{p_col}" IS NOT NULL)'
        ).fetchone()[0]
        n_orphan_rows = cur.execute(
            f'SELECT COUNT(*) FROM "{child}" c '
            f'WHERE c."{c_col}" IS NOT NULL '
            f'AND c."{c_col}" NOT IN '
            f'(SELECT "{p_col}" FROM "{parent}" WHERE "{p_col}" IS NOT NULL)'
        ).fetchone()[0]
        verdict = "✓" if n_orphan_sa2s == 0 else "⚠"
        w(f"- {verdict} {label}")
        w(f"  - `{child}.{c_col}` → `{parent}.{p_col}`")
        w(f"  - Orphan distinct SA2s: **{n_orphan_sa2s}**")
        w(f"  - Orphan rows: **{n_orphan_rows:,}**")
    except sqlite3.Error as e:
        w(f"- {label}: error ({e})")
if implicit_run == 0:
    w("(No implicit reference checks applicable.)")
w("")

# ---------------------------------------------------------------------------
# 5. Backups in data/
# ---------------------------------------------------------------------------
w("## 5. Backups in `data/`")
w("")
data_path = Path(DATA_DIR)
if data_path.exists() and data_path.is_dir():
    backups = sorted(
        [p for p in data_path.iterdir()
         if p.is_file() and "backup" in p.name.lower()],
        key=lambda p: p.stat().st_mtime,
    )
    if backups:
        w("| File | Size (MB) | Modified |")
        w("|---|---:|---|")
        total_mb = 0.0
        for b in backups:
            sz_mb = b.stat().st_size / (1024 * 1024)
            total_mb += sz_mb
            mt = datetime.fromtimestamp(b.stat().st_mtime).isoformat(timespec="seconds")
            w(f"| `{b.name}` | {sz_mb:,.1f} | {mt} |")
        w(f"| **TOTAL** | **{total_mb:,.1f}** | |")
    else:
        w("(no backup files found in `data/`)")
else:
    w(f"(`{DATA_DIR}/` not found)")
w("")

# ---------------------------------------------------------------------------
# 6. audit_log summary
# ---------------------------------------------------------------------------
w("## 6. `audit_log` summary")
w("")
if not audit_present:
    w("(no `audit_log` table found)")
else:
    w(f"Total rows: **{table_rows['audit_log']:,}**")
    w(f"Columns: {', '.join('`' + c + '`' for c in audit_cols)}")
    w("")

    # Action breakdown
    if audit_action_col:
        w(f"### 6a. Counts by `{audit_action_col}`")
        w("")
        w(f"| {audit_action_col} | Count |")
        w("|---|---:|")
        rows = cur.execute(
            f'SELECT "{audit_action_col}", COUNT(*) FROM audit_log '
            f'GROUP BY "{audit_action_col}" ORDER BY 2 DESC'
        ).fetchall()
        for r in rows:
            label = r[0] if r[0] is not None else "(NULL)"
            w(f"| `{label}` | {r[1]:,} |")
        w("")

    # Full dump (truncate long cell values)
    w("### 6b. All rows")
    w("")
    order_by = f'ORDER BY "{audit_id_col}"' if audit_id_col else ""
    select_cols = ", ".join(f'"{c}"' for c in audit_cols)
    rows = cur.execute(f"SELECT {select_cols} FROM audit_log {order_by}").fetchall()
    w("| " + " | ".join(audit_cols) + " |")
    w("|" + "|".join(["---"] * len(audit_cols)) + "|")
    for r in rows:
        cells = []
        for v in r:
            if v is None:
                cells.append("")
            else:
                s = str(v).replace("|", "\\|").replace("\n", " ").replace("\r", " ")
                if len(s) > 100:
                    s = s[:97] + "..."
                cells.append(s)
        w("| " + " | ".join(cells) + " |")
    w("")

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
w("---")
w("")
w("End of inventory. Read-only; no DB writes performed.")
w("")

# ---------------------------------------------------------------------------
# Write
# ---------------------------------------------------------------------------
os.makedirs("recon", exist_ok=True)
with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

conn.close()

print(f"OK  wrote {OUT_PATH}")
print(f"    tables       : {len(tables)}")
print(f"    total rows   : {total_rows:,}")
print(f"    db size      : {db_size_mb:,.1f} MB")
print(f"    output lines : {len(lines):,}")
