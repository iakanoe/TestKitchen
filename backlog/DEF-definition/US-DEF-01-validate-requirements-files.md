---
id: US-DEF-01
type: story
title: Validate requirements files
epic: EP-DEF
source_reqs: [DEF-R01, DEF-R02]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person defining a project, I want malformed requirements files reported, so that every requirement ID is unique, well placed, and resolvable.

## Acceptance criteria

- AC1: Given a file under `docs/requirements/` not named `<CODE>-<name>.md`, when `backlog_check.py` runs, then it reports an error that requirement files are named `<CODE>-<name>.md` and exits 1.
- AC2: Given a requirement line whose ID carries a code other than its file's code, when `backlog_check.py` runs, then it reports an error that the ID does not belong in that file.
- AC3: Given the same requirement ID on two lines, when `backlog_check.py` runs, then it reports an error that the ID is defined twice, naming the file that defined it first.
- AC4: Given a requirement whose text starts `(superseded YYYY-MM-DD by <ID>)` naming an ID that is not defined, when `backlog_check.py` runs, then it reports an error that the replacement is not defined.
- AC5: Given a superseded requirement that no ticket cites, when `backlog_check.py` runs, then it is not reported as uncovered.
- AC6: Given a `README.md` under `docs/requirements/`, when `backlog_check.py` runs, then it is not read as a requirements file and no error is reported.

## Notes

- Adopted 2026-11-25 from existing behavior: the behavior is in `template/scripts/backlog_check.py`.
- Which lines of a requirements file define a requirement is US-CONF-11/AC5.
- The criteria describe what happens now; confirmation happens on the cited `(observed in code)` requirements.

## Open questions

- None. This story records behavior that already exists; anything that looks unintended is filed as a decision on the epic.
