---
id: US-DEF-15
type: story
title: List the gaps of an undefined project
epic: EP-DEF
source_reqs: [DEF-R21, DEF-R24]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person who just installed Test Kitchen, I want `--gaps` to show that nothing is defined yet, so that an empty project never looks fully defined.

## Acceptance criteria

- AC1: Given `docs/product.md` holds only the shipped skeleton's headings and comments, when `backlog_check.py --gaps` runs, then it lists the file as only headings and comments and exits 1.
- AC2: Given no `docs/product.md`, when `backlog_check.py --gaps` runs, then it lists the file as missing.
- AC3: Given a `docs/product.md` that is not UTF-8 text, when `backlog_check.py --gaps` runs, then it lists the file as unreadable and exits 1.
- AC4: Given no requirement in any requirements file, when `backlog_check.py --gaps` runs, then it lists that no requirements are defined.
- AC5: Given code files and no epic declaring `code:`, when `backlog_check.py --gaps` runs, then it lists one line with the number of code files.
- AC6: Given at least one epic declares `code:`, when `backlog_check.py --gaps` runs, then it lists each code file no epic's globs claim, one line per file, and no claimed file.

## Notes

- Adopted 2026-11-25 from existing behavior: the behavior is in `template/scripts/backlog_check.py`. Decided in the decision-log entry "An empty project is not fully defined".
- The criteria describe what happens now; confirmation happens on the cited `(observed in code)` requirements.

## Open questions

- None. This story records behavior that already exists; anything that looks unintended is filed as a decision on the epic.
