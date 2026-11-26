"""US-DEF-33: `backlog_check.py` reads and checks `replaces:` (DEF-R45).

A ticket that changes done behavior lists the criteria it replaces; once it is done,
each replaced criterion must be crossed out as a `(removed …)` placeholder.

Each test builds a throwaway project from the baseline of `tests/test_backlog_check.py`
and runs `scripts/backlog_check.py` as a subprocess. This file carries no no-trace
marker, so its test names are real tags of US-DEF-33. Fixture ticket references are
joined from parts (see `ref`) and lists use YAML block form, so this repository's own
trace scan never reads them as tags of tickets that do not exist here.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers.kitchen_project import ticket  # noqa: E402
from test_backlog_check import BASELINE, EPIC_DIR, TASK2, US1, US5, Base  # noqa: E402

DONE_STORY = "US-PAY-01"   # done in the baseline, with live criteria AC1 and AC2
READY_TASK = "TASK-PAY-02"  # ready in the baseline
REPLACER = "US-PAY-05"


def ref(tid, n):
    """`<ticket>/AC<n>`, assembled so this file's text holds no criterion reference."""
    return tid + "/" + "AC" + str(n)


def replaces(*entries):
    """A `replaces:` frontmatter block in YAML block-list form."""
    return "replaces:\n" + "".join(f"  - {e}\n" for e in entries)


def tags(tid, *ns):
    """A fixture test file line tagging criteria in the identifier form."""
    stem = tid.lower().replace("-", "_")
    return "".join(f"test_{stem}" + f"_ac{n} pass\n" for n in ns)


def replacer(status="ready", entries=(ref(DONE_STORY, 2),)):
    return ticket(REPLACER, status=status, extra=replaces(*entries))


class ReplacesTest(Base):
    def test_us_def_33_ac1_a_live_criterion_of_a_done_ticket_is_accepted(self):
        """AC1: listing a live criterion of a done ticket is valid, ready or in progress."""
        self.assertClean({US5: replacer("ready")})
        self.assertClean({US5: replacer("in-progress"), "tests/test_replacer.txt": tags(REPLACER, 1, 2)})
        out = self.assertClean({US5: ticket(REPLACER, extra="replaces: []\n")})
        self.assertNotIn("unknown field", out)

    def test_us_def_33_ac2_replaces_must_be_a_list(self):
        """AC2: a value that is not a list is one error, with no errors about entries."""
        out = self.assertError({US5: ticket(REPLACER, extra="replaces: " + ref(DONE_STORY, 2) + "\n")},
                               "`replaces` is a list")
        self.assertEqual(sum(1 for line in out.splitlines() if line.startswith("ERROR")), 1, out)

    def test_us_def_33_ac3_entries_must_name_existing_criteria_of_done_tickets(self):
        """AC3: each malformed, missing, or not-done entry is an error naming the entry."""
        for entry in (DONE_STORY, ref(DONE_STORY, 9), ref("US-PAY-77", 1), ref(READY_TASK, 1)):
            with self.subTest(entry=entry):
                self.assertError({US5: replacer("ready", (entry,))}, f"replaces `{entry}`")

    def test_us_def_33_ac3_a_removed_placeholder_is_not_a_broken_reference(self):
        """AC3: naming a criterion already crossed out is not reported, on a ticket not yet done."""
        crossed = {
            US1: ticket(DONE_STORY, status="done", reqs=("PAY-R01", "PAY-R04"),
                        criteria=["Given a refund, when it is too large, then it is refused.",
                                  f"(removed 2026-11-26, replaced by {REPLACER})"]),
            "tests/test_pay.txt": tags(DONE_STORY, 1),
            US5: replacer("ready"),
        }
        self.assertClean(crossed)

    def test_us_def_33_ac4_a_done_replacer_with_a_live_replaced_criterion_fails(self):
        """AC4: once the replacing ticket is done, a replaced criterion that is still live is an error."""
        files = {US5: replacer("done"), "tests/test_replacer.txt": tags(REPLACER, 1, 2)}
        out = self.assertError(files, ref(DONE_STORY, 2))
        self.assertIn("still live", out)
        # The same entry on a replacing ticket that is not done is no error (AC1).
        self.assertClean({US5: replacer("ready")})
        # Each entry is judged on its own: only the criterion still live is reported.
        mixed = {
            US1: ticket(DONE_STORY, status="done", reqs=("PAY-R01", "PAY-R04"),
                        criteria=["Given a refund, when it is too large, then it is refused.",
                                  f"(removed 2026-11-26, replaced by {REPLACER})"]),
            "tests/test_pay.txt": tags(DONE_STORY, 1),
            US5: replacer("done", (ref(DONE_STORY, 1), ref(DONE_STORY, 2))),
            "tests/test_replacer.txt": tags(REPLACER, 1, 2),
        }
        out = self.assertError(mixed, ref(DONE_STORY, 1))
        self.assertNotIn(ref(DONE_STORY, 2), out)

    def test_us_def_33_ac5_crossed_out_criteria_satisfy_a_done_replacer(self):
        """AC5: a done replacing ticket whose replaced criterion is crossed out is clean."""
        files = {
            US1: ticket(DONE_STORY, status="done", reqs=("PAY-R01", "PAY-R04"),
                        criteria=["Given a refund, when it is too large, then it is refused.",
                                  f"(removed 2026-11-26, replaced by {REPLACER})"]),
            "tests/test_pay.txt": tags(DONE_STORY, 1),
            US5: replacer("done"),
            "tests/test_replacer.txt": tags(REPLACER, 1, 2),
        }
        self.assertClean(files)


# The baseline names a ready task and its epic folder; keep the imports used for readers.
assert TASK2.startswith(EPIC_DIR) and BASELINE

if __name__ == "__main__":
    unittest.main()
