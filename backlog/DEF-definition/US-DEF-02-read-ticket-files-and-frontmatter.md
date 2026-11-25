---
id: US-DEF-02
type: story
title: Read ticket files and their frontmatter
epic: EP-DEF
source_reqs: [DEF-R04, DEF-R05]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person maintaining the backlog, I want every ticket's frontmatter checked, so that the scripts can rely on its fields.

## Acceptance criteria

- AC1: Given a file inside a `delivery` folder under `backlog/` or a `backlog/README.md`, both without frontmatter, when `backlog_check.py` runs, then neither is read as a ticket and no error is reported.
- AC2: Given a ticket file with no `---` frontmatter block, invalid YAML frontmatter, frontmatter that is not a mapping, or text that is not UTF-8, when `backlog_check.py` runs, then it reports an error naming the problem.
- AC3: Given a ticket missing one of `id`, `type`, `title`, `owner`, `assignee_type`, `status`, or, on a ticket other than an epic, `epic`, `source_reqs`, `blocked_by`, when `backlog_check.py` runs, then it reports an error naming the missing field.
- AC4: Given a ticket whose `type`, `status`, `assignee_type`, or `priority` is outside its listed values, whose `refined` is not a `YYYY-MM-DD` date, whose `adopted` or `hotfix` is not true or false, or whose `source_reqs`, `blocked_by`, `fixes`, or `code` is not a list, when `backlog_check.py` runs, then it reports an error naming the field.
- AC5: Given a `code:` field on a ticket that is not an epic, or a decision whose `assignee_type` is not `human`, when `backlog_check.py` runs, then it reports an error.
- AC6: Given a ticket with a field the conventions do not list, when `backlog_check.py` runs, then it prints a warning about the unknown field and still exits 0.

## Notes

- Adopted 2026-11-25 from existing behavior: the behavior is in `template/scripts/backlog_check.py`.
- The criteria describe what happens now; confirmation happens on the cited `(observed in code)` requirements.

## Open questions

- None. This story records behavior that already exists; anything that looks unintended is filed as a decision on the epic.
