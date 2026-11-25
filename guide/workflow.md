# A day with Test Kitchen

This page follows one project from a rough idea to a release note. Commands are shown for Claude Code (`/define`, `/deliver`); in other agents, ask the agent to follow the playbook named next to each command ([agents.md](agents.md)). The scripts are the same everywhere.

## Morning: define

You open the project and run `/define` (`playbooks/define.md`). With an empty `docs/product.md`, it starts in mode `new` and asks:

> Describe the product in a few sentences: who uses it, what problem it solves for them, and what it looks like when it works. Rough is fine; we'll refine it together.

From your answer it works through the layers in order: vision, users and roles, capabilities (each becomes an epic), boundaries (what is out of scope), requirements, architecture, then stories and tasks. It asks about three questions per round, each with a recommendation and its reason. When you cannot answer yet, the question becomes a decision ticket (`DEC-`) if it is a choice, or a spike (`SPK-`) if something must be verified first. At the end of each topic it shows exactly what it will write and writes only after your yes.

By lunch you have `docs/product.md`, `docs/requirements/PAY-payments.md` with lines such as `- PAY-R03: A refund never exceeds the order total.`, an epic `backlog/PAY-payments/epic.md`, and stories such as `US-PAY-03` with numbered acceptance criteria. Stories you gave an owner and whose questions are answered are `ready`.

`python3 scripts/backlog_check.py --gaps` lists what still keeps the product from being fully defined: open decisions and spikes, drafts, unanswered questions, uncovered requirements, unconfirmed `(observed in code)` requirements, ready tickets not yet refined, and code no epic claims. [define.md](define.md) covers every mode.

## Afternoon: deliver

You run `/deliver next` (`playbooks/deliver.md`). `deliver.py next` picks the ticket: ready stories, tasks, and spikes not assigned to a person, whose blockers are done and whose branch nobody has taken, ordered by release slice, then priority (a ticket inherits the priority of the work it unblocks), then how many tickets it unblocks, then tickets you own, then ID. Say it picks `US-PAY-03`. The agent then runs the fourteen steps:

| Step | What happens |
| --- | --- |
| 1. Start | Branch `us-pay-03-refund-over-total` from an up-to-date default branch; `deliver.py context US-PAY-03` prints the criteria, the cited requirement text, the ADRs, and related tickets. |
| 2. Plan | From `deliver.py pr-body US-PAY-03`: one row per live criterion with its tests (allowed case, denied case, every limit and empty state), plus files and constraints. |
| 3. Questions | One round of questions about anything a user would notice that the ticket leaves open. |
| 4. Plan review | The fresh-context reviewer checks the plan against the ticket. |
| 5. Claim | The ticket goes `in-progress`; a draft change request shows the work is taken. |
| 6. Tests first | Tagged tests are written; `deliver.py gate red US-PAY-03` proves each criterion has a test that fails; the reviewer checks the tests; the freeze commit `test: US-PAY-03 failing tests`. |
| 7. Implement | Code until the tests pass. Frozen tests change only where they contradict the ticket or an ADR, and each change is listed. |
| 8. Check | Merge the default branch in; `python3 scripts/deliver.py check`. |
| 9. Final review | The reviewer checks the diff and ends with `Reviewed commit: <sha>` and the tally. CRITICAL findings are fixed. |
| 10. Capture | Every gap filed as a ticket, every decision and platform change logged; the ticket set to `done`. |
| 11. Change request | Every description section filled; the description committed as the delivery record (`deliver.py record`); `backlog_check.py --pr-body` and `deliver.py gate pr` pass; the change request marked ready. |
| 12. Merge | Once the checks pass on the head commit, `deliver.py merge-command <n> --head=<sha>` prints the one allowed merge command; `gate merge` runs first (in Claude Code the guard runs it). |
| 13. Verify | The change is tried after it ships, following `verify` in `kitchen.yml`; without it the record says "not verified after deploy". |
| 14. Close | Back to an up-to-date default branch; a report of what shipped, what was decided, and what was filed. |

How far the agent goes alone depends on `autonomy` in `kitchen.yml`: with `merge` it merges on green; with `pr` it stops at a ready change request and you merge; with `supervised` you also approve the plan and the tests. On the manual host, the agent always stops at "ready to merge".

The agent stops and asks you when it meets something only a person may settle: a decision to choose, a criterion that is ambiguous or would change, any change under `docs/`, a test that would have to be weakened, a gate that keeps failing, a failed deploy, a credential. It asks everything open in one round. `/deliver all` keeps going ticket after ticket until nothing is ready or a question needs you.

When nothing is ready, `/deliver` hands off to define: it brings you the decisions that block waiting tickets, most-blocking first, then the drafts to refine, then asks what to build next.

## Any time: status

```sh
python3 scripts/deliver.py status
```

One screen: how many tickets are in each status; the ready list in the order `next` would take them; what is in progress and on which branch; what is blocked and by what; open decisions and spikes; the gap count with the first few gaps; the test-debt count; the last five deliveries.

## Evening: release notes

```sh
python3 scripts/deliver.py release-notes          # tickets delivered since the last git tag
python3 scripts/deliver.py release-notes v1       # done tickets in release slice v1
```

Markdown on stdout: stories listed by their "so that …" outcome with their IDs, grouped under their epic; tasks and hotfixes under "Other changes". It never invents text: what it prints comes from the tickets.

## Other days

- **A bug report.** `/define bug` triages it: if the code breaks an existing criterion, a fix story with `fixes: [US-PAY-01/AC2]` whose first test reproduces the bug; if no criterion covers the case, a missing requirement (mode `change`); if unclear, a decision "is this intended?".
- **Production is broken.** `/define hotfix` creates a story with `hotfix: true`, a decision-log entry saying why the fast lane is used, and a draft task to refine it afterwards. `/deliver` skips the plan review and the questions round but keeps tests first, the review, the record, and the gates.
- **Existing code.** `/define adopt` maps what the code already does into requirements marked `(observed in code)` and `done` stories marked `adopted: true`; missing tests become test debt, never a blocker.
- **Planning releases.** `/define slice` asks five questions and proposes two to four release slices, written to `releases:` in `kitchen.yml` and `release:` on each ticket.
