---
id: DEC-DEF-07
type: decision
title: The guides and the replaces edit
epic: EP-DEF
source_reqs: [DEF-R25, DEF-R46]
blocked_by: []
owner: Ianick Noejovich
assignee_type: human
status: draft
---

## Question

Should `guide/define.md` and `guide/why.md` also say that a done ticket's criterion may be crossed out when a ticket that lists it under `replaces:` is delivered?

## Context

- Found on 2026-11-26 while planning TASK-DEF-04: `guide/define.md` (around line 31) and `guide/why.md` (around line 25) say done tickets are never rewritten, with no mention of the one allowed edit that DEC-DEF-04 introduced. TASK-DEF-04 now says it in `playbooks/define.md` and `backlog/README.md`.
- TASK-DEF-04's criteria name only the playbook and the backlog README, so the guides were left out of it.

## Options

None recorded. Proposals:

- (a) Add the allowed edit to both guides, in the words the playbook uses.
- (b) Leave the guides as they are: they summarize, and the playbook and README are the rules.

## Recommendation

(a): the guides are what people read first, and a guide that contradicts the playbook misleads them.

## Decides

A follow-up documentation task under EP-DEF on (a); nothing on (b).
