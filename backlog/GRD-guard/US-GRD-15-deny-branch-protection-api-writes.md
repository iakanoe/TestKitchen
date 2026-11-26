---
id: US-GRD-15
type: story
title: Deny branch-protection API writes
epic: EP-GRD
source_reqs: [GRD-R35]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: ready
refined: 2026-11-26
---

As a project owner, I want host API calls that change branch protection refused, so that sandbox mode cannot weaken the protection that holds against everything else.

## Acceptance criteria

- AC1: Given a `gh api` call that may write to `repos/{owner}/{repo}/branches/{branch}/protection` or a path under it (such as `…/protection/required_status_checks` or `…/protection/enforce_admins`), when the guard checks it, then it is denied.
- AC2: Given a `gh api` call that may write to `repos/{owner}/{repo}/rulesets` or a path under it (such as `…/rulesets/42`), when the guard checks it, then it is denied.
- AC3: Given a `gh api graphql` call with the `createBranchProtectionRule`, `updateBranchProtectionRule`, `deleteBranchProtectionRule`, `createRepositoryRuleset`, `updateRepositoryRuleset`, or `deleteRepositoryRuleset` mutation, when the guard checks it, then it is denied.
- AC4: Given a `glab api` call that may write to `projects/:id/protected_branches` or a path under it (such as `projects/:id/protected_branches/main`), when the guard checks it, then it is denied.
- AC5: Given any call of AC1 to AC4 with `KITCHEN_GUARD_SANDBOX=1`, when the guard checks it, then it is still denied.
- AC6: Given any address of AC1 to AC4 written in another spelling, when the guard checks it, then it is denied: with a leading `/`, as a full `https://api.github.com/…` URL, with a query string, with a trailing `/`, with a URL-encoded branch name, and on GitLab with a numeric project id or a URL-encoded path in place of `:id` or `:fullpath`.

## Notes

- Implements DEC-GRD-04, option (a), decided 2026-11-25 by Ianick Noejovich (its third part), as made exact on 2026-11-26 (GRD-R35 supersedes GRD-R31). US-GRD-14 and US-GRD-16 hold the other parts. It changes the behavior recorded by US-GRD-06 (host CLI and API calls), which stays as the record of the earlier behavior.
- "May write" is US-GRD-06/AC4's reading: a method other than GET in any form, fields or a form, `--input`, or graphql. US-GRD-06/AC1 keeps GET calls to these endpoints allowed.
- The endpoints, checked in the official documentation on 2026-11-26:
  - GitHub REST, branch protection: https://docs.github.com/en/rest/branches/branch-protection lists `PUT` and `DELETE` on `/repos/{owner}/{repo}/branches/{branch}/protection`, and `POST`, `PUT`, `PATCH`, or `DELETE` on its subpaths `enforce_admins`, `required_pull_request_reviews`, `required_signatures`, `required_status_checks` (and `…/contexts`), and `restrictions` (and `…/apps`, `…/teams`, `…/users`).
  - GitHub REST, rulesets: https://docs.github.com/en/rest/repos/rules lists `POST /repos/{owner}/{repo}/rulesets` and `PUT` and `DELETE` on `/repos/{owner}/{repo}/rulesets/{ruleset_id}`; its other endpoints, `rules/branches/{branch}` and the ruleset history, are reads only.
  - GitHub GraphQL: https://docs.github.com/en/graphql/reference/branches lists `createBranchProtectionRule`, `updateBranchProtectionRule`, and `deleteBranchProtectionRule`; https://docs.github.com/en/graphql/reference/repos lists `createRepositoryRuleset`, `updateRepositoryRuleset`, and `deleteRepositoryRuleset`.
  - GitLab REST: https://docs.gitlab.com/api/protected_branches/ lists `POST /projects/:id/protected_branches`, and `PATCH` and `DELETE` on `/projects/:id/protected_branches/:name`.
- The paths may be written with the CLI placeholders as well as real names: `gh api` fills `{owner}`, `{repo}`, and `{branch}`, and `glab api` fills placeholders such as `:id` and `:fullpath` (`hosts.py` already calls `projects/:fullpath/…`).
- US-GRD-06/AC5's "branches" means GitLab's `/repository/branches` endpoint (the guard matches `/repository/(commits|files|branches)`), a different endpoint from `protected_branches`, so this ticket does not overlap it.
- Organization-level rulesets (`orgs/{org}/rulesets`) and GitLab group-level protected branches are not in the decided list.
- Narrows US-GRD-06/AC4, which asks for a call that may write and does not merge or move a branch: these calls are now denied instead. That criterion is not listed as replaced, because the rest of it still holds.

## Open questions

- None. The decision log records this decision, and the decision of 2026-11-26 listed the endpoints.
