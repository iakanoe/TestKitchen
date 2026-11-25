---
id: US-DLV-07
type: story
title: Write the delivery record
epic: EP-DLV
source_reqs: [DLV-R10, DLV-R11]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As an agent delivering a change request, I want `deliver.py record` to write a verbatim copy of the description, committed with the work, without overwriting another change request's record, so that the delivery evidence lives in the repository.

## Acceptance criteria

- AC1: Given a description whose Ticket section names a story or task, when `deliver.py record` runs, then it writes `<epic folder>/delivery/<ID>.md` and prints that path; given any other description, it writes `backlog/delivery/<branch with / replaced by ->.md`.
- AC2: Given a description, when `deliver.py record` writes it, then the file starts with `# Delivery record: <ID or branch>`, `- Branch:` and `- Ticket:` lines, a `- Change request:` line only when `--cr` or `--url` is given, and a sentence saying where it came from, followed by the marker line and the description with line endings normalized.
- AC3: Given a record at the target path with the same branch and change-request lines, when `deliver.py record` runs again with an edited description, then it replaces that record.
- AC4: Given a record at the target path that belongs to another change request, when `deliver.py record` runs with `--cr=<N>`, then it writes `<name>-cr<N>.md` instead and leaves the other record unchanged.
- AC5: Given a record at the target path that belongs to another change request, when `deliver.py record` runs without `--cr`, then it fails with `already records another change request: pass --cr=<number>` and writes nothing.
- AC6: Given a `--cr` value that is not a number, when `deliver.py record` runs, then it fails with `--cr must be a change-request number` and writes nothing.

## Notes

Adopted 2026-11-25 from `template/scripts/deliver.py` (installed copy `scripts/deliver.py`); the criteria describe what the code does now and are not yet confirmed by a person. Records are history, not tickets: `backlog_check.py` skips them.

## Open questions

- None. Adopted behavior.
