---
id: US-DEF-04
type: story
title: Resolve ticket references and blockers
epic: EP-DEF
source_reqs: [DEF-R07]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person maintaining the backlog, I want every reference between tickets and requirements resolved, so that nothing points at something that does not exist.

## Acceptance criteria

- AC1: Given a `blocked_by` entry naming a ticket that does not exist or the ticket itself, when `backlog_check.py` runs, then it reports an error.
- AC2: Given a `source_reqs` entry naming a requirement that is not defined, when `backlog_check.py` runs, then it reports an error.
- AC3: Given a `fixes` entry that is not in `<ticket>/AC<n>` form or names a criterion that is not live, when `backlog_check.py` runs, then it reports an error, and a `fixes` entry naming a live criterion passes.
- AC4: Given a ticket body mentioning `<ticket>/AC<n>` for a criterion that is not live, when `backlog_check.py` runs, then it reports an error, and a mention of a live criterion passes.
- AC5: Given a `ready` ticket whose blocker is unfinished, when `backlog_check.py` runs, then no error is reported, and given the same ticket `done`, then it reports an error naming the blocker and its status.
- AC6: Given tickets whose `blocked_by` entries form a cycle, when `backlog_check.py` runs, then it reports the cycle once, as the chain of IDs back to the first.

## Notes

- Adopted 2026-11-25 from existing behavior: the behavior is in `template/scripts/backlog_check.py`.
- The criteria describe what happens now; confirmation happens on the cited `(observed in code)` requirements.

## Open questions

- None. This story records behavior that already exists; anything that looks unintended is filed as a decision on the epic.
