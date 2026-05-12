"""
A1 scoping probe — read-only.

Four open questions:
1. Why is Bayswater 211011251 not appearing in sa2_history.json under
   string key when V1 was verified on it? Key format / coverage issue?
2. What does build_sa2_history.py read, and how does it filter years?
3. Why do 2011/2016/2018 rows exist in abs_sa2_erp_annual with NULL
   under_5_persons? (Audit trail — incomplete ingest or placeholder?)
4. Are pre-2019 under_5 figures available in another DB table
   (Census 2011/2016 SA2-level tables)?

Run from repo root:
    python recon\probes\probe_a1_scoping.py
"""

import json
import re
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path("data") / "kintell.db"
HISTORY_JSON = Path("docs") / "sa2_history.json"
BUILD_SCRIPT = Path("build_sa2_history.py")


def section(title):
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def main():
    if not DB_PATH.exists():
        print(f"ERROR: {DB_PATH} not found. Run from repo root.", file=sys.stderr)
        sys.exit(1)

    # --- Q1: Bayswater key format and coverage in sa2_history.json ---
    section("1. sa2_history.json structure + Bayswater coverage")
    if not HISTORY_JSON.exists():
        print(f"  {HISTORY_JSON} not found.")
    else:
        size_mb = HISTORY_JSON.stat().st_size / (1024 * 1024)
        print(f"  File size: {size_mb:.1f} MB")
        try:
            data = json.loads(HISTORY_JSON.read_text(encoding="utf-8"))
            keys = list(data.keys())
            print(f"  Total top-level keys: {len(keys)}")
            print(f"  First 5 keys: {keys[:5]}")
            print(f"  Key type: {type(keys[0]).__name__ if keys else 'n/a'}")
            print(f"  '211011251' (Bayswater) as string key: {'211011251' in data}")
            print(f"  211011251 (Bayswater) as int key: {211011251 in data}")
            near = [k for k in keys if "21101" in str(k)][:10]
            print(f"  Keys containing '21101': {near}")
            print(f"  '118011341' (Bondi) as string key: {'118011341' in data}")

            # Sample one present key to understand structure
            sample_key = keys[0] if keys else None
            if sample_key is not None:
                entry = data[sample_key]
                print(f"\n  Sample entry for {sample_key}:")
                if isinstance(entry, dict):
                    print(f"    Top-level keys: {sorted(entry.keys())[:10]}")
                    for k, v in list(entry.items())[:3]:
                        if isinstance(v, dict):
                            sub = list(v.keys())[:5]
                            print(f"    {k}: dict with sub-keys {sub}")
                        elif isinstance(v, list):
                            print(f"    {k}: list of {len(v)} items")
                        else:
                            print(f"    {k}: {type(v).__name__}")
        except Exception as e:
            print(f"  Error reading sa2_history.json: {e}")

    # --- Q2: build_sa2_history.py — what SQL does it run? ---
    section("2. build_sa2_history.py — SQL queries and age_group filters")
    if not BUILD_SCRIPT.exists():
        print(f"  {BUILD_SCRIPT} not found.")
    else:
        text = BUILD_SCRIPT.read_text(encoding="utf-8")
        print(f"  File size: {len(text):,} chars, {text.count(chr(10))} lines")

        # Find SQL queries (heuristic: look for SELECT or FROM lines)
        sql_lines = []
        for i, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if re.search(r"\bSELECT\b|\bFROM\b|\bWHERE\b", stripped, re.IGNORECASE):
                sql_lines.append((i, stripped))
        print(f"  SQL-keyword lines: {len(sql_lines)}")
        for i, line in sql_lines[:30]:
            trimmed = line if len(line) <= 110 else line[:107] + "..."
            print(f"    L{i}: {trimmed}")
        if len(sql_lines) > 30:
            print(f"    ... and {len(sql_lines) - 30} more")

        # age_group references
        ag_lines = [
            (i, line.strip())
            for i, line in enumerate(text.splitlines(), start=1)
            if "age_group" in line or "under_5" in line or "pop_0_4" in line
        ]
        print(f"\n  age_group / under_5 / pop_0_4 references: {len(ag_lines)}")
        for i, line in ag_lines[:20]:
            trimmed = line if len(line) <= 110 else line[:107] + "..."
            print(f"    L{i}: {trimmed}")

        # year-filter references
        year_lines = [
            (i, line.strip())
            for i, line in enumerate(text.splitlines(), start=1)
            if re.search(r"year\s*[<>=]|\bMIN_YEAR\b|\bSTART_YEAR\b|2019", line)
        ]
        print(f"\n  year-filter / 2019 references: {len(year_lines)}")
        for i, line in year_lines[:20]:
            trimmed = line if len(line) <= 110 else line[:107] + "..."
            print(f"    L{i}: {trimmed}")

    # --- Q3: 2011/2016/2018 NULL row audit trail ---
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    section("3. 2011/2016/2018 row audit — what's NULL vs not")
    rows = cur.execute(
        "SELECT year, age_group, "
        "       COUNT(*) AS total, "
        "       SUM(CASE WHEN persons IS NULL THEN 1 ELSE 0 END) AS nulls "
        "FROM abs_sa2_erp_annual "
        "WHERE year IN (2011, 2016, 2018, 2019) "
        "GROUP BY year, age_group "
        "ORDER BY year, age_group"
    ).fetchall()
    print(f"  {'year':<6}{'age_group':<22}{'total':>10}{'nulls':>10}")
    for y, ag, total, nulls in rows:
        print(f"  {y:<6}{ag:<22}{total:>10,}{nulls:>10,}")

    section("4. audit_log entries that touched abs_sa2_erp_annual")
    cur.execute("PRAGMA table_info(audit_log)")
    cols = [c[1] for c in cur.fetchall()]
    print(f"  audit_log columns: {cols}")
    if "table_name" in cols:
        rows = cur.execute(
            "SELECT * FROM audit_log "
            "WHERE table_name = 'abs_sa2_erp_annual' "
            "ORDER BY rowid DESC LIMIT 15"
        ).fetchall()
    else:
        # Fallback: search all text columns
        rows = cur.execute(
            "SELECT * FROM audit_log "
            "WHERE EXISTS (SELECT 1 FROM pragma_table_info('audit_log') t "
            "              WHERE t.type LIKE '%TEXT%') "
            "ORDER BY rowid DESC LIMIT 15"
        ).fetchall()
    print(f"  Recent audit_log rows touching abs_sa2_erp_annual: {len(rows)}")
    for row in rows[:10]:
        # Print first 4 columns + truncated rest
        head = ", ".join(str(v)[:40] for v in row[:6])
        print(f"    {head}")

    # --- Q4: Census 2011/2016 SA2-level tables ---
    section("5. DB tables that might hold pre-2019 under-5 figures")
    tables = cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    candidate_tables = []
    for (t,) in tables:
        name_lower = t.lower()
        if any(s in name_lower for s in ["census", "abs_", "sa2", "erp", "pop"]):
            candidate_tables.append(t)
    print(f"  Candidate tables ({len(candidate_tables)}):")
    for t in candidate_tables:
        try:
            row_count = cur.execute(f"SELECT COUNT(*) FROM \"{t}\"").fetchone()[0]
        except Exception:
            row_count = "?"
        print(f"    {t} ({row_count} rows)")

    # For each candidate that mentions year, show year coverage
    section("6. Year coverage in candidate tables (where 'year' col exists)")
    for t in candidate_tables:
        try:
            cols_t = [c[1] for c in cur.execute(f"PRAGMA table_info(\"{t}\")").fetchall()]
        except Exception:
            continue
        year_col = next((c for c in cols_t if c.lower() in ("year", "ref_year", "census_year")), None)
        if year_col is None:
            continue
        try:
            yrs = cur.execute(
                f"SELECT DISTINCT \"{year_col}\" FROM \"{t}\" ORDER BY \"{year_col}\""
            ).fetchall()
            yr_list = [y[0] for y in yrs]
            print(f"    {t}.{year_col}: {yr_list[:15]}{' ...' if len(yr_list) > 15 else ''}")
        except Exception as e:
            print(f"    {t}.{year_col}: error {e}")

    con.close()
    print()
    print("Done. Read-only probe — no DB mutation.")


if __name__ == "__main__":
    main()
