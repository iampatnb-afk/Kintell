import json
with open("docs/sa2_history.json", encoding="utf-8") as f:
    d = json.load(f)
sa2 = next((s for s in d["sa2s"] if s["sa2_code"] == "211011251"), None)
if not sa2:
    print("Bayswater SA2 211011251 NOT FOUND in sa2_history.json")
    print("\nSimilar SA2 codes (likely ASGS-version siblings):")
    candidates = [s for s in d["sa2s"] if s["sa2_code"].startswith("21101")]
    for s in candidates[:10]:
        print(f"  {s['sa2_code']}  {s['sa2_name']}")
else:
    print(f"SA2: {sa2['sa2_code']} ({sa2['sa2_name']})")
    print(f"  quarters total: {len(sa2['quarters'])}")
    print()
    n_pop  = sum(1 for x in sa2['pop_0_4'] if x is not None)
    n_inc  = sum(1 for x in sa2['income'] if x is not None)
    n_ldc_places = sum(1 for x in sa2['by_subtype']['LDC']['places'] if x is not None)
    n_ldc_sr     = sum(1 for x in sa2['by_subtype']['LDC']['supply_ratio'] if x is not None)
    print(f"  pop_0_4 non-null:               {n_pop}/{len(sa2['quarters'])}")
    print(f"  income  non-null:               {n_inc}/{len(sa2['quarters'])}")
    print(f"  LDC places non-null:            {n_ldc_places}/{len(sa2['quarters'])}")
    print(f"  LDC supply_ratio non-null:      {n_ldc_sr}/{len(sa2['quarters'])}")
    print()
    # Find the first and last quarters where supply_ratio is populated
    qs = sa2['quarters']
    sr = sa2['by_subtype']['LDC']['supply_ratio']
    first = next((qs[i] for i, v in enumerate(sr) if v is not None), None)
    last  = next((qs[i] for i, v in enumerate(reversed(sr)) if v is not None), None)
    if last:
        last_idx = len(sr) - 1 - sr[::-1].index(next(v for v in reversed(sr) if v is not None))
        last = qs[last_idx]
    print(f"  LDC supply_ratio range:         {first} -> {last}")
    print()
    # Show pop_0_4 by year to identify the gap pattern
    print("  pop_0_4 by quarter (first 50):")
    for i in range(min(50, len(qs))):
        marker = "" if sa2['pop_0_4'][i] is not None else "    *** GAP ***"
        if i % 4 == 0 or marker:
            print(f"    {qs[i]:<10} pop={sa2['pop_0_4'][i]} {marker}")
