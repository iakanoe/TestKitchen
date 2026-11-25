---
id: US-CONF-03
type: story
title: Validate optional settings and fill their defaults
epic: EP-CONF
source_reqs: [CONF-R06, CONF-R07]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a project maintainer, I want optional settings to have defaults and clear errors, so that I only write what I change and a wrong value never passes silently.

## Acceptance criteria

- AC1: Given none of the optional keys, when the configuration is loaded, then it has no check command, no verify text, autonomy `merge`, split threshold 6, self-contained tickets off, release slices off, and an empty ignore list.
- AC2: Given `check_command` or `verify` left without a value, when the configuration is loaded, then it counts as absent; given a blank or non-text value, then an error says it must be a non-empty string.
- AC3: Given `autonomy` is anything other than `merge`, `pr`, or `supervised`, including a key left without a value, when the configuration is loaded, then an error lists the three allowed values.
- AC4: Given `split_threshold` is zero, negative, a decimal, true or false, or left without a value, when the configuration is loaded, then an error says it must be a positive whole number; given a positive whole number, then that number is used.
- AC5: Given `self_contained_tickets` is anything other than true or false, including a key left without a value, when the configuration is loaded, then an error says it must be true or false.
- AC6: Given `ignore` is an empty list, when the configuration is loaded, then nothing is ignored; given it is not a list, is left without a value, or holds a blank or non-text entry, then an error says it must be a list of glob strings.

## Notes

A key left without a value counts as absent for `check_command`, `verify`, `host`, and `releases`, but is an error for `autonomy`, `split_threshold`, `self_contained_tickets`, and `ignore` (observed; init.py writes optional keys as comments, so this rarely arises). What each setting does once loaded belongs to the epics that use it.

## Open questions

- None. Adopted behavior, recorded as the code does it now; a person confirms the requirements.
