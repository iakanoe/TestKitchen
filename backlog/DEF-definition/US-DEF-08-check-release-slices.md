---
id: US-DEF-08
type: story
title: Check release slices
epic: EP-DEF
source_reqs: [DEF-R11]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person ordering work into releases, I want slice assignments checked, so that no slice waits on work planned for a later one.

## Acceptance criteria

- AC1: Given `kitchen.yml` lists releases and a ticket's `release` is not one of them, when `backlog_check.py` runs, then it reports an error naming the listed releases.
- AC2: Given releases are listed and a deferred ticket's `release` is not the last slice, when `backlog_check.py` runs, then it reports an error that deferred tickets go to the last slice.
- AC3: Given releases are listed and a ticket's unfinished blocker is in a later slice than the ticket, when `backlog_check.py` runs, then it reports an error naming the blocker and its slice.
- AC4: Given releases are listed and every ticket's slice is valid, when `backlog_check.py` runs, then no release error is reported.
- AC5: Given `kitchen.yml` lists no releases and a ticket has a `release`, when `backlog_check.py` runs, then it prints a warning that the release is ignored and exits 0.

## Notes

- Adopted 2026-11-25 from existing behavior: the behavior is in `template/scripts/backlog_check.py`.
- The criteria describe what happens now; confirmation happens on the cited `(observed in code)` requirements.

## Open questions

- None. This story records behavior that already exists; anything that looks unintended is filed as a decision on the epic.
