---
id: US-DLV-01
type: story
title: Pick the next ticket deterministically
epic: EP-DLV
source_reqs: [DLV-R01, DLV-R02, DLV-R04]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As an agent or person delivering tickets, I want `deliver.py next` to name the ticket to take and say why the others wait, so that picking never depends on anyone's judgment or memory.

## Acceptance criteria

- AC1: Given ready stories, tasks, and spikes that are not assigned to a person, have no unfinished blocker, and whose branch is not taken, when `deliver.py next` runs, then it prints `NEXT <ID> (<title>) branch `<branch>`` for the first in order and a `READY <ID> (<title>)` line for each other one, in order, and exits 0.
- AC2: Given releases are on in `kitchen.yml`, when `deliver.py next` orders the offered tickets, then a ticket in an earlier slice comes first whatever its priority, and a ticket without a release comes last.
- AC3: Given offered tickets in the same slice, when `deliver.py next` orders them, then it ranks by effective priority (the highest of the ticket's own and of every unfinished ticket it blocks directly or transitively), then by how many unfinished tickets it blocks directly, then tickets whose owner equals `git config user.name` first, then by ID.
- AC4: Given a ready or in-progress story, task, or spike that is assigned to a person, has an unfinished blocker, has a branch held by an open change request or pushed to origin, or is in-progress with no such branch, when `deliver.py next` runs, then it is not offered and a `WAIT <ID>: <why>` line names that reason.
- AC5: Given the host CLI fails while listing taken branches, when `deliver.py next` runs, then it prints `FAIL cannot tell which branches are taken: …` and exits 1.

## Notes

Tickets that are draft, done, or deferred, and decisions and epics, are never offered or listed as waiting. Which branches count as taken comes from the host adapter (host epic).

## Open questions

- None. Adopted behavior; the order is the one `docs/spec-v0.1.md` section 5 describes.
