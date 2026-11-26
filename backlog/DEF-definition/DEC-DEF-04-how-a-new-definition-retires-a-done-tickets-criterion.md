---
id: DEC-DEF-04
type: decision
title: How a new definition retires a done ticket's criterion
epic: EP-DEF
source_reqs: [DEF-R45, DEF-R46, DLV-R51]
blocked_by: []
owner: Ianick Noejovich
assignee_type: human
status: done
---

## Question

When a new definition contradicts a criterion of a `done` ticket, how does that criterion stop binding, given that a done ticket is never rewritten?

## Context

- `playbooks/define.md` and `backlog/README.md` say a `done` ticket is never rewritten and a change to done behavior becomes a new ticket. Nothing says what happens to the old criterion: it stays live, so the backlog holds two criteria that disagree (for example US-DLV-21 lists adopted tickets in release notes, while US-DLV-39 leaves them out).
- A fix story already names the criterion a bug broke with `fixes: [<ticket>/AC<n>]` (DEF-R07), and a removed criterion stays as a placeholder `- AC<n>: (removed YYYY-MM-DD, <reason>)` (DEF-R08).
- A tag of a removed criterion is an error (DEF-R13), so tests that proved the old criterion must change when it is removed.

## Options

- (a) A `replaces:` frontmatter list, like `fixes:`: `/define` warns and shows the contradicted criterion, the new ticket lists it on a yes, and delivering the new ticket crosses the old criterion out, the one allowed edit of a done ticket; the checker refuses a done ticket whose replaced criteria are still live. Proposed by the owner on 2026-11-26.
- (b) Keep today's practice: the old criterion stays live and the new ticket's Notes say which one it changes. Proposed for comparison; it is what the refined drafts did before this decision.

## Recommendation

(a): the record then says which criterion binds, and the checker can enforce it.

## Decides

No ticket was blocked by it. It is implemented by US-DEF-33, TASK-DEF-04, US-DLV-41, and TASK-DLV-02.

## Outcome

- Date: 2026-11-26.
- Answer: Option (a). When a new definition contradicts a criterion of a `done` ticket (adopted or not), `/define` warns the person and shows the affected criterion; on a yes, the new ticket records it in a `replaces: [<ticket>/AC<n>]` frontmatter list (like `fixes:`); when that new ticket is delivered, the replaced criterion becomes `- AC<n>: (removed YYYY-MM-DD, replaced by <ticket>)` in the done ticket (the one allowed edit of a done ticket), and the checker refuses a done ticket whose `replaces:` criteria are still live. Until `backlog_check.py` accepts the field (US-DEF-33), tickets record the criteria they replace in their Notes.
- Decided by: Ianick Noejovich.
- Recorded in: requirements DEF-R45, DEF-R46, DLV-R51; US-DEF-33, TASK-DEF-04, US-DLV-41, TASK-DLV-02; decision log, "A new definition retires a done ticket's criterion through replaces".
