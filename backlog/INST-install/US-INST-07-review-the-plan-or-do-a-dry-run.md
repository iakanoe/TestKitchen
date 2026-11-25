---
id: US-INST-07
type: story
title: Review the plan or do a dry run
epic: EP-INST
source_reqs: [INST-R11]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a developer installing Test Kitchen, I want to see every file the installer will write before it writes anything, so that I can stop or adjust before my repository changes.

## Acceptance criteria

- AC1: Given an install with its answers, when the plan is shown, then it lists the version and the target, the source, the host with its reason, whether Claude Code files are installed, and the `tests`, `code`, and `test_command` answers.
- AC2: Given the plan, when it lists files, then each file has a `create` row, or an `exists` row saying yours is kept and the new version is written as `<name>.kitchen-new`, followed by a `write kitchen.lock` row and a note per CI file about its toolchain step.
- AC3: Given `--dry-run`, when the plan has been shown, then the run prints "Dry run: nothing was written.", writes nothing, asks for no confirmation, and exits 0.
- AC4: Given a real run, when the plan has been shown, then it asks "Write these files?" (default yes), and a no prints "Stopped. Nothing was written." and exits 1.

## Notes

Observed in `init.py` on 2026-11-25 by `/define adopt`; not yet confirmed by a person. Without a terminal the confirmation follows US-INST-04/AC5.

## Open questions

- None. Behavior recorded as observed; the person confirms it.
