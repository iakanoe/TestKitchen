---
id: TASK-DEF-07
type: task
title: Mark the adopted review-only criteria
epic: EP-DEF
source_reqs: [DEF-R48]
blocked_by: [US-DEF-34, TASK-DEF-06]
owner: Ianick Noejovich
assignee_type: either
status: draft
---

Add `(review)` to the live criteria of adopted `done` stories that only reading can check, so that `--test-debt` lists only debt a test can pay.

## Acceptance criteria

- AC1: Every live criterion of an adopted `done` story that only reading can check carries `(review)`, each added after the person's yes (in batches per epic), and `python3 scripts/backlog_check.py --test-debt` no longer lists them.

## Notes

- The owner estimated about 150 of the 636 `DEBT` lines on 2026-11-26 are review-only.
- Adding the marker to an adopted done story is the second allowed edit to a done ticket (DEF-R48); nothing else in those tickets changes.
- The person decides each marker: the agent proposes a batch per epic, with each criterion's text, at a define checkpoint.

## Open questions

- None. The marker's rules are fixed by DEF-R48.
