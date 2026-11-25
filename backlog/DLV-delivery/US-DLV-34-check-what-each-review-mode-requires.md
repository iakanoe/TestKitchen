---
id: US-DLV-34
type: story
title: Check what each review mode requires
epic: EP-DLV
source_reqs: [DLV-R43]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a reviewer, I want each mode to list exactly what it checks, so that plan, tests, diff, and ticket reviews are complete and comparable.

## Acceptance criteria

- AC1: Given `plan` mode, when the reviewer reviews, then for each live criterion it checks the plan has tests for the allowed case, the denied case, every named limit and empty state, and access rules at the enforcing interface, and it checks exactly one row per live criterion, no scope beyond the criteria (CRITICAL), every open user-visible choice listed, fail-closed handling of open DECs, and `Constrained by:` naming the ADRs and DECs without contradiction.
- AC2: Given `tests` mode, when the reviewer reviews, then it checks each test carries a live criterion's tag, would fail without the behavior, asserts the result a user or caller sees, and is not skipped or focused, runs `deliver.py gate red <ID>` to confirm each failure is the missing behavior, and reports criteria or named cases with no test that can fail.
- AC3: Given `diff` mode, when the reviewer reviews, then it reports under Completeness, Correctness (including repeated requests, concurrent use, and failure paths), Coherence (ADRs, project rules, marked fail-closed DEC seams, no scope beyond criteria, justified frozen-test changes), and Capture (filed gaps, decisions, and platform changes, comments, README updates, every to-do style marker naming a ticket), with any unfiled item CRITICAL.
- AC4: Given `ticket` mode, when the reviewer reviews, then it checks ambiguity, testability, missing denied, limit, or empty cases, scope creep, overlap with other tickets or DECs, size over `split_threshold`, and form against `backlog/README.md` (and, with `self_contained_tickets: true`, no repository paths, links, or document names).

## Notes

Adopted 2026-11-25 from `playbooks/review.md`; the criteria describe what the document says now and are not yet confirmed by a person. Playbook behavior is followed by agents and people, so it is verified by review, not by tests.

## Open questions

- None. Adopted behavior.
