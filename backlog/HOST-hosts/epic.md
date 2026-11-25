---
id: EP-HOST
type: epic
title: Host adapters
owner: Ianick Noejovich
assignee_type: either
status: ready
code: ["template/scripts/hosts.py"]
---

The host adapters let the workflow scripts work the same way on GitHub (pull requests through `gh`), GitLab (merge requests through `glab`), and the manual host (no CLI: a person reads and merges change requests). Each adapter lists the branches that open change requests and pushes claim, reads one change request with its checks in a host-neutral shape, and defines the one merge command an agent may run, pinned to the head commit. The epic also covers the CI and description templates installed per host (`template/github/`, `template/gitlab/`), the host settings the workflow needs, and `guide/hosts.md`, which documents the interface for adding a host.

## Boundaries

- The merge gate (`deliver.py gate merge`), `gate pr`, delivery records, and `deliver.py next`, `status`, and `merge-command` belong to the delivery epic; they call these adapters.
- The Claude Code guard, which allows a merge only when it equals the adapter's merge command and the gate passes, belongs to the guard epic.
- Choosing the host value (the `host` key and detection from the origin URL) belongs to the configuration epic; this epic starts from the configured value.
- Installing the host's CI files and filling the toolchain step under the marker line belong to the installer epic; this epic owns the templates' content, including the marker line and the placeholder.
- No host other than github, gitlab, and manual; no merged results pipelines on GitLab; no squash or rebase merges.

## Open

- DEC-HOST-01, DEC-HOST-02, SPK-HOST-01.
