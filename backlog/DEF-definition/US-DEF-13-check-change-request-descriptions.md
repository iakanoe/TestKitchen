---
id: US-DEF-13
type: story
title: Check change-request descriptions
epic: EP-DEF
source_reqs: [DEF-R19]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person reviewing a change request, I want its description checked for filed gaps and logged decisions, so that nothing found during the work is lost.

## Acceptance criteria

- AC1: Given a description whose `## Gaps found` bullets name existing tickets, whose `## Decisions` bullets end `Log: <title>` naming an existing decision-log heading, and whose `## Platform changes` is a single `None` bullet, when `backlog_check.py --pr-body=FILE` runs, then it exits 0, HTML comments included in the file being ignored.
- AC2: Given a description file that cannot be read, that lacks one of the three sections, or whose section has no bullet, when `backlog_check.py --pr-body=FILE` runs, then it reports an error and exits 1.
- AC3: Given a `## Gaps found` bullet naming no ticket, or any bullet naming a ticket that does not exist, when `backlog_check.py --pr-body=FILE` runs, then it reports an error.
- AC4: Given a decision or platform-change bullet whose `Log:` title has no decision-log heading, or with neither a `Log:` title nor a done DEC, when `backlog_check.py --pr-body=FILE` runs, then it reports an error.
- AC5: Given a decision bullet naming a done DEC and no `Log:` title, when `backlog_check.py --pr-body=FILE` runs, then it is accepted.
- AC6: Given a delivery record file with a description marker line, when `backlog_check.py --pr-body=FILE` runs, then only the description after the marker, read as TASK-CONF-02/AC4 states, is checked.

## Notes

- Adopted 2026-11-25 from existing behavior: the behavior is in `template/scripts/backlog_check.py`. The decision-log heading format is `### YYYY-MM-DD — <title>` with an em dash.
- The criteria describe what happens now; confirmation happens on the cited `(observed in code)` requirements.

## Open questions

- None. This story records behavior that already exists; anything that looks unintended is filed as a decision on the epic.
