---
id: US-GRD-10
type: story
title: Let denials win and honor the sandbox opt-in
epic: EP-GRD
source_reqs: [GRD-R24, GRD-R25]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person running agents unattended on a machine I chose, I want to turn the guard's asks into passes without ever relaxing its refusals, so that unattended runs keep going while pushes, merges, and the merge gate stay enforced.

## Acceptance criteria

- AC1: Given a call in which one part asks (a force push, a host command, a `-R` option) and another part is denied (a push of the default branch, `glab mr create --fill`), when it runs, with or without the sandbox opt-in, then the guard denies it.
- AC2: Given `KITCHEN_GUARD_SANDBOX=1`, when a command or file edit that would otherwise ask runs (other than a force push), then the guard lets it through without a prompt.
- AC3: Given `KITCHEN_GUARD_SANDBOX=1`, when a call the guard denies runs (including a git alias that pushes, merges, or runs a shell), then the guard still denies it.
- AC4: Given `KITCHEN_GUARD_SANDBOX=1`, when an otherwise allowed push is forced, then the guard still asks a person.
- AC5: Given `KITCHEN_GUARD_SANDBOX=1`, when an agent runs a merge of the right shape, then the guard still runs the merge gate and denies the merge when it fails.
- AC6: Given `KITCHEN_GUARD_SANDBOX` set to a value other than `1` (such as `true`), when a call that asks runs, then the guard still asks.

## Notes

- Adopted from `template/claude/hooks/guard.py` (`deny`, `ask`, `finish`). A denial ends the hook at once; asks are collected and returned only after every check ran, the force-push reason first, repeated reasons once. Behavior observed in the code and its tests on 2026-11-25, not yet confirmed by a person.
- Letting a denial win over an earlier ask is deliberate (decision-log entry "Guard choices made while building v0.1"). The opt-in is meant to be set per machine in the git-ignored `.claude/settings.local.json` (`CONTRIBUTING.md` section 2).

## Open questions

- None. The behavior is recorded as observed; the person confirms it when walking through the requirements.
