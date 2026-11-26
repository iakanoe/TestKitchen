"""US-DLV-38: `gate pr` judges the revision `--head` names (DLV-R48; decision log, "gate pr reads tickets and kitchen.yml at --head").

The ticket files and `kitchen.yml` are read at `--head`, like the branch history, the
tagged tests, and the delivery record, so the verdict never depends on which commit is
checked out or on uncommitted edits. Each test builds a fixture branch in a throwaway
project (tests/helpers/kitchen_project.py) the way the workflow builds it, then runs
`scripts/deliver.py gate pr --head=<rev>` as a subprocess from a checkout the test picks.

This file carries no no-trace marker, so its test names are real tags of US-DLV-38. The
fixture ticket's own tags and criterion references are therefore never written out in
full here: they come from tests/test_deliver.py (a no-trace file) or are assembled from
`TID`, so this repository's trace scan does not read them as tags of a missing ticket.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_deliver as td  # noqa: E402
import json  # noqa: E402
from helpers.kitchen_project import EPIC, kitchen_yml, ticket  # noqa: E402

TID = "US-PAY-" + "99"  # the fixture story of tests/test_deliver.py
RENAMED_PATH = f"{td.EPIC_DIR}/{TID}-renamed.md"
RENAMED_BRANCH = TID.lower() + "-renamed"
OTHER_EPIC_DIR = "backlog/REF-refunds"


def story_with(extra=""):
    """The fixture story with extra frontmatter, as `story_branch` wants it (a function of the status)."""
    return lambda status: td.story(status, extra=extra)


class AtHead(td.Repo):
    """Fixture branches built as in tests/test_deliver.py (GatePrTest's helpers, reused as they are)."""

    story_branch = td.GatePrTest.story_branch
    body = td.GatePrTest.body
    record = td.GatePrTest.record

    def passing(self, text=td.story, before_record=None):
        """A branch that follows the workflow and passes `gate pr`: (head sha, description)."""
        self.story_branch(text=text)
        if before_record:
            before_record()
        self.commit(f"chore: capture {TID}")
        body = self.body()
        self.record(body)
        return self.p.head(), body

    def on_top(self, rev, rel, text, message="chore: another revision"):
        """A commit on `rev` that writes one file; returns its sha (the checkout is left there)."""
        self.p.git("checkout", "-q", "--force", "--detach", rev)
        self.write(rel, text)
        return self.commit(message)

    def gate_at(self, head, body, branch=td.BRANCH, checkout=None):
        """`gate pr --head=<head>`, run from `checkout` (default: whatever is checked out now)."""
        if checkout:
            self.p.git("checkout", "-q", "--force", "--detach", checkout)
        f = self.p.tmp / "body.md"
        f.write_bytes(body.encode("utf-8"))
        return self.run_script("gate", "pr", f"--body-file={f}", f"--branch={branch}", f"--base={self.base}",
                               f"--head={head}")

    def claim_of(self, head):
        """The branch's first commit: the claim, where the ticket is `in-progress`."""
        return self.p.git("rev-list", "--reverse", f"{self.base}..{head}").split()[0]

    def assertVerdict(self, result, code, *lines):
        """Exit code `code`, and each of `lines` printed as a whole line."""
        exit_code, out = result
        self.assertEqual(exit_code, code, out)
        printed = out.splitlines()
        for line in lines:
            self.assertIn(line, printed, out)

    def fail_lines(self, out):
        return [line for line in out.splitlines() if line.startswith(("PASS", "FAIL"))]


class TicketFilesAtHead(AtHead):
    def test_us_dlv_38_ac1_a_ticket_done_at_head_passes_from_a_checkout_where_it_is_in_progress(self):
        head, body = self.passing()
        self.assertVerdict(self.gate_at(head, body, checkout=self.claim_of(head)), 0, f"PASS pr: {TID}")

    def test_us_dlv_38_ac1_a_ticket_in_progress_at_head_fails_from_a_checkout_where_it_is_done(self):
        self.story_branch()
        self.write(td.STORY_PATH, td.story("in-progress"))  # undo story_branch's uncommitted `done`
        body = self.body()
        self.record(body)
        head = self.p.head()
        self.on_top(head, td.STORY_PATH, td.story("done"))
        code, out = self.gate_at(head, body)
        self.assertEqual(code, 1, out)
        self.assertIn(f"FAIL {TID} is `in-progress`", out)

    def test_us_dlv_38_ac1_live_criteria_come_from_head(self):
        head, body = self.passing()
        three = ticket(TID, title="Fixture story", status="done", criteria=[
            "Given a fixture, when it is checked, then it passes.",
            "Given a fixture, when it is checked again, then it still passes.",
            "Given a fixture, when it is checked a third time, then it passes."])
        self.on_top(head, td.STORY_PATH, three)
        self.assertVerdict(self.gate_at(head, body), 0, f"PASS pr: {TID}")
        # The reverse: the third criterion exists at head only, so the plan misses it.
        self.p.git("checkout", "-q", "--force", "--detach", self.base)
        self.story_branch(text=lambda status: ticket(TID, title="Fixture story", status=status, criteria=[
            "Given a fixture, when it is checked, then it passes.",
            "Given a fixture, when it is checked again, then it still passes.",
            "Given a fixture, when it is checked a third time, then it passes."]))
        self.commit(f"chore: capture {TID}")
        body3 = self.body()
        self.record(body3)
        head3 = self.p.head()
        self.on_top(head3, td.STORY_PATH, td.story("done"))
        code, out = self.gate_at(head3, body3)
        self.assertEqual(code, 1, out)
        self.assertIn(f"FAIL Plan has no row for {TID}/AC3", out.splitlines())

    def test_us_dlv_38_ac1_the_hotfix_flag_comes_from_head(self):
        head, body = self.passing(text=story_with("hotfix: true\n"))
        self.on_top(head, td.STORY_PATH, td.story("done"))
        code, out = self.gate_at(head, body)
        self.assertEqual(code, 1, out)
        self.assertIn('FAIL hotfix: "## Decisions" needs a bullet saying why the hotfix lane was used, '
                      'ending "Log: <entry title>"', out.splitlines())
        self.assertIn('FAIL hotfix: "## Gaps found" must name the follow-up ticket', out.splitlines())
        # The reverse: the flag only in the checkout changes nothing.
        self.p.git("checkout", "-q", "--force", "--detach", self.base)
        head, body = self.passing()
        self.on_top(head, td.STORY_PATH, td.story("done", extra="hotfix: true\n"))
        self.assertVerdict(self.gate_at(head, body), 0, f"PASS pr: {TID}")

    def test_us_dlv_38_ac1_the_file_name_and_branch_come_from_head(self):
        old, body = self.passing()
        self.p.git("mv", td.STORY_PATH, RENAMED_PATH)
        renamed = self.commit(f"chore: rename {TID}")
        self.p.git("checkout", "-q", "--force", "--detach", old)
        self.assertVerdict(self.gate_at(renamed, body, branch=RENAMED_BRANCH), 0, f"PASS pr: {TID}")
        code, out = self.gate_at(renamed, body, branch=td.BRANCH)
        self.assertEqual(code, 1, out)
        self.assertIn(f"FAIL branch `{td.BRANCH}` is not the ticket's file name `{RENAMED_BRANCH}`", out.splitlines())

    def test_us_dlv_38_ac1_the_epic_folder_and_record_path_come_from_head(self):
        old, body = self.passing()
        self.write(f"{OTHER_EPIC_DIR}/epic.md", EPIC.format(extra="").replace("EP-PAY", "EP-REF"))
        self.p.git("mv", td.STORY_PATH, f"{OTHER_EPIC_DIR}/{TID}-fixture.md")
        (self.p.root / OTHER_EPIC_DIR / "delivery").mkdir()
        self.p.git("mv", f"{td.EPIC_DIR}/delivery/{TID}.md", f"{OTHER_EPIC_DIR}/delivery/{TID}.md")
        moved = self.commit(f"chore: move {TID}")
        self.assertVerdict(self.gate_at(moved, body, checkout=old), 0, f"PASS pr: {TID}")

    def test_us_dlv_38_ac1_the_ticket_type_comes_from_head(self):
        """A story needs the freeze commit; the same file typed as an untagged task would not."""
        self.write(td.STORY_PATH, td.story("in-progress"))
        self.commit(f"chore: start {TID}")
        self.write("src/fixture.py", "# implementation\n")
        self.write(td.STORY_PATH, td.story("done"))
        self.commit(f"feat: {TID} implementation")
        body = self.body()
        self.record(body)
        head = self.p.head()
        self.on_top(head, td.STORY_PATH, ticket(TID, type="task", title="Fixture story", status="done"))
        code, out = self.gate_at(head, body)
        self.assertEqual(code, 1, out)
        self.assertTrue(any(line.startswith(f'FAIL no commit "test: {TID} failing tests" on the branch')
                            for line in out.splitlines()), out)


class KitchenYmlAtHead(AtHead):
    def test_us_dlv_38_ac2_autonomy_comes_from_head(self):
        head, body = self.passing(before_record=lambda: self.write("kitchen.yml", kitchen_yml(autonomy="supervised")))
        self.on_top(head, "kitchen.yml", kitchen_yml())
        code, out = self.gate_at(head, body)
        self.assertEqual(code, 1, out)
        for what in ("Plan", "Tests"):
            self.assertIn(f'FAIL autonomy is supervised: "## Plan" needs "{what} approved by: <name>"', out.splitlines())
        # The reverse: supervised only in the checkout changes nothing.
        self.p.git("checkout", "-q", "--force", "--detach", self.base)
        head, body = self.passing()
        self.on_top(head, "kitchen.yml", kitchen_yml(autonomy="supervised"))
        self.assertVerdict(self.gate_at(head, body), 0, f"PASS pr: {TID}")

    def notes_branch(self, at_head):
        """A passing-shaped branch whose claim commit also adds notes/plan.txt, with `at_head` as kitchen.yml."""
        self.write("notes/plan.txt", "plan\n")
        self.write("kitchen.yml", at_head)
        return self.passing()

    def test_us_dlv_38_ac2_the_code_globs_come_from_head(self):
        with_notes = kitchen_yml(code=["src/**", "notes/**"])
        head, body = self.notes_branch(with_notes)
        self.on_top(head, "kitchen.yml", kitchen_yml())
        code, out = self.gate_at(head, body)
        self.assertEqual(code, 1, out)
        self.assertTrue(any(line.startswith("FAIL notes/plan.txt changed in ") and
                            line.endswith("at or before the freeze commit: implementation must come after the failing tests")
                            for line in out.splitlines()), out)
        # The reverse: notes/ is code only in the checkout.
        self.p.git("checkout", "-q", "--force", "--detach", self.base)
        head, body = self.notes_branch(kitchen_yml())
        self.on_top(head, "kitchen.yml", with_notes)
        self.assertVerdict(self.gate_at(head, body), 0, f"PASS pr: {TID}")

    def test_us_dlv_38_ac2_the_test_globs_come_from_head(self):
        head, body = self.passing(before_record=lambda: self.write(
            "kitchen.yml", kitchen_yml().replace('tests: ["tests/**"]', 'tests: ["spec/**"]')))
        self.on_top(head, "kitchen.yml", kitchen_yml())
        code, out = self.gate_at(head, body)
        self.assertEqual(code, 1, out)
        self.assertIn(f"FAIL {TID}/AC1 had no tagged test at the freeze commit", out.splitlines())

    def test_us_dlv_38_ac2_the_ignore_globs_come_from_head(self):
        head, body = self.notes_branch(kitchen_yml(code=["src/**", "notes/**"], ignore=["notes/**"]))
        self.on_top(head, "kitchen.yml", kitchen_yml(code=["src/**", "notes/**"]))
        self.assertVerdict(self.gate_at(head, body), 0, f"PASS pr: {TID}")

    def test_us_dlv_38_ac2_an_invalid_kitchen_yml_at_head_fails_even_with_a_valid_checkout(self):
        good, body = self.passing()
        self.write("kitchen.yml", "tests: [\n")
        bad = self.commit("chore: break kitchen.yml")
        code, out = self.gate_at(bad, body, checkout=good)
        self.assertEqual(code, 1, out)
        self.assertTrue(any(line.startswith("FAIL kitchen.yml: invalid YAML") for line in out.splitlines()), out)

    def test_us_dlv_38_ac2_an_invalid_kitchen_yml_in_the_checkout_does_not_matter(self):
        head, body = self.passing()
        self.on_top(head, "kitchen.yml", "tests: [\n")
        self.assertVerdict(self.gate_at(head, body), 0, f"PASS pr: {TID}")

    def test_us_dlv_38_ac2_a_kitchen_yml_missing_at_head_fails_even_with_one_in_the_checkout(self):
        good, body = self.passing()
        self.p.git("rm", "-q", "kitchen.yml")
        missing = self.commit("chore: remove kitchen.yml")
        code, out = self.gate_at(missing, body, checkout=good)
        self.assertEqual(code, 1, out)
        self.assertTrue(any(line.startswith("FAIL kitchen.yml: not found at ") for line in out.splitlines()), out)


class UncommittedEdits(AtHead):
    def test_us_dlv_38_ac3_uncommitted_edits_to_the_ticket_and_kitchen_yml_are_ignored(self):
        head, body = self.passing()
        self.p.write(td.STORY_PATH, td.story("ready"), add=False)
        self.p.write("kitchen.yml", kitchen_yml(autonomy="supervised"), add=False)
        for rev in ("HEAD", head):
            self.assertVerdict(self.gate_at(rev, body), 0, f"PASS pr: {TID}")
        self.p.git("add", "--", td.STORY_PATH, "kitchen.yml")  # staged, still not committed
        for rev in ("HEAD", head):
            self.assertVerdict(self.gate_at(rev, body), 0, f"PASS pr: {TID}")

    def test_us_dlv_38_ac3_an_uncommitted_invalid_kitchen_yml_is_ignored(self):
        head, body = self.passing()
        self.p.write("kitchen.yml", "tests: [\n", add=False)
        self.assertVerdict(self.gate_at(head, body), 0, f"PASS pr: {TID}")

    def test_us_dlv_38_ac3_an_uncommitted_done_does_not_hide_a_committed_in_progress(self):
        self.story_branch()
        self.write(td.STORY_PATH, td.story("in-progress"))  # undo story_branch's uncommitted `done`
        body = self.body()
        self.record(body)
        self.p.write(td.STORY_PATH, td.story("done"), add=False)
        code, out = self.gate_at("HEAD", body)
        self.assertEqual(code, 1, out)
        self.assertIn(f"FAIL {TID} is `in-progress`", out)

    def test_us_dlv_38_ac3_an_untracked_ticket_file_is_not_read(self):
        self.write("NOTES.txt", "notes\n")
        self.commit("chore: a branch that never adds the ticket")
        self.p.write(td.STORY_PATH, td.story("done"), add=False)
        body = self.body()
        self.assertVerdict(self.gate_at("HEAD", body), 1, f"FAIL {TID} does not exist")


class SameVerdictFromAnyCheckout(AtHead):
    def test_us_dlv_38_ac4_a_passing_branch_prints_the_same_from_the_base_commit(self):
        head, body = self.passing()
        own = self.gate_at(head, body, checkout=head)
        from_base = self.gate_at(head, body, checkout=self.base)
        self.assertVerdict(own, 0, f"PASS pr: {TID}")
        self.assertEqual(from_base, own)

    def test_us_dlv_38_ac4_a_failing_branch_prints_the_same_from_the_base_commit(self):
        self.story_branch()
        self.commit(f"chore: capture {TID}")
        body = self.body(plan=("AC1",))
        self.record(body)
        head = self.p.head()
        own = self.gate_at(head, body, checkout=head)
        from_base = self.gate_at(head, body, checkout=self.base)
        self.assertVerdict(own, 1, f"FAIL Plan has no row for {TID}/AC2")
        self.assertEqual(self.fail_lines(from_base[1]), self.fail_lines(own[1]))
        self.assertEqual(from_base, own)

    def test_us_dlv_38_ac4_a_checkout_without_kitchen_yml_prints_the_same(self):
        head, body = self.passing()
        own = self.gate_at(head, body, checkout=head)
        self.p.git("checkout", "-q", "--force", "--detach", self.base)
        self.p.git("rm", "-q", "kitchen.yml")
        self.commit("chore: a revision with no kitchen.yml")
        self.assertVerdict(own, 0, f"PASS pr: {TID}")
        self.assertEqual(self.gate_at(head, body), own)


    def test_us_dlv_38_ac4_a_kitchen_lock_only_at_head_prints_the_same(self):
        """kitchen.lock decides which files are framework files (excluded from every scan, so
        never code); read from the checkout, it would change the verdict between checkouts."""
        self.write("kitchen.lock", json.dumps({"files": {"notes/plan.txt": "0" * 64}}))
        self.write("notes/plan.txt", "plan\n")
        self.write("kitchen.yml", kitchen_yml(code=["src/**", "notes/**"]))
        head, body = self.passing()
        own = self.gate_at(head, body, checkout=head)
        self.p.git("rm", "-q", "kitchen.lock")
        self.commit("chore: drop the lock in another revision")
        self.assertVerdict(own, 0, f"PASS pr: {TID}")
        self.assertEqual(self.gate_at(head, body), own)


class TicketExistsAtHead(AtHead):
    def test_us_dlv_38_ac5_a_ticket_missing_at_head_does_not_exist(self):
        self.write("NOTES.txt", "notes\n")
        without = self.commit("chore: a branch that never adds the ticket")
        self.p.git("checkout", "-q", "--force", "--detach", self.base)
        branch_head, body = self.passing()
        result = self.gate_at(without, body, checkout=branch_head)
        self.assertVerdict(result, 1, f"FAIL {TID} does not exist")
        self.assertEqual(self.fail_lines(result[1]), [f"FAIL {TID} does not exist"])

    def test_us_dlv_38_ac5_a_ticket_present_only_at_head_is_judged_normally(self):
        head, body = self.passing()
        self.assertVerdict(self.gate_at(head, body, checkout=self.base), 0, f"PASS pr: {TID}")
        self.assertFalse((self.p.root / td.STORY_PATH).exists(), "the checkout must not hold the ticket file")
        short = self.body(plan=("AC1",))
        self.assertVerdict(self.gate_at(head, short, checkout=self.base), 1, f"FAIL Plan has no row for {TID}/AC2")


if __name__ == "__main__":
    unittest.main()
