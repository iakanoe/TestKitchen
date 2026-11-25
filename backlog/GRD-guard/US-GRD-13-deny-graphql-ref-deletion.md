---
id: US-GRD-13
type: story
title: Deny GraphQL ref deletion
epic: EP-GRD
source_reqs: [GRD-R28]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: draft
---

As a project owner, I want a GraphQL ref deletion refused like the REST one, so that sandbox mode cannot delete a branch on the host.

## Acceptance criteria

- AC1: Given a `gh api graphql` call with the `deleteRef` mutation, when the guard checks it, then it is denied.
- AC2: Given the same call with `KITCHEN_GUARD_SANDBOX=1`, when the guard checks it, then it is still denied.
- AC3: Given a `gh api graphql` call with the `updatePullRequestBranch` mutation, when the guard checks it, then it asks as a host API call that may write and is not denied.

## Notes

Implements DEC-GRD-03, option (a), decided 2026-11-25 by Ianick Noejovich; option (b), denying `updatePullRequestBranch`, was not chosen. GitHub's GraphQL reference lists `deleteRef` ("Delete a Git Ref."), https://docs.github.com/en/graphql/reference/git, checked 2026-11-25. It changes the behavior recorded by US-GRD-06, which stays as the record of the earlier behavior.

## Open questions

- None.
