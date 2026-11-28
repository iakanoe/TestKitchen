---
id: TASK-DLV-05
type: task
title: Wait for each review's report
epic: EP-DLV
source_reqs: [DLV-R61, DLV-R64]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: ready
refined: 2026-11-27
---

Make the delivery playbook say that, after running a review, the agent waits for its report before the next step, and what it may and may not do meanwhile, and that step 6 reruns the tests review until no CRITICAL finding is left.

## Acceptance criteria

- AC1: `template/playbooks/deliver.md` ("Reviews") tells the agent, after running a review (plan, tests, or diff), to wait for its report before the next step, and says that meanwhile it may read files and run read-only checks but does not edit repository files, run `init.py update`, claim, or commit.
- AC2: Step 6 of `template/playbooks/deliver.md` tells the agent, after fixing what the tests review finds, to run `gate red` and the tests review again until no CRITICAL finding is left, before the supervised tests approval and the freeze commit.
- AC3: Step 6's row in the "Done when" table of `template/playbooks/deliver.md` says no CRITICAL finding of the tests review is left, as step 4's row does for the plan review.

## Notes

- An untestable task: the final review verifies each criterion by reading the file (DLV-R37).
- Evidence: in the TASK-DEF-06 delivery (2026-11-27), the plan review started at 17:34:20 and ran in the background; the agent drafted its edits to `template/playbooks/define.md` and `template/backlog/README.md` from 17:34:38 and ran `init.py update` at 17:34:51, then received the report (CRITICAL: 0) at 17:35:04 and judged its suggestions "already covered by the draft". Nothing was claimed or committed before the report, and the playbook never said to wait.
- Why: an author who drafts before the report tends to check findings against the draft (anchoring), a draft is wasted when the report is critical, and TASK-DLV-03's ticket subagents would run reviews the same way, unattended.
- Evidence for AC2: in the US-GRD-17 delivery (2026-11-27), the tests review found 2 CRITICAL issues, which were fixed and frozen without a second review; steps 4 and 9 already rerun their reviews until no CRITICAL is left, step 6 only said "fix what it finds" (decision log, "The tests review reruns until no CRITICAL is left").
- US-DLV-25/AC3 (done) says step 6 fixes the tests review's findings and reruns `gate red`; AC2 extends it without contradicting it, so no `replaces:` is needed.
- Left out on purpose (refinement review, 2026-11-27): defining which checks count as "read-only", and forbidding drafts outside the repository while a review runs; either would change DLV-R61.
- Delivery's reviews only: define's refine reviews lead to changes that need the person's yes at a checkpoint anyway (decision log, "Delivery waits for each review's report").
- The root copy `playbooks/deliver.md` is an installed release: it changes only through `init.py update`, never by hand.

## Open questions

- None. The rules are fixed by DLV-R61 and DLV-R64.
