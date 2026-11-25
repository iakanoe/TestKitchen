---
id: US-CONF-08
type: story
title: Classify files as tests, code, or neither
epic: EP-CONF
source_reqs: [CONF-R13]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a project maintainer, I want each file classified as a test, product code, or neither, so that the gates and checks treat it consistently.

## Acceptance criteria

- AC1: Given a file that matches `tests` and is not excluded, when it is classified, then it is a test file.
- AC2: Given a file that matches `code`, does not match `tests`, and is not excluded, when it is classified, then it is a code file.
- AC3: Given a file that matches both `tests` and `code`, when it is classified, then it is a test file and not a code file.
- AC4: Given a file that matches `ignore`, when it is classified, then it is neither a test file nor a code file, even if it matches `tests` or `code`.
- AC5: Given a file that matches neither `tests` nor `code`, when it is classified, then it is neither.

## Notes

Framework files from `kitchen.lock` are excluded the same way as `ignore`; see US-CONF-09.

## Open questions

- None. Adopted behavior, recorded as the code does it now; a person confirms the requirements.
