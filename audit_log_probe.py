"""
audit_log_probe.py — Dump audit_log schema + last 3 rows. Read-only.
"""
import sqlite3

conn = sqlite3.connect("file:data/kintell.db?mode=ro", uri=True)
cur = conn.cursor()

print("=== audit_log schema (PRAGMA table_info) ===")
print("cid | name | type | notnull | default | pk")
print("----+------+------+---------+---------+---")
for cid, cname, ctype, notnull, dflt, pk in cur.execute(
    "PRAGMA table_info(audit_log)"
).fetchall():
    print(f"{cid} | {cname} | {ctype} | {notnull} | {dflt} | {pk}")

print()
print("=== last 3 audit_log rows ===")
cur.execute("SELECT * FROM audit_log ORDER BY rowid DESC LIMIT 3")
col_names = [d[0] for d in cur.description]
for row in cur.fetchall():
    print()
    print("---")
    for c, v in zip(col_names, row):
        sv = "(NULL)" if v is None else str(v)
        if len(sv) > 200:
            sv = sv[:197] + "..."
        print(f"  {c}: {sv}")

print()
print("=== distinct subject_type values (if column exists) ===")
audit_cols = [c[1] for c in cur.execute("PRAGMA table_info(audit_log)").fetchall()]
if "subject_type" in audit_cols:
    rows = cur.execute(
        "SELECT subject_type, COUNT(*) FROM audit_log "
        "GROUP BY subject_type ORDER BY 2 DESC"
    ).fetchall()
    for st, n in rows:
        print(f"  {st!r}: {n}")
else:
    print("  (no subject_type column)")

conn.close()
