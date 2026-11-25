---
id: DEC-GRD-03
type: decision
title: GraphQL ref deletion only asks
epic: EP-GRD
source_reqs: [GRD-R14]
blocked_by: []
owner: Ianick Noejovich
assignee_type: human
status: done
---

## Question

Is this intended? A REST call that writes a git ref is denied, but a GraphQL `deleteRef` mutation through `gh api graphql` only asks, so in sandbox mode it goes through without a prompt.

## Context

- Current behavior (verified on 2026-11-25 by feeding the hook JSON in a scratch project built like `tests/test_guard.py` does):
  - `gh api -X DELETE repos/o/r/git/refs/heads/x` is denied ("This host API call merges or moves a branch …").
  - `gh api graphql -f query='mutation { deleteRef(input: {refId: "x"}) { clientMutationId } }'` asks ("This is a host API call that may write"); with `KITCHEN_GUARD_SANDBOX=1` that ask passes.
  - `updatePullRequestBranch` (which updates a change request's branch on the host) also only asks.
- Evidence: `template/claude/hooks/guard.py:1005-1007` (`MERGE_API`) lists `mergePullRequest`, `enablePullRequestAutoMerge`, `mergeBranch`, `updateRef`/`updateRefs`, `createRef`, and `createCommitOnBranch`, but not `deleteRef`; `guard.py:1090-1097` denies only what `MERGE_API` matches.
- Likely intended: the decision-log entry "Guard hardening after the adversarial review" says "Host API calls that merge, write refs, or commit to a branch are refused, sandbox mode included". Deleting a ref is a ref write, and the REST form of it is already refused.
- GitHub's GraphQL reference lists `deleteRef` ("Delete a Git Ref."), `createRef`, `updateRef`, and `updateRefs` (https://docs.github.com/en/graphql/reference/git, checked 2026-11-25). That `updatePullRequestBranch` exists is not yet checked there.

## Options

None recorded. Proposals:

- (a) Add `deleteRef` (after checking GitHub's GraphQL reference for any other ref-writing mutation) to the denied mutations.
- (b) Also deny `updatePullRequestBranch`, since it moves a branch on the host outside `git push`.
- (c) Keep asking for both: a person or the sandbox opt-in decides.

## Recommendation

(a), and decide (b) with it: (a) brings the GraphQL path in line with the recorded decision and the REST path; (b) is a judgment call, because updating a change request's branch from its base is a step a person may want agents to take.

## Decides

US-GRD-06 (its host API criteria and notes). A change to the guard would be a new story in this epic.

## Outcome

- Date: 2026-11-25.
- Answer: Option (a): the GraphQL `deleteRef` mutation is denied like REST ref writes; `updatePullRequestBranch` is not denied (option (b) was not chosen) and still asks.
- Decided by: Ianick Noejovich.
- Recorded in: requirements GRD-R28; confirmed GRD-R14; US-GRD-13; decision log, "The guard denies GraphQL deleteRef".
