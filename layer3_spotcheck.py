"""
layer3_spotcheck.py

Read-only post-apply spotcheck of:
  - sa2_cohort (Layer 3 prep)
  - layer3_sa2_metric_banding (Layer 3 banding)

Validates 10 invariants and dumps a sample-SA2 profile for spot review.

Output: recon/layer3_spotcheck.md
No DB writes.

Usage:
  python layer3_spotcheck.py
"""
import sqlite3
from collections import Counter
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
DB_PATH = REPO_ROOT / "data" / "kintell.db"
OUT_PATH = REPO_ROOT / "recon" / "layer3_spotcheck.md"

# Sample SA2s to dump full profiles for (representative across cohorts)
SAMPLE_SA2_CODES = [
    "117031606",  # NSW Sydney CBD-ish (let validator pick if not present)
    "206041122",  # VIC Melbourne CBD-ish
    "305031120",  # QLD outback
    "208021180",  # VIC regional
    "117011320",  # the one in our dryrun sample
]


def fmt_int(n):
    return f"{n:,}" if n is not None else "n/a"


def main():
    print("layer3_spotcheck - read-only", flush=True)
    print(f"DB: {DB_PATH}")
    print()

    if not DB_PATH.exists():
        print(f"ERROR: DB not found")
        return 1

    uri = f"file:{DB_PATH.as_posix()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    cur = conn.cursor()

    invariants = []   # list of (label, passed: bool, detail: str)
    detail_blocks = []  # list of (heading, text) for the markdown

    # Invariant 1 — row count
    cur.execute("SELECT COUNT(*) FROM layer3_sa2_metric_banding")
    total_rows = cur.fetchone()[0]
    invariants.append((
        "Total row count > 10,000",
        total_rows > 10_000,
        f"layer3_sa2_metric_banding rows = {total_rows:,}",
    ))

    # Invariant 2 — PK uniqueness
    cur.execute("""
        SELECT COUNT(*) FROM (
            SELECT sa2_code, metric, year, cohort_def, COUNT(*) AS n
              FROM layer3_sa2_metric_banding
          GROUP BY sa2_code, metric, year, cohort_def
            HAVING n > 1
        )
    """)
    dup_pk = cur.fetchone()[0]
    invariants.append((
        "PK (sa2_code, metric, year, cohort_def) is unique",
        dup_pk == 0,
        f"duplicate PK tuples: {dup_pk}",
    ))

    # Invariant 3 — value range constraints
    cur.execute("""
        SELECT
          SUM(CASE WHEN percentile < 0 OR percentile > 100 THEN 1 ELSE 0 END),
          SUM(CASE WHEN decile < 1 OR decile > 10 THEN 1 ELSE 0 END),
          SUM(CASE WHEN band NOT IN ('low','mid','high') THEN 1 ELSE 0 END)
          FROM layer3_sa2_metric_banding
    """)
    pct_oor, dec_oor, band_oor = cur.fetchone()
    invariants.append((
        "percentile in [0,100], decile in [1,10], band in {low,mid,high}",
        (pct_oor or 0) == 0 and (dec_oor or 0) == 0 and (band_oor or 0) == 0,
        f"percentile out of range: {pct_oor or 0}; "
        f"decile out of range: {dec_oor or 0}; "
        f"band invalid: {band_oor or 0}",
    ))

    # Invariant 4 — no NULLs in core fields
    cur.execute("""
        SELECT
          SUM(CASE WHEN percentile IS NULL THEN 1 ELSE 0 END),
          SUM(CASE WHEN decile IS NULL THEN 1 ELSE 0 END),
          SUM(CASE WHEN band IS NULL THEN 1 ELSE 0 END),
          SUM(CASE WHEN cohort_key IS NULL THEN 1 ELSE 0 END),
          SUM(CASE WHEN cohort_n IS NULL THEN 1 ELSE 0 END),
          SUM(CASE WHEN raw_value IS NULL THEN 1 ELSE 0 END)
          FROM layer3_sa2_metric_banding
    """)
    pct_n, dec_n, band_n, ck_n, cn_n, rv_n = cur.fetchone()
    invariants.append((
        "Core fields all populated (percentile/decile/band/cohort/raw)",
        all(x == 0 for x in (pct_n, dec_n, band_n, ck_n, cn_n, rv_n)),
        f"NULLs - percentile: {pct_n}; decile: {dec_n}; "
        f"band: {band_n}; cohort_key: {ck_n}; "
        f"cohort_n: {cn_n}; raw_value: {rv_n}",
    ))

    # Invariant 5 — band-decile consistency
    cur.execute("""
        SELECT COUNT(*) FROM layer3_sa2_metric_banding
         WHERE NOT (
            (decile BETWEEN 1 AND 3 AND band = 'low')
            OR (decile BETWEEN 4 AND 6 AND band = 'mid')
            OR (decile BETWEEN 7 AND 10 AND band = 'high')
         )
    """)
    band_decile_inconsistent = cur.fetchone()[0]
    invariants.append((
        "band consistent with decile (1-3 low / 4-6 mid / 7-10 high)",
        band_decile_inconsistent == 0,
        f"inconsistent rows: {band_decile_inconsistent}",
    ))

    # Invariant 6 — cohort_n matches actual layer3 cohort size
    cur.execute("""
        SELECT
          SUM(CASE WHEN cohort_n != actual_n THEN 1 ELSE 0 END)
          FROM (
            SELECT
              metric, cohort_def, cohort_key,
              cohort_n,
              COUNT(*) AS actual_n
              FROM layer3_sa2_metric_banding
          GROUP BY metric, cohort_def, cohort_key, cohort_n
          )
    """)
    cohort_n_mismatch = cur.fetchone()[0] or 0
    invariants.append((
        "cohort_n matches actual cohort size in layer3 table",
        cohort_n_mismatch == 0,
        f"mismatched (metric x cohort_key) groups: {cohort_n_mismatch}",
    ))

    # Invariant 7 — every layer3 sa2_code exists in sa2_cohort
    cur.execute("""
        SELECT COUNT(DISTINCT l.sa2_code)
          FROM layer3_sa2_metric_banding l
         WHERE l.sa2_code NOT IN (SELECT sa2_code FROM sa2_cohort)
    """)
    orphan_sa2 = cur.fetchone()[0]
    invariants.append((
        "Every layer3 sa2_code present in sa2_cohort",
        orphan_sa2 == 0,
        f"orphan sa2_codes: {orphan_sa2}",
    ))

    # Invariant 8 — decile distribution roughly balanced within cohort
    # For each (metric, cohort_key), expect each decile within +/-2 of n/10.
    # Allow some tolerance because of ties / mid-rank assignment.
    cur.execute("""
        SELECT metric, cohort_key, decile, COUNT(*) AS n,
               (SELECT cohort_n
                  FROM layer3_sa2_metric_banding sub
                 WHERE sub.metric = outer_q.metric
                   AND sub.cohort_key = outer_q.cohort_key
                 LIMIT 1) AS coh_n
          FROM layer3_sa2_metric_banding outer_q
      GROUP BY metric, cohort_key, decile
    """)
    rows = cur.fetchall()
    bad_decile_balance = 0
    sampled_imbalance = []
    for metric, ck, dec, n, coh_n in rows:
        if coh_n is None or coh_n < 20:
            continue  # skip tiny cohorts where balance is meaningless
        expected = coh_n / 10.0
        # Tolerance: 50% of expected OR 3 absolute, whichever larger
        tol = max(3, expected * 0.5)
        if abs(n - expected) > tol:
            bad_decile_balance += 1
            if len(sampled_imbalance) < 10:
                sampled_imbalance.append(
                    (metric, ck, dec, n, round(expected, 1)))
    invariants.append((
        "Decile distribution balanced within cohort (cohort_n>=20)",
        bad_decile_balance == 0,
        f"imbalanced (metric x cohort_key x decile) groups: "
        f"{bad_decile_balance}",
    ))
    if sampled_imbalance:
        detail_blocks.append((
            "Inv 8 imbalanced sample (first 10)",
            "\n".join(
                f"- `{m}` cohort `{c}` decile {d}: actual {n} vs "
                f"expected ~{e}"
                for m, c, d, n, e in sampled_imbalance
            )
        ))

    # Invariant 9 — band distribution per metric ~30/30/40 within +/-3pp
    cur.execute("""
        SELECT metric, band, COUNT(*) AS n
          FROM layer3_sa2_metric_banding
      GROUP BY metric, band
    """)
    band_per_metric = {}
    for m, b, n in cur.fetchall():
        band_per_metric.setdefault(m, {})[b] = n
    band_dist_problems = []
    for m, bands in band_per_metric.items():
        total = sum(bands.values())
        if total == 0:
            continue
        low_pct = bands.get("low", 0) / total * 100
        mid_pct = bands.get("mid", 0) / total * 100
        high_pct = bands.get("high", 0) / total * 100
        # Theoretical: 30/30/40
        if (abs(low_pct - 30) > 3 or
                abs(mid_pct - 30) > 3 or
                abs(high_pct - 40) > 3):
            band_dist_problems.append(
                (m, round(low_pct, 1), round(mid_pct, 1),
                 round(high_pct, 1)))
    invariants.append((
        "Band distribution per metric is ~30/30/40 (+/-3pp)",
        len(band_dist_problems) == 0,
        f"metrics outside tolerance: {len(band_dist_problems)}",
    ))
    if band_dist_problems:
        detail_blocks.append((
            "Inv 9 band-distribution outliers",
            "\n".join(
                f"- `{m}`: low {lp}%, mid {mp}%, high {hp}%"
                for m, lp, mp, hp in band_dist_problems
            )
        ))

    # Invariant 10 — audit_log row 136 well-formed
    cur.execute("""
        SELECT audit_id, actor, action, subject_type, after_json
          FROM audit_log WHERE audit_id = 136
    """)
    row = cur.fetchone()
    if row:
        audit_id, actor, action, subj, after = row
        well_formed = (
            actor == "layer3_apply"
            and action == "layer3_banding_v1"
            and subj == "layer3_sa2_metric_banding"
            and "rows" in (after or "")
        )
        invariants.append((
            "audit_log row 136 well-formed",
            well_formed,
            f"actor={actor}, action={action}, subj={subj}, after={after}",
        ))
    else:
        invariants.append((
            "audit_log row 136 well-formed",
            False,
            "row 136 not found",
        ))

    # ---- Sample SA2 profile dump ----
    # Pick a few SA2s that exist in the table for spot review
    cur.execute("""
        SELECT DISTINCT sa2_code FROM layer3_sa2_metric_banding
         ORDER BY sa2_code
         LIMIT 1
    """)
    first_sa2 = cur.fetchone()[0]
    cur.execute("""
        SELECT DISTINCT sa2_code FROM layer3_sa2_metric_banding
         ORDER BY sa2_code DESC
         LIMIT 1
    """)
    last_sa2 = cur.fetchone()[0]

    sample_codes = [first_sa2, last_sa2]
    for c in SAMPLE_SA2_CODES:
        cur.execute(
            "SELECT 1 FROM layer3_sa2_metric_banding "
            "WHERE sa2_code = ? LIMIT 1", (c,))
        if cur.fetchone():
            sample_codes.append(c)
    sample_codes = list(dict.fromkeys(sample_codes))[:5]

    sample_profiles = []
    for sa2 in sample_codes:
        cur.execute("""
            SELECT name FROM (
                SELECT sa2_name AS name FROM sa2_cohort WHERE sa2_code = ?
            )
        """, (sa2,))
        nm_row = cur.fetchone()
        sa2_name = nm_row[0] if nm_row else None

        cur.execute("""
            SELECT metric, year, period_label, cohort_def, cohort_key,
                   cohort_n, raw_value, percentile, decile, band
              FROM layer3_sa2_metric_banding
             WHERE sa2_code = ?
          ORDER BY metric
        """, (sa2,))
        sample_profiles.append((sa2, sa2_name, cur.fetchall()))

    # Also: per-metric headlines
    cur.execute("""
        SELECT metric, year, COUNT(*) AS n,
               COUNT(DISTINCT cohort_key) AS n_cohorts,
               MIN(cohort_n) AS min_cohort,
               MAX(cohort_n) AS max_cohort
          FROM layer3_sa2_metric_banding
      GROUP BY metric, year
      ORDER BY metric
    """)
    per_metric = cur.fetchall()

    conn.close()

    # ---- Emit markdown ----
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out = []
    w = out.append

    w("# Layer 3 spotcheck")
    w("")
    w(f"_Generated: {datetime.now().isoformat(timespec='seconds')}_")
    w("")
    w("Read-only post-apply validation of `sa2_cohort` and "
      "`layer3_sa2_metric_banding` against 10 invariants.")
    w("")

    # Invariant table
    n_pass = sum(1 for _, p, _ in invariants if p)
    n_fail = sum(1 for _, p, _ in invariants if not p)
    w(f"## Invariants — {n_pass} of {len(invariants)} pass")
    w("")
    w("| # | Invariant | Result | Detail |")
    w("|---:|---|:-:|---|")
    for i, (label, passed, detail) in enumerate(invariants, 1):
        mark = "PASS" if passed else "**FAIL**"
        w(f"| {i} | {label} | {mark} | {detail} |")
    w("")

    if n_fail:
        w(f"### {n_fail} INVARIANT(S) FAILED — investigate before proceeding.")
        w("")

    # Detail blocks for inv 8/9
    for heading, text in detail_blocks:
        w(f"## {heading}")
        w("")
        w(text)
        w("")

    # Per-metric summary
    w("## Per-metric headlines")
    w("")
    w("| metric | year | rows | cohorts | min cohort | max cohort |")
    w("|---|---:|---:|---:|---:|---:|")
    for m, yr, n, ncoh, mn, mx in per_metric:
        w(f"| `{m}` | {yr} | {n:,} | {ncoh} | {mn} | {mx} |")
    w("")

    # Sample profiles
    w("## Sample SA2 profiles")
    w("")
    for sa2, name, rows in sample_profiles:
        w(f"### `{sa2}` — {name or '_(no name)_'}")
        w("")
        if not rows:
            w("_No layer3 rows for this SA2._")
            w("")
            continue
        w("| metric | year | period | cohort | key | n | raw | pctile | dec | band |")
        w("|---|---:|---|---|---|---:|---:|---:|---:|---|")
        for (metric, yr, plabel, cdef, ckey, cn,
             rv, pct, dec, band) in rows:
            rv_str = f"{rv:,.2f}" if rv is not None else "n/a"
            plabel_str = plabel if plabel else ""
            w(f"| `{metric}` | {yr} | {plabel_str} | {cdef} | "
              f"`{ckey}` | {cn} | {rv_str} | "
              f"{pct:.1f} | {dec} | {band} |")
        w("")

    OUT_PATH.write_text("\n".join(out), encoding="utf-8")
    size = OUT_PATH.stat().st_size

    print()
    print(f"Invariants: {n_pass} of {len(invariants)} pass")
    if n_fail:
        print(f"  {n_fail} FAILED")
    print(f"Wrote {OUT_PATH.relative_to(REPO_ROOT)} ({size:,} bytes)")
    return 0 if n_fail == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
