---
id: US-INST-22
type: story
title: Report errors with exit codes
epic: EP-INST
source_reqs: [INST-R27]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As an agent or CI job running the installer, I want one clear message and a stable exit code for every stop, so that I can tell a usage problem from a failure without parsing a traceback.

## Acceptance criteria

- AC1: Given a usage problem (a bad flag value, a missing answer without a terminal, a refused folder), when the run stops, then it prints `error: <message>` on standard error without a traceback and exits 2.
- AC2: Given a failure (a missing prerequisite, a failed download, a failed `git init`, an unreadable lock), when the run stops, then it prints `error: <message>` on standard error and exits 1.
- AC3: Given Ctrl-C during a run, when it stops, then it prints "Stopped." on standard error and exits 130.

## Notes

Observed in `init.py` on 2026-11-25 by `/define adopt`; not yet confirmed by a person. The exit codes are documented in the module docstring and `guide/install.md`; 130 for Ctrl-C is in the code only. A `kitchen.lock` whose `version` is not a dotted number makes `update` end in a Python traceback with exit code 1: DEC-INST-04 asks whether that is intended.

## Open questions

- None. Behavior recorded as observed; the person confirms it.
