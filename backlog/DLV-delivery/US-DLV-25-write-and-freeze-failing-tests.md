---
id: US-DLV-25
type: story
title: Write and freeze the failing tests
epic: EP-DLV
source_reqs: [DLV-R33]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As an agent delivering a ticket, I want step 6 to prove the missing behavior with tagged failing tests before any code and freeze them, so that tests come from the criteria rather than from the code.

## Acceptance criteria

- AC1: Given the live criteria, when step 6 writes tests, then every test proves a criterion through the interfaces users and callers use and carries its tag in either form (`[<ID>/AC<n>]` or the lowercase identifier form), with at least one per live criterion.
- AC2: Given the tests, when `deliver.py gate red <ID>` runs, then it must print PASS, and the agent reads each failure to confirm it is the missing behavior, with tests failing one by one rather than at load or compile time.
- AC3: Given passing `gate red`, when the tests are reviewed, then the agent runs the reviewer in `tests` mode, fixes its findings and reruns `gate red`, and under autonomy `supervised` waits for approval recorded as `Tests approved by: <name>`.
- AC4: Given reviewed tests, when the agent freezes them, then it commits only test files with exactly `test: <ID> failing tests`, once per branch, and afterwards changes a frozen test only where it contradicts the ticket or an accepted ADR, listing it under Test changes, never removing a criterion's tagged tests or adding skipped or focused tests.

## Notes

Adopted 2026-11-25 from `playbooks/deliver.md`; the criteria describe what the document says now and are not yet confirmed by a person. Playbook behavior is followed by agents and people, so it is verified by review, not by tests.

## Open questions

- None. Adopted behavior.
