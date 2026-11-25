# Define

How what a person knows becomes requirements, decisions, and tickets that `playbooks/deliver.md` can build, without anything being invented on the way. This playbook is the single source of the definition process: any AI agent or person follows it as written. In Claude Code, `/define` runs it; other agents are asked to follow this file.

The person decides. You ask, propose, record, and validate.

## Guardrails

- **Never invent.** A recommendation is not a decision, and a gap is not yours to fill. What the person cannot answer now becomes a DEC (a choice someone must make) or an SPK (something to verify first).
- **Write only after a yes** (see "Checkpoints"). A yes covers what was shown, nothing more.
- **Never upgrade certainty.** A proposal, a report, or a recollection never becomes "confirmed" without the person saying so.
- **Verify platform and tool claims in their official documentation before writing them.** A wrong "feature X does not exist" survives into requirements, tickets, and ADRs.
- **Record what people report verbatim, with its uncertainty** ("reported by the support team, unverified"). Rewording a reported constraint quietly changes it.
- **After bulk renames or find-and-replace, re-read every heading and table you touched.** Bulk edits break structure in ways a search does not show.
- **Decisions go into `docs/decision-log.md`,** never into an assistant's private memory: the next session, other agents, and other people cannot see private memory.
- **Never record credentials, tokens, or secrets.**
- **Permission.** Running this playbook is the request to write what the person approves at checkpoints, and to commit it through a change request (see "Committing"). It is not permission to decide anything.

## Commands and modes

`/define [mode] [topic]` in Claude Code; in other agents, ask: "Follow `playbooks/define.md`, mode `change`: <topic>."

| Mode | Use when | Writes |
| --- | --- | --- |
| `new` | There is no product definition yet | `docs/product.md`, requirements, ADRs, epics, tickets |
| `change` | A person wants to add or change behavior | Requirements, ADRs or DECs, tickets |
| `sweep` | Closing every definition gap `backlog_check.py --gaps` lists | Whatever each gap needs |
| `refine` | Getting tickets ready: clear, testable, owned, reviewed | Tickets (`refined:` dates) |
| `adopt` | The code exists but the backlog doesn't (or covers part of it) | Requirements `(observed in code)`, done stories `adopted: true`, epic `code:` globs |
| `slice` | Ordering work into releases | `releases:` in `kitchen.yml`, `release:` on tickets |
| `bug` | Something behaves wrongly | A fix story, a `change`, or a DEC |
| `hotfix` | Production is broken now | A hotfix story, a decision-log entry, a follow-up task |
| `ask` | A question about what the product does or must do | Nothing |

**Without a mode:**

- `docs/product.md` has no content (only its headings and comments) → `new`.
- There is code but no ticket under `backlog/` → offer `adopt`.
- Otherwise, run `python3 scripts/backlog_check.py --gaps`, summarize it in one line, and ask what the person wants: `change`, `refine`, or `sweep`.

## Layers

A product is defined in this order, because each layer is the input of the next. Finish a layer's checkpoint before moving down; go back up when a lower layer shows a gap above it.

| Layer | Written to |
| --- | --- |
| Vision | `docs/product.md`, "Vision" |
| Users and roles | `docs/product.md`, "Users and roles" |
| Capabilities (epics) | `docs/product.md`, "Capabilities"; one epic per capability, `backlog/<CODE>-<slug>/epic.md` |
| Boundaries (out of scope) | `docs/product.md`, "Boundaries"; each epic's `## Boundaries` |
| Requirements | `docs/requirements/<CODE>-<name>.md` |
| Architecture | `docs/architecture/ADR-nnn-<slug>.md` once decided; a DEC ticket while open |
| Stories and tasks | `backlog/<CODE>-<slug>/` |

**Epic codes** are one capital letter, then one to nine capitals or digits (`PAY`, `AUTH`, `CORE`), chosen with the person. One code names the epic, its folder, its requirements file, and every ticket and requirement ID in it.

**Requirements** are bullets in the epic's requirements file, one testable statement each:

```markdown
- PAY-R03: A refund never exceeds the order total.
```

- A new requirement takes the next free number in its file. IDs are never renumbered or reused: tickets, tests, and the decision log point to them.
- A wording fix that keeps the meaning is an edit. A change of meaning supersedes: mark the old line `(superseded YYYY-MM-DD by PAY-R07)` at the start of its text and add the new requirement. Superseded requirements no longer bind and are excluded from coverage.
- `(observed in code)` at the start of the text marks a requirement written by `adopt` that no person has confirmed yet. It counts as a gap until the person confirms it and the marker is removed.

**ADRs** record architecture decisions; their format is in `docs/architecture/README.md`. An accepted ADR binds every ticket.

**Tickets** follow `backlog/README.md`.

## Questioning

- **About three questions per round.** Each states the question in plain words, your recommendation, and why. More than that and answers get shallow; fewer and the work stalls.
- **Never invent an answer.** When the person doesn't know, propose a DEC (if it is a choice) or an SPK (if something must be verified first), and move on.
- **Does this need deciding now?** Ask yourself before every decision. If nothing ready, nothing in the current release slice, and nothing being built depends on it, propose deferring it. Deferring is itself a decision: it is logged, the DEC gets `status: deferred`, and every ticket that names it states its interim behavior (`Until decided: …`) or is deferred with it.
- **Short answers are normal** ("a", "ok", "1 yes, 2 no"). If an answer is ambiguous, say how you read it when you report back.
- **Options come from the record.** Present only the options `docs/` or the DEC records as recorded options; label your own as proposals.

### Decision format

Use this for every DEC, and for any round where the person chooses:

```markdown
**Next: DEC-PAY-02, <the question in plain words>.**

**Your next action:** <exactly what to reply, in one line: "pick a or b", or "ok, or change any row">.

**Already fixed:** <what docs/ and earlier decisions settle, with their IDs>.

- (a) **<option> (recommended).** <why, and what it costs>.
- (b) <option>. <what it costs>.
- (c) Defer. <what stays open, and the interim behavior>.

**After you reply:** <what will be written, and where>.
```

Several small sub-questions go in one table of at most five rows, answered with "ok" or the rows to change:

```markdown
| # | Question | Recommendation | Why |
| --- | --- | --- | --- |
| 1 | … | … | … |
```

### Applying a decision

After each answer, apply it everywhere in one pass, in this order:

1. The requirement text in `docs/requirements/` (a new ID, a wording fix, or a superseded line plus a new ID), or an ADR for an architecture choice.
2. The affected criteria and tickets: removed criteria stay as placeholders (`- AC4: (removed YYYY-MM-DD, DEC-PAY-02)`), new criteria take the next numbers, new requirements get new tickets. A `done` ticket is never rewritten: its change is a new ticket.
3. The epic's `## Open` line: remove the DEC.
4. The DEC: add `## Outcome` (the date, the answer, who decided, where it is recorded) and set `status: done` (or `deferred`).
5. The tickets it unblocks: remove it from `blocked_by`, and update every open question that named it.
6. The decision-log entry (below).
7. `python3 scripts/backlog_check.py`, which must exit 0.

Then report what changed in a few lines and present the next decision.

### Decision-log entries

`docs/decision-log.md`, newest first:

```markdown
### YYYY-MM-DD — <short, unique title>

- Decision: <what was decided>. Closes DEC-PAY-02.
- Why: <the reason>.
- Decided by: <person or role>.
- Recorded in: <requirement IDs, ADR, ticket IDs>.
```

Change requests cite entries by title (`Log: <title>`), so never rename a title. When a later decision replaces one, say so in the new entry and add a `- Superseded by: <new title>` line to the old one.

## Checkpoints

- At the end of each topic (a layer, an epic's requirements, a decision, a batch of tickets), show exactly what you will write: each file, each section, and the text. Write only after a yes. A yes covers what was shown; the next topic needs its own.
- **Requirements are always written** at their checkpoint, on the yes: what the person confirmed never stays only in chat.
- **Stories and tasks are always proposed,** and written only on a yes. A no leaves their requirements uncovered, which `--gaps` keeps listing.
- **Done tickets are never rewritten.** A change to done behavior becomes a new ticket, because the done ticket is the record of what was built and tested.
- **Readiness needs an owner.** The checkpoint that proposes `ready` asks who owns each ticket.
- After writing, run `python3 scripts/backlog_check.py` (it must exit 0) and report what changed.

## Splitting

- Each requirement becomes a story (what someone does and sees), a task (technical work with no user-facing behavior), or a constraint cited in `source_reqs` by the story it constrains.
- Each criterion lives in exactly one story. Another story that depends on it references `US-…/ACn`.
- Criteria come from the requirement text: the allowed case, the denied case, and every limit and empty state it names. Proposals and candidate designs go in Notes, never in criteria.
- Propose a split when a story has more live criteria than `split_threshold` (`kitchen.yml`, default 6), along a seam a user would notice: per role, per action, or per data state.
- Every gap becomes an open question naming a DEC or SPK, never a criterion.
- **Large repositories:** work one epic group at a time. Where the agent has subagents, give each group to one (with `backlog/README.md` and the group's requirement IDs) in parallel, then de-duplicate the overlaps yourself by topic: the same criterion in two stories, the same question in two DECs.

## Modes

### new

1. Ask exactly: "Describe the product in a few sentences: who uses it, what problem it solves for them, and what it looks like when it works. Rough is fine; we'll refine it together."
2. Draft the vision from the answer, in the person's words. Checkpoint.
3. Work down the layers: users and roles, capabilities (propose the epics and their codes), boundaries, then each epic's requirements, with question rounds and a checkpoint per topic.
4. Architecture: the choices the requirements force (where data lives, how it is hosted, what it integrates with). A choice the person makes becomes an ADR; an open one becomes a DEC.
5. Stories and tasks, per epic: propose them; write them as `draft` on a yes. Then run `refine` on them; the checkpoint that proposes `ready` asks for owners.
6. Offer to draft the `## This project` section of `AGENTS.md` (what the product is, the stack, how to install and run it, the coding rules), written only on a yes.
7. Offer `slice` if the work needs ordering into releases.
8. Run `python3 scripts/backlog_check.py --gaps` and continue as `sweep` until it prints nothing or the person stops.

### change

1. Restate the change in one sentence, and confirm it.
2. Find what it touches: the `docs/product.md` sections, the requirements (search their IDs and text), the ADRs, the DECs, and the tickets with their status.
3. Ask a question round about what the change leaves open.
4. Checkpoint: propose the new or superseded requirements, any ADR or DEC, and the ticket changes. Tickets that aren't done get criteria removed as placeholders and new ones appended; done tickets stay as they are and the change becomes a new ticket; tickets citing a superseded requirement are updated.
5. Apply on the yes, log the decision, run `backlog_check.py`, and `refine` the tickets you changed.

### sweep

Run `python3 scripts/backlog_check.py --gaps` and close each line, the ones blocking most work first:

| Gap | What closes it |
| --- | --- |
| An open DEC | A decision round, or a deferral the person approves |
| An open SPK | Delivering it (`playbooks/deliver.md`, "Spikes"), or asking the person for what it needs |
| A `draft` ticket | `refine` |
| An unanswered open question | An answer from the person, or a DEC or SPK |
| An uncovered requirement | A story or task that cites it, a constraint citation, or (with the person's yes) deferring its epic or superseding it |
| An `(observed in code)` requirement | The person confirms it (remove the marker), corrects it, or a DEC asks "Is this intended?" |
| A ready ticket without `refined:` | `refine` |
| Code no epic claims (one line per file, or one line in all when no epic declares `code:` yet) | Its globs added to an epic's `code:`, or a new epic |
| `docs/product.md` missing or only headings and comments | `new` (or `adopt` for existing code) |
| No requirements defined | `new`, `change`, or `adopt` |

Stop when `--gaps` prints nothing or the person stops, and report what is left.

### refine

1. Run `python3 scripts/backlog_check.py --refine` and handle each finding with the person: stories over `split_threshold` (propose a split), tickets citing superseded requirements, open questions naming a DEC that is now done, tickets missing a `release`, done hotfixes (their follow-up task), and tickets `in-progress` with no branch on origin (ask who holds them).
2. Run the reviewer in `ticket` mode on each ready or draft ticket, in a fresh context, with only the inputs `playbooks/review.md` lists for that mode.
3. Fix the findings with the person; criteria changes need a yes.
4. A ticket passes when its review has no CRITICAL left and every WARNING is settled. Set `refined: <today>`. The checkpoint that proposes `ready` asks for the owner.

A refined ticket whose criteria or open questions change later is reviewed again and gets a new date.

### adopt

For code that exists before its backlog. Existing behavior is recorded as it is, and the person confirms it; nothing is presented as intended until they do.

1. Build a capability map from the code: what users and callers can do, grouped into proposed epics, each with the `code:` globs it owns. Checkpoint.
2. Per epic (one subagent per epic group, where the agent has them): read the code and its tests, and propose:
   - requirements marked `(observed in code)`, describing what the code does now;
   - for each suspected bug, a DEC "Is this intended?" with the current behavior and the likely intended one;
   - stories for the existing behavior, `status: done` and `adopted: true`, whose criteria describe what the code does now (the checkpoint asks for owners);
   - the epic's `code:` globs.

   Write them on a yes.
3. Report missing tests as test debt (`python3 scripts/backlog_check.py --test-debt`): a separate list, never blocking. Offer tasks to pay it down.
4. Walk the person through the `(observed in code)` requirements; remove the marker from each one they confirm, and log what was confirmed.
5. Offer to draft the `## This project` section of `AGENTS.md` from what the code shows.
6. Adoption can span sessions. At the end of each session, add a decision-log entry ("Adopt progress: …") listing the epics done, in progress, and not started, so another session can continue.

### slice

1. Ask in one message:
   1. What hurts most today?
   2. Who uses it first, and how many?
   3. Is there a deadline or event?
   4. What does success look like a month after release?
   5. What can wait without anyone complaining?
2. Propose two to four slices in a table (`Slice | Users get | Epics | Waits on`). Order them so the first slices depend on nothing slow (external access, open spikes); run spikes that gate a later slice alongside the earlier ones. What every later slice needs (sign-in, permissions, the core records) usually goes first, even when the pain is elsewhere. Name what is left out.
3. On a yes: write `releases:` in `kitchen.yml` and `release:` on every story, task, and spike (deferred tickets go to the last slice), and log the decision with the slices and the success measure.

`/define slice` reshapes the slices later; moving a ticket between slices is a decision too. Once releases are on, `backlog_check.py` refuses an unfinished blocker in a later slice than the ticket it blocks.

### bug

Get the facts first, verbatim: what was done, what was expected, what happened, and where. Then triage:

- **(a) The code breaks an existing criterion.** Propose a fix story with `fixes: [US-…/ACn]`, citing the broken story's requirements, whose criteria restore that behavior for the reported case. Its first test reproduces the bug. It is delivered normally.
- **(b) No criterion covers the case.** It is a missing requirement: continue in `change`.
- **(c) Unclear whether it is a bug.** Open a DEC "Is this intended?" with what happens and what was expected.

### hotfix

Production is broken and cannot wait for the normal lane. In one checkpoint, propose and, on a yes, write:

- a story with `hotfix: true` whose criteria restore the broken behavior (with `fixes:` when it broke a criterion), with an owner, set `ready`;
- a decision-log entry saying why the hotfix lane is used;
- a draft task "Refine after hotfix US-…" for the follow-up (refine the hotfix story, file what it left out).

`/deliver` then skips the plan review and the questions round, but keeps tests first, the review, the record, and every gate.

### ask

Read-only: never writes. Answer from `docs/product.md`, the requirements, the ADRs, the DECs, the decision log, and the delivery records, citing each source (file and ID), and keep their qualifiers (`observed in code`, superseded, proposal, open). If nothing covers the question, say "not defined in this repo" and offer to open a DEC or SPK through normal define. Never fill the gap from general knowledge.

## Done

The product is fully defined when `python3 scripts/backlog_check.py --gaps` prints nothing: `docs/product.md` describes the product; at least one requirement exists; no open DEC, SPK, or question; every requirement covered by ready or done tickets; every code file inside some epic's `code:` globs; every ready ticket refined. An installed project with nothing defined yet is not "fully defined": `--gaps` lists its skeleton-only `docs/product.md`, "no requirements defined", and, when code exists, one line for code no epic claims.

Test debt (`--test-debt`) is a separate list and never keeps the product from being defined.

## Hand-off from deliver

When `deliver.py next` finds nothing ready, `playbooks/deliver.md` hands off here: first the `DECIDE` list (a decision round each, most-blocking first), then the `REFINE` list (`refine` on each), then the question "What should we build next?". With `/deliver all`, delivery resumes as soon as something is ready.

## Committing

Define writes on a branch of its own: `docs/define-<topic>` (or `docs/dec-<…>` for a single DEC, as `playbooks/deliver.md` describes). Once the topic's checkpoints are written:

1. Commit, and open a change request with `## Ticket` starting `None. Defines …`, every decision as a `## Decisions` bullet ending `Log: <entry title>`, and every gap left as a `## Gaps found` bullet naming its ticket.
2. Write and commit the delivery record, and run `backlog_check.py --pr-body` and `deliver.py gate pr`, as in step 11 of `playbooks/deliver.md`.
3. Merge as in step 12 of `playbooks/deliver.md`, which follows the autonomy level.

The default branch is what `deliver.py next`, other sessions, and other people read: definitions left on a branch are invisible to them. In Claude Code, the guard asks the person before each edit under `docs/` and to `AGENTS.md` and `kitchen.yml`; that is expected, since those edits follow a checkpoint yes.
