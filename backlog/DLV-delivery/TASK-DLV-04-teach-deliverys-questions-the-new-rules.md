---
id: TASK-DLV-04
type: task
title: Teach delivery's questions the new rules
epic: EP-DLV
source_reqs: [DLV-R62, DLV-R63, DLV-R65]
blocked_by: [TASK-DEF-08]
owner: Ianick Noejovich
assignee_type: either
status: in-progress
refined: 2026-11-27
---

Make `playbooks/deliver.md` follow define's rules on open DECs and on evaluating options for every question it asks the person in step 3 and under "Stop and ask", for every item the agent decides itself, and for the options of each DEC it opens.

## Acceptance criteria

- AC1: (removed 2026-11-27, DEC-DEF-05 reversed)
- AC2: (removed 2026-11-27, DEC-DEF-05 reversed)
- AC3: (removed 2026-11-27, replaced by AC5: point to define's named rules, not whole sections)
- AC4: (removed 2026-11-27, replaced by AC7: the check also applies after step 3 and to unlisted answers)
- AC5: Step 3 of `template/playbooks/deliver.md` tells the agent that every question of its questions round follows these parts of `playbooks/define.md`: the bullet "Check open decisions before recommending" (in "Questioning"), and from "Decision format" each option lettered with one For and one Against line plus the rules "Each option gets one 'For' line and one 'Against' line", "The recommendation compares", and "When the person questions a recommendation"; that a question which only confirms how to read a criterion lists each reasonable reading as such an option; that a question which is an open DEC gets that DEC's full decision round in define's whole "Decision format" (the Defer option and the brief's headings included); that the recommended option still comes first, as step 3 says, with "The recommendation compares" governing what the recommendation says; that define's round size ("About three questions per round") never applies in delivery, since step 3 asks everything in one round; and that, for every question that is not an open DEC, define's table of small sub-questions and the rest of the template (the Defer option and the brief's headings, the "**Recommendation:**" line among them) do not apply.
- AC6: (removed 2026-11-27, replaced by AC11: a stop question with no options needs only the open-DEC check)
- AC7: Step 3 of `template/playbooks/deliver.md` ("You decide, then log") tells the agent, before deciding such an item itself, to check the open DECs first, to ask an item that matches an open DEC's option, or otherwise answers an open DEC's question, in the questions round instead of deciding it, and that "Ground rules" covers such items that come up after step 3.
- AC8: `template/playbooks/deliver.md`, at step 10 ("Capture", "Gaps") and in the "Spikes" variant's follow-ups, tells the agent to write each option of a new DEC, and each proposal it adds after "None recorded. Proposals:", in the format `backlog/README.md` sets ("Bodies", Decision): `- (x) …` with indented `- For:` and `- Against:` lines, the options still coming only from what `docs/` records, otherwise "None recorded".
- AC9: (removed 2026-11-27, replaced by AC12: one rule in "Ground rules" for every variant)
- AC10: The "Stop and ask" list of `template/playbooks/deliver.md` names an answer to an open DEC's question in the same bullet as "a DEC option to choose".
- AC11: `template/playbooks/deliver.md` ("Stop and ask", "How to stop") tells the agent that every question it asks there follows step 3's questions-round rules as a whole (each option lettered with its For and Against lines, each reasonable reading of an ambiguous criterion listed as such an option, and a question that is an open DEC given that DEC's full decision round), and that a question with nothing to choose between (a location, a credential, an approval) needs only define's "Check open decisions before recommending" and, when the person questions its recommendation, the rule to re-evaluate and say what was missed or that nothing changed; and that a yes on a drafted change to `docs/`, to criteria, or to open questions is a choice between the draft and leaving things as they are, while an approval is only the supervised approval of an already-reviewed plan or tests.
- AC12: `template/playbooks/deliver.md` ("Ground rules") tells the agent that, in every variant (hotfix stories, spikes, decisions, and other changes included) and at any step, before deciding itself an item of the kind step 3's "You decide, then log" lists (plumbing, names, the wording of required texts, limits an ADR leaves open), it checks the open DECs, and that such an item that matches an open DEC's option, or otherwise answers an open DEC's question, found after step 3, or in a variant that skips step 3, is a stop under "Stop and ask".

## Notes

- An untestable task: the final review verifies each criterion by reading the file (DLV-R37), checking AC5's parts one by one (the define rules that apply, readings as options, an open DEC's full round, the recommended option first, and the exclusions), since splitting AC5 would take the ticket over `split_threshold`.
- AC1 and AC2 taught the reviewer the `(review)` marker, which was reversed on 2026-11-27 (decision log, "Review-only work stays in untestable tasks").
- Blocked by TASK-DEF-08: AC5 points to define's "Check open decisions before recommending", which must state the wider rule of DEF-R52 (an unlisted answer to an open DEC's question counts too) before delivery relies on it.
- A hotfix, a spike, a decision, and other changes skip step 3 (DLV-R37), but their stops still follow AC11 and their self-decided items AC12.
- US-DLV-24/AC3 (done) calls plumbing, names, required texts, and ADR-open limits the agent's choices; it stays true, since an item that is an open DEC's option was never the agent's to choose (deliver.md's "Never" already forbade choosing a DEC option), so AC7 and AC12 need no `replaces:`.
- The five points of the 2026-11-27 ticket-mode review and the step-10 gap from TASK-DEF-06's final review were settled on 2026-11-27 against define's delivered text (decision log, "Delivery points to define's named questioning rules", "Self-decided items are checked whenever they come up", "An answer to an open DEC's question counts as that DEC", "Stop-and-ask questions follow the questioning rules", "Delivery opens new DECs in the DEC format"). Its 2026-11-27 refinement review was settled the same day (decision log, "How the refinement reviews of TASK-DLV-04, TASK-DLV-05, and TASK-DEF-08 were settled").
- Refinement stop rule (owner, 2026-11-27): after six ticket-mode reviews, readings of the same wording that a later review raises without a CRITICAL are noted here for the delivering agent and its diff review instead of reopening refinement.
- Noted under the refinement stop rule (seventh review, 2026-11-27) for the delivering agent: in step 10, say proposals are optional and labeled as proposals, as `backlog/README.md` does (AC8 does not ban them); for a step-3 question about a criterion that depends on a ticket that isn't `done`, list its real choices (wait for that ticket, split, or a stated reading) as AC5's lettered options.
- The root copies (`playbooks/`) are an installed release: they change only through `init.py update`, never by hand.

## Open questions

- None. The rules are fixed by DLV-R62, DLV-R63, and DLV-R65.
