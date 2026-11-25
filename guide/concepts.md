# Concepts

Test Kitchen keeps a project's definition and its delivery in the repository, as plain files that people, agents, and scripts all read. This page names the pieces. [workflow.md](workflow.md) shows them in motion; [why.md](why.md) explains why each rule exists.

## The definition: product, requirements, decisions

- **`docs/product.md`**: the vision, the users and their roles, the capabilities, and the boundaries (what is out of scope).
- **Requirements**: one file per epic code, `docs/requirements/<CODE>-<name>.md`, holding requirement lines such as `- PAY-R03: A refund never exceeds the order total.` An ID is a code of 2 to 10 capitals or digits starting with a letter, `-R`, and two or more digits (`[A-Z][A-Z0-9]{1,9}-R\d{2,}`). Headings and prose around the lines are free. Two markers can start a requirement's text:
  - `(observed in code)`: written by the adopt mode from existing code and not yet confirmed by a person. It counts as a gap until someone confirms it.
  - `(superseded 2026-11-24 by PAY-R07)`: no longer binding. It leaves coverage, and tickets that still cite it are flagged.
- **Architecture decisions (ADRs)**: `docs/architecture/ADR-001-<slug>.md`, each with a `Status: proposed | accepted | superseded by ADR-nnn` line. Accepted ADRs bind every ticket.
- **The decision log**: `docs/decision-log.md`, entries headed `### YYYY-MM-DD — Title` (with an em dash), newest first. Each says what was decided, why, who decided, and where it is recorded.

## Tickets

Tickets live in `backlog/`, one folder per epic (`backlog/<CODE>-<slug>/`, holding `epic.md`), one markdown file per ticket with YAML frontmatter. The file name is the ID, a dash, and a kebab-case slug.

| Type | ID | Purpose | Done when |
| --- | --- | --- | --- |
| epic | `EP-PAY` | A capability; groups its tickets | All its tickets are done or deferred |
| story | `US-PAY-03` | User-facing behavior with acceptance criteria | Every live criterion has a passing tagged test |
| task | `TASK-CI-01` | Technical work with no user-facing behavior (refactor, upgrade, CI, test debt) | Every live criterion is met and reviewed |
| decision | `DEC-PAY-02` | A question a person must decide | The answer is recorded in `docs/` and the decision log |
| spike | `SPK-PAY-01` | A time-boxed investigation | Findings recorded, follow-ups filed |

IDs are stable: never renumbered, never reused. The frontmatter carries `id`, `type`, `title`, `epic`, `source_reqs` (the requirement IDs the ticket implements; empty only for tasks and spikes), `blocked_by`, `owner`, `assignee_type` (`human`, `agent`, or `either`; decisions are always `human`), `status` (`draft`, `ready`, `in-progress`, `done`, `deferred`), and optional fields: `priority`, `release`, `refined`, `adopted`, `hotfix`, `fixes`, and, on epics, `code` (the code areas the epic owns). `backlog/README.md` in an installed project is the full reference.

**Blocked by** means "can start, can't finish": a ticket can be `ready` while a blocker is unfinished, but `deliver.py next` never picks it until every blocker is done.

**Readiness.** A ticket can be `ready`, `in-progress`, or `done` only when its owner is set (not `TBD`), every open question is answered, a story or task has at least one live criterion, and, when release slices are on, it has a `release`.

## Acceptance criteria

A story says `As a <role>, I want <capability>, so that <outcome>.` and lists criteria:

```markdown
## Acceptance criteria

- AC1: Given an order of 40.00, when a refund of 40.00 is requested, then it is accepted.
- AC2: Given an order of 40.00, when a refund of 40.01 is requested, then it is refused with "Refund exceeds the order total".
- AC3: (removed 2026-11-24, replaced by AC4)
- AC4: Given …
```

Tasks use checkable statements instead of Given/when/then. Criteria numbers are stable: a new criterion takes the next number; a removed one stays as a placeholder with the date and the reason; a change of meaning is a removal plus a new criterion. A criterion that is not removed is **live**. Elsewhere a criterion is referred to as `US-PAY-03/AC2`.

**Open questions** sit in each ticket. Every bullet starts with `None` or names a DEC or SPK ticket. When that ticket is not done and not in `blocked_by`, the bullet says what the code does meanwhile (`Until decided: …`) and names the criterion that defines it. Code that meets an open decision fails closed.

## Test tags

A test proves a criterion by carrying its tag in its name, as the test runner reports it in JUnit XML. Two equivalent forms exist so every language can tag:

- canonical: `[US-PAY-03/AC2]`, anywhere in the test name or in a describe or class name;
- identifier: `us_pay_03_ac2`, in any case, bounded by characters that are not letters or digits: `test_us_pay_03_ac2_refund_denied`, `TestUS_PAY_03_AC2`.

Tasks use the same forms (`[TASK-CI-01/AC1]`, `task_ci_01_ac1`). A tag must name a live criterion of an `in-progress` or `done` ticket. A `done` story needs at least one tagged test per live criterion, unless it is `adopted: true`: then the missing tests are **test debt**, listed by `backlog_check.py --test-debt` and never an error. [test-runners.md](test-runners.md) shows where the tag goes for each runner.

## The freeze

Tests come before code. On a ticket's branch, the tagged tests are written first and `deliver.py gate red <ID>` runs them: every live criterion must have a tagged test that ran, and at least one must fail, because the behavior does not exist yet. Then the test files alone are committed with the message `test: <ID> failing tests`. That commit is **the freeze**: exactly one per branch, with no product code changed at or before it.

After the freeze, a test changes only where it contradicts the ticket or an ADR, and every test file changed after the freeze is listed under "Test changes" in the change request. No criterion may lose its tagged tests, and no skipped or focused test (`.skip(`, `.only(`, `@pytest.mark.skip`, `t.Skip(`, `@Disabled`, …) may be added.

## Reviews

A reviewer with fresh context, given only the inputs `playbooks/review.md` lists, checks the work. It has four modes: `plan` (the plan against the ticket), `tests` (the failing tests against the criteria), `diff` (the final change), and `ticket` (a ticket's readiness during refinement). Findings are `CRITICAL`, `WARNING`, or `SUGGESTION`. Every review ends with the tally line `CRITICAL: n, WARNING: n, SUGGESTION: n`; a diff review also ends with `Reviewed commit: <sha>`. A change to product code or tests after that commit needs another review.

## Change requests and records

Test Kitchen says **change request** for the host's unit of review; [hosts.md](hosts.md) gives each host's own name for it. One ticket per branch and change request. The ticket branch is the ticket file's name without `.md`, lowercased (`us-pay-03-refund-over-total`); decision work uses `docs/dec-<id>-<slug>`.

The change-request description has fixed sections: `## Ticket` (starting with the ticket ID, or `None. …` for a change with no ticket), `## Plan` (one row per live criterion, then `Constrained by:`), `## Gaps found`, `## Decisions`, `## Platform changes`, `## Test changes`, `## Review report`, and `## Checks`. Each gap names the ticket that holds it; each decision or platform change ends with `Log: <decision-log entry title>` or names a done DEC. A section may be a single `None`.

The description is committed, word for word, as the **delivery record**: `backlog/<epic folder>/delivery/<ID>.md` for a ticket, `backlog/delivery/<branch>.md` otherwise. The record outlives the change request and the host.

## Gates

The scripts, not the agent, decide whether work may move on:

| Gate | Checks | Runs |
| --- | --- | --- |
| `backlog_check.py` | Tickets well formed, IDs and links resolve, readiness, tags name live criteria, done stories have tests, TODOs name tickets, no `blocked_by` cycles, coverage of requirements | Locally, in `deliver.py check`, in CI |
| `deliver.py gate red <ID>` | Each live criterion has a tagged test that ran, and at least one failed | Before the freeze |
| `deliver.py gate pr` | Branch and record match the ticket; a plan row per live criterion; the freeze; no lost tags; test changes listed; no skips added; the last review has `CRITICAL: 0` and nothing changed after it; the ticket is done (or the description says why not) | Locally and in CI on every change request |
| `deliver.py gate merge <n> --head=<sha>` | The host says the change request is open, ready, mergeable, up to date, at that exact commit, with a passing `check` job and no failing or pending check, and `gate pr` passes | Before every merge (the guard runs it in Claude Code) |
| `deliver.py check` | `backlog_check.py`, the scripts' self-tests, then `check_command` or the full test run | Locally and as the CI `check` job |

## Code trace

In files matching `code` or `tests`, every `TODO`, `FIXME`, `XXX`, and `HACK` names a ticket ID, and every `DEC-…` mention names a ticket that exists (done ones are listed so they can be revisited). Files matching `kitchen.lock` (Test Kitchen's own) are never scanned. A file whose first ten lines contain `test-kitchen: no-trace` (in any comment syntax) is data, not trace: nothing in it is scanned, and its tags never prove a criterion, though the gates still see changes to it. Use it only for files whose text holds example tickets, such as tests of a tool that handles tickets.
