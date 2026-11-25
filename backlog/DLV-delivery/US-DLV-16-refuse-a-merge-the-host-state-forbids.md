---
id: US-DLV-16
type: story
title: Refuse a merge the host state forbids in gate merge
epic: EP-DLV
source_reqs: [DLV-R22]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a maintainer, I want `gate merge` to refuse unless the host shows an open, ready, green, mergeable change request at the pinned head, so that nothing merges on red or on a commit nobody checked.

## Acceptance criteria

- AC1: Given the manual host, when `deliver.py gate merge <N> --head=<sha>` runs, then it prints `FAIL the host is manual: a person checks and merges the change request`, calls no host CLI, and exits 1.
- AC2: Given an open, non-draft change request targeting the default branch, mergeable, with a passing `check` job at the pinned head, checked from a clean checkout of that head, when `deliver.py gate merge` runs, then it prints `PASS pr: <ID>` and `PASS merge <N>` and exits 0.
- AC3: Given a pinned sha that is not the head, or a change request that is not open, is a draft, or targets another branch, when `deliver.py gate merge` runs, then it fails naming each problem.
- AC4: Given the host reports the change request cannot be merged, or has not decided yet, when `deliver.py gate merge` runs, then it fails saying so.
- AC5: Given no passing job named `check` on the head, or any check failing or pending, when `deliver.py gate merge` runs, then it fails naming the check, with `never merge on a failing or pending check`.
- AC6: Given the host CLI cannot read the change request, when `deliver.py gate merge` runs, then it prints `FAIL cannot read <word> <N>: …` and exits 1.

## Notes

Adopted 2026-11-25 from `template/scripts/deliver.py` (installed copy `scripts/deliver.py`); the criteria describe what the code does now and are not yet confirmed by a person. How each host reports state, mergeability, and checks belongs to the host epic; in Claude Code the guard runs this gate before a merge (guard epic).

## Open questions

- None. Adopted behavior.
