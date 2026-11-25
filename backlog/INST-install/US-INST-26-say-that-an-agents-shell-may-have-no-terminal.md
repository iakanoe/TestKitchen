---
id: US-INST-26
type: story
title: Say that an agent's shell may have no terminal
epic: EP-INST
source_reqs: [INST-R33]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: draft
---

As an agent installing Test Kitchen, I want `AGENT-INSTALL.md` to state only what holds in every agent, so that I always pass `--yes` without relying on an unchecked claim about my shell.

## Acceptance criteria

- AC1: Given `AGENT-INSTALL.md`, when an agent reads its instruction about the terminal, then it says the shell may have no terminal for the installer to ask on and to always pass `--yes`.
- AC2: Given `AGENT-INSTALL.md`, when it is read, then no sentence states as fact that the agent's shell has no terminal.

## Notes

Implements DEC-INST-03, option (a), decided 2026-11-25 by Ianick Noejovich. It changes the instructions recorded by US-INST-24, which stays as the record of the earlier wording. A reviewer checks these criteria; no test can.

## Open questions

- None.
