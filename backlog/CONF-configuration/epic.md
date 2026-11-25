---
id: EP-CONF
type: epic
title: Configuration and conventions
owner: Ianick Noejovich
assignee_type: either
status: ready
code: ["template/scripts/kitchen_lib.py"]
---

The shared rules every Test Kitchen script, the guard, and the installer read the same way: loading and validating `kitchen.yml` (required and optional keys, defaults, host detection, the default branch), the glob syntax and the test/code/ignored classification built on it, the exclusion of framework files listed in `kitchen.lock`, the two test tag forms, the ticket and requirement ID formats, the `test-kitchen: no-trace` marker, the `test_command` placeholders, how git is called and how the project's files are listed, and the shared library's `--self-test` and `--config` command line. Requirements: `docs/requirements/CONF-configuration.md`.

## Boundaries

- What each setting does once loaded belongs to the epic that uses it: autonomy, hosts, and merging (delivery and host adapters), `split_threshold` and `self_contained_tickets` (backlog checks), release-slice rules (backlog checks and delivery).
- The backlog checks that use these conventions (tag tracing, to-do markers, decision mentions, coverage, gaps) and the gates that run `test_command` are owned by their own epics; this epic owns only the shared formats and readers.
- The installer's own lighter validation of `kitchen.yml` and its doctor checks (such as `{report}` being present in `test_command`) belong to the installer epic.
- No `[...]` classes or `{a,b}` alternatives in globs, and no configuration of IDs, tag forms, paths, or branch names: they are fixed conventions.

## Open

- None.
