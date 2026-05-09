r"""
layer4_4_step_a10b_languages_apply.py — A10/C8 follow-up: top-3 languages
spoken at home per SA2, parallel to country-of-birth top-N (D-A2).

Reads from abs_data/2021_TSP_SA2_for_AUS_short-header.zip (T10A + T10B,
already on disk and used by the A2 NES ingest).

Creates new table `abs_sa2_language_at_home_top_n`:

    sa2_code     TEXT
    census_year  INTEGER          (2021)
    rank         INTEGER          (1, 2, 3)
    language     TEXT
    count        INTEGER
    share_pct    REAL             (count / Tot_C21_P * 100)
    PRIMARY KEY (sa2_code, census_year, rank)

Display-only context. No banding, no calibration influence (mirrors COB
top-N convention). Renders as a context line below sa2_nes_share in the
Demographic mix sub-panel of the Catchment Position card.

Excluded columns (not real languages or aggregate buckets):
    Uses_Engl_only, Lang_used_home_NS, Tot,
    UOL_CL_Tot, UOL_CL_Oth, UOL_Other.

UOL_Pe_ex_Da appears in both T10A and T10B (alphabetic file-split lands
mid-language); merge dedups via suffix-DROP pattern.

Usage:
    python layer4_4_step_a10b_languages_apply.py             # dry-run
    python layer4_4_step_a10b_languages_apply.py --apply     # write
    python layer4_4_step_a10b_languages_apply.py --replace --apply

Run from repo root.
"""

import io
import json
import re
import shutil
import sqlite3
import sys
import warnings
import zipfile
from datetime import datetime
from pathlib import Path

DB_PATH = Path("data") / "kintell.db"
ZIP_PATH = Path("abs_data") / "2021_TSP_SA2_for_AUS_short-header.zip"
TARGET_TABLE = "abs_sa2_language_at_home_top_n"
ACTOR = "layer4_4_step_a10b_languages_apply"

ZIP_PREFIX = "2021 Census TSP Statistical Area 2 for AUS/"
T10A = f"{ZIP_PREFIX}2021Census_T10A_AUST_SA2.csv"
T10B = f"{ZIP_PREFIX}2021Census_T10B_AUST_SA2.csv"

CENSUS_YEAR = 2021
TOT_COL = "Tot_C21_P"
TOP_N = 3

# Prefixes to skip (not real languages or aggregate buckets)
EXCLUDE_PREFIXES = {
    "Uses_Engl_only",
    "Lang_used_home_NS",
    "Tot",
    "UOL_CL_Tot",
    "UOL_CL_Oth",
    "UOL_Other",
}

# Map TSP short-header language prefix → readable label
LANGUAGE_LABELS = {
    "UOL_Arabic":     "Arabic",
    "UOL_Aus_In_La":  "Australian Indigenous languages",
    "UOL_Bengali":    "Bengali",
    "UOL_Canton":     "Cantonese",
    "UOL_Croatian":   "Croatian",
    "UOL_Filipino":   "Filipino",
    "UOL_French":     "French",
    "UOL_German":     "German",
    "UOL_Gre":        "Greek",
    "UOL_Gujarati":   "Gujarati",
    "UOL_Hindi":      "Hindi",
    "UOL_Indon":      "Indonesian",
    "UOL_Italian":    "Italian",
    "UOL_Japanes":    "Japanese",
    "UOL_Korean":     "Korean",
    "UOL_Mac":        "Macedonian",
    "UOL_Malayalam":  "Malayalam",
    "UOL_Mandar":     "Mandarin",
    "UOL_Nepali":     "Nepali",
    "UOL_Pe_ex_Da":   "Persian (excl. Dari)",
    "UOL_Portuguese": "Portuguese",
    "UOL_Punjabi":    "Punjabi",
    "UOL_Russian":    "Russian",
    "UOL_Serbian":    "Serbian",
    "UOL_Sinhalese":  "Sinhalese",
    "UOL_Spanish":    "Spanish",
    "UOL_Tagalog":    "Tagalog",
    "UOL_Tamil":      "Tamil",
    "UOL_Thai":       "Thai",
    "UOL_Turkish":    "Turkish",
    "UOL_Urdu":       "Urdu",
    "UOL_Viet":       "Vietnamese",
}

VERIFY_SA2 = [
    ("211011251", "Bayswater Vic"),
    ("118011341", "Bondi Junction-Waverly NSW"),
    ("506031124", "Bentley-Wilson-St James WA"),
    ("702041063", "Outback NT (high-ATSI)"),
]


def section(title):
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def parse_args():
    return {
        "apply": "--apply" in sys.argv,
        "replace": "--replace" in sys.argv,
    }


def preflight():
    if not DB_PATH.exists():
        print(f"ERROR: {DB_PATH} not found.")
        sys.exit(1)
    if not ZIP_PATH.exists():
        print(f"ERROR: {ZIP_PATH} not found.")
        sys.exit(1)


def to_int(v):
    try:
        return int(v) if v not in ("", "..", "np", None) else None
    except (ValueError, TypeError):
        return None


def read_t10_merged():
    import pandas as pd
    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        for nm in (T10A, T10B):
            if nm not in z.namelist():
                print(f"ERROR: {nm} not in zip.")
                sys.exit(2)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            a = pd.read_csv(io.BytesIO(z.read(T10A)), dtype=str)
            b = pd.read_csv(io.BytesIO(z.read(T10B)), dtype=str)
    a.columns = [str(c).strip() for c in a.columns]
    b.columns = [str(c).strip() for c in b.columns]
    a["SA2_CODE_2021"] = a["SA2_CODE_2021"].astype(str).str.strip()
    b["SA2_CODE_2021"] = b["SA2_CODE_2021"].astype(str).str.strip()
    sa2_re = re.compile(r"^\d{9}$")
    a = a[a["SA2_CODE_2021"].str.match(sa2_re)].copy()
    b = b[b["SA2_CODE_2021"].str.match(sa2_re)].copy()
    merged = a.merge(b, on="SA2_CODE_2021", how="inner", suffixes=("", "_DROP"))
    for col in list(merged.columns):
        if col.endswith("_DROP"):
            merged = merged.drop(columns=[col])
    if TOT_COL not in merged.columns:
        print(f"ERROR: {TOT_COL} missing after merge.")
        sys.exit(2)
    print(f"  T10 merged: {len(merged):,} rows × {len(merged.columns)} cols")
    return merged.set_index("SA2_CODE_2021")


def language_columns_2021(t10):
    """Return list[(column_name, language_label)] for 2021 _P columns,
    excluding aggregate buckets and English-only / Lang-NS."""
    out = []
    for c in t10.columns:
        if not c.endswith("_C21_P"):
            continue
        prefix = c[: -len("_C21_P")]
        if prefix in EXCLUDE_PREFIXES:
            continue
        if prefix not in LANGUAGE_LABELS:
            # Defensive: warn on unknown prefix (e.g., new ABS column added)
            print(f"  WARN: unknown language prefix '{prefix}' — using raw name")
            label = prefix.replace("UOL_", "").replace("_", " ")
        else:
            label = LANGUAGE_LABELS[prefix]
        out.append((c, label))
    return out


def derive_topn(t10):
    cols = language_columns_2021(t10)
    print(f"  Language candidate columns (2021): {len(cols)}")

    rows = []
    skipped = 0
    for sa2 in t10.index:
        tot = to_int(t10.at[sa2, TOT_COL])
        if tot is None or tot <= 0:
            skipped += 1
            continue
        counts = []
        for col, label in cols:
            v = to_int(t10.at[sa2, col])
            if v is None or v <= 0:
                continue
            counts.append((v, label))
        if not counts:
            continue
        counts.sort(key=lambda r: -r[0])
        for rank, (v, label) in enumerate(counts[:TOP_N], start=1):
            share = round(v / tot * 100.0, 4)
            rows.append((sa2, CENSUS_YEAR, rank, label, v, share))
    print(f"  Top-{TOP_N} rows: {len(rows):,}  (sa2-skipped no-tot: {skipped})")
    return rows


def ensure_table(con, apply_mode):
    cur = con.cursor()
    exists = cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (TARGET_TABLE,),
    ).fetchone()
    if exists:
        print(f"  {TARGET_TABLE}: already exists.")
        return False
    if not apply_mode:
        print(f"  {TARGET_TABLE}: WOULD CREATE on --apply.")
        return False
    cur.execute(f"""
        CREATE TABLE "{TARGET_TABLE}" (
            sa2_code     TEXT    NOT NULL,
            census_year  INTEGER NOT NULL,
            rank         INTEGER NOT NULL,
            language     TEXT    NOT NULL,
            count        INTEGER,
            share_pct    REAL,
            PRIMARY KEY (sa2_code, census_year, rank)
        )
    """)
    cur.execute(
        "INSERT INTO audit_log "
        "(actor, action, subject_type, subject_id, before_json, after_json, reason, occurred_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))",
        (
            ACTOR,
            "language_at_home_top_n_create_v1",
            "schema",
            0,
            json.dumps({"existed": False}),
            json.dumps({"created_table": TARGET_TABLE}),
            "A10/C8 follow-up: create table for top-3 language-at-home display "
            "context. Parallel to abs_sa2_country_of_birth_top_n. Display-only.",
        ),
    )
    print(f"  {TARGET_TABLE}: CREATED.")
    return True


def write_rows(con, rows, replace=False):
    cur = con.cursor()
    if replace:
        n = cur.execute(f'DELETE FROM "{TARGET_TABLE}"').rowcount
        print(f"  Deleted {n:,} existing rows from {TARGET_TABLE}")
    cur.executemany(
        f'INSERT INTO "{TARGET_TABLE}" '
        f"(sa2_code, census_year, rank, language, count, share_pct) "
        f"VALUES (?, ?, ?, ?, ?, ?)",
        rows,
    )
    return cur.rowcount


def write_audit_log(con, action, subject_type, before, after, reason):
    cur = con.cursor()
    cur.execute(
        "INSERT INTO audit_log "
        "(actor, action, subject_type, subject_id, before_json, after_json, reason, occurred_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))",
        (ACTOR, action, subject_type, 0,
         json.dumps(before), json.dumps(after), reason),
    )
    return cur.execute("SELECT MAX(audit_id) FROM audit_log").fetchone()[0]


def backup_db():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.parent / f"pre_layer4_4_step_a10b_{timestamp}.db"
    print(f"  Backup: copying {DB_PATH} -> {backup_path}")
    shutil.copy2(DB_PATH, backup_path)
    size_mb = backup_path.stat().st_size / (1024 * 1024)
    print(f"  Backup size: {size_mb:.1f} MB")
    return backup_path


def main():
    args = parse_args()
    apply_mode = args["apply"]
    replace = args["replace"]

    print(f"DB:     {DB_PATH}")
    print(f"Source: {ZIP_PATH}")
    print(f"Target: {TARGET_TABLE}")
    print(f"Mode:   {'APPLY' if apply_mode else 'DRY-RUN'}"
          f"{'  REPLACE' if replace else ''}")
    preflight()

    section("Reading source")
    t10 = read_t10_merged()

    section("Top-3 spotcheck")
    rows = derive_topn(t10)
    by_sa2 = {}
    for sa2, yr, rank, lang, count, share in rows:
        by_sa2.setdefault(sa2, []).append((rank, lang, count, share))
    print()
    for sa2, name in VERIFY_SA2:
        triples = sorted(by_sa2.get(sa2, []))
        cells = ", ".join(f"#{r} {l} ({c}, {s:.1f}%)" for r, l, c, s in triples)
        print(f"  {sa2} ({name}): {cells if cells else 'NO DATA'}")

    section("Pre-state inventory")
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    max_audit = cur.execute("SELECT COALESCE(MAX(audit_id),0) FROM audit_log").fetchone()[0]
    print(f"  audit_log max audit_id: {max_audit:,}")
    table_exists = bool(cur.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (TARGET_TABLE,),
    ).fetchone())
    existing = 0
    if table_exists:
        existing = cur.execute(f'SELECT COUNT(*) FROM "{TARGET_TABLE}"').fetchone()[0]
    print(f"  {TARGET_TABLE}: table_exists={table_exists} rows={existing:,}")

    if existing > 0 and not replace and apply_mode:
        print()
        print(f"  ERROR: existing rows present and --replace not set.")
        print(f"  Re-run with --replace --apply to overwrite.")
        con.close()
        sys.exit(4)

    if not apply_mode:
        section("DRY-RUN — no DB mutation")
        print(f"  Would CREATE {TARGET_TABLE} (if missing) and insert {len(rows):,} rows.")
        print(f"  Would write 1-2 audit_log rows (next audit_id starts at {max_audit + 1}).")
        print(f"  To proceed: re-run with --apply.")
        con.close()
        return

    section("Backup")
    backup_path = backup_db()

    section("Writing")
    created = ensure_table(con, apply_mode=True)
    inserted = write_rows(con, rows, replace=replace)
    print(f"  Wrote {inserted:,} rows to {TARGET_TABLE}")
    aid = write_audit_log(
        con,
        "language_at_home_top_n_ingest_v1",
        TARGET_TABLE,
        {"existing_rows": existing, "table_created_this_run": created},
        {
            "rows_inserted": inserted,
            "sa2_count": len({r[0] for r in rows}),
            "census_year": CENSUS_YEAR,
            "top_n": TOP_N,
            "backup": str(backup_path),
        },
        "A10/C8 follow-up: top-3 languages spoken at home per SA2 (2021 only). "
        "Display-only context table accompanying sa2_nes_share. "
        "Reads ABS Census 2021 TSP T10A+T10B; excludes English-only, "
        "language-not-stated, and aggregate buckets.",
    )
    print(f"    audit_id={aid}")

    con.commit()

    section("Post-state")
    cur = con.cursor()
    c = cur.execute(f'SELECT COUNT(*) FROM "{TARGET_TABLE}"').fetchone()[0]
    print(f"  {TARGET_TABLE}: {c:,} rows")
    print()
    print("  Verification SA2 spotcheck (post-write):")
    for sa2, name in VERIFY_SA2:
        rows_v = cur.execute(
            f'SELECT rank, language, count, share_pct FROM "{TARGET_TABLE}" '
            f'WHERE sa2_code = ? AND census_year = ? ORDER BY rank',
            (sa2, CENSUS_YEAR),
        ).fetchall()
        cells = ", ".join(f"#{r[0]} {r[1]} ({r[2]}, {r[3]:.1f}%)" for r in rows_v)
        print(f"    {sa2} ({name}): {cells if cells else 'NO DATA'}")

    con.close()
    print()
    print("APPLIED.")


if __name__ == "__main__":
    main()
