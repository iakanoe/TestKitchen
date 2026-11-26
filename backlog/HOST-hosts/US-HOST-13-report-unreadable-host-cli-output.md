---
id: US-HOST-13
type: story
title: Report unreadable host CLI output
epic: EP-HOST
source_reqs: [HOST-R26]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: ready
refined: 2026-11-26
---

As an agent or person running the workflow scripts, I want host CLI output that is not JSON reported as a host error, so that the scripts give their own message instead of a traceback.

## Acceptance criteria

- AC1: Given `gh pr list` (GitHub) or `glab mr list` (GitLab) exits 0 but prints output that is neither empty nor JSON, when the adapter lists the branches of open change requests, then it raises a HostError naming the command.
- AC2: Given `gh pr view` (GitHub) or `glab mr view` (GitLab) exits 0 but prints output that is not JSON, or the GitLab jobs call `glab api --paginate projects/:fullpath/pipelines/<id>/jobs` exits 0 but prints output that is neither empty nor JSON, when the adapter reads a change request, then it raises a HostError naming the command.

## Notes

- Implements DEC-HOST-01 (fix), decided 2026-11-25 by Ianick Noejovich. It changes the behavior recorded by US-HOST-02 (open branches) and US-HOST-03 (failing host CLI), which stay as the record of the earlier behavior.
- `deliver.py next` and `status` already turn a HostError from the listing into their own message: `next` prints `FAIL cannot tell which branches are taken: …` and exits 1 (US-DLV-01/AC5), and `status` falls back to the branches seen at the last fetch with a NOTE (US-DLV-20/AC2).
- Replaces no criterion: US-HOST-02 and US-HOST-03 leave this case to their Notes.

## Open questions

- Empty output from a list command: SPK-HOST-01 will show what glab prints. Until decided: empty output counts as no open change requests (today's behavior), and AC1 and AC2 leave empty list output out.
