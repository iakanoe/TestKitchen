---
id: US-INST-09
type: story
title: Install the template files
epic: EP-INST
source_reqs: [INST-R09, INST-R10, INST-R13]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a developer installing Test Kitchen, I want the framework's files placed where my tools read them and my configuration written from my answers, so that the install works without hand edits.

## Acceptance criteria

- AC1: Given the template, when it is installed, then `claude/` goes to `.claude/`, `github/` to `.github/`, `gitlab/gitlab-ci.yml` to `.gitlab-ci.yml`, other `gitlab/` files to `.gitlab/`, a trailing `.tmpl` is dropped, and every other file keeps its relative path.
- AC2: Given cache or editor files (`__pycache__`, `.DS_Store`, `*.pyc`, `*.pyo`, `.pytest_cache`, `.mypy_cache`) or `.kitchen-new` files in the template, when it is installed, then they are skipped, and an executable template file stays executable.
- AC3: Given a `.tmpl` file, when it is rendered, then only the known `{{key}}` tokens (`tests`, `code`, `test_command`, `host_line`, `version`, `repo_url`) are replaced, and `{files}`, `{report}`, and all other text pass through unchanged.
- AC4: Given the three answers, when `kitchen.yml` is written, then it is valid YAML holding `tests` and `code` as lists and `test_command` as a string exactly as answered, the host line, and every optional key commented out with a one-line explanation, under a link to `guide/configuration.md` at the installed version.
- AC5: Given `--no-claude`, when an install runs, then neither `.claude/` nor `CLAUDE.md` is written, `AGENTS.md` still is, and the plan says "Claude Code files: no (--no-claude)".

## Notes

Observed in `init.py` on 2026-11-25 by `/define adopt`; not yet confirmed by a person. `kitchen.yml` comes from `template/kitchen.yml.tmpl`; values are written as JSON, which YAML reads as flow lists and double-quoted strings. `--no-claude` also skips `CLAUDE.md` by decision (decision log, "Installer choices made while building v0.1"); the lock records it (US-INST-10).

## Open questions

- None. Behavior recorded as observed; the person confirms it.
