---
id: US-GRD-11
type: story
title: Ask after a cd the guard cannot follow
epic: EP-GRD
source_reqs: [GRD-R32]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: ready
refined: 2026-11-26
---

As a project owner, I want the guard to ask about writes after a `cd` it cannot follow, so that a write to a protected path after one of them never goes through unasked.

## Acceptance criteria

- AC1: Given `cd -` earlier in a call (`cd /tmp && cd - && echo x > kitchen.yml`), when a later command in the call writes a file, then the guard asks.
- AC2: Given `popd` earlier in a call (`pushd /tmp && popd && echo x > kitchen.yml`), when a later command in the call writes a file, then the guard asks.
- AC3: Given a `cd` inside a subshell `( … )` or a group `{ …; }` earlier in a call (`(cd /tmp) && echo x > kitchen.yml`), when a later command in the call writes a file, then the guard asks.
- AC4: Given a `cd` inside a script run by `sh`, `bash`, `zsh`, `dash`, or `ksh` with `-c`, or in a command substitution `$(cd …)` or backticks, earlier in a call (`sh -c 'cd /tmp' && echo x > kitchen.yml`), when a later command in the call writes a file, then the guard asks.
- AC5: Given a `cd` in a pipeline stage earlier in a call (`cd /tmp | true && echo x > kitchen.yml`), when a later command in the call writes a file, then the guard asks.

## Notes

- Implements DEC-GRD-01, option (a), decided 2026-11-25 by Ianick Noejovich, as widened on 2026-11-26 to `-c` scripts and pipeline stages (GRD-R32 supersedes GRD-R26). It changes the behavior recorded by US-GRD-09, which stays as the record of the earlier behavior.
- US-GRD-09/AC4 keeps resolving writes after a `cd` to a folder known before the call runs, and allowing those that are not protected.
- Only later writes change: a write before the `cd -`, `popd`, or inner `cd` is still judged against the folder known at that point (US-GRD-09/AC4), so `echo x > notes.txt && (cd /tmp)` stays allowed.
- Replaces no criterion: US-GRD-09/AC4 already asks after a `cd` to a folder known only at run time, and no criterion says where a write after `cd -`, `popd`, or an inner `cd` resolves.

## Open questions

- None. The decision log records this decision, and the widening of 2026-11-26 added the `-c` and pipeline cases.
