# Backlog

The work items derived from the requirements in `docs/`. `docs/` holds what the product must do (requirements with IDs, boundaries, architecture decisions); the backlog holds how each part is accepted (acceptance criteria) and what is still open (decisions and spikes). A ticket cites requirement IDs and never restates or extends them, so a requirement changes in one place.

`python3 scripts/backlog_check.py` enforces every rule below that a script can check. `playbooks/define.md` writes tickets; `playbooks/deliver.md` builds them.

## Layout

One folder per epic, named `<CODE>-<slug>`, holding `epic.md` and the epic's tickets:

```
backlog/
  PAY-payments/
    epic.md
    US-PAY-01-refund-an-order.md
    US-PAY-03-refuse-refunds-over-the-order-total.md
    TASK-PAY-01-retry-failed-webhooks.md
    DEC-PAY-02-refund-window.md
    SPK-PAY-01-verify-provider-sandbox.md
    delivery/
      US-PAY-01.md
  delivery/
    docs-define-payments.md
```

`<CODE>` is the epic's code: one capital letter, then one to nine capitals or digits (`PAY`, `AUTH`, `CORE`). The same code names the epic's requirements file, `docs/requirements/<CODE>-<name>.md`. A cross-cutting epic (for example `CORE`) holds architecture and work no capability owns.

## Ticket types

| Type | Prefix | Purpose | Done when |
| --- | --- | --- | --- |
| `epic` | `EP-` | A capability; groups its tickets | All its tickets are done or deferred |
| `story` | `US-` | User-facing behavior with acceptance criteria | Every live criterion has a passing tagged test |
| `task` | `TASK-` | Technical work with no user-facing behavior (refactor, upgrade, CI, test debt) | Every live criterion is met and reviewed |
| `decision` | `DEC-` | A question a person must decide | The answer is recorded in `docs/` and in the decision log |
| `spike` | `SPK-` | A time-boxed investigation: verify access, an integration, or a direction | Findings are recorded and follow-ups filed |

IDs: `EP-<CODE>` for epics; `US-`, `TASK-`, `DEC-`, or `SPK-` plus `<CODE>-<nn>` (two or more digits) for the rest, for example `US-PAY-03`. IDs are stable: never renumber or reuse one, because tests, code comments, change requests, and the decision log point to them. The file name is the ID plus a kebab-case slug (`US-PAY-03-refuse-refunds-over-the-order-total.md`); an epic's file is `epic.md`.

## Frontmatter

```yaml
---
id: US-PAY-03
type: story              # epic | story | task | decision | spike
title: Refuse refunds over the order total
epic: EP-PAY             # omitted on epics
source_reqs: [PAY-R03]   # requirement IDs; [] allowed for tasks and spikes
blocked_by: []           # ticket IDs: this ticket can start but cannot finish before they are done
owner: TBD               # person or role accountable; must be set before ready
assignee_type: either    # human | agent | either (decisions are human)
status: draft            # draft | ready | in-progress | done | deferred
priority: normal         # optional: high | normal | low (default normal)
release: v1              # only when kitchen.yml lists releases
refined: 2026-01-31      # set by /define refine when the ticket passes refinement
adopted: true            # optional: written by adopt mode for behavior that already existed
hotfix: true             # optional: urgent-fix lane
fixes: [US-PAY-01/AC2]   # optional: bug-fix stories name the criterion the code broke
code: ["src/payments/**"]   # epics only, optional: code areas this epic owns
---
```

- `source_reqs` lists requirement IDs only. A requirement that is a pure constraint is cited by the story it constrains.
- `blocked_by` means "can start, can't finish": a blocked ticket may be `ready`, but `deliver.py next` never picks it while a blocker is unfinished, and it cannot be finished before them. Cycles are errors.
- `assignee_type`: decisions are always `human`, because only a person decides. The field is required on every ticket; stories, tasks, and spikes are usually `either`. `deliver.py next` never picks a `human` ticket.
- `priority` orders the ready tickets. A ticket inherits the highest priority of every unfinished ticket it unblocks, so a blocker never waits behind the work it holds up.
- `release` exists only when `kitchen.yml` lists `releases`. Then every story, task, and spike names one, deferred tickets use the last slice, and no unfinished blocker may sit in a later slice than the ticket it blocks (it would hold that slice back).
- `refined` is the date the ticket last passed refinement (`playbooks/define.md`, mode `refine`). A ready ticket without it counts as a definition gap.
- `adopted: true` marks behavior that existed before the backlog did (`playbooks/define.md`, mode `adopt`). Its missing tests are test debt, reported by `backlog_check.py --test-debt` and never errors.
- `hotfix: true` marks the urgent-fix lane: it skips the plan review and the questions round, and the change request must log why the lane was used and name the follow-up ticket.
- `fixes` names the criterion a bug broke. The fix story's first test reproduces the bug.
- `code` (epics only) lists the globs of the code the epic owns. Once any epic declares `code`, code files no epic claims are reported as definition gaps.

### Readiness

A ticket other than an epic that is `ready`, `in-progress`, or `done` needs:

- an owner (not `TBD`, not empty), so someone is accountable;
- every open question answered (see "Open questions");
- for stories and tasks, at least one live criterion;
- a `release`, when releases are on.

`ready` does not require finished blockers (see `blocked_by`).

## Bodies

**Story:**

```markdown
As a <role>, I want <capability>, so that <outcome>.

## Acceptance criteria

- AC1: Given <context>, when <action>, then <result>.

## Notes

Facts the work depends on (with their certainty), exclusions, related tickets.

## Open questions

- None. <why nothing is open>
```

**Task:** a plain description, then `## Acceptance criteria` (`- AC1: <checkable statement>`; Given/when/then not required), `## Notes`, `## Open questions`.

**Decision:** `## Question`, `## Context` (what `docs/` already settles), `## Options` (only options already recorded; otherwise "None recorded"), `## Recommendation`, `## Decides` (the tickets it unblocks). Once decided, add `## Outcome` (the date, the answer, who decided, where it is recorded) and set `status: done`.

**Spike:** `## Goal`, `## Context`, `## Done when`, `## Findings` (empty until the spike runs).

**Epic:** what the capability is, `## Boundaries` (what it does not do), `## Open` (the DEC and SPK IDs still open for it).

### Acceptance criteria

Criteria are numbered `AC1`, `AC2`, … and referenced elsewhere as `US-PAY-03/AC2` (tests, code, change requests, other tickets). Numbers are stable:

- Never renumber or reuse a number. A new criterion takes the next number, at the end of the list.
- A removed criterion stays as a placeholder: `- AC4: (removed YYYY-MM-DD, <reason or ticket>)`.
- Changing what a criterion means is a removal plus a new criterion, not an edit in place. Wording fixes that keep the meaning are fine.

A criterion is live unless it is removed. Criteria are written in English. Story criteria use Given/when/then.

### Open questions

Before a ticket can be `ready`, each bullet under `## Open questions` is answered in one of two forms:

- It starts with `None` (for example "None. Refund limits are fixed by PAY-R03.").
- It names a `DEC` or `SPK` ticket. If that ticket is not `done` and not in `blocked_by`, the bullet also states the interim behavior as `Until decided: …` and names the criterion that defines it: "Refunds after delivery: DEC-PAY-02. Until decided: AC4 refuses them."

A bare gap blocks readiness until it is filed as a `DEC` or `SPK`, so whoever builds the ticket never fills it in by guessing.

## Rules

- A ticket never adds scope beyond its cited requirements. Criteria come from the requirement text; a gap becomes an open question, a `DEC`, or an `SPK`, never an invented criterion.
- Each criterion lives in exactly one story; another story that depends on it references `US-…/ACn`.
- Every requirement that is not superseded is cited by at least one story or task that is not deferred. `backlog_check.py` warns about uncovered requirements (errors with `--strict`); epics with `status: deferred` are excluded.
- Proposals, candidate designs, and recalled claims never become criteria. Put them in Notes with their certainty.
- When a `DEC` is decided, the answer goes into `docs/` (a requirement or an ADR) and the decision log; then the DEC is `done`. New open questions become tickets.
- A `done` ticket is never rewritten. A change to done behavior is a new ticket, because the done ticket is the record of what was built and tested.
- Never record credentials, tokens, or secrets in a ticket.

### Self-contained tickets

By default, tickets are read inside this repository, and links to `docs/` are fine. When tickets are exported to a tracker or handed to readers without the repository, set `self_contained_tickets: true` in `kitchen.yml`. Then every ticket must work on its own:

- cite requirements by ID only, never by document name, path, or section;
- state each fact the work depends on in the ticket, in one short sentence, with its certainty ("reported by the team", "confirmed YYYY-MM-DD", "candidate, not decided");
- cite architecture decisions by ADR ID and other tickets by plain ID;
- no repository paths or links; external links only when the link itself is the subject.

`backlog_check.py` enforces this only when the setting is on.

## Tests and code trace

A test proves a criterion by carrying its tag in the test's name (as the test runner reports it in JUnit XML), in either form:

- canonical: `[US-PAY-03/AC2]`, anywhere in the test name or in a describe or class name;
- identifier: `us_pay_03_ac2`, in any case, bounded by non-alphanumerics (`test_us_pay_03_ac2_refund_denied`, `TestUS_PAY_03_AC2`), for languages whose test names cannot hold brackets.

Tasks tag the same way (`[TASK-CI-01/AC1]`, `task_ci_01_ac1`). A tag must name a live criterion of an `in-progress` or `done` ticket. A `done` story needs at least one tagged test for every live criterion, unless it is `adopted: true`.

In code and test files (the `code` and `tests` globs in `kitchen.yml`), every `TODO`, `FIXME`, `XXX`, or `HACK` names a ticket ID, so nothing left for later is lost; every `DEC-…` mention must exist, and mentions of decided DECs are listed for revisiting. Files matching `kitchen.lock` (Test Kitchen's own) are never scanned. A file whose first ten lines contain `test-kitchen: no-trace` (in any comment syntax) is data, not trace: nothing in it is scanned, and its tags never prove a criterion, though the gates still see changes to it. Use it only for files whose text holds example tickets, such as tests of a tool that handles tickets.

## Delivery records

Every change request commits its description, verbatim, as a delivery record: the plan, test changes, review report, and checks live nowhere else, and a host does not carry them to another host. `python3 scripts/deliver.py record` writes it:

- a story or task change request: `backlog/<epic folder>/delivery/<ID>.md`;
- any other change request: `backlog/delivery/<branch, with / as ->.md`.

A record never overwrites another change request's record: a follow-up change request for the same ticket, or a colliding branch name, gets `<name>-cr<number>.md` (pass `--cr=<number>`). `deliver.py gate pr` fails when the record is missing or differs from the description. Records are history, not tickets: they have no frontmatter and `backlog_check.py` skips them.
