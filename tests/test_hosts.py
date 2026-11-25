# test-kitchen: no-trace (the tickets, tags, and TODOs in this file are test data)
"""Tests for template/scripts/hosts.py: the github, gitlab, and manual adapters.

Fake `gh` and `glab` executables (tests/fakes/fake_cli.py) are put first on PATH and answer
from recorded JSON, so the adapters' exact commands and parsing are tested without the
network or an account. A real bare `origin` supplies pushed branches.

Run: python3 -m unittest discover -s tests -p 'test_hosts.py'
"""
import json
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers.kitchen_project import SCRIPTS, Project  # noqa: E402

# Import the scripts under test without writing __pycache__ into template/ (init copies that folder).
sys.dont_write_bytecode = True
sys.path.insert(0, str(SCRIPTS))
import hosts  # noqa: E402
import kitchen_lib as kl  # noqa: E402

SHA = "a" * 40
OLD = "b" * 40


def cfg(host):
    return kl.parse_config({"tests": ["tests/**"], "code": ["src/**"], "test_command": "x", "host": host})


class HostCase(unittest.TestCase):
    def setUp(self):
        self.p = Project()
        self.addCleanup(self.p.close)
        patcher = mock.patch.dict(os.environ, self.p.env(), clear=True)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.p.git("push", "-q", "origin", "HEAD:refs/heads/us-pay-09-pushed")

    def host(self, name):
        return hosts.get_host(cfg(name), self.p.root)


class GitHubTest(HostCase):
    PR = {"number": 7, "state": "OPEN", "isDraft": False, "baseRefName": "main", "headRefName": "us-pay-01-x",
          "headRefOid": SHA, "mergeable": "MERGEABLE", "body": "## Ticket\n\nUS-PAY-01", "url": "https://h/pr/7",
          "statusCheckRollup": [{"name": "check", "workflowName": "check", "status": "COMPLETED", "conclusion": "SUCCESS",
                                 "startedAt": "2026-01-01T10:00:00Z"}]}

    def view(self, **change):
        pr = dict(self.PR, **change)
        self.p.rules([{"cli": "gh", "args": ["pr", "view", "7", "--json", hosts.GITHUB_FIELDS], "stdout": json.dumps(pr)}])
        return self.host("github").view(7)

    def test_view_maps_every_field(self):
        cr = self.view()
        self.assertEqual((cr.number, cr.state, cr.draft, cr.base, cr.head_branch, cr.head_sha, cr.mergeable, cr.url),
                         (7, "open", False, "main", "us-pay-01-x", SHA, True, "https://h/pr/7"))
        self.assertEqual(cr.body, "## Ticket\n\nUS-PAY-01")
        self.assertEqual([(c.name, c.state) for c in cr.checks], [("check", "pass")])
        self.assertEqual(self.p.calls(), [{"cli": "gh", "args": ["pr", "view", "7", "--json", hosts.GITHUB_FIELDS]}])

    def test_states_and_mergeability(self):
        for change, want in [({"state": "MERGED"}, ("merged", True)), ({"state": "CLOSED", "mergeable": "CONFLICTING"}, ("closed", False)),
                             ({"mergeable": "UNKNOWN"}, ("open", None))]:
            with self.subTest(change=change):
                cr = self.view(**change)
                self.assertEqual((cr.state, cr.mergeable), want)

    def test_only_the_latest_run_of_each_check_counts(self):
        failed = {"name": "check", "workflowName": "check", "status": "COMPLETED", "conclusion": "FAILURE",
                  "startedAt": "2026-01-01T10:00:00Z"}
        passed = dict(failed, conclusion="SUCCESS", startedAt="2026-01-01T10:05:00Z")
        self.assertEqual([c.state for c in self.view(statusCheckRollup=[failed, passed]).checks], ["pass"])
        later_fail = dict(failed, startedAt="2026-01-01T10:09:00Z")
        self.assertEqual([c.state for c in self.view(statusCheckRollup=[passed, later_fail]).checks], ["fail"])

    def test_check_states(self):
        rollup = [
            {"name": "a", "status": "IN_PROGRESS"},
            {"name": "b", "status": "COMPLETED", "conclusion": "SKIPPED"},
            {"name": "c", "status": "COMPLETED", "conclusion": "NEUTRAL"},
            {"name": "d", "status": "COMPLETED", "conclusion": "CANCELLED"},
            {"name": "e", "status": "COMPLETED", "conclusion": "TIMED_OUT"},
            {"context": "ci/ext", "state": "PENDING"},
            {"context": "ci/ok", "state": "SUCCESS"},
            {"context": "ci/bad", "state": "ERROR"},
        ]
        got = {c.name: c.state for c in self.view(statusCheckRollup=rollup).checks}
        self.assertEqual(got, {"a": "pending", "b": "skipped", "c": "skipped", "d": "fail", "e": "fail",
                               "ci/ext": "pending", "ci/ok": "pass", "ci/bad": "fail"})

    def test_open_branches_adds_pushed_branches(self):
        self.p.rules([{"cli": "gh", "args": ["pr", "list", "--state", "open", "--json", "headRefName"],
                       "stdout": json.dumps([{"headRefName": "us-pay-02-open"}])}])
        self.assertEqual(self.host("github").open_branches(), {"us-pay-02-open", "us-pay-09-pushed", "main"})

    def test_cli_failures_raise(self):
        self.p.rules([{"cli": "gh", "args": ["pr"], "stderr": "not logged in", "exit": 4}])
        with self.assertRaises(hosts.HostError) as e:
            self.host("github").view(7)
        self.assertIn("not logged in", str(e.exception))
        os.environ["PATH"] = os.pathsep.join(p for p in os.environ["PATH"].split(os.pathsep) if p != str(self.p.bin))
        h = self.host("github")
        h.cli = "gh-does-not-exist"
        with self.assertRaises(hosts.HostError) as e:
            h.view(7)
        self.assertIn("not installed", str(e.exception))

    def test_merge_command_pins_the_head(self):
        self.assertEqual(self.host("github").merge_argv(7, SHA), ["gh", "pr", "merge", "7", "--merge", "--match-head-commit", SHA])
        for number, sha in [(7, "abc"), (7, SHA.upper()), ("7; rm", SHA), (0, SHA), ("", SHA)]:
            with self.subTest(number=number, sha=sha):
                with self.assertRaises(ValueError):
                    self.host("github").merge_argv(number, sha)


class GitLabTest(HostCase):
    MR = {"iid": 7, "state": "opened", "draft": False, "target_branch": "main", "source_branch": "us-pay-01-x",
          "sha": SHA, "detailed_merge_status": "mergeable", "description": "## Ticket\n\nUS-PAY-01",
          "web_url": "https://h/mr/7", "head_pipeline": {"id": 55, "sha": SHA, "status": "success"}}
    JOBS = "projects/:fullpath/pipelines/55/jobs"

    def view(self, jobs=(), **change):
        mr = dict(self.MR, **change)
        pages = "\n".join(json.dumps(page) for page in jobs) or "[]"
        self.p.rules([{"cli": "glab", "args": ["mr", "view", "7", "--output", "json"], "stdout": json.dumps(mr)},
                      {"cli": "glab", "args": ["api", "--paginate", self.JOBS], "stdout": pages}])
        return self.host("gitlab").view(7)

    def test_view_maps_every_field_and_reads_the_head_pipeline_jobs(self):
        jobs = [[{"id": 1, "name": "check", "status": "failed"}], [{"id": 2, "name": "check", "status": "success"},
                                                                    {"id": 3, "name": "lint", "status": "success"}]]
        cr = self.view(jobs)
        self.assertEqual((cr.number, cr.state, cr.draft, cr.base, cr.head_branch, cr.head_sha, cr.mergeable, cr.url),
                         (7, "open", False, "main", "us-pay-01-x", SHA, True, "https://h/mr/7"))
        self.assertEqual(sorted((c.name, c.state) for c in cr.checks), [("check", "pass"), ("lint", "pass")])
        self.assertEqual([c["args"] for c in self.p.calls()],
                         [["mr", "view", "7", "--output", "json"], ["api", "--paginate", self.JOBS]])

    def test_job_states(self):
        statuses = ["success", "failed", "canceled", "skipped", "manual", "running", "pending", "created",
                    "waiting_for_resource", "scheduled"]
        jobs = [[{"id": i, "name": s, "status": s} for i, s in enumerate(statuses)]
                + [{"id": 50, "name": "allowed", "status": "failed", "allow_failure": True},
                   {"id": 51, "name": "optional-manual", "status": "manual", "allow_failure": True}]]
        got = {c.name: c.state for c in self.view(jobs).checks}
        self.assertEqual(got, {"success": "pass", "failed": "fail", "canceled": "fail", "skipped": "skipped",
                               "manual": "pending", "running": "pending", "pending": "pending", "created": "pending",
                               "waiting_for_resource": "pending", "scheduled": "pending", "allowed": "skipped",
                               "optional-manual": "skipped"})

    def test_a_pipeline_for_another_commit_does_not_count(self):
        cr = self.view([[{"id": 1, "name": "check", "status": "success"}]], head_pipeline={"id": 55, "sha": OLD})
        self.assertEqual([c.state for c in cr.checks], ["pending"])
        self.assertIn("ran on bbbbbbbb", cr.checks[0].name)
        cr = self.view(head_pipeline=None)
        self.assertEqual(cr.checks, [])
        self.assertEqual(len(self.p.calls()), 3)  # no jobs call without a pipeline

    def test_states_and_mergeability(self):
        cases = [({"state": "merged"}, "merged", True), ({"state": "locked"}, "locked", True),
                 ({"detailed_merge_status": "checking"}, "open", None), ({"detailed_merge_status": "unchecked"}, "open", None),
                 ({"detailed_merge_status": "conflict"}, "open", False), ({"detailed_merge_status": "need_rebase"}, "open", False),
                 ({"detailed_merge_status": "not_approved"}, "open", False),
                 ({"detailed_merge_status": None, "merge_status": "can_be_merged"}, "open", True),
                 ({"detailed_merge_status": None, "merge_status": "cannot_be_merged"}, "open", False)]
        for change, state, mergeable in cases:
            with self.subTest(change=change):
                cr = self.view(**change)
                self.assertEqual((cr.state, cr.mergeable), (state, mergeable))
        self.assertTrue(self.view(draft=True).draft)
        self.assertTrue(self.view(draft=None, work_in_progress=True).draft)

    def test_open_branches_pages_through_open_merge_requests(self):
        page1 = [{"source_branch": f"b{i}"} for i in range(100)]
        args = ["mr", "list", "--output", "json", "--per-page", "100", "--page"]
        self.p.rules([{"cli": "glab", "args": args + ["1"], "stdout": json.dumps(page1)},
                      {"cli": "glab", "args": args + ["2"], "stdout": json.dumps([{"source_branch": "us-pay-02-open"}])}])
        got = self.host("gitlab").open_branches()
        self.assertEqual(len(got), 103)
        self.assertTrue({"b0", "b99", "us-pay-02-open", "us-pay-09-pushed"} <= got)

    def test_merge_command_pins_the_head_and_never_defers(self):
        self.assertEqual(self.host("gitlab").merge_argv("7", SHA),
                         ["glab", "mr", "merge", "7", "--sha", SHA, "--auto-merge=false", "--yes"])
        with self.assertRaises(ValueError):
            self.host("gitlab").merge_argv(7, "HEAD")


class ManualTest(HostCase):
    def test_manual_host_has_no_cli(self):
        h = self.host("manual")
        self.assertEqual((h.name, h.word), ("manual", "change request"))
        self.assertIsNone(h.merge_argv(7, SHA))
        with self.assertRaises(hosts.NotSupported):
            h.view(7)
        self.assertEqual(h.open_branches(), {"main", "us-pay-09-pushed"})
        self.assertEqual(self.p.calls(), [])

    def test_no_origin_means_no_pushed_branches(self):
        self.p.git("remote", "remove", "origin")
        self.assertEqual(self.host("manual").open_branches(), set())

    def test_an_unreachable_origin_fails_closed(self):
        self.p.git("remote", "set-url", "origin", str(self.p.tmp / "missing.git"))
        with self.assertRaises(hosts.HostError):
            self.host("manual").open_branches()

    def test_get_host_and_words(self):
        for name, word, cli in [("github", "pull request", "gh"), ("gitlab", "merge request", "glab"),
                                ("manual", "change request", None)]:
            h = self.host(name)
            self.assertEqual((h.name, h.word, h.cli), (name, word, cli))

    def test_self_test(self):
        code, out = self.p.run("hosts.py", "--self-test")
        self.assertEqual(code, 0, out)
        self.assertIn("PASS self-test", out)


if __name__ == "__main__":
    unittest.main()
