---
id: US-GRD-12
type: story
title: Ask about git config only for the config subcommand
epic: EP-GRD
source_reqs: [GRD-R27]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: draft
---

As a project owner, I want git setting changes to ask only for `git config` itself, so that a file or folder named `config` does not trigger a prompt.

## Acceptance criteria

- AC1: Given `git add config`, `git diff -- config`, or `git log -- config`, when the guard checks it, then it does not ask as a git setting change.
- AC2: Given `git config <key> <value>` or `git -C . config <key> <value>`, when the guard checks it, then it asks as a git setting change.

## Notes

Implements DEC-GRD-02, option (a), decided 2026-11-25 by Ianick Noejovich. It changes the behavior recorded by US-GRD-07, which stays as the record of the earlier behavior. Other checks on the same command (protected paths, aliases) are unchanged.

## Open questions

- None.
