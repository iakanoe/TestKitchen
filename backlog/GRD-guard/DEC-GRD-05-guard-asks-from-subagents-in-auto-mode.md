---
id: DEC-GRD-05
type: decision
title: Guard asks from subagents in auto mode
epic: EP-GRD
source_reqs: [GRD-R19, GRD-R22]
blocked_by: []
owner: Ianick Noejovich
assignee_type: human
status: done
---

## Question

When a subagent's tool call gets the guard's "ask", Claude Code in auto mode lets its classifier approve the call instead of the person. How should the guard keep "a person approves" for calls made in subagents?

## Context

- Found by SPK-DLV-02 on 2026-11-27 (Claude Code 2.1.331, desktop app, auto permission mode): the guard's denials hold in a subagent and in a nested one, but its asks for protected edits from a subagent (depth 1 background, depth 2 foreground) were accepted with `"source":"config","reasonType":"classifier"`. The same session's protected edits from the main conversation were approved by the person (`"source":"user_temporary"`). Other permission modes were not tested.
- GRD-R19 and GRD-R22 say an edit or a shell write to a protected path asks, so that a person approves it.
- Documented (code.claude.com, hooks page, checked 2026-11-26): the hook input of a subagent's call carries `agent_id` and `agent_type`; `agent_type` is also set in sessions started with `--agent`. The guard reads neither today.
- TASK-DLV-03 runs each ticket of `/deliver all` in a subagent, where protected edits and `init.py update` would happen; it is blocked by this DEC.

## Options

None recorded. Proposals:

- (a) The guard denies, instead of asking, when the hook input carries an `agent_id`, with a reason telling the subagent to hand the step back to the main session, where the ask reaches the person.
  - For: holds in every permission mode without depending on a setting, and fails closed, as undecided cases do.
  - Against: it relies on `agent_id` being present only in subagent calls, which the docs describe but do not promise; a subagent that does need a protected edit hands it back to the main session. (Corrected 2026-11-27: an earlier version said a ticket's subagent could no longer run `init.py update`; run by hand, the guard allows it, along with every other normal delivery step.)
- (b) Document that subagent-based delivery needs a permission mode in which a subagent's asks reach the person, after a spike checks which modes do.
  - For: no guard change, and protected edits stay inside the ticket's subagent.
  - Against: the guarantee depends on each person's setting, and the guard silently weakens for anyone using auto mode.
- (c) Accept the classifier's approval for calls made in subagents.
  - For: no work and no extra hand-offs.
  - Against: breaks GRD-R19 and GRD-R22's promise that a person approves changes to protected files whenever work runs in a subagent.

## Recommendation

(a): it keeps the guarantee in every mode and fails closed; the hand-offs it adds are the price of a person approving each protected change.

## Decides

TASK-DLV-03 (blocked by this DEC). On (a), a guard story; on (b), a spike on permission modes and a `CONTRIBUTING.md` change; nothing on (c).

## Outcome

2026-11-27: option (a), with sandbox mode unchanged, decided by Ianick Noejovich. Recorded in GRD-R36 and the decision log ("The guard denies in a subagent what it would ask"); built by US-GRD-17.
