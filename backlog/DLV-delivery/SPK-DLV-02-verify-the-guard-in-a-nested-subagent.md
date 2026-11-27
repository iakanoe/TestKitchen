---
id: SPK-DLV-02
type: spike
title: Verify the guard in a nested subagent
epic: EP-DLV
source_reqs: []
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: in-progress
---

## Goal

Find out whether the guard hook (`.claude/hooks/guard.py`) runs on the tool calls of a subagent started by another subagent, as the reviewer would be when TASK-DLV-03 runs each ticket in its own subagent.

## Context

- Documented on code.claude.com (hooks and sub-agents pages, checked 2026-11-26): `PreToolUse` hooks from project settings run on a subagent's tool calls, and the hook input carries `agent_id` and `agent_type`. The pages read did not say whether this holds for a nested subagent.
- Subagents may start subagents up to three levels deep by default (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`).
- Documented (sub-agents page): background subagents surface every permission prompt in the main session. Not documented: what a hook that returns "ask" does inside a subagent.

## Done when

- A subagent started by another subagent is asked to run a command the guard denies, and Findings record what happened and the Claude Code version.
- A subagent, in the foreground and in the background, is asked for an edit the guard answers with "ask" (a protected path), and Findings record whether the person is asked in the main session.
- If the guard does not run there, a DEC on how TASK-DLV-03 runs its reviews is filed; otherwise Findings say TASK-DLV-03 can proceed.

## Findings
