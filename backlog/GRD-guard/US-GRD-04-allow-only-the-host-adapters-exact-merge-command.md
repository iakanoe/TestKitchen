---
id: US-GRD-04
type: story
title: Allow only the host adapter's exact merge command
epic: EP-GRD
source_reqs: [GRD-R09]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a project owner, I want the only agent merge to be word for word the command the host adapter prints, alone in its call, so that no merge bypasses, defers, or rewrites what the gates checked.

## Acceptance criteria

- AC1: Given a GitHub project, when an agent runs `gh pr merge <number> --merge --match-head-commit <40-hex sha>` alone (also with the number or sha in plain quotes), then the guard passes it on to the merge gate; given a GitLab project, the same holds for `glab mr merge <number> --sha <40-hex sha> --auto-merge=false --yes`.
- AC2: Given a merge that differs from that command (`--admin`, `--auto`, `--squash`, `--rebase`, `-s`, `--delete-branch`, `--remove-source-branch`, an `=` form, reordered options, a missing pin, a branch name, a URL, `-R` or `--repo`, a short or uppercase sha, a number with leading zeros), when it runs, then the guard denies it without running the gate or calling the host, and the message shows the exact expected command or says merges never bypass the checks.
- AC3: Given a merge in the same call as anything else (a commit, a push, `; true`, a background `&`), when it runs, then the guard denies it with a message to run the merge alone in its call.
- AC4: Given a project on one host, when an agent runs the other host's merge command, then the guard denies it, naming the configured host and the only merge shape with placeholders.

## Notes

- Adopted from `template/claude/hooks/guard.py` (`guard_plain`, `guard_merge`, `BYPASS`). The expected words come from `scripts/hosts.py` `merge_argv`, so a new host adapter needs no guard change. Behavior observed in the code and its tests on 2026-11-25, not yet confirmed by a person.
- Comparing word for word (no `=` forms, no extra options) is deliberate (decision-log entry "Guard choices made while building v0.1").
- A trailing `#` comment of plain words after the merge command is accepted.

## Open questions

- None. The behavior is recorded as observed; the person confirms it when walking through the requirements.
