r"""
A2 verification — read calibrated_rate + rule_text from service_catchment_cache
for the three verification SA2s and confirm the NES nudge is now firing
(or correctly held neutral) per each SA2's NES share.

Read-only.
    python verify_a2_wire.py
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("data") / "kintell.db"

VERIFY = [
    ("211011251", "Bayswater Vic",                   0.311, "high (>=0.30) -> -0.02 expected"),
    ("118011341", "Bondi Junction-Waverly NSW",      0.236, "mid (no nudge expected)"),
    ("506031124", "Bentley-Wilson-St James WA",      0.376, "high (>=0.30) -> -0.02 expected"),
]


def main():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    for sa2, name, nes, expectation in VERIFY:
        rows = cur.execute(
            "SELECT calibrated_rate, rule_text FROM service_catchment_cache "
            "WHERE sa2_code = ? LIMIT 1",
            (sa2,),
        ).fetchall()
        print(f"\n{sa2}  {name}  (NES {nes:.3f})")
        print(f"  expectation: {expectation}")
        if not rows:
            print("  NO ROW")
            continue
        rate, rule = rows[0]
        print(f"  rate: {rate}")
        print(f"  rule: {rule}")
    con.close()


if __name__ == "__main__":
    main()
