# Decision log

Every decision about Test Kitchen, newest first. Each entry is a level-3 heading with the date, an em dash, and a short unique title, and says what was decided, why, who decided, and where it is recorded. Change requests cite entries by title ("Log: <title>"), so a title is never renamed; a replaced decision gets a "Superseded by: <new title>" line. Entries before the first release come from the planning conversation that produced `docs/spec-v0.1.md`; the project owner decided each one.

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
