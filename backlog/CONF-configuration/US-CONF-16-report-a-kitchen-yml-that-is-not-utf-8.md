---
id: US-CONF-16
type: story
title: Report a kitchen.yml that is not UTF-8
epic: EP-CONF
source_reqs: [CONF-R26]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: draft
---

As a project maintainer, I want a `kitchen.yml` saved in another encoding reported as a configuration error, so that I see what to fix instead of a traceback.

## Acceptance criteria

- AC1: Given a `kitchen.yml` whose bytes are not valid UTF-8, when the configuration loads, then it fails with the configuration error `kitchen.yml: not valid UTF-8` and no traceback.
- AC2: Given that file, when `python3 scripts/kitchen_lib.py --config` or `python3 scripts/backlog_check.py` runs, then the problem prints as an `ERROR` line and the run exits 1.

## Notes

Implements DEC-CONF-01, option (a), decided 2026-11-25 by Ianick Noejovich. It changes the behavior recorded by US-CONF-01, which stays as the record of the earlier behavior.

## Open questions

- None.
