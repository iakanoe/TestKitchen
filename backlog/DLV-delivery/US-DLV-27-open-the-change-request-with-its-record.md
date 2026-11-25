---
id: US-DLV-27
type: story
title: Open the change request with its record
epic: EP-DLV
source_reqs: [DLV-R35]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As an agent delivering a ticket, I want step 11 to fill the description, commit its record, and pass the description and delivery gates before marking the change request ready, so that the evidence is complete and kept in the repository.

## Acceptance criteria

- AC1: Given the body file, when step 11 fills it, then Ticket starts with the ticket ID (or `None. …`, or says why the ticket stays in progress and names the ticket holding the rest), Plan is the reviewed plan with any approvals, Gaps found names the ticket holding each gap, Decisions and Platform changes end each bullet with `Log: <entry title>` or name a done decision, Test changes lists changed tests with reasons, Review report holds every finding of every review ending with the final two closing lines quoted exactly, and Checks gives the check result, the `gate red` result, and what was tried by hand.
- AC2: Given a filled body file, when the agent publishes it, then it runs `deliver.py record`, commits `docs: delivery record`, runs `backlog_check.py --pr-body` and `deliver.py gate pr`, pushes, updates the description, and marks the change request ready (on GitLab, before the final push).
- AC3: Given the description is edited after the record, when the agent continues, then it reruns `record` and commits again; a record of another change request at the same path makes `record` write a `-cr<number>` file, and on the manual host `--cr` is left out unless `record` asks for it.
- AC4: Given a commit message or description that mentions a merge or push, when the agent commits or publishes it, then it writes the text to a file first (`git commit -F <file>`, a body file).

## Notes

Adopted 2026-11-25 from `playbooks/deliver.md`; the criteria describe what the document says now and are not yet confirmed by a person. Playbook behavior is followed by agents and people, so it is verified by review, not by tests. The host commands for each action are listed in the playbook's "Host commands" table (host epic).

## Open questions

- None. Adopted behavior.
