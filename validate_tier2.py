import sqlite3, json
conn = sqlite3.connect("data/kintell.db")

def show(label, gid):
    print(f"\n==== {label} (gid {gid}) ====")
    row = conn.execute(
        "SELECT canonical_name, display_name, ownership_type "
        "FROM groups WHERE group_id = ?", (gid,)).fetchone()
    print(f"  group: canonical={row[0]!r}  display={row[1]!r}  ownership_type={row[2]!r}")

    # Service-level coverage counts across this group's services
    stats = conn.execute("""
        SELECT COUNT(*) AS n,
               SUM(CASE WHEN lat IS NOT NULL THEN 1 ELSE 0 END) AS lat_n,
               SUM(CASE WHEN aria_plus IS NOT NULL THEN 1 ELSE 0 END) AS aria_n,
               SUM(CASE WHEN seifa_decile IS NOT NULL THEN 1 ELSE 0 END) AS seifa_n,
               SUM(CASE WHEN service_sub_type IS NOT NULL THEN 1 ELSE 0 END) AS sst_n,
               SUM(CASE WHEN provider_management_type IS NOT NULL THEN 1 ELSE 0 END) AS pmt_n,
               SUM(CASE WHEN rating_issued_date IS NOT NULL THEN 1 ELSE 0 END) AS rid_n,
               SUM(CASE WHEN qa1 IS NOT NULL THEN 1 ELSE 0 END) AS qa1_n
          FROM services s
          JOIN entities e ON e.entity_id = s.entity_id
         WHERE e.group_id = ? AND s.is_active = 1
    """, (gid,)).fetchone()
    n = stats[0]
    print(f"  services active: {n}")
    print(f"    lat populated        : {stats[1]}/{n}")
    print(f"    aria_plus populated  : {stats[2]}/{n}")
    print(f"    seifa populated      : {stats[3]}/{n}")
    print(f"    sub_type populated   : {stats[4]}/{n}")
    print(f"    pmt populated        : {stats[5]}/{n}")
    print(f"    rating_date populated: {stats[6]}/{n}")
    print(f"    qa1 populated        : {stats[7]}/{n}")

    # ARIA+ band distribution
    aria_dist = conn.execute("""
        SELECT COALESCE(aria_plus,'(null)') AS a, COUNT(*)
          FROM services s
          JOIN entities e ON e.entity_id = s.entity_id
         WHERE e.group_id = ? AND s.is_active = 1
         GROUP BY a ORDER BY 2 DESC
    """, (gid,)).fetchall()
    print("  ARIA+ distribution:")
    for band, ct in aria_dist:
        print(f"    {band:35} {ct}")

    # SEIFA decile distribution
    seifa_dist = conn.execute("""
        SELECT seifa_decile, COUNT(*)
          FROM services s
          JOIN entities e ON e.entity_id = s.entity_id
         WHERE e.group_id = ? AND s.is_active = 1
         GROUP BY seifa_decile ORDER BY seifa_decile
    """, (gid,)).fetchall()
    print("  SEIFA decile distribution:")
    for dec, ct in seifa_dist:
        label = str(dec) if dec is not None else "(null)"
        print(f"    decile {label:>5}  {ct}")

    # Service sub type distribution
    sst_dist = conn.execute("""
        SELECT COALESCE(service_sub_type,'(null)'), COUNT(*)
          FROM services s JOIN entities e ON e.entity_id = s.entity_id
         WHERE e.group_id = ? AND s.is_active = 1
         GROUP BY 1 ORDER BY 2 DESC
    """, (gid,)).fetchall()
    print("  Service Sub Type:")
    for t, ct in sst_dist:
        print(f"    {t:10} {ct}")

    # Sample 2 services — show what's actually in a row now
    sample = conn.execute("""
        SELECT service_name, lat, lng, aria_plus, seifa_decile,
               service_sub_type, rating_issued_date, overall_nqs_rating, qa1, qa7
          FROM services s JOIN entities e ON e.entity_id = s.entity_id
         WHERE e.group_id = ? AND s.is_active = 1
         LIMIT 2
    """, (gid,)).fetchall()
    print("  Sample rows:")
    for r in sample:
        print(f"    {r[0][:40]:40} lat={r[1]} lng={r[2]}")
        print(f"      ARIA={r[3]!r} SEIFA={r[4]} sub={r[5]!r}")
        print(f"      rating_date={r[6]!r} overall={r[7]!r} qa1={r[8]!r} qa7={r[9]!r}")

show("Sparrow", 1887)
show("Harmony", 236)
conn.close()
