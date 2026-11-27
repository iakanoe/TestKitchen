"""US-DEF-35: `backlog_check.py` checks DECs for evaluated options and a matching outcome (DEF-R51).

An open DEC (any status but `done` or `deferred`) gives every option under `## Options`
a `For:` line and an `Against:` line and has no `## Outcome`; a `done` or `deferred` DEC
has an `## Outcome`.

Each test builds a throwaway project from the baseline of `tests/test_backlog_check.py`
and runs `scripts/backlog_check.py` as a subprocess. This file carries no no-trace
marker, so its test names are real tags of US-DEF-35. The fixture DEC's ID is joined
from parts (see `DEC_ID`), so this repository's own trace scan never reads it as a
mention of a DEC that does not exist here.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers.kitchen_project import ticket  # noqa: E402
from test_backlog_check import DEC1, Base  # noqa: E402

DEC_ID = "DEC" + "-PAY-01"
OPEN = ("draft", "ready", "in-progress")
DECIDED = ("done", "deferred")

# Two evaluated options, in the README's sub-bullet form.
EVALUATED = ("- (a) Keep the limit.\n  - For: simple.\n  - Against: rigid.\n"
             "- (b) Drop the limit.\n  - For: lighter.\n  - Against: risky.\n")
# The same, as plain lines after "None recorded. Proposals:".
PLAIN = ("None recorded. Proposals:\n\n- (a) Keep the limit.\nFor: simple.\nAgainst: rigid.\n"
         "- (b) Drop the limit.\n    For: lighter.\n    Against: risky.\n")
# Options with no For or Against lines at all.
BARE = "- (a) Keep the limit.\n- (b) Drop the limit.\n"


def dec(status="draft", options=None, outcome=None, recommendation=None, context=None):
    """A DEC file's text: `options` replaces the body of `## Options`, `outcome` is appended
    as written (a heading and text), `recommendation` and `context` replace those sections."""
    text = ticket(DEC_ID, type="decision", assignee="human", status=status)
    if options is not None:
        text = text.replace("## Options\n\nNone recorded.\n", "## Options\n\n" + options)
    if recommendation is not None:
        text = text.replace("## Recommendation\n\nNone.\n", "## Recommendation\n\n" + recommendation)
    if context is not None:
        text = text.replace("## Context\n\nNone.\n", "## Context\n\n" + context)
    if outcome is not None:
        text += "\n" + outcome
    return text


OUTCOME = "## Outcome\n\n2026-01-01: (a), decided by the team, logged.\n"


class DecFormatTest(Base):
    def errors(self, text):
        """The ERROR lines `backlog_check.py` prints for a project holding this DEC."""
        code, out = self.check({DEC1: text})
        return code, [line for line in out.splitlines() if line.startswith("ERROR")], out

    def assertNoDecErrors(self, text):
        code, errors, out = self.errors(text)
        self.assertEqual(code, 0, out)
        self.assertEqual(errors, [], out)

    def assertDecError(self, text, *parts):
        """Exit 1 and one ERROR line naming the DEC and containing every part."""
        code, errors, out = self.errors(text)
        self.assertEqual(code, 1, out)
        self.assertTrue(any(DEC_ID in e and all(p in e for p in parts) for e in errors), out)
        return errors

    # --- AC1: an open DEC's option needs a For: line and an Against: line -------------------

    def test_us_def_35_ac1_an_option_missing_for_or_against_is_reported(self):
        """AC1: an option with only For, only Against, or neither is an error naming the DEC and its letter."""
        cases = {
            "only For": ("- (a) Keep the limit.\n  - For: simple.\n", "Against:"),
            "only Against": ("- (a) Keep the limit.\n  - Against: rigid.\n", "For:"),
            "neither": ("- (a) Keep the limit.\n", "For:"),
        }
        for status in OPEN:
            for name, (options, missing) in cases.items():
                with self.subTest(status=status, case=name):
                    self.assertDecError(dec(status, options), "option (a)", missing)

    def test_us_def_35_ac1_each_option_ends_at_the_next_option_or_the_end_of_options(self):
        """AC1: lines count only up to the next option or the end of `## Options`."""
        # A middle option with no lines is reported even though the next option has them.
        errors = self.assertDecError(dec(options="- (a) Keep.\n- (b) Drop.\n  - For: x.\n  - Against: y.\n"),
                                     "option (a)")
        self.assertFalse(any("option (b)" in e for e in errors), errors)
        # A For line under a later option does not count for an earlier one.
        self.assertDecError(dec(options="- (a) Keep.\n  - Against: y.\n- (b) Drop.\n  - For: x.\n  - Against: z.\n"),
                            "option (a)", "For:")
        # The last option's lines under the next heading do not count.
        self.assertDecError(dec(options="- (a) Keep.\n", recommendation="- For: x.\n- Against: y.\nFor: x.\nAgainst: y.\n"),
                            "option (a)")

    def test_us_def_35_ac1_evaluated_options_pass_in_either_form(self):
        """AC1: indented `- For:`/`- Against:` sub-bullets and plain lines both count; proposals are checked too."""
        for status in OPEN:
            with self.subTest(status=status):
                self.assertNoDecErrors(dec(status, EVALUATED))
                self.assertNoDecErrors(dec(status, PLAIN))
        self.assertDecError(dec(options="None recorded. Proposals:\n\n- (a) Keep the limit.\n  - For: simple.\n"),
                            "option (a)", "Against:")

    def test_us_def_35_ac1_an_indented_letter_bullet_is_not_an_option(self):
        """AC1: an option is an unindented bullet; an indented `- (a)` is not checked."""
        self.assertNoDecErrors(dec(options=EVALUATED + "  - (c) A note, not an option.\n"))
        self.assertDecError(dec(options=EVALUATED + "- (c) A real option.\n"), "option (c)")

    def test_us_def_35_ac1_the_marker_is_one_lowercase_letter(self):
        """AC1: `- (A)`, `- (ab)`, and `- (1)` are not options; `- (z)` is."""
        for marker in ("(A)", "(ab)", "(1)"):
            with self.subTest(marker=marker):
                self.assertNoDecErrors(dec(options=EVALUATED + f"- {marker} Not an option.\n"))
        self.assertDecError(dec(options=EVALUATED + "- (z) A real option.\n"), "option (z)")

    def test_us_def_35_ac1_the_line_must_start_with_for_or_against(self):
        """AC1: `For:` or `Against:` later in a line does not count; only at its start, after indentation and `- `."""
        self.assertDecError(dec(options="- (a) Keep.\n  - Note: For: x.\n  - See: Against: y.\n"), "option (a)")
        self.assertDecError(dec(options="- (a) Keep. For: x. Against: y.\n"), "option (a)")

    # --- AC2: an open DEC has no ## Outcome --------------------------------------------------

    def test_us_def_35_ac2_an_open_decision_with_an_outcome_is_reported(self):
        """AC2: every open status, also with trailing spaces or Windows line endings."""
        for status in OPEN:
            with self.subTest(status=status):
                self.assertDecError(dec(status, EVALUATED, OUTCOME), "an open decision records an outcome")
        self.assertDecError(dec("draft", EVALUATED, OUTCOME.replace("## Outcome\n", "## Outcome   \n")),
                            "an open decision records an outcome")
        self.assertDecError(dec("draft", EVALUATED, OUTCOME).replace("\n", "\r\n"),
                            "an open decision records an outcome")

    def test_us_def_35_ac2_only_the_exact_heading_counts(self):
        """AC2: `### Outcome`, `## Outcomes`, or the word in text are not an outcome section."""
        for outcome in ("### Outcome\n\nNot yet.\n", "## Outcomes\n\nNot yet.\n", "The Outcome is open.\n"):
            with self.subTest(outcome=outcome):
                self.assertNoDecErrors(dec("draft", EVALUATED, outcome))

    # --- AC3: a decided DEC has an ## Outcome ------------------------------------------------

    def test_us_def_35_ac3_a_decided_dec_without_an_outcome_is_reported(self):
        """AC3: `done` and `deferred` without `## Outcome`, or with only a near-miss heading."""
        for status in DECIDED:
            with self.subTest(status=status):
                self.assertDecError(dec(status, EVALUATED), "the decision has no outcome")
        for outcome in ("### Outcome\n\n(a).\n", "## Outcomes\n\n(a).\n"):
            with self.subTest(outcome=outcome):
                self.assertDecError(dec("done", EVALUATED, outcome), "the decision has no outcome")

    def test_us_def_35_ac3_a_decided_dec_with_an_outcome_passes(self):
        """AC3: the allowed case."""
        for status in DECIDED:
            with self.subTest(status=status):
                self.assertNoDecErrors(dec(status, EVALUATED, OUTCOME))

    # --- AC4: decided DECs' options are not checked ------------------------------------------

    def test_us_def_35_ac4_decided_decs_options_need_no_for_or_against(self):
        """AC4: bare options on a done or deferred DEC are fine; the same on a draft DEC are not."""
        for status in DECIDED:
            with self.subTest(status=status):
                self.assertNoDecErrors(dec(status, BARE, OUTCOME))
        self.assertDecError(dec("draft", BARE), "option (a)")

    # --- AC5: no option bullet, or letter bullets outside ## Options -------------------------

    def test_us_def_35_ac5_no_options_or_letter_bullets_elsewhere_are_not_reported(self):
        """AC5: `None recorded.` alone, and `- (x)` bullets under other sections, pass."""
        self.assertNoDecErrors(dec("draft"))
        self.assertNoDecErrors(dec("draft", recommendation=BARE))
        self.assertNoDecErrors(dec("ready", context=BARE))
        # Contrast: the same bullets under ## Options are options.
        self.assertDecError(dec("draft", BARE), "option (a)")


if __name__ == "__main__":
    unittest.main()
