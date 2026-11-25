---
id: US-DEF-05
type: story
title: Check the acceptance criteria format
epic: EP-DEF
source_reqs: [DEF-R08]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person writing tickets, I want criteria numbering and form checked, so that tests and change requests can point at a criterion by a number that never changes.

## Acceptance criteria

- AC1: Given a bullet under `## Acceptance criteria` not in `- AC<n>: <text>` form, when `backlog_check.py` runs, then it reports an error quoting the bullet.
- AC2: Given a criterion whose number is not greater than every number before it, when `backlog_check.py` runs, then it reports an error that the number is duplicated or out of order.
- AC3: Given a story criterion whose text does not start with `Given `, when `backlog_check.py` runs, then it reports an error that a story's criterion reads Given, when, then.
- AC4: Given a criterion written `(removed YYYY-MM-DD, <reason>)`, when `backlog_check.py` runs, then it is accepted and counted as not live.
- AC5: Given a task criterion written as a plain checkable statement, when `backlog_check.py` runs, then it is accepted.
- AC6: Given a task criterion with no text, when `backlog_check.py` runs, then it reports an error that the criterion is empty.

## Notes

- Adopted 2026-11-25 from existing behavior: the behavior is in `template/scripts/backlog_check.py`.
- The criteria describe what happens now; confirmation happens on the cited `(observed in code)` requirements.

## Open questions

- None. This story records behavior that already exists; anything that looks unintended is filed as a decision on the epic.
