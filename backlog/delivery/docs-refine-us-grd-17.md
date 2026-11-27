# Delivery record: docs/refine-us-grd-17

- Branch: `docs/refine-us-grd-17`
- Ticket: None

Written by `scripts/deliver.py record`. Everything below the marker is the change request's description, verbatim; `deliver.py gate pr` fails when it differs from the current description.

<!-- change-request-description -->

## Ticket

None. Defines: refines US-GRD-17 (deny in a subagent what the guard would ask), which is now `ready`.

## Plan

No ticket, so no criterion rows. Run through `/define refine US-GRD-17`: two fresh-context ticket-mode reviews, each settled with the owner.

- First review (CRITICAL: 2, WARNING: 2, SUGGESTION: 2): the criteria covered only protected edits and shell writes, not every ask GRD-R36 turns into a deny; the deny's reason was ambiguous; unusual `agent_id` values and `agent_type` alone were not covered. AC1 to AC3 and the story sentence were rewritten, and the owner decided how `agent_id` is read (absent, null, or empty means a main-session call; any other value counts as a subagent's).
- Second review (CRITICAL: 0, WARNING: 2, SUGGESTION: 3): AC2 now also covers AC5's deny; AC4 to AC6 use AC1's definition of a present `agent_id`, and AC1 names a non-string example; AC6 compares with the same call without an `agent_id` instead of "today"; GRD-R36 gains the null and empty reading; the Notes record that AC1 to AC3 were reworded before anything cited them.

US-GRD-17 is `ready` with `refined: 2026-11-27`. It unblocks TASK-DLV-03.

Constrained by: `playbooks/define.md` (refine), `backlog/README.md`.

## Gaps found

- None

## Decisions

- How the guard reads `agent_id`, and the rewritten criteria. Log: How the guard reads agent_id

## Platform changes

- None

## Test changes

None

## Review report

None: this change request touches no code or test file (only `docs/` and `backlog/`). The ticket had two ticket-mode reviews, settled with the owner.

## Checks

- `python3 scripts/backlog_check.py` and `--strict`: 0 errors, 0 warnings (6 epics, 149 stories, 19 tasks, 23 decisions, 3 spikes).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
