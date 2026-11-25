---
id: DEC-HOST-01
type: decision
title: Unreadable host CLI output when listing open branches
epic: EP-HOST
source_reqs: [HOST-R04, HOST-R05, HOST-R06]
blocked_by: []
owner: Ianick Noejovich
assignee_type: human
status: done
---

## Question

Is this intended? When `gh pr list` or `glab mr list` exits 0 but prints something that is not JSON, the adapter raises a JSON parse error (a ValueError), not a HostError, so `deliver.py next` and `deliver.py status` end with a Python traceback instead of their own message.

## Context

- Current: `_json_values` (template/scripts/hosts.py:81-89) lets `json.JSONDecodeError` escape from `GitHub.open_branches` (hosts.py:210-213) and `GitLab.open_branches` (hosts.py:336-345). `cmd_next` catches only `HostError` (template/scripts/deliver.py:218-220, where it would stop with "cannot tell which branches are taken"), `cmd_status` catches only `HostError` (deliver.py:906-910, where it would fall back to the branches from the last fetch), and `main` catches `Stop`, `ConfigError`, `GitError`, `HostError`, and `OSError` (deliver.py:1119), not `ValueError`. Reproduced on 2026-11-25 with the tests' fake `gh` answering `pr list` with a warning line before `[]`: both commands exited 1 with a traceback ending in `json.decoder.JSONDecodeError`.
- Likely intended: a host CLI that answers with something unreadable is treated like a failing CLI (HostError), so `next` stops with its usual message and `status` uses its offline fallback. `gate merge` already treats a `ValueError` from reading a change request as a refusal (deliver.py:800), so that path is not affected.
- The outcome is fail closed either way (nothing is picked or merged); the difference is the message and the `status` fallback. Real `gh` and `glab` print their notices on stderr, so how often this happens is not known.

## Options

None recorded.

## Recommendation

Proposal: treat unparseable CLI output as a HostError in the adapter, with a message naming the command, through a new fix story. Until decided, the current behavior stays as recorded.

## Decides

No open ticket waits on it. A change of behavior becomes a new story; the adopted stories stay as they are.

## Outcome

- Date: 2026-11-25.
- Answer: Fix: host CLI output that is not JSON, when listing the branches of open change requests or reading a change request, is a HostError naming the command.
- Decided by: Ianick Noejovich.
- Recorded in: requirements HOST-R26; confirmed HOST-R04, HOST-R06; US-HOST-13; decision log, "Unreadable host CLI output is a host error". HOST-R05 stays marked as observed in code until SPK-HOST-01 runs.
