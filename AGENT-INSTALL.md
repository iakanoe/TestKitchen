# Installing Test Kitchen: instructions for an AI agent

You are installing Test Kitchen v0.1.0 into the repository you are working in. Follow these steps in order. The person you work for decides; you prepare, run the installer, and report. Do not commit, push, or edit any file the installer did not create unless the person approves it in step 6.

The installer is `init.py`. Pinned copy:

- one line: `curl -fsSL https://raw.githubusercontent.com/iakanoe/TestKitchen/v0.1.0/init.py | python3 - <mode and flags>`
- or a clone: `git clone --branch v0.1.0 https://github.com/iakanoe/TestKitchen.git <temp dir>` and then `python3 <temp dir>/init.py <mode and flags>`

Your shell has no terminal for the installer to ask on, so always pass `--yes` for a real run; without it the installer stops before writing anything. A missing answer stops it too (exit code 2), and it says which flag to pass.

## 1. Check the folder and the prerequisites

- Work at the repository root (`git rev-parse --show-toplevel`). If the folder is not a git repository, tell the person: the installer will run `git init` there.
- If `git status --porcelain` shows uncommitted changes, tell the person and ask whether to go on; the installer only adds files, but a clean tree makes its changes easy to review.
- Check `python3 --version` (3.9 or later), `python3 -c "import yaml"` (PyYAML), and `git --version`. If PyYAML is missing, tell the person how to install it (`python3 -m pip install --user pyyaml`); do not install packages without their yes.
- If a `kitchen.lock` exists, Test Kitchen is already installed: run `init.py update --dry-run` instead, show the plan, and continue from step 4 with `update`.

## 2. Form your guesses

Look at the repository and guess the three answers. Each needs a reason you can state.

1. **Test files**: globs for test files and their helpers, such as `tests/**`, `**/*.test.ts`, `**/*_test.go`.
2. **Product code**: globs for the code the tests prove, such as `src/**`, `app/**`, `**/*.go`.
3. **Test command**: a shell command, run from the repository root, that runs the test files given in `{files}` (the whole suite when `{files}` is empty) and writes JUnit XML to the path `{report}`. Read the guide's test-runners page (`guide/test-runners.md` in the Test Kitchen repository) for one command per runner. Look at `package.json` scripts and dependencies, `pyproject.toml`, `pytest.ini`, `go.mod`, and the existing test folders.

Also note the host: `git remote get-url origin` on github.com means `github`, a GitLab URL means `gitlab`, anything else (or no remote) means `manual`, which installs no CI files.

Then run a dry run with your guesses and read its plan:

```sh
curl -fsSL https://raw.githubusercontent.com/iakanoe/TestKitchen/v0.1.0/init.py | python3 - --dry-run --yes \
  --tests '<globs>' --code '<globs>' --test-command '<command>'
```

## 3. Ask the person

Ask in one message:

- the three questions, each with your guess and its reason, asking them to confirm or correct it;
- the host, if you are not sure or if it came out `manual` while they use GitHub or GitLab (`--host github|gitlab|manual`);
- whether to skip the Claude Code files (`--no-claude`); the default installs them, and they are what enforces the merge guard in Claude Code.

Show the dry run's plan: which files it creates, which already exist and would get a side-by-side `<name>.kitchen-new` copy, and whether the CI toolchain step was recognized. Wait for the answers. Never invent an answer the person did not give; a guess they have not confirmed is not an answer.

## 4. Install

Run the installer with the confirmed answers:

```sh
curl -fsSL https://raw.githubusercontent.com/iakanoe/TestKitchen/v0.1.0/init.py | python3 - --yes \
  --tests '<globs>' --code '<globs>' --test-command '<command>' [--host <host>] [--no-claude]
```

For an update: `… | python3 - update --yes`. With `--yes`, files edited locally that also changed in the new version are kept, and the new version is written next to them as `<name>.kitchen-new`.

## 5. Check and report

Run `… | python3 - doctor` and report to the person:

- the files created, and every `<name>.kitchen-new` they need to merge into their own file by hand (then delete the copy);
- every doctor line marked `FAIL` or `WARN`, with the fix doctor printed;
- whether the CI toolchain step was filled or still needs their language setup;
- that nothing was committed: they review and commit the new files themselves, or ask you to.

## 6. Optional: draft the project section and a first epic

Offer, do not do:

- to draft the `## This project` section of `AGENTS.md` (what the project is, its stack, how to run it locally, anything an agent must know), from what you read in the repository;
- to run the definition workflow (`/define` in Claude Code, or `playbooks/define.md`): mode `adopt` when the repository already has code (it maps existing behavior to requirements marked `(observed in code)` and `done` stories marked `adopted: true`), mode `new` otherwise (it starts by asking the person to describe the product).

Show exactly what you would write and write it only after the person says yes.
