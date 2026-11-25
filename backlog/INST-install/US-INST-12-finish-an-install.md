---
id: US-INST-12
type: story
title: Finish an install
epic: EP-INST
source_reqs: [INST-R16]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a developer who just installed Test Kitchen, I want to be told what to do next and to see whether the install works, so that I can finish the setup without reading the code.

## Acceptance criteria

- AC1: Given the files were written, when the install finishes, then it prints "Installed Test Kitchen <version>." and numbered next steps: fill the `## This project` section of `AGENTS.md` (with a link to `AGENT-INSTALL.md` at that version), review and commit the new files, and define the product with `/define` or `playbooks/define.md`.
- AC2: Given the files were written, when the install finishes, then nothing is committed and `doctor` runs on the target.
- AC3: Given `doctor` reports a `FAIL` after an install, when the install exits, then its exit code is still 0.

## Notes

Observed in `init.py` on 2026-11-25 by `/define adopt`; not yet confirmed by a person. Exit 0 despite a doctor failure is a recorded choice (decision log, "Installer choices made while building v0.1") and is documented in `guide/install.md`. The side-by-side step comes first when there are copies (US-INST-08/AC3).

## Open questions

- None. Behavior recorded as observed; the person confirms it.
