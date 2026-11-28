# Delivery record: TASK-DEF-08

- Branch: `task-def-08-treat-any-answer-to-an-open-decs-question-as-that-dec`
- Ticket: TASK-DEF-08
- Change request: #31

Written by `scripts/deliver.py record`. Everything below the marker is the change request's description, verbatim; `deliver.py gate pr` fails when it differs from the current description.

<!-- change-request-description -->

## Ticket

TASK-DEF-08 Treat any answer to an open DEC's question as that DEC (requirements DEF-R52). Status: `done`.

## Plan

| Criterion | Tests |
| --- | --- |
| TASK-DEF-08/AC1 | Untestable task (DLV-R37): the final review reads `template/playbooks/define.md` "Questioning" and confirms the bullet is still named "Check open decisions before recommending", still tells the agent to search the decision log and the open DECs for the same kind of question before recommending, and tells it to present an option that matches an open DEC's option, or otherwise answers an open DEC's question, as that DEC (naming it and running its decision round), never as an ordinary choice. From the ticket's Notes (not AC1): the bullet's reason says that an unlisted answer accepted as an ordinary choice also settles the DEC silently. The installed copy `playbooks/define.md` matches `template/` after `python3 init.py update`. |

Files: `template/playbooks/define.md` (one bullet in "Questioning"), the root copy `playbooks/define.md` refreshed only through `python3 init.py update`, the ticket, and `docs/decision-log.md` (one entry for the bullet's wording, "How define words the wider open-DEC rule"; DEF-R52 itself is already logged in "An answer to an open DEC's question counts as that DEC"). No data changes, no interfaces, no code. User-visible parts: the playbook text agents follow.

Constrained by: no ADRs; no related DEC. TASK-DEF-06 (done; its AC3 stays true, DEF-R52 only widens it); TASK-DLV-04 (ready, blocked by this task; points delivery's questions to this bullet by name).

## Gaps found

- None

## Decisions

- The wording of the widened "Check open decisions before recommending" bullet in define's "Questioning". Log: How define words the wider open-DEC rule

## Platform changes

- None

## Test changes

None

## Review report

**Plan review** (plan mode): CRITICAL: 0, WARNING: 0, SUGGESTION: 2.
1. SUGGESTION: the plan row's check that the bullet's reason is widened comes from the ticket's Notes, not AC1. Done: the row now marks it as a Notes item.
2. SUGGESTION: the plan did not name the decision-log entry it adds. Done: the plan names "How define words the wider open-DEC rule" and the existing entry that logs DEF-R52.

**Final review** (diff mode, origin/main...HEAD): AC1 met by reading `template/playbooks/define.md` line 78; the bullet keeps its name and the search, matches DEF-R52's wording, and widens its reason as the Notes ask; the root copy matches the template and `kitchen.lock` (reinstalled, not hand-edited). No findings.

Reviewed commit: f3418b64d609cdc193aa458a0cf8fbea2e49f965
CRITICAL: 0, WARNING: 0, SUGGESTION: 0

## Checks

- `python3 scripts/deliver.py check`: PASS (backlog check 0 errors, 0 warnings; self-tests; 346 passed).
- `gate red`: skipped, an untestable task (DLV-R37); step 6 does not apply.
- By hand: `python3 init.py update --yes` refreshed `playbooks/define.md` (doctor: all checks passed; `cmp` with the template: identical); `python3 scripts/backlog_check.py` exits 0 after capture.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
