# ROLLBACK — Centre v1 stake 2026-05-12

*This file documents how to revert to centre v1 if v2 cut-over fails catastrophically. Per locked decisions in `project_centre_v2_redesign.md` (2026-05-10 PM s3) + DEC-84 (2026-05-12).*

## Stake reference

- **Tag:** `centre-v1-stake-2026-05-12`
- **Commit SHA:** `212b597` (master HEAD as of 2026-05-12; "End-of-session Tier-2 doc refresh — DEC-83 close")
- **Bundle dir:** `recon/v1_final_stake_2026-05-12/` (this directory)
- **Files in bundle:**
  - `centre.html` — v3.31 renderer (copy of `docs/centre.html` at stake time)
  - `centre_page.py` — v23 backend (copy of root `centre_page.py` at stake time)
  - `PAYLOAD_SCHEMA.md` — v6 payload schema documentation
  - `ROLLBACK.md` — this file

## Tag creation (Patrick action — must run BEFORE first centre_page.py v24 edit)

```powershell
cd C:\Users\Patrick Bell\remara-agent
git tag centre-v1-stake-2026-05-12 212b597
```

Verify:
```powershell
git tag --list "centre-v1-stake-*"
git rev-parse centre-v1-stake-2026-05-12   # should print 212b597...
```

Optional push to origin (only needed if working across multiple machines):
```powershell
git push origin centre-v1-stake-2026-05-12
```

## Recovery recipe — full revert to v1 renderer

If v2 catastrophically fails after cut-over:

```powershell
cd C:\Users\Patrick Bell\remara-agent
git checkout centre-v1-stake-2026-05-12 -- centre_page.py docs/centre.html
```

This restores `centre_page.py` and `docs/centre.html` to their stake-time state. Server-side route bindings (in `review_server.py` or wherever `/centres/{id}` is wired) may need to revert too if v2 introduced route changes — check that file's diff against the stake commit:

```powershell
git diff 212b597 -- review_server.py
```

After file revert, restart the dev server. v1 renderer should serve at `/centres/{id}` again.

## Recovery recipe — partial revert (cherry-pick from stake)

If only specific helpers or render functions need reverting (not the full file):

```powershell
git show centre-v1-stake-2026-05-12:docs/centre.html > /tmp/centre_v1_full.html
# Then manually copy specific function bodies from /tmp/centre_v1_full.html into current docs/centre.html
```

Same for centre_page.py.

## Database considerations

DEC-84 does NOT mutate `kintell.db` schema or data. v2 build will:
- **NOT** add new tables to `kintell.db` for the matrix (the matrix is purely a render-side reorganisation of existing payload data)
- **MAY** add new helper queries inside `centre_page.py` v24 to assemble matrix rows from existing tables — those queries are read-only
- **NOT** alter audit_log discipline (no STD-08 backup needed for v2 build itself; backups apply when ingesting new data)

If v2 cut-over is reverted, no DB rollback is needed. The stake recovery is purely file-level.

## Payload-schema considerations

v6 → v7 transition during v2 build:
- v6 contract preserved in `position.*` keys throughout transition
- v7 adds new top-level keys (`executive`, `matrix`, `drawer`) on top of v6
- Cut-over flips renderer to consume v7 keys; v6 keys become derived/redundant
- **Post-cut-over reversion path:** revert `centre_page.py` and `docs/centre.html` from stake; v6 payload contract resurrects automatically because v7 keys are additive

If a v2 patch in flight HAS modified the v6 contract (e.g. removed a `position.catchment_position.rows[].field`), revert touches more files. Check the diff between current state and stake:

```powershell
git diff 212b597 -- centre_page.py
```

Look for any deletions in `_layer3_position`, `_build_community_profile`, `LAYER3_METRIC_META`, `LAYER3_METRIC_INTENT_COPY`, `LAYER3_METRIC_TRAJECTORY_SOURCE`, `LAYER3_METRIC_ABOUT_DATA`, `POSITION_CARD_ORDER` registries. Restore those entries from the bundle copy.

## When to use this recovery

Use this recovery if:
- v2 renders blank or broken pages for representative SA2s after cut-over
- v2 breaks an existing institutional consumer of `/centres/{id}` (Excel export consumer, downstream API client, etc.)
- A critical metric becomes invisible or misrendered post-cut-over and a fix isn't viable within ~1 sess

Do NOT use this recovery for cosmetic issues, single-metric bugs, or layout polish — those are surgical fixes against the v2 codebase, not full reverts.

## Stake retirement

This stake bundle is preserved indefinitely for traceability per `project_centre_v2_redesign.md` ("recoverable with effort if v2 catastrophically fails"). The git tag `centre-v1-stake-2026-05-12` should not be deleted. The bundle directory may be archived (zipped) after v2 has been live for ~3 months without incident — Patrick's call.
