---
id: TASK-CONF-01
type: task
title: Call git with fixed settings
epic: EP-CONF
source_reqs: [CONF-R20]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

Every git call built through the shared library's helper runs with fixed settings, so the person's own git configuration and unusual file names cannot change what the scripts read.

## Acceptance criteria

- AC1: Every git command built through the shared git helper passes `core.quotePath=false`, `color.ui=never`, and `log.showSignature=false`; the repository-root lookup is the one plain `git rev-parse --show-toplevel` call, whose output those settings do not change.
- AC2: Commands are run with an argument list, never through a shell.
- AC3: A failing git command run through the shared helper raises an error that names the command and includes git's own message.
- AC4: With a global git configuration that turns path quoting on and colors on, file names with non-ASCII characters or spaces are still read correctly.

## Notes

Decision log, "History checks see merge commits". Diff commands in the delivery script add their own options (no color, no external diff, `-z`); those belong to the delivery epic.

## Open questions

- None. Adopted behavior, recorded as the code does it now; a person confirms the requirements.
