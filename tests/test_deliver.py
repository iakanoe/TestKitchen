# test-kitchen: no-trace (the tickets, tags, and TODOs in this file are test data)
"""Tests for template/scripts/deliver.py on real, throwaway git history.

Each class builds a project (tests/helpers/kitchen_project.py): the scripts under test
installed at scripts/, a kitchen.yml whose test_command is a fake JUnit runner, fixture
requirements and tickets, a git repository with a bare local `origin`. Branches are built
commit by commit the way the workflow builds them, and the script runs as a subprocess, the
way CI and the guard run it. Host CLIs are fakes on PATH; nothing touches the network.

Run: python3 -m unittest discover -s tests -p 'test_deliver.py'
"""
import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers.kitchen_project import EPIC, RUNNER, SCRIPTS, Project, kitchen_yml, ticket  # noqa: E402

# Import the scripts under test without writing __pycache__ into template/ (init copies that folder).
sys.dont_write_bytecode = True
sys.path.insert(0, str(SCRIPTS))
import hosts  # noqa: E402
import deliver  # noqa: E402

EPIC_DIR = "backlog/PAY-payments"
STORY_PATH = f"{EPIC_DIR}/US-PAY-99-fixture.md"
BRANCH = "us-pay-99-fixture"
TESTS = "tests/fixture.txt"
TAGGED = "us_pay_99_ac1_a fail\nus_pay_99_ac2_b fail\n"


def story(status, extra=""):
    return ticket("US-PAY-99", title="Fixture story", status=status, extra=extra)


class Repo(unittest.TestCase):
    """One project per class; every test starts from the base commit, detached and clean."""
    KITCHEN = None

    @classmethod
    def setUpClass(cls):
        cls.p = Project(kitchen=cls.KITCHEN)
        cls.addClassCleanup(cls.p.close)
        cls.p.git("config", "user.name", "Test Owner")
        cls.base = cls.p.head()

    def setUp(self):
        self.p.git("checkout", "-q", "--force", "--detach", self.base)
        # A test may leave an untracked file (an uncommitted record); the next must not inherit it.
        self.p.git("clean", "-fdq")

    def write(self, rel, text, append=False):
        self.p.write(rel, text, append=append)

    def commit(self, message, allow_empty=False):
        return self.p.commit(message, allow_empty)

    def run_script(self, *args, **env):
        return self.p.run("deliver.py", *args, **env)


class GatePrTest(Repo):
    def story_branch(self, tests=TAGGED, path=STORY_PATH, text=story, tests_path=TESTS):
        """Claim, freeze two tagged tests, implement, set done: a branch that follows the workflow."""
        self.write(path, text("in-progress"))
        self.commit("chore: start US-PAY-99")
        self.write(tests_path, tests)
        freeze = self.commit("test: US-PAY-99 failing tests")
        self.write("src/fixture.py", "# implementation\n")
        self.write(tests_path, tests.replace("fail", "pass"))
        self.commit("feat: US-PAY-99 implementation")
        self.write(path, text("done"))
        return freeze

    def body(self, reviewed=None, critical=0, ticket_line="US-PAY-99 Fixture. Status `done`.", plan=("AC1", "AC2"),
             test_changes=f"- `{TESTS}`: the implementation makes them pass", review=None, decisions="- None",
             gaps="- None", plan_extra=""):
        reviewed = reviewed or self.p.head()
        rows = "\n".join(f"| US-PAY-99/{ac} | t |" for ac in plan)
        review = review or f"Reviewed commit: {reviewed}\nCRITICAL: {critical}, WARNING: 0, SUGGESTION: 0\n"
        return (f"## Ticket\n\n{ticket_line}\n\n## Plan\n\n{rows}\n{plan_extra}\n## Gaps found\n\n{gaps}\n\n"
                f"## Decisions\n\n{decisions}\n\n## Platform changes\n\n- None\n\n## Test changes\n\n{test_changes}\n\n"
                f"## Review report\n\n{review}")

    def record(self, body, branch=BRANCH, *extra):
        """`deliver.py record` for a description, committed as the workflow commits it."""
        f = self.p.tmp / "body.md"
        f.write_bytes(body.encode("utf-8"))
        code, out = self.run_script("record", f"--body-file={f}", f"--branch={branch}", *extra)
        self.assertEqual(code, 0, out)
        self.commit("docs: delivery record", allow_empty=True)
        return out.strip()

    def gate(self, body, branch=BRANCH, base=None, record=True, **env):
        if record:
            self.record(body, branch)
        f = self.p.tmp / "body.md"
        f.write_bytes(body.encode("utf-8"))
        return self.run_script("gate", "pr", f"--body-file={f}", f"--branch={branch}", f"--base={base or self.base}",
                               "--head=HEAD", **env)

    def assertPasses(self, body, **kw):
        code, out = self.gate(body, **kw)
        self.assertEqual(code, 0, out)
        self.assertIn("PASS pr", out)

    def assertFails(self, body, reason, **kw):
        code, out = self.gate(body, **kw)
        self.assertEqual(code, 1, out)
        self.assertIn(reason, out)
        return out

    def side_merge(self, onto, edit=None):
        """Merge a side branch that only adds NOTES.txt into `onto`, applying `edit()` inside the merge commit."""
        self.p.git("checkout", "-q", "--detach", self.base)
        self.write("NOTES.txt", "notes\n")
        side = self.commit("chore: notes on a side branch")
        self.p.git("checkout", "-q", "--detach", onto)
        self.p.git("merge", "-q", "--no-ff", "--no-commit", side)
        if edit:
            edit()
        return self.commit("Merge branch 'side'")

    # --- the workflow --------------------------------------------------------------------

    def test_a_branch_that_follows_the_workflow_passes(self):
        self.story_branch()
        self.commit("chore: capture US-PAY-99")
        self.assertPasses(self.body())

    def test_a_non_ticket_change_request_passes_on_a_non_ticket_branch(self):
        self.assertPasses("## Ticket\n\nNone.\n", branch="fix/thing")

    def test_a_none_ticket_that_mentions_a_ticket_is_not_a_ticket_change_request(self):
        self.assertPasses("## Ticket\n\nNone. Delivers SPK-PAY-01 and follows up US-PAY-99.\n", branch="spk-pay-01-probe")

    def test_a_ticket_branch_must_name_its_ticket(self):
        for branch in (BRANCH, "task-pay-98-x"):
            with self.subTest(branch=branch):
                self.assertFails("## Ticket\n\nNone.\n", "names no US- or TASK- ticket first", branch=branch)

    def test_the_branch_must_match_the_ticket(self):
        self.story_branch()
        self.commit("chore: capture")
        self.assertFails(self.body(), "is not the ticket's file name", branch="us-pay-99-other")

    def test_every_live_criterion_needs_a_plan_row(self):
        self.story_branch()
        self.commit("chore: capture")
        self.assertFails(self.body(plan=("AC1",)), "Plan has no row for US-PAY-99/AC2")
        # A row for AC10 is not a row for AC1.
        self.assertFails(self.body(plan=("AC10", "AC2")), "Plan has no row for US-PAY-99/AC1")

    def test_no_freeze_commit_fails(self):
        self.write(STORY_PATH, story("done"))
        self.write(TESTS, TAGGED)
        self.commit("feat: everything at once")
        self.assertFails(self.body(), "tests were not frozen")

    def test_an_empty_freeze_fails(self):
        self.write(STORY_PATH, story("in-progress"))
        self.commit("chore: start US-PAY-99")
        self.commit("test: US-PAY-99 failing tests", allow_empty=True)
        self.write(TESTS, TAGGED)
        self.write(STORY_PATH, story("done"))
        self.commit("feat: tests and code")
        self.assertFails(self.body(), "had no tagged test at the freeze commit")

    def test_implementation_before_the_freeze_fails(self):
        self.write(STORY_PATH, story("in-progress"))
        self.write("src/fixture.py", "# too early\n")
        self.commit("feat: early")
        self.write(TESTS, TAGGED)
        self.commit("test: US-PAY-99 failing tests")
        self.write(STORY_PATH, story("done"))
        self.commit("chore: done")
        self.assertFails(self.body(), "implementation must come after the failing tests")

    def test_two_freeze_commits_fail(self):
        self.story_branch()
        self.commit("chore: capture")
        self.commit("test: US-PAY-99 failing tests", allow_empty=True)
        self.assertFails(self.body(), "there must be exactly one")

    def test_losing_a_tagged_test_fails(self):
        self.story_branch()
        self.write(TESTS, "us_pay_99_ac1_a pass\n")
        self.commit("feat: drop a test")
        self.assertFails(self.body(), "US-PAY-99/AC2: 1 tagged test(s) at the freeze, 0 now")

    def test_an_unlisted_test_change_fails(self):
        self.story_branch()
        self.commit("chore: capture")
        self.assertFails(self.body(test_changes="None"), 'is not listed under "Test changes"')

    def test_a_listed_test_change_passes_by_path_or_name(self):
        self.story_branch()
        self.commit("chore: capture")
        self.assertPasses(self.body(test_changes="- fixture.txt: outcomes flipped"))

    def test_skip_and_focus_markers_of_every_language(self):
        markers = ['it.skip("[US-PAY-99/AC2] c", () => {})', 'test.only("x", () => {})', 'describe.todo("x")',
                   'test.fixme("x", async () => {})', 'xit("x", () => {})', 'xdescribe("x", () => {})', 'xtest("x")',
                   'fit("x", () => {})', 'fdescribe("x", () => {})', "@pytest.mark.skip(reason='x')",
                   "@pytest.mark.skipif(True, reason='x')", "@pytest.mark.xfail", "pytest.skip('x')",
                   "@unittest.skip('x')", "@unittest.skipIf(True, 'x')", "self.skipTest('x')", 't.Skip("later")',
                   't.Skipf("later %d", 1)', "@Disabled", "@Ignore", 'xit "does x" do', '  skip "later"', "  pending"]
        for marker in markers:
            with self.subTest(marker=marker):
                self.assertTrue(deliver.SKIP_MARKERS.search(marker))
        for plain in ("items = stream.skipped", "# these tests fit in one file", "skipping = True", "def fit_line():",
                      "expect(x).toBe(1)", "pending_refunds = []"):
            with self.subTest(plain=plain):
                self.assertFalse(deliver.SKIP_MARKERS.search(plain))

    def test_adding_a_skipped_or_focused_test_after_the_freeze_fails(self):
        for marker in ('it.skip("[US-PAY-99/AC2] c", () => {})', "@pytest.mark.skip(reason='later')"):
            with self.subTest(marker=marker):
                self.setUp()
                self.story_branch()
                self.write(TESTS, marker + "\n", append=True)
                self.commit("feat: skip")
                self.assertFails(self.body(), "adds a skipped or focused test in tests/fixture.txt")

    def test_skip_calls_in_product_code_and_plain_words_are_fine(self):
        self.story_branch()
        self.write("src/fixture.py", "items = stream.skip(1)  # fit the page\n", append=True)
        self.write(TESTS, "# these tests fit in one file\n", append=True)
        self.commit("feat: more")
        self.assertPasses(self.body())

    def test_a_critical_finding_fails(self):
        self.story_branch()
        self.commit("chore: capture")
        self.assertFails(self.body(critical=1), "the last review reports 1 CRITICAL")

    def test_a_missing_review_fails(self):
        self.story_branch()
        self.commit("chore: capture")
        self.assertFails(self.body(review="Not reviewed.\n"), "no reviewer tally")

    def test_code_or_test_changes_after_the_reviewed_commit_fail(self):
        for path in ("src/fixture.py", TESTS):
            with self.subTest(path=path):
                self.setUp()
                self.story_branch()
                reviewed = self.commit("chore: capture")
                self.write(path, "# after review\n", append=True)
                self.commit("feat: late change")
                self.assertFails(self.body(reviewed=reviewed), "changed after the reviewed commit")

    def test_capture_changes_after_the_reviewed_commit_pass(self):
        self.story_branch()
        reviewed = self.commit("feat: last code")
        self.write("docs/decision-log.md", "\n", append=True)
        self.commit("chore: capture")
        self.assertPasses(self.body(reviewed=reviewed))

    def test_a_reviewed_commit_off_the_branch_fails(self):
        self.story_branch()
        tip = self.commit("chore: capture")
        self.p.git("checkout", "-q", "--detach", self.base)
        elsewhere = self.commit("chore: not on the branch", allow_empty=True)
        self.p.git("checkout", "-q", "--detach", tip)
        self.assertFails(self.body(reviewed=elsewhere), "is not on the branch")

    def test_the_last_tally_counts(self):
        self.story_branch()
        sha = self.commit("chore: capture")
        tally = "CRITICAL: {}, WARNING: 0, SUGGESTION: 0\n"
        self.assertPasses(self.body(review=tally.format(1) + f"Reviewed commit: {sha}\n" + tally.format(0)))
        self.assertFails(self.body(review=f"Reviewed commit: {sha}\n" + tally.format(0) + tally.format(2)),
                         "the last review reports 2 CRITICAL")

    def test_the_last_reviewed_commit_counts(self):
        self.story_branch()
        old = self.commit("chore: capture")
        self.write("src/fixture.py", "# fixed after the first review\n", append=True)
        new = self.commit("feat: fix review findings")
        tally = "CRITICAL: 0, WARNING: 0, SUGGESTION: 0\n"
        self.assertPasses(self.body(review=f"Reviewed commit: {old}\nReviewed commit: {new}\n{tally}"))
        self.assertFails(self.body(review=f"Reviewed commit: {new}\nReviewed commit: {old}\n{tally}"),
                         "changed after the reviewed commit")

    def test_a_missing_reviewed_commit_line_fails(self):
        self.story_branch()
        self.commit("chore: capture")
        self.assertFails(self.body(review="CRITICAL: 0, WARNING: 0, SUGGESTION: 0\n"), 'no "Reviewed commit: <sha>" line')

    def test_merging_the_default_branch_after_the_review_passes(self):
        """The default branch's own code changes, merged in after the review, are not this branch's."""
        self.story_branch()
        reviewed = self.commit("chore: capture")
        self.p.git("checkout", "-q", "--detach", self.base)
        self.write("src/from-main.py", "# another ticket, on main\n")
        main = self.commit("feat: another ticket on main")
        self.p.git("checkout", "-q", "--detach", reviewed)
        self.p.git("merge", "-q", "--no-ff", "--no-edit", main)
        self.assertPasses(self.body(reviewed=reviewed), base=main)

    # --- merge commits are history too ------------------------------------------------------

    def test_code_written_inside_a_merge_after_the_review_fails(self):
        self.story_branch()
        reviewed = self.commit("chore: capture")
        self.side_merge(reviewed, lambda: self.write("src/fixture.py", "# unreviewed\n", append=True))
        self.assertFails(self.body(reviewed=reviewed), "changed after the reviewed commit")

    def test_code_written_inside_a_merge_before_the_freeze_fails(self):
        self.write(STORY_PATH, story("in-progress"))
        start = self.commit("chore: start US-PAY-99")
        self.side_merge(start, lambda: self.write("src/fixture.py", "# written before the tests\n"))
        self.write(TESTS, TAGGED)
        self.commit("test: US-PAY-99 failing tests")
        self.write(STORY_PATH, story("done"))
        self.commit("chore: done")
        self.assertFails(self.body(test_changes="None"), "at or before the freeze commit")

    def test_a_skip_marker_added_inside_a_merge_fails(self):
        self.story_branch()
        tip = self.commit("chore: capture")
        self.side_merge(tip, lambda: self.write(TESTS, 'it.only("x", () => {})\n', append=True))
        self.assertFails(self.body(), "adds a skipped or focused test")

    def test_a_clean_merge_of_the_default_branch_passes_even_when_both_sides_changed_a_file(self):
        self.write("src/shared.py", "".join(f"line {i}\n" for i in range(1, 11)))
        start = self.commit("feat: shared module")
        self.story_branch()
        self.write("src/shared.py", (self.p.root / "src/shared.py").read_text().replace("line 1\n", "line one\n"))
        reviewed = self.commit("feat: tweak the shared module")
        self.p.git("checkout", "-q", "--detach", start)
        self.write("src/shared.py", (self.p.root / "src/shared.py").read_text().replace("line 10\n", "line ten\n"))
        self.write("tests/main_only.txt", 'it.skip("another ticket\'s pending test", () => {})\n')
        main = self.commit("feat: another ticket on main")
        self.p.git("checkout", "-q", "--detach", reviewed)
        self.p.git("merge", "-q", "--no-ff", "--no-edit", main)
        self.assertIn("line one", (self.p.root / "src/shared.py").read_text())
        self.assertIn("line ten", (self.p.root / "src/shared.py").read_text())
        self.assertPasses(self.body(reviewed=reviewed), base=main)

    # --- unusual paths and the person's git configuration ------------------------------------

    def test_skip_markers_are_found_whatever_the_file_name_or_git_config(self):
        config = self.p.tmp / "gitconfig"
        config.write_text("[diff]\n\tnoprefix = true\n\tmnemonicPrefix = true\n[core]\n\tquotePath = true\n"
                          "[color]\n\tui = always\n\tdiff = always\n")
        for name in ("tests/reembolsó.txt", "tests/refund limit.txt"):
            with self.subTest(name=name):
                self.setUp()
                self.story_branch(tests_path=name)
                self.write(name, 'it.only("[US-PAY-99/AC1] focus", () => {})\n', append=True)
                self.commit("feat: focus")
                out = self.assertFails(self.body(test_changes=f"- `{name}`: flipped"), f"adds a skipped or focused test in {name}",
                                       GIT_CONFIG_GLOBAL=str(config))
                self.assertNotIn("not listed", out)

    def test_a_record_in_an_epic_folder_with_a_non_ascii_name_is_found(self):
        folder = "backlog/BILL-cobros-año"
        self.write(f"{folder}/epic.md", EPIC.format(extra="").replace("EP-PAY", "EP-BILL"))
        path = f"{folder}/US-BILL-99-fixture.md"
        bill = lambda status: ticket("US-BILL-99", epic="EP-BILL", status=status)  # noqa: E731
        self.write(path, bill("in-progress"))
        self.commit("chore: start US-BILL-99")
        self.write(TESTS, "us_bill_99_ac1 fail\nus_bill_99_ac2 fail\n")
        self.commit("test: US-BILL-99 failing tests")
        self.write("src/bill.py", "# implementation\n")
        self.write(TESTS, "us_bill_99_ac1 pass\nus_bill_99_ac2 pass\n")
        self.write(path, bill("done"))
        reviewed = self.commit("feat: US-BILL-99")
        body = self.body(reviewed=reviewed, ticket_line="US-BILL-99 Billing.").replace("US-PAY-99/", "US-BILL-99/")
        self.assertPasses(body, branch="us-bill-99-fixture")
        code, out = self.run_script("status")
        self.assertIn(f"{folder}/delivery/US-BILL-99.md", out)

    def test_test_changes_name_whole_paths_not_substrings(self):
        self.story_branch()
        self.commit("chore: capture")
        self.assertFails(self.body(test_changes="- `tests/fixture.txt.old` and xfixture.txt"), 'is not listed under "Test changes"')
        self.assertPasses(self.body(test_changes="- tests/fixture.txt, flipped to pass."))

    def test_a_task_whose_tests_carry_its_tags_needs_a_freeze_commit(self):
        path = f"{EPIC_DIR}/TASK-PAY-98-cache.md"
        self.write(path, ticket("TASK-PAY-98", type="task", status="in-progress", reqs=()))
        self.commit("chore: start TASK-PAY-98")
        self.write("src/ci.py", "# code first\n")
        self.write(TESTS, "task_pay_98_ac1 pass\n")
        self.write(path, ticket("TASK-PAY-98", type="task", status="done", reqs=()))
        reviewed = self.commit("feat: code and tests together")
        body = self.body(reviewed=reviewed, ticket_line="TASK-PAY-98 Cache.").replace("US-PAY-99/AC1", "TASK-PAY-98/AC1")
        self.assertFails(body, "tests were not frozen before the implementation", branch="task-pay-98-cache")

    def test_a_non_ticket_change_request_that_changes_code_needs_a_review(self):
        self.write("src/fix.py", "# typo fixed\n")
        reviewed = self.commit("fix: typo")
        self.assertFails("## Ticket\n\nNone. Typo fix.\n", "no reviewer tally", branch="fix/typo")
        reviewed_body = (f"## Ticket\n\nNone. Typo fix.\n\n## Review report\n\nReviewed commit: {reviewed}\n"
                         "CRITICAL: 0, WARNING: 0, SUGGESTION: 0\n")
        self.assertPasses(reviewed_body, branch="fix/typo")
        self.write("src/fix.py", "# changed after the review\n", append=True)
        self.commit("fix: more")
        self.assertFails(reviewed_body, "changed after the reviewed commit", branch="fix/typo")

    def test_a_ticket_left_in_progress_needs_a_reason(self):
        self.story_branch()
        self.write(STORY_PATH, story("in-progress"))
        self.commit("chore: capture", allow_empty=True)
        self.assertFails(self.body(), "set it to done")
        self.assertPasses(self.body(ticket_line="US-PAY-99 stays `in-progress`: AC2 waits for US-PAY-03."))

    # --- lanes and autonomy ---------------------------------------------------------------

    def test_a_hotfix_names_why_and_its_follow_up(self):
        hot = lambda status: story(status, extra="hotfix: true\n")  # noqa: E731
        self.story_branch(text=hot)
        self.commit("chore: capture")
        code, out = self.gate(self.body())
        self.assertEqual(code, 1, out)
        self.assertIn('hotfix: "## Decisions" needs a bullet', out)
        self.assertIn('hotfix: "## Gaps found" must name the follow-up ticket', out)
        self.assertPasses(self.body(decisions="- Production refunds were down. Log: Use the hotfix lane for the refund outage",
                                    gaps="- Refine after the hotfix: TASK-PAY-50."))

    def test_supervised_autonomy_needs_named_approvals(self):
        self.story_branch()
        self.write("kitchen.yml", kitchen_yml(autonomy="supervised"))
        self.commit("chore: capture")
        code, out = self.gate(self.body())
        self.assertEqual(code, 1, out)
        self.assertIn('needs "Plan approved by: <name>"', out)
        self.assertIn('needs "Tests approved by: <name>"', out)
        self.assertFails(self.body(plan_extra="\nPlan approved by: <name>\nTests approved by: Dana\n"), "Plan approved by")
        self.assertPasses(self.body(plan_extra="\nPlan approved by: Dana\nTests approved by: Dana\n"))

    def test_a_task_without_a_freeze_commit_skips_the_test_checks(self):
        path = f"{EPIC_DIR}/TASK-PAY-98-cache.md"
        self.write(path, ticket("TASK-PAY-98", type="task", status="in-progress", reqs=()))
        self.commit("chore: start TASK-PAY-98")
        self.write("src/ci.py", "# cache\n")
        self.write(path, ticket("TASK-PAY-98", type="task", status="done", reqs=()))
        reviewed = self.commit("chore: cache dependencies")
        body = self.body(reviewed=reviewed, ticket_line="TASK-PAY-98 Cache.").replace("US-PAY-99/AC1", "TASK-PAY-98/AC1")
        self.assertPasses(body, branch="task-pay-98-cache")

    def test_a_task_with_a_freeze_commit_follows_the_test_rules(self):
        path = f"{EPIC_DIR}/TASK-PAY-98-cache.md"
        self.write(path, ticket("TASK-PAY-98", type="task", status="in-progress", reqs=()))
        self.write("src/ci.py", "# too early\n")
        self.commit("chore: start")
        self.write(TESTS, "task_pay_98_ac1 fail\n")
        self.commit("test: TASK-PAY-98 failing tests")
        self.write(path, ticket("TASK-PAY-98", type="task", status="done", reqs=()))
        reviewed = self.commit("chore: done")
        body = self.body(reviewed=reviewed, ticket_line="TASK-PAY-98 Cache.").replace("US-PAY-99/AC1", "TASK-PAY-98/AC1")
        self.assertFails(body, "implementation must come after the failing tests", branch="task-pay-98-cache")

    # --- delivery records ----------------------------------------------------------------

    def test_a_ticket_change_request_needs_a_committed_delivery_record(self):
        self.story_branch()
        self.commit("chore: capture")
        self.assertFails(self.body(), f"no delivery record at {EPIC_DIR}/delivery/US-PAY-99.md", record=False)

    def test_a_non_ticket_change_request_needs_one_too(self):
        self.assertFails("## Ticket\n\nNone.\n", "no delivery record at backlog/delivery/fix-thing.md",
                         branch="fix/thing", record=False)

    def test_an_uncommitted_record_does_not_count(self):
        self.story_branch()
        self.commit("chore: capture")
        body = self.body()
        rel = self.record(body)
        valid = (self.p.root / rel).read_text()
        self.p.git("reset", "-q", "--hard", "HEAD~1")
        (self.p.root / rel).parent.mkdir(parents=True, exist_ok=True)
        (self.p.root / rel).write_text(valid)
        self.assertFails(body, "no delivery record", record=False)

    def test_a_record_that_differs_from_the_description_fails(self):
        self.story_branch()
        self.commit("chore: capture")
        old = self.body()
        self.record(old)
        self.assertFails(old + "\n## Checks\n\nedited after the record\n", "matches the description", record=False)

    def test_record_keeps_the_description_verbatim_next_to_the_ticket(self):
        self.story_branch()
        self.commit("chore: capture")
        body = self.body() + "\n## Checks\n\n`deliver.py check`: passed\r\n"
        out = self.record(body, BRANCH, "--cr=9", "--url=https://example.test/cr/9")
        self.assertEqual(out, f"{EPIC_DIR}/delivery/US-PAY-99.md")
        text = (self.p.root / out).read_text()
        self.assertIn("# Delivery record: US-PAY-99", text)
        self.assertIn("- Change request: #9 https://example.test/cr/9", text)
        self.assertEqual(text.split("<!-- change-request-description -->\n", 1)[1].strip(), body.replace("\r\n", "\n").strip())

    def test_a_non_ticket_record_is_named_after_its_branch(self):
        out = self.record("## Ticket\n\nNone.\n", "docs/dec-pay-01-limits")
        self.assertEqual(out, "backlog/delivery/docs-dec-pay-01-limits.md")
        self.assertIn("# Delivery record: docs/dec-pay-01-limits", (self.p.root / out).read_text())

    def test_a_decorated_ticket_line_is_still_a_ticket_change_request(self):
        """Backticks, bold, or a bullet around the ID must not turn the ticket gates off."""
        self.story_branch()
        self.commit("chore: capture")
        for line in ("`US-PAY-99` Fixture.", "**US-PAY-99** Fixture.", "- US-PAY-99 Fixture.", "[US-PAY-99](x) Fixture."):
            with self.subTest(line=line):
                self.assertFails(self.body(ticket_line=line), "is not the ticket's file name", branch="chore/x")

    def test_a_second_change_request_for_a_ticket_gets_its_own_record(self):
        self.story_branch()
        self.commit("chore: capture")
        first, second = self.body(), self.body() + "\n## Checks\n\nfollow-up\n"
        self.assertEqual(self.record(first, BRANCH, "--cr=9"), f"{EPIC_DIR}/delivery/US-PAY-99.md")
        self.assertEqual(self.record(second, BRANCH, "--cr=12"), f"{EPIC_DIR}/delivery/US-PAY-99-cr12.md")
        self.assertPasses(first, record=False)
        self.assertPasses(second, record=False)

    def test_recording_the_same_change_request_again_replaces_its_record(self):
        self.story_branch()
        self.commit("chore: capture")
        self.record(self.body(), BRANCH, "--cr=9")
        edited = self.body() + "\n## Checks\n\nedited\n"
        self.assertEqual(self.record(edited, BRANCH, "--cr=9"), f"{EPIC_DIR}/delivery/US-PAY-99.md")
        self.assertIn("edited", (self.p.root / EPIC_DIR / "delivery/US-PAY-99.md").read_text())
        self.assertPasses(edited, record=False)

    def test_another_records_is_never_overwritten_without_a_number(self):
        """`docs/a-b` and `docs-a/b` both name backlog/delivery/docs-a-b.md."""
        self.record("## Ticket\n\nNone.\n", "docs/a-b", "--cr=3")
        f = self.p.tmp / "body.md"
        f.write_text("## Ticket\n\nNone. Another.\n")
        code, out = self.run_script("record", f"--body-file={f}", "--branch=docs-a/b")
        self.assertEqual(code, 1, out)
        self.assertIn("already records another change request", out)
        self.assertEqual(self.record("## Ticket\n\nNone. Another.\n", "docs-a/b", "--cr=4"), "backlog/delivery/docs-a-b-cr4.md")

    def test_record_works_without_a_number(self):
        self.assertEqual(self.record("## Ticket\n\nNone.\n", "fix/thing"), "backlog/delivery/fix-thing.md")
        self.assertNotIn("Change request:", (self.p.root / "backlog/delivery/fix-thing.md").read_text())

    def test_a_record_checked_out_with_windows_line_endings_still_matches(self):
        body = "## Ticket\n\nNone.\n"
        rel = self.record(body, "fix/thing")
        path = self.p.root / rel
        path.write_bytes(path.read_text().replace("\n", "\r\n").encode())
        self.p.git("-c", "core.autocrlf=false", "-c", "core.safecrlf=false", "add", "backlog")
        self.assertIn("i/crlf", self.p.git("ls-files", "--eol", rel), "the fixture must really hold CRLF")
        self.commit("docs: crlf record")
        self.assertPasses(body, branch="fix/thing", record=False)

    def test_gate_pr_can_read_the_description_from_the_branch_record(self):
        self.story_branch()
        self.commit("chore: capture")
        self.record(self.body())
        code, out = self.run_script("gate", "pr", "--from-record", f"--branch={BRANCH}", f"--base={self.base}")
        self.assertEqual(code, 0, out)
        self.assertIn(f"description read from {EPIC_DIR}/delivery/US-PAY-99.md", out)
        code, out = self.run_script("gate", "pr", "--from-record", "--branch=fix/none", f"--base={self.base}")
        self.assertEqual(code, 1, out)
        self.assertIn("needs exactly one delivery record", out)


class GateRedTest(unittest.TestCase):
    def project(self, tests=TAGGED, kitchen=None, status="in-progress", path=TESTS, **files):
        files = dict(files)
        files.setdefault(STORY_PATH, story(status))
        if tests is not None:
            files[path] = tests
        p = Project(files=files, kitchen=kitchen, origin=False)
        self.addCleanup(p.close)
        return p

    def red(self, p, tid="US-PAY-99", **env):
        return p.run("deliver.py", "gate", "red", tid, **env)

    def test_failing_tagged_tests_pass_the_gate(self):
        code, out = self.red(self.project())
        self.assertEqual(code, 0, out)
        self.assertIn("FAILED  us_pay_99_ac1_a", out)
        self.assertIn("PASS red", out)

    def test_already_passing_tests_fail_the_gate(self):
        code, out = self.red(self.project("us_pay_99_ac1_a pass\nus_pay_99_ac2_b fail\n"))
        self.assertEqual(code, 1, out)
        self.assertIn("AC1: every tagged test already passes", out)

    def test_skipped_and_missing_tests_did_not_run(self):
        code, out = self.red(self.project("us_pay_99_ac1_a skip\n[US-PAY-99/AC2] not-a-runner-line\n"))
        self.assertEqual(code, 1, out)
        self.assertIn("AC1: no tagged test ran (only skipped ones)", out)
        self.assertIn("AC2: no tagged test ran", out)

    def test_tags_in_class_names_count(self):
        code, out = self.red(self.project("test_a fail TestUS_PAY_99_AC1\ntest_b fail [US-PAY-99/AC2]\n"))
        self.assertEqual(code, 0, out)

    def test_no_report_or_a_broken_report_fails_with_the_output(self):
        p = self.project()
        code, out = self.red(p, JUNIT_RUNNER_NO_REPORT="1")
        self.assertEqual(code, 1, out)
        self.assertIn("wrote no JUnit report", out)
        self.assertIn("the test framework is missing", out)
        code, out = self.red(p, JUNIT_RUNNER_BAD_XML="1")
        self.assertEqual(code, 1, out)
        self.assertIn("not valid XML", out)

    def test_no_tagged_test_file(self):
        code, out = self.red(self.project(tests=None))
        self.assertEqual(code, 1, out)
        self.assertIn("no test file tags US-PAY-99", out)

    def test_only_tagged_test_files_are_run_and_dir_placeholders_strip_the_folder(self):
        kitchen = kitchen_yml().replace("test_command:", "#") + "test_command: " + json.dumps(
            f'cd tests && "{sys.executable}" "{RUNNER}" {{report}} {{files:tests}}') + "\n"
        p = self.project(kitchen=kitchen, **{"tests/other.txt": "unrelated fail\n"})
        code, out = self.red(p)
        self.assertEqual(code, 0, out)
        self.assertRegex(out, r"running: cd tests && .* fixture\.txt\n")
        self.assertNotIn("other.txt", out)

    def test_framework_files_listed_in_kitchen_lock_are_never_run(self):
        lock = json.dumps({"version": "0.1.0", "files": {"tests/framework.txt": "0"}})
        p = self.project(**{"tests/framework.txt": "us_pay_99_ac1_framework fail\n", "kitchen.lock": lock})
        code, out = self.red(p)
        self.assertEqual(code, 0, out)
        self.assertNotIn("framework", out)

    def test_tasks_without_tagged_tests_and_other_types(self):
        task = f"{EPIC_DIR}/TASK-PAY-98-cache.md"
        p = self.project(tests=None, **{task: ticket("TASK-PAY-98", type="task", status="in-progress", reqs=()),
                                        f"{EPIC_DIR}/SPK-PAY-01-probe.md": ticket("SPK-PAY-01", type="spike", reqs=())})
        code, out = self.red(p, "TASK-PAY-98")
        self.assertEqual(code, 0, out)
        self.assertIn("gate red does not apply", out)
        code, out = self.red(p, "SPK-PAY-01")
        self.assertEqual(code, 1, out)
        self.assertIn("applies to stories and tasks", out)
        code, out = self.red(p, "US-PAY-77")
        self.assertEqual(code, 1, out)
        self.assertIn("US-PAY-77 does not exist", out)

    def test_a_command_without_report_placeholder_is_refused(self):
        kitchen = kitchen_yml().replace("{report} ", "")
        code, out = self.red(self.project(kitchen=kitchen))
        self.assertEqual(code, 1, out)
        self.assertIn("no {report} placeholder", out)


class NextTest(unittest.TestCase):
    def next(self, files, kitchen=None, origin=True, rules=None, me="Test Owner"):
        p = Project(files=files, kitchen=kitchen, origin=origin)
        self.addCleanup(p.close)
        p.git("config", "user.name", me)
        if rules is not None:
            p.rules(rules)
        code, out = p.run("deliver.py", "next")
        return code, out, p

    def ids(self, out, label):
        return [line.split()[1].rstrip(":") for line in out.splitlines() if line.startswith(label + " ")]

    def test_order_priority_inheritance_dependents_owner_id(self):
        files = {
            f"{EPIC_DIR}/US-PAY-01-a.md": ticket("US-PAY-01", owner="Other"),
            f"{EPIC_DIR}/US-PAY-02-b.md": ticket("US-PAY-02", owner="Other", extra="priority: low\n"),
            f"{EPIC_DIR}/US-PAY-06-f.md": ticket("US-PAY-06", owner="Other", blocked_by=("US-PAY-02",), extra="priority: high\n"),
            f"{EPIC_DIR}/US-PAY-03-c.md": ticket("US-PAY-03", owner="Test Owner"),
            f"{EPIC_DIR}/US-PAY-04-d.md": ticket("US-PAY-04", owner="Other"),
            f"{EPIC_DIR}/US-PAY-07-g.md": ticket("US-PAY-07", status="draft", blocked_by=("US-PAY-04",)),
            f"{EPIC_DIR}/US-PAY-08-h.md": ticket("US-PAY-08", status="draft", blocked_by=("US-PAY-04",)),
            f"{EPIC_DIR}/US-PAY-05-e.md": ticket("US-PAY-05", assignee="human"),
            f"{EPIC_DIR}/TASK-PAY-09-i.md": ticket("TASK-PAY-09", type="task", owner="Other"),
            f"{EPIC_DIR}/US-PAY-10-j.md": ticket("US-PAY-10", status="done"),
        }
        code, out, _ = self.next(files)
        self.assertEqual(code, 0, out)
        self.assertTrue(out.startswith("NEXT US-PAY-02 (Fixture ticket) branch `us-pay-02-b`\n"), out)
        self.assertEqual(self.ids(out, "READY"), ["US-PAY-04", "US-PAY-03", "TASK-PAY-09", "US-PAY-01"])
        self.assertIn("WAIT US-PAY-05: assigned to a person", out)
        self.assertIn("WAIT US-PAY-06: blocked by US-PAY-02", out)
        self.assertNotIn("DECIDE", out)
        self.assertNotIn("REFINE", out)

    def test_release_slices_come_first(self):
        files = {
            f"{EPIC_DIR}/US-PAY-01-a.md": ticket("US-PAY-01", extra="release: v2\npriority: high\n"),
            f"{EPIC_DIR}/US-PAY-02-b.md": ticket("US-PAY-02", extra="release: v1\npriority: low\n"),
            f"{EPIC_DIR}/US-PAY-03-c.md": ticket("US-PAY-03", extra="priority: high\n"),
        }
        code, out, _ = self.next(files, kitchen=kitchen_yml(releases=["v1", "v2"]))
        self.assertEqual(self.ids(out, "NEXT") + self.ids(out, "READY"), ["US-PAY-02", "US-PAY-01", "US-PAY-03"])

    def test_taken_branches_wait(self):
        files = {
            f"{EPIC_DIR}/US-PAY-01-a.md": ticket("US-PAY-01"),
            f"{EPIC_DIR}/US-PAY-02-b.md": ticket("US-PAY-02", status="in-progress"),
            f"{EPIC_DIR}/US-PAY-03-c.md": ticket("US-PAY-03"),
            f"{EPIC_DIR}/US-PAY-04-d.md": ticket("US-PAY-04"),
        }
        rules = [{"cli": "gh", "args": ["pr", "list"], "stdout": json.dumps([{"headRefName": "us-pay-03-c"}])}]
        p = Project(files=files, kitchen=kitchen_yml(host="github"))
        self.addCleanup(p.close)
        p.rules(rules)
        p.git("push", "-q", "origin", "HEAD:refs/heads/us-pay-01-a")
        code, out = p.run("deliver.py", "next")
        self.assertEqual(code, 0, out)
        self.assertIn("NEXT US-PAY-04", out)
        self.assertIn("WAIT US-PAY-01: branch `us-pay-01-a` is taken", out)
        self.assertIn("WAIT US-PAY-03: branch `us-pay-03-c` is taken", out)
        self.assertIn("WAIT US-PAY-02: in-progress with no branch: ask who holds it", out)
        p.rules([{"cli": "gh", "args": ["pr", "list"], "stderr": "auth required", "exit": 4}])
        code, out = p.run("deliver.py", "next")
        self.assertEqual(code, 1, out)
        self.assertIn("cannot tell which branches are taken", out)

    def test_nothing_ready_hands_off_to_define(self):
        dec = lambda tid, status="ready": ticket(tid, type="decision", assignee="human", status=status)  # noqa: E731
        files = {
            f"{EPIC_DIR}/DEC-PAY-01-a.md": dec("DEC-PAY-01"),
            f"{EPIC_DIR}/DEC-PAY-02-b.md": dec("DEC-PAY-02"),
            f"{EPIC_DIR}/DEC-PAY-03-c.md": dec("DEC-PAY-03", "deferred") + "\n## Outcome\n\nParked.\n",
            f"{EPIC_DIR}/US-PAY-01-a.md": ticket("US-PAY-01", blocked_by=("DEC-PAY-01",)),
            f"{EPIC_DIR}/US-PAY-02-b.md": ticket("US-PAY-02", blocked_by=("DEC-PAY-01",)),
            f"{EPIC_DIR}/US-PAY-03-c.md": ticket("US-PAY-03", blocked_by=("TASK-PAY-09",)),
            f"{EPIC_DIR}/TASK-PAY-09-i.md": ticket("TASK-PAY-09", type="task", status="draft", blocked_by=("DEC-PAY-02",)),
            f"{EPIC_DIR}/US-PAY-04-d.md": ticket("US-PAY-04", blocked_by=("DEC-PAY-03",)),
            f"{EPIC_DIR}/US-PAY-05-e.md": ticket("US-PAY-05", status="draft"),
            f"{EPIC_DIR}/US-PAY-06-f.md": ticket("US-PAY-06", status="draft", extra="priority: high\n"),
        }
        code, out, _ = self.next(files)
        self.assertEqual(code, 0, out)
        self.assertTrue(out.startswith("NEXT none: nothing is ready;"), out)
        self.assertEqual(self.ids(out, "DECIDE"), ["DEC-PAY-01", "DEC-PAY-02"])
        self.assertIn("DECIDE DEC-PAY-01 (Fixture ticket): blocks 2 ticket(s): US-PAY-01, US-PAY-02", out)
        self.assertIn("DECIDE DEC-PAY-02 (Fixture ticket): blocks 2 ticket(s): TASK-PAY-09, US-PAY-03", out)
        self.assertEqual(self.ids(out, "REFINE"), ["US-PAY-06", "TASK-PAY-09", "US-PAY-05"])
        self.assertIn("WAIT US-PAY-04: blocked by DEC-PAY-03", out)
        lines = [line.split()[0] for line in out.splitlines()]
        self.assertLess(max(i for i, x in enumerate(lines) if x == "DECIDE"), min(i for i, x in enumerate(lines) if x == "REFINE"))

    def test_claimed_tickets_are_not_ready_in_status_and_next_counts_what_waits(self):
        p = Project(files={f"{EPIC_DIR}/US-PAY-01-a.md": ticket("US-PAY-01", title="Claimed")})
        self.addCleanup(p.close)
        p.git("push", "-q", "origin", "HEAD:refs/heads/us-pay-01-a")
        code, out = p.run("deliver.py", "next")
        self.assertEqual(code, 0, out)
        self.assertTrue(out.startswith("NEXT none: nothing is ready; 1 waiting (see WAIT lines)\n"), out)
        code, out = p.run("deliver.py", "status")
        self.assertEqual(code, 0, out)
        self.assertIn("READY (in `next` order)\n\nIN PROGRESS", out)

    def test_nothing_at_all(self):
        code, out, _ = self.next({}, origin=False)
        self.assertEqual(code, 0, out)
        self.assertEqual(out.strip(), "NEXT none: nothing is ready or waiting; run /define to plan more work")


class MergeGateTest(unittest.TestCase):
    """`gate merge` against fake host CLIs, from a pushed branch that follows the workflow."""

    def setUp(self):
        self.p = Project(kitchen=kitchen_yml(host="github"))
        self.addCleanup(self.p.close)
        p = self.p
        base = p.head()
        p.git("checkout", "-q", "-b", BRANCH)
        p.write(STORY_PATH, story("in-progress"))
        p.commit("chore: start US-PAY-99")
        p.write(TESTS, TAGGED)
        p.commit("test: US-PAY-99 failing tests")
        p.write("src/fixture.py", "# implementation\n")
        p.write(TESTS, TAGGED.replace("fail", "pass"))
        p.write(STORY_PATH, story("done"))
        reviewed = p.commit("feat: US-PAY-99")
        self.description = (f"## Ticket\n\nUS-PAY-99 Fixture.\n\n## Plan\n\n| US-PAY-99/AC1 | t |\n| US-PAY-99/AC2 | t |\n\n"
                            "## Gaps found\n\n- None\n\n## Decisions\n\n- None\n\n## Platform changes\n\n- None\n\n"
                            f"## Test changes\n\n- {TESTS}: flipped\n\n## Review report\n\nReviewed commit: {reviewed}\n"
                            "CRITICAL: 0, WARNING: 0, SUGGESTION: 0\n")
        f = p.tmp / "body.md"
        f.write_text(self.description)
        code, out = p.run("deliver.py", "record", f"--body-file={f}", f"--branch={BRANCH}", "--cr=7")
        self.assertEqual(code, 0, out)
        p.commit("docs: delivery record")
        p.git("push", "-q", "origin", BRANCH)
        self.head = p.head()
        self.base = base

    def github(self, **change):
        pr = {"number": 7, "state": "OPEN", "isDraft": False, "baseRefName": "main", "headRefName": BRANCH,
              "headRefOid": self.head, "mergeable": "MERGEABLE", "body": self.description, "url": "https://h/pr/7",
              "statusCheckRollup": [{"name": "check", "status": "COMPLETED", "conclusion": "SUCCESS"}]}
        pr.update(change)
        self.p.rules([{"cli": "gh", "args": ["pr", "view", "7"], "stdout": json.dumps(pr)}])

    def gate(self, head=None):
        return self.p.run("deliver.py", "gate", "merge", "7", f"--head={head or self.head}")

    def test_a_ready_green_change_request_at_the_pinned_head_passes(self):
        self.github()
        code, out = self.gate()
        self.assertEqual(code, 0, out)
        self.assertIn("PASS pr: US-PAY-99", out)
        self.assertIn("PASS merge 7", out)

    def test_each_host_state_problem_fails(self):
        cases = [
            ({}, "c" * 40, "the merge pins cccccccc"),
            ({"state": "MERGED"}, None, "the pull request is merged"),
            ({"isDraft": True}, None, "the pull request is a draft"),
            ({"baseRefName": "dev"}, None, "targets dev, not main"),
            ({"mergeable": "CONFLICTING"}, None, "cannot be merged (CONFLICTING)"),
            ({"mergeable": "UNKNOWN"}, None, "has not decided whether it can be merged"),
            ({"statusCheckRollup": []}, None, "no passing `check` job"),
            ({"statusCheckRollup": [{"name": "check", "status": "COMPLETED", "conclusion": "SUCCESS"},
                                    {"name": "lint", "status": "IN_PROGRESS"}]}, None, "check `lint` is pending"),
            ({"body": self.description.replace("- None\n\n## Platform", "\n## Platform")}, None, "needs at least one bullet"),
            ({"body": self.description + "\nedited live\n"}, None, "gate pr failed (above)"),
        ]
        for change, head, reason in cases:
            with self.subTest(reason=reason):
                self.github(**change)
                code, out = self.gate(head)
                self.assertEqual(code, 1, out)
                self.assertIn(reason, out)

    def test_backlog_errors_fail_the_merge(self):
        self.p.write(f"{EPIC_DIR}/US-PAY-50-bad.md", ticket("US-PAY-50", owner="TBD"))
        self.p.commit("chore: a ticket without an owner")
        self.p.git("push", "-q", "origin", BRANCH)
        self.head = self.p.head()
        self.github()
        code, out = self.gate()
        self.assertEqual(code, 1, out)
        self.assertIn(f"backlog: {EPIC_DIR}/US-PAY-50-bad.md: ready tickets need an owner", out)

    def test_the_checkout_must_be_the_clean_head(self):
        self.github()
        self.p.write("src/fixture.py", "# local edit\n", add=False)
        code, out = self.gate()
        self.assertEqual(code, 1, out)
        self.assertIn("clean checkout", out)

    def test_a_branch_behind_the_default_branch_fails(self):
        self.github()
        newer = self.p.git("commit-tree", f"{self.base}^{{tree}}", "-p", self.base, "-m", "chore: newer main").strip()
        self.p.git("push", "-q", "origin", f"{newer}:refs/heads/main")
        code, out = self.gate()
        self.assertEqual(code, 1, out)
        self.assertIn("behind origin/main", out)

    def test_gitlab(self):
        self.p.write("kitchen.yml", kitchen_yml(host="gitlab"))
        self.p.commit("chore: gitlab")
        self.p.git("push", "-q", "origin", BRANCH)
        head = self.p.head()
        mr = {"iid": 7, "state": "opened", "draft": False, "target_branch": "main", "source_branch": BRANCH, "sha": head,
              "detailed_merge_status": "mergeable", "description": self.description, "web_url": "https://h/mr/7",
              "head_pipeline": {"id": 55, "sha": head, "status": "success"}}
        jobs = [{"id": 1, "name": "check", "status": "success"}]
        self.p.rules([{"cli": "glab", "args": ["mr", "view", "7"], "stdout": json.dumps(mr)},
                      {"cli": "glab", "args": ["api", "--paginate", "projects/:fullpath/pipelines/55/jobs"], "stdout": json.dumps(jobs)}])
        code, out = self.gate(head)
        self.assertEqual(code, 0, out)
        self.assertIn("merge request 7 head", out)
        jobs[0]["status"] = "running"
        self.p.rules([{"cli": "glab", "args": ["mr", "view", "7"], "stdout": json.dumps(mr)},
                      {"cli": "glab", "args": ["api", "--paginate"], "stdout": json.dumps(jobs)}])
        code, out = self.gate(head)
        self.assertEqual(code, 1, out)
        self.assertIn("check `check` is pending", out)

    def test_the_manual_host_never_merges(self):
        self.p.write("kitchen.yml", kitchen_yml())
        code, out = self.gate()
        self.assertEqual(code, 1, out)
        self.assertIn("a person checks and merges", out)
        self.assertEqual(self.p.calls(), [])

    def test_merge_failures_on_change_request_data(self):
        cr = hosts.ChangeRequest(number=7, state="open", draft=False, base="main", head_branch=BRANCH, head_sha="a" * 40,
                                 mergeable=True, body="", checks=[hosts.Check("check", "pass")])
        self.assertEqual(deliver.merge_failures(cr, "a" * 40, "main"), [])
        cr.checks.append(hosts.Check("e2e", "fail"))
        self.assertEqual(deliver.merge_failures(cr, "a" * 40, "main"),
                         ["check `e2e` is failing: never merge on a failing or pending check"])


class CommandsTest(unittest.TestCase):
    def project(self, files=None, kitchen=None, origin=True):
        p = Project(files=files, kitchen=kitchen, origin=origin)
        self.addCleanup(p.close)
        return p

    def test_context_quotes_requirements_adrs_and_related_tickets(self):
        files = {
            f"{EPIC_DIR}/US-PAY-01-a.md": ticket("US-PAY-01", reqs=("PAY-R01", "PAY-R03"), blocked_by=("DEC-PAY-01",),
                                                 body_extra="\n- Follows ADR-002. Relates to US-PAY-02/AC1."),
            f"{EPIC_DIR}/US-PAY-02-b.md": ticket("US-PAY-02", title="Neighbor"),
            f"{EPIC_DIR}/DEC-PAY-01-c.md": ticket("DEC-PAY-01", type="decision", assignee="human", title="Limits"),
            "docs/architecture/ADR-001-storage.md": "# ADR-001\n\nStatus: accepted\n",
            "docs/architecture/ADR-002-queue.md": "# ADR-002\n\nStatus: proposed\n",
            "docs/architecture/ADR-003-cache.md": "# ADR-003\n\nStatus: proposed\n",
        }
        code, out = self.project(files).run("deliver.py", "context", "US-PAY-01")
        self.assertEqual(code, 0, out)
        for want in ("branch: us-pay-01-a", "Live criteria (the only requirements): AC1, AC2",
                     "- PAY-R01: Refunds never exceed the order total.",
                     "- PAY-R03: (superseded 2026-01-02 by PAY-R04) Refunds are emailed.",
                     "- ADR-001 (accepted): docs/architecture/ADR-001-storage.md",
                     "- ADR-002 (proposed) named in the ticket: docs/architecture/ADR-002-queue.md",
                     "- DEC-PAY-01 (Limits): ready", "- US-PAY-02 (Neighbor): ready", "## Ticket body"):
            self.assertIn(want, out)
        self.assertNotIn("ADR-003", out)

    def test_pr_body(self):
        files = {f"{EPIC_DIR}/US-PAY-01-a.md": ticket("US-PAY-01", extra="hotfix: true\n"),
                 f"{EPIC_DIR}/SPK-PAY-01-b.md": ticket("SPK-PAY-01", type="spike", title="Probe", reqs=())}
        p = self.project(files, kitchen=kitchen_yml(autonomy="supervised"))
        code, out = p.run("deliver.py", "pr-body", "US-PAY-01")
        self.assertEqual(code, 0, out)
        self.assertIn("| US-PAY-01/AC1 | |\n| US-PAY-01/AC2 | |", out)
        self.assertIn("Plan approved by: \nTests approved by: ", out)
        self.assertIn("Hotfix", out)
        for section in ("## Ticket", "## Plan", "## Gaps found", "## Decisions", "## Platform changes",
                        "## Test changes", "## Review report", "## Checks"):
            self.assertIn(section, out)
        code, out = p.run("deliver.py", "pr-body", "SPK-PAY-01")
        self.assertIn("## Ticket\n\nNone. Delivers SPK-PAY-01 Probe.", out)

    def test_merge_command_per_host(self):
        sha = "d" * 40
        p = self.project(origin=False)
        code, out = p.run("deliver.py", "merge-command", "7", f"--head={sha}")
        self.assertEqual(code, 1, out)
        self.assertIn("a person merges", out)
        for host, want in [("github", f"gh pr merge 7 --merge --match-head-commit {sha}"),
                           ("gitlab", f"glab mr merge 7 --sha {sha} --auto-merge=false --yes")]:
            with self.subTest(host=host):
                p.write("kitchen.yml", kitchen_yml(host=host), add=False)
                code, out = p.run("deliver.py", "merge-command", "7", f"--head={sha}")
                self.assertEqual((code, out.strip()), (0, want))
        p.write("kitchen.yml", kitchen_yml(host="github", autonomy="pr"), add=False)
        code, out = p.run("deliver.py", "merge-command", "7", f"--head={sha}")
        self.assertIn("NOTE autonomy is `pr`: a person runs this merge", out)
        code, out = p.run("deliver.py", "merge-command", "7", "--head=abc")
        self.assertEqual(code, 1, out)
        self.assertIn("full 40-character", out)

    def test_check_runs_everything_and_names_the_first_failure(self):
        p = self.project(origin=False)
        code, out = p.run("deliver.py", "check")
        self.assertEqual(code, 0, out)
        for step in ("== backlog_check", "== self-test kitchen_lib", "== self-test hosts", "== self-test backlog_check",
                     "== self-test deliver", "== test_command (full run)", "PASS check"):
            self.assertIn(step, out)
        p.write("kitchen.yml", kitchen_yml(check_command="echo lint-ran && exit 3"), add=False)
        code, out = p.run("deliver.py", "check")
        self.assertEqual(code, 1, out)
        self.assertIn("lint-ran", out)
        self.assertIn("FAIL check_command exited 3", out)
        p.write(f"{EPIC_DIR}/US-PAY-01-a.md", ticket("US-PAY-01", owner="TBD"), add=False)
        code, out = p.run("deliver.py", "check")
        self.assertEqual(code, 1, out)
        self.assertIn("FAIL backlog_check", out)
        self.assertNotIn("== self-test", out)

    def test_status(self):
        files = {
            f"{EPIC_DIR}/US-PAY-01-a.md": ticket("US-PAY-01", title="Ready one"),
            f"{EPIC_DIR}/US-PAY-02-b.md": ticket("US-PAY-02", title="Busy", status="in-progress"),
            f"{EPIC_DIR}/US-PAY-03-c.md": ticket("US-PAY-03", title="Waiting", blocked_by=("DEC-PAY-01",)),
            f"{EPIC_DIR}/DEC-PAY-01-d.md": ticket("DEC-PAY-01", type="decision", assignee="human", title="Limits"),
            f"{EPIC_DIR}/US-PAY-04-e.md": ticket("US-PAY-04", status="done", extra="adopted: true\n"),
            f"{EPIC_DIR}/delivery/US-PAY-04.md": "# Delivery record: US-PAY-04\n",
        }
        p = self.project(files)
        p.git("push", "-q", "origin", "HEAD:refs/heads/us-pay-02-b")
        p.git("fetch", "-q", "origin")
        code, out = p.run("deliver.py", "status")
        self.assertEqual(code, 0, out)
        for want in ("STATUS draft: 0  ready: 3  in-progress: 1  done: 1  deferred: 0", "READY (in `next` order)\n  US-PAY-01 Ready one",
                     "IN PROGRESS\n  US-PAY-02 Busy (branch `us-pay-02-b`, on origin)", "BLOCKED\n  US-PAY-03 Waiting: blocked by DEC-PAY-01",
                     "OPEN DECISIONS AND SPIKES\n  DEC-PAY-01 Limits (ready)", "TEST DEBT 2",
                     f"LAST DELIVERIES\n  "):
            self.assertIn(want, out)
        self.assertRegex(out, rf"LAST DELIVERIES\n  \d{{4}}-\d\d-\d\d {EPIC_DIR}/delivery/US-PAY-04.md")
        self.assertRegex(out, r"GAPS \d+")

    def test_release_notes(self):
        so_that = lambda tid, outcome, **kw: ticket(tid, status="done", **kw).replace("so that refunds are safe", f"so that {outcome}")  # noqa: E731
        files = {
            f"{EPIC_DIR}/US-PAY-01-a.md": so_that("US-PAY-01", "nobody is refunded twice", extra="release: v1\n"),
            f"{EPIC_DIR}/US-PAY-02-b.md": so_that("US-PAY-02", "receipts reach customers", extra="release: v2\n"),
            f"{EPIC_DIR}/TASK-PAY-03-c.md": ticket("TASK-PAY-03", type="task", status="done", title="Cache builds", extra="release: v1\n"),
            f"{EPIC_DIR}/US-PAY-04-d.md": ticket("US-PAY-04", status="done", title="Restore refunds", extra="release: v1\nhotfix: true\n"),
            f"{EPIC_DIR}/US-PAY-05-e.md": ticket("US-PAY-05", extra="release: v1\n"),
        }
        p = self.project(files, kitchen=kitchen_yml(releases=["v1", "v2"]))
        code, out = p.run("deliver.py", "release-notes", "v1")
        self.assertEqual(code, 0, out)
        self.assertEqual(out, "# Release notes: v1\n\n## Payments\n\n- Nobody is refunded twice. (US-PAY-01)\n\n"
                              "## Other changes\n\n- Cache builds (TASK-PAY-03)\n- Restore refunds (US-PAY-04, hotfix)\n\n")
        code, out = p.run("deliver.py", "release-notes")
        self.assertIn("# Release notes\n", out)
        self.assertIn("- Receipts reach customers. (US-PAY-02)", out)
        p.git("tag", "v0.1.0")
        p.write(f"{EPIC_DIR}/delivery/US-PAY-02-cr4.md", "# Delivery record: US-PAY-02\n")
        p.commit("docs: delivery record")
        code, out = p.run("deliver.py", "release-notes")
        self.assertEqual(out, "# Release notes since v0.1.0\n\n## Payments\n\n- Receipts reach customers. (US-PAY-02)\n\n")
        code, out = p.run("deliver.py", "release-notes", "v9")
        self.assertEqual(code, 1, out)
        self.assertIn("`v9` is not in kitchen.yml releases", out)

    def test_usage_errors_exit_2_before_reading_the_config(self):
        p = self.project(origin=False)
        (p.root / "kitchen.yml").unlink()
        for args in (["bogus"], ["gate", "merge", "5"], ["gate", "merge", "5", "--head=abc123"], ["record", "--body=x"],
                     ["gate", "pr", "--branch=x"], ["gate", "pr", "--branch=x", "--body-file=f", "--from-record"], ["next", "--now"]):
            with self.subTest(args=args):
                code, out = p.run("deliver.py", *args)
                self.assertEqual(code, 2, out)
                self.assertIn("Usage", out)
        code, out = p.run("deliver.py", "next")
        self.assertEqual(code, 1, out)
        self.assertIn("FAIL kitchen.yml: not found", out)

    def test_gate_pr_falls_back_to_the_local_default_branch(self):
        p = self.project(origin=False)
        p.git("checkout", "-q", "-b", "docs/notes")
        f = p.tmp / "body.md"
        f.write_text("## Ticket\n\nNone. Notes.\n")
        code, out = p.run("deliver.py", "record", f"--body-file={f}", "--branch=docs/notes")
        self.assertEqual(code, 0, out)
        p.commit("docs: delivery record")
        code, out = p.run("deliver.py", "gate", "pr", f"--body-file={f}", "--branch=docs/notes")
        self.assertEqual(code, 0, out)
        self.assertIn("NOTE origin/main does not exist: measuring from the local main branch", out)
        p.git("branch", "-m", "main", "trunk-renamed")
        code, out = p.run("deliver.py", "gate", "pr", f"--body-file={f}", "--branch=docs/notes")
        self.assertEqual(code, 1, out)
        self.assertIn("pass --base=<rev>", out)

    def test_self_test(self):
        code, out = self.project(origin=False).run("deliver.py", "--self-test")
        self.assertEqual(code, 0, out)
        self.assertIn("PASS self-test", out)


if __name__ == "__main__":
    unittest.main()
