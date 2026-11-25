---
id: US-DEF-26
type: story
title: Slice work into releases
epic: EP-DEF
source_reqs: [DEF-R36]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person planning releases, I want the work cut into a few ordered slices, so that each release gives users something and waits on nothing slow.

## Acceptance criteria

- AC1: Given mode `slice`, when the agent starts, then it asks in one message what hurts most today, who uses it first and how many, any deadline or event, what success looks like a month after release, and what can wait.
- AC2: Given the answers, when the agent proposes slices, then it shows two to four in a table (slice, users get, epics, waits on), ordered so the first slices depend on nothing slow, and names what is left out.
- AC3: Given a yes to the slices, when the agent writes them, then it writes `releases:` in `kitchen.yml`, a `release:` on every story, task, and spike (deferred ones in the last slice), and a decision-log entry with the slices and the success measure.
- AC4: Given a later request to move a ticket between slices, when the agent handles it, then it treats the move as a decision.

## Notes

- Adopted 2026-11-25 from existing behavior: playbook behavior (`playbooks/define.md`): an agent following it does this, so its criteria are verified by review, not by tests. The script side (release fields) is in the release-slice story of this epic.
- The criteria describe what happens now; confirmation happens on the cited `(observed in code)` requirements.

## Open questions

- None. This story records behavior that already exists; anything that looks unintended is filed as a decision on the epic.
