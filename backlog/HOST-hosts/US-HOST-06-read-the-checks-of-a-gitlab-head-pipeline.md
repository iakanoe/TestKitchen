---
id: US-HOST-06
type: story
title: Read the checks of a GitLab head pipeline
epic: EP-HOST
source_reqs: [HOST-R12, HOST-R13]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As the merge gate, I want the jobs of a merge request's head pipeline as checks, counted only when they ran on the head commit, so that nothing merges on a pipeline that tested other code.

## Acceptance criteria

- AC1: Given a head pipeline with an id that ran on the head commit, when the merge request is read, then its jobs are read with `glab api --paginate projects/:fullpath/pipelines/<id>/jobs`, across every page returned, and for each job name the job with the highest id is its check.
- AC2: Given jobs of each status, when the merge request is read, then success passes, failed fails, canceled or canceling fails, skipped is skipped, manual is pending, and any other status (such as running, pending, created, waiting_for_resource, or scheduled) is pending.
- AC3: Given a failed job or a manual job that is allowed to fail, when the merge request is read, then its check is skipped.
- AC4: Given a head pipeline that ran on another commit than the head (a merged results pipeline included), when the merge request is read, then its jobs do not count and the only check is a pending one naming the pipeline id and the first 8 characters of its commit.
- AC5: Given a merge request with no head pipeline, when it is read, then it has no checks and no jobs call is made.

## Notes

- Merged results pipelines are not supported in this version (decision log, "Required host settings"): AC4 makes the merge gate wait on them instead of trusting them.
- The jobs API leaves retried jobs out by default, per the GitLab documentation cited in `template/scripts/hosts.py`; AC1's highest-id rule also covers them if they appear.
- Never run against a real `glab` or GitLab project: the tests answer from recorded JSON. SPK-HOST-01 verifies the jobs call, the `:fullpath` placeholder, and the page format end to end.

## Open questions

- None. Adopted behavior, recorded as it is; verification on a real GitLab project is tracked in the epic's spike.
