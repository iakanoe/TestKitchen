---
id: US-DEF-09
type: story
title: Keep tickets self-contained when asked
epic: EP-DEF
source_reqs: [DEF-R12]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person exporting tickets to readers without the repository, I want repository links and paths in ticket bodies reported, so that every ticket reads on its own.

## Acceptance criteria

- AC1: Given `self_contained_tickets: true` and a ticket body with a markdown link to a relative path, when `backlog_check.py` runs, then it reports an error per link, with its body line number.
- AC2: Given `self_contained_tickets: true` and a ticket body naming a repository path or document, when `backlog_check.py` runs, then it reports an error per occurrence.
- AC3: Given `self_contained_tickets: true` and a ticket body linking only to an `https` address, when `backlog_check.py` runs, then no error is reported.
- AC4: Given the setting is off and a ticket body links to repository files, when `backlog_check.py` runs, then no error is reported.

## Notes

- Adopted 2026-11-25 from existing behavior: the behavior is in `template/scripts/backlog_check.py`.
- The criteria describe what happens now; confirmation happens on the cited `(observed in code)` requirements.

## Open questions

- None. This story records behavior that already exists; anything that looks unintended is filed as a decision on the epic.
