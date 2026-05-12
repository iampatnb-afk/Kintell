"""
OI-12 backup pruner — interactive cleanup of data/ DB backups.

Retention policy:
  - KEEP all backups matching kintell.db.backup_pre_*  (named milestones)
  - KEEP most recent N timestamped backups            (rolling window; default N=3)
  - DELETE everything else

Default mode is DRY RUN (lists what would happen, no files touched).
Use --apply to perform the deletion.

Usage:
  python prune_db_backups.py            # dry run, default keep=3
  python prune_db_backups.py --keep 5   # dry run, keep 5 most recent
  python prune_db_backups.py --apply    # actually delete

Backups are gitignored (per DEC-31 and existing .gitignore), so no
git operations are needed after deletion. Disk space is reclaimed
immediately.

Read-only by default. Safe to run multiple times to see what would
happen before committing to deletion.
"""

import argparse
import re
import sys
from pathlib import Path

DATA_DIR = Path("data")
BACKUP_GLOB = "kintell.db.backup_*"
NAMED_ANCHOR_RE = re.compile(r"^kintell\.db\.backup_pre_")


def fmt_size(n_bytes: float) -> str:
    """Human-readable byte size."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n_bytes < 1024:
            return f"{n_bytes:.1f} {unit}"
        n_bytes /= 1024
    return f"{n_bytes:.1f} PB"


def main() -> int:
    ap = argparse.ArgumentParser(
        description="OI-12 backup pruner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument(
        "--keep",
        type=int,
        default=3,
        help="Number of most-recent timestamped backups to keep (default 3). "
             "Named-milestone backups (kintell.db.backup_pre_*) are always kept.",
    )
    ap.add_argument(
        "--apply",
        action="store_true",
        help="Actually delete (default is dry run).",
    )
    args = ap.parse_args()

    if not DATA_DIR.exists():
        print(f"ERROR: {DATA_DIR}/ not found. Run from repo root.")
        return 1

    backups = sorted(
        DATA_DIR.glob(BACKUP_GLOB),
        key=lambda p: p.stat().st_mtime,
        reverse=True,  # newest first
    )

    if not backups:
        print(f"No backups found matching '{BACKUP_GLOB}' in {DATA_DIR}/.")
        return 0

    total_size = sum(b.stat().st_size for b in backups)
    print(f"Found {len(backups)} backup(s) in {DATA_DIR}/; "
          f"total size {fmt_size(total_size)}")
    print()

    # Categorise
    keep_named: list[Path] = []
    keep_recent: list[Path] = []
    delete: list[Path] = []
    recent_count = 0

    for b in backups:
        if NAMED_ANCHOR_RE.match(b.name):
            keep_named.append(b)
        elif recent_count < args.keep:
            keep_recent.append(b)
            recent_count += 1
        else:
            delete.append(b)

    # Display plan
    bar = "=" * 80

    print(bar)
    print(f"KEEP — Named milestone anchors ({len(keep_named)})")
    print(bar)
    if keep_named:
        for b in keep_named:
            print(f"  {b.name:<62} {fmt_size(b.stat().st_size):>10}")
    else:
        print("  (none)")
    print()

    print(bar)
    print(f"KEEP — Most recent {args.keep} timestamped ({len(keep_recent)})")
    print(bar)
    if keep_recent:
        for b in keep_recent:
            print(f"  {b.name:<62} {fmt_size(b.stat().st_size):>10}")
    else:
        print("  (none)")
    print()

    print(bar)
    print(f"DELETE — Older timestamped ({len(delete)})")
    print(bar)
    delete_size = 0
    if delete:
        for b in delete:
            sz = b.stat().st_size
            delete_size += sz
            print(f"  {b.name:<62} {fmt_size(sz):>10}")
    else:
        print("  (none)")
    print()

    print(bar)
    print("SUMMARY")
    print(bar)
    print(f"  Current state:    {len(backups)} backup(s); "
          f"{fmt_size(total_size)}")
    print(f"  Would delete:     {len(delete)} file(s); "
          f"{fmt_size(delete_size)}")
    print(f"  Final state:      "
          f"{len(keep_named) + len(keep_recent)} backup(s); "
          f"{fmt_size(total_size - delete_size)}")
    print()

    if not delete:
        print("Nothing to delete. Exiting.")
        return 0

    if not args.apply:
        print("DRY RUN — no files touched. Re-run with --apply to perform deletion.")
        return 0

    # Apply
    print(bar)
    print("APPLYING — deleting older backups...")
    print(bar)
    deleted_count = 0
    deleted_size = 0
    failed: list[tuple[str, str]] = []
    for b in delete:
        try:
            sz = b.stat().st_size
            b.unlink()
            deleted_count += 1
            deleted_size += sz
            print(f"  deleted: {b.name}  ({fmt_size(sz)})")
        except OSError as e:
            failed.append((b.name, str(e)))
            print(f"  FAILED:  {b.name}  -- {e}")

    print()
    print(f"Deleted {deleted_count} file(s); reclaimed {fmt_size(deleted_size)}.")
    if failed:
        print(f"WARN: {len(failed)} file(s) could not be deleted (see above).")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
