---
id: US-INST-18
type: story
title: Doctor checks the configuration
epic: EP-INST
source_reqs: [INST-R23]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a maintainer of a project using Test Kitchen, I want `doctor` to catch a broken `kitchen.yml`, so that the scripts do not fail later on a typo.

## Acceptance criteria

- AC1: Given `kitchen.yml` is missing, is not valid YAML, is not a mapping, or cannot be read because PyYAML is missing, when `doctor` runs, then it fails saying which.
- AC2: Given `kitchen.yml` has unknown keys, `tests` or `code` that is not a non-empty list of globs, an empty `test_command`, a `host` other than github, gitlab, or manual, or an `autonomy` other than merge, pr, or supervised, when `doctor` runs, then it fails listing each problem and pointing to `guide/configuration.md`.
- AC3: Given a `test_command` without `{report}`, when `doctor` runs, then it fails and points to `guide/test-runners.md`.
- AC4: Given a `tests` or `code` glob that matches no project file outside the `ignore` globs, when `doctor` runs, then it warns that the glob matches no file yet, which is fine for a new project; otherwise it passes.

## Notes

Observed in `init.py` on 2026-11-25 by `/define adopt`; not yet confirmed by a person. This is light validation; `scripts/backlog_check.py` does the full one (comment in `load_config`). Globs that match nothing are warnings by decision (decision log, "Installer choices made while building v0.1").

## Open questions

- None. Behavior recorded as observed; the person confirms it.
