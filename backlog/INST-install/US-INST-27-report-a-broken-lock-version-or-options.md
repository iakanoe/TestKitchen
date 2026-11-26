---
id: US-INST-27
type: story
title: Report a broken lock version or options
epic: EP-INST
source_reqs: [INST-R36]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: ready
refined: 2026-11-26
---

As an agent or CI job running the installer, I want a broken lock version or options reported like any other broken lock, so that I get one error line that says what to do instead of a traceback.

## Acceptance criteria

- AC1: Given a `kitchen.lock` whose `version` is not `X.Y.Z` with an optional leading `v` (such as `main` or `1.2`), when `update` runs, then it prints `error: kitchen.lock … Restore it from git history.` on standard error, with no traceback, and exits 1.
- AC2: Given a `kitchen.lock` with no `version`, when `update` runs, then it prints the same error and exits 1.
- AC3: Given a `kitchen.lock` whose `options` is not a table (such as `"options": "x"`), when `update` runs, then it prints the same error, with no traceback, and exits 1.

## Notes

- Implements DEC-INST-04, option (a), decided 2026-11-25 by Ianick Noejovich, as widened on 2026-11-26 (INST-R36 supersedes INST-R34: a missing version, an `options` value that is not a table, and the exact `X.Y.Z` form). The `X.Y.Z` form is the one `normalize_version` in `init.py` already accepts for `--version`.
- A lock whose `version` is `X.Y.Z` or `vX.Y.Z` updates as US-INST-13 records; `1.2` was accepted before this decision and is refused now.
- The other broken-lock errors (invalid JSON, no `files` table) and the exit codes stay as US-INST-22/AC2 records them; usage problems and Ctrl-C as US-INST-22/AC1 and AC3.
- Replaces no criterion: the traceback for a malformed version is in US-INST-22's Notes, not its criteria.

## Open questions

- None. The decision log records this decision, and the widening of 2026-11-26 settled the missing version, the options, and the accepted form.
