#!/usr/bin/env python3
"""
layer4_2_probe.py — read-only inventory for Layer 4.2 pre-work.

Layer 4.2 will add four things to the centre page:
  1. Trajectory sparklines per metric (historical line per row)
  2. Cohort-distribution histogram per metric (cohort shape + you-are-here)
  3. Gradient strip (single-hue blue ramp on decile cells)
  4. Catchment data on the centre page (supply ratio, competitor density,
     places-within-catchment) — moved from a future catchment page
     onto the centre page itself

This probe answers, before any code is generated:

  A. Catchment surface
     - What .py files compute catchment data, and what do they expose?
       (module2b_catchment.py, catchment_html.py, catchment_page.py if any)
     - Is there a docs/catchment.html, and what render functions live in it?
     - What columns / tables exist for catchment data
       (service_catchment_cache, anything else)
     - Are supply_ratio / competitor_density already computed somewhere?

  B. Trajectory data
     - Per source table (abs_sa2_erp_annual, abs_sa2_births_annual,
       abs_sa2_unemployment_quarterly, ee_sa2 metric tables for income+LFP):
       row count, date range, distinct period count, sample row for
       Bentley WA (SA2 506031124, the now-correct service 246 SA2)
     - This tells us the actual historical depth available per metric
       so the sparkline / trajectory-trio design can be honest about
       what's renderable

  C. Catchment data shape for the centre
     - service_catchment_cache schema if present + populated row count
     - Are there per-centre supply-ratio / competitor-density values
       anywhere already?

Read-only. Output: recon/layer4_2_probe.md.
"""

from __future__ import annotations

import re
import sqlite3
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent
RECON = REPO / "recon"
RECON.mkdir(exist_ok=True)
OUT = RECON / "layer4_2_probe.md"
DB = REPO / "data" / "kintell.db"

# Files that almost certainly contain catchment computation or rendering
CATCHMENT_FILE_HINTS = (
    "catchment", "module2b", "module2c", "supply_ratio", "competitor"
)

# The new-correct SA2 for Bentley WA (after Step 1c) — used as a sample
# probe target. If this SA2 isn't in the cohort tables, that's a blocker
# we need to know about now.
SAMPLE_SA2 = "506031124"

# Layer 3 metrics paired with the source tables we expect them to map to.
# The probe inspects each source for its actual historical depth.
TRAJECTORY_SOURCES = [
    # (layer3_metric_name, source_table, value_col, period_col,
    #  filter_clause_template_or_None, kind)
    # 'kind' is 'annual' or 'quarterly' — controls how we render the
    # x-axis in Layer 4.2.
    ("sa2_under5_count",            "abs_sa2_erp_annual",
     "persons", "year",
     "age_group = 'under_5_persons'", "annual"),
    ("sa2_total_population",        "abs_sa2_erp_annual",
     "persons", "year",
     "age_group = 'total_persons'", "annual"),
    ("sa2_births_count",            "abs_sa2_births_annual",
     "births_count", "year",
     None, "annual"),
    ("sa2_unemployment_rate",       "abs_sa2_unemployment_quarterly",
     "rate", "year_qtr",
     None, "quarterly"),
    # The income trio + LFP triplet sit in a metric_name long-format table.
    # Probe heuristically: any table with metric_name + sa2_code + year + value.
]

# Long-format metric tables — discovered at runtime, not hardcoded
LONG_FORMAT_METRIC_HINTS = ("metric_name", "metric")


def fmt_int(n):
    return f"{n:,}" if n is not None else "—"


def open_db_ro() -> sqlite3.Connection:
    try:
        con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    except sqlite3.Error:
        con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def list_repo_files(suffixes: tuple[str, ...]) -> list[Path]:
    out = []
    EXCLUDE = {".git", ".venv", "venv", "__pycache__",
               "node_modules", "recon", "abs_data", "data"}
    for p in REPO.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix not in suffixes:
            continue
        if any(part in EXCLUDE for part in p.parts):
            continue
        out.append(p)
    return sorted(out)


def matches_hint(name: str, hints: tuple[str, ...]) -> bool:
    nl = name.lower()
    return any(h in nl for h in hints)


def read_text_safe(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return p.read_text(encoding="utf-8", errors="replace")


def grep_lines(p: Path, pattern: re.Pattern[str], max_hits: int = 60) -> list[tuple[int, str]]:
    hits = []
    for i, line in enumerate(read_text_safe(p).splitlines(), 1):
        if pattern.search(line):
            hits.append((i, line.rstrip()))
            if len(hits) >= max_hits:
                break
    return hits


def py_function_index(p: Path) -> list[dict]:
    import ast
    src = read_text_safe(p)
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return [{"name": f"<parse error: {e}>", "lineno": 0,
                 "end_lineno": 0, "doc": ""}]
    out = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            doc_full = ast.get_docstring(node) or ""
            doc_first = doc_full.splitlines()[0] if doc_full else ""
            out.append({
                "name": node.name,
                "lineno": node.lineno,
                "end_lineno": getattr(node, "end_lineno", node.lineno),
                "doc": doc_first,
            })
    out.sort(key=lambda f: f["lineno"])
    return out


def main() -> None:
    buf: list[str] = []
    buf.append(f"# Layer 4.2 Pre-Work Probe — {datetime.now().isoformat(timespec='seconds')}\n\n")
    buf.append(f"Repo root: `{REPO}`\n")
    buf.append(f"DB: `{DB}` (read-only)\n")

    # ---------- A. Catchment surface ----------
    buf.append("\n## A. Catchment surface\n")

    py_files = list_repo_files((".py",))
    html_files = list_repo_files((".html",))
    catchment_py = [p for p in py_files if matches_hint(p.name, CATCHMENT_FILE_HINTS)]
    catchment_html = [p for p in html_files if matches_hint(p.name, CATCHMENT_FILE_HINTS)]

    buf.append(f"\n### A.1 Catchment-flavoured Python files ({len(catchment_py)})\n\n")
    if not catchment_py:
        buf.append("_(none found)_\n")
    else:
        for p in catchment_py:
            rel = p.relative_to(REPO)
            buf.append(f"\n#### `{rel}` ({p.stat().st_size} bytes)\n\n")
            funcs = py_function_index(p)
            if funcs:
                buf.append("Functions:\n\n")
                buf.append("| name | lines | first-line doc |\n")
                buf.append("|---|---|---|\n")
                for f in funcs[:40]:
                    doc = (f["doc"] or "").replace("|", "\\|")[:80]
                    buf.append(f"| `{f['name']}` | {f['lineno']}–{f['end_lineno']} | {doc} |\n")
            # Targeted keyword hits — the things we want to lift
            kw_re = re.compile(r"(?i)(supply_ratio|competitor|places.{0,20}per|under5|"
                               r"u_?5|catchment|histogram|render|fmt|seifa|irsd|aria)")
            hits = grep_lines(p, kw_re, max_hits=40)
            if hits:
                buf.append("\nKeyword hits (first 40):\n\n```\n")
                for ln, txt in hits:
                    buf.append(f"{ln:5}: {txt[:200]}\n")
                buf.append("```\n")

    buf.append(f"\n### A.2 Catchment-flavoured HTML files ({len(catchment_html)})\n\n")
    if not catchment_html:
        buf.append("_(no docs/catchment.html or similar — Layer 4.2 will need to invent the visual primitives, but inherit from operator.html / centre.html)_\n")
    else:
        for p in catchment_html:
            rel = p.relative_to(REPO)
            buf.append(f"\n#### `{rel}` ({p.stat().st_size} bytes)\n\n")
            text = read_text_safe(p)
            # Render functions
            funcs = sorted(set(re.findall(r"function\s+(render[A-Za-z_]+)\s*\(", text))
                           | set(re.findall(r"\bconst\s+(render[A-Za-z_]+)\s*=\s*", text)))
            if funcs:
                buf.append("Render functions:\n\n```\n")
                for f in funcs:
                    buf.append(f"  {f}\n")
                buf.append("```\n")
            # H3 sections
            headings = re.findall(r"<h3[^>]*>(.*?)</h3>", text,
                                  re.IGNORECASE | re.DOTALL)
            headings = [re.sub(r"\s+", " ", h).strip() for h in headings]
            if headings:
                buf.append("\nH3 sections:\n\n```\n")
                for h in headings[:30]:
                    buf.append(f"  {h[:120]}\n")
                buf.append("```\n")
            # Catchment-data shape — what fields does it read?
            kw_re = re.compile(r"(?i)(supply.?ratio|competitor|under5|u_?5|"
                               r"catchment|histogram|seifa|irsd)")
            hits = grep_lines(p, kw_re, max_hits=30)
            if hits:
                buf.append("\nKeyword hits:\n\n```\n")
                for ln, txt in hits:
                    buf.append(f"{ln:5}: {txt[:200]}\n")
                buf.append("```\n")

    # ---------- B. DB tables relevant to catchment + trajectory ----------
    buf.append("\n## B. DB tables\n")

    if not DB.exists():
        buf.append(f"\n**DB not found at `{DB}`** — skipping DB sections.\n")
    else:
        con = open_db_ro()

        # B.1 service_catchment_cache + any other catchment tables
        buf.append("\n### B.1 Catchment-flavoured tables\n\n")
        all_tables = [r["name"] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "ORDER BY name").fetchall()]
        catch_tables = [t for t in all_tables
                        if matches_hint(t, ("catchment", "supply", "competitor"))]
        if not catch_tables:
            buf.append("_(no tables matching catchment/supply/competitor)_\n")
        else:
            for t in catch_tables:
                buf.append(f"\n#### `{t}`\n\n")
                cols = [dict(r) for r in con.execute(f"PRAGMA table_info({t})")]
                buf.append("```\n")
                for c in cols:
                    buf.append(f"  {c['name']:<28} {c['type']:<10} pk={c['pk']} notnull={c['notnull']}\n")
                buf.append("```\n")
                try:
                    n = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                    buf.append(f"\nRow count: **{n:,}**\n")
                    if n > 0:
                        buf.append("\nFirst row sample:\n\n```\n")
                        sample = con.execute(f"SELECT * FROM {t} LIMIT 1").fetchone()
                        if sample is not None:
                            for k in sample.keys():
                                v = sample[k]
                                vstr = str(v)
                                if len(vstr) > 80:
                                    vstr = vstr[:77] + "..."
                                buf.append(f"  {k:<28} = {vstr}\n")
                        buf.append("```\n")
                except sqlite3.OperationalError as e:
                    buf.append(f"\n_(could not read: {e})_\n")

        # B.2 services columns relevant to catchment
        buf.append("\n### B.2 `services` table — catchment-relevant columns\n\n")
        svc_cols = [r["name"] for r in con.execute("PRAGMA table_info(services)")]
        catch_cols = [c for c in svc_cols if matches_hint(c, (
            "sa2", "aria", "seifa", "u5", "under5", "supply", "ratio",
            "competitor", "catchment", "lat", "lng"))]
        buf.append("```\n")
        for c in catch_cols:
            buf.append(f"  {c}\n")
        buf.append("```\n")

        # B.3 Trajectory source tables — annual + quarterly
        buf.append("\n## C. Trajectory data — source-table inventory\n")
        buf.append(f"\nSample SA2 = `{SAMPLE_SA2}` (Bentley - Wilson - St James, the corrected SA2 for service 246 after Step 1c).\n\n")

        for layer3_metric, table, value_col, period_col, filter_clause, kind in TRAJECTORY_SOURCES:
            buf.append(f"\n### {layer3_metric}\n\n")
            if table not in all_tables:
                buf.append(f"⚠ **table `{table}` not found** — sparkline impossible for this metric.\n")
                continue

            buf.append(f"Source table: `{table}`  (kind: {kind})\n")
            cols = [r["name"] for r in con.execute(f"PRAGMA table_info({table})")]
            if value_col not in cols:
                buf.append(f"⚠ value column `{value_col}` not in table — actual cols: {', '.join(cols)}\n")
                continue
            if period_col not in cols:
                buf.append(f"⚠ period column `{period_col}` not in table — actual cols: {', '.join(cols)}\n")
                continue

            try:
                n = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                buf.append(f"\n- Total rows: **{n:,}**\n")
                where_clause = f"WHERE {filter_clause}" if filter_clause else ""
                row = con.execute(
                    f"SELECT MIN({period_col}) AS mn, MAX({period_col}) AS mx, "
                    f"COUNT(DISTINCT {period_col}) AS n_periods "
                    f"  FROM {table} {where_clause}"
                ).fetchone()
                buf.append(f"- Period range: **{row['mn']} → {row['mx']}**, {row['n_periods']} distinct periods\n")
                if filter_clause:
                    buf.append(f"- Filter applied: `{filter_clause}`\n")

                # Sample SA2 trajectory
                sa2_where = f"sa2_code = ?"
                if filter_clause:
                    sa2_where = f"{filter_clause} AND " + sa2_where
                sample_rows = con.execute(
                    f"SELECT {period_col}, {value_col} FROM {table} "
                    f" WHERE {sa2_where} "
                    f" ORDER BY {period_col}",
                    (SAMPLE_SA2,)
                ).fetchall()
                if sample_rows:
                    buf.append(f"\n- Sample trajectory for SA2 `{SAMPLE_SA2}` ({len(sample_rows)} points):\n\n")
                    buf.append("```\n")
                    for r in sample_rows:
                        buf.append(f"  {r[0]:>10}  {r[1]}\n")
                    buf.append("```\n")
                else:
                    buf.append(f"\n_(no rows for sample SA2 `{SAMPLE_SA2}` — sparkline would render empty)_\n")

            except sqlite3.OperationalError as e:
                buf.append(f"\n_(query failed: {e})_\n")

        # C.2 Long-format metric tables (income trio + LFP triplet)
        buf.append("\n### Long-format metric tables (income trio + LFP triplet)\n\n")
        # Find tables with metric_name column
        long_tables = []
        for t in all_tables:
            tcols = [r["name"] for r in con.execute(f"PRAGMA table_info({t})")]
            if "metric_name" in tcols and ("sa2_code" in tcols or "sa2" in tcols):
                long_tables.append((t, tcols))

        if not long_tables:
            buf.append("_(no long-format metric tables found with metric_name + sa2_code)_\n")
        else:
            for t, tcols in long_tables:
                buf.append(f"\n#### `{t}`  (cols: {', '.join(tcols)})\n\n")
                # Distinct metrics + their period coverage
                try:
                    period_col_guess = next(
                        (c for c in ("year", "period", "year_qtr", "as_at", "snapshot_date")
                         if c in tcols),
                        None,
                    )
                    metrics = con.execute(
                        f"SELECT metric_name, COUNT(DISTINCT {period_col_guess}) AS n_periods, "
                        f"       MIN({period_col_guess}) AS mn, MAX({period_col_guess}) AS mx, "
                        f"       COUNT(*) AS n_rows "
                        f"  FROM {t} GROUP BY metric_name "
                        f" ORDER BY metric_name"
                        if period_col_guess else
                        f"SELECT metric_name, COUNT(*) AS n_rows FROM {t} "
                        f" GROUP BY metric_name ORDER BY metric_name"
                    ).fetchall()
                    if period_col_guess:
                        buf.append(f"Period column guess: `{period_col_guess}`\n\n")
                        buf.append("| metric_name | rows | distinct periods | min | max |\n")
                        buf.append("|---|---:|---:|---|---|\n")
                        for r in metrics:
                            buf.append(f"| {r['metric_name']} | {r['n_rows']:,} | {r['n_periods']} | {r['mn']} | {r['mx']} |\n")
                    else:
                        buf.append("| metric_name | rows |\n")
                        buf.append("|---|---:|\n")
                        for r in metrics:
                            buf.append(f"| {r['metric_name']} | {r['n_rows']:,} |\n")

                    # Sample trajectory for SA2 506031124 on the income + LFP metrics
                    income_lfp_metrics = [
                        "median_employee_income_annual",
                        "median_equiv_household_income_weekly",
                        "median_total_income_excl_pensions_annual",
                        "ee_lfp_persons_pct",
                        "census_lfp_females_pct",
                        "census_lfp_males_pct",
                    ]
                    found_metrics = {r["metric_name"] for r in metrics}
                    relevant = [m for m in income_lfp_metrics if m in found_metrics]
                    if relevant and period_col_guess:
                        buf.append(f"\nSample trajectory for SA2 `{SAMPLE_SA2}`:\n\n")
                        for m in relevant:
                            sa2_col = "sa2_code" if "sa2_code" in tcols else "sa2"
                            value_col_guess = next(
                                (c for c in ("value", "value_num", "value_real",
                                             "metric_value", "amount")
                                 if c in tcols),
                                None,
                            )
                            if not value_col_guess:
                                buf.append(f"_(no value column found for `{t}`)_\n")
                                break
                            sample_rows = con.execute(
                                f"SELECT {period_col_guess}, {value_col_guess} "
                                f"  FROM {t} "
                                f" WHERE metric_name = ? AND {sa2_col} = ? "
                                f" ORDER BY {period_col_guess}",
                                (m, SAMPLE_SA2),
                            ).fetchall()
                            if sample_rows:
                                buf.append(f"\n- **{m}** ({len(sample_rows)} points):\n")
                                buf.append("\n```\n")
                                for r in sample_rows:
                                    buf.append(f"  {r[0]:>10}  {r[1]}\n")
                                buf.append("```\n")
                            else:
                                buf.append(f"\n- **{m}**: _(no rows for sample SA2)_\n")
                except sqlite3.OperationalError as e:
                    buf.append(f"\n_(query failed: {e})_\n")

        con.close()

    # ---------- D. Catchment computation summary ----------
    buf.append("\n## D. Open questions for the design doc\n")
    buf.append("\nQuestions surfaced by this probe (to be closed in the design note):\n\n")
    buf.append("1. **Supply-ratio source.** Probe section A.1 will reveal whether `module2b_catchment.py` already computes per-centre supply ratio, and whether it's stored anywhere (`service_catchment_cache`?) or recomputed per render.\n")
    buf.append("2. **Competitor density definition.** Centres within X km? Within same SA2? Within ABS Distance to Service shape? — pick one before building.\n")
    buf.append("3. **Cohort-distribution histogram bin count.** 10 bins (decile-aligned) or finer (20–30 for shape visibility)?\n")
    buf.append("4. **Sparse-trajectory rendering.** Income trio + LFP triplet have only 3–4 data points. Render as small connected-dot trajectory rather than sparkline. Probe section C confirms exact point counts.\n")
    buf.append("5. **Catchment-data placement on centre page.** New `Catchment metrics` section after Catchment / before Population? Or rolled into Catchment card?\n")

    OUT.write_text("".join(buf), encoding="utf-8")
    print(f"Wrote {OUT}")
    print(f"Size: {OUT.stat().st_size} bytes")


if __name__ == "__main__":
    main()
