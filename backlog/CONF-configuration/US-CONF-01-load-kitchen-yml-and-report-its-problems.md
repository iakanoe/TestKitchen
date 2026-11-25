---
id: US-CONF-01
type: story
title: Load kitchen.yml and report its problems
epic: EP-CONF
source_reqs: [CONF-R01, CONF-R04, CONF-R05]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a project maintainer, I want `kitchen.yml` loaded with every problem reported clearly, so that a broken or mistyped configuration never silently changes what the scripts do.

## Acceptance criteria

- AC1: Given no `kitchen.yml` at the repository root, when the configuration is loaded, then it fails with an error saying the file was not found and to run init.py.
- AC2: Given a `kitchen.yml` that is not valid YAML, when the configuration is loaded, then it fails with an "invalid YAML" error.
- AC3: Given a `kitchen.yml` whose content is a list or a single value, when the configuration is loaded, then it fails with an error saying it must be a mapping of keys to values.
- AC4: Given an empty `kitchen.yml`, when the configuration is loaded, then it fails with exactly three errors, one for each missing required key.
- AC5: Given a `kitchen.yml` with a key outside the known set, when the configuration is loaded, then it fails with an error naming that key and listing the known keys.
- AC6: Given a `kitchen.yml` with several invalid values, when the configuration is loaded, then every problem is reported at once, one line each, every line starting with `kitchen.yml:`.

## Notes

Unknown keys are errors as typo protection: a misspelled optional key would otherwise fall back to its default silently (code comment, observed). A `kitchen.yml` that is not UTF-8 currently ends in an unhandled decoding error rather than a configuration error; DEC-CONF-01 asks whether that is intended. The installer's own lighter check of `kitchen.yml` belongs to the installer epic.

## Open questions

- None. Adopted behavior, recorded as the code does it now; a person confirms the requirements.
- None. The undecoded-file case is outside these criteria and is asked in DEC-CONF-01.
