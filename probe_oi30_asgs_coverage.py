"""
probe_oi30_asgs_coverage.py — read-only probe of pop_0_4 coverage gaps.

Origin: OI-30. Layer 4.2-A.3c verification surfaced that Bayswater
(SA2 211011251) lacks pre-2019 pop_0_4 data — supply_ratio is None
for the 27 pre-2019 quarters. Hypothesis: 211011251 is a 2021-ASGS
code; pre-2019 ABS data uses 2016-ASGS codes for the same suburb
under a different code.

This probe quantifies the issue across the full SA2 set anchored by
the platform: coverage depth distribution, earliest-data-year
distribution, anchor-SA2 verification, top-30 sparsest examples.
Output informs V1.5 ingest fix scope.

Read-only. No DB mutations.
Output: recon/oi30_asgs_coverage_probe.md
"""

import sqlite3
from collections import Counter
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent
DB = REPO / "data" / "kintell.db"
OUT = REPO / "recon" / "oi30_asgs_coverage_probe.md"

ANCHORS = [
    ("211011251", "Sparrow Bayswater LDC (svc 2358) — known sparse"),
    ("118011341", "Bondi Junction-Waverly (svc 103) — likely full"),
]


def main() -> None:
    if not DB.exists():
        raise FileNotFoundError(f"DB not found at {DB}")

    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row

    print("=" * 64)
    print("OI-30 probe: pop_0_4 coverage across catchment-anchored SA2s")
    print("=" * 64)

    cols_erp = [r["name"] for r in con.execute("PRAGMA table_info(abs_sa2_erp_annual)")]
    print(f"\nabs_sa2_erp_annual cols: {cols_erp}")

    sa2s = [r["sa2_code"] for r in con.execute(
        "SELECT DISTINCT sa2_code FROM service_catchment_cache "
        "WHERE sa2_code IS NOT NULL"
    )]
    print(f"Distinct SA2s in service_catchment_cache: {len(sa2s)}")

    sql = (
        "SELECT COUNT(DISTINCT year) AS n_years, "
        "       MIN(year) AS first_year, MAX(year) AS last_year "
        "FROM abs_sa2_erp_annual "
        "WHERE sa2_code = ? AND age_group = 'under_5_persons' "
        "  AND persons IS NOT NULL"
    )

    coverage = {}
    for s in sa2s:
        r = con.execute(sql, (s,)).fetchone()
        coverage[s] = (r["n_years"] or 0, r["first_year"], r["last_year"])

    buckets = Counter()
    first_year_dist = Counter()
    for s, (n, fy, _) in coverage.items():
        if n == 0:
            buckets["zero"] += 1
        elif n >= 12:
            buckets["full (>=12 years)"] += 1
        elif n >= 6:
            buckets["partial (6-11 years)"] += 1
        else:
            buckets["sparse (1-5 years)"] += 1
        if fy is not None:
            first_year_dist[fy] += 1

    print("\n--- Bucket distribution ---")
    for label, count in buckets.most_common():
        pct = 100 * count / max(len(sa2s), 1)
        print(f"  {label}: {count} ({pct:.1f}%)")

    print("\n--- Anchor SA2s ---")
    for code, note in ANCHORS:
        n, fy, ly = coverage.get(code, (0, None, None))
        print(f"  {code}: {n} years, range {fy}-{ly}  [{note}]")

    sparse = sorted(
        [(s, n, fy, ly) for s, (n, fy, ly) in coverage.items() if 0 < n < 12],
        key=lambda x: (x[1], x[2] or 9999)
    )
    zero = [(s, fy, ly) for s, (n, fy, ly) in coverage.items() if n == 0]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        f.write("# OI-30 probe — pop_0_4 coverage across catchment SA2s\n\n")
        f.write(f"*Run: {datetime.now().isoformat(timespec='seconds')}. Read-only probe per DEC-65.*\n\n")

        f.write("## Headline\n\n")
        f.write(f"- Distinct SA2s in `service_catchment_cache`: **{len(sa2s)}**\n")
        for label, count in buckets.most_common():
            pct = 100 * count / max(len(sa2s), 1)
            f.write(f"- {label}: **{count}** ({pct:.1f}%)\n")
        f.write("\n")

        f.write("## Earliest-year-of-data distribution\n\n")
        f.write("When does pop_0_4 data start for SA2s where it exists?\n\n")
        f.write("| First year | Count | % of covered SA2s |\n|---|---|---|\n")
        total_with_data = sum(first_year_dist.values())
        for yr in sorted(first_year_dist):
            c = first_year_dist[yr]
            pct = 100 * c / max(total_with_data, 1)
            f.write(f"| {yr} | {c} | {pct:.1f}% |\n")
        f.write("\n")

        f.write("## Anchor verification\n\n")
        for code, note in ANCHORS:
            n, fy, ly = coverage.get(code, (0, None, None))
            f.write(f"- `{code}`: **{n} years**, range {fy}-{ly} — {note}\n")
        f.write("\n")

        f.write(f"## Sparse SA2s (1-11 years) — top 30 of {len(sparse)}\n\n")
        f.write("| SA2 code | Years | First year | Last year |\n|---|---|---|---|\n")
        for s, n, fy, ly in sparse[:30]:
            f.write(f"| `{s}` | {n} | {fy} | {ly} |\n")
        f.write("\n")

        f.write(f"## Zero-coverage SA2s ({len(zero)} total)\n\n")
        if zero:
            f.write("First 20 listed:\n\n")
            f.write("| SA2 code |\n|---|\n")
            for s, _, _ in zero[:20]:
                f.write(f"| `{s}` |\n")
            f.write("\n")
        else:
            f.write("None — every catchment-anchored SA2 has at least 1 year of pop_0_4 data.\n\n")

        f.write("## Hypothesis assessment\n\n")
        f.write("If 2021-ASGS codes lack pre-2019 ABS data, expect:\n\n")
        f.write("- A meaningful cluster of SA2s with first_year >= 2019\n")
        f.write("- Bayswater (211011251) in that cluster\n")
        f.write("- Sparse SA2 codes follow 2021-ASGS patterns\n\n")
        f.write("Reader: cross-reference the first-year distribution. If most sparse SA2s start at 2019 or later, hypothesis is supported and the V1.5 fix is an ASGS concordance step in `build_sa2_history.py`.\n")

    con.close()
    print(f"\nReport written: {OUT}")
    print("=" * 64)


if __name__ == "__main__":
    main()
