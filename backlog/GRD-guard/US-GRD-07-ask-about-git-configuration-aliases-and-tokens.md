---
id: US-GRD-07
type: story
title: Ask about git configuration, aliases, and tokens
epic: EP-GRD
source_reqs: [GRD-R16, GRD-R17, GRD-R18]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a project owner, I want changes to git configuration, git aliases the guard cannot read, and host tokens in commands to go before a person, so that settings that run programs or redirect pushes are never changed or used silently.

## Acceptance criteria

- AC1: Given a `git config` call that writes (setting a key, `--global`, values that contain the words get or list, `git -C <folder> config …`, a quoted `"git"`), when it runs, then the guard asks a person; `git config --get-regexp`, `--get`, `--list`, and the `get` and `list` subcommands go through.
- AC2: Given `git -c <key>=<value>`, `git --config-env`, or a `GIT_*` variable assignment before git, in a call that names no push or merge, when it runs, then the guard asks a person.
- AC3: Given a git alias that pushes, merges, or runs a shell, when an agent runs it by its name in any case (`git ship`, `git Ship`, `git SHIP`), then the guard denies it; a name that is a built-in command spelled exactly runs the built-in (`git log`), while the same name in another case runs the alias (`git Log`).
- AC4: Given a git alias that does not push, merge, or run a shell, when an agent runs it, then the guard asks a person.
- AC5: Given a command that names a host token variable (such as `GH_TOKEN`, `GITHUB_TOKEN`, `GITLAB_TOKEN`) or a `PRIVATE-TOKEN` header, when it runs, then the guard asks a person.
- AC6: Given a command that names the `.git` folder, `~/.gitconfig`, or the `git`, `gh`, or `glab-cli` folders under `~/.config`, even only to read (`cd .git && ls`, `cat ~/.config/git/config`), when it runs, then the guard asks a person; names that only start with `.git` (`.gitignore`, `.github/`, `.gitlab-ci.yml`) do not.

## Notes

- Adopted from `template/claude/hooks/guard.py` (`guard_git`, `git_aliases`, `GIT_BUILTINS`, `ASK_COMMANDS`). Aliases are read with `git config --get-regexp` from the call's folder, so the person's global aliases count. Behavior observed in the code and its tests on 2026-11-25, not yet confirmed by a person.
- In a call that names a push or a merge, `git -c` and other options before the subcommand are denied by the plain-command rule rather than asked.
- Any other word of a git command that matches an alias name also asks.
- An open decision in this epic asks whether a file argument named `config` in any git command (`git add config`, `git diff -- config`) should keep asking as a git setting change.

## Open questions

- None. The behavior is recorded as observed; the person confirms it when walking through the requirements.
