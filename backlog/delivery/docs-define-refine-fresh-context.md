# Delivery record: docs/define-refine-fresh-context

- Branch: `docs/define-refine-fresh-context`
- Ticket: None

Written by `scripts/deliver.py record`. Everything below the marker is the change request's description, verbatim; `deliver.py gate pr` fails when it differs from the current description.

<!-- change-request-description -->

## Ticket

None. Defines: refines the fresh-context-per-ticket work (`/define refine US-DLV-42`): US-DLV-42 becomes TASK-DLV-03, the `/define` half moves to TASK-DEF-05 (now ready), and TASK-DLV-03 waits for SPK-DLV-02.

## Plan

No ticket, so no criterion rows. Five fresh-context ticket-mode reviews (four on US-DLV-42/TASK-DLV-03, one on TASK-DEF-05); the owner settled each round. Claude Code behavior was checked in the official docs (sub-agents, hooks pages) on 2026-11-26: resuming a returned subagent, hooks in subagents, AskUserQuestion removed from subagents, background subagents surfacing permission prompts.

Changes:
- US-DLV-42 becomes TASK-DLV-03 (an untestable task; the old ID is retired), with a dedicated `ticket-deliverer` agent, the main session picking and handing off, and what counts as a finished ticket.
- DLV-R54 names its files (wording fix); DLV-R53 is superseded by DLV-R55 (adds a replacement subagent when one cannot be resumed).
- New TASK-DEF-05 (`ready`, `refined: 2026-11-26`) for the `/define` half of DLV-R54.
- SPK-DLV-02 points at TASK-DLV-03 and also checks what a guard "ask" does inside a subagent.
- TASK-DLV-03's refinement pauses until SPK-DLV-02: the fourth review's open points are its open questions, with a proposed direction in its Notes.

Constrained by: `playbooks/define.md` (refine), `backlog/README.md`.

## Gaps found

- TASK-DLV-03: the fourth ticket-mode review's six open points, recorded as its open questions until SPK-DLV-02 is done.
- SPK-DLV-02: Verify the guard in a nested subagent (open; blocks TASK-DLV-03).
- DEC-DEF-05: Criteria only a reviewer can check (open; the owner will take it up next, with changes so agents stop proposing tests for review-only criteria and stop presenting options they have not evaluated).

## Decisions

- US-DLV-42 becomes an untestable task with a resumed subagent and a split-off `/define` part. Log: US-DLV-42 becomes TASK-DLV-03
- The worker agent and when a ticket is finished. Log: TASK-DLV-03 names its worker agent and when a ticket is finished
- The checkout after ready to merge, the agent file, and DLV-R55. Log: TASK-DLV-03 settles the checkout, the agent file, and DLV-R55
- Refinement pauses until the spike; TASK-DEF-05 is ready. Log: TASK-DLV-03 waits for SPK-DLV-02; TASK-DEF-05 is ready

## Platform changes

- None

## Test changes

None

## Review report

None: this change request touches no code or test file (only `docs/` and `backlog/`). The tickets themselves were reviewed in ticket mode five times, and the owner settled each round.

## Checks

- `python3 scripts/backlog_check.py`: 0 errors, 0 warnings (6 epics, 145 stories, 16 tasks, 22 decisions, 3 spikes).
- `deliver.py next`: `NEXT TASK-DEF-05`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
