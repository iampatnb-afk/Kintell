r"""
Recovery probe — assess layer3_sa2_metric_banding damage and locate the
catchment-banding script.

Read-only.
    python recovery_probe.py
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("data") / "kintell.db"


def section(t):
    print()
    print("=" * 72)
    print(t)
    print("=" * 72)


def main():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    # ----------------------------------------------------------------
    section("1. Current metrics in layer3_sa2_metric_banding")
    rows = cur.execute(
        "SELECT metric, COUNT(*) FROM layer3_sa2_metric_banding "
        "GROUP BY metric ORDER BY metric"
    ).fetchall()
    print(f"  Distinct metrics: {len(rows)}")
    catchment_expected = {"sa2_supply_ratio", "sa2_demand_supply",
                          "sa2_child_to_place", "sa2_adjusted_demand"}
    present = {r[0] for r in rows}
    for metric, count in rows:
        marker = "  catchment" if metric in catchment_expected else ""
        print(f"    {metric:<35} {count:>6,}{marker}")
    missing = catchment_expected - present
    if missing:
        print(f"\n  MISSING catchment metrics: {sorted(missing)}")
    else:
        print(f"\n  All catchment metrics present.")

    # ----------------------------------------------------------------
    section("2. service_catchment_cache state (data source intact?)")
    rc = cur.execute("SELECT COUNT(*) FROM service_catchment_cache").fetchone()[0]
    print(f"  Row count: {rc:,}")
    sample = cur.execute(
        "SELECT supply_ratio, demand_supply, child_to_place, adjusted_demand "
        "FROM service_catchment_cache WHERE supply_ratio IS NOT NULL LIMIT 3"
    ).fetchall()
    print(f"  Sample rows (non-null supply_ratio):")
    for r in sample:
        print(f"    sr={r[0]}, ds={r[1]}, ctp={r[2]}, ad={r[3]}")

    # ----------------------------------------------------------------
    section("3. audit_log history for layer3_catchment_banding")
    rows = cur.execute(
        "SELECT audit_id, action, occurred_at, after_json FROM audit_log "
        "WHERE action LIKE '%catchment_banding%' OR action LIKE '%layer3%' "
        "ORDER BY audit_id DESC LIMIT 15"
    ).fetchall()
    for r in rows:
        after = (r[3] or "")[:120]
        print(f"  audit_id={r[0]:>4}  {r[1]:<45}  {r[2]}")
        if after:
            print(f"             after_json: {after}...")

    con.close()

    # ----------------------------------------------------------------
    section("4. Filesystem search — candidate catchment banding scripts")
    repo_root = Path(".")
    candidates = []
    for pat in ["*catchment*band*.py", "*layer3*catchment*.py",
                "*step_2_5_2*.py", "*sub_pass_2_5_2*.py", "*2_5_2*.py"]:
        for p in repo_root.glob(pat):
            if p.is_file():
                candidates.append(p)
    candidates = sorted(set(candidates))
    if candidates:
        print(f"  Candidate scripts found:")
        for c in candidates:
            print(f"    {c}  ({c.stat().st_size:,} bytes)")
    else:
        print(f"  No exact-name matches.")

    # Also check populate_service_catchment_cache.py for embedded banding
    pop = Path("populate_service_catchment_cache.py")
    if pop.exists():
        text = pop.read_text(encoding="utf-8")
        if "layer3_catchment_banding" in text or "layer3_sa2_metric_banding" in text:
            print(f"\n  populate_service_catchment_cache.py contains banding-related code.")
            for i, ln in enumerate(text.splitlines(), 1):
                if "layer3_sa2_metric_banding" in ln or "layer3_catchment_banding" in ln:
                    print(f"    L{i:4}: {ln.strip()[:120]}")

    # Also search for any .py with "sa2_supply_ratio" to find the catchment-banding home
    print(f"\n  Files mentioning 'sa2_supply_ratio' (likely contain catchment banding logic):")
    for p in repo_root.glob("*.py"):
        if not p.is_file():
            continue
        try:
            text = p.read_text(encoding="utf-8")
            if "sa2_supply_ratio" in text and "layer3" in text.lower():
                # Count lines mentioning sa2_supply_ratio
                hits = sum(1 for ln in text.splitlines() if "sa2_supply_ratio" in ln)
                print(f"    {p.name}  ({hits} sa2_supply_ratio hits)")
        except Exception:
            pass

    print()
    print("Done. Read-only probe.")


if __name__ == "__main__":
    main()
