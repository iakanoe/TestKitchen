---
id: US-INST-27
type: story
title: Report a lock version that is not a number
epic: EP-INST
source_reqs: [INST-R34]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: draft
---

As an agent or CI job running the installer, I want a broken lock version reported like any other broken lock, so that I get one error line that says what to do instead of a traceback.

## Acceptance criteria

- AC1: Given a `kitchen.lock` whose `version` is not a dotted number (for example `main`), when `update` runs, then it prints `error: kitchen.lock … Restore it from git history.` on standard error, with no traceback, and exits 1.
- AC2: Given a `kitchen.lock` whose `version` is a dotted number, when `update` runs, then it is not refused because of its version.

## Notes

Implements DEC-INST-04, option (a), decided 2026-11-25 by Ianick Noejovich. It changes the behavior recorded by US-INST-22, whose exception for a malformed lock version no longer holds; the rest of INST-R34 (exit codes, Ctrl-C) is what US-INST-22 records.

## Open questions

- None.
