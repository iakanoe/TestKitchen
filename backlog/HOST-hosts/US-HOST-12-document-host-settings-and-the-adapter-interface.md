---
id: US-HOST-12
type: story
title: Document host settings and the adapter interface
epic: EP-HOST
source_reqs: [HOST-R24, HOST-R25]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person setting up a project, or a contributor adding a host, I want one guide that states the host settings the workflow needs and how the adapters work, so that merges do not fail on host settings and a new host can be added the same way.

## Acceptance criteria

- AC1: Given `guide/hosts.md`, when a person reads its host settings section, then it states that merge commits must be allowed (on GitLab, the merge method "Merge commit") because squash and rebase rewrite the freeze and reviewed commits, that GitLab merged results pipelines must be off because the adapter treats them as pending, and that a CI job named `check` must run on every change request.
- AC2: Given `guide/hosts.md`, when a person reads it, then it explains how the host is chosen, what each adapter runs, what the merge gate asks of every host, the adapter interface, and the steps to add a host.

## Notes

- These settings are documented, not checked by any script; host branch protection is recommended there as the only rule that holds against merges made outside the workflow.
- Small differences between the guide and the code, recorded as found on 2026-11-25: the guide's `gh pr list` line omits `--limit 1000`, and its interface listing omits the change request's `mergeable_detail` field and GitLab's passed-through `locked` state.

## Open questions

- None. Adopted behavior, recorded as it is; nothing is open for this story.
