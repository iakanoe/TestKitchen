# Delivery record: spk-dlv-02-verify-the-guard-in-a-nested-subagent

- Branch: `spk-dlv-02-verify-the-guard-in-a-nested-subagent`
- Ticket: None
- Change request: #22

Written by `scripts/deliver.py record`. Everything below the marker is the change request's description, verbatim; `deliver.py gate pr` fails when it differs from the current description.

<!-- change-request-description -->

## Ticket

None. Spike SPK-DLV-02: Verify the guard in a nested subagent.

## Plan

Two probes, each harmless whether or not the guard ran, on Claude Code 2.1.331 (desktop app, auto permission mode):

- **Deny:** a subagent (depth 1) and a subagent it started (depth 2) each ran `git -C /nonexistent-guard-probe push origin HEAD`. The guard denied it at both depths (checked in their transcripts, `spawnDepth` 1 and 2).
- **Ask:** the same two depths each made one Edit to `docs/product.md` with text not in the file. The guard answers `ask` for it (run by hand on the same input), but both calls were approved by auto mode's classifier (`"source":"config","reasonType":"classifier"`), not by the person. The main conversation's protected edits the same day were approved by the person (`"source":"user_temporary"`).

Findings are in SPK-DLV-02, which is `done`. Not tested: other permission modes, and a depth-1 foreground subagent.

## Gaps found

- DEC-GRD-05: Guard asks from subagents in auto mode (filed by this spike; now blocks TASK-DLV-03).

## Decisions

- None

## Platform changes

- None

## Test changes

None

## Review report

None: this change request touches no code or test file (only `backlog/`).

## Checks

- `python3 scripts/backlog_check.py` and `--strict`: 0 errors, 0 warnings (6 epics, 148 stories, 19 tasks, 23 decisions, 3 spikes).
- `docs/product.md` unchanged after the probes (`git status`).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
