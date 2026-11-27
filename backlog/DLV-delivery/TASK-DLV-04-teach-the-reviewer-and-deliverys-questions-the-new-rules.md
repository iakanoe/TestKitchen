---
id: TASK-DLV-04
type: task
title: Teach the reviewer and delivery's questions the new rules
epic: EP-DLV
source_reqs: [DLV-R58, DLV-R59]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: draft
---

Change `playbooks/review.md` so the reviewer checks `(review)` criteria by name and challenges markers a test could check, and make step 3 of `playbooks/deliver.md` follow define's rules on open DECs and on evaluating options.

## Acceptance criteria

- AC1: `template/playbooks/review.md` diff mode tells the reviewer to check each live `(review)` criterion against the diff and write `Checked by review: <ID>/AC<n>` for each one met, an unmet one being CRITICAL.
- AC2: `template/playbooks/review.md` ticket mode tells the reviewer to flag a `(review)` criterion that a tagged test could check.
- AC3: Step 3 of `template/playbooks/deliver.md` tells the agent to apply `playbooks/define.md`'s rules on open DECs and on evaluating each option (DEF-R49, DEF-R50) to its questions round.

## Notes

- An untestable task under the rule in force until US-DEF-34 and US-DLV-43 are delivered: the final review verifies each criterion by reading the files (DLV-R37).
- Decided 2026-11-27 (decision log, "Review-only criteria carry a (review) marker" and "Agents check open decisions and evaluate options before recommending").
- The root copies (`playbooks/`) are an installed release: they change only through `init.py update`, never by hand.

## Open questions

- None. The rules are fixed by DLV-R58 and DLV-R59.
