---
id: TASK-DEF-01
type: task
title: "Pay test debt: tagged tests for EP-DEF"
epic: EP-DEF
source_reqs: []
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: draft
---

The adopted criteria of EP-DEF are proven today only by untagged tests in files that carry the no-trace marker, or only by review, so `--test-debt` lists them all. This task adds tagged tests in new test files that hold no example tickets, so each criterion a test can check is proven by a test the backlog check counts.

## Acceptance criteria

- AC1: Every adopted criterion of EP-DEF that a test can check has a tagged test in a test file without the no-trace marker.
- AC2: python3 scripts/backlog_check.py --test-debt lists only criteria that only a review can check.

## Notes

The adopt notes for EP-DEF map each criterion to the untagged tests that prove it today, or say that none does or that only a review can.

## Open questions

- None.
