---
id: US-INST-02
type: story
title: Check prerequisites before installing
epic: EP-INST
source_reqs: [INST-R03]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a developer installing Test Kitchen, I want missing prerequisites named before anything is written, so that I fix my machine instead of debugging a half-done install.

## Acceptance criteria

- AC1: Given Python 3.7 or 3.8, when `init.py` starts, then it prints "Test Kitchen needs Python 3.9 or later; this is Python X.Y." and exits 1.
- AC2: Given `git` is not on the PATH, when an install or update starts, then it stops with exit code 1 saying git is missing.
- AC3: Given PyYAML cannot be imported, when a real install or update runs, then it stops with exit code 1 and the command to install PyYAML; on a dry run it prints the same text as a warning and continues.
- AC4: Given the host is github or gitlab and `gh` or `glab` is not on the PATH, when an install or update runs, then it warns that the CLI is missing and continues.

## Notes

Observed in `init.py` on 2026-11-25 by `/define adopt`; not yet confirmed by a person. Python 3.6 and older cannot parse `init.py` (`from __future__ import annotations` needs 3.7), so they get a syntax error instead of the sentence in AC1: DEC-INST-02 asks whether that is intended. `doctor` reports the same prerequisites as checks (US-INST-17).

## Open questions

- None. Behavior recorded as observed; the person confirms it.
