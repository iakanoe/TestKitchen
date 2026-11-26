---
id: TASK-INST-03
type: task
title: Say that an agent's shell may have no terminal
epic: EP-INST
source_reqs: [INST-R35]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: in-progress
refined: 2026-11-26
---

`AGENT-INSTALL.md` and `guide/install.md` state as fact that an agent's shell has no terminal, which nobody has checked across agents. This task rewords both so they say the shell may have none, while still telling the agent to always pass `--yes`.

## Acceptance criteria

- AC1: `AGENT-INSTALL.md` says that the agent's shell may have no terminal for the installer to ask on, and tells the agent to always pass `--yes` for a real run.
- AC2: No sentence in `AGENT-INSTALL.md` or `guide/install.md` states that an agent's shell has no terminal.
- AC3: `AGENT-INSTALL.md` and `guide/install.md` say that the installer stops before writing without `--yes` only when there is no terminal to ask on.
- AC4: `guide/install.md`, "Answering without a terminal", no longer gives an agent's shell as a place with no terminal; it says that an agent's shell may have none.

## Notes

- Implements DEC-INST-03, option (a), decided 2026-11-25 by Ianick Noejovich, as widened on 2026-11-26 to `guide/install.md` (INST-R35 supersedes INST-R33). Filed on 2026-11-25 as US-INST-26; it became this task on 2026-11-26 because only a reviewer can check its criteria.
- The final review verifies each criterion by reading the files; no test can.
- It changes the instructions recorded by US-INST-24, which stays as the record of the earlier wording. `AGENT-INSTALL.md` is at the repository root and `guide/install.md` is in `guide/`; neither is installed.

## Open questions

- None. The decision log records this decision.
