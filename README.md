# Test Kitchen

*Let the agents cook (then taste the food) AKA vibecoding for devs with trust issues.*

Test Kitchen is a small framework you install into a repository so AI agents can define and deliver your project under guardrails. Requirements and tickets live in the repository as plain markdown. Tests are written first, seen failing, and then frozen. A reviewer with fresh context checks the plan, the tests, and the final diff. Every gap and decision found along the way is written down. Nothing merges unless deterministic gates pass. It works with any language, any test runner that writes JUnit XML, GitHub, GitLab, or no host at all, and any agent that can read markdown and run a script.

## Why

An agent can write a lot of plausible code quickly. The hard part is trusting it. Did it build what was asked, or what it guessed? Do the tests prove the requirement, or were they written to pass the code? Did it quietly decide something a person should have decided? Will anyone know why the code looks the way it does in six months?

Test Kitchen answers those questions with records and scripts instead of hope. The requirement is a numbered line in `docs/`. The ticket cites it and lists acceptance criteria. Each criterion has a test that names it and was seen failing before the code existed. The change request carries the plan, the review, and every decision, and it is committed as a record. The merge happens only when scripts, not the agent's own judgment, say the gates pass. [guide/why.md](guide/why.md) explains each rule.

## What you get

- **A definition workflow** (`/define`): turns a rough description, or existing code, into a product doc, requirement lines, epics, and tickets with acceptance criteria, asking about three questions at a time and turning what nobody can answer yet into decision tickets.
- **A delivery workflow** (`/deliver`): picks the next ready ticket deterministically, plans from its criteria, writes failing tagged tests, implements, checks, gets a fresh-context review, records every gap and decision, opens the change request, and merges only on green.
- **Scripts that hold the facts**: `scripts/backlog_check.py` validates tickets, requirements, and coverage; `scripts/deliver.py` picks work and runs the gates (`gate red`, `gate pr`, `gate merge`, `check`), prints a status screen and release notes.
- **A merge guard for Claude Code**: a hook that refuses any merge the gate has not passed, and any push to the default branch.
- **CI for GitHub or GitLab**: a `check` job that runs the same checks on every change request.
- **Plain-markdown playbooks** that any agent can follow, and an installer that never overwrites your files.

## Install

Run it from the root of the project's git repository. All three paths install the same thing and ask the same three questions: which files are tests, which files are product code, and which command runs the tests and writes JUnit XML. The installer guesses the answers from the folder, shows a plan, and never overwrites a file: when one already exists, the new version is written next to it as `<name>.kitchen-new`.

**1. One line** (pinned to a release):

```sh
curl -fsSL https://raw.githubusercontent.com/iakanoe/TestKitchen/v0.1.0/init.py | python3 -
```

Add `--dry-run` after the `-` to only see the plan: `… | python3 - --dry-run`.

**2. Clone, then run:**

```sh
git clone --branch v0.1.0 https://github.com/iakanoe/TestKitchen.git
python3 TestKitchen/init.py --target path/to/your/project
```

**3. Ask your agent.** Paste this into your agent's chat, in the project's repository:

```text
Install Test Kitchen v0.1.0 in this repository by following
https://github.com/iakanoe/TestKitchen/blob/v0.1.0/AGENT-INSTALL.md
exactly. Ask me the questions it lists before writing anything, and do not commit.
```

`init.py` is not copied into your project. To check the install any time, run `curl -fsSL https://raw.githubusercontent.com/iakanoe/TestKitchen/v0.1.0/init.py | python3 - doctor` from the project folder (or `python3 <clone>/init.py doctor` from a clone). [guide/install.md](guide/install.md) covers every flag, `update`, `doctor`, the list of installed files, and how to remove Test Kitchen by hand.

## Quick tour

```text
/define                          describe the product; get requirements, epics, and tickets
/deliver next                    take the next ready ticket through to a merged change request
python3 scripts/deliver.py status    one screen: ready, in progress, blocked, open decisions, gaps
```

In agents other than Claude Code, ask the agent to "follow `playbooks/define.md`" or "follow `playbooks/deliver.md` for the next ticket". [guide/workflow.md](guide/workflow.md) walks through a day with Test Kitchen.

## Works with any agent

The process lives in plain markdown (`AGENTS.md`, `CONTRIBUTING.md`, `playbooks/`) and Python scripts, so any agent that reads files and runs commands can follow it: Claude Code, Codex, Cursor, and others.

**Claude Code is recommended:** Test Kitchen was developed and tested there, and it is the only agent where the merge guard is enforced. Elsewhere the gates still run in CI, but nothing stops an agent from merging on a failing check except its own discipline; [guide/agents.md](guide/agents.md) explains how to compensate.

## Requirements

- `git` and Python 3.9 or later with PyYAML (`python3 -m pip install --user pyyaml`).
- A test runner that writes JUnit XML ([guide/test-runners.md](guide/test-runners.md) covers pytest, vitest, jest, node:test, Go, and JUnit 5).
- For GitHub, the `gh` CLI signed in; for GitLab, the `glab` CLI signed in. Without a host, a person merges by hand.

## Documentation

| Page | Covers |
| --- | --- |
| [guide/concepts.md](guide/concepts.md) | Tickets, criteria, tags, the freeze, reviews, records, gates |
| [guide/configuration.md](guide/configuration.md) | Every `kitchen.yml` key, with examples per stack |
| [guide/workflow.md](guide/workflow.md) | A day with Test Kitchen: define, deliver, status, release notes |
| [guide/define.md](guide/define.md) | The definition modes, and what "fully defined" means |
| [guide/hosts.md](guide/hosts.md) | GitHub, GitLab, and manual adapters; adding a host |
| [guide/agents.md](guide/agents.md) | Using it from Claude Code, Codex, Cursor, and others |
| [guide/test-runners.md](guide/test-runners.md) | JUnit output and tag forms per test runner |
| [guide/install.md](guide/install.md) | Install, update, doctor, the installed files, removing it |
| [guide/why.md](guide/why.md) | Why each rule exists |

[examples/](examples/) holds `kitchen.yml` files for several stacks. [CHANGELOG.md](CHANGELOG.md) lists each release and its migration notes.

## License

Apache License 2.0. See [LICENSE](LICENSE).
