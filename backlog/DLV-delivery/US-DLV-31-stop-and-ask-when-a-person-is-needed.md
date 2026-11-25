---
id: US-DLV-31
type: story
title: Stop and ask when a person is needed
epic: EP-DLV
source_reqs: [DLV-R39]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person running the workflow, I want the agent to stop only for a known list of reasons and to ask everything at once, so that it works without stopping otherwise and never decides what is mine.

## Acceptance criteria

- AC1: Given any of the listed situations (an unclean checkout or unmerged branch, a DEC option to choose, an ambiguous or contradicting criterion or one depending on unfinished work, unsettled user-visible behavior, a change under `docs/` or to criteria or open questions, a blocking gap, a criterion that cannot be proven here, a partly testable task, a test that would be weakened, a check or gate it cannot fix, a failed CI run, deploy, or broken behavior after the merge, a platform, deploy, release, restore, or secret change by hand, the location of a reference input or a credential, supervised approvals, or a crossed product boundary), when the agent meets it, then it stops, asks, and waits.
- AC2: Given several open questions, when the agent stops, then it asks all of them in one round, each with its recommendation first.
- AC3: Given a stop, when the agent waits, then it has committed and pushed first and noted in the draft change request what is waiting.
- AC4: Given a headless run, when the agent must stop, then it prints the questions and stops.

## Notes

Adopted 2026-11-25 from `playbooks/deliver.md`; the criteria describe what the document says now and are not yet confirmed by a person. Playbook behavior is followed by agents and people, so it is verified by review, not by tests.

## Open questions

- None. Adopted behavior.
