---
id: US-DLV-14
type: story
title: Enforce the hotfix lane and supervised approvals in gate pr
epic: EP-DLV
source_reqs: [DLV-R20]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a maintainer, I want `gate pr` to require a hotfix's reason and follow-up and a supervised project's named approvals, so that the lanes that skip or add steps leave a record.

## Acceptance criteria

- AC1: Given a `hotfix: true` ticket and no Decisions bullet ending `Log: <entry title>`, when `deliver.py gate pr` runs, then it fails saying Decisions needs a bullet giving why the hotfix lane was used.
- AC2: Given a `hotfix: true` ticket and a Gaps found section that names no ticket other than this one, when `deliver.py gate pr` runs, then it fails saying Gaps found must name the follow-up ticket.
- AC3: Given a `hotfix: true` ticket with both, when `deliver.py gate pr` runs, then the hotfix checks pass.
- AC4: Given autonomy `supervised` and a Plan without `Plan approved by: <name>` or without `Tests approved by: <name>`, when `deliver.py gate pr` runs, then it fails for each missing line.
- AC5: Given autonomy `supervised` and an approval line whose name is empty, `TBD`, `-`, or starts with `<`, when `deliver.py gate pr` runs, then it does not count; a real name passes.

## Notes

Adopted 2026-11-25 from `template/scripts/deliver.py` (installed copy `scripts/deliver.py`); the criteria describe what the code does now and are not yet confirmed by a person. Under `supervised`, a hotfix also needs both approvals (decision-log entry "Script choices made while building v0.1").

## Open questions

- None. Adopted behavior.
