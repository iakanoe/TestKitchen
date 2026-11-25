---
id: US-DEF-25
type: story
title: Adopt existing code
epic: EP-DEF
source_reqs: [DEF-R35, DEF-R27]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person bringing existing code under Test Kitchen, I want its current behavior recorded as unconfirmed requirements and done stories, so that I can confirm it rather than have it presented as intended.

## Acceptance criteria

- AC1: Given mode `adopt`, when the agent starts, then it builds a capability map from the code (what users and callers can do, grouped into proposed epics with the `code:` globs each owns) for a checkpoint.
- AC2: Given an approved capability map, when the agent works an epic, then it proposes requirements marked `(observed in code)`, a DEC "Is this intended?" per suspected bug with current and likely intended behavior, `done` stories with `adopted: true` whose criteria describe what the code does now, and the epic's globs, writing them on a yes and asking for owners.
- AC3: Given adopted stories with untested criteria, when the agent reports, then it lists them as test debt from `backlog_check.py --test-debt`, separate and never blocking, and offers tasks to pay it down.
- AC4: Given written observed requirements, when the agent walks the person through them, then it removes the marker from each one the person confirms and logs what was confirmed.
- AC5: Given an adoption, when the code shows the stack and how to run it, then the agent offers to draft the `AGENTS.md` project section.
- AC6: Given an adoption session ending, when the agent stops, then it adds an "Adopt progress" decision-log entry listing the epics done, in progress, and not started.

## Notes

- Adopted 2026-11-25 from existing behavior: playbook behavior (`playbooks/define.md`): an agent following it does this, so its criteria are verified by review, not by tests; in Claude Code each epic group goes to a subagent.
- The criteria describe what happens now; confirmation happens on the cited `(observed in code)` requirements.

## Open questions

- None. This story records behavior that already exists; anything that looks unintended is filed as a decision on the epic.
