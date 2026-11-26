---
id: DEC-DEF-06
type: decision
title: Refined wording for in-progress tickets
epic: EP-DEF
source_reqs: [DEF-R20, DEF-R44]
blocked_by: []
owner: Ianick Noejovich
assignee_type: human
status: draft
---

## Question

Should the "Done" texts say that in-progress tickets, not only ready ones, need a `refined:` date?

## Context

- Found on 2026-11-26 while delivering TASK-DEF-03: the "Done" paragraph of `playbooks/define.md` and `guide/define.md`, "Done means no gaps", say "every ready ticket refined", while `backlog_check.py --gaps` (DEF-R20) lists every `ready` or `in-progress` story, task, or spike without `refined:`.
- TASK-DEF-03's plan review held the change outside its criteria (DEF-R44 names observed requirements, drafts, and coverage only), so it was left out.
- The difference rarely shows: a ticket becomes `in-progress` from `ready`, so it was normally refined before.

## Options

None recorded. Proposals:

- (a) Say "every ready or in-progress ticket refined" in both texts, matching `--gaps`.
- (b) Keep the wording; the in-progress case follows from the ready one.

## Recommendation

(a): the texts promise to describe exactly what `--gaps` checks (DEF-R44), and the change is two words in two files.

## Decides

A follow-up documentation task under EP-DEF on (a); nothing on (b).
