---
id: US-HOST-03
type: story
title: Report a missing or failing host CLI
epic: EP-HOST
source_reqs: [HOST-R06]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As an agent or person running the workflow scripts, I want a clear error when the host CLI is missing or fails, so that I know what to fix and nothing proceeds on a guess.

## Acceptance criteria

- AC1: Given the host's CLI is not installed or not on PATH, when the adapter calls it, then a HostError says the CLI is not installed or not on PATH and that the host needs it.
- AC2: Given the host's CLI exits non-zero with a message on stderr, when the adapter calls it, then a HostError names the command and carries that message.
- AC3: Given the host's CLI exits non-zero with nothing on stderr, when the adapter calls it, then the HostError carries its stdout instead.

## Notes

- A signed-out CLI is one case of AC2 (for example `gh` exiting 4 with "not logged in").
- A CLI that exits 0 with output that is not JSON is not covered here: DEC-HOST-01.

## Open questions

- None. Adopted behavior, recorded as it is; nothing is open for this story.
