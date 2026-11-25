---
id: DEC-DEF-02
type: decision
title: Readiness rules skip epics
epic: EP-DEF
source_reqs: [DEF-R09]
blocked_by: []
owner: Ianick Noejovich
assignee_type: human
status: draft
---

## Question

Is this intended? A `ready` or `done` epic with owner `TBD` (or empty) passes `backlog_check.py`, while `backlog/README.md` says any ticket that is `ready`, `in-progress`, or `done` needs an owner.

## Context

- Current behavior: readiness (owner, release, criteria, open questions) is checked only for tickets that are not epics; an epic only needs the `owner` field to be present. A fixture whose epic is `status: ready` with `owner: TBD` validates with 0 errors (verified 2026-11-25).
- Likely intended behavior: unclear. Either epics need a real owner once `ready` (the README's wording, since its ticket-types table lists epics as tickets), or epics are containers and the readiness section means work tickets only.
- Evidence: `template/scripts/backlog_check.py:324-325` (`if t.type != "epic" and t.status in STARTED: self._readiness(t)`); `template/backlog/README.md:74-81` ("A ticket that is `ready`, `in-progress`, or `done` needs: an owner (not `TBD`, not empty)"); `docs/decision-log.md`, "Script choices made while building v0.1": "Epics need only id, type, title, owner, assignee_type, status" (fields, not values).

## Options

- (a) Require a real owner on `ready`, `in-progress`, and `done` epics (owner only; criteria, open questions, and release stay work-ticket rules).
- (b) Keep epics exempt and say in `backlog/README.md`, "Readiness", that it applies to tickets other than epics.

None of these is recorded in `docs/`; both are proposals.

## Recommendation

(b), proposed: it matches the decision-log choice that epics need only their fields, and changing the script could fail existing installed projects whose epics use `TBD`.

## Decides

The DEF-R09 wording (confirm or supersede), and either a fix story or a README wording change. No ticket is blocked by it.
