---
id: US-DLV-42
type: story
title: Deliver each ticket of /deliver all in a fresh context
epic: EP-DLV
source_reqs: [DLV-R52, DLV-R53, DLV-R54]
blocked_by: [SPK-DLV-02]
owner: Ianick Noejovich
assignee_type: either
status: draft
---

As a person running `/deliver all`, I want each ticket delivered in a fresh context, so that later tickets don't carry earlier tickets' context and cost.

## Acceptance criteria

- AC1: Given `/deliver all` in an agent that can start a fresh context, when the playbook delivers a ticket, then it delivers it in a fresh context (a subagent or a new session) and the next ticket starts from the repository, not from the previous ticket's context.
- AC2: Given `/deliver all` in an agent that cannot start a fresh context, when the playbook runs, then it delivers the tickets one after another in the same session.
- AC3: Given `/deliver all` in Claude Code, when the skill delivers a ticket, then it starts one subagent for that ticket, which follows `playbooks/deliver.md` for that ticket only and runs its reviews through the `ticket-reviewer` subagent.
- AC4: Given a question that needs the person inside a ticket's subagent, when the subagent reaches it, then it commits and pushes its work and returns the question; the main session asks it in one AskUserQuestion round and passes the answers back to that ticket's subagent, or, headless, prints it and stops.
- AC5: Given `/deliver <ID>` or `/deliver next`, when the skill runs, then it delivers in the current session, without a ticket subagent.
- AC6: Given the `/deliver` and `/define` skills, when they say how to read the playbooks and rule files, then they say to use the file-read tool, one file per call, never combined with other commands.

## Notes

- Measured on the US-DLV-38 delivery run (2026-11-26, in the desktop app): about 2.37M effective tokens; the context reached 254k tokens on that one ticket, so a second ticket in the same session would start there. A combined `cat playbooks/deliver.md && deliver.py next` call overflowed into a saved file that was then read a second time.
- Documented on code.claude.com (sub-agents and hooks pages, checked 2026-11-26): a subagent starts with a fresh context and may start subagents up to three levels deep; `PreToolUse` hooks from project settings run on a subagent's tool calls, with `agent_id` and `agent_type` in the hook input; `AskUserQuestion` is always removed from subagents. Not found in the docs read: whether hooks run on a nested subagent's calls (SPK-DLV-02).
- Candidate, not decided: a dedicated agent file for the ticket worker, or a general-purpose subagent given the skill.
- US-DLV-37/AC1 is not contradicted: `/deliver all` still repeats until nothing is ready, and each ticket's subagent reads the playbooks in full.

## Open questions

- Whether the guard runs on the tool calls of the reviewer a ticket's subagent starts: SPK-DLV-02 (in `blocked_by`).
