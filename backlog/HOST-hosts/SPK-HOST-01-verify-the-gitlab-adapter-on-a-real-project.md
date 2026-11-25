---
id: SPK-HOST-01
type: spike
title: Verify the GitLab adapter on a real GitLab project
epic: EP-HOST
source_reqs: [HOST-R05, HOST-R10, HOST-R11, HOST-R12, HOST-R13, HOST-R16, HOST-R21, HOST-R22]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: draft
---

## Goal

Find out whether the GitLab adapter and the GitLab CI template work end to end against a real `glab` and a real GitLab project: listing open merge requests, reading a merge request with its head pipeline jobs, the merge command, and the `check` job in merge request and branch pipelines.

## Context

- The glab commands and flags were checked against the official glab and GitLab documentation (cited in `template/scripts/hosts.py`), but they were never run: glab was not installed on the build machine (decision log, "Script choices made while building v0.1").
- The tests use a fake `glab` that answers from recorded JSON written from the documentation, so they prove the parsing, not the real output shape.
- Points only a real run settles: whether `glab mr list --output json --per-page --page` pages as assumed; whether `glab mr view --output json` includes `head_pipeline` with `id` and `sha`, `detailed_merge_status`, and `draft`; whether `glab api --paginate projects/:fullpath/pipelines/<id>/jobs` resolves the placeholder and prints pages the parser reads; whether `glab mr merge --sha --auto-merge=false --yes` merges at once and refuses a moved head; and whether the CI template's workflow rules, draft detection, record checks, and `gate pr --from-record` behave as written.

## Done when

- Each command above has been run against a throwaway GitLab project, and its real output or behavior is recorded under Findings, with the glab and GitLab versions used.
- Every difference from what the adapter or the CI template assumes is filed as a follow-up ticket, or the findings say there is none.

## Findings
