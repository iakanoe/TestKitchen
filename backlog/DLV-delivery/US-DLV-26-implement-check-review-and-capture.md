---
id: US-DLV-26
type: story
title: Implement, check, review, and capture
epic: EP-DLV
source_reqs: [DLV-R34]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As an agent delivering a ticket, I want steps 7 to 10 to turn frozen tests green, pass the full check and a fresh review, and record everything found, so that the change is complete and nothing stays only in chat.

## Acceptance criteria

- AC1: Given frozen failing tests, when step 7 implements, then the agent writes code until they pass, comments each non-obvious decision, structure, interface, and seam with its criterion or ADR, marks each open-DEC seam with the DEC, its fail-closed behavior, and the criterion, makes every to-do style marker name a ticket, and commits `feat: <ID> …` as it goes.
- AC2: Given passing tests, when step 8 checks, then the agent fetches and merges `origin/<default>` and runs `deliver.py check` in a separate call, which must pass in full, and for user-facing work tries the change as a user would and notes what it saw.
- AC3: Given a passing check, when step 9 reviews, then the agent first updates READMEs and in-code documentation and commits every code and test file, runs the reviewer in `diff` mode, fixes every CRITICAL, fixes or files every WARNING, fixes, files, or notes every SUGGESTION, reruns the check and the reviewer after any fix, and afterwards touches only files outside code and tests.
- AC4: Given the review, when step 10 captures, then every gap is filed as a draft DEC (options only from `docs/`), an SPK, or a note on a later ticket, without editing criteria or open questions without a yes; one decision-log entry records the ticket's decisions, and each platform change gets its own entry.
- AC5: Given capture, when the agent finishes step 10, then it updates any status list the project keeps, sets the ticket `done` (stopping to ask if a live criterion cannot be proven here), and runs `backlog_check.py`, which must exit 0.

## Notes

Adopted 2026-11-25 from `playbooks/deliver.md`; the criteria describe what the document says now and are not yet confirmed by a person. Playbook behavior is followed by agents and people, so it is verified by review, not by tests.

## Open questions

- None. Adopted behavior.
