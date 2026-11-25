---
id: US-DLV-32
type: story
title: Keep the ground rules of delivery
epic: EP-DLV
source_reqs: [DLV-R40]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person relying on agents, I want delivery to follow fixed ground rules, so that facts, gates, decisions, and records never depend on an agent's memory or convenience.

## Acceptance criteria

- AC1: Given a criterion, requirement, ticket status, or check result to state, when the agent states it, then it has read it in this session from a file or a script's output, and it quotes the text when the text matters to a choice.
- AC2: Given a gate that prints FAIL, when the agent continues, then it fixes the cause and reruns the gate, never rewording, skipping, or working around it.
- AC3: Given a DEC option, a criterion change, a `docs/` change, or a platform setting change, when it arises, then a person decides, and code meeting an open DEC fails closed until it is decided.
- AC4: Given a gap, decision, or platform change, when the ticket finishes, then each is filed as a ticket or a decision-log entry and listed in the change request.
- AC5: Given the work, when the agent works, then it stays in this checkout on the ticket's branch, never creating another folder or worktree and never switching away from uncommitted or unmerged work.
- AC6: Given credentials, tokens, keys, or sign-in links, when the agent records anything, then none of them is recorded.

## Notes

Adopted 2026-11-25 from `playbooks/deliver.md`; the criteria describe what the document says now and are not yet confirmed by a person. Playbook behavior is followed by agents and people, so it is verified by review, not by tests. Where `backlog/README.md` or the project rules in `AGENTS.md` disagree with the playbook, they win and the disagreement is a gap to file.

## Open questions

- None. Adopted behavior.
