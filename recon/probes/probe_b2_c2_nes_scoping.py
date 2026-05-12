r"""
B2 + C2-NES scoping probe.

Read-only extraction of:
  - layer3_apply.py (or equivalent) configuration pattern for metrics
  - centre_page.py LAYER3_METRIC_META (and related constants)
  - existing Lite-weight catchment row pattern (closest analogue for NES)

Run from repo root:
    python recon\probes\probe_b2_c2_nes_scoping.py
"""

import re
from pathlib import Path

CANDIDATES_LAYER3 = [
    Path("layer3_apply.py"),
    Path("layer3_sa2_metric_banding_apply.py"),
]

CENTRE_PAGE = Path("centre_page.py")


def section(t):
    print()
    print("=" * 72)
    print(t)
    print("=" * 72)


def show_block(text, line_no, before=2, after=8):
    lines = text.splitlines()
    start = max(0, line_no - 1 - before)
    end = min(len(lines), line_no + after)
    for i in range(start, end):
        marker = ">>" if i == line_no - 1 else "  "
        print(f"  {marker} L{i+1:4}: {lines[i]}")


def main():
    # ---------------------------------------------------------------
    section("1. Find layer3 apply script")
    layer3_path = None
    for c in CANDIDATES_LAYER3:
        if c.exists():
            layer3_path = c
            print(f"  Found: {c}")
            break
    if layer3_path is None:
        # Search filesystem
        matches = list(Path(".").glob("layer3*.py"))
        print(f"  Default candidates not found.")
        print(f"  Filesystem search for layer3*.py: {matches}")
        if matches:
            layer3_path = matches[0]
            print(f"  Using: {layer3_path}")

    # ---------------------------------------------------------------
    if layer3_path:
        section(f"2. layer3 apply — metric definitions in {layer3_path.name}")
        text = layer3_path.read_text(encoding="utf-8")
        lines = text.splitlines()
        print(f"  Total lines: {len(lines)}")

        # Look for METRIC_DEFINITIONS, METRICS, METRIC_META, etc.
        for pat in ["METRIC_DEFINITIONS", "METRICS =", "METRIC_META",
                    "METRIC_CONFIG", "METRIC_LIST", "metric_definitions"]:
            for i, ln in enumerate(lines, start=1):
                if pat in ln:
                    print(f"\n  [HIT] {pat} at L{i}:")
                    show_block(text, i, before=1, after=20)
                    break

        # Show all DICT / list definitions whose name contains 'METRIC'
        print("\n  All top-level constants matching METRIC:")
        for i, ln in enumerate(lines, start=1):
            if re.match(r"^[A-Z_]*METRIC[A-Z_]*\s*=", ln):
                print(f"    L{i:4}: {ln.rstrip()}")

        # Show how lfp_females (closest census-based analogue) is defined
        print("\n  LFP / Census references (closest NES analogue):")
        for i, ln in enumerate(lines, start=1):
            if "lfp_female" in ln.lower() or "census_lfp" in ln.lower():
                print(f"    L{i:4}: {ln.rstrip()}")

    # ---------------------------------------------------------------
    if not CENTRE_PAGE.exists():
        print(f"\nERROR: {CENTRE_PAGE} not found.")
        return

    section(f"3. centre_page.py — LAYER3_METRIC_META + related constants")
    text = CENTRE_PAGE.read_text(encoding="utf-8")
    lines = text.splitlines()
    print(f"  Total lines: {len(lines)}")

    # Show all top-level LAYER3_* constant declarations
    print("\n  Top-level LAYER3_ constants:")
    for i, ln in enumerate(lines, start=1):
        if re.match(r"^LAYER3_", ln):
            print(f"    L{i:4}: {ln.rstrip()}")

    # ---------------------------------------------------------------
    section("4. LAYER3_METRIC_META content")
    for i, ln in enumerate(lines, start=1):
        if re.match(r"^LAYER3_METRIC_META\s*=", ln):
            # Print the whole dict
            print(f"  Found at L{i}. Showing full definition:")
            depth = 0
            for j in range(i - 1, min(i + 200, len(lines))):
                content = lines[j]
                depth += content.count("{") - content.count("}")
                print(f"  L{j+1:4}: {content}")
                if depth == 0 and j > i - 1:
                    break
            break

    # ---------------------------------------------------------------
    section("5. How sa2_lfp_females (Lite catchment Census metric) is registered")
    # Find sa2_lfp_females references in centre_page.py
    for i, ln in enumerate(lines, start=1):
        if "sa2_lfp_females" in ln:
            print(f"  L{i:4}: {ln.rstrip()}")

    # ---------------------------------------------------------------
    section("6. LAYER3_METRIC_TRAJECTORY_SOURCE content (for trajectory sourcing)")
    for i, ln in enumerate(lines, start=1):
        if re.match(r"^LAYER3_METRIC_TRAJECTORY_SOURCE\s*=", ln):
            print(f"  Found at L{i}. Showing full definition:")
            depth = 0
            for j in range(i - 1, min(i + 100, len(lines))):
                content = lines[j]
                depth += content.count("{") - content.count("}")
                print(f"  L{j+1:4}: {content}")
                if depth == 0 and j > i - 1:
                    break
            break

    # ---------------------------------------------------------------
    section("7. LAYER3_METRIC_INTENT_COPY — find sa2_lfp_* example to copy from")
    found_intent = False
    for i, ln in enumerate(lines, start=1):
        if re.match(r"^LAYER3_METRIC_INTENT_COPY\s*=", ln):
            found_intent = True
            print(f"  Found at L{i}. Showing first ~50 lines:")
            for j in range(i - 1, min(i + 80, len(lines))):
                print(f"  L{j+1:4}: {lines[j]}")
            break
    if not found_intent:
        print("  Not found by exact name. Searching for 'INTENT_COPY':")
        for i, ln in enumerate(lines, start=1):
            if "INTENT_COPY" in ln and "=" in ln:
                print(f"    L{i:4}: {ln.rstrip()}")

    print()
    print("Done. Read-only probe.")


if __name__ == "__main__":
    main()
