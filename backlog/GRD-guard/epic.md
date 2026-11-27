---
id: EP-GRD
type: epic
title: Merge guard
owner: Ianick Noejovich
assignee_type: either
status: ready
code: ["template/claude/hooks/guard.py"]
---

The Claude Code hook that runs before every shell command and file edit in an installed project and turns the workflow's hardest rules into allow, ask, or deny decisions: pushes only in the one plain shape, merges only through the host adapter's exact command after the merge gate (and never on the manual host or under autonomy `pr` or `supervised`), host CLI and API calls limited to reads and the workflow's steps, git configuration, aliases, and tokens put before a person, and edits to the definition, process, guardrail, and framework files asked about first. It fails closed. Requirements: `docs/requirements/GRD-guard.md`.

## Boundaries

- Claude Code only. Other agents follow the playbooks and run the merge gate themselves; nothing local enforces the rules there.
- Not a sandbox: it reads commands literally, so text assembled at run time (variables that build a command, a script written and then run, a build-tool target, the content of a patch file) is out of its reach. Host branch protection is what holds against everything.
- It decides only; it never runs the guarded command and never writes to the project (it reads git, `kitchen.yml`, `kitchen.lock`, and the project's scripts, and runs the merge gate).
- The merge gate's checks belong to the delivery scripts, and what each host's merge command is belongs to the host adapter; the guard only enforces that the gate passes and that the command matches.
- What a person or a headless run does with an ask (a prompt, or a refusal in `claude -p`) is Claude Code's behavior, not the guard's.

## Open

- DEC-GRD-05.
