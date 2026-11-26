# Decision log

Every decision about Test Kitchen, newest first. Each entry is a level-3 heading with the date, an em dash, and a short unique title, and says what was decided, why, who decided, and where it is recorded. Change requests cite entries by title ("Log: <title>"), so a title is never renamed; a replaced decision gets a "Superseded by: <new title>" line. Entries before the first release come from the planning conversation that produced `docs/spec-v0.1.md`; the project owner decided each one.

### 2026-11-26 — The adopt fix tickets are refined and ready

- Decision: The 24 tickets of the adopt fixes are refined after two fresh-context reviews and set to `ready` with `refined: 2026-11-26`. The owner approved eight precision fixes: US-DEF-33 names the replacing ticket as the one that must be `done` and treats a `replaces:` entry naming a removed criterion as valid; US-DLV-41/AC1 states the exact `PASS pr: <ID>` output and that `<ID>` is the delivered ticket's; US-DLV-38 gains a criterion that the verdict follows `--head` for a ticket present at only one revision; TASK-INST-03 splits its criteria so each claim stands alone; US-GRD-11 names the shells and command substitution; US-GRD-15 notes that US-GRD-06/AC5's "branches" is GitLab's `/repository/branches` and gains a criterion that every spelling of the listed addresses counts; US-GRD-16, US-DLV-39, and US-DLV-40 wait on US-DEF-33 (`blocked_by`) so the `replaces:` field exists first.
- Why: Two independent reviews found criteria that a reviewer could read two ways or that left a case open; each fix makes the criterion observable, and the blocker order keeps the tickets that replace criteria from being delivered before the checker accepts `replaces:`.
- Decided by: Ianick Noejovich.
- Recorded in: the tickets.

### 2026-11-26 — A new definition retires a done ticket's criterion through replaces

- Decision: When a new definition contradicts a criterion of a `done` ticket (adopted or not), `/define` warns the person and shows the affected criterion; on a yes, the new ticket records it in a `replaces: [<ticket>/AC<n>]` frontmatter list (like `fixes:`); when that new ticket is delivered, the replaced criterion becomes `- AC<n>: (removed YYYY-MM-DD, replaced by <ticket>)` in the done ticket (the one allowed edit of a done ticket), and the checker refuses a done ticket whose `replaces:` criteria are still live. Until `backlog_check.py` accepts the field, the tickets that replace criteria list them in their Notes ("Replaces (to become a `replaces:` field once US-DEF-33 is delivered)"): US-DLV-39 (US-DLV-21/AC1, AC3, AC4), US-DLV-40 (US-DLV-04/AC2, AC3, AC4), and US-GRD-16 (US-GRD-08/AC3, US-GRD-09/AC6). Closes DEC-DEF-04.
- Why: A done ticket is never rewritten, so without this the backlog keeps two live criteria that disagree, and nothing says which one binds.
- Decided by: Ianick Noejovich.
- Recorded in: requirements DEF-R45, DEF-R46, DLV-R51; DEC-DEF-04; US-DEF-33, TASK-DEF-04, US-DLV-41, TASK-DLV-02.

### 2026-11-26 — Review-only stories become tasks

- Decision: The three documentation-only stories become tasks with new IDs: US-DEF-31 becomes TASK-DEF-02, US-DEF-32 becomes TASK-DEF-03, and US-INST-26 becomes TASK-INST-03; the old IDs are retired, never reused. Their criteria are checkable statements, and the final review verifies them. DEC-DEF-05 asks how such criteria should be accepted from now on.
- Why: A done story needs a tagged test for every live criterion (DEF-R14), and no test can check the wording of a playbook, a guide, or an instruction file; an untestable task is confirmed by the final reviewer instead (DLV-R37).
- Decided by: Ianick Noejovich.
- Recorded in: TASK-DEF-02, TASK-DEF-03, TASK-INST-03; DEC-DEF-02, DEC-DEF-03, DEC-INST-03 (their outcomes); DEC-DEF-05 (open). The entries "Epics stay exempt from readiness", "The playbook's Done paragraph follows --gaps", and "AGENT-INSTALL.md says the shell may have no terminal" name the old IDs.

### 2026-11-26 — Refinement widens ten requirements of the adopt decisions

- Decision: Refining the tickets of the 2026-11-25 decisions, the owner made ten requirements wider or exact, each superseded by a new one: CONF-R28 (a glob is refused when it starts with `/` after surrounding whitespace is trimmed and a leading `./` is removed); DEF-R43 and DEF-R44 (`guide/concepts.md` and `guide/define.md` are fixed in the same tickets, and the Done paragraph also says draft stories and tasks are gaps); GRD-R32 (a `cd` inside a shell's `-c` script or a pipeline stage also makes the folder unknown); GRD-R33 (`git apply`, `patch`, and `git reset --hard` ask in every project, while `git apply --check`, `--stat`, `--numstat`, and `patch --dry-run` stay allowed); GRD-R34 (appending to the decision log stays free through `>>`, `tee -a`, Edit, and MultiEdit, while replacing or removing it asks, a Write call included); GRD-R35 (the branch-protection writes denied are listed, as GitHub's and GitLab's documentation confirm them on 2026-11-26); INST-R35 (`guide/install.md` drops the claim that an agent's shell has no terminal); INST-R36 (a missing lock `version`, or an `options` value that is not a table, is a broken lock, and the accepted version form is `X.Y.Z` with an optional leading `v`); INST-R37 (the line telling the person to set `host:` prints in the plan, on `--dry-run` too, and after a real run). US-GRD-14 is split: the decision-log part becomes US-GRD-16. US-HOST-13 gets an open question naming SPK-HOST-01: until it runs, empty output from a list command counts as no open change requests. It widens, and does not replace, the entries "Globs never start with a slash", "Epics stay exempt from readiness", "The playbook's Done paragraph follows --gaps", "The guard treats the folder as unknown after cd -, popd, or a subshell cd", "The guard asks before writes it cannot see", "AGENT-INSTALL.md says the shell may have no terminal", "A lock version that is not a number is a broken lock", and "Host switch on update tells the person to set kitchen.yml's host".
- Why: The ticket review found cases the 2026-11-25 wording left open (whitespace and `./` before a slash, other folder changes, which writes append and which replace, which endpoints protect a branch, other broken lock fields, the guides that repeat the same text), and each answer fails toward the stricter or clearer reading.
- Decided by: Ianick Noejovich.
- Recorded in: requirements CONF-R28, DEF-R43, DEF-R44, GRD-R32, GRD-R33, GRD-R34, GRD-R35, INST-R35, INST-R36, INST-R37; superseded CONF-R27, DEF-R41, DEF-R42, GRD-R26, GRD-R29, GRD-R30, GRD-R31, INST-R33, INST-R34, INST-R30; US-CONF-17, TASK-DEF-02, TASK-DEF-03, US-GRD-11, US-GRD-14, US-GRD-15, US-GRD-16, US-HOST-13, TASK-INST-03, US-INST-25, US-INST-27; the outcomes of DEC-CONF-02, DEC-DEF-02, DEC-DEF-03, DEC-GRD-01, DEC-GRD-04, DEC-INST-01, DEC-INST-03, DEC-INST-04.

### 2026-11-26 — New tickets leave out criteria that are already true

- Decision: A new ticket's criteria state only what changes. A criterion that restates behavior already true today (other checks unchanged, GET reads stay allowed, a full sha still builds the command) is left out, and a Notes line names the existing criterion that holds it. Draft tickets were never referenced by tests, so their criteria are renumbered from AC1. When a new ticket replaces a criterion of a done ticket, it keeps the part of that criterion that stays true, since that part would otherwise lose its criterion once the old one is crossed out.
- Why: A criterion that is already true passes before any code changes, so it proves nothing about the change and duplicates a criterion that lives in another story.
- Decided by: Ianick Noejovich.
- Recorded in: US-CONF-17, US-DEF-30, TASK-DEF-02, US-GRD-11, US-GRD-12, US-GRD-13, US-GRD-15, US-HOST-13, US-HOST-14, US-INST-25, US-INST-27.

### 2026-11-25 — The guard asks before writes it cannot see

- Decision: Option (a): `git apply`, `patch`, and `git reset --hard` ask whenever the project has protected files; deleting or truncating `docs/decision-log.md` asks while appending stays free; branch-protection API writes are denied. Closes DEC-GRD-04.
- Why: As the DEC recommended, each one is a plain command an agent might run by mistake, which is the guard's job; `git reset --hard` asking may slow some recoveries, an accepted cost.
- Decided by: Ianick Noejovich.
- Recorded in: requirements GRD-R29, GRD-R30, GRD-R31; superseded GRD-R20 (by GRD-R30); confirmed GRD-R22; US-GRD-14, US-GRD-15. It narrows "The guard does not ask before decision-log edits": appending and edits stay free.

### 2026-11-25 — The guard denies GraphQL deleteRef

- Decision: Option (a): the GraphQL `deleteRef` mutation is denied like REST ref writes; `updatePullRequestBranch` is not denied (option (b) was not chosen) and still asks. Closes DEC-GRD-03.
- Why: It brings the GraphQL path in line with the REST path and with "Guard hardening after the adversarial review" (host API calls that write refs are refused); GitHub's GraphQL reference lists `deleteRef` ("Delete a Git Ref."), https://docs.github.com/en/graphql/reference/git, checked 2026-11-25.
- Decided by: Ianick Noejovich.
- Recorded in: requirements GRD-R28; confirmed GRD-R14; US-GRD-13.

### 2026-11-25 — git config asks only for the config subcommand

- Decision: Option (a): `git config` asks only when git's subcommand, after the global options, is `config`. Closes DEC-GRD-02.
- Why: As the DEC recommended, it matches the stated rule and the guard's docstring, keeps every `git config` write asking, and removes prompts on ordinary file names.
- Decided by: Ianick Noejovich.
- Recorded in: requirements GRD-R27; confirmed GRD-R16; US-GRD-12.

### 2026-11-25 — The guard treats the folder as unknown after cd -, popd, or a subshell cd

- Decision: Option (a): after `cd -`, `popd`, or a `cd` inside a subshell or group, the guard treats the folder as unknown, so every later write in the call asks. Closes DEC-GRD-01.
- Why: As the DEC recommended, it fails toward asking, matches how the guard already treats a folder known only at run time, and is small.
- Decided by: Ianick Noejovich.
- Recorded in: requirements GRD-R26; confirmed GRD-R22; US-GRD-11.

### 2026-11-25 — The merge sha check matches the whole value

- Decision: Fix: the merge sha check matches the whole value, so a trailing newline is refused. Closes DEC-HOST-02.
- Why: As the DEC proposed, it closes a gap in the fail-closed validation of the one function that defines the allowed merge command; HOST-R14 already says only the full 40-character sha is accepted.
- Decided by: Ianick Noejovich.
- Recorded in: requirements HOST-R27; confirmed HOST-R14; US-HOST-14.

### 2026-11-25 — Unreadable host CLI output is a host error

- Decision: Fix: host CLI output that is not JSON, when listing the branches of open change requests or reading a change request, is a HostError naming the command. Closes DEC-HOST-01.
- Why: As the DEC proposed, an unreadable answer is treated like a failing CLI, so `next` stops with its own message and `status` uses its offline fallback instead of a traceback.
- Decided by: Ianick Noejovich.
- Recorded in: requirements HOST-R26; confirmed HOST-R04, HOST-R06; US-HOST-13. HOST-R05 stays marked as observed in code until SPK-HOST-01 runs.

### 2026-11-25 — pr-body prints the playbook's Ticket line per type

- Decision: Option (b): `deliver.py pr-body` prints the playbook's wording per type (`None. Spike <ID>: …` for a spike, `None. Decides <ID> …` for a decision) and refuses an epic. Closes DEC-DLV-03.
- Why: As the DEC recommended, the script is where facts come from, so its skeleton should already say what the playbook asks for, and refusing an epic matches "an epic is not delivered".
- Decided by: Ianick Noejovich.
- Recorded in: requirements DLV-R50; superseded DLV-R06 (by DLV-R50); confirmed DLV-R37; US-DLV-40.

### 2026-11-25 — Release notes leave out adopted tickets

- Decision: Option (b): release notes leave adopted tickets out on every path. Closes DEC-DLV-02.
- Why: As the DEC recommended, adopted tickets record behavior that shipped before the backlog existed, so listing them as a release's changes misleads, and the tag and no-tag paths then agree.
- Decided by: Ianick Noejovich.
- Recorded in: requirements DLV-R49; superseded DLV-R27 (by DLV-R49); US-DLV-39.

### 2026-11-25 — gate pr reads tickets and kitchen.yml at --head

- Decision: Option (b): `deliver.py gate pr` reads the ticket files and `kitchen.yml` at `--head` too, so it judges exactly the revision it names. Closes DEC-DLV-01.
- Why: The gate then judges one revision consistently even when CI checks out another commit than the one it names.
- Decided by: Ianick Noejovich.
- Recorded in: requirements DLV-R48; confirmed DLV-R14, DLV-R16, DLV-R20; US-DLV-38.

### 2026-11-25 — The playbook's Done paragraph follows --gaps

- Decision: Option (a): the "Done" paragraph of `playbooks/define.md` is reworded to match `--gaps`: it adds unconfirmed observed requirements and says "cited by a story or task that is not deferred". Closes DEC-DEF-03.
- Why: As the DEC recommended, the script's rule is tested and drafts already show as their own gap, so only the text was out of step.
- Decided by: Ianick Noejovich.
- Recorded in: requirements DEF-R42; confirmed DEF-R03, DEF-R18, DEF-R39; US-DEF-32.

### 2026-11-25 — Epics stay exempt from readiness

- Decision: Option (b): epics stay exempt from the readiness rules, and `backlog/README.md`, "Readiness", says that it applies to tickets other than epics. Closes DEC-DEF-02.
- Why: As the DEC recommended, it matches the recorded choice that epics need only their fields ("Script choices made while building v0.1"), and requiring owners could fail installed projects whose epics use `TBD`.
- Decided by: Ianick Noejovich.
- Recorded in: requirements DEF-R41; confirmed DEF-R09; US-DEF-31.

### 2026-11-25 — The strict summary counts uncovered requirements

- Decision: Option (a): the `backlog_check.py` summary counts uncovered requirements, as errors with `--strict` and as warnings without it; exit codes are unchanged. Closes DEC-DEF-01.
- Why: As the DEC recommended, a summary that disagrees with the lines under it misleads people and CI logs, and no exit code changes.
- Decided by: Ianick Noejovich.
- Recorded in: requirements DEF-R40; confirmed DEF-R17, DEF-R18; US-DEF-30.

### 2026-11-25 — Globs never start with a slash

- Decision: Option (a): a glob with a leading `/` is rejected with a message like the backslash one. Closes DEC-CONF-02.
- Why: As the DEC recommended, it keeps one meaning per pattern, and the reason backslashes are rejected (they would silently match nothing) applies equally.
- Decided by: Ianick Noejovich.
- Recorded in: requirements CONF-R27; confirmed CONF-R11, CONF-R12; US-CONF-17.

### 2026-11-25 — A kitchen.yml that is not UTF-8 is a configuration error

- Decision: Option (a): a `kitchen.yml` that is not valid UTF-8 is the configuration error `kitchen.yml: not valid UTF-8`, with no traceback. Closes DEC-CONF-01.
- Why: As the DEC recommended, it matches CONF-R05 and the configuration guide's promise of one clear message per invalid value.
- Decided by: Ianick Noejovich.
- Recorded in: requirements CONF-R26; confirmed CONF-R01, CONF-R05; US-CONF-16.

### 2026-11-25 — A lock version that is not a number is a broken lock

- Decision: Option (a): a `kitchen.lock` whose `version` is not a dotted number gives the same `error: kitchen.lock … Restore it from git history.` failure (exit 1) as other broken locks. Closes DEC-INST-04.
- Why: As the DEC recommended, one check makes every lock problem read the same way.
- Decided by: Ianick Noejovich.
- Recorded in: requirements INST-R34; superseded INST-R27 (by INST-R34); confirmed INST-R17; US-INST-27.

### 2026-11-25 — AGENT-INSTALL.md says the shell may have no terminal

- Decision: Option (a): `AGENT-INSTALL.md` is reworded to "Your shell may have no terminal …; always pass `--yes`". Closes DEC-INST-03.
- Why: As the DEC recommended, it keeps the instruction to always pass `--yes` and drops a claim nobody has checked across agents.
- Decided by: Ianick Noejovich.
- Recorded in: requirements INST-R33; confirmed INST-R07, INST-R29; US-INST-26.

### 2026-11-25 — Python 3.6 and older may fail with a syntax error

- Decision: Option (b): Python 3.6 and older getting a syntax error before the version check is accepted, and the code comment in `init.py` is corrected to say that Python 3.7 and later get the sentence. Closes DEC-INST-02.
- Why: As the DEC recommended, Python 3.6 is long out of support, and keeping it parseable would need a style exception in `init.py`.
- Decided by: Ianick Noejovich.
- Recorded in: requirements INST-R32; confirmed INST-R03; TASK-INST-02. INST-R03 also lost its reference to this DEC (a wording fix).

### 2026-11-25 — Host switch on update tells the person to set kitchen.yml's host

- Decision: Option (a): `kitchen.yml` stays untouched; an `update --host <new host>` that changes the host prints that `host:` in `kitchen.yml` must be set to the new host, and `doctor`'s host-mismatch fix offers both directions (set `host:` in `kitchen.yml` to the installed host, or run `update --host <other host>`). Closes DEC-INST-01.
- Why: As the DEC recommended, it keeps the recorded rule that `update` never edits the project's configuration ("Installer choices made while building v0.1") and stops `doctor` from pointing the person back to the host they just left.
- Decided by: Ianick Noejovich.
- Recorded in: requirements INST-R30, INST-R31; confirmed INST-R20, INST-R25; US-INST-25.

### 2026-11-25 — Adopt progress: all six epics written

- Decision: the six epics are adopted and written: `INST` (29 requirements, 24 stories), `CONF` (25, 15 stories and 2 tasks), `DEF` (39, 29 stories), `DLV` (47, 37 stories), `HOST` (25, 12 stories), `GRD` (25, 10 stories); every story and adopted task is `done` with `adopted: true`; each epic has one draft "Pay test debt" task. Each epic's checkpoint was approved as shown. 18 DECs ask "Is this intended?" about behavior found while reading the code (DEC-GRD-03's GraphQL claim was checked in GitHub's GraphQL reference; DEC-GRD-04 collects the writes the guard does not see), and SPK-HOST-01 verifies the GitLab adapter on a real GitLab project.
- Why: adopt mode, step 2 of `playbooks/define.md`.
- Decided by: Ianick Noejovich (each epic's checkpoint).
- Recorded in: `docs/requirements/*.md`; `backlog/*/`.
- Not done yet (for the next session): step 4, confirming the 190 `(observed in code)` requirements (the person chose to do it after all epics were written); the 18 DECs and SPK-HOST-01; the six test-debt tasks (636 criteria on `--test-debt`, about 150 of them review-only).

### 2026-11-25 — Adopt: test debt and review-only behavior

- Decision: Test Kitchen's adopted criteria are recorded as test debt, with one draft task per epic ("Pay test debt: tagged tests for EP-<CODE>") that adds tagged tests in new test files without the no-trace marker. Behavior only a review can check (playbooks, docs, agent instructions) stays in adopted stories, and its criteria stay on the test-debt list, read as "review only".
- Why: this repository's test files carry `test-kitchen: no-trace` because they hold example tickets, so tags there can never prove a criterion; paying the debt in separate files needs no framework change. Keeping review-only behavior in stories keeps its requirements covered without stretching what a task is.
- Decided by: Ianick Noejovich.
- Recorded in: the epics' test-debt tasks; `backlog_check.py --test-debt`.

### 2026-11-25 — Adopt: product, epics, and owner

- Decision: `docs/product.md` is written as confirmed (vision, three roles, six capabilities, boundaries). The existing code is split into six epics, each owning one code file: `INST` (`init.py`), `CONF` (`template/scripts/kitchen_lib.py`), `DEF` (`template/scripts/backlog_check.py`), `DLV` (`template/scripts/deliver.py`), `HOST` (`template/scripts/hosts.py`), `GRD` (`template/claude/hooks/guard.py`). Ianick Noejovich owns the epics and every adopted ticket. The six epics were drafted in parallel and de-duplicated before their checkpoints.
- Why: one epic per capability gives every code file exactly one owner, so `--gaps` reports no unclaimed code.
- Decided by: Ianick Noejovich.
- Recorded in: `docs/product.md`; `backlog/<CODE>-*/epic.md`.

### 2026-11-25 — CI runs Python 3.9 on Ubuntu 24.04

The product-test job on Python 3.9 failed before running anything: `actions/setup-python` publishes 3.9 builds only for Ubuntu 22.04 and 24.04, and `ubuntu-latest` is now 26.04. The 3.9 job pins `ubuntu-24.04`; the current-Python job stays on `ubuntu-latest`. 3.9 stays the supported minimum because it is the `python3` macOS ships. When GitHub retires the 24.04 image, the minimum has to move or 3.9 has to run another way. Recorded in `.github/workflows/ci.yml`. Decided while fixing CI on the first change request.

### 2026-11-25 — An empty project is not fully defined

Right after installing Test Kitchen on itself, `backlog_check.py --gaps` printed nothing although nothing was defined: with no requirements, coverage passed trivially, and the unmapped-code check only ran once some epic declared `code:`. `--gaps` now also lists a missing `docs/product.md`, a `docs/product.md` with only the skeleton's headings and comments, a project with no requirements, and, while no epic declares `code:`, existing code as one gap in all (one line per file once any epic declares `code:`, as before). This amends `docs/spec-v0.1.md` section 5. Decided by the project owner ("fix the hole first").

### 2026-11-25 — Test Kitchen installed on its own repository

The root now runs Test Kitchen 0.1.0, installed from the local `template/` (the bootstrap case of "Dogfooding layout"): `tests: ["tests/**"]`, `code: ["init.py", "template/scripts/**", "template/claude/hooks/**"]` (the product code that needs tests first; playbooks and docs don't), `ignore: ["examples/**", "tests/fixtures/**"]`, host github. The test command runs the stdlib unittest suite through pytest, because unittest writes no JUnit XML; pytest is a development dependency only, installed in CI's toolchain step. The CI is two workflows rather than one with two jobs: `check.yml` (the installed framework file, changed only through `init.py update`) and `ci.yml` (the product tests on Python 3.9 and a current Python). The template's decision-log header was merged into this log's introduction. Next step for the owner: `/define adopt` on this repository, after which all work goes through `/define` and `/deliver`.

### 2026-11-25 — Guard hardening after the adversarial review

A fresh-context adversarial review reproduced five ways around the guard: push/merge words built at run time (`git pu$'\x73'h`), host-API merges (`gh api …/merges -fbase=main`), glab's `accept`/`new` aliases, git aliases in another case (`git Ship`), and a guard that fails to compile letting every call through. The shell side now uses a lexer that splits commands the way bash and zsh do, decodes `$'…'`, flags anything built at run time, and reads inside `$()`, backticks, `sh -c`, `eval`, `xargs`, and `find -exec`. Choices:
- A git/gh/glab program or subcommand built at run time is refused. Unknown gh/glab top-level commands (possible aliases or extensions) are refused. Host API calls that merge, write refs, or commit to a branch are refused, sandbox mode included, as is `gh repo sync <repository>`. A git alias that pushes, merges, or runs a shell is refused; other aliases ask. `git -c`, `--config-env`, and `GIT_*` variables ask.
- The hook command is `python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/guard.py" || exit 2`: a guard that can't start exits 2, which blocks the call, instead of 1, which Claude Code treats as non-blocking.
- Shell writes to protected paths are read from every redirect form and from the files writing programs name (`sed -i`, `perl -i`, `find -delete`, `curl -o`, `tar -C`, `git clean`, `dd of=`, …), resolved against the call's working folder; archive extraction, `wget`, `curl -O`, and `git clean` without a path count as writes to the current folder. Paths are compared after NFKC normalization and case folding.
- An unquoted bare `push` or `merge` word still triggers the strict checks, so `make push` or `pytest -k merge` is refused; quoting the word avoids it. Path parts (`tests/push.test.ts`) and quoted search patterns don't count. Heredoc bodies fed to `cat` are data; fed to a shell or interpreter, they are code.

### 2026-11-24 — The `test-kitchen: no-trace` marker

Test Kitchen's own tests are full of example tickets, tags, and TODOs, which the trace scans read as real references, so the repository could not install Test Kitchen on itself. A file whose first ten lines contain `test-kitchen: no-trace` is now treated as data: it is not scanned for tags, TODOs, or DEC mentions, and its tags never prove a criterion. The gates still classify it as a test or code file, so changes to it still count for the freeze and review checks. Only the first lines count, so the marker can't hide in the middle of a file. Any project whose tests handle ticket-like text can use it. Decided while installing Test Kitchen on its own repository; recorded in `template/backlog/README.md` and `guide/concepts.md`.

### 2026-11-24 — History checks see merge commits

The fresh-context review found that code written inside a merge commit (a conflict resolution after the review, or an implementation slipped in before the freeze) was invisible to `gate pr`. Now a merge commit changes a file when git's combined diff (`--cc`) shows a hunk for it; a conflict resolved by taking one side counts as no change, so a clean merge of the default branch still passes. In a merge, a skip marker counts only when its line is new against every parent. Every git call whose output is parsed runs with `core.quotePath=false`, no color, no external diff, and explicit prefixes, so user git config and unusual file names can't hide changes. Other fixes from the same review: `gate merge` also fails on backlog errors; a task whose tests carry its tags needs a freeze commit; "Test changes" matches whole paths or file names, not substrings; `status` leaves claimed tickets out of READY; `gate pr` falls back to the local default branch when `origin/<default>` is missing; globs with backslashes are rejected; a `kitchen.lock` that isn't valid JSON is a config error (the guard then refuses pushes and merges).

### 2026-11-24 — Guard choices made while building v0.1

Made by the builder of `template/claude/hooks/guard.py`, within `docs/spec-v0.1.md` section 6:
- The project root is `CLAUDE_PROJECT_DIR`, else the git checkout the guard file sits in (never the command's working directory). Pushes and merges are refused unless they run from that checkout, so other worktrees and clones are refused.
- A merge must equal `merge_argv` word for word: no `--delete-branch`, `=` forms, or reordered options (the source project let some reach the gate). A merge through the other host's CLI is refused, and the message shows the right command.
- Every check runs before any ask is returned, and a refusal always wins, so an ask (a force push) can't hide a later refused command (a push to the default branch) in the same call. This closes a hole in the source project's hook.
- Protected paths match case-insensitively (macOS); `.claude/` and `.git/` count at any depth; the decision-log exemption wins even if `kitchen.lock` lists the file. The four framework scripts are always protected, as is every `.kitchen-new` copy of a locked file, and all of `scripts/` when the lock can't be read. `python3 scripts/x.py … > file` is not a write to the script.
- glab rules (checked against the glab docs): `mr create` with `--push`, `--fill`/`-f` (which push unless `--push=false`), or `--auto-merge` is refused; `--create-source-branch` asks; `ci view` asks; `glab api --form` is a write. The token list covers GitHub, GitLab (including `CI_JOB_TOKEN` and the `PRIVATE-TOKEN` header), and OAuth names. `touch`, `chmod`, `unlink`, and bare folder names (`rm -rf docs`) are writes. The default branch is compared without case.
- The merge gate runs with the hook's own interpreter. If the scripts, `kitchen.yml`, or `kitchen.lock` fail to load, only pushes and merges are refused; other work continues.

### 2026-11-24 — A change request with no ticket that touches code needs a review

`gate pr` used to check only the delivery record for a change request whose `## Ticket` starts `None. …`, so code could reach the default branch with no review at all. Now, when the branch's own changes touch a `code` or `tests` file, such a change request must also pass the review checks: a tally with `CRITICAL: 0`, a `Reviewed commit:` on the branch, and nothing in code or tests changed after it. It still needs no plan or freeze, because it has no criteria. Decided while fixing the fresh-context review of v0.1; recorded in `template/playbooks/deliver.md` and `template/CONTRIBUTING.md`.

### 2026-11-24 — Test Kitchen's own files are excluded from project scans

A project whose `code` or `tests` globs are broad (`**/*.py`) would otherwise scan the installed framework scripts, whose comments hold example TODOs and DEC IDs, and fail its first `check` right after install. Every file listed in `kitchen.lock` is left out of the code trace, tag scans, and gate classification. Decided while fixing the fresh-context review of v0.1.

### 2026-11-24 — Required host settings

Merges must be merge commits (the gates and records point at the freeze and reviewed commits, which squash and rebase rewrite), and on GitLab merged results pipelines must be off (the adapter reads the branch's own head pipeline and fails closed on a merged results one). Documented in `guide/hosts.md` and `template/CONTRIBUTING.md`. Decided while fixing the fresh-context review of v0.1.

### 2026-11-24 — Script choices made while building v0.1

Made by the builder of `kitchen_lib.py`, `hosts.py`, `backlog_check.py`, and `deliver.py`, within `docs/spec-v0.1.md` section 5:
- Unknown ticket fields warn, not fail. Epics need only id, type, title, owner, assignee_type, status. Stories must cite a requirement once `ready` or later; decisions may cite none. Slugs are lowercase kebab-case.
- A `done` ticket with an unfinished blocker is an error. A deferred ticket with a release must be in the last slice; a `release` while slices are off only warns. `priority` is a ticket field only, not a `kitchen.yml` key.
- TODO and DEC tracing scans test files as well as code; scans include untracked files that git does not ignore.
- Globs support `**`, `*`, `?` only (no `[...]` or `{a,b}`). Identifier tags also accept a camel-case left boundary (`TestUS_PAY_03_AC2`).
- `next` always prints a `NEXT` line first (`NEXT none: …` when nothing is ready); DECIDE includes decisions that block indirectly; REFINE lists draft stories, tasks, and spikes; IDs sort naturally.
- `gate red`: skipped tests don't count as run; a task without tags passes. Plan rows match exactly (`AC10` never counts as `AC1`). Skip/focus markers are checked in test files only.
- Hotfix: `## Gaps found` must name another existing ticket; under `supervised`, hotfixes also need the approvals.
- Records carry `- Change request: #N url`; the marker is `<!-- change-request-description -->` (`<!-- pr-description -->` is read too). `gate pr --from-record` uses the record committed on the branch for this branch's name. `--pr-body` accepts a record file and checks the text after the marker.
- GitLab: a failed job that may fail counts as skipped; a manual job is skipped if it may fail, else pending; GitLab's "still checking" merge states mean unknown; merged-results pipelines fail closed. The glab commands follow the official docs cited in `hosts.py`, but were not run (glab is not installed on the build machine).
- `merge-command` exits 0 under `pr`/`supervised` with a note on stderr, and 1 on the manual host. `status` reads local copies of origin's branches and works offline. Release notes cover done tickets only.

### 2026-11-24 — Installer choices made while building v0.1

Made by the builder of `init.py`, within `docs/spec-v0.1.md` section 8:
- `kitchen.lock` is JSON (any reader, including the guard, can read it without PyYAML): `about`, `lock_format: 1`, `version`, `source`, `options {host, no_claude, toolchain}`, `files {path: sha256}`, `side_by_side`. `kitchen.yml` is not in `files`; `update` never touches it.
- A local source is recorded as `local checkout (commit <sha>)`, never an absolute path. Run from a clone, `init.py` installs from its own `template/`; it downloads only with `--version`. The default version is the running file's `VERSION`; there is no "latest" lookup.
- `--no-claude` also skips `CLAUDE.md`. `--host` can switch hosts on update; `--no-claude` can be turned on by an update, never off.
- Without a terminal and without `--yes`, anything needing confirmation stops with exit 2 and writes nothing; a dry run never asks. Installing into a subfolder of a repository is refused; `git init` happens only after the plan is confirmed. Install exits 0 once files are written even if the doctor run after it reports failures.
- Update conflicts only when both sides changed a file; a deleted framework file is restored.
- `.tmpl` is dropped anywhere in `template/`; only known `{{key}}` tokens are replaced.
- CI toolchain fill: only npm and pip are recognized (yarn, pnpm, bun, Poetry, uv, Pipenv leave the placeholder). The Python fill installs `pyyaml` (plus `pytest` when the test command uses it). Node on GitLab installs `nodejs npm` with apt when missing (image `python:3`). The marker becomes `# TEST-KITCHEN: toolchain setup (filled by init.py: …)`.
- Doctor is read-only, fails when Claude Code's `disableAllHooks` is on, and treats globs that match nothing and a signed-out host CLI as warnings.
- Guessed test commands: pytest as `python3 -m pytest`; Go as `gotestsum … ./...` (a full run, since `go test` takes packages); JUnit 5 needs a small merge script shown in the guide.

### 2026-11-24 — Process-doc choices made while building v0.1

Made by the builder of the playbooks and CI templates, within `docs/spec-v0.1.md` sections 7 and 9:
- `/define` commits on a `docs/define-<topic>` branch through a non-ticket change request, merged according to the autonomy level. Spike and DEC change requests start `## Ticket` with `None. …`.
- A task that is only partly testable is a reason to stop and propose a split, since `gate red` needs a test per criterion.
- A hotfix skips only the questions round and the plan review; the tests review still runs.
- A bug-fix test may carry both its own tag and the broken criterion's tag.
- A person merges with a merge commit (no squash or rebase), so the freeze and reviewed commits survive on the default branch.
- Each ticket's decision-log entries are written at the capture step; a replaced entry gets a `Superseded by:` line and titles are never renamed.
- A deferred DEC has `status: deferred` and is not open; a decided DEC gets an `## Outcome` section.
- The full stop-and-ask list lives only in `playbooks/deliver.md`; `CONTRIBUTING.md` summarizes it.
- GitHub CI: push trigger `[main, master]`; GitLab CI: no duplicate pipelines, `GIT_DEPTH: "0"`, drafts detected by `CI_MERGE_REQUEST_DRAFT` or a "Draft:" title, and `--pr-body` reads the committed record because the description variable is truncated at 2700 characters. GitLab starts no pipeline when a draft is marked ready, so the playbook marks the merge request ready before the final push.

### 2026-11-24 — The guard does not ask before decision-log edits

`docs/decision-log.md` is appended to at every ticket's capture step. Protecting it like the rest of `docs/` would make every delivery ask a person and stop unattended runs. The source project kept its decision log outside the protected folders too. Every other `docs/` file stays protected. Decided while building v0.1 (raised by the process-doc builder).

### 2026-11-24 — GitHub home: iakanoe/TestKitchen

The repository lives at github.com/iakanoe/TestKitchen (public, empty when chosen); `origin` is `git@github.com:iakanoe/TestKitchen.git`. The installer clones over HTTPS (`https://github.com/iakanoe/TestKitchen.git`) so installing needs no SSH key, and the pinned one-liner is `https://raw.githubusercontent.com/iakanoe/TestKitchen/v0.1.0/init.py`. Nothing is pushed until the owner says so. Decided by the project owner.

### 2026-11-24 — Build v0.1 from the approved plan

The planning is done and v0.1 is built from `docs/spec-v0.1.md`. Nothing is pushed or published until the owner says so. Decided by the project owner.

### 2026-11-24 — `blocked_by` means "can start, can't finish"

A ticket can be `ready` while a blocker is unfinished, and `deliver.py next` still never picks it. Readiness covers what the ticket itself needs (owner, answered questions, live criteria); blockers only control picking and finishing. This differs from the source project, where `ready` also required finished blockers. Recorded in `docs/spec-v0.1.md` section 3.

### 2026-11-24 — Two tag forms for tests

Tests prove criteria by tag in the test name, either `[US-PAY-03/AC2]` or the identifier form `us_pay_03_ac2`. The identifier form exists because many languages (Python, Go, Java) report function names that cannot hold brackets. Recorded in `docs/spec-v0.1.md` section 3.

### 2026-11-24 — Scope of v0.1

In: the delivery workflow (`/deliver`), the definition workflow (`/define` with modes new, change, sweep, refine, adopt, slice, bug, hotfix, ask), task tickets, the autonomy setting, `deliver.py status`, release notes, optional release slices, optional priority, host adapters (github, gitlab, manual), the installer with update and doctor, and the agent install prompt. Later: traceability report, learning from reviews (`/define retro`), richer delivery-record data. Decided by the project owner.

### 2026-11-24 — Platform-agnostic by design

No language, framework, or platform is assumed: three required config keys (`tests`, `code`, `test_command`) plus optional ones, and JUnit XML as the one test-result format. Hosts are adapters; the neutral term is "change request". Any AI agent can run it from `AGENTS.md` and the plain-markdown playbooks; Claude Code is recommended because it was developed and tested there and is the only agent where the merge guard is enforced. Decided by the project owner.

### 2026-11-24 — Name, license, language

Name "Test Kitchen", tagline "Let the agents cook (then taste the food) AKA vibecoding for devs with trust issues"; no kitchen metaphors anywhere else. License Apache-2.0. Docs in English only. Decided by the project owner.

### 2026-11-24 — Dogfooding layout

The product lives in `template/`, with instruction files stored inertly (`AGENTS.md.tmpl`, `claude/`, `github/`, `gitlab/`) and renamed on install, so Test Kitchen can later be installed on its own repository without the two interfering. The root runs the previous release and is changed only through `init.py update`. Decided by the project owner (the safer of the two options offered).
