---
id: US-CONF-05
type: story
title: Detect the host from the origin remote
epic: EP-CONF
source_reqs: [CONF-R09]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a project maintainer, I want the host detected from the origin remote unless I set it, so that most projects need no host setting and the rest can name theirs.

## Acceptance criteria

- AC1: Given `host` is `github`, `gitlab`, or `manual`, when the configuration is loaded, then that host is used and the configuration records it as not detected.
- AC2: Given `host` is any other value, including a different letter case, when the configuration is loaded, then an error lists the three allowed hosts.
- AC3: Given `host` is absent or left without a value and the `origin` URL contains `github.com` in any letter case, when the configuration is loaded, then the host is `github` and is recorded as detected.
- AC4: Given `host` is absent and the `origin` URL contains `gitlab`, when the configuration is loaded, then the host is `gitlab`.
- AC5: Given `host` is absent and the `origin` URL contains neither, or there is no `origin` remote, when the configuration is loaded, then the host is `manual`.

## Notes

A GitHub Enterprise or self-hosted GitLab URL that hides the host name is detected as `manual`; `guide/configuration.md` tells people to set `host` then. A URL that contains both names is detected as `github`.

## Open questions

- None. Adopted behavior, recorded as the code does it now; a person confirms the requirements.
