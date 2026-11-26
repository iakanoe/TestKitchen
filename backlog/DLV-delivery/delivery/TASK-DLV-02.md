# Delivery record: TASK-DLV-02

- Branch: `task-dlv-02-tell-the-agent-to-cross-out-replaced-criteria`
- Ticket: TASK-DLV-02
- Change request: #9 https://github.com/iakanoe/TestKitchen/pull/9

Written by `scripts/deliver.py record`. Everything below the marker is the change request's description, verbatim; `deliver.py gate pr` fails when it differs from the current description.

<!-- change-request-description -->

## Ticket

TASK-DLV-02 Tell the agent to cross out replaced criteria (requirements DLV-R51). Status: `done`.

## Plan

| Criterion | Tests |
| --- | --- |
| TASK-DLV-02/AC1 | Untestable (documentation). The final review reads `template/playbooks/deliver.md`, step 10 (Capture): a new bullet "Replaced criteria", before "Status", telling the agent that when the ticket lists `replaces:`, it turns each replaced criterion into `- AC<n>: (removed YYYY-MM-DD, replaced by <ID>)` (`<ID>` being this ticket) in its done ticket within this change request, and that this is the one edit a done ticket allows. |

Files: `template/playbooks/deliver.md` (product copy) and this repository's installed `playbooks/deliver.md` plus `kitchen.lock`, refreshed only through `python3 init.py update`. No code change; the gate that enforces it is US-DLV-41. Untestable task: no step 6.

Constrained by: no accepted ADRs; DEC-DEF-04 (done).

## Gaps found

- None

## Decisions

- The capture-step wording: exact edit, stated as the one exception to asking; `gate pr` not described before US-DLV-41. Log: TASK-DLV-02: crossing out at capture

## Platform changes

- None

## Test changes

None

## Review report

Plan review (fresh context, Sonnet): CRITICAL 0, WARNING 0, SUGGESTION 3. Taken: the bullet is the stated exception to asking before editing criteria; it names the date, the ID, and that only that line changes. Not taken: describing `gate pr`'s refusal, which US-DLV-41 will add; the bullet names `backlog_check.py`'s existing check instead.

Final review (fresh context, Sonnet, diff mode): AC1 met by reading the file; the installed copy equals the template. SUGGESTION 1 (split the long bullet line): not taken, the playbook keeps one line per bullet.

Reviewed commit: bd482145b3561fa014d89d5377b4c8529e4a1b54
CRITICAL: 0, WARNING: 0, SUGGESTION: 1

## Checks

- Untestable task: no `gate red`; the criterion verified by the final review reading the file.
- `deliver.py check` on bd48214: PASS (backlog check, four self-tests, 263 tests passed).
