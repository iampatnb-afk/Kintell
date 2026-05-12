"""
A1 follow-up probe — locate the 6-year window filter.

The previous probe established that abs_sa2_erp_annual has all 9 years
(2011, 2016, 2018, 2019-2024) of under_5_persons data. So the 6-year
window OI-30 surfaced is being imposed downstream. This probe finds where.

Read-only. Run from repo root:
    python recon\probes\probe_a1_filter_source.py
"""

import json
import re
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path("data") / "kintell.db"
HISTORY_JSON = Path("docs") / "sa2_history.json"
REPO_ROOT = Path(".")


def section(title):
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def main():
    if not DB_PATH.exists():
        print(f"ERROR: {DB_PATH} not found. Run from repo root.", file=sys.stderr)
        sys.exit(1)

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    section("1. Bayswater 211011251 under_5_persons by year (raw DB)")
    rows = cur.execute(
        "SELECT year, persons FROM abs_sa2_erp_annual "
        "WHERE sa2_code = '211011251' AND age_group = 'under_5_persons' "
        "ORDER BY year"
    ).fetchall()
    if not rows:
        print("  No under_5_persons rows for this SA2 in DB.")
    else:
        for y, p in rows:
            print(f"  {y}: {p}")
        print(f"  -> {len(rows)} years of data in DB")

    section("2. Bondi Junction-Waverly 118011341 under_5_persons by year (raw DB)")
    rows = cur.execute(
        "SELECT year, persons FROM abs_sa2_erp_annual "
        "WHERE sa2_code = '118011341' AND age_group = 'under_5_persons' "
        "ORDER BY year"
    ).fetchall()
    if not rows:
        print("  No under_5_persons rows for this SA2 in DB.")
    else:
        for y, p in rows:
            print(f"  {y}: {p}")
        print(f"  -> {len(rows)} years of data in DB")

    con.close()

    section("3. sa2_history.json contents for Bayswater 211011251")
    if not HISTORY_JSON.exists():
        print(f"  {HISTORY_JSON} not found.")
    else:
        try:
            data = json.loads(HISTORY_JSON.read_text(encoding="utf-8"))
            entry = data.get("211011251") or data.get(211011251)
            if entry is None:
                print("  SA2 211011251 not found in sa2_history.json")
            else:
                print(f"  Top-level keys: {sorted(entry.keys())}")
                for key in entry.keys():
                    val = entry[key]
                    if isinstance(val, dict):
                        sample_year_keys = []
                        for sub_k, sub_v in val.items():
                            if isinstance(sub_v, list) and sub_v:
                                periods = [
                                    p.get("period") if isinstance(p, dict) else None
                                    for p in sub_v[:3]
                                ]
                                last_periods = [
                                    p.get("period") if isinstance(p, dict) else None
                                    for p in sub_v[-3:]
                                ]
                                print(f"    {key}.{sub_k}: {len(sub_v)} points; "
                                      f"first={periods}, last={last_periods}")
                                sample_year_keys.append(sub_k)
                            elif isinstance(sub_v, dict):
                                print(f"    {key}.{sub_k}: dict with keys "
                                      f"{list(sub_v.keys())[:5]}")
                            if len(sample_year_keys) >= 3:
                                break
                    elif isinstance(val, list):
                        print(f"    {key}: list of {len(val)} items")
                    else:
                        print(f"    {key}: {type(val).__name__} = {val!r:.80}")
        except Exception as e:
            print(f"  Error reading sa2_history.json: {e}")

    section("4. Codebase scan — files containing '2019' near 'year' or 'period'")
    candidate_patterns = [
        re.compile(r"year\s*>=\s*2019"),
        re.compile(r"year\s*>\s*2018"),
        re.compile(r"WHERE.*year.*2019", re.IGNORECASE),
        re.compile(r"period.*2019"),
        re.compile(r"start.*2019"),
        re.compile(r"min.*year.*2019"),
        re.compile(r"\b2019\b"),
    ]
    py_files = sorted(REPO_ROOT.glob("*.py"))
    py_files += sorted((REPO_ROOT / "recon").glob("*.py")) if (REPO_ROOT / "recon").exists() else []
    hits = {}
    for f in py_files:
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        for i, line in enumerate(text.splitlines(), start=1):
            for pat in candidate_patterns:
                if pat.search(line):
                    hits.setdefault(str(f), []).append((i, line.strip()))
                    break
    if not hits:
        print("  No matches.")
    else:
        for f, matches in hits.items():
            print(f"\n  {f} ({len(matches)} matches)")
            for line_no, line in matches[:8]:
                trimmed = line if len(line) <= 110 else line[:107] + "..."
                print(f"    L{line_no}: {trimmed}")
            if len(matches) > 8:
                print(f"    ... and {len(matches) - 8} more")

    section("5. Codebase scan — files containing 'sa2_history' or 'under_5_persons'")
    keywords = ["sa2_history", "under_5_persons", "abs_sa2_erp_annual", "build_sa2_history"]
    keyword_hits = {kw: [] for kw in keywords}
    for f in py_files:
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        for kw in keywords:
            if kw in text:
                count = text.count(kw)
                keyword_hits[kw].append((str(f), count))
    for kw, files in keyword_hits.items():
        if files:
            print(f"\n  '{kw}':")
            for fname, count in files:
                print(f"    {fname} ({count} occurrences)")
        else:
            print(f"\n  '{kw}': no matches")

    print()
    print("Done. Read-only probe — no DB mutation.")


if __name__ == "__main__":
    main()
