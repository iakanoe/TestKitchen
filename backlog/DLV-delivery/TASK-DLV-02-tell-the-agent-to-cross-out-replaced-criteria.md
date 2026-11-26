---
id: TASK-DLV-02
type: task
title: Tell the agent to cross out replaced criteria
epic: EP-DLV
source_reqs: [DLV-R51]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
refined: 2026-11-26
---

When a delivered ticket lists `replaces:`, its change request crosses the replaced criteria out in their done tickets. This task adds that step to the delivery playbook.

## Acceptance criteria

- AC1: `template/playbooks/deliver.md` tells the agent, when the ticket lists `replaces:`, to turn each replaced criterion into `- AC<n>: (removed YYYY-MM-DD, replaced by <ID>)` in its done ticket within the same change request, and says that this is the one edit a done ticket allows.

## Notes

- Implements DEC-DEF-04, decided 2026-11-26 by Ianick Noejovich. The gate that enforces it is US-DLV-41.
- The final review verifies the criterion by reading the file; no test can.
- The product copy is `template/playbooks/deliver.md`; the root copy is an installed release that changes only through `init.py update`.

## Open questions

- None. The decision log records this decision.
