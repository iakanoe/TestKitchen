# Delivery record: TASK-DEF-06

- Branch: `task-def-06-write-the-questioning-rules-into-define`
- Ticket: TASK-DEF-06
- Change request: #25

Written by `scripts/deliver.py record`. Everything below the marker is the change request's description, verbatim; `deliver.py gate pr` fails when it differs from the current description.

<!-- change-request-description -->

## Ticket

TASK-DEF-06 Write the questioning rules into define (requirements DEF-R49, DEF-R50, DEF-R51). Status: `done`.

## Plan

| Criterion | Tests |
| --- | --- |
| TASK-DEF-06/AC3 | Untestable task (DLV-R37): the final review reads `template/playbooks/define.md` "Questioning" and confirms a bullet tells the agent, before recommending, to search the decision log and the open DECs for the same kind of question, and to present an option matching an open DEC's option as that DEC, never as an ordinary choice. The installed copy `playbooks/define.md` matches after `init.py update`. |
| TASK-DEF-06/AC4 | Untestable task: the final review reads "Decision format" and confirms the template gives each option one "For" line and one "Against" line (cost, and what in `docs/`, the backlog, or the decision log it conflicts with), the recommendation says why it beats each other option and its strongest reason against, and a rule says that when the person questions a recommendation the agent re-evaluates and says what it missed, or that nothing changed. |
| TASK-DEF-06/AC5 | Untestable task: the final review reads `template/backlog/README.md` "Bodies", **Decision**, and confirms it states the option bullet format `- (x) …` (one lowercase letter, unindented, including proposals after "None recorded. Proposals:") with indented `- For: …` and `- Against: …` sub-bullets (a plain `For:`/`Against:` line also accepted) for a DEC that is not `done` or `deferred`; no `## Outcome` on such a DEC; and an `## Outcome` on a `done` or `deferred` DEC. `backlog_check.py` still exits 0 (existing DECs unchanged). |

Files: `template/playbooks/define.md` ("Questioning" bullet; "Decision format" template and rules), `template/backlog/README.md` ("Bodies", Decision), the root copies `playbooks/define.md` and `backlog/README.md` refreshed only through `python3 init.py update`, the ticket, and `docs/decision-log.md`. No data changes, no interfaces, no code. User-visible parts: the playbook and README text agents follow.

Constrained by: no ADRs; DEC-DEF-05 (done, its `(review)` outcome reversed in the decision log, "Review-only work stays in untestable tasks"); US-DEF-35 (ready, checks the AC5 format; blocked by this task).

## Gaps found

- `deliver.md` step 10 opens a new DEC without the DEF-R51 option format (final review, suggestion 2): filed as a note on TASK-DLV-04.

## Decisions

- The wording of the new rules in define's "Questioning" and "Decision format" and in the backlog README's Decision body. Log: How define's playbook and the backlog README word the questioning rules

## Platform changes

- None

## Test changes

None

## Review report

**Plan review** (plan mode): CRITICAL: 0, WARNING: 0, SUGGESTION: 3.
1. SUGGESTION: use the same option shape in define's brief as in the README's DEC format. Done: both use `- (x) …` with indented `- For:` / `- Against:`.
2. SUGGESTION: give the Defer option For and Against lines. Done.
3. SUGGESTION: the plan lists `docs/decision-log.md` but `## Decisions` said None. Done: decision-log entry added and cited below.

**Final review** (diff mode, origin/main...HEAD): AC3, AC4, AC5 met by reading the files; root copies byte-identical to `template/`.
1. SUGGESTION: Defer's Against placeholder in the template doesn't ask for conflicts. Noted, not applied: the rule under the template ("Each option gets one For line and one Against line", naming cost and conflicts) binds every option, Defer included; recorded in the decision-log entry.
2. SUGGESTION: `deliver.md` step 10 opens DECs without the For/Against format. Filed as a note on TASK-DLV-04.

The reviewer could not finish its own test run; `deliver.py check` below covers it.

Reviewed commit: 245a1bfd21c901c07b2ec4ec34c23d2b49748d5b
CRITICAL: 0, WARNING: 0, SUGGESTION: 2

## Checks

- `python3 scripts/deliver.py check`: PASS (backlog check 0 errors, 0 warnings; self-tests; 316 passed).
- `gate red`: skipped, an untestable task (DLV-R37); step 6 does not apply.
- By hand: `init.py update --yes` refreshed `playbooks/define.md` and `backlog/README.md` (doctor: all checks passed); `python3 scripts/backlog_check.py` exits 0 after capture.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
