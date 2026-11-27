# Delivery record: docs/define-dec-check

- Branch: `docs/define-dec-check`
- Ticket: None

Written by `scripts/deliver.py record`. Everything below the marker is the change request's description, verbatim; `deliver.py gate pr` fails when it differs from the current description.

<!-- change-request-description -->

## Ticket

None. Defines: a `backlog_check.py` check for DEC files (DEF-R51, US-DEF-35), reverses the `(review)` marker (DEC-DEF-05's outcome), adds a check against open DECs for items delivery decides itself (DLV-R60), and refines the questioning-rule tickets.

## Plan

No ticket, so no criterion rows. Run through `/define change` and `/define refine`, with each option evaluated for and against before the owner chose.

- **DEC check:** DEF-R51 and US-DEF-35 (`ready`): an option of an open DEC needs `For:` and `Against:` lines; an open DEC has no `## Outcome`; a `done` or `deferred` DEC has one. DEC-DEF-06 and DEC-DEF-07 got their For and Against lines.
- **Marker reversed:** five ticket-mode reviews found the `(review)` marker would also change the criterion format check, the freeze check, `gate red` for all-review stories, the plan and tests reviews, and delivery steps 2 and 6, several times the cost estimated when DEC-DEF-05 was decided. The owner reversed it: DEF-R14 and DLV-R08 are restored (today's superseded markers on them removed, so their done stories cover them again); DEF-R47, DEF-R48, DLV-R56 to DLV-R58 are superseded by them; US-DEF-34, US-DLV-43, and TASK-DEF-07 are deferred and retired; the marker criteria of TASK-DEF-06 and TASK-DLV-04 are removed.
- **Delivery's questions:** every step-3 question follows define's rules, and items the agent decides itself are checked against open DECs (new DLV-R60, TASK-DLV-04/AC4).
- **Refinement:** US-DEF-35 and TASK-DEF-06 passed (two review rounds each) and are `ready` with `refined: 2026-11-27`. TASK-DLV-04 stays `draft`, to be refined after TASK-DEF-06 is delivered. TASK-DEF-06 and TASK-DLV-04 were renamed to match their titles (IDs unchanged).

Constrained by: `playbooks/define.md` (change, refine), `backlog/README.md`.

## Gaps found

- TASK-DLV-04: draft; five points from its last ticket-mode review are in its Notes, to settle after TASK-DEF-06 is delivered.

## Decisions

- The DEC check and the two open DECs' For and Against lines. Log: Open DECs carry evaluated options; outcomes match status
- The `(review)` marker is reversed. Log: Review-only work stays in untestable tasks
- Every step-3 question follows define's rules; self-decided items are checked against open DECs. Log: Delivery's questions and self-decided items follow define's rules
- TASK-DLV-04 waits for TASK-DEF-06; two tickets ready. Log: TASK-DLV-04 is refined after TASK-DEF-06

## Platform changes

- None

## Test changes

None

## Review report

None: this change request touches no code or test file (only `docs/` and `backlog/`). The tickets had eight fresh-context ticket-mode reviews; the owner settled every round.

## Checks

- `python3 scripts/backlog_check.py` and `--strict`: 0 errors, 0 warnings (6 epics, 148 stories, 19 tasks, 22 decisions, 3 spikes).
- `deliver.py next`: `NEXT TASK-DEF-06`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
