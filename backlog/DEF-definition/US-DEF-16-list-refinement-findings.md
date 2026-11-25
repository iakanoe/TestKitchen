---
id: US-DEF-16
type: story
title: List refinement findings
epic: EP-DEF
source_reqs: [DEF-R22]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person refining tickets, I want the checks a script can make listed for me, so that the review covers the rest.

## Acceptance criteria

- AC1: Given an unfinished story with more live criteria than `split_threshold`, when `backlog_check.py --refine` runs, then it lists the count and suggests a split.
- AC2: Given a ticket citing a superseded requirement, when `backlog_check.py --refine` runs, then it lists the requirement and its replacement, adding for a done ticket that a change becomes a new ticket.
- AC3: Given an unfinished ticket whose open question names a DEC or SPK that is done, when `backlog_check.py --refine` runs, then it lists the question for re-checking.
- AC4: Given releases are listed and an unfinished story, task, or spike has no `release`, when `backlog_check.py --refine` runs, then it lists it as having no release slice.
- AC5: Given a done story with `hotfix: true` and no `refined:`, when `backlog_check.py --refine` runs, then it lists it for refinement and its follow-up.
- AC6: Given an `in-progress` ticket whose branch (its file name without `.md`, lowercased) is not on origin, when `backlog_check.py --refine` runs, then it lists it, stops listing it once the branch is pushed, exits 0, and prints a warning instead of the check when origin's branches cannot be listed.

## Notes

- Adopted 2026-11-25 from existing behavior: the behavior is in `template/scripts/backlog_check.py`.
- The criteria describe what happens now; confirmation happens on the cited `(observed in code)` requirements.

## Open questions

- None. This story records behavior that already exists; anything that looks unintended is filed as a decision on the epic.
