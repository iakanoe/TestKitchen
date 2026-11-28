# Delivery record: docs/define-refine-dlv-04-05

- Branch: `docs/define-refine-dlv-04-05`
- Ticket: None
- Change request: #30

Written by `scripts/deliver.py record`. Everything below the marker is the change request's description, verbatim; `deliver.py gate pr` fails when it differs from the current description.

<!-- change-request-description -->

## Ticket

None. Defines: refines TASK-DLV-04 (teach delivery's questions the new rules) and TASK-DLV-05 (wait for each review's report), files TASK-DEF-08 (treat any answer to an open DEC's question as that DEC), and marks all three `ready`.

## Plan

No ticket, so no criterion rows. Run through `/define refine TASK-DLV-04 TASK-DLV-05`, with the owner settling every point.

- TASK-DLV-04's five held review points and the step-10 gap, settled against define's delivered "Questioning" and "Decision format": step 3 points to define's named rules (not whole sections); the open-DEC check covers self-decided items whenever they come up and in every variant; an unlisted answer to an open DEC's question counts as that DEC (DEF-R52 supersedes DEF-R49, DLV-R63 supersedes DLV-R60, new TASK-DEF-08 for define's side); "Stop and ask" questions follow the same rules (DLV-R62 supersedes DLV-R59); new DECs, at step 10 and as a spike's follow-ups, carry the DEC option format (DLV-R65).
- The step-6 inconsistency seen in the US-GRD-17 delivery (tests-review CRITICALs fixed but not re-reviewed before the freeze): DLV-R64, added to TASK-DLV-05 as AC2, with AC3 for the "Done when" row.
- Ticket-mode reviews: TASK-DLV-04 seven, TASK-DLV-05 three, TASK-DEF-08 three. No CRITICAL in any; every WARNING settled with the owner; the owner set a stop rule for wording-only readings after the sixth review.

TASK-DLV-04, TASK-DLV-05, and TASK-DEF-08 are `ready` with `refined: 2026-11-27`, owner Ianick Noejovich. TASK-DLV-04 is blocked by TASK-DEF-08.

Constrained by: `playbooks/define.md` (refine, change), `backlog/README.md`.

## Gaps found

- Define's side of DEF-R52 (the "Check open decisions before recommending" bullet must name unlisted answers): TASK-DEF-08.

## Decisions

- Step 3 points to define's named questioning rules. Log: Delivery points to define's named questioning rules
- The open-DEC check applies to self-decided items whenever they come up. Log: Self-decided items are checked whenever they come up
- An unlisted answer to an open DEC's question counts as that DEC (DEF-R52, DLV-R63, TASK-DEF-08). Log: An answer to an open DEC's question counts as that DEC
- "Stop and ask" questions follow the questioning rules (DLV-R62). Log: Stop-and-ask questions follow the questioning rules
- New DECs carry the DEC option format (DLV-R65). Log: Delivery opens new DECs in the DEC format
- Step 6 reruns the tests review until no CRITICAL is left (DLV-R64). Log: The tests review reruns until no CRITICAL is left
- How each review's warnings and suggestions were settled, and the stop rule. Log: How the refinement reviews of TASK-DLV-04, TASK-DLV-05, and TASK-DEF-08 were settled
- The three tickets are ready. Log: TASK-DLV-04, TASK-DLV-05, and TASK-DEF-08 are ready

## Platform changes

- None

## Test changes

None

## Review report

None: this change request touches no code or test file (only `docs/` and `backlog/`). The tickets had thirteen ticket-mode reviews in all, each settled with the owner; their findings and outcomes are in the decision-log entry "How the refinement reviews of TASK-DLV-04, TASK-DLV-05, and TASK-DEF-08 were settled" and the tickets' Notes.

## Checks

- `python3 scripts/backlog_check.py` and `--strict`: 0 errors, 0 warnings (6 epics, 149 stories, 21 tasks, 23 decisions, 3 spikes).
- `python3 scripts/deliver.py check`: PASS, 346 tests passed.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
