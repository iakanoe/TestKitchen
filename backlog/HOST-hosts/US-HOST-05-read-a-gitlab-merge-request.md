---
id: US-HOST-05
type: story
title: Read a GitLab merge request
epic: EP-HOST
source_reqs: [HOST-R10, HOST-R11]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As the merge gate, I want a GitLab merge request in the host-neutral change-request shape, so that I can decide whether it may merge the same way on every host.

## Acceptance criteria

- AC1: Given an open, non-draft, mergeable merge request, when it is read, then `glab mr view <n> --output json` is called first, and the change request carries its iid as number, state "open", draft false, target branch as base, source branch as head branch, `sha` as head sha, mergeable true, description as body, and `web_url` as url.
- AC2: Given a merge request in state merged, closed, or any other state such as locked, when it is read, then its state is "merged", "closed", or the GitLab state unchanged.
- AC3: Given a merge request marked `draft`, or only `work_in_progress` on older versions, when it is read, then it is a draft.
- AC4: Given a merge request without `sha`, when it is read, then its head sha is `diff_refs.head_sha`.
- AC5: Given a detailed_merge_status, when the merge request is read, then `mergeable` is mergeable, `checking`, `unchecked`, `preparing`, or `approvals_syncing` is unknown, and any other value (such as `conflict`, `need_rebase`, or `not_approved`) is not mergeable.
- AC6: Given no detailed_merge_status, when the merge request is read, then merge_status `can_be_merged` is mergeable, `cannot_be_merged` is not mergeable, and anything else is unknown.

## Notes

- Never run against a real `glab` or GitLab project: the field names follow the GitLab REST documentation cited in `template/scripts/hosts.py`, and the tests answer from recorded JSON. SPK-HOST-01 verifies them end to end.
- The head pipeline's checks are covered by the story on GitLab pipeline checks.

## Open questions

- None. Adopted behavior, recorded as it is; verification on a real GitLab project is tracked in the epic's spike.
