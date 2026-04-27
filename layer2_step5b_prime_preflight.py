"""
Layer 2 Step 5b-prime — Preflight (read-only).
==============================================
Verifies all required inputs exist and dumps schemas/state needed
to write the apply script correctly.

Outputs:
  recon/layer2_step5b_prime_preflight.md
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("data/kintell.db")
EE_WB = Path("abs_data/Education and employment database.xlsx")
T33_CSV = Path("recon/layer2_step5b_prime_t33_derived.csv")
RECON_DIR = Path("recon")
OUT = RECON_DIR / "layer2_step5b_prime_preflight.md"


def main():
    RECON_DIR.mkdir(exist_ok=True)
    L = []

    def out(s=""):
        print(s)
        L.append(s)

    out("# Layer 2 Step 5b-prime — Preflight")
    out(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    out("")

    # 1. File existence
    out("## File checks")
    for label, p in [("DB", DB_PATH), ("EE Database", EE_WB), ("T33 derived CSV", T33_CSV)]:
        if p.exists():
            sz = p.stat().st_size
            out(f"  ✓ {label}: `{p}` ({sz:,} bytes)")
        else:
            out(f"  ✗ {label}: `{p}` NOT FOUND")
    out("")

    if not DB_PATH.exists():
        out("Cannot proceed — DB missing.")
        OUT.write_text("\n".join(L), encoding="utf-8")
        return

    # 2. DB inspection
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [r[0] for r in cur.fetchall()]
    out(f"## DB tables ({len(tables)} total)")
    out("")
    for t in tables:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        n = cur.fetchone()[0]
        out(f"  - {t} ({n:,} rows)")
    out("")

    # Target table presence (should NOT exist yet)
    target = "abs_sa2_education_employment_annual"
    if target in tables:
        out(f"⚠ Target table `{target}` already exists — apply will DROP and recreate.")
    else:
        out(f"✓ Target table `{target}` does not yet exist (expected).")
    out("")

    # audit_log schema
    out("## audit_log schema")
    out("")
    cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='audit_log'")
    row = cur.fetchone()
    if row:
        out("```sql")
        out(row[0])
        out("```")
    else:
        out("⚠ audit_log table not found.")
    out("")

    # audit_log columns (PRAGMA)
    cur.execute("PRAGMA table_info(audit_log)")
    cols = cur.fetchall()
    if cols:
        out("Columns:")
        out("")
        out("| cid | name | type | notnull | dflt | pk |")
        out("|----:|:-----|:-----|--------:|:-----|---:|")
        for c in cols:
            out(f"| {c['cid']} | {c['name']} | {c['type']} | {c['notnull']} | {c['dflt_value']} | {c['pk']} |")
        out("")

    # Last 5 audit_log entries
    out("## Last 5 audit_log entries")
    out("")
    try:
        cur.execute("SELECT * FROM audit_log ORDER BY rowid DESC LIMIT 5")
        rows = cur.fetchall()
        if rows:
            for row in rows:
                out("```")
                for k in row.keys():
                    v = row[k]
                    if isinstance(v, str) and len(v) > 200:
                        v = v[:200] + "..."
                    out(f"  {k}: {v}")
                out("```")
                out("")
        else:
            out("(no rows)")
    except sqlite3.Error as e:
        out(f"⚠ Error: {e}")

    # SA2 reference count from existing tables (sanity)
    out("## SA2 reference counts (sanity)")
    out("")
    for ref_table, label in [
        ("abs_sa2_erp_annual", "ERP table (Step 6)"),
        ("abs_sa2_socioeconomic_annual", "Socioeconomic (Step 5b)"),
    ]:
        if ref_table in tables:
            try:
                cur.execute(f"SELECT COUNT(DISTINCT sa2_code) FROM {ref_table}")
                n = cur.fetchone()[0]
                out(f"  - {label}: {n:,} distinct SA2 codes in `{ref_table}`")
            except sqlite3.Error as e:
                out(f"  - {label}: error querying — {e}")

    conn.close()

    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"\nWritten to: {OUT}")


if __name__ == "__main__":
    main()
