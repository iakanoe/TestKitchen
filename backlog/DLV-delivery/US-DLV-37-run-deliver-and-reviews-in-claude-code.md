---
id: US-DLV-37
type: story
title: Run /deliver and reviews in Claude Code
epic: EP-DLV
source_reqs: [DLV-R46, DLV-R47]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person using Claude Code, I want `/deliver` and the reviewer to be thin wrappers over the playbooks that add only Claude Code mechanics, so that the process is the same in every agent.

## Acceptance criteria

- AC1: Given `/deliver` with a ticket ID, `next`, no argument, or `all`, when the skill runs, then it delivers that ticket, the ticket `deliver.py next` names, or repeats until nothing is ready and the hand-off leaves nothing to do, after reading `playbooks/deliver.md`, `CONTRIBUTING.md`, `AGENTS.md`, and `backlog/README.md` in full, and keeps a task list of the playbook's steps.
- AC2: Given a review step, when the skill runs it, then it uses the `ticket-reviewer` subagent with only the inputs `playbooks/review.md` lists for the mode.
- AC3: Given open questions, when the skill asks them, then it asks all in one AskUserQuestion round, one question per decision, with the recommendation as the first option marked "(recommended)" and context the options cannot hold written before the call.
- AC4: Given `NEXT none`, a guard denial, the session's model, or a headless run, when the skill meets it, then it hands off through `/define`, treats a guard denial as final, sets no model of its own, and in a headless run prints the questions or decision briefs and stops.
- AC5: Given the `ticket-reviewer` agent, when it is started, then it has only the Read, Grep, Glob, and Bash tools, follows `playbooks/review.md` in the mode it was given using only the inputs given, stays read-only, and ends with the closing lines the playbook gives for that mode, exactly.

## Notes

Adopted 2026-11-25 from `.claude/skills/deliver/SKILL.md` and `.claude/agents/ticket-reviewer.md`; the criteria describe what the document says now and are not yet confirmed by a person. Playbook behavior is followed by agents and people, so it is verified by review, not by tests.

## Open questions

- None. Adopted behavior.
