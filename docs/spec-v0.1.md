# Test Kitchen v0.1: build spec

Status: approved plan, 2026-11-24. This file is the single brief for building v0.1. Every part (scripts, guard, playbooks, installer, docs) follows it; where a part needs a choice this file does not make, the builder makes it, comments it in the code, and adds a line to `docs/decision-log.md`.

**Test Kitchen.** *Let the agents cook (then taste the food) AKA vibecoding for devs with trust issues.*

A portable framework that organizes a software project so AI agents can define and deliver it under guardrails: requirements and tickets live in the repository, tests come first and are frozen, a fresh-context reviewer checks the work, every gap and decision is recorded, and nothing merges unless deterministic gates pass.

## 0. Ground rules for every builder

- **Language:** English only, in code, docs, and messages.
- **No metaphors.** The name and tagline are the only kitchen words anywhere. No "recipe", "chef", "cook", "taste", "serve", "ingredients" in docs, code, or messages.
- **Stack-agnostic.** No language, framework, test runner, or platform is assumed. Examples may show several (Python/pytest, JS/vitest, Node's built-in runner, Go), always side by side and never as defaults.
- **Host-agnostic.** Use the neutral word **change request** in shared text. Host-specific words ("pull request", "merge request") only appear inside host adapters, host templates, and host-specific guide sections.
- **Agent-agnostic.** The plain-markdown playbooks in `playbooks/` are the single source of the process. Claude Code files (skills, reviewer agent, hook) are thin wrappers that point at the playbooks and add only Claude-specific mechanics.
- **Scripts:** Python 3.9 compatible (no `match`, no `X | Y` type unions at runtime; use `from __future__ import annotations` if you annotate), standard library plus PyYAML only. They run from any directory inside the repository.
- **Document everything.** Every module starts with a docstring saying what it does and how it is used. Every non-obvious decision, regex, convention, and seam gets a comment saying why. If a rule exists, the docs say why it exists.
- **Scrub.** Nothing from the source project may appear: none of its company, client, product, platform, or tool names, its document names, its requirement, module, or slice IDs, its people, or its dates. Examples use neutral codes such as `PAY`, `AUTH`, `CORE`.
- **Never** record credentials, tokens, or project-specific secrets anywhere, including test fixtures.

## 1. Where it comes from

v0.1 ports and generalizes the delivery system of an existing private project. Builders read these source files (read only, never edit them) and carry over their behavior unless this spec changes it:

| Source (in the private project) | Becomes |
| --- | --- |
| `CONTRIBUTING.md` | `template/CONTRIBUTING.md` and `template/playbooks/deliver.md` |
| `.claude/skills/deliver/SKILL.md` | `template/playbooks/deliver.md` (process) + `template/claude/skills/deliver/SKILL.md` (thin wrapper) |
| `.claude/agents/ticket-reviewer.md` | `template/playbooks/review.md` + `template/claude/agents/ticket-reviewer.md` (thin wrapper) |
| `.claude/hooks/guard.py`, `.claude/hooks/test_guard.py` | `template/claude/hooks/guard.py`, `tests/test_guard.py` |
| `.claude/settings.json` | `template/claude/settings.json` |
| `scripts/backlog_check.py` | `template/scripts/backlog_check.py` (+ `kitchen_lib.py`) |
| `scripts/deliver.py`, `scripts/test_deliver.py` | `template/scripts/deliver.py`, `template/scripts/hosts.py`, `tests/test_deliver.py` |
| `backlog/README.md` | `template/backlog/README.md` |
| `.github/pull_request_template.md`, `.github/workflows/app.yml` | `template/github/…`, `template/gitlab/…` |
| `AGENTS.md` (repo level) | `template/AGENTS.md.tmpl` |

A second private input, a skill that turned requirements into a backlog, supplies ideas listed in section 9 (decision format, apply checklist, splitting rules, guardrails), scrubbed the same way.

## 2. Repository layout (this repository)

```
test-kitchen/
  README.md            front door: name, tagline, why, 3 install paths, quick tour
  LICENSE              Apache-2.0, verbatim
  CHANGELOG.md         semver; every release lists changes and migration notes
  AGENT-INSTALL.md     instructions an AI agent follows to install Test Kitchen
  init.py              installer / updater / doctor (single file, stdlib + PyYAML optional, see 8)
  template/            THE PRODUCT: what gets installed into a project
  guide/               user documentation
  examples/            kitchen.yml examples per stack (no example project)
  tests/               the product's tests (unittest, stdlib only) and fixtures
  docs/                this repository's own definition (spec, decision log)
  .github/workflows/ci.yml   this repository's CI (product tests job; root `check` job added when it installs itself)
```

`template/` stores instruction files **inertly** so tools never load them while developing Test Kitchen itself:

| In `template/` | Installed as |
| --- | --- |
| `AGENTS.md.tmpl` | `AGENTS.md` |
| `CLAUDE.md.tmpl` | `CLAUDE.md` |
| `kitchen.yml.tmpl` | `kitchen.yml` (filled by init from the answers) |
| `claude/` | `.claude/` (skipped with `--no-claude`) |
| `github/` | `.github/` (host github only) |
| `gitlab/gitlab-ci.yml` | `.gitlab-ci.yml` (host gitlab only) |
| `gitlab/merge_request_templates/` | `.gitlab/merge_request_templates/` (host gitlab only) |
| everything else | same relative path (`CONTRIBUTING.md`, `playbooks/`, `scripts/`, `backlog/README.md`, `docs/…` skeletons) |

Dogfooding (later, phase 7 of the build): this repository's root becomes a Test Kitchen project installed from the previous release (for the bootstrap, v0.1 itself from the local `template/`). Root copies of framework files are changed only through `init.py update`. `examples/`, `tests/fixtures/`, and `template/` are listed under `ignore:` in the root `kitchen.yml`.

## 3. Conventions in an installed project (no config)

### Paths

```
kitchen.yml                 config (section 4)
kitchen.lock                version + installed files with their sha256 (written by init)
AGENTS.md, CLAUDE.md        agent entry points
CONTRIBUTING.md             the workflow, short; points to playbooks
playbooks/deliver.md        the delivery process (single source)
playbooks/define.md         the definition process (single source)
playbooks/review.md         the reviewer brief (single source)
scripts/kitchen_lib.py      shared config, paths, tags, globs
scripts/hosts.py            host adapters: github, gitlab, manual
scripts/backlog_check.py    validates backlog + docs, coverage, gaps, refine, test debt
scripts/deliver.py          deterministic workflow steps and gates
docs/product.md             vision, users/roles, capabilities, boundaries
docs/requirements/<CODE>-<name>.md   requirement lines
docs/architecture/ADR-nnn-<slug>.md  architecture decisions
docs/decision-log.md        every decision, newest first
backlog/README.md           ticket rules
backlog/<CODE>-<slug>/epic.md, <ID>-<slug>.md, delivery/<ID>.md
backlog/delivery/<branch>.md
.claude/ (skills/deliver, skills/define, agents/ticket-reviewer.md, hooks/guard.py, settings.json)
.github/ or .gitlab-ci.yml + .gitlab/  (per host)
```

The default branch is detected (`origin/HEAD`, else `main`, else `master`). The CI job that gates merging is named `check`.

### Requirements

- File `docs/requirements/<CODE>-<name>.md`, one per epic code. Requirement lines: `- PAY-R03: <text>`. ID regex `[A-Z][A-Z0-9]{1,9}-R\d{2,}`.
- Markers at the start of the text:
  - `(observed in code)` — written by adopt mode, not yet confirmed by a person; counts as a gap.
  - `(superseded YYYY-MM-DD by PAY-R07)` — no longer binding; excluded from coverage; tickets that cite it are flagged by refine.
- Other text in the file (headings, prose) is free.

### Decision log

`docs/decision-log.md`, entries `### YYYY-MM-DD — Title` (em dash), newest first, each saying what was decided, why, who decided, and where it is recorded. Change-request "Decisions" / "Platform changes" bullets end with `Log: <entry title>`; the title must exist.

### ADRs

`docs/architecture/ADR-001-<slug>.md` with a `Status: proposed | accepted | superseded by ADR-nnn` line. Accepted ADRs bind every ticket.

### Tickets

IDs: `EP-<CODE>` for epics; `US-`, `TASK-`, `DEC-`, `SPK-` + `<CODE>-NN` (two or more digits) for the rest. `<CODE>` is `[A-Z][A-Z0-9]{1,9}`. IDs are stable: never renumbered or reused. File name = ID + `-` + kebab slug. One folder per epic: `backlog/<CODE>-<slug>/`, holding `epic.md`.

| Type | Prefix | Purpose | Done when |
| --- | --- | --- | --- |
| `epic` | `EP-` | A capability; groups its tickets | All its tickets are done or deferred |
| `story` | `US-` | User-facing behavior with acceptance criteria | Every live criterion has a passing tagged test |
| `task` | `TASK-` | Technical work with no user-facing behavior (refactor, upgrade, CI, test debt) | Every live criterion is met and reviewed |
| `decision` | `DEC-` | A question a person must decide | Answer recorded in `docs/` + decision log |
| `spike` | `SPK-` | Time-boxed investigation | Findings recorded, follow-ups filed |

Frontmatter:

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
refined: 2026-11-24      # set by /define refine when the ticket passes refinement
adopted: true            # optional: written by adopt mode for behavior that already existed
hotfix: true             # optional: urgent-fix lane
fixes: [US-PAY-01/AC2]   # optional: bug-fix stories name the criterion the code broke
code: ["src/payments/**"]   # epics only, optional: code areas this epic owns
---
```

Bodies:

- **Story:** `As a <role>, I want <capability>, so that <outcome>.` then `## Acceptance criteria` (`- AC1: Given …, when …, then ….`), `## Notes`, `## Open questions`.
- **Task:** a plain description, then `## Acceptance criteria` (`- AC1: <checkable statement>`; no Given/when/then required), `## Notes`, `## Open questions`.
- **Decision:** `## Question`, `## Context`, `## Options`, `## Recommendation`, `## Decides`.
- **Spike:** `## Goal`, `## Context`, `## Done when`, `## Findings`.
- **Epic:** what the capability is, `## Boundaries`, `## Open` (DEC/SPK IDs).

Criteria numbering is stable: never renumber or reuse; a new criterion takes the next number at the end; a removed one stays as `- AC4: (removed YYYY-MM-DD, <reason or ticket>)`; a change of meaning is a removal plus a new criterion. Criteria are English. Referenced elsewhere as `US-PAY-03/AC2`.

Open questions: each bullet starts with `None` or names a DEC/SPK. If that ticket is not done and not in `blocked_by`, the bullet states the interim behavior as `Until decided: …` and names the criterion that defines it.

Readiness (`ready`, `in-progress`, `done`): owner is not `TBD`/empty, every open question answered, stories and tasks have at least one live criterion, and, when releases are on, a `release`. `ready` does **not** require blockers to be done (blocked_by means "can start, can't finish"); `deliver.py next` never picks a ticket with an unfinished blocker.

Done story: every live criterion has at least one tagged test, unless `adopted: true` (then missing tests are **test debt**, reported separately, never errors).

### Test tags

A test proves a criterion by carrying its tag in the test's name (as the runner reports it in JUnit XML). Two equivalent forms, so every language can tag:

- canonical: `[US-PAY-03/AC2]` (anywhere in the name or a describe/class name);
- identifier: `us_pay_03_ac2` (any case, bounded by non-alphanumerics: `test_us_pay_03_ac2_refund_denied`, `TestUS_PAY_03_AC2`).

Both forms also work for tasks (`[TASK-CI-01/AC1]`, `task_ci_01_ac1`). Tags must name a live criterion of an `in-progress` or `done` ticket.

Skipped or focused tests may not be added after the freeze. The built-in detector covers at least: JS/TS `.skip(`, `.only(`, `.todo(`, `.fixme(`, `xit(`, `xdescribe(`, `xtest(`, `fit(`, `fdescribe(`; Python `@pytest.mark.skip`, `@pytest.mark.skipif`, `@pytest.mark.xfail`, `pytest.skip(`, `@unittest.skip`, `self.skipTest(`; Go `t.Skip(`; JVM `@Disabled`, `@Ignore`; Ruby `skip`, `xit`, `pending`. Documented in the guide.

### Code trace

Files matching `code` (section 4): every `TODO`/`FIXME`/`XXX`/`HACK` names a ticket ID; `DEC-…` mentions must exist (done ones are listed for revisiting).

### Branches and records

- Ticket branch = the ticket file's stem, lowercased (`us-pay-03-refund-over-total`, `task-ci-01-cache-deps`). Decision work: `docs/dec-<id>-<slug>`.
- Freeze commit message: `test: <ID> failing tests` (exactly one per branch).
- Reviewer closing lines: `Reviewed commit: <sha>` and `CRITICAL: n, WARNING: n, SUGGESTION: n`.
- Delivery record: the change-request description, verbatim, committed at `backlog/<epic folder>/delivery/<ID>.md` (ticket change requests) or `backlog/delivery/<branch with / as ->.md` (others); never overwrites another change request's record (`-pr<n>` suffix rule kept, named `-cr<n>`).

### Change-request description sections

`## Ticket` (starts with the US-/TASK- ID, or `None. …` for a non-ticket change), `## Plan` (table: one row per live criterion `| US-PAY-03/AC1 | tests… |`, then `Constrained by:`), `## Gaps found`, `## Decisions`, `## Platform changes`, `## Test changes`, `## Review report`, `## Checks`. Gaps bullets name the ticket that holds the gap; Decisions / Platform changes bullets end `Log: <entry title>` or name a done DEC; each section may be a single `None`.

## 4. `kitchen.yml`

```yaml
# Test Kitchen configuration. Everything else is a convention: see guide/configuration.md.
tests: ["tests/**", "**/*.test.ts"]        # required: globs of test files (and their helpers)
code: ["src/**"]                            # required: globs of product code
test_command: "python -m pytest {files} --junitxml={report}"   # required
# check_command: "npm run lint && npm run typecheck"   # optional: replaces the default full test run in `deliver.py check`
# verify: "Open the staging site and try the new behavior."  # optional: plain words; missing → "not verified after deploy"
# host: github            # optional: github | gitlab | manual; detected from the origin remote
# autonomy: merge         # optional: merge (agent merges on green) | pr (a person merges) | supervised (a person also approves plan and tests)
# split_threshold: 6      # optional: refine flags stories with more live criteria than this
# self_contained_tickets: false   # optional: tickets must read without the repository (no repo paths or links)
# releases: [v1, v2, later]       # optional: release slices, in order; turns slice rules on
# ignore: ["examples/**", "**/fixtures/**"]   # optional: excluded from every scan
```

- Globs: `**` matches any number of path segments (including none), `*` anything but `/`, `?` one char but `/`. Paths are repository-relative with `/`. A file matching both `tests` and `code` is a test.
- `test_command` placeholders: `{files}` → the test files to run, shell-quoted, root-relative, space-separated (empty for a full run, so the command must run the whole suite when given no files); `{files:<dir>}` → the same paths with the `<dir>/` prefix stripped (for runners invoked inside a subfolder, e.g. `cd app && npx vitest run {files:app} …`); `{report}` → path of the JUnit XML file the command must write. The command runs through the shell from the repository root.
- Unknown keys are errors (typo protection). Invalid values give one clear message each.

## 5. Scripts (`template/scripts/`)

### `kitchen_lib.py` (shared; imported by everything, including the guard)

```python
class ConfigError(Exception)
def repo_root(start=None) -> Path          # git rev-parse --show-toplevel; else parent of scripts/
@dataclass Config: tests, code, test_command, check_command=None, verify=None, host="manual",
    host_detected: bool, autonomy="merge", split_threshold=6, self_contained_tickets=False,
    releases=None (list or None), ignore=[]
def load_config(root) -> Config            # reads kitchen.yml; host detected when absent
def detect_host(root) -> str               # origin URL: github.com → github; "gitlab" → gitlab; else manual
def default_branch(root) -> str
def glob_to_regex(pattern) -> re.Pattern; def matches(path, patterns) -> bool
def is_test(path, cfg); def is_code(path, cfg)   # ignore-aware; tests win over code
def find_tags(text) -> list[tuple[str, int]]     # both tag forms → ("US-PAY-03", 2)
TICKET_ID, REQ_ID regexes; ticket id parsing helpers
def tracked_files(root, rev=None) -> list[str]   # git ls-files / git ls-tree
```

### `hosts.py` (adapters)

```python
@dataclass Check: name, state  # "pass" | "fail" | "pending" | "skipped"
@dataclass ChangeRequest: number, state ("open"|"merged"|"closed"), draft, base, head_branch, head_sha,
    mergeable (True | False | None=unknown), body, checks: list[Check], url
class Host:
    name: str; word: str            # "pull request" | "merge request" | "change request"
    def open_branches(self) -> set[str]     # head branches of open change requests (+ pushed branches via git)
    def view(self, number) -> ChangeRequest # raises NotSupported on manual
    def merge_argv(self, number, sha) -> list[str] | None   # the one allowed merge command; None on manual
def get_host(cfg, root) -> Host
```

- **github** uses `gh`: `gh pr list --state open --json headRefName`, `gh pr view N --json state,isDraft,baseRefName,headRefName,headRefOid,mergeable,body,statusCheckRollup,url`; merge `gh pr merge N --merge --match-head-commit SHA`. Latest run per check wins (port the original logic).
- **gitlab** uses `glab`: open MRs, MR view as JSON, head pipeline jobs, merge pinned to the head sha with auto-merge off. **Verify every glab command and flag against the official glab docs before relying on it** (and cite the doc URL in a comment); if a needed flag does not exist, choose the closest safe form and log the decision.
- **manual** has no CLI: `open_branches` = pushed branches only; no `view`; no merge. The agent stops at "ready to merge" and a person merges.
- The adapter interface is documented in `guide/hosts.md` so others can add hosts.

### `backlog_check.py`

```
python3 scripts/backlog_check.py                 # validate everything; ERROR lines exit 1, WARN lines don't
python3 scripts/backlog_check.py --strict        # uncovered requirements are errors
python3 scripts/backlog_check.py --pr-body=FILE  # also check a change-request description
python3 scripts/backlog_check.py --gaps          # what keeps the product from being fully defined; exit 1 if any
python3 scripts/backlog_check.py --refine        # refine findings (script part); exit 0
python3 scripts/backlog_check.py --test-debt     # adopted done tickets' criteria with no tagged test; exit 0
python3 scripts/backlog_check.py --self-test     # built-in self-test on a temp fixture; exit 0/1
```

Output lines start with a fixed label: `ERROR`, `WARN `, `GAP  `, `REFINE`, `DEBT `, then `<file or ID>: <message>`.

Validation (errors): everything the original checks, generalized (frontmatter, IDs vs type and file name, epic and blocked_by targets exist, source_reqs exist, criteria format, `…/ACn` references resolve, readiness, open questions, tags name live criteria of started tickets, done stories have tests unless adopted, TODOs name tickets, DEC mentions exist), plus: no `blocked_by` cycles; with releases on, `release` is in the list and no unfinished blocker is in a later slice than the ticket; `fixes:` targets exist; `refined:` is a date; `priority` value. With `self_contained_tickets: true`, the original "no repository links or document names" rule applies to ticket bodies; otherwise it does not.

Coverage: every requirement that is not superseded is cited by at least one non-deferred story or task (constraints by the story they constrain); epics with `status: deferred` are excluded. Uncovered = WARN (ERROR with `--strict`).

`--gaps` lists: open DECs and SPKs; tickets in `draft`; unanswered open questions; uncovered requirements; `(observed in code)` requirements; ready/in-progress tickets without `refined:`; code files (matching `code`, not ignored) that no epic's `code:` globs claim. Test debt is **not** a gap. (Amended 2026-11-25, see the decision log, "An empty project is not fully defined": `--gaps` also lists a missing or skeleton-only `docs/product.md` and a project with no requirements, and while no epic declares `code:`, existing code is one gap in all.)

`--refine` lists: stories with more live criteria than `split_threshold` (suggest a split); tickets citing superseded requirements; tickets whose open questions name a DEC that is now done (re-check them); with releases on, stories/tasks/spikes with no `release`; hotfix tickets done; tickets `in-progress` with no branch on origin.

### `deliver.py`

```
python3 scripts/deliver.py next                    # ticket to take, other ready ones, why the rest wait; hands off to define when none
python3 scripts/deliver.py context <ID>            # criteria, cited requirement text, ADRs, related tickets, body
python3 scripts/deliver.py pr-body <ID>            # change-request description skeleton, one plan row per live criterion
python3 scripts/deliver.py gate red <ID>           # each live criterion has a tagged test that runs and fails
python3 scripts/deliver.py record --body-file=F --branch=B [--cr=N] [--url=U]
python3 scripts/deliver.py gate pr (--body-file=F | --from-record) --branch=B [--base=REV] [--head=REV]
python3 scripts/deliver.py gate merge <N> --head=<SHA>   # host state + gate pr; the guard runs it
python3 scripts/deliver.py merge-command <N> --head=<SHA> # prints the one allowed merge command for this host
python3 scripts/deliver.py check                   # backlog_check + self-tests + check_command or full test run
python3 scripts/deliver.py status                  # one screen: ready / in progress / blocked / open decisions / gaps / test debt / last deliveries
python3 scripts/deliver.py release-notes [<slice>] # markdown from done stories ("so that…" lines), grouped by epic
python3 scripts/deliver.py --self-test
```

- **next.** Candidates: `story`, `task`, `spike` in `ready`, not `assignee_type: human`, blockers all done, branch not taken (open change request or pushed branch). Order: (1) slice index when releases are on (no release = last); (2) effective priority, where a ticket inherits the highest priority of every unfinished ticket it transitively unblocks; (3) number of unfinished tickets directly blocked by it, descending; (4) owned by the person running it (`git config user.name`) first; (5) ID ascending. Output lines: `NEXT`, `READY`, `WAIT`. When nothing is ready: `DECIDE <DEC>` lines for DECs blocking waiting tickets, most-blocking first; then `REFINE <ID>` lines for draft tickets in the same order; if neither, `NEXT none: nothing is ready or waiting; run /define to plan more work`.
- **gate red.** Test files = files matching `tests` whose text holds a tag for the ticket. Runs `test_command` with `{files}` = those files and `{report}` = a temp file outside the repository; parses the JUnit XML (testcase name + classname; `failure`/`error` → failed, `skipped` → skipped). Each live criterion needs a tagged test that ran, and at least one of them failed. No report written → FAIL with the command's output tail. Tasks: gate red is optional (only when the task has tagged tests).
- **gate pr.** Port of the original, with `app/` → `code`/`tests` globs and `Story` → `Ticket`:
  - non-ticket change request: record check only; a ticket-named branch (`us-`, `task-`) cannot skip the ticket checks;
  - branch = ticket file stem; record committed and equal to the description;
  - plan row per live criterion;
  - last review: tally present, `CRITICAL: 0`, `Reviewed commit:` on the branch, no `code`/`tests` file changed after it;
  - ticket `done`, or `in-progress` with the reason and the ticket holding the rest named in `## Ticket`;
  - stories (and tasks that have a freeze commit): exactly one freeze commit; no `code` file changed at or before it; every live criterion tagged at the freeze; no criterion lost tagged tests; test files changed after the freeze are listed under `## Test changes`; no skipped/focused test added after the freeze;
  - `hotfix: true`: `## Decisions` has a `Log:` bullet (why the hotfix lane was used), and `## Gaps found` names the follow-up ticket;
  - `autonomy: supervised`: `## Plan` contains `Plan approved by: <name>` and `Tests approved by: <name>`.
  - `--from-record` reads the description from this branch's committed record (used by CI on hosts whose CI cannot read the live description; `gate merge` still compares the record with the live description).
- **gate merge.** Host `view`; fails when: head ≠ pinned sha; not open; draft; base ≠ default branch; mergeable is False or unknown; no passing `check` job on the head; any check failing or pending; the checkout is not a clean checkout of the head; the branch is behind `origin/<default>`; `backlog_check --pr-body` errors; `gate pr` fails. Manual host: prints that a person merges and exits 1.
- **check.** Runs `backlog_check.py`, the three `--self-test`s, then `check_command` if set, else `test_command` as a full run. Exit 1 on the first failure, naming it. This is what CI runs.
- **status.** Counts per status; READY list in `next` order; IN PROGRESS with branch; BLOCKED with blockers; open DECs/SPKs; `--gaps` count with the first few; test debt count; last 5 delivery records (by commit date).
- **release-notes.** With a slice argument (releases on): done stories/tasks in that slice. Without: tickets whose delivery record was added since the last git tag (all done tickets when there is no tag). Stories are listed by their "so that …" outcome with the ID, grouped under the epic title; tasks and hotfixes go under "Other changes". Output is markdown on stdout. It never invents text.

### `--self-test` (all three scripts)

Each script can check itself in seconds without network: build a tiny fixture project in a temp directory (a kitchen.yml, a requirement file, an epic, a story, a test file), run its own logic against it, and print `PASS self-test` or the failures. Used by `deliver.py check` and `init.py doctor`.

## 6. Guard (`template/claude/hooks/guard.py`, Claude Code only)

Port of the original hook, generalized:

- Same tokenizer and allowlist approach for any command that pushes or merges; same "plain command" rules; same push shape (`git push [-u] origin <branch>`, never the default branch).
- **Merge shape per host** comes from `hosts.py`: `merge_argv` defines the only allowed merge; the guard runs `deliver.py gate merge <n> --head=<sha>` first. `manual` host: every merge is denied ("a person merges"). `autonomy: pr | supervised`: every agent merge is denied with the same message.
- Allowed read/workflow CLI commands per host: github `gh pr …`, `gh run …`, reads; gitlab `glab mr …`, `glab ci …`, reads; writes through `gh api`/`glab api` ask.
- Protected paths (editing asks a person): `docs/`, `.claude/`, `.github/`, `.gitlab/`, `.gitlab-ci.yml`, `.git/`, `scripts/` framework files listed in `kitchen.lock`, `playbooks/`, `kitchen.yml`, `kitchen.lock`, `CONTRIBUTING.md`, `AGENTS.md`, `CLAUDE.md`. Reading stays free.
- Asks: git config writes, anything naming `.git`, `.gitconfig`, `.config/git`, `.config/gh`, `.config/glab-cli`; tokens in commands; host API writes. Drop the source project's platform-specific rules (its deploy CLI, its database tool, its migrations rule).
- Sandbox opt-in kept, renamed `KITCHEN_GUARD_SANDBOX=1`.
- Fails closed. `tests/test_guard.py` lists every allowed/asked/denied shape (port the original cases, with neutral branch names and numbers), and exercises both hosts and the manual host and each autonomy level, using fake `gh`/`glab` executables on `PATH` (never the network).

`template/claude/settings.json` registers the hook exactly as the original does.

## 7. Playbooks, wrappers, and process docs (`template/`)

- `CONTRIBUTING.md`: short. Principles (one ticket per branch; tests first; agents never decide; nothing only in chat; fresh-context reviews; facts from scripts; nothing merges on red), the enforcement table (what is enforced and where, generalized), when an agent stops and asks, how to run it in Claude Code and in other agents, per-machine setup. Points to the playbooks for the steps.
- `playbooks/deliver.md`: the 14-step delivery process (start, plan, questions, plan review, claim, tests first, implement, check, final review, capture, change request, merge, verify, close), generalized; variants for tasks (tests first only when testable), bug-fix stories, hotfix stories (no plan review or questions round; still tests first, review, record; decision-log entry; follow-up refine ticket), spikes, and DECs; autonomy levels (`merge` / `pr` / `supervised`) and the manual host (stop at "ready to merge"); `/deliver <ID>`, `/deliver next`, `/deliver all`; **when nothing is ready, hand off to define**: blocking DECs most-blocking first, then drafts to refine, then ask "what next?"; in `/deliver all` resume delivering once something is ready; headless runs print decision briefs and stop. Stop-and-ask list.
- `playbooks/define.md`: section 9.
- `playbooks/review.md`: the fresh-context reviewer brief with four modes: `plan`, `tests`, `diff` (from the original), and `ticket` (refinement: ambiguity, testability, missing denied/empty/limit cases, scope creep beyond cited requirements, overlap with other tickets, size over `split_threshold`). Findings are CRITICAL / WARNING / SUGGESTION; ends with the tally line, and in diff mode `Reviewed commit: <sha>`. Inputs per mode are listed; the reviewer gets nothing else.
- `AGENTS.md.tmpl`: a framework section (what Test Kitchen is in one paragraph, where everything lives, the rules: answer from `docs/`/`backlog/` and say "not defined in this repo" instead of guessing, propose `docs/` changes before writing, document everything, never record secrets, commit only through the workflow, the commands) and a clearly marked `## This project` section left for the project (init leaves a placeholder; `/define` or the agent install drafts it on approval).
- `CLAUDE.md.tmpl`: `@AGENTS.md` plus one line about the skills.
- `claude/skills/deliver/SKILL.md`, `claude/skills/define/SKILL.md`: frontmatter (name, description with trigger phrases), then "Follow `playbooks/<x>.md`" plus Claude mechanics only (reviewer subagent via `.claude/agents/ticket-reviewer.md`, AskUserQuestion for decision rounds, model note).
- `claude/agents/ticket-reviewer.md`: frontmatter (name, description, read-only tools) + "Follow `playbooks/review.md`".
- `backlog/README.md`: the ticket rules of section 3, generalized from the original.
- `docs/product.md`, `docs/decision-log.md`, `docs/requirements/README.md`, `docs/architecture/README.md`: skeletons with one-line instructions, no example content.
- `github/pull_request_template.md`, `github/workflows/check.yml` (job `check`: checkout with full history, Python + PyYAML, a clearly marked toolchain setup step, `deliver.py check`, and on pull requests `backlog_check --pr-body` + `deliver.py gate pr` with the live description; triggers include `edited`); `gitlab/gitlab-ci.yml` (job `check`, same steps, `gate pr --from-record` on merge-request pipelines, full clone depth) and `gitlab/merge_request_templates/Default.md`. The toolchain step is a marked placeholder that init fills when it recognizes the stack (Node: setup + `npm ci`; Python: setup + `pip install -r requirements.txt`/project install) and leaves for the person otherwise.

## 8. Installer (`init.py`) and front door

- One file at the repository root, runnable as `curl -fsSL https://raw.githubusercontent.com/iakanoe/TestKitchen/v0.1.0/init.py | python3 -` (headline) or after cloning (`python3 init.py` from the target folder, or `python3 path/to/init.py --target DIR`). The clone URL lives in one constant, `REPO_URL = "https://github.com/iakanoe/TestKitchen.git"`.
- Modes: install (default), `update`, `doctor`. Flags: `--dry-run`, `--yes`, `--tests`, `--code`, `--test-command`, `--host`, `--no-claude`, `--source DIR` (install from a local checkout instead of cloning; used by tests and dogfooding), `--version vX.Y.Z`, `--target DIR`.
- Install flow: check prerequisites (python ≥ 3.9, PyYAML, git; gh/glab only warned about per host); check the folder (not a git repo → offer `git init`; uncommitted changes → warn and ask; `kitchen.lock` present → switch to update); get the pinned version (shallow clone to a temp dir, or `--source`); ask the three questions with guesses (test globs, code globs, test command — guessed from files such as `package.json`, `pyproject.toml`, `go.mod`); detect the host; show the plan (each file: create / exists → side-by-side `<name>.kitchen-new`); `--dry-run` stops here; never overwrite anything; write `kitchen.yml`, files, `kitchen.lock` (version, file list, sha256 of each installed file); fill the CI toolchain step when recognized; then run `doctor`.
- `update`: fetch the new version; for each framework file listed in the lock: unchanged locally → replace; edited locally → conflict, ask keep / take / diff (`--yes` keeps and writes `.kitchen-new`); new files added; removed files listed (never deleted); prints the CHANGELOG migration notes between versions; rewrites the lock.
- `doctor` (read-only): prerequisites, `kitchen.yml` valid and globs match something, `test_command` has `{report}`, guard registered in `.claude/settings.json` (unless `--no-claude` was used, recorded in the lock), CI file present and its toolchain step filled, host CLI signed in, `backlog_check.py` and the three `--self-test`s pass. Prints a checklist with what to do for each failure.
- No uninstall command: `guide/install.md` lists every installed file.
- `AGENT-INSTALL.md`: what an agent does: ask the person the three questions (with its guesses from the repo), run `init.py --yes` with the answers (from a pinned URL or clone), run `doctor`, report. Optional second step: offer to draft the `## This project` section of `AGENTS.md` and a first epic with draft stories via `/define` (`playbooks/define.md` mode `adopt` for existing code, `new` otherwise); writes only after the person approves. The README carries a copyable prompt pointing to the pinned `AGENT-INSTALL.md`.
- `README.md`: name, tagline, what it is (one paragraph), why (the trust problem, in plain words), what you get (bullets), the three install paths (one-liner, clone-then-run, agent prompt), a quick tour (`/define`, `/deliver next`, `deliver.py status`), works with any agent (Claude Code recommended: developed and tested there, and the only agent where the merge guard is enforced), requirements, license.
- `guide/`: `concepts.md` (tickets, criteria, tags, freeze, reviews, records, gates), `configuration.md` (every `kitchen.yml` key, examples per stack), `workflow.md` (a day with Test Kitchen: define → deliver → status → release notes), `define.md` (modes, done = no gaps), `hosts.md` (adapters, the interface, adding one), `agents.md` (using it from Claude Code, Codex, Cursor, others), `test-runners.md` (JUnit output and tag forms for pytest, vitest, jest, node:test, go, junit5), `install.md` (install, update, doctor, the installed-file list, removing it by hand), `why.md` (why each rule exists).
- `examples/`: `kitchen.yml` examples (python-pytest, node-vitest, node-test, go, monorepo with `{files:app}`).
- `CHANGELOG.md`: `## 0.1.0 — unreleased` with the feature list.

## 9. Define (`playbooks/define.md`, `/define`)

Modes: `new`, `change`, `sweep`, `refine`, `adopt`, `slice`, `bug`, `hotfix`, `ask`. Without a mode it picks: no `docs/product.md` content → `new`; code but no backlog → offer `adopt`; otherwise ask what the person wants (change, refine, sweep).

- **Opening question (new):** "Describe the product in a few sentences: who uses it, what problem it solves for them, and what it looks like when it works. Rough is fine; we'll refine it together."
- **Layers, in order:** vision → users and roles → capabilities (epics) → boundaries (out of scope) → requirements → architecture (ADR or DEC) → stories and tasks.
- **Questioning:** about three questions per round, each with a recommendation and why; never invent an answer; what the person cannot answer now becomes a DEC (a choice) or SPK (something to verify). "Does this need deciding now?" — propose deferring when it doesn't (deferring is itself a decision, logged).
- **Decision format** (DECs, and any decision round): *Your next action* (one line), *Already fixed* (what the docs settle), lettered options each with what it costs, the recommendation, *After you reply* (what will be written). Sub-questions as a table of at most 5 rows.
- **After each decision, an ordered apply checklist:** requirement text in `docs/requirements/` (or an ADR), affected criteria (removed ones stay as placeholders), the epic's Open line, the DEC status, unblocked tickets' open questions, the decision-log entry, `backlog_check.py`.
- **Checkpoints:** at the end of each topic the agent shows exactly what it will write and writes only after a yes. Requirements are always written (on the yes). Stories and tasks are always proposed, written on a yes. Done tickets are never rewritten: a change becomes a new ticket. Readiness needs an owner: the checkpoint that proposes `ready` asks for it.
- **Splitting rules:** each requirement becomes a story or is a constraint on one; each criterion lives in exactly one story (others reference it); propose a split above `split_threshold`. For large repositories, work per epic group (subagents where the agent has them).
- **refine:** run `backlog_check.py --refine`, then the reviewer in `ticket` mode on each ready or draft ticket; fix with the person; set `refined: <date>` when a ticket passes.
- **adopt:** for existing code: build a capability map from the code; write requirements marked `(observed in code)` until the person confirms; suspected bugs become DECs ("is this intended?"); existing behavior becomes `done` stories with `adopted: true`; missing tests are reported as test debt (`--test-debt`), a separate list, never blocking; epics get `code:` globs; multi-session: progress is noted in the decision log so another session can continue.
- **slice:** five questions (what hurts most today, who the first users are, any deadline, what success looks like after a month, what can wait), then propose 2–4 slices; on a yes write `releases:` in `kitchen.yml` and `release:` on each ticket. `/define slice` reshapes later. Deferred tickets go to the last slice.
- **bug:** triage first: (a) the code breaks an existing criterion → a fix story with `fixes: [US-…/ACn]` whose first test reproduces the bug, delivered normally; (b) no criterion covers the case → it is a missing requirement → `change` mode; (c) unclear → a DEC "is this intended?".
- **hotfix:** production is broken: create a story with `hotfix: true` (criteria: the broken behavior restored), a decision-log entry saying why the lane is used, and a draft TASK "Refine after hotfix US-…" for the follow-up; `/deliver` then skips plan review and the questions round but keeps tests first, review, record, and gates.
- **ask:** read-only. Answer from `docs/product.md`, requirements, ADRs, DECs, the decision log, and delivery records, citing each source. If nothing covers it, say "not defined in this repo" and offer to open a DEC or SPK through normal define. Never writes.
- **Done:** `backlog_check.py --gaps` prints nothing: no open DEC/SPK/question, every requirement covered by ready/done tickets, no unmapped code, every ready ticket refined. Test debt is separate.
- **Guardrails:** verify any platform or tool claim in its official docs before writing it; record constraints people report verbatim, with their uncertainty; after bulk renames, re-read headings and tables.
- **Hand-off from deliver:** when `deliver.py next` finds nothing, `/deliver` runs define on the DECIDE list first, then the REFINE list, then asks what to build next.

## 10. Tests (`tests/`, unittest, stdlib only)

- `test_kitchen_lib.py`, `test_backlog_check.py`, `test_deliver.py` (real throwaway git repos with a bare `origin`, port of the original's approach), `test_hosts.py` (fake `gh`/`glab` executables on `PATH`), `test_guard.py`, `test_init.py` (install from `--source` into temp repos: dry run writes nothing, never overwrites, side-by-side copies, lock contents, update conflicts, doctor), `test_agnostic.py` (fixture projects in `tests/fixtures/python/` and `tests/fixtures/node/`: install, write a story, failing tagged tests, `gate red` PASS, implement, `check` PASS; skipped with a clear reason when pytest or node ≥ 20 is missing).
- `python3 -m unittest discover -s tests` runs everything. No network.

## 11. Out of scope for v0.1

Traceability report, `/define retro` (learning from reviews), agent/model/time/review-round data in delivery records, other-agent command shortcuts, an uninstall command, an example project, pushing or publishing (only on the owner's explicit go-ahead).
