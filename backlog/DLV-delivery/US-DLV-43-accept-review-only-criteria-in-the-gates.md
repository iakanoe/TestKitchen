---
id: US-DLV-43
type: story
title: Accept review-only criteria in the gates
epic: EP-DLV
source_reqs: [DLV-R56, DLV-R57]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: deferred
replaces: [US-DLV-06/AC2, US-DLV-06/AC4]
---

As a person delivering a ticket, I want the gates to skip tests for `(review)` criteria and require the final review to name each one as checked, so that review-only criteria are accepted by name instead of by a test that cannot exist.

## Acceptance criteria

- AC1: Given every live criterion not marked `(review)` has at least one tagged test that ran and at least one that failed, when `deliver.py gate red <ID>` runs, then it prints `PASS red: every live criterion of <ID> has a failing tagged test`, names each `(review)` criterion it skipped, and exits 0.
- AC2: Given a live criterion not marked `(review)` with no tagged test in the report, or only skipped ones, when `deliver.py gate red <ID>` runs, then it prints `FAIL AC<n>: no tagged test ran` (adding `(only skipped ones)` when skipped) and exits 1.
- AC3: Given a ticket change request whose ticket has a live `(review)` criterion and whose review report has no line `Checked by review: <ID>/AC<n>` for it, when `deliver.py gate pr` runs, then it prints `FAIL Review report: <ID>/AC<n> is not checked by review` and exits 1.
- AC4: Given a ticket change request whose review report has a `Checked by review: <ID>/AC<n>` line for every live `(review)` criterion of the ticket, when `deliver.py gate pr` runs, then its review check passes as before.

## Notes

- Retired 2026-11-27: DEC-DEF-05 reversed (decision log, "Review-only work stays in untestable tasks"); this ID is never reused.
- Decided 2026-11-27 (DEC-DEF-05, option (b); decision log, "Review-only criteria carry a (review) marker").
- Replaces US-DLV-06/AC2 and AC4 (shown to the owner and approved on 2026-11-27): each becomes the same rule with `(review)` criteria left out. They are crossed out when this story is delivered.
- `backlog_check.py`'s side is US-DEF-34; the reviewer writes the `Checked by review:` lines (TASK-DLV-04).

## Open questions

- None. The gate rules are fixed by DLV-R56 and DLV-R57.
