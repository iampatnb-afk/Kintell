# layer2_step1_spotcheck.py — read-only verification
import sqlite3, os
DB = os.path.join("data", "kintell.db")
conn = sqlite3.connect(DB)
cur = conn.cursor()

def q(sql, params=()):
    cur.execute(sql, params)
    return cur.fetchall()

print("=== 1. Coverage summary ===")
for label, sql in [
    ("active services total", "SELECT COUNT(*) FROM services WHERE is_active=1"),
    ("with sa2_code populated", "SELECT COUNT(*) FROM services WHERE is_active=1 AND sa2_code IS NOT NULL AND sa2_code != ''"),
    ("with sa2_name populated", "SELECT COUNT(*) FROM services WHERE is_active=1 AND sa2_name IS NOT NULL AND sa2_name != ''"),
    ("still NULL/empty", "SELECT COUNT(*) FROM services WHERE is_active=1 AND (sa2_code IS NULL OR sa2_code = '')"),
]:
    print(f"  {label:<32} {q(sql)[0][0]}")

print("\n=== 2. Sparrow Ellenbrook centres (postcode 6069) ===")
rows = q("""SELECT service_id, service_name, postcode, sa2_code, sa2_name
              FROM services
             WHERE is_active=1 AND postcode='6069'
             ORDER BY service_name LIMIT 10""")
for r in rows:
    print(f"  id={r[0]:<6} {r[1][:50]:<50} pc={r[2]} sa2={r[3]} {r[4]}")

print("\n=== 3. ACT spot checks (Garran/Mawson) ===")
rows = q("""SELECT service_id, service_name, postcode, sa2_code, sa2_name
              FROM services
             WHERE is_active=1 AND postcode IN ('2605','2607')
             ORDER BY service_id LIMIT 5""")
for r in rows:
    print(f"  id={r[0]:<4} {r[1][:45]:<45} pc={r[2]} sa2={r[3]} {r[4]}")

print("\n=== 4. Top 10 SA2s by service count ===")
rows = q("""SELECT sa2_code, sa2_name, COUNT(*) AS n
              FROM services
             WHERE is_active=1 AND sa2_code IS NOT NULL AND sa2_code != ''
             GROUP BY sa2_code, sa2_name
             ORDER BY n DESC LIMIT 10""")
for r in rows:
    print(f"  {r[2]:>4}  {r[0]}  {r[1]}")

print("\n=== 5. The 7 unbackfilled active services ===")
rows = q("""SELECT service_id, service_name, postcode, sa2_code
              FROM services
             WHERE is_active=1 AND (sa2_code IS NULL OR sa2_code = '')
             ORDER BY postcode, service_id""")
for r in rows:
    print(f"  id={r[0]:<6} {r[1][:50]:<50} pc={r[2]!r}  sa2={r[3]!r}")

print("\n=== 6. Latest audit_log row ===")
rows = q("""SELECT audit_id, actor, action, subject_type, occurred_at, substr(reason,1,120)
              FROM audit_log ORDER BY audit_id DESC LIMIT 1""")
for r in rows:
    print(f"  audit_id={r[0]} actor={r[1]} action={r[2]} subject={r[3]} at={r[4]}")
    print(f"  reason={r[5]}...")

conn.close()
