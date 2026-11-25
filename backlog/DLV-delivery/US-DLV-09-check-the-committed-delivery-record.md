---
id: US-DLV-09
type: story
title: Check the committed delivery record in gate pr
epic: EP-DLV
source_reqs: [DLV-R13]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a maintainer, I want `gate pr` to require a committed record that matches the description, so that the description's evidence cannot drift from what the repository keeps.

## Acceptance criteria

- AC1: Given a ticket change request with no record committed at the head, when `deliver.py gate pr` runs, then it fails with `no delivery record at <epic folder>/delivery/<ID>.md` and how to write one.
- AC2: Given a non-ticket change request with no committed record, when `deliver.py gate pr` runs, then it fails with `no delivery record at backlog/delivery/<branch name>.md`.
- AC3: Given a record that exists in the working tree but is not committed at the head, when `deliver.py gate pr` runs, then it does not count and the gate fails.
- AC4: Given committed records whose descriptions all differ from the description being checked, when `deliver.py gate pr` runs, then it fails saying no record matches the description.
- AC5: Given two committed records for the same ticket (`<ID>.md` and `<ID>-cr<n>.md`) or a record committed with Windows line endings, when `deliver.py gate pr` runs, then a record whose description matches passes the record check.
- AC6: Given an epic folder whose name has non-ASCII characters, when `deliver.py gate pr` looks for the record, then it finds it.

## Notes

Adopted 2026-11-25 from `template/scripts/deliver.py` (installed copy `scripts/deliver.py`); the criteria describe what the code does now and are not yet confirmed by a person.

## Open questions

- None. Adopted behavior.
