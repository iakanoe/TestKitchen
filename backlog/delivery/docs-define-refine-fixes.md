# Delivery record: docs/define-refine-fixes

- Branch: `docs/define-refine-fixes`
- Ticket: None

Written by `scripts/deliver.py record`. Everything below the marker is the change request's description, verbatim; `deliver.py gate pr` fails when it differs from the current description.

<!-- change-request-description -->

## Ticket

None. Defines: refines the fix tickets the adopt decisions created, so `/deliver` can build them.

## Plan

No ticket, so no criterion rows. Two fresh-context ticket-mode reviews (the second on Sonnet); the owner settled every CRITICAL and WARNING. Changes: criteria already true moved to Notes; review-only stories became tasks (`TASK-INST-03`, `TASK-DEF-02`, `TASK-DEF-03`); `US-GRD-14` split (new `US-GRD-16`); new rule DEC-DEF-04 (`replaces:`) with its requirements and tickets (`US-DEF-33`, `TASK-DEF-04`, `US-DLV-41`, `TASK-DLV-02`); ten requirements widened or made exact (superseded per the playbook); branch-protection endpoints checked in the GitHub and GitLab docs on 2026-11-26. 24 tickets are `ready` with `refined: 2026-11-26`; three wait on `US-DEF-33`.

Constrained by: `playbooks/define.md` (refine), `backlog/README.md`.

## Gaps found

- DEC-DEF-05: Criteria only a reviewer can check (open, decide later).
- SPK-HOST-01: Verify the GitLab adapter on a real GitLab project (still open).

## Decisions

- The adopt fix tickets are refined and ready. Log: The adopt fix tickets are refined and ready
- A new definition retires a done ticket's criterion through replaces. Log: A new definition retires a done ticket's criterion through replaces
- Review-only stories become tasks. Log: Review-only stories become tasks
- Refinement widens ten requirements of the adopt decisions. Log: Refinement widens ten requirements of the adopt decisions
- New tickets leave out criteria that are already true. Log: New tickets leave out criteria that are already true

## Platform changes

- None

## Test changes

None

## Review report

None: this change request touches no code or test file (only `docs/` and `backlog/`). The tickets themselves were reviewed twice in ticket mode, and the owner approved every resulting change.

## Checks

- `python3 scripts/backlog_check.py` and `--strict`: 0 errors, 0 warnings (6 epics, 145 stories, 14 tasks, 20 decisions, 1 spike).
- `--gaps`: 169 lines (unconfirmed requirements, DEC-DEF-05, SPK-HOST-01, test-debt tasks).
- `deliver.py next`: `NEXT US-DEF-33`.
