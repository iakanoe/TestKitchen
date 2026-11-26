---
id: US-DLV-39
type: story
title: Leave adopted tickets out of release notes
epic: EP-DLV
source_reqs: [DLV-R49]
blocked_by: [US-DEF-33]
owner: Ianick Noejovich
assignee_type: either
status: ready
refined: 2026-11-26
---

As a project maintainer, I want release notes to list only delivered changes, so that behavior recorded by adopt never reads as part of a release.

## Acceptance criteria

- AC1: Given releases are on and a listed slice holding done stories and tasks, some marked `adopted: true`, when `deliver.py release-notes <slice>` runs, then it prints `# Release notes: <slice>` and the done stories and tasks of that slice that are not adopted, and no adopted ticket.
- AC2: Given no slice argument, a git tag, and done stories and tasks whose delivery record (a `-cr<n>` one included) was added since the last tag, some marked `adopted: true`, when `deliver.py release-notes` runs, then it prints `# Release notes since <tag>` and those that are not adopted, and no adopted ticket.
- AC3: Given no slice argument, no git tag, and done stories and tasks, some marked `adopted: true`, when `deliver.py release-notes` runs, then it prints `# Release notes` and every done story and task that is not adopted, and no adopted ticket.
- AC4: Given a run whose chosen tickets would all be adopted, when `deliver.py release-notes` runs, then it prints the heading and `No changes.`.

## Notes

- Implements DEC-DLV-02, option (b), decided 2026-11-25 by Ianick Noejovich. The slice refusals (US-DLV-21/AC2), the layout (US-DLV-21/AC5), and "No changes." for an empty selection (US-DLV-21/AC6) stay as US-DLV-21 records them.
- Replaces (to become a `replaces:` field once US-DEF-33 is delivered): US-DLV-21/AC1, US-DLV-21/AC3, US-DLV-21/AC4, which list adopted tickets. AC1 to AC3 restate what those criteria say about the headings and the non-adopted tickets, because that part stays true and must not lose its criterion when they are crossed out.

## Open questions

- None. The decision log records this decision.
