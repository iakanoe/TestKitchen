# test-kitchen: no-trace (the tickets, tags, and TODOs in this file are test data)
"""Proves Test Kitchen is stack-agnostic: the same story goes through every gate in a
Python project (pytest, identifier tags) and a Node project (node:test, bracket tags).

Each test copies a fixture from tests/fixtures/, installs Test Kitchen with init.py
(non-interactive, manual host, so no CLI or network is needed), defines one
requirement file, one epic and one story, and then walks the delivery steps the way
an agent would: claim, failing tagged tests, `gate red`, freeze commit, implement,
`check`, review lines, `record`, `gate pr`. It also checks that `gate pr` refuses a
code change made after the reviewed commit, and that release notes list the story.

A stack whose runner is missing is skipped with the reason (pytest importable from
this interpreter; node 20 or later for its JUnit reporter). No network.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from importlib.util import find_spec
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures"
BRANCH = "us-calc-01-add-and-divide"
STORY = "backlog/CALC-core/US-CALC-01-add-and-divide.md"


def node_major():
    """Major version of `node` on PATH, or 0 when it is missing."""
    node = shutil.which("node")
    if not node:
        return 0
    out = subprocess.run([node, "--version"], capture_output=True, text=True).stdout.strip()
    try:
        return int(out.lstrip("v").split(".")[0])
    except ValueError:
        return 0


REQUIREMENTS = """\
# CALC: core arithmetic

- CALC-R01: The calculator adds two integers.
- CALC-R02: Dividing by zero is refused with a clear error.
"""

EPIC = """\
---
id: EP-CALC
type: epic
title: Core arithmetic
owner: Tester
assignee_type: either
status: ready
code: ["{code}"]
---

The basic operations of the calculator.

## Boundaries

No floating-point formatting.

## Open

None.
"""

STORY_TEXT = """\
---
id: US-CALC-01
type: story
title: Add and divide
epic: EP-CALC
source_reqs: [CALC-R01, CALC-R02]
blocked_by: []
owner: Tester
assignee_type: either
status: ready
refined: 2026-11-24
---

As a user, I want to add and divide numbers, so that I can do quick sums.

## Acceptance criteria

- AC1: Given two integers, when I add them, then I get their sum.
- AC2: Given a divisor of zero, when I divide, then I get an error saying division by zero is refused.

## Notes

None.

## Open questions

- None. Both behaviors are fixed by CALC-R01 and CALC-R02.
"""

BODY = """\
## Ticket

US-CALC-01 Add and divide (requirements CALC-R01, CALC-R02). Status: `done`.

## Plan

| Criterion | Tests |
| --- | --- |
| US-CALC-01/AC1 | adds two integers |
| US-CALC-01/AC2 | refuses division by zero |

Constrained by: none.

## Gaps found

- None

## Decisions

- None

## Platform changes

- None

## Test changes

None

## Review report

No findings.

Reviewed commit: {sha}
CRITICAL: 0, WARNING: 0, SUGGESTION: 0

## Checks

deliver.py check passed.
"""

PYTHON = {
    "fixture": "python",
    "tests": "tests/**",
    "code": "calc/**",
    # sys.executable, so the runner is the interpreter that has pytest.
    "test_command": f"{sys.executable} -m pytest {{files}} --junitxml={{report}}",
    "test_file": "tests/test_calc.py",
    # Identifier tags: pytest reports function names, which cannot hold brackets.
    # `import calc` (not `from calc import add`) so a missing function fails each
    # test on its own instead of failing collection, which would hide the tags.
    "tests_text": """\
        import pytest
        import calc


        def test_us_calc_01_ac1_adds_two_integers():
            assert calc.add(2, 3) == 5


        def test_us_calc_01_ac2_refuses_division_by_zero():
            with pytest.raises(ValueError, match="division by zero"):
                calc.divide(1, 0)
        """,
    "code_file": "calc/__init__.py",
    "code_text": """\
        \"\"\"Core arithmetic (US-CALC-01).\"\"\"


        def add(a, b):
            \"\"\"US-CALC-01/AC1: the sum of two integers.\"\"\"
            return a + b


        def divide(a, b):
            \"\"\"US-CALC-01/AC2: refuse a zero divisor.\"\"\"
            if b == 0:
                raise ValueError("division by zero is refused")
            return a / b
        """,
}

NODE = {
    "fixture": "node",
    "tests": "src/**/*.test.js",
    "code": "src/**",
    "test_command": "node --test --test-reporter=junit --test-reporter-destination={report} {files}",
    "test_file": "src/calc.test.js",
    "tests_text": """\
        import { test } from 'node:test';
        import assert from 'node:assert/strict';
        import * as calc from './calc.js';

        test('[US-CALC-01/AC1] adds two integers', () => {
          assert.equal(calc.add(2, 3), 5);
        });

        test('[US-CALC-01/AC2] refuses division by zero', () => {
          assert.throws(() => calc.divide(1, 0), RangeError);
        });
        """,
    "code_file": "src/calc.js",
    "code_text": """\
        // Core arithmetic (US-CALC-01).

        // US-CALC-01/AC1: the sum of two integers.
        export function add(a, b) {
          return a + b;
        }

        // US-CALC-01/AC2: refuse a zero divisor instead of returning Infinity.
        export function divide(a, b) {
          if (b === 0) throw new RangeError('division by zero is refused');
          return a / b;
        }
        """,
}


class StoryFlow:
    """One fixture project in a temp folder, with a bare local origin."""

    def __init__(self, stack, tmp):
        self.stack = stack
        self.dir = Path(tmp) / "project"
        self.origin = Path(tmp) / "origin.git"
        shutil.copytree(FIXTURES / stack["fixture"], self.dir)
        # Isolate git from the machine's config (signing, hooks, default branch).
        self.env = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
                        GIT_AUTHOR_NAME="Tester", GIT_AUTHOR_EMAIL="t@example.com",
                        GIT_COMMITTER_NAME="Tester", GIT_COMMITTER_EMAIL="t@example.com",
                        PYTHONDONTWRITEBYTECODE="1")

    def run(self, *cmd, ok=True):
        r = subprocess.run(cmd, cwd=self.dir, env=self.env, capture_output=True, text=True)
        if ok and r.returncode:
            raise AssertionError(f"{' '.join(cmd)} exited {r.returncode}\n{r.stdout}\n{r.stderr}")
        return r

    def git(self, *args):
        return self.run("git", *args).stdout.strip()

    def script(self, name, *args, ok=True):
        return self.run(sys.executable, f"scripts/{name}", *args, ok=ok)

    def write(self, rel, text):
        path = self.dir / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(text), encoding="utf-8")

    def set_status(self, status):
        path = self.dir / STORY
        text = path.read_text(encoding="utf-8")
        path.write_text("\n".join(f"status: {status}" if line.startswith("status: ") else line
                                  for line in text.splitlines()) + "\n", encoding="utf-8")

    def install_and_define(self):
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Tester")  # `next` compares owners with it
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "fixture")
        self.run("git", "init", "-q", "--bare", str(self.origin))
        self.git("remote", "add", "origin", str(self.origin))
        s = self.stack
        self.run(sys.executable, str(ROOT / "init.py"), "--yes", "--host", "manual",
                 "--tests", s["tests"], "--code", s["code"], "--test-command", s["test_command"])
        self.write("docs/requirements/CALC-core.md", REQUIREMENTS)
        self.write("backlog/CALC-core/epic.md", EPIC.format(code=s["code"]))
        self.write(STORY, STORY_TEXT)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "chore: install Test Kitchen, define CALC")
        self.git("push", "-q", "-u", "origin", "main")


@unittest.skipUnless(find_spec("pytest"), "pytest is not importable from this interpreter")
class PythonStack(unittest.TestCase):
    stack = PYTHON

    def test_story_goes_through_every_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = StoryFlow(self.stack, tmp)
            p.install_and_define()
            self.assertEqual(p.script("backlog_check.py").returncode, 0)
            self.assertIn("NEXT US-CALC-01", p.script("deliver.py", "next").stdout)

            # Claim, then the failing tagged tests: gate red must pass before the freeze.
            p.git("checkout", "-q", "-b", BRANCH)
            p.set_status("in-progress")
            p.git("commit", "-qam", "chore: claim US-CALC-01")
            p.write(self.stack["test_file"], self.stack["tests_text"])
            red = p.script("deliver.py", "gate", "red", "US-CALC-01")
            self.assertIn("PASS red", red.stdout)
            p.git("add", "-A")
            p.git("commit", "-qm", "test: US-CALC-01 failing tests")

            # Implement and check.
            p.write(self.stack["code_file"], self.stack["code_text"])
            p.git("commit", "-qam", "feat: US-CALC-01 add and divide")
            self.assertIn("PASS check", p.script("deliver.py", "check").stdout)

            # Review, done, record, gate pr.
            body = Path(tmp) / "body.md"
            body.write_text(BODY.format(sha=p.git("rev-parse", "HEAD")), encoding="utf-8")
            p.set_status("done")
            p.script("deliver.py", "record", f"--body-file={body}", f"--branch={BRANCH}")
            p.git("add", "-A")
            p.git("commit", "-qm", "docs: US-CALC-01 done, delivery record")
            gate = ["gate", "pr", f"--body-file={body}", f"--branch={BRANCH}", "--base=origin/main"]
            self.assertIn("PASS pr: US-CALC-01", p.script("deliver.py", *gate).stdout)

            # A code change after the reviewed commit needs another review.
            with open(p.dir / self.stack["code_file"], "a", encoding="utf-8") as f:
                f.write("\n")
            p.git("commit", "-qam", "fix: late change")
            late = p.script("deliver.py", *gate, ok=False)
            self.assertEqual(late.returncode, 1)
            self.assertIn("after the reviewed commit", late.stdout)
            p.git("reset", "-q", "--hard", "HEAD~1")

            # A person merges (manual host); release notes then list the story.
            p.git("checkout", "-q", "main")
            p.git("merge", "-q", "--no-ff", BRANCH, "-m", "Merge US-CALC-01")
            notes = p.script("deliver.py", "release-notes").stdout
            self.assertIn("I can do quick sums. (US-CALC-01)", notes)
            self.assertIn("NEXT none", p.script("deliver.py", "next").stdout)


@unittest.skipUnless(node_major() >= 20, "node 20 or later is not on PATH")
class NodeStack(PythonStack):
    stack = NODE


# PythonStack's skip condition must not carry over to NodeStack: unittest stores the
# skip on the class, so NodeStack needs its own when pytest is missing but node is not.
NodeStack.__unittest_skip__ = node_major() < 20
NodeStack.__unittest_skip_why__ = "node 20 or later is not on PATH"

if __name__ == "__main__":
    unittest.main()
