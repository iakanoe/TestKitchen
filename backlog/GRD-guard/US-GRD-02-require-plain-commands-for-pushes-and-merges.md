---
id: US-GRD-02
type: story
title: Require plain commands for pushes and merges
epic: EP-GRD
source_reqs: [GRD-R04, GRD-R05, GRD-R12]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a project owner, I want every call that names a push or a merge to be plain shell built only from the workflow's programs, so that what the guard checks is exactly what the shell runs.

## Acceptance criteria

- AC1: Given a call that names a push or a merge, when it holds a character outside the plain set (`$`, a redirect, a subshell or group, braces, `~`, a background `&`, `|&`, a control character such as a carriage return), an unterminated quote, `$`, a backtick, or a backslash inside double quotes, or a comment with anything but plain words, then the guard denies it and says to run merges and pushes as plain commands.
- AC2: Given an unquoted bare `push` or `merge` word in a command whose program is outside the workflow list (`make push`, `pytest -k merge`), when it runs, then the guard denies it; the same word quoted (`pytest -k "merge"`), as a path part (`npx vitest run tests/push.test.ts`, `sed -n 1,40p src/merge.py`), or in an allowed reader (`rg -n push src/`, `grep -rn push playbooks/`) goes through.
- AC3: Given a call that names a push or a merge, when it also runs a program outside the workflow list (a shell, a wrapper such as `env` or `timeout`, an interpreter, `rg --pre`, `sort`), a git subcommand or option outside the list (`git -C`, `git merge -s`, `git log --output`), or a `git fetch` or `git pull` with another source or an option such as `--upload-pack`, then the guard denies it.
- AC4: Given the workflow's own command blocks (committing and pushing a branch, opening a draft change request with `gh pr create` or `glab mr create`, fetching and merging `origin/<default>`, writing the record and running `backlog_check.py` and `deliver.py gate pr` before the push, watching checks), when they run, then they go through.
- AC5: Given a git, gh, or glab command whose program or subcommand is built at run time (decoded `$'…'`, an empty `$()` or backtick splice, `${…}`, a backslash, a program named by a variable or `$(…)`), when it runs, then the guard denies it; expansions in arguments after the subcommand, such as a commit message from `$(cat <<'EOF' … EOF)` that names no push or merge, go through.
- AC6: Given a push or a merge inside `$(…)`, backticks, `sh -c` or another shell's `-c`, `eval`, `xargs`, `find -exec`, text piped or fed by a heredoc or here-string to a shell, a function body, or a `python3 -c` one-liner, when it runs, then the guard denies it; a heredoc body read by `cat` or `git commit -F -` is data and goes through.

## Notes

- Adopted from `template/claude/hooks/guard.py` (`needs_plain`, `plain_commands`, `guard_plain`, `guard_fetch`, `lex`, `analyze`, `expand`, `guard_dynamic`). Behavior observed in the code and its tests on 2026-11-25, not yet confirmed by a person.
- That an unquoted bare `push` or `merge` word triggers the strict checks is deliberate (decision-log entry "Guard hardening after the adversarial review"). A git option that holds the word, such as `git log --grep=merge`, is refused for the same reason.
- `python3 scripts/deliver.py` and `scripts/backlog_check.py` are accepted only by that relative path (or `../scripts/`); `./scripts/…` or an absolute path in a call that names a push or a merge is refused.

## Open questions

- None. The behavior is recorded as observed; the person confirms it when walking through the requirements.
