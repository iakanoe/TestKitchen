# test-kitchen: no-trace (the tickets, tags, and TODOs in this file are test data)
"""Tests for template/scripts/backlog_check.py: validation, trace, coverage, and its modes.

Each test builds a small project (tests/helpers/kitchen_project.py) from a valid baseline,
changes one thing, and runs the script as a subprocess from the project, the way people
and CI run it.

Run: python3 -m unittest discover -s tests -p 'test_backlog_check.py'
"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers.kitchen_project import EPIC, Project, kitchen_yml, ticket  # noqa: E402

EPIC_DIR = "backlog/PAY-payments"
US1 = f"{EPIC_DIR}/US-PAY-01-refund-limit.md"
TASK2 = f"{EPIC_DIR}/TASK-PAY-02-log-refunds.md"
US5 = f"{EPIC_DIR}/US-PAY-05-new.md"
DEC1 = f"{EPIC_DIR}/DEC-PAY-01-limit-source.md"

# A valid project: a done story with tagged tests (both tag forms), a ready task, code
# whose TODO names a ticket. Every requirement that is not superseded is covered.
BASELINE = {
    US1: ticket("US-PAY-01", status="done", reqs=("PAY-R01", "PAY-R04")),
    TASK2: ticket("TASK-PAY-02", type="task", reqs=("PAY-R02",), extra="refined: 2026-01-05\n"),
    "tests/test_pay.txt": "test_us_pay_01_ac1_refused pass\n[US-PAY-01/AC2] logged pass\n",
    "src/pay.py": "# Refund rules.\n# TODO(US-PAY-01): tidy the names\n",
    # The epic claims the code, so the baseline has no unmapped-code gap.
    "backlog/PAY-payments/epic.md": EPIC.format(extra='code: ["src/**"]\n'),
}


class Base(unittest.TestCase):
    def project(self, files=None, git=False, origin=False, kitchen=None):
        merged = dict(BASELINE)
        merged.update(files or {})
        p = Project(files=merged, git=git, origin=origin, kitchen=kitchen)
        self.addCleanup(p.close)
        return p

    def check(self, files=None, *args, kitchen=None):
        return self.project(files, kitchen=kitchen).run("backlog_check.py", *args)

    def assertClean(self, files=None, *args, kitchen=None):
        code, out = self.check(files, *args, kitchen=kitchen)
        self.assertEqual(code, 0, out)
        self.assertNotIn("ERROR", out)
        self.assertNotIn("WARN", out)
        return out

    def assertError(self, files, text, *args, kitchen=None):
        code, out = self.check(files, *args, kitchen=kitchen)
        self.assertEqual(code, 1, out)
        self.assertTrue(any(line.startswith("ERROR") and text in line for line in out.splitlines()), out)
        return out

    def assertWarn(self, files, text, *args, kitchen=None):
        code, out = self.check(files, *args, kitchen=kitchen)
        self.assertEqual(code, 0, out)
        self.assertTrue(any(line.startswith("WARN ") and text in line for line in out.splitlines()), out)
        return out


class ValidationTest(Base):
    def test_the_baseline_is_clean(self):
        out = self.assertClean()
        self.assertIn("backlog: 1 epic, 1 story, 1 task, 0 decision, 0 spike; 0 error(s), 0 warning(s)", out)

    def test_runs_from_any_folder(self):
        p = self.project()
        (p.root / "src" / "deep").mkdir()
        code, out = p.run("backlog_check.py", cwd=p.root / "src" / "deep")
        self.assertEqual(code, 0, out)

    def test_ids_types_and_file_names(self):
        cases = [
            ({US5: ticket("US-PAY-05", type="task")}, "does not match type"),
            ({f"{EPIC_DIR}/US-PAY-05.md": ticket("US-PAY-05")}, "file name must be `US-PAY-05-<kebab-case-slug>.md`"),
            ({f"{EPIC_DIR}/US-PAY-05-Bad-Name.md": ticket("US-PAY-05")}, "file name must be"),
            ({US5: ticket("US-PAY-05", type="bug")}, "type `bug` not in"),
            ({US5: ticket("US-PAY-5")}, "does not match type"),
            ({f"{EPIC_DIR}/US-PAY-01-copy.md": ticket("US-PAY-01")}, "duplicate id `US-PAY-01`"),
            ({"backlog/PAY-payments/sub/epic.md": EPIC.format(extra="").replace("EP-PAY", "EP-SUB")},
             "an epic lives in its own folder"),
            ({"backlog/payments/epic.md": EPIC.format(extra="").replace("EP-PAY", "EP-BILL")},
             "an epic's folder is named `BILL-<slug>`"),
        ]
        for files, text in cases:
            with self.subTest(text=text):
                self.assertError(files, text)

    def test_epic_membership(self):
        cases = [
            ({US5: ticket("US-PAY-05", epic="EP-NOPE")}, "epic `EP-NOPE` does not exist"),
            ({"backlog/BILL-billing/epic.md": EPIC.format(extra="").replace("EP-PAY", "EP-BILL"),
              "backlog/BILL-billing/US-PAY-05-x.md": ticket("US-PAY-05")}, "not in its epic's folder"),
            ({f"{EPIC_DIR}/US-BILL-05-x.md": ticket("US-BILL-05")}, "id code `BILL` does not match epic `EP-PAY`"),
        ]
        for files, text in cases:
            with self.subTest(text=text):
                self.assertError(files, text)

    def test_field_values(self):
        cases = [
            ({US5: ticket("US-PAY-05", extra="priority: urgent\n")}, "priority `urgent` not in"),
            ({US5: ticket("US-PAY-05", extra="refined: soon\n")}, "is not a date"),
            ({US5: ticket("US-PAY-05", extra="hotfix: yes please\n")}, "`hotfix` is true or false"),
            ({US5: ticket("US-PAY-05", status="started")}, "status `started` not in"),
            ({US5: ticket("US-PAY-05", assignee="robot")}, "assignee_type `robot` not in"),
            ({DEC1: ticket("DEC-PAY-01", type="decision", assignee="agent")}, "decisions are assigned to humans"),
            ({US5: ticket("US-PAY-05", extra="code: [src/**]\n")}, "`code:` globs belong on epics only"),
            ({US5: ticket("US-PAY-05").replace("owner: Team\n", "")}, "missing `owner`"),
            ({US5: ticket("US-PAY-05", reqs=())}, "ready stories cite at least one requirement"),
            ({US5: "No frontmatter here.\n"}, "missing frontmatter"),
            ({US5: "---\nid: [unclosed\n---\nbody\n"}, "invalid YAML frontmatter"),
        ]
        for files, text in cases:
            with self.subTest(text=text):
                self.assertError(files, text)

    def test_unknown_fields_warn(self):
        self.assertWarn({US5: ticket("US-PAY-05", reqs=("PAY-R01",), extra="relase: v1\n")}, "unknown field `relase`")

    def test_tasks_and_spikes_may_cite_no_requirement(self):
        self.assertClean({f"{EPIC_DIR}/TASK-PAY-03-ci.md": ticket("TASK-PAY-03", type="task", reqs=()),
                          f"{EPIC_DIR}/SPK-PAY-01-probe.md": ticket("SPK-PAY-01", type="spike", reqs=())})

    def test_references(self):
        cases = [
            ({US5: ticket("US-PAY-05", blocked_by=("US-PAY-77",))}, "blocked_by `US-PAY-77` does not exist"),
            ({US5: ticket("US-PAY-05", blocked_by=("US-PAY-05",))}, "blocked_by names the ticket itself"),
            ({US5: ticket("US-PAY-05", reqs=("PAY-R99",))}, "source_reqs `PAY-R99` is not defined"),
            ({US5: ticket("US-PAY-05", extra="fixes: [US-PAY-01/AC9]\n")}, "fixes `US-PAY-01/AC9` is not a live"),
            ({US5: ticket("US-PAY-05", extra="fixes: [PAY-R01]\n")}, "is not a criterion reference"),
            ({US5: ticket("US-PAY-05", body_extra="\n- Relates to US-PAY-01/AC7.")}, "`US-PAY-01/AC7` is not a live"),
        ]
        for files, text in cases:
            with self.subTest(text=text):
                self.assertError(files, text)
        self.assertClean({US5: ticket("US-PAY-05", extra="fixes: [US-PAY-01/AC2]\n",
                                      body_extra="\n- Restores US-PAY-01/AC2.")})

    def test_blocked_by_cycles_are_reported_once(self):
        out = self.assertError({US5: ticket("US-PAY-05", blocked_by=("US-PAY-06",)),
                                f"{EPIC_DIR}/US-PAY-06-x.md": ticket("US-PAY-06", blocked_by=("US-PAY-05",))},
                               "blocked_by cycle US-PAY-05 -> US-PAY-06 -> US-PAY-05")
        self.assertEqual(out.count("blocked_by cycle"), 1)

    def test_ready_may_wait_for_a_blocker_but_done_may_not(self):
        """blocked_by means "can start, can't finish"."""
        self.assertClean({US5: ticket("US-PAY-05", blocked_by=("TASK-PAY-02",))})
        self.assertError({US5: ticket("US-PAY-05", status="done", blocked_by=("TASK-PAY-02",)),
                          "tests/t5.txt": "us_pay_05_ac1 pass\nus_pay_05_ac2 pass\n"},
                         "done, but blocker TASK-PAY-02 is `ready`")

    def test_criteria(self):
        story = ticket("US-PAY-05", criteria=["When a refund is asked, then it is refused."])
        self.assertError({US5: story}, "AC1: a story's criterion reads `Given …")
        swapped = ticket("US-PAY-05").replace("- AC1:", "- ACX:").replace("- AC2:", "- AC1:").replace("- ACX:", "- AC2:")
        self.assertError({US5: swapped}, "AC1 is duplicated or out of order")
        self.assertError({US5: ticket("US-PAY-05", criteria=["Given a, when b, then c.", "Given d, when e, then f."])
                         .replace("- AC2:", "- AC 2:")}, "criterion not in `- AC<n>: …` form")
        self.assertError({US5: ticket("US-PAY-05", criteria=["(removed 2026-01-01, replaced by US-PAY-06)"])},
                         "a ready story needs at least one live acceptance criterion")
        self.assertClean({US5: ticket("US-PAY-05", criteria=["(removed 2026-01-01, see DEC-PAY-01 (merged))",
                                                             "Given a, when b, then c."])})

    def test_owner_and_open_questions(self):
        cases = [
            ({US5: ticket("US-PAY-05", owner="TBD")}, "ready tickets need an owner"),
            ({US5: ticket("US-PAY-05", questions=["Who approves refunds?"])}, "open question is unanswered"),
            ({US5: ticket("US-PAY-05", questions=["Limit source: DEC-PAY-09."])}, "names unknown ticket `DEC-PAY-09`"),
            ({DEC1: ticket("DEC-PAY-01", type="decision", assignee="human", status="draft"),
              US5: ticket("US-PAY-05", questions=["Limit source: DEC-PAY-01."])},
             "open DEC-PAY-01 needs `Until decided: …`"),
            ({DEC1: ticket("DEC-PAY-01", type="decision", assignee="human", status="draft"),
              US5: ticket("US-PAY-05", questions=["Limit source: DEC-PAY-01. Until decided: AC9 refuses."])},
             "open DEC-PAY-01 needs `Until decided: …`"),
        ]
        for files, text in cases:
            with self.subTest(text=text):
                self.assertError(files, text)
        dec = ticket("DEC-PAY-01", type="decision", assignee="human", status="draft")
        self.assertClean({DEC1: dec, US5: ticket("US-PAY-05", questions=["Limit source: DEC-PAY-01. Until decided: AC1 refuses."])})
        self.assertClean({DEC1: dec, US5: ticket("US-PAY-05", blocked_by=("DEC-PAY-01",), questions=["Limit source: DEC-PAY-01."])})
        # Drafts may hold bare questions: they are gaps (--gaps), not errors.
        self.assertClean({US5: ticket("US-PAY-05", status="draft", owner="TBD", questions=["Who approves?"])})

    def test_a_decided_dec_may_carry_an_outcome_section(self):
        dec = ticket("DEC-PAY-01", type="decision", assignee="human", status="done") + "\n## Outcome\n\nB, logged.\n"
        self.assertClean({DEC1: dec, US5: ticket("US-PAY-05", questions=["Limit source: DEC-PAY-01."])})

    def test_windows_line_endings_parse_the_same(self):
        self.assertClean({US5: ticket("US-PAY-05").replace("\n", "\r\n")})

    def test_delivery_records_are_not_tickets(self):
        self.assertClean({f"{EPIC_DIR}/delivery/US-PAY-01.md": "# Delivery record\n\nNo frontmatter, see docs/x.md.\n",
                          "backlog/delivery/fix-thing.md": "# Delivery record\n", "backlog/README.md": "# Rules\n"})

    def test_requirement_files(self):
        cases = [
            ({"docs/requirements/payments.md": "- PAY-R09: x\n"}, "requirement files are named `<CODE>-<name>.md`"),
            ({"docs/requirements/AUTH-login.md": "- PAY-R09: x\n"}, "PAY-R09 does not belong in a AUTH file"),
            ({"docs/requirements/PAY-more.md": "- PAY-R01: again\n"}, "PAY-R01 is defined twice"),
            ({"docs/requirements/PAY-more.md": "- PAY-R09: (superseded 2026-01-01 by PAY-R98) x\n"},
             "superseded by PAY-R98, which is not defined"),
        ]
        for files, text in cases:
            with self.subTest(text=text):
                self.assertError(files, text)

    def test_config_errors_are_reported(self):
        code, out = self.check(kitchen="tests: [t/**]\ncode: [s/**]\ntest_command: x\ncolour: blue\n")
        self.assertEqual(code, 1, out)
        self.assertIn("ERROR kitchen.yml: unknown key `colour`", out)


class ReleaseTest(Base):
    KITCHEN = kitchen_yml(releases=["v1", "v2", "later"])

    def test_release_rules(self):
        cases = [
            ({US5: ticket("US-PAY-05", extra="release: v9\n")}, "release `v9` not in kitchen.yml releases"),
            ({US5: ticket("US-PAY-05")}, "ready tickets need a release"),
            ({US5: ticket("US-PAY-05", status="deferred", extra="release: v1\n")}, "deferred tickets go to the last slice"),
            ({US5: ticket("US-PAY-05", blocked_by=("US-PAY-06",), extra="release: v1\n"),
              f"{EPIC_DIR}/US-PAY-06-x.md": ticket("US-PAY-06", extra="release: v2\n")},
             "release `v1` is earlier than unfinished blocker US-PAY-06 (`v2`)"),
        ]
        base = {US1: ticket("US-PAY-01", status="done", reqs=("PAY-R01", "PAY-R04"), extra="release: v1\n"),
                TASK2: ticket("TASK-PAY-02", type="task", reqs=("PAY-R02",), extra="release: v1\n")}
        for files, text in cases:
            with self.subTest(text=text):
                self.assertError(dict(base, **files), text, kitchen=self.KITCHEN)
        self.assertClean(dict(base, **{US5: ticket("US-PAY-05", extra="release: v2\n")}), kitchen=self.KITCHEN)

    def test_a_release_without_slices_warns(self):
        self.assertWarn({US5: ticket("US-PAY-05", extra="release: v1\n")}, "release `v1` is ignored")


class TraceTest(Base):
    def test_tags_must_name_live_criteria_of_started_tickets(self):
        self.assertError({"tests/t.txt": "us_pay_01_ac9 pass\n"}, "tag `US-PAY-01/AC9` is not a live acceptance criterion")
        self.assertError({US5: ticket("US-PAY-05", status="draft"), "tests/t.txt": "[US-PAY-05/AC1] x pass\n"},
                         "tag `US-PAY-05/AC1` belongs to a `draft` ticket")
        self.assertError({"tests/t.txt": "test_us_pay_77_ac1 pass\n"}, "tag `US-PAY-77/AC1` is not a live")

    def test_tags_outside_test_files_do_not_count(self):
        self.assertError({"tests/test_pay.txt": "nothing\n", "src/pay.py": "# test_us_pay_01_ac1 [US-PAY-01/AC2]\n"},
                         "done, but no tagged test for AC1, AC2")

    def test_a_bug_fix_test_may_also_tag_the_criterion_it_restores(self):
        """A fix story's test carries its own tag and the broken done story's tag."""
        self.assertClean({US5: ticket("US-PAY-05", status="in-progress", extra="fixes: [US-PAY-01/AC2]\n"),
                          "tests/fix.txt": "[US-PAY-05/AC1] [US-PAY-01/AC2] x\nus_pay_05_ac2 pass\n"})

    def test_done_stories_need_tests_unless_adopted(self):
        self.assertError({"tests/test_pay.txt": "test_us_pay_01_ac1 pass\n"}, "done, but no tagged test for AC2")
        adopted = {US1: ticket("US-PAY-01", status="done", reqs=("PAY-R01", "PAY-R04"), extra="adopted: true\n"),
                   "tests/test_pay.txt": "test_us_pay_01_ac1 pass\n"}
        self.assertClean(adopted)
        p = self.project(adopted)
        code, out = p.run("backlog_check.py", "--test-debt")
        self.assertEqual(code, 0, out)
        self.assertIn("DEBT  US-PAY-01/AC2: adopted behavior with no tagged test", out)
        self.assertNotIn("AC1", out)

    def test_in_progress_stories_without_tests_warn(self):
        self.assertWarn({US5: ticket("US-PAY-05", status="in-progress"), "tests/t5.txt": "us_pay_05_ac1 fail\n"},
                        "no tagged test yet for AC2")

    def test_todos_name_tickets_in_code_and_tests(self):
        self.assertError({"src/pay.py": "x = 1\n# TODO: later\n"}, "src/pay.py:2: TODO/FIXME/XXX/HACK names no existing ticket")
        self.assertError({"tests/helper.txt": "FIXME US-PAY-77\n"}, "tests/helper.txt:1: TODO")
        self.assertClean({"src/pay.py": "# HACK until TASK-PAY-02 lands\n", "docs/notes.md": "TODO anything\n"})

    def test_dec_mentions(self):
        self.assertError({"src/pay.py": "# Fails closed until DEC-PAY-04 is decided.\n"}, "`DEC-PAY-04` does not exist")
        self.assertWarn({DEC1: ticket("DEC-PAY-01", type="decision", assignee="human", status="done"),
                         "src/pay.py": "# Seam for DEC-PAY-01.\n"}, "DEC-PAY-01 is decided; revisit this seam")

    def test_no_trace_files_are_data_not_trace(self):
        """A file marked `test-kitchen: no-trace` holds example tickets: nothing in it is
        checked, and its tags prove nothing (the done story still needs real tests)."""
        data = "# test-kitchen: no-trace\nus_pay_01_ac9 pass\n# TODO later\nsee DEC-PAY-77\n"
        self.assertClean({"tests/test_tool.txt": data})
        self.assertError({"tests/test_pay.txt": "nothing\n",
                          "tests/test_tool.txt": "// test-kitchen: no-trace\ntest_us_pay_01_ac1 [US-PAY-01/AC2]\n"},
                         "done, but no tagged test for AC1, AC2")
        # Only the first lines count, so the marker can't hide in the middle of a file.
        late = "\n" * 12 + "# test-kitchen: no-trace\n# TODO later\n"
        self.assertError({"tests/test_tool.txt": late}, "TODO/FIXME/XXX/HACK names no existing ticket")

    def test_ignore_excludes_files_from_every_scan(self):
        kitchen = kitchen_yml(ignore=["src/vendor/**", "backlog/archive/**"])
        self.assertClean({"src/vendor/lib.py": "# TODO whatever\n", "backlog/archive/old.md": "no frontmatter\n"},
                         kitchen=kitchen)


class FrameworkFilesTest(Base):
    def test_framework_files_listed_in_kitchen_lock_are_not_scanned(self):
        """Globs that cover the installed scripts must not report the framework's own TODO/DEC examples."""
        # A stand-in framework file with an unowned TODO (the real scripts carry the
        # no-trace marker, so they would pass either way).
        kitchen = kitchen_yml().replace('code: ["src/**"]', 'code: ["**/*.py"]')
        tool = {"scripts/tool.py": "# TODO later\n"}
        code, out = self.check(tool, kitchen=kitchen)
        self.assertEqual(code, 1, out)
        self.assertIn("ERROR scripts/tool.py", out)
        lock = json.dumps({"version": "0.1.0", "files": {"scripts/tool.py": "0"}})
        self.assertClean(dict(tool, **{"kitchen.lock": lock}), kitchen=kitchen)


class SelfContainedTest(Base):
    def test_repository_links_and_names_only_when_tickets_must_be_self_contained(self):
        files = {US5: ticket("US-PAY-05", body_extra="\n- See [the rules](../README.md) and docs/product.md.")}
        out = self.assertError(files, "links to a repository file", kitchen=kitchen_yml(self_contained_tickets=True))
        self.assertIn("names a repository path or document", out)
        self.assertClean(files)
        self.assertClean({US5: ticket("US-PAY-05", body_extra="\n- See [the spec](https://example.com/spec).")},
                         kitchen=kitchen_yml(self_contained_tickets=True))


class CoverageTest(Base):
    def test_uncovered_requirements_warn_and_strict_makes_them_errors(self):
        files = {TASK2: ticket("TASK-PAY-02", type="task", reqs=())}
        self.assertWarn(files, "PAY-R02: not cited by any story or task")
        self.assertError(files, "PAY-R02: not cited by any story or task", "--strict")

    def test_superseded_and_deferred(self):
        # PAY-R03 is superseded in the baseline and never reported.
        self.assertNotIn("PAY-R03", self.assertClean())
        # A deferred ticket covers nothing.
        self.assertWarn({TASK2: ticket("TASK-PAY-02", type="task", reqs=("PAY-R02",), status="deferred")},
                        "PAY-R02: not cited")
        # A deferred epic's requirements are excluded.
        self.assertClean({"docs/requirements/BILL-billing.md": "- BILL-R01: Invoices.\n",
                          "backlog/BILL-billing/epic.md": EPIC.format(extra="").replace("EP-PAY", "EP-BILL")
                          .replace("status: ready", "status: deferred")})


class CrBodyTest(Base):
    GOOD = ("## Ticket\n\nUS-PAY-01\n\n## Gaps found\n\n- Limits per region: DEC-PAY-01.\n\n"
            "## Decisions\n\n- Kept refunds manual. Log: Refunds stay manual.\n\n## Platform changes\n\n- None\n")
    FILES = {DEC1: ticket("DEC-PAY-01", type="decision", assignee="human", status="draft")}

    def body_check(self, body, files=None):
        p = self.project(dict(self.FILES, **(files or {})))
        (p.tmp / "body.md").write_text(body, encoding="utf-8")
        return p.run("backlog_check.py", f"--pr-body={p.tmp / 'body.md'}")

    def test_a_complete_description_passes(self):
        code, out = self.body_check(self.GOOD)
        self.assertEqual(code, 0, out)
        code, out = self.body_check("## Gaps found\n\n- None\n\n## Decisions\n\n- None. Nothing decided.\n\n"
                                    "## Platform changes\n\n<!-- hint: - x -->\n- None\n")
        self.assertEqual(code, 0, out)

    def test_each_problem(self):
        cases = [
            (self.GOOD.replace("## Platform changes\n\n- None\n", ""), 'missing "## Platform changes" section'),
            (self.GOOD.replace("- None\n", ""), '"Platform changes" needs at least one bullet'),
            (self.GOOD.replace("DEC-PAY-01", "the region rules"), "needs a ticket ID"),
            (self.GOOD.replace("DEC-PAY-01", "DEC-PAY-09"), "`DEC-PAY-09` does not exist"),
            (self.GOOD.replace("Log: Refunds stay manual", "Log: Something else"), 'no decision-log entry titled "Something else"'),
            (self.GOOD.replace(" Log: Refunds stay manual.", ""), 'needs "Log: <entry title>" or a done DEC'),
            (self.GOOD.replace(" Log: Refunds stay manual.", " See DEC-PAY-01."), 'needs "Log: <entry title>" or a done DEC'),
        ]
        for body, text in cases:
            with self.subTest(text=text):
                code, out = self.body_check(body)
                self.assertEqual(code, 1, out)
                self.assertIn(text, out)

    def test_a_done_dec_stands_in_for_a_log_entry(self):
        done = {DEC1: ticket("DEC-PAY-01", type="decision", assignee="human", status="done")}
        code, out = self.body_check(self.GOOD.replace(" Log: Refunds stay manual.", " Decided in DEC-PAY-01."), done)
        self.assertEqual(code, 0, out)

    def test_a_delivery_record_file_is_checked_after_its_marker(self):
        for marker in ("<!-- change-request-description -->", "<!-- pr-description -->"):
            with self.subTest(marker=marker):
                record = f"# Delivery record: US-PAY-01\r\n\r\n- Branch: `x`\r\n\r\n{marker}\r\n\r\n" + self.GOOD.replace("\n", "\r\n")
                code, out = self.body_check(record)
                self.assertEqual(code, 0, out)
                code, out = self.body_check(record.replace("Log: Refunds", "Log: Nope"))
                self.assertEqual(code, 1, out)


class ModesTest(Base):
    def test_gaps(self):
        files = {
            "backlog/PAY-payments/epic.md": EPIC.format(extra='code: ["src/pay/**"]\n'),
            DEC1: ticket("DEC-PAY-01", type="decision", assignee="human", status="ready", title="Limit source"),
            f"{EPIC_DIR}/DEC-PAY-02-parked.md": ticket("DEC-PAY-02", type="decision", assignee="human", status="deferred"),
            f"{EPIC_DIR}/SPK-PAY-01-probe.md": ticket("SPK-PAY-01", type="spike", status="draft", reqs=()),
            US5: ticket("US-PAY-05", status="draft", owner="TBD", reqs=(), questions=["Who approves refunds?"]),
            f"{EPIC_DIR}/US-PAY-06-ready.md": ticket("US-PAY-06", reqs=("PAY-R01",)),
            TASK2: ticket("TASK-PAY-02", type="task", reqs=()),
            "docs/requirements/PAY-more.md": "- PAY-R09: (observed in code) Refunds round down.\n",
            "src/pay/ok.py": "# claimed\n",
            "src/other.py": "# not claimed\n",
        }
        p = self.project(files)
        code, out = p.run("backlog_check.py", "--gaps")
        self.assertEqual(code, 1, out)
        for line in ("GAP   DEC-PAY-01: open decision: Limit source", "GAP   SPK-PAY-01: open spike",
                     "GAP   US-PAY-05: draft story", "GAP   US-PAY-05: unanswered open question: Who approves refunds?",
                     "GAP   US-PAY-06: ready but not refined", "GAP   TASK-PAY-02: ready but not refined",
                     "GAP   PAY-R02: not cited by any story or task",
                     "GAP   PAY-R09: observed in code, not yet confirmed by a person",
                     "GAP   src/other.py: code that no epic's `code:` globs claim"):
            self.assertIn(line, out)
        self.assertNotIn("DEC-PAY-02", out)  # deferred: parked on purpose, not open
        self.assertNotIn("src/pay/ok.py", out)
        self.assertNotIn("SPK-PAY-01: draft", out)  # listed once, as open

    def test_an_empty_project_is_not_fully_defined(self):
        """An installed but undefined project must not pass --gaps by having nothing to check."""
        # The shipped skeleton, so a template edit that adds real text to it fails here.
        skeleton = (Path(__file__).resolve().parent.parent / "template/docs/product.md").read_text(encoding="utf-8")
        files = {"docs/product.md": skeleton, "docs/requirements/PAY-payments.md": None,
                 "backlog/PAY-payments/epic.md": None, US1: None, TASK2: None, "tests/test_pay.txt": None,
                 "src/pay.py": "x = 1\n"}
        p = self.project(files)
        code, out = p.run("backlog_check.py", "--gaps")
        self.assertEqual(code, 1, out)
        for line in ("GAP   docs/product.md: only headings and comments: describe the product",
                     "GAP   docs/requirements: no requirements defined",
                     "GAP   code: 1 code file(s), but no epic claims code with `code:` globs"):
            self.assertIn(line, out)
        code, out = self.project({"docs/product.md": None}).run("backlog_check.py", "--gaps")
        self.assertIn("GAP   docs/product.md: missing: describe the product", out)

    def test_no_gaps_exits_zero(self):
        code, out = self.project().run("backlog_check.py", "--gaps")
        self.assertEqual(code, 0, out)
        self.assertEqual(out.strip(), "")

    def test_refine(self):
        long = ticket("US-PAY-05", reqs=("PAY-R03",), criteria=[f"Given {i}, when x, then y." for i in range(1, 9)],
                      questions=["Limit source: DEC-PAY-01."], extra="release: v1\n")
        files = {
            DEC1: ticket("DEC-PAY-01", type="decision", assignee="human", status="done"),
            US5: long,
            f"{EPIC_DIR}/US-PAY-06-x.md": ticket("US-PAY-06", status="in-progress", extra="release: v1\n"),
            f"{EPIC_DIR}/US-PAY-07-x.md": ticket("US-PAY-07", status="draft", owner="TBD"),
            f"{EPIC_DIR}/US-PAY-08-hot.md": ticket("US-PAY-08", status="done", extra="hotfix: true\nrelease: v1\n"),
            "tests/hot.txt": "us_pay_08_ac1 pass\nus_pay_08_ac2 pass\nus_pay_06_ac1 fail\n",
            US1: ticket("US-PAY-01", status="done", reqs=("PAY-R01", "PAY-R04"), extra="release: v1\n"),
            TASK2: ticket("TASK-PAY-02", type="task", reqs=("PAY-R02",), extra="release: v1\n"),
        }
        p = self.project(files, git=True, origin=True, kitchen=kitchen_yml(releases=["v1", "later"], split_threshold=6))
        code, out = p.run("backlog_check.py", "--refine")
        self.assertEqual(code, 0, out)
        for line in ("REFINE US-PAY-05: 8 live criteria, more than split_threshold 6",
                     "REFINE US-PAY-05: cites PAY-R03, superseded by PAY-R04",
                     "REFINE US-PAY-05: open question names DEC-PAY-01, which is done",
                     "REFINE US-PAY-07: no release slice",
                     "REFINE US-PAY-08: hotfix done",
                     "REFINE US-PAY-06: in-progress, but branch `us-pay-06-x` is not on origin"):
            self.assertIn(line, out)
        p.git("push", "-q", "origin", "HEAD:refs/heads/us-pay-06-x")
        code, out = p.run("backlog_check.py", "--refine")
        self.assertNotIn("US-PAY-06", out)

    def test_modes_do_not_combine(self):
        for args in (["--gaps", "--refine"], ["--gaps", "--strict"], ["--bogus"]):
            with self.subTest(args=args):
                code, out = self.check(None, *args)
                self.assertEqual(code, 2, out)

    def test_self_test(self):
        code, out = self.project().run("backlog_check.py", "--self-test")
        self.assertEqual(code, 0, out)
        self.assertIn("PASS self-test", out)


if __name__ == "__main__":
    unittest.main()
