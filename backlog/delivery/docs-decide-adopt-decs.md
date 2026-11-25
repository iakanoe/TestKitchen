# Delivery record: docs/decide-adopt-decs

- Branch: `docs/decide-adopt-decs`
- Ticket: None

Written by `scripts/deliver.py record`. Everything below the marker is the change request's description, verbatim; `deliver.py gate pr` fails when it differs from the current description.

<!-- change-request-description -->

## Ticket

None. Defines the outcome of the 18 DECs opened by `/define adopt`: each decision applied to the requirements, the DECs, and new draft tickets.

## Plan

No ticket, so no criterion rows. Per decision, in the order `playbooks/define.md` ("Applying a decision") gives: requirement text (new or superseding), DEC outcome and status, epic Open line, new draft tickets, decision-log entry. Requirements a decision confirms lose the `(observed in code)` marker (29 confirmed); HOST requirements also cited by SPK-HOST-01 stay marked. No adopted done ticket was edited.

Constrained by: `playbooks/define.md`, `backlog/README.md`.

## Gaps found

- US-CONF-16: Report a kitchen.yml that is not UTF-8 (draft; implements its DEC).
- US-CONF-17: Refuse globs that start with a slash (draft; implements its DEC).
- US-DEF-30: Count uncovered requirements in the summary (draft; implements its DEC).
- US-DEF-31: Say that readiness rules skip epics (draft; implements its DEC).
- US-DEF-32: Match the playbook's Done paragraph to --gaps (draft; implements its DEC).
- US-DLV-38: Judge gate pr at the revision it names (draft; implements its DEC).
- US-DLV-39: Leave adopted tickets out of release notes (draft; implements its DEC).
- US-DLV-40: Print the playbook's Ticket line for spikes and decisions (draft; implements its DEC).
- US-GRD-11: Ask after a cd the guard cannot follow (draft; implements its DEC).
- US-GRD-12: Ask about git config only for the config subcommand (draft; implements its DEC).
- US-GRD-13: Deny GraphQL ref deletion (draft; implements its DEC).
- US-GRD-14: Ask before writes the guard cannot see (draft; implements its DEC).
- US-GRD-15: Deny branch-protection API writes (draft; implements its DEC).
- US-HOST-13: Report unreadable host CLI output (draft; implements its DEC).
- US-HOST-14: Refuse a merge sha with a trailing newline (draft; implements its DEC).
- TASK-INST-02: Correct the Python version comment in init.py (draft; implements its DEC).
- US-INST-25: Tell the person how to finish a host switch (draft; implements its DEC).
- US-INST-26: Say that an agent's shell may have no terminal (draft; implements its DEC).
- US-INST-27: Report a lock version that is not a number (draft; implements its DEC).
- SPK-HOST-01: Verify the GitLab adapter on a real GitLab project (still open).

## Decisions

- The guard asks before writes it cannot see. Log: The guard asks before writes it cannot see
- The guard denies GraphQL deleteRef. Log: The guard denies GraphQL deleteRef
- git config asks only for the config subcommand. Log: git config asks only for the config subcommand
- The guard treats the folder as unknown after cd -, popd, or a subshell cd. Log: The guard treats the folder as unknown after cd -, popd, or a subshell cd
- The merge sha check matches the whole value. Log: The merge sha check matches the whole value
- Unreadable host CLI output is a host error. Log: Unreadable host CLI output is a host error
- pr-body prints the playbook's Ticket line per type. Log: pr-body prints the playbook's Ticket line per type
- Release notes leave out adopted tickets. Log: Release notes leave out adopted tickets
- gate pr reads tickets and kitchen.yml at --head. Log: gate pr reads tickets and kitchen.yml at --head
- The playbook's Done paragraph follows --gaps. Log: The playbook's Done paragraph follows --gaps
- Epics stay exempt from readiness. Log: Epics stay exempt from readiness
- The strict summary counts uncovered requirements. Log: The strict summary counts uncovered requirements
- Globs never start with a slash. Log: Globs never start with a slash
- A kitchen.yml that is not UTF-8 is a configuration error. Log: A kitchen.yml that is not UTF-8 is a configuration error
- A lock version that is not a number is a broken lock. Log: A lock version that is not a number is a broken lock
- AGENT-INSTALL.md says the shell may have no terminal. Log: AGENT-INSTALL.md says the shell may have no terminal
- Python 3.6 and older may fail with a syntax error. Log: Python 3.6 and older may fail with a syntax error
- Host switch on update tells the person to set kitchen.yml's host. Log: Host switch on update tells the person to set kitchen.yml's host

## Platform changes

- None

## Test changes

None

## Review report

None: this change request touches no code or test file (only `docs/` and `backlog/`). The owner decided each DEC in a decision round and approved the drafted application as a whole before it was written.

## Checks

- `python3 scripts/backlog_check.py` and `--strict`: 0 errors, 0 warnings (6 epics, 145 stories, 9 tasks, 18 decisions, 1 spike).
- `--gaps`: 187 lines (was 215): 161 unconfirmed requirements, SPK-HOST-01, 6 test-debt tasks, 19 new draft tickets.
- `--refine`: 9 findings, all tickets citing a superseded requirement (5 adopted stories, 4 closed DECs); each change already has its new ticket.
