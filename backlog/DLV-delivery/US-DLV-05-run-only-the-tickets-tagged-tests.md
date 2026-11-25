---
id: US-DLV-05
type: story
title: Run only the ticket's tagged tests in gate red
epic: EP-DLV
source_reqs: [DLV-R07, DLV-R09]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As an agent delivering a ticket, I want `gate red` to run exactly the tests that carry the ticket's tags and refuse a run it cannot read, so that the failing-tests check judges the right tests.

## Acceptance criteria

- AC1: Given test files matching the `tests` globs, some tagging the ticket and some not, when `deliver.py gate red <ID>` runs, then `test_command` receives only the files that tag the ticket, never a file listed in `kitchen.lock` or marked no-trace.
- AC2: Given a `test_command` with `{report}` and `{files}` placeholders, when `deliver.py gate red <ID>` runs, then it prints `running: <command>`, writes the report to a temporary folder outside the repository, and removes it afterwards.
- AC3: Given a `test_command` without a `{report}` placeholder, when `deliver.py gate red <ID>` runs, then it fails with `test_command has no {report} placeholder` and exits 1.
- AC4: Given a test command that writes no report, or a report that is not valid XML, when `deliver.py gate red <ID>` runs, then it fails saying the tests could not run (with the end of the command's output) or that the report is not valid XML, and exits 1.
- AC5: Given a story whose tags appear in no test file, when `deliver.py gate red <ID>` runs, then it fails with `no test file tags <ID>` and both tag forms it expects, and exits 1.

## Notes

Adopted 2026-11-25 from `template/scripts/deliver.py` (installed copy `scripts/deliver.py`); the criteria describe what the code does now and are not yet confirmed by a person. How `{files}` placeholders render is shared library behavior.

## Open questions

- None. Adopted behavior.
