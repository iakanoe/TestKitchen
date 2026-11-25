---
id: US-INST-10
type: story
title: Record the install in kitchen.lock
epic: EP-INST
source_reqs: [INST-R14]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a maintainer of a project using Test Kitchen, I want a lock file recording what was installed, so that updates and the guard can tell framework files and my edits apart.

## Acceptance criteria

- AC1: Given a finished install or update, when `kitchen.lock` is written, then it is JSON with `about`, `lock_format: 1`, `version`, `source`, `options` (`host`, `no_claude`, `toolchain`), `files`, and `side_by_side`.
- AC2: Given a release from a local checkout, when the lock is written, then `source` reads `local checkout (commit <sha>)`, or `local checkout` when the checkout is not a git repository, and never a local path; given a download, it reads `<repository URL>@v<version>`.
- AC3: Given the installed files, when the lock is written, then `files` maps every framework path except `kitchen.yml` to the sha256 of the content installed there or offered as `<name>.kitchen-new`.
- AC4: Given `.kitchen-new` copies on disk when the lock is written, when `side_by_side` is filled, then it lists each file, `kitchen.yml` included, whose copy is waiting.

## Notes

Observed in `init.py` on 2026-11-25 by `/define adopt`; not yet confirmed by a person. JSON was chosen so readers without PyYAML (the guard) can read it (decision log, "Installer choices made while building v0.1").

## Open questions

- None. Behavior recorded as observed; the person confirms it.
