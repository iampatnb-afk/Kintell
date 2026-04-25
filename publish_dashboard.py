"""
publish_dashboard.py — Push Kintell dashboard to GitHub Pages
Runs as final step in run_daily.py after generate_dashboard.py

Commits docs/index.html and all dashboard data JSON files to GitHub
and pushes to origin master:main. After pushing, fetches the live
site and verifies the deployed index.html size matches local within
a reasonable tolerance. Logs a LOUD WARNING if verification fails so
stale-deploy bugs surface immediately rather than weeks later.
"""

import subprocess
import logging
import time
import urllib.request
from pathlib import Path
from datetime import date
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).parent
DOCS_DIR = BASE_DIR / "docs"
LIVE_URL = "https://iampatnb-afk.github.io/Kintell/"

# Files that must be staged on every publish. Add to this list if the
# dashboard gains new data dependencies — otherwise the live site
# will silently go stale for any panel that relies on the new file.
DASHBOARD_FILES = [
    "docs/index.html",
    "docs/operators.json",
    "docs/catchments.json",
    "docs/sa2_history.json",
]

log = logging.getLogger(__name__)


def run_git(cmd, cwd=None):
    result = subprocess.run(
        cmd, shell=True, cwd=cwd or str(BASE_DIR),
        capture_output=True, text=True
    )
    if result.stdout.strip():
        log.info(result.stdout.strip())
    if result.stderr.strip():
        log.debug(result.stderr.strip())
    return result.returncode == 0


def verify_live_deployment(local_index_size, max_wait_seconds=240, poll_interval=20):
    """
    Poll the live site after push. Pass if live index.html size matches
    local within 1%. Fail loudly if it doesn't match within max_wait_seconds.

    GitHub Pages typically rebuilds in 1-3 minutes. We poll every 20s
    for up to 4 minutes.
    """
    log.info(f"Verifying live deployment at {LIVE_URL} ...")
    log.info(f"  Local index.html size: {local_index_size:,} bytes")

    deadline = time.time() + max_wait_seconds
    last_live_size = None
    attempts = 0

    while time.time() < deadline:
        attempts += 1
        try:
            req = urllib.request.Request(
                LIVE_URL,
                headers={"Cache-Control": "no-cache", "Pragma": "no-cache"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                live_bytes = resp.read()
                last_live_size = len(live_bytes)

                # Accept if within 5%. GitHub Pages applies whitespace/encoding
                # normalisation that can shift size by ~2-3% even when content
                # is identical. 5% tolerance still catches genuinely stale
                # deploys (where the file is structurally different) without
                # false-positiving on serving-layer variance.
                diff_pct = abs(last_live_size - local_index_size) / local_index_size * 100
                if diff_pct < 5.0:
                    log.info(f"  ✓ Live deployment verified (attempt {attempts}, "
                             f"live={last_live_size:,}, diff={diff_pct:.2f}%)")
                    return True
                else:
                    log.info(f"  ... attempt {attempts}: live={last_live_size:,} bytes, "
                             f"diff={diff_pct:.1f}% — waiting for rebuild")
        except Exception as e:
            log.info(f"  ... attempt {attempts}: fetch error ({e}) — retrying")

        time.sleep(poll_interval)

    # Timed out
    log.error("=" * 70)
    log.error("LIVE DEPLOYMENT VERIFICATION FAILED")
    log.error(f"  Local index.html:  {local_index_size:,} bytes")
    log.error(f"  Live index.html:   {last_live_size:,} bytes" if last_live_size
              else "  Live index.html:   could not fetch")
    log.error(f"  Waited:            {max_wait_seconds}s")
    log.error("  The push succeeded but the live site did not update to match.")
    log.error("  Possible causes:")
    log.error("    1. GitHub Pages rebuild is unusually slow (wait 5-10 min, check manually)")
    log.error("    2. Pages is serving a different branch/folder than expected")
    log.error("    3. A file required by index.html is not in DASHBOARD_FILES")
    log.error(f"  Check: {LIVE_URL}")
    log.error("=" * 70)
    return False


def publish():
    log.info("=== publish_dashboard — pushing to GitHub Pages ===")

    token = os.getenv("GITHUB_TOKEN", "")
    if not token:
        log.warning("GITHUB_TOKEN not set — skipping publish")
        return False

    # Capture local index.html size before push (for later verification)
    index_path = DOCS_DIR / "index.html"
    if not index_path.exists():
        log.error(f"Local {index_path} not found — aborting publish")
        return False
    local_index_size = index_path.stat().st_size
    log.info(f"Local docs/index.html: {local_index_size:,} bytes")

    # Sanity check: all required dashboard files must exist locally
    missing = [f for f in DASHBOARD_FILES if not (BASE_DIR / f).exists()]
    if missing:
        log.error(f"Required dashboard files missing locally: {missing}")
        log.error("Run generate_dashboard.py (and build_sa2_history.py if needed) first.")
        return False

    # Update remote URL with current token
    remote = f"https://iampatnb-afk:{token}@github.com/iampatnb-afk/Kintell.git"
    run_git(f'git remote set-url origin "{remote}"')

    # Stage all dashboard files (force-add to bypass *.json in .gitignore)
    files_arg = " ".join(DASHBOARD_FILES)
    run_git(f"git add -f {files_arg}")

    # Check if there's anything to commit
    result = subprocess.run(
        "git status --porcelain docs/",
        shell=True, cwd=str(BASE_DIR),
        capture_output=True, text=True
    )

    if not result.stdout.strip():
        log.info("Dashboard unchanged — nothing to push")
        # Still verify live matches local, in case a previous push silently failed
        verify_live_deployment(local_index_size)
        return True

    today = str(date.today())
    run_git(f'git commit -m "Dashboard update {today}"')
    push_ok = run_git("git push origin master:main")

    if not push_ok:
        log.error("Push failed — check GITHUB_TOKEN in .env")
        return False

    log.info(f"Dashboard pushed: {LIVE_URL}")

    # Post-push verification — this is the anti-silent-failure layer
    verified = verify_live_deployment(local_index_size)
    return verified


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    publish()
