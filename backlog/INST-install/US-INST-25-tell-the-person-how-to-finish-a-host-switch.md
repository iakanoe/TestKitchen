---
id: US-INST-25
type: story
title: Tell the person how to finish a host switch
epic: EP-INST
source_reqs: [INST-R37, INST-R31]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: ready
refined: 2026-11-26
---

As a maintainer switching my project to another host, I want `update` and `doctor` to tell me how to make `kitchen.yml`'s `host:` agree with the installed host, so that I know which setting is left for me to change.

## Acceptance criteria

- AC1: Given an install for one host, when `update --host <another host>` shows its plan, with or without `--dry-run`, then the plan holds a line saying that `host:` in `kitchen.yml` must be set to the new host.
- AC2: Given the same update as a real run that the person confirms, when it finishes writing, then it prints that line again.
- AC3: Given an install for one host, when `update --host <the same host>` or `update` without `--host` runs, then neither its plan nor the end of the run holds the line of AC1.
- AC4: Given `doctor` warns that the host differs from the installed one (US-INST-20/AC1), when it prints the fix, then the fix offers both directions: set `host:` in `kitchen.yml` to the installed host, or run `update --host <the other host>`.

## Notes

- Implements DEC-INST-01, option (a), decided 2026-11-25 by Ianick Noejovich, as made exact on 2026-11-26 (INST-R37 supersedes INST-R30: the line is in the plan, on `--dry-run` too, and after a real run). It changes the behavior recorded by US-INST-16 (host switch on update) and US-INST-20 (doctor's host check), which stay as the record of the earlier behavior.
- `update` still never writes `kitchen.yml` (US-INST-13/AC6). The plan's existing `host: <host>; Claude Code files: …` line is not the line of AC1. A declined confirmation stops as US-INST-07/AC4 records. The old host's CI files stay on disk (US-INST-16/AC2).
- Replaces no criterion: US-INST-20/AC1's suggestion of `update --host <that host>` is still one of the two directions AC4 offers.

## Open questions

- None. The decision log records this decision, and the decision of 2026-11-26 said when the line prints.
