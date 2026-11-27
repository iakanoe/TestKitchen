# Changelog

Test Kitchen follows semantic versioning. Each release has a `## x.y.z — date` section, newest first, listing its changes and its migration notes: what a project on the previous version must do after `init.py update`. `init.py update` prints the migration notes of every release between the installed version and the new one, so every release keeps a `### Migration notes` subsection, even when it only says "None". Changes not yet released collect under `## Unreleased`, which becomes the next `## x.y.z — date` section when that release is tagged; `init.py update` reads versioned sections only.

## Unreleased

### Changed

- The guard refuses, instead of asking, a call made in a subagent that it would ask about (the hook input carries an `agent_id`), keeping the ask's reasons and telling the subagent to hand the step back to the main session. In auto permission mode a subagent's asks were approved by a classifier rather than the person. The sandbox opt-in (`KITCHEN_GUARD_SANDBOX=1`) applies first; a force push from a subagent is refused.
- The `/define` skill tells the agent to read `playbooks/define.md` in full first, then `backlog/README.md` and `AGENTS.md`, with the file-read tool, one file per call, never combined with other commands in one shell call, so a combined call no longer overflows into a saved file that is read twice.

### Fixed

- `backlog_check.py --gaps` no longer reports an installed but undefined project as fully defined. It now lists a missing or skeleton-only `docs/product.md`, a project with no requirements, and existing code while no epic claims any with `code:`.

### Migration notes

- After updating, steps a subagent ran that the guard asks about (protected edits, git settings, host writes, force pushes) are refused in the subagent; run them from the main session, where you are asked.
- After updating, `--gaps` may list new lines for projects that never filled `docs/product.md`, defined no requirements, or gave no epic `code:` globs. Close them with `/define` (`new`, `adopt`, or `sweep`).

## 0.1.0 — 2026-11-25

### Added

- Conventions for requirements (`docs/requirements/<CODE>-<name>.md`, IDs such as `PAY-R03`, `(observed in code)` and `(superseded …)` markers), architecture decisions (`docs/architecture/ADR-nnn-<slug>.md`), and the decision log (`docs/decision-log.md`).
- Tickets in `backlog/`: epics, stories, tasks, decisions, and spikes, with stable IDs, YAML frontmatter, acceptance criteria numbered for good, open questions with interim behavior, readiness rules, optional priority, release slices, hotfix and bug-fix fields.
- Test tags in two equivalent forms, `[US-PAY-03/AC2]` and `us_pay_03_ac2`, read from JUnit XML, so any language can prove a criterion.
- `kitchen.yml` with three required keys (`tests`, `code`, `test_command`) and optional ones (`check_command`, `verify`, `host`, `autonomy`, `split_threshold`, `self_contained_tickets`, `releases`, `ignore`).
- `scripts/backlog_check.py`: validation, requirement coverage, `--gaps`, `--refine`, `--test-debt`, change-request description checks, `--self-test`.
- `scripts/deliver.py`: `next`, `context`, `pr-body`, `gate red`, `record`, `gate pr`, `gate merge`, `merge-command`, `check`, `status`, `release-notes`, `--self-test`.
- Host adapters for GitHub (`gh`), GitLab (`glab`), and a manual host where a person merges.
- Playbooks: `playbooks/deliver.md` (the 14-step delivery process with variants for tasks, bug fixes, hotfixes, spikes, and decisions), `playbooks/define.md` (modes new, change, sweep, refine, adopt, slice, bug, hotfix, ask), and `playbooks/review.md` (the fresh-context reviewer in plan, tests, diff, and ticket modes).
- Autonomy levels: `merge` (the agent merges on green), `pr` (a person merges), `supervised` (a person also approves the plan and the tests).
- Claude Code integration: `/deliver` and `/define` skills, the `ticket-reviewer` agent, and the guard hook that refuses unsafe pushes and any merge the gate has not passed.
- CI templates: a GitHub Actions workflow and a GitLab CI pipeline, each with a `check` job.
- `init.py`: install (with guessed answers, a plan, `--dry-run`, side-by-side copies instead of overwrites, and `kitchen.lock`), `update` (keep / take / diff on conflicts, migration notes), and `doctor`.
- `AGENT-INSTALL.md`: instructions an AI agent follows to install Test Kitchen.
- The user guide in `guide/` and `kitchen.yml` examples in `examples/`.
- The `test-kitchen: no-trace` marker: a file holding example tickets as data (tests of a tool that handles tickets) is left out of the trace scans, and its tags prove nothing. Test Kitchen's own files listed in `kitchen.lock` are never scanned.
- Gates that see merge commits: code written inside a merge (a conflict resolution after the review, an implementation before the freeze) counts as a change, and a clean merge of the default branch still passes.
- A change request with no ticket that touches code or tests needs a final review.

### Migration notes

- None: first release.
