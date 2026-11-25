---
id: US-HOST-13
type: story
title: Report unreadable host CLI output
epic: EP-HOST
source_reqs: [HOST-R26]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: draft
---

As an agent or person running the workflow scripts, I want host CLI output that is not JSON reported as a host error, so that the scripts give their own message instead of a traceback.

## Acceptance criteria

- AC1: Given `gh pr list` or `glab mr list` exits 0 but prints output that is not JSON, when an adapter lists the branches of open change requests, then it raises a HostError naming the command.
- AC2: Given a host CLI call that reads a change request exits 0 but prints output that is not JSON, when an adapter reads the change request, then it raises a HostError naming the command.
- AC3: Given such output while listing open branches, when `deliver.py next` or `deliver.py status` runs, then it ends without a traceback.

## Notes

Implements DEC-HOST-01 (fix), decided 2026-11-25 by Ianick Noejovich. It changes the behavior recorded by US-HOST-02 (open branches) and US-HOST-03 (failing host CLI), which stay as the record of the earlier behavior. `next` and `status` already handle a HostError (US-DLV-01, US-DLV-20).

## Open questions

- None.
