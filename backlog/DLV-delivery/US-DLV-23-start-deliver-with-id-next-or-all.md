---
id: US-DLV-23
type: story
title: Start /deliver with an ID, next, or all
epic: EP-DLV
source_reqs: [DLV-R30, DLV-R31]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person running the workflow, I want `/deliver` to take one ticket, the next one, or every ready one, and to hand off to define when nothing is ready, so that delivery keeps going without me choosing the order.

## Acceptance criteria

- AC1: Given a ticket ID, when `/deliver <ID>` runs (or another agent is asked to deliver that ticket following the playbook), then a story or task goes through the 14 steps, a spike or decision goes through its variant, and an epic is not delivered.
- AC2: Given `/deliver next` or no argument, when the agent picks, then it fetches origin, runs `deliver.py next`, and takes the `NEXT` ticket, never reordering by its own judgment; if it thinks the order is wrong it says so and asks.
- AC3: Given `/deliver all`, when a ticket is closed, then the agent returns to picking until nothing is ready and the hand-off leaves nothing to do, or a question needs a person, and it ends by printing `deliver.py status`; change requests waiting for a person's merge do not block it.
- AC4: Given `NEXT none`, when a person is present, then the agent hands off to define as US-DEF-29/AC2 states, one `DECIDE` line at a time, and under `/deliver all` resumes delivering once `next` names a ticket.
- AC5: Given `NEXT none` in a headless run, when the agent hands off, then it never decides or marks a ticket ready, prints a decision brief for each `DECIDE` line and the `REFINE` list with what each draft lacks, and stops.

## Notes

Adopted 2026-11-25 from `playbooks/deliver.md`; the criteria describe what the document says now and are not yet confirmed by a person. Playbook behavior is followed by agents and people, so it is verified by review, not by tests.

## Open questions

- None. Adopted behavior.
