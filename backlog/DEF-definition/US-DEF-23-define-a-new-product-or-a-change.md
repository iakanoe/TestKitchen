---
id: US-DEF-23
type: story
title: Define a new product or a change
epic: EP-DEF
source_reqs: [DEF-R33]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person starting a product or changing one, I want a guided path for each, so that the definition grows in the same order every time.

## Acceptance criteria

- AC1: Given mode `new`, when the agent starts, then it asks exactly the playbook's opening question about who uses the product, what problem it solves, and what it looks like when it works.
- AC2: Given the person's description, when the agent continues `new`, then it drafts the vision in the person's words for a checkpoint and works down the layers with question rounds, turning each architecture choice into an ADR when made and a DEC when open.
- AC3: Given the requirements of `new` are written, when the agent proposes tickets, then it writes them as `draft` on a yes, refines them, offers the `AGENTS.md` project section and `slice`, and continues as `sweep`.
- AC4: Given mode `change`, when the agent starts, then it restates the change in one sentence for confirmation and finds the product sections, requirements, ADRs, DECs, and tickets it touches.
- AC5: Given a confirmed change, when the agent reaches the checkpoint, then it proposes the new or superseded requirements, any ADR or DEC, and the ticket changes: unfinished tickets get removed criteria as placeholders and new ones appended, done tickets stay and the change becomes a new ticket, and tickets citing a superseded requirement are updated.
- AC6: Given a yes to a change, when the agent applies it, then it logs the decision, runs `backlog_check.py`, and refines the tickets it changed.

## Notes

- Adopted 2026-11-25 from existing behavior: playbook behavior (`playbooks/define.md`): an agent following it does this, so its criteria are verified by review, not by tests.
- The criteria describe what happens now; confirmation happens on the cited `(observed in code)` requirements.

## Open questions

- None. This story records behavior that already exists; anything that looks unintended is filed as a decision on the epic.
