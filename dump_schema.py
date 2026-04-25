import sqlite3, pathlib
conn = sqlite3.connect("data/kintell.db")
cur = conn.cursor()
out = ["=== .schema ==="]
for (sql,) in cur.execute("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY type, name"):
    out.append(sql)
out.append("")
out.append("=== tables + row counts ===")
for (name,) in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
    count = cur.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
    out.append(f"{name}: {count} rows")
pathlib.Path("schema_dump.txt").write_text("\n".join(out), encoding="utf-8")
print("wrote schema_dump.txt")
