# Delivery record: docs/define-cost-report

- Branch: `docs/define-cost-report`
- Ticket: None

Written by `scripts/deliver.py record`. Everything below the marker is the change request's description, verbatim; `deliver.py gate pr` fails when it differs from the current description.

<!-- change-request-description -->

## Ticket

None. Defines: a cost report tool for this repository's delivery runs (`tools/usage_report.py`, built later as a `chore/` change), and corrects the measured cost of the US-DLV-38 run to about 1.61M effective tokens.

## Plan

No ticket, so no criterion rows. Run through `/define change`. The owner chose, each option evaluated for and against: a repository-only tool built as a `chore/` change (not a product feature, not a new epic); per-model weights from the Anthropic pricing page; grouped output with per-subagent totals, peak context, and `--json`. Checking the pricing page (2026-11-27) showed cache reads cost 0.05× on Claude Opus 5.5, not 0.1×, so the US-DLV-38 figure is corrected; its shares and conclusions are unchanged.

Changes:
- Two decision-log entries.
- SPK-DLV-01: the corrected figure, and measurement with `tools/usage_report.py`.
- TASK-DLV-03: the corrected figure in Notes.

Follow-up, not a gap: `tools/usage_report.py` itself is built in a separate `chore/` change, with tests on synthetic transcripts; it has no ticket by decision.

Constrained by: `playbooks/define.md` (change), `backlog/README.md`.

## Gaps found

- None

## Decisions

- A repository-only cost report tool. Log: A cost report for this repository's delivery runs
- The US-DLV-38 cost corrected. Log: The US-DLV-38 run cost about 1.61M effective tokens, not 2.37M

## Platform changes

- None

## Test changes

None

## Review report

None: this change request touches no code or test file (only `docs/` and `backlog/`).

## Checks

- `python3 scripts/backlog_check.py`: 0 errors, 0 warnings (6 epics, 147 stories, 19 tasks, 22 decisions, 3 spikes).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
