---
id: US-GRD-06
type: story
title: Limit host CLI and API calls
epic: EP-GRD
source_reqs: [GRD-R13, GRD-R14, GRD-R15]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a project owner, I want `gh` and `glab` to run freely only for reads and the workflow's steps, with host writes put before a person and host-side merges and branch moves refused, so that the host CLIs open no path around the push and merge rules.

## Acceptance criteria

- AC1: Given either host configured, when an agent runs a gh or glab read or workflow step (`gh pr view`/`list`/`checks`/`create`/`edit`/`ready`, `gh run list`/`watch`, `glab mr view`/`list`/`create`/`update`/`note`/`diff`/`checkout`, `glab ci status`/`list`/`trace`, a GET `gh api` or `glab api` call, `--version`), then the guard lets it through.
- AC2: Given a built-in gh or glab command outside those (`gh repo sync` with no repository, `gh workflow run`, `gh config set`, `gh alias set` with a non-merge expansion, `glab mr approve`/`close`/`rebase`, `glab ci run`/`retry`/`view`, `glab variable set`, `glab release create`, `glab repo mirror` pulling, a `-R` option before the command group), when it runs, then the guard asks a person.
- AC3: Given a gh or glab top-level command that is not built in (an alias or extension such as `gh m 7`), when it runs, then the guard denies it.
- AC4: Given a `gh api` or `glab api` call that may write (`-X`/`--method` other than GET in any case or attached form, `-f`/`-F`/`--field`/`--raw-field`/`--form`/`--input`, clustered short options such as `-fbase=main`, or graphql), when its endpoint does not merge or move a branch, then the guard asks a person.
- AC5: Given a host API call that may write to a merge endpoint, a git ref, contents, repository commits, files, or branches, auto-merge, or rebase, or a graphql `mergePullRequest` or `enablePullRequestAutoMerge` mutation, or `gh repo sync` naming a repository or with `--force`, or a `glab repo mirror` pushing, when it runs, then the guard denies it.
- AC6: Given `glab mr create` or `glab mr new` with `--push`, `--push=true`, `--fill`, `-f` in any short-option cluster (unless `--push=false` is given), or `--auto-merge`, or `glab mr accept`, when it runs, then the guard denies it; `glab mr create --create-source-branch` asks.

## Notes

- Adopted from `template/claude/hooks/guard.py` (`guard_host`, `api_writes`, `guard_glab_create`, `GH_FREE`, `GLAB_FREE`, `KNOWN_GROUPS`, `MERGE_API`). The glab rules were checked against the glab documentation by the builder (decision-log entry "Guard choices made while building v0.1"). Behavior observed in the code and its tests on 2026-11-25, not yet confirmed by a person.
- `docs/spec-v0.1.md` section 6 lists the allowed CLI commands per host; the code allows both CLIs' reads and steps whatever host is configured, because a machine may have both. The merge rule still accepts only the configured host's command.
- An open decision in this epic asks whether a graphql `deleteRef` mutation, which today only asks, should be denied like the REST ref writes.
- Calls that place `-R` before `api` are not read as API calls; they ask as an unknown command group instead.

## Open questions

- None. The behavior is recorded as observed; the person confirms it when walking through the requirements.
