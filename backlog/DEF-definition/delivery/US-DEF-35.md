# Delivery record: US-DEF-35

- Branch: `us-def-35-check-decs-for-evaluated-options-and-a-matching-outcome`
- Ticket: US-DEF-35
- Change request: #29

Written by `scripts/deliver.py record`. Everything below the marker is the change request's description, verbatim; `deliver.py gate pr` fails when it differs from the current description.

<!-- change-request-description -->

## Ticket

US-DEF-35 Check DECs for evaluated options and a matching outcome (requirements DEF-R51). Status: `done`.

## Plan

| Criterion | Tests |
| --- | --- |
| US-DEF-35/AC1 | `tests/test_def_dec_format.py`, running `backlog_check.py` as a subprocess on throwaway projects. Denied: an open (draft, ready, in-progress) DEC whose option `- (a) …` has only a `For:` line, only an `Against:` line, or neither, each reported as an ERROR naming the DEC and `(a)`; the gap is found for the last option (ending at the end of `## Options`) and for a middle option (ending at the next option), an option whose `For:` line sits under a different option does not count, and the last option whose `For:` and `Against:` lines appear only under the next heading (`## Recommendation`) is still reported. An indented `  - (a) …` bullet under `## Options` is not an option and is not reported. Allowed: `- For:`/`- Against:` sub-bullets indented, and plain `For:`/`Against:` lines, both pass; options listed after `None recorded. Proposals:` are checked the same way. The command exits 1 on the error. |
| US-DEF-35/AC2 | Denied: a draft, a ready, and an in-progress DEC with a heading line `## Outcome` (also with trailing spaces, and in a file with Windows line endings) gets an ERROR naming the DEC and saying an open decision records an outcome. Allowed: a heading that is not exactly `## Outcome` (`### Outcome`, `## Outcomes`) and the word Outcome in body text are not reported. |
| US-DEF-35/AC3 | Denied: a `done` DEC and a `deferred` DEC without `## Outcome` each get an ERROR naming the DEC and saying the decision has no outcome. Denied too: a `done` DEC whose only outcome heading is `### Outcome` or `## Outcomes` (not exactly `## Outcome`). Allowed: a `done` and a `deferred` DEC with `## Outcome` pass clean. |
| US-DEF-35/AC4 | A `done` DEC and a `deferred` DEC (each with `## Outcome`) whose options `- (a)`, `- (b)` have no `For:` or `Against:` lines: the check exits 0 with no ERROR. Contrast in the same test: the same options on a draft DEC are reported, so the test fails if the status exception is missing. |
| US-DEF-35/AC5 | An open DEC whose `## Options` holds only `None recorded.` (no option bullet) passes clean; an open DEC with `- (a) …` bullets under `## Recommendation` or `## Context` (outside `## Options`) and no For/Against lines passes clean. Contrast: the same bullets moved under `## Options` are reported. |

Files: `template/scripts/backlog_check.py` (a DEC-format rule run per decision ticket during validation, with a comment citing DEF-R51 and US-DEF-35; the module docstring's list of checks), the root copy `scripts/backlog_check.py` and `kitchen.lock` through `python3 init.py update` only; new `tests/test_def_dec_format.py` (no no-trace marker; fixture DEC IDs joined from parts so this repository's trace scan doesn't read them); `tests/test_backlog_check.py` fixture updates forced by AC3 (an `## Outcome` added to the done or deferred DECs in `test_dec_mentions`, `test_a_done_dec_stands_in_for_a_log_entry`, `test_gaps`, and `test_refine`) and in `tests/test_deliver.py` (`test_nothing_ready_hands_off_to_define`, the deferred DEC), made before the freeze commit; `template/CONTRIBUTING.md` (the enforcement table's ticket row names the DEC format) and its root copy through `init.py update`; `CHANGELOG.md` (Unreleased: Added, and a migration note); the ticket; `docs/decision-log.md`.

Data changes: none (DEC files are read, not written). Interfaces: `backlog_check.py` gains three ERROR messages, run by everyone (`backlog_check.py`, `deliver.py check`, CI, `gate pr`); no new flag. User-visible parts: the three error texts (wording decided and logged):
- AC1: `<DEC>: option (<x>) under ## Options has no `For:` [or `Against:`] line (DEF-R51)`.
- AC2: `<DEC>: an open decision records an outcome: remove `## Outcome`, or set status done or deferred once decided (DEF-R51)`.
- AC3: `<DEC>: the decision has no outcome (status <status>): add `## Outcome` (DEF-R51)`.

Readings decided and logged (the criteria's words are used as written): a status that is not `done` or `deferred`, including an invalid one, counts as open; "exactly `## Outcome`" ignores trailing spaces and Windows line endings, as `kitchen_lib.section` does; an option bullet is `- (<a-z>)` at the start of the line followed by a space or the end of the line.

Constrained by: no ADRs; TASK-DEF-06 (done; wrote the format into `backlog/README.md`); DEC-DEF-06 and DEC-DEF-07 (draft, already in the required format; this repo's backlog must stay clean); no DEC applies to the check itself.

## Gaps found

- None

## Decisions

- How the check reads open status, the exact `## Outcome` heading, and option bullets, and the three error texts. Log: How backlog_check.py reads and reports the DEC format

## Platform changes

- None

## Test changes

None after the freeze commit. In the freeze commit itself, AC3 forced an `## Outcome` onto existing done or deferred DEC fixtures (no assertion changed): `tests/test_backlog_check.py` (`test_dec_mentions`, `test_a_done_dec_stands_in_for_a_log_entry`, `test_gaps`, `test_refine`) and `tests/test_deliver.py` (`test_nothing_ready_hands_off_to_define`, the deferred DEC).

## Review report

**Plan review** (plan mode): CRITICAL: 0, WARNING: 2, SUGGESTION: 3.
1. WARNING (AC1): no test showed For/Against lines after `## Options` ends are ignored. Fixed: the last option's lines under `## Recommendation` are still reported.
2. WARNING (AC3): "exactly `## Outcome`" untested for decided DECs. Fixed: a done DEC with only `### Outcome` or `## Outcomes` is reported.
3. SUGGESTION (AC2): trailing spaces, CRLF, and in-progress untested. Fixed: all three added.
4. SUGGESTION: the "unindented" part of an option untested. Fixed: an indented `- (c)` is not reported.
5. SUGGESTION: `tests/test_deliver.py`'s deferred DEC fixture not listed. Fixed: given an `## Outcome` and listed under Files and Test changes.

**Tests review** (tests mode): CRITICAL: 0, WARNING: 2, SUGGESTION: 2. `gate red` PASS; every failure is the missing behavior.
1. WARNING (AC1): the one-lowercase-letter marker untested. Fixed: `- (A)`, `- (ab)`, `- (1)` are not options, `- (z)` is.
2. WARNING (AC1): "starts with" `For:`/`Against:` untested. Fixed: the words later in a line do not count.
3. SUGGESTION: tests pinned wording AC1 doesn't require (backticks). Fixed: assertions now check `For:`/`Against:` without backticks; "option (a)" stays as the decided wording.
4. SUGGESTION: the `test_deliver.py` fixture change is not in the ticket's Notes. Noted: listed under Test changes.

**Final review** (diff mode, origin/main...HEAD): every criterion implemented and tested; 346 tests OK; this repo's 23 DECs pass; installed copy byte-identical.
1. SUGGESTION: name the `test_deliver.py` fixture change in the change request. Done: under Test changes.
2. SUGGESTION: `## Outcome` and `For:` patterns also match inside fenced code blocks. Noted, not filed: no DEC quotes one; recorded in the decision-log entry.

The reviewer did not re-run `gate red` (it needs the pre-implementation commit); its result before implementing is below.

Reviewed commit: 7d15f1ba632685c2efcc3f00aa803e8c8ac5e5aa
CRITICAL: 0, WARNING: 0, SUGGESTION: 2

## Checks

- `python3 scripts/deliver.py check`: PASS (backlog check 0 errors, 0 warnings, 23 DECs; self-tests; 346 passed).
- `gate red US-DEF-35` before implementing: PASS (10 of 12 tagged tests failed on exit 0 with no DEC error; the two "reports nothing" allowed-case tests passed, as they should).
- By hand: `python3 init.py update --yes` refreshed `scripts/backlog_check.py`, `CONTRIBUTING.md`, and `kitchen.lock` (doctor: all checks passed); `python3 scripts/backlog_check.py` exits 0 after capture.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
