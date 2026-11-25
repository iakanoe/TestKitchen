---
id: US-INST-24
type: story
title: Follow the agent install instructions
epic: EP-INST
source_reqs: [INST-R29]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a developer who asks an AI agent to install Test Kitchen, I want the agent to follow fixed instructions that ask me before writing, so that nothing is installed from guesses I never confirmed.

## Acceptance criteria

- AC1: Given `AGENT-INSTALL.md`, when an agent follows it, then it works at the repository root, tells the person about a missing git repository or uncommitted changes, checks Python, PyYAML, and git without installing packages unasked, and switches to `update --dry-run` when a `kitchen.lock` exists.
- AC2: Given the repository, when the agent forms its guesses, then each of the three answers and the host has a stated reason, and it runs a dry run with `--yes` and the guesses.
- AC3: Given the guesses and the plan, when the agent asks the person, then one message holds the three questions with guesses and reasons, the host when unsure, the `--no-claude` choice, and the dry run's plan, and no unconfirmed guess is used as an answer.
- AC4: Given confirmed answers, when the agent installs, then it runs `init.py` with `--yes` and the answers, runs `doctor`, and reports the files created, the side-by-side copies, every `FAIL` and `WARN` with its fix, the toolchain step's state, and that nothing was committed.
- AC5: Given the install is done, when the agent offers more, then it only offers to draft the `## This project` section of `AGENTS.md` and to run `/define` (`adopt` for existing code, `new` otherwise), and writes only after the person's yes.

## Notes

Observed in `AGENT-INSTALL.md` on 2026-11-25 by `/define adopt`; not yet confirmed by a person. These are instructions an agent follows, so no automated test can prove them. The file states that an agent's shell has no terminal; DEC-INST-03 asks whether that claim should stand.

## Open questions

- None. Behavior recorded as observed; the person confirms it.
