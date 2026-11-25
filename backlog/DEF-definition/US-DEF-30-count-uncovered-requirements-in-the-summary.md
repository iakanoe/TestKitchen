---
id: US-DEF-30
type: story
title: Count uncovered requirements in the summary
epic: EP-DEF
source_reqs: [DEF-R40]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: draft
---

As a person or CI job reading `backlog_check.py` output, I want the summary counts to match the lines under them, so that a log never says `0 error(s)` above an `ERROR` line.

## Acceptance criteria

- AC1: Given an uncovered requirement and `--strict`, when `backlog_check.py` runs, then the summary's error count includes each uncovered requirement printed as an `ERROR` line.
- AC2: Given an uncovered requirement without `--strict`, when `backlog_check.py` runs, then the summary's warning count includes each uncovered requirement printed as a `WARN` line.
- AC3: Given uncovered requirements, when the counts include them, then the exit code is unchanged: 1 with `--strict`, and 0 without it when there are no errors.

## Notes

Implements DEC-DEF-01, option (a), decided 2026-11-25 by Ianick Noejovich. It changes the summary recorded by US-DEF-12, which stays as the record of the earlier behavior.

## Open questions

- None.
