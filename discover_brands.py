"""
discover_brands.py
────────────────────────────────────────────────────────────────
Phase A of the linker: discover candidate brands by scanning
service_name prefixes, populate the brands table, and assign
brand_id to services.

Algorithm:
  - Normalise each service_name (lowercase, strip punctuation)
  - Extract 3-word and 2-word prefixes
  - Sort candidate prefixes longest-first, frequency desc
  - Greedy claim: longest qualifying prefix wins per service
  - Qualifying = 5+ services share the prefix
  - Reject single-word prefixes that are sector-generic

For each brand, group_id is assigned by majority: the group
holding the most of the brand's services. This is a temporary
assignment; it gets re-pointed to the canonical group after
Phase B (propose_merges.py) runs and groups are merged.

Multi-group brands — brands whose services span >1 group — are
listed at the end as "LINKER HOT SPOTS." These are the primary
input for Phase B.

Idempotent: clears + rebuilds brands on every run.
Run from: C:\\Users\\Patrick Bell\\remara-agent
"""

import re
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "data" / "kintell.db"

# Tuning
MIN_BRAND_SERVICES = 5
MAX_PREFIX_WORDS   = 3
MIN_PREFIX_WORDS   = 2

# Single-word prefixes that are too generic to be a brand on their own.
# (These are only rejected when the candidate is a 1-word prefix,
# which won't happen under current MIN_PREFIX_WORDS=2 but left in
# case the threshold is dropped.)
STOPWORD_SINGLES = {
    "the", "little", "early", "kids", "tiny", "happy", "busy",
    "our", "my", "childcare", "daycare", "learning", "child",
}


def normalise(s):
    """Lowercase, strip non-alphanumerics, collapse whitespace."""
    s = (s or "").lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def title_case_brand(s):
    """Smart title-casing that leaves small connector words lower."""
    small = {"a", "an", "the", "and", "or", "of", "for", "to", "in", "on"}
    words = s.split()
    return " ".join(
        w.capitalize() if i == 0 or w not in small else w
        for i, w in enumerate(words)
    )


def prefix_of(service_name, n):
    tokens = normalise(service_name).split()
    if len(tokens) < n:
        return None
    return " ".join(tokens[:n])


def is_reasonable_brand(prefix):
    words = prefix.split()
    if not words:
        return False
    if len(words) == 1 and words[0] in STOPWORD_SINGLES:
        return False
    return True


def main():
    if not DB_PATH.exists():
        print(f"[X] Database not found: {DB_PATH}")
        print("    Run init_db.py + build_graph.py first.")
        sys.exit(1)

    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON")

    # ── Clear brand data ──
    print("Clearing existing brand data...")
    conn.execute("DELETE FROM evidence WHERE field_name = 'brand_id'")
    conn.execute("UPDATE services SET brand_id = NULL")
    conn.execute("DELETE FROM brands")
    conn.execute("DELETE FROM sqlite_sequence WHERE name = 'brands'")
    conn.commit()

    # ── Read services with entity/group context ──
    rows = conn.execute("""
        SELECT s.service_id, s.service_name, s.approval_granted_date,
               s.approved_places, e.entity_id, e.group_id
          FROM services s
          LEFT JOIN entities e ON e.entity_id = s.entity_id
    """).fetchall()

    print(f"\nScanning {len(rows)} services for brand prefixes...")

    # ── Tally prefix occurrences ──
    prefix_services = defaultdict(list)
    for row in rows:
        name = row[1]
        for n in range(MAX_PREFIX_WORDS, MIN_PREFIX_WORDS - 1, -1):
            p = prefix_of(name, n)
            if p:
                prefix_services[p].append(row)

    print(f"  Distinct candidate prefixes: {len(prefix_services):,}")

    # ── Greedy claim: longest qualifying prefix wins ──
    candidate_order = sorted(
        prefix_services.keys(),
        key=lambda p: (-len(p.split()), -len(prefix_services[p]))
    )

    claimed          = set()
    brand_of_service = {}
    brand_members    = {}

    for p in candidate_order:
        if not is_reasonable_brand(p):
            continue
        members = [r for r in prefix_services[p] if r[0] not in claimed]
        if len(members) < MIN_BRAND_SERVICES:
            continue
        for r in members:
            claimed.add(r[0])
            brand_of_service[r[0]] = p
        brand_members[p] = members

    print(f"  Candidate brands: {len(brand_members):,}")
    print(f"  Services claimed: {len(brand_of_service):,}")
    print(f"  Unclaimed:        {len(rows) - len(brand_of_service):,}")

    # ── Insert brands (majority group wins) ──
    print("\nWriting brands and assigning services...")
    brand_id_of = {}
    skipped_no_group = 0

    for prefix, members in brand_members.items():
        group_counts = defaultdict(int)
        for r in members:
            gid = r[5]
            if gid is not None:
                group_counts[gid] += 1

        if not group_counts:
            # Brand held entirely by orphan entities — cannot set group_id
            # (schema requires NOT NULL). Skip for v1; these surface once
            # their entities are linked to groups.
            skipped_no_group += 1
            continue

        majority_group = max(
            group_counts.items(),
            key=lambda kv: (kv[1], -kv[0])
        )[0]

        dates = [r[2] for r in members if r[2]]
        first_opened = min(dates) if dates else None

        cur = conn.execute(
            "INSERT INTO brands "
            "(name, service_name_prefix, group_id, first_centre_opened) "
            "VALUES (?, ?, ?, ?)",
            (title_case_brand(prefix), prefix, majority_group, first_opened)
        )
        brand_id_of[prefix] = cur.lastrowid

    conn.commit()

    # ── Assign brand_id to services + evidence ──
    n_assigned = 0
    for sid, prefix in brand_of_service.items():
        brand_id = brand_id_of.get(prefix)
        if brand_id is None:
            continue
        conn.execute(
            "UPDATE services SET brand_id=? WHERE service_id=?",
            (brand_id, sid)
        )
        conn.execute(
            "INSERT INTO evidence "
            "(subject_type, subject_id, field_name, asserted_value, "
            " source_type, confidence, asserted_by) "
            "VALUES ('service', ?, 'brand_id', ?, "
            "        'brand_prefix_match', 0.9, 'system')",
            (sid, str(brand_id))
        )
        n_assigned += 1
    conn.commit()

    print(f"  Brands inserted: {len(brand_id_of):,}")
    print(f"  Services with brand_id: {n_assigned:,}")
    if skipped_no_group:
        print(f"  [!] {skipped_no_group} candidate brands skipped "
              "(entities unlinked to groups)")

    # ── Top brands ──
    print("\n  Top 15 brands by service count:")
    top = conn.execute("""
        SELECT b.name,
               COUNT(s.service_id)        AS svc,
               COALESCE(SUM(s.approved_places), 0) AS places,
               COUNT(DISTINCT e.group_id)  AS groups_c,
               COUNT(DISTINCT e.entity_id) AS entities_c
          FROM brands b
          LEFT JOIN services s ON s.brand_id = b.brand_id
          LEFT JOIN entities e ON e.entity_id = s.entity_id
         GROUP BY b.brand_id
         ORDER BY svc DESC
         LIMIT 15
    """).fetchall()
    for name, svc, pl, gc, ec in top:
        print(f"    {svc:4d} centres  {pl:6d} places  "
              f"{gc:2d} groups  {ec:3d} entities   {name}")

    # ── Linker hot spots ──
    print("\n  LINKER HOT SPOTS — brands spanning >1 group:")
    print("  (Primary input for propose_merges.py, next cycle.)")
    hot = conn.execute("""
        SELECT b.name,
               COUNT(s.service_id) AS svc,
               COUNT(DISTINCT e.group_id) AS gc
          FROM brands b
          JOIN services s ON s.brand_id = b.brand_id
          JOIN entities e ON e.entity_id = s.entity_id
         GROUP BY b.brand_id
        HAVING gc > 1
         ORDER BY gc DESC, svc DESC
         LIMIT 30
    """).fetchall()
    for name, svc, gc in hot:
        print(f"    {gc:2d} groups  {svc:4d} centres   {name}")

    n_hot = conn.execute("""
        SELECT COUNT(*) FROM (
          SELECT b.brand_id
            FROM brands b
            JOIN services s ON s.brand_id = b.brand_id
            JOIN entities e ON e.entity_id = s.entity_id
           GROUP BY b.brand_id
          HAVING COUNT(DISTINCT e.group_id) > 1
        )
    """).fetchone()[0]
    print(f"\n  Total multi-group brands: {n_hot}")

    # ── Sparrow check ──
    print("\n  Sparrow check:")
    sp = conn.execute("""
        SELECT b.name,
               COUNT(DISTINCT e.group_id) AS gc,
               COUNT(s.service_id)        AS svc
          FROM brands b
          JOIN services s ON s.brand_id = b.brand_id
          JOIN entities e ON e.entity_id = s.entity_id
         WHERE LOWER(b.name) LIKE 'sparrow%'
         GROUP BY b.brand_id
    """).fetchall()
    if not sp:
        print("    [!] No sparrow brand detected — diagnostic needed.")
    for name, gc, svc in sp:
        print(f"    {svc:3d} services  {gc:2d} groups   {name}")

    conn.close()
    print(f"\nDone.  {DB_PATH}")


if __name__ == "__main__":
    main()
