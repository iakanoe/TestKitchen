---
id: US-CONF-09
type: story
title: Exclude framework files listed in kitchen.lock
epic: EP-CONF
source_reqs: [CONF-R14]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a project maintainer with broad globs, I want Test Kitchen's own installed files left out of my scans, so that its example text never fails my checks right after install.

## Acceptance criteria

- AC1: Given `kitchen.lock` lists a path under `files` that the project's `code` or `tests` globs cover, when the configuration is loaded, then that path is neither a code file nor a test file.
- AC2: Given `kitchen.lock` lists a path, when its copy with the `.kitchen-new` suffix is classified, then that copy is excluded too.
- AC3: Given there is no `kitchen.lock`, or its `files` is missing or empty, when the configuration is loaded, then no file is excluded this way.
- AC4: Given a `kitchen.lock` that is not valid JSON, or whose top level is not an object, when the configuration is loaded, then it fails with an error saying the lock is not valid JSON and to restore it from git history.
- AC5: Given a `kitchen.lock` whose `files` is not a table of paths, when the configuration is loaded, then it fails with an error saying so and to restore it from git history.

## Notes

Paths are compared exactly as the lock writes them. Decision log, "Test Kitchen's own files are excluded from project scans" and "History checks see merge commits" (a lock that isn't valid JSON is a config error).

## Open questions

- None. Adopted behavior, recorded as the code does it now; a person confirms the requirements.
