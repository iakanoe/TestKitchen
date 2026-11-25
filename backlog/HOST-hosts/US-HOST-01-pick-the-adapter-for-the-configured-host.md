---
id: US-HOST-01
type: story
title: Pick the adapter for the configured host
epic: EP-HOST
source_reqs: [HOST-R01, HOST-R02]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a workflow script (and the agent or person running it), I want one adapter per host that names the host and its change requests, so that the rest of the workflow talks to GitHub, GitLab, or no host the same way.

## Acceptance criteria

- AC1: Given the configured host is `github`, `gitlab`, or `manual`, when the adapter is requested, then it is named after the host, calls its change requests "pull request", "merge request", or "change request" respectively, and uses the CLI `gh`, `glab`, or none.
- AC2: Given a configured host value that is not one of the three, when the adapter is requested, then the manual adapter is returned.
- AC3: Given the manual host, when a change request is read, then NotSupported (a kind of HostError) is raised saying a person checks and merges it, and no host CLI is called.
- AC4: Given the manual host, when the merge command is requested, then there is none (None), and no host CLI is called.

## Notes

- The host value comes from `kitchen.yml` or the origin URL; validating and detecting it belongs to the configuration epic. Configuration validation already refuses other values, so AC2 is a fallback for direct callers.
- The manual host's open branches are covered by the story on claimed branches.

## Open questions

- None. Adopted behavior, recorded as it is; nothing is open for this story.
