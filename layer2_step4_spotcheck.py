# layer2_step4_spotcheck.py — read-only verification of nqs_history
import sqlite3, os
DB = os.path.join("data", "kintell.db")
conn = sqlite3.connect(DB)
cur = conn.cursor()
def q(sql, params=()):
    cur.execute(sql, params); return cur.fetchall()

print("=== 1. Coverage summary ===")
for label, sql in [
    ("nqs_history rowcount", "SELECT COUNT(*) FROM nqs_history"),
    ("unique service_approval_numbers", "SELECT COUNT(DISTINCT service_approval_number) FROM nqs_history"),
    ("unique provider_ids", "SELECT COUNT(DISTINCT provider_id) FROM nqs_history WHERE provider_id IS NOT NULL"),
    ("unique quarters", "SELECT COUNT(DISTINCT quarter) FROM nqs_history"),
    ("rows joining live services", "SELECT COUNT(DISTINCT nh.service_approval_number) FROM nqs_history nh JOIN services s ON s.service_approval_number = nh.service_approval_number"),
    ("orphan history sids (closed centres)", "SELECT COUNT(DISTINCT service_approval_number) FROM nqs_history WHERE service_approval_number NOT IN (SELECT service_approval_number FROM services WHERE service_approval_number IS NOT NULL)"),
]:
    print(f"  {label:<40} {q(sql)[0][0]:,}")

print("\n=== 2. Quarter coverage (rowcount per quarter, oldest -> newest) ===")
rows = q("""SELECT quarter, quarter_end_date, COUNT(*) AS n
              FROM nqs_history
             GROUP BY quarter, quarter_end_date
             ORDER BY quarter_end_date""")
for qtr, qe, n in rows:
    print(f"  {qtr:<8} {qe}  {n:>6}")

print("\n=== 3. Sparrow Ellenbrook centres — NQS history depth ===")
rows = q("""SELECT s.service_id, s.service_name, COUNT(nh.nqs_history_id) AS quarters_in_history,
                   MIN(nh.quarter_end_date) AS first_seen, MAX(nh.quarter_end_date) AS last_seen
              FROM services s
              LEFT JOIN nqs_history nh ON nh.service_approval_number = s.service_approval_number
             WHERE s.is_active=1
               AND s.suburb LIKE 'ELLENBROOK%'
               AND s.service_name LIKE '%Sparrow%' OR s.service_name LIKE '%Coolamon%' OR s.service_name LIKE '%Malvern Springs%'
             GROUP BY s.service_id, s.service_name
             LIMIT 8""")
for r in rows:
    print(f"  id={r[0]:<6} {r[1][:40]:<40} q_in_hist={r[2]:>3}  {r[3]} -> {r[4]}")

print("\n=== 4. PA-chain example: SE-00009638 (preflight sample) ===")
rows = q("""SELECT quarter, quarter_end_date, provider_id, provider_name, overall_rating
              FROM nqs_history
             WHERE service_approval_number='SE-00009638'
             ORDER BY quarter_end_date""")
for r in rows:
    print(f"  {r[0]:<8} {r[1]}  {r[2]:<14}  rating={r[4]!r:<25}  prov={r[3][:30]!r}")

print("\n=== 5. NQS rating drift over time — random LDC service ===")
rows = q("""SELECT service_approval_number FROM nqs_history
             WHERE service_type='Centre-Based Care' AND overall_rating IS NOT NULL
             GROUP BY service_approval_number
            HAVING COUNT(DISTINCT overall_rating) >= 3
             ORDER BY RANDOM() LIMIT 1""")
if rows:
    sample_san = rows[0][0]
    print(f"  sampled: {sample_san}")
    rows = q("""SELECT quarter_end_date, overall_rating
                  FROM nqs_history WHERE service_approval_number=?
                 ORDER BY quarter_end_date""", (sample_san,))
    last_rating = None
    for qe, r in rows:
        marker = " <-- change" if r != last_rating and last_rating is not None else ""
        print(f"    {qe}  {r!r}{marker}")
        last_rating = r

print("\n=== 6. Top 10 providers by quarters-of-history coverage ===")
rows = q("""SELECT provider_id, provider_name, COUNT(*) AS rowcount,
                   COUNT(DISTINCT service_approval_number) AS centres,
                   COUNT(DISTINCT quarter_end_date) AS quarters
              FROM nqs_history
             WHERE provider_id IS NOT NULL
             GROUP BY provider_id, provider_name
             ORDER BY rowcount DESC LIMIT 10""")
for r in rows:
    print(f"  {r[0]:<14} {(r[1] or '')[:40]:<40} rows={r[2]:>6} centres={r[3]:>4} qtrs={r[4]:>3}")

print("\n=== 7. Schema sanity — last 3 columns of a sample row ===")
rows = q("""SELECT service_approval_number, quarter, postcode, latitude, longitude,
                   long_day_care, oshc_after_school, max_places
              FROM nqs_history WHERE quarter='Q42025' LIMIT 5""")
for r in rows:
    print(f"  {r[0]:<14} {r[1]:<8} pc={r[2]} lat={r[3]} lng={r[4]} ldc={r[5]} oshc_after={r[6]} places={r[7]}")

conn.close()
