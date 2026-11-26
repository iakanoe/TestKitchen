# Delivery record: US-DLV-38

- Branch: `us-dlv-38-judge-gate-pr-at-the-revision-it-names`
- Ticket: US-DLV-38
- Change request: #15

Written by `scripts/deliver.py record`. Everything below the marker is the change request's description, verbatim; `deliver.py gate pr` fails when it differs from the current description.

<!-- change-request-description -->

## Ticket

US-DLV-38 Judge gate pr at the revision it names (requirements DLV-R48). Status: `done`.

## Plan

All tests are in `tests/test_dlv_gate_pr_at_head.py`. They build a throwaway project (`tests/helpers/kitchen_project.py`) whose fixture story follows the workflow (claim, freeze, implement, done, delivery record), then run `scripts/deliver.py gate pr --body-file=F --branch=B --base=<base> --head=<rev>` as a subprocess, from a checkout chosen by each test, and compare its `PASS`/`FAIL` lines and exit code.

| Criterion | Tests |
| --- | --- |
| US-DLV-38/AC1 | Allowed: the ticket is `done` at `<rev>` but `in-progress` in the checkout (the claim commit is checked out): `PASS`, exit 0. Denied: the ticket is `in-progress` at `<rev>` but `done` in the checkout: `FAIL … is \`in-progress\``, exit 1. Live criteria: `<rev>` adds an AC3 the plan has no row for, the checkout has two criteria: `FAIL Plan has no row for …/AC3`. Hotfix flag: `hotfix: true` only at `<rev>` (no Decisions log bullet): the two hotfix `FAIL` lines; `hotfix: true` only in the checkout: `PASS`. File name: the ticket file renamed at `<rev>` while the checkout has the old name: the branch matching `<rev>`'s file name passes, the old name fails with `branch … is not the ticket's file name`. Epic folder: the ticket and its record moved to another epic folder at `<rev>`: `PASS` (the record is looked up under `<rev>`'s folder). Type: a story with no freeze commit at `<rev>`, the same file typed `task` in the checkout: `FAIL no commit "test: … failing tests"`. |
| US-DLV-38/AC2 | `autonomy: supervised` only at `<rev>` (no approval lines): both `autonomy is supervised` `FAIL` lines; only in the checkout: `PASS`. `code` glob: at `<rev>` it matches a file changed before the freeze, in the checkout it does not: `FAIL … at or before the freeze commit`; the reverse: `PASS`. `tests` glob: at `<rev>` the tagged test file is outside `tests`, in the checkout inside: `FAIL … had no tagged test at the freeze commit`. `ignore`: at `<rev>` the file changed before the freeze is ignored, in the checkout it is code: `PASS`. An invalid `kitchen.yml` at `<rev>` with a valid one in the checkout: the configuration `FAIL` line, exit 1; the reverse (valid at `<rev>`, invalid committed in the checkout): `PASS`. A `kitchen.yml` missing at `<rev>` with one in the checkout: `FAIL kitchen.yml: not found at <rev>`, exit 1. |
| US-DLV-38/AC3 | `--head` is the checked-out commit (passed as `HEAD` and as the sha); uncommitted edits set the ticket to `ready` and `kitchen.yml` to `autonomy: supervised`: still `PASS`, exit 0. Reverse: the committed ticket is `in-progress`, an uncommitted edit sets it to `done`: `FAIL … is \`in-progress\``. The same edits staged (`git add`, no commit): still ignored. An uncommitted edit that makes `kitchen.yml` invalid: still `PASS`. An untracked ticket file present only in the working tree is not read either (the committed branch names a ticket that does not exist at `<rev>` → `FAIL … does not exist`). |
| US-DLV-38/AC4 | A branch that passes from its own checkout: run again with the same `--head` from the base commit (where the ticket file does not exist); stdout lines and exit code are identical. Same for a branch that fails (a missing plan row): identical `FAIL` lines and exit code from both checkouts. A checkout with no `kitchen.yml` at all: the same lines and exit code as the branch's own checkout. `kitchen.lock` only at `<rev>` (it lists a file changed before the freeze, so that file is a framework file, not code): the same `PASS` from a checkout without the lock; the lock is read at `<rev>` because it is part of what decides code and tests. |
| US-DLV-38/AC5 | Missing at `--head`: the ticket file exists in the checkout but `<rev>` (a commit on the base that never adds it): `FAIL US-…-99 does not exist`, exit 1. Present only at `--head`: run from the base commit, where the file does not exist: judged normally, `PASS` (and a normal `FAIL` when the plan misses a row). |

Files:

- `template/scripts/kitchen_lib.py`: `load_config(root, rev=None)` and `framework_files(root, rev=None)` read `kitchen.yml` and `kitchen.lock` at `rev` when given; a new `blobs_at(root, rev, paths)` reads files at a revision in one `git cat-file --batch` call.
- `template/scripts/backlog_check.py`: `Backlog(root, cfg, rev=None)` lists files with `tracked_files(root, rev)` and reads requirements, tickets, and traced files at `rev` when given (no disk reads).
- `template/scripts/deliver.py`: `Project` loads `kitchen.yml` lazily, and `gate pr` never touches the checkout's configuration: `Project.at(rev)` returns a view of the same repository whose configuration and backlog are read at `rev`, so a missing or invalid `kitchen.yml` in the checkout does not matter; `gate_pr` resolves `--head` and judges everything through that view; `read_at` reuses `blobs_at`; the usage text and the `gate merge` comment say what is read where.
- `tests/test_dlv_gate_pr_at_head.py` (new).
- Installed copies under `scripts/` refreshed through `init.py update`; `guide/concepts.md` gate table row says `gate pr` reads everything at `--head`, committed files only.

Data changes: none (no stored format changes).

Interfaces: `deliver.py gate pr` (same options; anyone may call it, CI and agents do); `gate merge` calls `gate_pr` unchanged. Python signatures gain optional `rev` parameters (internal; default keeps today's behavior for every other caller).

User-visible: no new texts except a missing `kitchen.yml` at `--head`: `FAIL kitchen.yml: not found at <rev>` (a configuration error, exit 1, like a missing file today).

Constrained by: no accepted ADRs (`docs/architecture/` holds none). DEC-DLV-01: done (option (b)). Behavior recorded by US-DLV-10 and US-DLV-14 (done) changes as DEC-DLV-01 says; their tests in `tests/test_deliver.py` stay valid when they commit what they judge.

## Gaps found

- None

## Decisions

- `gate pr` reads `kitchen.yml`, `kitchen.lock`, and the ticket files at `--head` through a repository view (`Project.at`), loads the checkout's configuration only on first use (never in `gate pr`), and prints `FAIL kitchen.yml: not found at <sha>` when `--head` has none; `kitchen.lock` is read at `--head` too because it decides what is code (AC4). Log: US-DLV-38: gate pr reads kitchen.lock at --head too

## Platform changes

- None

## Test changes

None

## Review report

Plan review (fresh-context reviewer, mode plan): CRITICAL: 0, WARNING: 2, SUGGESTION: 2.

- WARNING: `Project()` loads the checkout's `kitchen.yml` eagerly, so an invalid or missing one there would fail `gate pr` before it reads `--head`. Fixed: the configuration loads lazily and `gate pr` never touches the checkout's; tests added for an invalid committed checkout copy (AC2), an uncommitted invalid edit (AC3), and a checkout with no `kitchen.yml` (AC4).
- WARNING: the AC1 row did not cover the ticket type or the epic folder. Fixed: tests for a story at `--head` typed as a task in the checkout, and for the ticket and record moved to another epic folder.
- SUGGESTION: say whether edits are staged. Taken: the AC3 test also runs with the edits staged.
- SUGGESTION: `kitchen.lock` read at `--head` had no test. Taken (see the tests review).

Tests review (mode tests): CRITICAL: 0, WARNING: 2, SUGGESTION: 1.

- WARNING: the `kitchen.lock` test was tagged AC2, which names only `kitchen.yml`. Fixed: it is now an AC4 test (the same verdict from a checkout without the lock), and the choice is logged.
- WARNING: no test for a `kitchen.yml` missing at `--head`. Fixed: added (`FAIL kitchen.yml: not found at …`).
- SUGGESTION: two tests used `--head` equal to `--base`. Taken: both now judge a commit on the base that never adds the ticket.

Final review (mode diff, range `origin/main...HEAD`): CRITICAL: 0, WARNING: 0, SUGGESTION: 2.

- SUGGESTION: `playbooks/deliver.md`, "One checkout", says "the gates read this checkout". Noted, not taken: still true for `gate red`, `gate merge`, and `backlog_check.py`; recorded in the decision-log entry.
- SUGGESTION: reading `kitchen.lock` at `--head` goes beyond the ticket's notes while Decisions said None. Taken: the Decisions bullet above and its decision-log entry.

Reviewed commit: edea5dd58c809b91bffb08d1b62c201fa0372131
CRITICAL: 0, WARNING: 0, SUGGESTION: 2

## Checks

- `gate red US-DLV-38` before implementing: PASS (24 tagged tests, all failing because `gate pr` read the checkout).
- `deliver.py check`: PASS, 300 passed, 1017 subtests passed (pytest from a throwaway virtualenv, as CI installs it).
- `backlog_check.py`: 0 errors, 0 warnings. `init.py update --source .`: doctor, all checks passed.
- By hand: `gate pr` on this branch with `--head=HEAD` and with the head sha, both from this checkout.


🤖 Generated with [Claude Code](https://claude.com/claude-code)
