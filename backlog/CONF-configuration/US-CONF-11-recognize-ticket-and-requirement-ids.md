---
id: US-CONF-11
type: story
title: Recognize ticket and requirement IDs
epic: EP-CONF
source_reqs: [CONF-R17]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a maintainer reading the backlog with the scripts, I want one fixed format for epic codes, ticket IDs, criterion references, and requirement IDs, so that every tool reads the same references the same way.

## Acceptance criteria

- AC1: Given an epic code of an upper-case letter and one to nine upper-case letters or digits, when an ID is parsed, then it is accepted; a code in lower case, of one character, or longer than ten characters is not.
- AC2: Given `EP-` plus a code, or `US-`, `TASK-`, `DEC-`, or `SPK-` plus a code, `-`, and two or more digits, when an ID is parsed, then it yields its prefix, code, and number; a one-digit number, an epic ID with a number, or any other prefix is not an ID.
- AC3: Given a ticket ID in free text, when mentions are read, then it counts only when not preceded by a word character or `-` and not followed by a word character, and an epic ID also not followed by `-`.
- AC4: Given a story or task ID followed by `/AC` and a number in free text, when criterion references are read, then it yields that ticket and criterion number.
- AC5: Given a requirements file, when requirement IDs are read, then an ID is a code, `-R`, and two or more digits, and a requirement is defined only by a line `- <ID>: <text>`.
- AC6: Given ticket IDs that differ in number length, when they are sorted, then they sort by number rather than as text.

## Notes

Two or more digits keep numbers sorting and reading the same everywhere (code comment, observed). Requirement file naming and duplicate checks belong to the backlog-check epic.

## Open questions

- None. Adopted behavior, recorded as the code does it now; a person confirms the requirements.
