---
id: US-DEF-27
type: story
title: Triage bugs and open hotfixes
epic: EP-DEF
source_reqs: [DEF-R37]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person reporting a problem, I want it triaged into the right kind of ticket, so that broken behavior is restored and new behavior is defined properly.

## Acceptance criteria

- AC1: Given mode `bug`, when the agent starts, then it records verbatim what was done, what was expected, what happened, and where, before triage.
- AC2: Given a bug that breaks an existing criterion, when the agent triages it, then it proposes a fix story with `fixes:` naming that criterion, citing the broken story's requirements, whose first test reproduces the bug.
- AC3: Given a bug no criterion covers, when the agent triages it, then it treats it as a missing requirement and continues in `change`.
- AC4: Given a report that may or may not be a bug, when the agent triages it, then it opens a DEC "Is this intended?" with what happens and what was expected.
- AC5: Given mode `hotfix`, when the agent proposes it, then one checkpoint holds a `ready` story with `hotfix: true`, an owner, and criteria restoring the behavior (with `fixes:` when it broke a criterion), a decision-log entry saying why the lane is used, and a draft follow-up task to refine it.

## Notes

- Adopted 2026-11-25 from existing behavior: playbook behavior (`playbooks/define.md`): an agent following it does this, so its criteria are verified by review, not by tests.
- The criteria describe what happens now; confirmation happens on the cited `(observed in code)` requirements.

## Open questions

- None. This story records behavior that already exists; anything that looks unintended is filed as a decision on the epic.
