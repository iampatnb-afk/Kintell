"""
probe_oi37_window_subscription.py
=================================
Read-only.

For OI-37 we need Lite rows to re-render their delta badge when the
trend-window bar changes selection. Full rows already do something
similar — their charts re-filter on window change. Need to see HOW that
happens so the Lite badge can use the same pattern (rather than
inventing new subscription wiring).

Extracts:
  1. Trend-window button click handler(s) — what runs when user picks 3Y/5Y/10Y/All
  2. _filterTrajectoryByRange function — the existing window-filter logic
  3. _yearOfPeriod helper — extracts year from period_label/period strings
  4. Anything that re-renders or refreshes after window change
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def find_repo_root() -> Path | None:
    for c in [Path(__file__).resolve().parents[2], Path.cwd()]:
        if (c / "centre_page.py").exists():
            return c
    return None


def find_function_block(lines, fn_name, max_lines=200):
    patterns = [
        f"function {fn_name}(",
        f"const {fn_name} =",
        f"{fn_name} = (",
    ]
    start = -1
    for i, ln in enumerate(lines):
        if any(p in ln for p in patterns):
            start = i
            break
    if start < 0:
        return -1, -1, []
    depth = 0
    started = False
    for j in range(start, min(len(lines), start + max_lines)):
        for ch in lines[j]:
            if ch == "{":
                depth += 1
                started = True
            elif ch == "}":
                depth -= 1
                if started and depth == 0:
                    return start + 1, j + 1, lines[start:j + 1]
    return start + 1, start + max_lines, lines[start:start + max_lines]


def search_lines(lines, pattern, context=2):
    rx = re.compile(pattern)
    hits = []
    for i, ln in enumerate(lines):
        if rx.search(ln):
            s = max(0, i - context)
            e = min(len(lines), i + context + 1)
            hits.append((i + 1, lines[s:e], s + 1))
    return hits


def main():
    root = find_repo_root()
    if root is None:
        print("[ERROR] could not locate repo root.")
        return 2

    centre_html = root / "docs" / "centre.html"
    if not centre_html.exists():
        print(f"[ERROR] {centre_html} not found")
        return 2

    text = centre_html.read_bytes().decode("utf-8", errors="replace")
    lines = text.splitlines()

    out_path = root / "recon" / "oi37_window_subscription.txt"
    out_path.parent.mkdir(exist_ok=True)
    out_fh = open(out_path, "w", encoding="utf-8", newline="\n")

    def emit(s=""):
        sys.stdout.write(s + "\n")
        out_fh.write(s + "\n")

    emit(f"[probe] centre.html: {centre_html}")
    emit(f"[probe] writing to : {out_path}")

    # 1. Functions of interest
    targets = [
        "_filterTrajectoryByRange",
        "_yearOfPeriod",
        "_renderTrajectory",
    ]
    for fn in targets:
        emit("")
        emit("=" * 72)
        emit(f"FUNCTION: {fn}")
        emit("=" * 72)
        s, e, body = find_function_block(lines, fn)
        if s < 0:
            emit(f"  [NOT FOUND]")
            continue
        emit(f"  start L{s}  end L{e}  ({len(body)} lines)")
        emit("")
        for k, ln in enumerate(body[:80]):
            emit(f"  L{s + k:>5d}: {ln}")
        if len(body) > 80:
            emit(f"  ... ({len(body) - 80} more lines truncated)")

    # 2. Trend window button click / activeRange / range-btn handlers
    emit("")
    emit("=" * 72)
    emit("TREND-WINDOW EVENT WIRING")
    emit("=" * 72)
    for pattern, label in [
        (r"range-btn",          "range-btn occurrences"),
        (r"activeRange",        "activeRange occurrences"),
        (r"trajRangeBar",       "trajRangeBar occurrences"),
        (r"traj-range",         "traj-range occurrences"),
        (r"window\.location",   "window.location ref"),
    ]:
        emit("")
        emit(f"--- {label} ---")
        hits = search_lines(lines, pattern, context=3)
        if not hits:
            emit("  (no matches)")
        for line_no, ctx, start_line in hits[:8]:
            emit(f"  L{line_no} (showing context):")
            for k, ln in enumerate(ctx):
                marker = " >>>" if (start_line + k) == line_no else "    "
                emit(f"  {marker} L{start_line + k:>5d}: {ln}")
            emit("")

    # 3. _renderLiteRow location — for patch reference
    emit("")
    emit("=" * 72)
    emit("LITE ROW REMINDER (for patch context)")
    emit("=" * 72)
    s, e, body = find_function_block(lines, "_renderLiteRow")
    emit(f"  _renderLiteRow at L{s}-L{e} (full body in oi36_render_path.txt)")
    emit(f"  Key lines for patch insertion point:")
    for k, ln in enumerate(body):
        if "asAtStamp" in ln or "p.trajectory" in ln or "asAtRaw" in ln:
            emit(f"  L{s + k:>5d}: {ln}")

    out_fh.close()
    emit("")
    emit("[OK] complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
