"""
probe_4_2_a_3_verification_sa2.py — read-only.

Picks a verification service_id for sub-pass 4.2-A.3:
  - In a Major-Cities NSW SA2 (state_code='1', ra_band=1)
  - With non-null catchment ratios in service_catchment_cache
  - Cohort large enough that all 4 banded metrics have rows
  - Active service

Then dumps everything the renderer will read for that service_id:
  - service_catchment_cache row (24 cols)
  - layer3_sa2_metric_banding rows for the 4 catchment metrics
    (sa2_supply_ratio, sa2_child_to_place, sa2_adjusted_demand,
     sa2_demand_supply)
  - sa2_cohort row
  - existing _layer3_position output proxy (just shows what
    rows are findable; doesn't import centre_page)

Output gives me a known-good test case for the implementation
+ confirms data is renderable end-to-end.

No DB writes.
"""

import os
import sqlite3

DB_PATH = os.path.join("data", "kintell.db")


def main():
    if not os.path.exists(DB_PATH):
        print(f"ERROR: {DB_PATH} missing")
        return

    uri = f"file:{DB_PATH}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # --- 1. Find a verification service ----------------------------------
    print("=" * 72)
    print(" 1. PICKING VERIFICATION SERVICE")
    print("=" * 72)

    cur.execute("""
        SELECT s.service_id, s.service_name, s.suburb, s.state,
               s.sa2_code, s.sa2_name, s.approved_places,
               c.u5_pop, c.supply_ratio, c.child_to_place,
               c.adjusted_demand, c.demand_supply,
               c.demand_share_state, c.calibrated_rate,
               c.competing_centres_count
        FROM services s
        JOIN service_catchment_cache c USING (service_id)
        JOIN sa2_cohort coh USING (sa2_code)
        WHERE s.is_active = 1
          AND coh.state_code = '1'      -- NSW
          AND coh.ra_band = 1            -- Major Cities
          AND c.supply_ratio IS NOT NULL
          AND c.child_to_place IS NOT NULL
          AND c.adjusted_demand IS NOT NULL
          AND c.demand_supply IS NOT NULL
          AND c.demand_share_state IS NOT NULL
          AND c.competing_centres_count >= 3
        ORDER BY s.service_id
        LIMIT 1
    """)
    pick = cur.fetchone()
    if not pick:
        print("ERROR: no candidate found")
        return

    sid = pick["service_id"]
    sa2 = pick["sa2_code"]
    print(f"\nverification service_id = {sid}")
    print(f"  name        : {pick['service_name']}")
    print(f"  suburb      : {pick['suburb']}, {pick['state']}")
    print(f"  sa2         : {sa2} ({pick['sa2_name']})")
    print(f"  places      : {pick['approved_places']}")
    print(f"  competing   : {pick['competing_centres_count']}")

    # --- 2. Cache row ---------------------------------------------------
    print()
    print("=" * 72)
    print(" 2. service_catchment_cache row")
    print("=" * 72)
    cur.execute(
        "SELECT * FROM service_catchment_cache WHERE service_id = ?",
        (sid,),
    )
    cache = cur.fetchone()
    print()
    for k in cache.keys():
        v = cache[k]
        if isinstance(v, str) and len(v) > 70:
            v = v[:67] + "..."
        print(f"  {k:<28} {v}")

    # --- 3. Layer 3 banding rows for the 4 new catchment metrics --------
    print()
    print("=" * 72)
    print(" 3. layer3_sa2_metric_banding for catchment metrics")
    print("=" * 72)
    metrics = ["sa2_supply_ratio", "sa2_child_to_place",
               "sa2_adjusted_demand", "sa2_demand_supply"]
    placeholders = ",".join("?" for _ in metrics)
    cur.execute(
        f"SELECT * FROM layer3_sa2_metric_banding "
        f"WHERE sa2_code = ? AND metric IN ({placeholders}) "
        f"ORDER BY metric",
        (sa2, *metrics),
    )
    rows = cur.fetchall()
    if not rows:
        print(f"\n  NO ROWS — banding missing for SA2 {sa2}")
    else:
        print()
        for row in rows:
            print(f"  {row['metric']}:")
            for k in row.keys():
                v = row[k]
                if isinstance(v, float):
                    v = f"{v:.4f}"
                print(f"    {k:<14} {v}")
            print()

    # --- 4. sa2_cohort row ----------------------------------------------
    print("=" * 72)
    print(" 4. sa2_cohort row (for cohort labelling)")
    print("=" * 72)
    cur.execute("SELECT * FROM sa2_cohort WHERE sa2_code = ?", (sa2,))
    coh = cur.fetchone()
    print()
    for k in coh.keys():
        print(f"  {k:<14} {coh[k]}")

    # --- 5. Layer 3 row count for this SA2 (existing metrics) -----------
    print()
    print("=" * 72)
    print(" 5. existing layer3 metrics for this SA2")
    print("=" * 72)
    cur.execute(
        "SELECT metric, decile, band, cohort_n FROM "
        "layer3_sa2_metric_banding WHERE sa2_code = ? "
        "ORDER BY metric",
        (sa2,),
    )
    print()
    for row in cur.fetchall():
        print(f"  {row['metric']:<28} decile={row['decile']:<3} "
              f"band={row['band']:<5} cohort_n={row['cohort_n']}")

    # --- 6. URL for spot-check ------------------------------------------
    print()
    print("=" * 72)
    print(f" SPOT-CHECK URL: centre.html?id={sid}")
    print("=" * 72)

    conn.close()


if __name__ == "__main__":
    main()
