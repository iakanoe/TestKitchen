---
id: US-DEF-17
type: story
title: Run the self-test and reject bad arguments
epic: EP-DEF
source_reqs: [DEF-R23]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person installing or checking Test Kitchen, I want the script to check itself and refuse arguments it cannot honor, so that a broken install or a mistyped command is noticed.

## Acceptance criteria

- AC1: Given any project, when `backlog_check.py --self-test` runs, then it prints `PASS self-test` and exits 0 without using the network.
- AC2: Given two of the modes `--gaps`, `--refine`, `--test-debt`, `--self-test` together, or one of them with `--strict`, when `backlog_check.py` runs, then it prints the usage and exits 2.
- AC3: Given one of those modes with `--pr-body=FILE`, when `backlog_check.py` runs, then it prints the usage and exits 2.
- AC4: Given an argument the script does not know, when `backlog_check.py` runs, then it prints the usage and exits 2.

## Notes

- Adopted 2026-11-25 from existing behavior: the behavior is in `template/scripts/backlog_check.py`. The self-test's broken-fixture cases run inside the script and cannot be triggered from outside.
- The criteria describe what happens now; confirmation happens on the cited `(observed in code)` requirements.

## Open questions

- None. This story records behavior that already exists; anything that looks unintended is filed as a decision on the epic.
