---
id: US-DLV-04
type: story
title: Print the change-request skeleton
epic: EP-DLV
source_reqs: [DLV-R06]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As an agent delivering a ticket, I want `deliver.py pr-body` to print the description skeleton with one plan row per live criterion, so that every criterion is planned and every section the gates read exists.

## Acceptance criteria

- AC1: Given a story or task, when `deliver.py pr-body <ID>` runs, then the Ticket section names the ID, title, cited requirements, and status (adding `Hotfix.` for a hotfix), and the Plan section is a `Criterion | Tests` table with one empty row per live criterion followed by `Constrained by:`.
- AC2: Given any ticket, when `deliver.py pr-body <ID>` runs, then it prints the sections Ticket, Plan, Gaps found (`- None`), Decisions (`- None`), Platform changes (`- None`), Test changes (`None`), Review report, and Checks, in that order.
- AC3: Given a ticket that is not a story or task, when `deliver.py pr-body <ID>` runs, then the Ticket section is `None. Delivers <ID> <title>.` and the Plan section is `None.`.
- AC4: Given autonomy `supervised`, when `deliver.py pr-body <ID>` runs, then the Plan ends with empty `Plan approved by:` and `Tests approved by:` lines.
- AC5: Given a `hotfix: true` ticket, when `deliver.py pr-body <ID>` runs, then the Decisions section holds a comment saying to replace `None` with the reason for the hotfix lane ending `Log: <decision-log entry title>`, and to name the follow-up ticket under Gaps found.

## Notes

Adopted 2026-11-25 from `template/scripts/deliver.py` (installed copy `scripts/deliver.py`); the criteria describe what the code does now and are not yet confirmed by a person.

## Open questions

- None. Adopted behavior; the wording of the Ticket line for spikes and decisions is asked separately in this epic's open decisions.
