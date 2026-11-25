# Defining the product

The definition workflow (`/define` in Claude Code, `playbooks/define.md` everywhere) turns what people know into files the delivery workflow can build from: `docs/product.md`, requirement lines in `docs/requirements/`, ADRs, decision-log entries, and tickets in `backlog/`. The agent asks; people decide. Nothing is written without a yes.

## Modes

Without a mode, `/define` picks one: no content in `docs/product.md` means `new`; code but no backlog means it offers `adopt`; otherwise it asks what you want (change, refine, sweep).

| Mode | Use it to |
| --- | --- |
| `new` | Define a product from a description, layer by layer. |
| `change` | Add or change behavior: new requirements, amended ones, the tickets they need. |
| `sweep` | Walk the whole definition looking for gaps and inconsistencies. |
| `refine` | Make tickets ready: run `backlog_check.py --refine`, review each ready or draft ticket in `ticket` mode, fix with you, mark it `refined: <date>`. |
| `adopt` | Bring existing code in: map its behavior to requirements and done stories. |
| `slice` | Plan release slices. |
| `bug` | Triage a bug report. |
| `hotfix` | Open the urgent-fix lane when production is broken. |
| `ask` | Answer a question from the definition, read-only. |

## How it asks

- **Layers, in order:** vision, users and roles, capabilities (epics), boundaries (out of scope), requirements, architecture (an ADR or a DEC), stories and tasks.
- **About three questions per round**, each with a recommendation and its reason. The agent never invents an answer.
- **What cannot be answered now becomes a ticket:** a `DEC-` for a choice someone must make, a `SPK-` for something to verify first. It also asks "does this need deciding now?" and proposes deferring when it does not; deferring is itself a decision, and it is logged.
- **Decision format.** Every decision round shows: *Your next action* (one line); *Already fixed* (what the docs settle); lettered options, each with what it costs; the recommendation; *After you reply* (what will be written). Sub-questions come as a table of at most five rows.
- **After each decision, an ordered checklist:** the requirement text (or an ADR), the affected criteria (removed ones stay as placeholders), the epic's Open line, the DEC's status, the open questions of tickets it unblocks, the decision-log entry, then `backlog_check.py`.

## Checkpoints

At the end of each topic the agent shows exactly what it will write and writes only after a yes. Requirements are written on that yes. Stories and tasks are proposed and written on a yes. Done tickets are never rewritten: a change to delivered behavior is a new ticket. A ticket becomes `ready` only with an owner, so the checkpoint that proposes `ready` asks who owns it.

## Splitting rules

- Each requirement becomes a story, or is a constraint on one.
- Each criterion lives in exactly one story; others reference it as `US-PAY-03/AC2`.
- A story with more live criteria than `split_threshold` (default 6) gets a proposed split.
- In a large repository the agent works one group of epics at a time (with subagents, where the agent has them).

## Adopting existing code

`adopt` builds a capability map from the code, then:

- writes requirements marked `(observed in code)` until a person confirms them (each unconfirmed one is a gap);
- turns suspected bugs into decisions ("is this intended?"), never into requirements;
- records existing behavior as `done` stories with `adopted: true`; their missing tests are test debt (`backlog_check.py --test-debt`), a separate list that never blocks anything;
- gives each epic `code:` globs, so `--gaps` can report code that no epic claims;
- notes its progress in the decision log, so another session can continue a large adoption.

## Slices, bugs, hotfixes

- **slice:** five questions (what hurts most today, who the first users are, any deadline, what success looks like after a month, what can wait), then two to four proposed slices. On a yes, `releases:` goes into `kitchen.yml` and `release:` onto each ticket. Deferred tickets go to the last slice. Run it again to reshape.
- **bug:** (a) the code breaks an existing criterion: a fix story with `fixes: [US-…/ACn]` whose first test reproduces the bug, delivered normally; (b) no criterion covers the case: it is a missing requirement, handled in `change` mode; (c) unclear: a decision "is this intended?".
- **hotfix:** a story with `hotfix: true` whose criteria restore the broken behavior, a decision-log entry saying why the lane is used, and a draft task "Refine after hotfix US-…" for the follow-up. Delivery skips the plan review and the questions round and keeps everything else.

## Asking questions

`ask` is read-only. It answers from `docs/product.md`, the requirements, the ADRs, the decisions, the decision log, and the delivery records, citing each source. When nothing covers the question it says "not defined in this repo" and offers to open a DEC or SPK through normal define.

## Done means no gaps

The product is fully defined when `python3 scripts/backlog_check.py --gaps` prints nothing:

- no open decision, spike, or open question;
- every requirement that is not superseded is covered by ready or done tickets;
- no `(observed in code)` requirement left unconfirmed;
- every ready ticket is refined;
- no product code outside every epic's `code:` globs (checked once at least one epic declares `code:`).

Test debt is reported separately and is not a gap.

## Guardrails

- Platform or tool claims are checked in their official docs before they are written down.
- Constraints people report are recorded in their words, with their uncertainty.
- After bulk renames, headings and tables are re-read.

## From delivery back to definition

When `deliver.py next` finds nothing ready, `/deliver` hands off here: first the decisions blocking waiting tickets (the `DECIDE` lines, most-blocking first), then the drafts to refine (the `REFINE` lines), then the question "what next?".
