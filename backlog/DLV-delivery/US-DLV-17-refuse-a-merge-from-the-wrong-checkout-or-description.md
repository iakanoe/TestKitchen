---
id: US-DLV-17
type: story
title: Refuse a merge from the wrong checkout or description in gate merge
epic: EP-DLV
source_reqs: [DLV-R23]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a maintainer, I want `gate merge` to check the local checkout, the backlog, and the live description before a merge, so that the gates read exactly what is being merged.

## Acceptance criteria

- AC1: Given a checkout that is not the change request's head or has uncommitted changes to tracked files, when `deliver.py gate merge` runs, then it fails asking to run the merge from a clean checkout of the head, and stops checking there.
- AC2: Given a branch that does not contain `origin/<default>`, when `deliver.py gate merge` runs, then it fails saying the branch is behind and must merge it in, push, and wait for the check.
- AC3: Given backlog errors in the checkout, when `deliver.py gate merge` runs, then it fails with one `backlog: <where>: <message>` line per error.
- AC4: Given a live description that breaks the description rules `backlog_check.py --pr-body` applies, when `deliver.py gate merge` runs, then it fails with those messages.
- AC5: Given a live description on which `gate pr` fails (for example one edited after its record was committed), when `deliver.py gate merge` runs, then it prints the `gate pr` failures and `FAIL gate pr failed (above)`.
- AC6: Given `origin/<default>` cannot be fetched, when `deliver.py gate merge` runs, then it fails saying it cannot tell whether the branch is up to date.

## Notes

Adopted 2026-11-25 from `template/scripts/deliver.py` (installed copy `scripts/deliver.py`); the criteria describe what the code does now and are not yet confirmed by a person.

## Open questions

- None. Adopted behavior.
