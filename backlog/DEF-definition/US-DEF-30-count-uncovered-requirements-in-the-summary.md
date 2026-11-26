---
id: US-DEF-30
type: story
title: Count uncovered requirements in the summary
epic: EP-DEF
source_reqs: [DEF-R40]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: in-progress
refined: 2026-11-26
---

As a person or CI job reading `backlog_check.py` output, I want the summary counts to match the lines under them, so that a log never says `0 error(s)` above an `ERROR` line.

## Acceptance criteria

- AC1: Given a project whose only finding is one uncovered requirement, when `backlog_check.py --strict` runs, then the summary line ends `1 error(s), 0 warning(s)`, matching the one `ERROR` line printed for it.
- AC2: Given the same project, when `backlog_check.py` runs without `--strict`, then the summary line ends `0 error(s), 1 warning(s)`, matching the one `WARN` line printed for it.

## Notes

- Implements DEC-DEF-01, option (a), decided 2026-11-25 by Ianick Noejovich. It changes the summary recorded by US-DEF-12, which stays as the record of the earlier behavior.
- The summary line's form is `backlog: <n> epic, <n> story, <n> task, <n> decision, <n> spike; <n> error(s), <n> warning(s)` (US-DEF-12/AC1).
- Exit codes do not change: US-DEF-12/AC3 keeps the run without `--strict` exiting 0, and US-DEF-12/AC4 keeps the `--strict` run exiting 1.
- Replaces no criterion: no criterion of US-DEF-12 states the summary counts when a requirement is uncovered.

## Open questions

- None. The decision log records this decision.
