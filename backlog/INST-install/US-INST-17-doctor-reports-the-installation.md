---
id: US-INST-17
type: story
title: Doctor reports the installation
epic: EP-INST
source_reqs: [INST-R21, INST-R22]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a maintainer of a project using Test Kitchen, I want a read-only checklist of what my install needs, so that I find what is broken and how to fix it.

## Acceptance criteria

- AC1: Given a project, when `doctor` runs, then it writes no file, no `__pycache__` either, prints one `PASS`, `WARN`, `FAIL`, or `SKIP` line per check with the fix indented under each problem, and ends with "doctor: all checks passed" or "doctor: N failed, M warning(s)".
- AC2: Given any check failed, when `doctor` exits, then the exit code is 1; otherwise it is 0, warnings included.
- AC3: Given the environment, when `doctor` runs, then it reports the Python version and fails when PyYAML or git is missing or the target is not a git repository.
- AC4: Given no `kitchen.lock`, or one that is not valid JSON or has no `files` table, when `doctor` runs, then it fails with the command to install, or with the advice to restore the lock from git history; given a valid lock, it passes with the installed version.
- AC5: Given a valid lock listing a framework file that is missing, when `doctor` runs, then it fails naming the missing files and the update command that restores them; otherwise it passes with the number of files.
- AC6: Given a `<name>.kitchen-new` copy next to a locked file or `kitchen.yml`, when `doctor` runs, then it warns that the copy is waiting to be merged.

## Notes

Observed in `init.py` on 2026-11-25 by `/define adopt`; not yet confirmed by a person. Doctor duplicates the glob rules and `kitchen.yml` keys on purpose, so it works when the installed scripts are missing or broken (comments in `init.py`).

## Open questions

- None. Behavior recorded as observed; the person confirms it.
