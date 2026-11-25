---
id: US-DEF-24
type: story
title: Sweep gaps and refine tickets
epic: EP-DEF
source_reqs: [DEF-R34, DEF-R27]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person getting the backlog ready, I want gaps closed one by one and tickets reviewed before they are ready, so that delivery only picks clear, testable, owned tickets.

## Acceptance criteria

- AC1: Given mode `sweep`, when the agent runs, then it runs `backlog_check.py --gaps` and closes each line with the action the playbook's gap table names, the lines blocking most work first.
- AC2: Given a sweep, when `--gaps` prints nothing or the person stops, then the agent stops and reports what is left.
- AC3: Given mode `refine`, when the agent runs, then it runs `backlog_check.py --refine` and handles each finding with the person.
- AC4: Given a ready or draft ticket in `refine`, when the agent reviews it, then the reviewer runs in `ticket` mode in a fresh context with only the inputs `playbooks/review.md` lists, and criteria changes need the person's yes.
- AC5: Given a reviewed ticket with no CRITICAL left and every WARNING settled, when refinement ends, then the agent sets `refined:` to today, and the checkpoint that proposes `ready` asks for the owner.
- AC6: Given a refined ticket whose criteria or open questions change later, when the agent changes it, then the ticket is reviewed again and gets a new date.

## Notes

- Adopted 2026-11-25 from existing behavior: playbook behavior (`playbooks/define.md`): an agent following it does this, so its criteria are verified by review, not by tests; in Claude Code the reviewer is the `ticket-reviewer` subagent.
- The criteria describe what happens now; confirmation happens on the cited `(observed in code)` requirements.

## Open questions

- None. This story records behavior that already exists; anything that looks unintended is filed as a decision on the epic.
