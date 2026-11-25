---
id: US-CONF-02
type: story
title: Validate the required keys
epic: EP-CONF
source_reqs: [CONF-R02, CONF-R03, CONF-R06, CONF-R12]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a project maintainer, I want the three required keys checked when the configuration loads, so that every script agrees on which files are tests, which are code, and how the tests run.

## Acceptance criteria

- AC1: Given `tests` or `code` is missing, when the configuration is loaded, then an error names the key as required and shows an example list of globs.
- AC2: Given `tests` or `code` is an empty list, is not a list, or holds a blank or non-text entry, when the configuration is loaded, then an error says it must be a non-empty list of glob strings and shows the value received.
- AC3: Given a glob in `tests`, `code`, or `ignore` that contains a backslash, when the configuration is loaded, then an error says globs use `/` between folders and lists the offending globs.
- AC4: Given `test_command` is missing, left without a value, blank, or not text, when the configuration is loaded, then an error says it is required or must be a non-empty string.
- AC5: Given a `test_command` that contains neither `{files}` nor `{report}`, when the configuration is loaded, then it loads without an error.
- AC6: Given globs or a `test_command` with surrounding whitespace, when the configuration is loaded, then the loaded values have that whitespace trimmed.

## Notes

AC5 records observed behavior: `guide/configuration.md` says `{report}` is required, and that is enforced by the red gate and the installer's doctor, not when the configuration loads. A glob starting with `/` loads without an error and matches nothing; DEC-CONF-02 asks whether it should be rejected like a backslash.

## Open questions

- None. Adopted behavior, recorded as the code does it now; a person confirms the requirements.
- None. Leading-slash globs are outside these criteria and are asked in DEC-CONF-02.
