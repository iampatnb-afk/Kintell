"""
inventory_for_layer2_5.py — read-only DB inventory.

Lists every table in data/kintell.db with row count and columns.
Highlights tables matching keyword patterns that Layer 2.5 needs:
  ERP / population (u5_pop)
  LFP (female_lfp_pct)
  income (median_income, calibration nudge)
  SEIFA (seifa_irsd)
  SALM / unemployment (unemployment_pct)
  IVI / vacancies
  CCS (ccs_dependency_pct)
  cohort / banding

No DB writes. Safe to run anytime.
"""

import os
import sqlite3
from collections import defaultdict

DB_PATH = os.path.join("data", "kintell.db")

KEYWORD_BUCKETS = {
    "ERP / pop / births": ("erp", "pop", "birth", "u5",
                           "under5", "under_5"),
    "LFP / labour": ("lfp", "labour", "labor"),
    "Income": ("income", "earn"),
    "SEIFA": ("seifa", "irsd", "irsad", "ier", "ieo"),
    "SALM / unemployment": ("salm", "unemploy"),
    "IVI / vacancies": ("ivi", "vacanc", "jsa"),
    "CCS / subsidy": ("ccs", "subsidy"),
    "Cohort / banding / Layer 3": ("cohort", "band", "layer3",
                                    "decile"),
    "Services / NQS / ACECQA": ("service", "nqs", "acecqa",
                                 "provider"),
}


def main():
    if not os.path.exists(DB_PATH):
        print(f"ERROR: DB not found at {DB_PATH}")
        return

    uri = f"file:{DB_PATH}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    cur = conn.cursor()

    cur.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type='table' ORDER BY name"
    )
    all_tables = [r[0] for r in cur.fetchall()]
    print(f"Total tables: {len(all_tables)}")
    print()

    # Bucket tables by keyword
    buckets = defaultdict(list)
    for t in all_tables:
        tl = t.lower()
        matched = False
        for label, kws in KEYWORD_BUCKETS.items():
            if any(kw in tl for kw in kws):
                buckets[label].append(t)
                matched = True
                break
        if not matched:
            buckets["Other"].append(t)

    # Print bucketed inventory
    for label in list(KEYWORD_BUCKETS.keys()) + ["Other"]:
        tables = buckets.get(label, [])
        if not tables:
            continue
        print("=" * 72)
        print(f"  {label}  ({len(tables)} tables)")
        print("=" * 72)
        for t in tables:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {t}")
                n = cur.fetchone()[0]
            except Exception as e:
                n = f"ERR: {e}"
            cur.execute(f"PRAGMA table_info({t})")
            cols = [r[1] for r in cur.fetchall()]
            print(f"\n  {t}  ({n:,} rows)" if isinstance(n, int)
                  else f"\n  {t}  ({n})")
            # Print columns wrapped to 70 chars
            line = "    cols: "
            for c in cols:
                if len(line) + len(c) + 2 > 72:
                    print(line)
                    line = "          "
                line += c + ", "
            if line.strip() != "cols:":
                print(line.rstrip(", "))
        print()

    conn.close()


if __name__ == "__main__":
    main()
