#!/usr/bin/env python3
"""
layer4_consistency_probe.py — read-only consistency inventory.

Scans the repo for:
  1. Where each Layer 4 metric currently displays (under5, total_pop,
     births, unemployment, the income trio, the LFP triplet, plus
     seifa for palette comparison) — Python files build payloads,
     HTML/JS files render them.
  2. CSS variables and class-name conventions in docs/*.html
     (the palette + named primitives the centre Position card should
     reuse rather than reinvent).
  3. JS visual primitive function names already in use (for histograms,
     sparklines, decile bars, band chips).

Read-only. Only writes recon/layer4_consistency_probe.md.
"""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent
RECON = REPO / "recon"
RECON.mkdir(exist_ok=True)
OUT = RECON / "layer4_consistency_probe.md"

EXCLUDE_DIRS = {
    "recon", "data", "abs_data", "node_modules", ".git",
    "__pycache__", ".venv", "venv", "dist", "build",
}

METRIC_GROUPS: dict[str, list[str]] = {
    "under5":           ["under5", "under-5", "under_5", "u5_", "_u5"],
    "total_population": ["total_population", "total_pop", "erp"],
    "births":           ["births", "birth_count", "tfr"],
    "unemployment":     ["unemployment", "unemploy"],
    "income":           ["median_employee_income", "median_household_income",
                         "median_total_income", "household_income",
                         "employee_income", "total_income"],
    "lfp":              ["lfp_persons", "lfp_females", "lfp_males",
                         "labour_force_participation", "labour force participation"],
    "seifa_palette":    ["irsd", "irsad", "seifa"],
}

TOKEN_RES = {
    group: re.compile(r"(?i)(" + "|".join(re.escape(t) for t in toks) + r")")
    for group, toks in METRIC_GROUPS.items()
}

CSS_VAR_RE = re.compile(r"(--[\w-]+)\s*:\s*([^;}\n]+)")
CSS_CLASS_RE = re.compile(r"\.([a-zA-Z][\w-]*)\s*\{")
JS_FUNC_RE = re.compile(r"function\s+([a-zA-Z_][\w]*)\s*\(")
JS_ARROW_RE = re.compile(r"\bconst\s+([a-zA-Z_][\w]*)\s*=\s*(?:\([^)]*\)|[\w]+)\s*=>")

VISUAL_HINT_RE = re.compile(
    r"(?i)(histogram|sparkline|decile|band|chip|fact|render|draw|primitive|widget|seifa|cohort)"
)


def iter_files(suffixes: tuple[str, ...]) -> list[Path]:
    out: list[Path] = []
    for p in REPO.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix not in suffixes:
            continue
        if any(part in EXCLUDE_DIRS for part in p.parts):
            continue
        out.append(p)
    return sorted(out)


def read_text_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def grep_file(path: Path, pat: re.Pattern[str], max_hits: int = 15) -> list[tuple[int, str]]:
    hits: list[tuple[int, str]] = []
    for i, line in enumerate(read_text_safe(path).splitlines(), 1):
        if pat.search(line):
            hits.append((i, line.rstrip()))
            if len(hits) >= max_hits:
                break
    return hits


def main() -> None:
    buf: list[str] = []
    buf.append(f"# Layer 4 Consistency Probe — {datetime.now().isoformat(timespec='seconds')}\n\n")
    buf.append(f"Repo root: `{REPO}`\n\n")
    buf.append(f"Excluded dirs: `{sorted(EXCLUDE_DIRS)}`\n")

    py_files = iter_files((".py",))
    html_files = iter_files((".html",))
    buf.append(f"\nScanned: **{len(py_files)} .py files**, **{len(html_files)} .html files**.\n")

    # ---------- PART 1: Where each Layer 4 metric currently displays ----------
    buf.append("\n## 1. Where each Layer 4 metric already appears\n")
    for group, pat in TOKEN_RES.items():
        buf.append(f"\n### {group}\n")
        any_hit = False
        for path in py_files + html_files:
            hits = grep_file(path, pat, max_hits=15)
            if not hits:
                continue
            any_hit = True
            buf.append(f"\n**`{path.relative_to(REPO)}`** ({len(hits)} hits shown, capped at 15)\n```\n")
            for ln, txt in hits:
                buf.append(f"{ln:5}: {txt[:240]}\n")
            buf.append("```\n")
        if not any_hit:
            buf.append("_(no matches anywhere — Layer 4 introduces this metric to the UI.)_\n")

    # ---------- PART 2: CSS variables / palette tokens ----------
    buf.append("\n## 2. CSS variables / palette tokens (docs/*.html)\n")
    found_palette = False
    for path in html_files:
        text = read_text_safe(path)
        vars_in_file: dict[str, str] = {}
        for m in CSS_VAR_RE.finditer(text):
            name = m.group(1)
            value = m.group(2).strip()[:80]
            vars_in_file[name] = value
        if not vars_in_file:
            continue
        found_palette = True
        buf.append(f"\n### `{path.relative_to(REPO)}` ({len(vars_in_file)} variables)\n```\n")
        for name, value in sorted(vars_in_file.items())[:80]:
            buf.append(f"  {name}: {value}\n")
        buf.append("```\n")
    if not found_palette:
        buf.append("_(no CSS variables found — styles may live in plain selectors.)_\n")

    # ---------- PART 3: Visual-primitive CSS class names ----------
    buf.append("\n## 3. Visual-primitive CSS class names (filtered: histogram/sparkline/decile/band/chip/fact/render/draw/seifa/cohort)\n")
    found_classes = False
    for path in html_files:
        text = read_text_safe(path)
        classes = CSS_CLASS_RE.findall(text)
        relevant = sorted(set(c for c in classes if VISUAL_HINT_RE.search(c)))
        if not relevant:
            continue
        found_classes = True
        buf.append(f"\n### `{path.relative_to(REPO)}`\n```\n")
        for c in relevant:
            buf.append(f"  .{c}\n")
        buf.append("```\n")
    if not found_classes:
        buf.append("_(no relevant CSS classes found.)_\n")

    # ---------- PART 4: JS visual primitive function names ----------
    buf.append("\n## 4. JS visual primitive functions in docs/*.html (filtered for relevance)\n")
    found_funcs = False
    for path in html_files:
        text = read_text_safe(path)
        funcs = set(JS_FUNC_RE.findall(text)) | set(JS_ARROW_RE.findall(text))
        relevant = sorted(f for f in funcs if VISUAL_HINT_RE.search(f))
        if not relevant:
            continue
        found_funcs = True
        buf.append(f"\n### `{path.relative_to(REPO)}`\n```\n")
        for f in relevant:
            buf.append(f"  {f}\n")
        buf.append("```\n")
    if not found_funcs:
        buf.append("_(no relevant JS functions found.)_\n")

    OUT.write_text("".join(buf), encoding="utf-8")
    print(f"Wrote {OUT}")
    print(f"Size: {OUT.stat().st_size} bytes")


if __name__ == "__main__":
    main()
