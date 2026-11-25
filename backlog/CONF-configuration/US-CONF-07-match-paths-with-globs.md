---
id: US-CONF-07
type: story
title: Match repository paths with globs
epic: EP-CONF
source_reqs: [CONF-R11]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a project maintainer, I want globs that mean the same thing on every system, so that the same `kitchen.yml` classifies the same files everywhere.

## Acceptance criteria

- AC1: Given a pattern with `**` as a whole segment, when a path is matched, then it matches any number of folders including none: a folder followed by `/**` covers its whole tree but not a sibling folder whose name merely starts the same, `**/` at the start matches at the root and at any depth, and `a/**/b` also matches `a/b`.
- AC2: Given a pattern with `**` inside a segment, when a path is matched, then the `**` matches any characters, `/` included.
- AC3: Given a pattern with `*`, when a path is matched, then it matches any run of characters within one folder name and never crosses `/`.
- AC4: Given a pattern with `?`, when a path is matched, then it matches exactly one character other than `/`.
- AC5: Given a pattern with bracket or brace characters, when a path is matched, then those characters match only themselves.
- AC6: Given a pattern or a path that starts with `./`, when they are compared, then the `./` is ignored, and a match always covers the whole path.

## Notes

Brace expansion and bracket classes are left out on purpose so a pattern reads the same in every shell and language (decision log, "Script choices made while building v0.1").

## Open questions

- None. Adopted behavior, recorded as the code does it now; a person confirms the requirements.
