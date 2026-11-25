---
id: US-INST-03
type: story
title: Check the target folder
epic: EP-INST
source_reqs: [INST-R01, INST-R04]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a developer installing Test Kitchen, I want the installer to check where it is about to write, so that it lands at my repository root and never mixes with unreviewed work.

## Acceptance criteria

- AC1: Given `--target` naming something that is not a folder, when any mode runs, then it stops with exit code 2.
- AC2: Given a target inside a git repository that is not the repository root, when an install runs, then it stops with exit code 2 and names the root to run at or to pass with `--target`.
- AC3: Given a target that is not a git repository, when an install runs, then the plan's first row is `git init`, and `git init` runs only after the plan is confirmed.
- AC4: Given a target that is not a git repository, when an install runs with `--dry-run`, then no `.git` folder is created and no file is written.
- AC5: Given a repository with uncommitted or untracked changes, when an install runs, then it warns and asks "Continue with uncommitted changes?" (default no; a no prints "Stopped. Nothing was written." and exits 1), and a dry run only warns.
- AC6: Given a target that already has a `kitchen.lock`, when an install runs, then it says Test Kitchen is already installed and runs `update` instead.

## Notes

Observed in `init.py` on 2026-11-25 by `/define adopt`; not yet confirmed by a person. Installing into a subfolder is refused and `git init` waits for the confirmation by decision (decision log, "Installer choices made while building v0.1").

## Open questions

- None. Behavior recorded as observed; the person confirms it.
