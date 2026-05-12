"""
probe_oi36_phase3_5_render_path.py
==================================
Read-only probe.

The OI-36 patcher worked. centre_page.py is shipping sa2_nes_share in
the JSON payload (confirmed via /api/centre/2358 Preview tab). The
JS-side order array has been updated to include sa2_nes_share. Yet
the row does not render in the Catchment Position card.

Likely cause: renderPositionRow() — the function order.map() calls per
metric — has a row_weight branch (full / lite / context) and the lite
branch does something that renders nothing for catchment_position
metrics specifically. Need to see the actual code.

This probe extracts:
  1. renderPositionRow function definition (full body)
  2. _renderLiteRow function definition (full body) — if it exists
  3. _renderContextRow function definition (full body) — if it exists
  4. _renderFullRow function definition — first 50 lines for shape

Output to console + recon/oi36_render_path.txt.
"""

from __future__ import annotations

import sys
from pathlib import Path


def find_repo_root() -> Path | None:
    for c in [Path(__file__).resolve().parents[2], Path.cwd()]:
        if (c / "centre_page.py").exists():
            return c
    return None


def find_function_block(lines: list, fn_name: str, max_lines: int = 200) -> tuple:
    """Find a JS function definition block. Returns (start_line, end_line, body_lines).

    Looks for both `function name(` and `const name = ` and `name = (...) =>`."""
    patterns = [
        f"function {fn_name}(",
        f"const {fn_name} =",
        f"{fn_name} = (",
        f"{fn_name}(centre)",
        f"{fn_name}(p)",
        f"{fn_name}(key, p)",
        f"{fn_name}(k, p)",
    ]

    start = -1
    for i, ln in enumerate(lines):
        for p in patterns:
            if p in ln:
                start = i
                break
        if start >= 0:
            break

    if start < 0:
        return -1, -1, []

    # Walk forward tracking brace depth from the first { we see
    depth = 0
    started = False
    for j in range(start, min(len(lines), start + max_lines)):
        ln = lines[j]
        for ch in ln:
            if ch == "{":
                depth += 1
                started = True
            elif ch == "}":
                depth -= 1
                if started and depth == 0:
                    return start + 1, j + 1, lines[start:j + 1]
    return start + 1, start + max_lines, lines[start:start + max_lines]


def main() -> int:
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

    out_path = root / "recon" / "oi36_render_path.txt"
    out_path.parent.mkdir(exist_ok=True)
    out_fh = open(out_path, "w", encoding="utf-8", newline="\n")

    def emit(s: str = "") -> None:
        sys.stdout.write(s + "\n")
        out_fh.write(s + "\n")

    emit(f"[probe] centre.html: {centre_html}")
    emit(f"[probe] writing to : {out_path}")

    targets = [
        "renderPositionRow",
        "_renderFullRow",
        "_renderLiteRow",
        "_renderContextRow",
    ]

    for fn in targets:
        emit("")
        emit("=" * 72)
        emit(f"FUNCTION: {fn}")
        emit("=" * 72)
        s, e, body = find_function_block(lines, fn)
        if s < 0:
            emit(f"  [NOT FOUND] no definition matching {fn}")
            continue
        emit(f"  start L{s}  end L{e}  ({len(body)} lines)")
        emit("")
        # For _renderFullRow show only first 50 lines of body (it's huge)
        cap = 50 if fn == "_renderFullRow" else 200
        for k, ln in enumerate(body[:cap]):
            emit(f"  L{s + k:>5d}: {ln}")
        if len(body) > cap:
            emit(f"  ... ({len(body) - cap} more lines truncated)")

    out_fh.close()
    emit("")
    emit("[OK] complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
