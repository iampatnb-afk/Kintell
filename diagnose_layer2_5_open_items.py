"""
diagnose_layer2_5_open_items.py — read-only.

Investigates three open items from sub-pass 2.5.1:
  1. median_income returned 0 rows for 2025 — what's happening?
  2. seifa_irsd has no source — where does SEIFA actually live?
  3. new_competitor_12m = 0 everywhere — date format issue?

No DB writes.
"""

import os
import sqlite3

DB_PATH = os.path.join("data", "kintell.db")


def section(title):
    print()
    print("=" * 72)
    print(f"  {title}")
    print("=" * 72)


def main():
    if not os.path.exists(DB_PATH):
        print(f"ERROR: {DB_PATH} missing")
        return

    uri = f"file:{DB_PATH}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    cur = conn.cursor()

    # ------------------------------------------------------------------
    # ISSUE 1: median_income year/value distribution
    # ------------------------------------------------------------------
    section("ISSUE 1 — median_equiv_household_income_weekly per year")
    cur.execute(
        "SELECT year, COUNT(*) AS rows, "
        "COUNT(value) AS non_null_rows, "
        "ROUND(AVG(value), 2) AS avg_val "
        "FROM abs_sa2_socioeconomic_annual "
        "WHERE metric_name = 'median_equiv_household_income_weekly' "
        "GROUP BY year ORDER BY year"
    )
    rows = cur.fetchall()
    print(f"{'year':<8}{'rows':>8}{'non-null':>10}{'avg_value':>14}")
    for y, n, nn, av in rows:
        print(f"{y:<8}{n:>8,}{nn:>10,}{str(av):>14}")

    print()
    print("All metric_name year-counts (for context):")
    cur.execute(
        "SELECT metric_name, MIN(year), MAX(year), COUNT(DISTINCT year) "
        "FROM abs_sa2_socioeconomic_annual GROUP BY metric_name"
    )
    for m, y0, y1, ny in cur.fetchall():
        print(f"  {m:<50} {y0}–{y1} ({ny} years)")

    # ------------------------------------------------------------------
    # ISSUE 2: SEIFA — where does it live?
    # ------------------------------------------------------------------
    section("ISSUE 2 — SEIFA source hunt")
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' "
        "ORDER BY name"
    )
    all_tables = [r[0] for r in cur.fetchall()]

    matches = []
    for t in all_tables:
        cur.execute(f"PRAGMA table_info({t})")
        cols = [r[1] for r in cur.fetchall()]
        for c in cols:
            cl = c.lower()
            if any(k in cl for k in ("seifa", "irsd", "irsad",
                                      "ier", "ieo", "decile")):
                matches.append((t, c))

    if not matches:
        print("No tables/columns with SEIFA-like names found.")
    else:
        print(f"Found {len(matches)} candidate (table, column) pairs:")
        for t, c in matches:
            try:
                cur.execute(
                    f"SELECT COUNT(*), COUNT({c}), "
                    f"MIN({c}), MAX({c}) FROM {t}"
                )
                n, nn, mn, mx = cur.fetchone()
                print(f"  {t}.{c:<22} rows={n:,} "
                      f"non-null={nn:,} min={mn} max={mx}")
            except Exception as e:
                print(f"  {t}.{c}: ERR {e}")

    # ------------------------------------------------------------------
    # ISSUE 3: approval_granted_date format and recency
    # ------------------------------------------------------------------
    section("ISSUE 3 — services.approval_granted_date inspection")

    # Coverage
    cur.execute(
        "SELECT COUNT(*) AS total, "
        "COUNT(approval_granted_date) AS non_null, "
        "MIN(approval_granted_date), MAX(approval_granted_date) "
        "FROM services WHERE is_active = 1 "
        "AND sa2_code IS NOT NULL"
    )
    total, nn, mn, mx = cur.fetchone()
    print(f"Active services: {total:,}")
    print(f"  approval_granted_date non-null: {nn:,} "
          f"({nn / total * 100:.1f}%)")
    print(f"  range: {mn!r}  →  {mx!r}")

    # Sample 10 distinct values
    cur.execute(
        "SELECT DISTINCT approval_granted_date FROM services "
        "WHERE approval_granted_date IS NOT NULL "
        "ORDER BY RANDOM() LIMIT 10"
    )
    print()
    print("Sample distinct values:")
    for (d,) in cur.fetchall():
        print(f"  {d!r}")

    # Test julianday() on a sample
    print()
    print("julianday() compatibility test:")
    cur.execute(
        "SELECT approval_granted_date, "
        "julianday(approval_granted_date) AS j "
        "FROM services "
        "WHERE approval_granted_date IS NOT NULL "
        "ORDER BY RANDOM() LIMIT 5"
    )
    for d, j in cur.fetchall():
        print(f"  {d!r:<20} -> julianday={j}")

    # How many fall within last 365 days from now?
    cur.execute(
        "SELECT COUNT(*) FROM services "
        "WHERE is_active = 1 AND sa2_code IS NOT NULL "
        "AND approval_granted_date IS NOT NULL "
        "AND julianday(approval_granted_date) >= "
        "    julianday('now', '-365 days')"
    )
    n_recent = cur.fetchone()[0]
    print(f"\nServices opened in last 365 days (julianday-based): "
          f"{n_recent:,}")

    # And within last 5 years for comparison
    cur.execute(
        "SELECT COUNT(*) FROM services "
        "WHERE is_active = 1 AND sa2_code IS NOT NULL "
        "AND approval_granted_date IS NOT NULL "
        "AND julianday(approval_granted_date) >= "
        "    julianday('now', '-1825 days')"
    )
    n_5yr = cur.fetchone()[0]
    print(f"Services opened in last 5 years: {n_5yr:,}")

    # And check what 'now' resolves to
    cur.execute("SELECT date('now')")
    print(f"SQLite date('now') = {cur.fetchone()[0]}")

    conn.close()


if __name__ == "__main__":
    main()
