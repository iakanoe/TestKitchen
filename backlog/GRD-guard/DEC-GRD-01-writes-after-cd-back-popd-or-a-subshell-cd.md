---
id: DEC-GRD-01
type: decision
title: Writes after cd back, popd, or a subshell cd
epic: EP-GRD
source_reqs: [GRD-R22]
blocked_by: []
owner: Ianick Noejovich
assignee_type: human
status: done
---

## Question

Is this intended? The guard follows `cd` to resolve relative write targets, but it ignores `cd -` and `popd` and treats a `cd` inside a subshell `( … )` as if it changed the folder for the rest of the call. So a write to a protected path after one of these goes through without asking.

## Context

- Current behavior (verified on 2026-11-25 by feeding the hook JSON in a scratch project built like `tests/test_guard.py` does):
  - `cd /tmp && cd - && echo x > kitchen.yml` is allowed, though the shell writes the project's `kitchen.yml`.
  - `cd /tmp; cd -; rm -rf docs` is allowed, though it removes the project's `docs/`.
  - `pushd /tmp && popd && echo x > kitchen.yml` is allowed (`popd` is not followed).
  - `(cd /tmp) && echo x > kitchen.yml` is allowed (the subshell's `cd` is applied to the commands after it).
  - In the other direction, `cd docs && cd - && echo x > notes.txt` and `(cd docs) && echo x > notes.txt` ask about `docs/notes.txt`, which the shell does not write.
- Evidence: `template/claude/hooks/guard.py:1309-1315` (`guard_writes`): `cd`/`pushd` move the tracked folder, `cd -` is skipped (`target != "-"`), `popd` is not handled, and `lex()` (`guard.py:760-762`) treats `(` and `)` as plain separators, so subshells are not scoped.
- Likely intended: GRD-R22 says targets "follow `cd`", and the code already treats a folder it cannot know (`cd $X`) as unknown, so every later write asks (`guard.py:1311-1318`). A folder it does not track would get the same treatment.
- Already settled: the guard is a guardrail against mistakes, not a sandbox (`CONTRIBUTING.md` section 2); shell writes to protected paths ask (decision-log entry "Guard hardening after the adversarial review").

## Options

None recorded. Proposals:

- (a) Treat the folder as unknown after `cd -`, `popd`, and any `cd` inside a subshell or group, so every later write in the call asks, as after `cd $X`.
- (b) Track the folder stack precisely: remember the previous folder for `cd -`, keep a `pushd`/`popd` stack, and scope `cd` to its subshell.
- (c) Keep the current behavior as a known limitation and say so in `CONTRIBUTING.md` section 2.

## Recommendation

(a): it fails toward asking, matches how the guard already treats a folder known only at run time, and is small. (b) is more precise but adds shell modelling for a rare case.

## Decides

US-GRD-09 (its folder-following criterion and notes). A change to the guard would be a new story in this epic.

## Outcome

- Date: 2026-11-25.
- Answer: Option (a): after `cd -`, `popd`, or a `cd` inside a subshell or group, the guard treats the folder as unknown, so every later write in the call asks.
- Decided by: Ianick Noejovich.
- Recorded in: requirements GRD-R26; confirmed GRD-R22; US-GRD-11; decision log, "The guard treats the folder as unknown after cd -, popd, or a subshell cd".
