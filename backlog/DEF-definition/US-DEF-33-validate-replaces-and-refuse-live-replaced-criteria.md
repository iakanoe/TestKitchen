---
id: US-DEF-33
type: story
title: Validate replaces and refuse live replaced criteria
epic: EP-DEF
source_reqs: [DEF-R45]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
refined: 2026-11-26
---

As a person or agent changing done behavior, I want `backlog_check.py` to read and check `replaces:`, so that a delivered change never leaves the criterion it replaced binding.

## Acceptance criteria

- AC1: Given a ticket whose `replaces:` lists a live criterion of a `done` ticket (`replaces: [<ticket>/AC<n>]`), when `backlog_check.py` runs, then it reports no error and no unknown-field warning for the field.
- AC2: Given a `replaces:` value that is not a list, when `backlog_check.py` runs, then it reports an error that `replaces` must be a list.
- AC3: Given a `replaces:` entry that is not a criterion reference (a ticket ID alone), names a criterion that does not exist (including a criterion of a ticket that does not exist), or names a criterion of a ticket that is not `done`, when `backlog_check.py` runs, then it reports an error naming the entry. An entry that names a criterion already written as a `(removed …)` placeholder is not a broken reference and is not reported.
- AC4: Given a `done` ticket that carries `replaces:` (the replacing ticket) and names a criterion that is still live, when `backlog_check.py` runs, then it reports an error naming that criterion.
- AC5: Given a `done` ticket that carries `replaces:` and whose replaced criteria are each `- AC<n>: (removed YYYY-MM-DD, replaced by <its ID>)`, when `backlog_check.py` runs, then it reports no error for them.

## Notes

- Implements DEC-DEF-04, decided 2026-11-26 by Ianick Noejovich.
- The field follows `fixes:` (DEF-R05 lists it among the list fields; DEF-R07 checks its entries); `replaces:` joins both. A removed criterion is the placeholder form of DEF-R08.
- Once this story is delivered, the tickets whose Notes say "Replaces (to become a `replaces:` field once US-DEF-33 is delivered)" move those criteria into the field.
- Only the replacing ticket (the one carrying `replaces:`) must be `done` for the check of AC4; the ticket whose criterion is replaced is never judged by it, and it may already show the criterion as a `(removed …)` placeholder.
- A reference to a criterion in a ticket body must name a live criterion (DEF-R07), so once a criterion is crossed out as replaced, a body that still names it in the `<ticket>/AC<n>` form fails the check; a done ticket cannot be rewritten to drop such a reference. Today only the Notes of the replacing tickets themselves name the criteria they replace.

## Open questions

- None. The decision log records this decision.
