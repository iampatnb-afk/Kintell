#!/usr/bin/env python3
"""
layer4_design_probe.py — read-only probe of the Layer 4 design surface.

Run from repo root. Writes recon/layer4_design_probe.md.

What this probe captures (matches PRE-WORK SCOPE in
remara_project_status_2026-04-28.txt):

  1. centre_page.py shape: function index + lines that mention
     decile / SEIFA / band / percentile / weighted_decile / irsd
     (= the touchpoints where Position bands will attach).
  2. docs/centre.html structure: headings, Jinja blocks/includes,
     count of card-class elements, any markers that already hint at
     Now / Trajectory / Position / SEIFA / decile / band / peer / cohort.
  3. Operator + catchment SEIFA primitive: keyword hits in
     operator_page.py, catchment_page.py, module2*.py, plus any
     HTML partials that look SEIFA / decile related. This is the
     "Visual Consistency Principle" reuse target.
  4. layer3_sa2_metric_banding: schema, indexes, per-metric stats
     (incl. how many rows have cohort_n < 10 — informs the cohort_n
     display rule), and one full multi-metric SA2 sample.

Read-only: opens the DB in `mode=ro`, only file write is the
recon/layer4_design_probe.md report itself.
"""
from __future__ import annotations

import ast
import re
import sqlite3
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent
RECON = REPO / "recon"
RECON.mkdir(exist_ok=True)
OUT = RECON / "layer4_design_probe.md"
DB = REPO / "data" / "kintell.db"

KEYWORDS = (
    "decile", "seifa", "band", "percentile",
    "weighted_decile", "weighted decile", "irsd", "cohort",
)
KEYWORD_RE = re.compile(r"\b(" + "|".join(re.escape(k) for k in KEYWORDS) + r")\b", re.IGNORECASE)


def find_first(*candidates: str) -> Path | None:
    for c in candidates:
        p = REPO / c
        if p.exists() and p.is_file():
            return p
    return None


def glob_first(pattern: str) -> Path | None:
    for p in sorted(REPO.glob(pattern)):
        if p.is_file():
            return p
    return None


def py_function_index(path: Path) -> list[dict]:
    src = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return [{"name": f"<parse error: {e}>", "lineno": 0, "end_lineno": 0,
                 "args": [], "doc": ""}]
    funcs: list[dict] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            doc_full = ast.get_docstring(node) or ""
            doc_first = doc_full.splitlines()[0] if doc_full else ""
            funcs.append({
                "name": node.name,
                "lineno": node.lineno,
                "end_lineno": getattr(node, "end_lineno", node.lineno),
                "args": [a.arg for a in node.args.args],
                "doc": doc_first,
            })
    funcs.sort(key=lambda f: f["lineno"])
    return funcs


def keyword_hits(path: Path, max_hits: int = 80) -> list[tuple[int, str]]:
    hits: list[tuple[int, str]] = []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="replace")
    for i, line in enumerate(text.splitlines(), 1):
        if KEYWORD_RE.search(line):
            hits.append((i, line.rstrip()))
            if len(hits) >= max_hits:
                break
    return hits


def html_structure(path: Path) -> dict:
    src = path.read_text(encoding="utf-8")
    headings = re.findall(r"<(h[1-6])[^>]*>(.*?)</\1>", src, re.IGNORECASE | re.DOTALL)
    headings = [(tag.lower(), re.sub(r"\s+", " ", txt).strip()[:140])
                for tag, txt in headings]
    jinja = re.findall(
        r"\{%\s*(block|extends|include|import|from|macro|endblock|endmacro|set)\b[^%]*%\}",
        src,
    )
    cards = re.findall(r'class="[^"]*\bcard\b[^"]*"', src)
    section_markers = re.findall(
        r'\b(id|class)="([^"]*\b(?:now|trajectory|position|seifa|decile|band|peer|cohort)\b[^"]*)"',
        src,
        re.IGNORECASE,
    )
    return {
        "lines": src.count("\n") + 1,
        "size_bytes": path.stat().st_size,
        "headings": headings[:80],
        "jinja_blocks": jinja[:80],
        "card_count": len(cards),
        "section_markers": section_markers[:80],
    }


def db_sample() -> dict:
    if not DB.exists():
        return {"error": f"DB not found at {DB}"}
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    try:
        out: dict = {}
        out["schema_layer3"] = [dict(r) for r in con.execute(
            "PRAGMA table_info(layer3_sa2_metric_banding)")]
        out["schema_cohort"] = [dict(r) for r in con.execute(
            "PRAGMA table_info(sa2_cohort)")]
        out["indexes_layer3"] = [dict(r) for r in con.execute(
            "SELECT name, sql FROM sqlite_master "
            "WHERE type='index' AND tbl_name='layer3_sa2_metric_banding'")]
        out["row_count"] = con.execute(
            "SELECT COUNT(*) FROM layer3_sa2_metric_banding").fetchone()[0]
        out["per_metric"] = [dict(r) for r in con.execute("""
            SELECT metric, cohort_def, COUNT(*) AS rows,
                   MIN(cohort_n) AS min_cn, MAX(cohort_n) AS max_cn,
                   SUM(CASE WHEN cohort_n <  10 THEN 1 ELSE 0 END) AS rows_cn_lt_10,
                   SUM(CASE WHEN cohort_n >= 10 AND cohort_n < 20 THEN 1 ELSE 0 END) AS rows_cn_10_19
              FROM layer3_sa2_metric_banding
             GROUP BY metric, cohort_def
             ORDER BY metric""")]
        sample_sa2 = con.execute("""
            SELECT sa2_code, COUNT(*) AS n
              FROM layer3_sa2_metric_banding
             GROUP BY sa2_code
             HAVING n >= 8
             ORDER BY n DESC, sa2_code
             LIMIT 1""").fetchone()
        if sample_sa2:
            out["sample_sa2"] = sample_sa2["sa2_code"]
            out["sample_rows"] = [dict(r) for r in con.execute(
                "SELECT * FROM layer3_sa2_metric_banding "
                "WHERE sa2_code = ? ORDER BY metric",
                (sample_sa2["sa2_code"],))]
        else:
            out["sample_sa2"] = None
            out["sample_rows"] = []
        return out
    finally:
        con.close()


def collect_py_candidates() -> list[Path]:
    seen: set[Path] = set()
    patterns = (
        "operator_page.py", "catchment_page.py",
        "app/operator_page.py", "app/catchment_page.py",
        "src/operator_page.py", "src/catchment_page.py",
        "module2*.py", "app/module2*.py", "src/module2*.py",
        "**/operator_page.py", "**/catchment_page.py", "**/module2*.py",
    )
    for pat in patterns:
        for p in REPO.glob(pat):
            if p.is_file() and p.suffix == ".py":
                seen.add(p.resolve())
    return sorted(seen)


def collect_html_candidates() -> list[Path]:
    seen: set[Path] = set()
    patterns = (
        "docs/operator.html", "docs/catchment.html", "docs/industry.html",
        "docs/_*.html", "templates/*.html",
        "**/_seifa*.html", "**/_decile*.html", "**/_band*.html",
        "**/operator.html", "**/catchment.html",
    )
    for pat in patterns:
        for p in REPO.glob(pat):
            if p.is_file():
                seen.add(p.resolve())
    return sorted(seen)


def write_section(buf: list[str], title: str, level: int = 2) -> None:
    buf.append(f"\n{'#' * level} {title}\n")


def main() -> None:
    buf: list[str] = []
    buf.append(f"# Layer 4 Design Probe — {datetime.now().isoformat(timespec='seconds')}\n\n")
    buf.append(f"Repo root: `{REPO}`  \n")
    buf.append(f"DB: `{DB}` (read-only)\n")

    # 1. centre_page.py
    write_section(buf, "1. centre_page.py")
    centre_py = (
        find_first("centre_page.py", "app/centre_page.py", "src/centre_page.py")
        or glob_first("**/centre_page.py")
    )
    if centre_py is None:
        buf.append("**centre_page.py NOT FOUND** — searched repo root, app/, src/, "
                   "and recursive glob. If it lives elsewhere, paste its path manually.\n")
    else:
        buf.append(f"Path: `{centre_py.relative_to(REPO)}`  "
                   f"({centre_py.stat().st_size} bytes)\n\n")
        buf.append("### Functions\n\n")
        buf.append("| name | lines | args | first-line doc |\n")
        buf.append("|---|---|---|---|\n")
        for f in py_function_index(centre_py):
            doc = (f["doc"] or "").replace("|", "\\|")[:90]
            args = ", ".join(f["args"]) or "-"
            buf.append(f"| `{f['name']}` | {f['lineno']}–{f['end_lineno']} | "
                       f"{args} | {doc} |\n")
        buf.append("\n### Keyword hits — decile / seifa / band / percentile / wd / irsd / cohort\n\n```\n")
        hits = keyword_hits(centre_py)
        if not hits:
            buf.append("(no matches — banding is genuinely greenfield in this file)\n")
        else:
            for ln, txt in hits:
                buf.append(f"{ln:5}: {txt}\n")
        buf.append("```\n")

    # 2. docs/centre.html
    write_section(buf, "2. docs/centre.html")
    centre_html = (
        find_first("docs/centre.html", "templates/centre.html")
        or glob_first("**/centre.html")
    )
    if centre_html is None:
        buf.append("**centre.html NOT FOUND** — searched docs/, templates/, recursive glob.\n")
    else:
        s = html_structure(centre_html)
        buf.append(f"Path: `{centre_html.relative_to(REPO)}`  "
                   f"({s['size_bytes']} bytes, {s['lines']} lines)\n\n")
        buf.append(f"Card-class element count: **{s['card_count']}**\n\n")
        buf.append("### Headings (in document order)\n\n```\n")
        for tag, txt in s["headings"]:
            buf.append(f"<{tag}> {txt}\n")
        buf.append("```\n\n### Jinja constructs\n\n```\n")
        for b in s["jinja_blocks"]:
            buf.append(f"{{% {b} ... %}}\n")
        buf.append("```\n\n### Section / card markers (now / trajectory / position / seifa / decile / band / peer / cohort)\n\n```\n")
        if not s["section_markers"]:
            buf.append("(no markers found — Layer 4 will introduce these)\n")
        else:
            for kind, kw in s["section_markers"]:
                buf.append(f"{kind}=\"{kw}\"\n")
        buf.append("```\n")

    # 3. Operator/catchment SEIFA primitive (visual reuse target)
    write_section(buf, "3. Operator / catchment SEIFA primitive — reuse target")
    py_candidates = collect_py_candidates()
    if not py_candidates:
        buf.append("_No operator/catchment/module2* Python files found._\n")
    for p in py_candidates:
        hits = keyword_hits(p, max_hits=60)
        if not hits:
            continue
        buf.append(f"\n### `{p.relative_to(REPO)}`  ({p.stat().st_size} bytes)\n\n```\n")
        for ln, txt in hits:
            buf.append(f"{ln:5}: {txt}\n")
        buf.append("```\n")

    html_candidates = collect_html_candidates()
    if not html_candidates:
        buf.append("\n_No relevant HTML partials found beyond centre.html._\n")
    for p in html_candidates:
        if centre_html is not None and p == centre_html.resolve():
            continue
        hits = keyword_hits(p, max_hits=40)
        if not hits:
            continue
        buf.append(f"\n### `{p.relative_to(REPO)}`  ({p.stat().st_size} bytes)\n\n```\n")
        for ln, txt in hits:
            buf.append(f"{ln:5}: {txt}\n")
        buf.append("```\n")

    # 4. layer3_sa2_metric_banding sample
    write_section(buf, "4. layer3_sa2_metric_banding — schema + sample")
    d = db_sample()
    if "error" in d:
        buf.append(f"**{d['error']}**\n")
    else:
        buf.append(f"Total rows: **{d['row_count']}**\n\n")
        buf.append("### Schema — layer3_sa2_metric_banding\n\n```\n")
        for c in d["schema_layer3"]:
            buf.append(f"  {c['name']:<14} {c['type']:<8} pk={c['pk']} notnull={c['notnull']}\n")
        buf.append("```\n\n### Schema — sa2_cohort\n\n```\n")
        for c in d["schema_cohort"]:
            buf.append(f"  {c['name']:<14} {c['type']:<8} pk={c['pk']} notnull={c['notnull']}\n")
        buf.append("```\n\n### Indexes on layer3_sa2_metric_banding\n\n```\n")
        for idx in d["indexes_layer3"]:
            buf.append(f"  {idx['name']}: {idx['sql']}\n")
        buf.append("```\n\n### Per-metric stats (drives cohort_n display rule)\n\n")
        buf.append("| metric | cohort_def | rows | min cn | max cn | rows cn<10 | rows cn 10-19 |\n")
        buf.append("|---|---|---:|---:|---:|---:|---:|\n")
        for r in d["per_metric"]:
            buf.append(f"| {r['metric']} | {r['cohort_def']} | {r['rows']} | "
                       f"{r['min_cn']} | {r['max_cn']} | "
                       f"{r['rows_cn_lt_10']} | {r['rows_cn_10_19']} |\n")
        buf.append(f"\n### Sample SA2 — all metric rows for sa2_code `{d['sample_sa2']}`\n\n```\n")
        for r in d["sample_rows"]:
            buf.append(f"{dict(r)}\n")
        buf.append("```\n")

    OUT.write_text("".join(buf), encoding="utf-8")
    print(f"Wrote {OUT}")
    print(f"Size: {OUT.stat().st_size} bytes")


if __name__ == "__main__":
    main()
