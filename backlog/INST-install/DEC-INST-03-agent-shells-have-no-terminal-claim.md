---
id: DEC-INST-03
type: decision
title: AGENT-INSTALL.md states that an agent's shell has no terminal
epic: EP-INST
source_reqs: [INST-R07, INST-R29]
blocked_by: []
owner: Ianick Noejovich
assignee_type: human
status: done
---

## Question

Is this intended? `AGENT-INSTALL.md` states as fact that "Your shell has no terminal for the installer to ask on" and that without `--yes` the installer stops before writing anything; that cannot be verified for every agent.

## Context

- Current behavior of the code: `init.py` asks on standard input when it is a terminal, else opens `/dev/tty` when it can (`init.py:247-263`). Only when neither works and `--yes` is absent does a confirmation stop the run with exit code 2 (`init.py:294-302`).
- Checked on 2026-11-25 in one agent (Claude Code's desktop app): its shell had no terminal, so `/dev/tty` could not be opened and the claim held. Not checked in other agents or in a terminal-based agent session, where the shell could have a controlling terminal; there a run without `--yes` would prompt on that terminal instead of stopping.
- The same file tells the agent to always pass `--yes` for a real run, so following it as written avoids the case. Its step 2 dry run also passes `--yes`.
- Already settled: nothing in `docs/` or the decision log records which agents have a terminal.

## Options

None recorded. Proposals, not decisions:

- (a) Reword to "Your shell may have no terminal for the installer to ask on; always pass `--yes` …", which stays true either way.
- (b) Keep the sentence as it is.

## Recommendation

(a): it keeps the instruction (always pass `--yes`) and drops a claim nobody has checked across agents.

## Decides

No ticket waits on it. US-INST-24 records the instructions as they are; a wording change is a new ticket under EP-INST.

## Outcome

- Date: 2026-11-25.
- Answer: Option (a): `AGENT-INSTALL.md` is reworded to "Your shell may have no terminal …; always pass `--yes`".
- Decided by: Ianick Noejovich.
- Recorded in: requirements INST-R33; confirmed INST-R07, INST-R29; US-INST-26; decision log, "AGENT-INSTALL.md says the shell may have no terminal".
