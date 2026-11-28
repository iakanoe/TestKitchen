---
id: TASK-DEF-08
type: task
title: Treat any answer to an open DEC's question as that DEC
epic: EP-DEF
source_reqs: [DEF-R52]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: in-progress
refined: 2026-11-27
---

Widen define's rule on open decisions so that an option answering an open DEC's question is presented as that DEC even when the DEC does not list it.

## Acceptance criteria

- AC1: `template/playbooks/define.md` ("Questioning") keeps the bullet named "Check open decisions before recommending", keeps telling the agent to search the decision log and the open DECs for the same kind of question before recommending, and tells it to present an option that matches an open DEC's option, or otherwise answers an open DEC's question, as that DEC (naming it and running its decision round), never as an ordinary choice.

## Notes

- An untestable task: the final review verifies the criterion by reading the file (DLV-R37).
- Why: an answer the DEC does not list still settles the DEC if the person accepts it as an ordinary choice, the same silent decision DEF-R49 was written to prevent (decision log, "An answer to an open DEC's question counts as that DEC").
- TASK-DEF-06/AC3 (done) stays true under DEF-R52, which only widens it, so this task needs no `replaces:`.
- TASK-DLV-04 points delivery's questions to this bullet and is blocked by this task.
- For the delivering agent (refinement review, 2026-11-27): keep the bullet's reason, widened to say that an unlisted answer accepted as an ordinary choice also settles the DEC silently.
- The root copy `playbooks/define.md` is an installed release: it changes only through `init.py update`, never by hand.

## Open questions

- None. The rule is fixed by DEF-R52.
