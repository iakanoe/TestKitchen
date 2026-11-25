---
id: US-DLV-29
type: story
title: Deliver tasks, fixes, hotfixes, spikes, decisions, and other changes
epic: EP-DLV
source_reqs: [DLV-R37]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As an agent delivering work that is not a plain story, I want each variant to say which steps change, so that every kind of change goes through the gates that fit it.

## Acceptance criteria

- AC1: Given a task, when it is delivered, then a testable task follows all 14 steps including step 6, an untestable task skips step 6 with each plan row saying how its criterion is shown to be met and the final reviewer confirming each, and a partly testable task is a stop to propose a split.
- AC2: Given a story with `fixes:`, when it is delivered, then its first test reproduces the bug on the current code, is tagged with the fix story's criterion (and may also carry the broken criterion's tag), and commits are named `fix: <ID> …`.
- AC3: Given a `hotfix: true` story, when it is delivered, then steps 3 and 4 are skipped and everything else runs, with a Decisions bullet ending `Log: <the hotfix entry's title>` and the follow-up task named under Gaps found.
- AC4: Given a spike, when it is delivered, then the agent creates and claims its branch, investigates read-only unless the spike allows otherwise, records findings, proposes any requirement change to the person instead of applying it, files follow-ups, sets it done, and opens a change request whose Ticket starts `None. Spike …`, with a record, merged as in step 12.
- AC5: Given a decision, when it is delivered, then the agent presents it in define's decision format with a recommendation, never picks an option, applies the drafted changes after a yes on the branch `docs/<decision file name lowercased>`, and opens a change request whose Ticket starts `None. Decides …` with a Decisions bullet ending `Log: <entry title>`, a record, and a merge as in step 12.
- AC6: Given a change with no behavior to accept, when it is delivered, then it uses a `fix/`, `chore/`, or `docs/` branch with Ticket starting `None. …`, commits its record, passes the checks, gets a final review when it touches code or tests, and shows any `docs/` change to the person first; a change in behavior always has a ticket.

## Notes

Adopted 2026-11-25 from `playbooks/deliver.md`; the criteria describe what the document says now and are not yet confirmed by a person. Playbook behavior is followed by agents and people, so it is verified by review, not by tests.

## Open questions

- None. Adopted behavior.
