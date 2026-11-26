---
id: US-DLV-40
type: story
title: Print the playbook's Ticket line for spikes and decisions
epic: EP-DLV
source_reqs: [DLV-R50]
blocked_by: [US-DEF-33]
owner: Ianick Noejovich
assignee_type: either
status: ready
refined: 2026-11-26
---

As an agent delivering a spike or a decision, I want the change-request skeleton to carry the Ticket line the playbook asks for, so that I do not have to rewrite it.

## Acceptance criteria

- AC1: Given a spike, when `deliver.py pr-body <ID>` runs, then the Ticket section starts `None. Spike <ID>: ` and the Plan section starts `None.`.
- AC2: Given a decision, when `deliver.py pr-body <ID>` runs, then the Ticket section starts `None. Decides <ID>` and the Plan section starts `None.`.
- AC3: Given an epic, when `deliver.py pr-body <ID>` runs, then it prints a `FAIL` line saying that an epic is not delivered, prints no skeleton, and exits 1.
- AC4: Given a story, task, spike, or decision, when `deliver.py pr-body <ID>` runs, then it prints the sections Ticket, Plan, Gaps found (`- None`), Decisions (`- None`), Platform changes (`- None`), Test changes (`None`), Review report, and Checks, in that order.
- AC5: Given autonomy `supervised` and a story, task, spike, or decision, when `deliver.py pr-body <ID>` runs, then the Plan section ends with empty `Plan approved by:` and `Tests approved by:` lines.

## Notes

- Implements DEC-DLV-03, option (b), decided 2026-11-25 by Ianick Noejovich. The story and task skeleton (US-DLV-04/AC1) and the hotfix comment (US-DLV-04/AC5) stay as US-DLV-04 records them. US-DLV-29 records the playbook's spike and decision variants, which already ask for these lines.
- Replaces (to become a `replaces:` field once US-DEF-33 is delivered): US-DLV-04/AC3 (`None. Delivers <ID> <title>.` for every ticket that is not a story or task), and US-DLV-04/AC2 and US-DLV-04/AC4, which promise a skeleton for any ticket, epics included. AC4 and AC5 restate what those two say for the types that are still delivered, because that part stays true and must not lose its criterion when they are crossed out.
- A `FAIL <message>` line and exit 1 is how `pr-body` already refuses an ID that names no ticket (US-DLV-22/AC3).

## Open questions

- None. The decision log records this decision.
