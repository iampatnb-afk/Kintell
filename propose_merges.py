"""
propose_merges.py
────────────────────────────────────────────────────────────────
Phase B of the linker.

For each brand spanning >1 group, propose pairwise merges of
every non-canonical group into the canonical group (the group
holding the most services under that brand).

Composite confidence (0.0–1.0):

  base = min(concentration_A, concentration_B)
    where concentration_X = brand_services_in_X / total_services_in_X

Adjustments:
  +0.10  if the two groups appear in each other's fuzzy_related
         (from operators_target_list.json)
  +0.05  if they share a phone_related link
  ×0.30  penalty for religious naming patterns (St X, Sacred Heart,
         Our Lady, Holy X, etc.) — separate parishes that happen to
         share saint names
  ×0.60  penalty if the non-canonical group's brand concentration is
         < 50% (suggests the brand is incidental, not defining)

Writes one link_candidates row per proposal, with the full signal
set serialised into evidence_json for review.

Idempotent: clears link_candidates for link_type='group_merge' at
start. Does not touch any group/entity/service data — proposals
only, review flows into merges as a separate cycle.

Run from: C:\\Users\\Patrick Bell\\remara-agent
"""

import json
import math
import re
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

ROOT           = Path(__file__).resolve().parent
DB_PATH        = ROOT / "data" / "kintell.db"
OPERATORS_FILE = ROOT / "operators_target_list.json"


def as_str(v):
    if v is None:
        return ""
    if isinstance(v, float):
        if math.isnan(v):
            return ""
        return str(v)
    try:
        return str(v).strip()
    except Exception:
        return ""


# ── Religious / denominational patterns ─────────────────────────────
# These are rejected at the merge-confidence level because separate
# parishes genuinely share these names. They remain in the proposal
# list (for transparency) but at very low confidence.
RELIGIOUS_PATTERNS = [
    r"^st\s+[a-z]+('?s|s)?$",
    r"^saint\s+",
    r"^our lady",
    r"^sacred heart",
    r"^holy\s+",
    r"^immaculate",
    r"^blessed\s+",
    r"^mater\s+",
]


def is_religious(brand_name):
    lower = as_str(brand_name).lower()
    return any(re.match(p, lower) for p in RELIGIOUS_PATTERNS)


def main():
    if not DB_PATH.exists():
        print(f"[X] Database not found: {DB_PATH}")
        print("    Run init_db.py + build_graph.py + "
              "discover_brands.py first.")
        sys.exit(1)
    if not OPERATORS_FILE.exists():
        print(f"[X] Missing: {OPERATORS_FILE}")
        sys.exit(1)

    # ── Load operator signals (fuzzy, phone) from target list ──
    print("Loading operators_target_list.json for signal enrichment...")
    with OPERATORS_FILE.open(encoding="utf-8") as f:
        operators = json.load(f)
    if isinstance(operators, dict):
        operators = list(operators.values())

    name_to_signals = {}
    for rec in operators:
        if not isinstance(rec, dict):
            continue
        legal = as_str(rec.get("legal_name")).lower()
        if not legal:
            continue
        fuzzy = set()
        for item in rec.get("fuzzy_related", []) or []:
            if isinstance(item, dict):
                fuzzy.add(as_str(item.get("name")).lower())
            else:
                fuzzy.add(as_str(item).lower())
        phone = set()
        for item in rec.get("phone_related", []) or []:
            if isinstance(item, dict):
                phone.add(as_str(item.get("name")).lower())
            else:
                phone.add(as_str(item).lower())
        name_to_signals[legal] = {"fuzzy": fuzzy, "phone": phone}
    print(f"  Loaded signals for {len(name_to_signals):,} groups")

    # ── Connect ──
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON")

    # ── Clear prior merge proposals ──
    print("\nClearing prior group-merge proposals...")
    conn.execute(
        "DELETE FROM link_candidates WHERE link_type = 'group_merge'"
    )
    conn.commit()

    # ── Pre-compute per-group total service counts ──
    print("Computing per-group service totals...")
    total_per_group = dict(conn.execute("""
        SELECT g.group_id, COUNT(s.service_id)
          FROM groups g
          LEFT JOIN entities e ON e.group_id  = g.group_id
          LEFT JOIN services s ON s.entity_id = e.entity_id
         GROUP BY g.group_id
    """).fetchall())
    print(f"  {len(total_per_group):,} groups")

    # ── Get all multi-group brands ──
    multi_brands = conn.execute("""
        SELECT b.brand_id, b.name, COUNT(DISTINCT e.group_id) AS gc
          FROM brands b
          JOIN services s ON s.brand_id = b.brand_id
          JOIN entities e ON e.entity_id = s.entity_id
         GROUP BY b.brand_id
        HAVING gc > 1
         ORDER BY gc DESC
    """).fetchall()
    print(f"\nProcessing {len(multi_brands)} multi-group brands...")

    total_proposals = 0
    religious_count = 0

    for brand_id, brand_name, group_count in multi_brands:
        # Per-group brand service count
        per_group = conn.execute("""
            SELECT e.group_id, g.canonical_name,
                   COUNT(s.service_id) AS brand_svc
              FROM services s
              JOIN entities e ON e.entity_id = s.entity_id
              JOIN groups g   ON g.group_id  = e.group_id
             WHERE s.brand_id = ?
             GROUP BY e.group_id
             ORDER BY brand_svc DESC, e.group_id ASC
        """, (brand_id,)).fetchall()

        if len(per_group) < 2:
            continue

        # Canonical = largest brand presence
        canon_gid, canon_name, canon_brand_svc = per_group[0]
        canon_total = total_per_group.get(canon_gid, 0) or 1
        canon_conc  = canon_brand_svc / canon_total

        brand_is_religious = is_religious(brand_name)
        if brand_is_religious:
            religious_count += 1

        canon_lower = canon_name.lower()
        canon_signals = name_to_signals.get(canon_lower, {})

        for gid, gname, brand_svc in per_group[1:]:
            total = total_per_group.get(gid, 0) or 1
            other_conc = brand_svc / total

            base = min(canon_conc, other_conc)
            confidence = base

            signals = {
                "brand": brand_name,
                "brand_id": brand_id,
                "canonical_group": canon_name,
                "canonical_group_id": canon_gid,
                "canonical_brand_svc": canon_brand_svc,
                "canonical_total_svc": canon_total,
                "canonical_concentration": round(canon_conc, 3),
                "other_group": gname,
                "other_group_id": gid,
                "other_brand_svc": brand_svc,
                "other_total_svc": total,
                "other_concentration": round(other_conc, 3),
                "adjustments": [],
            }

            # Religious penalty
            if brand_is_religious:
                confidence *= 0.30
                signals["adjustments"].append(
                    "religious_pattern x0.30"
                )

            # Low-concentration penalty on non-canonical side
            if other_conc < 0.5:
                confidence *= 0.60
                signals["adjustments"].append(
                    "other_concentration<0.5 x0.60"
                )

            # Fuzzy-related boost
            gname_lower  = gname.lower()
            other_signals = name_to_signals.get(gname_lower, {})
            if (gname_lower in canon_signals.get("fuzzy", set()) or
                canon_lower  in other_signals.get("fuzzy", set())):
                confidence = min(1.0, confidence + 0.10)
                signals["adjustments"].append("fuzzy_related +0.10")

            # Phone-related boost
            if (gname_lower in canon_signals.get("phone", set()) or
                canon_lower  in other_signals.get("phone", set())):
                confidence = min(1.0, confidence + 0.05)
                signals["adjustments"].append("phone_related +0.05")

            confidence = max(0.0, min(1.0, confidence))

            conn.execute(
                "INSERT INTO link_candidates "
                "(link_type, from_type, from_id, to_type, to_id, "
                " composite_confidence, evidence_json, priority, status) "
                "VALUES ('group_merge', 'group', ?, 'group', ?, "
                "        ?, ?, ?, 'pending')",
                (gid, canon_gid, round(confidence, 3),
                 json.dumps(signals, separators=(",", ":")),
                 int(round(confidence * 100)))
            )
            total_proposals += 1

    conn.commit()
    print(f"\n  Proposals written: {total_proposals:,}")
    print(f"  Religious-pattern brands: {religious_count}")

    # ── Summary distribution ──
    buckets = conn.execute("""
        SELECT
          SUM(CASE WHEN composite_confidence >= 0.85 THEN 1 ELSE 0 END) AS hi,
          SUM(CASE WHEN composite_confidence >= 0.50
                   AND composite_confidence <  0.85 THEN 1 ELSE 0 END) AS md,
          SUM(CASE WHEN composite_confidence <  0.50 THEN 1 ELSE 0 END) AS lo
          FROM link_candidates
         WHERE link_type = 'group_merge'
    """).fetchone()
    hi, md, lo = buckets
    print(f"\n  Confidence distribution:")
    print(f"    HIGH  (≥0.85) : {hi:,}  — auto-accept candidates")
    print(f"    MED   (0.50–0.85): {md:,}  — human review queue")
    print(f"    LOW   (<0.50) : {lo:,}  — probable false positives")

    # ── Top 25 high-confidence proposals ──
    print("\n  Top 25 merge proposals by confidence:")
    top = conn.execute("""
        SELECT c.composite_confidence,
               gA.canonical_name AS from_name,
               gB.canonical_name AS to_name,
               c.evidence_json
          FROM link_candidates c
          JOIN groups gA ON gA.group_id = c.from_id
          JOIN groups gB ON gB.group_id = c.to_id
         WHERE c.link_type = 'group_merge'
         ORDER BY c.composite_confidence DESC, c.candidate_id
         LIMIT 25
    """).fetchall()
    for conf, a, b, ev in top:
        ev_d = json.loads(ev)
        brand = ev_d.get("brand", "")
        print(f"    {conf:.2f}   {a[:45]:45s} → {b[:45]:45s}  [{brand}]")

    # ── Sparrow-specific view ──
    print("\n  Sparrow proposed merges:")
    sp = conn.execute("""
        SELECT c.composite_confidence,
               gA.canonical_name AS from_name,
               gB.canonical_name AS to_name
          FROM link_candidates c
          JOIN groups gA ON gA.group_id = c.from_id
          JOIN groups gB ON gB.group_id = c.to_id
          JOIN brands b  ON b.brand_id  = CAST(json_extract(c.evidence_json,
                                                            '$.brand_id') AS INTEGER)
         WHERE c.link_type = 'group_merge'
           AND LOWER(b.name) LIKE 'sparrow%'
         ORDER BY c.composite_confidence DESC
    """).fetchall()
    for conf, a, b in sp:
        print(f"    {conf:.2f}   {a[:50]:50s} → {b}")
    print(f"  Total Sparrow proposals: {len(sp)}  "
          f"(expected 7: the 8 fragments minus the canonical)")

    # ── Lowest-confidence proposals (review sample) ──
    print("\n  15 lowest-confidence proposals (manual-review candidates):")
    lo_rows = conn.execute("""
        SELECT c.composite_confidence,
               gA.canonical_name AS from_name,
               gB.canonical_name AS to_name,
               c.evidence_json
          FROM link_candidates c
          JOIN groups gA ON gA.group_id = c.from_id
          JOIN groups gB ON gB.group_id = c.to_id
         WHERE c.link_type = 'group_merge'
         ORDER BY c.composite_confidence ASC, c.candidate_id
         LIMIT 15
    """).fetchall()
    for conf, a, b, ev in lo_rows:
        ev_d = json.loads(ev)
        brand = ev_d.get("brand", "")
        print(f"    {conf:.2f}   {a[:45]:45s} → {b[:45]:45s}  [{brand}]")

    conn.close()
    print(f"\nDone.  {DB_PATH}")


if __name__ == "__main__":
    main()
