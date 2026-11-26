---
id: SPK-DLV-02
type: spike
title: Verify the guard in a nested subagent
epic: EP-DLV
source_reqs: []
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: draft
---

## Goal

Find out whether the guard hook (`.claude/hooks/guard.py`) runs on the tool calls of a subagent started by another subagent, as the reviewer would be when US-DLV-42 runs each ticket in its own subagent.

## Context

- Documented on code.claude.com (hooks and sub-agents pages, checked 2026-11-26): `PreToolUse` hooks from project settings run on a subagent's tool calls, and the hook input carries `agent_id` and `agent_type`. The pages read did not say whether this holds for a nested subagent.
- Subagents may start subagents up to three levels deep by default (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`).

## Done when

- A subagent started by another subagent is asked to run a command the guard denies, and Findings record what happened and the Claude Code version.
- If the guard does not run there, a DEC on how US-DLV-42 runs its reviews is filed; otherwise Findings say US-DLV-42 can proceed.

## Findings
