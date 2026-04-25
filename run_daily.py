"""
run_daily.py — Remara Agent Weekly Runner
Runs every Tuesday at 10:00 AM via Windows Task Scheduler.

Pipeline:
  1. module1_acecqa.py          — ACECQA diff (new/changed services)
  2. module2_enrichment.py      — Contact enrichment via Claude
  3. module2b_catchment.py      — SA2 catchment + ABS demographics
  4. module2c_targeting.py      — Operator group scoring
  5. generate_prospecting_page  — HTML prospecting page
  6. module3_da_portals.py      — DA portal monitoring
  7. module6_news.py            — Weekly news brief
  8. module5_digest.py          — Email digest (sends to Gmail)

Schedule: Every Tuesday at 10:00 AM
  Task name: Remara Weekly Run
  Program: python
  Arguments: "C:\\Users\\Patrick Bell\\remara-agent\\run_daily.py"
  Start in: C:\\Users\\Patrick Bell\\remara-agent
"""

import subprocess
import sys
import logging
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
LOG_FILE = BASE_DIR / "data" / "run_daily.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ]
)
log = logging.getLogger(__name__)


def run_module(script: str, label: str, timeout: int = 600) -> bool:
    script_path = BASE_DIR / script
    if not script_path.exists():
        log.warning(f"SKIP {label} — {script} not found")
        return False

    log.info(f"--- {label} ---")
    start = datetime.now()
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(BASE_DIR),
            timeout=timeout,
        )
        elapsed = (datetime.now() - start).seconds
        if result.returncode == 0:
            log.info(f"OK {label} ({elapsed}s)")
            return True
        else:
            log.error(f"FAILED {label} (exit code {result.returncode})")
            return False
    except subprocess.TimeoutExpired:
        log.error(f"TIMEOUT {label} (>{timeout}s)")
        return False
    except Exception as e:
        log.error(f"ERROR {label}: {e}")
        return False


def run():
    log.info("=" * 60)
    log.info(f"Remara Weekly Run — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    log.info("=" * 60)

    results = {}

    results["acecqa"]       = run_module("module1_acecqa.py",             "1. ACECQA diff",          timeout=1800)
    results["enrichment"]   = run_module("module2_enrichment.py",          "2. Contact enrichment")
    results["catchment"]    = run_module("module2b_catchment.py",          "3. Catchment data")
    results["targeting"]    = run_module("module2c_targeting.py",          "4. Operator targeting",   timeout=300)
    results["prospecting"]  = run_module("generate_prospecting_page.py",   "5. Prospecting page")
    results["da_portals"]   = run_module("module3_da_portals.py",          "6. DA portals")
    results["property"]     = run_module("module4_property.py",            "7. Property research", timeout=900)
    results["news"]         = run_module("module6_news.py",                "8. News brief",           timeout=1200)
    results["digest"]       = run_module("module5_digest.py",              "9. Email digest")
    results["dashboard"]    = run_module("generate_dashboard.py",          "10. Dashboard")
    results["publish"]      = run_module("publish_dashboard.py",           "11. Publish to GitHub")

    log.info("=" * 60)
    ok      = sum(1 for v in results.values() if v is True)
    failed  = sum(1 for v in results.values() if v is False)
    log.info(f"Complete: {ok} OK, {failed} failed/skipped")
    log.info(f"Log: {LOG_FILE}")
    log.info("=" * 60)


if __name__ == "__main__":
    run()
