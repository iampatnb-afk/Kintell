"""
smoke_test_centre_page_v9.py — read-only.

Quick verification of Layer 4.2-A.3 Python-side wiring before the
live HTML spot-check. Calls get_centre_payload(103) — verification
service Kool HQ Waverley, Bondi Junction - Waverly SA2 — and
asserts:

  - schema_version == 'centre_payload_v5'
  - position dict has 'catchment_position' key
  - all 5 catchment metrics present with confidence='normal'
  - sa2_supply_ratio.raw_value matches the cache (~2.25)
  - sa2_supply_ratio.reversible == True with pair_with set
  - sa2_demand_share_state.raw_value matches the cache (~0.00187)
  - sa2_demand_share_state has no decile/band (unbanded)
  - intent_copy populated from the sa2_-prefixed keys

Prints PASS or FAIL per check. Exits 0 on all-pass.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from centre_page import get_centre_payload  # noqa


VERIFICATION_SID = 103


def check(name, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {name}{(' — ' + detail) if detail else ''}")
    return ok


def main():
    print(f"smoke test: get_centre_payload({VERIFICATION_SID})")
    print()

    payload = get_centre_payload(VERIFICATION_SID)
    if payload is None:
        print("ERROR: get_centre_payload returned None")
        sys.exit(2)

    all_ok = True

    # 1. schema version
    sv = payload.get("schema_version")
    all_ok &= check("schema_version is centre_payload_v5",
                    sv == "centre_payload_v5",
                    f"got {sv!r}")

    # 2. position has catchment_position
    pos = payload.get("position", {})
    cp = pos.get("catchment_position")
    all_ok &= check("position.catchment_position exists",
                    cp is not None,
                    f"keys: {list(pos.keys())}")

    if not cp:
        print("CANNOT CONTINUE — no catchment_position block")
        sys.exit(1)

    # 3. all 5 entries
    expected = {"sa2_supply_ratio", "sa2_demand_supply",
                "sa2_child_to_place", "sa2_adjusted_demand",
                "sa2_demand_share_state"}
    all_ok &= check("all 5 catchment metrics in catchment_position",
                    set(cp.keys()) >= expected,
                    f"got: {sorted(cp.keys())}")

    # 4. supply_ratio sanity
    sr = cp.get("sa2_supply_ratio") or {}
    rv = sr.get("raw_value")
    all_ok &= check(
        "sa2_supply_ratio.raw_value ~ 2.25",
        rv is not None and 2.0 < rv < 2.5,
        f"got {rv}",
    )
    all_ok &= check(
        "sa2_supply_ratio.confidence == 'normal'",
        sr.get("confidence") == "normal",
        f"got {sr.get('confidence')!r}",
    )
    all_ok &= check(
        "sa2_supply_ratio.decile == 10",
        sr.get("decile") == 10,
        f"got {sr.get('decile')}",
    )
    all_ok &= check(
        "sa2_supply_ratio.band == 'high'",
        sr.get("band") == "high",
        f"got {sr.get('band')!r}",
    )
    all_ok &= check(
        "sa2_supply_ratio.reversible == True",
        sr.get("reversible") is True,
        f"got {sr.get('reversible')!r}",
    )
    all_ok &= check(
        "sa2_supply_ratio.pair_with == 'sa2_child_to_place'",
        sr.get("pair_with") == "sa2_child_to_place",
        f"got {sr.get('pair_with')!r}",
    )
    all_ok &= check(
        "sa2_supply_ratio.intent_copy populated",
        bool(sr.get("intent_copy")),
        (sr.get("intent_copy") or "")[:60],
    )

    # 5. demand_share_state sanity (unbanded)
    ds = cp.get("sa2_demand_share_state") or {}
    rv = ds.get("raw_value")
    all_ok &= check(
        "sa2_demand_share_state.raw_value ~ 0.00187",
        rv is not None and 0.001 < rv < 0.005,
        f"got {rv}",
    )
    all_ok &= check(
        "sa2_demand_share_state.confidence == 'normal'",
        ds.get("confidence") == "normal",
        f"got {ds.get('confidence')!r}",
    )
    all_ok &= check(
        "sa2_demand_share_state.decile is None (unbanded)",
        ds.get("decile") is None,
        f"got {ds.get('decile')!r}",
    )
    all_ok &= check(
        "sa2_demand_share_state.row_weight == 'context'",
        ds.get("row_weight") == "context",
        f"got {ds.get('row_weight')!r}",
    )

    # 6. demand_supply reversibility
    dsy = cp.get("sa2_demand_supply") or {}
    all_ok &= check(
        "sa2_demand_supply.reversible == True",
        dsy.get("reversible") is True,
        f"got {dsy.get('reversible')!r}",
    )
    all_ok &= check(
        "sa2_demand_supply.row_weight == 'lite'",
        dsy.get("row_weight") == "lite",
        f"got {dsy.get('row_weight')!r}",
    )

    # 7. existing population/labour blocks still populated
    all_ok &= check(
        "position.population still populated",
        bool(pos.get("population")),
        f"keys: {list((pos.get('population') or {}).keys())[:3]}…",
    )
    all_ok &= check(
        "position.labour_market still populated",
        bool(pos.get("labour_market")),
        f"keys: {list((pos.get('labour_market') or {}).keys())[:3]}…",
    )

    print()
    if all_ok:
        print("ALL CHECKS PASSED.")
        sys.exit(0)
    else:
        print("SOME CHECKS FAILED. Inspect above.")
        # Dump the catchment_position block for debugging
        print()
        print("catchment_position dump:")
        print(json.dumps(cp, indent=2, default=str))
        sys.exit(1)


if __name__ == "__main__":
    main()
