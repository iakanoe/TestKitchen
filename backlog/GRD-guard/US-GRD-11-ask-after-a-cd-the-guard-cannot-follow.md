---
id: US-GRD-11
type: story
title: Ask after a cd the guard cannot follow
epic: EP-GRD
source_reqs: [GRD-R26]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: draft
---

As a project owner, I want the guard to ask about writes after `cd -`, `popd`, or a `cd` inside a subshell or group, so that a write to a protected path after one of them never goes through unasked.

## Acceptance criteria

- AC1: Given `cd -` earlier in a call, when a later command in the call writes a file, then the guard asks.
- AC2: Given `popd` earlier in a call, when a later command in the call writes a file, then the guard asks.
- AC3: Given a `cd` inside a subshell `( … )` or a group `{ …; }`, when a later command in the call writes a file, then the guard asks.
- AC4: Given a call whose only folder changes are `cd` to folders known before it runs, when a command writes a path that is not protected, then the guard allows it.

## Notes

Implements DEC-GRD-01, option (a), decided 2026-11-25 by Ianick Noejovich. Examples from the DEC: `cd /tmp && cd - && echo x > kitchen.yml`, `pushd /tmp && popd && echo x > kitchen.yml`, and `(cd /tmp) && echo x > kitchen.yml` each ask. It changes the behavior recorded by US-GRD-09, which stays as the record of the earlier behavior.

## Open questions

- None.
