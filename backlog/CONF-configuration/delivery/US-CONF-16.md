# Delivery record: US-CONF-16

- Branch: `us-conf-16-report-a-kitchen-yml-that-is-not-utf-8`
- Ticket: US-CONF-16
- Change request: #12 https://github.com/iakanoe/TestKitchen/pull/12

Written by `scripts/deliver.py record`. Everything below the marker is the change request's description, verbatim; `deliver.py gate pr` fails when it differs from the current description.

<!-- change-request-description -->

## Ticket

US-CONF-16 Report a kitchen.yml that is not UTF-8 (requirements CONF-R26). Status: `done`.

## Plan

| Criterion | Tests |
| --- | --- |
| US-CONF-16/AC1 | Denied: a fixture project whose `kitchen.yml` holds Latin-1 bytes (`# caf\xe9`); `kitchen_lib.load_config(root)` raises `ConfigError` whose text is exactly `kitchen.yml: not valid UTF-8`. Limit: a valid UTF-8 file with non-ASCII text (`# café`) still loads. |
| US-CONF-16/AC2 | Denied: on that project, `python3 scripts/kitchen_lib.py --config` and `python3 scripts/backlog_check.py` each exit 1 with a line starting `ERROR` that holds `kitchen.yml: not valid UTF-8`, and neither output holds `Traceback`. |

Tests: new file `tests/test_conf_utf8.py` (tags `us_conf_16_ac1`, `us_conf_16_ac2`; no no-trace marker), using the fixture project from `tests/helpers/kitchen_project.py`; the bad file is written with raw bytes after the project is built.
Files: `template/scripts/kitchen_lib.py` (`load_config` catches `UnicodeDecodeError` and raises the configuration error); this repository's installed `scripts/kitchen_lib.py` and `kitchen.lock`, refreshed only through `init.py update`. No new interface; the new user-visible text is `kitchen.yml: not valid UTF-8`.

Constrained by: no accepted ADRs; DEC-CONF-01 (done).

## Gaps found

- None

## Decisions

- Catch only around the read, and the message text. Log: US-CONF-16: a kitchen.yml that is not UTF-8

## Platform changes

- None

## Test changes

None

## Review report

Plan review (fresh context, Sonnet): no findings; SUGGESTION 3, taken: the exact `ERROR kitchen.yml: not valid UTF-8` line for `backlog_check.py`; the catch only around the read; the docstring lists the failure modes.

Tests review (fresh context, Sonnet): CRITICAL 0, WARNING 0, SUGGESTION 3. Taken before the freeze: AC2 split into one test per command. Not taken: a looser `--config` assertion is fine given US-CONF-14/AC4; other encodings (the Latin-1 case meets the criterion). Before the review, the first `gate red` run showed the AC1 tests failing on a broken import (a dataclass needs its module registered); fixed in the test helper before the freeze, so every failure is the missing behavior.

Final review (fresh context, Sonnet, diff mode): no issues. SUGGESTION 1 (`raise … from None`): noted, not taken.

Reviewed commit: 5ebaa3f04815171590fe202161558676a67a8eb5
CRITICAL: 0, WARNING: 0, SUGGESTION: 1

## Checks

- `deliver.py gate red US-CONF-16` before implementing: PASS (the AC1 and AC2 tests failed on the raw `UnicodeDecodeError`; the UTF-8 limit test passed, as it should).
- `deliver.py check` on 5ebaa3f: PASS (backlog check, four self-tests, 267 tests passed).
