---
id: US-INST-16
type: story
title: Switch host or drop Claude Code files on update
epic: EP-INST
source_reqs: [INST-R20]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a maintainer of a project using Test Kitchen, I want an update to change the host or drop the Claude Code files, so that the install follows my project without a reinstall.

## Acceptance criteria

- AC1: Given `update` without `--host`, when it picks the host, then it uses the lock's `options.host`, else the host detected from `origin`.
- AC2: Given `update --host <another host>`, when it runs, then the other host's files are added, the previous host's files are listed as no longer part of Test Kitchen and left on disk, and the lock records the new host.
- AC3: Given `update --no-claude` on an install with Claude Code files, when it runs, then the `.claude/` files and `CLAUDE.md` are listed as removed and left on disk, and the lock's `options.no_claude` becomes true.
- AC4: Given a lock with `options.no_claude` true, when `update` runs without `--no-claude`, then the Claude Code files are still not installed.

## Notes

Observed in `init.py` on 2026-11-25 by `/define adopt`; not yet confirmed by a person. `--no-claude` can be turned on but never off by decision (decision log, "Installer choices made while building v0.1"). A host switch leaves `kitchen.yml`'s `host` line as it was, and `doctor` then suggests switching back: DEC-INST-01 asks whether that is intended. Seen by running `init.py` in a throwaway repository on 2026-11-25.

## Open questions

- None. Behavior recorded as observed; the person confirms it.
