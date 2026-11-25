---
id: US-DLV-06
type: story
title: Judge the failing tests in gate red
epic: EP-DLV
source_reqs: [DLV-R08, DLV-R09]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As an agent or reviewer, I want `gate red` to pass only when every live criterion has a tagged test that ran and failed, so that tests are proven to need the missing behavior before any code is written.

## Acceptance criteria

- AC1: Given a JUnit report, when `deliver.py gate red <ID>` reads it, then a test case with a `failure` or `error` element counts as failed, one with `skipped` as skipped, and any other as passed, a tag in either the test name or the class name counts, and each tagged test's result is printed.
- AC2: Given every live criterion has at least one tagged test that ran and at least one that failed, when `deliver.py gate red <ID>` runs, then it prints `PASS red: every live criterion of <ID> has a failing tagged test` and exits 0.
- AC3: Given a live criterion whose tagged tests all pass, when `deliver.py gate red <ID>` runs, then it prints `FAIL AC<n>: every tagged test already passes, so none proves the missing behavior` and exits 1.
- AC4: Given a live criterion with no tagged test in the report, or only skipped ones, when `deliver.py gate red <ID>` runs, then it prints `FAIL AC<n>: no tagged test ran` (adding `(only skipped ones)` when skipped) and exits 1.
- AC5: Given a task whose tags appear in no test file, when `deliver.py gate red <ID>` runs, then it prints that gate red does not apply and exits 0; given a spike, decision, or epic, it fails because the gate applies to stories and tasks.
- AC6: Given a story or task with tagged test files but no live criteria, when `deliver.py gate red <ID>` runs, then it fails with `<ID> has no live criteria`.

## Notes

Adopted 2026-11-25 from `template/scripts/deliver.py` (installed copy `scripts/deliver.py`); the criteria describe what the code does now and are not yet confirmed by a person.

## Open questions

- None. Adopted behavior.
