# Install, update, doctor

`init.py` is one self-contained Python file. It installs Test Kitchen into a project's repository, updates an installed copy, and checks one. It needs Python 3.9 or later and git; the installed scripts also need PyYAML, which `init.py` checks for and explains how to install.

## Installing

Run from the root of the project's git repository:

```sh
# 1. One line, pinned to a release
curl -fsSL https://raw.githubusercontent.com/iakanoe/TestKitchen/v0.1.0/init.py | python3 -

# 2. Clone, then run (installs from the clone's own template/, no second download)
git clone --branch v0.1.0 https://github.com/iakanoe/TestKitchen.git
python3 TestKitchen/init.py --target path/to/project
```

The third path is to ask an agent: the README has a prompt that points it at [AGENT-INSTALL.md](../AGENT-INSTALL.md).

What an install does, in order:

1. **Prerequisites.** Python 3.9+, PyYAML, and git are required (a dry run only warns about PyYAML). `gh` or `glab` is only warned about, for the host in use.
2. **The folder.** Not a git repository: the plan includes `git init`. Inside a repository but not at its root: refused, with the root to use. Uncommitted changes: a warning and a question (commit first so Test Kitchen's changes can be reviewed on their own). A `kitchen.lock` already there: it runs `update` instead.
3. **The release.** From `--source DIR`, else from the checkout `init.py` sits in, else a shallow clone of the release tag (`--version`, default: the version of the `init.py` you run).
4. **Three questions**, each with a guess from the folder ([below](#the-three-questions)).
5. **The host**, from `--host` or the `origin` remote ([hosts.md](hosts.md)).
6. **The plan.** Every file: `create`, or `exists` (yours is kept and the new version is written next to it as `<name>.kitchen-new`). `--dry-run` stops here and writes nothing.
7. **Writing**, after a yes: `kitchen.yml` from your answers, the framework files, the CI toolchain step when the stack is recognized, and `kitchen.lock`. Nothing is overwritten. Nothing is committed.
8. **Doctor**, then the next steps: merge any `.kitchen-new` copies by hand, fill the `## This project` section of `AGENTS.md`, commit, define the product.

### Flags

| Flag | Meaning |
| --- | --- |
| `install` / `update` / `doctor` | The mode (default `install`). |
| `--dry-run` | Show the plan; write nothing. |
| `--yes` | Answer yes to every question; questions take their guesses. On update, conflicting files keep your version and get a `.kitchen-new` copy. |
| `--tests GLOBS` | Test file globs, comma-separated; repeatable. |
| `--code GLOBS` | Product code globs, comma-separated; repeatable. |
| `--test-command COMMAND` | The command that runs tests and writes JUnit XML to `{report}`. |
| `--host github\|gitlab\|manual` | Override host detection. |
| `--no-claude` | Skip the Claude Code files (`.claude/` and `CLAUDE.md`). |
| `--source DIR` | Install from a local Test Kitchen checkout instead of downloading. |
| `--version vX.Y.Z` | The release to install or update to. |
| `--target DIR` | The project's repository root (default: the current folder). |

### Answering without a terminal

Questions are read from the terminal, even when the script arrives through a pipe (`curl … | python3 -`, where standard input is the script itself). With `--yes`, or without any terminal (CI; an agent's shell may have none), nothing is asked: each question takes its flag or its guess, and a required answer with neither stops the run with exit code 2 and the flag to pass. Without a terminal and without `--yes`, the run stops before writing, because nobody confirmed the plan.

Exit codes: `0` success, `1` a failure (prerequisite, download, or a `FAIL` in `doctor` mode; an install still exits `0` once its files are written, even if the doctor run after it reports a failure), `2` a usage problem (including a missing answer).

### The three questions

1. **Test files**: globs, guessed from top-level `tests/`, `test/`, `__tests__/`, `spec/` folders and from file names such as `*.test.ts`, `*.spec.js`, `test_*.py`, `*_test.go`.
2. **Product code**: globs, guessed from `src/`, `lib/`, `app/`, `pkg/`, `cmd/`, `internal/`, Python package folders, or `**/*.go` for a Go module.
3. **Test command**: guessed from `package.json` (vitest, jest, or `node --test` in the test script), pytest configuration or dependencies, or `go.mod`. The command must contain `{report}`. See [test-runners.md](test-runners.md).

Guesses are shown as defaults; they are never applied without being shown.

### The CI toolchain step

The CI templates contain one step under the line `# TEST-KITCHEN: toolchain setup`, a placeholder for setting up your language and installing dependencies. When the stack is recognized, `init.py` replaces it:

| Stack | Recognized when | GitHub Actions | GitLab CI (image `python:3`) |
| --- | --- | --- | --- |
| Node | `package.json` at the root and no yarn, pnpm, or bun lock file | `actions/setup-node` (`.nvmrc` or `.node-version` if present, else `lts/*`; npm cache when locked) and `npm ci` (`npm install` without a lock file) | installs `nodejs` and `npm` from the image's package manager when missing, then `npm ci` |
| Python | `requirements*.txt`, `pyproject.toml`, `setup.py`, or `setup.cfg`, and no Poetry, uv, or Pipenv lock file | `actions/setup-python` (`.python-version` if present, else `3.x`) and `python3 -m pip install pyyaml …` | `python3 -m pip install pyyaml …` |

The pip line installs the requirement files (`-r requirements.txt`, plus `requirements-dev.txt` and similar when present), or the project itself (`-e .`) when there are none; it adds `pytest` when the test command uses it, and always PyYAML so the scripts keep working in the interpreter the step sets up. A project with both stacks gets both. The marker line then reads `# TEST-KITCHEN: toolchain setup (filled by init.py: …)`. Otherwise the placeholder stays, and doctor warns until you replace it.

## The lock: `kitchen.lock`

JSON (which YAML readers also accept), written by `init.py` and never edited by hand:

```json
{
  "about": "Written by Test Kitchen's init.py; do not edit. …",
  "lock_format": 1,
  "version": "0.1.0",
  "source": "https://github.com/iakanoe/TestKitchen.git@v0.1.0",
  "options": {"host": "github", "no_claude": false, "toolchain": ["python"]},
  "files": {
    "AGENTS.md": "<sha256>",
    "scripts/deliver.py": "<sha256>"
  },
  "side_by_side": ["AGENTS.md"]
}
```

- `source`: where the release came from; a local checkout is recorded as `local checkout (commit <sha>)`, never as a local path.
- `options`: the host the files were installed for, whether `--no-claude` was used, and the stacks the CI step was filled for.
- `files`: every framework file with the sha256 of the content Test Kitchen installed (or offered as `<name>.kitchen-new`). `kitchen.yml` is not listed: it is your configuration.
- `side_by_side`: files whose `.kitchen-new` copy was waiting to be merged when the lock was written.

`update` compares your files with these hashes to tell your edits from the framework's. The Claude Code guard treats the framework scripts listed here as protected.

## Updating

```sh
curl -fsSL https://raw.githubusercontent.com/iakanoe/TestKitchen/v0.2.0/init.py | python3 - update
python3 TestKitchen/init.py update --target path/to/project    # from a newer clone
```

For each framework file:

| Your copy | The new version | Result |
| --- | --- | --- |
| Unchanged since install | Changed | Replaced |
| Edited | Unchanged | Kept; nothing to do |
| Edited | Changed | Conflict: keep yours (the new version is written as `<name>.kitchen-new`), take the new version, or see the diff first. `--yes` keeps yours. |
| Missing | Any | Restored |
| Not installed before, file exists | New in this version | Written as `<name>.kitchen-new` |
| Not installed before | New in this version | Added |
| Installed before | Removed from this version | Listed, never deleted |

It prints the migration notes of every release between the installed version and the new one ([CHANGELOG.md](../CHANGELOG.md)), rewrites the lock, and runs doctor. It never touches `kitchen.yml`. `--host` switches the host's files; `--no-claude` can be added on an update but not removed. `--dry-run` shows the plan without writing.

`AGENTS.md` is meant to be edited (its `## This project` section), so expect a conflict on it whenever a release changes its framework part: take the diff and carry the framework changes into your copy.

## Doctor

```sh
curl -fsSL https://raw.githubusercontent.com/iakanoe/TestKitchen/v0.1.0/init.py | python3 - doctor
# or, from a clone: python3 <clone>/init.py doctor
```

Read-only. A checklist of `PASS`, `WARN`, `FAIL`, and `SKIP` lines, each problem followed by what to do. Exit code 1 when anything fails.

- Python, PyYAML, git, and a git repository.
- `kitchen.lock` readable; every framework file in it present; `.kitchen-new` copies still waiting (warning).
- `kitchen.yml` valid (required keys, known keys, allowed values); each glob matches at least one file (warning, since a new project may have no tests yet); `test_command` contains `{report}`.
- The merge guard registered in `.claude/settings.json` (a PreToolUse hook running `.claude/hooks/guard.py`) and not switched off by `disableAllHooks`; skipped when installed with `--no-claude`.
- The CI file present and its toolchain step filled (warning when not); a warning when `kitchen.yml` or the remote names a different host than the one the CI files were installed for.
- `gh` or `glab` installed and signed in (warning).
- `scripts/backlog_check.py` passes, and every framework script that has a `--self-test` passes it.

If the guard is not registered, put this block back into `.claude/settings.json` (it is the one `template/claude/settings.json` installs):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash|Edit|Write|MultiEdit|NotebookEdit",
        "hooks": [
          {"type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/guard.py\" || exit 2"}
        ]
      }
    ]
  }
}
```

## Installed files

`kitchen.lock` lists exactly what your install wrote. For v0.1.0:

| Path | What it is |
| --- | --- |
| `kitchen.yml` | Configuration (your answers) |
| `kitchen.lock` | Version, options, and installed files with their hashes |
| `AGENTS.md` | Agent entry point; its `## This project` section is yours |
| `CLAUDE.md` | Claude Code entry point (imports `AGENTS.md`); not with `--no-claude` |
| `CONTRIBUTING.md` | The workflow in short |
| `playbooks/deliver.md`, `playbooks/define.md`, `playbooks/review.md` | The processes |
| `scripts/kitchen_lib.py`, `scripts/hosts.py`, `scripts/backlog_check.py`, `scripts/deliver.py` | The scripts |
| `docs/product.md`, `docs/decision-log.md`, `docs/requirements/README.md`, `docs/architecture/README.md` | Definition skeletons |
| `backlog/README.md` | Ticket rules |
| `.claude/skills/deliver/SKILL.md`, `.claude/skills/define/SKILL.md`, `.claude/agents/ticket-reviewer.md`, `.claude/hooks/guard.py`, `.claude/settings.json` | Claude Code files; not with `--no-claude` |
| `.github/workflows/check.yml`, `.github/pull_request_template.md` | GitHub only |
| `.gitlab-ci.yml`, `.gitlab/merge_request_templates/Default.md` | GitLab only |

## Removing Test Kitchen

There is no uninstall command; removal is a normal commit you can review.

1. Delete every path listed under `files` in `kitchen.lock` that you no longer want, then `kitchen.yml` and `kitchen.lock`.
2. If you merged Test Kitchen's hook into an existing `.claude/settings.json`, remove the `PreToolUse` entry that runs `.claude/hooks/guard.py`. If you merged its CI steps into an existing workflow, remove them.
3. Your own content (requirements, decisions, tickets, delivery records in `docs/` and `backlog/`) is yours: keep it as documentation or delete it.
