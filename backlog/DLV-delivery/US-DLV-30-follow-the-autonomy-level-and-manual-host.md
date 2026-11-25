---
id: US-DLV-30
type: story
title: Follow the autonomy level and the manual host
epic: EP-DLV
source_reqs: [DLV-R38]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person setting up the workflow, I want the autonomy level and the manual host to set how far an agent goes alone, so that I choose where a person takes over.

## Acceptance criteria

- AC1: Given autonomy `merge` (the default), when an agent delivers a ticket, then it runs all 14 steps and merges on green through the merge gate, and a person answers only what the stop-and-ask list names.
- AC2: Given autonomy `pr`, when an agent delivers a ticket, then it runs steps 1 to 11 and stops at "ready to merge", a person merges, and the agent verifies afterwards when asked.
- AC3: Given autonomy `supervised`, when an agent delivers a ticket, then it behaves as under `pr` and also stops after the plan review and after the tests review until a person approves, named in the Plan.
- AC4: Given an agent other than Claude Code, when autonomy is `pr` or `supervised`, then the agent keeps to its level itself (in Claude Code the guard denies agent merges).
- AC5: Given `host: manual`, when an agent delivers a ticket, then a pushed branch is the claim, at step 11 it writes the description file and record, runs `--pr-body` and `gate pr` locally, and pushes for a person to open the change request, and at step 12 it stops and hands over the branch, head sha, description file, and the checks to confirm before a merge-commit merge.

## Notes

Adopted 2026-11-25 from `playbooks/deliver.md`; the criteria describe what the document says now and are not yet confirmed by a person. Playbook behavior is followed by agents and people, so it is verified by review, not by tests.

## Open questions

- None. Adopted behavior.
