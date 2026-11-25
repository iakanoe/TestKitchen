---
id: US-GRD-08
type: story
title: Ask before editing protected files
epic: EP-GRD
source_reqs: [GRD-R19, GRD-R20, GRD-R21]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a project owner, I want file edits to the project's definition, process, guardrail, and framework files to ask me first, while the decision log stays open for every delivery, so that agents change what the project is only with a person's yes.

## Acceptance criteria

- AC1: Given an Edit, Write, MultiEdit, or NotebookEdit call on a protected path (a file under `docs/` other than the decision log, `.claude/` or `.git` at any depth, `.github/`, `.gitlab/`, `.gitlab-ci.yml`, `playbooks/`, `kitchen.yml`, `kitchen.lock`, `CONTRIBUTING.md`, `AGENTS.md`, `CLAUDE.md`, a framework script, or the git, gh, or glab configuration files in the home folder), when it runs, then the guard asks a person.
- AC2: Given an edit of any other file (source, tests, tickets, delivery records, `README.md`, a project script, `app/docs/…`, `.gitignore`, `.github-notes.md`, `playbooks.md`, a file outside the project), when it runs, then the guard lets it through.
- AC3: Given `docs/decision-log.md` (also written `Docs/Decision-Log.md`) is listed in `kitchen.lock`, when an agent edits it, then the guard lets it through; a similarly named file such as `docs/decision-log.md.bak` asks.
- AC4: Given a file `kitchen.lock` lists, or its `.kitchen-new` copy, when an agent edits it, then the guard asks and says the file is listed in `kitchen.lock`; with no `kitchen.lock`, the four framework scripts and the fixed paths still ask while other scripts go through; with an unreadable `kitchen.lock`, every file under `scripts/` asks.
- AC5: Given a protected path written in another case or Unicode compatibility form (`DOCS/x.md`, `Kitchen.yml` with a Kelvin sign, a long s), through `..`, relative to the call's working folder, or through a symbolic link into a protected folder, when it is edited, then the guard asks as for the plain path.

## Notes

- Adopted from `template/claude/hooks/guard.py` (`guard_edit`, `protected`, `fold`, `Lock`, `PROTECTED_REL`, `CONFIG_FILES`). Behavior observed in the code and its tests on 2026-11-25, not yet confirmed by a person.
- The decision-log exemption is deliberate (decision-log entry "The guard does not ask before decision-log edits"), and wins over the lock (entry "Guard choices made while building v0.1"). It also lets an agent overwrite, move, or delete the decision log without asking.
- `guide/agents.md` lists the protected paths without the `.kitchen-new` copies and the git, gh, and glab configuration files; `CONTRIBUTING.md` section 2 lists both.

## Open questions

- None. The behavior is recorded as observed; the person confirms it when walking through the requirements.
