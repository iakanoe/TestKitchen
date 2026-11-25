---
id: US-HOST-14
type: story
title: Refuse a merge sha with a trailing newline
epic: EP-HOST
source_reqs: [HOST-R27]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: draft
---

As a project owner, I want the merge command built only from an exact 40-character sha, so that the one function that defines the allowed merge command validates its input completely.

## Acceptance criteria

- AC1: Given 40 lowercase hexadecimal characters followed by a newline, when a merge command is built, then ValueError is raised before any CLI runs.
- AC2: Given exactly 40 lowercase hexadecimal characters, when a merge command is built, then the sha is accepted and appears unchanged in the command.

## Notes

Implements DEC-HOST-02 (fix), decided 2026-11-25 by Ianick Noejovich. It changes the behavior recorded by US-HOST-07, which stays as the record of the earlier behavior.

## Open questions

- None.
