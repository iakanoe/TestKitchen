---
id: US-DLV-21
type: story
title: Print release notes from done tickets
epic: EP-DLV
source_reqs: [DLV-R27]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person releasing the product, I want `deliver.py release-notes` to list the done stories and tasks of a slice or since the last tag, so that release notes come from the record and never from invented text.

## Acceptance criteria

- AC1: Given releases are on and a listed slice, when `deliver.py release-notes <slice>` runs, then it prints `# Release notes: <slice>` and the done stories and tasks whose `release` is that slice.
- AC2: Given a slice argument while `kitchen.yml` lists no releases, or a slice not in the list, when `deliver.py release-notes` runs, then it fails saying there are no slices or that the slice is not in the releases.
- AC3: Given no slice argument and a git tag, when `deliver.py release-notes` runs, then it prints `# Release notes since <tag>` and the done stories and tasks whose delivery record (including a `-cr<n>` one) was added since the last tag.
- AC4: Given no slice argument and no git tag, when `deliver.py release-notes` runs, then it prints `# Release notes` and every done story and task.
- AC5: Given chosen tickets, when `deliver.py release-notes` prints them, then each story appears as `- <its "so that" outcome, capitalized, or its title>. (<ID>)` under a heading with its epic's title, and tasks and hotfix stories appear as `- <title> (<ID>)` (adding `, hotfix`) under `## Other changes`.
- AC6: Given no ticket is chosen, when `deliver.py release-notes` runs, then it prints the heading and `No changes.`.

## Notes

Adopted 2026-11-25 from `template/scripts/deliver.py` (installed copy `scripts/deliver.py`); the criteria describe what the code does now and are not yet confirmed by a person. Adopted stories are done stories, so they are included by the slice and no-tag rules; this epic's open decisions ask whether that is intended.

## Open questions

- None. Adopted behavior; whether adopted stories belong in release notes is asked separately in this epic's open decisions.
