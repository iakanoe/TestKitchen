---
id: US-DEF-12
type: story
title: Report validation and coverage
epic: EP-DEF
source_reqs: [DEF-R17, DEF-R18]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person or CI job checking the backlog, I want one summary line, one line per finding, and a clear exit code, so that a script or a person can act on the result.

## Acceptance criteria

- AC1: Given a valid project, when `backlog_check.py` runs, then it prints `backlog: <n> epic, <n> story, <n> task, <n> decision, <n> spike; 0 error(s), 0 warning(s)` and exits 0.
- AC2: Given a `kitchen.yml` with an unknown key, when `backlog_check.py` runs, then it prints the problem as an `ERROR kitchen.yml:` line and exits 1.
- AC3: Given a requirement that is not superseded and is cited by no story or task, when `backlog_check.py` runs, then it prints a `WARN` line "not cited by any story or task" and exits 0.
- AC4: Given the same uncovered requirement, when `backlog_check.py --strict` runs, then the line is an `ERROR` and the run exits 1.
- AC5: Given a requirement cited only by a deferred ticket, or belonging to an epic with `status: deferred`, when `backlog_check.py` runs, then the first is reported as uncovered and the second is not.

## Notes

- Adopted 2026-11-25 from existing behavior: the behavior is in `template/scripts/backlog_check.py`. With `--strict` the summary's error count leaves out the uncovered requirements; see DEC-DEF-01.
- Run from a subfolder, the script finds the repository root as US-CONF-15/AC1 states.
- The criteria describe what happens now; confirmation happens on the cited `(observed in code)` requirements.

## Open questions

- None. This story records behavior that already exists; anything that looks unintended is filed as a decision on the epic.
