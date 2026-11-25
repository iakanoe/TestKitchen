---
id: US-DEF-20
type: story
title: Ask and decide without inventing
epic: EP-DEF
source_reqs: [DEF-R28, DEF-R29]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person defining a product, I want questions in small rounds with recommendations, and nothing invented for me, so that every recorded answer is mine.

## Acceptance criteria

- AC1: Given a topic with open points, when the agent asks, then each round holds about three questions, each in plain words with a recommendation and why.
- AC2: Given a question the person cannot answer now, when the round ends, then the agent proposes a DEC for a choice or an SPK for something to verify, and records no answer of its own.
- AC3: Given a decision that nothing ready, in the current slice, or being built depends on, when the agent presents it, then it proposes deferring it, and on a yes the deferral is logged, the DEC becomes `deferred`, and each ticket naming it states its interim behavior or is deferred too.
- AC4: Given a decision round, when the agent presents it, then it shows the next decision in plain words, "Your next action" in one line, "Already fixed" with IDs, lettered options each with its cost (the recommended one marked, and a defer option with the interim behavior), and "After you reply".
- AC5: Given several small sub-questions, when the agent presents them, then they come as one table of at most five rows (question, recommendation, why), answered with "ok" or the rows to change.
- AC6: Given options, reported constraints, or platform claims, when the agent records them, then it presents only options recorded in `docs/` or the DEC (labeling its own as proposals), keeps reported constraints verbatim with their certainty, checks platform claims in official documentation, and records no secret.

## Notes

- Adopted 2026-11-25 from existing behavior: playbook behavior (`playbooks/define.md`): an agent following it does this, so its criteria are verified by review, not by tests.
- The criteria describe what happens now; confirmation happens on the cited `(observed in code)` requirements.

## Open questions

- None. This story records behavior that already exists; anything that looks unintended is filed as a decision on the epic.
