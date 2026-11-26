"""US-DEF-30: the summary line counts uncovered requirements (DEF-R40).

The summary must match the lines printed under it: an uncovered requirement is an ERROR
line with `--strict` and a WARN line without it, so it is counted the same way. Exit
codes do not change. Each test builds a throwaway project from the clean baseline of
`tests/test_backlog_check.py`, adds one requirement no ticket cites, and runs
`scripts/backlog_check.py`. This file carries no no-trace marker, so its test names are
real tags of US-DEF-30.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_backlog_check import Base  # noqa: E402

UNCOVERED = {"docs/requirements/PAY-more.md": "- PAY-R09: Refunds are logged.\n"}


def summary(out):
    return next(line for line in out.splitlines() if line.startswith("backlog:"))


def labelled(out, label):
    return [line for line in out.splitlines() if line.startswith(label)]


class SummaryTest(Base):
    def test_us_def_30_ac1_strict_counts_the_uncovered_requirement_as_an_error(self):
        code, out = self.check(UNCOVERED, "--strict")
        self.assertTrue(summary(out).endswith("; 1 error(s), 0 warning(s)"), out)
        self.assertEqual(labelled(out, "ERROR"), ["ERROR PAY-R09: not cited by any story or task"], out)
        self.assertEqual(code, 1, out)

    def test_us_def_30_ac1_strict_counts_it_together_with_other_errors(self):
        broken = dict(UNCOVERED, **{"src/pay.py": "x = 1\n# TODO: later\n"})
        code, out = self.check(broken, "--strict")
        self.assertTrue(summary(out).endswith("; 2 error(s), 0 warning(s)"), out)
        self.assertEqual(len(labelled(out, "ERROR")), 2, out)

    def test_us_def_30_ac1_a_clean_project_counts_nothing(self):
        """Limit: with nothing uncovered the counts stay at zero."""
        code, out = self.check({}, "--strict")
        self.assertTrue(summary(out).endswith("; 0 error(s), 0 warning(s)"), out)
        self.assertEqual(code, 0, out)

    def test_us_def_30_ac2_without_strict_it_counts_as_a_warning(self):
        code, out = self.check(UNCOVERED)
        self.assertTrue(summary(out).endswith("; 0 error(s), 1 warning(s)"), out)
        self.assertEqual(labelled(out, "WARN"), ["WARN  PAY-R09: not cited by any story or task"], out)
        self.assertEqual(code, 0, out)


if __name__ == "__main__":
    unittest.main()
