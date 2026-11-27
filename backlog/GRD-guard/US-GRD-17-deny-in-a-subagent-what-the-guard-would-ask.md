---
id: US-GRD-17
type: story
title: Deny in a subagent what the guard would ask
epic: EP-GRD
source_reqs: [GRD-R36]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
refined: 2026-11-27
---

As a person who approves what the guard asks about, I want the guard to deny, instead of asking, a call made in a subagent that it would ask about, so that the step comes back to the main session where I am the one asked, whatever the permission mode.

## Acceptance criteria

- AC1: Given an `agent_id` that is present and not null or an empty string (a non-string value such as a number or `{}` counts), sandbox mode off (`KITCHEN_GUARD_SANDBOX` unset or not exactly `1`), and a call the guard would ask about (a protected edit with Edit, Write, MultiEdit, or NotebookEdit; a shell write to a protected path or one it cannot resolve; a force push; a host command or host API call that may write; a git setting, alias, `-c`, or `GIT_*` variable; or any other ask), when the guard runs, then it denies the call.
- AC2: Given a call AC1 or AC5 denies, when the guard reports it, then the reason contains every reason the ask would have given, without repeats and in the ask's order, and tells the subagent to hand the step back to the main session, where the person is asked.
- AC3: Given the calls of AC1 with no `agent_id`, a null one, an empty one, or with `agent_type` set and no `agent_id`, when the guard runs, then it asks as before.
- AC4: Given `KITCHEN_GUARD_SANDBOX=1` and a call that would otherwise ask (not a force push), with an `agent_id` that is present and not null or an empty string, when the guard runs, then it lets the call through.
- AC5: Given `KITCHEN_GUARD_SANDBOX=1`, an `agent_id` that is present and not null or an empty string, and a force push, when the guard runs, then it denies the call.
- AC6: Given a call with an `agent_id` that is present and not null or an empty string, when the guard runs and the same call without an `agent_id` would be allowed or denied, then its decision is that same allow or deny.

## Notes

- Decided 2026-11-27 (DEC-GRD-05 outcome; decision log, "The guard denies in a subagent what it would ask").
- Evidence: SPK-DLV-02 found that in auto mode (Claude Code 2.1.331, desktop app) the guard's asks from a subagent, at depth 1 and depth 2, were approved by the classifier, while the main conversation's asks reached the person. Run by hand, the guard asks about none of the normal delivery steps (`init.py update`, commits, plain branch pushes, the `gh pr` steps, the gates and `record`, edits to `template/`, `tests/`, `backlog/`, `guide/`, `CHANGELOG.md`, the decision log), so this deny falls only on steps that need the person anyway.
- How `agent_id` is read (decided 2026-11-27; decision log, "How the guard reads agent_id"): absent, null, or an empty string means a main-session call; any other value, including a number, an object, or whitespace, counts as a subagent's call. This fails closed for asks without breaking the main session if Claude Code ever sends a null `agent_id` there, which has not been verified either way.
- Documented on code.claude.com (hooks page, checked 2026-11-26): the hook input of a subagent's call carries `agent_id` and `agent_type`. `agent_type` alone is also set in sessions started with `--agent`, so it does not trigger this rule (AC3).
- GRD-R36 narrows, without contradicting, the done criteria US-GRD-08/AC1, AC4, AC5, US-GRD-09/AC1 to AC4, and US-GRD-10/AC4: they describe calls without an `agent_id`, which their tests send none of (decision log, "The guard denies in a subagent what it would ask").
- AC1 to AC3 were reworded in place on 2026-11-27, during refinement and before any test, code, or change request cited them, rather than removed and renumbered.
- The code is `template/claude/hooks/guard.py`; the root copy `.claude/hooks/guard.py` changes only through `init.py update`.

## Open questions

- None. The rule is fixed by GRD-R36, and the reading of `agent_id` by the decision log entry above.
