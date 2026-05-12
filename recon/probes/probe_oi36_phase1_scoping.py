"""
probe_oi36_phase1_scoping.py
============================
Read-only Phase 1 probe for OI-36 (C2-NES render-side).

Purpose
-------
Inform the surgical-vs-refactor decision by enumerating, with data, how
the catchment-position card is currently assembled in:

  - centre.html        (renderer / template)
  - centre_page.py     (Python payload assembly)

And by comparing to how OTHER cards (workforce, population, etc.) are
assembled — looking for an existing dynamic pattern that the
catchment-position card could conform to.

Output
------
A structured scoping note with three sections:

  A. HARDCODING INVENTORY
       - per catchment metric: count of identifier mentions per file
       - locations of the apparent assembly block(s)
  B. DYNAMIC-PATTERN RECON
       - does any code already iterate LAYER3_METRIC_META by card?
       - if so, where, and what does the loop look like?
  C. RECOMMENDATION
       - SURGICAL  : low touchpoint count, no existing dynamic pattern
       - REFACTOR  : moderate-to-high touchpoints AND a dynamic pattern
                     already exists elsewhere — refactor is "make
                     catchment match the existing pattern", not net-new
                     architecture
       - SURGICAL + bank refactor : high touchpoints but no existing
                     pattern — refactor scope is large, ship surgical
                     for OI-36 and bank refactor as a separate item

This probe DOES NOT mutate any file. It only reads.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT_CANDIDATES = [
    Path(__file__).resolve().parents[2],
    Path.cwd(),
]

CATCHMENT_METRICS = [
    "sa2_supply_ratio",
    "sa2_demand_supply",
    "sa2_child_to_place",
    "sa2_adjusted_demand",
    "sa2_demand_share_state",
    "sa2_nes_share",
]

# Other cards we know exist in LAYER3_METRIC_META.
OTHER_CARD_NAMES = [
    "workforce",
    "population",
    "labour_market",
    "now",
    "demographic",
    "centre_quality",
]


def find_repo_root() -> Path | None:
    for c in REPO_ROOT_CANDIDATES:
        if (c / "centre_page.py").exists():
            return c
        if (c / "docs" / "centre.html").exists():
            return c
    return None


def find_file(repo_root: Path, name: str, also_check_docs: bool = True) -> Path | None:
    candidates = [repo_root / name]
    if also_check_docs:
        candidates.append(repo_root / "docs" / name)
    for c in candidates:
        if c.exists():
            return c
    return None


def read_text(path: Path) -> str:
    return path.read_bytes().decode("utf-8", errors="replace")


def count_mentions(text: str, identifiers: list[str]) -> dict:
    out = {}
    for ident in identifiers:
        pattern = r"\b" + re.escape(ident) + r"\b"
        out[ident] = len(re.findall(pattern, text))
    return out


def find_assembly_block(text: str) -> list:
    hits = []
    keywords = (
        "catchment_position",
        "Catchment Position",
        "catchment-position",
    )
    for i, line in enumerate(text.split("\n"), start=1):
        for kw in keywords:
            if kw in line:
                hits.append((i, line.rstrip()))
                break
    return hits


def find_dynamic_patterns_python(text: str) -> list:
    """Look for evidence of a metric-driven loop in Python."""
    hits = []
    patterns = [
        r"for\s+\w+\s+in\s+LAYER3_METRIC_META",
        r"LAYER3_METRIC_META\.items\(\)",
        r"LAYER3_METRIC_META\.values\(\)",
        r"\.get\(['\"]card['\"]\)",
        r"\['card'\]\s*==",
        r"\[\"card\"\]\s*==",
    ]
    for i, line in enumerate(text.split("\n"), start=1):
        for p in patterns:
            if re.search(p, line):
                hits.append((i, line.strip()))
                break
    return hits


def find_dynamic_patterns_html(text: str) -> list:
    """Look for JS-side iteration patterns (forEach / for..of / map)."""
    hits = []
    patterns = [
        r"\.forEach\s*\(",
        r"for\s*\(\s*const\s+\w+\s+of\s+",
        r"for\s*\(\s*let\s+\w+\s+of\s+",
        r"\.map\s*\(\s*\(",
        r"\.filter\s*\(\s*\(",
    ]
    for i, line in enumerate(text.split("\n"), start=1):
        for p in patterns:
            if re.search(p, line):
                hits.append((i, line.strip()))
                break
    return hits


def find_card_assembly_functions(text: str) -> list:
    """Find Python functions that look like card assembly (e.g.
    _renderFullRow, _build_catchment_card, etc.)."""
    hits = []
    patterns = [
        r"^\s*def\s+(_?(?:render|build|assemble|make|compose)_\w*)",
        r"^\s*def\s+(\w*card\w*)",
        r"^\s*def\s+(\w*catchment\w*)",
    ]
    for i, line in enumerate(text.split("\n"), start=1):
        for p in patterns:
            m = re.search(p, line)
            if m:
                hits.append((i, line.strip()))
                break
    return hits


def main() -> int:
    repo_root = find_repo_root()
    if repo_root is None:
        print("[ERROR] could not locate repo root.")
        print("        run this from the repo root, e.g. C:\\Users\\Patrick Bell\\remara-agent")
        return 2

    print(f"[probe] repo root      : {repo_root}")

    centre_html = find_file(repo_root, "centre.html")
    centre_py = find_file(repo_root, "centre_page.py", also_check_docs=False)

    if centre_html is None:
        print("[ERROR] could not find centre.html (looked in repo root and docs/)")
        return 2
    if centre_py is None:
        print("[ERROR] could not find centre_page.py")
        return 2

    print(f"[probe] centre.html    : {centre_html}")
    print(f"[probe] centre_page.py : {centre_py}")

    html_text = read_text(centre_html)
    py_text = read_text(centre_py)

    html_lines = html_text.count("\n") + 1
    py_lines = py_text.count("\n") + 1
    print(f"[probe] centre.html    : {len(html_text):>9d} bytes, ~{html_lines:>5d} lines")
    print(f"[probe] centre_page.py : {len(py_text):>9d} bytes, ~{py_lines:>5d} lines")
    print()

    # ----- A: Hardcoding inventory --------------------------------------
    print("=" * 72)
    print("A. HARDCODING INVENTORY — catchment metric mentions per file")
    print("=" * 72)
    html_counts = count_mentions(html_text, CATCHMENT_METRICS)
    py_counts = count_mentions(py_text, CATCHMENT_METRICS)
    print(f"  {'metric':<28} {'centre.html':>12} {'centre_page.py':>16}")
    print(f"  {'-' * 28} {'-' * 12} {'-' * 16}")
    for m in CATCHMENT_METRICS:
        flag = "  <- target (NES)" if m == "sa2_nes_share" else ""
        print(f"  {m:<28} {html_counts[m]:>12d} {py_counts[m]:>16d}{flag}")
    print()

    baseline_html = html_counts["sa2_supply_ratio"]
    baseline_py = py_counts["sa2_supply_ratio"]
    nes_html = html_counts["sa2_nes_share"]
    nes_py = py_counts["sa2_nes_share"]

    print(f"  baseline (sa2_supply_ratio): {baseline_html} html / {baseline_py} python")
    print(f"  nes      (sa2_nes_share)   : {nes_html} html / {nes_py} python")
    print()

    print("Likely 'catchment_position' assembly locations:")
    html_hits = find_assembly_block(html_text)
    py_hits = find_assembly_block(py_text)
    print(f"  centre.html    : {len(html_hits)} hit(s)")
    for ln, sn in html_hits[:10]:
        print(f"    L{ln:>5d}: {sn[:100]}")
    print(f"  centre_page.py : {len(py_hits)} hit(s)")
    for ln, sn in py_hits[:10]:
        print(f"    L{ln:>5d}: {sn[:100]}")
    print()

    print("Card-assembly-shaped function definitions in centre_page.py:")
    fn_hits = find_card_assembly_functions(py_text)
    for ln, sn in fn_hits[:15]:
        print(f"    L{ln:>5d}: {sn[:100]}")
    print()

    # ----- B: Dynamic-pattern recon -------------------------------------
    print("=" * 72)
    print("B. DYNAMIC-PATTERN RECON — does a metric-driven loop exist?")
    print("=" * 72)
    py_dyn = find_dynamic_patterns_python(py_text)
    html_dyn = find_dynamic_patterns_html(html_text)

    print(f"  centre_page.py — Python iteration over LAYER3_METRIC_META: "
          f"{len(py_dyn)} hit(s)")
    for ln, sn in py_dyn[:15]:
        print(f"    L{ln:>5d}: {sn[:100]}")
    print()
    print(f"  centre.html    — JS iteration patterns (forEach/for..of/map): "
          f"{len(html_dyn)} hit(s)")
    for ln, sn in html_dyn[:15]:
        print(f"    L{ln:>5d}: {sn[:100]}")
    print()

    # ----- C: Recommendation -------------------------------------------
    print("=" * 72)
    print("C. RECOMMENDATION")
    print("=" * 72)

    total_baseline = baseline_html + baseline_py
    has_python_dyn = len(py_dyn) >= 2
    has_html_dyn = len(html_dyn) >= 3

    print(f"  baseline touchpoints (sa2_supply_ratio total) : {total_baseline}")
    print(f"  Python iteration over LAYER3_METRIC_META       : "
          f"{'yes' if has_python_dyn else 'no'}  ({len(py_dyn)} hit(s))")
    print(f"  JS iteration patterns in centre.html           : "
          f"{'yes' if has_html_dyn else 'no'}  ({len(html_dyn)} hit(s))")
    print()

    has_dynamic = has_python_dyn or has_html_dyn

    if total_baseline <= 4:
        rec = "SURGICAL"
        reason = ("Low touchpoint count. Surgical patch is the lowest-risk "
                  "path. Refactor would be net-new architecture for marginal "
                  "saved effort across upcoming Phase A items.")
    elif total_baseline <= 10 and has_dynamic:
        rec = "REFACTOR"
        reason = ("Moderate touchpoints AND a dynamic iteration pattern "
                  "already exists in the codebase. Refactor is 'make "
                  "catchment-position card match the existing pattern', "
                  "not net-new architecture. Expected to save ~0.6-0.9 sess "
                  "across A3/A4/B1/B5 follow-on render work.")
    elif total_baseline > 10 and has_dynamic:
        rec = "REFACTOR (strongly)"
        reason = ("High touchpoint count makes per-metric surgical patches "
                  "expensive across upcoming A3/A4/B1/B5 work. Existing "
                  "dynamic pattern lowers refactor risk significantly.")
    elif total_baseline > 10 and not has_dynamic:
        rec = "SURGICAL with refactor banked separately"
        reason = ("High touchpoint count but no existing dynamic pattern. "
                  "Refactor would be net-new architecture work. Recommend "
                  "shipping surgical for OI-36 to close the visible gap; "
                  "bank a 'catchment-card metric-driven refactor' OI for "
                  "scoping at next housekeeping pass.")
    else:
        rec = "SURGICAL"
        reason = ("Moderate touchpoints, no existing dynamic pattern. "
                  "Surgical is the safer bet; refactor cost not justified "
                  "without an existing pattern to conform to.")

    print(f"  RECOMMENDATION : {rec}")
    print(f"  REASON         : {reason}")
    print()
    print("Notes:")
    print("  - Inspect the assembly-block hits above to confirm auto-counts")
    print("    reflect actual hardcoding (not just comments / docstrings).")
    print("  - If you disagree with the recommendation, paste this output")
    print("    back to Claude for re-evaluation with full context.")
    print()
    print("[OK] Phase 1 probe complete — read-only, no mutations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
