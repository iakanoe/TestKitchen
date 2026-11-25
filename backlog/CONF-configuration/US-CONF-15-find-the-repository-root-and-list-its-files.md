---
id: US-CONF-15
type: story
title: Find the repository root and list its files
epic: EP-CONF
source_reqs: [CONF-R21, CONF-R22]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a maintainer running the scripts from anywhere, I want them to find their own project and list its files the way git sees them, so that results never depend on the current folder.

## Acceptance criteria

- AC1: Given the scripts run from a subfolder or from another folder, when the repository root is looked up, then it is the git top level of the folder holding the scripts.
- AC2: Given the scripts are not inside a git repository, when the repository root is looked up, then it is the parent of the scripts folder.
- AC3: Given a working tree with tracked files, new files not yet added, ignored files, and deleted files, when the files are listed, then the list holds the tracked and new files, sorted and `/`-separated, and leaves out ignored and deleted ones.
- AC4: Given a revision, when the files are listed at it, then the list holds exactly the files of that commit.
- AC5: Given a folder outside any git repository, when the files are listed, then the list holds every file under it except inside hidden folders.

## Notes

A new test file counts before it is added to git, so a test written but not staged is still seen (code comment, observed).

## Open questions

- None. Adopted behavior, recorded as the code does it now; a person confirms the requirements.
