---
id: US-DLV-28
type: story
title: Merge, verify, and close
epic: EP-DLV
source_reqs: [DLV-R36]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As an agent delivering a ticket, I want steps 12 to 14 to merge only through the gate at a checked sha, confirm the result after the merge, and report, so that nothing merges on red and broken behavior stops the work.

## Acceptance criteria

- AC1: Given autonomy `merge` on GitHub or GitLab, when step 12 merges, then the agent waits until every check on the latest commit has finished and passed, reads the head sha, prints `deliver.py merge-command <N> --head=<sha>`, and runs exactly that command alone from this clean checkout, never a merge command of its own or extra options.
- AC2: Given an agent without the guard, when it is about to merge, then it runs `deliver.py gate merge <N> --head=<sha>` immediately before and merges only on PASS; on a FAIL it fixes the cause and never retries the same merge unchanged.
- AC3: Given autonomy `pr` or `supervised`, or the manual host, when step 12 is reached, then the agent stops at "ready to merge", confirms the checks and (on GitHub or GitLab) `gate merge`, reports the change request, its head sha, and the gate result, and says a person merges it with a merge commit, never squash or rebase.
- AC4: Given a merge, when step 13 verifies, then the agent watches the default branch's CI run (and deploy) for the merge commit, stops on a failure, does what `verify:` in `kitchen.yml` says and notes what it saw, or reports "not verified after deploy" when it is unset, and keeps any credential used out of the repository and discards it; when a person merges, it reports what `verify` asks for.
- AC5: Given a finished ticket, when step 14 closes, then the agent returns to the up-to-date default branch, leaves the merged branch as it is, and reports what shipped with the change request's link, what it decided and logged, and what it filed.

## Notes

Adopted 2026-11-25 from `playbooks/deliver.md`; the criteria describe what the document says now and are not yet confirmed by a person. Playbook behavior is followed by agents and people, so it is verified by review, not by tests. An agent in a host app may be told not to poll CI; how it waits for checks is a host-app matter.

## Open questions

- None. Adopted behavior.
