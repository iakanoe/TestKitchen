---
id: EP-INST
type: epic
title: Install and update
owner: Ianick Noejovich
assignee_type: either
status: ready
code: ["init.py"]
---

Installing Test Kitchen into a project's repository and keeping it current, through the single file `init.py`: an install that asks three questions with guesses from the folder, shows a plan, supports `--dry-run`, never overwrites a file (side-by-side `.kitchen-new` copies instead), writes `kitchen.yml` and `kitchen.lock`, and fills the CI toolchain step when it recognizes the stack; `update`, which replaces untouched framework files, handles conflicts, prints migration notes, and can switch hosts; and `doctor`, a read-only checklist of what the install needs to work. It also covers `template/kitchen.yml.tmpl` and the installer-facing parts of `README.md`, `AGENT-INSTALL.md`, and `guide/install.md`. Requirements: `docs/requirements/INST-install.md`.

## Boundaries

- No uninstall command: removal is by hand, as `guide/install.md` lists.
- No "latest version" lookup: the default release is the running file's own version.
- It never commits, pushes, or deletes a file, and never edits `kitchen.yml` after the install wrote it.
- It does not install language toolchains or project dependencies on the machine; it only writes the CI step that does so, and only for npm and pip.
- The content of the installed framework files (scripts, guard, playbooks, CI templates other than the toolchain step) belongs to the epics that own them.
- It does not run the definition workflow; it only points to it in its next steps.

## Open

- None.
