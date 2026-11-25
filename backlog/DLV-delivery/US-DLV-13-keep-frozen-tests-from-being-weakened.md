---
id: US-DLV-13
type: story
title: Keep frozen tests from being weakened in gate pr
epic: EP-DLV
source_reqs: [DLV-R18, DLV-R19]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a maintainer, I want `gate pr` to refuse lost tagged tests, unlisted test changes, and added skip or focus markers after the freeze, so that the tests that proved the criteria still prove them at merge.

## Acceptance criteria

- AC1: Given a live criterion with no tagged test at the freeze commit, when `deliver.py gate pr` runs, then it fails with `<ID>/AC<n> had no tagged test at the freeze commit`.
- AC2: Given a live criterion with fewer tagged tests at the head than at the freeze, when `deliver.py gate pr` runs, then it fails naming both counts.
- AC3: Given a test file changed by the branch's own commits after the freeze, when `deliver.py gate pr` runs, then it fails unless Test changes names its whole path or file name (a longer path or a word containing the name does not count).
- AC4: Given a branch commit after the freeze that adds a line with a skip or focus marker to a test file (for example `.skip(`, `.only(`, `xit(`, `fit(`, `@pytest.mark.skip`, `@unittest.skip`, `self.skipTest(`, `t.Skip(`, `@Disabled`, `@Ignore`, or a Ruby `skip` or `pending` statement), whatever the file name or the person's git configuration, when `deliver.py gate pr` runs, then it fails naming the commit, the file, and the line.
- AC5: Given skip-like calls in product code, or test lines where marker words appear as plain words (`skipped`, `fit in`, `pending_refunds`), when `deliver.py gate pr` runs, then they are not flagged.
- AC6: Given a merge commit, when `deliver.py gate pr` looks for markers, then only lines new against every parent count, so a marker written inside the merge fails and one brought in from the default branch does not.

## Notes

Adopted 2026-11-25 from `template/scripts/deliver.py` (installed copy `scripts/deliver.py`); the criteria describe what the code does now and are not yet confirmed by a person.

## Open questions

- None. Adopted behavior; markers added before or in the freeze commit are outside these checks, as `playbooks/deliver.md` step 6 describes the freeze rules from the freeze on.
