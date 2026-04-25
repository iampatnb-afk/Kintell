# Kintell — Deployment & Publishing

## How publishing works

The dashboard is served via **GitHub Pages** from the `docs/` folder of the
`iampatnb-afk/Kintell` repo, branch `main`. Local development pushes from
branch `master` to remote `main` (historical convention).

Live URL: https://iampatnb-afk.github.io/Kintell/

`publish_dashboard.py` runs as the final step of `run_daily.py` after
`generate_dashboard.py` completes. It stages all files listed in the
`DASHBOARD_FILES` constant, commits, pushes, and then verifies the live
site matches local.

## The files that must be published

The dashboard loads data from several JSON files that sit alongside
`index.html` in `docs/`. These files are excluded from git by the blanket
`*.json` rule in `.gitignore`, so `publish_dashboard.py` uses `git add -f`
to force-stage them on every publish.

Currently published:
- `docs/index.html` — the dashboard itself
- `docs/operators.json` — Panel 2 operator intelligence
- `docs/catchments.json` — Panel 3 catchment data
- `docs/sa2_history.json` — Panel 3 historical time series

**If a new panel or chart ever loads a new JSON file, add it to the
`DASHBOARD_FILES` list in `publish_dashboard.py`.** Otherwise the live
site will silently go stale for anything that relies on the new file.

## The failure mode this protects against

Between roughly the Panel 3 build and 2026-04-21, the live site was
weeks out of date because `publish_dashboard.py` only staged two files
(`index.html` and `operators.json`). `sa2_history.json` and
`catchments.json` existed locally but were never pushed. Local testing
looked fine; live was stale. The bug was invisible because publishing
appeared to succeed every day.

**The verification step in `publish_dashboard.py` is the fix.** After
every push, it polls the live URL for up to 4 minutes and compares the
size of live `index.html` against local. If they don't match within 1%,
it logs a loud `LIVE DEPLOYMENT VERIFICATION FAILED` block with
diagnostic hints. Watch `run_daily.py` logs for this warning.

## When the live site doesn't match local

Run this diagnostic ladder in order:

**1. Is the local dashboard actually current?**
   - `python generate_dashboard.py`
   - Check `docs/index.html` timestamp is fresh
   - Load `http://localhost:8000/` (serving from `docs/`) and verify
     locally first. If local is broken, the push will be broken too.

**2. Did publish_dashboard.py actually run successfully?**
   - Run it directly: `python publish_dashboard.py`
   - Look for `Dashboard pushed` and then either
     `✓ Live deployment verified` or `LIVE DEPLOYMENT VERIFICATION FAILED`
   - If "GITHUB_TOKEN not set", check `.env` file

**3. Is every needed file in DASHBOARD_FILES?**
   - If a new chart or panel was added recently, its JSON may not be
     in the publish list
   - Open `publish_dashboard.py`, check the `DASHBOARD_FILES` constant
   - Cross-check against files referenced in `docs/index.html`
     (search for `fetch(` or `.json`)

**4. Did the push actually land on origin?**
   - `git log --oneline -3` — should show your latest commit
   - `git log origin/main --oneline -3` — should match
   - If `origin/main` is behind, push is failing silently

**5. Is GitHub Pages serving from the right place?**
   - Visit https://github.com/iampatnb-afk/Kintell/settings/pages
   - Source should be: Deploy from branch `main`, folder `/docs`
   - If it's pointing anywhere else, that's the problem

**6. Has GitHub Pages actually rebuilt?**
   - Visit https://github.com/iampatnb-afk/Kintell/actions
   - Look for a green "pages build and deployment" run matching your
     most recent commit
   - If the run is red, click it to see the error

**7. Am I looking at a cached browser copy?**
   - Hard refresh: Ctrl+F5
   - Or open in an incognito window
   - GitHub Pages also caches at its CDN — sometimes a 1-2 minute wait
     helps

## Manual recovery (nuclear option)

If automation is broken and you just need the live site current:

```
git add -f docs/index.html docs/operators.json docs/catchments.json docs/sa2_history.json
git commit -m "Manual publish YYYY-MM-DD"
git push origin master:main
```

Then wait 2 minutes and hard-refresh the live URL.

## Known constraints and gotchas

- `.gitignore` has `*.json` — every JSON file is excluded by default.
  `publish_dashboard.py` uses `git add -f` to override this for the
  four dashboard files specifically. Don't remove `*.json` from
  `.gitignore` — it correctly excludes scratch data, contacts, and
  backup files across the project.

- Branch naming mismatch: local is `master`, remote is `main`.
  `git push origin master:main` is the correct syntax. Don't try to
  push `main` locally — it doesn't exist.

- `generate_dashboard.py` auto-copies some files from `data/` to
  `docs/` but not all of them. Specifically, `sa2_history.json` is
  not auto-copied. After running `build_sa2_history.py`, run
  `copy data\sa2_history.json docs\sa2_history.json` before publishing.

- GitHub Pages rebuild time varies: usually 1-2 minutes, occasionally
  5-10 minutes during GitHub outages. The verification step waits up
  to 4 minutes before declaring failure.
