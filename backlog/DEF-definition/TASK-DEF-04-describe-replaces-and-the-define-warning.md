---
id: TASK-DEF-04
type: task
title: Describe replaces and the define warning
epic: EP-DEF
source_reqs: [DEF-R46]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: in-progress
refined: 2026-11-26
---

The define playbook and the backlog conventions say a `done` ticket is never rewritten, but not how a new definition retires a done ticket's criterion. This task adds the `replaces:` field, the warning `/define` gives, and the one allowed edit of a done ticket to both texts.

## Acceptance criteria

- AC1: `template/playbooks/define.md` says that when a new definition contradicts a live criterion of a `done` ticket, adopted or not, the agent warns the person and shows that criterion before writing, and on a yes the new ticket lists it under `replaces:`.
- AC2: Wherever `template/playbooks/define.md` says that a `done` ticket is never rewritten, it names crossing a replaced criterion out at delivery as the one allowed edit.
- AC3: `template/backlog/README.md` documents `replaces:` in its frontmatter example and field list as it documents `fixes:`, and its rule that a `done` ticket is never rewritten names the same one allowed edit.

## Notes

- Implements DEC-DEF-04, decided 2026-11-26 by Ianick Noejovich. The delivery side (the crossing out and its gate) is US-DLV-41 and TASK-DLV-02.
- The final review verifies each criterion by reading the files; no test can.
- The product copies are under `template/`; the root copies are an installed release that changes only through `init.py update`.

## Open questions

- None. The decision log records this decision.
