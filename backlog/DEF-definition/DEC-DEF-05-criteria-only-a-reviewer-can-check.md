---
id: DEC-DEF-05
type: decision
title: Criteria only a reviewer can check
epic: EP-DEF
source_reqs: [DEF-R14, DLV-R37]
blocked_by: []
owner: Ianick Noejovich
assignee_type: human
status: done
---

## Question

How should a criterion that only a reviewer can check (the wording of a playbook, a guide, or an instruction file) be accepted, when a `done` story needs a tagged test for every live criterion?

## Context

- A `done` story needs a tagged test for every live criterion (DEF-R14); an adopted story's untagged criteria are test debt instead.
- An untestable task skips the failing-tests step, and the final reviewer confirms each criterion (DLV-R37).
- On 2026-11-26 three documentation-only stories became tasks for that reason (decision log, "Review-only stories become tasks": US-INST-26, US-DEF-31, and US-DEF-32 became TASK-INST-03, TASK-DEF-02, and TASK-DEF-03).
- About 150 adopted criteria can only be checked by reading (the owner's estimate on 2026-11-26); they count as test debt (`backlog_check.py --test-debt`) although no test can pay it.

## Options

- (a) Keep using tasks for review-only work, as decided on 2026-11-26; the adopted review-only criteria stay test debt.
- (b) A `(review)` marker at the start of a criterion: such a criterion needs no tagged test, and the gate requires the final review to name it as checked.
- (c) Text tests: tests that read the file and assert the wording, tagged like any other test.

All three were named by the owner on 2026-11-26; none is recorded in `docs/` yet.

## Recommendation

(b), proposed by the owner: it keeps review-only criteria in the stories they belong to, and it would also clear the review-only adopted criteria from test debt.

## Decides

No ticket waits on it.

## Outcome

2026-11-27: option (b), the `(review)` marker, decided by Ianick Noejovich. Recorded in DEF-R47, DEF-R48, DLV-R56, DLV-R57, DLV-R58 and the decision log ("Review-only criteria carry a (review) marker"); built by US-DEF-34, US-DLV-43, TASK-DLV-04, TASK-DEF-06, and TASK-DEF-07.
