---
id: DEC-HOST-02
type: decision
title: A merge sha with a trailing newline is accepted
epic: EP-HOST
source_reqs: [HOST-R14]
blocked_by: []
owner: Ianick Noejovich
assignee_type: human
status: done
---

## Question

Is this intended? Building a merge command accepts a head sha of 40 hexadecimal characters followed by a newline, and puts that value, newline included, into the merge command.

## Context

- Current: `SHA = re.compile(r"^[0-9a-f]{40}$")` is applied with `SHA.match` (template/scripts/hosts.py:37 and 76). In Python, `$` also matches just before a final newline, so `_merge_args` with 40 hexadecimal characters plus a newline returns the sha with the newline, and `merge_argv` returns a command containing it. Checked on 2026-11-25.
- Likely intended: only "the full 40-character commit sha", as the error message in `_merge_args` (hosts.py:77-78) and HOST-R14 say.
- Impact looks small: the merge gate compares the given head with the change request's head sha, so such a value would be refused there, and the host would not find that commit. It is still a gap in the fail-closed validation of the one function that defines the allowed merge command.

## Options

None recorded.

## Recommendation

Proposal: match the whole value (`fullmatch`, or `\Z` instead of `$`), through a new fix story with a test for a trailing newline.

## Decides

No open ticket waits on it. A change of behavior becomes a new story; the adopted stories stay as they are.

## Outcome

- Date: 2026-11-25.
- Answer: Fix: the merge sha check matches the whole value, so a trailing newline is refused.
- Decided by: Ianick Noejovich.
- Recorded in: requirements HOST-R27; confirmed HOST-R14; US-HOST-14; decision log, "The merge sha check matches the whole value".
