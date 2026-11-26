---
id: TASK-DEF-03
type: task
title: Match the Done paragraph and guide to --gaps
epic: EP-DEF
source_reqs: [DEF-R44]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: in-progress
refined: 2026-11-26
---

The "Done" paragraph of `playbooks/define.md` and the "Done means no gaps" section of `guide/define.md` describe "fully defined" differently from what `backlog_check.py --gaps` checks. This task rewords both; `--gaps` does not change.

## Acceptance criteria

- AC1: The "Done" paragraph of `template/playbooks/define.md` lists requirements still marked `(observed in code)` and draft stories and tasks among what keeps the product from being fully defined.
- AC2: The same paragraph says that a requirement is covered when a story or task that is not deferred cites it, and no longer says "covered by ready or done tickets".
- AC3: `guide/define.md`, "Done means no gaps", lists draft stories and tasks among the gaps, says that a requirement is covered when a story or task that is not deferred cites it, and no longer says "covered by ready or done tickets".

## Notes

- Implements DEC-DEF-03, option (a), decided 2026-11-25 by Ianick Noejovich, as widened on 2026-11-26 to `guide/define.md` and to draft stories and tasks (DEF-R44 supersedes DEF-R42). Filed on 2026-11-25 as US-DEF-32; it became this task on 2026-11-26 because only a reviewer can check its criteria.
- The final review verifies each criterion by reading the files; no test can.
- `--gaps` lists each draft story or task and each unconfirmed observed requirement (DEF-R20); `guide/define.md` already lists the unconfirmed observed requirements.
- The playbook wording it changes is what US-DEF-29 records. The product copy is `template/playbooks/define.md`; the root copy is an installed release that changes only through `init.py update`. `guide/` is not installed and is edited in place.

## Open questions

- None. The decision log records this decision.
