# Delivery record: fix/gaps-empty-project

- Branch: `fix/gaps-empty-project`
- Ticket: None

Written by `scripts/deliver.py record`. Everything below the marker is the change request's description, verbatim; `deliver.py gate pr` fails when it differs from the current description.

<!-- change-request-description -->

## Ticket

None. Fixes a hole found right after Test Kitchen was installed on its own repository: `backlog_check.py --gaps` reported an installed but undefined project as fully defined. There is no backlog yet to hold a ticket (`/define adopt` comes next).

## Plan

`--gaps` also lists:
- a missing `docs/product.md`, or one with only the skeleton's headings and comments;
- an unreadable `docs/product.md`;
- a project with no requirements;
- existing code while no epic claims any with `code:` (one line in all; per file once any epic declares `code:`, as before).

Tests: `test_an_empty_project_is_not_fully_defined` (uses the shipped `template/docs/product.md` skeleton, plus missing and non-UTF-8 cases); the baseline fixture gains a real `docs/product.md` and an epic that claims `src/**`, so `test_no_gaps_exits_zero` still proves a defined project is gap-free.

Constrained by: `docs/spec-v0.1.md` section 5 (amended).

## Gaps found

- None

## Decisions

- `--gaps` treats an empty project as not fully defined. Log: An empty project is not fully defined

## Platform changes

- None

## Test changes

`tests/test_backlog_check.py` (new test; baseline epic claims `src/**`), `tests/helpers/kitchen_project.py` (baseline `docs/product.md`).

## Review report

Fresh-context reviewer (`ticket-reviewer`, diff mode), three rounds.

Round 1 (fadae19): CRITICAL: 0, WARNING: 1, SUGGESTION: 4. Fixed in c973fb5: define.md `## Done` named the wrong gaps; the test now uses the shipped skeleton; an unreadable product.md gets its own message; the spec's Done bullet amended; the CHANGELOG explains `## Unreleased`.

Round 2 (c973fb5): CRITICAL: 0, WARNING: 1, SUGGESTION: 1. Fixed in b021c8c: the unreadable case is tested; the file is read once and the message names both causes.

Round 3 (b021c8c): no findings.

Reviewed commit: b021c8ce2b2023e4d82f4b8a0021048b43d1b071
CRITICAL: 0, WARNING: 0, SUGGESTION: 0

## Checks

- `python3 -m unittest discover -s tests`: 257 tests OK (1 skipped: the Python stack of the agnosticism test, without pytest).
- `python3 scripts/backlog_check.py`: 0 errors. `--gaps` at the root now prints the three expected lines (product.md skeleton, no requirements, 6 unclaimed code files).
- The root copy of `scripts/backlog_check.py` and `playbooks/define.md` was updated only through `init.py update`; doctor passes.
- The reviewer saw one full-suite run fail once while it ran a second test process in parallel; a rerun passed (257 OK) and the failing test wasn't captured. Not reproduced, so not filed.
