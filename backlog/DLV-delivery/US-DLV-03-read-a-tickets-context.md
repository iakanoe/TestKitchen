---
id: US-DLV-03
type: story
title: Read a ticket's context
epic: EP-DLV
source_reqs: [DLV-R05]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As an agent or reviewer, I want `deliver.py context` to print a ticket's criteria, cited requirement text, ADRs, and related tickets, so that the work starts from the recorded text instead of a summary.

## Acceptance criteria

- AC1: Given a ticket, when `deliver.py context <ID>` runs, then it prints the ID and title, the file, the branch, the type, status, owner, and priority (`normal` when unset), the release when releases are on, `hotfix` and `adopted` when set, and the epic with its `code:` globs when it has any.
- AC2: Given a story or task, when `deliver.py context <ID>` runs, then it prints `Live criteria (the only requirements):` followed by its live criterion numbers, or `none`.
- AC3: Given a ticket citing requirements, when `deliver.py context <ID>` runs, then each cited requirement is printed with its text verbatim (including a superseded marker), `NOT FOUND in docs/requirements/` for an ID that does not exist, and `- none` when it cites none.
- AC4: Given ADR files under `docs/architecture/`, when `deliver.py context <ID>` runs, then it lists every ADR whose status starts with `accepted` and every ADR the ticket body names, each with its status and path (`named in the ticket` when named, `NOT FOUND` when named but missing), and leaves out the others.
- AC5: Given tickets named in the body, in `blocked_by`, or in `fixes`, when `deliver.py context <ID>` runs, then each is listed with its title and status (or `does not exist`), followed by the ticket body.

## Notes

Adopted 2026-11-25 from `template/scripts/deliver.py` (installed copy `scripts/deliver.py`); the criteria describe what the code does now and are not yet confirmed by a person.

## Open questions

- None. Adopted behavior.
