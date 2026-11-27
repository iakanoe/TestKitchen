---
id: TASK-DEF-06
type: task
title: Write the review marker and the questioning rules into define
epic: EP-DEF
source_reqs: [DEF-R48, DEF-R49, DEF-R50]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: draft
---

Document the `(review)` marker in the ticket rules and the define playbook, and add the rules on open DECs and on evaluating options to define's questioning.

## Acceptance criteria

- AC1: `template/backlog/README.md` says a criterion starting with `(review)` is checked by the final review instead of a tagged test, never carries a tag, is never test debt, and is added only by a person at a define checkpoint; and lists adding the marker to a live criterion of an adopted `done` story as the second allowed edit to a done ticket.
- AC2: `template/playbooks/define.md` ("Splitting") tells the agent to propose `(review)` only for a criterion whose subject is wording no test can check, shown at the checkpoint for the person's yes.
- AC3: `template/playbooks/define.md` ("Questioning") tells the agent, before recommending, to search the decision log and the open DECs for the same kind of question, and to present an option that matches an open DEC's option as that DEC, never as an ordinary choice.
- AC4: `template/playbooks/define.md` ("Decision format") gives each option one "For" line and one "Against" line naming its cost and what in `docs/`, the backlog, or the decision log it conflicts with; makes the recommendation say why it beats each other option and the strongest reason against it; and, when the person questions a recommendation, has the agent re-evaluate and say what it missed, or that nothing changed.

## Notes

- An untestable task under the rule in force until US-DEF-34 and US-DLV-43 are delivered: the final review verifies each criterion by reading the files (DLV-R37).
- Why the questioning rules: on 2026-11-26 an agent recommended text tests, an option of the then-open DEC-DEF-05, as an ordinary choice, and later presented a recommendation it reversed once asked to justify it (decision log, "Agents check open decisions and evaluate options before recommending").
- The root copies (`backlog/README.md`, `playbooks/`) are an installed release: they change only through `init.py update`, never by hand.

## Open questions

- None. The rules are fixed by DEF-R48, DEF-R49, and DEF-R50.
