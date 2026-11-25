---
id: US-DEF-22
type: story
title: Define layer by layer and split requirements
epic: EP-DEF
source_reqs: [DEF-R32]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person defining a product, I want it defined from vision down to tickets and each requirement split into tickets the same way, so that every ticket traces back to what I confirmed.

## Acceptance criteria

- AC1: Given a product to define, when the agent works, then it goes through vision, users and roles, capabilities, boundaries, requirements, architecture, and stories and tasks in that order, going back up when a lower layer shows a gap.
- AC2: Given a new capability, when the agent proposes its epic, then the code (one capital, then one to nine capitals or digits) is chosen with the person and names the epic, its folder, its requirements file, and every ID in it.
- AC3: Given a requirement whose meaning changes, when the agent records it, then the old line is marked superseded with the date and the new ID and a new requirement takes the next free number, while a wording fix is an edit and no ID is reused.
- AC4: Given a requirement to split, when the agent proposes tickets, then it becomes a story, a task, or a constraint cited by a story, with criteria taken only from the requirement text and proposals kept in Notes.
- AC5: Given a gap found while splitting, when the agent records it, then it becomes an open question naming a DEC or SPK, never a criterion.
- AC6: Given a story with more live criteria than `split_threshold`, when the agent proposes it, then it proposes a split along a seam a user would notice (per role, action, or data state).

## Notes

- Adopted 2026-11-25 from existing behavior: playbook behavior (`playbooks/define.md`): an agent following it does this, so its criteria are verified by review, not by tests.
- The criteria describe what happens now; confirmation happens on the cited `(observed in code)` requirements.

## Open questions

- None. This story records behavior that already exists; anything that looks unintended is filed as a decision on the epic.
