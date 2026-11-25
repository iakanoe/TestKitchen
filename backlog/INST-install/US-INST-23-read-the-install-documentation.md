---
id: US-INST-23
type: story
title: Read the install documentation
epic: EP-INST
source_reqs: [INST-R28]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a developer evaluating Test Kitchen, I want install, update, doctor, and removal documented in one place, so that I know what the installer will do before I run it.

## Acceptance criteria

- AC1: Given `README.md`, when a person reads its Install section, then it gives the pinned one-liner with how to add `--dry-run`, the clone-then-run commands for v0.1.0, and a copyable agent prompt pointing to the pinned `AGENT-INSTALL.md`, and says that `init.py` is not copied into the project and how to run `doctor`.
- AC2: Given `guide/install.md`, when a person reads it, then it lists what an install does in order, every flag, the behavior without a terminal, the exit codes, where guesses come from, and the toolchain stacks recognized.
- AC3: Given `guide/install.md`, when a person reads it, then it explains the lock's fields, the update outcome per file, the doctor checks with the guard hook block to restore, the files v0.1.0 installs, and how to remove Test Kitchen by hand.

## Notes

Observed in `README.md` and `guide/install.md` on 2026-11-25 by `/define adopt`; not yet confirmed by a person. The documented behavior matched the code where checked; differences are listed in the adopt notes. The pinned tag `v0.1.0` exists on the remote (checked with `git ls-remote` on 2026-11-25).

## Open questions

- None. Behavior recorded as observed; the person confirms it.
