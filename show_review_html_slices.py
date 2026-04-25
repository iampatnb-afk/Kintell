"""
show_review_html_slices.py  v1
------------------------------
Read-only. Prints slices of docs/review.html around every match for:
  - /api/centres
  - 'load failed' (case-insensitive)
  - <details>                  (likely where the toggle is bound)
  - addEventListener('toggle'  (the lazy-load trigger)
  - renderCentres / centreList / centres_list / data.centres

Each match gets 20 lines of context on either side, labelled with line
numbers, so we can see the handler end-to-end without the whole file.
"""

import re
from pathlib import Path

FILE = Path("docs/review.html")
CONTEXT = 20

PATTERNS = [
    r"/api/centres",
    r"load\s*failed",
    r"<details",
    r"addEventListener\(\s*['\"]toggle",
    r"\btoggle\b",
    r"renderCentres",
    r"centreList|centres_list",
    r"data\.centres",
]


def main() -> None:
    if not FILE.exists():
        print(f"{FILE} not found.")
        return

    lines = FILE.read_text(encoding="utf-8", errors="replace").splitlines()
    n = len(lines)
    print(f"File: {FILE}  ({n} lines)")

    combined = re.compile("|".join(PATTERNS), re.IGNORECASE)

    # Find all match line numbers (1-based)
    hits = [i + 1 for i, line in enumerate(lines) if combined.search(line)]
    if not hits:
        print("No pattern hits.")
        return

    # Merge overlapping context windows
    windows = []
    for h in hits:
        start = max(1, h - CONTEXT)
        end = min(n, h + CONTEXT)
        if windows and start <= windows[-1][1] + 1:
            windows[-1] = (windows[-1][0], max(windows[-1][1], end))
        else:
            windows.append((start, end))

    for start, end in windows:
        print()
        print("=" * 72)
        print(f"  Lines {start}..{end}")
        print("=" * 72)
        for ln in range(start, end + 1):
            marker = " >>" if ln in hits else "   "
            print(f"{ln:>5}{marker} {lines[ln - 1]}")


if __name__ == "__main__":
    main()
