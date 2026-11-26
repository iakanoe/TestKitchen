# Delivery record: TASK-DEF-04

- Branch: `task-def-04-describe-replaces-and-the-define-warning`
- Ticket: TASK-DEF-04
- Change request: #8 https://github.com/iakanoe/TestKitchen/pull/8

Written by `scripts/deliver.py record`. Everything below the marker is the change request's description, verbatim; `deliver.py gate pr` fails when it differs from the current description.

<!-- change-request-description -->

## Ticket

TASK-DEF-04 Describe replaces and the define warning (requirements DEF-R46). Status: `done`.

## Plan

| Criterion | Tests |
| --- | --- |
| TASK-DEF-04/AC1 | Untestable (documentation). The final review reads `template/playbooks/define.md`: a new Checkpoints bullet "Contradicting a done criterion" (warn the person and show the live criterion of a done ticket, adopted or not, before writing; on a yes the new ticket lists it under `replaces:`), and `change` step 4 says the new ticket lists the criteria it contradicts under `replaces:` after the person's yes. |
| TASK-DEF-04/AC2 | Untestable. Every place in `template/playbooks/define.md` that says a done ticket is never rewritten (Applying a decision step 2, the Checkpoints bullet, `change` step 4; found with `grep -n -i 'never rewritten\|done tickets stay\|stay as they are'`) names the one allowed edit: crossing out a replaced criterion as `- AC<n>: (removed YYYY-MM-DD, replaced by <ID>)` when the replacing ticket is delivered. |
| TASK-DEF-04/AC3 | Untestable. `template/backlog/README.md`: a `replaces:` line in the frontmatter example next to `fixes:`, a field-list bullet like the `fixes` one (what it lists, the cross-out at delivery, that `backlog_check.py` refuses a done ticket leaving one live), and its "never rewritten" rule naming the same allowed edit. |

Files: `template/playbooks/define.md`, `template/backlog/README.md` (product copies), and this repository's installed `playbooks/define.md`, `backlog/README.md`, `kitchen.lock`, refreshed only through `python3 init.py update`. No code change. Untestable task: no step 6.

Plan review (fresh context, Sonnet): CRITICAL 0, WARNING 3, SUGGESTION 3. Taken: the grep also matches "stay as they are"; the README says `backlog_check.py` refuses a done replacing ticket that leaves a replaced criterion live (US-DEF-33 is done, so the check exists); one cross-out format in both files. Filed: `guide/define.md` and `guide/why.md` also say done tickets are never rewritten, outside this task's criteria: DEC-DEF-07.

Constrained by: no accepted ADRs; DEC-DEF-04 (done).

## Gaps found

- `guide/define.md` and `guide/why.md` still say done tickets are never rewritten, without the allowed edit: DEC-DEF-07 (draft), outside this task's criteria.

## Decisions

- One cross-out wording in the playbook, the README, and the checker; the warn-and-ask bullet. Log: TASK-DEF-04: replaces in the playbook and README

## Platform changes

- None

## Test changes

None

## Review report

Plan review (fresh context, Sonnet): CRITICAL 0, WARNING 3, SUGGESTION 3. WARNINGs: the grep now also matches "stay as they are"; the guides' "never rewritten" filed as DEC-DEF-07; the README states the checker's rule as it exists (US-DEF-33 is done). Suggestions: one cross-out wording in both files (taken); the others needed no change.

Final review (fresh context, Sonnet, diff mode): AC1, AC2, AC3 met by reading the files; the wording matches the decision log and the checker. SUGGESTION 1 ("without the yes, nothing is written and the contradiction is a DEC" goes slightly past AC1): kept, since it restates the playbook's existing rule that what a person can't answer becomes a DEC.

Reviewed commit: 9656ff882aa726393dc347e3819bc350c0b894b9
CRITICAL: 0, WARNING: 0, SUGGESTION: 1

## Checks

- Untestable task: no `gate red`; each criterion verified by the final review reading the files.
- `deliver.py check` on 9656ff8: PASS (backlog check, four self-tests, 263 tests passed).
