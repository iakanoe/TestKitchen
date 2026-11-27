---
id: SPK-DLV-02
type: spike
title: Verify the guard in a nested subagent
epic: EP-DLV
source_reqs: []
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
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

Run on 2026-11-27 with Claude Code 2.1.331 (the desktop app, recorded in the transcripts; `claude --version` on the same machine prints 2.1.308), in the auto permission mode, from a session in this repository with the guard registered in `.claude/settings.json` and no `KITCHEN_GUARD_SANDBOX`.

- **Denials hold in nested subagents.** A general-purpose subagent (spawn depth 1, background) and a subagent it started (spawn depth 2, foreground) each ran `git -C /nonexistent-guard-probe push origin HEAD` once. At both depths the guard denied it with its message "`git -C` can't run in a call that merges or pushes …", as their transcripts record (subagent metadata `spawnDepth` 1 and 2). Nothing was pushed. The command was chosen so that, had the guard not run, git would have failed on the missing folder instead.
- **Asks from a subagent do not reach the person in auto mode.** The same two depths each made one Edit to `docs/product.md`, a protected path. Run by hand on the same input, the guard answers `ask` ("docs/product.md is a definition, guardrail, process, or instruction file; a person approves changes to it first."). Neither call reached the person: each transcript records `"permissionDecision":{"decision":"accept","source":"config","reasonType":"classifier"}`, so auto mode's classifier approved it, at depth 1 (background) and depth 2 (foreground). The edits changed nothing only because their old text was not in the file. In the same session, the four Edit calls to protected `docs/` files made from the main conversation each record `"source":"user_temporary"`: the person was asked and approved them.
- **Not tested:** other permission modes, and a depth-1 foreground subagent (the Agent tool here starts depth-1 subagents in the background). The guard does not read the hook input's `agent_id` today.
- **For TASK-DLV-03:** the guard runs on a nested subagent's calls, so its denials hold for a reviewer started by a ticket's subagent. But in auto mode a ticket subagent's protected edits and `init.py update` would be approved by the classifier, not the person, which breaks GRD-R19 and GRD-R22's "asks". Filed as DEC-GRD-05, which now blocks TASK-DLV-03.
