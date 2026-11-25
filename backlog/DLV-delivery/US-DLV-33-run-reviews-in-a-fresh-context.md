---
id: US-DLV-33
type: story
title: Run reviews in a fresh context with only their inputs
epic: EP-DLV
source_reqs: [DLV-R41, DLV-R42]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person relying on reviews, I want each review to run in a fresh context with only the inputs its mode lists, so that the reviewer judges the work against the ticket and not against the author's reasoning.

## Acceptance criteria

- AC1: Given a review in delivery, when the agent runs it, then it uses a fresh context (the `ticket-reviewer` subagent in Claude Code, a new session or agent given `playbooks/review.md` elsewhere) and passes only the mode, the repository path, the ticket path, the accepted ADR paths, each related DEC with its status, and the plan text, test file paths, or diff range `origin/<default>...HEAD`, never its reasoning or expectations.
- AC2: Given a review report, when the agent continues, then the report goes into the change request as it is, with what was done about each finding.
- AC3: Given a reviewer, when it reviews, then it stays read-only, using the shell only for `git diff`, `git log`, `git show`, `git rev-parse`, `grep`, the project's test command, `deliver.py context`, `deliver.py gate red`, and `backlog_check.py`.
- AC4: Given a mode, when the reviewer starts, then it receives exactly the inputs `playbooks/review.md` lists for that mode (for `ticket` mode: the ticket and epic paths, the other tickets in the epic and those citing the same requirements, `split_threshold`, and `self_contained_tickets`), says in the report which input is missing, and reads the ticket, its cited requirements via `context`, the ADRs, `backlog/README.md`, and (outside `ticket` mode) the project rules.
- AC5: Given the work under review, when the reviewer judges it, then only the ticket's live criteria, cited requirements, and accepted ADRs are requirements, and it reports only what it checked and says what it could not check.

## Notes

Adopted 2026-11-25 from `playbooks/deliver.md` ("Reviews") and `playbooks/review.md`; the criteria describe what the document says now and are not yet confirmed by a person. Playbook behavior is followed by agents and people, so it is verified by review, not by tests.

## Open questions

- None. Adopted behavior.
