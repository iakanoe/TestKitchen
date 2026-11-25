---
id: US-INST-20
type: story
title: Doctor checks the host and CI
epic: EP-INST
source_reqs: [INST-R25]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a maintainer of a project using Test Kitchen, I want `doctor` to check that CI and the host CLI match my host, so that the `check` job and change requests work.

## Acceptance criteria

- AC1: Given `kitchen.yml`'s `host`, or else the host detected from `origin`, differs from the lock's host, when `doctor` runs, then it warns and suggests `update --host <that host>`.
- AC2: Given the lock's host is manual, when `doctor` runs, then it skips the CI check and says to run `deliver.py check` before every merge; given another host with no CI file in the lock, it warns; given a locked CI file missing on disk, it fails.
- AC3: Given a CI file, when `doctor` checks its toolchain step, then the marker filled by init passes, the placeholder text (or the file exactly as installed with the bare marker) warns that the step is not filled, and any other content passes as edited by hand.
- AC4: Given host github or gitlab, when `doctor` runs, then it warns when `gh` or `glab` is not installed or its `auth status` fails, with the install or sign-in command, and passes when signed in.

## Notes

Observed in `init.py` on 2026-11-25 by `/define adopt`; not yet confirmed by a person. A signed-out host CLI is a warning by decision (decision log, "Installer choices made while building v0.1"). After `update --host`, AC1 points back to the old host: DEC-INST-01.

## Open questions

- None. Behavior recorded as observed; the person confirms it.
