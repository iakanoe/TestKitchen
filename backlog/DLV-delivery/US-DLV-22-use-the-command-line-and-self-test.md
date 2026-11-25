---
id: US-DLV-22
type: story
title: Use the command line safely and self-test it
epic: EP-DLV
source_reqs: [DLV-R28, DLV-R29]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As an agent, person, or CI job, I want `deliver.py` to report usage errors before doing anything and to check itself without a network, so that a typo never runs a gate the wrong way and a broken install is caught early.

## Acceptance criteria

- AC1: Given an unknown command, an option the command does not accept, a missing required option, `gate pr` with both or neither of `--body-file` and `--from-record`, or `gate merge` without a numeric number and a full 40-character sha, when `deliver.py` runs, then it prints the usage on standard error and exits 2 without reading `kitchen.yml`.
- AC2: Given a valid command and a missing or invalid `kitchen.yml`, a git error, a host error, or an unreadable file, when `deliver.py` runs, then it prints each line of the error prefixed `FAIL` and exits 1.
- AC3: Given an ID that names no ticket, when `context`, `pr-body`, or `gate red` runs, then it prints `FAIL <ID> does not exist` and exits 1.
- AC4: Given `deliver.py --self-test`, when it runs, then it builds a temporary git repository with its own git identity and no user configuration, walks one story through `next`, `gate red`, `record`, and `gate pr`, checks that `gate pr` refuses a critical finding, and prints `PASS self-test` with exit 0, or each failure, its captured output, and a failure count with exit 1.

## Notes

Adopted 2026-11-25 from `template/scripts/deliver.py` (installed copy `scripts/deliver.py`); the criteria describe what the code does now and are not yet confirmed by a person.

## Open questions

- None. Adopted behavior.
