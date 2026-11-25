---
id: US-DLV-39
type: story
title: Leave adopted tickets out of release notes
epic: EP-DLV
source_reqs: [DLV-R49]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: draft
---

As a project maintainer, I want release notes to list only delivered changes, so that behavior recorded by adopt never reads as part of a release.

## Acceptance criteria

- AC1: Given done tickets marked `adopted: true` and a release slice, when `deliver.py release-notes <slice>` runs, then the adopted tickets are not listed.
- AC2: Given no git tag, when `deliver.py release-notes` runs, then adopted tickets are not listed, while the other done stories and tasks are.
- AC3: Given a git tag, when `deliver.py release-notes` runs, then adopted tickets are not listed.
- AC4: Given a selection that holds only adopted tickets, when `deliver.py release-notes` runs, then it prints "No changes.".

## Notes

Implements DEC-DLV-02, option (b), decided 2026-11-25 by Ianick Noejovich. It changes the selection recorded by US-DLV-21, which stays as the record of the earlier behavior; the rest of DLV-R49 (slice refusals, layout) is what US-DLV-21 records.

## Open questions

- None.
