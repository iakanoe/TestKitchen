---
id: US-HOST-08
type: story
title: Self-test the host adapters offline
epic: EP-HOST
source_reqs: [HOST-R17]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person or CI job checking an installed project, I want the host adapters to test their own parsing without a CLI or network, so that a broken adapter shows up before it is trusted with a merge.

## Acceptance criteria

- AC1: Given the installed scripts, when `python3 scripts/hosts.py --self-test` runs, then it parses recorded gh and glab output without calling any CLI or the network, prints `PASS self-test`, and exits 0.
- AC2: Given a self-test expectation that does not hold, when the self-test runs, then it prints a FAIL line for each failure, ends with `FAIL self-test: <n> failure(s)`, and exits 1.
- AC3: Given any arguments other than `--self-test`, when the script runs, then it prints its usage text and exits 2.

## Notes

- `deliver.py check` runs this self-test, and the installer's doctor runs it too; both belong to other epics.

## Open questions

- None. Adopted behavior, recorded as it is; nothing is open for this story.
