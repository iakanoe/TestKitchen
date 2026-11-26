---
id: US-CONF-17
type: story
title: Refuse globs that start with a slash
epic: EP-CONF
source_reqs: [CONF-R28]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: ready
refined: 2026-11-26
---

As a project maintainer, I want a glob that starts with `/` refused when the configuration loads, so that a pattern never loads and then silently matches nothing.

## Acceptance criteria

- AC1: Given a `tests`, `code`, or `ignore` glob that starts with `/` (such as `/vendor/**`), when the configuration loads, then it fails with one `kitchen.yml:` error that names the key, lists the offending globs, and says that globs are relative to the repository root and never start with `/`.
- AC2: Given a glob that starts with `/` only once its surrounding whitespace is trimmed (`" /vendor/**"`) or once a leading `./` is removed (`.//vendor/**`), when the configuration loads, then it fails with the same error.
- AC3: Given one key holding both a glob with a backslash and a glob that starts with `/`, when the configuration loads, then both errors are reported, one line each.

## Notes

- Implements DEC-CONF-02, option (a), decided 2026-11-25 by Ianick Noejovich, as widened on 2026-11-26 (CONF-R28 supersedes CONF-R27: whitespace and a leading `./` are removed before the check).
- The backslash error this one follows names the key and lists the offending globs (US-CONF-02/AC3); every problem is reported at once (CONF-R05, US-CONF-01/AC6).
- A glob that starts with a folder name or with `./` and a folder name (`./src/**`) still loads and matches as US-CONF-02 and US-CONF-07/AC6 record; this story does not restate that.
- Replaces no criterion: no criterion of US-CONF-02 or US-CONF-07 says that a glob starting with `/` loads.

## Open questions

- None. The decision log records this decision, and the widening of 2026-11-26 settled the whitespace and `./` cases.
