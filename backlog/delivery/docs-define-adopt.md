# Delivery record: docs/define-adopt

- Branch: `docs/define-adopt`
- Ticket: None

Written by `scripts/deliver.py record`. Everything below the marker is the change request's description, verbatim; `deliver.py gate pr` fails when it differs from the current description.

<!-- change-request-description -->

## Ticket

None. Defines Test Kitchen in its own repository through `/define adopt`: `docs/product.md`, six epics, their observed requirements, and adopted tickets for the behavior that already exists.

## Plan

No ticket, so no criterion rows. What was written, each epic after its own checkpoint yes:

| Epic | Owns | Requirements | Stories | Tasks | DECs |
| --- | --- | --- | --- | --- | --- |
| INST | `init.py` | 29 | 24 | 1 (draft) | 4 |
| CONF | `template/scripts/kitchen_lib.py` | 25 | 15 | 2 + 1 (draft) | 2 |
| DEF | `template/scripts/backlog_check.py` | 39 | 29 | 1 (draft) | 3 |
| DLV | `template/scripts/deliver.py` | 47 | 37 | 1 (draft) | 3 |
| HOST | `template/scripts/hosts.py` | 25 | 12 | 1 (draft) | 2 + SPK |
| GRD | `template/claude/hooks/guard.py` | 25 | 10 | 1 (draft) | 4 |

Every requirement is marked `(observed in code)` until the owner confirms it. Every adopted ticket is `done` with `adopted: true`, owned by Ianick Noejovich.

Constrained by: `playbooks/define.md` (adopt), `backlog/README.md`.

## Gaps found

- DEC-CONF-01: A kitchen.yml that is not UTF-8 ends in an unhandled error.
- DEC-CONF-02: Globs starting with a slash load but match nothing.
- DEC-DEF-01: Strict summary leaves out uncovered-requirement errors.
- DEC-DEF-02: Readiness rules skip epics.
- DEC-DEF-03: Playbook done condition differs from what --gaps checks.
- DEC-DLV-01: gate pr reads tickets and kitchen.yml from the checkout, not from --head.
- DEC-DLV-02: Release notes include adopted stories.
- DEC-DLV-03: Change-request skeleton wording for spikes and decisions.
- DEC-GRD-01: Writes after cd back, popd, or a subshell cd.
- DEC-GRD-02: A file named config in a git command.
- DEC-GRD-03: GraphQL ref deletion only asks.
- DEC-GRD-04: Writes the guard does not see.
- DEC-HOST-01: Unreadable host CLI output when listing open branches.
- DEC-HOST-02: A merge sha with a trailing newline is accepted.
- DEC-INST-01: Host switch on update leaves kitchen.yml's host unchanged.
- DEC-INST-02: Python older than 3.7 gets a syntax error instead of the version message.
- DEC-INST-03: AGENT-INSTALL.md states that an agent's shell has no terminal.
- DEC-INST-04: A malformed lock version ends update in a traceback.
- SPK-HOST-01: Verify the GitLab adapter on a real GitLab project.
- TASK-CONF-03: Pay test debt: tagged tests for EP-CONF.
- TASK-DEF-01: Pay test debt: tagged tests for EP-DEF.
- TASK-DLV-01: Pay test debt: tagged tests for EP-DLV.
- TASK-GRD-01: Pay test debt: tagged tests for EP-GRD.
- TASK-HOST-01: Pay test debt: tagged tests for EP-HOST.
- TASK-INST-01: Pay test debt: tagged tests for EP-INST.

## Decisions

- `docs/product.md`, the six epics and their code, and the owner. Log: Adopt: product, epics, and owner
- Adopted criteria are test debt with one task per epic; review-only behavior stays in stories. Log: Adopt: test debt and review-only behavior
- All six epics written; what is left for the next session. Log: Adopt progress: all six epics written

## Platform changes

- None

## Test changes

None

## Review report

None: this change request touches no code or test file (only `docs/` and `backlog/`), so `gate pr` needs no review. Every epic was shown to the owner at its checkpoint before it was written.

## Checks

- `python3 scripts/backlog_check.py` and `--strict`: 0 errors, 0 warnings (6 epics, 127 stories, 8 tasks, 18 decisions, 1 spike).
- `--gaps`: 190 unconfirmed observed requirements, 18 open DECs, 1 open spike, 6 draft tasks; no unclaimed code and no empty `docs/product.md` any more.
- `--test-debt`: 636 criteria (about 150 of them review-only).
