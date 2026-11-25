---
id: US-HOST-02
type: story
title: List the branches open change requests and pushes claim
epic: EP-HOST
source_reqs: [HOST-R02, HOST-R03, HOST-R04, HOST-R05]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As an agent picking the next ticket, I want the branches that open change requests and pushes already hold, so that I never start a ticket someone else has claimed.

## Acceptance criteria

- AC1: Given the GitHub host, when the open branches are listed, then the result is the head branches that `gh pr list --state open --json headRefName --limit 1000` returns, plus every branch pushed to origin.
- AC2: Given the GitLab host, when the open branches are listed, then `glab mr list --output json --per-page 100 --page <n>` is read from page 1 until a page holds fewer than 100 entries, and the result is every source branch on those pages plus every branch pushed to origin.
- AC3: Given the GitLab host and a CLI that keeps returning full pages, when the open branches are listed, then reading stops after page 50.
- AC4: Given the manual host, when the open branches are listed, then the result is the branches pushed to origin, and no host CLI is called.
- AC5: Given a repository with no `origin` remote, when the pushed branches are listed, then the result is empty.
- AC6: Given an `origin` remote that cannot be listed, when the pushed branches are listed, then a HostError is raised instead of returning a guess.

## Notes

- Pushed branches come from `git ls-remote --heads origin`, so a branch pushed without a change request still claims its ticket.
- AC2 and AC3 rely on recorded `glab` output only: the GitLab adapter has never run against a real `glab` or GitLab project (SPK-HOST-01).
- Above 1000 open pull requests (GitHub) or 5000 open merge requests (GitLab), the extra change requests are left out without a warning; their branches still count when they live on origin.
- Unreadable (non-JSON) list output escapes as a parse error rather than a HostError: DEC-HOST-01.
- `deliver.py next` and `status` use this list; how they react to it belongs to the delivery epic.

## Open questions

- None. Adopted behavior, recorded as it is; the open points are tracked in the epic's decision and spike tickets.
