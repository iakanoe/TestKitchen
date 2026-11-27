---
id: US-DEF-35
type: story
title: Check DECs for evaluated options and a matching outcome
epic: EP-DEF
source_reqs: [DEF-R51]
blocked_by: [TASK-DEF-06]
owner: Ianick Noejovich
assignee_type: either
status: done
refined: 2026-11-27
---

As a person deciding DECs, I want `backlog_check.py` to refuse an open DEC whose options are not evaluated or that already records an outcome, and a decided DEC without one, so that I decide from evaluated options and every decision is recorded where it was made.

## Acceptance criteria

- AC1: Given a DEC that is not `done` or `deferred` with an option (an unindented bullet `- (<one lowercase letter>) …` under `## Options`) that has no line whose text, after its indentation and an optional `- `, starts with `For:`, or none that starts with `Against:`, before the next option or the end of `## Options`, when `backlog_check.py` runs, then it reports an error naming the DEC and the option's letter.
- AC2: Given a DEC that is not `done` or `deferred` and has a heading that is exactly `## Outcome`, when `backlog_check.py` runs, then it reports an error naming the DEC and saying an open decision records an outcome.
- AC3: Given a DEC with status `done` or `deferred` and no heading that is exactly `## Outcome`, when `backlog_check.py` runs, then it reports an error naming the DEC and saying the decision has no outcome.
- AC4: Given a `done` or `deferred` DEC whose options have no `For:` or `Against:` lines, when `backlog_check.py` runs, then it reports nothing about them.
- AC5: Given a DEC that is not `done` or `deferred` whose `## Options` has no option bullet, or that has `- (x)` bullets outside `## Options`, when `backlog_check.py` runs, then it reports nothing about them.

## Notes

- Decided 2026-11-27 (decision log, "Open DECs carry evaluated options; outcomes match status"). All 20 done DECs already have an Outcome, and DEC-DEF-06 and DEC-DEF-07 got their For and Against lines in the same change.
- It enforces the DEC-file half of DEF-R50. Decision briefs given in chat stay with the playbook rules of TASK-DEF-06, which also writes the format into `backlog/README.md` (AC5); this story is blocked by it so the README describes the format before the check enforces it.
- Existing frozen tests build `done` or `deferred` DEC fixtures without an `## Outcome` and will need one because of AC3: in `tests/test_backlog_check.py`, `test_dec_mentions`, `test_a_done_dec_stands_in_for_a_log_entry`, `test_refine`, and the deferred `DEC-PAY-02` fixture. The change is a fixture update forced by this story, not a weakened test.
- For the release notes: after `init.py update`, an installed project whose open DECs have options without For and Against lines, or whose done or deferred DECs have no Outcome, fails `backlog_check.py` until it adds them.

## Open questions

- None. The checks are fixed by DEF-R51.
