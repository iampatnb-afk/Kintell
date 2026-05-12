"""
backup_kintell.py — automated daily backup of the Kintell database + memory
to Google Drive (G:\\My Drive\\Novara_Backups\\kintell\\).

Approach
--------
1. Compress `data/kintell.db` (~620MB → ~180MB) using gzip.
2. Write to daily/ folder with ISO timestamp filename.
3. On the 1st of each week (Mondays), also write a copy to weekly/.
4. On the 1st of each month, also write a copy to monthly/.
5. Apply retention: keep last 7 daily, last 4 weekly, last 12 monthly.
6. Also snapshot the claude memory directory (small, ~20-30 markdown files)
   as a single tar.gz inside the same daily folder — Patrick's operational
   memory carries decisions + preferences that aren't in the repo.

Designed to run via Windows Task Scheduler nightly (~3 AM local). Idempotent
within a 24h window — re-running same-day overwrites the existing daily.

Run manually:
    python backup_kintell.py

Output:
    [ok] Daily backup: kintell-2026-05-12.db.gz (172.3 MB)
    [ok] Memory snapshot: memory-2026-05-12.tar.gz (0.04 MB)
    [ok] Weekly promoted: kintell-2026-05-11_wk.db.gz
    [ok] Retention: kept 7 daily / 4 weekly / 12 monthly; pruned 3 stale snapshots
"""

import argparse
import datetime
import gzip
import os
import re
import shutil
import sys
import tarfile
from pathlib import Path

# ── Configuration ───────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent
DB_PATH = REPO_ROOT / "data" / "kintell.db"
MEMORY_DIR = Path.home() / ".claude" / "projects" / "C--Users-Patrick-Bell-remara-agent" / "memory"

BACKUP_ROOT = Path(r"G:\My Drive\Novara_Backups\kintell")
DAILY_DIR = BACKUP_ROOT / "daily"
WEEKLY_DIR = BACKUP_ROOT / "weekly"
MONTHLY_DIR = BACKUP_ROOT / "monthly"

RETAIN_DAILY = 7
RETAIN_WEEKLY = 4
RETAIN_MONTHLY = 12

# ── Helpers ─────────────────────────────────────────────────────────


def _human_mb(path: Path) -> str:
    return f"{path.stat().st_size / (1024 * 1024):.1f} MB"


def _gzip_file(src: Path, dst: Path) -> None:
    """Copy `src` to `dst` with gzip compression. dst should end in .gz."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    with open(src, "rb") as f_in, gzip.open(dst, "wb", compresslevel=6) as f_out:
        shutil.copyfileobj(f_in, f_out, length=1024 * 1024)


def _prune_to_n(folder: Path, pattern: str, keep: int) -> int:
    """Delete files matching `pattern` in `folder` beyond the most recent `keep`.
    Returns the number of files pruned. Sorts by filename (ISO date naming
    means lexical sort = chronological sort)."""
    if not folder.exists():
        return 0
    matched = sorted(folder.glob(pattern))
    if len(matched) <= keep:
        return 0
    to_delete = matched[: len(matched) - keep]
    for f in to_delete:
        try:
            f.unlink()
        except OSError as e:
            print(f"  [warn] could not delete {f.name}: {e}", file=sys.stderr)
    return len(to_delete)


def _snapshot_memory(dst: Path) -> bool:
    """Tar.gz the .claude memory directory. Skips silently if dir is absent."""
    if not MEMORY_DIR.exists():
        print(f"  [skip] memory dir not found at {MEMORY_DIR}")
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(dst, "w:gz", compresslevel=6) as tar:
        # arcname relative to dir name so the archive unpacks cleanly
        tar.add(MEMORY_DIR, arcname=MEMORY_DIR.name)
    return True


# ── Main ────────────────────────────────────────────────────────────


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Backup Kintell DB + memory to Drive.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would happen without writing.")
    args = parser.parse_args(argv)

    today = datetime.date.today()
    iso = today.isoformat()

    if not DB_PATH.exists():
        print(f"[FAIL] DB not found at {DB_PATH}", file=sys.stderr)
        return 1
    if not BACKUP_ROOT.exists():
        print(f"[FAIL] Backup root not found at {BACKUP_ROOT}", file=sys.stderr)
        print("  Is Google Drive mounted / synced?")
        return 1

    print(f"=== Kintell backup — {iso} ===")
    print(f"  DB source: {DB_PATH} ({_human_mb(DB_PATH)})")
    print(f"  Target:    {BACKUP_ROOT}")

    # 1. Daily DB backup
    daily_name = f"kintell-{iso}.db.gz"
    daily_path = DAILY_DIR / daily_name
    if args.dry_run:
        print(f"  [dry-run] would write {daily_path}")
    else:
        _gzip_file(DB_PATH, daily_path)
        print(f"[ok] Daily backup: {daily_name} ({_human_mb(daily_path)})")

    # 2. Memory snapshot (same daily folder; small)
    mem_name = f"memory-{iso}.tar.gz"
    mem_path = DAILY_DIR / mem_name
    if args.dry_run:
        print(f"  [dry-run] would write {mem_path}")
    else:
        if _snapshot_memory(mem_path):
            print(f"[ok] Memory snapshot: {mem_name} ({_human_mb(mem_path)})")

    # 3. Weekly promotion (Mondays — weekday() == 0)
    if today.weekday() == 0:
        weekly_name = f"kintell-{iso}_wk.db.gz"
        weekly_path = WEEKLY_DIR / weekly_name
        if args.dry_run:
            print(f"  [dry-run] would promote weekly {weekly_path}")
        else:
            shutil.copy2(daily_path, weekly_path)
            print(f"[ok] Weekly promoted: {weekly_name}")

    # 4. Monthly promotion (1st of month)
    if today.day == 1:
        monthly_name = f"kintell-{iso}_mo.db.gz"
        monthly_path = MONTHLY_DIR / monthly_name
        if args.dry_run:
            print(f"  [dry-run] would promote monthly {monthly_path}")
        else:
            shutil.copy2(daily_path, monthly_path)
            print(f"[ok] Monthly promoted: {monthly_name}")

    # 5. Retention prune
    pruned_d = _prune_to_n(DAILY_DIR, "kintell-*.db.gz", RETAIN_DAILY) if not args.dry_run else 0
    pruned_m_daily = _prune_to_n(DAILY_DIR, "memory-*.tar.gz", RETAIN_DAILY) if not args.dry_run else 0
    pruned_w = _prune_to_n(WEEKLY_DIR, "kintell-*_wk.db.gz", RETAIN_WEEKLY) if not args.dry_run else 0
    pruned_mo = _prune_to_n(MONTHLY_DIR, "kintell-*_mo.db.gz", RETAIN_MONTHLY) if not args.dry_run else 0
    total_pruned = pruned_d + pruned_m_daily + pruned_w + pruned_mo
    print(f"[ok] Retention: kept {RETAIN_DAILY} daily / {RETAIN_WEEKLY} weekly / "
          f"{RETAIN_MONTHLY} monthly; pruned {total_pruned} stale snapshots.")

    print("=== Done ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
