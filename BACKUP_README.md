# Kintell backup setup

## What's backed up

| Asset | Location | Frequency |
|---|---|---|
| Code + docs | GitHub `iampatnb-afk/Kintell` master | every commit (manual `git push`) |
| `data/kintell.db` | `G:\My Drive\Novara_Backups\kintell\daily\` (gzip) | nightly 03:00 |
| `.claude/.../memory/` | same daily folder as a .tar.gz | nightly 03:00 |
| Weekly DB archive | `G:\My Drive\Novara_Backups\kintell\weekly\` | every Monday |
| Monthly DB archive | `G:\My Drive\Novara_Backups\kintell\monthly\` | 1st of month |

## Retention

- **Daily:** last 7 snapshots
- **Weekly:** last 4 snapshots
- **Monthly:** last 12 snapshots

Total Drive usage stabilises at ~7 × 122MB + 4 × 122MB + 12 × 122MB ≈ **2.8 GB** at current DB size.

## Manual run

```bash
cd "C:\Users\Patrick Bell\remara-agent"
python backup_kintell.py
```

Or dry-run:

```bash
python backup_kintell.py --dry-run
```

## Scheduling the nightly run (one-time setup)

1. Open **Task Scheduler** (`taskschd.msc`)
2. Right-click the task library tree → **Import Task...**
3. Select `C:\Users\Patrick Bell\remara-agent\backup_kintell_taskscheduler.xml`
4. (Optional) Tweak the StartBoundary in the Triggers tab if 03:00 doesn't suit
5. Click OK

The task will run nightly under your interactive user (so Drive's sync path is reachable).

## Restoring

```bash
# 1. Pick a snapshot
ls "G:\My Drive\Novara_Backups\kintell\daily"

# 2. Decompress
gzip -d -c "G:\My Drive\Novara_Backups\kintell\daily\kintell-2026-05-12.db.gz" > restored_kintell.db

# 3. Replace the live DB (BACK UP the current one first!)
mv data/kintell.db data/kintell.db.pre_restore
mv restored_kintell.db data/kintell.db
```

For the memory snapshot:

```bash
tar -xzf "G:\My Drive\Novara_Backups\kintell\daily\memory-2026-05-12.tar.gz" -C "C:\Users\Patrick Bell\.claude\projects\C--Users-Patrick-Bell-remara-agent\"
```

## What's NOT backed up

- `Project Folder Docs/` (PDF reading copies) — recoverable from original publishers
- `recon/patchers_*` (excluded by .gitignore)
- `data/*.json` (regeneratable build artefacts; `sa2_history.json` exists in `docs/` which IS committed)
- `data/kintell.db.backup_pre_*` files (~30 local STD-08 backups, ~8.5 GB total — too large for Drive backup)

## Security notes

- The GitHub PAT is currently embedded in `git remote -v` URL. Recommend rotating + removing.
- Drive sync covers cloud upload — local cache is at `G:\My Drive\Novara_Backups\` and Google Drive replicates to cloud automatically.
