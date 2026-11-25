# Product

## Vision

Test Kitchen is a framework you install into a repository so AI agents can define and deliver the project under guardrails. Requirements and tickets live in the repository as plain markdown; tests are written first, seen failing, and frozen; a reviewer with fresh context checks the plan, the tests, and the diff; every gap and decision is written down; and nothing merges unless deterministic gates pass. It works with any language and any test runner that writes JUnit XML, on GitHub, GitLab, or no host, with any agent that can read markdown and run a script.

## Users and roles

- **Person** (project owner or developer): installs Test Kitchen, answers definition questions, decides DECs, approves checkpoints, and merges when the autonomy setting says a person merges.
- **Agent**: follows the playbooks to define and deliver; proposes and records, never decides.
- **Reviewer**: a read-only agent with fresh context that reviews plans, tests, diffs, and tickets.

## Capabilities

- `INST` Install and update: install into a repository, update it, check it with doctor.
- `CONF` Configuration and conventions: `kitchen.yml`, globs, tags, IDs, the no-trace marker.
- `DEF` Definition: backlog and requirement conventions, `/define`, `backlog_check.py`.
- `DLV` Delivery: `/deliver`, `deliver.py` gates, status, release notes, fresh-context reviews.
- `HOST` Host adapters: GitHub, GitLab, or a manual host, and their CI templates.
- `GRD` Merge guard: the Claude Code hook that holds pushes, merges, and protected edits to the rules.

## Boundaries

- The guard is a guardrail against mistakes, not a sandbox, and only Claude Code enforces it.
- No sync with external trackers, no uninstall command, no example project.
- Not yet: a traceability report, learning from reviews, richer delivery-record data.
