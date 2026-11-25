---
id: US-INST-14
type: story
title: Resolve update conflicts
epic: EP-INST
source_reqs: [INST-R18]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a maintainer who edited a framework file, I want to choose what happens when the new release changed it too, so that neither my edit nor the framework's change is lost silently.

## Acceptance criteria

- AC1: Given a locked file edited locally whose new version also differs from the locked one, when `update` plans, then it lists the file as a conflict.
- AC2: Given a conflict and a terminal, when the update is applied, then it asks per file to keep yours, take the new version, or show the diff (default keep).
- AC3: Given the answer keep, or `--yes`, when the conflict is resolved, then your file stays, the new version is written as `<name>.kitchen-new`, and the summary lists the files kept.
- AC4: Given the answer take, when the conflict is resolved, then the new version replaces your file.
- AC5: Given the answer diff, when the conflict is resolved, then a unified diff from `yours/<path>` to `new/<path>` is printed and the question is asked again.

## Notes

Observed in `init.py` on 2026-11-25 by `/define adopt`; not yet confirmed by a person. After a keep, the lock records the new version's hash, so the next update sees the file as edited locally (US-INST-15/AC5).

## Open questions

- None. Behavior recorded as observed; the person confirms it.
