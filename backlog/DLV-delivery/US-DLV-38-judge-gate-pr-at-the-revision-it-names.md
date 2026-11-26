---
id: US-DLV-38
type: story
title: Judge gate pr at the revision it names
epic: EP-DLV
source_reqs: [DLV-R48]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: ready
refined: 2026-11-26
---

As an agent, reviewer, or CI job, I want `gate pr` to read the ticket files and `kitchen.yml` at `--head`, so that it judges one revision consistently, whatever commit is checked out.

## Acceptance criteria

- AC1: Given ticket files at `<rev>` that differ from those in the checkout, when `deliver.py gate pr --head=<rev>` runs from a checkout of another commit, then its `PASS` and `FAIL` lines and exit code follow the ticket files as they are at `<rev>`.
- AC2: Given a `kitchen.yml` at `<rev>` that differs from the one in the checkout, when `deliver.py gate pr --head=<rev>` runs from a checkout of another commit, then its `PASS` and `FAIL` lines and exit code follow the whole `kitchen.yml` as it is at `<rev>`.
- AC3: Given `--head` names the checked-out commit and the working tree holds uncommitted edits to a ticket file or to `kitchen.yml`, when `deliver.py gate pr` runs, then the edits are ignored and the result follows the committed files.
- AC4: Given a branch that passes `gate pr` from its own checkout, when the same command with the same `--head` runs from a checkout of the base commit, then it prints the same `PASS` and `FAIL` lines and exits with the same code.
- AC5: Given a ticket that exists in the checkout but not at `--head` (or the reverse), when `deliver.py gate pr --head=<rev>` runs, then the verdict follows `--head`: a ticket missing at `--head` prints `FAIL <ID> does not exist`, and a ticket present only at `--head` is judged normally.

## Notes

- Implements DEC-DLV-01, option (b), decided 2026-11-25 by Ianick Noejovich. It changes the behavior recorded by US-DLV-10 (ticket, plan, and status) and US-DLV-14 (hotfix lane and autonomy), which stay as the record of the earlier behavior.
- "The ticket files" means everything the gate reads from them: whether the ticket exists, its type, its live criteria, its status, its file name (the branch name), its epic folder (the record path), and its `hotfix` flag. "The whole `kitchen.yml`" includes the `tests`, `code`, and `ignore` globs and the autonomy level.
- AC3 does for tickets and `kitchen.yml` what US-DLV-09/AC3 already does for the delivery record.
- How each CI template checks out belongs to EP-HOST.
- Replaces no criterion: no criterion of US-DLV-09, US-DLV-10, or US-DLV-14 says which revision the ticket files or `kitchen.yml` are read at.

## Open questions

- None. The decision log records this decision.
