---
id: EP-DEF
type: epic
title: Definition
owner: Ianick Noejovich
assignee_type: either
status: ready
code: ["template/scripts/backlog_check.py"]
---

How what people know becomes requirements, decisions, and tickets, and how those are checked: the ticket and requirement conventions (`backlog/README.md`, the `docs/` skeletons), `backlog_check.py` (validation, trace, coverage, `--strict`, `--pr-body`, `--gaps`, `--refine`, `--test-debt`, `--self-test`), and the `/define` process (`playbooks/define.md` and the `define` skill), with the guides that explain them (`guide/define.md`, `guide/concepts.md`).

## Boundaries

- Delivering tickets, the gates (`gate red`, `gate pr`, `gate merge`), `deliver.py next`, and delivery records belong to delivery; this epic covers only the define side of the hand-off and the `--pr-body` description check.
- Shared parsing (ticket IDs, tag forms, globs, frontmatter, configuration loading) lives in `kitchen_lib.py`, which this epic uses but does not own.
- The reviewer's `ticket` mode is defined in `playbooks/review.md`; this epic only says when refine runs it.
- The guard that asks before edits under `docs/` belongs to the Claude Code hooks.

## Open

- DEC-DEF-05, DEC-DEF-06, DEC-DEF-07.
