"""Host adapters: how the scripts read change requests and the one way each host merges them.

A host is where change requests live: GitHub (pull requests, through the `gh` CLI),
GitLab (merge requests, through the `glab` CLI), or `manual` (no CLI: a person reads and
merges change requests). `deliver.py` (next, gate merge, merge-command) and the Claude
Code guard talk to the host only through this interface, so adding a host means adding
one class here (guide/hosts.md documents the interface).

    Host.name, Host.word          "github" / "pull request", "gitlab" / "merge request", "manual" / "change request"
    Host.open_branches() -> set   head branches of open change requests, plus branches pushed to origin
    Host.view(number) -> ChangeRequest   raises NotSupported on manual, HostError when the CLI fails
    Host.merge_argv(number, sha) -> list | None   the only allowed merge command; None on manual
    get_host(cfg, root) -> Host

Every merge command pins the head commit the checks passed on, so nothing pushed after
the merge gate ran can be merged with it, and none enables auto-merge (a deferred merge
would land later, after the gate's view went stale).

Usage from the command line:

    python3 scripts/hosts.py --self-test   # parses recorded gh/glab output; prints "PASS self-test"; exit 0/1

Standard library only (plus kitchen_lib). Python 3.9 compatible.
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kitchen_lib  # noqa: E402

SHA = re.compile(r"^[0-9a-f]{40}$")


@dataclass
class Check:
    """One CI check (GitHub check run or status, GitLab job) on the change request's head."""
    name: str
    state: str  # "pass" | "fail" | "pending" | "skipped"


@dataclass
class ChangeRequest:
    """A change request as the merge gate needs it, the same shape on every host."""
    number: int
    state: str  # "open" | "merged" | "closed" (GitLab's transient "locked" is passed through)
    draft: bool
    base: str  # target branch
    head_branch: str
    head_sha: str
    mergeable: Optional[bool]  # True, False, or None when the host has not decided yet
    body: str  # the description, raw markdown
    checks: List[Check] = field(default_factory=list)
    url: str = ""
    mergeable_detail: str = ""  # the host's own word for mergeability, for messages


class HostError(Exception):
    """The host CLI is missing, signed out, or failed."""


class NotSupported(HostError):
    """The host has no CLI for this (the manual host)."""


def _merge_args(number, sha):
    """Validate a merge's change-request number and head sha; ValueError when malformed (fail closed)."""
    n = str(number).strip()
    if not n.isdigit() or int(n) < 1:
        raise ValueError(f"change request number must be a positive integer, got {number!r}")
    if not SHA.match(str(sha)):
        raise ValueError(f"head sha must be the full 40-character commit sha, got {sha!r}")
    return str(int(n)), str(sha)


def _json_values(text):
    """Every JSON value in `text`: one document, several concatenated (paginated CLI output), or one per line."""
    dec, i, out, text = json.JSONDecoder(), 0, [], (text or "").strip()
    while i < len(text):
        value, i = dec.raw_decode(text, i)
        out.append(value)
        while i < len(text) and text[i].isspace():
            i += 1
    return out


def _items(text):
    """The objects in a CLI's JSON list output, flattening per-page arrays."""
    items = []
    for v in _json_values(text):
        items.extend(v if isinstance(v, list) else [v])
    return [x for x in items if isinstance(x, dict)]


class Host:
    """The manual host, and the base of the others: no CLI, only git."""
    name = "manual"
    word = "change request"
    cli = None

    def __init__(self, root, cfg=None):
        self.root = Path(root)
        self.cfg = cfg

    def pushed_branches(self):
        """Branch names on origin (`git ls-remote --heads origin`); empty when there is no origin remote.

        A branch pushed without a change request still claims its ticket. When origin exists
        but cannot be listed, this raises: claims must not be guessed.
        """
        remotes = kitchen_lib.run(kitchen_lib.git_argv("remote"), self.root).stdout.split()
        if "origin" not in remotes:
            return set()
        r = kitchen_lib.run(kitchen_lib.git_argv("ls-remote", "--heads", "origin"), self.root)
        if r.returncode:
            raise HostError(f"git ls-remote --heads origin failed: {r.stderr.strip()}")
        return {line.split("refs/heads/", 1)[1] for line in r.stdout.splitlines() if "refs/heads/" in line}

    def open_branches(self):
        return self.pushed_branches()

    def view(self, number):
        raise NotSupported(f"the manual host has no CLI to read change request {number}: a person checks and merges it")

    def merge_argv(self, number, sha):
        """The only allowed merge command, as argv; None on the manual host (a person merges)."""
        return None

    def _cli(self, *args):
        try:
            r = kitchen_lib.run([self.cli, *args], self.root)
        except FileNotFoundError:
            raise HostError(f"`{self.cli}` is not installed or not on PATH; the {self.name} host needs it")
        if r.returncode:
            raise HostError(f"`{self.cli} {' '.join(args)}` failed: {(r.stderr or r.stdout).strip()}")
        return r.stdout


# --- GitHub -------------------------------------------------------------------------------

GITHUB_FIELDS = "number,state,isDraft,baseRefName,headRefName,headRefOid,mergeable,body,statusCheckRollup,url"


def github_check_state(c):
    """A statusCheckRollup entry as pass / fail / pending / skipped.

    Check runs have status + conclusion; commit statuses (StatusContext) have only state.
    Anything not clearly passed or skipped is a failure, so an unknown value fails closed.
    """
    if "conclusion" not in c and ("context" in c or c.get("__typename") == "StatusContext"):
        st = str(c.get("state") or "").upper()
        return {"SUCCESS": "pass", "PENDING": "pending", "EXPECTED": "pending"}.get(st, "fail")
    if str(c.get("status") or "COMPLETED").upper() != "COMPLETED":
        return "pending"
    conclusion = str(c.get("conclusion") or "").upper()
    if conclusion == "SUCCESS":
        return "pass"
    if conclusion in ("SKIPPED", "NEUTRAL"):
        return "skipped"
    return "fail"


def github_checks(rollup):
    """Only the latest run of each check counts, as on GitHub's own page.

    Editing a description reruns the check, and the earlier run on the same head stays in
    the rollup; without this, a fixed description would still show the old failure (or an
    old pass would hide a new failure). Runs are keyed by workflow and check name and
    ordered by start time; ISO 8601 timestamps sort as text.
    """
    latest = {}
    for c in rollup or []:
        key = (c.get("workflowName"), c.get("name") or c.get("context"))
        if key not in latest or (c.get("startedAt") or "") >= (latest[key].get("startedAt") or ""):
            latest[key] = c
    return [Check(name=str(c.get("name") or c.get("context") or "?"), state=github_check_state(c))
            for c in latest.values()]


def github_change_request(pr):
    """`gh pr view --json` output as a ChangeRequest."""
    mergeable = str(pr.get("mergeable") or "UNKNOWN").upper()
    return ChangeRequest(
        number=int(pr.get("number") or 0),
        state={"OPEN": "open", "MERGED": "merged", "CLOSED": "closed"}.get(str(pr.get("state")).upper(),
                                                                         str(pr.get("state")).lower()),
        draft=bool(pr.get("isDraft")),
        base=pr.get("baseRefName") or "",
        head_branch=pr.get("headRefName") or "",
        head_sha=pr.get("headRefOid") or "",
        mergeable={"MERGEABLE": True, "CONFLICTING": False}.get(mergeable),
        body=pr.get("body") or "",
        checks=github_checks(pr.get("statusCheckRollup")),
        url=pr.get("url") or "",
        mergeable_detail=mergeable,
    )


class GitHub(Host):
    """Pull requests through the GitHub CLI (https://cli.github.com/manual/)."""
    name = "github"
    word = "pull request"
    cli = "gh"

    def open_branches(self):
        # https://cli.github.com/manual/gh_pr_list (--state open, --json headRefName, --limit)
        out = self._cli("pr", "list", "--state", "open", "--json", "headRefName", "--limit", "1000")
        return {p["headRefName"] for p in _items(out) if p.get("headRefName")} | self.pushed_branches()

    def view(self, number):
        # https://cli.github.com/manual/gh_pr_view (--json with the fields in GITHUB_FIELDS)
        number, _ = _merge_args(number, "0" * 40)
        out = self._cli("pr", "view", number, "--json", GITHUB_FIELDS)
        return github_change_request(json.loads(out))

    def merge_argv(self, number, sha):
        # https://cli.github.com/manual/gh_pr_merge: --merge makes a merge commit;
        # --match-head-commit refuses the merge unless the head is still that sha. Never
        # --auto (a deferred merge) or --admin (bypasses requirements).
        n, sha = _merge_args(number, sha)
        return ["gh", "pr", "merge", n, "--merge", "--match-head-commit", sha]


# --- GitLab -------------------------------------------------------------------------------
#
# Verified against the official docs (2026-11-24):
#   glab mr list   https://gitlab.com/gitlab-org/cli/-/blob/main/docs/source/mr/list.md
#                  (open by default; -F/--output json; -P/--per-page, default 30; -p/--page)
#   glab mr view   https://gitlab.com/gitlab-org/cli/-/blob/main/docs/source/mr/view.md
#                  (-F/--output json prints the merge request object of the REST API below)
#   glab mr merge  https://gitlab.com/gitlab-org/cli/-/blob/main/docs/source/mr/merge.md
#                  (--sha "Merge only if the HEAD of the source branch matches this SHA";
#                   --auto-merge "Set auto-merge. (default true)", so it is turned off
#                   explicitly; -y/--yes skips the confirmation prompt)
#   glab api       https://gitlab.com/gitlab-org/cli/-/blob/main/docs/source/api/_index.md
#                  (GET by default without fields; :fullpath placeholder; --paginate)
#   MR fields      https://docs.gitlab.com/api/merge_requests/ (state opened/closed/merged/locked;
#                  draft; sha; detailed_merge_status; head_pipeline {id, sha, status})
#   Pipeline jobs  https://docs.gitlab.com/api/jobs/ (GET /projects/:id/pipelines/:pipeline_id/jobs;
#                  retried jobs are left out by default, so each job name is its latest run)

# detailed_merge_status values that mean "not decided yet" rather than "cannot merge".
GITLAB_UNDECIDED = {"checking", "unchecked", "preparing", "approvals_syncing"}


def gitlab_mergeable(mr):
    """True only for detailed_merge_status `mergeable`; None while GitLab is still checking; else False.

    Every other value (conflict, need_rebase, not_approved, discussions_not_resolved,
    ci_must_pass, draft_status, ...) blocks the merge, which is the safe reading. Older
    GitLab versions without detailed_merge_status fall back to the deprecated merge_status.
    """
    detail = mr.get("detailed_merge_status")
    if detail:
        return True if detail == "mergeable" else None if detail in GITLAB_UNDECIDED else False
    return {"can_be_merged": True, "cannot_be_merged": False}.get(mr.get("merge_status"))


def gitlab_check_state(job):
    """A pipeline job's status as pass / fail / pending / skipped.

    A failed job marked `allow_failure` does not fail the pipeline on GitLab, so it is
    skipped here (the `check` job itself must still succeed). A manual job is pending unless
    it is allowed to fail (GitLab's non-blocking manual job). Unknown statuses are pending.
    """
    st = job.get("status")
    if st == "success":
        return "pass"
    if st == "failed":
        return "skipped" if job.get("allow_failure") else "fail"
    if st in ("canceled", "canceling"):
        return "fail"
    if st == "skipped":
        return "skipped"
    if st == "manual":
        return "skipped" if job.get("allow_failure") else "pending"
    return "pending"


def gitlab_checks(jobs):
    """The latest job per name (highest id), as Checks."""
    latest = {}
    for j in jobs or []:
        name = str(j.get("name") or "?")
        if name not in latest or (j.get("id") or 0) >= (latest[name].get("id") or 0):
            latest[name] = j
    return [Check(name=n, state=gitlab_check_state(j)) for n, j in latest.items()]


def gitlab_change_request(mr, jobs):
    """`glab mr view --output json` output plus its head pipeline's jobs, as a ChangeRequest.

    The jobs count only when the head pipeline ran on the head commit. Otherwise (no
    pipeline yet, or one for an older commit, or a merged-results pipeline, which runs on
    a merge commit and is not supported in this version) a pending pseudo-check says so, and the
    merge gate fails closed.
    """
    head = mr.get("sha") or (mr.get("diff_refs") or {}).get("head_sha") or ""
    pipeline = mr.get("head_pipeline") or {}
    if pipeline and pipeline.get("sha") == head:
        checks = gitlab_checks(jobs)
    elif pipeline:
        checks = [Check(name=f"pipeline on the head commit (pipeline {pipeline.get('id')} ran on "
                             f"{str(pipeline.get('sha'))[:8]})", state="pending")]
    else:
        checks = []
    state = mr.get("state") or ""
    return ChangeRequest(
        number=int(mr.get("iid") or 0),
        state={"opened": "open", "merged": "merged", "closed": "closed"}.get(state, state),
        draft=bool(mr.get("draft") or mr.get("work_in_progress")),
        base=mr.get("target_branch") or "",
        head_branch=mr.get("source_branch") or "",
        head_sha=head,
        mergeable=gitlab_mergeable(mr),
        body=mr.get("description") or "",
        checks=checks,
        url=mr.get("web_url") or "",
        mergeable_detail=str(mr.get("detailed_merge_status") or mr.get("merge_status") or "unknown"),
    )


class GitLab(Host):
    """Merge requests through the GitLab CLI (sources cited above)."""
    name = "gitlab"
    word = "merge request"
    cli = "glab"
    PER_PAGE = 100
    MAX_PAGES = 50  # 5000 open merge requests; a bound so a misbehaving CLI cannot loop forever

    def open_branches(self):
        # glab mr list: open merge requests by default; JSON objects carry `source_branch`.
        names = set()
        for page in range(1, self.MAX_PAGES + 1):
            items = _items(self._cli("mr", "list", "--output", "json", "--per-page", str(self.PER_PAGE),
                                     "--page", str(page)))
            names |= {m["source_branch"] for m in items if m.get("source_branch")}
            if len(items) < self.PER_PAGE:
                break
        return names | self.pushed_branches()

    def view(self, number):
        number, _ = _merge_args(number, "0" * 40)
        mr = json.loads(self._cli("mr", "view", number, "--output", "json"))
        pipeline = mr.get("head_pipeline") or {}
        jobs = []
        if pipeline.get("id"):
            # GET is glab api's default without fields; --paginate fetches every page.
            jobs = _items(self._cli("api", "--paginate", f"projects/:fullpath/pipelines/{int(pipeline['id'])}/jobs"))
        return gitlab_change_request(mr, jobs)

    def merge_argv(self, number, sha):
        # Pinned to the head sha (--sha) and merged now, never queued (--auto-merge=false),
        # without an interactive prompt (--yes). The merge method is the project's setting.
        n, sha = _merge_args(number, sha)
        return ["glab", "mr", "merge", n, "--sha", sha, "--auto-merge=false", "--yes"]


HOSTS = {"github": GitHub, "gitlab": GitLab, "manual": Host}


def get_host(cfg, root):
    """The adapter for `cfg.host` (from kitchen.yml, or detected from the origin URL)."""
    return HOSTS.get(cfg.host, Host)(root, cfg)


# --- self-test ----------------------------------------------------------------------------

def self_test():
    """Parse recorded host output; return a list of failures. No CLI or network is used."""
    failures = []

    def expect(what, got, want):
        if got != want:
            failures.append(f"{what}: got {got!r}, want {want!r}")

    sha = "a" * 40
    old = {"name": "check", "workflowName": "check", "status": "COMPLETED", "conclusion": "FAILURE",
           "startedAt": "2026-01-01T10:00:00Z"}
    new = dict(old, conclusion="SUCCESS", startedAt="2026-01-01T10:05:00Z")
    pr = github_change_request({"number": 7, "state": "OPEN", "isDraft": False, "baseRefName": "main",
                                "headRefName": "us-pay-03-x", "headRefOid": sha, "mergeable": "MERGEABLE",
                                "body": "b", "statusCheckRollup": [old, new], "url": "u"})
    expect("github latest run wins", [(c.name, c.state) for c in pr.checks], [("check", "pass")])
    expect("github state", (pr.state, pr.mergeable), ("open", True))
    mr = gitlab_change_request({"iid": 7, "state": "opened", "draft": False, "target_branch": "main",
                                "source_branch": "us-pay-03-x", "sha": sha, "detailed_merge_status": "mergeable",
                                "description": "b", "head_pipeline": {"id": 1, "sha": sha}},
                               [{"id": 1, "name": "check", "status": "failed"},
                                {"id": 2, "name": "check", "status": "success"},
                                {"id": 3, "name": "lint", "status": "failed", "allow_failure": True}])
    expect("gitlab checks", sorted((c.name, c.state) for c in mr.checks), [("check", "pass"), ("lint", "skipped")])
    expect("gitlab undecided", gitlab_mergeable({"detailed_merge_status": "checking"}), None)
    expect("gitlab conflict", gitlab_mergeable({"detailed_merge_status": "conflict"}), False)
    expect("gitlab merge", GitLab(".").merge_argv(7, sha),
           ["glab", "mr", "merge", "7", "--sha", sha, "--auto-merge=false", "--yes"])
    expect("github merge", GitHub(".").merge_argv("7", sha),
           ["gh", "pr", "merge", "7", "--merge", "--match-head-commit", sha])
    expect("manual merge", Host(".").merge_argv(7, sha), None)
    expect("paginated json", len(_items('[{"a": 1}]\n[{"a": 2}]')), 2)
    try:
        GitHub(".").merge_argv(7, "abc")
        failures.append("a short sha was accepted")
    except ValueError:
        pass
    return failures


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        problems = self_test()
        for p in problems:
            print("FAIL", p)
        print("PASS self-test" if not problems else f"FAIL self-test: {len(problems)} failure(s)")
        sys.exit(1 if problems else 0)
    print(__doc__)
    sys.exit(2)
