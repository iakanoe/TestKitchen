---
id: US-DEF-10
type: story
title: Prove criteria with tagged tests
epic: EP-DEF
source_reqs: [DEF-R13, DEF-R14]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person accepting delivered work, I want each done story's criteria tied to tests by tag, so that a criterion counts as built only when a test proves it.

## Acceptance criteria

- AC1: Given a test file with a tag, in either form, naming a criterion that is not live or a ticket that does not exist, when `backlog_check.py` runs, then it reports an error that the tag is not a live acceptance criterion.
- AC2: Given a test file with a tag naming a live criterion of a `draft` or `ready` ticket, when `backlog_check.py` runs, then it reports an error that tags name started tickets.
- AC3: Given a `done` story whose criteria are tagged only in code files, when `backlog_check.py` runs, then those tags prove nothing and it reports the criteria as untested.
- AC4: Given a `done` story without `adopted: true` and a live criterion no test file tags, when `backlog_check.py` runs, then it reports an error naming the untagged criteria.
- AC5: Given an `in-progress` story with a live criterion no test file tags, when `backlog_check.py` runs, then it prints a warning naming the untagged criteria and exits 0.
- AC6: Given a `done` story with `adopted: true` and an untagged live criterion, when `backlog_check.py` runs, then no error is reported, and `--test-debt` prints a `DEBT` line for that criterion only and exits 0.

## Notes

- Adopted 2026-11-25 from existing behavior: the behavior is in `template/scripts/backlog_check.py`; the tag patterns themselves live in `kitchen_lib.py`.
- The criteria describe what happens now; confirmation happens on the cited `(observed in code)` requirements.

## Open questions

- None. This story records behavior that already exists; anything that looks unintended is filed as a decision on the epic.
