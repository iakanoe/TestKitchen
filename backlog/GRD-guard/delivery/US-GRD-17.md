# Delivery record: US-GRD-17

- Branch: `us-grd-17-deny-in-a-subagent-what-the-guard-would-ask`
- Ticket: US-GRD-17
- Change request: #27

Written by `scripts/deliver.py record`. Everything below the marker is the change request's description, verbatim; `deliver.py gate pr` fails when it differs from the current description.

<!-- change-request-description -->

## Ticket

US-GRD-17 Deny in a subagent what the guard would ask (requirements GRD-R36). Status: `done`.

## Plan

All tests are in the new file `tests/test_guard_subagent.py`. They feed the installed guard the PreToolUse JSON (`tool_name`, `tool_input`, `cwd`, plus `agent_id` / `agent_type` as the case needs) as a subprocess, reusing the throwaway project and the call lists (`ALLOW`, `ASK`, `FORCE_ASK`, `DENY`, `REACHES_GATE`, `EDIT_ASK`, `HOME_CONFIG_ASK`, `EDIT_ALLOW`) of `tests/test_guard.py`, so every ask shape the guard already has is covered. "A subagent id" below means each of `"a1b2c3"`, `7`, `{}`, `[]`, `false`, and `" "` (whitespace).

| Criterion | Tests |
| --- | --- |
| US-GRD-17/AC1 | Allowed-side contrast is AC3. Denied: with sandbox unset, every `ASK` command (shell writes to protected paths, writes after `cd`, host commands and host API writes, git settings, aliases, `-c`, `GIT_*`) and every `FORCE_ASK` command with `agent_id: "a1b2c3"` → `deny`; one shell ask, one force push, and one protected edit with each other subagent id (`7`, `{}`, `[]`, `false`, `" "`) → `deny`; every `EDIT_ASK` path and `HOME_CONFIG_ASK` file with Write → `deny`; a protected path with Edit, MultiEdit, and NotebookEdit → `deny`; the git alias that asks (`git st` with `alias.st=status`) → `deny`. Limit: `KITCHEN_GUARD_SANDBOX=true` (not exactly `1`) with an agent id → `deny`. |
| US-GRD-17/AC2 | For a single-reason ask (`echo x > kitchen.yml`), a protected edit (`scripts/extra_tool.py`, whose reason names kitchen.lock), and a multi-reason call (`git push --force origin <B> && gh repo sync && echo x > kitchen.yml`): the subagent's deny reason starts with the exact text of the main session's ask reason (every reason, same order), and each reason line appears once. A call whose two parts give the same ask reason (`echo x > kitchen.yml && echo y > kitchen.yml`) carries that reason once. Every deny of AC1 and AC5 names the subagent and says to hand the step back to the main session, where the person is asked (the reason ends with the exact hand-back line below). AC5's deny under sandbox carries the force push's ask reason. |
| US-GRD-17/AC3 | The AC1 calls (all `ASK`, `FORCE_ASK`, `EDIT_ASK` with Write) with no `agent_id`, `agent_id: null`, `agent_id: ""`, and `agent_type: "general-purpose"` with no `agent_id` → `ask`, with the same reason as the plain call. |
| US-GRD-17/AC4 | `KITCHEN_GUARD_SANDBOX=1` and `agent_id: "a1b2c3"`: every `ASK` command and every `EDIT_ASK` / `HOME_CONFIG_ASK` Write → `allow`; one shell ask with each other subagent id → `allow`. |
| US-GRD-17/AC5 | `KITCHEN_GUARD_SANDBOX=1` and an agent id: every `FORCE_ASK` command → `deny`; a force push joined with another ask (`git push --force origin <B> && echo x > kitchen.yml`) → `deny`. Contrast: the same calls without `agent_id` still `ask` (existing sandbox behavior). |
| US-GRD-17/AC6 | With `agent_id: "a1b2c3"`: every `ALLOW` command and `EDIT_ALLOW` path → `allow` (with and without sandbox); every `DENY` command and `REACHES_GATE` merge → `deny` with exactly the same reason as without `agent_id` (with and without sandbox); a call that both asks and is denied (`git push --force origin <B> && git push origin main`) → the deny of the call without `agent_id`, not the subagent's hand-back text. A tool the guard does not check (Read) → `allow`. The printed merge on a change request whose merge gate passes (the fixture of `MergeTest` in `tests/test_guard.py`) → `allow` with an agent id, as without one. |

Files:

- `template/claude/hooks/guard.py`: `main()` reads `agent_id` from the hook input; `finish()`, after the sandbox opt-in, turns the collected asks into a deny when the call came from a subagent. The reason is the ask's reason text (same dedup and order: firm reasons first) followed by one hand-back line. The module docstring gains a paragraph on the rule.
- `.claude/hooks/guard.py` (root copy): refreshed only through `python3 init.py update`.
- `tests/test_guard_subagent.py` (new).
- `guide/agents.md`, `template/CONTRIBUTING.md` (guard and sandbox paragraphs; the root `CONTRIBUTING.md` through `init.py update`), `CHANGELOG.md` (`## Unreleased`).

Data changes: none. Interfaces: the guard's PreToolUse decision for calls whose hook input carries `agent_id`; callers are Claude Code's hook runner only. User-visible text: one new line at the end of a subagent's deny reason, wording decided here and logged: "This call came from a subagent, where the guard can't ask the person; hand this step back to the main session, which runs it and the person is asked there."

Constrained by: no accepted ADRs. DEC-GRD-05: done (option (a)). Decision-log entries "The guard denies in a subagent what it would ask" and "How the guard reads agent_id".

## Gaps found

- None

## Decisions

- The wording of the subagent's hand-back line and where it goes in the deny reason. Log: The guard's hand-back line for subagent calls
- AC3, AC4, and AC6 describe unchanged behavior, so each also has a boundary test against its contrast, which `gate red` needs to fail. Log: Unchanged-behavior criteria get a boundary test

## Platform changes

- None

## Test changes

None

## Review report

**Plan review** (`ticket-reviewer`, mode plan): CRITICAL 0, WARNING 1, SUGGESTION 2.

- WARNING: the hand-back wording was "decided here and logged" while `## Decisions` said None. Done: added the `## Decisions` bullet and the decision-log entry "The guard's hand-back line for subagent calls".
- SUGGESTION: AC6 lacked the allow path of a merge that passes the gate. Done: `test_us_grd_17_ac6_a_merge_that_passes_the_gate_stays_allowed` on the `MergeTest` fixture.
- SUGGESTION: check the exact hand-back line, not two words. Done: the AC2 tests assert the reason ends with the exact line.

**Tests review** (`ticket-reviewer`, mode tests): CRITICAL 2, WARNING 0, SUGGESTION 2.

- CRITICAL: the multi-reason fixture (force push + `gh repo sync` + write) is denied without an `agent_id`, so it could never pass. Done: replaced with `git config core.x y && gh repo sync && echo x > kitchen.yml` (checked: asks with three reasons).
- CRITICAL: the AC5 case `git push --force … && echo x > kitchen.yml` is already a deny, breaking the contrast. Done: dropped from AC5, moved to the AC6 deny list.
- SUGGESTION: hand-back checked only on Bash denies. Done: the AC2 test also checks Write, Edit, MultiEdit, and NotebookEdit denies.
- SUGGESTION: AC4 sandbox checked only with Write. Done: Edit, MultiEdit, and NotebookEdit added.

Both CRITICALs were fixed before the freeze commit and `gate red` rerun (PASS); the fixtures were checked by hand to ask without an `agent_id`. The tests review was not rerun; the diff review covered the frozen tests.

**Diff review** (`ticket-reviewer`, mode diff): CRITICAL 0, WARNING 2, SUGGESTION 1.

- WARNING: the test comment cites the decision-log entry "The guard's hand-back line for subagent calls", not yet written. Done: added at capture under exactly that title.
- WARNING: the test comment cites "Unchanged-behavior criteria get a boundary test", not yet written. Done: added at capture under exactly that title.
- SUGGESTION: `kitchen.lock`'s `source` named the test commit because `init.py update` ran on uncommitted changes. Done: reran `init.py update --source . --yes` from the clean reviewed head; only the `source` label changed.

Reviewed commit: 51f25a48e4617005513e256abfb786d2c4e6746a
CRITICAL: 0, WARNING: 2, SUGGESTION: 1

## Checks

- `python3 scripts/deliver.py check`: PASS (backlog check, self-tests, full pytest run: 334 passed).
- `python3 scripts/deliver.py gate red US-GRD-17` before implementing: PASS (every live criterion has a failing tagged test; each failure `'ask' != 'deny'` or the AC6 list contrast).
- By hand: the guard on the plain fixtures without `agent_id` (multi-reason, repeated reason, `echo x > kitchen.yml`, sandboxed force push) asks with the expected reasons; `init.py update` and `doctor` pass. Not tried inside a real Claude Code subagent; the tests send the hook input Claude Code documents.
