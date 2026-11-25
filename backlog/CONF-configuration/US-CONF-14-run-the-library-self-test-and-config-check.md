---
id: US-CONF-14
type: story
title: Run the library self-test and config check
epic: EP-CONF
source_reqs: [CONF-R23]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a project maintainer, I want to check the shared library and see my loaded configuration from the command line, so that I can tell quickly whether the scripts and `kitchen.yml` are sound.

## Acceptance criteria

- AC1: Given a working installation, when `python3 scripts/kitchen_lib.py --self-test` runs, then it prints `PASS self-test` and exits 0, without network access.
- AC2: Given a self-test check that fails, when `--self-test` runs, then it prints one `FAIL` line per failure and a `FAIL self-test` summary with the count, and exits 1.
- AC3: Given a valid `kitchen.yml`, when `python3 scripts/kitchen_lib.py --config` runs, then it prints each loaded setting as `key: value` and exits 0.
- AC4: Given an invalid `kitchen.yml`, when `--config` runs, then it prints each problem on its own `ERROR` line and exits 1.
- AC5: Given no arguments or any other arguments, when the library is run, then it prints its usage text and exits 2.

## Notes

`--config` reads the project the scripts belong to, from any working directory (US-CONF-15). The delivery `check` command runs this self-test.

## Open questions

- None. Adopted behavior, recorded as the code does it now; a person confirms the requirements.
