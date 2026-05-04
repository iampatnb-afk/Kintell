"""
cleanup_session_2026-05-03.py — end-of-session housekeeping.

Five tasks:
  1. Fill <v20-commit> and <doc-commit> placeholders in PROJECT_STATUS.md
     and PHASE_LOG.md with the actual hashes (11b27e2 and 54bacfe).
  2. Archive the session's patcher + apply scripts to recon/patchers_2026-05-03/
     so they're preserved (per past convention) but out of the repo root.
  3. Remove .bak_* files older than today (working-tree clutter).
  4. Remove docs/centre.v3_*_backup_*.html files (legacy backups from 04/29
     untouched since, mentioned in OI-13).
  5. Print final git status summary so you know what's still untracked.

Read-only on git history. Will modify working tree only. After running,
review and commit the placeholder fix in a small follow-up commit;
archive moves and bak deletions are working-tree-only and don't need
committing (recon/ files are gitignored or untracked anyway, but the
patchers will become tracked when you stage them).

Discipline:
  - STD-08: backups for the 2 modified docs before placeholder fix
  - Idempotency: re-run safe (placeholder fix only triggers if literal
    "<v20-commit>" or "<doc-commit>" still in file)
"""

import shutil
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent
DOCS = REPO / "recon" / "Document and Status DB"

PROJECT_STAT  = DOCS / "PROJECT_STATUS.md"
PHASE_LOG     = DOCS / "PHASE_LOG.md"

V20_HASH = "11b27e2"
DOC_HASH = "54bacfe"

STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")


def task1_fill_placeholders() -> int:
    """Substitute <v20-commit> -> 11b27e2 and <doc-commit> -> 54bacfe."""
    print("\n[Task 1] Fill commit-hash placeholders")
    print("-" * 56)

    targets = [PROJECT_STAT, PHASE_LOG]
    changed_count = 0

    for path in targets:
        if not path.exists():
            print(f"  SKIP {path.name}: not found")
            continue

        text = path.read_text(encoding="utf-8")
        n_v20 = text.count("<v20-commit>")
        n_doc = text.count("<doc-commit>")

        if n_v20 == 0 and n_doc == 0:
            print(f"  SKIP {path.name}: no placeholders found (already filled)")
            continue

        # Backup before modify
        backup = path.with_name(f"{path.name}.bak_{STAMP}")
        shutil.copy2(path, backup)

        new = text.replace("<v20-commit>", f"`{V20_HASH}`").replace(
            "<doc-commit>", f"`{DOC_HASH}`"
        )
        # The above adds extra backticks because the placeholders were
        # already inside backticks in the source (`<v20-commit>`). Strip
        # the doubled backticks.
        new = new.replace(f"``{V20_HASH}``", f"`{V20_HASH}`")
        new = new.replace(f"``{DOC_HASH}``", f"`{DOC_HASH}`")

        path.write_text(new, encoding="utf-8", newline="")
        print(f"  {path.name}: replaced {n_v20} <v20-commit> + {n_doc} <doc-commit>")
        changed_count += 1

    return changed_count


def task2_archive_scripts() -> int:
    """Move session patcher + apply scripts to recon/patchers_2026-05-03/."""
    print("\n[Task 2] Archive throwaway scripts to recon/patchers_2026-05-03/")
    print("-" * 56)

    archive = REPO / "recon" / "patchers_2026-05-03"
    archive.mkdir(parents=True, exist_ok=True)

    candidates = [
        "patch_oi32_about_data.py",
        "patch_oi32_polish.py",
        "patch_oi32_polish_r2.py",
        "patch_oi32_v20_bundle.py",
        "apply_session_docs.py",
    ]
    moved = 0
    for name in candidates:
        src = REPO / name
        if not src.exists():
            print(f"  SKIP {name}: not found in repo root")
            continue
        dst = archive / name
        if dst.exists():
            dst.unlink()  # overwrite if re-run
        shutil.move(str(src), str(dst))
        print(f"  moved: {name} -> recon/patchers_2026-05-03/")
        moved += 1

    return moved


def task3_remove_old_baks() -> tuple:
    """Remove .bak_* files older than today (keep today's as safety net)."""
    print("\n[Task 3] Remove .bak_* files older than today")
    print("-" * 56)

    today_yyyymmdd = datetime.now().strftime("%Y%m%d")
    removed = 0
    kept = 0
    bytes_freed = 0

    # Look in repo root, docs/, recon/Document and Status DB/
    search_dirs = [
        REPO,
        REPO / "docs",
        DOCS,
    ]
    for sd in search_dirs:
        if not sd.exists():
            continue
        for p in sd.iterdir():
            if not p.is_file():
                continue
            name = p.name
            if ".bak_" not in name:
                continue
            # Try to extract YYYYMMDD from filename
            try:
                bak_idx = name.rindex(".bak_") + len(".bak_")
                date_part = name[bak_idx:bak_idx + 8]
                if not date_part.isdigit():
                    print(f"  SKIP unparseable: {name}")
                    continue
            except (ValueError, IndexError):
                print(f"  SKIP unparseable: {name}")
                continue

            if date_part < today_yyyymmdd:
                size = p.stat().st_size
                p.unlink()
                bytes_freed += size
                removed += 1
            else:
                kept += 1

    print(f"  removed: {removed} backup file(s) ({bytes_freed/1024:.1f} KB freed)")
    print(f"  kept (today's, safety net): {kept}")
    return removed, kept


def task4_remove_legacy_docs_baks() -> int:
    """Remove docs/centre.v3_*_backup_*.html files (OI-13 mentions these)."""
    print("\n[Task 4] Remove legacy docs/centre.v3_*_backup_*.html files")
    print("-" * 56)

    docs_dir = REPO / "docs"
    if not docs_dir.exists():
        print("  SKIP: docs/ not found")
        return 0

    removed = 0
    for p in docs_dir.iterdir():
        if not p.is_file():
            continue
        name = p.name
        if name.startswith("centre.v3_") and "_backup_" in name and name.endswith(".html"):
            p.unlink()
            print(f"  removed: docs/{name}")
            removed += 1

    if removed == 0:
        print("  no matching files found")
    return removed


def task5_summary() -> None:
    """Print suggested next-steps."""
    print("\n[Task 5] Summary + next steps")
    print("-" * 56)
    print("\nRecommended next:")
    print("  1. Verify placeholder fix:")
    print("     git diff \"recon/Document and Status DB/\"")
    print()
    print("  2. Stage the placeholder fix + the archived patchers:")
    print("     git add \"recon/Document and Status DB/PROJECT_STATUS.md\" `")
    print("             \"recon/Document and Status DB/PHASE_LOG.md\" `")
    print("             \"recon/patchers_2026-05-03/\"")
    print()
    print("  3. Commit:")
    print('     git commit -m "Cleanup: fill commit-hash placeholders in PROJECT_STATUS + PHASE_LOG (11b27e2 + 54bacfe); archive session patchers to recon/patchers_2026-05-03/."')
    print("     git push")
    print()
    print("  4. Final git status check:")
    print("     git status")
    print()
    print("  After that, the working tree should be clean except for legacy")
    print("  untracked files from prior sessions (probe_*.py, smoke_test_*.py,")
    print("  inventory_db_backups.py, prune_db_backups.py) — those are noise")
    print("  carried from earlier sessions, not introduced today.")


def main() -> None:
    print("=" * 64)
    print("End-of-session cleanup — 2026-05-03 evening")
    print("=" * 64)

    n_placeholder = task1_fill_placeholders()
    n_archived    = task2_archive_scripts()
    n_baks_removed, n_baks_kept = task3_remove_old_baks()
    n_docs_baks   = task4_remove_legacy_docs_baks()

    print("\n" + "=" * 64)
    print("DONE.")
    print(f"  Files placeholder-fixed:   {n_placeholder}")
    print(f"  Scripts archived:          {n_archived}")
    print(f"  .bak_* files removed:      {n_baks_removed} (kept {n_baks_kept})")
    print(f"  Legacy docs/ baks removed: {n_docs_baks}")
    print("=" * 64)

    task5_summary()


if __name__ == "__main__":
    main()
