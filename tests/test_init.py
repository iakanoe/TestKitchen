"""Tests for init.py: install, update, and doctor, plus its pure helpers.

Each end-to-end test builds a small fake Test Kitchen checkout (template/,
CHANGELOG.md, and an init.py holding only a VERSION line) in a temp folder and
installs it with --source into a throwaway git repository. So the tests never
depend on the real template's contents (other parts of the product own those)
and never touch the network.

init.py runs as a subprocess, the way people run it, in a new session so it
has no controlling terminal: it can never block on a prompt, which is exactly
the agent/CI situation these tests check. Fake `gh` and `glab` executables on
PATH keep doctor's sign-in check offline. HOME points at a temp folder so the
developer's own git configuration (signing, hooks) cannot interfere.

Run: python3 -m unittest tests.test_init -v
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import site
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
INIT = ROOT / "init.py"
KITCHEN_TMPL = ROOT / "template" / "kitchen.yml.tmpl"


def load_init():
    """init.py imported as a module, for its pure helpers."""
    spec = importlib.util.spec_from_file_location("kitchen_init", str(INIT))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


init = load_init()

GITHUB_CI = """name: Check
on: [pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      # TEST-KITCHEN: toolchain setup
      - name: Toolchain setup (placeholder)
        run: echo "Toolchain setup is not filled in. Replace this step."

      - name: Check
        run: python3 scripts/deliver.py check
"""

GITLAB_CI = """check:
  image: python:3.12
  script:
    # TEST-KITCHEN: toolchain setup
    - echo "Toolchain setup is not filled in. Replace this line."
    - python3 scripts/deliver.py check
"""

# Stands in for every framework script: passes its normal run and its self-test.
FAKE_SCRIPT = '''"""Fake framework script for init.py tests."""
import sys
if "--self-test" in sys.argv:
    print("PASS self-test")
sys.exit(0)
'''

GUARD_SETTINGS = json.dumps({
    "hooks": {"PreToolUse": [{
        "matcher": "Bash|Edit|Write",
        "hooks": [{"type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/guard.py\""}],
    }]}
}, indent=2) + "\n"


def write_tree(base: Path, files: Dict[str, Optional[str]]) -> None:
    for rel, content in files.items():
        path = base / rel
        if content is None:
            if path.exists():
                path.unlink()
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def snapshot(base: Path) -> Dict[str, bytes]:
    """Every file in the work tree (not .git) with its content."""
    out = {}
    for dirpath, dirnames, filenames in os.walk(str(base)):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for name in filenames:
            path = Path(dirpath) / name
            out[path.relative_to(base).as_posix()] = path.read_bytes()
    return out


class InitTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="tk-init-test-")).resolve()
        self.addCleanup(shutil.rmtree, str(self.tmp), True)
        home = self.tmp / "home"
        home.mkdir()
        fakebin = self.tmp / "bin"
        fakebin.mkdir()
        for name in ("gh", "glab"):
            tool = fakebin / name
            tool.write_text("#!/bin/sh\nexit 0\n")
            tool.chmod(0o755)
        self.env = dict(
            os.environ,
            HOME=str(home),
            XDG_CONFIG_HOME=str(home / ".config"),
            # A new HOME would hide packages installed with `pip install --user`
            # (PyYAML among them); keep the real user site visible.
            PYTHONUSERBASE=site.getuserbase(),
            GIT_CONFIG_NOSYSTEM="1",
            GIT_AUTHOR_NAME="Test", GIT_AUTHOR_EMAIL="test@example.invalid",
            GIT_COMMITTER_NAME="Test", GIT_COMMITTER_EMAIL="test@example.invalid",
            PATH=str(fakebin) + os.pathsep + os.environ.get("PATH", ""),
        )

    # -- fixtures ----------------------------------------------------------

    def make_source(self, name: str, version: str, overrides: Optional[Dict[str, Optional[str]]] = None,
                    changelog: Optional[str] = None) -> Path:
        src = self.tmp / name
        files: Dict[str, Optional[str]] = {
            "init.py": 'VERSION = "%s"\n' % version,
            "CHANGELOG.md": changelog or ("# Changelog\n\n## %s — unreleased\n\n### Migration notes\n- None.\n" % version),
            "template/kitchen.yml.tmpl": KITCHEN_TMPL.read_text(encoding="utf-8"),
            "template/AGENTS.md.tmpl": "# Agents\n\nFramework section for {{version}}.\n\n## This project\n\n(fill in)\n",
            "template/CLAUDE.md.tmpl": "@AGENTS.md\n",
            "template/CONTRIBUTING.md": "Contributing v1\n",
            "template/playbooks/deliver.md": "deliver v1\n",
            "template/backlog/README.md": "backlog rules\n",
            "template/docs/decision-log.md": "# Decision log\n",
            "template/scripts/backlog_check.py": FAKE_SCRIPT,
            "template/scripts/deliver.py": FAKE_SCRIPT,
            "template/scripts/__pycache__/junk.cpython-39.pyc": "not installed",
            "template/claude/settings.json": GUARD_SETTINGS,
            "template/claude/hooks/guard.py": "# fake guard\n",
            "template/github/workflows/check.yml": GITHUB_CI,
            "template/github/pull_request_template.md": "## Ticket\n",
            "template/gitlab/gitlab-ci.yml": GITLAB_CI,
            "template/gitlab/merge_request_templates/Default.md": "## Ticket\n",
        }
        files.update(overrides or {})
        write_tree(src, files)
        return src

    def make_project(self, origin: Optional[str] = "https://github.com/example/demo.git",
                     files: Optional[Dict[str, Optional[str]]] = None) -> Path:
        project = self.tmp / "project"
        project.mkdir()
        self.git(project, "init", "-q")
        if origin:
            self.git(project, "remote", "add", "origin", origin)
        write_tree(project, files if files is not None else {
            "pyproject.toml": "[project]\nname = \"demo\"\n\n[tool.pytest.ini_options]\n",
            "src/demo/__init__.py": "",
            "tests/test_demo.py": "def test_demo():\n    pass\n",
        })
        self.git(project, "add", "-A")
        self.git(project, "commit", "-q", "-m", "initial", "--allow-empty")
        return project

    def git(self, cwd: Path, *args: str) -> str:
        result = subprocess.run(["git"] + list(args), cwd=str(cwd), env=self.env,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def run_init(self, project: Path, *args: str) -> subprocess.CompletedProcess:
        # start_new_session: no controlling terminal, so /dev/tty cannot be
        # opened and init.py behaves as it does under an agent or in CI.
        return subprocess.run(
            [sys.executable, str(INIT)] + list(args), cwd=str(project), env=self.env,
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True, timeout=120, start_new_session=True,
        )

    def install(self, project: Path, source: Path, *extra: str) -> subprocess.CompletedProcess:
        result = self.run_init(project, "--yes", "--source", str(source), "--tests", "tests/**",
                               "--code", "src/**", "--test-command",
                               "python3 -m pytest {files} --junitxml={report}", *extra)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def lock(self, project: Path) -> dict:
        return json.loads((project / "kitchen.lock").read_text(encoding="utf-8"))


class InstallTests(InitTestCase):
    def test_help_works(self) -> None:
        result = self.run_init(self.tmp, "--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        for flag in ("--dry-run", "--yes", "--tests", "--code", "--test-command", "--host", "--no-claude",
                     "--source", "--version", "--target", "update", "doctor"):
            self.assertIn(flag, result.stdout)

    def test_dry_run_writes_nothing(self) -> None:
        source = self.make_source("src", "0.1.0")
        project = self.make_project()
        before = snapshot(project)
        result = self.run_init(project, "--dry-run", "--source", str(source))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(snapshot(project), before)
        self.assertIn("Dry run: nothing was written.", result.stdout)
        self.assertIn("create", result.stdout)
        self.assertIn("AGENTS.md", result.stdout)
        # The answers were guessed from pyproject.toml and the folders.
        self.assertIn("python3 -m pytest {files} --junitxml={report}", result.stdout)
        self.assertIn("tests/**", result.stdout)

    def test_dry_run_on_a_plain_folder_does_not_run_git_init(self) -> None:
        source = self.make_source("src", "0.1.0")
        folder = self.tmp / "plain"
        folder.mkdir()
        result = self.run_init(folder, "--dry-run", "--source", str(source), "--tests", "t/**", "--code", "c/**",
                               "--test-command", "x {report}")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("git init", result.stdout)
        self.assertFalse((folder / ".git").exists())
        self.assertEqual(snapshot(folder), {})

    def test_install_creates_mapped_files_and_lock(self) -> None:
        source = self.make_source("src", "0.1.0")
        project = self.make_project()
        result = self.install(project, source)
        for rel in ("AGENTS.md", "CLAUDE.md", "kitchen.yml", "kitchen.lock", "CONTRIBUTING.md",
                    "playbooks/deliver.md", "backlog/README.md", "docs/decision-log.md",
                    "scripts/backlog_check.py", "scripts/deliver.py", ".claude/settings.json",
                    ".claude/hooks/guard.py", ".github/workflows/check.yml", ".github/pull_request_template.md"):
            self.assertTrue((project / rel).is_file(), rel)
        for rel in ("AGENTS.md.tmpl", "kitchen.yml.tmpl", "claude", "github", "gitlab", ".gitlab-ci.yml",
                    ".gitlab", "scripts/__pycache__"):
            self.assertFalse((project / rel).exists(), rel)
        self.assertIn("Framework section for 0.1.0.", (project / "AGENTS.md").read_text())

        import yaml
        config = yaml.safe_load((project / "kitchen.yml").read_text())
        self.assertEqual(config, {"tests": ["tests/**"], "code": ["src/**"],
                                  "test_command": "python3 -m pytest {files} --junitxml={report}"})

        lock = self.lock(project)
        self.assertEqual(lock["version"], "0.1.0")
        self.assertTrue(lock["source"].startswith("local checkout"))
        self.assertEqual(lock["options"]["host"], "github")
        self.assertFalse(lock["options"]["no_claude"])
        self.assertEqual(lock["options"]["toolchain"], ["python"])
        self.assertNotIn("kitchen.yml", lock["files"])
        self.assertIn(".claude/settings.json", lock["files"])
        for rel, sha in lock["files"].items():
            self.assertEqual(init.sha256_file(project / rel), sha, rel)
        self.assertEqual(lock["side_by_side"], [])

        # The toolchain step was filled for Python, at the step's indentation.
        ci = (project / ".github/workflows/check.yml").read_text()
        self.assertIn("# TEST-KITCHEN: toolchain setup (filled by init.py: python)", ci)
        self.assertIn("      - uses: actions/setup-python@v7", ci)
        self.assertIn("python3 -m pip install pyyaml pytest -e .", ci)
        self.assertNotIn("not filled in", ci)
        self.assertEqual(yaml.safe_load(ci)["jobs"]["check"]["steps"][-1]["name"], "Check")
        # doctor ran at the end and found nothing to fail.
        self.assertIn("Test Kitchen doctor", result.stdout)
        self.assertIn("doctor: ", result.stdout)
        self.assertNotIn("FAIL", result.stdout)

    def test_existing_files_get_side_by_side_copies(self) -> None:
        source = self.make_source("src", "0.1.0")
        project = self.make_project(files={
            "AGENTS.md": "my own agent rules\n",
            "CONTRIBUTING.md": "my contributing\n",
            "tests/test_a.py": "",
        })
        result = self.install(project, source)
        self.assertEqual((project / "AGENTS.md").read_text(), "my own agent rules\n")
        self.assertEqual((project / "CONTRIBUTING.md").read_text(), "my contributing\n")
        self.assertIn("Framework section", (project / "AGENTS.md.kitchen-new").read_text())
        self.assertEqual((project / "CONTRIBUTING.md.kitchen-new").read_text(), "Contributing v1\n")
        self.assertIn("AGENTS.md.kitchen-new", result.stdout)
        lock = self.lock(project)
        self.assertEqual(lock["side_by_side"], ["AGENTS.md", "CONTRIBUTING.md"])
        self.assertIn("AGENTS.md", lock["files"])
        self.assertIn("WARN  AGENTS.md.kitchen-new waiting to be merged", result.stdout)

    def test_existing_kitchen_yml_is_not_overwritten(self) -> None:
        source = self.make_source("src", "0.1.0")
        project = self.make_project(files={"kitchen.yml": "tests: [mine]\n"})
        self.install(project, source)
        self.assertEqual((project / "kitchen.yml").read_text(), "tests: [mine]\n")
        self.assertTrue((project / "kitchen.yml.kitchen-new").is_file())

    def test_no_claude_skips_claude_files(self) -> None:
        source = self.make_source("src", "0.1.0")
        project = self.make_project()
        result = self.install(project, source, "--no-claude")
        self.assertFalse((project / ".claude").exists())
        self.assertFalse((project / "CLAUDE.md").exists())
        self.assertTrue((project / "AGENTS.md").is_file())
        lock = self.lock(project)
        self.assertTrue(lock["options"]["no_claude"])
        self.assertFalse(any(path.startswith(".claude/") for path in lock["files"]))
        self.assertIn("SKIP  merge guard", result.stdout)

    def test_gitlab_host_installs_only_gitlab_files(self) -> None:
        source = self.make_source("src", "0.1.0")
        project = self.make_project()  # origin is GitHub; --host wins
        self.install(project, source, "--host", "gitlab")
        self.assertTrue((project / ".gitlab-ci.yml").is_file())
        self.assertTrue((project / ".gitlab/merge_request_templates/Default.md").is_file())
        self.assertFalse((project / ".github").exists())
        import yaml
        self.assertEqual(yaml.safe_load((project / "kitchen.yml").read_text())["host"], "gitlab")
        ci = (project / ".gitlab-ci.yml").read_text()
        self.assertIn("    - 'python3 -m pip install pyyaml pytest -e .'", ci)
        self.assertEqual(yaml.safe_load(ci)["check"]["script"][-1], "python3 scripts/deliver.py check")

    def test_host_is_detected_from_origin(self) -> None:
        source = self.make_source("src", "0.1.0")
        project = self.make_project(origin="git@gitlab.example.com:team/demo.git")
        self.install(project, source)
        self.assertTrue((project / ".gitlab-ci.yml").is_file())
        self.assertFalse((project / ".github").exists())
        self.assertEqual(self.lock(project)["options"]["host"], "gitlab")
        import yaml
        self.assertNotIn("host", yaml.safe_load((project / "kitchen.yml").read_text()))

    def test_manual_host_installs_no_ci_files(self) -> None:
        source = self.make_source("src", "0.1.0")
        project = self.make_project(origin=None)
        result = self.install(project, source)
        self.assertFalse((project / ".github").exists())
        self.assertFalse((project / ".gitlab-ci.yml").exists())
        self.assertEqual(self.lock(project)["options"]["host"], "manual")
        self.assertIn("SKIP  CI: manual host", result.stdout)

    def test_missing_answer_without_terminal_fails_clearly(self) -> None:
        source = self.make_source("src", "0.1.0")
        project = self.make_project(files={"README.md": "nothing to guess from\n"})
        before = snapshot(project)
        result = self.run_init(project, "--yes", "--source", str(source))
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("--tests", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(snapshot(project), before)

    def test_no_terminal_without_yes_refuses_to_write(self) -> None:
        source = self.make_source("src", "0.1.0")
        project = self.make_project()
        before = snapshot(project)
        result = self.run_init(project, "--source", str(source))
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("--yes", result.stderr)
        self.assertEqual(snapshot(project), before)

    def test_test_command_without_report_is_refused(self) -> None:
        source = self.make_source("src", "0.1.0")
        project = self.make_project()
        result = self.run_init(project, "--yes", "--source", str(source), "--test-command", "pytest")
        self.assertEqual(result.returncode, 2)
        self.assertIn("{report}", result.stderr)
        self.assertFalse((project / "kitchen.lock").exists())

    def test_install_at_a_subfolder_of_a_repository_is_refused(self) -> None:
        source = self.make_source("src", "0.1.0")
        project = self.make_project()
        sub = project / "src"
        result = self.run_init(sub, "--yes", "--source", str(source))
        self.assertEqual(result.returncode, 2)
        self.assertIn("repository root", result.stderr)

    def test_install_over_an_existing_install_runs_update(self) -> None:
        source = self.make_source("src", "0.1.0")
        project = self.make_project()
        self.install(project, source)
        result = self.run_init(project, "--yes", "--source", str(source))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Running update instead", result.stdout)
        self.assertFalse((project / "AGENTS.md.kitchen-new").exists())


class UpdateTests(InitTestCase):
    def test_update_replaces_unchanged_files_and_reports_conflicts(self) -> None:
        v1 = self.make_source("v1", "0.1.0")
        project = self.make_project()
        self.install(project, v1)
        (project / "CONTRIBUTING.md").write_text("Contributing v1, edited by the project\n")
        (project / "docs/decision-log.md").write_text("# Decision log\n\n### a project entry\n")
        v2 = self.make_source("v2", "0.2.0", overrides={
            "template/CONTRIBUTING.md": "Contributing v2\n",
            "template/playbooks/deliver.md": "deliver v2\n",
            "template/playbooks/define.md": "define v2\n",
            "template/backlog/README.md": None,
        }, changelog=(
            "# Changelog\n\n## 0.2.0 — 2026-12-01\n\n### Added\n- define playbook\n\n"
            "### Migration notes\n- Add `split_threshold` to kitchen.yml if you want a stricter limit.\n\n"
            "## 0.1.0 — 2026-11-24\n\n### Migration notes\n- None: first release.\n"
        ))
        result = self.run_init(project, "update", "--yes", "--source", str(v2))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        out = result.stdout
        # Unchanged locally → replaced.
        self.assertEqual((project / "playbooks/deliver.md").read_text(), "deliver v2\n")
        # Edited locally and changed in v2 → conflict; --yes keeps it and writes a side-by-side copy.
        self.assertEqual((project / "CONTRIBUTING.md").read_text(), "Contributing v1, edited by the project\n")
        self.assertEqual((project / "CONTRIBUTING.md.kitchen-new").read_text(), "Contributing v2\n")
        self.assertIn("conflict", out)
        self.assertIn("CONTRIBUTING.md", out)
        # Edited locally, unchanged in v2 → kept, no copy.
        self.assertIn("### a project entry", (project / "docs/decision-log.md").read_text())
        self.assertFalse((project / "docs/decision-log.md.kitchen-new").exists())
        # New file added; removed file listed, not deleted.
        self.assertEqual((project / "playbooks/define.md").read_text(), "define v2\n")
        self.assertTrue((project / "backlog/README.md").is_file())
        self.assertIn("removed", out)
        self.assertIn("backlog/README.md", out)
        # Migration notes between the versions are printed; older ones are not.
        self.assertIn("split_threshold", out)
        self.assertNotIn("None: first release.", out)
        # The lock moved to 0.2.0 with the new hashes, and dropped the removed file.
        lock = self.lock(project)
        self.assertEqual(lock["version"], "0.2.0")
        self.assertNotIn("backlog/README.md", lock["files"])
        self.assertEqual(lock["files"]["playbooks/deliver.md"], init.sha256_file(project / "playbooks/deliver.md"))
        self.assertEqual(lock["files"]["CONTRIBUTING.md"], init.sha256_bytes(b"Contributing v2\n"))
        self.assertEqual(lock["side_by_side"], ["CONTRIBUTING.md"])
        # kitchen.yml is the project's: update leaves it alone.
        self.assertIn("tests/**", (project / "kitchen.yml").read_text())

    def test_update_dry_run_writes_nothing(self) -> None:
        v1 = self.make_source("v1", "0.1.0")
        project = self.make_project()
        self.install(project, v1)
        v2 = self.make_source("v2", "0.2.0", overrides={"template/playbooks/deliver.md": "deliver v2\n"})
        before = snapshot(project)
        result = self.run_init(project, "update", "--dry-run", "--source", str(v2))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("replace", result.stdout)
        self.assertEqual(snapshot(project), before)

    def test_update_restores_a_deleted_framework_file(self) -> None:
        v1 = self.make_source("v1", "0.1.0")
        project = self.make_project()
        self.install(project, v1)
        (project / "playbooks/deliver.md").unlink()
        result = self.run_init(project, "update", "--yes", "--source", str(v1))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("restore", result.stdout)
        self.assertEqual((project / "playbooks/deliver.md").read_text(), "deliver v1\n")

    def test_update_without_lock_fails_clearly(self) -> None:
        v1 = self.make_source("v1", "0.1.0")
        project = self.make_project()
        result = self.run_init(project, "update", "--yes", "--source", str(v1))
        self.assertEqual(result.returncode, 2)
        self.assertIn("kitchen.lock", result.stderr)


class DoctorTests(InitTestCase):
    def test_doctor_reports_missing_guard_registration(self) -> None:
        source = self.make_source("src", "0.1.0")
        project = self.make_project()
        self.install(project, source)
        ok = self.run_init(project, "doctor")
        self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)
        self.assertIn("PASS  merge guard registered", ok.stdout)

        (project / ".claude/settings.json").write_text("{}\n")
        before = snapshot(project)
        result = self.run_init(project, "doctor")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("FAIL  merge guard not registered", result.stdout)
        self.assertIn(".claude/settings.json", result.stdout)
        self.assertIn("Restore the hook", result.stdout)
        self.assertEqual(snapshot(project), before)  # read-only: no __pycache__, nothing else

    def test_doctor_reports_disabled_hooks(self) -> None:
        source = self.make_source("src", "0.1.0")
        project = self.make_project()
        self.install(project, source)
        (project / ".claude/settings.local.json").write_text('{"disableAllHooks": true}\n')
        result = self.run_init(project, "doctor")
        self.assertEqual(result.returncode, 1)
        self.assertIn("disableAllHooks", result.stdout)

    def test_doctor_warns_about_an_unfilled_toolchain_step(self) -> None:
        source = self.make_source("src", "0.1.0")
        project = self.make_project(files={"tests/x.txt": "", "src/x.txt": ""})  # no recognizable stack
        result = self.install(project, source)
        self.assertIn("stack not recognized", result.stdout)
        doctor = self.run_init(project, "doctor")
        self.assertEqual(doctor.returncode, 0, doctor.stdout)
        self.assertIn("WARN  CI file .github/workflows/check.yml: toolchain step not filled", doctor.stdout)
        # Edited elsewhere but the placeholder is still there: still not filled.
        ci = project / ".github/workflows/check.yml"
        ci.write_text(ci.read_text() + "# a comment\n")
        doctor = self.run_init(project, "doctor")
        self.assertIn("toolchain step not filled", doctor.stdout)
        # The placeholder replaced by hand: doctor trusts the person.
        ci.write_text(ci.read_text().replace("Toolchain setup is not filled in. Replace this step.", "make deps"))
        doctor = self.run_init(project, "doctor")
        self.assertIn("edited since install", doctor.stdout)

    def test_doctor_without_install_fails(self) -> None:
        project = self.make_project()
        result = self.run_init(project, "doctor")
        self.assertEqual(result.returncode, 1)
        self.assertIn("FAIL  kitchen.lock missing", result.stdout)


class HelperTests(unittest.TestCase):
    def test_template_mapping(self) -> None:
        m = init.map_template_path
        self.assertEqual(m("AGENTS.md.tmpl", "github", False), "AGENTS.md")
        self.assertEqual(m("CLAUDE.md.tmpl", "github", False), "CLAUDE.md")
        self.assertIsNone(m("CLAUDE.md.tmpl", "github", True))
        self.assertEqual(m("kitchen.yml.tmpl", "manual", False), "kitchen.yml")
        self.assertEqual(m("claude/hooks/guard.py", "manual", False), ".claude/hooks/guard.py")
        self.assertIsNone(m("claude/settings.json", "github", True))
        self.assertEqual(m("github/workflows/check.yml", "github", False), ".github/workflows/check.yml")
        self.assertIsNone(m("github/workflows/check.yml", "gitlab", False))
        self.assertEqual(m("gitlab/gitlab-ci.yml", "gitlab", False), ".gitlab-ci.yml")
        self.assertEqual(m("gitlab/merge_request_templates/Default.md", "gitlab", False),
                         ".gitlab/merge_request_templates/Default.md")
        self.assertIsNone(m("gitlab/gitlab-ci.yml", "manual", False))
        self.assertEqual(m("playbooks/deliver.md", "manual", False), "playbooks/deliver.md")
        self.assertEqual(m("docs/requirements/README.md", "github", True), "docs/requirements/README.md")

    def test_fill_toolchain_github_node(self) -> None:
        stacks = [{"stack": "node", "install": "npm ci", "cache": "npm", "version_file": ""}]
        text, status = init.fill_toolchain(GITHUB_CI, "github", stacks)
        self.assertEqual(status, "filled")
        self.assertIn("      - uses: actions/setup-node@v7\n        with:\n          node-version: lts/*\n"
                      "          cache: npm\n      - name: Install Node dependencies\n        run: npm ci\n\n"
                      "      - name: Check\n", text)
        import yaml
        steps = yaml.safe_load(text)["jobs"]["check"]["steps"]
        self.assertEqual([s.get("name") or s.get("uses") for s in steps],
                         ["actions/checkout@v4", "actions/setup-node@v7", "Install Node dependencies", "Check"])

    def test_fill_toolchain_gitlab_both_stacks(self) -> None:
        stacks = [{"stack": "node", "install": "npm ci", "cache": "npm", "version_file": ""},
                  {"stack": "python", "install": "python3 -m pip install pyyaml -r requirements.txt", "version_file": ""}]
        text, status = init.fill_toolchain(GITLAB_CI, "gitlab", stacks)
        self.assertEqual(status, "filled")
        import yaml
        script = yaml.safe_load(text)["check"]["script"]
        self.assertEqual(script[1:], ["npm ci", "python3 -m pip install pyyaml -r requirements.txt",
                                      "python3 scripts/deliver.py check"])
        self.assertTrue(script[0].startswith("command -v npm"))

    def test_fill_toolchain_leaves_unrecognized_and_unmarked_files(self) -> None:
        self.assertEqual(init.fill_toolchain(GITHUB_CI, "github", []), (GITHUB_CI, "unrecognized"))
        self.assertEqual(init.fill_toolchain("jobs: {}\n", "github", [{"stack": "node"}]), ("jobs: {}\n", "no-marker"))

    def test_detect_toolchain(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_tree(root, {"package.json": "{}", "package-lock.json": "{}", "requirements.txt": "",
                              ".python-version": "3.12\n"})
            stacks = init.detect_toolchain(root, "python3 -m pytest {files} --junitxml={report}")
            self.assertEqual([s["stack"] for s in stacks], ["node", "python"])
            self.assertEqual(stacks[0]["install"], "npm ci")
            self.assertEqual(stacks[1]["install"], "python3 -m pip install pyyaml pytest -r requirements.txt")
            self.assertEqual(stacks[1]["version_file"], ".python-version")
            write_tree(root, {"yarn.lock": "", "uv.lock": ""})
            self.assertEqual(init.detect_toolchain(root), [])

    def test_guess_node_vitest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {"package.json": json.dumps({"devDependencies": {"vitest": "^3"}}),
                     "src/app.ts": "", "src/app.test.ts": "", "e2e/flow.spec.ts": ""}
            write_tree(root, files)
            g = init.guess_answers(root, sorted(files))
            self.assertEqual(g.test_command, init.CMD_VITEST)
            self.assertCountEqual(g.tests, ["**/*.test.ts", "**/*.spec.ts"])
            self.assertEqual(g.code, ["src/**"])

    def test_guess_python_and_go(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {"pytest.ini": "", "mypkg/__init__.py": "", "tests/test_x.py": ""}
            write_tree(root, files)
            g = init.guess_answers(root, sorted(files))
            self.assertEqual(g.test_command, init.CMD_PYTEST)
            self.assertEqual(g.tests, ["tests/**"])
            self.assertEqual(g.code, ["mypkg/**"])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {"go.mod": "module example.com/x\n", "pay/refund.go": "", "pay/refund_test.go": ""}
            write_tree(root, files)
            g = init.guess_answers(root, sorted(files))
            self.assertEqual(g.test_command, init.CMD_GO)
            self.assertEqual(g.tests, ["**/*_test.go"])
            self.assertEqual(g.code, ["**/*.go"])

    def test_glob_semantics(self) -> None:
        r = init.glob_to_regex
        self.assertTrue(r("**/*.test.ts").match("a.test.ts"))
        self.assertTrue(r("**/*.test.ts").match("a/b/c.test.ts"))
        self.assertFalse(r("*.py").match("a/b.py"))
        self.assertTrue(r("tests/**").match("tests/x/y.py"))
        self.assertTrue(r("src/?.go").match("src/a.go"))
        self.assertFalse(r("src/?.go").match("src/ab.go"))

    def test_migration_notes_between_versions(self) -> None:
        log = ("## 0.3.0 — later\n### Migration notes\n- three\n\n## 0.2.0 — x\n### Added\n- a\n"
               "### Migration notes\n- two\n\n## 0.1.0 — y\n### Migration notes\n- one\n")
        self.assertEqual(init.migration_notes(log, "0.1.0", "0.3.0"), [("0.2.0", "- two"), ("0.3.0", "- three")])
        self.assertEqual(init.migration_notes(log, "0.2.0", "0.2.0"), [])

    def test_kitchen_template_renders_valid_yaml(self) -> None:
        import yaml
        values = init.config_values("0.1.0", ["tests/**", "**/*.test.ts"], ["src/**"],
                                    'cd app && npx vitest run {files:app} --outputFile.junit={report} --name "x: y"',
                                    "github", True, "chosen with --host")
        config = yaml.safe_load(init.render(KITCHEN_TMPL.read_text(encoding="utf-8"), values))
        self.assertEqual(config["tests"], ["tests/**", "**/*.test.ts"])
        self.assertEqual(config["test_command"],
                         'cd app && npx vitest run {files:app} --outputFile.junit={report} --name "x: y"')
        self.assertEqual(config["host"], "github")
        self.assertEqual(set(config), {"tests", "code", "test_command", "host"})


if __name__ == "__main__":
    unittest.main()
