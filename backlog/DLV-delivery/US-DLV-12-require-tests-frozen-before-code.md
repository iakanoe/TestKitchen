---
id: US-DLV-12
type: story
title: Require tests frozen before the code in gate pr
epic: EP-DLV
source_reqs: [DLV-R17]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a maintainer, I want `gate pr` to require one freeze commit before any code changed, so that tests are written from the criteria and not bent to fit the code.

## Acceptance criteria

- AC1: Given a story branch with no commit named `test: <ID> failing tests`, when `deliver.py gate pr` runs, then it fails saying the tests were not frozen before the implementation.
- AC2: Given a branch with more than one commit named `test: <ID> failing tests`, when `deliver.py gate pr` runs, then it fails saying there must be exactly one.
- AC3: Given a code file changed in a commit at or before the freeze commit, including code written inside a merge commit, when `deliver.py gate pr` runs, then it fails saying implementation must come after the failing tests.
- AC4: Given a task whose tests carry its tags and no freeze commit, when `deliver.py gate pr` runs, then it fails saying the task's tests carry its tags, so it is tested first.
- AC5: Given a task with no tagged tests and no freeze commit, when `deliver.py gate pr` runs, then the freeze and test checks are skipped; given a task with a freeze commit, they apply as for a story.

## Notes

Adopted 2026-11-25 from `template/scripts/deliver.py` (installed copy `scripts/deliver.py`); the criteria describe what the code does now and are not yet confirmed by a person. The gate does not check that the freeze commit holds only test files; it checks that no code file changed at or before it.

## Open questions

- None. Adopted behavior.
