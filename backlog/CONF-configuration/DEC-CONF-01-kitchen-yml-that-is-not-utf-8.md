---
id: DEC-CONF-01
type: decision
title: A kitchen.yml that is not UTF-8 ends in an unhandled error
epic: EP-CONF
source_reqs: [CONF-R01, CONF-R05]
blocked_by: []
owner: Ianick Noejovich
assignee_type: human
status: draft
---

## Question

Is this intended? A `kitchen.yml` whose bytes are not valid UTF-8 (for example a file saved as Latin-1 with an accented character in a comment) makes the configuration load fail with an unhandled decoding error and a Python traceback, instead of a `kitchen.yml:` configuration error.

## Context

- Current behavior (verified 2026-11-25 by running `python3 scripts/kitchen_lib.py --config` on a copy with a `0xff` byte in `kitchen.yml`): a `UnicodeDecodeError` traceback. `backlog_check.py` catches only configuration errors around loading, so it would end the same way. The guard catches every exception when loading and refuses pushes and merges, so nothing unsafe happens; the person just gets a traceback rather than a message.
- Evidence: `template/scripts/kitchen_lib.py:337` reads the file as UTF-8 and `:338` catches only `yaml.YAMLError`; `template/scripts/backlog_check.py:680-681` catches only `ConfigError`. By contrast, `framework_files` (`kitchen_lib.py:355-356`) catches `ValueError`, so a non-UTF-8 `kitchen.lock` already gives a clear configuration error.
- Likely intended behavior: a configuration error such as "kitchen.yml: not valid UTF-8", in line with CONF-R05 and `guide/configuration.md` ("Each invalid value gives one clear message").

## Options

None recorded.

## Recommendation

Proposal, not decided: treat an undecodable `kitchen.yml` as a configuration error with a one-line message, through a fix story under this epic.

## Decides

- Whether a fix story is filed against CONF-R01; US-CONF-01 stays as recorded either way.
