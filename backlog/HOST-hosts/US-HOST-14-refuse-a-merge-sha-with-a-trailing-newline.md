---
id: US-HOST-14
type: story
title: Refuse a merge sha with a trailing newline
epic: EP-HOST
source_reqs: [HOST-R27]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: ready
refined: 2026-11-26
---

As a project owner, I want the merge command built only from an exact 40-character sha, so that the one function that defines the allowed merge command validates its input completely.

## Acceptance criteria

- AC1: Given the GitHub or the GitLab host and a head sha of 40 lowercase hexadecimal characters followed by a newline, when the merge command is built, then ValueError is raised before any host CLI runs.

## Notes

- Implements DEC-HOST-02 (fix), decided 2026-11-25 by Ianick Noejovich. It changes the behavior recorded by US-HOST-07, which stays as the record of the earlier behavior.
- US-HOST-07/AC1 and AC2 keep an exact 40-character sha building the command unchanged.
- The manual host builds no merge command, so it has no sha to check.
- Replaces no criterion: US-HOST-07/AC4 already says a sha that is not exactly 40 lowercase hexadecimal characters raises ValueError; this story makes the code meet it for a trailing newline.

## Open questions

- None. The decision log records this decision.
