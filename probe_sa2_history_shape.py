import json
with open("docs/sa2_history.json", encoding="utf-8") as f:
    d = json.load(f)
arr = d.get("sa2s", d) if isinstance(d, dict) else d
sa2 = next((s for s in arr if s.get("sa2_code") == "118011341"), None)
if not sa2:
    print("NOT FOUND")
else:
    print("keys:", list(sa2.keys()))
    print("quarters count:", len(sa2.get("quarters", [])))
    print("centre_events count:", len(sa2.get("centre_events", [])))
    print("first event keys:", list(sa2["centre_events"][0].keys()) if sa2.get("centre_events") else "(none)")
    print("first event sample:", sa2["centre_events"][0] if sa2.get("centre_events") else "(none)")
