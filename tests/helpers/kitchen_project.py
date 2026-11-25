"""Throwaway Test Kitchen projects for the script tests.

A `Project` is a temporary folder holding a copy of the scripts under test (installed at
`scripts/`, the way init installs them), a `kitchen.yml`, fixture requirements, decision
log, and tickets, optionally a git repository with a bare local `origin`. Scripts run as
subprocesses from inside it, so they find their root exactly as they do in a real project.

The scripts under test come from `template/scripts/`, or from the folder named by the
KITCHEN_SCRIPTS environment variable (to test another copy, such as an installed one).

Git runs with the person's global and system configuration turned off (no signing, hooks,
or aliases leak in) and a fixed author. Fake `gh` and `glab` executables (tests/fakes) can
be put first on PATH; nothing here touches the network.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = Path(os.environ.get("KITCHEN_SCRIPTS") or ROOT / "template" / "scripts")
FAKES = ROOT / "tests" / "fakes"
RUNNER = Path(__file__).resolve().parent / "junit_runner.py"
SCRIPT_NAMES = ("kitchen_lib.py", "hosts.py", "backlog_check.py", "deliver.py")

GIT_ENV = {
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_AUTHOR_NAME": "Test Owner",
    "GIT_AUTHOR_EMAIL": "owner@example.invalid",
    "GIT_COMMITTER_NAME": "Test Owner",
    "GIT_COMMITTER_EMAIL": "owner@example.invalid",
    "GIT_TERMINAL_PROMPT": "0",
}


def runner_command():
    """A test_command that runs the fake JUnit runner (a JSON string is valid YAML)."""
    return json.dumps(f'"{sys.executable}" "{RUNNER}" {{report}} {{files}}')


def kitchen_yml(**extra):
    """A kitchen.yml with the fake runner; extra keys are appended as YAML."""
    lines = ['tests: ["tests/**"]', 'code: ["src/**"]', f"test_command: {runner_command()}", "host: manual"]
    for k, v in extra.items():
        if k == "host":
            lines = [x for x in lines if not x.startswith("host:")]
        lines.append(f"{k}: {json.dumps(v)}")
    return "\n".join(lines) + "\n"


REQUIREMENTS = """# Payments requirements

Free text is allowed here.

- PAY-R01: Refunds never exceed the order total.
- PAY-R02: Refunds are logged.
- PAY-R03: (superseded 2026-01-02 by PAY-R04) Refunds are emailed.
- PAY-R04: Refund receipts are shown on screen.
"""

DECISION_LOG = """# Decision log

### 2026-01-03 — Use the hotfix lane for the refund outage

Decided by the owner.

### 2026-01-01 — Refunds stay manual

Decided by the owner.
"""

# A product description with real content, so the baseline project is fully defined.
PRODUCT = """# Product

## Vision

Shop staff take payments and refund them without calling support.
"""

EPIC = """---
id: EP-PAY
type: epic
title: Payments
owner: Team
assignee_type: either
status: ready
{extra}---

Taking and refunding payments.

## Boundaries

- None.

## Open

- None.
"""


def ticket(tid, type="story", title="Fixture ticket", epic="EP-PAY", status="ready", reqs=("PAY-R01",),
           blocked_by=(), owner="Team", assignee="either", extra="", criteria=None, questions=("None. Fixture.",),
           body_extra=""):
    """A ticket file's text. `criteria` defaults to two story criteria (or one task criterion)."""
    if criteria is None:
        criteria = (["Given a fixture, when it is checked, then it passes.",
                     "Given a fixture, when it is checked again, then it still passes."]
                    if type == "story" else ["The fixture is checked."])
    fm = [f"id: {tid}", f"type: {type}", f"title: {title}", f"epic: {epic}",
          f"source_reqs: [{', '.join(reqs)}]", f"blocked_by: [{', '.join(blocked_by)}]",
          f"owner: {owner}", f"assignee_type: {assignee}", f"status: {status}"]
    head = "---\n" + "\n".join(fm) + "\n" + extra + "---\n\n"
    if type in ("story", "task"):
        intro = ("As a clerk, I want the fixture to work, so that refunds are safe.\n\n" if type == "story"
                 else "Technical fixture work.\n\n")
        acs = "\n".join(f"- AC{i}: {c}" for i, c in enumerate(criteria, 1))
        qs = "\n".join(f"- {q}" for q in questions)
        return f"{head}{intro}## Acceptance criteria\n\n{acs}\n\n## Notes\n\n- Fixture.{body_extra}\n\n## Open questions\n\n{qs}\n"
    if type == "decision":
        return f"{head}## Question\n\nWhich?{body_extra}\n\n## Context\n\nNone.\n\n## Options\n\nNone recorded.\n\n## Recommendation\n\nNone.\n\n## Decides\n\nNone.\n"
    return f"{head}## Goal\n\nFind out.{body_extra}\n\n## Context\n\nNone.\n\n## Done when\n\nKnown.\n\n## Findings\n\nNone.\n"


def fake_bin(folder):
    """Create `gh` and `glab` wrappers around tests/fakes/fake_cli.py in `folder`; return the folder."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    for name in ("gh", "glab"):
        p = folder / name
        p.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{FAKES / "fake_cli.py"}" {name} "$@"\n')
        p.chmod(0o755)
    return folder


class Project:
    """A temporary Test Kitchen project. Call `close()` (or use addCleanup) to remove it."""

    def __init__(self, files=None, git=True, origin=True, kitchen=None):
        self.tmp = Path(tempfile.mkdtemp(prefix="kitchen-test-"))
        self.root = self.tmp / "project"
        self.root.mkdir()
        self.bin = fake_bin(self.tmp / "bin")
        self.rules_file = self.tmp / "rules.json"
        self.log_file = self.tmp / "cli.log"
        (self.root / "scripts").mkdir()
        for name in SCRIPT_NAMES:
            shutil.copy(SCRIPTS / name, self.root / "scripts" / name)
        base = {
            "kitchen.yml": kitchen or kitchen_yml(),
            "docs/requirements/PAY-payments.md": REQUIREMENTS,
            "docs/decision-log.md": DECISION_LOG,
            "docs/product.md": PRODUCT,
            "backlog/PAY-payments/epic.md": EPIC.format(extra=""),
        }
        base.update(files or {})
        for rel, text in base.items():
            if text is not None:
                self.write(rel, text, add=False)
        if git:
            self.git("init", "-q")
            self.git("symbolic-ref", "HEAD", "refs/heads/main")
            self.git("add", "-A")
            self.git("commit", "-q", "-m", "chore: fixture project")
            if origin:
                self.origin = self.tmp / "origin.git"
                subprocess.run(["git", "init", "-q", "--bare", str(self.origin)], check=True, env=self.env())
                self.git("remote", "add", "origin", str(self.origin))
                self.git("push", "-q", "origin", "main")
                self.git("fetch", "-q", "origin")

    def close(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def env(self, **extra):
        env = dict(os.environ)
        env.update(GIT_ENV)
        env["PATH"] = str(self.bin) + os.pathsep + env.get("PATH", "")
        env["FAKE_CLI_RULES"] = str(self.rules_file)
        env["FAKE_CLI_LOG"] = str(self.log_file)
        env.pop("KITCHEN_GUARD_SANDBOX", None)
        env.update(extra)
        return env

    def write(self, rel, text, add=True, append=False):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a" if append else "w", encoding="utf-8", newline="") as f:
            f.write(text)
        if add and (self.root / ".git").exists():
            self.git("add", "--", rel)

    def git(self, *args):
        r = subprocess.run(["git", *args], cwd=self.root, env=self.env(), capture_output=True, text=True)
        if r.returncode:
            raise AssertionError(f"git {' '.join(args)} failed: {r.stderr}")
        return r.stdout

    def commit(self, message, allow_empty=False):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message, *(["--allow-empty"] if allow_empty else []))
        return self.git("rev-parse", "HEAD").strip()

    def head(self):
        return self.git("rev-parse", "HEAD").strip()

    def rules(self, rules):
        """Set the fake CLI's answers (see tests/fakes/fake_cli.py)."""
        self.rules_file.write_text(json.dumps(rules), encoding="utf-8")

    def calls(self):
        if not self.log_file.exists():
            return []
        return [json.loads(line) for line in self.log_file.read_text().splitlines()]

    def run(self, script, *args, cwd=None, **env):
        """Run scripts/<script> with args; returns (exit code, stdout + stderr)."""
        r = subprocess.run([sys.executable, str(self.root / "scripts" / script), *args],
                           cwd=cwd or self.root, env=self.env(**env), capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr
