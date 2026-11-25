# Contributing

This is how every change reaches the default branch, whether a person or an AI agent makes it. The steps live in the playbooks; this file says why the process looks the way it does, what enforces it, and how to run it.

| Playbook | Covers |
| --- | --- |
| [`playbooks/define.md`](playbooks/define.md) | Turning what people know into requirements, decisions, and tickets |
| [`playbooks/deliver.md`](playbooks/deliver.md) | Building one ticket: plan, tests first, implement, review, record, merge, verify |
| [`playbooks/review.md`](playbooks/review.md) | The fresh-context reviewer's brief |

Ticket rules are in [`backlog/README.md`](backlog/README.md); project rules are in the `## This project` section of [`AGENTS.md`](AGENTS.md).

## 1. Principles

- **One ticket per branch and change request.** The ticket's live acceptance criteria are the only requirements; the requirements it cites and the accepted ADRs are the only other inputs that bind. Small units keep reviews honest and history readable.
- **Tests first.** Tests come from the criteria. They are committed and seen failing before any code, then frozen, so they are written from what was asked rather than bent to fit what was built.
- **Agents never decide.** Choosing a DEC's option, changing a criterion, changing anything under `docs/`, and changing platform settings need a person. Code that meets an open DEC fails closed.
- **Nothing stays only in chat.** Every gap is filed as a ticket, every decision and platform change gets a decision-log entry, and the change request lists them all. Chat disappears; the repository is what the next reader has.
- **Fresh-context reviews.** A reviewer that sees only the ticket and the work checks the plan, the failing tests, and the final diff. An author, person or model, reviewing their own reasoning tends to confirm it.
- **Facts come from scripts, not memory.** Picking a ticket, a ticket's criteria, the cited requirement text, and every gate come from `scripts/deliver.py` and `scripts/backlog_check.py`. Models do the judgment work in between.
- **Nothing merges on red.** No merge while any check fails or is pending, and only through the merge gate.

## 2. What is enforced, and where

| Rule | Enforced by |
| --- | --- |
| Tickets are well formed (frontmatter, IDs, criteria, readiness, open questions, no `blocked_by` cycles, release order); cited requirements exist; test tags name live criteria of started tickets; a `done` story has a tagged test for every live criterion (adopted stories report test debt instead); every `TODO` names a ticket; `DEC-…` mentions exist | `backlog_check.py`, inside `deliver.py check` (CI) |
| The change request files every gap, decision, and platform change, pointing to tickets and decision-log entries that exist | `backlog_check.py --pr-body` (CI, and `gate merge`) |
| A ticket change request has a plan row for every live criterion | `deliver.py gate pr` (CI) |
| Each live criterion has a tagged test that fails before the implementation | `deliver.py gate red`, at step 6 |
| Tests were frozen in exactly one `test: <ID> failing tests` commit, before any code changed | `deliver.py gate pr` (CI) |
| No criterion lost tagged tests after the freeze; test files changed after it are listed under "Test changes"; no skipped or focused test was added after it | `deliver.py gate pr` (CI) |
| The last review names the commit it reviewed, has no CRITICAL finding, and no code or test file changed after it (this also applies to a change request with no ticket that touches code or tests); the ticket is `done`, or the change request says why not and names the ticket that holds the rest | `deliver.py gate pr` (CI) |
| A hotfix logs why the lane was used and names its follow-up ticket; with `autonomy: supervised`, a named person approved the plan and the tests | `deliver.py gate pr` (CI) |
| The description is committed as its delivery record, and the two match | `deliver.py gate pr` (CI), `gate merge` (against the live description) |
| No merge unless a `check` job passed on the head and no check fails or is pending; the change request is open, not a draft, targets the default branch, is mergeable, and is up to date; the merge runs from a clean checkout of its head and is pinned to that head; `gate pr` passes | `deliver.py gate merge`: run by the guard in Claude Code, by the agent itself elsewhere |
| The only merge is the command `deliver.py merge-command` prints, alone in its call; no agent merge on the manual host or with autonomy `pr` or `supervised` | the guard |
| Any command with an unquoted `push` or `merge` word, or a git/gh/glab word built at run time (`$'…'`, `$()`, backticks), must be a plain allowed command; so `make push` or `pytest -k merge` is refused (quote the word: `pytest -k "merge"`), while paths such as `tests/push.test.ts` are fine | the guard |
| A push is only `git push [-u] origin <branch>` (also `--set-upstream`, `-n`, `-q`, `-v`), from this checkout, naming one existing local branch that is not the default branch, and only while `remote.origin.push` and `remote.origin.mirror` are unset; force pushes ask | the guard |
| Editing `docs/` (except `docs/decision-log.md`), `.claude/`, `.github/`, `.gitlab/`, `.gitlab-ci.yml`, `.git/`, `playbooks/`, every file `kitchen.lock` lists (the framework scripts, `backlog/README.md`, …) and their `.kitchen-new` copies, `kitchen.yml`, `kitchen.lock`, `CONTRIBUTING.md`, `AGENTS.md`, `CLAUDE.md`, or the git and host CLI configuration files asks a person | the guard |
| Git configuration writes, commands naming `.git` or the git and host CLI configuration, commands that may run a git alias, tokens in commands, host API writes, and host CLI subcommands outside reads and the workflow's steps ask a person; `glab mr create` with `--push`, `--fill`, or `--auto-merge` is refused (it would push or merge outside the rules) | the guard |

**The guard** is `.claude/hooks/guard.py`, a Claude Code hook registered in `.claude/settings.json`. It checks every shell command and file edit in every Claude Code session and subagent in the repository, and it fails closed: if it errors, the call is denied. Merges and pushes are checked against an allowlist, not a list of bad shapes: a command that names a push or a merge must be plain (simple words, quotes without expansions, the separators `;`, `&&`, `||`, `|`) and use only the programs the workflow uses. So write commit messages and descriptions to a file first (`git commit -F <file>`, a body file). Its docstring lists the exact shapes.

**What the guard can't see.** It reads commands literally. Text built at run time (variables that assemble a command, an interpreter's `-c`, a script written and then run, a build-tool target) is out of its reach. It is a guardrail against mistakes, not a sandbox against a model trying to evade it. What holds against everything is the host's own branch protection: where your host and plan allow it, protect the default branch and require the `check` job to pass before merging.

**Sandbox opt-in.** On a machine you have chosen to run unattended, set `KITCHEN_GUARD_SANDBOX=1` in the git-ignored `.claude/settings.local.json` (`{"env": {"KITCHEN_GUARD_SANDBOX": "1"}}`). The guard then lets its "ask" cases through without a prompt. Denials and force pushes are unchanged, and the agent still stops for everything the playbooks list, through its own questions rather than the guard.

## 3. When an agent stops and asks

An agent stops, asks a person, and waits for: a DEC to decide; a criterion that is ambiguous or depends on unbuilt work; behavior a user would notice that nothing settles; any change under `docs/` or to a ticket's criteria; a gap that blocks the ticket; a ticket that would merge unfinished; a test that would be weakened; a check or gate it can't make pass within scope; a failed deploy; a platform change; a credential; and, by autonomy level, approvals and merges. The full list is in `playbooks/deliver.md`, "Stop and ask". It asks everything in one round, commits and pushes before waiting, and in a headless run prints its questions and stops. Everything else it decides and logs.

## 4. Running it

The workflow does not depend on a model or a tool: it is the playbooks, the rules files, and the scripts. Run it on whichever agent and model you choose.

**In Claude Code** (recommended: the workflow was developed and tested there, and it is the only agent where the guard enforces the merge and push rules):

- `/define` defines (modes in `playbooks/define.md`); `/deliver US-PAY-03` delivers one ticket, `/deliver next` picks one, and `/deliver all` keeps going until nothing is ready or a question needs a person.
- The skills (`.claude/skills/`) and the reviewer (`.claude/agents/ticket-reviewer.md`) set no model: they run on the session's model (the model picker, `/model`, or `claude --model <name>`).
- Running `/deliver` is the request to commit, push, open the change request, and merge on green (with autonomy `merge`) for the ticket it works on.
- Unattended: `claude -p "/deliver all" --permission-mode acceptEdits`, adding `--model <name>` to choose one and `--allowedTools` for `Bash(git *)`, `Bash(python3 scripts/*)`, your host CLI (`Bash(gh *)` or `Bash(glab *)`), and your test tools. The guard's asks become refusals there (edits under `docs/` other than the decision log ask), so a run that needs a person stops, unless the sandbox opt-in is set.

**In another agent** (Codex, Cursor, or any other that reads `AGENTS.md`):

- Ask it to follow `playbooks/define.md` or `playbooks/deliver.md`, and to run the same `scripts/deliver.py` steps and gates.
- For each review, give a fresh session or agent `playbooks/review.md` and only the inputs it lists for the mode.
- The guard is Claude Code only. Elsewhere, the agent runs `python3 scripts/deliver.py gate merge <number> --head=<sha>` from a clean checkout of the change request's head before every merge, merges only with the command `deliver.py merge-command` prints, and stops for everything in "Stop and ask". CI still runs `gate pr` on every change request.

**By hand:** follow the playbooks yourself. You approve the plan and the tests in place of the reviewer.

## 5. Setup per machine

- Python 3.9 or later, with PyYAML (`python3 -m pip install pyyaml`);
- git;
- the host CLI, signed in: `gh` for GitHub, `glab` for GitLab (none for the manual host);
- the project's own toolchain (see `## This project` in `AGENTS.md`);
- on the host: merge commits allowed (no squash-only or rebase-only setting), and on GitLab, merged results pipelines off, because the gates point at the branch's own commits;
- optionally, Claude Code.

`python3 scripts/deliver.py check` confirms the setup: it runs the backlog check, the scripts' self-tests, and the project's tests.
