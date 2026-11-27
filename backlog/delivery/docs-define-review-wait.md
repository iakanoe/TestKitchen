# Delivery record: docs/define-review-wait

- Branch: `docs/define-review-wait`
- Ticket: None

Written by `scripts/deliver.py record`. Everything below the marker is the change request's description, verbatim; `deliver.py gate pr` fails when it differs from the current description.

<!-- change-request-description -->

## Ticket

None. Defines: delivery waits for each review's report before the next step (DLV-R61, TASK-DLV-05).

## Plan

No ticket, so no criterion rows. Run through `/define change` after tracing the TASK-DEF-06 delivery's transcript: its plan review ran in the background, and the agent drafted its edits and ran `init.py update` before the report arrived (nothing was claimed or committed first). The owner chose, each option evaluated for and against: a sentence in the playbook's "Reviews" section (not a forced-foreground setting, not accepting it), for delivery's three reviews only, allowing reads and read-only checks meanwhile.

Changes: new DLV-R61; new draft task TASK-DLV-05; one decision-log entry.

Constrained by: `playbooks/define.md` (change), `backlog/README.md`.

## Gaps found

- TASK-DLV-05: draft; needs `/define refine`.

## Decisions

- Delivery waits for each review's report. Log: Delivery waits for each review's report

## Platform changes

- None

## Test changes

None

## Review report

None: this change request touches no code or test file (only `docs/` and `backlog/`).

## Checks

- `python3 scripts/backlog_check.py` and `--strict`: 0 errors, 0 warnings (6 epics, 149 stories, 20 tasks, 23 decisions, 3 spikes).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
