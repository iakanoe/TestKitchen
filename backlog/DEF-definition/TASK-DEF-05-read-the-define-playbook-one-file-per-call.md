---
id: TASK-DEF-05
type: task
title: Read the define playbook one file per call
epic: EP-DEF
source_reqs: [DLV-R54]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: in-progress
refined: 2026-11-26
---

Change the `/define` skill so it reads its playbook and the files it lists one file per call, as the `/deliver` skill will (TASK-DLV-03).

## Acceptance criteria

- AC1: `template/claude/skills/define/SKILL.md` tells the agent to read `playbooks/define.md` in full first, then `backlog/README.md` and `AGENTS.md`, with the file-read tool, one file per call, never combined with other commands in one shell call.

## Notes

- Split from TASK-DLV-03 because EP-DLV's Boundaries give the define skill to EP-DEF. DEF-R27 already lists what the define skill reads first; that stays.
- An untestable task: the final review verifies the criterion by reading the file (DLV-R37).
- The root copy `.claude/skills/define/SKILL.md` is an installed release: it changes only through `init.py update`, never by hand.

## Open questions

- None. The behavior is fixed by DLV-R54.
