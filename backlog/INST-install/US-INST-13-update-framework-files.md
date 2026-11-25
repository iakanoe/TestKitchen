---
id: US-INST-13
type: story
title: Update framework files
epic: EP-INST
source_reqs: [INST-R17]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a maintainer of a project using Test Kitchen, I want an update to replace only the framework files I did not touch, so that I get the new release without losing my edits.

## Acceptance criteria

- AC1: Given no `kitchen.lock` in the target, when `update` runs, then it stops with exit code 2 saying Test Kitchen is not installed there.
- AC2: Given a locked framework file, when `update` compares it, then a file unchanged since install whose new version differs is replaced, a file edited locally whose new version is unchanged is kept with nothing written, and a file equal to the new version is counted as unchanged.
- AC3: Given a locked framework file missing locally, when `update` runs, then the new version is restored.
- AC4: Given a file new in this version, when `update` runs, then it is added, or, when a file already exists at that path, written as `<name>.kitchen-new` with yours kept.
- AC5: Given a locked file the new version no longer ships, when `update` runs, then it is listed as removed, left on disk, and dropped from the lock.
- AC6: Given `kitchen.yml`, or `--tests`, `--code`, or `--test-command` on the command line, when `update` runs, then `kitchen.yml` is never written and the flags only produce a warning that they apply to install.

## Notes

Observed in `init.py` on 2026-11-25 by `/define adopt`; not yet confirmed by a person. A deleted framework file is restored by decision (decision log, "Installer choices made while building v0.1"). Conflicts (edited on both sides): US-INST-14.

## Open questions

- None. Behavior recorded as observed; the person confirms it.
