"""
proc_helpers.py — STD-13 process-discovery helpers (Win11-compatible).

Purpose
-------
Replace the deprecated WMIC-based python.exe orphan check with a
Get-CimInstance Win32_Process equivalent. WMIC is deprecated on Windows 11
and is being phased out by Microsoft; new scripts MUST use the helper here
instead of shelling out to `wmic.exe` directly.

Same return shape as the historical _wmic_python_procs() functions in
populate_service_catchment_cache.py, layer3_x_catchment_metric_banding.py,
migrate_4_3_5_service_catchment_cache.py, and migrate_4_3_5b_rename_capture_rate.py.
Drop-in compatible with the existing std13_self_check() pattern.

Historical scripts are not retrofitted — they have already shipped and are
idempotency-guarded against re-runs. The WMIC-unavailable warning they emit
is harmless (the check skips gracefully). Future scripts should
`from proc_helpers import std13_self_check` and call it directly.

Usage
-----
    # Quick / canonical use — match historical std13_self_check pattern:
    from proc_helpers import std13_self_check
    std13_self_check(log, fail)  # log/fail are your script's logger funcs

    # Direct query if you need the (pid, ppid) list:
    from proc_helpers import query_python_processes
    procs = query_python_processes()  # list[(pid, ppid)] or None

Compatibility
-------------
- Windows 10: works (Get-CimInstance was added in PowerShell 3.0 / WMF 3.0)
- Windows 11: works (canonical post-WMIC pattern)
- Non-Windows: query_python_processes() returns None; std13_self_check()
  logs a skip warning. Same fail-soft semantics as the historical helpers.

Returns None when:
- PowerShell is not on PATH (FileNotFoundError)
- Get-CimInstance command fails (CalledProcessError)
- Query times out (TimeoutExpired; default 10s)

Callers should treat None as "could not check; skip with warning".

References
----------
STD-13 (working standards): orphan python.exe must not be alive when
mutation scripts run. The check exists to prevent a stale review_server.py
or interactive interpreter holding a stale module import while a script
tries to mutate the underlying file.
"""

import os
import subprocess
from typing import Callable, Optional


def query_python_processes() -> Optional[list[tuple[int, int]]]:
    """Return list of (pid, parent_pid) for all running python.exe processes.

    Uses Get-CimInstance Win32_Process via PowerShell shell-out (Win11-safe;
    WMIC-free). Returns None on any failure — callers should treat None as
    "could not check; skip with warning" (matches historical
    _wmic_python_procs() fail-soft semantics).
    """
    cmd = [
        "powershell.exe",
        "-NoProfile",
        "-NonInteractive",
        "-Command",
        # Emit one "pid,ppid" line per python.exe process. ForEach-Object
        # gives us a clean format we can split on comma without dealing
        # with PowerShell's CSV quoting.
        "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
        "ForEach-Object { \"$($_.ProcessId),$($_.ParentProcessId)\" }",
    ]
    try:
        out = subprocess.check_output(
            cmd,
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None

    procs: list[tuple[int, int]] = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(",")
        if len(parts) != 2:
            continue
        try:
            pid = int(parts[0])
            ppid = int(parts[1])
        except ValueError:
            continue
        procs.append((pid, ppid))
    return procs


def std13_self_check(log: Callable[[str], None],
                     fail: Callable[[str], None]) -> None:
    """STD-13 orphan-python.exe check. Drop-in for historical pattern.

    Scans for python.exe processes not descended from this script's PID.
    Calls log() for status messages; calls fail() if orphans are detected
    (fail is expected to raise / sys.exit; std13_self_check returns
    normally if the check passes or skips).

    Drop-in replacement for the per-script std13_self_check() functions
    in the historical Layer 2.5 / 4.3.5 / 4.3.5b mutation scripts.

    Example caller:
        from proc_helpers import std13_self_check
        std13_self_check(log, fail)
    """
    log("STD-13: scanning for orphan python.exe (Get-CimInstance)")
    my_pid = os.getpid()
    procs = query_python_processes()
    if procs is None:
        log("STD-13: process query unavailable; SKIPPING with warning")
        return
    excluded = {my_pid}
    changed = True
    while changed:
        changed = False
        for pid, ppid in procs:
            if ppid in excluded and pid not in excluded:
                excluded.add(pid)
                changed = True
    orphans = [pid for pid, _ in procs if pid not in excluded]
    if orphans:
        fail(f"STD-13: orphan python.exe alive: {orphans}")
    log(f"STD-13: clean ({len(procs)} python procs, all descendants)")


# Self-test: when run directly, prints what query_python_processes returns.
# Useful for verifying the helper works on a given machine before any
# downstream script depends on it.
if __name__ == "__main__":
    import sys
    print("proc_helpers.py self-test")
    print("=" * 60)
    procs = query_python_processes()
    if procs is None:
        print("query_python_processes() returned None")
        print("  -> Get-CimInstance unavailable or failed.")
        print("  -> std13_self_check() would log 'SKIPPING with warning'.")
        sys.exit(1)
    print(f"query_python_processes() returned {len(procs)} python.exe process(es):")
    print()
    print(f"  {'PID':>8}  {'PPID':>8}  {'note':<40}")
    print(f"  {'-'*8}  {'-'*8}  {'-'*40}")
    my_pid = os.getpid()
    for pid, ppid in sorted(procs):
        note = "  <-- this process" if pid == my_pid else ""
        print(f"  {pid:>8}  {ppid:>8}  {note:<40}")
    print()
    print(f"This process PID:    {my_pid}")
    print(f"This process PPID:   {os.getppid()}")
    print()
    print("Self-test PASSED. Helper is wired correctly for STD-13 use.")
