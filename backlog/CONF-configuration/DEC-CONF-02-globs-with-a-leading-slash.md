---
id: DEC-CONF-02
type: decision
title: Globs starting with a slash load but match nothing
epic: EP-CONF
source_reqs: [CONF-R11, CONF-R12]
blocked_by: []
owner: Ianick Noejovich
assignee_type: human
status: draft
---

## Question

Is this intended? A glob written with a leading `/` (for example `/vendor/**` in `ignore`, meaning "from the repository root") loads without any error and then matches no file, because paths are compared without a leading slash.

## Context

- Current behavior (verified 2026-11-25): a configuration with a `tests`, `code`, or `ignore` glob starting with `/` loads, and matching `src/a.py` against `/src/**` is false. A leading `./` is stripped and a backslash is rejected, but a leading `/` is neither.
- Evidence: `template/scripts/kitchen_lib.py:256` gives the reason backslashes are rejected ("a backslash would silently match nothing"), which applies equally to a leading `/`; `:154` strips only `./`; `matches` at `:176` strips only `./` from paths.
- Partly mitigated: the installer's doctor warns about each `tests` or `code` glob that matches no file (`init.py:1381-1387`), but it does not check `ignore` globs, and `backlog_check.py` and the gates give no warning.
- Likely intended behavior: either reject a leading `/` with a clear message, as backslashes are, or read it as the repository root.

## Options

None recorded.

## Recommendation

Proposal, not decided: reject a leading `/` with a message like the backslash one, since that keeps one meaning per pattern and matches the existing rule's reason.

## Decides

- Whether a fix story is filed against CONF-R11 and CONF-R12; US-CONF-02 and US-CONF-07 stay as recorded either way.
