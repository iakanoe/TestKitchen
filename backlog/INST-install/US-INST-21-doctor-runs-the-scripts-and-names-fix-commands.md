---
id: US-INST-21
type: story
title: Doctor runs the scripts and names fix commands
epic: EP-INST
source_reqs: [INST-R26, INST-R21]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a maintainer of a project using Test Kitchen, I want `doctor` to run the installed scripts and give me commands that work from my project folder, so that I can fix a broken install in one step.

## Acceptance criteria

- AC1: Given `scripts/backlog_check.py`, when `doctor` runs, then it runs the script and passes when it exits 0 or fails with the end of its output; given the script missing on an installed project, it fails with the restore command.
- AC2: Given locked files `scripts/<name>.py` whose text mentions `--self-test`, when `doctor` runs, then it runs each with `--self-test` and passes or fails per script, with the end of its output on a failure.
- AC3: Given `init.py` runs from a clone, when doctor, install, or update suggests running it again, then the command is `python3 <absolute path of that init.py> … --target .`; when piped, it is the pinned `curl -fsSL … | python3 -` one-liner.

## Notes

Observed in `init.py` on 2026-11-25 by `/define adopt`; not yet confirmed by a person. `init.py` is never copied into a project, so a bare `python3 init.py` hint would not work there (comment in `rerun`).

## Open questions

- None. Behavior recorded as observed; the person confirms it.
