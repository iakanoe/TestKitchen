---
id: US-DLV-24
type: story
title: Start, plan, question, review the plan, and claim
epic: EP-DLV
source_reqs: [DLV-R32]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As an agent delivering a ticket, I want the first five steps to set up the branch, a reviewed plan, and a visible claim, so that the work starts from the recorded criteria and others see the ticket is taken.

## Acceptance criteria

- AC1: Given a clean checkout with no unmerged work, when step 1 starts, then the agent switches to the up-to-date default branch, creates the branch named like the ticket file lowercased, runs `deliver.py context <ID>`, installs dependencies as `AGENTS.md` says, and reads the ADRs, the project rules, recent decision-log entries about neighboring tickets, and the code it builds on.
- AC2: Given the ticket, when step 2 plans, then the agent writes the `pr-body` skeleton to a file outside the repository or in an ignored path, never adds or drops a plan row, fills each row with the allowed, denied, limit, and empty cases (access rules tested at the enforcing interface), and lists files, data changes, interfaces, user-visible parts, and `Constrained by:`.
- AC3: Given open points, when step 3 sorts them, then the person decides, in one round with a recommendation each, every unsettled user-visible rule, criterion depending on an unfinished ticket, or ambiguous criterion (behavior changes are drafted as criterion changes and need a yes), while plumbing, names, required texts, and limits an ADR leaves open are the agent's choices, logged at capture.
- AC4: Given a plan, when step 4 reviews it, then the agent runs the reviewer in `plan` mode, fixes every CRITICAL and reruns until none is left, fixes or files every WARNING, and under autonomy `supervised` waits for a person's approval recorded as `Plan approved by: <name>`.
- AC5: Given a reviewed plan, when step 5 claims the ticket, then the agent sets `status: in-progress`, commits `chore: start <ID>`, pushes the branch, and opens a draft change request with the body file; on the manual host the pushed branch is the claim.

## Notes

Adopted 2026-11-25 from `playbooks/deliver.md`; the criteria describe what the document says now and are not yet confirmed by a person. Playbook behavior is followed by agents and people, so it is verified by review, not by tests.

## Open questions

- None. Adopted behavior.
