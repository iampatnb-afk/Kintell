import urllib.request, json, pathlib, sys
BASE = "http://127.0.0.1:8001"
targets = {"sparrow_1887": 1887, "harmony_236": 236}
results = {}
for label, gid in targets.items():
    try:
        with urllib.request.urlopen(f"{BASE}/api/operator/{gid}", timeout=10) as r:
            results[label] = json.loads(r.read())
        print(f"{label}: OK")
    except Exception as e:
        results[label] = {"ERROR": str(e)}
        print(f"{label}: ERROR {e}")
pathlib.Path("operator_payload_snapshot.json").write_text(
    json.dumps(results, indent=2, default=str), encoding="utf-8"
)
print("wrote operator_payload_snapshot.json")
