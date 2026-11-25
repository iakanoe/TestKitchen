# Deliver

How a ticket goes from `ready` to merged and verified. This playbook is the single source of the delivery process: any AI agent or person follows it as written. In Claude Code, `/deliver` runs it; other agents are asked to follow this file. `CONTRIBUTING.md` explains why the process looks like this and what enforces it; `backlog/README.md` holds the ticket rules; `playbooks/review.md` is the reviewer's brief; `playbooks/define.md` is where tickets come from.

The person running you wants you to work without stopping. Stop only for the reasons in "Stop and ask". In every other case, decide, record the decision, and keep going.

## Ground rules

- **Facts come from files and scripts, never from memory.** Before you state a criterion, a requirement, a ticket status, or a check result, read it from `scripts/deliver.py`, the file, or a command's output in this session. If you didn't read it, you don't know it.
- **Quote, don't paraphrase,** when a criterion's or requirement's text matters to a choice. Paraphrase drifts, and the drift becomes the spec.
- **A gate's FAIL is final.** Fix the cause and rerun the gate. Never reword, skip, or work around a gate: the gates are the only part of the process that does not depend on anyone's judgment.
- **Agents never decide.** Choosing a DEC's option, changing a criterion, changing anything under `docs/`, and changing platform settings need a person. Code that meets an open DEC fails closed (it refuses, or does the least, until the DEC is decided).
- **Nothing stays only in chat.** Every gap is filed as a ticket, every decision and platform change gets a decision-log entry, and the change request lists them all. Chat is gone after the session; the repository is what the next reader has.
- **Permission.** Running this playbook is the request to commit, push, open the change request, and (with autonomy `merge`) merge on green, for the ticket it works on. It is not permission for anything in "Stop and ask".
- **One checkout.** Work in this checkout, on the ticket's own branch. Never create another folder or worktree for the work, and never switch away from uncommitted or unmerged work: the gates read this checkout, and another checkout may hold someone's work in progress.
- **Where rules live.** Ticket format and readiness: `backlog/README.md`. Project coding rules: the `## This project` section of `AGENTS.md`. If they disagree with this playbook, they win, and the disagreement is a gap to file.

## Commands

| Command (Claude Code) | Other agents: ask for | Does |
| --- | --- | --- |
| `/deliver <ID>` | "Deliver US-PAY-03 following `playbooks/deliver.md`." | Delivers that ticket: a story or task through the 14 steps, a spike or DEC through its variant below. An epic is not delivered; its tickets are. |
| `/deliver next` (or no argument) | "Deliver the next ticket following `playbooks/deliver.md`." | Runs `deliver.py next` and delivers the ticket it names. |
| `/deliver all` | "Deliver tickets until none is ready, following `playbooks/deliver.md`." | Repeats `next` until nothing is ready and the hand-off to define leaves nothing to do, or a question needs a person. Ends by printing `python3 scripts/deliver.py status`. |

Keep a list of the steps for the current ticket and tick them off as you go.

## Picking

```bash
git fetch origin
python3 scripts/deliver.py next
```

- `NEXT <ID> …` names the ticket to take and its branch. Take it.
- `READY <ID> …` lines are the other ready tickets, in order; `WAIT <ID>: <why>` lines say why each remaining ticket waits (an unfinished blocker, assigned to a person, its branch already taken).
- The order is fixed by the script: release slice (when releases are on), effective priority, how many unfinished tickets each one unblocks, owned by the person running it, then ID. Never pick by your own judgment over the script's order. If you think the order is wrong, say so and ask.
- `NEXT none …` means nothing is ready: hand off to define (next section).

## When nothing is ready: hand off to define

When `deliver.py next` prints `NEXT none`, it also prints what would unblock work:

1. **`DECIDE <DEC>` lines,** the DECs blocking waiting tickets, most-blocking first. Run a decision round for each, in that order, one at a time: the decision format and the apply checklist in `playbooks/define.md`, delivered as in "Decisions (DEC)" below.
2. **`REFINE <ID>` lines,** the draft tickets, in the same order. Run `playbooks/define.md` mode `refine` on each until it is `ready` and refined (an owner, every open question answered, the reviewer's ticket mode passed).
3. **Neither** (`NEXT none: nothing is ready or waiting; run /define to plan more work`): ask the person "What should we build next?" and continue in `playbooks/define.md` (mode `change`, or `new` for a new product).

With `/deliver all`, once a decision or refinement has reached the default branch, run `deliver.py next` again; as soon as it names a ticket, resume delivering.

**Headless** (no person to ask, for example an unattended run): never decide, never mark a ticket ready. Print a decision brief in the decision format of `playbooks/define.md` for each `DECIDE` line, then the `REFINE` list with what each draft lacks, and stop.

## The steps

| Step | Done when |
| --- | --- |
| 1. Start | Branch created, context read |
| 2. Plan | A plan row per live criterion, with its tests |
| 3. Questions | Every question answered or filed |
| 4. Plan review | No CRITICAL finding left (and, if supervised, the plan approved) |
| 5. Claim | Ticket `in-progress`, branch pushed, draft change request open |
| 6. Tests first | `gate red` passes, tests reviewed, tests frozen |
| 7. Implement | Tests pass |
| 8. Check | `deliver.py check` passes |
| 9. Final review | Tally shows `CRITICAL: 0` |
| 10. Capture | Nothing found is unrecorded |
| 11. Change request | Description and record checked, change request ready |
| 12. Merge | Merged, or handed to a person as ready to merge |
| 13. Verify | Behavior seen after the merge, or reported as not verified |
| 14. Close | Reported |

A person following this playbook by hand approves the plan (step 4) and the tests (step 6) themselves, in place of the reviewer.

### 1. Start

If the checkout has uncommitted changes, or is on a branch whose work isn't merged, stop and ask: it may be the person's or another session's work in progress. Otherwise, from the up-to-date default branch (`main` unless the repository uses another name), create the ticket's branch: the ticket file's name without `.md`, lowercased (`us-pay-03-refuse-refunds-over-the-order-total`). `deliver.py next` prints it.

```bash
git switch <default>
git pull --ff-only origin <default>
git switch -c <branch>
python3 scripts/deliver.py context <ID>
```

Install the project's dependencies the way `AGENTS.md` (`## This project`) says. `context` prints the live criteria, the cited requirement text verbatim, the ADRs, the related tickets, and the ticket body. Use that text, not a summary. Then read:

- the ADRs that `context` prints (every accepted ADR binds every ticket);
- the `## This project` section of `AGENTS.md`;
- the recent decision-log entries about neighboring tickets, whose choices you must stay consistent with;
- the code the ticket builds on.

### 2. Plan

1. Write the change-request skeleton to a file outside the repository (or in a git-ignored path), so it is never committed by accident: `python3 scripts/deliver.py pr-body <ID>`. It has one `## Plan` row per live criterion. Never add or drop a row: the rows are how `gate pr` knows every criterion was planned.
2. Fill each row with its tests: the allowed case, the denied case, and every limit and empty state the criterion names. Test access rules at the interface that enforces them (the route, command, or public function), not only in a helper.
3. Under the table, list:
   - the files you will add or change;
   - data changes (schemas, migrations, stored formats);
   - interfaces (routes, commands, public functions) and who may call them;
   - user-visible parts (screens, messages, new texts);
   - `Constrained by:` the accepted ADRs, and each related DEC with its status.

### 3. Questions

Sort everything the ticket leaves open into two kinds.

**The person decides.** Ask about all of these in one round, each with your recommendation first:

- a rule, permission, field, option, or behavior a user would notice that no criterion, requirement, or accepted ADR settles;
- a criterion that depends on a ticket that isn't `done`;
- a criterion that is ambiguous (two reasonable readings lead to different tests).

If an answer adds or changes behavior, it is a criterion change: draft it in the ticket as `playbooks/define.md` describes, show it, and get a yes before you rely on it.

**You decide, then log.** These go into the decision-log entry you write in step 10:

- plumbing a criterion needs;
- names;
- the wording of texts a criterion requires (following the project's style guide, if `## This project` names one);
- limits an ADR leaves to the implementation.

### 4. Plan review

1. Run the reviewer in `plan` mode (see "Reviews").
2. Fix every CRITICAL finding and rerun until none is left. Settle every WARNING: fix it, or file it as a gap and say why in the plan.
3. With autonomy `supervised`, show the reviewed plan to a person and wait for their approval. Add `Plan approved by: <name>` to `## Plan`; `gate pr` checks it.

### 5. Claim

Set `status: in-progress` in the ticket file, then:

```bash
git add backlog
git commit -m "chore: start <ID>"
git push -u origin <branch>
```

Open a draft change request with the body file as its description (see "Host commands"). The pushed branch and the draft tell everyone, and `deliver.py next`, that the ticket is taken. On the manual host, the pushed branch is the claim.

### 6. Tests first

1. Write the tests that prove each live criterion, through the interfaces users and callers use. Tag every test name with its criterion, in either form: `[US-PAY-03/AC2]` or `us_pay_03_ac2` (see `backlog/README.md`). Every live criterion needs at least one tagged test.
2. Run `python3 scripts/deliver.py gate red <ID>`. It must print `PASS`: each live criterion has tagged tests that ran, and at least one of them fails. A test that fails because of a typo, a missing import, or a broken fixture doesn't count: read each failure and make sure it is the missing behavior. Tests must fail one by one, not all at once while the file loads or compiles: a load error hides the tags, and stub code added to get past it changes code before the freeze, which `gate pr` refuses. Test Kitchen's guide shows how for each runner: https://github.com/iakanoe/TestKitchen/blob/v0.1.0/guide/test-runners.md.
3. Run the reviewer in `tests` mode, and fix what it finds (then run `gate red` again).
4. With autonomy `supervised`, show the tests to a person and wait for their approval. Add `Tests approved by: <name>` to `## Plan`.
5. Commit only test files (files matching `tests` in `kitchen.yml`), with exactly this message:

```bash
git commit -m "test: <ID> failing tests"
```

This is the freeze commit; there is exactly one per branch. From here on the tests are frozen, and `gate pr` checks it:

- no code file (matching `code`) may change at or before the freeze commit;
- a frozen test changes only where it contradicts the ticket or an accepted ADR, and each changed test file goes under `## Test changes` with its reason;
- no criterion may lose tagged tests;
- no skipped or focused test may be added (`.skip(`, `.only(`, `xit(`, `@pytest.mark.skip`, `@unittest.skip`, `t.Skip(`, `@Disabled`, …).

Tests come first so that they are written from the criteria, not from the code, and the freeze keeps them from being bent to fit the code afterwards.

### 7. Implement

Write code until the tests pass. Follow the project rules in `## This project` of `AGENTS.md`. Also:

- Comment each non-obvious decision, data structure, interface, and seam with what it does and the criterion or ADR behind it.
- Mark each seam where an open DEC applies with a comment naming the DEC, the fail-closed behavior, and the criterion, for example `DEC-PAY-02 open: refunds after delivery are refused (US-PAY-03/AC4)`, in the language's comment syntax. `backlog_check.py` lists these once the DEC is decided, so the seam is revisited.
- Every `TODO`, `FIXME`, `XXX`, or `HACK` names a ticket.
- Commit as you go (`feat: <ID> …`).

### 8. Check

Bring in the default branch, then run the full check, each in a call of its own:

```bash
git fetch origin
git merge origin/<default>
```

```bash
python3 scripts/deliver.py check
```

`check` runs `backlog_check.py`, the scripts' self-tests, and the project's `check_command` (or the full test run). It must pass in full; it is what CI runs. For user-facing work, also try the change the way a user would (run it locally) and note what you saw.

### 9. Final review

1. Update the project's READMEs and in-code documentation first, and commit every file matching `code` or `tests`: any later change to those files fails `gate pr` until it is reviewed again. From step 10 on, touch only `backlog/`, `docs/`, and other files outside `code` and `tests`.
2. Run the reviewer in `diff` mode, and handle each finding:
   - CRITICAL: fix it.
   - WARNING: fix it, or file it as a gap and justify it.
   - SUGGESTION: fix it, file it, or note it.
3. After any fix, rerun `deliver.py check` and the reviewer. The change request quotes the last review's closing lines exactly: `Reviewed commit: <sha>` and the tally.

### 10. Capture

Nothing found may stay only in chat.

- **Gaps.** File each as one of:
  - a new DEC (`status: draft`; its options come only from what `docs/` records, otherwise "None recorded");
  - a new SPK, with the next free number in that epic;
  - a note on the later ticket that will close it.

  Never edit a ticket's criteria or open questions without the person's yes.
- **Decisions.** Add one entry at the top of `docs/decision-log.md` (`### YYYY-MM-DD — <title>`), shaped like the entries already there. It records who confirmed what, every built behavior the ticket left open, the new user-visible texts, the test changes, and the filed gaps.
- **Platform changes.** Any setting changed outside the code (host settings, secrets by name only, external services) gets its own decision-log entry.
- **READMEs.** Update any status or capability list the project keeps when a capability ships.
- **Status.** Set the ticket to `done`. If a live criterion can't be proven in this ticket, stop and ask (the ticket would merge `in-progress`, which needs the person's yes and a ticket that holds the rest).
- **Check.** Run `python3 scripts/backlog_check.py`. It must exit 0.

`docs/decision-log.md` is the one file under `docs/` the guard does not protect: entries are added at every ticket's capture step, and asking each time would stop unattended runs. Every other `docs/` file asks the person first.

### 11. Change request

Fill every section of the body file:

- **Ticket:** starts with the ticket ID (markdown around it is fine). `None. …` makes it a non-ticket change request even if a ticket is named later. A ticket left `in-progress` (only with the person's yes) says why and names the ticket that holds the rest.
- **Plan:** the reviewed plan; with `supervised`, the two approval lines.
- **Gaps found:** each bullet names the ticket that now holds the gap, or a single `- None`.
- **Decisions** and **Platform changes:** each bullet ends with `Log: <exact decision-log entry title>` or names a done DEC, or the section is a single `- None`.
- **Test changes:** every test file changed after the freeze, with the reason, or `None`.
- **Review report:** every finding of every review, with what was done about it, ending with the final reviewer's two closing lines, quoted exactly.
- **Checks:** the `deliver.py check` result (with test counts), the `gate red` result before implementing, and what was tried by hand.

Then write the delivery record (a verbatim copy of the description, kept in the repository because the evidence lives nowhere else), commit it, check the description, and publish it:

```bash
python3 scripts/deliver.py record --body-file=<body file> --branch=<branch> --cr=<number>
git add backlog
git commit -m "docs: delivery record"
python3 scripts/backlog_check.py --pr-body=<body file>
python3 scripts/deliver.py gate pr --body-file=<body file> --branch=<branch>
git push origin <branch>
```

Then update the change request's description from the body file and mark it ready (see "Host commands"; on GitLab, update and mark ready before the push).

- `gate pr` fails when the record is missing or differs from the description. If you edit the description afterwards, rerun `record` and commit again.
- If a record for another change request already exists at that path (a follow-up change request for the same ticket, or a colliding branch name), `record` writes `<name>-cr<number>.md` instead and never overwrites; it needs `--cr`. On the manual host, where there is no number yet, leave `--cr` out unless `record` asks for it.
- Write commit messages and descriptions that mention a merge or push to a file first (`git commit -F <file>`, a body file): in Claude Code the guard refuses a push or merge command that carries unusual shell syntax, and plain files keep every command plain.

### 12. Merge

What happens here depends on the autonomy level in `kitchen.yml` (see "Autonomy") and the host.

**With autonomy `merge`** (the default), on GitHub or GitLab:

1. Wait for the checks on the change request's latest commit, and confirm every one passed. A check still pending means wait and look again, never merge.
2. Read the head commit's sha (see "Host commands"): the sha the checks passed on.
3. Print the one allowed merge command:

   ```bash
   python3 scripts/deliver.py merge-command <number> --head=<sha>
   ```

4. Run exactly the command it printed, alone in its own call, from this checkout, clean, on the change request's branch at that sha. Never type a merge command of your own, and never add options to the printed one.

In Claude Code, the guard runs `python3 scripts/deliver.py gate merge <number> --head=<sha>` before the merge and refuses it on any FAIL. In any other agent, run that gate yourself immediately before the merge, and merge only on `PASS`. The merge is pinned to that sha, so nothing pushed after the gate can ride along. On a FAIL, fix the cause; never retry the same merge unchanged.

**With autonomy `pr` or `supervised`, or on the manual host:** stop at "ready to merge". Confirm the checks passed and, on GitHub or GitLab, that `deliver.py gate merge <number> --head=<sha>` passes. Then report the change request, its head sha, and the gate result, and say that a person merges it. A person merges with a merge commit, not squash or rebase: squashing or rebasing rewrites the commits the gates and the record point to (the freeze commit, the reviewed commit).

### 13. Verify

After the merge:

1. Watch the default branch's CI run (and the deploy, if the project has one) for the merge commit (see "Host commands"). A failed run or deploy stops the workflow.
2. Do what `verify:` in `kitchen.yml` says, in its plain words, and note what you saw. If `verify` is not set, report "not verified after deploy".

Broken behavior after the merge is a stop. Any sign-in link or credential used to verify is a secret: keep it out of the repository, the change request, tickets, and logs, and discard it after use.

When a person merges (autonomy `pr` or `supervised`, or the manual host), report what `verify` asks for so it can be done after their merge.

### 14. Close

1. Return to the up-to-date default branch: `git switch <default>` then `git pull --ff-only origin <default>`.
2. Leave the merged branch as it is.
3. Report what shipped (with the change request's link), what you decided and logged, and what you filed.
4. With `/deliver all`, return to "Picking". Change requests waiting for a person's merge do not block it: their branches are taken, so `next` skips them.

## Variants

### Tasks

A task has criteria but no user-facing behavior. It follows the 14 steps, with one difference: tests come first only when the criteria can be proven by tests.

- **Testable task** (a refactor that keeps behavior, a fix to a build script): deliver it like a story, including step 6. `gate red` then wants a tagged test for every live criterion, and `gate pr` holds the task to the freeze rules.
- **Untestable task** (an upgrade, a CI change): skip step 6. Each plan row says how its criterion is shown to be met (a command's output, a CI run, a review finding), and the final reviewer confirms each one.
- If only some criteria can be tested, stop and ask the person to split the task: once a task has tagged tests, `gate red` wants one for every live criterion.

### Bug-fix stories

A story with `fixes: [US-…/ACn]` repairs a criterion the code broke. Deliver it as a story. Its first test reproduces the bug: it fails on the current code for the reason the bug report gives. Tag it with the fix story's own criterion; it may also carry the broken criterion's tag, so the original criterion gains the test that would have caught the bug. Commit as `fix: <ID> …`.

### Hotfix stories

A story with `hotfix: true` restores broken behavior in production. `playbooks/define.md` (mode `hotfix`) creates it, with a decision-log entry saying why the lane is used and a draft follow-up task ("Refine after hotfix US-…").

- Skip step 3 (questions) and step 4 (plan review), so the fix is not held up by work that can wait for the follow-up.
- Everything else runs: tests first (`gate red`, tests review, freeze commit), the final review, capture, the record, and every gate.
- `## Decisions` has a bullet ending `Log: <the hotfix entry's title>`, and `## Gaps found` names the follow-up task. `gate pr` checks both.

### Spikes

A spike investigates; it does not ship behavior.

1. Create the spike's branch (its file name, lowercased) and claim it as in step 5.
2. Read the goal and the "Done when" list. Investigate read-only, unless the spike allows otherwise.
3. Record the findings under `## Findings`. A finding that changes a requirement goes to the person as a proposed `docs/` change (`playbooks/define.md`, mode `change`); never apply it on your own.
4. File the follow-ups (DECs, SPKs, draft stories or tasks) and set the spike to `done`.
5. Open the change request with `## Ticket` starting `None. Spike SPK-…: …` (only story and task change requests carry the ticket checks), write and commit the record, and merge as in step 12.

### Decisions (DEC)

DECs are `assignee_type: human`: you prepare the decision; a person makes it.

1. Read the DEC, the requirements it cites, and the tickets it unblocks.
2. Present it in the decision format of `playbooks/define.md`, with your recommendation and its reasons. The person chooses. Never pick an option, not even "for now".
3. Draft every change the answer causes (the apply checklist in `playbooks/define.md`), show the draft, and apply it after a yes.
4. Work on the branch `docs/` plus the DEC file's name without `.md`, lowercased (`docs/dec-pay-02-refund-window`). Open a change request with `## Ticket` starting `None. Decides DEC-…`, and a `## Decisions` bullet naming the DEC and ending with `Log: <entry title>`. Write and commit the record, and merge as in step 12.

### Other changes

A change with no behavior to accept (a typo, a comment, a broken link) uses a `fix/`, `chore/`, or `docs/` branch, with `## Ticket` starting `None. …`. It still commits its record and passes the checks, and when it touches a file matching `code` or `tests` it also needs a final review (step 9): `gate pr` then requires the tally with `CRITICAL: 0` and a `Reviewed commit:` with nothing in code or tests changed after it. A change in behavior always has a ticket. A branch named like a ticket (`us-…`, `task-…`) can't skip the ticket checks.

Show anything under `docs/` to the person before you apply it.

## Autonomy

`autonomy` in `kitchen.yml` sets how far an agent goes on its own:

| Level | The agent | A person |
| --- | --- | --- |
| `merge` (default) | Runs all 14 steps and merges on green through the merge gate. | Answers what "Stop and ask" lists. |
| `pr` | Runs steps 1–11 and stops at "ready to merge" (step 12). | Merges; the agent verifies afterwards when asked. |
| `supervised` | As `pr`, and also stops after the plan review and after the tests review for approval. | Approves the plan and the tests (named in `## Plan`, which `gate pr` checks), and merges. |

In Claude Code, the guard denies every agent merge under `pr` and `supervised`. Elsewhere, the agent keeps to its level itself.

## Manual host

With `host: manual` (no host CLI, or a host without an adapter), the scripts cannot see change requests:

- `deliver.py next` treats pushed branches as taken; the pushed branch is the claim (step 5).
- At step 11, write the description file and the record, run `backlog_check.py --pr-body` and `gate pr` locally, and push. A person opens the change request with that description.
- Step 12 always stops at "ready to merge": `gate merge` prints that a person merges. Hand the person the branch, the head sha, the description file, and the checks to confirm: `deliver.py check` and `gate pr --body-file=<file> --branch=<branch>` pass on a clean checkout of the head, and any CI the project has is green. They merge with a merge commit.

## Host commands

The host-specific commands the steps refer to. `<n>` is the change request's number.

| Action | GitHub (`gh`) | GitLab (`glab`) |
| --- | --- | --- |
| Open a draft change request (step 5) | `gh pr create --draft --base <default> --head <branch> --title "feat: <ID> <title>" --body-file <body file>` | `glab mr create --draft --source-branch <branch> --target-branch <default> --title "feat: <ID> <title>" --description-file <body file> --yes` |
| Find its number | `gh pr view <branch> --json number -q .number` | `glab mr view <branch> --output json --jq .iid` |
| Update the description (step 11) | `gh pr edit <n> --body-file <body file>` | `glab mr update <n> --description-file <body file> --yes` |
| Mark it ready (step 11) | `gh pr ready <n>` | `glab mr update <n> --ready --yes` |
| Wait for the checks (step 12) | `gh pr checks <n> --watch --fail-fast`, then `gh pr checks <n>` | `glab mr view <n> --output json --jq .head_pipeline.status`, repeated while it is `created`, `pending`, or `running`; it must end `success` |
| Read the head sha (step 12) | `gh pr view <n> --json headRefOid -q .headRefOid` | `glab mr view <n> --output json --jq .sha` |
| Read the merge commit (step 13) | `gh pr view <n> --json mergeCommit -q .mergeCommit.oid` | `glab mr view <n> --output json --jq .merge_commit_sha` |
| Watch CI on the default branch (step 13) | `gh run list --branch <default> --commit <sha>`, then `gh run watch <run id> --exit-status` | `glab ci status --branch <default> --wait` (check it reports the merge commit) |
| Merge (step 12) | Only what `deliver.py merge-command` prints | Only what `deliver.py merge-command` prints |

- **GitHub** reruns the check when the description is edited (`edited`) or the draft is marked ready, and the check reads the live description.
- **GitLab** starts no pipeline when a description is edited or a draft is marked ready, so its check reads the description from the committed delivery record and skips the delivery gate on drafts. At step 11, update the description and mark the merge request ready before the final push, so the pipeline on the final head runs the gate; otherwise start a new pipeline for the merge request. `gate merge` compares the record with the live description before any merge.
- **Manual:** none of these; see "Manual host".

## Reviews

Each review runs in a fresh context: in Claude Code the `ticket-reviewer` subagent; elsewhere a new session or agent given `playbooks/review.md`. A reviewer that shares your context shares your blind spots, so give it only the inputs `playbooks/review.md` lists for the mode (delivery uses `plan`, `tests`, and `diff`; `ticket` mode belongs to `/define refine`, which gives it its own inputs):

- the mode (`plan`, `tests`, or `diff`);
- the repository path and the ticket path;
- the accepted ADR paths, and each related DEC's ID and status;
- what to review: the plan text, the test file paths, or the diff range (`origin/<default>...HEAD`).

Never pass your reasoning, your conclusions, or what you expect it to find. Its report goes into the change request as it is, with what you did about each finding.

## Stop and ask

Stop, ask the person, and wait when you meet any of these:

- a checkout with uncommitted changes, or on a branch whose work isn't merged;
- a DEC option to choose;
- a criterion that is ambiguous, contradicts the plan, or depends on a ticket that isn't done;
- behavior a user would notice that no criterion, requirement, or accepted ADR settles;
- any change under `docs/`, or to a ticket's criteria or open questions;
- a gap that blocks the current ticket;
- a live criterion that can't be proven in this ticket, so it would merge `in-progress`;
- a task whose criteria are only partly testable (propose a split);
- a test that would have to be weakened;
- a check failure you can't fix within the ticket's scope;
- a gate that keeps failing;
- a failed CI run or deploy after the merge, or broken behavior;
- a platform setting change, or a deploy, release, restore, or secret change by hand;
- the location of a reference input, or a credential;
- with autonomy `supervised`: the plan and the tests, for approval;
- anything that crosses a boundary in `docs/product.md`.

How to stop:

- **Ask everything open in one round,** each question with your recommendation first. Several small rounds cost the person more than one complete one.
- **Commit and push before you wait,** and note in the draft change request what is waiting, so the work survives the session.
- **Headless:** print the questions and stop.

## Never

- Never choose a DEC option or invent a criterion.
- Never skip `gate red`, or commit implementation before the `test: <ID> failing tests` commit.
- Never merge on a failing or pending check, with a merge command of your own, or with options that bypass the host's checks (administrator overrides, auto-merge).
- Never record credentials, tokens, keys, or sign-in links.
- Never create another folder or worktree for the work, and never switch away from uncommitted or unmerged work: ask.
- Never finish a ticket with a gap, decision, or platform change unrecorded.
