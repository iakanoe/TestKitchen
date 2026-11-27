---
id: TASK-DLV-04
type: task
title: Teach delivery's questions the new rules
epic: EP-DLV
source_reqs: [DLV-R59, DLV-R60]
blocked_by: [TASK-DEF-06]
owner: Ianick Noejovich
assignee_type: either
status: draft
---

Make step 3 of `playbooks/deliver.md` follow define's rules on open DECs and on evaluating options, for every question it asks and for every item it decides itself.

## Acceptance criteria

- AC1: (removed 2026-11-27, DEC-DEF-05 reversed)
- AC2: (removed 2026-11-27, DEC-DEF-05 reversed)
- AC3: Step 3 of `template/playbooks/deliver.md` tells the agent to apply, to every question of its questions round (including one that only confirms how to read a criterion), the rules in `playbooks/define.md`'s "Questioning" (search the decision log and open DECs first, DEF-R49) and "Decision format" (each option with one For and one Against line, and the recommendation compared with each other option, DEF-R50).
- AC4: Step 3 of `template/playbooks/deliver.md` ("You decide, then log") tells the agent, before deciding an item itself, to check the open DECs, and to ask an item that matches an open DEC's option in the questions round instead of deciding it.

## Notes

- An untestable task: the final review verifies the criterion by reading the file (DLV-R37).
- AC1 and AC2 taught the reviewer the `(review)` marker, which was reversed on 2026-11-27 (decision log, "Review-only work stays in untestable tasks").
- Blocked by TASK-DEF-06, which writes the rules AC3 points to into `playbooks/define.md`; delivered first, AC3 would point to rules a reader cannot find.
- Decided 2026-11-27 (decision log, "Agents check open decisions and evaluate options before recommending" and "Delivery's questions and self-decided items follow define's rules").
- To refine after TASK-DEF-06 is delivered, against define's real text (decision log, "TASK-DLV-04 is refined after TASK-DEF-06"). Its 2026-11-27 ticket-mode review left: (1) CRITICAL: AC3 points to whole sections of `define.md` whose other rules (about three questions per round; the small sub-question table with no options) conflict with step 3 and with "every question"; state the rules themselves instead; (2) the summaries in AC3 leave out parts of DEF-R49 and DEF-R50; (3) AC4 does not say what happens when a self-decided item comes up after step 3 (a stop under "Stop and ask" is the likely answer); (4) whether "matches an open DEC's option" includes an item that answers an open DEC's question or one of its proposals; (5) the hotfix lane and later "Stop and ask" rounds are outside DLV-R59 and DLV-R60.
- The root copies (`playbooks/`) are an installed release: they change only through `init.py update`, never by hand.

## Open questions

- None. The rules are fixed by DLV-R59 and DLV-R60, and by the owner's choice that every question follows them (decision log, "Delivery's questions and self-decided items follow define's rules").
