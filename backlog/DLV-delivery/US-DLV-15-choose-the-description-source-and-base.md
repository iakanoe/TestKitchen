---
id: US-DLV-15
type: story
title: Choose the description source and base for gate pr
epic: EP-DLV
source_reqs: [DLV-R21]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a CI job or person running `gate pr`, I want it to read the description from the branch's record when the host cannot supply it and to find its base on its own, so that the gate runs the same everywhere.

## Acceptance criteria

- AC1: Given `--from-record` and exactly one delivery record committed on the branch whose branch line names this branch, when `deliver.py gate pr` runs, then it prints `description read from <path>` and checks that description.
- AC2: Given `--from-record` and no such record, or more than one, when `deliver.py gate pr` runs, then it fails with `--from-record needs exactly one delivery record for branch … committed on it` and the records it found.
- AC3: Given no `--base`, when `deliver.py gate pr` runs, then it measures from `origin/<default>`, or from the local default branch with `NOTE origin/<default> does not exist: measuring from the local <default> branch`, or fails asking for `--base=<rev>` when neither exists.

## Notes

Adopted 2026-11-25 from `template/scripts/deliver.py` (installed copy `scripts/deliver.py`); the criteria describe what the code does now and are not yet confirmed by a person. Which hosts' CI uses `--from-record` belongs to the host epic.

## Open questions

- None. Adopted behavior.
