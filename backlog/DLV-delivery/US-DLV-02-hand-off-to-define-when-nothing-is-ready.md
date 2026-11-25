---
id: US-DLV-02
type: story
title: Hand off to define when nothing is ready
epic: EP-DLV
source_reqs: [DLV-R03]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As an agent or person delivering tickets, I want `deliver.py next` to say what would unblock work when nothing is ready, so that delivery continues with the decisions and refinements that matter most.

## Acceptance criteria

- AC1: Given waiting tickets blocked, directly or through other unfinished tickets, by decisions that are not done, when `deliver.py next` runs and nothing is ready, then it prints a `DECIDE <DEC> (<title>): blocks <n> ticket(s): <IDs>` line for each such decision, the one blocking the most unfinished tickets first.
- AC2: Given a deferred decision that blocks a ticket, when `deliver.py next` runs, then no `DECIDE` line names it and the blocked ticket still has its `WAIT` line.
- AC3: Given draft stories, tasks, or spikes, when `deliver.py next` runs and nothing is ready, then it prints a `REFINE <ID> (<title>)` line for each, in `next` order, after every `DECIDE` line.
- AC4: Given nothing is ready, when `deliver.py next` runs, then its first line is `NEXT none: nothing is ready; decide the DECIDE tickets, then refine the REFINE tickets (run /define)` when there is something to decide or refine, `NEXT none: nothing is ready; <n> waiting (see WAIT lines)` when only waiting work exists, and `NEXT none: nothing is ready or waiting; run /define to plan more work` when there is neither, and it exits 0.
- AC5: Given at least one ticket is ready, when `deliver.py next` runs, then it prints no `DECIDE` or `REFINE` line.

## Notes

The first variant of the `NEXT none` line is printed even when there are only `REFINE` lines.

## Open questions

- None. Adopted behavior; the hand-off order matches `playbooks/deliver.md`, "When nothing is ready".
