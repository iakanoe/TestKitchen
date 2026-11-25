---
id: US-CONF-04
type: story
title: Configure release slices
epic: EP-CONF
source_reqs: [CONF-R08]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a project maintainer, I want to list release slices in order in `kitchen.yml`, so that slice rules turn on only when I declare them.

## Acceptance criteria

- AC1: Given `releases` is a list of slice names, when the configuration is loaded, then the slices are kept in the given order.
- AC2: Given `releases` is absent or left without a value, when the configuration is loaded, then release slices are off.
- AC3: Given `releases` is an empty list, is not a list, or holds a blank or non-text name such as a number, when the configuration is loaded, then an error says it must be a non-empty list of slice names and to remove the key to turn slices off.
- AC4: Given `releases` lists the same name twice, when the configuration is loaded, then an error says a slice is listed twice.

## Notes

Slice names are compared as text, so YAML numbers are refused (code comment, observed). Names are not trimmed. The slice rules themselves belong to the backlog-check and delivery epics.

## Open questions

- None. Adopted behavior, recorded as the code does it now; a person confirms the requirements.
