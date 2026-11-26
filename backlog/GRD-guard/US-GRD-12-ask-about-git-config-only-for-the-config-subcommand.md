---
id: US-GRD-12
type: story
title: Ask about git config only for the config subcommand
epic: EP-GRD
source_reqs: [GRD-R27]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: ready
refined: 2026-11-26
---

As a project owner, I want git setting changes to ask only for `git config` itself, so that a file or folder named `config` does not trigger a prompt.

## Acceptance criteria

- AC1: Given `git add config`, `git diff -- config`, or `git log -- config`, when the guard checks it, then it does not ask with the git setting change reason ("This is a git setting change …").
- AC2: Given `config` as the value of one of git's global options (`git -C config status`, `git --git-dir config log`), when the guard checks it, then it does not ask with the git setting change reason.

## Notes

- Implements DEC-GRD-02, option (a), decided 2026-11-25 by Ianick Noejovich. It changes the behavior recorded by US-GRD-07, which stays as the record of the earlier behavior.
- US-GRD-07/AC1 keeps every `git config` write asking, `git -C <folder> config …` included. The other asks of GRD-R16 (`git -c`, `git --config-env`, and `GIT_*` assignments, US-GRD-07/AC2) and the alias asks (US-GRD-07/AC3, AC4) stay as they are; a command may still ask for one of those reasons.
- Replaces no criterion: no criterion of US-GRD-07 says that a `config` file name asks.

## Open questions

- None. The decision log records this decision.
