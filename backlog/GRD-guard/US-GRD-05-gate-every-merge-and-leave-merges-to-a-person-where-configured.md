---
id: US-GRD-05
type: story
title: Gate every merge and leave merges to a person where configured
epic: EP-GRD
source_reqs: [GRD-R10, GRD-R11]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a project owner, I want the guard to run the merge gate before an agent merge and to refuse agent merges when a person is meant to merge, so that nothing merges on red or against the project's autonomy setting.

## Acceptance criteria

- AC1: Given a change request that follows the workflow and `autonomy: merge` on GitHub or GitLab, when an agent runs the command `deliver.py merge-command` prints, from the project root or a subfolder, then the guard runs `deliver.py gate merge` (which reads the host), and on a pass lets the merge through.
- AC2: Given the merge gate fails (a failing or pending check, a pin that is not the change request's head, a change request the host cannot return), when the merge runs, then the guard denies it with "Merge gate failed" and the gate's output.
- AC3: Given a merge of the right shape run from another checkout, when it runs, then the guard denies it with a message to merge from this project's checkout, without running the gate or calling the host.
- AC4: Given the manual host, when an agent runs any merge command, then the guard denies it with a message that a person merges the change request because the host is manual, without running the gate or calling the host.
- AC5: Given `autonomy: pr` or `autonomy: supervised` on GitHub or GitLab, when an agent runs the printed merge command, then the guard denies it with a message that a person merges, naming the autonomy setting, without running the gate or calling the host; pushes of a work branch still go through.

## Notes

- Adopted from `template/claude/hooks/guard.py` (`guard_merge`, `same_checkout`). The gate runs with the guard's own interpreter and a 300-second limit; a timeout denies. Behavior observed in the code and its tests on 2026-11-25, not yet confirmed by a person.
- The gate's own checks belong to the delivery scripts, not to this epic.

## Open questions

- None. The behavior is recorded as observed; the person confirms it when walking through the requirements.
