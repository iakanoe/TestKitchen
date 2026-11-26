---
id: TASK-DEF-02
type: task
title: Say that readiness rules skip epics
epic: EP-DEF
source_reqs: [DEF-R43]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: in-progress
refined: 2026-11-26
---

`backlog/README.md` and `guide/concepts.md` describe the readiness rules as if they applied to every ticket, while `backlog_check.py` applies them to tickets other than epics. This task makes both texts say so; the check does not change.

## Acceptance criteria

- AC1: `template/backlog/README.md`, "Readiness", says that the readiness rules apply to tickets other than epics.
- AC2: `guide/concepts.md`, "Readiness", says that the readiness rules apply to tickets other than epics.

## Notes

- Implements DEC-DEF-02, option (b), decided 2026-11-25 by Ianick Noejovich, as widened on 2026-11-26 to `guide/concepts.md` (DEF-R43 supersedes DEF-R41). Filed on 2026-11-25 as US-DEF-31; it became this task on 2026-11-26 because only a reviewer can check its criteria.
- The final review verifies each criterion by reading the files; no test can.
- The check's behavior stays as US-DEF-06/AC1 records it: an epic is left out of the owner check whatever its status or owner (`TBD` or empty).
- The README wording it changes is what US-DEF-18/AC3 records. The product copy is `template/backlog/README.md`; the root copy is an installed release that changes only through `init.py update`. `guide/` is not installed and is edited in place.

## Open questions

- None. The decision log records this decision.
