---
id: US-INST-05
type: story
title: Guess the answers from the project
epic: EP-INST
source_reqs: [INST-R06]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a developer installing Test Kitchen, I want the installer to propose answers from my files, so that I confirm instead of typing globs and runner flags from memory.

## Acceptance criteria

- AC1: Given a `package.json` whose dependencies or test script mention vitest, else jest, else whose test script uses `node --test`, when the installer guesses, then the test command is its vitest, jest, or node:test command writing JUnit XML to `{report}`, with a note to add `jest-junit` when jest is used without it.
- AC2: Given no JavaScript runner and a `pytest.ini`, a `conftest.py`, or a Python configuration or requirements file mentioning pytest, when the installer guesses, then the test command is `python3 -m pytest {files} --junitxml={report}`; given none of those and a `go.mod`, it is `gotestsum --junitfile {report} -- ./...` with a note that gotestsum must be installed.
- AC3: Given top-level `tests/`, `test/`, `__tests__/`, or `spec/` folders, when the installer guesses test globs, then each becomes `<folder>/**`, and test files outside them (`*.test.*` or `*.spec.*` JavaScript and TypeScript files, `test_*.py`, `*_test.py`, `*_test.go`, files under `__tests__/`) add a matching `**/` glob.
- AC4: Given a `go.mod`, when the installer guesses code globs, then the guess is `**/*.go`; otherwise each top-level `src/`, `lib/`, `app/`, `pkg/`, `cmd/`, or `internal/` folder becomes `<folder>/**`, and without those a Python project's top-level package folders (holding `__init__.py`, other than `tests` and `test`) do.
- AC5: Given dependency or build folders (`node_modules`, `.venv`, `venv`, `env`, `dist`, `build`, `vendor`, `target`, and similar), when the project's files are listed for guessing, then they are skipped, and in a git repository only tracked and untracked-but-not-ignored files count.

## Notes

Observed in `init.py` on 2026-11-25 by `/define adopt`; not yet confirmed by a person. The listing stops at 50,000 files (`SCAN_LIMIT`). The Go command always runs the whole suite because `go test` takes packages, not files (decision log, "Installer choices made while building v0.1").

## Open questions

- None. Behavior recorded as observed; the person confirms it.
