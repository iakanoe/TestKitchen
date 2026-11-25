---
id: US-DEF-32
type: story
title: Match the playbook's Done paragraph to --gaps
epic: EP-DEF
source_reqs: [DEF-R42]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: draft
---

As a person or agent defining a product, I want the playbook's "Done" paragraph to describe what `--gaps` checks, so that "fully defined" means one thing in the text and in the script.

## Acceptance criteria

- AC1: Given `playbooks/define.md`, "Done", when it is read, then it lists requirements still marked as observed in code among what keeps the product from being fully defined.
- AC2: Given the same paragraph, when it is read, then it says a requirement is covered when it is cited by a story or task that is not deferred, and no longer says "covered by ready or done tickets".

## Notes

Implements DEC-DEF-03, option (a), decided 2026-11-25 by Ianick Noejovich. `--gaps` itself does not change. It changes the playbook wording recorded by US-DEF-29, which stays as the record of the earlier wording. The product copy is `template/playbooks/define.md`; the root copy is an installed release that changes only through `init.py update`.

## Open questions

- None.
