# Delivery record: US-CONF-17

- Branch: `us-conf-17-refuse-globs-that-start-with-a-slash`
- Ticket: US-CONF-17
- Change request: #13 https://github.com/iakanoe/TestKitchen/pull/13

Written by `scripts/deliver.py record`. Everything below the marker is the change request's description, verbatim; `deliver.py gate pr` fails when it differs from the current description.

<!-- change-request-description -->

## Ticket

US-CONF-17 Refuse globs that start with a slash (requirements CONF-R28). Status: `done`.

## Plan

| Criterion | Tests |
| --- | --- |
| US-CONF-17/AC1 | Denied, for each key (`tests`, `code`, `ignore`): `parse_config` with that key holding `/vendor/**` raises `ConfigError` with exactly one line, starting `kitchen.yml:`, naming the key, listing `/vendor/**`, and saying globs are relative to the repository root and never start with `/`. Allowed (limit): `src/**` and `./src/**` load. |
| US-CONF-17/AC2 | Denied: `" /vendor/**"` and `.//vendor/**` give the same error (one line, naming the key and the glob). |
| US-CONF-17/AC3 | Denied: one key holding `a\\b` and `/vendor/**` gives two `kitchen.yml:` lines: the existing backslash one and the new one. |

Tests: new file `tests/test_conf_rooted_globs.py` (tags `us_conf_17_ac1`..`ac3`), calling the project copy's `parse_config` like `tests/test_conf_utf8.py` does.
Files: `template/scripts/kitchen_lib.py` (`_globs`: a second check after the backslash one, on each glob with surrounding whitespace trimmed and one leading `./` removed; it no longer returns before the second check, so both problems are reported); this repository's installed copy and `kitchen.lock`, refreshed only through `init.py update`. New user-visible text: "`<key>` globs are relative to the repository root and never start with `/`: [...]".

Constrained by: no accepted ADRs; DEC-CONF-02 (done).

## Gaps found

- None

## Decisions

- The rooted-glob check, its message, and both checks running before the return. Log: US-CONF-17: globs that start with a slash

## Platform changes

- None

## Test changes

None

## Review report

Plan review (fresh context, Sonnet): CRITICAL 0, WARNING 0, SUGGESTION 5. Taken: two offending globs in one line; globs listed as written; `.github/**` must still load. Not taken: a glob with both problems, `././x`, and a bare `/` (no criterion names them).

Tests review (fresh context, Sonnet): CRITICAL 0, WARNING 0, SUGGESTION 2. Taken before the freeze: AC3 checks each line names its own glob. Not taken: `" ./ /vendor/**"` and bare `/`, which CONF-R28 does not name.

Final review (fresh context, Sonnet, diff mode): no findings beyond SUGGESTION 1 (a `"./ /vendor/**"` case), noted, not taken.

Reviewed commit: 7aa6e04a9cb187f244ba7249feab1da4cd51b570
CRITICAL: 0, WARNING: 0, SUGGESTION: 1

## Checks

- `deliver.py gate red US-CONF-17` before implementing: PASS (the AC1, AC2, AC3 tests failed: no error raised, or only the backslash line; the limit test passed).
- `deliver.py check` on 7aa6e04: PASS (backlog check, four self-tests, 272 passed).
