---
id: US-HOST-10
type: story
title: Run the check job on GitLab
epic: EP-HOST
source_reqs: [HOST-R19, HOST-R21, HOST-R22]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a project on GitLab, I want an installed pipeline with a job named `check` that runs the workflow checks once per push, reading the description from the committed delivery record, so that the merge gate has a passing `check` in the head pipeline to rely on.

## Acceptance criteria

- AC1: Given the installed GitLab pipeline, when a commit is pushed to a branch with an open merge request, then only a merge request pipeline runs; when the branch has no open merge request, then a branch pipeline runs.
- AC2: Given the pipeline, when the `check` job runs, then it uses the `python:3` image with a full clone (`GIT_DEPTH: "0"`), installs PyYAML, reaches the line under the `# TEST-KITCHEN: toolchain setup` marker line, which until replaced only prints a warning that the toolchain setup is not filled in, and then runs `python3 scripts/deliver.py check`.
- AC3: Given a merge request pipeline for a draft (`CI_MERGE_REQUEST_DRAFT` is true, or the title starts with `Draft:`, `[Draft]`, or `(Draft)`), when the `check` job runs, then it prints that the description checks and the delivery gate run once the merge request is ready, and runs neither.
- AC4: Given a merge request pipeline for a merge request that is not a draft, when the `check` job runs, then `python3 scripts/backlog_check.py --pr-body=<record>` runs on every delivery record the branch adds or changes, the job fails on the first record that fails, and a message says so when no record changed.
- AC5: Given a merge request pipeline for a merge request that is not a draft, when the record checks pass, then `python3 scripts/deliver.py gate pr --from-record` runs with the source branch, the diff base sha, and the head sha (the source branch sha when GitLab sets it, else the commit sha), and its failure fails the job.

## Notes

- GitLab CI cannot rely on the live description: its variable is cut at 2700 characters and editing the description starts no pipeline, so CI reads the committed record and the merge gate compares it with the live description (decision log, "Process-doc choices made while building v0.1").
- GitLab starts no pipeline when a draft is marked ready, so the playbook marks it ready before the final push.
- Never run on a real GitLab project: SPK-HOST-01 verifies the workflow rules, draft detection, record checks, and `gate pr --from-record` end to end.
- `.gitlab/merge_request_templates/Default.md` is covered by the story on description templates; the installer fills the toolchain line (installer epic).

## Open questions

- None. Adopted behavior, recorded as it is; verification on a real GitLab project is tracked in the epic's spike.
