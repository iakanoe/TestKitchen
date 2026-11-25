---
id: US-HOST-09
type: story
title: Run the check job on GitHub
epic: EP-HOST
source_reqs: [HOST-R18, HOST-R19, HOST-R20]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a project on GitHub, I want an installed workflow with a job named `check` that runs the workflow checks on every pull request and default-branch push, so that the merge gate has a passing `check` on the head to rely on.

## Acceptance criteria

- AC1: Given the installed GitHub workflow, when a pull request is opened, synchronized, reopened, edited, or marked ready for review, or a commit is pushed to `main` or `master`, then a job named `check` runs.
- AC2: Given the `check` job, when it starts, then it has read-only access to repository contents and checks out the full git history.
- AC3: Given the `check` job, when it runs, then it sets up Python with PyYAML, reaches the step under the `# TEST-KITCHEN: toolchain setup` marker line, which until replaced only prints a warning that the toolchain setup is not filled in, and then runs `python3 scripts/deliver.py check`.
- AC4: Given a pull request event, when the `check` job runs, then the live description is passed through an environment variable, written to a file, and checked with `python3 scripts/backlog_check.py --pr-body=<file>`.
- AC5: Given a pull request that is not a draft, when the `check` job runs, then it also runs `python3 scripts/deliver.py gate pr` with that description file, the head branch, the base sha, and the head sha.
- AC6: Given a push event, when the `check` job runs, then neither description step runs.

## Notes

- `.github/pull_request_template.md` is covered by the story on description templates.
- The installer copies this file and fills the toolchain step when it recognizes the stack; that belongs to the installer epic.
- This repository's own root `.github/workflows/check.yml` is an installed copy with the toolchain step filled, so it differs from the template.

## Open questions

- None. Adopted behavior, recorded as it is; nothing is open for this story.
