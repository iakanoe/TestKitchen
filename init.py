#!/usr/bin/env python3
"""Test Kitchen installer, updater, and doctor.

Installs Test Kitchen into a project's repository, updates an installed copy
to another version, and checks that an installed copy works.

Usage (run from the project's repository root, or pass --target):

    curl -fsSL https://raw.githubusercontent.com/iakanoe/TestKitchen/v0.1.0/init.py | python3 -
    python3 path/to/test-kitchen/init.py [install|update|doctor] [options]

Modes:
    install   (default) ask three questions, show the plan, write the files,
              write kitchen.lock, then run doctor. Switches to update when the
              folder already has a kitchen.lock.
    update    replace framework files that were not edited locally, ask about
              the ones that were, add new files, list removed ones (never
              deletes), print the migration notes, rewrite kitchen.lock.
    doctor    read-only checklist: prerequisites, kitchen.yml, the guard, CI,
              the host CLI, and the scripts' self-tests.

The file is self-contained on purpose: it must run from a pipe (`curl … |
python3 -`), where there is no checkout next to it. The bootstrap part uses the
standard library only; PyYAML is a prerequisite of the installed scripts, so
this file checks for it and explains how to install it, but never needs it to
start. Python 3.9 compatible.

Exit codes: 0 success; 1 a failure (prerequisite, fetch, doctor FAIL);
2 a usage problem, including a required answer that could not be asked.
The user guide (guide/install.md) documents every mode, flag, and file.
"""

from __future__ import annotations

import sys

# Checked before anything else so an old interpreter gets a sentence, not a
# traceback. The rest of the file uses syntax that Python 3.9 accepts.
if sys.version_info < (3, 9):  # pragma: no cover - depends on the interpreter
    sys.stderr.write(
        "Test Kitchen needs Python 3.9 or later; this is Python %d.%d.\n"
        % (sys.version_info[0], sys.version_info[1])
    )
    sys.exit(1)

import argparse
import difflib
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

VERSION = "0.1.0"

# Where releases are downloaded from. HTTPS, so cloning needs no SSH key.
# Each release is a tag `vX.Y.Z`; init clones exactly that tag.
REPO_URL = "https://github.com/iakanoe/TestKitchen.git"
# The same repository's web address, for links written into installed files.
REPO_WEB = "https://github.com/iakanoe/TestKitchen"
# The pinned one-liner for this version. init.py is never installed into a
# project, so every "run init.py again" hint must be a command that works from
# the project folder: this URL when piped, or the clone's absolute path.
RAW_URL = "https://raw.githubusercontent.com/iakanoe/TestKitchen/v%s/init.py" % VERSION

LOCK_NAME = "kitchen.lock"
CONFIG_NAME = "kitchen.yml"
# Side-by-side suffix: when a file already exists, the framework's version is
# written next to it under this name instead of overwriting it.
NEW_SUFFIX = ".kitchen-new"
# The CI templates mark the one step init may replace with this exact line.
TOOLCHAIN_MARKER = "# TEST-KITCHEN: toolchain setup"
# Written in place of the marker once init has filled the step, so doctor can
# tell a filled step from the untouched placeholder.
TOOLCHAIN_FILLED = TOOLCHAIN_MARKER + " (filled by init.py:"
# Text inside the CI templates' placeholder step; while it is there, the step
# has not been filled by init or by hand.
TOOLCHAIN_PLACEHOLDER = "Toolchain setup is not filled in"
LOCK_FORMAT = 1

HOSTS = ("github", "gitlab", "manual")
# kitchen.yml keys (spec section 4). Duplicated from scripts/kitchen_lib.py on
# purpose: doctor must work before (and without) the installed scripts.
CONFIG_KEYS = {
    "tests", "code", "test_command", "check_command", "verify", "host",
    "autonomy", "split_threshold", "self_contained_tickets", "releases", "ignore",
}
# Never copied from template/: caches and editor droppings, plus our own
# side-by-side files if someone ran an install inside the template.
TEMPLATE_SKIP_NAMES = {"__pycache__", ".DS_Store", ".git", ".pytest_cache", ".mypy_cache"}
TEMPLATE_SKIP_SUFFIXES = (".pyc", ".pyo", NEW_SUFFIX)
# Folders never scanned when guessing answers or matching globs: they are
# dependencies or build output, and can hold hundreds of thousands of files.
SCAN_SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "env", "__pycache__", "dist", "build",
    ".tox", "vendor", "target", ".mypy_cache", ".pytest_cache", ".next", "coverage",
}
SCAN_LIMIT = 50000

# Test commands init proposes when it recognizes the runner. Each writes JUnit
# XML to {report}, the one result format Test Kitchen reads. guide/test-runners.md
# explains each one.
CMD_PYTEST = "python3 -m pytest {files} --junitxml={report}"
CMD_VITEST = "npx vitest run {files} --reporter=default --reporter=junit --outputFile.junit={report}"
CMD_JEST = "JEST_JUNIT_OUTPUT_FILE={report} npx jest --ci --reporters=default --reporters=jest-junit {files}"
CMD_NODE_TEST = (
    "node --test --test-reporter=spec --test-reporter-destination=stdout "
    "--test-reporter=junit --test-reporter-destination={report} {files}"
)
# `go test` takes packages, not files, so the Go command always runs the whole
# suite; tags still select criteria by test name.
CMD_GO = "gotestsum --junitfile {report} -- ./..."


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------


class UsageError(Exception):
    """A problem the person fixes by changing the command line (exit 2)."""


class Failure(Exception):
    """A problem that stops the run (exit 1)."""


def say(text: str = "") -> None:
    print(text, flush=True)


def warn(text: str) -> None:
    print("warning: " + text, file=sys.stderr, flush=True)


def run(argv: List[str], cwd: Optional[Path] = None, timeout: int = 120,
        env: Optional[Dict[str, str]] = None) -> subprocess.CompletedProcess:
    """Runs a command and captures its output; never raises for a missing program.

    stdin is closed for every child: when this file arrives through a pipe,
    stdin is (or was) the script itself, and no child should read from it.
    """
    try:
        return subprocess.run(
            argv, cwd=str(cwd) if cwd else None, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True, timeout=timeout, env=env,
        )
    except FileNotFoundError:
        return subprocess.CompletedProcess(argv, 127, "", "%s: command not found" % argv[0])
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(argv, 124, "", "%s: timed out after %ss" % (argv[0], timeout))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> Optional[str]:
    try:
        return sha256_bytes(path.read_bytes())
    except OSError:
        return None


def tail(text: str, lines: int = 15) -> str:
    return "\n".join(text.strip().splitlines()[-lines:])


def vtuple(version: str) -> Tuple[int, ...]:
    return tuple(int(part) for part in version.lstrip("v").split("."))


def normalize_version(value: str) -> str:
    """'v1.2.3' or '1.2.3' → '1.2.3'; anything else is a usage error."""
    if not re.fullmatch(r"v?\d+\.\d+\.\d+", value or ""):
        raise UsageError("--version must look like v1.2.3, got %r" % value)
    return value.lstrip("v")


def split_globs(values: Optional[List[str]]) -> List[str]:
    """--tests/--code accept comma-separated lists and may be repeated.

    Commas are safe separators: Test Kitchen globs have no brace expansion.
    """
    out: List[str] = []
    for value in values or []:
        out.extend(part.strip() for part in value.split(",") if part.strip())
    return out


def glob_to_regex(pattern: str) -> "re.Pattern[str]":
    """Compiles a kitchen.yml glob (spec section 4) to a full-match regex.

    `**/` matches zero or more whole path segments, any other `**` matches
    anything, `*` anything but `/`, `?` one character but `/`. This mirrors
    scripts/kitchen_lib.py; it lives here too because doctor must work when
    the installed scripts are missing or broken.
    """
    out: List[str] = []
    i = 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif pattern[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    return re.compile("".join(out) + r"\Z")


def matches_any(path: str, patterns: List[str]) -> bool:
    return any(glob_to_regex(p).match(path) for p in patterns)


# --------------------------------------------------------------------------
# Asking the person
# --------------------------------------------------------------------------


class Prompter:
    """Asks questions, or explains why it cannot.

    Interactive when stdin is a terminal, or when /dev/tty can be opened: a
    piped install (`curl … | python3 -`) has the script on stdin, so answers
    are read from the controlling terminal instead. Non-interactive with
    --yes (every question takes its default) or with no terminal at all
    (agents, CI). Without a terminal and without --yes, nothing that needs a
    yes can go ahead: the run stops and says to pass --yes, because writing
    files nobody confirmed is worse than stopping.
    """

    def __init__(self, assume_yes: bool) -> None:
        self.assume_yes = assume_yes
        self._tty_in = None
        self._tty_out = None
        self.interactive = False
        if assume_yes:
            return
        if sys.stdin is not None and sys.stdin.isatty():
            self.interactive = True
            return
        try:
            self._tty_in = open("/dev/tty", "r")
            self._tty_out = open("/dev/tty", "w")
            self.interactive = True
        except OSError:
            # No controlling terminal (agent shell, CI, a detached process).
            self._tty_in = self._tty_out = None

    def _read(self, prompt: str) -> str:
        if self._tty_in is not None and self._tty_out is not None:
            self._tty_out.write(prompt)
            self._tty_out.flush()
            line = self._tty_in.readline()
            return line.rstrip("\n") if line else ""
        try:
            return input(prompt)
        except EOFError:
            return ""

    def value(self, question: str, default: Optional[str], flag: str) -> str:
        """A free-text answer. Without a way to ask, the default or a clear failure."""
        if not self.interactive:
            if default:
                return default
            raise UsageError(
                "%s: no answer given and none could be guessed, and there is no terminal "
                "to ask on. Pass %s." % (question, flag)
            )
        while True:
            shown = " [%s]" % default if default else ""
            answer = self._read("%s%s: " % (question, shown)).strip()
            if answer:
                return answer
            if default:
                return default
            say("  An answer is required (or press Ctrl-C to stop).")

    def confirm(self, question: str, default: bool) -> bool:
        """A yes/no question. --yes answers yes; no terminal and no --yes stops."""
        if self.assume_yes:
            return True
        if not self.interactive:
            raise UsageError(
                "%s There is no terminal to ask on: rerun with --yes to accept, "
                "or with --dry-run to only see the plan." % question
            )
        hint = "[Y/n]" if default else "[y/N]"
        while True:
            answer = self._read("%s %s " % (question, hint)).strip().lower()
            if not answer:
                return default
            if answer in ("y", "yes"):
                return True
            if answer in ("n", "no"):
                return False

    def choose(self, question: str, choices: Dict[str, str], default: str) -> str:
        """One letter from `choices` (letter → meaning). --yes takes the default."""
        if not self.interactive:
            return default
        letters = "/".join(choices)
        while True:
            answer = self._read("%s [%s, default %s] " % (question, letters, default)).strip().lower()
            if not answer:
                return default
            if answer[:1] in choices:
                return answer[:1]


# --------------------------------------------------------------------------
# Where the framework comes from
# --------------------------------------------------------------------------


class Source:
    """A Test Kitchen release on disk: a folder holding `template/` and CHANGELOG.md."""

    def __init__(self, root: Path, version: str, label: str, tempdir: Optional[str] = None) -> None:
        self.root = root
        self.version = version
        self.label = label
        self.tempdir = tempdir

    @property
    def template(self) -> Path:
        return self.root / "template"

    def changelog(self) -> str:
        try:
            return (self.root / "CHANGELOG.md").read_text(encoding="utf-8")
        except OSError:
            return ""

    def cleanup(self) -> None:
        if self.tempdir:
            shutil.rmtree(self.tempdir, ignore_errors=True)


def read_source_version(root: Path) -> str:
    """The version a checkout holds: its init.py VERSION, else its newest CHANGELOG heading."""
    try:
        text = (root / "init.py").read_text(encoding="utf-8")
        match = re.search(r'(?m)^VERSION = "(\d+\.\d+\.\d+)"', text)
        if match:
            return match.group(1)
    except OSError:
        pass
    try:
        text = (root / "CHANGELOG.md").read_text(encoding="utf-8")
        match = re.search(r"(?m)^## v?(\d+\.\d+\.\d+)", text)
        if match:
            return match.group(1)
    except OSError:
        pass
    raise Failure("Cannot tell which version %s holds: no VERSION in init.py and no "
                  "'## x.y.z' heading in CHANGELOG.md." % root)


def rerun(args: str = "") -> str:
    """The command that runs this init.py again from the project folder.

    init.py is not copied into projects, so `python3 init.py …` would fail there.
    Run from a clone, the hint names the clone's file; piped, the pinned URL.
    """
    here = Path(__file__)
    tail = (" " + args) if args else ""
    if here.is_file():
        return "python3 %s%s --target ." % (shlex.quote(str(here.resolve())), tail)
    return "curl -fsSL %s | python3 -%s" % (RAW_URL, tail)


def local_checkout() -> Optional[Path]:
    """The checkout this file sits in, when run as a file rather than from a pipe.

    The clone-then-run install path (`python3 test-kitchen/init.py --target
    …`) already has the release on disk, so cloning it again would be waste.
    A piped script has `__file__ == "<stdin>"`, which is not a file, so a
    project that happens to have its own `template/` folder is never mistaken
    for a checkout; the kitchen.yml.tmpl check guards the same mistake.
    """
    here = Path(__file__)
    if not here.is_file():
        return None
    root = here.resolve().parent
    if (root / "template" / "kitchen.yml.tmpl").is_file():
        return root
    return None


def git_short_sha(root: Path) -> Optional[str]:
    result = run(["git", "rev-parse", "--short=12", "HEAD"], cwd=root)
    return result.stdout.strip() if result.returncode == 0 else None


def resolve_source(args: argparse.Namespace) -> Source:
    """Picks where the release comes from: --source, the checkout next to this file, or a clone.

    The lock records a label, never an absolute local path: lock files are
    committed, and local paths leak user names and mean nothing elsewhere.
    """
    wanted = normalize_version(args.version) if args.version else None
    if args.source:
        root = Path(args.source).expanduser().resolve()
        if not (root / "template").is_dir():
            raise UsageError("--source %s has no template/ folder; point it at a Test Kitchen checkout." % args.source)
        version = read_source_version(root)
        if wanted and wanted != version:
            raise UsageError("--source holds version %s but --version asks for %s." % (version, wanted))
        sha = git_short_sha(root)
        return Source(root, version, "local checkout" + (" (commit %s)" % sha if sha else ""))
    checkout = local_checkout()
    if checkout is not None and not wanted:
        sha = git_short_sha(checkout)
        return Source(checkout, read_source_version(checkout),
                      "local checkout" + (" (commit %s)" % sha if sha else ""))
    version = wanted or VERSION
    tempdir = tempfile.mkdtemp(prefix="test-kitchen-")
    dest = Path(tempdir) / "test-kitchen"
    # Shallow clone of the release tag only: the tag pins the version, and the
    # history is not needed. GIT_TERMINAL_PROMPT=0 makes a missing or private
    # repository fail instead of waiting for a password nobody will type.
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    result = run(["git", "clone", "--quiet", "--depth", "1", "--branch", "v" + version, REPO_URL, str(dest)],
                 timeout=300, env=env)
    if result.returncode != 0:
        shutil.rmtree(tempdir, ignore_errors=True)
        raise Failure("Could not download Test Kitchen v%s from %s:\n%s\nWith a local checkout, pass --source DIR."
                      % (version, REPO_URL, tail(result.stderr)))
    return Source(dest, read_source_version(dest), "%s@v%s" % (REPO_URL, version), tempdir)


# --------------------------------------------------------------------------
# Template mapping and rendering
# --------------------------------------------------------------------------


def map_template_path(rel: str, host: str, no_claude: bool) -> Optional[str]:
    """Where a file under template/ is installed, or None when it is not installed.

    template/ stores instruction files inertly so tools never load them while
    Test Kitchen itself is developed (spec section 2): `claude/` → `.claude/`,
    `github/` → `.github/`, `gitlab/gitlab-ci.yml` → `.gitlab-ci.yml`, other
    `gitlab/…` → `.gitlab/…`, and a trailing `.tmpl` is dropped. Host folders
    install only for their host. --no-claude skips every Claude Code file:
    `.claude/` and `CLAUDE.md`, whose only content points Claude Code at
    AGENTS.md and its skills. Everything else keeps its relative path, so a
    new template file needs no change here.
    """
    parts = rel.split("/")
    top = parts[0]
    if top == "claude":
        if no_claude:
            return None
        dest = "/".join([".claude"] + parts[1:])
    elif top == "github":
        if host != "github":
            return None
        dest = "/".join([".github"] + parts[1:])
    elif top == "gitlab":
        if host != "gitlab":
            return None
        dest = ".gitlab-ci.yml" if rel == "gitlab/gitlab-ci.yml" else "/".join([".gitlab"] + parts[1:])
    else:
        if rel == "CLAUDE.md.tmpl" and no_claude:
            return None
        dest = rel
    if dest.endswith(".tmpl"):
        dest = dest[: -len(".tmpl")]
    return dest


def walk_template(template: Path) -> List[str]:
    """Every file under template/, as sorted '/'-separated relative paths."""
    found: List[str] = []
    for dirpath, dirnames, filenames in os.walk(str(template)):
        dirnames[:] = sorted(d for d in dirnames if d not in TEMPLATE_SKIP_NAMES)
        for name in filenames:
            if name in TEMPLATE_SKIP_NAMES or name.endswith(TEMPLATE_SKIP_SUFFIXES):
                continue
            full = Path(dirpath) / name
            found.append(full.relative_to(template).as_posix())
    return sorted(found)


def render(text: str, values: Dict[str, str]) -> str:
    """Replaces `{{key}}` for the known keys only.

    Exact-token replacement, not a template engine: `{files}` and `{report}`
    placeholders (single braces) and anything unknown pass through untouched.
    """
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


class TemplateFile:
    def __init__(self, src: str, dest: str, content: bytes, executable: bool) -> None:
        self.src = src
        self.dest = dest
        self.content = content
        self.executable = executable


def build_files(source: Source, host: str, no_claude: bool, values: Dict[str, str],
                stacks: List[Dict[str, str]], notes: List[str]) -> Dict[str, TemplateFile]:
    """Maps, renders, and toolchain-fills every template file for this install."""
    files: Dict[str, TemplateFile] = {}
    for rel in walk_template(source.template):
        dest = map_template_path(rel, host, no_claude)
        if dest is None:
            continue
        path = source.template / rel
        content = path.read_bytes()
        if rel.endswith(".tmpl"):
            content = render(content.decode("utf-8"), values).encode("utf-8")
        style = ci_style(dest)
        if style:
            text = content.decode("utf-8")
            text, status = fill_toolchain(text, style, stacks)
            content = text.encode("utf-8")
            notes.append(toolchain_note(dest, status, stacks))
        files[dest] = TemplateFile(rel, dest, content, bool(path.stat().st_mode & 0o111))
    return files


# --------------------------------------------------------------------------
# CI toolchain step
# --------------------------------------------------------------------------


def ci_style(dest: str) -> Optional[str]:
    """Which CI syntax a destination file uses, or None if it is not a CI file."""
    if dest.startswith(".github/workflows/") and dest.endswith((".yml", ".yaml")):
        return "github"
    if dest == ".gitlab-ci.yml":
        return "gitlab"
    return None


def detect_toolchain(target: Path, test_command: str = "") -> List[Dict[str, str]]:
    """The stacks whose CI setup init can write: Node (npm) and Python (pip).

    Only stacks recognized with certainty: Node with npm (a yarn, pnpm, or bun
    lock file means another package manager, which is left to the person) and
    Python installed with pip (Poetry, uv, and Pipenv lock files are left to
    the person too). Anything else keeps the template's placeholder step and
    doctor warns about it. A project can have both stacks; both get set up.
    """
    stacks: List[Dict[str, str]] = []
    exists = lambda name: (target / name).is_file()  # noqa: E731 - local shorthand
    if exists("package.json") and not any(exists(n) for n in ("yarn.lock", "pnpm-lock.yaml", "bun.lockb", "bun.lock")):
        locked = exists("package-lock.json") or exists("npm-shrinkwrap.json")
        version_file = next((n for n in (".nvmrc", ".node-version") if exists(n)), "")
        stacks.append({
            "stack": "node",
            # `npm ci` needs a lock file; without one, `npm install` is the only option.
            "install": "npm ci" if locked else "npm install",
            "cache": "npm" if locked else "",
            "version_file": version_file,
        })
    python_markers = ("requirements.txt", "pyproject.toml", "setup.py", "setup.cfg")
    other_python = ("poetry.lock", "uv.lock", "Pipfile", "Pipfile.lock")
    if any(exists(n) for n in python_markers) and not any(exists(n) for n in other_python):
        req_files = [n for n in ("requirements.txt", "requirements-dev.txt", "dev-requirements.txt",
                                 "requirements-test.txt") if exists(n)]
        # PyYAML is always installed: the step may set up a new interpreter
        # after the template's own PyYAML step, and the scripts need it.
        # pytest is added when the test command uses it, because projects
        # often keep it out of their runtime requirements.
        packages = ["pyyaml"] + (["pytest"] if "pytest" in test_command else [])
        if req_files:
            install = " ".join(packages + ["-r " + n for n in req_files])
        else:
            install = " ".join(packages + ["-e ."])
        stacks.append({
            "stack": "python",
            "install": "python3 -m pip install " + install,
            "version_file": ".python-version" if exists(".python-version") else "",
        })
    return stacks


def toolchain_lines(style: str, indent: str, stacks: List[Dict[str, str]]) -> List[str]:
    """The replacement step(s), indented like the placeholder step."""
    lines: List[str] = []
    for s in stacks:
        if style == "github":
            if s["stack"] == "node":
                # setup-node@v7 is the current major (its release page); `lts/*` is
                # documented setup-node syntax for the latest LTS release.
                lines += [indent + "- uses: actions/setup-node@v7", indent + "  with:"]
                lines.append(indent + ("    node-version-file: " + s["version_file"] if s["version_file"]
                                       else "    node-version: lts/*"))
                if s["cache"]:
                    lines.append(indent + "    cache: " + s["cache"])
                lines += [indent + "- name: Install Node dependencies", indent + "  run: " + s["install"]]
            else:
                lines += [indent + "- uses: actions/setup-python@v7", indent + "  with:"]
                lines.append(indent + ("    python-version-file: " + s["version_file"] if s["version_file"]
                                       else '    python-version: "3.x"'))
                lines += [indent + "- name: Install Python dependencies", indent + "  run: " + s["install"]]
        else:
            # GitLab has no setup actions: the job's image provides the tools.
            # Node is installed from the image's package manager only when the
            # image lacks it. Items are single-quoted so YAML never reads
            # `>`, `|`, or `:` inside them as syntax.
            if s["stack"] == "node":
                lines.append(indent + "- 'command -v npm >/dev/null || (apt-get update -qq && apt-get install -y -qq nodejs npm)'")
            lines.append(indent + "- '" + s["install"].replace("'", "''") + "'")
    return lines


def _indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def fill_toolchain(text: str, style: str, stacks: List[Dict[str, str]]) -> Tuple[str, str]:
    """Replaces the single step under the marker line; returns (text, status).

    The step is the list item right after the marker, plus every following
    line indented deeper than the marker; it ends at the first non-blank line
    at the marker's indentation or less (the next step, a comment, or the end
    of the list). That works for a GitHub Actions step (`- name:` with
    deeper `run:` lines) and a GitLab script item alike. Status: "filled",
    "unrecognized" (no stack to set up; left as is), "no-marker", or
    "bad-shape" (no list item under the marker; left as is).
    """
    lines = text.splitlines(keepends=True)
    marker_at = next((i for i, line in enumerate(lines) if line.strip() == TOOLCHAIN_MARKER), None)
    if marker_at is None:
        return text, "no-marker"
    if not stacks:
        return text, "unrecognized"
    indent = lines[marker_at][: _indent_of(lines[marker_at])]
    start = next((j for j in range(marker_at + 1, len(lines)) if lines[j].strip()), None)
    if start is None or not lines[start].startswith(indent + "-"):
        return text, "bad-shape"
    end = start + 1
    while end < len(lines) and (not lines[end].strip() or _indent_of(lines[end]) > len(indent)):
        end += 1
    while end - 1 > start and not lines[end - 1].strip():
        end -= 1  # trailing blank lines stay between this step and the next
    names = ", ".join(s["stack"] for s in stacks)
    new = [indent + TOOLCHAIN_FILLED + " " + names + ")\n"]
    new += [line + "\n" for line in toolchain_lines(style, indent, stacks)]
    return "".join(lines[:marker_at] + new + lines[end:]), "filled"


def toolchain_note(dest: str, status: str, stacks: List[Dict[str, str]]) -> str:
    if status == "filled":
        return "%s: toolchain step filled for %s." % (dest, ", ".join(s["stack"] for s in stacks))
    if status == "unrecognized":
        return ("%s: stack not recognized; fill the step under '%s' yourself "
                "(set up your language and install dependencies)." % (dest, TOOLCHAIN_MARKER))
    if status == "bad-shape":
        return "%s: no step found under '%s'; left as is." % (dest, TOOLCHAIN_MARKER)
    return "%s: no toolchain marker; left as is." % dest


# --------------------------------------------------------------------------
# Looking at the project
# --------------------------------------------------------------------------


def is_git_repo(target: Path) -> bool:
    return run(["git", "rev-parse", "--is-inside-work-tree"], cwd=target).returncode == 0


def git_toplevel(target: Path) -> Optional[Path]:
    result = run(["git", "rev-parse", "--show-toplevel"], cwd=target)
    return Path(result.stdout.strip()).resolve() if result.returncode == 0 else None


def list_project_files(target: Path) -> List[str]:
    """Repository-relative files: tracked plus untracked-but-not-ignored, minus dependency folders."""
    files: List[str] = []
    if is_git_repo(target):
        result = run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=target)
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if line and not any(part in SCAN_SKIP_DIRS for part in line.split("/")[:-1]):
                    files.append(line)
                    if len(files) >= SCAN_LIMIT:
                        break
            return sorted(set(files))
    for dirpath, dirnames, filenames in os.walk(str(target)):
        dirnames[:] = [d for d in dirnames if d not in SCAN_SKIP_DIRS]
        for name in filenames:
            files.append((Path(dirpath) / name).relative_to(target).as_posix())
            if len(files) >= SCAN_LIMIT:
                return sorted(files)
    return sorted(files)


class Guess:
    def __init__(self) -> None:
        self.tests: List[str] = []
        self.code: List[str] = []
        self.test_command: Optional[str] = None
        self.reasons: List[str] = []


JS_TEST_FILE = re.compile(r"\.(test|spec)\.([cm]?[jt]sx?)$")


def guess_answers(target: Path, files: List[str]) -> Guess:
    """Guesses the three answers from the project's files. Guesses are shown, never applied silently."""
    g = Guess()
    top_dirs = {f.split("/")[0] for f in files if "/" in f}
    names = set(files)
    text = lambda name: _read_text(target / name)  # noqa: E731 - local shorthand

    pkg: Dict = {}
    if "package.json" in names:
        try:
            pkg = json.loads(text("package.json") or "{}")
        except ValueError:
            pkg = {}
    deps: Dict = {}
    for key in ("dependencies", "devDependencies"):
        if isinstance(pkg.get(key), dict):
            deps.update(pkg[key])
    test_script = str((pkg.get("scripts") or {}).get("test", "")) if isinstance(pkg.get("scripts"), dict) else ""

    if "vitest" in deps or "vitest" in test_script:
        g.test_command = CMD_VITEST
        g.reasons.append("package.json uses vitest")
    elif "jest" in deps or "jest" in test_script:
        g.test_command = CMD_JEST
        note = "" if "jest-junit" in deps else " (add the jest-junit package for the JUnit report)"
        g.reasons.append("package.json uses jest" + note)
    elif "node --test" in test_script:
        g.test_command = CMD_NODE_TEST
        g.reasons.append("package.json's test script uses node --test")

    python_files = ("pyproject.toml", "setup.cfg", "tox.ini", "pytest.ini", "setup.py")
    is_python = any(n in names for n in python_files + ("requirements.txt",)) or any(f.endswith(".py") for f in files)
    uses_pytest = "pytest.ini" in names or any(f == "conftest.py" or f.endswith("/conftest.py") for f in files) \
        or any("pytest" in text(n) for n in python_files + ("requirements.txt", "requirements-dev.txt") if n in names)
    if g.test_command is None and uses_pytest:
        g.test_command = CMD_PYTEST
        g.reasons.append("the project uses pytest")

    is_go = "go.mod" in names
    if g.test_command is None and is_go:
        g.test_command = CMD_GO
        g.reasons.append("go.mod found (the command needs gotestsum installed)")

    for folder in ("tests", "test", "__tests__", "spec"):
        if folder in top_dirs:
            g.tests.append(folder + "/**")
    covered = lambda f: matches_any(f, g.tests)  # noqa: E731 - local shorthand
    extra: List[str] = []
    for f in files:
        base = f.rsplit("/", 1)[-1]
        js = JS_TEST_FILE.search(base)
        if js and not covered(f):
            extra.append("**/*.%s.%s" % (js.group(1), js.group(2)))
        elif base.endswith(".py") and (base.startswith("test_") or base.endswith("_test.py")) and not covered(f):
            extra.append("**/test_*.py" if base.startswith("test_") else "**/*_test.py")
        elif base.endswith("_test.go"):
            extra.append("**/*_test.go")
        if "/__tests__/" in "/" + f and not covered(f):
            extra.append("**/__tests__/**")
    for pattern in extra:
        if pattern not in g.tests:
            g.tests.append(pattern)
    if g.tests:
        g.reasons.append("test files found in the project")

    if is_go:
        g.code = ["**/*.go"]  # Go code lives everywhere; *_test.go files count as tests (tests win).
    else:
        for folder in ("src", "lib", "app", "pkg", "cmd", "internal"):
            if folder in top_dirs:
                g.code.append(folder + "/**")
        if not g.code and is_python:
            for folder in sorted(top_dirs):
                if folder + "/__init__.py" in names and folder not in ("tests", "test"):
                    g.code.append(folder + "/**")
    if g.code:
        g.reasons.append("code folders found in the project")
    return g


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def detect_host(target: Path) -> Tuple[str, str]:
    """(host, why) from the origin remote, by the same rule as scripts/kitchen_lib.py."""
    result = run(["git", "remote", "get-url", "origin"], cwd=target)
    url = result.stdout.strip() if result.returncode == 0 else ""
    if not url:
        return "manual", "no origin remote"
    if "github.com" in url:
        return "github", "origin is on github.com"
    if "gitlab" in url.lower():
        return "gitlab", "origin is a GitLab URL"
    return "manual", "origin is neither github.com nor GitLab"


# --------------------------------------------------------------------------
# Prerequisites
# --------------------------------------------------------------------------


def has_pyyaml() -> bool:
    try:
        import yaml  # noqa: F401 - availability check only
        return True
    except ImportError:
        return False


PYYAML_HELP = ("PyYAML is missing; Test Kitchen's scripts read YAML. Install it with "
               "`python3 -m pip install --user pyyaml` (or your system's package, such as python3-yaml).")
HOST_CLI = {"github": ("gh", "the GitHub CLI: https://cli.github.com"),
            "gitlab": ("glab", "the GitLab CLI: https://gitlab.com/gitlab-org/cli")}


def check_prerequisites(host: str, strict: bool) -> None:
    """Python is already checked at the top. PyYAML and git stop a real run; the host CLI only warns."""
    problems = []
    if shutil.which("git") is None:
        raise Failure("git is missing. Install git, then run this again.")
    if not has_pyyaml():
        problems.append(PYYAML_HELP)
    cli = HOST_CLI.get(host)
    if cli and shutil.which(cli[0]) is None:
        warn("%s is not installed. The delivery workflow uses %s to open and merge change requests." % (cli[0], cli[1]))
    if problems:
        if strict:
            raise Failure("\n".join(problems))
        for problem in problems:
            warn(problem)


# --------------------------------------------------------------------------
# kitchen.lock
# --------------------------------------------------------------------------


def read_lock(target: Path) -> Optional[Dict]:
    """The lock is JSON. JSON is also valid YAML, so tools reading it with PyYAML get the same data."""
    path = target / LOCK_NAME
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise Failure("%s is not valid JSON (%s). Restore it from git history." % (LOCK_NAME, exc))
    if not isinstance(data, dict) or not isinstance(data.get("files"), dict):
        raise Failure("%s has no 'files' table. Restore it from git history." % LOCK_NAME)
    return data


def write_lock(target: Path, version: str, source: Source, host: str, no_claude: bool,
               stacks: List[Dict[str, str]], files: Dict[str, str]) -> None:
    side_by_side = sorted(dest for dest in list(files) + [CONFIG_NAME]
                          if (target / (dest + NEW_SUFFIX)).is_file())
    data = {
        "about": "Written by Test Kitchen's init.py; do not edit. update and doctor compare "
                 "files against these hashes.",
        "lock_format": LOCK_FORMAT,
        "version": version,
        "source": source.label,
        "options": {"host": host, "no_claude": no_claude,
                    "toolchain": [s["stack"] for s in stacks]},
        # Framework path → sha256 of the content Test Kitchen installed there
        # (or offered next to it as <path>.kitchen-new). kitchen.yml is not
        # listed: it is the project's own configuration and update never touches it.
        "files": dict(sorted(files.items())),
        "side_by_side": side_by_side,
    }
    (target / LOCK_NAME).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------
# Writing
# --------------------------------------------------------------------------


def write_file(target: Path, dest: str, content: bytes, executable: bool) -> None:
    path = target / dest
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    if executable:
        path.chmod(path.stat().st_mode | 0o111)


def print_plan(rows: List[Tuple[str, str, str]]) -> None:
    width = max([len(action) for action, _, _ in rows] + [6])
    for action, path, note in rows:
        say("  %s  %s%s" % (action.ljust(width), path, ("  (" + note + ")") if note else ""))


def resolve_target(args: argparse.Namespace) -> Path:
    target = Path(args.target).expanduser().resolve() if args.target else Path.cwd().resolve()
    if not target.is_dir():
        raise UsageError("--target %s is not a folder." % target)
    return target


# --------------------------------------------------------------------------
# install
# --------------------------------------------------------------------------


def config_values(source_version: str, tests: List[str], code: List[str], test_command: str,
                  host: str, host_given: bool, host_reason: str) -> Dict[str, str]:
    """Values for `{{key}}` tokens in .tmpl files. Lists and strings are written as JSON,
    which YAML reads as flow lists and double-quoted strings."""
    if host_given:
        host_line = "host: %s   # optional: github | gitlab | manual; set by init.py --host" % host
    else:
        host_line = ("# host: %s   # optional: github | gitlab | manual; detected from the origin remote (%s)"
                     % (host, host_reason))
    return {
        "tests": json.dumps(tests, ensure_ascii=False),
        "code": json.dumps(code, ensure_ascii=False),
        "test_command": json.dumps(test_command, ensure_ascii=False),
        "host_line": host_line,
        "version": source_version,
        "repo_url": REPO_WEB,
    }


def ask_questions(args: argparse.Namespace, prompter: Prompter, guess: Guess) -> Tuple[List[str], List[str], str]:
    """The three questions. Flags answer them; otherwise the guess is offered as the default."""
    if guess.reasons and prompter.interactive:
        say("Guesses from this folder: " + "; ".join(guess.reasons) + ".")
    tests = split_globs(args.tests)
    if not tests:
        answer = prompter.value("Test files (globs, comma-separated)", ", ".join(guess.tests) or None, "--tests 'GLOB[,GLOB…]'")
        tests = split_globs([answer])
    code = split_globs(args.code)
    if not code:
        answer = prompter.value("Product code (globs, comma-separated)", ", ".join(guess.code) or None, "--code 'GLOB[,GLOB…]'")
        code = split_globs([answer])
    command = args.test_command
    while not command:
        command = prompter.value("Test command (must write JUnit XML to {report})", guess.test_command,
                                 "--test-command 'COMMAND'")
        if "{report}" not in command and prompter.interactive:
            say("  The command must contain {report}: Test Kitchen reads the JUnit XML written there.")
            command = None
    if "{report}" not in command:
        raise UsageError("The test command must contain {report}, the path of the JUnit XML file it writes: %r" % command)
    return tests, code, command


def cmd_install(args: argparse.Namespace, prompter: Prompter) -> int:
    target = resolve_target(args)
    if (target / LOCK_NAME).is_file():
        say("%s found: Test Kitchen is already installed here. Running update instead." % LOCK_NAME)
        return cmd_update(args, prompter)
    host_given = bool(args.host)
    if shutil.which("git") is None:
        raise Failure("git is missing. Install git, then run this again.")
    repo = is_git_repo(target)
    if repo:
        top = git_toplevel(target)
        if top is not None and top != target:
            raise UsageError("%s is inside the repository %s. Install at the repository root "
                             "(run there, or pass --target %s)." % (target, top, top))
    host, host_reason = (args.host, "chosen with --host") if host_given else detect_host(target)
    check_prerequisites(host, strict=not args.dry_run)

    if repo:
        dirty = run(["git", "status", "--porcelain"], cwd=target).stdout.strip()
        if dirty:
            warn("this folder has uncommitted changes. Test Kitchen only adds files, but committing "
                 "first lets you review its changes on their own.")
            if not args.dry_run and not prompter.confirm("Continue with uncommitted changes?", default=False):
                say("Stopped. Nothing was written.")
                return 1

    source = resolve_source(args)
    try:
        guess = guess_answers(target, list_project_files(target))
        tests, code, command = ask_questions(args, prompter, guess)
        stacks = detect_toolchain(target, command)
        values = config_values(source.version, tests, code, command, host, host_given, host_reason)
        notes: List[str] = []
        files = build_files(source, host, args.no_claude, values, stacks, notes)

        say("")
        say("Test Kitchen %s → %s" % (source.version, target))
        say("  source: %s" % source.label)
        say("  host: %s (%s)%s" % (host, host_reason, "" if host != "manual" else
                                    "; no CI files. Pass --host github or --host gitlab to get them"))
        say("  Claude Code files: %s" % ("no (--no-claude)" if args.no_claude else "yes"))
        say("  tests: %s" % ", ".join(tests))
        say("  code: %s" % ", ".join(code))
        say("  test_command: %s" % command)
        rows: List[Tuple[str, str, str]] = []
        if not repo:
            rows.append(("git init", ".", "this folder is not a git repository"))
        for dest in sorted(files):
            if (target / dest).exists():
                rows.append(("exists", dest, "yours is kept; new version written as %s%s" % (dest, NEW_SUFFIX)))
            else:
                rows.append(("create", dest, ""))
        rows.append(("write", LOCK_NAME, "version and sha256 of each installed file"))
        print_plan(rows)
        for note in notes:
            say("  note: " + note)
        if args.dry_run:
            say("Dry run: nothing was written.")
            return 0
        if not prompter.confirm("Write these files?", default=True):
            say("Stopped. Nothing was written.")
            return 1

        if not repo:
            result = run(["git", "init", "--quiet"], cwd=target)
            if result.returncode != 0:
                raise Failure("git init failed:\n" + tail(result.stderr))
        hashes: Dict[str, str] = {}
        for dest, tf in sorted(files.items()):
            exists = (target / dest).exists()
            write_file(target, dest + NEW_SUFFIX if exists else dest, tf.content, tf.executable)
            if dest != CONFIG_NAME:
                hashes[dest] = sha256_bytes(tf.content)
        write_lock(target, source.version, source, host, args.no_claude, stacks, hashes)
    finally:
        source.cleanup()

    pending = [dest for dest in sorted(files) if (target / (dest + NEW_SUFFIX)).is_file()]
    say("")
    say("Installed Test Kitchen %s." % source.version)
    say("Next:")
    step = 1
    if pending:
        say("  %d. Merge each side-by-side copy into your file by hand, then delete the copy: %s"
            % (step, ", ".join(d + NEW_SUFFIX for d in pending)))
        step += 1
    say("  %d. Fill the '## This project' section of AGENTS.md (an agent can draft it: see %s/blob/v%s/AGENT-INSTALL.md)." % (step, REPO_WEB, source.version))
    say("  %d. Review and commit the new files (for example: chore: install Test Kitchen %s)." % (step + 1, source.version))
    say("  %d. Define the product: /define in Claude Code, or follow playbooks/define.md with any agent." % (step + 2))
    say("")
    run_doctor(target)
    return 0


# --------------------------------------------------------------------------
# update
# --------------------------------------------------------------------------


def migration_notes(changelog: str, old: str, new: str) -> List[Tuple[str, str]]:
    """(version, notes) for every release after `old` up to and including `new`, oldest first.

    CHANGELOG.md has one `## x.y.z …` section per release, each with a
    `### Migration notes` subsection: what a project on the previous version
    must do. Missing subsections give empty notes.
    """
    found: List[Tuple[str, str]] = []
    for section in re.split(r"(?m)^## ", changelog)[1:]:
        head, _, body = section.partition("\n")
        match = re.match(r"v?(\d+\.\d+\.\d+)", head.strip())
        if not match:
            continue
        version = match.group(1)
        if vtuple(old) < vtuple(version) <= vtuple(new):
            notes = re.search(r"(?ms)^### Migration notes[^\n]*\n(.*?)(?=^### |\Z)", body)
            found.append((version, notes.group(1).strip() if notes else ""))
    return sorted(found, key=lambda item: vtuple(item[0]))


def configured_test_command(target: Path) -> str:
    """kitchen.yml's test_command, read with a regex so update works without PyYAML."""
    match = re.search(r"(?m)^test_command:\s*(.+?)\s*$", _read_text(target / CONFIG_NAME))
    return match.group(1) if match else ""


def cmd_update(args: argparse.Namespace, prompter: Prompter) -> int:
    target = resolve_target(args)
    lock = read_lock(target)
    if lock is None:
        raise UsageError("No %s in %s: Test Kitchen is not installed here. Run init.py without 'update' to install."
                         % (LOCK_NAME, target))
    if args.tests or args.code or args.test_command:
        warn("--tests, --code, and --test-command only apply to install; edit kitchen.yml instead.")
    old_version = str(lock.get("version", "0.0.0"))
    options = lock.get("options") or {}
    host = args.host or options.get("host") or detect_host(target)[0]
    # --no-claude can be turned on by an update but not off: dropping the
    # flag is not a request to install Claude Code files the person refused.
    no_claude = bool(args.no_claude or options.get("no_claude"))
    check_prerequisites(host, strict=not args.dry_run)

    source = resolve_source(args)
    try:
        stacks = detect_toolchain(target, configured_test_command(target))
        # kitchen.yml is the project's own file: update renders only the
        # tokens other templates may use, and never writes kitchen.yml.
        values = {"version": source.version, "repo_url": REPO_WEB}
        notes: List[str] = []
        new_files = build_files(source, host, no_claude, values, stacks, notes)
        new_files.pop(CONFIG_NAME, None)
        locked: Dict[str, str] = {k: str(v) for k, v in lock["files"].items()}

        rows: List[Tuple[str, str, str]] = []
        actions: Dict[str, str] = {}
        same = 0
        for dest in sorted(new_files):
            new_sha = sha256_bytes(new_files[dest].content)
            local = target / dest
            local_sha = sha256_file(local) if local.is_file() else None
            if dest not in locked:
                action = "add-side" if local.exists() else "add"
            elif local_sha is None:
                action = "restore"
            elif local_sha == new_sha:
                action = "same"
            elif local_sha == locked[dest]:
                action = "replace"  # not edited locally: safe to replace
            elif new_sha == locked[dest]:
                action = "keep"  # edited locally, and the new version did not change it
            else:
                action = "conflict"  # edited locally and changed in the new version
            actions[dest] = action
            if action == "same":
                same += 1
                continue
            note = {
                "add": "new in this version",
                "add-side": "new in this version; yours is kept, new version written as %s%s" % (dest, NEW_SUFFIX),
                "restore": "missing locally",
                "replace": "unchanged locally; new version",
                "keep": "edited locally; the new version did not change it",
                "conflict": "edited locally and changed in the new version: keep, take, or diff",
            }[action]
            rows.append(({"add-side": "add", "restore": "restore"}.get(action, action), dest, note))
        removed = sorted(dest for dest in locked if dest not in new_files)
        for dest in removed:
            rows.append(("removed", dest, "no longer part of Test Kitchen; not deleted, remove it by hand if unused"))

        say("Test Kitchen update %s → %s in %s" % (old_version, source.version, target))
        say("  source: %s" % source.label)
        say("  host: %s; Claude Code files: %s" % (host, "no (--no-claude)" if no_claude else "yes"))
        if vtuple(source.version) < vtuple(old_version):
            warn("%s is older than the installed %s." % (source.version, old_version))
        if rows:
            print_plan(rows)
        say("  unchanged: %d file(s)" % same)
        for note in notes:
            say("  note: " + note)
        notes_found = migration_notes(source.changelog(), old_version, source.version)
        if notes_found:
            say("")
            say("Migration notes (%s → %s):" % (old_version, source.version))
            for version, text in notes_found:
                say("  %s: %s" % (version, text.replace("\n", "\n    ") if text else "none."))
        if args.dry_run:
            say("Dry run: nothing was written.")
            return 0
        if not prompter.confirm("Apply this update?", default=True):
            say("Stopped. Nothing was written.")
            return 1

        conflicts_kept: List[str] = []
        hashes: Dict[str, str] = {}
        for dest in sorted(new_files):
            tf = new_files[dest]
            hashes[dest] = sha256_bytes(tf.content)
            action = actions[dest]
            if action in ("add", "restore", "replace"):
                write_file(target, dest, tf.content, tf.executable)
            elif action == "add-side":
                write_file(target, dest + NEW_SUFFIX, tf.content, tf.executable)
            elif action == "conflict":
                if resolve_conflict(prompter, target, dest, tf.content) == "take":
                    write_file(target, dest, tf.content, tf.executable)
                else:
                    write_file(target, dest + NEW_SUFFIX, tf.content, tf.executable)
                    conflicts_kept.append(dest)
        write_lock(target, source.version, source, host, no_claude, stacks, hashes)
    finally:
        source.cleanup()

    say("")
    say("Updated Test Kitchen to %s." % source.version)
    if conflicts_kept:
        say("Kept your version of: %s. The new versions are next to them as <name>%s; merge by hand, then delete them."
            % (", ".join(conflicts_kept), NEW_SUFFIX))
    if removed:
        say("No longer part of Test Kitchen (not deleted): %s" % ", ".join(removed))
    say("Review and commit the changes (for example: chore: update Test Kitchen to %s)." % source.version)
    say("")
    run_doctor(target)
    return 0


def resolve_conflict(prompter: Prompter, target: Path, dest: str, new_content: bytes) -> str:
    """keep / take / diff for one conflicted file. --yes (or no terminal) keeps."""
    while True:
        choice = prompter.choose(
            "%s was edited locally and changed in the new version. [k]eep yours (new version saved as %s%s), "
            "[t]ake the new version, or show the [d]iff?" % (dest, dest, NEW_SUFFIX),
            {"k": "keep", "t": "take", "d": "diff"}, "k")
        if choice == "d":
            local = _read_text(target / dest).splitlines(keepends=True)
            new = new_content.decode("utf-8", errors="replace").splitlines(keepends=True)
            say("".join(difflib.unified_diff(local, new, "yours/" + dest, "new/" + dest)))
            continue
        return "take" if choice == "t" else "keep"


# --------------------------------------------------------------------------
# doctor
# --------------------------------------------------------------------------


class Checklist:
    def __init__(self) -> None:
        self.items: List[Tuple[str, str, str]] = []

    def add(self, status: str, title: str, fix: str = "") -> None:
        self.items.append((status, title, fix))
        say("  %s  %s" % (status, title))
        if fix:
            for line in fix.splitlines():
                say("        " + line)

    def failed(self) -> int:
        return sum(1 for status, _, _ in self.items if status == "FAIL")

    def warned(self) -> int:
        return sum(1 for status, _, _ in self.items if status == "WARN")


def _script_env() -> Dict[str, str]:
    # Doctor is read-only: keep Python from writing __pycache__ folders into
    # the project's scripts/ while running them.
    return dict(os.environ, PYTHONDONTWRITEBYTECODE="1")


def load_config(target: Path) -> Tuple[Optional[Dict], str]:
    """(config, problem). Light validation; scripts/backlog_check.py does the full one."""
    path = target / CONFIG_NAME
    if not path.is_file():
        return None, "%s is missing" % CONFIG_NAME
    try:
        import yaml
    except ImportError:
        return None, "cannot read %s without PyYAML" % CONFIG_NAME
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return None, "%s is not valid YAML: %s" % (CONFIG_NAME, str(exc).splitlines()[0])
    if not isinstance(data, dict):
        return None, "%s must be a mapping of keys" % CONFIG_NAME
    problems = []
    unknown = sorted(set(data) - CONFIG_KEYS)
    if unknown:
        problems.append("unknown key(s): %s" % ", ".join(unknown))
    for key in ("tests", "code"):
        value = data.get(key)
        if isinstance(value, str):
            value = [value]
        if not value or not isinstance(value, list) or not all(isinstance(v, str) and v for v in value):
            problems.append("%s must be a non-empty list of globs" % key)
    if not isinstance(data.get("test_command"), str) or not data.get("test_command", "").strip():
        problems.append("test_command must be a non-empty string")
    if "host" in data and data["host"] not in HOSTS:
        problems.append("host must be one of %s" % ", ".join(HOSTS))
    if "autonomy" in data and data["autonomy"] not in ("merge", "pr", "supervised"):
        problems.append("autonomy must be merge, pr, or supervised")
    return data, "; ".join(problems)


def guard_status(target: Path) -> Tuple[bool, str]:
    """Is the guard hook registered as Claude Code's PreToolUse hook, and not switched off?"""
    if not (target / ".claude" / "hooks" / "guard.py").is_file():
        return False, ".claude/hooks/guard.py is missing"
    path = target / ".claude" / "settings.json"
    try:
        settings = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False, ".claude/settings.json is missing or not valid JSON"
    registered = False
    hooks = settings.get("hooks", {}) if isinstance(settings, dict) else {}
    for entry in hooks.get("PreToolUse", []) if isinstance(hooks, dict) else []:
        for hook in entry.get("hooks", []) if isinstance(entry, dict) else []:
            if isinstance(hook, dict) and "guard.py" in str(hook.get("command", "")):
                registered = True
    if not registered:
        return False, "no PreToolUse hook in .claude/settings.json runs .claude/hooks/guard.py"
    # Claude Code's `disableAllHooks` setting turns every hook off, the guard
    # included; a local settings file can set it without touching settings.json.
    for name in ("settings.json", "settings.local.json"):
        try:
            data = json.loads((target / ".claude" / name).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(data, dict) and data.get("disableAllHooks") is True:
            return False, ".claude/%s sets disableAllHooks, which switches the guard off" % name
    return True, ""


GUARD_FIX = ("Restore the hook: copy the \"hooks\" block from Test Kitchen's template/claude/settings.json "
             "into .claude/settings.json (Test Kitchen's guide/install.md shows it), or run init.py update "
             "(see the update command in the guide) if the file was not edited. Without it nothing stops an agent from merging on a failing check.")


def run_doctor(target: Path) -> int:
    say("Test Kitchen doctor: %s" % target)
    c = Checklist()
    c.add("PASS", "Python %d.%d.%d" % sys.version_info[:3])
    if has_pyyaml():
        c.add("PASS", "PyYAML installed")
    else:
        c.add("FAIL", "PyYAML missing", PYYAML_HELP)
    if shutil.which("git"):
        c.add("PASS", "git installed")
    else:
        c.add("FAIL", "git missing", "Install git.")
    repo = shutil.which("git") is not None and is_git_repo(target)
    if repo:
        c.add("PASS", "git repository")
    else:
        c.add("FAIL", "not a git repository", "Run `git init` here, or run doctor from the repository root.")

    try:
        lock = read_lock(target)
    except Failure as exc:
        lock = None
        c.add("FAIL", "kitchen.lock unreadable", str(exc))
    else:
        if lock is None:
            c.add("FAIL", "kitchen.lock missing", "Install Test Kitchen here: " + rerun())
        else:
            c.add("PASS", "Test Kitchen %s installed (kitchen.lock)" % lock.get("version", "?"))
    locked: Dict[str, str] = {k: str(v) for k, v in (lock or {}).get("files", {}).items()}
    options = (lock or {}).get("options") or {}

    missing = sorted(dest for dest in locked if not (target / dest).is_file())
    if lock is not None:
        if missing:
            c.add("FAIL", "framework files missing: %s" % ", ".join(missing),
                  "Restore them with: " + rerun("update"))
        else:
            c.add("PASS", "all %d framework files present" % len(locked))
    for dest in sorted(list(locked) + [CONFIG_NAME]):
        if (target / (dest + NEW_SUFFIX)).is_file():
            c.add("WARN", "%s%s waiting to be merged" % (dest, NEW_SUFFIX),
                  "Merge it into %s by hand, then delete %s%s." % (dest, dest, NEW_SUFFIX))

    config, problem = load_config(target)
    if problem:
        c.add("FAIL", "kitchen.yml: " + problem, "Fix kitchen.yml; guide/configuration.md lists every key.")
    else:
        c.add("PASS", "kitchen.yml valid")
    if config:
        files = list_project_files(target)
        ignore = config.get("ignore") or []
        ignore = [ignore] if isinstance(ignore, str) else [g for g in ignore if isinstance(g, str)]
        scanned = [f for f in files if not matches_any(f, ignore)]
        for key in ("tests", "code"):
            globs = config.get(key) or []
            globs = [globs] if isinstance(globs, str) else [g for g in globs if isinstance(g, str)]
            empty = [g for g in globs if not any(glob_to_regex(g).match(f) for f in scanned)]
            if empty:
                c.add("WARN", "%s glob(s) match no file yet: %s" % (key, ", ".join(empty)),
                      "Fine for a new project; otherwise fix the globs in kitchen.yml.")
            elif globs:
                c.add("PASS", "%s globs match files" % key)
        command = config.get("test_command")
        if isinstance(command, str) and "{report}" in command:
            c.add("PASS", "test_command writes JUnit XML to {report}")
        elif isinstance(command, str):
            c.add("FAIL", "test_command has no {report}",
                  "The command must write JUnit XML to the {report} path: guide/test-runners.md has one per runner.")

    if lock is not None:
        if options.get("no_claude"):
            c.add("SKIP", "merge guard: Claude Code files not installed (--no-claude)",
                  "Agents without the guard must run deliver.py gate merge before every merge (guide/agents.md).")
        else:
            ok, why = guard_status(target)
            if ok:
                c.add("PASS", "merge guard registered in .claude/settings.json")
            else:
                c.add("FAIL", "merge guard not registered: " + why, GUARD_FIX)

        installed_host = options.get("host", "manual")
        config_host = (config or {}).get("host") or (detect_host(target)[0] if repo else "manual")
        if config_host != installed_host:
            c.add("WARN", "kitchen.yml or the origin remote says host %s, but the CI files installed are for %s"
                  % (config_host, installed_host),
                  "Run: " + rerun("update --host %s" % config_host))
        ci_files = [dest for dest in sorted(locked) if ci_style(dest)]
        if installed_host == "manual":
            c.add("SKIP", "CI: manual host, no CI files",
                  "Run python3 scripts/deliver.py check yourself before every merge.")
        elif not ci_files:
            c.add("WARN", "CI: no CI file in this install", "Run: " + rerun("update --host %s" % installed_host))
        for dest in ci_files:
            path = target / dest
            if not path.is_file():
                c.add("FAIL", "CI file missing: %s" % dest, "Restore it with: " + rerun("update"))
                continue
            text = _read_text(path)
            # Filled by init: the marker carries init's note. Unfilled: the
            # template's placeholder text is still there, or (for a template
            # whose placeholder wording differs) the file is byte-for-byte
            # what init installed with the bare marker. Anything else was
            # edited by hand, which doctor cannot judge.
            unfilled = TOOLCHAIN_PLACEHOLDER in text or (
                TOOLCHAIN_MARKER in text and sha256_file(path) == locked.get(dest))
            if TOOLCHAIN_FILLED in text:
                c.add("PASS", "CI file %s present, toolchain step filled by init" % dest)
            elif not unfilled:
                c.add("PASS", "CI file %s present (edited since install; check its toolchain step by hand)" % dest)
            else:
                c.add("WARN", "CI file %s: toolchain step not filled" % dest,
                      "Replace the step under '%s' with your language setup and dependency install, "
                      "or CI cannot run your tests." % TOOLCHAIN_MARKER)

        cli = HOST_CLI.get(config_host)
        if cli:
            if shutil.which(cli[0]) is None:
                c.add("WARN", "%s not installed" % cli[0], "Install %s and sign in." % cli[1])
            elif run([cli[0], "auth", "status"], cwd=target, timeout=30).returncode == 0:
                c.add("PASS", "%s signed in" % cli[0])
            else:
                c.add("WARN", "%s not signed in" % cli[0], "Run: %s auth login" % cli[0])

    scripts = target / "scripts"
    if (scripts / "backlog_check.py").is_file():
        result = run([sys.executable, "scripts/backlog_check.py"], cwd=target, timeout=300, env=_script_env())
        if result.returncode == 0:
            c.add("PASS", "backlog_check.py passes")
        else:
            c.add("FAIL", "backlog_check.py reports errors",
                  tail(result.stdout + "\n" + result.stderr) + "\nFix the ERROR lines above.")
    elif lock is not None:
        c.add("FAIL", "scripts/backlog_check.py missing", "Restore it with: " + rerun("update"))
    # Every installed script that offers --self-test runs it: the set of
    # scripts may grow between versions, and the lock says which are ours.
    for dest in sorted(locked):
        if re.fullmatch(r"scripts/[^/]+\.py", dest) and "--self-test" in _read_text(target / dest):
            result = run([sys.executable, dest, "--self-test"], cwd=target, timeout=300, env=_script_env())
            if result.returncode == 0:
                c.add("PASS", "%s --self-test" % dest)
            else:
                c.add("FAIL", "%s --self-test fails" % dest,
                      tail(result.stdout + "\n" + result.stderr) + "\nRestore the file with init.py update, or report the failure.")

    failed, warned = c.failed(), c.warned()
    say("doctor: %s" % ("all checks passed" if not failed and not warned else
                        "%d failed, %d warning(s)" % (failed, warned)))
    return 1 if failed else 0


def cmd_doctor(args: argparse.Namespace) -> int:
    return run_doctor(resolve_target(args))


# --------------------------------------------------------------------------
# Command line
# --------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="init.py",
        description="Install, update, or check Test Kitchen %s in a project repository." % VERSION,
        epilog=(
            "examples:\n"
            "  (run from the project folder; <clone> is your Test Kitchen checkout)\n"
            "  python3 <clone>/init.py --dry-run            show what an install would write\n"
            "  python3 <clone>/init.py --yes --tests 'tests/**' --code 'src/**' \\\n"
            "      --test-command 'python3 -m pytest {files} --junitxml={report}'\n"
            "  python3 <clone>/init.py update               update to this file's version\n"
            "  python3 <clone>/init.py doctor               check the installed copy\n"
            "Piped: curl -fsSL <init.py URL> | python3 - [mode] [options]\n"
            "Questions are read from the terminal; with --yes or without a terminal they take\n"
            "their defaults, and a required answer with no default stops the run (exit 2)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("mode", nargs="?", default="install", choices=("install", "update", "doctor"),
                        help="install (default), update, or doctor")
    parser.add_argument("--dry-run", action="store_true", help="show the plan and write nothing")
    parser.add_argument("--yes", action="store_true",
                        help="answer yes to every question; on update conflicts, keep yours and write <name>.kitchen-new")
    parser.add_argument("--tests", action="append", metavar="GLOBS",
                        help="test file globs, comma-separated (repeatable)")
    parser.add_argument("--code", action="append", metavar="GLOBS",
                        help="product code globs, comma-separated (repeatable)")
    parser.add_argument("--test-command", metavar="COMMAND",
                        help="command that runs tests and writes JUnit XML to {report}")
    parser.add_argument("--host", choices=HOSTS, help="change-request host (default: detected from the origin remote)")
    parser.add_argument("--no-claude", action="store_true", help="skip the Claude Code files (.claude/ and CLAUDE.md)")
    parser.add_argument("--source", metavar="DIR", help="install from a local Test Kitchen checkout instead of downloading")
    parser.add_argument("--version", metavar="vX.Y.Z", help="the release to install or update to (default: %s)" % VERSION)
    parser.add_argument("--target", metavar="DIR", help="the project's repository root (default: the current folder)")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.mode == "doctor":
            return cmd_doctor(args)
        prompter = Prompter(assume_yes=args.yes)
        if args.mode == "update":
            return cmd_update(args, prompter)
        return cmd_install(args, prompter)
    except UsageError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    except Failure as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nStopped.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
