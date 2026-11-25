---
id: US-CONF-06
type: story
title: Find the default branch
epic: EP-CONF
source_reqs: [CONF-R10]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a project maintainer, I want the default branch found without any setting, so that the gates compare against the branch the project really merges into.

## Acceptance criteria

- AC1: Given `origin/HEAD` points to a branch, when the default branch is looked up, then it is that branch.
- AC2: Given no `origin/HEAD` and a `main` branch that exists on `origin` or locally, when the default branch is looked up, then it is `main`.
- AC3: Given no `origin/HEAD`, no `main`, and a `master` branch that exists on `origin` or locally, when the default branch is looked up, then it is `master`.
- AC4: Given no `origin/HEAD`, no `main`, and no `master`, when the default branch is looked up, then it is `main`.

## Notes

`guide/configuration.md` states the order as `origin/HEAD`, else `main`, else `master`; the code also accepts local branches of those names.

## Open questions

- None. Adopted behavior, recorded as the code does it now; a person confirms the requirements.
