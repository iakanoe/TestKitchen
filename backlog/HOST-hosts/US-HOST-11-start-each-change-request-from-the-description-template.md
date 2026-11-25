---
id: US-HOST-11
type: story
title: Start each change request from the description template
epic: EP-HOST
source_reqs: [HOST-R23]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As an agent or person opening a change request, I want the host to prefill the description with the sections the checks read, so that every gap, decision, test change, and review lands where the gates look for it.

## Acceptance criteria

- AC1: Given the GitHub host, when a pull request is opened, then its description starts from a template with the sections Ticket, Plan (with a criterion-and-tests table and a "Constrained by:" line), Gaps found, Decisions, Platform changes, Test changes, Review report, and Checks, each with guidance, and "None" as the default of Gaps found, Decisions, Platform changes, and Test changes.
- AC2: Given the GitLab host, when a merge request is opened with the default template, then its description has the same sections and defaults, and the Ticket guidance says GitLab CI reads the committed delivery record, so after every edit of the description the record is rewritten, committed, and pushed.

## Notes

- The sections and what they must contain are defined by the delivery workflow and checked by `backlog_check.py --pr-body` and `deliver.py gate pr` (delivery epic); this story covers only the templates' content.
- `deliver.py pr-body` writes a whole description; the templates are the starting point for one written by hand.

## Open questions

- None. Adopted behavior, recorded as it is; nothing is open for this story.
