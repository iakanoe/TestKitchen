---
id: US-DEF-31
type: story
title: Say that readiness rules skip epics
epic: EP-DEF
source_reqs: [DEF-R41]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: draft
---

As a person writing tickets, I want `backlog/README.md` to say which tickets the readiness rules apply to, so that the rule I read matches what the check enforces.

## Acceptance criteria

- AC1: Given `backlog/README.md`, "Readiness", when it is read, then it says that the readiness rules apply to tickets other than epics.
- AC2: Given a `ready` epic with owner `TBD`, when `backlog_check.py` runs, then it reports no readiness error for the epic.

## Notes

Implements DEC-DEF-02, option (b), decided 2026-11-25 by Ianick Noejovich. The check's behavior stays as US-DEF-06 records it; only the README wording that US-DEF-18 (shipped skeletons and guides) records changes. The product copy is `template/backlog/README.md`; the root copy is an installed release that changes only through `init.py update`.

## Open questions

- None.
