---
id: US-INST-06
type: story
title: Choose the host
epic: EP-INST
source_reqs: [INST-R08]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a developer installing Test Kitchen, I want the host chosen from my remote or a flag, so that I get the CI and change-request files my host runs and nothing else.

## Acceptance criteria

- AC1: Given `--host github`, `--host gitlab`, or `--host manual`, when an install runs, then that host is used whatever the remote says, and `kitchen.yml` gets an uncommented `host: <host>` line.
- AC2: Given no `--host`, when an install runs, then an `origin` URL containing `github.com` gives github, one containing `gitlab` in any case gives gitlab, and any other URL or no `origin` gives manual, and `kitchen.yml` gets the host as a commented `# host:` line with the reason.
- AC3: Given host github, when files are installed, then the `.github/` files are installed and no GitLab files; given host gitlab, `.gitlab-ci.yml` and the `.gitlab/` files are installed and no `.github/` files.
- AC4: Given host manual, when an install runs, then no CI or change-request template files are installed, and the plan says to pass `--host github` or `--host gitlab` to get them.

## Notes

Observed in `init.py` on 2026-11-25 by `/define adopt`; not yet confirmed by a person. Detection follows the same rule as `scripts/kitchen_lib.py` (comment in `detect_host`); a GitHub Enterprise or self-hosted GitLab URL without those words is manual. Switching host later: US-INST-16.

## Open questions

- None. Behavior recorded as observed; the person confirms it.
