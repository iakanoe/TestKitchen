---
id: US-DLV-19
type: story
title: Run the full check
epic: EP-DLV
source_reqs: [DLV-R25]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As an agent, person, or CI job, I want `deliver.py check` to run the backlog check, the scripts' self-tests, and the project's checks in one command, so that local runs and CI agree.

## Acceptance criteria

- AC1: Given a project with no `check_command`, when `deliver.py check` runs, then it runs `backlog_check.py`, the self-tests of `kitchen_lib`, `hosts`, `backlog_check`, and `deliver`, then `test_command` as a full run with no files, printing `== <step>` before each, and prints `PASS check` when all pass.
- AC2: Given a `check_command` in `kitchen.yml`, when `deliver.py check` runs, then it runs that command in place of the full test run.
- AC3: Given a failing step, when `deliver.py check` runs, then it prints `FAIL <step>` (with the exit code for the project command), runs no later step, and exits 1.

## Notes

Adopted 2026-11-25 from `template/scripts/deliver.py` (installed copy `scripts/deliver.py`); the criteria describe what the code does now and are not yet confirmed by a person. `docs/spec-v0.1.md` section 5 says three self-tests; the code runs four (the fourth is `deliver.py`'s own).

## Open questions

- None. Adopted behavior.
