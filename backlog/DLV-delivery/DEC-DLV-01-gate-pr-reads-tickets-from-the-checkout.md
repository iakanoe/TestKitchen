---
id: DEC-DLV-01
type: decision
title: gate pr reads tickets and kitchen.yml from the checkout, not from --head
epic: EP-DLV
source_reqs: [DLV-R14, DLV-R16, DLV-R20]
blocked_by: []
owner: Ianick Noejovich
assignee_type: human
status: done
---

## Question

Is this intended? `deliver.py gate pr --head=<rev>` reads the branch history, the tagged tests, and the delivery record at `<rev>`, but reads the ticket (its live criteria, status, branch name, hotfix flag) and `kitchen.yml` (the `code` and `tests` globs, autonomy) from the working tree, so a run whose checkout is not `<rev>` judges `<rev>`'s history against another version of the ticket and configuration.

## Context

- Current: `Project` loads `kitchen.yml` and the backlog from the repository root on disk (`template/scripts/deliver.py:85-94`); `gate_pr` takes the ticket from that backlog (`:679-681`) and uses its live criteria (`:691`), status (`:697`), hotfix flag (`:736`), and the configured autonomy (`:742`), while the history checks, tag counts, and record lookup use the `--head` revision (`:662`, `:688`, `:704-705`).
- Observed 2026-11-25 in a throwaway repository: a branch that passes `gate pr` from its own checkout fails with `FAIL <ID> does not exist` (the base commit has no such ticket file) when the same command, with the same `--head`, runs from a checkout of the base commit.
- `gate merge` already guards against this for itself: it refuses unless the checkout is a clean checkout of the head, with the comment "The gate reads the backlog from this checkout, so it must be the head being merged, unchanged" (`template/scripts/deliver.py:807-813`). `gate pr` has no such check, and its usage line documents `--head=REV` as a free option (`:13`).
- Where the CI templates check out a different commit than the `--head` they pass (for example a host's merge preview of the change request), the ticket and configuration come from that commit. How each CI template checks out belongs to the host epic.
- Likely intended: the gate judges one revision consistently, either by reading everything at `--head` or by refusing a checkout that differs from it.

## Options

None recorded. Proposals, not decided anywhere:

- (a) Keep the current behavior and document that `--head` must be the checked-out commit.
- (b) Read the ticket files and `kitchen.yml` at `--head`.
- (c) Refuse, as `gate merge` does, when the checkout is not `--head`.

## Recommendation

(b) if CI must keep checking a preview commit, since it makes the gate judge exactly the revision it names; otherwise (c), which is the smallest change and matches `gate merge`.

## Decides

- US-DLV-10 (branch, plan rows, and status are judged against the ticket file).
- US-DLV-14 (the hotfix flag and the autonomy level are read from the same files).

## Outcome

- Date: 2026-11-25.
- Answer: Option (b): `deliver.py gate pr` reads the ticket files and `kitchen.yml` at `--head` too, so it judges exactly the revision it names.
- Decided by: Ianick Noejovich.
- Recorded in: requirements DLV-R48; confirmed DLV-R14, DLV-R16, DLV-R20; US-DLV-38; decision log, "gate pr reads tickets and kitchen.yml at --head".
