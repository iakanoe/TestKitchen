---
id: US-DLV-41
type: story
title: Refuse a delivery that leaves replaced criteria live
epic: EP-DLV
source_reqs: [DLV-R51]
blocked_by: [US-DEF-33]
owner: Ianick Noejovich
assignee_type: either
status: ready
refined: 2026-11-26
---

As a reviewer or CI job, I want `gate pr` to refuse a change request that delivers a ticket with `replaces:` while a replaced criterion is still live, so that the done ticket's record says which criterion binds.

## Acceptance criteria

- AC1: Given a ticket change request whose ticket lists `replaces:` and whose replaced criteria are each `- AC<n>: (removed YYYY-MM-DD, replaced by <ID>)` at `--head`, when `deliver.py gate pr` runs, then it prints `PASS pr: <ID>` and exits 0, where the `<ID>` in each `replaced by <ID>` is the delivered ticket's own ID.
- AC2: Given the same change request with one replaced criterion still live at `--head`, when `deliver.py gate pr` runs, then it prints `FAIL <ID>/AC<n> is replaced but still live: cross it out as (removed YYYY-MM-DD, replaced by <ID>)` naming that criterion, where `<ID>` in `replaced by <ID>` is the delivered ticket's ID, and exits 1.

## Notes

- Implements DEC-DEF-04, decided 2026-11-26 by Ianick Noejovich. The playbook step that tells the agent to make the edit is TASK-DLV-02; the checker's own refusal of a done ticket with live replaced criteria is US-DEF-33/AC4.
- Blocked by US-DEF-33 because `backlog_check.py` must accept the `replaces:` field before a ticket can carry it.
- A tag of a removed criterion is an error (DEF-R13), so a change request that crosses a criterion out also changes the tests tagged with it, and names them under Test changes (DLV-R18).

- Gap found while planning US-DEF-33 (2026-11-26): `deliver.py context` lists the tickets named in `fixes:` among the related tickets but not those named in `replaces:`; this ticket, which teaches delivery about `replaces:`, is where that closes.

## Open questions

- None. The decision log records this decision.
