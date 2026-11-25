---
id: DEC-INST-01
type: decision
title: Host switch on update leaves kitchen.yml's host unchanged
epic: EP-INST
source_reqs: [INST-R20, INST-R25]
blocked_by: []
owner: Ianick Noejovich
assignee_type: human
status: done
---

## Question

Is this intended? After `init.py update --host <new host>`, `kitchen.yml` keeps its old `host` line (or none, when the host was detected), so the scripts still use the old host and `doctor` warns and suggests running `update --host <old host>`, which undoes the switch.

## Context

- Current behavior: `update` never writes `kitchen.yml` (`init.py:1116-1121`) but installs the files for `args.host` (`init.py:1107`) and records it in the lock (`init.py:1199`). `doctor` compares the lock's host with `kitchen.yml`'s `host`, else the host detected from `origin` (`init.py:1408-1413`), and on a mismatch suggests `update --host <kitchen.yml or origin host>`. The previous host's CI files are listed as "no longer part of Test Kitchen" and stay on disk (`init.py:1156-1158`), so an old `.github/workflows/check.yml` keeps running if the repository is still on GitHub.
- Reproduced on 2026-11-25 in a throwaway repository: install with `--host github`, then `update --yes --host gitlab`. Result: `kitchen.yml` still says `host: github`, the lock says gitlab, `.github/workflows/check.yml` and `.gitlab-ci.yml` both exist, and `doctor` prints `WARN kitchen.yml or the origin remote says host github, but the CI files installed are for gitlab` with `Run: … update --host github`.
- Already settled: `update` never touches `kitchen.yml` (decision log, "Installer choices made while building v0.1": "`kitchen.yml` is not in `files`; `update` never touches it"), and `--host` can switch hosts on update (same entry). `guide/install.md` says "`--host` switches the host's files" and does not mention `kitchen.yml`.
- Likely intended: after a host switch, the scripts, CI files, and `doctor` agree on the new host, or the person is told exactly which line of `kitchen.yml` to change.

## Options

None recorded. Proposals, not decisions:

- (a) Keep `kitchen.yml` untouched, and have `update --host` print that `host:` in `kitchen.yml` must be set to the new host; make `doctor`'s fix text offer both directions (set `host:` in `kitchen.yml`, or run `update --host <other>`).
- (b) Let `update --host` rewrite only the `host:` line of `kitchen.yml`, which changes the recorded rule that `update` never touches it.
- (c) Keep the current behavior and document the manual `kitchen.yml` edit in `guide/install.md`.

## Recommendation

(a): it keeps the recorded rule that `update` never edits the project's configuration, and it stops `doctor` from pointing the person back to the host they just left.

## Decides

No ticket waits on it. Any change becomes a new story under EP-INST; US-INST-16 and US-INST-20 stay the record of today's behavior.

## Outcome

- Date: 2026-11-25.
- Answer: Option (a): `kitchen.yml` stays untouched; an `update --host <new host>` that changes the host prints that `host:` in `kitchen.yml` must be set to the new host, and `doctor`'s host-mismatch fix offers both directions (set `host:` in `kitchen.yml` to the installed host, or run `update --host <other host>`).
- Decided by: Ianick Noejovich.
- Recorded in: requirements INST-R30, INST-R31; confirmed INST-R20, INST-R25; US-INST-25; decision log, "Host switch on update tells the person to set kitchen.yml's host".
