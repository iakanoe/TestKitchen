---
id: US-DLV-08
type: story
title: Tell ticket and non-ticket change requests apart in gate pr
epic: EP-DLV
source_reqs: [DLV-R12]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a maintainer, I want `gate pr` to decide from the Ticket section whether a change request delivers a story or task, so that ticket checks cannot be skipped and changes without a ticket are still checked.

## Acceptance criteria

- AC1: Given a Ticket section starting with a story or task ID wrapped in backticks, bold, a bullet, or a link, when `deliver.py gate pr` runs, then it applies the ticket checks.
- AC2: Given a Ticket section starting `None.` that names a ticket later, when `deliver.py gate pr` runs on a branch not named like a ticket, then it treats it as a non-ticket change request.
- AC3: Given a branch starting `us-` or `task-` and a Ticket section that does not start with a story or task ID, when `deliver.py gate pr` runs, then it fails saying the Ticket section names no story or task first.
- AC4: Given a non-ticket change request whose branch commits change no code or test file, when `deliver.py gate pr` runs, then it prints that only the description checks and the delivery record apply, and passes when the record matches.
- AC5: Given a non-ticket change request whose branch commits change a code or test file, when `deliver.py gate pr` runs, then it also applies the review checks of gate pr (tally, reviewed commit, nothing changed after it).
- AC6: Given a Ticket section starting with a story or task ID that does not exist, when `deliver.py gate pr` runs, then it fails with `<ID> does not exist`.

## Notes

Adopted 2026-11-25 from `template/scripts/deliver.py` (installed copy `scripts/deliver.py`); the criteria describe what the code does now and are not yet confirmed by a person.

## Open questions

- None. Adopted behavior; the decision-log entry "A change request with no ticket that touches code needs a review" records why non-ticket change requests are reviewed.
