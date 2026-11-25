---
id: US-INST-08
type: story
title: Keep existing files
epic: EP-INST
source_reqs: [INST-R12]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a developer with files of my own, I want the installer never to overwrite them, so that installing Test Kitchen cannot destroy my work.

## Acceptance criteria

- AC1: Given a file already at a framework path, when an install writes files, then the existing file is left byte for byte and the framework's version is written next to it as `<name>.kitchen-new`.
- AC2: Given an existing `kitchen.yml`, when an install writes files, then it is kept and the configuration rendered from the answers is written as `kitchen.yml.kitchen-new`.
- AC3: Given side-by-side copies were written, when the install finishes, then its first next step lists every `<name>.kitchen-new` to merge into the file by hand and then delete.

## Notes

Observed in `init.py` on 2026-11-25 by `/define adopt`; not yet confirmed by a person. A `.kitchen-new` left by an earlier run is replaced by the new one: it is Test Kitchen's own copy, not the project's file. `doctor` keeps warning about waiting copies (US-INST-17/AC6).

## Open questions

- None. Behavior recorded as observed; the person confirms it.
