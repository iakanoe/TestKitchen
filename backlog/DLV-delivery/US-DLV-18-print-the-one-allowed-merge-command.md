---
id: US-DLV-18
type: story
title: Print the one allowed merge command
epic: EP-DLV
source_reqs: [DLV-R24]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As an agent or person merging, I want `deliver.py merge-command` to print the only merge command the workflow allows, so that nobody types a merge of their own.

## Acceptance criteria

- AC1: Given the GitHub or GitLab host and a full sha, when `deliver.py merge-command <N> --head=<sha>` runs, then it prints the host adapter's merge command pinned to that sha, shell-quoted on one line, and exits 0.
- AC2: Given the manual host, when `deliver.py merge-command` runs, then it fails saying there is no merge command and a person merges, and exits 1.
- AC3: Given autonomy `pr` or `supervised`, when `deliver.py merge-command` runs, then it still prints the command and exits 0, with `NOTE autonomy is `<level>`: a person runs this merge, not an agent` on standard error.
- AC4: Given a sha the host adapter refuses (US-HOST-07/AC4), when `deliver.py merge-command` runs, then it fails with the adapter's message asking for the full 40-character sha.

## Notes

Adopted 2026-11-25 from `template/scripts/deliver.py` (installed copy `scripts/deliver.py`); the criteria describe what the code does now and are not yet confirmed by a person. The exact command per host is defined by the host adapter (host epic).

## Open questions

- None. Adopted behavior.
