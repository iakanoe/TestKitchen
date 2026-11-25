---
id: US-DEF-11
type: story
title: Trace to-do markers and decision mentions
epic: EP-DEF
source_reqs: [DEF-R15, DEF-R16]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person keeping work from getting lost, I want every to-do marker and decision mention in code and tests tied to a ticket, so that nothing left for later is forgotten.

## Acceptance criteria

- AC1: Given a line in a code or test file holding a to-do marker word and no existing ticket ID, when `backlog_check.py` runs, then it reports an error at that file and line, while the same line in a file outside the `code` and `tests` globs is not checked.
- AC2: Given a code or test file mentioning a decision ID that does not exist, when `backlog_check.py` runs, then it reports an error, and given the mentioned decision is done, then it prints a warning to revisit that seam.
- AC3: Given files matching the `ignore` globs, among them a file under `backlog/` without frontmatter and a code file with an unowned marker, when `backlog_check.py` runs, then none of them is scanned or read as a ticket.
- AC4: Given a test file whose first ten lines contain `test-kitchen: no-trace`, when `backlog_check.py` runs, then its markers and mentions are not checked and its tags prove no criterion.

## Notes

- Adopted 2026-11-25 from existing behavior: the behavior is in `template/scripts/backlog_check.py`. The four marker words are listed in `backlog/README.md`, "Tests and code trace".
- Which files are excluded (`ignore`, and the framework files `kitchen.lock` lists) is US-CONF-09/AC1 and the configuration epic's classification; where the no-trace marker counts is US-CONF-12/AC1.
- The criteria describe what happens now; confirmation happens on the cited `(observed in code)` requirements.

## Open questions

- None. This story records behavior that already exists; anything that looks unintended is filed as a decision on the epic.
