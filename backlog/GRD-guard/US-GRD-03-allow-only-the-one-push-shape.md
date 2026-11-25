---
id: US-GRD-03
type: story
title: Allow only the one push shape
epic: EP-GRD
source_reqs: [GRD-R06, GRD-R07, GRD-R08]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a project owner, I want an agent to push only its own branch to origin by name, from this checkout, so that nothing lands on the default branch or anywhere else without the merge path.

## Acceptance criteria

- AC1: Given an existing local branch other than the default branch, when an agent runs `git push origin <branch>`, `git push -u origin <branch>`, or `git push --set-upstream origin <branch>` from the project root or a subfolder, then the guard lets it through.
- AC2: Given a push that names the default branch (in any case, including a default branch detected from `origin/HEAD` such as `trunk`), a refspec, a wildcard, `HEAD`, a `refs/`, `heads/`, or `origin/` prefix, a branch that does not exist locally, another remote, several branches, no branch, `--all`, `--mirror`, or another option such as `--no-verify`, when it runs, then the guard denies it, and a push of the default branch names that branch in the message.
- AC3: Given a push run from another checkout (another repository, `git -C <folder>`, or a `cd` elsewhere first), when it runs, then the guard denies it with a message to push from this project's checkout.
- AC4: Given `remote.origin.push` or `remote.origin.mirror` is set in the project's git configuration, when any push runs, then the guard denies it; once the setting is removed, the same push goes through.
- AC5: Given a push of an allowed branch that is forced (`-f`, `--force`, `--force-with-lease`, or `+<branch>`), when it runs, then the guard asks a person; a forced push of the default branch is denied.

## Notes

- Adopted from `template/claude/hooks/guard.py` (`guard_push`, `same_checkout`). Behavior observed in the code and its tests on 2026-11-25, not yet confirmed by a person.
- The push options `-n`/`--dry-run`, `-q`/`--quiet`, and `-v`/`--verbose` are also accepted.
- Force pushes keep asking in sandbox mode; that is recorded with the sandbox behavior of this epic.

## Open questions

- None. The behavior is recorded as observed; the person confirms it when walking through the requirements.
