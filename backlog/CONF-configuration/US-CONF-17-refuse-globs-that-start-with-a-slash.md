---
id: US-CONF-17
type: story
title: Refuse globs that start with a slash
epic: EP-CONF
source_reqs: [CONF-R27]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: draft
---

As a project maintainer, I want a glob that starts with `/` refused when the configuration loads, so that a pattern never loads and then silently matches nothing.

## Acceptance criteria

- AC1: Given a `tests`, `code`, or `ignore` glob that starts with `/`, when the configuration loads, then it fails with a `kitchen.yml:` error, worded like the backslash error, saying that globs are relative to the repository root and never start with `/`.
- AC2: Given a glob that starts with `./` or with a folder name, when the configuration loads, then this rule does not refuse it.

## Notes

Implements DEC-CONF-02, option (a), decided 2026-11-25 by Ianick Noejovich. It changes the behavior recorded by US-CONF-02 (required keys) and US-CONF-07 (glob matching), which stay as the record of the earlier behavior.

## Open questions

- None.
