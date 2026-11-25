---
id: US-DLV-35
type: story
title: Grade and close the review report
epic: EP-DLV
source_reqs: [DLV-R44]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As an agent and a gate reading reviews, I want findings graded by one severity scale and the report to end with fixed lines, so that `gate pr` can read the outcome and people can act on each finding.

## Acceptance criteria

- AC1: Given a finding, when the reviewer grades it, then CRITICAL means the work cannot move on until it is fixed, WARNING means it may ship only if fixed or filed with a recorded justification, and SUGGESTION is optional, with the examples `playbooks/review.md` gives for each.
- AC2: Given findings, when the reviewer writes the report, then it lists them most severe first, each with severity, location (file and line, or criterion), what is wrong in one sentence, and the evidence, followed by what it could not check.
- AC3: Given any mode, when the reviewer ends the report, then the last line is exactly `CRITICAL: n, WARNING: n, SUGGESTION: n`; in `diff` mode it is preceded by `Reviewed commit: <full sha from git rev-parse HEAD in the reviewed checkout>`.

## Notes

Adopted 2026-11-25 from `playbooks/review.md`; the criteria describe what the document says now and are not yet confirmed by a person. Playbook behavior is followed by agents and people, so it is verified by review, not by tests.

## Open questions

- None. Adopted behavior.
