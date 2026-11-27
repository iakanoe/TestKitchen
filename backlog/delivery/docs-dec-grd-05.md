# Delivery record: docs/dec-grd-05

- Branch: `docs/dec-grd-05`
- Ticket: None

Written by `scripts/deliver.py record`. Everything below the marker is the change request's description, verbatim; `deliver.py gate pr` fails when it differs from the current description.

<!-- change-request-description -->

## Ticket

None. Defines: decides DEC-GRD-05: the guard denies in a subagent what it would ask, so a protected change made in a subagent comes back to the main session, where the person is asked.

## Plan

No ticket, so no criterion rows. Run through `/define`, with each option evaluated for and against before the owner chose.

- Before the round, the guard was run by hand on the normal delivery steps: it asks about none of them (`init.py update`, commits, plain branch pushes, the `gh pr` steps, the gates and `record`, edits to `template/`, `tests/`, `backlog/`, `guide/`, `CHANGELOG.md`, the decision log). This corrected DEC-GRD-05's option (a) "Against" line, which wrongly said a ticket's subagent could no longer run `init.py update`.
- The owner chose option (a), with sandbox mode unchanged, and read the done criteria that say the guard "asks" (US-GRD-08/AC1, AC4, AC5, US-GRD-09/AC1 to AC4, US-GRD-10/AC4) as narrowed, not contradicted: they describe calls without an `agent_id`.

Changes: new GRD-R36; new draft story US-GRD-17; DEC-GRD-05 `done` with its outcome; EP-GRD's `## Open` back to none; TASK-DLV-03 now blocked by US-GRD-17; a note on US-GRD-16; one decision-log entry.

Constrained by: `playbooks/define.md`, `backlog/README.md`.

## Gaps found

- US-GRD-17: draft; needs `/define refine` before it can be delivered (it unblocks TASK-DLV-03).

## Decisions

- The guard denies in a subagent what it would ask; DEC-GRD-05 closed. Log: The guard denies in a subagent what it would ask

## Platform changes

- None

## Test changes

None

## Review report

None: this change request touches no code or test file (only `docs/` and `backlog/`).

## Checks

- `python3 scripts/backlog_check.py` and `--strict`: 0 errors, 0 warnings (6 epics, 149 stories, 19 tasks, 23 decisions, 3 spikes).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
