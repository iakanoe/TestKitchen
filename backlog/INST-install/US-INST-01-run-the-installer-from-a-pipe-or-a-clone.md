---
id: US-INST-01
type: story
title: Run the installer from a pipe or a clone
epic: EP-INST
source_reqs: [INST-R01, INST-R02]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a developer adding Test Kitchen to a repository, I want to run one installer file from a pinned URL or from a clone, so that I get exactly the release I chose without extra setup.

## Acceptance criteria

- AC1: Given `init.py --help`, when it runs, then it exits 0 and lists the modes `install`, `update`, and `doctor` and the flags `--dry-run`, `--yes`, `--tests`, `--code`, `--test-command`, `--host`, `--no-claude`, `--source`, `--version`, and `--target`.
- AC2: Given `init.py` run as a file from a Test Kitchen clone without `--source` or `--version`, when it installs or updates, then it uses the clone's own `template/` and downloads nothing.
- AC3: Given `init.py` run from a pipe, or with `--version` and no `--source`, when it needs the release, then it shallow-clones the tag `v<version>` (default: the running file's own version) of `https://github.com/iakanoe/TestKitchen.git` with git's password prompt switched off, and deletes the clone when the run ends.
- AC4: Given the download fails, when the clone exits with an error, then the run stops with exit code 1, names the version and the URL, shows the end of git's error, and suggests `--source DIR`.
- AC5: Given `--source DIR`, when DIR has no `template/` folder or holds another version than `--version` asks for, then the run stops with exit code 2 and says which.
- AC6: Given a `--version` value that is not `vX.Y.Z` or `X.Y.Z` (for example `latest`), when the run starts, then it stops with exit code 2 saying the version must look like `v1.2.3`.

## Notes

Observed in `init.py` on 2026-11-25 by `/define adopt`; not yet confirmed by a person. The version of a `--source` or clone is its `init.py` `VERSION` line, else its newest `## x.y.z` CHANGELOG heading (`read_source_version`). There is no "latest" lookup (decision log, "Installer choices made while building v0.1"). Where the lock records the source: US-INST-10.

## Open questions

- None. Behavior recorded as observed; the person confirms it.
