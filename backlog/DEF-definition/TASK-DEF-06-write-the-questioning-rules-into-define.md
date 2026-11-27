---
id: TASK-DEF-06
type: task
title: Write the questioning rules into define
epic: EP-DEF
source_reqs: [DEF-R49, DEF-R50, DEF-R51]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: in-progress
refined: 2026-11-27
---

Add the rules on open DECs and on evaluating options to define's questioning, and the DEC format that `backlog_check.py` will check (US-DEF-35) to the ticket rules.

## Acceptance criteria

- AC1: (removed 2026-11-27, DEC-DEF-05 reversed)
- AC2: (removed 2026-11-27, DEC-DEF-05 reversed)
- AC3: `template/playbooks/define.md` ("Questioning") tells the agent, before recommending, to search the decision log and the open DECs for the same kind of question, and to present an option that matches an open DEC's option as that DEC, never as an ordinary choice.
- AC4: `template/playbooks/define.md` ("Decision format") gives each option one "For" line and one "Against" line naming its cost and what in `docs/`, the backlog, or the decision log it conflicts with; makes the recommendation say why it beats each other option and the strongest reason against it; and, when the person questions a recommendation, has the agent re-evaluate and say what it missed, or that nothing changed.
- AC5: `template/backlog/README.md` ("Bodies", **Decision**) says: each option under `## Options` of a DEC that is not `done` or `deferred`, including the agent's own proposals listed after "None recorded. Proposals:", is an unindented bullet `- (x) …` where `x` is one lowercase letter, followed by indented sub-bullets `- For: …` and `- Against: …` (the check also accepts a plain `For:` or `Against:` line); a DEC that is not `done` or `deferred` has no `## Outcome`; and a `done` or `deferred` DEC has one.

## Notes

- An untestable task: the final review verifies each criterion by reading the files (DLV-R37).
- AC1 and AC2 documented the `(review)` marker, which was reversed on 2026-11-27 (decision log, "Review-only work stays in untestable tasks").
- Why the questioning rules: on 2026-11-26 an agent recommended text tests, an option of the then-open DEC-DEF-05, as an ordinary choice, and later presented a recommendation it reversed once asked to justify it (decision log, "Agents check open decisions and evaluate options before recommending").
- AC5 is the format US-DEF-35 checks (DEF-R51); US-DEF-35 is blocked by this task so the README describes the format before the check enforces it.
- The root copies (`backlog/README.md`, `playbooks/`) are an installed release: they change only through `init.py update`, never by hand.

## Open questions

- None. The rules are fixed by DEF-R49, DEF-R50, and DEF-R51.
