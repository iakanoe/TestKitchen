---
id: US-INST-11
type: story
title: Fill the CI toolchain step
epic: EP-INST
source_reqs: [INST-R15]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a developer installing Test Kitchen, I want the CI step that sets up my language filled in when the installer recognizes my stack, so that the `check` job can run my tests from the first change request.

## Acceptance criteria

- AC1: Given a root `package.json` and no `yarn.lock`, `pnpm-lock.yaml`, `bun.lockb`, or `bun.lock`, when the toolchain is detected, then Node is set up with `npm ci` (with `package-lock.json` or `npm-shrinkwrap.json`, plus the npm cache on GitHub) or `npm install` (without), using `.nvmrc` or `.node-version` when present, else `lts/*`.
- AC2: Given `requirements.txt`, `pyproject.toml`, `setup.py`, or `setup.cfg` and no `poetry.lock`, `uv.lock`, `Pipfile`, or `Pipfile.lock`, when the toolchain is detected, then Python is set up with `python3 -m pip install pyyaml`, plus `pytest` when the test command mentions pytest, plus `-r` for each of `requirements.txt`, `requirements-dev.txt`, `dev-requirements.txt`, and `requirements-test.txt` present (else `-e .`), using `.python-version` when present, else `3.x`.
- AC3: Given host github and recognized stacks, when the CI file is written, then the step under the marker is replaced, at its indentation, by `actions/setup-node@v7` or `actions/setup-python@v7` and an install step per stack, and the rest of the workflow is unchanged.
- AC4: Given host gitlab and recognized stacks, when the CI file is written, then the script item under the marker is replaced by single-quoted items: for Node an `apt-get` install of `nodejs` and `npm` when `npm` is missing, then the install command; for Python the pip command.
- AC5: Given the step was replaced, when the CI file is written, then the marker line reads `# TEST-KITCHEN: toolchain setup (filled by init.py: <stacks>)`, the plan notes "toolchain step filled for <stacks>", and the lock's `options.toolchain` lists the stacks.
- AC6: Given no recognized stack, a CI file without the marker, or a marker with no list item under it, when the CI file is written, then it is left as the template has it, and the plan notes that the stack was not recognized (fill the step yourself), that there is no marker, or that no step was found.

## Notes

Observed in `init.py` on 2026-11-25 by `/define adopt`; not yet confirmed by a person. Only npm and pip are recognized by decision (decision log, "Installer choices made while building v0.1"). `actions/setup-node` and `actions/setup-python` both publish a `v7` tag (checked with `git ls-remote` on 2026-11-25). `update` refills the step from the project's current files and `kitchen.yml` test command.

## Open questions

- None. Behavior recorded as observed; the person confirms it.
