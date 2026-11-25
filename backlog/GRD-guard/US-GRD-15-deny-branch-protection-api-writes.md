---
id: US-GRD-15
type: story
title: Deny branch-protection API writes
epic: EP-GRD
source_reqs: [GRD-R31]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: draft
---

As a project owner, I want host API calls that change branch protection refused, so that sandbox mode cannot weaken the protection that holds against everything else.

## Acceptance criteria

- AC1: Given a `gh api` or `glab api` call that writes branch protection, when the guard checks it, then it is denied.
- AC2: Given the same call with `KITCHEN_GUARD_SANDBOX=1`, when the guard checks it, then it is still denied.
- AC3: Given a `gh api` or `glab api` call that only reads branch protection, when the guard checks it, then this rule does not deny it.

## Notes

Implements DEC-GRD-04, option (a), decided 2026-11-25 by Ianick Noejovich (its third part; US-GRD-14 holds the other two). It changes the behavior recorded by US-GRD-06 (host CLI and API calls), which stays as the record of the earlier behavior.

## Open questions

- None.
