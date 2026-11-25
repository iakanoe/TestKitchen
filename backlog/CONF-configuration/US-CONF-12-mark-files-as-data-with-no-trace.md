---
id: US-CONF-12
type: story
title: Mark files as data with the no-trace marker
epic: EP-CONF
source_reqs: [CONF-R18]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a maintainer of a tool that handles ticket text, I want to mark a file as data, so that its example tickets, tags, and to-do markers are not read as real references.

## Acceptance criteria

- AC1: Given a file whose marker appears only after its tenth line, when the file is read, then the marker has no effect.
- AC2: Given the marker inside any comment syntax, such as after `#` or `//`, when the file is read, then the marker is recognized.
- AC3: Given a marked file that matches `tests` or `code`, when it is classified, then it keeps that classification, so the gates still see changes to it.

## Notes

Decision log, "The `test-kitchen: no-trace` marker". Only the first lines count, so the marker cannot hide in the middle of a file. The scans that honor it belong to the backlog-check and delivery epics (US-DEF-11/AC4 for `backlog_check.py`, US-DLV-05/AC1 for `gate red`); this story owns the marker's rule.

## Open questions

- None. Adopted behavior, recorded as the code does it now; a person confirms the requirements.
