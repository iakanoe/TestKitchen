## Ticket

<!-- Start with the ticket ID (US-… or TASK-…), its title, and its status; `python3 scripts/deliver.py pr-body <ID>` writes this whole description for you. For a merge request that is not a story or task (a spike, a decision, a small fix), start with "None." and say what it is. A ticket left in-progress says why here and names the ticket that holds the rest. GitLab CI reads this description from its committed delivery record (`deliver.py record`), not from this page: after every edit here, rerun `record`, commit, and push. -->

## Plan

<!-- One row per live criterion, with the tests that prove it: the allowed case, the denied case, and every limit and empty state the criterion names. Then the files, data changes, interfaces, and user-visible parts, and "Constrained by:" the accepted ADRs and each related DEC with its status. With autonomy supervised, add "Plan approved by: <name>" and "Tests approved by: <name>". -->

| Criterion | Tests |
| --- | --- |

Constrained by:

## Gaps found

<!-- Behavior, follow-ups, or open questions this work found. Each bullet names the ticket that now holds it (a new DEC or SPK, or a note added to a later ticket). Or a single "- None". -->

- None

## Decisions

<!-- Every decision made during this work, each bullet ending with "Log: <decision-log entry title>" or naming a done DEC. Or a single "- None". -->

- None

## Platform changes

<!-- Settings changed outside the code (host settings, external services, secrets by name only), each bullet ending with "Log: <decision-log entry title>". Or a single "- None". -->

- None

## Test changes

<!-- Every test file changed after the freeze commit ("test: <ID> failing tests"), with the reason. A frozen test changes only where it contradicts the ticket or an accepted ADR. -->

None

## Review report

<!-- Every finding of the plan, tests, and final reviews (CRITICAL / WARNING / SUGGESTION), each with what was done about it. A story or task merge request ends with the final reviewer's two closing lines, quoted exactly: the "Reviewed commit:" line with its sha (no code or test file may change after it) and the tally line, which must show CRITICAL: 0. -->

## Checks

<!-- The `python3 scripts/deliver.py check` result (with test counts), the `deliver.py gate red` result before implementing, and what was tried by hand. -->
