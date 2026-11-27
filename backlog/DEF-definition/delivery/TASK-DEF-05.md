# Delivery record: TASK-DEF-05

- Branch: `task-def-05-read-the-define-playbook-one-file-per-call`
- Ticket: TASK-DEF-05
- Change request: #28

Written by `scripts/deliver.py record`. Everything below the marker is the change request's description, verbatim; `deliver.py gate pr` fails when it differs from the current description.

<!-- change-request-description -->

## Ticket

TASK-DEF-05 Read the define playbook one file per call (requirements DLV-R54). Status: `done`.

## Plan

| Criterion | Tests |
| --- | --- |
| TASK-DEF-05/AC1 | Untestable task (DLV-R37): the final review reads `template/claude/skills/define/SKILL.md` and confirms it tells the agent to read `playbooks/define.md` in full first, then `backlog/README.md` and `AGENTS.md`, with the file-read tool, one file per call, never combined with other commands in one shell call. It also confirms the installed copy `.claude/skills/define/SKILL.md` matches the template after `python3 init.py update` (byte-identical), and that the skill's other mechanics are unchanged. |

Files: `template/claude/skills/define/SKILL.md` (the opening paragraph that says what to read first), the root copy `.claude/skills/define/SKILL.md` and `kitchen.lock` refreshed only through `python3 init.py update`, `CHANGELOG.md` (`## Unreleased`, Changed), the ticket, and `docs/decision-log.md`. No data changes, no interfaces, no code (the skill file matches neither `code` nor `tests` in `kitchen.yml`). User-visible parts: the skill text the agent follows.

Constrained by: no ADRs; DEF-R27 (observed in code; what the define skill reads first, unchanged); TASK-DLV-03 (draft, the `/deliver` half of DLV-R54; not touched here); no related DEC.

## Gaps found

- None

## Decisions

- The wording of the define skill's reading rule and its stated reason; the two files keep DLV-R54's order without requiring one. Log: How the define skill words its one-file-per-call reading

## Platform changes

- None

## Test changes

None

## Review report

**Plan review** (plan mode): CRITICAL: 0, WARNING: 0, SUGGESTION: 1.
1. SUGGESTION: the plan row said `backlog/README.md` and `AGENTS.md` are read "in that order", stricter than AC1. Done: "in that order" removed from the row.

**Final review** (diff mode, origin/main...HEAD): AC1 met by reading `template/claude/skills/define/SKILL.md` line 9; the installed copy's change is identical and `kitchen.lock` matches; scope limited to AC1; CHANGELOG updated. No findings. The reviewer did not run the full test suite (`deliver.py check` below covers it) and could not tell from the diff alone that `init.py update` wrote the installed copy (it did: see Checks).

Reviewed commit: c5c895bdf4c503de498c789aaf485fe1490a4ce2
CRITICAL: 0, WARNING: 0, SUGGESTION: 0

## Checks

- `python3 scripts/deliver.py check`: PASS (backlog check; self-tests; 334 passed).
- `gate red`: skipped, an untestable task (DLV-R37); step 6 does not apply.
- By hand: `python3 init.py update --yes` refreshed `.claude/skills/define/SKILL.md` and `kitchen.lock` (doctor: all checks passed); `cmp` shows the installed copy byte-identical to the template; `python3 scripts/backlog_check.py` exits 0 after capture.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
