---
id: DEC-GRD-04
type: decision
title: Writes the guard does not see
epic: EP-GRD
source_reqs: [GRD-R20, GRD-R22]
blocked_by: []
owner: Ianick Noejovich
assignee_type: human
status: done
---

## Question

Should the guard cover these writes, which it lets through today without asking?

## Context

- Found while adopting the guard (2026-11-25), by feeding the hook JSON in a scratch project:
  - `git apply`, `patch`, and `git reset --hard` can change protected files without an ask, because the guard reads only the files a command names, and these commands take their targets from a patch or from the history.
  - Deleting `docs/decision-log.md` goes through: the decision log is exempt from protection so every delivery can append to it (GRD-R20), and the exemption also covers removing it.
  - REST calls that change branch protection only ask, so sandbox mode lets them through.
- Already decided: the guard is a guardrail against mistakes, not a sandbox ("Guard hardening after the adversarial review"); it asks before writes to protected paths it can see (GRD-R22).

## Options

None recorded. Proposals:

- (a) Ask for `git apply`, `patch`, and `git reset --hard` whenever the project has protected files, ask before deleting or truncating the decision log (appending stays free), and deny branch-protection API writes.
- (b) Cover only the decision-log deletion, and document the rest as limits of a guardrail.
- (c) Keep today's behavior and document all of it as limits.

## Recommendation

(a): each one is a plain command an agent might run by mistake, which is the guard's job; `git reset --hard` asking may slow some recoveries, which is an acceptable cost.

## Decides

US-GRD-08 and US-GRD-09 (protected edits and shell writes); a change would be a new story in this epic.

## Outcome

- Date: 2026-11-25.
- Answer: Option (a): `git apply`, `patch`, and `git reset --hard` ask whenever the project has protected files; deleting or truncating `docs/decision-log.md` asks while appending stays free; branch-protection API writes are denied.
- Decided by: Ianick Noejovich.
- Recorded in: requirements GRD-R29, GRD-R30, GRD-R31; superseded GRD-R20 (by GRD-R30); confirmed GRD-R22; US-GRD-14, US-GRD-15; decision log, "The guard asks before writes it cannot see". It narrows "The guard does not ask before decision-log edits": appending and edits stay free.
