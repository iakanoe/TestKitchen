---
id: US-INST-04
type: story
title: Answer the three questions
epic: EP-INST
source_reqs: [INST-R05, INST-R07]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a developer installing Test Kitchen, I want to answer three questions on a terminal or with flags, so that the configuration is mine whether I install by hand, from an agent, or in CI.

## Acceptance criteria

- AC1: Given `--tests`, `--code`, and `--test-command`, when an install runs, then none of the three questions is asked, and the glob flags, comma-separated and repeatable, become the `tests` and `code` lists.
- AC2: Given a terminal and a question without its flag, when it is asked, then the guess is shown as the default in brackets after a "Guesses from this folder" line with the reasons, an empty answer takes the guess, and a question with no guess is asked again until answered.
- AC3: Given a test command without `{report}`, when it is typed at the terminal, then the installer says the command must contain `{report}` and asks again; when it comes from `--test-command`, the run stops with exit code 2 and writes nothing.
- AC4: Given `--yes` or no terminal, when a question has no flag, then it takes the guess; when there is no guess either, the run stops with exit code 2, names the flag to pass, and writes nothing.
- AC5: Given no terminal and no `--yes`, when the run reaches a confirmation, then it stops with exit code 2, says to rerun with `--yes` or `--dry-run`, and writes nothing.
- AC6: Given a piped run whose standard input is the script itself, when a question or confirmation is asked, then it is read from the controlling terminal (`/dev/tty`).

## Notes

Observed in `init.py` on 2026-11-25 by `/define adopt`; not yet confirmed by a person. Stopping instead of writing unconfirmed files is a recorded choice (decision log, "Installer choices made while building v0.1"). How guesses are made: US-INST-05.

## Open questions

- None. Behavior recorded as observed; the person confirms it.
