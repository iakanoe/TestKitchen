---
id: US-DEF-07
type: story
title: Require answered open questions
epic: EP-DEF
source_reqs: [DEF-R10]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person building a ticket, I want every open question answered or filed before the ticket is ready, so that nobody fills a gap by guessing.

## Acceptance criteria

- AC1: Given a `ready`, `in-progress`, or `done` story or task with an open-question bullet that neither starts with `None` nor names a DEC or SPK, when `backlog_check.py` runs, then it reports an error that the question is unanswered.
- AC2: Given such a ticket whose open question names a DEC or SPK that does not exist, when `backlog_check.py` runs, then it reports an error naming the unknown ticket.
- AC3: Given such a ticket whose open question names a DEC that is not done and not in `blocked_by`, and the text after `Until decided:` names none of the ticket's live criteria, when `backlog_check.py` runs, then it reports an error asking for `Until decided:` naming a live criterion.
- AC4: Given such a ticket whose open question names an open DEC with `Until decided:` naming a live criterion, or names a DEC listed in `blocked_by`, or names a done DEC, when `backlog_check.py` runs, then no error is reported.
- AC5: Given a `draft` story with an unanswered open question, when `backlog_check.py` runs, then no error is reported for it.

## Notes

- Adopted 2026-11-25 from existing behavior: the behavior is in `template/scripts/backlog_check.py`. The check applies to stories and tasks only.
- The criteria describe what happens now; confirmation happens on the cited `(observed in code)` requirements.

## Open questions

- None. This story records behavior that already exists; anything that looks unintended is filed as a decision on the epic.
