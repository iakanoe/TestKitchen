---
id: US-DLV-10
type: story
title: Match the branch, plan, and ticket status in gate pr
epic: EP-DLV
source_reqs: [DLV-R14, DLV-R16]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a maintainer, I want `gate pr` to check that a ticket change request is on the ticket's branch, plans every live criterion, and finishes the ticket, so that nothing merges half planned or half done without saying so.

## Acceptance criteria

- AC1: Given a branch that follows the workflow (claim, freeze, implementation, done, record, review), when `deliver.py gate pr` runs, then it prints `PASS pr: <ID>` and exits 0.
- AC2: Given a branch whose name is not the ticket's file name lowercased, when `deliver.py gate pr` runs, then it fails saying the branch is not the ticket's file name.
- AC3: Given a Plan with no row naming `<ID>/AC<n>` for a live criterion, when `deliver.py gate pr` runs, then it fails with `Plan has no row for <ID>/AC<n>`, and a row for criterion 10 does not count as a row for criterion 1.
- AC4: Given a ticket that is not `done` and is not explained as staying in progress, when `deliver.py gate pr` runs, then it fails saying to set it to done or say why it stays in-progress and name the ticket that holds the rest.
- AC5: Given an `in-progress` ticket whose Ticket section says `in-progress` and names another ticket, when `deliver.py gate pr` runs, then the status check passes.

## Notes

Adopted 2026-11-25 from `template/scripts/deliver.py` (installed copy `scripts/deliver.py`); the criteria describe what the code does now and are not yet confirmed by a person. The ticket, its live criteria, and `kitchen.yml` are read from the working tree, not from `--head`; this epic's open decisions ask whether that is intended.

## Open questions

- None. Adopted behavior; whether the ticket files should be read at `--head` is asked separately in this epic's open decisions.
