---
id: US-DEF-21
type: story
title: Write only after a yes, and apply decisions in one pass
epic: EP-DEF
source_reqs: [DEF-R30, DEF-R31]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person defining a product, I want to see exactly what will be written and have each decision applied everywhere at once, so that the record matches what I approved.

## Acceptance criteria

- AC1: Given the end of a topic, when the agent reaches the checkpoint, then it shows each file, section, and text it will write, and writes only after a yes that covers exactly what was shown.
- AC2: Given a checkpoint with requirements and proposed stories, when the person says yes to the requirements and no to the stories, then the requirements are written and the stories are not, leaving their requirements listed as uncovered.
- AC3: Given a change to behavior a `done` ticket records, when the agent proposes it, then it proposes a new ticket and leaves the done ticket unchanged.
- AC4: Given a checkpoint that proposes `ready`, when the agent presents it, then it asks who owns each ticket.
- AC5: Given an answered decision, when the agent applies it, then it updates, in order, the requirement or ADR, the affected criteria (removed ones kept as dated placeholders) and tickets, the epic's `## Open` line, the DEC's `## Outcome` and status, the unblocked tickets' `blocked_by` and open questions, and the decision log.
- AC6: Given the decision log, when the agent adds an entry, then it is a `### YYYY-MM-DD — <title>` heading, newest first, with Decision, Why, Decided by, and Recorded in, never renamed later, a replaced entry getting a `Superseded by:` line, and `backlog_check.py` exits 0 afterwards.

## Notes

- Adopted 2026-11-25 from existing behavior: playbook behavior (`playbooks/define.md`): an agent following it does this, so its criteria are verified by review, not by tests.
- The criteria describe what happens now; confirmation happens on the cited `(observed in code)` requirements.

## Open questions

- None. This story records behavior that already exists; anything that looks unintended is filed as a decision on the epic.
