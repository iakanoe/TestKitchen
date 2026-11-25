---
id: US-GRD-14
type: story
title: Ask before writes the guard cannot see
epic: EP-GRD
source_reqs: [GRD-R29, GRD-R30]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: draft
---

As a project owner, I want the guard to ask before commands whose targets it cannot read and before the decision log is deleted or truncated, so that these mistakes reach a person.

## Acceptance criteria

- AC1: Given a project with protected files, when a call runs `git apply`, `patch`, or `git reset --hard`, then the guard asks.
- AC2: Given a shell command that deletes `docs/decision-log.md`, when the guard checks it, then it asks.
- AC3: Given a shell command that truncates `docs/decision-log.md` (such as a `>` redirect to it), when the guard checks it, then it asks.
- AC4: Given a shell command that appends to `docs/decision-log.md` with `>>`, or an edit of it, when the guard checks it, then the guard allows it.

## Notes

Implements DEC-GRD-04, option (a), decided 2026-11-25 by Ianick Noejovich (its first two parts; US-GRD-15 holds the third). It changes the behavior recorded by US-GRD-08 (protected edits) and US-GRD-09 (shell writes), which stay as the record of the earlier behavior.

## Open questions

- None.
