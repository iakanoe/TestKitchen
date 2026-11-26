# Delivery record: TASK-INST-03

- Branch: `task-inst-03-say-that-an-agents-shell-may-have-no-terminal`
- Ticket: TASK-INST-03
- Change request: #11 https://github.com/iakanoe/TestKitchen/pull/11

Written by `scripts/deliver.py record`. Everything below the marker is the change request's description, verbatim; `deliver.py gate pr` fails when it differs from the current description.

<!-- change-request-description -->

## Ticket

TASK-INST-03 Say that an agent's shell may have no terminal (requirements INST-R35). Status: `done`.

## Plan

| Criterion | Tests |
| --- | --- |
| TASK-INST-03/AC1 | Untestable (documentation). The final review reads `AGENT-INSTALL.md` line 10: "Your shell may have no terminal for the installer to ask on, so always pass `--yes` for a real run." |
| TASK-INST-03/AC2 | Untestable. `grep -n -i 'has no terminal' AGENT-INSTALL.md guide/install.md` finds nothing, and no sentence presents an agent's shell as having no terminal. |
| TASK-INST-03/AC3 | Untestable. `AGENT-INSTALL.md`: "Without `--yes`, the installer stops before writing anything when there is no terminal to ask on (and asks on the terminal when there is one)." `guide/install.md` already says "Without a terminal and without `--yes`, the run stops before writing"; the review confirms it. |
| TASK-INST-03/AC4 | Untestable. `guide/install.md`, "Answering without a terminal": "(an agent's shell, CI)" becomes "(CI; an agent's shell may have none)". |

Files: `AGENT-INSTALL.md`, `guide/install.md` (neither is installed; edited in place). No code change. Untestable task: no step 6.

Constrained by: no accepted ADRs; DEC-INST-03 (done).

## Gaps found

- None

## Decisions

- The terminal wording in both files. Log: TASK-INST-03: terminal wording

## Platform changes

- None

## Test changes

None

## Review report

Plan review (fresh context, Sonnet): CRITICAL 0, WARNING 0, SUGGESTION 3, all taken: a broader grep (`no terminal`, `without .*terminal`, every hit read); the exit-code-2 clause kept; the guide's stop sentence rechecked after the edit.

Final review (fresh context, Sonnet, diff mode): AC1 to AC4 met by reading the files; no findings.

Reviewed commit: 739786020e3e0c2fa935146c2b814f2ecddc4b0f
CRITICAL: 0, WARNING: 0, SUGGESTION: 0

## Checks

- Untestable task: no `gate red`; each criterion verified by the final review reading the files.
- `deliver.py check` on 7397860: PASS (backlog check, four self-tests, 263 tests passed); `tests/test_release.py` passes (pinned links unchanged).
