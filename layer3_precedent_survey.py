"""
layer3_precedent_survey.py

Read-only precedent survey for Layer 3 banding decisions.

Per Decision 65: before designing Layer 3 schema, catalogue all existing
percentile / banding / cohort / composite-score conventions already
shipped on Industry, Catchment, Operator, and Centre v1 pages.

Outputs:
  - recon/layer3_precedent_survey.md   (the survey artefact)
  - stdout: progress + summary

No DB writes. No file mutations outside recon/.

Usage:
  cd <repo root>
  python layer3_precedent_survey.py
"""
import os
import re
import sqlite3
from collections import defaultdict
from datetime import datetime
from pathlib import Path


# --------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent
DB_PATH = REPO_ROOT / "data" / "kintell.db"
OUTPUT_PATH = REPO_ROOT / "recon" / "layer3_precedent_survey.md"

# Directories pruned during walk
SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "env",
    "dist", "build", "data", "abs_data", ".pytest_cache", ".mypy_cache",
    ".idea", ".vscode", "coverage", ".next", ".nuxt",
}

# File extensions scanned for code evidence
CODE_EXTS = {
    ".py", ".html", ".htm", ".js", ".jsx", ".ts", ".tsx", ".vue",
    ".sql", ".css", ".scss", ".md", ".txt", ".json",
}

# Keyword regexes (case-insensitive). Label -> pattern.
KEYWORDS = {
    "percentile":   r"percentile",
    "rank":         r"\brank\b|\branked\b|\branking\b",
    "cohort":       r"cohort",
    "band":         r"\bband\b|\bbanded\b|\bbanding\b|\bbands\b",
    "decile":       r"decile",
    "quintile":     r"quintile",
    "quartile":     r"quartile",
    "tier":         r"\btier\b|\btiered\b|\btiers\b",
    "composite":    r"composite",
    "score":        r"\bscore\b|\bscored\b|\bscoring\b|\bscores\b",
    "z-score":      r"z[-_]?score|zscore",
    "ntile_sql":    r"ntile|percent_rank|dense_rank|"
                    r"row_number\s*\(\s*\)\s*over",
    "low_med_high": r"\blow\s*[/|]\s*med(?:ium)?\s*[/|]\s*high\b|"
                    r"\blow\s*,?\s*medium\s*,?\s*high\b",
    "vs_peers":     r"vs[\s_]+peer|vs[\s_]+state|vs[\s_]+national|"
                    r"vs[\s_]+remoteness|peer[s]?[\s_]+(?:comparison|group)",
    "seifa":        r"seifa",
    "aria":         r"\baria\+?\b",
}

# Page heuristic — substring match on path (case-insensitive)
PAGE_HEURISTICS = [
    ("industry",  re.compile(r"industry",  re.IGNORECASE)),
    ("catchment", re.compile(r"catchment", re.IGNORECASE)),
    ("operator",  re.compile(r"operator",  re.IGNORECASE)),
    ("centre",    re.compile(r"\bcentre\b|\bcenter\b", re.IGNORECASE)),
]

# DB column-name fragments treated as banding/percentile evidence
DB_COL_FRAGS = [
    "percentile", "rank", "band", "decile", "quintile",
    "quartile", "score", "tier", "cohort", "seifa", "aria", "peer",
]

SNIPPET_MAX = 180
HITS_PER_FILE_CAP = 5


# --------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------

def iter_code_files():
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext in CODE_EXTS:
                yield Path(dirpath) / fname


def read_text_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="latin-1")
        except Exception:
            return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def classify_page(rel_path: Path):
    s = str(rel_path).replace("\\", "/")
    return [label for label, pat in PAGE_HEURISTICS if pat.search(s)]


def clip(s: str, n: int = SNIPPET_MAX) -> str:
    s = s.replace("\t", " ").replace("|", "\\|").rstrip()
    if len(s) > n:
        return s[: n - 1] + "..."
    return s


# --------------------------------------------------------------------
# Repo scan
# --------------------------------------------------------------------

def scan_repo():
    print("[1/3] Scanning repo for banding/percentile precedent...",
          flush=True)
    compiled = {k: re.compile(p, re.IGNORECASE) for k, p in KEYWORDS.items()}
    hits = []
    files_scanned = 0

    self_name = "layer3_precedent_survey.py"
    self_out = "recon/layer3_precedent_survey.md"

    for path in iter_code_files():
        rel = path.relative_to(REPO_ROOT)
        rel_posix = str(rel).replace("\\", "/")
        if rel.name == self_name or rel_posix == self_out:
            continue
        text = read_text_safe(path)
        if not text:
            continue
        files_scanned += 1
        pages = classify_page(rel)
        seen_per_file = defaultdict(int)
        for line_no, line in enumerate(text.splitlines(), 1):
            for kw, regex in compiled.items():
                if regex.search(line):
                    seen_per_file[kw] += 1
                    if seen_per_file[kw] <= HITS_PER_FILE_CAP:
                        hits.append({
                            "keyword": kw,
                            "rel_path": rel_posix,
                            "line_no": line_no,
                            "snippet": clip(line),
                            "pages": pages,
                        })

    print(f"  files scanned: {files_scanned}", flush=True)
    print(f"  total hits:    {len(hits)}", flush=True)
    return hits


# --------------------------------------------------------------------
# DB scan
# --------------------------------------------------------------------

def scan_db():
    print("[2/3] Scanning DB schema for banding/percentile evidence...",
          flush=True)
    findings = {"columns": [], "views": [], "tables_named": []}

    if not DB_PATH.exists():
        print(f"  DB not found at {DB_PATH} - skipping DB scan", flush=True)
        return findings

    uri = f"file:{DB_PATH.as_posix()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    cur = conn.cursor()

    cur.execute("""
        SELECT type, name, sql
          FROM sqlite_master
         WHERE type IN ('table', 'view')
           AND name NOT LIKE 'sqlite_%'
         ORDER BY type, name
    """)
    objects = cur.fetchall()

    name_pat_re = re.compile("|".join(DB_COL_FRAGS), re.IGNORECASE)
    win_re = re.compile(
        r"percent_rank|ntile|dense_rank|"
        r"\brank\s*\(\s*\)\s*over|"
        r"row_number\s*\(\s*\)\s*over",
        re.IGNORECASE,
    )

    for obj_type, name, sql in objects:
        if name_pat_re.search(name):
            findings["tables_named"].append({"type": obj_type, "name": name})

        if obj_type == "view" and sql and win_re.search(sql):
            findings["views"].append({"name": name, "sql": sql})

        if obj_type == "table":
            try:
                cur.execute(f"PRAGMA table_info('{name}')")
                cols = cur.fetchall()
            except sqlite3.Error:
                cols = []
            for cid, cname, ctype, notnull, dflt, pk in cols:
                if not name_pat_re.search(cname):
                    continue
                samples = []
                non_null_count = None
                try:
                    cur.execute(
                        f'SELECT DISTINCT "{cname}" FROM "{name}" '
                        f'WHERE "{cname}" IS NOT NULL LIMIT 5'
                    )
                    samples = [str(r[0]) for r in cur.fetchall()]
                except sqlite3.Error:
                    pass
                try:
                    cur.execute(
                        f'SELECT COUNT(*) FROM "{name}" '
                        f'WHERE "{cname}" IS NOT NULL'
                    )
                    non_null_count = cur.fetchone()[0]
                except sqlite3.Error:
                    pass
                findings["columns"].append({
                    "table": name,
                    "column": cname,
                    "type": ctype or "",
                    "non_null_count": non_null_count,
                    "samples": samples,
                })

    conn.close()
    print(f"  matched columns:           {len(findings['columns'])}",
          flush=True)
    print(f"  banding-named tables/views: {len(findings['tables_named'])}",
          flush=True)
    print(f"  views with window funcs:   {len(findings['views'])}",
          flush=True)
    return findings


# --------------------------------------------------------------------
# Markdown emit
# --------------------------------------------------------------------

def emit_markdown(hits, db_findings):
    print(f"[3/3] Writing {OUTPUT_PATH}...", flush=True)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out = []
    w = out.append

    w("# Layer 3 Precedent Survey")
    w("")
    w(f"_Generated: {datetime.now().isoformat(timespec='seconds')}_")
    w("")
    w("Read-only catalogue of existing percentile / banding / cohort / "
      "composite-score conventions across the repo and DB. "
      "Per Decision 65: Layer 3 must adopt these where they exist rather "
      "than redesign.")
    w("")
    w("**Sections:**")
    w("- A. DB evidence (column names, sample values, views with window funcs)")
    w("- B. Code evidence (per-keyword hits across the repo)")
    w("- C. Page-by-page heuristic grouping")
    w("- D. Open questions for Patrick (Decision 65 D1-D4)")
    w("")
    w("---")
    w("")

    # ---- Section A ----
    w("## A. DB evidence")
    w("")

    cols = db_findings["columns"]
    w("### A.1 Columns matching banding/percentile/score patterns")
    w("")
    if cols:
        w("| Table | Column | Type | Non-null rows | Sample values |")
        w("|---|---|---|---:|---|")
        for c in sorted(cols, key=lambda x: (x["table"], x["column"])):
            nn = c["non_null_count"]
            nn_str = "n/a" if nn is None else f"{nn:,}"
            samples = ", ".join(c["samples"]) if c["samples"] else "_(none)_"
            samples = clip(samples, 80)
            w(f"| `{c['table']}` | `{c['column']}` | {c['type']} | "
              f"{nn_str} | {samples} |")
    else:
        w("_No matching columns found._")
    w("")

    w("### A.2 Tables/views with banding-flavoured names")
    w("")
    tn = db_findings["tables_named"]
    if tn:
        for t in tn:
            w(f"- {t['type']}: `{t['name']}`")
    else:
        w("_None found._")
    w("")

    w("### A.3 Views with window functions (PERCENT_RANK / NTILE / RANK OVER)")
    w("")
    views = db_findings["views"]
    if views:
        for v in views:
            w(f"#### `{v['name']}`")
            w("")
            w("```sql")
            w(v["sql"])
            w("```")
            w("")
    else:
        w("_None found._")
    w("")

    w("---")
    w("")

    # ---- Section B ----
    w("## B. Code evidence")
    w("")
    by_kw = defaultdict(list)
    for h in hits:
        by_kw[h["keyword"]].append(h)

    if not hits:
        w("_No keyword hits found._")
        w("")
    else:
        w("### B.1 Hit counts by keyword (top files)")
        w("")
        w("| Keyword | Hits | Files | Top files |")
        w("|---|---:|---:|---|")
        for kw in sorted(by_kw.keys()):
            kw_hits = by_kw[kw]
            files_for_kw = defaultdict(int)
            for h in kw_hits:
                files_for_kw[h["rel_path"]] += 1
            top = sorted(files_for_kw.items(), key=lambda x: -x[1])[:3]
            top_str = "; ".join(f"`{p}` ({n})" for p, n in top)
            w(f"| {kw} | {len(kw_hits)} | {len(files_for_kw)} | "
              f"{clip(top_str, 100)} |")
        w("")

        w(f"### B.2 Per-keyword hits (capped at {HITS_PER_FILE_CAP} per file)")
        w("")
        for kw in sorted(by_kw.keys()):
            kw_hits = by_kw[kw]
            w(f"#### `{kw}` - {len(kw_hits)} hit(s)")
            w("")
            w("| File | Line | Snippet |")
            w("|---|---:|---|")
            for h in sorted(kw_hits,
                            key=lambda x: (x["rel_path"], x["line_no"])):
                w(f"| `{h['rel_path']}` | {h['line_no']} | "
                  f"`{clip(h['snippet'], 140)}` |")
            w("")

    w("---")
    w("")

    # ---- Section C ----
    w("## C. Page-by-page heuristic grouping")
    w("")
    w("_Grouped by path-name match: 'industry' / 'catchment' / 'operator' / "
      "'centre' substring in file path. Files matching no page or multiple "
      "pages are listed separately. **This is heuristic - Patrick to "
      "verify.**_")
    w("")

    by_page = defaultdict(lambda: defaultdict(set))
    no_page = defaultdict(set)
    multi_page = defaultdict(set)

    for h in hits:
        if not h["pages"]:
            no_page[h["keyword"]].add(h["rel_path"])
        elif len(h["pages"]) == 1:
            by_page[h["pages"][0]][h["keyword"]].add(h["rel_path"])
        else:
            multi_page[frozenset(h["pages"])].add(
                (h["rel_path"], h["keyword"]))

    page_order = ["industry", "catchment", "operator", "centre"]
    for idx, page in enumerate(page_order, 1):
        w(f"### C.{idx} {page.capitalize()} tab")
        w("")
        if not by_page[page]:
            w("_No keyword hits in files path-matching this page._")
            w("")
            continue
        w("| Keyword | Files |")
        w("|---|---|")
        for kw in sorted(by_page[page].keys()):
            files = sorted(by_page[page][kw])
            files_str = "; ".join(f"`{f}`" for f in files[:5])
            if len(files) > 5:
                files_str += f"; ...+{len(files) - 5} more"
            w(f"| {kw} | {clip(files_str, 200)} |")
        w("")

    w("### C.5 Multi-page files (path matched >1 page)")
    w("")
    if multi_page:
        for pages, items in sorted(multi_page.items(),
                                   key=lambda x: sorted(x[0])):
            file_count = len({f for f, _ in items})
            w(f"- **pages: {' + '.join(sorted(pages))}** - "
              f"{len(items)} hit(s) across {file_count} file(s)")
    else:
        w("_None._")
    w("")

    w("### C.6 Unclassified (no page in path)")
    w("")
    if no_page:
        w("| Keyword | Files |")
        w("|---|---|")
        for kw in sorted(no_page.keys()):
            files = sorted(no_page[kw])
            files_str = "; ".join(f"`{f}`" for f in files[:5])
            if len(files) > 5:
                files_str += f"; ...+{len(files) - 5} more"
            w(f"| {kw} | {clip(files_str, 200)} |")
    else:
        w("_None._")
    w("")

    w("---")
    w("")

    # ---- Section D ----
    w("## D. Open questions for Patrick (Decision 65 D1-D4)")
    w("")
    w("**D1. Layer 3 table shape:**")
    w("- Option A - wide table per SA2 (one row per SA2, many "
      "percentile/band cols)")
    w("- Option B - long format (sa2_code, metric, year, cohort_def, "
      "percentile, band)")
    w("- Option C - hybrid (long for stable Layer 3 metrics, wide mart "
      "view for Layer 4 reads)")
    w("")
    w("Survey evidence: _[fill in after review of Sections A-C]_")
    w("")
    w("**D2. RWCI weighting (only if RWCI in Layer 3 scope):**")
    w("- Option A - equal-weight z-scored inputs")
    w("- Option B - hand-calibrated weights (Patrick supplies)")
    w("- Option C - principal-component on inputs across all SA2s")
    w("- Option D - defer RWCI to Layer 3b")
    w("")
    w("Survey evidence: _[fill in]_")
    w("")
    w("**D3. Cohort definitions per metric:**")
    w("- Default cohort: state-x-remoteness?")
    w("- Per-metric override?")
    w("")
    w("Survey evidence: _[fill in - note any precedent like SEIFA decile "
      "= national, ARIA = remoteness band, etc.]_")
    w("")
    w("**D4. Session scope:**")
    w("- Full Layer 3 + RWCI / Layer 3 minus RWCI / pre-work + scope only")
    w("")

    OUTPUT_PATH.write_text("\n".join(out), encoding="utf-8")
    size = OUTPUT_PATH.stat().st_size
    print(f"  wrote {OUTPUT_PATH} ({size:,} bytes)", flush=True)


# --------------------------------------------------------------------
# Main
# --------------------------------------------------------------------

def main():
    print("Layer 3 Precedent Survey - read-only")
    print(f"Repo: {REPO_ROOT}")
    print(f"DB:   {DB_PATH}")
    print(f"Out:  {OUTPUT_PATH}")
    print()
    hits = scan_repo()
    db_findings = scan_db()
    emit_markdown(hits, db_findings)
    print()
    print("Survey complete.")
    print(f"Review: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
