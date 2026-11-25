---
id: US-DLV-38
type: story
title: Judge gate pr at the revision it names
epic: EP-DLV
source_reqs: [DLV-R48]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: draft
---

As an agent, reviewer, or CI job, I want `gate pr` to read the ticket and `kitchen.yml` at `--head`, so that it judges one revision consistently, whatever commit is checked out.

## Acceptance criteria

- AC1: Given a checkout of another commit than `--head`, when `deliver.py gate pr --head=<rev>` runs, then it reads the ticket files (live criteria, status, branch name, hotfix flag) at `<rev>`.
- AC2: Given a checkout of another commit than `--head`, when `deliver.py gate pr --head=<rev>` runs, then it reads `kitchen.yml` (the `code` and `tests` globs and the autonomy level) at `<rev>`.
- AC3: Given a branch that passes `gate pr` from its own checkout, when the same command with the same `--head` runs from a checkout of the base commit, then it gives the same result.

## Notes

Implements DEC-DLV-01, option (b), decided 2026-11-25 by Ianick Noejovich. It changes the behavior recorded by US-DLV-10 (ticket, plan, and status) and US-DLV-14 (hotfix lane and autonomy), which stay as the record of the earlier behavior. How each CI template checks out belongs to EP-HOST.

## Open questions

- None.
