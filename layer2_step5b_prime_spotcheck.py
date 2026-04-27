"""
Layer 2 Step 5b-prime — Spotcheck (read-only).
================================================
Real queries against the now-committed abs_sa2_education_employment_annual
table. Verifies:
  1. Schema + indexes present
  2. Sample SA2 trajectories (Braidwood, Sydney inner, regional)
  3. Female LFP distribution by state (Decision 54 stratification)
  4. RWCI input cross-check on a sample SA2
  5. Cross-source validation: ee_lfp_persons_pct vs derived persons LFP
     (computed on-the-fly from T33 CSV — should be near-identical)

Outputs:
  recon/layer2_step5b_prime_spotcheck.md
"""

import csv
import sqlite3
from pathlib import Path
from collections import defaultdict
from datetime import datetime

DB_PATH = Path("data/kintell.db")
T33_CSV = Path("recon/layer2_step5b_prime_t33_derived.csv")
RECON_DIR = Path("recon")
OUT_MD = RECON_DIR / "layer2_step5b_prime_spotcheck.md"

TABLE = "abs_sa2_education_employment_annual"

# Sample SA2s for trajectory inspection
SAMPLE_SA2S = [
    ("101011001", "Braidwood (NSW regional)"),
    ("117031337", "Sydney - Haymarket / The Rocks (NSW inner)"),
    ("206011105", "Carlton (VIC inner)"),
    ("306011124", "Spring Hill (QLD inner)"),
]

# Some flexibility: these codes may not match exactly. Script will fall back
# to "first 4 SA2s with full trajectory" if a target is missing.


def main():
    RECON_DIR.mkdir(exist_ok=True)
    L = []

    def out(s=""):
        print(s)
        L.append(s)

    out("# Layer 2 Step 5b-prime — Spotcheck")
    out(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    out("")

    if not DB_PATH.exists():
        out(f"ERROR: DB missing at {DB_PATH}")
        OUT_MD.write_text("\n".join(L), encoding="utf-8")
        return

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 1. Schema + indexes
    out("## 1. Schema + indexes")
    out("")
    cur.execute(f"SELECT sql FROM sqlite_master WHERE name=?", (TABLE,))
    row = cur.fetchone()
    if row:
        out("```sql")
        out(row[0])
        out("```")
    cur.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name=? AND name NOT LIKE 'sqlite_%'", (TABLE,))
    idxs = cur.fetchall()
    out("")
    out(f"Indexes ({len(idxs)}):")
    for r in idxs:
        out(f"  - {r['name']}")
    out("")

    # Quick row + metric count
    cur.execute(f"SELECT COUNT(*), COUNT(DISTINCT metric_name), COUNT(DISTINCT sa2_code) FROM {TABLE}")
    n, nm, ns = cur.fetchone()
    out(f"Rows: {n:,} | metrics: {nm} | distinct SA2s: {ns:,}")
    out("")

    # 2. Sample SA2 trajectories
    out("## 2. Sample SA2 trajectories")
    out("")

    # Resolve sample SA2s — use defined codes if present in DB, else fallback
    used_samples = []
    for code, label in SAMPLE_SA2S:
        cur.execute(f"SELECT COUNT(*) FROM {TABLE} WHERE sa2_code=?", (code,))
        if cur.fetchone()[0] > 0:
            used_samples.append((code, label))
    if len(used_samples) < 4:
        # Fallback: first 4 SA2s with rows in all three census years for ee_lfp_persons_pct
        cur.execute(f"""
            SELECT sa2_code FROM {TABLE}
            WHERE metric_name = 'ee_lfp_persons_pct'
            GROUP BY sa2_code
            HAVING COUNT(DISTINCT year) = 3
            ORDER BY sa2_code
            LIMIT 4
        """)
        for r in cur.fetchall():
            if not any(r[0] == c for c, _ in used_samples):
                used_samples.append((r[0], "(fallback sample)"))
        used_samples = used_samples[:4]

    for code, label in used_samples:
        out(f"### SA2 `{code}` — {label}")
        out("")
        out("**Census trajectory** (2011 → 2016 → 2021):")
        out("")
        out("| Metric | 2011 | 2016 | 2021 |")
        out("|:-------|-----:|-----:|-----:|")
        for metric in ["ee_year12_completion_pct", "ee_bachelor_degree_pct",
                       "ee_lfp_persons_pct", "ee_unemployment_rate_persons_pct",
                       "census_lfp_females_pct", "census_lfp_males_pct",
                       "ee_managers_pct", "ee_professionals_pct", "ee_clerical_admin_pct"]:
            cur.execute(f"SELECT year, value FROM {TABLE} WHERE sa2_code=? AND metric_name=? ORDER BY year",
                        (code, metric))
            vals = {r['year']: r['value'] for r in cur.fetchall()}
            row = f"| {metric}"
            for y in [2011, 2016, 2021]:
                v = vals.get(y)
                row += f" | {v:.2f}" if v is not None else " | —"
            row += " |"
            out(row)
        out("")
        out("**Annual trajectory** (preschool 4yo + total jobs):")
        out("")
        out("| Year | preschool 4yo | total jobs | female jobs | info_media | finance | prof_sci |")
        out("|-----:|-------------:|----------:|-----------:|----------:|-------:|---------:|")
        years = sorted(set())
        cur.execute(f"SELECT DISTINCT year FROM {TABLE} WHERE sa2_code=? AND metric_name='ee_jobs_total_count' ORDER BY year",
                    (code,))
        years = [r[0] for r in cur.fetchall()]
        for y in years:
            row = f"| {y}"
            for m in ["ee_preschool_4yo_count", "ee_jobs_total_count",
                      "ee_jobs_females_count", "ee_jobs_info_media_count",
                      "ee_jobs_finance_count", "ee_jobs_professional_scientific_count"]:
                cur.execute(f"SELECT value FROM {TABLE} WHERE sa2_code=? AND year=? AND metric_name=?",
                            (code, y, m))
                r = cur.fetchone()
                v = r[0] if r else None
                row += f" | {int(v):,}" if v is not None else " | —"
            row += " |"
            out(row)
        out("")

    # 3. Female LFP distribution by state (using SA2 code first digit as state proxy)
    out("## 3. Female LFP distribution by state (2021)")
    out("")
    out("State derived from SA2 code first digit (1=NSW, 2=VIC, 3=QLD, 4=SA, "
        "5=WA, 6=TAS, 7=NT, 8=ACT, 9=Other Territories).")
    out("")
    out("| State | n SA2s | min | p25 | median | p75 | max | mean |")
    out("|------:|------:|----:|----:|------:|----:|----:|-----:|")
    cur.execute(f"""
        SELECT substr(sa2_code, 1, 1) AS state_digit, value
        FROM {TABLE}
        WHERE metric_name = 'census_lfp_females_pct' AND year = 2021
          AND value BETWEEN 0 AND 100
        ORDER BY state_digit, value
    """)
    by_state = defaultdict(list)
    for r in cur.fetchall():
        by_state[r['state_digit']].append(r['value'])
    state_names = {"1": "NSW", "2": "VIC", "3": "QLD", "4": "SA",
                   "5": "WA", "6": "TAS", "7": "NT", "8": "ACT", "9": "OT"}
    for sd in sorted(by_state.keys()):
        vals = sorted(by_state[sd])
        n = len(vals)
        if n == 0:
            continue
        p25 = vals[n // 4]
        p50 = vals[n // 2]
        p75 = vals[3 * n // 4]
        mean = sum(vals) / n
        label = state_names.get(sd, f"({sd})")
        out(f"| {label} | {n} | {vals[0]:.1f} | {p25:.1f} | {p50:.1f} | "
            f"{p75:.1f} | {vals[-1]:.1f} | {mean:.1f} |")
    out("")

    # 4. RWCI input cross-check — top 10 SA2s by occupation knowledge share
    out("## 4. RWCI inputs — top 10 SA2s by occupation knowledge share (2021)")
    out("")
    out("Occupation knowledge share = managers + professionals + clerical (%).")
    out("Inner-city / professional-services SA2s should dominate.")
    out("")
    cur.execute(f"""
        WITH occ AS (
          SELECT sa2_code,
                 SUM(CASE WHEN metric_name = 'ee_managers_pct' THEN value END) AS mgr,
                 SUM(CASE WHEN metric_name = 'ee_professionals_pct' THEN value END) AS prof,
                 SUM(CASE WHEN metric_name = 'ee_clerical_admin_pct' THEN value END) AS clerk
          FROM {TABLE}
          WHERE metric_name IN ('ee_managers_pct', 'ee_professionals_pct', 'ee_clerical_admin_pct')
            AND year = 2021
            AND value BETWEEN 0 AND 100
          GROUP BY sa2_code
        )
        SELECT sa2_code, mgr, prof, clerk, (mgr + prof + clerk) AS knowledge_share
        FROM occ
        WHERE mgr IS NOT NULL AND prof IS NOT NULL AND clerk IS NOT NULL
        ORDER BY knowledge_share DESC
        LIMIT 10
    """)
    out("| SA2 | Mgr % | Prof % | Clerical % | Knowledge share % |")
    out("|:----|-----:|------:|----------:|----------------:|")
    for r in cur.fetchall():
        out(f"| {r['sa2_code']} | {r['mgr']:.1f} | {r['prof']:.1f} | "
            f"{r['clerk']:.1f} | {r['knowledge_share']:.1f} |")
    out("")

    out("## 5. RWCI inputs — top 10 SA2s by industry knowledge share (latest year)")
    out("")
    out("Industry knowledge share = (info_media + finance + prof_sci + admin_support) / total_jobs.")
    out("")
    cur.execute(f"""
        SELECT MAX(year) FROM {TABLE} WHERE metric_name = 'ee_jobs_total_count'
    """)
    latest = cur.fetchone()[0]
    out(f"Latest year: {latest}")
    out("")

    cur.execute(f"""
        WITH ind AS (
          SELECT sa2_code,
                 SUM(CASE WHEN metric_name = 'ee_jobs_info_media_count' THEN value END) AS info,
                 SUM(CASE WHEN metric_name = 'ee_jobs_finance_count' THEN value END) AS fin,
                 SUM(CASE WHEN metric_name = 'ee_jobs_professional_scientific_count' THEN value END) AS prof,
                 SUM(CASE WHEN metric_name = 'ee_jobs_admin_support_count' THEN value END) AS admin,
                 SUM(CASE WHEN metric_name = 'ee_jobs_total_count' THEN value END) AS tot
          FROM {TABLE}
          WHERE metric_name IN (
              'ee_jobs_info_media_count', 'ee_jobs_finance_count',
              'ee_jobs_professional_scientific_count', 'ee_jobs_admin_support_count',
              'ee_jobs_total_count')
            AND year = ?
          GROUP BY sa2_code
        )
        SELECT sa2_code, info, fin, prof, admin, tot,
               100.0 * (info + fin + prof + admin) / tot AS knowledge_pct
        FROM ind
        WHERE info IS NOT NULL AND fin IS NOT NULL AND prof IS NOT NULL
          AND admin IS NOT NULL AND tot IS NOT NULL AND tot > 100
        ORDER BY knowledge_pct DESC
        LIMIT 10
    """, (latest,))
    out("| SA2 | info | finance | prof_sci | admin | total | knowledge % |")
    out("|:----|-----:|-------:|--------:|------:|------:|-----------:|")
    for r in cur.fetchall():
        out(f"| {r['sa2_code']} | {int(r['info']):,} | {int(r['fin']):,} | "
            f"{int(r['prof']):,} | {int(r['admin']):,} | {int(r['tot']):,} | "
            f"{r['knowledge_pct']:.1f} |")
    out("")

    # 6. Cross-source validation: ee_lfp_persons_pct (EE DB) vs T33-derived
    out("## 6. Cross-source validation — EE DB col 55 vs T33-derived persons LFP")
    out("")
    out("Both should report the same Census persons LFP rate per (SA2, year). "
        "Material divergence indicates a source mismatch.")
    out("")

    # Build T33 persons LFP map from CSV
    t33_lookup = {}  # (sa2, year) -> lfp_persons_pct
    if T33_CSV.exists():
        with open(T33_CSV, "r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                if row.get("sex") != "P":
                    continue
                try:
                    t33_lookup[(row["sa2_code"], int(row["year"]))] = float(row["lfp_rate_pct"]) if row["lfp_rate_pct"] else None
                except (ValueError, TypeError):
                    continue

    cur.execute(f"""
        SELECT sa2_code, year, value
        FROM {TABLE}
        WHERE metric_name = 'ee_lfp_persons_pct'
          AND value BETWEEN 0 AND 100
    """)
    diffs = []
    for r in cur.fetchall():
        key = (r['sa2_code'], r['year'])
        t33_val = t33_lookup.get(key)
        if t33_val is None:
            continue
        diffs.append(abs(r['value'] - t33_val))

    if diffs:
        n = len(diffs)
        diffs.sort()
        out(f"Compared {n:,} (SA2, year) pairs in [0, 100] range.")
        out("")
        out(f"- mean abs difference: {sum(diffs)/n:.3f} pp")
        out(f"- median abs diff:     {diffs[n//2]:.3f} pp")
        out(f"- p95 abs diff:        {diffs[int(n*0.95)]:.3f} pp")
        out(f"- max abs diff:        {diffs[-1]:.3f} pp")
    else:
        out("(no overlap to compare — unexpected)")
    out("")

    conn.close()
    OUT_MD.write_text("\n".join(L), encoding="utf-8")
    print(f"\nWritten to: {OUT_MD}")


if __name__ == "__main__":
    main()
