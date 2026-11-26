# Delivery record: TASK-DEF-03

- Branch: `task-def-03-match-the-done-paragraph-to-gaps`
- Ticket: TASK-DEF-03
- Change request: #7 https://github.com/iakanoe/TestKitchen/pull/7

Written by `scripts/deliver.py record`. Everything below the marker is the change request's description, verbatim; `deliver.py gate pr` fails when it differs from the current description.

<!-- change-request-description -->

## Ticket

TASK-DEF-03 Match the Done paragraph and guide to --gaps (requirements DEF-R44). Status: `done`.

## Plan

| Criterion | Tests |
| --- | --- |
| TASK-DEF-03/AC1 | Untestable (documentation). The final review reads `template/playbooks/define.md`, "Done": the list states "no requirement still marked `(observed in code)`" and "no draft story or task" in those words. |
| TASK-DEF-03/AC2 | Untestable. Same paragraph: "every requirement that is not superseded and not in a deferred epic is covered, that is, cited by a story or task that is not deferred" replaces "covered by ready or done tickets"; `grep -n 'ready or done tickets'` on both files finds nothing. The "refined" item is left as it is. |
| TASK-DEF-03/AC3 | Untestable. `guide/define.md`, "Done means no gaps": a new bullet "no draft story or task"; the coverage bullet says "every requirement that is not superseded and not in a deferred epic is covered: cited by a story or task that is not deferred". The refined bullet is left as it is. |

Files: `template/playbooks/define.md` (product copy), `guide/define.md` (edited in place), and this repository's installed `playbooks/define.md` plus `kitchen.lock`, refreshed only through `python3 init.py update`. No code change; `--gaps` stays as DEF-R20 and DEF-R21 record it. Step 6 does not apply: an untestable task.

Plan review 1 (fresh context, Sonnet): CRITICAL 1, WARNING 1, SUGGESTION 2. CRITICAL (changing the "refined" item to ready or in-progress is beyond the criteria): dropped; the mismatch (both texts say ready tickets, `--gaps` also checks in-progress ones) is filed as a gap at capture. WARNING (deferred-epic exception missing from the coverage wording): taken. Suggestions taken: a grep for the old phrase; "no draft story or task" stated explicitly in the playbook.

Constrained by: no accepted ADRs; DEC-DEF-03 (done).

## Gaps found

- Both Done texts say "every ready ticket refined" while `--gaps` also checks in-progress tickets: filed as DEC-DEF-06 (draft), outside this task's criteria.

## Decisions

- The Done wording, with the deferred-epic exception and the refined item left as it is. Log: TASK-DEF-03: Done wording follows --gaps

## Platform changes

- None

## Test changes

None

## Review report

Plan review 1 (fresh context, Sonnet): CRITICAL 1, WARNING 1, SUGGESTION 2. CRITICAL (refined item changed beyond the criteria): dropped and filed as DEC-DEF-06. WARNING (deferred-epic exception): taken, confirmed in `uncovered()`. Suggestions taken (grep for the old phrase; "no draft story or task" stated explicitly).

Plan review 2 (fresh context, Sonnet): CRITICAL 0, WARNING 0, SUGGESTION 2: verify the deferred-epic exemption (done: `uncovered()` skips deferred epics) and list the filed gap under Gaps found (done).

Final review (fresh context, Sonnet, diff mode): AC1, AC2, AC3 met by reading the files; "ready or done tickets" no longer appears in `playbooks/`, `template/`, or `guide/`; the wording matches `--gaps`. SUGGESTION 1 (the lock names the commit before the one holding it): expected, no change.

Reviewed commit: 24ff5797cf2bd3b3e0f93ff7b0687707baa7b675
CRITICAL: 0, WARNING: 0, SUGGESTION: 1

## Checks

- Untestable task: no `gate red`; each criterion verified by the final review reading the files.
- `deliver.py check` on 24ff579: PASS (backlog check, four self-tests, 263 tests passed).
