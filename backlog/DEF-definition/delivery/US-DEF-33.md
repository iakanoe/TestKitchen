# Delivery record: US-DEF-33

- Branch: `us-def-33-validate-replaces-and-refuse-live-replaced-criteria`
- Ticket: US-DEF-33
- Change request: #5 https://github.com/iakanoe/TestKitchen/pull/5

Written by `scripts/deliver.py record`. Everything below the marker is the change request's description, verbatim; `deliver.py gate pr` fails when it differs from the current description.

<!-- change-request-description -->

## Ticket

US-DEF-33 Validate replaces and refuse live replaced criteria (requirements DEF-R45). Status: `done`.

## Plan

| Criterion | Tests |
| --- | --- |
| US-DEF-33/AC1 | Allowed: a ready ticket and an in-progress ticket each list one live criterion of the done fixture story in `replaces:` (block-list form) → exit 0, no ERROR and no `unknown field` WARN. Empty: `replaces: []` → clean. |
| US-DEF-33/AC2 | Denied: `replaces:` holding a plain string → ERROR saying `replaces` is a list. |
| US-DEF-33/AC3 | Denied, one fixture each, ERROR naming the entry: a ticket ID alone; a criterion number the done story lacks (AC9); a criterion of a ticket that does not exist; a live criterion of a ticket that is `ready`. Allowed: an entry naming a `(removed …)` placeholder of a done ticket, on a ticket that is not done → no error. |
| US-DEF-33/AC4 | Denied: a `done` replacing ticket whose `replaces:` names a still-live criterion → ERROR naming that criterion. Limit: the same entry on a `ready` replacing ticket → no AC4 error (the check applies only to done replacing tickets). |
| US-DEF-33/AC5 | Allowed: the done story shows the criterion as `- AC2: (removed 2026-11-26, replaced by <replacing ID>)`, the replacing ticket is `done` and lists it → exit 0, no ERROR or WARN. |

Tests: a new file `tests/test_def_replaces.py` (no no-trace marker, so its tags count), reusing the fixture project and baseline of `tests/test_backlog_check.py`; each test runs `scripts/backlog_check.py` as a subprocess in a throwaway project. Fixture ticket references are built by joining strings, so the repository's own trace scan never reads them as tags.

Files:
- `template/scripts/backlog_check.py`: `replaces` joins the known fields and the list-typed fields; a new validation block next to the `fixes:` one (entry form, existence, done target, live-or-removed), plus the done-replacing-ticket check; module docstring updated.
- `tests/test_def_replaces.py`: the tagged tests.
- `scripts/backlog_check.py`, `kitchen.lock`: this repository's installed copy, refreshed only through `python3 init.py update` after the product change.
No data or stored-format change beyond the new optional frontmatter field. Interfaces: `backlog_check.py`'s output gains ERROR lines; no new command or flag. User-visible texts: the new ERROR messages (worded like the `fixes` ones).

Plan review (fresh context, Sonnet): CRITICAL 0, WARNING 1, SUGGESTION 5.
- WARNING, `template/backlog/README.md` must document `replaces:`: held by TASK-DEF-04/AC3, which documents the field in the README; not in this story's scope.
- Taken into the tests: a non-list value gives only the "is a list" error (AC2); the AC5 fixture keeps the replacing ticket's body free of `<ticket>/AC<n>` references.
- Decided, logged at capture: a `replaces:` entry is checked in this order: form, existence of the criterion (a `(removed …)` placeholder exists), target ticket `done`; so a placeholder in a ticket that is not done still fails the "not done" rule, because the field only ever names done tickets (DEF-R45).
- Gap, noted on US-DLV-41: `deliver.py context` lists `fixes:` targets among related tickets but will not list `replaces:` targets.
- Not taken: a ticket listing its own criterion, or one entry twice (low value; a self-reference already fails the "not done" rule while the ticket is open).

Constrained by: no accepted ADRs; DEC-DEF-04 (done).

## Gaps found

- `deliver.py context` lists `fixes:` targets among related tickets but not `replaces:` targets: noted on US-DLV-41, which teaches delivery about `replaces:`.

## Decisions

- Check order and message wording for `replaces:` entries; a placeholder in a not-done ticket still fails the not-done rule. Log: US-DEF-33: how backlog_check reads replaces

## Platform changes

- None

## Test changes

None

## Review report

Plan review (fresh context, Sonnet): CRITICAL 0, WARNING 1, SUGGESTION 5. WARNING (README must document `replaces:`): held by TASK-DEF-04/AC3. Taken: single error for a non-list value; AC5 fixture body free of criterion references; check order decided and logged. Filed: the `context` gap on US-DLV-41. Not taken: self-reference and duplicate entries.

Tests review (fresh context, Sonnet): CRITICAL 0, WARNING 0, SUGGESTION 3. Taken before the freeze: a done replacer naming one crossed-out and one live criterion (only the live one is reported). Not taken: mapping and non-string entries (covered by the list check and the reference form); message wording, which the implementation matched to the existing "is a list" message.

Final review (fresh context, Sonnet, diff mode): no defects; SUGGESTION 1 (a no-op line keeping two imports used in the test file), noted and not taken, since it would change a frozen test for no behavior.

Reviewed commit: fc288f6a9ec996a6ca2e39b81debb562ddd6f4f3
CRITICAL: 0, WARNING: 0, SUGGESTION: 1

## Checks

- `deliver.py gate red US-DEF-33` before implementing: PASS (all 6 tagged tests failed on `unknown field replaces`, the missing behavior).
- `deliver.py check` on fc288f6: PASS (backlog check, four self-tests, 263 tests passed).
- `backlog_check.py` on this repository after the change: 0 errors, 0 warnings.
