---
id: US-DLV-40
type: story
title: Print the playbook's Ticket line for spikes and decisions
epic: EP-DLV
source_reqs: [DLV-R50]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: draft
---

As an agent delivering a spike or a decision, I want the change-request skeleton to carry the Ticket line the playbook asks for, so that I do not have to rewrite it.

## Acceptance criteria

- AC1: Given a spike, when `deliver.py pr-body <ID>` runs, then the Ticket line starts `None. Spike <ID>: ` and the Plan is `None.`.
- AC2: Given a decision, when `deliver.py pr-body <ID>` runs, then the Ticket line starts `None. Decides <ID>` and the Plan is `None.`.
- AC3: Given an epic, when `deliver.py pr-body <ID>` runs, then it is refused with a message that an epic is not delivered, and no skeleton is printed.

## Notes

Implements DEC-DLV-03, option (b), decided 2026-11-25 by Ianick Noejovich. It changes the skeleton recorded by US-DLV-04, which stays as the record of the earlier behavior; the story and task skeleton, supervised approval lines, and hotfix comment stay as US-DLV-04 records. US-DLV-29 records the playbook's spike and decision variants, which already ask for these lines.

## Open questions

- None.
