---
id: DEC-DEF-01
type: decision
title: Strict summary leaves out uncovered-requirement errors
epic: EP-DEF
source_reqs: [DEF-R17, DEF-R18]
blocked_by: []
owner: Ianick Noejovich
assignee_type: human
status: done
---

## Question

Is this intended? With `--strict`, the summary line counts only validation errors, so it can say `0 error(s)` while `ERROR` lines for uncovered requirements follow and the run exits 1.

## Context

- Current behavior: `main` builds the summary from `errors` (validation and `--pr-body` errors) before the uncovered requirements are computed; with `--strict` they are then printed as `ERROR` lines and make the exit code 1, but are not in the count. A project whose only problem is one uncovered requirement prints `backlog: …; 0 error(s), 0 warning(s)` followed by `ERROR <ID>: not cited by any story or task` and exits 1 (verified 2026-11-25 on a fixture project).
- Likely intended behavior: the summary's error count matches the `ERROR` lines printed (and, without `--strict`, the warning count would include the uncovered `WARN` lines the same way).
- Evidence: `template/scripts/backlog_check.py:711-719` (summary at 712-713, uncovered lines at 717-718); `docs/spec-v0.1.md` section 5 (`backlog_check.py`): "ERROR lines exit 1, WARN lines don't"; no test covers the summary under `--strict` (`tests/test_backlog_check.py`, `CoverageTest`).

## Options

- (a) Count uncovered requirements in the summary: as errors with `--strict`, as warnings without it.
- (b) Keep the summary as a count of validation findings only, and say so in the usage text.

None of these is recorded in `docs/`; both are proposals.

## Recommendation

(a), proposed: a summary that disagrees with the lines under it misleads people and CI logs; the change is small and does not change any exit code.

## Decides

The DEF-R17 and DEF-R18 wording (confirm or supersede), and whether a fix story follows. No ticket is blocked by it.

## Outcome

- Date: 2026-11-25.
- Answer: Option (a): the `backlog_check.py` summary counts uncovered requirements, as errors with `--strict` and as warnings without it; exit codes are unchanged.
- Decided by: Ianick Noejovich.
- Recorded in: requirements DEF-R40; confirmed DEF-R17, DEF-R18; US-DEF-30; decision log, "The strict summary counts uncovered requirements".
