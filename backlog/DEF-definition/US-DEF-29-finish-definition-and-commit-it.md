---
id: US-DEF-29
type: story
title: Finish definition and commit it
epic: EP-DEF
source_reqs: [DEF-R39]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person relying on the backlog, I want a clear end to definition and every definition merged where others read it, so that other sessions and people see the same record.

## Acceptance criteria

- AC1: Given `backlog_check.py --gaps` prints nothing, when the agent reports, then it calls the product fully defined, and otherwise it does not, test debt never counting against it.
- AC2: Given delivery hands off because nothing is ready, when define takes over, then it runs a decision round for each DECIDE line (most blocking first), then `refine` on each REFINE line, then asks "What should we build next?".
- AC3: Given checkpoints written for a topic, when the agent commits, then it works on a `docs/define-<topic>` branch (or `docs/dec-<id>-<slug>` for a single decision).
- AC4: Given a definition branch, when the agent opens its change request, then `## Ticket` starts `None. Defines`, every decision is a `## Decisions` bullet ending `Log: <entry title>`, and every gap left is a `## Gaps found` bullet naming its ticket.
- AC5: Given an open definition change request, when the agent finishes it, then it commits the delivery record, runs `backlog_check.py --pr-body` and `deliver.py gate pr`, and merges as the autonomy level allows.

## Notes

- Adopted 2026-11-25 from existing behavior: playbook behavior (`playbooks/define.md`): an agent following it does this, so its criteria are verified by review, not by tests. The playbook's "Done" paragraph and `--gaps` differ in wording; see DEC-DEF-03.
- The criteria describe what happens now; confirmation happens on the cited `(observed in code)` requirements.

## Open questions

- None. This story records behavior that already exists; anything that looks unintended is filed as a decision on the epic.
