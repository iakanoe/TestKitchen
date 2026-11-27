---
id: US-GRD-17
type: story
title: Deny in a subagent what the guard would ask
epic: EP-GRD
source_reqs: [GRD-R36]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: draft
---

As a person who approves changes to protected files, I want the guard to deny, instead of asking, a protected change made in a subagent, so that the change comes back to the main session where I am the one asked, whatever the permission mode.

## Acceptance criteria

- AC1: Given an Edit to a protected path (such as `docs/product.md`) with a non-empty `agent_id` in the hook input and no sandbox mode, when the guard runs, then it denies the call, and its reason names the path, says a person approves changes to it, and tells the subagent to hand the step back to the main session.
- AC2: Given a shell command that writes a protected path, with a non-empty `agent_id` and no sandbox mode, when the guard runs, then it denies the call with the same kind of reason.
- AC3: Given the same calls with no `agent_id`, or an empty one, when the guard runs, then it asks as before.
- AC4: Given `KITCHEN_GUARD_SANDBOX=1` and a call with a non-empty `agent_id` that would otherwise ask (not a force push), when the guard runs, then it lets the call through.
- AC5: Given `KITCHEN_GUARD_SANDBOX=1`, a non-empty `agent_id`, and a force push, when the guard runs, then it denies the call.
- AC6: Given a call with a non-empty `agent_id` that the guard allows or denies today, when the guard runs, then its decision is unchanged.

## Notes

- Decided 2026-11-27 (DEC-GRD-05 outcome; decision log, "The guard denies in a subagent what it would ask").
- Evidence: SPK-DLV-02 found that in auto mode (Claude Code 2.1.331, desktop app) the guard's asks from a subagent, at depth 1 and depth 2, were approved by the classifier, while the main conversation's asks reached the person. Run by hand, the guard asks about none of the normal delivery steps (`init.py update`, commits, plain pushes of the ticket's branch, the `gh pr` steps, the gates and `record`, edits to `template/`, `tests/`, `backlog/`, `guide/`, `CHANGELOG.md`, the decision log), so this deny falls only on steps that need the person anyway.
- Documented on code.claude.com (hooks page, checked 2026-11-26): the hook input of a subagent's call carries `agent_id` and `agent_type`. `agent_type` alone is also set in sessions started with `--agent`, so it does not trigger this rule.
- GRD-R36 narrows, without contradicting, the done criteria US-GRD-08/AC1, AC4, AC5, US-GRD-09/AC1 to AC4, and US-GRD-10/AC4: they describe calls without an `agent_id`, which their tests send none of (decision log, "The guard denies in a subagent what it would ask").
- The code is `template/claude/hooks/guard.py`; the root copy `.claude/hooks/guard.py` changes only through `init.py update`.

## Open questions

- None. The rule is fixed by GRD-R36.
