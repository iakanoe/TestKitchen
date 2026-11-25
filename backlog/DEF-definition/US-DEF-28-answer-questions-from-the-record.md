---
id: US-DEF-28
type: story
title: Answer questions from the record
epic: EP-DEF
source_reqs: [DEF-R38]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person asking what the product does or must do, I want answers taken only from the repository, so that I can trust where each answer comes from.

## Acceptance criteria

- AC1: Given mode `ask`, when the agent answers, then it writes nothing.
- AC2: Given a question the definition covers, when the agent answers, then it cites each source by file and ID and keeps its qualifiers (observed in code, superseded, proposal, open).
- AC3: Given a question nothing in the repository covers, when the agent answers, then it says "not defined in this repo", offers to open a DEC or SPK, and does not answer from general knowledge.

## Notes

- Adopted 2026-11-25 from existing behavior: playbook behavior (`playbooks/define.md`): an agent following it does this, so its criteria are verified by review, not by tests.
- The criteria describe what happens now; confirmation happens on the cited `(observed in code)` requirements.

## Open questions

- None. This story records behavior that already exists; anything that looks unintended is filed as a decision on the epic.
