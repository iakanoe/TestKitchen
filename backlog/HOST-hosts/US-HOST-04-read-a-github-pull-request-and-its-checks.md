---
id: US-HOST-04
type: story
title: Read a GitHub pull request and its checks
epic: EP-HOST
source_reqs: [HOST-R07, HOST-R08, HOST-R09]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As the merge gate, I want a GitHub pull request in the host-neutral change-request shape with its checks as pass, fail, pending, or skipped, so that I can decide whether it may merge the same way on every host.

## Acceptance criteria

- AC1: Given an open, non-draft, mergeable pull request, when it is read, then `gh pr view <n> --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeable,body,statusCheckRollup,url` is the only call, and the change request carries its number, state "open", draft false, base branch, head branch, head sha, mergeable true, body, and url.
- AC2: Given a pull request in state MERGED or CLOSED, or with mergeable CONFLICTING or UNKNOWN, when it is read, then its state is "merged" or "closed" and its mergeability is false for CONFLICTING and unknown for any value other than MERGEABLE.
- AC3: Given check runs in the rollup, when the pull request is read, then a run not yet COMPLETED is pending, conclusion SUCCESS passes, SKIPPED or NEUTRAL is skipped, and any other conclusion (such as CANCELLED or TIMED_OUT) fails.
- AC4: Given commit statuses in the rollup, when the pull request is read, then SUCCESS passes, PENDING or EXPECTED is pending, and any other state (such as ERROR) fails.
- AC5: Given a check that ran more than once on the head, when the pull request is read, then only the run with the latest start time counts, whether it passed after an earlier failure or failed after an earlier pass.
- AC6: Given checks with the same name in two different workflows, when the pull request is read, then each workflow's latest run is reported as its own check.

## Notes

- Editing a description reruns the `check` job, and the earlier run on the same head stays in the rollup; AC5 is why a fixed description does not keep showing the old failure.
- How the merge gate uses these checks belongs to the delivery epic.

## Open questions

- None. Adopted behavior, recorded as it is; nothing is open for this story.
