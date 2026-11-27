---
id: TASK-DLV-05
type: task
title: Wait for each review's report
epic: EP-DLV
source_reqs: [DLV-R61]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: draft
---

Make the delivery playbook say that, after running a review, the agent waits for its report before the next step, and what it may and may not do meanwhile.

## Acceptance criteria

- AC1: `template/playbooks/deliver.md` ("Reviews") tells the agent, after running a review (plan, tests, or diff), to wait for its report before the next step, and says that meanwhile it may read files and run read-only checks but does not edit repository files, run `init.py update`, claim, or commit.

## Notes

- An untestable task: the final review verifies the criterion by reading the file (DLV-R37).
- Evidence: in the TASK-DEF-06 delivery (2026-11-27), the plan review started at 17:34:20 and ran in the background; the agent drafted its edits to `template/playbooks/define.md` and `template/backlog/README.md` from 17:34:38 and ran `init.py update` at 17:34:51, then received the report (CRITICAL: 0) at 17:35:04 and judged its suggestions "already covered by the draft". Nothing was claimed or committed before the report, and the playbook never said to wait.
- Why: an author who drafts before the report tends to check findings against the draft (anchoring), a draft is wasted when the report is critical, and TASK-DLV-03's ticket subagents would run reviews the same way, unattended.
- Delivery's reviews only: define's refine reviews lead to changes that need the person's yes at a checkpoint anyway (decision log, "Delivery waits for each review's report").
- The root copy `playbooks/deliver.md` is an installed release: it changes only through `init.py update`, never by hand.

## Open questions

- None. The rule is fixed by DLV-R61.
