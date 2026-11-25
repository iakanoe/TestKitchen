---
id: US-INST-25
type: story
title: Tell the person how to finish a host switch
epic: EP-INST
source_reqs: [INST-R30, INST-R31]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: draft
---

As a maintainer switching my project to another host, I want `update` and `doctor` to tell me how to make `kitchen.yml` agree with the installed host, so that the scripts, the CI files, and `doctor` end up on the same host.

## Acceptance criteria

- AC1: Given an install for one host, when `update --host <another host>` runs, then it prints that `host:` in `kitchen.yml` must be set to the new host, and `kitchen.yml` is left unchanged.
- AC2: Given an install for one host, when `update --host <the same host>` runs, then it prints no line about `host:` in `kitchen.yml`.
- AC3: Given `kitchen.yml` or the `origin` remote names another host than the one the CI files were installed for, when `doctor` runs, then its fix offers both directions: set `host:` in `kitchen.yml` to the installed host, or run `update --host <the other host>`.

## Notes

Implements DEC-INST-01, option (a), decided 2026-11-25 by Ianick Noejovich. It changes the behavior recorded by US-INST-16 (host switch on update) and US-INST-20 (doctor's host check), which stay as the record of the earlier behavior. `update` still never writes `kitchen.yml` (INST-R17), and `doctor` still warns on the mismatch (INST-R25); only its fix text changes.

## Open questions

- None.
