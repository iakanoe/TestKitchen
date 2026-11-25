# Configuration: `kitchen.yml`

`kitchen.yml` sits at the repository root. Three keys are required; everything else is optional or a convention ([concepts.md](concepts.md)). `init.py` writes the file from your three answers, with every optional key present as a comment.

```yaml
tests: ["tests/**", "**/*.test.ts"]
code: ["src/**"]
test_command: "python3 -m pytest {files} --junitxml={report}"
```

Unknown keys are errors, so a typo never silently turns a setting off. Each invalid value gives one clear message.

## Required keys

### `tests`

Globs of test files and their helpers (fixtures, conftest files, test utilities). Test files are what `gate red` runs, what the freeze commit may contain, and what "Test changes" must list after the freeze.

### `code`

Globs of product code: the files the tests prove. No product code may change at or before the freeze, and a change to product code after the last review needs another review. A file matching both `tests` and `code` counts as a test, so `code: ["**/*.go"]` with `tests: ["**/*_test.go"]` works.

### `test_command`

A shell command, run from the repository root, that runs tests and writes JUnit XML. Placeholders:

| Placeholder | Becomes |
| --- | --- |
| `{files}` | The test files to run: shell-quoted, relative to the repository root, separated by spaces. Empty for a full run, so the command must run the whole suite when given no files. |
| `{files:<dir>}` | The same paths with the `<dir>/` prefix removed, for runners started inside a subfolder: `cd app && npx vitest run {files:app} …`. |
| `{report}` | The absolute path of the JUnit XML file the command must write (a temporary file outside the repository). |

`{report}` is required: JUnit XML is the one result format Test Kitchen reads. `{files}` is optional; a command without it always runs the whole suite, which is correct but slower. [test-runners.md](test-runners.md) has a command for each common runner.

## Optional keys

| Key | Default | Meaning |
| --- | --- | --- |
| `check_command` | the full test run | Replaces the full test run in `deliver.py check` (after the backlog check and the self-tests). Use it to add lint and type checks; it must run the tests too. Example: `"npm run lint && npm run typecheck && npx vitest run"`. |
| `verify` | none | Plain words saying how to try a change after it ships, read at the delivery's verify step. Without it, deliveries report "not verified after deploy". Example: `"Open the staging site and try the new behavior."` |
| `host` | detected | `github`, `gitlab`, or `manual`. When absent, detected from the `origin` remote: a github.com URL means `github`, a URL containing "gitlab" means `gitlab`, anything else `manual`. Set it for GitHub Enterprise or a self-hosted GitLab whose URL hides it. See [hosts.md](hosts.md). |
| `autonomy` | `merge` | `merge`: the agent merges on green. `pr`: the agent stops at a ready change request and a person merges. `supervised`: as `pr`, and a person also approves the plan and the tests (`Plan approved by:` and `Tests approved by:` lines in the plan). |
| `split_threshold` | `6` | Refinement flags stories with more live criteria than this, suggesting a split. |
| `self_contained_tickets` | `false` | When `true`, ticket bodies may not link or name repository files, so a ticket reads on its own when copied into another tracker or handed to an agent without the repository. |
| `releases` | none | Release slices in order, such as `[v1, v2, later]`. Turns slice rules on: every story, task, and spike needs a `release` from the list, `next` picks earlier slices first, and no unfinished blocker may sit in a later slice than the ticket it blocks. `/define slice` writes it. |
| `ignore` | none | Globs excluded from every scan: tests, code, tags, TODOs, coverage. Example: `["examples/**", "**/fixtures/**"]`. |

## Globs

Paths are relative to the repository root and use `/`.

- `**` matches any number of path segments, including none: `**/*.test.ts` matches `a.test.ts` and `src/a/b.test.ts`.
- `*` matches anything except `/`: `src/*.py` matches `src/a.py` but not `src/a/b.py`.
- `?` matches one character except `/`.

There is no brace expansion; list each pattern instead.

## Examples per stack

Each file in [examples/](../examples/) is a complete `kitchen.yml` with comments:

| Example | Stack |
| --- | --- |
| [python-pytest](../examples/python-pytest/kitchen.yml) | Python with pytest |
| [node-vitest](../examples/node-vitest/kitchen.yml) | TypeScript with Vitest |
| [node-test](../examples/node-test/kitchen.yml) | JavaScript with Node's built-in runner |
| [go](../examples/go/kitchen.yml) | Go with gotestsum |
| [monorepo](../examples/monorepo/kitchen.yml) | An application in `app/`, run with `{files:app}` |

## Conventions that need no configuration

The paths in [concepts.md](concepts.md) (`docs/`, `backlog/`, `playbooks/`, `scripts/`), the ID formats, the test tags, the branch names, the freeze commit message, and the change-request sections are fixed. The default branch is detected from `origin/HEAD`, else `main`, else `master`. The CI job that gates merging is always named `check`.
