# Hosts

A host is where change requests live: GitHub pull requests, GitLab merge requests, or nothing at all. Everything host-specific goes through one adapter in `scripts/hosts.py`; the rest of Test Kitchen says "change request" and asks the adapter.

## Choosing the host

`host:` in `kitchen.yml` sets it. When absent, it is detected from `git remote get-url origin`: a `github.com` URL means `github`, a URL containing "gitlab" means `gitlab`, anything else, or no remote, means `manual`. GitHub Enterprise and self-hosted GitLab instances whose URL does not say so need `host:` set.

The installer uses the same detection (or `--host`) to decide which CI files to install. To switch hosts later, set `host:` and run the installer again with `update --host <host>` (`curl -fsSL https://raw.githubusercontent.com/iakanoe/TestKitchen/v0.1.0/init.py | python3 - update --host <host>`): the new host's files are added, and the old host's files are listed as no longer part of the install (never deleted).

## Host settings Test Kitchen needs

- **Merge commits allowed.** The only merge an agent may run creates a merge commit (`gh pr merge --merge`; on GitLab, the project's merge method must be "Merge commit"). Squash and rebase merges would rewrite the freeze commit and the reviewed commit, which the gates and the delivery records point at. A repository set to squash-only or rebase-only makes every merge fail.
- **GitLab: merged results pipelines off.** v0.1 reads the head pipeline of the merge request's own branch. A merged results pipeline tests a merge result instead, so the adapter reports it as pending and fails closed: the agent would wait forever. Keep "Enable merged results pipelines" off.
- **A CI job named `check`** that runs on every change request (the installed CI file does this).

## The adapters

### github

Uses the GitHub CLI, `gh`, signed in.

- Open change requests: `gh pr list --state open --json headRefName`.
- One change request: `gh pr view <n> --json state,isDraft,baseRefName,headRefName,headRefOid,mergeable,body,statusCheckRollup,url`. When a check ran several times, its latest run counts.
- The one allowed merge: `gh pr merge <n> --merge --match-head-commit <sha>`. GitHub then merges only that exact commit, so nothing pushed after the gate passed can ride along.
- CI: `.github/workflows/check.yml`, job `check`. On pull requests it also runs `backlog_check.py --pr-body` and `deliver.py gate pr` on the live description; the `edited` trigger re-runs it when the description changes.
- Description template: `.github/pull_request_template.md`.

### gitlab

Uses the GitLab CLI, `glab`, signed in: open merge requests, a merge request as JSON, the jobs of its head pipeline, and a merge pinned to the head commit with auto-merge off. Each command is checked against the official glab documentation, cited in `scripts/hosts.py`.

- CI: `.gitlab-ci.yml`, job `check`, with a full clone so the gates can read the branch history. In merge-request pipelines it runs `deliver.py gate pr --from-record`: the check reads the description from the branch's committed delivery record. Before merging, `gate merge` compares that record with the live description.
- Description template: `.gitlab/merge_request_templates/Default.md`.

### manual

No CLI and no CI files. Open branches are the branches pushed to `origin`. There is no change-request view and no merge command: the agent stops at "ready to merge" and a person merges. Run `python3 scripts/deliver.py check` (and `gate pr`) yourself before merging.

## What `gate merge` asks of every host

`deliver.py gate merge <n> --head=<sha>` refuses when: the change request's head is not `<sha>`; it is not open; it is a draft; its base is not the default branch; it is not mergeable, or mergeability is unknown; no `check` job passed on the head; any check failed or is pending; the local checkout is not a clean checkout of the head; the branch is behind `origin/<default>`; `backlog_check.py --pr-body` finds errors; or `gate pr` fails. On the manual host it prints that a person merges and exits 1.

Host branch protection, where your plan offers it (require the `check` job, forbid direct pushes to the default branch), is the only rule that holds even against a merge made outside the workflow. Turn it on when you can.

## The adapter interface

```python
@dataclass
class Check:
    name: str
    state: str            # "pass" | "fail" | "pending" | "skipped"

@dataclass
class ChangeRequest:
    number: int
    state: str            # "open" | "merged" | "closed"
    draft: bool
    base: str
    head_branch: str
    head_sha: str
    mergeable: bool | None   # None = unknown
    body: str
    checks: list[Check]
    url: str

class Host:
    name: str             # "github", "gitlab", "manual"
    word: str             # "pull request", "merge request", "change request"
    def open_branches(self) -> set[str]: ...              # heads of open change requests, plus pushed branches
    def view(self, number) -> ChangeRequest: ...          # raises NotSupported on manual
    def merge_argv(self, number, sha) -> list[str] | None: ...  # the one allowed merge command; None on manual

def get_host(cfg, root) -> Host: ...
```

`merge_argv` is the single definition of an allowed merge: `deliver.py merge-command` prints it, and the Claude Code guard allows a merge only when the command matches it exactly and `gate merge` passes.

## Adding a host

1. Add a `Host` subclass to `scripts/hosts.py` that implements `open_branches`, `view`, and `merge_argv` with the host's CLI, mapping its states onto `Check` and `ChangeRequest`. Pin the merge to the head commit; never use an auto-merge or admin option.
2. Register it in `get_host`, and add its name to the `host` values `scripts/kitchen_lib.py` accepts and detects.
3. Teach the guard (`.claude/hooks/guard.py`) which of the host CLI's commands are reads and workflow steps (allowed) and which are writes (asked).
4. Add CI and description templates under `template/<host>/`, with a job named `check` and the toolchain marker line, and teach `init.py` the new name: its `HOSTS` list, its `detect_host`, its `HOST_CLI` table, and the folder mapping in `map_template_path` (the installer maps host folders by name).
5. Add tests with a fake CLI executable on `PATH`, as `tests/test_hosts.py` does for the existing hosts. Tests never use the network.
