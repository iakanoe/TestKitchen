---
id: US-DLV-36
type: story
title: Explain the process in CONTRIBUTING.md
epic: EP-DLV
source_reqs: [DLV-R45]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person or agent contributing, I want `CONTRIBUTING.md` to explain why the process looks as it does, what enforces each rule, and how to run it, so that I can trust and operate the workflow without reading the scripts.

## Acceptance criteria

- AC1: Given `CONTRIBUTING.md`, when a contributor opens it, then it points to `playbooks/define.md`, `playbooks/deliver.md`, and `playbooks/review.md` with what each covers, to `backlog/README.md` for ticket rules, and to the `## This project` section of `AGENTS.md` for project rules.
- AC2: Given its principles section, when a contributor reads it, then it states: one ticket per branch and change request; tests first; agents never decide; nothing stays only in chat; fresh-context reviews; facts come from scripts; nothing merges on red.
- AC3: Given its enforcement section, when a contributor reads it, then each enforced rule names what enforces it (`backlog_check.py`, `--pr-body`, `gate red`, `gate pr`, `gate merge`, or the guard), and it explains the guard, what the guard cannot see, and the sandbox opt-in.
- AC4: Given its stop-and-ask section, when a contributor reads it, then it summarizes when an agent stops and asks and points to the full list in `playbooks/deliver.md`.
- AC5: Given its running section, when a contributor reads it, then it explains running the workflow in Claude Code (commands, no model set, unattended runs), in another agent (follow the playbooks, fresh reviews, run `gate merge` and only the printed merge command), and by hand (approving the plan and tests in place of the reviewer).
- AC6: Given its setup section, when a contributor reads it, then it lists Python 3.9 or later with PyYAML, git, the signed-in host CLI, the project's toolchain, merge commits allowed on the host (and GitLab merged results pipelines off), optionally Claude Code, and `deliver.py check` to confirm the setup.

## Notes

Adopted 2026-11-25 from `CONTRIBUTING.md`; the criteria describe what the document says now and are not yet confirmed by a person. Playbook behavior is followed by agents and people, so it is verified by review, not by tests. The guard's exact rules belong to the guard epic.

## Open questions

- None. Adopted behavior.
