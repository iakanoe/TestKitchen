# Delivery record: docs/define-fresh-context-per-ticket

- Branch: `docs/define-fresh-context-per-ticket`
- Ticket: None

Written by `scripts/deliver.py record`. Everything below the marker is the change request's description, verbatim; `deliver.py gate pr` fails when it differs from the current description.

<!-- change-request-description -->

## Ticket

None. Defines: each ticket of `/deliver all` runs in a fresh context, so later tickets stop carrying earlier tickets' context and cost.

## Plan

No ticket, so no criterion rows. Run through `/define change` after measuring the US-DLV-38 delivery run (about 2.37M effective tokens; the context reached 254k tokens on that one ticket). The owner chose, in one question round: a subagent per ticket under `/deliver all`, with the rule in the playbook and the skill; a spike to measure the CLI before any advice on lean sessions; and a hint to read the playbooks one file per call. Claude Code behavior was checked in the official docs (sub-agents, hooks, mcp, permissions pages) on 2026-11-26.

Changes: DLV-R52, DLV-R53, DLV-R54 added (nothing superseded); new story US-DLV-42 (draft, blocked by SPK-DLV-02); new spikes SPK-DLV-01 and SPK-DLV-02; EP-DLV's `## Open` lists both spikes; one decision-log entry.

Constrained by: `playbooks/define.md` (change), `backlog/README.md`.

## Gaps found

- SPK-DLV-01: Measure a delivery run from the CLI (open).
- SPK-DLV-02: Verify the guard in a nested subagent (open; blocks US-DLV-42).
- US-DLV-42: Deliver each ticket of /deliver all in a fresh context (draft; needs `/define refine`).

## Decisions

- Each ticket of `/deliver all` runs in a fresh context; in Claude Code, a subagent per ticket that hands its questions back. Log: Fresh context per ticket under /deliver all

## Platform changes

- None

## Test changes

None

## Review report

None: this change request touches no code or test file (only `docs/` and `backlog/`). US-DLV-42 gets its ticket-mode review in `/define refine`.

## Checks

- `python3 scripts/backlog_check.py`: 0 errors, 0 warnings (6 epics, 146 stories, 14 tasks, 22 decisions, 3 spikes).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
