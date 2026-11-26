# Delivery record: US-DEF-30

- Branch: `us-def-30-count-uncovered-requirements-in-the-summary`
- Ticket: US-DEF-30
- Change request: #14 https://github.com/iakanoe/TestKitchen/pull/14

Written by `scripts/deliver.py record`. Everything below the marker is the change request's description, verbatim; `deliver.py gate pr` fails when it differs from the current description.

<!-- change-request-description -->

## Ticket

US-DEF-30 Count uncovered requirements in the summary (requirements DEF-R40). Status: `done`.

## Plan

| Criterion | Tests |
| --- | --- |
| US-DEF-30/AC1 | The baseline fixture project (clean) plus one requirement no ticket cites: `--strict` → summary ends `1 error(s), 0 warning(s)`, exactly one `ERROR` line, exit 1 (unchanged). Limit: the clean baseline → `0 error(s), 0 warning(s)`. |
| US-DEF-30/AC2 | Same project without `--strict` → summary ends `0 error(s), 1 warning(s)`, exactly one `WARN` line, exit 0 (unchanged). |

Tests: new file `tests/test_def_summary.py` (tags `us_def_30_ac1`, `us_def_30_ac2`), reusing the baseline of `tests/test_backlog_check.py`.
Files: `template/scripts/backlog_check.py` (`main`: compute the uncovered requirements before printing the summary and add them to the error or warning count); this repository's installed copy and `kitchen.lock`, refreshed only through `init.py update`. No new text; exit codes unchanged.

Constrained by: no accepted ADRs; DEC-DEF-01 (done).

## Gaps found

- None

## Decisions

- The summary counts, and the frozen-test fixture fix. Log: US-DEF-30: summary counts and a frozen-test fix

## Platform changes

- None

## Test changes

- `tests/test_def_summary.py`: after the freeze, the fixture string holding the to-do marker word is assembled from parts, because this repository's own trace scan read the literal word as an unowned marker (it contradicted the project rule that every such marker names a ticket). The test asserts exactly the same thing.

## Review report

Plan review (fresh context, Sonnet): CRITICAL 0, WARNING 0, SUGGESTION 4. Taken: the output order is unchanged; a `--strict` case with another error counts both. Not taken: citing the decision-log entry in Decisions (it is cited now); a `--pr-body` count test (optional; the same code path).

Tests review (fresh context, on the session model, because the Sonnet run stopped at a usage limit): CRITICAL 0, WARNING 0, SUGGESTION 3. Taken before the freeze: the counted line is the uncovered requirement's own line. Not taken: a clearer failure if the summary line is missing; a docstring note on the extra case.

Final review (fresh context, Sonnet, diff mode): no findings. (It reported "no frozen tests were changed"; one fixture string was, see Test changes, after its range was read as a whole.)

Reviewed commit: 583cef23c33b1afd7b1f21eab78eb3784b6e4ac0
CRITICAL: 0, WARNING: 0, SUGGESTION: 0

## Checks

- `deliver.py gate red US-DEF-30` before implementing: PASS (the summary showed `0 error(s)` or `1 error(s)` above more ERROR lines; the clean-project limit test passed).
- `deliver.py check` on 583cef2: PASS (backlog check, four self-tests, 276 passed); `init.py doctor`: all checks passed after the fixture fix.
