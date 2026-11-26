# Delivery record: TASK-DEF-02

- Branch: `task-def-02-say-that-readiness-rules-skip-epics`
- Ticket: TASK-DEF-02
- Change request: #6 https://github.com/iakanoe/TestKitchen/pull/6

Written by `scripts/deliver.py record`. Everything below the marker is the change request's description, verbatim; `deliver.py gate pr` fails when it differs from the current description.

<!-- change-request-description -->

## Ticket

TASK-DEF-02 Say that readiness rules skip epics (requirements DEF-R43). Status: `done`.

## Plan

| Criterion | Tests |
| --- | --- |
| TASK-DEF-02/AC1 | Untestable (documentation). Shown by the final review reading `template/backlog/README.md`, "Readiness": its lead-in becomes "A ticket other than an epic that is `ready`, `in-progress`, or `done` needs:". |
| TASK-DEF-02/AC2 | Untestable (documentation). Shown by the final review reading `guide/concepts.md`, "Readiness": "A ticket other than an epic can be `ready`, …". |

Files: `template/backlog/README.md` (product copy), `guide/concepts.md` (edited in place, not installed), and this repository's installed `backlog/README.md` plus `kitchen.lock`, refreshed only through `python3 init.py update`. No code, data, or interface change; `backlog_check.py` behavior stays as US-DEF-06/AC1 records it. Step 6 (tests first) does not apply: an untestable task.

Plan review (fresh context, Sonnet): CRITICAL 0, WARNING 0, SUGGESTION 2. Taken: no rationale sentence beyond what AC1 asks; `deliver.py check` after the `init.py update` refresh.

Constrained by: no accepted ADRs; DEC-DEF-02 (done).

## Gaps found

- None

## Decisions

- The readiness wording, with no added rationale. Log: TASK-DEF-02: readiness wording

## Platform changes

- None

## Test changes

None

## Review report

Plan review (fresh context, Sonnet): CRITICAL 0, WARNING 0, SUGGESTION 2. Taken: no rationale sentence beyond what AC1 asks; `deliver.py check` after the `init.py update` refresh.

Final review (fresh context, Sonnet, diff mode): AC1 and AC2 met by reading the files; the installed `backlog/README.md` equals the product copy. SUGGESTION 1 (mention the 2026-11-26 widening in the original DEC-DEF-02 log entry): not taken, since entries are history and the widening has its own entry.

Reviewed commit: c1db9663ed90d34c5cccb63054d2fe8d4b885261
CRITICAL: 0, WARNING: 0, SUGGESTION: 1

## Checks

- Untestable task: no `gate red`; each criterion verified by the final review reading the files.
- `deliver.py check` on c1db966: PASS (backlog check, four self-tests, 263 tests passed).
