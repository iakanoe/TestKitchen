# Delivery record: docs/define-review-marker

- Branch: `docs/define-review-marker`
- Ticket: None

Written by `scripts/deliver.py record`. Everything below the marker is the change request's description, verbatim; `deliver.py gate pr` fails when it differs from the current description.

<!-- change-request-description -->

## Ticket

None. Defines: decides DEC-DEF-05 (criteria only a reviewer can check carry a `(review)` marker) and adds rules so agents check open decisions and evaluate options before recommending.

## Plan

No ticket, so no criterion rows. Run through `/define change`. The owner chose in one decision round, each option evaluated against the repository first: DEC-DEF-05 option (b), the `(review)` marker; the open-DEC rule in both playbooks; one "For" and one "Against" line per option. At the checkpoint the owner also approved the two consequences the evaluation found: a second allowed edit to done tickets (adding the marker to adopted criteria) and `gate red` skipping `(review)` criteria; and the five done criteria the change contradicts (US-DEF-10/AC4, AC5, AC6; US-DLV-06/AC2, AC4), now listed under `replaces:`.

Changes:
- Requirements: DEF-R14 superseded by DEF-R47; DLV-R08 superseded by DLV-R56; new DEF-R48, DEF-R49, DEF-R50, DLV-R57, DLV-R58, DLV-R59.
- DEC-DEF-05 is `done` with its outcome; EP-DEF's `## Open` no longer lists it.
- New draft tickets: US-DEF-34, US-DLV-43, TASK-DLV-04, TASK-DEF-06, TASK-DEF-07.

Constrained by: `playbooks/define.md` (change), `backlog/README.md`.

## Gaps found

- US-DEF-34, US-DLV-43, TASK-DLV-04, TASK-DEF-06: draft; need `/define refine`.
- TASK-DEF-07: draft, blocked by US-DEF-34 and TASK-DEF-06; marks the adopted review-only criteria with the owner, a batch per epic.

## Decisions

- Review-only criteria carry a `(review)` marker; closes DEC-DEF-05. Log: Review-only criteria carry a (review) marker
- Agents check open decisions and evaluate options before recommending. Log: Agents check open decisions and evaluate options before recommending

## Platform changes

- None

## Test changes

None

## Review report

None: this change request touches no code or test file (only `docs/` and `backlog/`). The new tickets get their ticket-mode reviews in `/define refine`.

## Checks

- `python3 scripts/backlog_check.py`: 0 errors, 0 warnings (6 epics, 147 stories, 19 tasks, 22 decisions, 3 spikes).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
