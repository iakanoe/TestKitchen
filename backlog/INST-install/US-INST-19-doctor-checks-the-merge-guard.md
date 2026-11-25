---
id: US-INST-19
type: story
title: Doctor checks the merge guard
epic: EP-INST
source_reqs: [INST-R24]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a maintainer using Claude Code, I want `doctor` to fail when the merge guard is not active, so that I know when nothing stops an agent from merging on a failing check.

## Acceptance criteria

- AC1: Given `.claude/hooks/guard.py` exists and a `PreToolUse` hook in `.claude/settings.json` has a command naming `guard.py`, when `doctor` runs, then the merge guard check passes.
- AC2: Given the guard file is missing, `.claude/settings.json` is missing or not valid JSON, or no `PreToolUse` hook runs the guard, when `doctor` runs, then it fails with the reason and how to restore the hook block.
- AC3: Given `.claude/settings.json` or `.claude/settings.local.json` sets `disableAllHooks: true`, when `doctor` runs, then it fails saying that the setting switches the guard off.
- AC4: Given a lock with `options.no_claude` true, when `doctor` runs, then it skips the guard check and reminds that agents without the guard must run `deliver.py gate merge` before every merge.

## Notes

Observed in `init.py` on 2026-11-25 by `/define adopt`; not yet confirmed by a person. Failing on `disableAllHooks` is a recorded choice (decision log, "Installer choices made while building v0.1"). An install over an existing `.claude/settings.json` leaves the guard unregistered until the `.kitchen-new` copy is merged, so this check fails right after such an install (seen on 2026-11-25).

## Open questions

- None. Behavior recorded as observed; the person confirms it.
