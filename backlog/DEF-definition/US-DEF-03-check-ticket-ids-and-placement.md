---
id: US-DEF-03
type: story
title: Check ticket IDs and placement
epic: EP-DEF
source_reqs: [DEF-R06]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person maintaining the backlog, I want ticket IDs, file names, and folders checked, so that every ID is stable and every ticket is found with its epic.

## Acceptance criteria

- AC1: Given a ticket whose ID does not match its type's prefix or has fewer than two digits, when `backlog_check.py` runs, then it reports an error that the ID does not match the type.
- AC2: Given a ticket other than an epic whose file is not named `<ID>-<kebab-case-slug>.md`, when `backlog_check.py` runs, then it reports an error naming the expected file name.
- AC3: Given two tickets with the same ID, when `backlog_check.py` runs, then it reports a duplicate-ID error naming the other file.
- AC4: Given an epic whose file is not `epic.md`, that is not in its own folder directly under `backlog/`, or whose folder is not named `<CODE>-<slug>`, when `backlog_check.py` runs, then it reports an error.
- AC5: Given a ticket whose `epic` names no existing epic, when `backlog_check.py` runs, then it reports an error that the epic does not exist.
- AC6: Given a ticket outside its epic's folder, or whose ID code differs from its epic's code, when `backlog_check.py` runs, then it reports an error.

## Notes

- Adopted 2026-11-25 from existing behavior: the behavior is in `template/scripts/backlog_check.py`.
- The criteria describe what happens now; confirmation happens on the cited `(observed in code)` requirements.

## Open questions

- None. This story records behavior that already exists; anything that looks unintended is filed as a decision on the epic.
