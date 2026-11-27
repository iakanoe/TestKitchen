---
id: US-DEF-34
type: story
title: Accept review-only criteria without a tagged test
epic: EP-DEF
source_reqs: [DEF-R47, DEF-R48]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: deferred
replaces: [US-DEF-10/AC4, US-DEF-10/AC5, US-DEF-10/AC6]
---

As a person defining tickets, I want criteria that only a reviewer can check to carry a `(review)` marker, so that they stay in their story without a tagged test or permanent test debt.

## Acceptance criteria

- AC1: Given a `done` story without `adopted: true` and a live criterion no test file tags, when `backlog_check.py` runs, then it reports an error naming the untagged criteria, leaving out those whose text starts with `(review)`.
- AC2: Given an `in-progress` story with a live criterion no test file tags, when `backlog_check.py` runs, then it prints a warning naming the untagged criteria, leaving out `(review)` ones, and exits 0.
- AC3: Given a `done` story with `adopted: true` and an untagged live criterion, when `backlog_check.py` runs, then no error is reported, and `--test-debt` prints a `DEBT` line for that criterion unless its text starts with `(review)`, and exits 0.
- AC4: Given a test file whose tag names a live `(review)` criterion, when `backlog_check.py` runs, then it reports an error that a `(review)` criterion is checked by the final review, not by a test.

## Notes

- Retired 2026-11-27: DEC-DEF-05 reversed (decision log, "Review-only work stays in untestable tasks"); this ID is never reused.
- Decided 2026-11-27 (DEC-DEF-05, option (b); decision log, "Review-only criteria carry a (review) marker").
- Replaces US-DEF-10/AC4, AC5, and AC6 (shown to the owner and approved on 2026-11-27): each becomes the same rule with `(review)` criteria left out. They are crossed out when this story is delivered.
- The gates' side is US-DLV-43; the reviewer's side and the docs are TASK-DLV-04 and TASK-DEF-06.

## Open questions

- None. The marker's rules are fixed by DEF-R47 and DEF-R48.
