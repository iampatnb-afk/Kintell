"""
add_std36_session_start.py — append STD-36 (session-start upload convention)
to STANDARDS.md.

Single-mutation idempotent appender. STD-08 backup; checks for sentinel
before applying.
"""

import shutil
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent
STANDARDS = REPO / "recon" / "Document and Status DB" / "STANDARDS.md"

STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

SENTINEL = "### STD-36 — Session-start upload convention"

# Anchor: end of Process section, before "---" + "## Coding"
ANCHOR = """This standard supersedes the implicit "produce a monolith only when restructuring" assumption from the 2026-04-28 doc restructure. Monoliths now ship every session that materially changes Tier-2 state.

---

## Coding"""

REPLACEMENT = """This standard supersedes the implicit "produce a monolith only when restructuring" assumption from the 2026-04-28 doc restructure. Monoliths now ship every session that materially changes Tier-2 state.

### STD-36 — Session-start upload convention
*Origin: 2026-05-04*

At the start of every chat session, the operator uploads a fixed set of files so Claude is working from on-disk ground truth rather than potentially-stale project knowledge. This eliminates the recurring multi-round-trip context-recovery probe that opens otherwise.

**Required uploads at session start:**

1. **Active code files** under edit or likely to be touched:
   - `centre_page.py`
   - `docs/centre.html`
   - Any other code file the session will modify (e.g. a build script if it's the focus)

2. **Tier-2 doc set** (all 5 from `recon/Document and Status DB/`):
   - `PROJECT_STATUS.md`
   - `OPEN_ITEMS.md`
   - `PHASE_LOG.md`
   - `ROADMAP.md`
   - `DECISIONS.md`

3. **Plus a one-line `git log --oneline -1`** in the kickoff message so HEAD is verified at the actual hash, not assumed from project knowledge.

**Why.** Project knowledge lags HEAD by 0-N commits depending on whether monoliths have been re-uploaded; Tier-2 docs in project knowledge are a snapshot of last upload, not on-disk current. Without the upload convention, Claude's first 3-5 turns of a session are spent probing for ground truth — work that adds zero value to the actual task. With the convention, Claude has on-disk current state in turn 1 and can begin productive work immediately.

**STANDARDS.md is NOT in the required uploads** because Claude reads it from project knowledge as the institutional standard reference, and it changes infrequently. If a session is going to modify STANDARDS.md, upload it then.

**What this is not.** This is not a substitute for end-of-session doc refresh (STD-35) or for monolith regen — those remain mandatory. STD-36 governs the inbound side of every session; STD-35 governs the outbound side.

---

## Coding"""


def main() -> None:
    print("=" * 64)
    print("Appending STD-36 to STANDARDS.md")
    print("=" * 64)

    if not STANDARDS.exists():
        raise FileNotFoundError(f"STANDARDS.md not found at {STANDARDS}")

    text = STANDARDS.read_text(encoding="utf-8")

    if SENTINEL in text:
        print("\nSKIP: STD-36 already present (idempotent — already applied).")
        return

    if ANCHOR not in text:
        # Try LF normalisation in case file is CRLF
        anchor_crlf = ANCHOR.replace("\n", "\r\n")
        if anchor_crlf in text:
            anchor_used = anchor_crlf
            replacement_used = REPLACEMENT.replace("\n", "\r\n")
        else:
            raise RuntimeError(
                "Anchor not found. STANDARDS.md structure may have changed.\n"
                f"Anchor first 80 chars: {ANCHOR[:80]!r}"
            )
    else:
        anchor_used = ANCHOR
        replacement_used = REPLACEMENT

    if text.count(anchor_used) > 1:
        raise RuntimeError(f"Anchor not unique ({text.count(anchor_used)} matches).")

    # Backup
    backup = STANDARDS.with_name(f"{STANDARDS.name}.bak_{STAMP}")
    shutil.copy2(STANDARDS, backup)
    print(f"\nBackup: {backup.name}")

    new_text = text.replace(anchor_used, replacement_used, 1)
    STANDARDS.write_text(new_text, encoding="utf-8", newline="")
    print("STANDARDS.md updated with STD-36.")
    print("\nNext: stage + commit.")
    print('  git add "recon/Document and Status DB/STANDARDS.md"')
    print('  git commit -m "STD-36 added: session-start upload convention. Fixes recurring multi-round-trip context-recovery overhead at chat start. Operator uploads active code files + 5 Tier-2 docs at session start; HEAD verified via git log --oneline -1 in kickoff message."')
    print("  git push")


if __name__ == "__main__":
    main()
