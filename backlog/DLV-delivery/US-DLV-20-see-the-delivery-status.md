---
id: US-DLV-20
type: story
title: See the delivery status on one screen
epic: EP-DLV
source_reqs: [DLV-R26]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person following the work, I want `deliver.py status` to show what is ready, taken, blocked, open, missing, and recently delivered, so that I can see the state of delivery at a glance.

## Acceptance criteria

- AC1: Given a backlog, when `deliver.py status` runs, then its first line counts the non-epic tickets per status (draft, ready, in-progress, done, deferred) and adds a note to run `backlog_check.py` when the backlog has errors.
- AC2: Given tickets claimed by an open change request or a pushed branch, when `deliver.py status` runs, then the READY section lists the ready tickets in `next` order without the claimed ones; when the host cannot be read, it uses the branches seen at the last fetch and prints a NOTE.
- AC3: Given in-progress, blocked, and open decision or spike tickets, when `deliver.py status` runs, then IN PROGRESS shows each in-progress ticket's branch and whether it is on origin, BLOCKED shows each unfinished ticket's open blockers, and OPEN DECISIONS AND SPIKES lists decisions and spikes that are not done or deferred with their status.
- AC4: Given definition gaps and test debt, when `deliver.py status` runs, then it prints the gap count with the first five gaps (pointing to `backlog_check.py --gaps` when there are more) and the test-debt count.
- AC5: Given committed delivery records, when `deliver.py status` runs, then LAST DELIVERIES lists the five most recently committed records that still exist, newest first, each with its commit date, including paths with spaces or non-ASCII characters.

## Notes

Adopted 2026-11-25 from `template/scripts/deliver.py` (installed copy `scripts/deliver.py`); the criteria describe what the code does now and are not yet confirmed by a person. Status reads local copies of origin's branches and works offline.

## Open questions

- None. Adopted behavior.
