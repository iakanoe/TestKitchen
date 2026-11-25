---
id: US-DEF-06
type: story
title: Enforce readiness
epic: EP-DEF
source_reqs: [DEF-R09]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person deciding what can be built, I want tickets that claim readiness checked, so that nothing is picked up without an owner, a criterion, and a requirement.

## Acceptance criteria

- AC1: Given a `ready`, `in-progress`, or `done` ticket other than an epic whose owner is empty or `TBD`, when `backlog_check.py` runs, then it reports an error that it needs an owner.
- AC2: Given a `ready`, `in-progress`, or `done` story or task with no live criterion, when `backlog_check.py` runs, then it reports an error that it needs at least one live acceptance criterion.
- AC3: Given a `ready`, `in-progress`, or `done` story with empty `source_reqs`, when `backlog_check.py` runs, then it reports an error, while a task or spike with empty `source_reqs` passes.
- AC4: Given `kitchen.yml` lists releases and a `ready`, `in-progress`, or `done` story, task, or spike has no `release`, when `backlog_check.py` runs, then it reports an error that it needs a release.
- AC5: Given a `draft` story with owner `TBD`, when `backlog_check.py` runs, then no readiness error is reported for it.

## Notes

- Adopted 2026-11-25 from existing behavior: the behavior is in `template/scripts/backlog_check.py`. Epics are not checked for readiness; see DEC-DEF-02.
- The criteria describe what happens now; confirmation happens on the cited `(observed in code)` requirements.

## Open questions

- None. This story records behavior that already exists; anything that looks unintended is filed as a decision on the epic.
