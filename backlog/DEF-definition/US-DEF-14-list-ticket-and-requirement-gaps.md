---
id: US-DEF-14
type: story
title: List ticket and requirement gaps
epic: EP-DEF
source_reqs: [DEF-R03, DEF-R20]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person defining the product, I want one list of what keeps it from being fully defined, so that I know what to decide or refine next.

## Acceptance criteria

- AC1: Given a DEC or SPK that is neither `done` nor `deferred`, when `backlog_check.py --gaps` runs, then it lists the ticket as an open decision or spike with its title, and a deferred DEC is not listed.
- AC2: Given a `draft` story or task, when `backlog_check.py --gaps` runs, then it lists it as a draft with its title, and a draft spike is listed once, as open.
- AC3: Given an unfinished story with an open-question bullet that neither starts with `None` nor names a DEC or SPK, when `backlog_check.py --gaps` runs, then it lists the unanswered question.
- AC4: Given a `ready` or `in-progress` story, task, or spike without `refined:`, when `backlog_check.py --gaps` runs, then it lists it as not refined.
- AC5: Given an uncovered requirement and a requirement starting `(observed in code)`, when `backlog_check.py --gaps` runs, then it lists the first as not cited and the second as not yet confirmed by a person.
- AC6: Given a project with no gaps, when `backlog_check.py --gaps` runs, then it prints nothing and exits 0, while any gap, or a validation error (announced by a `WARN` line), makes it exit 1.

## Notes

- Adopted 2026-11-25 from existing behavior: the behavior is in `template/scripts/backlog_check.py`.
- The criteria describe what happens now; confirmation happens on the cited `(observed in code)` requirements.

## Open questions

- None. This story records behavior that already exists; anything that looks unintended is filed as a decision on the epic.
