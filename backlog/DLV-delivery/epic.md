---
id: EP-DLV
type: epic
title: Delivery
owner: Ianick Noejovich
assignee_type: either
status: ready
code: ["template/scripts/deliver.py"]
---

Delivery takes a ready ticket to merged, verified work under deterministic gates. It covers `deliver.py` (picking the next ticket and handing off to define, a ticket's context, the change-request skeleton, `gate red` with JUnit parsing, delivery records, `gate pr`, `gate merge`, the merge command, `check`, `status`, release notes, and the self-test), the `/deliver` process in `playbooks/deliver.md` (14 steps, variants, autonomy levels, the manual host, and when to stop and ask), the fresh-context reviewer in `playbooks/review.md`, `CONTRIBUTING.md`, and the Claude Code wrappers `.claude/skills/deliver/SKILL.md` and `.claude/agents/ticket-reviewer.md`.

## Boundaries

- Host adapters (how `gh` and `glab` are called, how a change request's state and checks are read, the exact merge command each host allows) and the CI templates belong to the host epic; this epic only uses what the adapter reports.
- The Claude Code guard (which commands and edits it allows, asks about, or refuses, and when it runs `gate merge`) belongs to the guard epic.
- Ticket format, the backlog check, and `--pr-body` description rules belong to the backlog epic; `gate merge` and the playbook only call them.
- The definition process (`playbooks/define.md`, `/define`) belongs to the define epic; delivery only hands off to it.

## Open

- SPK-DLV-01, SPK-DLV-02.
