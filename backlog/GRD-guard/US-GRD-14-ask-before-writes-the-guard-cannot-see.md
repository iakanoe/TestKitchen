---
id: US-GRD-14
type: story
title: Ask before writes the guard cannot see
epic: EP-GRD
source_reqs: [GRD-R33]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: ready
refined: 2026-11-26
---

As a project owner, I want the guard to ask before commands whose targets it cannot read, so that a patch or a hard reset that changes protected files reaches a person.

## Acceptance criteria

- AC1: Given any project, with or without a `kitchen.lock`, when a call runs `git apply <patch>`, `patch` (such as `patch -p1 < fix.diff`), or `git reset --hard`, then the guard asks.
- AC2: Given `git apply` with `--check`, `--stat`, or `--numstat` and without `--apply`, or `patch --dry-run`, when the guard checks it, then this rule does not ask; with `--apply` added (`git apply --stat --apply fix.diff`), it asks.

## Notes

- Implements DEC-GRD-04, option (a), decided 2026-11-25 by Ianick Noejovich (its first part), as made exact on 2026-11-26 (GRD-R33 supersedes GRD-R29: every project, and the forms that do not write stay allowed). US-GRD-16 holds the decision-log part and US-GRD-15 the branch-protection part. It changes the behavior recorded by US-GRD-09, which stays as the record of the earlier behavior.
- Git's documentation marks `--check`, `--stat`, and `--numstat` (and `--summary`) as "Turns off apply", and says `--apply` given after them also applies the patch: https://git-scm.com/docs/git-apply, checked 2026-11-26. `--summary` is not among the decided forms, so it asks.
- Replaces no criterion: US-GRD-09's Notes, not its criteria, put `git apply` and `patch` out of reach.

## Open questions

- None. The decision log records this decision, and the decisions of 2026-11-26 settled which projects and which forms.
