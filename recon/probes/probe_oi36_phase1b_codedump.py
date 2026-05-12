"""
probe_oi36_phase1b_codedump.py
==============================
Read-only code-region dump for OI-36 refactor authoring.

Phase 1 scoping confirmed REFACTOR. This probe extracts the specific
code regions Claude needs to read to author the patcher accurately
without guessing at file structure.

Output goes to BOTH stdout AND recon/oi36_codedump.txt so the operator
can paste the console output back, or share the file if it's too large
for the terminal.

Regions dumped:
  1. centre_page.py LAYER3_METRIC_META definitions (L575-700)
  2. centre_page.py LAYER3_METRIC_META iteration loops (L1640-1760)
  3. centre_page.py — other catchment_position mentions
  4. centre.html — position card rendering area (L2300-2400)
  5. centre.html — other catchment_position references

Read-only. No file mutations.
"""

from __future__ import annotations

import sys
from pathlib import Path


def find_repo_root() -> Path | None:
    for c in [Path(__file__).resolve().parents[2], Path.cwd()]:
        if (c / "centre_page.py").exists():
            return c
    return None


def find_file(root: Path, name: str, check_docs: bool = True) -> Path | None:
    candidates = [root / name]
    if check_docs:
        candidates.append(root / "docs" / name)
    for c in candidates:
        if c.exists():
            return c
    return None


def read_lines(path: Path) -> list:
    return path.read_bytes().decode("utf-8", errors="replace").splitlines()


def find_all(lines: list, needle: str) -> list:
    return [i + 1 for i, ln in enumerate(lines) if needle in ln]


class Output:
    """Write to both stdout and a file."""
    def __init__(self, file_path: Path):
        self.fh = open(file_path, "w", encoding="utf-8", newline="\n")

    def write(self, text: str) -> None:
        sys.stdout.write(text)
        self.fh.write(text)

    def close(self) -> None:
        self.fh.close()


def dump_region(out: Output, label: str, lines: list, start: int, end: int) -> None:
    out.write(f"\n--- {label} (L{start}-L{end}) ---\n")
    s = max(1, start) - 1
    e = min(len(lines), end)
    for i in range(s, e):
        out.write(f"  L{i+1:>5d}: {lines[i]}\n")


def section(out: Output, n: int, title: str) -> None:
    out.write("\n" + "=" * 76 + "\n")
    out.write(f"{n}. {title}\n")
    out.write("=" * 76 + "\n")


def main() -> int:
    root = find_repo_root()
    if root is None:
        print("[ERROR] could not locate repo root.")
        return 2

    centre_html = find_file(root, "centre.html")
    centre_py = find_file(root, "centre_page.py", check_docs=False)
    if centre_html is None or centre_py is None:
        print("[ERROR] could not find centre.html or centre_page.py")
        return 2

    out_path = root / "recon" / "oi36_codedump.txt"
    out_path.parent.mkdir(exist_ok=True)
    out = Output(out_path)

    out.write(f"[probe] centre_page.py : {centre_py}\n")
    out.write(f"[probe] centre.html    : {centre_html}\n")
    out.write(f"[probe] writing to     : {out_path}\n")

    py_lines = read_lines(centre_py)
    html_lines = read_lines(centre_html)

    # 1. LAYER3_METRIC_META catchment_position entries
    section(out, 1, "centre_page.py — LAYER3_METRIC_META + nearby (L575-L700)")
    cp_hits_py = find_all(py_lines, "catchment_position")
    out.write(f"  all 'catchment_position' lines in centre_page.py: {cp_hits_py}\n")
    dump_region(out, "META definitions area", py_lines, 575, 700)

    # 2. LAYER3_METRIC_META iteration loops
    section(out, 2, "centre_page.py — LAYER3_METRIC_META iteration loops")
    dump_region(out, "iter loop around L1659", py_lines, 1640, 1700)
    dump_region(out, "iter loop around L1697", py_lines, 1690, 1760)

    # 3. Other catchment_position mentions in centre_page.py
    section(out, 3, "centre_page.py — other catchment_position mentions (with context)")
    seen = set()
    for ln in cp_hits_py:
        if 575 <= ln <= 700 or 1640 <= ln <= 1760:
            continue
        bucket = ln // 40
        if bucket in seen:
            continue
        seen.add(bucket)
        dump_region(out, f"context for L{ln}", py_lines, ln - 8, ln + 14)

    # 4. centre.html position card rendering area
    section(out, 4, "centre.html — position card rendering area (L2300-L2400)")
    dump_region(out, "position-card render area", html_lines, 2300, 2400)

    # 5. Other catchment_position references in centre.html
    section(out, 5, "centre.html — all catchment_position references (with context)")
    cp_hits_html = find_all(html_lines, "catchment_position")
    out.write(f"  all 'catchment_position' lines in centre.html: {cp_hits_html}\n")
    seen = set()
    for ln in cp_hits_html:
        if 2300 <= ln <= 2400:
            continue
        bucket = ln // 40
        if bucket in seen:
            continue
        seen.add(bucket)
        dump_region(out, f"context for L{ln}", html_lines, ln - 8, ln + 18)

    out.write("\n[OK] code dump complete.\n")
    out.write(f"[OK] saved to {out_path}\n")
    out.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
