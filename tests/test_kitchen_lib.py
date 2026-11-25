# test-kitchen: no-trace (the tickets, tags, and TODOs in this file are test data)
"""Tests for template/scripts/kitchen_lib.py: config, globs, tags, IDs, git helpers.

Run: python3 -m unittest discover -s tests -p 'test_kitchen_lib.py'
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers.kitchen_project import GIT_ENV, SCRIPTS, Project  # noqa: E402

# Import the scripts under test without writing __pycache__ into template/ (init copies that folder).
sys.dont_write_bytecode = True
sys.path.insert(0, str(SCRIPTS))
import kitchen_lib as kl  # noqa: E402

BASE = {"tests": ["tests/**"], "code": ["src/**"], "test_command": "run {files} --junit {report}"}


class GlobTest(unittest.TestCase):
    def test_double_star_matches_any_number_of_segments_including_none(self):
        cases = [
            ("tests/**", "tests/a.py", True), ("tests/**", "tests/a/b/c.py", True), ("tests/**", "testsx/a.py", False),
            ("**/*.test.ts", "a.test.ts", True), ("**/*.test.ts", "x/y/a.test.ts", True),
            ("src/**/b.py", "src/b.py", True), ("src/**/b.py", "src/x/y/b.py", True), ("src/**/b.py", "src/xb.py", False),
            ("**", "anything/at/all", True),
        ]
        for pattern, path, want in cases:
            with self.subTest(pattern=pattern, path=path):
                self.assertEqual(kl.matches(path, [pattern]), want)

    def test_single_star_and_question_mark_stay_inside_a_segment(self):
        self.assertTrue(kl.matches("src/a.py", ["src/*.py"]))
        self.assertFalse(kl.matches("src/a/b.py", ["src/*.py"]))
        self.assertTrue(kl.matches("src/a.py", ["src/?.py"]))
        self.assertFalse(kl.matches("src/ab.py", ["src/?.py"]))
        self.assertFalse(kl.matches("src/a/b", ["src?a/b"]))

    def test_other_characters_are_literal(self):
        self.assertTrue(kl.matches("a[1].py", ["a[1].py"]))
        self.assertFalse(kl.matches("a1.py", ["a[1].py"]))
        self.assertTrue(kl.matches("src/x.py", ["./src/**"]))

    def test_tests_win_over_code_and_ignore_wins_over_both(self):
        cfg = kl.parse_config(dict(BASE, code=["src/**"], tests=["src/**/*_test.go", "tests/**"], ignore=["src/gen/**"]))
        self.assertTrue(kl.is_test("src/pay/x_test.go", cfg))
        self.assertFalse(kl.is_code("src/pay/x_test.go", cfg))
        self.assertTrue(kl.is_code("src/pay/x.go", cfg))
        self.assertFalse(kl.is_code("src/gen/x.go", cfg))
        self.assertFalse(kl.is_test("src/gen/x_test.go", cfg))


class TagTest(unittest.TestCase):
    def test_both_forms_and_tasks(self):
        cases = [
            ('it("[US-PAY-03/AC2] refunds are refused", …)', [("US-PAY-03", 2)]),
            ("describe [US-PAY-03/AC2] > refuses", [("US-PAY-03", 2)]),
            ("test_us_pay_03_ac2_refund_denied", [("US-PAY-03", 2)]),
            ("TestUS_PAY_03_AC2", [("US-PAY-03", 2)]),
            ("TestUS_PAY_03_AC2_RefundDenied", [("US-PAY-03", 2)]),
            ("tests.test_pay.Test_us_pay_03_ac12", [("US-PAY-03", 12)]),
            ("[TASK-CI-01/AC1] caches", [("TASK-CI-01", 1)]),
            ("test_task_ci_01_ac1", [("TASK-CI-01", 1)]),
            ("test_us_pay_03_ac1 and [US-PAY-04/AC2]", [("US-PAY-03", 1), ("US-PAY-04", 2)]),
        ]
        for text, want in cases:
            with self.subTest(text=text):
                self.assertEqual(kl.find_tags(text), want)

    def test_identifier_tags_must_be_bounded(self):
        for text in ("bonus_pay_03_ac2", "focus_pay_03_ac2", "us_pay_03_ac2x", "us_pay_03_ac2b",
                     "us_pay_3_ac2", "us_p_03_ac2", "[US-PAY-03/AC]", "[DEC-PAY-01/AC1]"):
            with self.subTest(text=text):
                self.assertEqual(kl.find_tags(text), [])


class IdTest(unittest.TestCase):
    def test_ticket_ids(self):
        self.assertEqual(kl.parse_ticket_id("US-PAY-03"), ("US", "PAY", "03"))
        self.assertEqual(kl.parse_ticket_id("TASK-CI2-100"), ("TASK", "CI2", "100"))
        self.assertEqual(kl.parse_ticket_id("EP-AUTH"), ("EP", "AUTH", None))
        for bad in ("US-PAY-3", "EP-PAY-01", "US-pay-03", "XX-PAY-03", "US-P-03", "US-ABCDEFGHIJK-01"):
            with self.subTest(bad=bad):
                self.assertIsNone(kl.parse_ticket_id(bad))

    def test_ticket_mentions_in_text(self):
        text = "See US-PAY-03/AC2, DEC-PAY-01, EP-PAY, but not XUS-PAY-03 or EP-PAY-01 or US-ASCII."
        self.assertEqual(kl.TICKET_REF.findall(text), ["US-PAY-03", "DEC-PAY-01", "EP-PAY"])

    def test_natural_order(self):
        ids = ["US-PAY-10", "US-PAY-9X", "US-PAY-02", "US-PAY-100"]
        self.assertEqual(sorted(ids[:1] + ids[2:], key=kl.ticket_sort_key), ["US-PAY-02", "US-PAY-10", "US-PAY-100"])


class ConfigTest(unittest.TestCase):
    def test_defaults(self):
        cfg = kl.parse_config(dict(BASE))
        self.assertEqual((cfg.autonomy, cfg.split_threshold, cfg.self_contained_tickets, cfg.releases, cfg.ignore),
                         ("merge", 6, False, None, []))
        self.assertTrue(cfg.host_detected)

    def test_every_invalid_value_gives_its_own_message(self):
        bad = {"tests": "tests/**", "code": [], "test_command": "", "host": "bitbucket", "autonomy": "always",
               "split_threshold": True, "self_contained_tickets": "yes", "releases": [], "ignore": [3], "colour": "x"}
        with self.assertRaises(kl.ConfigError) as e:
            kl.parse_config(bad)
        lines = str(e.exception).splitlines()
        self.assertEqual(len(lines), 10, lines)
        for word in ("unknown key `colour`", "`tests`", "`code`", "`test_command`", "`host`", "`autonomy`",
                     "`split_threshold`", "`self_contained_tickets`", "`releases`", "`ignore`"):
            self.assertTrue(any(word in line for line in lines), word)

    def test_required_keys(self):
        with self.assertRaises(kl.ConfigError) as e:
            kl.parse_config({})
        self.assertEqual(len(str(e.exception).splitlines()), 3)

    def test_releases_and_options(self):
        cfg = kl.parse_config(dict(BASE, releases=["v1", "v2", "later"], autonomy="supervised", host="gitlab",
                                   split_threshold=4, self_contained_tickets=True, check_command="make check",
                                   verify="Open the site."))
        self.assertEqual(cfg.releases, ["v1", "v2", "later"])
        self.assertEqual((cfg.host, cfg.host_detected, cfg.autonomy, cfg.split_threshold), ("gitlab", False, "supervised", 4))
        with self.assertRaises(kl.ConfigError):
            kl.parse_config(dict(BASE, releases=["v1", "v1"]))

    def test_backslash_globs_are_rejected(self):
        with self.assertRaises(kl.ConfigError) as e:
            kl.parse_config(dict(BASE, tests=["tests\\**"]))
        self.assertIn("never a backslash", str(e.exception))

    def test_kitchen_lock_files_are_excluded_from_every_scan(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "kitchen.yml").write_text("tests: [tests/**]\ncode: ['**/*.py']\ntest_command: x {files}\n")
            cfg = kl.load_config(d)
            self.assertEqual(cfg.framework, frozenset())
            self.assertTrue(kl.is_code("scripts/deliver.py", cfg))
            Path(d, "kitchen.lock").write_text(json.dumps({"version": "0.1.0", "files": {
                "scripts/deliver.py": "ab12", "tests/helper_from_framework.py": "cd34"}}))
            cfg = kl.load_config(d)
            self.assertFalse(kl.is_code("scripts/deliver.py", cfg))
            self.assertTrue(kl.is_ignored("scripts/deliver.py.kitchen-new", cfg))
            self.assertFalse(kl.is_test("tests/helper_from_framework.py", cfg))
            self.assertTrue(kl.is_code("src/app.py", cfg))
            Path(d, "kitchen.lock").write_text("{not json")
            with self.assertRaises(kl.ConfigError) as e:
                kl.load_config(d)
            self.assertIn("kitchen.lock: not valid JSON", str(e.exception))

    def test_load_config_reads_the_file_and_reports_yaml_errors(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(kl.ConfigError) as e:
                kl.load_config(d)
            self.assertIn("not found", str(e.exception))
            Path(d, "kitchen.yml").write_text("tests: [unclosed\n")
            with self.assertRaises(kl.ConfigError) as e:
                kl.load_config(d)
            self.assertIn("invalid YAML", str(e.exception))
            Path(d, "kitchen.yml").write_text("tests: [t/**]\ncode: [s/**]\ntest_command: x {files}\n")
            self.assertEqual(kl.load_config(d).host, "manual")


class CommandTest(unittest.TestCase):
    def test_placeholders(self):
        files = ["app/tests/a b.ts", "app/tests/c.ts"]
        self.assertEqual(kl.render_command("t {files} --out={report}", files, "/r d/x.xml"),
                         "t 'app/tests/a b.ts' app/tests/c.ts --out='/r d/x.xml'")
        self.assertEqual(kl.render_command("cd app && t {files:app}", files, "r"), "cd app && t 'tests/a b.ts' tests/c.ts")
        self.assertEqual(kl.render_command("cd app && t {files:app/}", ["lib/x.ts"], "r"), "cd app && t ../lib/x.ts")
        self.assertEqual(kl.render_command("t {files} ${HOME} {a,b}", [], "r"), "t  ${HOME} {a,b}")


class GitTest(unittest.TestCase):
    def setUp(self):
        self.p = Project(files={"src/a.py": "x\n", ".gitignore": "build/\n"}, origin=False)
        self.addCleanup(self.p.close)

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.p.root, env=dict(os.environ, **GIT_ENV), capture_output=True, text=True)

    def test_repo_root_from_a_subfolder_and_from_the_scripts_folder(self):
        (self.p.root / "src" / "deep").mkdir()
        self.assertEqual(kl.repo_root(self.p.root / "src" / "deep"), self.p.root.resolve())
        code, out = self.p.run("kitchen_lib.py", "--config", cwd=self.p.root / "src")
        self.assertEqual(code, 0, out)
        self.assertIn("host: 'manual'", out)

    def test_repo_root_outside_git_is_the_parent_of_scripts(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(kl.repo_root(d), Path(kl.__file__).resolve().parent.parent)

    def test_detect_host_from_origin(self):
        for url, want in [("git@github.com:o/r.git", "github"), ("https://gitlab.example.com/o/r.git", "gitlab"),
                          ("https://git.example.com/o/r.git", "manual")]:
            with self.subTest(url=url):
                self.git("remote", "remove", "origin")
                self.git("remote", "add", "origin", url)
                self.assertEqual(kl.detect_host(self.p.root), want)

    def test_default_branch(self):
        self.assertEqual(kl.default_branch(self.p.root), "main")
        self.git("branch", "-m", "main", "master")
        self.assertEqual(kl.default_branch(self.p.root), "master")
        self.git("update-ref", "refs/remotes/origin/trunk", "HEAD")
        self.git("symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/trunk")
        self.assertEqual(kl.default_branch(self.p.root), "trunk")

    def test_tracked_files_include_new_files_and_skip_ignored_ones(self):
        self.p.write("src/new.py", "y\n", add=False)
        self.p.write("build/out.py", "z\n", add=False)
        files = kl.tracked_files(self.p.root)
        self.assertIn("src/new.py", files)
        self.assertIn("src/a.py", files)
        self.assertNotIn("build/out.py", files)
        at_head = kl.tracked_files(self.p.root, "HEAD")
        self.assertIn("src/a.py", at_head)
        self.assertNotIn("src/new.py", at_head)

    def test_frontmatter_with_windows_line_endings(self):
        fm, body = kl.parse_frontmatter("---\r\nid: US-PAY-01\r\n---\r\n\r\nBody\r\n")
        self.assertEqual(fm, {"id": "US-PAY-01"})
        self.assertEqual(body, "\nBody\n")
        self.assertEqual(kl.parse_frontmatter("no frontmatter"), (None, "no frontmatter"))

    def test_decision_log_titles(self):
        self.assertEqual(kl.decision_log_titles(self.p.root),
                         {"Use the hotfix lane for the refund outage", "Refunds stay manual"})


class SelfTest(unittest.TestCase):
    def test_self_test_passes(self):
        p = Project(git=False)
        self.addCleanup(p.close)
        code, out = p.run("kitchen_lib.py", "--self-test")
        self.assertEqual(code, 0, out)
        self.assertIn("PASS self-test", out)


if __name__ == "__main__":
    unittest.main()
