---
id: US-DLV-11
type: story
title: Require a final review of what is merged in gate pr
epic: EP-DLV
source_reqs: [DLV-R15]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a maintainer, I want `gate pr` to require a clean final review that names the commit it reviewed with no code or tests changed after it, so that every merged line was reviewed.

## Acceptance criteria

- AC1: Given a Review report, when `deliver.py gate pr` runs, then it reads the last `CRITICAL: n, WARNING: n, SUGGESTION: n` tally, and fails when there is none or when its CRITICAL count is above 0.
- AC2: Given a Review report without a `Reviewed commit: <sha>` line, when `deliver.py gate pr` runs, then it fails with `Review report has no "Reviewed commit: <sha>" line`.
- AC3: Given a last `Reviewed commit:` that is not an ancestor of the head, when `deliver.py gate pr` runs, then it fails saying the reviewed commit is not on the branch.
- AC4: Given a code or test file changed by the branch's own commits after the last reviewed commit, when `deliver.py gate pr` runs, then it fails with `code or tests changed after the reviewed commit … review again`.
- AC5: Given only files outside code and tests changed after the reviewed commit, or the default branch merged in after it, when `deliver.py gate pr` runs, then the review check passes.
- AC6: Given a merge commit after the review that writes code of its own, when `deliver.py gate pr` runs, then it fails; given a clean merge of the default branch where both sides changed the same file in different places, the review check passes.

## Notes

Adopted 2026-11-25 from `template/scripts/deliver.py` (installed copy `scripts/deliver.py`); the criteria describe what the code does now and are not yet confirmed by a person. The reviewed commit may be abbreviated (7 to 40 hex characters), although `playbooks/review.md` asks for the full sha.

## Open questions

- None. Adopted behavior; the decision-log entry "History checks see merge commits" records why merges are read with a combined diff.
